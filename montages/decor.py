"""Decor evenementiel pour les plans sans rush (fond papier).

Yanis : « pour les plans ou il y a juste le lapin, fais quelque chose de
plus, la c'est vide et fade » et « on est dans l'evenementiel ».

D'ou :
  - une ARCHE DOREE en fond, qui est litteralement un de ses produits
    (arche circulaire doree, 40 €) et qui pose tout de suite l'univers ;
  - des CONFETTIS qui tombent en continu, sur trois plans de profondeur a
    des vitesses differentes (parallaxe) ;
  - une lueur chaude au centre, pour que le fond ne soit plus un aplat.

Les confettis sont trois PNG fixes plus hauts que le cadre, qu'on fait
defiler par expression `mod()` : c'est fluide et ca ne coute pas une suite
de centaines d'images.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

import da

W, H = 1080, 1920
ICI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(ICI, "_tmp_decor")
os.makedirs(TMP, exist_ok=True)

PAPIER = (240, 235, 223)
OR = (198, 162, 86)
OR_CLAIR = (224, 199, 139)
BORDEAUX = da.BORDEAUX
ROUGE = da.ROUGE
CREME = da.CREME


def _p(n):
    return os.path.join(TMP, n)


def fond_evenement(nom="fond_event.png"):
    """Fond creme + lueur chaude + arche doree + ligne de sol."""
    p = _p(nom)
    if os.path.exists(p):
        return p
    img = Image.new("RGB", (W, H), PAPIER)

    # lueur chaude centrale
    lueur = Image.new("L", (W, H), 0)
    dl = ImageDraw.Draw(lueur)
    dl.ellipse([-180, 180, W + 180, 1500], fill=120)
    lueur = lueur.filter(ImageFilter.GaussianBlur(220))
    chaud = Image.new("RGB", (W, H), (255, 246, 226))
    img = Image.composite(chaud, img, lueur)

    d = ImageDraw.Draw(img)

    # trame tres discrete
    for x in range(0, W, 54):
        d.line([(x, 0), (x, H)], fill=(231, 225, 211), width=1)
    for y in range(0, H, 54):
        d.line([(0, y), (W, y)], fill=(231, 225, 211), width=1)

    # arche doree : montants + demi-cercle, dessinee en double trait
    cx = W // 2
    larg, bas, haut_arc = 640, 1530, 470
    g, dr_ = cx - larg // 2, cx + larg // 2
    for ep, coul in ((16, OR_CLAIR), (7, OR)):
        d.line([(g, bas), (g, haut_arc)], fill=coul, width=ep)
        d.line([(dr_, bas), (dr_, haut_arc)], fill=coul, width=ep)
        d.arc([g, haut_arc - larg // 2, dr_, haut_arc + larg // 2],
              start=180, end=360, fill=coul, width=ep)

    # sol
    d.line([(90, bas + 6), (W - 90, bas + 6)], fill=(214, 204, 186), width=4)

    img = img.filter(ImageFilter.GaussianBlur(0.4))
    img.save(p)
    return p


def confettis(nom, graine, nb=70, echelle=1.0, opacite=235):
    """Bande de confettis 2x plus haute que le cadre, pour defiler en boucle."""
    p = _p(nom)
    if os.path.exists(p):
        return p
    rnd = random.Random(graine)
    img = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    couleurs = [OR, OR_CLAIR, ROUGE, BORDEAUX, (250, 246, 238)]
    for _ in range(nb):
        x = rnd.randint(-20, W + 20)
        y = rnd.randint(0, H * 2)
        c = rnd.choice(couleurs) + (opacite,)
        forme = rnd.random()
        t = rnd.uniform(9, 20) * echelle
        if forme < 0.55:                      # bandelette
            lo, la = t * 2.4, t * 0.55
            bande = Image.new("RGBA", (int(lo), int(la)), c)
            bande = bande.rotate(rnd.uniform(0, 180), expand=True,
                                 resample=Image.BICUBIC)
            img.alpha_composite(bande, (int(x), int(y)))
        elif forme < 0.8:                     # rond
            d.ellipse([x, y, x + t, y + t], fill=c)
        else:                                 # losange
            d.polygon([(x, y + t / 2), (x + t / 2, y), (x + t, y + t / 2),
                       (x + t / 2, y + t)], fill=c)
    img.save(p)
    return p


def couches_confettis():
    """Trois profondeurs : loin/petit/lent, pres/gros/rapide."""
    return [
        {"png": confettis("conf_loin.png", 7, nb=90, echelle=0.65, opacite=170),
         "vitesse": 46},
        {"png": confettis("conf_moyen.png", 21, nb=60, echelle=1.0, opacite=215),
         "vitesse": 78},
        {"png": confettis("conf_pres.png", 44, nb=34, echelle=1.5, opacite=240),
         "vitesse": 122},
    ]


def expr_chute(vitesse):
    """Expression de defilement vertical en boucle sans raccord visible."""
    return f"-{H}+mod(t*{vitesse},{H})"
