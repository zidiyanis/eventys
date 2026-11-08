"""Lecture du fichier cles.env, sans jamais afficher un secret.

    import cles
    k = cles.get("ELEVENLABS_API_KEY")        # leve une erreur si absente
    k = cles.get("X", obligatoire=False)      # renvoie None si absente

La fonction `etat()` imprime un tableau de controle : pour chaque cle, si
elle est remplie, sa longueur et ses 4 premiers caracteres. Juste de quoi
verifier qu'elle a ete bien collee, jamais de quoi la reveler.
"""
import os

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "cles.env")


def _lire():
    valeurs = {}
    if not os.path.exists(FICHIER):
        return valeurs
    with open(FICHIER, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#") or "=" not in ligne:
                continue
            nom, _, val = ligne.partition("=")
            val = val.strip().strip('"').strip("'")
            if val:
                valeurs[nom.strip()] = val
    return valeurs


def get(nom, obligatoire=True):
    v = _lire().get(nom) or os.environ.get(nom)
    if not v and obligatoire:
        raise SystemExit(
            f"Cle manquante : {nom}\n"
            f"Ouvre {FICHIER}, colle-la apres le signe =, et enregistre.")
    return v


def etat():
    v = _lire()
    attendues = ["ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID"]
    print(f"Fichier : {FICHIER}")
    print(f"{'CLE':<26} {'ETAT':<10} DETAIL")
    print("-" * 60)
    for nom in attendues:
        if nom in v:
            print(f"{nom:<26} {'remplie':<10} "
                  f"{len(v[nom])} caracteres, debut {v[nom][:4]}…")
        else:
            print(f"{nom:<26} {'VIDE':<10} -")
    extra = [k for k in v if k not in attendues]
    if extra:
        print("\nAutres cles presentes :", ", ".join(extra))


if __name__ == "__main__":
    etat()
