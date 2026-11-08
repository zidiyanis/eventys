"""Refabrique les stickers du lapin, propres et nets.

Probleme de la 1ere version : le detourage coupait DANS le fin liseré blanc
deja present sur la planche, en laissant un bord en marches d'escalier
(12,6 % de pixels semi-transparents, crenelage visible des qu'on agrandit).

Ici :
  1. masque de fond par remplissage depuis les bords (le t-shirt blanc, qui
     est enclos dans la silhouette, reste donc opaque) ;
  2. masque lisse (fermeture morphologique + flou) au lieu d'un seuil dur ;
  3. agrandissement x2 en lanczos AVANT tout trace, pour un bord doux ;
  4. contour blanc epais redessine proprement par dilatation du masque,
     facon autocollant decoupe ;
  5. ombre portee douce, pour decoller le sticker de l'image.
"""
import os

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ICI = os.path.dirname(os.path.abspath(__file__))
PLANCHE = os.path.join(ICI, "_cartes", "Planche d’autocollants de lapins EVENTYS.png")
SORTIE = os.path.join(ICI, "_cartes", "stickers")

NOMS = [
    "salut_pouce_leve_gauche", "salut_main_levee", "pouce_leve", "montre_la_main",
    "pointe_du_doigt", "timide_main_bouche", "bras_leves_content", "bras_croises",
    "au_telephone", "assis_chaise_bureau", "assis_tailleur_cafe", "assis_bureau_laptop",
]

ECHELLE = 2          # agrandissement avant trace du contour
BORD = 18            # epaisseur du liseré blanc, en pixels de l'image agrandie
# Pas d'ombre portee : a 42 % et peu floutee elle tracait un SECOND contour
# visible autour du liseré (le "fantome" signale par Yanis). Le liseré blanc
# suffit a decoller le sticker de l'image.
OMBRE = 0
FLOU_OMBRE = 0


def masque_figure(cellule):
    """Alpha lisse de la figure : 255 dedans, 0 dehors, bord adouci."""
    arr = np.array(cellule.convert("RGB")).astype(np.int16)
    # 246 et non 232 : la planche porte deja un halo clair autour de chaque
    # figure ; a 232 ce halo restait colle au sticker et faisait un liseré sale.
    blanc = arr.min(axis=2) > 246

    lab, n = ndimage.label(blanc, structure=np.ones((3, 3)))
    bords = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    bords.discard(0)
    fond = np.isin(lab, list(bords))

    figure = ~fond
    # bouche les trous et mange le crenelage
    figure = ndimage.binary_closing(figure, structure=np.ones((5, 5)))
    figure = ndimage.binary_fill_holes(figure)
    figure = ndimage.binary_opening(figure, structure=np.ones((3, 3)))

    # La decoupe en grille laisse entrer un bout du lapin voisin sur les
    # bords : on ne garde que la plus grosse forme, le reste est du voisin.
    lab2, n2 = ndimage.label(figure, structure=np.ones((3, 3)))
    if n2 > 1:
        tailles = ndimage.sum(figure, lab2, range(1, n2 + 1))
        figure = (lab2 == (int(np.argmax(tailles)) + 1))
    return Image.fromarray((figure * 255).astype(np.uint8), mode="L")


def fabrique(cellule, chemin):
    m = masque_figure(cellule)
    w, h = cellule.size
    gw, gh = w * ECHELLE, h * ECHELLE

    rgb = cellule.convert("RGB").resize((gw, gh), Image.LANCZOS)
    m = m.resize((gw, gh), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.6))
    # recentre le degrade du bord : evite le halo gris autour de la figure
    m = m.point(lambda v: 0 if v < 90 else (255 if v > 170 else int((v - 90) * 255 / 80)))

    figure = Image.merge("RGBA", (*rgb.split(), m))

    # contour blanc : masque dilate
    dil = m.filter(ImageFilter.MaxFilter(BORD * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    contour = Image.new("RGBA", (gw, gh), (255, 255, 255, 255))
    contour.putalpha(dil)

    pad = 6
    toile = Image.new("RGBA", (gw + pad * 2, gh + pad * 2), (0, 0, 0, 0))
    toile.alpha_composite(contour, (pad, pad))
    toile.alpha_composite(figure, (pad, pad))

    bbox = toile.getbbox()
    if bbox:
        toile = toile.crop(bbox)
    toile.save(chemin)
    return toile.size


def main():
    planche = Image.open(PLANCHE).convert("RGB")
    W, H = planche.size
    cols, lignes = 4, 3
    cw, ch = W / cols, H / lignes
    os.makedirs(SORTIE, exist_ok=True)
    for i in range(cols * lignes):
        r, c = divmod(i, cols)
        marge = 6
        boite = (max(int(c * cw) - marge, 0), max(int(r * ch) - marge, 0),
                 min(int((c + 1) * cw) + marge, W), min(int((r + 1) * ch) + marge, H))
        cel = planche.crop(boite)
        nom = f"{i:02d}_{NOMS[i]}.png"
        taille = fabrique(cel, os.path.join(SORTIE, nom))
        print(nom, taille)


if __name__ == "__main__":
    main()
