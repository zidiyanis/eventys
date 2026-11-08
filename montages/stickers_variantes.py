"""80 stickers a partir des stickers valides, SANS redessiner le lapin.

Le personnage reste le meme (pixels d'origine) ; on ajoute un effet dessine
autour (coeurs, etoiles, sueur, ?, !, Zzz, notes, colere, confettis, ampoule),
et on retourne les poses SANS logo (le logo serait a l'envers).

    python montages/stickers_variantes.py
Sortie : montages/_cartes/stickers_80/ + planches de controle.
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
CARTES = os.path.join(ICI, "_cartes")
SRC_V2 = os.path.join(CARTES, "stickers_v2")        # 00-11 redecoupes entiers
SRC_OLD = os.path.join(CARTES, "stickers")           # 12-17 (chemise / t-shirt)
SORTIE = os.path.join(CARTES, "stickers_80")

BORDEAUX = (107, 30, 46, 255)
ROUGE = (226, 48, 62, 255)
OR = (255, 196, 43, 255)
BLEU = (86, 170, 236, 255)
ROSE = (255, 120, 150, 255)
SS = 2  # sur-echantillonnage (4 fait deborder la memoire)


def police(taille, gras=True):
    for nom in ("arialbd.ttf" if gras else "arial.ttf", "seguisym.ttf"):
        try:
            return ImageFont.truetype(os.path.join(r"C:\Windows\Fonts", nom), taille)
        except OSError:
            continue
    return ImageFont.load_default()


def coeur(d, cx, cy, t, col):
    pts = []
    for k in range(0, 360, 4):
        a = math.radians(k)
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a)
              - math.cos(4 * a))
        pts.append((cx + x * t / 34, cy + y * t / 34))
    d.polygon(pts, fill=col)


def etoile(d, cx, cy, t, col):
    pts = []
    for k in range(8):
        r = t if k % 2 == 0 else t * 0.28
        a = math.radians(k * 45 - 90)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=col)


def goutte(d, cx, cy, t, col):
    d.ellipse([cx - t * .5, cy - t * .1, cx + t * .5, cy + t * .9], fill=col)
    d.polygon([(cx, cy - t * .9), (cx - t * .45, cy + t * .25),
               (cx + t * .45, cy + t * .25)], fill=col)


def texte(d, cx, cy, s, t, col):
    f = police(int(t))
    b = d.textbbox((0, 0), s, font=f)
    d.text((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2), s, font=f, fill=col)


def colere(d, cx, cy, t, col):
    e = max(int(t * .16), 3)
    for dx, dy, a0 in ((-1, -1, 90), (1, -1, 180), (-1, 1, 0), (1, 1, 270)):
        bx, by = cx + dx * t * .32, cy + dy * t * .32
        d.arc([bx - t * .32, by - t * .32, bx + t * .32, by + t * .32],
              a0, a0 + 90, fill=col, width=e)


def eclair(d, cx, cy, t):
    pts = [(.15, -.6), (-.35, .08), (-.02, .08), (-.2, .62), (.38, -.12),
           (.03, -.12), (.2, -.6)]
    d.polygon([(cx + x * t, cy + y * t) for x, y in pts], fill=OR)


def confettis(d, cx, cy, t, col, graine=1):
    r = random.Random(graine)
    for _ in range(16):
        x, y = cx + r.uniform(-1.1, 1.1) * t, cy + r.uniform(-.7, .7) * t
        c = r.choice([ROUGE, OR, BLEU, ROSE, BORDEAUX])
        s = r.uniform(.07, .14) * t
        if r.random() < .5:
            d.ellipse([x - s, y - s, x + s, y + s], fill=c)
        else:
            d.rectangle([x - s, y - s * .5, x + s, y + s * .5], fill=c)


def ampoule(d, cx, cy, t, col):
    d.ellipse([cx - t * .38, cy - t * .55, cx + t * .38, cy + t * .21], fill=OR)
    d.rectangle([cx - t * .2, cy + t * .15, cx + t * .2, cy + t * .42],
                fill=(150, 150, 160, 255))
    for k in range(-2, 3):
        a = math.radians(k * 32 - 90)
        d.line([(cx + math.cos(a) * t * .55, cy - t * .17 + math.sin(a) * t * .6),
                (cx + math.cos(a) * t * .85, cy - t * .17 + math.sin(a) * t * .9)],
               fill=OR, width=max(int(t * .08), 3))


# nom -> fonction(draw, cx, cy, taille)
EFFETS = {
    "coeurs": lambda d, x, y, t: (coeur(d, x, y, t, ROUGE),
                                  coeur(d, x - t * .7, y + t * .6, t * .6, ROSE),
                                  coeur(d, x + t * .6, y + t * .8, t * .5, ROUGE)),
    "etoiles": lambda d, x, y, t: (etoile(d, x, y, t, OR),
                                   etoile(d, x - t * .8, y + t * .5, t * .55, OR),
                                   etoile(d, x + t * .7, y + t * .7, t * .4, OR)),
    "sueur": lambda d, x, y, t: (goutte(d, x, y, t * .8, BLEU),
                                 goutte(d, x + t * .6, y + t * .5, t * .5, BLEU)),
    "question": lambda d, x, y, t: texte(d, x, y, "?", t * 1.5, BORDEAUX),
    "exclamation": lambda d, x, y, t: (texte(d, x, y, "!", t * 1.6, ROUGE),
                                       texte(d, x + t * .55, y + t * .1, "!", t * 1.2, ROUGE)),
    "zzz": lambda d, x, y, t: (texte(d, x, y, "Z", t * 1.0, BORDEAUX),
                               texte(d, x + t * .6, y - t * .6, "z", t * .75, BORDEAUX),
                               texte(d, x + t * 1.1, y - t * 1.1, "z", t * .55, BORDEAUX)),
    "notes": lambda d, x, y, t: (texte(d, x, y, "\u266a", t * 1.5, BORDEAUX),
                                 texte(d, x + t * .8, y - t * .4, "\u266b", t * 1.2, BORDEAUX)),
    "eclair": lambda d, x, y, t: eclair(d, x, y, t * 1.3),
    "confettis": lambda d, x, y, t: confettis(d, x, y, t * 1.6, None, int(x)),
    "idee": lambda d, x, y, t: ampoule(d, x, y, t * 1.4, None),
}
NOMS = list(EFFETS)


def charger_poses():
    poses = []
    for dossier in (SRC_V2, SRC_OLD):
        for f in sorted(os.listdir(dossier)):
            if not f.lower().endswith(".png") or f.startswith("_"):
                continue
            num = int(f[:2])
            if dossier == SRC_V2 and num > 11:
                continue
            if dossier == SRC_OLD and num < 12:
                continue
            poses.append((f[:-4], Image.open(os.path.join(dossier, f)).convert("RGBA")))
    return poses


def rogner(im, marge=14):
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    im = im.crop(bb)
    out = Image.new("RGBA", (im.width + 2 * marge, im.height + 2 * marge), (0, 0, 0, 0))
    out.paste(im, (marge, marge), im)
    return out


def avec_effet(base, effet, cote):
    w, h = base.size
    pad_x, pad_h = int(w * .30), int(h * .30)
    cw, ch = w + 2 * pad_x, h + pad_h
    toile = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    toile.paste(base, (pad_x, pad_h), base)
    t = w * .20
    cx = pad_x + (w * .86 if cote == "d" else w * .14)
    cy = pad_h * .62
    # couche d'effet sur-echantillonnee
    couche = Image.new("RGBA", (cw * SS, ch * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(couche)
    EFFETS[effet](d, cx * SS, cy * SS, t * SS)
    couche = couche.resize((cw, ch), Image.LANCZOS)
    # contour blanc "autocollant" autour de l'effet
    alpha = couche.getchannel("A")
    halo = alpha.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(.6))
    blanc = Image.new("RGBA", (cw, ch), (255, 255, 255, 255))
    blanc.putalpha(halo)
    toile.alpha_composite(blanc)
    toile.alpha_composite(couche)
    return rogner(toile)


def main():
    os.makedirs(SORTIE, exist_ok=True)
    poses = charger_poses()
    print(len(poses), "poses de base")
    sans_logo = {n for n, _ in poses if int(n[:2]) >= 12}
    liste = []
    for n, im in poses:
        liste.append((n, im, "base"))
        if n in sans_logo:
            liste.append((n + "_miroir", im.transpose(Image.FLIP_LEFT_RIGHT), "miroir"))
    total = 0
    for i, (n, im, _) in enumerate(liste):
        rogner(im).save(os.path.join(SORTIE, f"{n}.png"))
        total += 1
    # 3 effets differents par pose de base, decales pour varier
    k = 0
    for i, (n, im, genre) in enumerate(liste):
        if genre == "miroir":
            continue
        for j in range(3):
            effet = NOMS[(i * 3 + j + i // 3) % len(NOMS)]
            cote = "d" if (i + j) % 2 == 0 else "g"
            avec_effet(im, effet, cote).save(
                os.path.join(SORTIE, f"{n}__{effet}.png"))
            total += 1
            k += 1
    print(total, "stickers ecrits dans", SORTIE)


if __name__ == "__main__":
    main()
