"""Kit graphique inspire de la video de reference fournie par Yanis.

Ce que j'ai retenu de la reference (WhatsApp Video 2026-10-12) :
  - fond papier creme avec une trame tres discrete ;
  - personnage en autocollant decoupe, liseré blanc epais, ombre portee ;
  - sous-titres : la phrase entiere est lisible, et le mot "en cours" est
    surligne en rouge, facon karaoke ;
  - etiquettes : boite blanche, filet noir franc, ombre portee decalee ;
  - badges rouges pour les chiffres.

Je garde les couleurs et la typo d'Eventys (Bodoni, creme, bordeaux) pour
les etiquettes produit, et je passe sur un grotesque gras uniquement pour
les sous-titres karaoke, qui doivent se lire en une fraction de seconde.
"""
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

import da

W, H, FPS = 1080, 1920, 30
ICI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(ICI, "_tmp_graph")

CREME = da.CREME
BORDEAUX = da.BORDEAUX
ROUGE = da.ROUGE
ENCRE = da.ENCRE
PAPIER = (240, 236, 222)

GRAS = "C:/Windows/Fonts/arialbd.ttf"


def _dir(nom):
    d = os.path.join(TMP, nom)
    os.makedirs(d, exist_ok=True)
    return d


# --------------------------------------------------------------------------
# Fond papier
# --------------------------------------------------------------------------

def fond_papier(nom="papier.png"):
    """Fond creme avec une trame quadrillee tres legere."""
    os.makedirs(TMP, exist_ok=True)
    p = os.path.join(TMP, nom)
    if os.path.exists(p):
        return p
    img = Image.new("RGB", (W, H), PAPIER)
    d = ImageDraw.Draw(img)
    pas = 46
    trait = (228, 223, 208)
    for x in range(0, W, pas):
        d.line([(x, 0), (x, H)], fill=trait, width=1)
    for y in range(0, H, pas):
        d.line([(0, y), (W, y)], fill=trait, width=1)
    img = img.filter(ImageFilter.GaussianBlur(0.4))
    img.save(p)
    return p


# --------------------------------------------------------------------------
# Sous-titres karaoke
# --------------------------------------------------------------------------

def _lignes(mots, font, dr, largeur_max):
    """Repartit les mots en lignes qui tiennent dans largeur_max."""
    lignes, cour = [], []
    for m in mots:
        essai = " ".join(cour + [m])
        if dr.textlength(essai, font=font) > largeur_max and cour:
            lignes.append(cour)
            cour = [m]
        else:
            cour.append(m)
    if cour:
        lignes.append(cour)
    return lignes


def karaoke_seq(texte, nom, dur, mots_par_sec=2.6, taille=58,
                largeur_max=880):
    """Phrase entiere lisible, mot courant surligne en rouge.

    Retourne (motif, largeur, hauteur). La boite est de taille fixe : le
    texte ne doit jamais se redisposer en cours de lecture.
    """
    d = _dir("kara_" + nom)
    # Bodoni comme TOUT le reste de la video : le grotesque gras
    # n'apparaissait qu'une fois et passait pour un oubli.
    font = ImageFont.truetype(da.BODONI_B, taille)
    dr0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    mots = texte.split()
    lignes = _lignes(mots, font, dr0, largeur_max)

    larg = int(max(dr0.textlength(" ".join(l), font=font) for l in lignes)) + 40
    inter = int(taille * 1.34)
    haut = inter * len(lignes) + 26

    n = max(int(dur * FPS), 2)
    for i in range(n):
        t = i / FPS
        actif = min(int(t * mots_par_sec), len(mots) - 1)
        img = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        k = 0
        for li, ligne in enumerate(lignes):
            lw = dr.textlength(" ".join(ligne), font=font)
            x = (larg - lw) / 2
            y = 12 + li * inter
            for m in ligne:
                coul = ROUGE if k == actif else BORDEAUX
                dr.text((x, y), m, font=font, fill=coul)
                x += dr.textlength(m + " ", font=font)
                k += 1
        img.save(os.path.join(d, f"{i:04d}.png"))
    return os.path.join(d, "%04d.png"), larg, haut


# --------------------------------------------------------------------------
# Etiquettes et badges
# --------------------------------------------------------------------------

def etiquette(texte, nom, prix=None, taille=64, decal=9):
    """Boite claire, filet franc, ombre portee decalee (facon papier colle)."""
    os.makedirs(TMP, exist_ok=True)
    f = ImageFont.truetype(da.BODONI_B, taille)
    fp = ImageFont.truetype(da.BODONI_B, int(taille * 1.05))
    dr0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    esp = 4
    lt = sum(dr0.textlength(c, font=f) for c in texte) + esp * (len(texte) - 1)
    bw, bh = int(lt) + 60, taille + 46
    pw, ph = 0, 0
    if prix:
        lp = sum(dr0.textlength(c, font=fp) for c in prix) + esp * (len(prix) - 1)
        pw, ph = int(lp) + 54, int(taille * 1.05) + 36

    larg = max(bw, pw) + decal + 8
    haut = bh + (ph + 14 if prix else 0) + decal + 8
    img = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # etiquette principale
    R = 18   # angles arrondis, demande de Yanis le 2026-10-15
    d.rounded_rectangle([decal, decal, decal + bw, decal + bh], radius=R,
                        fill=(26, 20, 19, 230))
    d.rounded_rectangle([0, 0, bw, bh], radius=R,
                        fill=CREME + (250,), outline=ENCRE + (255,), width=4)
    x = (bw - lt) / 2
    for c in texte:
        d.text((x, 20), c, font=f, fill=BORDEAUX)
        x += d.textlength(c, font=f) + esp

    # badge prix
    if prix:
        y0 = bh + 14
        d.rounded_rectangle([decal, y0 + decal, decal + pw, y0 + decal + ph],
                            radius=R, fill=(26, 20, 19, 230))
        d.rounded_rectangle([0, y0, pw, y0 + ph], radius=R,
                            fill=ROUGE + (252,), outline=ENCRE + (255,), width=4)
        x = (pw - lp) / 2
        for c in prix:
            d.text((x, y0 + 14), c, font=fp, fill=CREME)
            x += d.textlength(c, font=fp) + esp

    p = os.path.join(TMP, nom)
    img.save(p)
    return p, larg, haut


def etiquette_pop_seq(texte, nom, dur, prix=None, taille=64):
    """Etiquette qui claque : elle depasse sa taille puis se cale."""
    base, bl, bh = etiquette(texte, f"_base_{nom}.png", prix=prix, taille=taille)
    src = Image.open(base).convert("RGBA")
    d = _dir("pop_" + nom)
    n = max(int(dur * FPS), 2)
    duree_pop = 0.22
    for i in range(n):
        t = i / FPS
        if t >= duree_pop:
            ech = 1.0
        else:
            p = t / duree_pop
            ech = 0.55 + 0.52 * p + 0.10 * (1 - p) * (1 if p > 0.6 else p / 0.6)
            ech = min(ech, 1.12)
        img = Image.new("RGBA", (bl, bh), (0, 0, 0, 0))
        w2, h2 = max(int(bl * ech), 2), max(int(bh * ech), 2)
        red = src.resize((w2, h2), Image.LANCZOS)
        img.alpha_composite(red, ((bl - w2) // 2, (bh - h2) // 2))
        img.save(os.path.join(d, f"{i:04d}.png"))
    return os.path.join(d, "%04d.png"), bl, bh


# --------------------------------------------------------------------------
# Checklist qui se coche
# --------------------------------------------------------------------------

def checklist_seq(titre, items, coches, nom, dur, taille=42):
    """Panneau liste ; `coches` = nombre de lignes deja validees sur ce plan.

    La ligne qui vient d'etre cochee apparait en bordeaux avec sa coche qui
    se dessine, les precedentes restent en encre, les suivantes sont pales.
    """
    d = _dir("check_" + nom)
    f = ImageFont.truetype(da.BODONI_B, taille)
    ft = ImageFont.truetype(da.BODONI_B, int(taille * 1.05))
    dr0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    larg = int(max([dr0.textlength(i, font=f) for i in items]
                   + [dr0.textlength(titre, font=ft)])) + 150
    inter = int(taille * 1.62)
    haut = int(taille * 1.9) + inter * len(items) + 34

    n = max(int(dur * FPS), 2)
    for k in range(n):
        t = k / FPS
        img = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        dr.rounded_rectangle([0, 0, larg - 1, haut - 1], radius=22,
                             fill=CREME + (238,), outline=ENCRE + (90,), width=3)
        dr.text((28, 22), titre, font=ft, fill=BORDEAUX)
        dr.line([(28, int(taille * 1.62)), (larg - 28, int(taille * 1.62))],
                fill=ENCRE + (70,), width=2)
        for i, it in enumerate(items):
            y = int(taille * 1.9) + i * inter
            fait = i < coches
            neuf = (i == coches - 1)
            coul = BORDEAUX if neuf else (ENCRE if fait else (176, 168, 160))
            # case
            dr.rounded_rectangle([28, y + 4, 28 + taille - 10, y + taille - 6],
                                 radius=6, outline=coul + (255,), width=3)
            if fait:
                # la coche se dessine sur 0.25 s pour la ligne qui vient de tomber
                p = min(t / 0.25, 1.0) if neuf else 1.0
                x0, y0 = 34, y + int(taille * 0.52)
                pts = [(x0, y0), (x0 + 9, y0 + 10), (x0 + 24, y0 - 12)]
                if p > 0.5:
                    dr.line([pts[0], pts[1]], fill=coul, width=5)
                    q = (p - 0.5) / 0.5
                    bx = pts[1][0] + (pts[2][0] - pts[1][0]) * q
                    by = pts[1][1] + (pts[2][1] - pts[1][1]) * q
                    dr.line([pts[1], (bx, by)], fill=coul, width=5)
                else:
                    q = p / 0.5
                    bx = pts[0][0] + (pts[1][0] - pts[0][0]) * q
                    by = pts[0][1] + (pts[1][1] - pts[0][1]) * q
                    dr.line([pts[0], (bx, by)], fill=coul, width=5)
            dr.text((28 + taille + 18, y), it, font=f, fill=coul)
        img.save(os.path.join(d, f"{k:04d}.png"))
    return os.path.join(d, "%04d.png"), larg, haut


# --------------------------------------------------------------------------
# Bloc d'appel a l'action + signature de marque
# --------------------------------------------------------------------------

def bloc_cta(question, compte, nom="cta.png", taille=66):
    """Bandeau bordeaux plein (la question) + bandeau creme (le compte).

    Le CTA doit se distinguer au premier coup d'oeil des bulles de vannes :
    meme forme et meme couleur que les blagues, l'oeil ne faisait plus la
    difference entre une plaisanterie et l'action a faire. Un bandeau plein
    se lit aussi en moins d'une seconde, la ou une bulle qui s'ecrit en
    demande trois.
    """
    f = ImageFont.truetype(da.BODONI_B, taille)
    fc = ImageFont.truetype(da.BODONI, int(taille * 0.62))
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    esp = 4
    lq = sum(d0.textlength(c, font=f) for c in question) + esp * (len(question) - 1)
    lc = d0.textlength(compte, font=fc)

    bw, bh = int(lq) + 76, taille + 50
    cw, ch = int(lc) + 54, int(taille * 0.62) + 32
    larg = max(bw, cw) + 12
    haut = bh + 12 + ch + 12
    img = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    x0 = (larg - bw) // 2
    d.rounded_rectangle([x0 + 9, 9, x0 + bw + 9, bh + 9], radius=18,
                        fill=(26, 20, 19, 215))
    d.rounded_rectangle([x0, 0, x0 + bw, bh], radius=18,
                        fill=ROUGE + (252,), outline=ENCRE + (255,), width=4)
    x = x0 + (bw - lq) / 2
    for c in question:
        d.text((x, 20), c, font=f, fill=CREME)
        x += d.textlength(c, font=f) + esp

    y0 = bh + 12
    x1 = (larg - cw) // 2
    d.rounded_rectangle([x1 + 7, y0 + 7, x1 + cw + 7, y0 + ch + 7], radius=14,
                        fill=(26, 20, 19, 180))
    d.rounded_rectangle([x1, y0, x1 + cw, y0 + ch], radius=14,
                        fill=CREME + (250,), outline=ENCRE + (235,), width=3)
    d.text((x1 + (cw - lc) / 2, y0 + 12), compte, font=fc, fill=BORDEAUX)

    p = os.path.join(TMP, nom)
    os.makedirs(TMP, exist_ok=True)
    img.save(p)
    return p, larg, haut


def signature(compte="@eventys.paris", nom="signature.png", taille=34):
    """Petit filigrane permanent : sans lui, une video repartagee en story
    ne dit a personne qui contacter."""
    p = os.path.join(TMP, nom)
    os.makedirs(TMP, exist_ok=True)
    f = ImageFont.truetype(da.BODONI_B, taille)
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lt = int(d0.textlength(compte, font=f))
    img = Image.new("RGBA", (lt + 24, taille + 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # ombre portee douce : le filigrane doit tenir sur fond clair comme sombre
    d.text((12 + 2, 10 + 2), compte, font=f, fill=(20, 14, 13, 150))
    d.text((12, 10), compte, font=f, fill=(250, 246, 240, 232))
    img.save(p)
    return p, lt + 24, taille + 22
