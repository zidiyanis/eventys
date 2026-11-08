# -*- coding: utf-8 -*-
"""Detoure les neuf poses du lapin DEGUISE en stickers utilisables.

CE QUI A ETE REFUSE AVANT. Premiere tentative : un chapeau de sorciere
dessine au crayon PAR-DESSUS les stickers existants (`deguisement.py`).
Yanis : « c'est de la merde », puis « je veux juste que le lapin soit
deguise en un sticker, pas avec un truc collé par dessus ». Il a raison :
un chapeau pose en calque n'epouse pas la tete, ne projette pas d'ombre,
et masquait les yeux sur trois poses.

CE QU'ON FAIT A LA PLACE. Le lapin est GENERE deguise — costume complet
(chapeau de sorciere, cape noire, t-shirt blanc dessous) — puis detoure
avec exactement la meme chaine que les poses 12 a 17 de la planche
d'origine (`stickers_generes.py`), pour que tout se melange sans qu'on
voie la difference : masque par remplissage depuis les bords, lissage,
agrandissement x2, lisere blanc epais, ombre portee.

Les images sources sont dans `_cartes/generes_halloween/`, generees par
Figma AI le 01/11 (fichier « Eventys — lapin deguise Halloween »). Les
liens de telechargement de Figma expirent au bout de 7 jours : les PNG
sont donc gardes sur le disque, ce sont eux la source, pas les liens.

    python H:/eventys/montages/stickers_halloween.py
"""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

import stickers_generes as SG  # noqa: E402

SRC = os.path.join(ICI, "_cartes", "generes_halloween")
DST = os.path.join(ICI, "_cartes", "stickers_halloween")

# Les numeros sont ceux du gabarit : un plan appelle sa pose par son nom
# complet, donc les deux jeux (normal et deguise) doivent porter les
# memes noms de fichier pour etre interchangeables.
NUMEROS = {
    "salut_pouce_leve_gauche": "00",
    "pouce_leve": "02",
    "montre_la_main": "03",
    "chemise_debout": "12",
    "chemise_bras_croises": "13",
    "chemise_telephone": "14",
    "tshirt_pointe_ordre": "15",
    "lunettes_bras_croises": "16",
    "lunettes_pointe": "17",
}


def main():
    os.makedirs(DST, exist_ok=True)
    for f in sorted(os.listdir(SRC)):
        base, ext = os.path.splitext(f)
        if ext.lower() != ".png" or base not in NUMEROS:
            continue
        num = NUMEROS[base]
        out = os.path.join(DST, f"{num}_{base}.png")
        taille = SG.fabrique(os.path.join(SRC, f), out)
        print(f"  {num}_{base}.png  {taille}")


if __name__ == "__main__":
    main()
