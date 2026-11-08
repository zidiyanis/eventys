"""Modeles de stories Eventys — 1080x1920.

Contrainte majeure de l'API : une story publiee par programme ne peut porter
AUCUN autocollant interactif (sondage, question, lien, compte a rebours) et
aucune legende. Tout ce qu'on veut dire doit donc etre INCRUSTE dans l'image.

Zone sure des stories, plus severe que celle des Reels :
  - l'interface occupe le haut (barre de progression, profil) : rien au-dessus
    de y=260
  - et le bas (champ « Envoyer un message », fleche de partage) : rien en
    dessous de y=1620
D'ou une bande utile de 1360 px de haut, bien plus etroite qu'un Reel.
"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import da

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
SORTIE = os.path.join(ICI, "_stories")

W, H = 1080, 1920
HAUT_SUR, BAS_SUR = 260, 1620

CREME, BORDEAUX, ROUGE, ENCRE = da.CREME, da.BORDEAUX, da.ROUGE, da.ENCRE
OR = (198, 162, 86)


def _p(nom):
    os.makedirs(SORTIE, exist_ok=True)
    return os.path.join(SORTIE, nom)


def _larg(d, txt, f, esp=0):
    return sum(d.textlength(c, font=f) for c in txt) + esp * max(len(txt) - 1, 0)


def _ecrire(d, x, y, txt, f, coul, esp=0):
    for c in txt:
        d.text((x, y), c, font=f, fill=coul)
        x += d.textlength(c, font=f) + esp


def _image_video(video, t, sortie):
    subprocess.run([FF, "-y", "-v", "error", "-ss", f"{t}", "-i", video,
                    "-frames:v", "1", sortie], check=True)
    return sortie


def _fond(source, assombrir=0.0, flou=0):
    """Charge une image ou un plan et le cadre en 9:16 plein ecran."""
    im = Image.open(source).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    gx, gy = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((gx, gy, gx + W, gy + H))
    if flou:
        im = im.filter(ImageFilter.GaussianBlur(flou))
    if assombrir:
        voile = Image.new("RGB", (W, H), (18, 14, 12))
        im = Image.blend(im, voile, assombrir)
    return im.convert("RGBA")


def _bandeau(d, y, haut, coul, marge=0):
    d.rectangle([marge, y, W - marge, y + haut], fill=coul)


# --------------------------------------------------------------------------
# Modele A — annoncer la publication du jour
# --------------------------------------------------------------------------

def modele_annonce(source, nom="A_annonce.png",
                   titre="NOUVELLE VIDÉO", accroche="Eventys reprend."):
    img = _fond(source, assombrir=0.18)
    d = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(da.BODONI_B, 72)
    f_a = ImageFont.truetype(da.BODONI, 44)
    f_c = ImageFont.truetype(da.BODONI_B, 34)

    lt = _larg(d, titre, f_t, 10)
    bw, bh = int(lt) + 90, 128
    bx, by = (W - bw) // 2, 470
    d.rounded_rectangle([bx + 8, by + 9, bx + bw + 8, by + bh + 9], radius=20,
                        fill=(20, 14, 12, 130))
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=20,
                        fill=ROUGE + (250,), outline=ENCRE + (255,), width=4)
    _ecrire(d, bx + (bw - lt) / 2, by + 26, titre, f_t, CREME, 10)

    la = _larg(d, accroche, f_a)
    cw, ch = int(la) + 70, 100
    cx, cy = (W - cw) // 2, by + bh + 26
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=18,
                        fill=CREME + (244,))
    _ecrire(d, cx + (cw - la) / 2, cy + 22, accroche, f_a, BORDEAUX)

    # invitation a balayer, posee au-dessus de la zone basse de l'interface
    fleche = "VOIR LA VIDÉO EN ENTIER"
    lf = _larg(d, fleche, f_c, 5)
    _ecrire(d, (W - lf) / 2, BAS_SUR - 90, fleche, f_c, CREME, 5)

    img.convert("RGB").save(_p(nom), quality=94)
    return _p(nom)


# --------------------------------------------------------------------------
# Modele B — un produit, un prix
# --------------------------------------------------------------------------

def modele_prix(source, article, prix, nom="B_prix.png"):
    img = _fond(source, assombrir=0.10)
    d = ImageDraw.Draw(img)
    f_a = ImageFont.truetype(da.BODONI_B, 62)
    f_p = ImageFont.truetype(da.BODONI_B, 104)

    la, lp = _larg(d, article, f_a, 8), _larg(d, prix, f_p, 4)
    bw = int(max(la, lp)) + 110
    bh = 290
    bx, by = (W - bw) // 2, 1180

    d.rounded_rectangle([bx + 10, by + 11, bx + bw + 10, by + bh + 11],
                        radius=24, fill=(20, 14, 12, 120))
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24,
                        fill=CREME + (248,), outline=OR + (255,), width=4)
    _ecrire(d, bx + (bw - la) / 2, by + 34, article, f_a, ENCRE, 8)
    d.line([(bx + 60, by + 128), (bx + bw - 60, by + 128)], fill=OR, width=3)
    _ecrire(d, bx + (bw - lp) / 2, by + 150, prix, f_p, BORDEAUX, 4)

    img.convert("RGB").save(_p(nom), quality=94)
    return _p(nom)


# --------------------------------------------------------------------------
# Modele C — coulisses, ton parle
# --------------------------------------------------------------------------

def modele_coulisses(source, phrase, nom="C_coulisses.png",
                     pose="16_lunettes_bras_croises"):
    img = _fond(source, assombrir=0.12)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(da.BODONI_B, 50)

    mots, lignes, cur = phrase.split(), [], []
    for m in mots:
        essai = " ".join(cur + [m])
        if d.textlength(essai, font=f) > 620 and cur:
            lignes.append(" ".join(cur)); cur = [m]
        else:
            cur.append(m)
    lignes.append(" ".join(cur))

    lw = int(max(d.textlength(l, font=f) for l in lignes)) + 76
    lh = len(lignes) * 70 + 54
    bx, by = (W - lw) // 2, 1210
    d.rounded_rectangle([bx + 8, by + 9, bx + lw + 8, by + lh + 9], radius=22,
                        fill=(20, 14, 12, 120))
    d.rounded_rectangle([bx, by, bx + lw, by + lh], radius=22,
                        fill=CREME + (246,))
    for i, l in enumerate(lignes):
        x = bx + (lw - d.textlength(l, font=f)) / 2
        d.text((x, by + 26 + i * 70), l, font=f, fill=BORDEAUX)

    chemin = os.path.join(ICI, "_cartes", "stickers", pose + ".png")
    if os.path.exists(chemin):
        lap = Image.open(chemin).convert("RGBA")
        lt = 300
        lap = lap.resize((lt, int(lap.height * lt / lap.width)), Image.LANCZOS)
        img.alpha_composite(lap, (62, by - lap.height + 26))

    img.convert("RGB").save(_p(nom), quality=94)
    return _p(nom)


# --------------------------------------------------------------------------
# Modele D — la question qui fait ecrire
# --------------------------------------------------------------------------

def modele_question(source, question="C'EST POUR QUELLE DATE ?",
                    sous="Écris-nous en message privé", nom="D_question.png"):
    # Un simple assombrissement ne suffisait pas : sur une table claire, le
    # texte creme restait illisible. On pose un vrai voile sombre.
    img = _fond(source, assombrir=0.44, flou=4)
    d = ImageDraw.Draw(img)
    f_q = ImageFont.truetype(da.BODONI_B, 82)
    f_s = ImageFont.truetype(da.BODONI, 48)

    mots, lignes, cur = question.split(), [], []
    for m in mots:
        essai = " ".join(cur + [m])
        if d.textlength(essai, font=f_q) > 700 and cur:
            lignes.append(" ".join(cur)); cur = [m]
        else:
            cur.append(m)
    lignes.append(" ".join(cur))

    y = 760
    for l in lignes:
        lq = _larg(d, l, f_q, 6)
        _ecrire(d, (W - lq) / 2, y, l, f_q, CREME, 6)
        y += 110

    d.line([(W / 2 - 170, y + 40), (W / 2 + 170, y + 40)], fill=OR, width=4)
    ls = _larg(d, sous, f_s)
    sw, sh = int(ls) + 70, 92
    sx, sy = (W - sw) // 2, y + 78
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=18,
                        fill=CREME + (244,))
    _ecrire(d, sx + (sw - ls) / 2, sy + 22, sous, f_s, BORDEAUX)

    img.convert("RGB").save(_p(nom), quality=94)
    return _p(nom)
