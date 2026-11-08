"""Detoure les poses generees (Figma AI) avec la meme chaine que la planche.

Les images generees arrivent sur fond blanc uni, sans liseré : on applique
donc exactement le meme traitement que `stickers_hd.py` (masque par
remplissage depuis les bords, lissage, agrandissement, liseré blanc epais)
pour que les poses generees et les poses de la planche de Yanis se melangent
sans qu'on voie la difference.
"""
import os

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "_cartes", "generes")
DST = os.path.join(ICI, "_cartes", "stickers")

ECHELLE = 2
BORD = 18


def masque_figure(img):
    arr = np.array(img.convert("RGB")).astype(np.int16)
    blanc = arr.min(axis=2) > 238

    lab, n = ndimage.label(blanc, structure=np.ones((3, 3)))
    bords = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    bords.discard(0)
    fond = np.isin(lab, list(bords))

    fig = ~fond
    fig = ndimage.binary_closing(fig, structure=np.ones((5, 5)))
    fig = ndimage.binary_fill_holes(fig)
    fig = ndimage.binary_opening(fig, structure=np.ones((3, 3)))
    lab2, n2 = ndimage.label(fig, structure=np.ones((3, 3)))
    if n2 > 1:
        tailles = ndimage.sum(fig, lab2, range(1, n2 + 1))
        fig = (lab2 == (int(np.argmax(tailles)) + 1))
    return Image.fromarray((fig * 255).astype(np.uint8), mode="L")


def fabrique(src_path, dst_path):
    im = Image.open(src_path).convert("RGB")
    m = masque_figure(im)
    w, h = im.size
    gw, gh = w * ECHELLE, h * ECHELLE

    rgb = im.resize((gw, gh), Image.LANCZOS)
    m = m.resize((gw, gh), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.6))
    m = m.point(lambda v: 0 if v < 90 else (255 if v > 170 else int((v - 90) * 255 / 80)))
    figure = Image.merge("RGBA", (*rgb.split(), m))

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
    toile.save(dst_path)
    return toile.size


NUMEROS = {
    "chemise_debout": "12",
    "chemise_bras_croises": "13",
    "chemise_telephone": "14",
    "tshirt_pointe_ordre": "15",
    "scene_jardin": None,          # scene plein cadre, pas un sticker
    "lunettes_bras_croises": "16",
    "lunettes_pointe": "17",
}

if __name__ == "__main__":
    for f in sorted(os.listdir(SRC)):
        if not f.lower().endswith(".png"):
            continue
        base = os.path.splitext(f)[0]
        if base not in NUMEROS:
            continue
        num = NUMEROS[base]
        if num is None:            # image de decor, pas a detourer
            continue
        out = os.path.join(DST, f"{num}_{base}.png")
        print(f"{num}_{base}.png", fabrique(os.path.join(SRC, f), out))
