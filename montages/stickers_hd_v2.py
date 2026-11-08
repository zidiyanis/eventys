"""Redecoupe les 12 lapins de la planche FORME PAR FORME (et non en grille fixe).

Probleme de `stickers_hd.py` : la planche est coupee en 4 x 3 cases egales, et
un bras tendu (poses 03 et 04), une main (06), une oreille ou l'ordinateur
(11) depassent de leur case : ils sont tronques net.

Ici, chaque lapin est isole par composantes connexes du non-blanc, puis passe
dans la meme chaine de detourage (`fabrique`) que la v1. Sortie dans
`_cartes/stickers_v2` : les stickers actuels ne sont pas touches.
"""
import os

import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage

import stickers_hd as v1

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "_cartes", "stickers_v2")
MARGE = 40          # le liseré redessine (~9 px) doit tenir dans la case
PAD_PLANCHE = 60    # blanc ajoute autour de la planche entiere


def boites(planche):
    arr = np.array(planche.convert("RGB")).astype(np.int16)
    non_blanc = arr.min(axis=2) < 250
    # Le fin liseré gris qui entoure chaque sticker est une courbe fermee :
    # sans dilatation, chaque lapin forme deja UNE composante (mesure : 12
    # grandes formes a 250 ; des 2 iterations, les voisins fusionnent).
    forme = non_blanc
    lab, n = ndimage.label(forme)
    tailles = ndimage.sum(forme, lab, range(1, n + 1))
    garde = [i + 1 for i, t in enumerate(tailles) if t > 20000]
    res = []
    for i in garde:
        ys, xs = np.where(lab == i)
        res.append((xs.min(), ys.min(), xs.max(), ys.max()))
    return res


def main():
    planche = Image.open(v1.PLANCHE).convert("RGB")
    # Du blanc tout autour : certains lapins touchent le bord de la planche,
    # et le liseré blanc redessine autour d'eux serait coupe net.
    planche = ImageOps.expand(planche, border=PAD_PLANCHE, fill=(255, 255, 255))
    W, H = planche.size
    bx = [b for b in boites(planche) if (b[1] + b[3]) / 2 < 880 + PAD_PLANCHE]
    print(len(bx), "formes trouvees sur les 2 premieres rangees (attendu : 8)")
    if len(bx) != 8:
        raise SystemExit("les formes ne sont pas separees : on s'arrete")
    bx.sort(key=lambda b: (b[1] + b[3]) / 2)
    lignes = [sorted(bx[i * 4:(i + 1) * 4], key=lambda b: b[0]) for i in range(2)]
    # Rangee du bas : le lapin au cafe et celui a l'ordinateur se touchent
    # sur la planche, ils fusionnent. Cases mesurees a la main (x0, x1).
    bas = [(10, 262), (268, 552), (548, 826), (822, 1122)]
    y0, y1 = 870 + PAD_PLANCHE, H
    lignes.append([(x0 + PAD_PLANCHE, y0, x1 + PAD_PLANCHE, y1)
                   for (x0, x1) in bas])
    # Les voisins du bas se touchent : on blanchit tout ce qui depasse de
    # la case, sauf vers l'exterieur de la planche (pas de voisin la).
    blanchir = []
    for x0, y0b, x1, y1b in lignes[2]:
        blanchir.append((x0, x1))
    lignes_blanchies = {tuple(b): True for b in lignes[2]}
    os.makedirs(SORTIE, exist_ok=True)
    k = 0
    for ligne in lignes:
        for (x0, y0, x1, y1) in ligne:
            boite = (max(x0 - MARGE, 0), max(y0 - MARGE, 0),
                     min(x1 + MARGE, W), min(y1 + MARGE, H))
            cel = planche.crop(boite)
            if (x0, y0, x1, y1) in lignes_blanchies:
                # blanc hors de la case, a gauche et a droite (6 px de tolerance)
                gauche = x0 - boite[0] - 6
                droite = x1 - boite[0] + 6
                if k != 8 and gauche > 0:      # le 08 est au bord gauche
                    cel.paste((255, 255, 255), (0, 0, gauche, cel.height))
                if k != 11 and droite < cel.width:  # le 11 est au bord droit
                    cel.paste((255, 255, 255), (droite, 0, cel.width, cel.height))
            nom = f"{k:02d}_{v1.NOMS[k]}.png"
            print(nom, v1.fabrique(cel, os.path.join(SORTIE, nom)))
            k += 1


if __name__ == "__main__":
    main()
