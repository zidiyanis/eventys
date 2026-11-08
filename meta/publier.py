"""Publie un Reel (Instagram + Facebook, automatique). --brouillon : paquet Drive sans publier.

Publie un Reel sur Instagram depuis le disque local (mode --en-ligne).

    python H:/eventys/meta/publier.py montages/RETOUR_v4_lapin-patron.mp4 legende.txt
    python H:/eventys/meta/publier.py --verifier       (controle sans rien publier)

POURQUOI UN TUNNEL
Instagram ne recoit pas le fichier : il exige une URL publique et vient
telecharger la video lui-meme. Plutot que d'heberger les videos en ligne, on
ouvre un tunnel Cloudflare ephemere vers un serveur local, le temps que Meta
vienne chercher le fichier, puis on referme. L'adresse n'existe plus apres.

ETAPES COTE META (obligatoirement dans cet ordre)
  1. creer un conteneur media  -> POST /{ig_user_id}/media
  2. attendre son encodage     -> GET  /{container_id}?fields=status_code
  3. publier                   -> POST /{ig_user_id}/media_publish
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import controle  # noqa: E402
import doublon  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
IDENT = os.path.join(ICI, "identifiants.json")
CLOUDFLARED = os.path.join(RACINE, "tools", "bin", "cloudflared.exe")
API = "https://graph.facebook.com/v21.0"
PORT = 8723


# --------------------------------------------------------------- Meta

def _appel(chemin, params, poste=False):
    donnees = urllib.parse.urlencode(params).encode()
    url = f"{API}/{chemin}"
    req = (urllib.request.Request(url, data=donnees, method="POST") if poste
           else urllib.request.Request(f"{url}?{donnees.decode()}"))
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode()).get("error", {})
        raise SystemExit(f"\nMeta refuse : {err.get('message')}"
                         f"\n  code {err.get('code')}"
                         f" / sous-code {err.get('error_subcode')}")


def charge_identifiants():
    if not os.path.exists(IDENT):
        raise SystemExit(f"Fichier absent : {IDENT}\n"
                         "Le jeton n'a pas encore ete configure.")
    with open(IDENT, encoding="utf-8") as f:
        d = json.load(f)
    if not d.get("ig_user_id"):
        raise SystemExit("Aucun compte Instagram dans les identifiants.")
    return d


# --------------------------------------------------- serveur + tunnel

class _Muet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def ouvre_tunnel(dossier):
    """Sert `dossier` en local, puis l'expose par un tunnel Cloudflare."""
    serveur = ThreadingHTTPServer(
        ("127.0.0.1", PORT), partial(_Muet, directory=dossier))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()

    proc = subprocess.Popen(
        [CLOUDFLARED, "tunnel", "--url", f"http://127.0.0.1:{PORT}",
         "--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace", bufsize=1)

    base, debut = None, time.time()
    while time.time() - debut < 60:
        ligne = proc.stdout.readline()
        if not ligne:
            break
        m = re.search(r"https://[-\w]+\.trycloudflare\.com", ligne)
        if m:
            base = m.group(0)
            break
    if not base:
        proc.kill(); serveur.shutdown()
        raise SystemExit("Le tunnel Cloudflare n'a pas demarre.")
    threading.Thread(target=lambda: [l for l in proc.stdout], daemon=True).start()

    # Le tunnel renvoie 502 pendant quelques secondes le temps que Cloudflare
    # propage le sous-domaine. Si on donnait l'adresse a Meta pendant cette
    # fenetre, le telechargement echouerait et la publication avec.
    temoin = next((f for f in os.listdir(dossier)
                   if os.path.isfile(os.path.join(dossier, f))), None)
    if temoin:
        sonde = f"{base}/{urllib.parse.quote(temoin)}"
        for _ in range(24):
            time.sleep(5)
            try:
                req = urllib.request.Request(sonde, method="HEAD")
                with urllib.request.urlopen(req, timeout=20):
                    break
            except Exception:
                continue
        else:
            proc.kill(); serveur.shutdown()
            raise SystemExit("Le tunnel ne repond pas apres 120 s.")
    return base, serveur, proc


# ------------------------------------------------------------- flux

def publier(video, legende, vignette_s=None, forcer=False):
    """Publie un Reel sur Instagram et sur la Page Facebook.

    Un controle automatique passe AVANT. L'API Instagram ne sait pas
    supprimer une publication : une erreur publiee reste en ligne jusqu'a
    ce que Yanis l'efface a la main. La seule protection est donc de
    refuser de publier ce qui ne va pas.
    """
    pbs, mesures = controle.controler(video)
    print("Controle avant publication :")
    for m in mesures:
        print("   ", m)
    if pbs:
        print("\nPROBLEMES :")
        for x in pbs:
            print("   -", x)
        if not forcer:
            raise SystemExit(
                "\nPublication annulee. Corrige, ou relance avec --forcer "
                "si tu assumes.")
        print("\n(--forcer : on publie quand meme)")
    print()

    # Deuxieme barriere, independante de la premiere : a-t-on DEJA publie
    # ca ? Le meme Reel est parti trois jours de suite les 26, 27 et 28
    # octobre, et les vues sont tombees de 17 162 a 2 631. Rien ne se
    # supprime chez Instagram : ce refus est la seule protection.
    d_refus, d_avert, d_mesures = doublon.controler(video, legende)
    print("Controle des doublons :")
    for m in d_mesures:
        print("   ", m)
    for a in d_avert:
        print("  ! ", a)
    if d_refus:
        print("\nDOUBLON :")
        for x in d_refus:
            print("   -", x)
        if not forcer:
            raise SystemExit(
                "\nPublication annulee : ce contenu a deja ete publie. "
                "Monte autre chose, ou relance avec --forcer si tu assumes.")
        print("\n(--forcer : on republie quand meme)")
    print()

    ident = charge_identifiants()
    ig = ident["ig_user_id"]
    jeton = ident["page_token"]

    video = os.path.abspath(video)
    dossier, nom = os.path.dirname(video), os.path.basename(video)
    taille = os.path.getsize(video) / 1048576
    print(f"Video : {nom}  ({taille:.1f} Mo)")
    print(f"Compte Instagram : {ig}\n")

    print("1/4  Ouverture du tunnel…")
    base, serveur, proc = ouvre_tunnel(dossier)
    url = f"{base}/{urllib.parse.quote(nom)}"
    print(f"     {base}")

    try:
        print("2/4  Creation du conteneur…")
        params = {
            "media_type": "REELS",
            "video_url": url,
            "caption": legende,
            "share_to_feed": "true",
            "access_token": jeton,
        }
        if vignette_s is not None:
            # Sans cela, Instagram prend la PREMIERE image comme couverture.
            # Sur une video qui ouvre sur le rideau du box, ca donne une
            # vignette grise au milieu d'une grille de tables dressees — ca
            # detonne. On designe donc une image choisie.
            params["thumb_offset"] = str(int(vignette_s * 1000))
        cont = _appel(f"{ig}/media", params, poste=True)["id"]
        print(f"     conteneur {cont}")

        print("3/4  Encodage par Meta (peut prendre quelques minutes)…")
        for i in range(90):
            time.sleep(5)
            st = _appel(cont, {"fields": "status_code,status",
                               "access_token": jeton})
            code = st.get("status_code")
            print(f"     [{i*5:>4}s] {code}")
            if code == "FINISHED":
                break
            if code == "ERROR":
                raise SystemExit(f"     Encodage echoue : {st.get('status')}")
        else:
            raise SystemExit("     Delai depasse.")

        print("4/5  Publication sur Instagram…")
        pub = _appel(f"{ig}/media_publish",
                     {"creation_id": cont, "access_token": jeton}, poste=True)
        print(f"     publie — media {pub['id']}")

        # Inscrit au registre IMMEDIATEMENT, avant Facebook : si Facebook
        # echoue et qu'on relance, le Reel Instagram est deja en ligne et
        # doit etre reconnu comme tel.
        doublon.enregistrer(video, legende, media_id=pub["id"])
        print("     inscrit au registre des publications")

        if ident.get("peut_publier_facebook") and not SANS_FACEBOOK:
            print("5/5  Publication sur la Page Facebook…")
            try:
                fid = publier_facebook(video, legende, base, ident)
                print(f"     publie — video {fid}")
            except SystemExit as e:
                # Un echec cote Facebook ne doit pas laisser croire que la
                # publication Instagram a rate : elle est deja en ligne.
                print(f"     ECHEC Facebook : {e}")
                print("     (la publication Instagram est bien passee)")
        else:
            print("5/5  Facebook ignore.")
        print("\nTermine.")
    finally:
        print("\nFermeture du tunnel.")
        proc.kill()
        serveur.shutdown()


def brouillon(video, legende, vignette_s=None, forcer=False):
    """Mode par defaut des videos : controles, puis paquet Drive, rien en ligne.

    Les memes barrieres que `publier` s'appliquent, pour ne pas deposer un
    brouillon qui serait refuse ensuite. Le registre des doublons n'est PAS
    alimente : rien n'est publie tant que Yanis n'a pas appuye lui-meme.
    Mode --brouillon, optionnel.
    """
    pbs, mesures = controle.controler(video)
    print("Controle :")
    for m in mesures:
        print("   ", m)
    if pbs:
        print("\nPROBLEMES :")
        for x in pbs:
            print("   -", x)
        if not forcer:
            raise SystemExit("\nBrouillon annule. Corrige, ou --forcer.")
    d_refus, d_avert, d_mesures = doublon.controler(video, legende)
    for a in d_avert:
        print("  ! ", a)
    if d_refus:
        print("\nDOUBLON :")
        for x in d_refus:
            print("   -", x)
        if not forcer:
            raise SystemExit("\nBrouillon annule : deja publie. --forcer si tu assumes.")

    sys.path.insert(0, os.path.join(RACINE, "montages"))
    import paquet_tiktok
    d = paquet_tiktok.preparer_brouillon(video, legende, vignette_s)
    print(f"\nBrouillon pret (rien n'est publie) : {d}")
    for f in sorted(os.listdir(d)):
        print("  ", f)


def publier_facebook(video, legende, base, ident):
    """Publie la meme video sur la Page Facebook.

    Facebook accepte lui aussi une URL : on reutilise le tunnel deja ouvert
    pour Instagram plutot que d'en monter un second. L'API Page est plus
    simple qu'Instagram — pas de conteneur ni d'attente d'encodage, un seul
    appel suffit.
    """
    nom = os.path.basename(video)
    url = f"{base}/{urllib.parse.quote(nom)}"
    rep = _appel(f"{ident['page_id']}/videos", {
        "file_url": url,
        "description": legende,
        "access_token": ident["page_token"],
    }, poste=True)
    return rep.get("id")


def publier_story(image, ident, base):
    """Publie une story Instagram (image fixe).

    L'API n'accepte ni legende ni autocollant interactif sur une story :
    tout le texte doit deja etre incruste dans l'image. Et elle ne sait pas
    l'epingler « a la une » — ca reste a faire a la main dans les 24 h.
    """
    nom = os.path.basename(image)
    cont = _appel(f"{ident['ig_user_id']}/media", {
        "media_type": "STORIES",
        "image_url": f"{base}/{urllib.parse.quote(nom)}",
        "access_token": ident["page_token"],
    }, poste=True)["id"]
    for _ in range(40):
        st = _appel(cont, {"fields": "status_code",
                           "access_token": ident["page_token"]})
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            raise SystemExit(f"     encodage echoue : {st}")
        time.sleep(3)
    return _appel(f"{ident['ig_user_id']}/media_publish",
                  {"creation_id": cont,
                   "access_token": ident["page_token"]}, poste=True)["id"]


def story_video(video):
    """Publie une VIDEO en story.

    L'API ne sait pas « partager une publication dans sa story » comme le
    fait l'application : il n'existe pas de story qui renvoie vers un post.
    On republie donc la video elle-meme en story. Limites de Meta : 60 s et
    100 Mo, ce que notre Reel respecte.
    """
    ident = charge_identifiants()
    video = os.path.abspath(video)
    dossier, nom = os.path.dirname(video), os.path.basename(video)
    taille = os.path.getsize(video) / 1048576
    print(f"Story video : {nom}  ({taille:.1f} Mo)")

    print("1/3  Ouverture du tunnel…")
    base, serveur, proc = ouvre_tunnel(dossier)
    print(f"     {base}")
    try:
        print("2/3  Creation du conteneur…")
        cont = _appel(f"{ident['ig_user_id']}/media", {
            "media_type": "STORIES",
            "video_url": f"{base}/{urllib.parse.quote(nom)}",
            "access_token": ident["page_token"],
        }, poste=True)["id"]

        for i in range(60):
            time.sleep(5)
            st = _appel(cont, {"fields": "status_code,status",
                               "access_token": ident["page_token"]})
            code = st.get("status_code")
            print(f"     [{i*5:>4}s] {code}")
            if code == "FINISHED":
                break
            if code == "ERROR":
                raise SystemExit(f"     encodage echoue : {st.get('status')}")
        else:
            raise SystemExit("     delai depasse.")

        print("3/3  Publication…")
        mid = _appel(f"{ident['ig_user_id']}/media_publish",
                     {"creation_id": cont,
                      "access_token": ident["page_token"]}, poste=True)["id"]
        print(f"\n     story publiee — {mid}")
        return mid
    finally:
        print("\nFermeture du tunnel.")
        proc.kill()
        serveur.shutdown()


def _story_video_depuis(video, ident, base):
    """Publie une video en story, le tunnel etant deja ouvert."""
    nom = os.path.basename(video)
    cont = _appel(f"{ident['ig_user_id']}/media", {
        "media_type": "STORIES",
        "video_url": f"{base}/{urllib.parse.quote(nom)}",
        "access_token": ident["page_token"],
    }, poste=True)["id"]
    for _ in range(60):
        time.sleep(4)
        st = _appel(cont, {"fields": "status_code,status",
                           "access_token": ident["page_token"]})
        code = st.get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise SystemExit(f"     encodage echoue : {st.get('status')}")
    else:
        raise SystemExit("     delai depasse.")
    return _appel(f"{ident['ig_user_id']}/media_publish",
                  {"creation_id": cont,
                   "access_token": ident["page_token"]}, poste=True)["id"]


def stories(dossier):
    """Publie en stories tout un dossier, images ET videos.

    Une story en image fixe ne peut pas porter de son : pour avoir de la
    musique, il faut une video. Le dossier peut donc contenir les deux, et
    chaque fichier part par le bon chemin selon son extension.
    """
    ident = charge_identifiants()
    fichiers = sorted(f for f in os.listdir(dossier)
                      if f.lower().endswith((".png", ".jpg", ".mp4", ".mov")))
    if not fichiers:
        raise SystemExit("Aucun fichier publiable dans " + dossier)
    # Une story deja publiee il y a moins de deux semaines est ecartee, pas
    # refusee : la serie du jour continue sans elle. Au-dela de deux
    # semaines, plus personne ne s'en souvient et le recyclage est legitime.
    import datetime
    recents = {l["sha"] for l in doublon.lire()
               if l.get("quoi") == "STORY" and l.get("sha")
               and l["date"][:10] >= (datetime.date.today()
                                      - datetime.timedelta(days=14)
                                      ).strftime("%Y-%m-%d")}
    gardes = []
    for f in fichiers:
        s = doublon.sha(os.path.join(dossier, f))
        if s in recents:
            print(f"     ECARTEE (deja publiee ces 14 jours) : {f}")
        else:
            gardes.append(f)
    fichiers = gardes
    if not fichiers:
        raise SystemExit("Toutes les stories de ce dossier ont deja ete "
                         "publiees ces 14 jours.")

    print(f"{len(fichiers)} story(ies) a publier depuis {dossier}")
    print("1/2  Ouverture du tunnel…")
    base, serveur, proc = ouvre_tunnel(os.path.abspath(dossier))
    print(f"     {base}")
    try:
        print("2/2  Publication…")
        for i, f in enumerate(fichiers, 1):
            chemin = os.path.join(dossier, f)
            if f.lower().endswith((".mp4", ".mov")):
                mid = _story_video_depuis(chemin, ident, base)
            else:
                mid = publier_story(chemin, ident, base)
            print(f"     {i}/{len(fichiers)}  {f}  ->  {mid}")
            doublon.enregistrer(chemin, "", media_id=mid, quoi="STORY")
            time.sleep(2)
    finally:
        print("\nFermeture du tunnel.")
        proc.kill()
        serveur.shutdown()


def carrousel(dossier, legende):
    """Publie un carrousel Instagram (jusqu'a 10 images).

    Trois temps : un conteneur par image avec `is_carousel_item`, puis un
    conteneur CAROUSEL qui les rassemble, puis la publication. Toutes les
    images doivent avoir le MEME rapport largeur/hauteur, sinon Meta refuse.
    """
    ident = charge_identifiants()
    ig, jeton = ident["ig_user_id"], ident["page_token"]
    images = sorted((f for f in os.listdir(dossier)
                     if f.lower().endswith((".jpg", ".jpeg", ".png"))),
                    key=lambda f: int(os.path.splitext(f)[0])
                    if os.path.splitext(f)[0].isdigit() else 0)
    if not images:
        raise SystemExit("Aucune image dans " + dossier)
    print(f"Carrousel de {len(images)} images")

    print("1/4  Ouverture du tunnel…")
    base, serveur, proc = ouvre_tunnel(os.path.abspath(dossier))
    print(f"     {base}")
    try:
        print("2/4  Creation des conteneurs…")
        enfants = []
        for i, img in enumerate(images, 1):
            c = _appel(f"{ig}/media", {
                "image_url": f"{base}/{urllib.parse.quote(img)}",
                "is_carousel_item": "true",
                "access_token": jeton,
            }, poste=True)["id"]
            enfants.append(c)
            print(f"     {i}/{len(images)}  {img}  ->  {c}")

        print("3/4  Assemblage du carrousel…")
        pere = _appel(f"{ig}/media", {
            "media_type": "CAROUSEL",
            "children": ",".join(enfants),
            "caption": legende,
            "access_token": jeton,
        }, poste=True)["id"]

        for i in range(40):
            time.sleep(4)
            st = _appel(pere, {"fields": "status_code",
                               "access_token": jeton})
            if st.get("status_code") == "FINISHED":
                break
            if st.get("status_code") == "ERROR":
                raise SystemExit(f"     echec : {st}")

        print("4/4  Publication…")
        mid = _appel(f"{ig}/media_publish",
                     {"creation_id": pere, "access_token": jeton},
                     poste=True)["id"]
        print(f"\n     carrousel publie — {mid}")
        return mid
    finally:
        print("\nFermeture du tunnel.")
        proc.kill()
        serveur.shutdown()


def verifier():
    ident = charge_identifiants()
    print("Identifiants presents :")
    print("  Page           :", ident.get("page_nom"), f"({ident.get('page_id')})")
    print("  Instagram      :", ident.get("ig_user_id"))
    print("  Jeton de Page  :", f"{len(ident.get('page_token',''))} caracteres")
    print("  Facebook       :",
          "publication possible" if ident.get("peut_publier_facebook")
          else "lecture seule")
    print("\nTest du tunnel…")
    base, serveur, proc = ouvre_tunnel(RACINE)
    print("  ok :", base)
    proc.kill(); serveur.shutdown()
    print("\nTout est en place.")


SANS_FACEBOOK = False

if __name__ == "__main__":
    SANS_FACEBOOK = "--sans-facebook" in sys.argv
    sys.argv = [a for a in sys.argv if a != "--sans-facebook"]
    if "--verifier" in sys.argv:
        verifier()
    elif "--carrousel" in sys.argv:
        i = sys.argv.index("--carrousel")
        with open(sys.argv[i + 2], encoding="utf-8") as f:
            carrousel(sys.argv[i + 1], f.read().strip())
    elif "--story-video" in sys.argv:
        story_video(sys.argv[sys.argv.index("--story-video") + 1])
    elif "--stories" in sys.argv:
        stories(sys.argv[sys.argv.index("--stories") + 1])
    elif len(sys.argv) >= 3:
        args = [a for a in sys.argv if a not in ("--forcer", "--brouillon")]
        vign = float(args[3]) if len(args) > 3 else None
        with open(args[2], encoding="utf-8") as f:
            leg = f.read().strip()
        if "--brouillon" in sys.argv:
            brouillon(args[1], leg, vignette_s=vign,
                      forcer="--forcer" in sys.argv)
        else:
            publier(args[1], leg, vignette_s=vign,
                    forcer="--forcer" in sys.argv)
    else:
        print(__doc__)
