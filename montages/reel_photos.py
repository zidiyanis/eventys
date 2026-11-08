"""Reel anime a partir de photos — 1080x1920.

Format pense pour repondre a une mesure : le Reel du 20 octobre faisait 35 s
pour 9,9 s de visionnage moyen. Les gens partaient au tiers. Sur 14 s, ces
memes 9,9 s representent 71 % de la video, et une partie la termine — c'est
la RETENTION que l'algorithme regarde, pas la duree.

Chaque photo recoit un leger mouvement : une image strictement fixe sur un
Reel se lit comme une erreur et fait passer le doigt.
"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import da

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
TMP = os.path.join(ICI, "_tmp_reel_photos")

W, H, FPS = 1080, 1920, 30
CREME, BORDEAUX, ENCRE = da.CREME, da.BORDEAUX, da.ENCRE
OR = (198, 162, 86)

Y_TEXTE = 1180          # sous la zone sure haute, au-dessus de y=1440
X_MAX = 850


def _p(n):
    os.makedirs(TMP, exist_ok=True)
    return os.path.join(TMP, n)


def _larg(d, t, f, esp=0):
    return sum(d.textlength(c, font=f) for c in t) + esp * max(len(t) - 1, 0)


def _ecrire(d, x, y, t, f, coul, esp=0):
    for c in t:
        d.text((x, y), c, font=f, fill=coul)
        x += d.textlength(c, font=f) + esp


def carte_texte(texte, nom, accent=False, taille=52):
    """Bandeau creme avec le texte, a poser sur la photo."""
    f = ImageFont.truetype(da.BODONI_B, taille)
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    esp = 3
    mots, lignes, cur = texte.split(), [], []
    for m in mots:
        if _larg(d0, " ".join(cur + [m]), f, esp) > 700 and cur:
            lignes.append(" ".join(cur)); cur = [m]
        else:
            cur.append(m)
    lignes.append(" ".join(cur))

    lw = int(max(_larg(d0, l, f, esp) for l in lignes)) + 70
    inter = int(taille * 1.3)
    lh = inter * len(lignes) + 44
    img = Image.new("RGBA", (lw + 16, lh + 18), (0, 0, 0, 0))
    o = Image.new("RGBA", (lw, lh), (20, 14, 12, 120))
    img.alpha_composite(o.filter(ImageFilter.GaussianBlur(10)), (10, 12))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, lw, lh], radius=20, fill=CREME + (218,),
                        outline=OR + (255,) if accent else None,
                        width=3 if accent else 0)
    coul = BORDEAUX if accent else ENCRE
    for i, l in enumerate(lignes):
        x = (lw - _larg(d, l, f, esp)) / 2
        _ecrire(d, x, 20 + i * inter, l, f, coul, esp)
    p = _p(nom)
    img.save(p)
    return p, img.width, img.height


def plan(source, sortie, duree, za=1.00, zb=1.015, ancre=0.5):
    """Une photo, mise au format 9:16 avec un mouvement lent.

    Deux precautions contre le tremblement, apprises a la dure :

    1. le zoom est calcule au DOUBLE de la definition puis reduit, parce
       que `zoompan` avance par pixels entiers ;
    2. et surtout le zoom reste LENT. Une premiere version montait de 5 %
       en 2,8 s — cinq fois le rythme des stories — et ca sautait
       visiblement. La mesure d'irregularite passait de 0,10 a 0,40.
       Viser 0,5 % par seconde au maximum.
    """
    frames = max(int(duree * FPS), 1)
    k = max(za, zb) * 1.12
    iw = int(W * 2 * k) // 2 * 2
    ih = int(H * 2 * k) // 2 * 2
    z = f"{za:.4f}+({zb - za:.4f})*min(on/{frames},1)"
    subprocess.run([
        FF, "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS),
        "-t", f"{duree:.3f}", "-i", source,
        "-vf", (f"scale={iw}:{ih}:force_original_aspect_ratio=increase:"
                f"flags=lanczos,"
                f"crop={iw}:{ih}:(in_w-out_w)/2:(in_h-out_h)*{ancre:.3f},"
                f"setsar=1,"
                f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d=1:s={W * 2}x{H * 2}:fps={FPS},"
                f"scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p"),
        "-c:v", "libx264", "-preset", "medium", "-b:v", "8M",
        "-maxrate", "10M", "-bufsize", "14M",
        "-g", str(FPS * 2), "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", sortie,
    ], check=True)
    return duree
