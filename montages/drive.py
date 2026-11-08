"""Range le Google Drive d'Eventys et y depose le contenu du jour.

Contraintes imposees par l'usage reel : Yanis consulte ce Drive depuis son
TELEPHONE. Donc jamais de .md (ne s'ouvre pas), des noms numerotes (le tri
mobile est alphabetique), et un seul dossier dans « A PUBLIER » pour qu'il
n'ait jamais a chercher lequel est le bon.

Arborescence :

    Eventys/
      A PUBLIER/<date>/        le jour en cours, et lui seul
        1 - VIDEO TIKTOK.mp4
        2 - DESCRIPTION A COPIER.txt
        3 - A FAIRE.txt
        4 - STORIES/           les stories deja publiees, pour archive
        5 - CARROUSEL/         les images du carrousel, s'il y en a un
      DEJA PUBLIE/<date>/      les jours passes, memes dossiers
      ARCHIVES REELS/          les anciens montages qui trainaient
"""
import datetime
import os
import shutil
import subprocess

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FP = os.path.join(RACINE, "tools", "bin", "ffprobe.exe")

BASE = (r"G:\Mon Drive\Eventys" if os.path.isdir(r"G:\Mon Drive")
        else os.path.join(RACINE, "_drive"))
A_PUBLIER = os.path.join(BASE, "A PUBLIER")
ARCHIVE = os.path.join(BASE, "DEJA PUBLIE")
ANCIENS = os.path.join(BASE, "ARCHIVES REELS")

HASHTAGS = ("#locationmobilier #mariage #idf #valdoise "
            "#evenementiel #chaisenapoleon")


def duree(f):
    r = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", f], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def ranger_tout():
    """Met de l'ordre dans l'ensemble du Drive Eventys.

    Trois endroits, et trois seulement :
      A PUBLIER     le jour en cours, et lui seul
      DEJA PUBLIE   l'historique, un dossier par jour
      ARCHIVES      tout ce qui date d'avant l'automatisation

    Les anciens montages trainaient en vrac a la racine du Drive. Ils sont
    regroupes par mois, parce qu'une liste de 40 fichiers sur un telephone
    n'est pas consultable.
    """
    import re
    os.makedirs(ARCHIVE, exist_ok=True)
    anciens = os.path.join(BASE, "ARCHIVES")
    os.makedirs(anciens, exist_ok=True)

    # 1. l'ancien dossier ARCHIVES REELS devient ARCHIVES/2026-10 et avant
    vieux = os.path.join(BASE, "ARCHIVES REELS")
    deplaces = 0
    if os.path.isdir(vieux):
        for f in os.listdir(vieux):
            m = re.match(r"(\d{4})-(\d{2})", f)
            mois = f"{m.group(1)}-{m.group(2)}" if m else "avant automatisation"
            cible = os.path.join(anciens, mois)
            os.makedirs(cible, exist_ok=True)
            src, dst = os.path.join(vieux, f), os.path.join(cible, f)
            if not os.path.exists(dst):
                shutil.move(src, dst)
                deplaces += 1
        try:
            os.rmdir(vieux)
        except OSError:
            pass
    return deplaces


def ranger_ancien_dossier():
    """Deplace l'ancien dossier « Eventys - Reels » dans les archives.

    Il trainait a la racine du Drive avec des montages de plusieurs
    semaines melanges — c'est exactement ce que Yanis veut voir disparaitre.
    """
    vieux = os.path.join(os.path.dirname(BASE), "Eventys - Reels")
    if not os.path.isdir(vieux):
        return None
    os.makedirs(ANCIENS, exist_ok=True)
    for f in os.listdir(vieux):
        src, dst = os.path.join(vieux, f), os.path.join(ANCIENS, f)
        if not os.path.exists(dst):
            shutil.move(src, dst)
    try:
        os.rmdir(vieux)
    except OSError:
        pass
    return ANCIENS


def archiver_jours_passes(aujourdhui):
    if not os.path.isdir(A_PUBLIER):
        return
    os.makedirs(ARCHIVE, exist_ok=True)
    for nom in os.listdir(A_PUBLIER):
        if nom == aujourdhui:
            continue
        src = os.path.join(A_PUBLIER, nom)
        if not os.path.isdir(src):
            continue
        dst = os.path.join(ARCHIVE, nom)
        if os.path.exists(dst):
            shutil.rmtree(src, ignore_errors=True)
        else:
            shutil.move(src, dst)


def deposer(video=None, accroche="", stories=None, carrousel=None,
            quand=None, theme="", legende=None):
    """Depose tout le contenu du jour dans un dossier unique et date."""
    quand = quand or datetime.date.today()
    jour = quand.strftime("%Y-%m-%d")
    archiver_jours_passes(jour)
    dossier = os.path.join(A_PUBLIER, jour)
    os.makedirs(dossier, exist_ok=True)

    # La legende doit etre deposee MEME les jours sans video : un carrousel
    # a aussi besoin de son texte, et Yanis le cherchait dans le dossier.
    if legende:
        with open(os.path.join(dossier, "2 - DESCRIPTION A COPIER.txt"),
                  "w", encoding="utf-8") as f:
            f.write(legende.strip() + "\n")

    lignes_tiktok = []
    if video:
        shutil.copy(video, os.path.join(dossier, "1 - VIDEO TIKTOK.mp4"))
        # Le gabarit ne sert que SI aucune legende n'a ete ecrite pour la
        # video du jour. Il ecrasait la vraie legende le 26 octobre — et
        # comme il etait sans accents (« Napoleon », « Ile-de-France »),
        # c'est cette version-la qui serait partie sur TikTok.
        if not legende:
            with open(os.path.join(dossier, "2 - DESCRIPTION A COPIER.txt"),
                      "w", encoding="utf-8") as f:
                f.write(f"{accroche}\n\n"
                        "Chaises Napoléon, tables, vaisselle.\n"
                        "Livré et monté en Île-de-France.\n\n"
                        "Chaise 3 € · Table 10 € · Kit vaisselle 2 €\n\n"
                        "C'est pour quelle date ?\n\n"
                        f"{HASHTAGS}\n")
        lignes_tiktok = [
            "TIKTOK - 2 MINUTES",
            "------------------",
            "1. Sur ORDINATEUR, va sur tiktok.com",
            "   (l'application ne sait pas programmer)",
            "",
            '2. Bouton "Televerser"',
            '   Depose "1 - VIDEO TIKTOK.mp4"',
            "",
            '3. Ouvre "2 - DESCRIPTION A COPIER.txt"',
            "   Copie tout, colle dans la description",
            "",
            '4. Active "Planifier la video", choisis 19h00',
            "",
            '5. Clique sur "Planifier"',
            "",
            f"Duree : {duree(video):.0f} secondes",
        ]

    if stories:
        d = os.path.join(dossier, "4 - STORIES")
        os.makedirs(d, exist_ok=True)
        for i, s in enumerate(sorted(stories), 1):
            shutil.copy(s, os.path.join(d, f"story {i}{os.path.splitext(s)[1]}"))

    if carrousel:
        d = os.path.join(dossier, "5 - CARROUSEL")
        os.makedirs(d, exist_ok=True)
        for i, c in enumerate(carrousel, 1):
            shutil.copy(c, os.path.join(d, f"image {i}{os.path.splitext(c)[1]}"))

    bloc = "\n".join(lignes_tiktok) if lignes_tiktok else \
        "Pas de video aujourd'hui : c'est un jour carrousel.\nRien a faire sur TikTok."

    texte = f"""EVENTYS - A FAIRE LE {quand.strftime('%d/%m/%Y')}
==========================================

THEME DU JOUR : {theme or '(a definir)'}


INSTAGRAM ET FACEBOOK
---------------------
Publies automatiquement a 17h. Rien a faire.


{bloc}


LES 2 GESTES SUR INSTAGRAM
--------------------------
- Partager la publication dans ta story
  (depuis l'application, pour la vignette cliquable)

- Epingler une story en "A la une" si elle merite d'y rester
  Tu as 24h, apres elle disparait


Le reste est deja fait.
"""
    with open(os.path.join(dossier, "3 - A FAIRE.txt"), "w",
              encoding="utf-8") as f:
        f.write(texte)
    return dossier
