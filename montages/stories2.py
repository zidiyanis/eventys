"""Stories Eventys — compositions, pas des captures legendees.

Les premiers modeles posaient un bandeau de texte sur une photo plein ecran :
ca revenait a publier une capture. Ici l'image devient un ELEMENT d'une mise
en page, dans la charte de la marque — fond papier, arche doree, Bodoni,
creme et bordeaux — au lieu d'en etre le fond.

Zone sure des stories : rien au-dessus de y=260 (barre de progression et
profil), rien en dessous de y=1620 (champ de message et partage).
"""
import math
import os
import random
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import da

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
SORTIE = os.path.join(ICI, "_stories")

W, H = 1080, 1920
HAUT_SUR, BAS_SUR = 260, 1620

PAPIER = (243, 239, 230)
CREME, BORDEAUX, ROUGE, ENCRE = da.CREME, da.BORDEAUX, da.ROUGE, da.ENCRE
OR = (198, 162, 86)
GRIS = (124, 112, 100)


def _p(nom):
    os.makedirs(SORTIE, exist_ok=True)
    return os.path.join(SORTIE, nom)


def _larg(d, t, f, esp=0):
    return sum(d.textlength(c, font=f) for c in t) + esp * max(len(t) - 1, 0)


def _ecrire(d, x, y, t, f, coul, esp=0):
    for c in t:
        d.text((x, y), c, font=f, fill=coul)
        x += d.textlength(c, font=f) + esp


# Deux teintes de fond, a alterner d'une story a l'autre pour donner du
# rythme a une serie. Chaque teinte emporte sa propre palette de texte :
# sur un fond bordeaux, l'encre et le bordeaux deviennent illisibles.
TEINTES = {
    "beige": {
        "fond": PAPIER, "lueur": (252, 249, 242),
        "titre": BORDEAUX, "texte": ENCRE, "discret": GRIS,
        "pastille": ROUGE, "sur_pastille": CREME, "filet": OR,
        "arche": 70,
    },
    # Exactement la teinte des pastilles de prix — c'est celle que Yanis a
    # designee. Un bordeaux plus sombre avait ete essaye d'abord : trop
    # lourd, et il ne repondait a rien d'autre dans la charte.
    "bordeaux": {
        "fond": ROUGE, "lueur": (191, 88, 88),
        "titre": CREME, "texte": (248, 240, 236), "discret": (238, 214, 208),
        "pastille": CREME, "sur_pastille": ROUGE, "filet": (238, 214, 196),
        "arche": 130,
    },
}


def fond_papier(arche=True, teinte="beige"):
    """Fond de marque : aplat teinte, lueur chaude, arche doree discrete."""
    t = TEINTES[teinte]
    img = Image.new("RGB", (W, H), t["fond"])
    lueur = Image.new("L", (W, H), 0)
    ImageDraw.Draw(lueur).ellipse([-200, 180, W + 200, 1600], fill=110)
    img = Image.composite(Image.new("RGB", (W, H), t["lueur"]), img,
                          lueur.filter(ImageFilter.GaussianBlur(200)))
    img = img.convert("RGBA")
    if arche:
        a = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(a)
        larg, cx = 620, W // 2
        g, dte = cx - larg // 2, cx + larg // 2
        bas, haut = 1560, 520
        for ep, al in ((3, t["arche"]),):
            dr.line([(g, bas), (g, haut)], fill=OR + (al,), width=ep)
            dr.line([(dte, bas), (dte, haut)], fill=OR + (al,), width=ep)
            dr.arc([g, haut - larg // 2, dte, haut + larg // 2], 180, 360,
                   fill=OR + (al,), width=ep)
        img = Image.alpha_composite(img, a)
    return img


FICHIER_LOGO = os.path.join(os.path.dirname(ICI), "assets", "LOGO_eventys.png")


def _logo_detoure(haut):
    """Le vrai logo de Yanis, fond rendu transparent, mis a l'echelle."""
    import numpy as np
    im = Image.open(FICHIER_LOGO).convert("RGB")
    a = np.array(im).astype(int)
    alpha = np.clip((236 - a.mean(axis=2)) * 8, 0, 255).astype(np.uint8)
    out = Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), "RGBA")
    out = out.crop(out.getbbox())
    r = haut / out.height
    return out.resize((int(out.width * r), haut), Image.LANCZOS)


def logo(img, teinte="beige", y=286, haut=132):
    """Le logo d'origine, centre en haut — dans la zone sure (y > 260).

    Le lettrage Bodoni qui tenait lieu de logo a ete remplace par le vrai
    fichier de Yanis : trois typographies differentes selon le support, ce
    n'est plus une marque.

    Sur fond bordeaux, le logo bicolore devient illisible : on le passe alors
    en creme uni, sa silhouette suffit a le reconnaitre.
    """
    t = TEINTES[teinte]
    lg = _logo_detoure(haut)
    if teinte != "beige":
        plein = Image.new("RGBA", lg.size, CREME + (255,))
        plein.putalpha(lg.split()[3])
        lg = plein
    img.alpha_composite(lg, ((W - lg.width) // 2, y))
    d = ImageDraw.Draw(img)
    bas = y + haut + 20
    d.line([(W / 2 - 150, bas), (W / 2 + 150, bas)], fill=t["filet"], width=3)
    return bas


def photo_cadre(source, larg, haut, rayon=26, angle=0.0, bord=True,
                coul_bord=(255, 253, 248, 255), entiere=False):
    """Une photo dans un cadre arrondi, legerement inclinee.

    `entiere=True` : la photo tient TOUTE dans le cadre, qui s'adapte a ses
    proportions. C'est le mode a utiliser pour montrer un produit.

    Pourquoi : le mode recadre prend une bande au centre. Sur une photo
    verticale de couvert dresse, cette bande tombait sur la nappe vide — la
    story annoncait « kit vaisselle » et ne montrait aucun produit.
    """
    im = Image.open(source).convert("RGB")
    if entiere:
        r = min(larg / im.width, haut / im.height)
        im = im.resize((max(int(im.width * r), 1), max(int(im.height * r), 1)),
                       Image.LANCZOS).convert("RGBA")
        larg, haut = im.size
    else:
        r = max(larg / im.width, haut / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1),
                       Image.LANCZOS)
        gx, gy = (im.width - larg) // 2, (im.height - haut) // 2
        im = im.crop((gx, gy, gx + larg, gy + haut)).convert("RGBA")

    masque = Image.new("L", (larg, haut), 0)
    ImageDraw.Draw(masque).rounded_rectangle([0, 0, larg - 1, haut - 1],
                                             radius=rayon, fill=255)
    im.putalpha(masque)

    if bord:
        cadre = Image.new("RGBA", (larg + 20, haut + 20), (0, 0, 0, 0))
        ImageDraw.Draw(cadre).rounded_rectangle(
            [0, 0, larg + 19, haut + 19], radius=rayon + 8,
            fill=coul_bord)
        cadre.alpha_composite(im, (10, 10))
        im = cadre

    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    return im


def _ombre(img, calque, pos, flou=18, alpha=90):
    """Pose une ombre portee sous un calque avant de le coller."""
    o = Image.new("RGBA", img.size, (0, 0, 0, 0))
    silhouette = Image.new("RGBA", calque.size, (20, 14, 12, alpha))
    silhouette.putalpha(calque.split()[3].point(lambda v: int(v * alpha / 255)))
    o.alpha_composite(silhouette, (pos[0] + 6, pos[1] + 10))
    img.alpha_composite(o.filter(ImageFilter.GaussianBlur(flou)))
    img.alpha_composite(calque, pos)


# --------------------------------------------------------------------------
# 1. Fiche produit editoriale
# --------------------------------------------------------------------------

def fiche_produit(source, article, prix, detail, nom="E_fiche.png",
                  teinte="beige"):
    t = TEINTES[teinte]
    img = fond_papier(teinte=teinte)
    d = ImageDraw.Draw(img)
    f_sur = ImageFont.truetype(da.BODONI, 30)
    f_t = ImageFont.truetype(da.BODONI_B, 72)
    f_p = ImageFont.truetype(da.BODONI_B, 96)
    f_d = ImageFont.truetype(da.BODONI, 36)

    bas_logo = logo(img, teinte)
    d = ImageDraw.Draw(img)
    sur = "ÎLE-DE-FRANCE"
    ls = _larg(d, sur, f_sur, 8)
    _ecrire(d, (W - ls) / 2, bas_logo + 26, sur, f_sur, t["discret"], 8)

    # MISE EN PAGE ANCREE PAR LE BAS. L'ancienne version empilait les
    # elements depuis le haut : avec une photo de 820 px, le detail
    # finissait vers y=1750, soit DERRIERE la barre de reponse d'Instagram
    # — invisible pour tout le monde. Le relecteur l'a mesure le 28/10.
    # On part donc du plancher de la zone sure (y=1440) et on remonte ;
    # c'est la photo qui absorbe ce qui reste, jamais le texte.
    BAS = 1420                       # derniere ligne d'encre autorisee
    h_detail, h_titre = 46, 86
    h_past = 120 if prix else 0
    y_detail = BAS - h_detail
    y_past = y_detail - 24 - h_past
    y_titre = y_past - (46 if prix else 10) - h_titre
    haut_photo = max(int(y_titre - 28 - (bas_logo + 56)), 240)

    photo = photo_cadre(source, 780, haut_photo, rayon=30,
                        coul_bord=CREME + (255,), entiere=True)
    _ombre(img, photo, ((W - photo.width) // 2, bas_logo + 56))

    d = ImageDraw.Draw(img)
    lt = _larg(d, article, f_t, 6)
    _ecrire(d, (W - lt) / 2, y_titre, article, f_t, t["titre"], 6)

    # Pas de prix sur toutes les fiches : une pastille vide s'affichait
    # comme un rectangle orphelin sous le titre.
    if prix:
        lp = _larg(d, prix, f_p, 2)
        bw = int(lp) + 90
        bx = (W - bw) // 2
        d.rounded_rectangle([bx, y_past, bx + bw, y_past + h_past],
                            radius=20, fill=t["pastille"],
                            outline=t["filet"], width=4)
        _ecrire(d, bx + (bw - lp) / 2, y_past + 8, prix, f_p,
                t["sur_pastille"], 2)
    ld = _larg(d, detail, f_d)
    _ecrire(d, (W - ld) / 2, y_detail, detail, f_d, t["texte"])

    img.convert("RGB").save(_p(nom), quality=95)
    return _p(nom)


# --------------------------------------------------------------------------
# 2. Planche souvenir — photos inclinees facon tirages
# --------------------------------------------------------------------------

def planche_photos(sources, titre, sous, nom="F_planche.png",
                   teinte="beige"):
    t = TEINTES[teinte]
    img = fond_papier(arche=False, teinte=teinte)
    logo(img, teinte)
    places = [(120, 480, -6.5), (470, 700, 5.0), (190, 1000, 3.5)]
    for i, src in enumerate(sources[:3]):
        x, y, ang = places[i]
        ph = photo_cadre(src, 440, 440, rayon=14, angle=ang,
                         coul_bord=CREME + (255,))
        _ombre(img, ph, (x, y), flou=22, alpha=80)

    d = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(da.BODONI_B, 62)
    f_s = ImageFont.truetype(da.BODONI, 38)
    lt = _larg(d, titre, f_t, 5)
    _ecrire(d, (W - lt) / 2, 1430, titre, f_t, t["titre"], 5)
    d.line([(W / 2 - 110, 1512), (W / 2 + 110, 1512)],
           fill=t["filet"], width=2)
    ls = _larg(d, sous, f_s)
    _ecrire(d, (W - ls) / 2, 1534, sous, f_s, t["discret"])

    img.convert("RGB").save(_p(nom), quality=95)
    return _p(nom)


# --------------------------------------------------------------------------
# 3. Avant / apres
# --------------------------------------------------------------------------

def deux_temps(haut, bas, nom="G_deux_temps.png", teinte="beige",
               etiq_haut="AVANT", etiq_bas="APRÈS",
               phrase="La même pièce, deux heures plus tard."):
    """Deux images superposees, avec leurs etiquettes.

    Les libelles sont des PARAMETRES, pas des constantes : tant qu'on n'a
    pas de vraies prises « piece vide / piece dressee » au meme cadrage,
    ecrire « AVANT / APRES » serait un mensonge. On ecrit alors ce que
    l'image montre vraiment — « JOUR / SOIR », par exemple.
    """
    t = TEINTES[teinte]
    img = fond_papier(arche=False, teinte=teinte)
    logo(img, teinte)
    d = ImageDraw.Draw(img)
    f_e = ImageFont.truetype(da.BODONI_B, 40)
    f_t = ImageFont.truetype(da.BODONI_B, 58)

    for i, (src, etiq) in enumerate(((haut, etiq_haut), (bas, etiq_bas))):
        y = 500 + i * 540
        ph = photo_cadre(src, 820, 460, rayon=22,
                         coul_bord=CREME + (255,))
        _ombre(img, ph, ((W - ph.width) // 2, y))
        d = ImageDraw.Draw(img)
        le = _larg(d, etiq, f_e, 6)
        bw, bh = int(le) + 56, 76
        bx = (W - bw) // 2
        coul = t["discret"] if i == 0 else t["pastille"]
        d.rounded_rectangle([bx, y - 48, bx + bw, y - 48 + bh], radius=16,
                            fill=coul)
        _ecrire(d, bx + (bw - le) / 2, y - 34, etiq, f_e,
                t["sur_pastille"] if i else t["fond"], 6)

    lt = _larg(d, phrase, f_t)
    if lt > 880:
        f_t = ImageFont.truetype(da.BODONI_B, 44)
        lt = _larg(d, phrase, f_t)
    _ecrire(d, (W - lt) / 2, 1560, phrase, f_t, t["titre"])

    img.convert("RGB").save(_p(nom), quality=95)
    return _p(nom)


# --------------------------------------------------------------------------
# 4. Grille catalogue
# --------------------------------------------------------------------------

def grille_catalogue(articles, nom="H_grille.png", teinte="beige"):
    """articles : [(source, nom, prix), ...] — quatre maximum."""
    t = TEINTES[teinte]
    img = fond_papier(arche=False, teinte=teinte)
    d = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(da.BODONI_B, 64)
    f_n = ImageFont.truetype(da.BODONI_B, 32)
    f_p = ImageFont.truetype(da.BODONI_B, 40)

    bas_logo = logo(img, teinte)
    d = ImageDraw.Draw(img)
    titre = "NOTRE CATALOGUE"
    f_t = ImageFont.truetype(da.BODONI, 38)
    lt = _larg(d, titre, f_t, 8)
    _ecrire(d, (W - lt) / 2, bas_logo + 28, titre, f_t, t["discret"], 8)

    # Vignettes et interligne reduits : avec des cellules de 400 px et un
    # interligne de 160, la pastille de la deuxieme rangee tombait a
    # y=1634, sous la barre de reponse d'Instagram. Ici la derniere encre
    # est a y=1424, soit dans la zone sure.
    cw, ch = 390, 320
    gx, gy, ecart = 120, bas_logo + 70, 60
    for i, (src, art, prix) in enumerate(articles[:4]):
        x = gx + (i % 2) * (cw + ecart)
        y = gy + (i // 2) * (ch + 150)
        ph = photo_cadre(src, cw, ch, rayon=18,
                         coul_bord=CREME + (255,))
        _ombre(img, ph, (x - 10, y - 10), flou=14, alpha=70)
        d = ImageDraw.Draw(img)
        ln = _larg(d, art, f_n, 3)
        _ecrire(d, x + (cw - ln) / 2, y + ch + 22, art, f_n,
                t["texte"], 3)
        lp = _larg(d, prix, f_p, 2)
        bw, bh = int(lp) + 40, 58
        bx = x + (cw - bw) // 2
        d.rounded_rectangle([bx, y + ch + 68, bx + bw, y + ch + 68 + bh],
                            radius=14, fill=t["pastille"])
        _ecrire(d, bx + (bw - lp) / 2, y + ch + 78, prix, f_p,
                t["sur_pastille"], 2)

    img.convert("RGB").save(_p(nom), quality=95)
    return _p(nom)
