"""Story faite d'un VRAI CLIP de rush, pas d'une photo animee.

Pourquoi ce fichier existe : les stories etaient jusqu'ici des cartes
fabriquees (fiche produit, grille de catalogue) ou des photos fixes avec un
travelling. Yanis a demande deux fois l'inverse — « utilise d'autres videos,
d'autre contenu des rushes, et que ce soit plus varie ».

Une serie de stories doit donc melanger trois natures :
  - des clips de rush habilles (ce fichier),
  - des cartes fabriquees (stories2.py),
  - le Reel du jour lui-meme (publier.story_video).

L'habillage est volontairement leger : logo en haut au centre, une seule
carte de texte en bas. Le sujet, c'est le mobilier qui bouge, pas la mise
en page.

Contraintes Meta deja payees cher et reprises ici telles quelles :
  - debit plancher 5 Mb/s, sinon erreur 2207077 ;
  - yuv420p, 48 kHz, sinon la story est muette chez une partie des gens ;
  - pas de `crf` avec `-b:v`, libx264 ferait gagner le crf.
"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

import da
import stories2 as S2

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
RUSH = os.path.join(RACINE, "Video", "rush")
TMP = os.path.join(ICI, "_stories", "_tmp_clip")

W, H, FPS = 1080, 1920, 30
CREME, BORDEAUX, ROUGE, ENCRE = da.CREME, da.BORDEAUX, da.ROUGE, da.ENCRE
OR = (198, 162, 86)

# LA ZONE SURE D'UNE STORY N'EST PAS CELLE D'UN REEL. Le Reel s'arrete a
# y=1440 parce que la legende, le nom de compte et les boutons occupent
# tout le bas. Une story n'a que la barre « Envoyer un message », qui
# commence vers y=1670. Le cartouche se pose donc a 1380 et descend jusque
# vers 1630 : c'est volontaire, et c'est plus lisible que de tout tasser
# au milieu. Les cartes fabriquees de stories2.py, elles, s'arretent a
# 1440 — elles portent des prix qu'on doit pouvoir lire sur une capture.
Y_CARTE = 1380


def _p(nom):
    os.makedirs(TMP, exist_ok=True)
    return os.path.join(TMP, nom)


def _larg(d, t, f, esp=0):
    return sum(d.textlength(c, font=f) for c in t) + esp * max(len(t) - 1, 0)


def _ecrire(d, x, y, t, f, coul, esp=0):
    for c in t:
        d.text((x, y), c, font=f, fill=coul)
        x += d.textlength(c, font=f) + esp


def habillage(titre, detail, prix=None, teinte="beige", nom="hab.png"):
    """Calque transparent 1080x1920 : logo en haut, carte de texte en bas."""
    from PIL import ImageFilter
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # Sur une carte fabriquee, le logo se pose sur un aplat choisi. Ici il se
    # pose sur un rush : fond blanc de chaises a une seconde, interieur de
    # box sombre a la suivante. Le logo bicolore disparaissait sur les deux.
    # On le passe donc toujours en creme uni, et on glisse derriere lui un
    # voile sombre tres flou : creme sur halo, ca tient sur n'importe quel
    # fond sans se voir comme un bandeau.
    voile = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(voile).ellipse([W // 2 - 330, 240, W // 2 + 330, 530],
                                  fill=(18, 12, 10, 120))
    img.alpha_composite(voile.filter(ImageFilter.GaussianBlur(55)))
    S2.logo(img, teinte="bordeaux", y=272, haut=184)

    f_t = ImageFont.truetype(da.BODONI_B, 64)
    f_d = ImageFont.truetype(da.BODONI_B, 38)
    f_p = ImageFont.truetype(da.BODONI_B, 54)
    d0 = ImageDraw.Draw(img)

    esp_t, esp_d = 7, 3
    lt = _larg(d0, titre, f_t, esp_t)
    ld = _larg(d0, detail, f_d, esp_d) if detail else 0
    lp = _larg(d0, prix, f_p, 3) if prix else 0

    larg = int(max(lt, ld)) + 90
    haut = 150 + (60 if detail else 0)
    if prix:
        larg = max(larg, int(lp) + 90)
        haut += 86

    carte = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
    dc = ImageDraw.Draw(carte)
    dc.rounded_rectangle([0, 0, larg - 1, haut - 1], radius=28,
                         fill=CREME + (235,), outline=OR + (210,), width=3)
    y = 34
    _ecrire(dc, (larg - lt) / 2, y, titre, f_t, BORDEAUX, esp_t)
    y += 86
    if detail:
        _ecrire(dc, (larg - ld) / 2, y, detail, f_d, ENCRE, esp_d)
        y += 58
    if prix:
        # Pastille rouge : c'est la seule couleur pleine de la charte, elle
        # sert uniquement au prix pour qu'il soit cherche du regard.
        pl, ph = int(lp) + 56, 72
        px = (larg - pl) // 2
        dc.rounded_rectangle([px, y, px + pl, y + ph], radius=22,
                             fill=ROUGE + (255,))
        _ecrire(dc, px + 28, y + 8, prix, f_p, CREME, 3)

    # Ombre portee : sans elle la carte creme disparait sur une chaise
    # blanche, et nos rushes sont pleins de chaises blanches.
    from PIL import ImageFilter
    ombre = Image.new("RGBA", (larg + 60, haut + 60), (0, 0, 0, 0))
    ombre.paste((18, 12, 10, 130), (30, 36, 30 + larg, 36 + haut))
    ombre = ombre.filter(ImageFilter.GaussianBlur(18))
    x = (W - larg) // 2
    img.alpha_composite(ombre, (x - 30, Y_CARTE - 30))
    img.alpha_composite(carte, (x, Y_CARTE))

    p = _p(nom)
    img.save(p)
    return p


def est_hdr(path):
    r = subprocess.run([FF.replace("ffmpeg", "ffprobe"), "-v", "error",
                        "-select_streams", "v:0", "-show_entries",
                        "stream=color_transfer", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return "arib-std-b67" in r.stdout or "smpte2084" in r.stdout


TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,"
           "zscale=p=bt709,tonemap=hable:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def clip(stem, dossier, t0, t1, titre, detail, sortie,
         prix=None, teinte="beige", lit=None, debut_son=0.0,
         va_et_vient=False, ancre=0.5, ancre_x=0.5):
    """Un morceau de rush, recadre en 9:16, habille et sonorise.

    `va_et_vient` joue le plan puis le meme plan a l'envers, ce qui double
    sa duree sans raccord visible. Sert quand un rush ne contient que deux
    secondes exploitables : au-dela, la camera quitte le sujet. Mieux vaut
    repasser sur deux bonnes secondes qu'en montrer quatre dont deux vides.
    """
    src = None
    d = os.path.join(RUSH, dossier)
    for f in os.listdir(d):
        if f.startswith(stem) and "(1)" not in f and \
                f.lower().endswith((".mov", ".mp4")):
            src = os.path.join(d, f)
            break
    if src is None:
        raise SystemExit(f"{stem} introuvable dans {dossier}")

    dur = (t1 - t0) * (2 if va_et_vient else 1)
    hab = habillage(titre, detail, prix, teinte,
                    nom=os.path.basename(sortie) + ".png")

    chaine = f"fps={FPS}"
    if est_hdr(src):
        chaine += "," + TONEMAP
    # Pas de zoompan : il avance par pixels entiers et fait trembler.
    # `ancre` : point de recadrage vertical, 0 = haut, 1 = bas. Nos rushes
    # sont en paysage et le meuble est dans la moitie basse ; un 9:16
    # centre garde le haut du mur. Sur une source 16:9, c'est sans effet :
    # la hauteur est deja exacte et seule la LARGEUR est coupee — d'ou
    # `ancre_x`, 0 = bord gauche, 1 = bord droit. Il sert a sortir du cadre
    # ce qui ne nous appartient pas : une plaque, un vehicule floque.
    chaine += (f",scale={W}:{H}:force_original_aspect_ratio=increase:"
               f"flags=lanczos,crop={W}:{H}:(in_w-out_w)*{ancre_x:.3f}:"
               f"(in_h-out_h)*{ancre:.3f},setsar=1,"
               f"eq=contrast=1.04:saturation=1.03:gamma=1.01,format=yuv420p")

    cmd = [FF, "-y", "-v", "error", "-ss", f"{t0}", "-to", f"{t1}", "-i", src,
           "-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.2f}", "-i", hab]
    if lit:
        cmd += ["-ss", f"{debut_son:.2f}", "-t", f"{dur:.2f}", "-i", lit]

    # L'aller-retour se fait AVANT l'habillage : sinon `reverse` renverrait
    # aussi le logo et la carte de texte.
    if va_et_vient:
        chaine += (",split=2[f][b];[b]reverse[r];"
                   "[f][r]concat=n=2:v=1:a=0")
    filtre = (f"[0:v]{chaine}[v0];"
              f"[v0][1:v]overlay=0:0:format=auto,format=yuv420p[v]")
    cmd += ["-filter_complex", filtre, "-map", "[v]"]
    if lit:
        cmd += ["-map", "2:a",
                "-af", f"afade=t=in:st=0:d=0.5,"
                       f"afade=t=out:st={max(dur - 0.7, 0):.2f}:d=0.7,"
                       f"volume=0.9,aresample=48000",
                "-c:a", "aac", "-b:a", "128k", "-ar", "48000"]
    cmd += ["-t", f"{dur:.2f}",
            "-c:v", "libx264", "-preset", "medium",
            "-b:v", "6M", "-minrate", "4M", "-maxrate", "8M", "-bufsize", "12M",
            "-g", str(FPS * 2), "-keyint_min", str(FPS),
            "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
            "-colorspace", "bt709", "-color_primaries", "bt709",
            "-color_trc", "bt709", "-color_range", "tv",
            "-movflags", "+faststart", sortie]
    subprocess.run(cmd, check=True)
    return sortie
