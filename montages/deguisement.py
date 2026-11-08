# -*- coding: utf-8 -*-
"""Le lapin deguise : un chapeau de sorciere pose sur chaque pose.

Demande de Yanis le 31/10 : « aujourd'hui c'est Halloween donc je veux que
tu fasses une video avec le lapin deguise ».

LA CHARTE PASSE AVANT LA FETE. Le chapeau est NOIR, bandeau BORDEAUX,
boucle DOREE. Pas d'orange : la charte creme/bordeaux de Yanis est le
seul element qui rende les videos reconnaissables entre elles, et une
tache orange sur le seul plan ou l'oeil se pose aurait coute plus que la
blague n'aurait rapporte.

POURQUOI UN DECALAGE PAR POSE. Premiere version : une seule hauteur
relative pour les neuf poses (sommet de la matiere + 13 % de la hauteur
de l'image). Le relecteur a montre que le bord du chapeau COUVRAIT LES
DEUX YEUX sur `16_lunettes_bras_croises` — c'est-a-dire sur le plan
d'ouverture ET sur la vignette du Reel — ainsi que sur
`13_chemise_bras_croises`, et masquait un oeil sur `12_chemise_debout`.

La cause : les stickers ne sont pas cadres pareil. Sur les poses en
chemise, la tete occupe une part plus petite de l'image, donc 13 % de la
hauteur tombent plus bas sur le visage. Une proportion unique ne peut pas
marcher ; il faut un reglage par pose, mesure a l'oeil sur le rendu a la
taille reelle d'affichage (200 px de large).

    python H:/eventys/montages/deguisement.py
"""
import os

from PIL import Image, ImageDraw

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "_cartes", "stickers")
DST = os.path.join(ICI, "_cartes", "stickers_halloween")

NOIR = (26, 22, 24, 255)
BORDEAUX = (111, 47, 47, 255)
DORE = (198, 160, 92, 255)

# pose -> (hauteur du bord du chapeau en fraction de l'image, depuis le
#          point le plus haut du sticker ; largeur du bord en fraction de
#          la largeur de l'image)
# Les six premieres valeurs sont celles qui passaient deja. Les trois
# dernieres ont ete remontees apres le relecteur.
POSES = {
    "00_salut_pouce_leve_gauche": (0.130, 0.44),
    "02_pouce_leve": (0.130, 0.44),
    "03_montre_la_main": (0.130, 0.44),
    "14_chemise_telephone": (0.130, 0.44),
    "15_tshirt_pointe_ordre": (0.130, 0.44),
    "17_lunettes_pointe": (0.130, 0.44),
    "12_chemise_debout": (0.092, 0.40),
    "13_chemise_bras_croises": (0.080, 0.40),
    "16_lunettes_bras_croises": (0.078, 0.40),
}


def tete(im, part):
    """Centre horizontal entre les oreilles, et hauteur du bord du chapeau.

    Les oreilles tombent sur les cotes : dans la bande du haut, le centre
    de masse horizontal tombe donc entre elles, c'est-a-dire sur le crane.
    """
    a = im.split()[3]
    w, h = im.size
    px = a.load()
    haut = None
    sx = n = 0
    for y in range(h):
        ligne = [x for x in range(w) if px[x, y] > 40]
        if not ligne:
            continue
        if haut is None:
            haut = y
        if y < haut + int(h * 0.18):
            sx += sum(ligne)
            n += len(ligne)
        else:
            break
    return int(sx / n), haut + int(h * part)


def chapeau(w, h, larg_part):
    """Le chapeau seul, centre du BORD au centre du calque."""
    larg = int(w * larg_part)
    haut = int(h * 0.16)
    cote = max(larg, haut) * 3
    L = Image.new("RGBA", (cote, cote), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    bx = by = cote // 2
    d.ellipse([bx - larg // 2, by - larg // 10,
               bx + larg // 2, by + larg // 10], fill=NOIR)
    d.polygon([(bx - int(larg * 0.26), by + 2), (bx + int(larg * 0.26), by + 2),
               (bx + int(larg * 0.07), by - haut)], fill=NOIR)
    d.ellipse([bx - int(larg * 0.26), by - int(larg * 0.115),
               bx + int(larg * 0.26), by + int(larg * 0.02)], fill=BORDEAUX)
    d.rectangle([bx - int(larg * 0.05), by - int(larg * 0.095),
                 bx + int(larg * 0.05), by - int(larg * 0.015)], fill=DORE)
    # `expand=False` : le centre du calque ne bouge pas, donc le centre du
    # bord non plus, et la pose reste calculable apres l'inclinaison.
    return L.rotate(12, resample=Image.BICUBIC, expand=False)


def main():
    os.makedirs(DST, exist_ok=True)
    for nom, (part, larg_part) in POSES.items():
        im = Image.open(os.path.join(SRC, nom + ".png")).convert("RGBA")
        w, h = im.size
        cx, cy = tete(im, part)
        L = chapeau(w, h, larg_part)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        out.paste(im, (0, 0))
        out.alpha_composite(L, (cx - L.size[0] // 2, cy - L.size[1] // 2))
        out.save(os.path.join(DST, nom + ".png"))
        print(f"  {nom}")


if __name__ == "__main__":
    main()
