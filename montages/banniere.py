"""Banniere de Page Facebook pour Eventys — version au logo et aux dessins.

Trois versions ont ete rejetees avant celle-ci :
  1. un fond genere par IA (villa toscane) : « trop IA » ;
  2. un triptyque de trois photos reelles : trop charge ;
  3. une version epuree au lettrage Bodoni : bonne, mais ce n'etait pas le
     vrai logo d'Eventys.

Yanis a ensuite fourni son logo (EVENT + monogramme YS) et demande
explicitement : aucune photo incrustee, et des MEUBLES DESSINES.

D'ou cette version : le logo d'origine, et des illustrations au trait de la
chaise Napoleon, de la table dressee et de l'arche — generees puis
detourees, dans la teinte terracotta du logo.

Format : 1640x624 (le double de l'affichage bureau 820x312).
  - coin BAS GAUCHE laisse vide : la photo de profil s'y pose sur ordinateur
  - tout ce qui compte reste CENTRE : sur mobile, Facebook rogne les cotes
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import da

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
LOGO = os.path.join(RACINE, "assets", "LOGO_eventys.png")
ILLUS = os.path.join(RACINE, "assets", "illus")
SORTIE = os.path.join(ICI, "BANNIERE_facebook.png")

L, H = 1640, 624

# Palette relevee directement dans le logo de Yanis
PAPIER = (240, 237, 236)
TERRA = (191, 87, 85)
BORDEAUX = (111, 47, 47)
OR = (198, 162, 86)
GRIS = (138, 124, 118)

SUR_MOBILE = 1280          # bande centrale conservee par le rognage mobile


def _larg(d, t, f, esp):
    return sum(d.textlength(c, font=f) for c in t) + esp * max(len(t) - 1, 0)


def _ecrire(d, x, y, t, f, coul, esp):
    for c in t:
        d.text((x, y), c, font=f, fill=coul)
        x += d.textlength(c, font=f) + esp


def _dessin(nom, haut, opacite=255):
    """Charge une illustration detouree, mise a l'echelle par sa hauteur."""
    im = Image.open(os.path.join(ILLUS, nom)).convert("RGBA")
    r = haut / im.height
    im = im.resize((max(int(im.width * r), 1), haut), Image.LANCZOS)
    if opacite < 255:
        a = im.split()[3].point(lambda v: int(v * opacite / 255))
        im.putalpha(a)
    return im


def _logo(haut):
    """Logo d'origine, fond rendu transparent."""
    im = Image.open(LOGO).convert("RGB")
    import numpy as np
    a = np.array(im).astype(int)
    clarte = a.mean(axis=2)
    alpha = np.clip((236 - clarte) * 8, 0, 255).astype(np.uint8)
    out = Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), "RGBA")
    bb = out.getbbox()
    out = out.crop(bb)
    r = haut / out.height
    return out.resize((int(out.width * r), haut), Image.LANCZOS)


def construire():
    img = Image.new("RGB", (L, H), PAPIER)

    # Lueur chaude : evite l'aplat mort sans ajouter de motif.
    lueur = Image.new("L", (L, H), 0)
    ImageDraw.Draw(lueur).ellipse([-280, -220, L + 280, H + 220], fill=104)
    img = Image.composite(Image.new("RGB", (L, H), (250, 247, 245)), img,
                          lueur.filter(ImageFilter.GaussianBlur(200)))
    img = img.convert("RGBA")

    # --- les meubles dessines, STRICTEMENT dans les marges ---
    # Premiere tentative : ils etaient places au centre, et le logo comme le
    # sous-titre leur passaient dessus — illisible. Le bandeau central
    # (x de 380 a 1260) reste donc entierement vide, c'est la place du logo
    # et de la ligne de texte, qui fait a elle seule 820 px de large.
    CLAIR_G, CLAIR_D = 380, 1260

    arche = _dessin("arche_detoure.png", 372, opacite=74)
    img.alpha_composite(arche, (34, 128))

    ch = _dessin("chaise_detoure.png", 318, opacite=132)
    img.alpha_composite(ch, (CLAIR_G - ch.width - 6, H - 318 - 104))

    table = _dessin("table_detoure.png", 268, opacite=96)
    img.alpha_composite(table, (L - table.width - 30, H - 268 - 128))

    ch2 = _dessin("chaise_detoure.png", 300, opacite=124)
    img.alpha_composite(ch2, (CLAIR_D + 8, H - 300 - 112))

    # --- le logo, au centre ---
    lg = _logo(268)
    img.alpha_composite(lg, ((L - lg.width) // 2, 118))

    d = ImageDraw.Draw(img)
    f_s = ImageFont.truetype(da.BODONI, 30)
    f_c = ImageFont.truetype(da.BODONI, 26)

    sous, esp = "MOBILIER ÉVÉNEMENTIEL   ·   ÎLE-DE-FRANCE", 8
    ls = _larg(d, sous, f_s, esp)
    y = 118 + lg.height + 10
    d.line([(L / 2 - ls / 2, y), (L / 2 - 46, y)], fill=OR, width=2)
    d.line([(L / 2 + 46, y), (L / 2 + ls / 2, y)], fill=OR, width=2)
    d.polygon([(L / 2, y - 7), (L / 2 + 8, y), (L / 2, y + 7), (L / 2 - 8, y)],
              fill=OR)
    _ecrire(d, (L - ls) / 2 + esp / 2, y + 24, sous, f_s, GRIS, esp)

    compte = "@eventys.paris"
    lc = _larg(d, compte, f_c, 3)
    _ecrire(d, (L - lc) / 2 + 1.5, y + 78, compte, f_c, TERRA, 3)

    img.convert("RGB").save(SORTIE, quality=97)
    return SORTIE, (L, H)


if __name__ == "__main__":
    print(*construire())
