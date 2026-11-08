"""Deuxieme serie de directions de montage (apres retours de Yanis).

Retours pris en compte :
  - le sticker lapin est valide, mais il ne doit pas "juste etre coupe" :
    il arrive en sautant, il flotte, il change de pose, il "parle" par des
    bulles qui s'ecrivent lettre par lettre ;
  - au moins 20 s par video, sans etirer artificiellement ;
  - le style editorial est garde (decline ici en version animee) ;
  - aucune pause ni effet bugue : chaque calque reste dans la duree de son
    plan, et aucun plan ne finit sur une image figee.

Nouveaux effets par rapport a styles.py :
  - flottement (sinus) et saut d'arrivee de la mascotte
  - changement de pose en cours de plan
  - bulles et titres fabriques en SUITES de PNG (texte qui s'ecrit)
  - zoom "snap" (coup de zoom qui se resorbe) en plus du zoom lineaire
"""
import math
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

import da
import styles as S

W, H, FPS = S.W, S.H, S.FPS
FF, OUT = S.FF, S.OUT
CREME, BORDEAUX, ROUGE = S.CREME, S.BORDEAUX, S.ROUGE
X_MAX = S.X_MAX
TMP = os.path.join(OUT, "_tmp_styles2")


def _dir(nom):
    d = os.path.join(TMP, nom)
    os.makedirs(d, exist_ok=True)
    return d


# --------------------------------------------------------------------------
# Mouvements de la mascotte
# --------------------------------------------------------------------------

def flotte(base, amp=14, freq=0.75):
    """Respiration : la mascotte monte et descend doucement, en continu.

    C'est ce qui empeche l'impression de sticker colle. Pas de virgule dans
    l'expression, mais elle est quotee en aval de toute facon.
    """
    return f"{base}+{amp}*sin(2*PI*{freq}*t)"


def saut(x_fin, x_hors, t0, duree=0.42):
    """Arrivee en glissade + petit rebond amorti a l'atterrissage."""
    p = f"min(max((t-{t0:.3f})/{duree:.3f},0),1)"
    glisse = f"({x_fin})+(({x_hors})-({x_fin}))*pow(1-{p},3)"
    return glisse


def rebond(base, t0, duree=0.42, h=38):
    """Hauteur du rebond : remonte puis retombe, puis flottement continu."""
    p = f"min(max((t-{t0:.3f})/{duree:.3f},0),1)"
    arc = f"{h}*sin(PI*{p})"
    return f"{base}-{arc}+10*sin(2*PI*0.75*max(t-{t0 + duree:.3f},0))"


# --------------------------------------------------------------------------
# Textes animes (suites de PNG)
# --------------------------------------------------------------------------

def _mesure(texte, font, esp):
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    return S._largeur_espace(d0, texte, font, esp)


def bulle_seq(texte, prix, nom, dur, vitesse=26.0, queue_x=None):
    """Bulle de dialogue dont le texte s'ecrit, puis le prix apparait.

    Retourne (motif_png, largeur, hauteur). La boite garde une taille FIXE
    (calculee sur le texte complet) : sinon la bulle grandit a chaque lettre
    et ca saute.
    """
    d = _dir(nom)
    f_txt = ImageFont.truetype(da.BODONI, 44)
    f_prix = ImageFont.truetype(da.BODONI_B, 64)
    esp = 2
    lt = _mesure(texte, f_txt, esp)
    lp = _mesure(prix, f_prix, esp) if prix else 0
    larg = int(max(lt, lp)) + 84
    haut = 148 if prix else 104
    n = max(int(dur * FPS), 2)
    t_fin_texte = len(texte) / vitesse
    for i in range(n):
        t = i / FPS
        img = Image.new("RGBA", (larg, haut + 20), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        dr.rounded_rectangle([0, 0, larg - 1, haut - 1], radius=32,
                             fill=CREME + (243,))
        qx = 70 if queue_x is None else max(44, min(int(queue_x), larg - 44))
        dr.polygon([(qx - 10, haut - 2), (qx + 26, haut - 2), (qx, haut + 18)],
                   fill=CREME + (243,))
        k = min(int(t * vitesse) + 1, len(texte))
        bout = texte[:k]
        lb = _mesure(bout, f_txt, esp)
        S._ecrire_espace(dr, (larg - lt) / 2, 28, bout, f_txt, BORDEAUX, esp)
        if prix and t > t_fin_texte + 0.12:
            S._ecrire_espace(dr, (larg - lp) / 2, 78, prix, f_prix, ROUGE, esp)
        img.save(os.path.join(d, f"{i:04d}.png"))
    return os.path.join(d, "%04d.png"), larg, haut + 20


def titre_seq(titre, prix, nom, dur, vitesse=16.0):
    """Style editorial : filet qui se trace, puis capitales qui apparaissent."""
    d = _dir(nom)
    f_t = ImageFont.truetype(da.BODONI, 52)
    f_p = ImageFont.truetype(da.BODONI_I, 42)
    esp = 13
    lt = _mesure(titre, f_t, esp)
    lp = _mesure(prix, f_p, 3) if prix else 0
    larg = int(max(lt, lp, 420)) + 24
    haut = 168 if prix else 104
    n = max(int(dur * FPS), 2)
    for i in range(n):
        t = i / FPS
        img = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        trait = min(t / 0.45, 1.0) * 58
        if trait > 1:
            dr.line([(larg / 2 - trait, 5), (larg / 2 + trait, 5)],
                    fill=CREME + (230,), width=3)
        if t > 0.30:
            k = min(int((t - 0.30) * vitesse) + 1, len(titre))
            S._ecrire_espace(dr, (larg - lt) / 2, 34, titre[:k], f_t, CREME, esp)
        if prix and t > 0.30 + len(titre) / vitesse + 0.15:
            S._ecrire_espace(dr, (larg - lp) / 2, 106, prix, f_p, CREME, 3)
        img.save(os.path.join(d, f"{i:04d}.png"))
    return os.path.join(d, "%04d.png"), larg, haut


# --------------------------------------------------------------------------
# Rendu
# --------------------------------------------------------------------------

def plan(sortie, stem, folder, t0, t1, za=1.0, zb=1.0, speed=1.0,
         snap=False, ancre=0.5, ancre_x=0.5):
    """Comme styles.plan, avec en plus un mode `snap` (coup de zoom amorti)."""
    path = S.B.src(stem, folder)
    dur_in = t1 - t0
    chaine = f"fps={FPS}"
    if S.B.est_hdr(path):
        chaine += "," + S.B.TONEMAP
    if snap:
        frames = max(int(round(dur_in * FPS)), 1)
        k = max(za, zb, 1.0) * 1.2
        iw, ih = int(W * k) // 2 * 2, int(H * k) // 2 * 2
        # part fort puis se resorbe vite, puis derive lentement
        z = f"{zb:.4f}+{max(za - zb, 0.10):.4f}*exp(-on/6)"
        chaine += (f",scale={iw}:{ih}:force_original_aspect_ratio=increase:flags=lanczos,"
                   f"crop={iw}:{ih}:(in_w-out_w)*{ancre_x:.3f}:"
                   f"(in_h-out_h)*{ancre:.3f},setsar=1,"
                   f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                   f"d=1:s={W}x{H}:fps={FPS},setsar=1")
    else:
        chaine += "," + S._kenburns(za, zb, dur_in, ancre, ancre_x)
    if speed != 1.0:
        chaine += f",setpts=PTS/{speed}"
    chaine += ",eq=contrast=1.04:saturation=1.03:gamma=1.01"
    subprocess.run([
        FF, "-y", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", path,
        "-vf", chaine + ",format=yuv420p",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", sortie,
    ], check=True)
    return dur_in / speed


def pose(video, calques, sortie, dur):
    """Pose des calques (PNG fixe ou SUITE de PNG) sur un plan."""
    if not calques:
        import shutil
        shutil.copy(video, sortie)
        return sortie
    cmd = [FF, "-y", "-v", "error", "-i", video]
    for c in calques:
        if c.get("seq"):
            cmd += ["-framerate", str(FPS), "-i", c["seq"]]
        else:
            cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}",
                    "-i", c["png"]]
    filt, prev = [], "0:v"
    for i, c in enumerate(calques, start=1):
        lab, out = f"c{i}", ("vout" if i == len(calques) else f"v{i}")
        ech = f"scale={c['w']}:-1," if c.get("w") else ""
        fd = c.get("fade", 0.16)
        t0, t1 = c["t0"], min(c["t1"], dur)
        filt.append(
            f"[{i}:v]{ech}format=rgba,"
            f"fade=t=in:st=0:d={fd:.3f}:alpha=1,"
            f"fade=t=out:st={max(t1 - t0 - fd, 0.02):.3f}:d={fd:.3f}:alpha=1,"
            f"setpts=PTS+{t0:.3f}/TB[{lab}]"
        )
        filt.append(
            f"[{prev}][{lab}]overlay=x='{c['x']}':y='{c['y']}':format=auto:"
            f"eof_action=pass:enable='between(t,{t0:.3f},{t1:.3f})'[{out}]"
        )
        prev = out
    # Les calques sont en RGBA : sans conversion finale, `overlay=format=auto`
    # sort en yuv444p et x264 encode en High 4:4:4. Ni Instagram ni TikTok
    # n'acceptent ce profil, et beaucoup de lecteurs refusent l'image.
    filt.append(f"[{prev}]format=yuv420p[fin]")
    subprocess.run([
        *cmd, "-filter_complex", ";".join(filt), "-map", "[fin]",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", sortie,
    ], check=True)
    return sortie
