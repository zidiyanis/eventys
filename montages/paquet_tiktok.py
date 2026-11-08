"""Prepare le dossier « pret a publier » dans Google Drive.

TikTok reste manuel : son API exige un site web verifie, que Yanis n'a pas
encore. Le but est donc que sa manipulation quotidienne dure deux minutes,
depuis son telephone.

Deux contraintes qui dictent la forme :
  - uniquement des .txt : un .md ne s'ouvre pas sur un telephone ;
  - des noms NUMEROTES : sur mobile, l'ordre d'affichage est alphabetique,
    donc la numerotation remplace toute explication.

    python H:/eventys/montages/paquet_tiktok.py <video.mp4> "<accroche>"
"""
import datetime
import os
import shutil
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FP = os.path.join(RACINE, "tools", "bin", "ffprobe.exe")

# Google Drive est monte sur G: — on ecrit dedans pour que le dossier
# arrive seul sur le telephone. Sinon on retombe en local.
BASE = (r"G:\Mon Drive\Eventys" if os.path.isdir(r"G:\Mon Drive")
        else os.path.join(RACINE, "_drive"))
A_PUBLIER = os.path.join(BASE, "A PUBLIER")
ARCHIVE = os.path.join(BASE, "DEJA PUBLIE")

HASHTAGS = ("#locationmobilier #mariage #idf #valdoise "
            "#evenementiel #chaisenapoleon")

GABARIT = """{accroche}

Chaises Napoleon, tables, vaisselle.
Livre et monte en Ile-de-France.

Chaise 3 EUR - Table 10 EUR - Kit vaisselle 2 EUR

C'est pour quelle date ?

{hashtags}
"""


def duree(f):
    r = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", f], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def _archiver_anciens(aujourdhui):
    """Deplace les jours passes dans DEJA PUBLIE.

    Sans ca, « A PUBLIER » accumule les dossiers et on ne sait plus lequel
    est celui du jour — ce qui est precisement ce qu'on veut eviter sur un
    telephone.
    """
    if not os.path.isdir(A_PUBLIER):
        return
    os.makedirs(ARCHIVE, exist_ok=True)
    for nom in os.listdir(A_PUBLIER):
        if nom == aujourdhui:
            continue
        src = os.path.join(A_PUBLIER, nom)
        if os.path.isdir(src):
            dst = os.path.join(ARCHIVE, nom)
            if os.path.exists(dst):
                shutil.rmtree(src, ignore_errors=True)
            else:
                shutil.move(src, dst)


def preparer(video, accroche, quand=None):
    quand = quand or datetime.date.today()
    jour = quand.strftime("%Y-%m-%d")
    _archiver_anciens(jour)

    dossier = os.path.join(A_PUBLIER, jour)
    os.makedirs(dossier, exist_ok=True)

    cible = os.path.join(dossier, "1 - VIDEO TIKTOK.mp4")
    shutil.copy(video, cible)

    with open(os.path.join(dossier, "2 - DESCRIPTION A COPIER.txt"),
              "w", encoding="utf-8") as f:
        f.write(GABARIT.format(accroche=accroche, hashtags=HASHTAGS))

    marche = f"""EVENTYS - A FAIRE LE {quand.strftime('%d/%m/%Y')}
==========================================

INSTAGRAM ET FACEBOOK
---------------------
Deja publies automatiquement. Rien a faire.


TIKTOK - 2 MINUTES
------------------
1. Sur ORDINATEUR, va sur tiktok.com
   (l'application ne sait pas programmer)

2. Bouton "Televerser"
   Depose le fichier "1 - VIDEO TIKTOK.mp4"

3. Ouvre "2 - DESCRIPTION A COPIER.txt"
   Copie tout, colle dans la description

4. Active "Planifier la video"
   Choisis 19h00

5. Clique sur "Planifier"

Duree de la video : {duree(video):.0f} secondes


LES 2 GESTES SUR INSTAGRAM
--------------------------
- Partager le Reel dans ta story
  (depuis l'application, pour avoir la vignette cliquable)

- Epingler une story en "A la une" si elle merite d'y rester
  Tu as 24h, apres elle disparait


Tout est deja fait pour le reste.
"""
    with open(os.path.join(dossier, "3 - A FAIRE.txt"), "w",
              encoding="utf-8") as f:
        f.write(marche)
    return dossier


def preparer_brouillon(video, legende, vignette_s=None, quand=None):
    """Depose la video + sa vraie legende dans « A PUBLIER », sans rien publier.

    Yanis ouvre le dossier sur son telephone, importe la video dans
    Instagram / TikTok, colle la legende et enregistre en brouillon.
    """
    quand = quand or datetime.date.today()
    jour = quand.strftime("%Y-%m-%d")
    _archiver_anciens(jour)

    dossier = os.path.join(A_PUBLIER, jour)
    os.makedirs(dossier, exist_ok=True)

    nom = os.path.basename(video)
    if "STORY" in nom.upper():
        nom = "VIDEO"
    shutil.copy(video, os.path.join(dossier, "1 - VIDEO.mp4"))

    with open(os.path.join(dossier, "2 - LEGENDE A COPIER.txt"),
              "w", encoding="utf-8") as f:
        f.write(legende.strip() + "\n")

    vign = (f"\nVignette : choisis l'image a {vignette_s:g} s dans "
            f"\"Modifier la couverture\".\n" if vignette_s is not None else "")
    marche = f"""EVENTYS - BROUILLON DU {quand.strftime('%d/%m/%Y')}
==========================================
Rien n'est publie. A toi de decider quand.

INSTAGRAM
---------
1. + puis Reel, choisis "1 - VIDEO.mp4"
2. Suivant, colle "2 - LEGENDE A COPIER.txt"
3. Fleche retour : "Enregistrer le brouillon"{vign}

TIKTOK
------
1. + puis Importer, choisis "1 - VIDEO.mp4"
2. Suivant, colle la legende
3. En bas a gauche : "Brouillons"
   (les brouillons restent sur ce telephone)

Duree de la video : {duree(video):.0f} secondes
"""
    with open(os.path.join(dossier, "3 - A FAIRE.txt"), "w",
              encoding="utf-8") as f:
        f.write(marche)
    return dossier


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    d = preparer(sys.argv[1], sys.argv[2])
    print(d)
    for f in sorted(os.listdir(d)):
        print("  ", f)
