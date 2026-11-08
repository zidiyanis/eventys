"""Trois directions de montage differentes, pour que Yanis choisisse un style.

Ce module ne reprend PAS les cut-lists de `build.py` : chaque style a son
propre choix de plans, son propre rythme et sa propre typo animee. Le but
n'est pas de livrer trois fois la meme video avec un vernis different, mais
de proposer trois partis pris reellement distincts.

  A : "Le lapin te guide"  - mascotte presente, chaleureux, rythme moyen
  B : "Editorial"          - premium, lent, typographie, mascotte en signature
  C : "Punchy"             - coupes rapides, gros texte qui claque, stickers

Technique : les animations de texte sont fabriquees en suites de PNG avec
Pillow (ffmpeg/drawtext ne sait faire ni interlettrage ni bicolore ni
easing), puis composees par ffmpeg. Les mouvements simples (glissade,
fondu) passent par des expressions `overlay` sur un PNG fixe, moins couteux
qu'une suite d'images.
"""
import math
import os
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

import build as B
import da

W, H = 1080, 1920
FPS = 30
FF = B.FF
OUT = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(OUT, "_tmp_styles")
STICKERS = os.path.join(OUT, "_cartes", "stickers")

CREME = da.CREME
BORDEAUX = da.BORDEAUX
ROUGE = da.ROUGE
ENCRE = da.ENCRE

# Zone sure : rien au-dessus de y=230, rien sous y=1440, 230 px libres a droite.
SAFE_TOP, SAFE_BAS, SAFE_DROITE = 230, 1440, 230
X_MAX = W - SAFE_DROITE  # 850


def _dir(nom):
    d = os.path.join(TMP, nom)
    os.makedirs(d, exist_ok=True)
    return d


def ease_out(t):
    """Decelere en fin de course (cubic)."""
    return 1 - (1 - t) ** 3


def ease_overshoot(t, amp=1.25):
    """Depasse legerement puis revient : donne du punch a une arrivee."""
    if t >= 1:
        return 1.0
    return 1 + (amp - 1) * math.sin(math.pi * t) * (1 - t) + (t - 1) * 0 + (t ** 1) - (t ** 1) + (ease_out(t) - 1)


def _ecrire_espace(draw, x, y, texte, font, fill, espace):
    for c in texte:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + espace


def _largeur_espace(draw, texte, font, espace):
    return sum(draw.textlength(c, font=font) for c in texte) + espace * max(0, len(texte) - 1)


# --------------------------------------------------------------------------
# Rendu d'un plan source (tonemap HDR + cadrage + Ken Burns)
# --------------------------------------------------------------------------

def plan(sortie, stem, folder, t0, t1, zoom_a=1.0, zoom_b=1.0, speed=1.0,
         grade=True):
    """Extrait un plan, le met au format 9:16 avec un Ken Burns zoom_a->zoom_b."""
    path = B.src(stem, folder)
    dur_in = t1 - t0
    # `fps` EN PREMIER : les rushes Contenue Vlog_ sont en 120 i/s. Tonemapper
    # et zoomer 120 images/s pour n'en garder que 30 multipliait le temps de
    # rendu par 4 (16 min pour un plan de 2 s) et quadruplait le debit du
    # fichier. On decime d'abord, on filtre ensuite.
    chaine = f"fps={FPS}"
    if B.est_hdr(path):
        chaine += "," + B.TONEMAP
    chaine += "," + _kenburns(zoom_a, zoom_b, dur_in)
    if speed != 1.0:
        chaine += f",setpts=PTS/{speed}"
    if grade:
        chaine += ",eq=contrast=1.04:saturation=1.03:gamma=1.01"
    subprocess.run([
        FF, "-y", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", path,
        "-vf", chaine + ",format=yuv420p",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", sortie,
    ], check=True)
    return dur_in / speed


def _cadre(z, ancre=0.5, ancre_x=0.5):
    """Cadrage 9:16 fixe, zoom constant z.

    `ancre`   : point de coupe VERTICAL,   0 = haut,    1 = bas.
    `ancre_x` : point de coupe HORIZONTAL, 0 = gauche,  1 = droite.
    """
    zw, zh = int(W * z), int(H * z)
    return (f"scale={zw}:{zh}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{H}:(in_w-out_w)*{ancre_x:.3f}:"
            f"(in_h-out_h)*{ancre:.3f},setsar=1")


def _kenburns(za, zb, dur, ancre=0.5, ancre_x=0.5):
    """Zoom anime continu za -> zb sur `dur` secondes.

    ATTENTION, LE PIEGE : beaucoup de nos rushes portent une metadonnee
    `rotation=-90` — tout le dossier Contenue Vlog_, par exemple. ffprobe
    annonce alors 3840x2160, mais ffmpeg les redresse au decodage et
    travaille sur du 2160x3840, c'est-a-dire du 9:16 EXACT. Sur ceux-la,
    rien n'est jamais recadre et NI `ancre` NI `ancre_x` n'ont d'effet :
    ce qu'on voit dans le rush est exactement ce qu'on aura a l'ecran.
    Pour savoir a qui on a affaire :

        ffprobe -v error -select_streams v:0                 -show_entries stream_side_data=rotation <fichier>

    `ancre_x` est le point de recadrage HORIZONTAL, de 0 (bord gauche de
    l'image source) a 1 (bord droit). Ajoute le 28 octobre : sur une source
    16:9 agrandie pour couvrir du 9:16, la hauteur est deja exacte et c'est
    la LARGEUR qu'on coupe — l'ancre verticale n'y change donc rien, et le
    seul reglage utile est celui-ci. Il sert surtout a sortir du cadre un
    objet de marque tierce : un camion floque, un sac, une bouteille. Nos
    rushes en sont pleins et c'est la raison la plus frequente de jeter un
    plan par ailleurs bon.

    `ancre` est le point de recadrage VERTICAL, de 0 (haut de l'image
    source) a 1 (bas). Il ne compte que pour les sources 4:3 ou verticales. Il a ete ajoute le 27 octobre apres trois erreurs
    identiques : nos rushes sont filmes en PAYSAGE, le 9:16 en prend une
    bande, et un recadrage centre garde systematiquement le haut de la piece
    — le sapin, le mur, le televiseur — en coupant la table, qui est dans la
    moitie basse. Le plan « 12 kits vaisselle » montrait un sapin.

    Passe par `zoompan` : `crop` ne reevalue PAS w/h dans le temps (seules x
    et y sont dynamiques), donc une taille de crop variable fait echouer le
    filtre (EINVAL). On cadre d'abord en 9:16 a 2x, puis zoompan reechantillonne
    vers 1080x1920 -- le surechantillonnage evite le tremblement typique de
    zoompan sur petits pas de zoom.
    """
    if abs(za - zb) < 1e-3:
        return _cadre(max(za, 1.0), ancre, ancre_x)
    frames = max(int(round(dur * FPS)), 1)
    zexpr = f"{za:.4f}+({zb - za:.4f})*min(on/{frames},1)"
    # Intermediaire juste au-dessus du zoom max : 2x faisait sauter zoompan
    # en memoire (ENOMEM) sur les sources 4K.
    k = max(za, zb, 1.0) * 1.15
    iw, ih = int(W * k) // 2 * 2, int(H * k) // 2 * 2
    return (f"scale={iw}:{ih}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={iw}:{ih}:(in_w-out_w)*{ancre_x:.3f}:"
            f"(in_h-out_h)*{ancre:.3f},setsar=1,"
            f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d=1:s={W}x{H}:fps={FPS},setsar=1")


def concat(parts, sortie):
    """Coupes franches. Plus net que le fondu croise sur des plans dissemblables."""
    lst = os.path.join(TMP, "liste.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts:
            f.write("file '" + p.replace("\\", "/") + "'\n")
    subprocess.run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", sortie], check=True)
    return sortie


def pose(video, calques, sortie, dur):
    """Pose des calques sur UN plan court (temps relatif au debut du plan).

    Un overlay par plan, et non sur la video entiere : chaque appel ffmpeg
    n'a alors que 1 a 2 entrees PNG sur 1 a 3 secondes, au lieu de dix flux
    RGBA infinis sur toute la video (ce qui etait injouable en temps).
    """
    if not calques:
        shutil.copy(video, sortie)
        return sortie
    cmd = [FF, "-y", "-v", "error", "-i", video]
    for c in calques:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}",
                "-i", c["png"]]
    filt, prev = [], "0:v"
    for i, c in enumerate(calques, start=1):
        lab, out = f"c{i}", ("vout" if i == len(calques) else f"v{i}")
        ech = f"scale={c['w']}:-1," if c.get("w") else ""
        f_in, f_out = c.get("fade", 0.18), c.get("fade", 0.18)
        t0, t1 = c["t0"], min(c["t1"], dur)
        filt.append(
            f"[{i}:v]{ech}format=rgba,"
            f"fade=t=in:st={t0:.3f}:d={f_in:.3f}:alpha=1,"
            f"fade=t=out:st={max(t1 - f_out, t0 + 0.01):.3f}:d={f_out:.3f}:alpha=1[{lab}]"
        )
        filt.append(
            # format=auto obligatoire : sans lui l'overlay convertit le
            # calque en yuv420 (sans canal alpha) et le degrade disparait.
            f"[{prev}][{lab}]overlay=x='{c['x']}':y='{c['y']}':format=auto:"
            f"enable='between(t,{t0:.3f},{t1:.3f})'[{out}]"
        )
        prev = out
    subprocess.run([
        *cmd, "-filter_complex", ";".join(filt), "-map", f"[{prev}]",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", sortie,
    ], check=True)
    return sortie


# ==========================================================================
# Cartes : une typo differente par style
# ==========================================================================

def _png(nom):
    return os.path.join(_dir("cartes"), nom)


def mesure_bulle(texte, prix=None):
    """Dimensions d'une bulle SANS la dessiner.

    Sert a calculer la position horizontale AVANT le rendu, pour que la
    queue de la bulle tombe pile au-dessus de la mascotte.
    """
    f_txt = ImageFont.truetype(da.BODONI, 44)
    f_prix = ImageFont.truetype(da.BODONI_B, 64)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    esp = 2
    lt = _largeur_espace(d0, texte, f_txt, esp)
    lp = _largeur_espace(d0, prix, f_prix, esp) if prix else 0
    larg = int(max(lt, lp)) + 84
    haut = 148 if prix else 104
    return larg, haut + 20


def bulle(texte, prix, nom, queue_x=None):
    """Bulle de dialogue. `queue_x` = abscisse de la pointe DANS la bulle.

    Avant, la queue etait clouee a 70 px du bord gauche : des que la
    mascotte passait a droite, la bulle pointait dans le vide. Maintenant
    l'appelant impose ou la pointe doit tomber.
    """
    f_txt = ImageFont.truetype(da.BODONI, 44)
    f_prix = ImageFont.truetype(da.BODONI_B, 64)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    esp = 2
    lt = _largeur_espace(d0, texte, f_txt, esp)
    lp = _largeur_espace(d0, prix, f_prix, esp) if prix else 0
    larg = int(max(lt, lp)) + 84
    haut = 148 if prix else 104
    img = Image.new("RGBA", (larg, haut + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, larg - 1, haut - 1], radius=32, fill=CREME + (243,))
    qx = 70 if queue_x is None else max(44, min(int(queue_x), larg - 44))
    d.polygon([(qx - 10, haut - 2), (qx + 26, haut - 2), (qx, haut + 18)],
              fill=CREME + (243,))
    _ecrire_espace(d, (larg - lt) / 2, 28, texte, f_txt, BORDEAUX, esp)
    if prix:
        _ecrire_espace(d, (larg - lp) / 2, 78, prix, f_prix, ROUGE, esp)
    p = _png(nom)
    img.save(p)
    return p, larg, haut + 20


def edito(titre, prix, nom):
    """Style B : filet fin + capitales tres espacees, beaucoup de vide."""
    f_t = ImageFont.truetype(da.BODONI, 52)
    f_p = ImageFont.truetype(da.BODONI_I, 42)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    esp = 13
    lt = _largeur_espace(d0, titre, f_t, esp)
    lp = _largeur_espace(d0, prix, f_p, 3) if prix else 0
    larg = int(max(lt, lp, 420)) + 24
    haut = 168 if prix else 104
    img = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([(larg / 2 - 58, 5), (larg / 2 + 58, 5)], fill=CREME + (230,), width=3)
    _ecrire_espace(d, (larg - lt) / 2, 34, titre, f_t, CREME, esp)
    if prix:
        _ecrire_espace(d, (larg - lp) / 2, 106, prix, f_p, CREME, 3)
    p = _png(nom)
    img.save(p)
    return p, larg, haut


def punch(texte, nom, accent=False):
    """Style C : gros bloc, texte large, lisible en une demi-seconde."""
    taille = 90 if len(texte) <= 14 else 68
    f = ImageFont.truetype(da.BODONI_B, taille)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    esp = 5
    lt = _largeur_espace(d0, texte, f, esp)
    larg, haut = int(lt) + 68, taille + 56
    img = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, larg - 1, haut - 1], radius=12,
                        fill=(ROUGE if accent else CREME) + (248,))
    _ecrire_espace(d, (larg - lt) / 2, 20, texte, f,
                   CREME if accent else BORDEAUX, esp)
    p = _png(nom)
    img.save(p)
    return p, larg, haut



def voile(nom="voile.png", haut=920, force=150, montee=0.22):
    """Degrade sombre : monte vite sur `montee` du haut, puis reste plein.

    Style B ecrit en creme : sans voile, le texte disparait sur les plans
    clairs (chaises blanches en plein jour). Un degrade classique (opacite
    max tout en bas) ne servait a rien : le texte est a 130 px du haut du
    voile, la ou l'opacite valait encore 9/255. D'ou le plateau.
    """
    col = Image.new("RGBA", (1, haut), (0, 0, 0, 0))
    px = col.load()
    lim = max(int(haut * montee), 1)
    for y in range(haut):
        a = int(force * min(y / lim, 1.0))
        px[0, y] = (18, 14, 13, a)
    img = col.resize((W, haut), Image.BILINEAR)
    p = _png(nom)
    img.save(p)
    return p


def sticker(pose_nom):
    return os.path.join(STICKERS, pose_nom + ".png")


def glisse(x_fin, x_hors, t0, duree=0.32):
    """Expression ffmpeg : glissade avec deceleration (ease-out cubique)."""
    return (f"({x_fin})+(({x_hors})-({x_fin}))*"
            f"pow(1-min(max((t-{t0:.3f})/{duree:.3f},0),1),3)")


# ==========================================================================
# STYLE A : "Le lapin te guide" - mascotte presente, chaleureux
# ==========================================================================
# (stem, dossier, t0, t1, zoom_a, zoom_b, vitesse, texte, prix, pose)
A = [
    ("IMG_1044", "Contenue Vlog_", 0.8, 3.0, 1.00, 1.06, 1.0, "Coucou, moi c'est", "EVENTYS", "01_salut_main_levee"),
    ("IMG_1049", "Contenue Vlog_", 1.2, 3.2, 1.00, 1.08, 1.0, "Chaise Napoléon", "3 €", "02_pouce_leve"),
    ("IMG_4054", "Mariages", 0.3, 2.1, 1.02, 1.10, 1.0, "Le couvert complet", "2 €", "04_pointe_du_doigt"),
    ("IMG_4045", "Mariages", 1.7, 3.7, 1.00, 1.07, 1.0, "La table", "10 €", None),
    ("IMG_0968", "Contenue Vlog_", 2.5, 6.5, 1.00, 1.05, 1.6, "On livre en Île-de-France", None, "03_montre_la_main"),
    ("IMG_4046", "Mariages", 7.95, 8.90, 1.00, 1.06, 1.0, None, None, None),
    ("IMG_9425", "Ramadan_", 16.8, 19.2, 1.00, 1.08, 1.0, "Écris-nous en privé", None, "08_au_telephone"),
]


def style_a(nom="STYLE_A_lapin-guide"):
    d = _dir("A")
    parts = []
    for i, p in enumerate(A):
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = plan(brut, *p[:6], speed=p[6])
        texte, prix, pose_nom = p[7], p[8], p[9]
        cal = []
        t0 = 0.22
        t1 = dur - 0.12
        if pose_nom:
            sw = 320
            cal.append({"png": sticker(pose_nom), "w": sw,
                        "x": glisse(60, -sw - 20, t0), "y": 980,
                        "t0": t0, "t1": t1, "fade": 0.16})
        if texte:
            png, lw, lh = bulle(texte, prix, f"a{i}.png")
            x = 410 if pose_nom else int((W - lw) / 2)
            x = min(x, X_MAX - lw) if lw < X_MAX else 30
            cal.append({"png": png, "w": None, "x": str(x),
                        "y": glisse(735, 820, t0 + 0.08), "t0": t0 + 0.08,
                        "t1": t1, "fade": 0.16})
        fin = os.path.join(d, f"{i:02d}.mp4")
        parts.append(pose(brut, cal, fin, dur))
    final = os.path.join(OUT, nom + ".mp4")
    concat(parts, final)
    return final


# ==========================================================================
# STYLE B : "Editorial" - lent, premium, typo, mascotte en signature
# ==========================================================================
B_ = [
    ("IMG_1742", "Contenue Vlog_", 3.5, 6.0, 1.00, 1.07, 1.0, "EVENTYS", None, None),
    ("IMG_1049", "Contenue Vlog_", 1.0, 3.6, 1.04, 1.12, 1.0, "CHAISE NAPOLÉON", "3 € pièce", None),
    ("IMG_4054", "Mariages", 0.2, 2.8, 1.00, 1.08, 1.0, "LE COUVERT", "2 € pièce", None),
    ("IMG_4045", "Mariages", 1.6, 4.2, 1.02, 1.09, 1.0, "LA TABLE", "10 €", None),
    ("IMG_9422", "Ramadan_", 0.3, 2.6, 1.00, 1.07, 1.0, None, None, None),
    ("IMG_4046", "Mariages", 7.95, 8.85, 1.00, 1.05, 1.0, "ÎLE-DE-FRANCE", None, None),
    ("IMG_9425", "Ramadan_", 16.7, 19.4, 1.00, 1.08, 1.0, "MESSAGE PRIVÉ", "pour un devis", "07_bras_croises"),
]


def style_b(nom="STYLE_B_editorial"):
    d = _dir("B")
    parts = []
    for i, p in enumerate(B_):
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = plan(brut, *p[:6], speed=p[6])
        titre, prix, pose_nom = p[7], p[8], p[9]
        cal = []
        if titre:
            cal.append({"png": voile(), "w": None, "x": "0",
                        "y": str(H - 920), "t0": 0.30, "t1": dur - 0.12,
                        "fade": 0.5})
            png, lw, lh = edito(titre, prix, f"b{i}.png")
            cal.append({"png": png, "w": None, "x": str(int((W - lw) / 2)),
                        "y": "1190", "t0": 0.40, "t1": dur - 0.20, "fade": 0.45})
        if pose_nom:
            cal.append({"png": sticker(pose_nom), "w": 200, "x": "85",
                        "y": "1150", "t0": 0.85, "t1": dur - 0.15, "fade": 0.4})
        fin = os.path.join(d, f"{i:02d}.mp4")
        parts.append(pose(brut, cal, fin, dur))
    final = os.path.join(OUT, nom + ".mp4")
    concat(parts, final)
    return final


# ==========================================================================
# STYLE C : "Punchy" - coupes rapides, gros texte qui claque
# ==========================================================================
C = [
    ("IMG_1044", "Contenue Vlog_", 1.0, 1.8, 1.04, 1.12, 1.0, "ON EST DE RETOUR", None),
    ("IMG_1742", "Contenue Vlog_", 3.6, 4.4, 1.00, 1.08, 1.0, "100 CHAISES", None),
    ("IMG_1049", "Contenue Vlog_", 1.3, 2.1, 1.04, 1.14, 1.0, "3 € PIÈCE", "02_pouce_leve"),
    ("IMG_1047", "Contenue Vlog_", 0.2, 0.9, 1.00, 1.08, 1.0, "PRÊTES", None),
    ("IMG_4045", "Mariages", 1.8, 2.6, 1.02, 1.10, 1.0, "TABLES 10 €", None),
    ("IMG_1013", "Contenue Vlog_", 2.5, 3.3, 1.10, 1.20, 1.0, "RONDES OU RECT.", None),
    ("IMG_4054", "Mariages", 0.4, 1.2, 1.02, 1.12, 1.0, "COUVERTS 2 €", None),
    ("IMG_0963", "Contenue Vlog_", 0.15, 0.75, 1.00, 1.08, 1.0, "ON CHARGE", None),
    ("IMG_0968", "Contenue Vlog_", 3.0, 5.4, 1.00, 1.06, 2.0, "ON LIVRE", None),
    ("IMG_1716", "Contenue Vlog_", 1.6, 3.2, 1.00, 1.08, 1.4, "ON MONTE", None),
    ("IMG_4046", "Mariages", 7.95, 8.85, 1.00, 1.06, 1.0, "ET VOILÀ", None),
    ("IMG_9425", "Ramadan_", 16.8, 19.0, 1.00, 1.09, 1.0, "DEVIS EN PRIVÉ", "08_au_telephone"),
]


def style_c(nom="STYLE_C_punchy"):
    d = _dir("C")
    parts = []
    for i, p in enumerate(C):
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = plan(brut, *p[:6], speed=p[6])
        texte, pose_nom = p[7], p[8]
        dernier = (i == len(C) - 1)
        cal = []
        png, lw, lh = punch(texte, f"c{i}.png", accent=dernier)
        x = int((W - lw) / 2)
        if lw > X_MAX - 40:
            x = 30
        cal.append({"png": png, "w": None, "x": str(max(x, 24)),
                    "y": glisse(1150, 1205, 0.04, 0.13),
                    "t0": 0.04, "t1": dur - 0.02, "fade": 0.07})
        if pose_nom:
            sw = 290
            cal.append({"png": sticker(pose_nom), "w": sw,
                        "x": glisse(70, -sw - 20, 0.06, 0.2), "y": 760,
                        "t0": 0.06, "t1": dur - 0.02, "fade": 0.09})
        fin = os.path.join(d, f"{i:02d}.mp4")
        parts.append(pose(brut, cal, fin, dur))
    final = os.path.join(OUT, nom + ".mp4")
    concat(parts, final)
    return final


if __name__ == "__main__":
    import sys
    for q in (sys.argv[1:] or ["a", "b", "c"]):
        print({"a": style_a, "b": style_b, "c": style_c}[q](), flush=True)
