"""Publication automatique de 17h — lancee par le Planificateur Windows.

    python H:/eventys/publier_17h.py

Ce script ne CREE rien : il publie ce qui attend dans le dossier du jour.
La production (script, voix, montage) se fait le matin, en session, avec les
agents. Cette separation est voulue : si le montage echoue le matin, rien ne
part a 17h, et on le voit avant plutot qu'apres.

Il ecrit son compte rendu dans journal/<date>.txt, pour qu'on puisse savoir
le lendemain ce qui s'est passe meme si personne ne regardait.
"""
import datetime
import os
import sys
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "meta"))
sys.path.insert(0, os.path.join(ICI, "montages"))

JOURNAL = os.path.join(ICI, "journal")
PRET = os.path.join(ICI, "_a_publier_aujourdhui")
ARCHIVE = os.path.join(ICI, "journal", "deja_publie")


def noter(lignes, texte):
    print(texte, flush=True)
    lignes.append(texte)


def vider(*chemins):
    """Sort du dossier du jour ce qui vient d'etre publie.

    LA CAUSE DU DOUBLON DES 26, 27 ET 28 OCTOBRE. Ce script publie ce qu'il
    trouve dans `_a_publier_aujourdhui` ; comme rien n'en sortait jamais, la
    meme video repartait chaque soir. Les vues sont tombees de 17 162 a
    2 631 pour le deuxieme passage.

    On DEPLACE, on ne supprime pas : le fichier reste consultable dans
    `journal/deja_publie/<date>/`. Et si le deplacement echoue, le registre
    des doublons (meta/doublon.py) refusera quand meme la republication —
    deux protections independantes pour la meme erreur.
    """
    import shutil
    dest = os.path.join(ARCHIVE, datetime.date.today().strftime("%Y-%m-%d"))
    os.makedirs(dest, exist_ok=True)
    faits = []
    for c in chemins:
        if c and os.path.exists(c):
            try:
                shutil.move(c, os.path.join(dest, os.path.basename(c)))
                faits.append(os.path.basename(c))
            except OSError as e:
                return f"ATTENTION : {os.path.basename(c)} n'a pas pu etre " \
                       f"archive ({e}) — il repartirait demain."
    return f"Archive dans journal/deja_publie/ : {', '.join(faits)}"


def main():
    lignes = []
    debut = datetime.datetime.now()
    noter(lignes, f"=== {debut:%Y-%m-%d %H:%M} — publication automatique ===")

    if not os.path.isdir(PRET):
        noter(lignes, "Rien a publier : le dossier du jour n'existe pas.")
        noter(lignes, "La production du matin n'a probablement pas tourne.")
        return 1, lignes

    video = next((os.path.join(PRET, f) for f in sorted(os.listdir(PRET))
                  if f.lower().endswith(".mp4")), None)
    legende = os.path.join(PRET, "legende.txt")
    dossier_stories = os.path.join(PRET, "stories")

    import publier as P

    if video and os.path.exists(legende):
        with open(legende, encoding="utf-8") as f:
            texte = f.read().strip()
        # La vignette est lue dans un fichier a part : sans elle, Instagram
        # prend la premiere image, et notre ouverture sur le rideau du box
        # donne une vignette grise au milieu d'une grille de tables dressees.
        fv = os.path.join(PRET, "vignette.txt")
        vign = None
        if os.path.exists(fv):
            try:
                vign = float(open(fv, encoding="utf-8").read().strip())
            except ValueError:
                vign = None
        noter(lignes, f"Publication du Reel : {os.path.basename(video)}"
                      f" (vignette a {vign}s)" if vign else
                      f"Publication du Reel : {os.path.basename(video)}")
        P.publier(video, texte, vignette_s=vign)
        noter(lignes, "  Reel publie sur Instagram et Facebook.")
        # TikTok : brouillon dans la boite de reception, Yanis n'a plus
        # qu'a coller la legende et publier. Un echec ici ne doit jamais
        # faire croire que Instagram a rate : le Reel est deja en ligne.
        try:
            sys.path.insert(0, os.path.join(ICI, "montages"))
            import tiktok_brouillon as TT
            TT.envoyer_avec_legende(video, texte, vign)
            noter(lignes, "  Brouillon TikTok envoye (legende copiee).")
        except BaseException as e:
            noter(lignes, f"  TikTok : echec ({e}). Instagram est OK.")
        noter(lignes, "  " + vider(video, legende,
                                   os.path.join(PRET, "vignette.txt")))
    else:
        noter(lignes, "Pas de video aujourd'hui (jour carrousel ou "
                      "production manquante).")

    if os.path.isdir(dossier_stories) and os.listdir(dossier_stories):
        noter(lignes, f"Publication des stories "
                      f"({len(os.listdir(dossier_stories))} fichiers)…")
        P.stories(dossier_stories)
        noter(lignes, "  Stories publiees.")
        noter(lignes, "  " + vider(*[os.path.join(dossier_stories, f)
                                     for f in os.listdir(dossier_stories)]))
    else:
        noter(lignes, "Aucune story a publier.")

    return 0, lignes


if __name__ == "__main__":
    os.makedirs(JOURNAL, exist_ok=True)
    try:
        code, lignes = main()
    except Exception:
        code = 2
        lignes = ["ECHEC :", traceback.format_exc()]
        print("\n".join(lignes), flush=True)
    fin = datetime.datetime.now()
    lignes.append(f"=== termine a {fin:%H:%M}, code {code} ===")
    with open(os.path.join(JOURNAL, f"{fin:%Y-%m-%d}.txt"), "a",
              encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n\n")
    sys.exit(code)
