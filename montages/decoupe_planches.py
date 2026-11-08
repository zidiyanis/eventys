"""Decoupe les planches de lapins (grille 4x3, fond blanc) en stickers PNG.

    python montages/decoupe_planches.py            (toutes les planches presentes)

Entree : montages/_cartes/generes_v4/planche_NN.png
Sortie : montages/_cartes/stickers_nouveaux/NN_nom.png (RGBA, contour blanc
"autocollant", ombre au sol retiree) + montages/_cartes/CONTROLE_nouveaux_N.jpg
Le lapin n'est jamais redessine : ce sont les pixels de la planche.
"""
import glob
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ICI = os.path.dirname(os.path.abspath(__file__))
CARTES = os.path.join(ICI, "_cartes")
ENTREE = os.path.join(CARTES, "generes_v4")
SORTIE = os.path.join(CARTES, "stickers_nouveaux")
COLS, LIGNES = 4, 3
MIN_LARGEUR_PLANCHE = 1000   # en dessous : les lapins feraient moins de 150 px

NOMS = {
    1: ["joie", "rit_aux_eclats", "pleure_de_joie", "surpris", "choque", "amoureux",
        "timide", "fier", "clin_d_oeil", "saute_de_joie", "enerve", "triste"],
    2: ["reflechit", "a_une_idee", "epuise", "endormi", "peur", "boude",
        "embarrasse", "soulage", "curieux", "perplexe", "excite", "blase"],
    3: ["pouce_leve", "deux_pouces", "applaudit", "salue", "high_five", "ok",
        "croise_les_doigts", "chut", "montre_gauche", "montre_droite",
        "fait_signe_de_venir", "accueille"],
    4: ["porte_chaise", "assis_chaise", "empile_chaises", "chariot_chaises",
        "porte_table_ronde", "metre_ruban", "assiette", "plateau_verres",
        "couverts", "deplie_nappe", "arche_doree", "cles_camion"],
    5: ["telephone", "au_telephone", "devis", "liste_coche", "calendrier",
        "ordinateur", "porte_carton", "diable", "lunettes_soleil", "casquette",
        "gilet", "sac_a_dos"],
    6: ["pere_noel", "bonnet_echarpe", "pull_de_noel", "cadeau", "guirlande",
        "doudoune", "chocolat_chaud", "sapin", "bonhomme_de_neige",
        "manteau_echarpe", "champagne", "reveillon"],
    7: ["chapeau_paille", "glace", "bouquet", "arrosoir", "ballon_de_plage",
        "barbecue", "limonade", "eventail", "casquette_gourde", "ventilateur",
        "panier_pique_nique", "oeuf_de_paques"],
    8: ["impermeable", "echarpe_automne", "feuille", "citrouille", "sorcier",
        "lanterne", "dattes", "coeur_tissu", "tasse_fumante", "bottes_de_pluie",
        "bonnet_mitaines", "fleurs_seches"],
    9: ["mariage_costume", "mariee_voile", "gateau_anniversaire", "ballons",
        "confettis", "trinque", "chef", "dj", "photographe", "micro", "danse",
        "diplome"],
}


def masque_lapin(rgb):
    """True la ou il y a le lapin (ou ses accessoires), False sur le fond."""
    h, w, _ = rgb.shape
    blanc = rgb.min(axis=2) >= 250
    lab, n = ndi.label(blanc)
    bord = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    bord.discard(0)
    fond = np.isin(lab, list(bord))
    fg = ~fond
    fg = ndi.binary_opening(fg, iterations=1)
    return ndi.binary_fill_holes(fg)


def retire_ombre(rgb, m):
    """Enleve l'ombre grise sous les pieds (bas du lapin, gris neutre clair)."""
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        return m
    y0, y1 = ys.min(), ys.max()
    zone = np.zeros_like(m)
    zone[int(y1 - (y1 - y0) * 0.16):y1 + 1, :] = True
    mx, mn = rgb.max(axis=2).astype(int), rgb.min(axis=2).astype(int)
    neutre_clair = ((mx - mn) <= 9) & (mn >= 185)
    m2 = m & ~(zone & neutre_clair)
    m2 = ndi.binary_opening(m2, iterations=2)
    lab, n = ndi.label(m2)
    if n > 1:
        tailles = ndi.sum(m2, lab, range(1, n + 1))
        m2 = lab == (1 + int(np.argmax(tailles)))
    return ndi.binary_fill_holes(m2)


def sticker(rgb, m, contour=11, marge=14):
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    pad = contour + marge
    sub = rgb[max(y0 - pad, 0):y1 + pad, max(x0 - pad, 0):x1 + pad]
    mm = m[max(y0 - pad, 0):y1 + pad, max(x0 - pad, 0):x1 + pad]
    # le contour ne doit pas deborder dans le voisin : on travaille dans la case
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * contour + 1, 2 * contour + 1))
    halo = cv2.dilate(mm.astype(np.uint8) * 255, k)
    halo = cv2.GaussianBlur(halo, (0, 0), 1.2)
    lapin = cv2.GaussianBlur(mm.astype(np.uint8) * 255, (0, 0), 0.8)
    out = np.zeros(sub.shape[:2] + (4,), np.uint8)
    out[..., :3] = 255
    out[..., 3] = halo
    a = lapin.astype(float)[..., None] / 255
    out[..., :3] = (sub * a + 255 * (1 - a)).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def decoupe(num):
    f = os.path.join(ENTREE, f"planche_{num:02d}.png")
    img = Image.open(f).convert("RGB")
    if img.width < MIN_LARGEUR_PLANCHE:
        print(f"planche {num} : {img.width} px de large, trop petite, a retelecharger")
        return []
    rgb = np.array(img)
    h, w, _ = rgb.shape
    m = masque_lapin(rgb)
    lab, n = ndi.label(m)
    cases = {}
    for i in range(1, n + 1):
        comp = lab == i
        if comp.sum() < 2500:
            continue
        ys, xs = np.nonzero(comp)
        c = min(int(xs.mean() / (w / COLS)), COLS - 1)
        r = min(int(ys.mean() / (h / LIGNES)), LIGNES - 1)
        cases.setdefault((r, c), np.zeros_like(m))
        cases[(r, c)] |= comp
    os.makedirs(SORTIE, exist_ok=True)
    sortis = []
    for (r, c), cm in sorted(cases.items()):
        idx = r * COLS + c
        nom = NOMS[num][idx] if idx < len(NOMS.get(num, [])) else f"pose{idx + 1}"
        cm = retire_ombre(rgb, cm)
        im = sticker(rgb, cm)
        chemin = os.path.join(SORTIE, f"{num:02d}_{idx + 1:02d}_{nom}.png")
        im.save(chemin)
        sortis.append(chemin)
    print(f"planche {num} : {len(sortis)} stickers")
    return sortis


def controle(fichiers, nom):
    CW, CH = 240, 300
    cols = 8
    rows = (len(fichiers) + cols - 1) // cols
    S = Image.new("RGB", (cols * CW, rows * (CH + 18)), (110, 110, 120))
    d = ImageDraw.Draw(S)
    for i, f in enumerate(fichiers):
        im = Image.open(f).convert("RGBA")
        im.thumbnail((CW - 10, CH - 10))
        x, y = (i % cols) * CW, (i // cols) * (CH + 18)
        S.paste(im, (x + (CW - im.width) // 2, y + (CH - im.height) // 2), im)
        d.text((x + 4, y + CH + 2), os.path.basename(f)[:-4][:36], fill=(255, 255, 255))
    S.save(nom, quality=84)


if __name__ == "__main__":
    nums = sorted(int(os.path.basename(p)[8:10])
                  for p in glob.glob(os.path.join(ENTREE, "planche_*.png")))
    tous = []
    for n in nums:
        tous += decoupe(n)
    for k in range(0, len(tous), 24):
        controle(tous[k:k + 24], os.path.join(CARTES, f"CONTROLE_nouveaux_{k // 24 + 1}.jpg"))
    print(len(tous), "stickers au total")
