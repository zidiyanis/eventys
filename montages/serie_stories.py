"""Genere une serie de stories, en alternant les teintes de fond.

    python H:/eventys/montages/serie_stories.py

L'alternance beige / bordeaux donne du rythme : quand quelqu'un fait defiler
plusieurs stories d'affilee, le changement de fond signale qu'il passe a une
autre information. Deux stories beiges de suite se confondent.
"""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import stories2 as S  # noqa: E402

X = os.path.join(ICI, "_stories", "src")


def serie():
    sorties = []
    sorties.append(S.fiche_produit(
        f"{X}/chaise_seule.jpg", "CHAISE NAPOLÉON", "3 €",
        "Livrée et montée · Île-de-France",
        nom="1_beige_fiche.png", teinte="beige"))

    sorties.append(S.grille_catalogue([
        (f"{X}/chaise_seule.jpg", "CHAISE NAPOLÉON", "3 €"),
        (f"{X}/ronde.jpg", "TABLE RONDE", "10 €"),
        (f"{X}/couvert.jpg", "KIT VAISSELLE", "2 €"),
        (f"{X}/camion.jpg", "LIVRAISON", "IDF"),
    ], nom="2_bordeaux_grille.png", teinte="bordeaux"))

    sorties.append(S.planche_photos(
        [f"{X}/longue.jpg", f"{X}/ronde.jpg", f"{X}/couvert.jpg"],
        "UN MARIAGE EN JUIN", "40 chaises · 5 tables · 40 couverts",
        nom="3_beige_planche.png", teinte="beige"))

    sorties.append(S.fiche_produit(
        f"{X}/ronde.jpg", "TABLE RONDE", "10 €",
        "Jusqu'à 10 personnes",
        nom="4_bordeaux_fiche.png", teinte="bordeaux"))
    return sorties


if __name__ == "__main__":
    for p in serie():
        print(" ", os.path.basename(p))
