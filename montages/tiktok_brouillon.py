"""Envoie une video dans la boite de reception TikTok, en BROUILLON.

Rien n'est publie : la video arrive dans l'application TikTok, Yanis la
termine (legende, vignette) et publie lui-meme. Scope utilise : video.upload.

    python montages/tiktok_brouillon.py --connexion      (une seule fois)
    python montages/tiktok_brouillon.py <video.mp4>      (envoie en brouillon)

La connexion ouvre TikTok dans le navigateur ; la page
https://eventysparis.fr/callback affiche un code a coller dans le terminal.
Les jetons vont dans meta/tiktok_jetons.json (secret, jamais affiche).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)
sys.path.insert(0, ICI)
import cles  # noqa: E402

JETONS = os.path.join(RACINE, "meta", "tiktok_jetons.json")
REDIRECT = "https://eventysparis.fr/callback"
SCOPES = "user.info.basic,video.upload"
API = "https://open.tiktokapis.com/v2"
MORCEAU = 10 * 1024 * 1024


def _requete(url, donnees=None, entetes=None, methode=None, json_corps=False):
    entetes = dict(entetes or {})
    if donnees is not None and not isinstance(donnees, bytes):
        if json_corps:
            donnees = json.dumps(donnees).encode()
            entetes["Content-Type"] = "application/json; charset=UTF-8"
        else:
            donnees = urllib.parse.urlencode(donnees).encode()
            entetes["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=donnees, headers=entetes,
                                 method=methode)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            txt = r.read().decode()
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        corps = e.read().decode()
        raise SystemExit(f"\nTikTok refuse ({e.code}) : {corps[:400]}")


def _sauver(rep):
    if "access_token" not in rep:
        raise SystemExit(f"Reponse inattendue : {list(rep)} "
                         f"{rep.get('error_description', '')}")
    rep["expire_le"] = int(time.time()) + int(rep.get("expires_in", 0))
    with open(JETONS, "w", encoding="utf-8") as f:
        json.dump(rep, f)


def connexion():
    cle = cles.get("TIKTOK_CLIENT_KEY")
    secret = cles.get("TIKTOK_CLIENT_SECRET")
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode({
        "client_key": cle, "scope": SCOPES, "response_type": "code",
        "redirect_uri": REDIRECT, "state": "eventys"})
    print("Ouverture de TikTok. Connecte-toi avec le compte Eventys, autorise,")
    print("puis copie le code affiche sur la page eventysparis.fr/callback.\n")
    webbrowser.open(url)
    code = urllib.parse.unquote(input("Code : ").strip())
    rep = _requete(f"{API}/oauth/token/", {
        "client_key": cle, "client_secret": secret, "code": code,
        "grant_type": "authorization_code", "redirect_uri": REDIRECT})
    _sauver(rep)
    print("Connecte. Jetons enregistres (meta/tiktok_jetons.json).")


def jeton():
    if not os.path.exists(JETONS):
        raise SystemExit("Pas connecte : lance d'abord --connexion.")
    with open(JETONS, encoding="utf-8") as f:
        j = json.load(f)
    if j["expire_le"] - time.time() < 300:
        rep = _requete(f"{API}/oauth/token/", {
            "client_key": cles.get("TIKTOK_CLIENT_KEY"),
            "client_secret": cles.get("TIKTOK_CLIENT_SECRET"),
            "grant_type": "refresh_token",
            "refresh_token": j["refresh_token"]})
        _sauver(rep)
        j = rep
    return j["access_token"]


def brouillon(video):
    video = os.path.abspath(video)
    taille = os.path.getsize(video)
    morceau = taille if taille <= MORCEAU else MORCEAU
    nb = max(1, taille // morceau)  # le dernier morceau absorbe le reste
    acces = jeton()
    ent = {"Authorization": f"Bearer {acces}"}

    print(f"Video : {os.path.basename(video)} ({taille/1048576:.1f} Mo)")
    rep = _requete(f"{API}/post/publish/inbox/video/init/", {
        "source_info": {"source": "FILE_UPLOAD", "video_size": taille,
                        "chunk_size": morceau, "total_chunk_count": nb}},
        ent, json_corps=True)
    if rep.get("error", {}).get("code", "ok") != "ok":
        raise SystemExit(f"Init refusee : {rep['error']}")
    url, pid = rep["data"]["upload_url"], rep["data"]["publish_id"]

    with open(video, "rb") as f:
        for i in range(nb):
            debut = i * morceau
            fin = taille - 1 if i == nb - 1 else debut + morceau - 1
            f.seek(debut)
            bloc = f.read(fin - debut + 1)
            _requete(url, bloc, {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes {debut}-{fin}/{taille}"},
                methode="PUT")
            print(f"  morceau {i+1}/{nb} envoye")

    for _ in range(120):  # 10 min : un fichier de 27 Mo a depasse 2 min 30
        st = _requete(f"{API}/post/publish/status/fetch/",
                      {"publish_id": pid}, ent, json_corps=True)
        etat = st.get("data", {}).get("status", "?")
        print("  statut :", etat)
        if etat in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"):
            print("\nBrouillon livre : ouvre TikTok, tu le trouves dans la "
                  "notification / boite de reception.")
            return
        if etat == "FAILED":
            raise SystemExit(f"Echec : {st['data'].get('fail_reason')}")
        time.sleep(5)
    raise SystemExit("Delai depasse : verifie dans TikTok.")


SITE = "eventysparis.fr"
LIEU = "Île-de-France"
HASHTAGS = ("#locationmobilier #chaisenapoleon #mariage #evenementiel "
            "#idf #valdoise #paris")


def legende_tiktok(texte):
    """Legende Instagram + lieu + site, sans doublon.

    L'API TikTok (inbox) n'accepte NI legende NI lieu : ils se saisissent
    dans l'application. On prepare donc le texte et on le met au
    presse-papiers / dans Drive pour qu'il n'y ait qu'a coller.
    """
    t = texte.strip()
    if SITE not in t:
        t += (f"\n\n🪑 Location de mobilier événementiel\n📍 {LIEU}\n"
              f"🌐 {SITE}\n💬 Écris-nous en message privé pour un devis")
    # Hashtags en dernier, comme sur Instagram. Si la legende en porte
    # deja, on ne les double pas.
    if "#" not in t:
        t += "\n\n" + HASHTAGS
    return t


REGISTRE_DISCORD = os.path.join(RACINE, "meta", "discord_messages.json")


def _discord(url, methode, corps=None):
    req = urllib.request.Request(
        url, data=json.dumps(corps).encode() if corps is not None else None,
        headers={"Content-Type": "application/json",
                 "User-Agent": "EventysBot/1.0"}, method=methode)
    txt = urllib.request.urlopen(req, timeout=30).read().decode()
    return json.loads(txt) if txt else {}


def extraire_couverture(video, seconde):
    """Image de la video a la seconde choisie -> jpg (pour la joindre)."""
    import subprocess
    import tempfile
    sortie = os.path.join(tempfile.gettempdir(), "eventys_couverture.jpg")
    ff = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
    subprocess.run([ff, "-y", "-v", "error", "-ss", str(seconde), "-i", video,
                    "-frames:v", "1", "-q:v", "2", sortie], check=True)
    return sortie


def _discord_avec_fichier(url, contenu, chemin):
    """POST multipart : un message + une image jointe."""
    import uuid
    lim = uuid.uuid4().hex
    with open(chemin, "rb") as f:
        donnees = f.read()
    crlf = "\r\n"
    entete_json = crlf.join([
        f"--{lim}",
        'Content-Disposition: form-data; name="payload_json"',
        "Content-Type: application/json", "",
        json.dumps({"content": contenu}), ""])
    entete_fichier = crlf.join([
        f"--{lim}",
        'Content-Disposition: form-data; name="files[0]"; '
        'filename="couverture.jpg"',
        "Content-Type: image/jpeg", "", ""])
    corps = (entete_json + entete_fichier).encode("utf-8") + donnees \
        + (crlf + f"--{lim}--" + crlf).encode()
    req = urllib.request.Request(
        url, data=corps, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={lim}",
                 "User-Agent": "EventysBot/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode())


def titre_video(video, legende):
    """Titre lisible : la 1re ligne de la legende, sinon le nom du fichier."""
    for ligne in legende.splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#"):
            return ligne[:90]
    return os.path.splitext(os.path.basename(video))[0].replace("_", " ")


def envoyer_discord(video, legende, vignette_s=None):
    """Poste dans Discord : 1 message d'en-tete (quelle video, quel jour) puis
    1 message avec la legende SEULE, a copier d'un appui long.

    Jamais deux fois le meme message : une video donnee, un jour donne, a
    une seule paire de messages. Meme texte -> on ne renvoie rien ; texte
    modifie -> on SUPPRIME l'ancienne paire avant de poster la nouvelle.
    """
    import datetime
    import hashlib
    url = cles.get("DISCORD_WEBHOOK_URL", obligatoire=False)
    if not url:
        print("Discord : pas de webhook dans cles.env, ignore.")
        return
    jour = datetime.date.today()
    cle = f"{jour:%Y-%m-%d} {os.path.basename(video)}"
    empreinte = hashlib.sha256(legende.encode()).hexdigest()

    reg = {}
    if os.path.exists(REGISTRE_DISCORD):
        with open(REGISTRE_DISCORD, encoding="utf-8") as f:
            reg = json.load(f)
    ancien = reg.get(cle)
    if ancien and ancien["empreinte"] == empreinte:
        print("Discord : ce message est deja la, rien renvoye.")
        return
    if ancien:
        for mid in ancien["ids"]:
            try:
                _discord(f"{url}/messages/{mid}", "DELETE")
            except urllib.error.HTTPError:
                pass  # deja supprime a la main
        print("Discord : ancien message supprime (mise a jour).")

    entete = (f"📹 **{titre_video(video, legende)}**\n"
              f"🗓️ {jour:%d/%m/%Y}  ·  🎞️ {os.path.basename(video)}\n"
              + (f"🖼️ Couverture : enregistre l'image ci-dessous, puis dans "
                 f"TikTok « Modifier la couverture » (ou glisse jusqu'à "
                 f"{vignette_s:g} s)\n" if vignette_s is not None else "")
              + "👇 La légende à copier est juste en dessous")
    ids = []
    if vignette_s is not None:
        img = extraire_couverture(video, vignette_s)
        ids.append(_discord_avec_fichier(url + "?wait=true", entete, img)["id"])
        suite = (legende[:1990],)
    else:
        suite = (entete, legende[:1990])
    for contenu in suite:
        ids.append(_discord(url + "?wait=true", "POST",
                            {"content": contenu})["id"])
    reg[cle] = {"empreinte": empreinte, "ids": ids}
    with open(REGISTRE_DISCORD, "w", encoding="utf-8") as f:
        json.dump(reg, f)
    print("Legende envoyee sur Discord (titre + date + texte).")


def envoyer_avec_legende(video, texte, vignette_s=None):
    """Envoie en brouillon, depose la legende dans Drive, copie-la."""
    leg = legende_tiktok(texte)
    try:
        brouillon(video)
    except SystemExit as e:
        # Un delai d'attente ne veut pas dire que l'envoi a echoue : TikTok
        # traite parfois le fichier plus de 2 minutes. La legende part quand
        # meme, pour que Yanis ait tout sous la main.
        print(f"TikTok : {e}")
    try:
        import datetime
        import paquet_tiktok
        dossier = os.path.join(paquet_tiktok.A_PUBLIER,
                               datetime.date.today().strftime("%Y-%m-%d"))
        os.makedirs(dossier, exist_ok=True)
        with open(os.path.join(dossier, "TIKTOK - LEGENDE A COLLER.txt"),
                  "w", encoding="utf-8") as f:
            f.write(leg + "\n")
        envoyer_discord(video, leg, vignette_s)
        import subprocess
        subprocess.run(["clip"], input=leg.encode("utf-16"), check=False)
        print("Legende copiee + deposee dans Drive (TIKTOK - LEGENDE A COLLER).")
    except Exception as e:  # le brouillon est deja parti : ne rien casser
        print(f"(legende non deposee : {e})")


if __name__ == "__main__":
    if "--connexion" in sys.argv:
        connexion()
    elif len(sys.argv) >= 2:
        brouillon(sys.argv[1])
    else:
        print(__doc__)
