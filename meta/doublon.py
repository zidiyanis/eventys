"""Detecte si une video a DEJA ete publiee — avant de la republier.

POURQUOI CE FICHIER EXISTE. Le meme Reel (CALCUL_50.mp4) est parti trois
jours de suite, les 26, 27 et 28 octobre 2026. La cause est bete : le
dossier `_a_publier_aujourdhui` n'etait jamais vide apres une publication,
et `publier_17h.py` publie simplement ce qu'il y trouve. Personne ne
verifiait, et l'API Instagram ne sait pas supprimer : les copies restent en
ligne jusqu'a ce que Yanis les efface a la main.

Le cout est mesurable dans les statistiques :
    26/10  17 162 vues   194 J'aime   228 enregistrements
    27/10   2 631 vues    27 J'aime    24 enregistrements  <- meme video
Soit six fois moins. L'algorithme reconnait un contenu deja vu et cesse de
le montrer ; et l'abonne qui l'a deja vu passe.

TROIS NIVEAUX DE DETECTION, du plus sur au plus fin :

1. EMPREINTE DU FICHIER (sha256). Repond a « est-ce exactement ce fichier ».
   C'est le cas du 27 et du 28 octobre. Infaillible, mais aveugle a un
   simple reencodage.

2. EMPREINTE D'IMAGE (dHash de 16 images). Repond a « est-ce la meme video,
   meme reexportee ». On prend 16 images reparties sur la duree, on les
   reduit a 9x8 en niveaux de gris, et on code chaque image sur 64 bits en
   comparant chaque pixel a son voisin de droite. Insensible au debit, a la
   compression et a un leger recadrage ; sensible au contenu.

3. IMAGES COMMUNES. Repond a la demande de Yanis : « il faut utiliser
   d'autres rushes ». On compte combien d'images de la nouvelle video
   trouvent une jumelle dans une video deja publiee, quel que soit leur
   ordre. Au-dela de 35 %, on recycle, meme si le montage est different.
   C'est un avertissement, pas un refus : la boucle d'ouverture sur le box
   est volontairement toujours la meme.

La legende est verifiee aussi : une accroche identique est un doublon aux
yeux de l'abonne, meme si les images changent.

Le registre `meta/publie.json` garde une ligne par publication. Il est
complete depuis l'API au besoin : ce qui est en ligne fait foi, pas ce que
nos fichiers croient.
"""
import hashlib
import json
import os
import subprocess

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
FP = os.path.join(RACINE, "tools", "bin", "ffprobe.exe")
REGISTRE = os.path.join(ICI, "publie.json")

N_IMAGES = 16          # images echantillonnees par video
BITS_IMAGE = 8         # deux images se ressemblent sous 8 bits d'ecart sur 64
# Seuils cales sur des mesures reelles du 28/10, en comparant nos montages
# aux copies telechargees depuis Instagram :
#   CALCUL_50 contre sa propre publication ............ 75 %
#   COULISSES contre sa propre publication ............ 100 %
#   CALCUL_50 contre le Reel du 20/10 (meme box) ...... 25 %
#   NOEL_12 contre tout l'historique .................. 0 %
# Le 75 % montre ce que coute le reencodage d'Instagram : une video
# identique peut descendre sous 80 %. Un vrai inedit plafonne a 25 %, et
# seulement a cause du plan d'ouverture sur le box, commun a toutes nos
# videos. L'ecart entre 25 et 75 est large : on coupe au milieu.
SEUIL_MEME = 0.55      # au-dela => meme video, refus
SEUIL_RECYCLE = 0.35   # au-dela => on repuise dans les memes rushes, alerte


# --------------------------------------------------------- empreintes

def sha(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def duree(chemin):
    r = subprocess.run([FP, "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", chemin],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def _dhash(chemin, t):
    """64 bits decrivant l'image a l'instant t.

    9x8 pixels gris : on compare chaque pixel a son voisin de droite, ce qui
    donne 8 bits par ligne. On code des PENTES, pas des luminosites : un
    changement global de luminosite ou de contraste ne change rien.
    """
    r = subprocess.run([FF, "-v", "error", "-ss", f"{t:.2f}", "-i", chemin,
                        "-frames:v", "1", "-vf",
                        "scale=9:8:flags=area,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    px = r.stdout
    if len(px) < 72:
        return None
    v = 0
    for y in range(8):
        for x in range(8):
            v = (v << 1) | (1 if px[y * 9 + x] > px[y * 9 + x + 1] else 0)
    return v


def empreinte(chemin):
    """Liste de N_IMAGES entiers 64 bits, repartis sur la duree."""
    d = duree(chemin)
    if d <= 0:
        return []
    out = []
    for i in range(N_IMAGES):
        # On evite les deux extremites : la premiere et la derniere image
        # sont souvent noires ou en fondu.
        t = d * (0.03 + 0.94 * i / max(N_IMAGES - 1, 1))
        h = _dhash(chemin, t)
        if h is not None:
            out.append(h)
    return out


def _ecart(a, b):
    return bin(a ^ b).count("1")


def part_commune(ea, eb):
    """Part des images de `ea` qui trouvent une jumelle dans `eb`."""
    if not ea or not eb:
        return 0.0
    n = sum(1 for a in ea if any(_ecart(a, b) <= BITS_IMAGE for b in eb))
    return n / len(ea)


# ----------------------------------------------------------- registre

def lire():
    if not os.path.exists(REGISTRE):
        return []
    with open(REGISTRE, encoding="utf-8") as f:
        return json.load(f)


def ecrire(lignes):
    with open(REGISTRE, "w", encoding="utf-8") as f:
        json.dump(lignes, f, ensure_ascii=False, indent=1)


def enregistrer(video, legende, media_id=None, permalink=None, quoi="REELS"):
    """A appeler APRES une publication reussie, jamais avant."""
    import datetime
    lignes = lire()
    lignes.insert(0, {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "fichier": os.path.basename(video),
        "quoi": quoi,
        "sha": sha(video),
        "empreinte": [f"{h:016x}" for h in empreinte(video)],
        "accroche": (legende or "").strip().split("\n")[0][:90],
        "media_id": media_id,
        "permalink": permalink,
    })
    ecrire(lignes)
    return lignes[0]


def _emp(ligne):
    return [int(x, 16) for x in ligne.get("empreinte") or []]


# ------------------------------------------------------------ controle

def controler(video, legende="", quoi="REELS"):
    """Rend (refus, avertissements, mesures).

    `refus` non vide = on ne publie pas.
    """
    import datetime
    refus, avert, mesures = [], [], []
    lignes = lire()
    if not lignes:
        avert.append("Registre vide : aucune comparaison possible. "
                     "Lance `python meta/doublon.py --rattraper`.")
        return refus, avert, mesures

    s = sha(video)
    for l in lignes:
        if l.get("sha") == s:
            refus.append(f"FICHIER DEJA PUBLIE le {l['date']} "
                         f"({l.get('permalink') or l.get('media_id')}). "
                         f"C'est exactement le meme fichier.")
    mesures.append(f"sha256 {s[:12]} — {'DEJA VU' if refus else 'inedit'}")

    acc = (legende or "").strip().split("\n")[0][:90]
    if acc:
        for l in lignes:
            if l.get("accroche") and l["accroche"] == acc:
                refus.append(f"ACCROCHE IDENTIQUE a celle du {l['date']} : "
                             f"« {acc} »")

    e = empreinte(video)
    mesures.append(f"empreinte sur {len(e)} images")
    if e:
        pires = []
        for l in lignes:
            eb = _emp(l)
            if not eb:
                continue
            p = part_commune(e, eb)
            if p > 0:
                pires.append((p, l))
        pires.sort(reverse=True, key=lambda x: x[0])
        for p, l in pires[:3]:
            mesures.append(f"{p * 100:4.0f} % d'images communes avec "
                           f"{l['fichier']} ({l['date']})")
        if pires:
            p, l = pires[0]
            if p >= SEUIL_MEME:
                refus.append(f"MEME VIDEO que {l['fichier']} publiee le "
                             f"{l['date']} : {p * 100:.0f} % des images sont "
                             f"identiques, meme si le fichier differe.")
            elif p >= SEUIL_RECYCLE:
                avert.append(f"{p * 100:.0f} % des images viennent des memes "
                             f"rushes que {l['fichier']} ({l['date']}). "
                             f"Change de matiere : c'est la demande de Yanis.")

    # Deux Reels le meme jour : jamais voulu, et le second etouffe le premier.
    today = datetime.date.today().strftime("%Y-%m-%d")
    meme_jour = [l for l in lignes
                 if l.get("quoi") == quoi and l["date"].startswith(today)]
    if meme_jour and quoi == "REELS":
        refus.append(f"UN REEL EST DEJA PARTI AUJOURD'HUI "
                     f"({meme_jour[0]['fichier']} a "
                     f"{meme_jour[0]['date'][-5:]}).")
    return refus, avert, mesures


# ---------------------------------------------------------- rattrapage

def rattraper(depuis="2026-10-01"):
    """Remplit le registre depuis CE QUI EST EN LIGNE.

    L'historique est anterieur au registre : sans ce rattrapage, la premiere
    publication apres l'installation ne serait comparee a rien.

    On ne se contente pas des legendes : pour chaque Reel recent, on
    telecharge la copie publiee par Instagram et on calcule son empreinte
    d'image. C'est volontaire — nos fichiers locaux peuvent mentir (un
    montage renomme, reexporte, un dossier du jour pas vide), la publication
    en ligne ne mentit pas. Le sha local est ajoute en plus quand on
    reconnait le fichier, pour attraper le cas du fichier identique.
    """
    import tempfile
    import urllib.parse
    import urllib.request
    ident = json.load(open(os.path.join(ICI, "identifiants.json"),
                           encoding="utf-8"))
    u = ("https://graph.facebook.com/v21.0/%s/media?" % ident["ig_user_id"]
         + urllib.parse.urlencode({
             "limit": 50, "access_token": ident["page_token"],
             "fields": "id,caption,timestamp,permalink,media_product_type,"
                       "media_url"}))
    with urllib.request.urlopen(u, timeout=60) as r:
        data = json.load(r)["data"]

    # Tous les mp4 qu'on a sous la main, par empreinte : sert a retrouver
    # QUEL montage local correspond a une publication en ligne.
    locaux = {}
    for d in (os.path.join(RACINE, "_a_publier_aujourdhui"),
              os.path.join(RACINE, "montages")):
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.lower().endswith(".mp4"):
                locaux[os.path.join(d, f)] = None

    lignes = []
    for m in data:
        acc = (m.get("caption") or "").strip().split("\n")[0][:90]
        l = {
            "date": m["timestamp"][:10] + " " + m["timestamp"][11:16],
            "fichier": "(non retrouve sur le disque)",
            "quoi": m.get("media_product_type"),
            "sha": None, "empreinte": [], "accroche": acc,
            "media_id": m["id"], "permalink": m.get("permalink"),
        }
        lignes.append(l)
        if l["date"] < depuis or not m.get("media_url"):
            continue
        tmp = os.path.join(tempfile.gettempdir(), f"ig_{m['id']}.mp4")
        try:
            if not os.path.exists(tmp):
                urllib.request.urlretrieve(m["media_url"], tmp)
            l["empreinte"] = [f"{h:016x}" for h in empreinte(tmp)]
        except Exception as e:
            print(f"  {l['date']} : copie en ligne illisible ({e})")
            continue
        finally:
            pass
        # Quel fichier local est-ce ? On compare les empreintes.
        eb = _emp(l)
        best, bp = None, 0.0
        for chemin in locaux:
            if locaux[chemin] is None:
                locaux[chemin] = empreinte(chemin)
            p = part_commune(locaux[chemin], eb)
            if p > bp:
                best, bp = chemin, p
        if best and bp >= SEUIL_MEME:
            l["fichier"] = os.path.basename(best)
            l["sha"] = sha(best)
            print(f"  {l['date']} = {l['fichier']} ({bp*100:.0f} %)")
        else:
            print(f"  {l['date']} : empreinte relevee en ligne, "
                  f"fichier local inconnu")
        try:
            os.remove(tmp)
        except OSError:
            pass
    ecrire(lignes)
    print(f"{len(lignes)} publications enregistrees dans {REGISTRE}")
    return lignes


if __name__ == "__main__":
    import sys
    if "--rattraper" in sys.argv:
        rattraper()
    elif len(sys.argv) > 1:
        v = sys.argv[1]
        leg = sys.argv[2] if len(sys.argv) > 2 else ""
        if leg and os.path.exists(leg):
            leg = open(leg, encoding="utf-8").read()
        r, a, m = controler(v, leg)
        for x in m:
            print("   ", x)
        for x in a:
            print("  ! ", x)
        for x in r:
            print("  REFUS :", x)
        print("\n=> " + ("PUBLICATION REFUSEE" if r
                         else "inedit, on peut publier"))
        sys.exit(1 if r else 0)
    else:
        for l in lire():
            print(l["date"], l.get("quoi"), l["fichier"], "|", l["accroche"])
