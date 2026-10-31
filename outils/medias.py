# -*- coding: utf-8 -*-
"""Fabrique les medias web du site Eventys a partir des rushes.

Les originaux (H:\\eventys\\Video\\rush) ne sont JAMAIS modifies : on lit, on
recadre, on retouche legerement, on ecrit dans site-internet\\assets.

Photos  : HEIC/JPG -> recadrage au ratio demande -> retouche douce -> WebP
          en deux largeurs (srcset).
Videos  : MOV HDR (bt2020/HLG) -> tonemap SDR bt709 -> MP4 h264 muet + poster.
          Sans le tonemap, l'image parait cramee chez le visiteur.

Lancer :  python site-internet\\outils\\medias.py
"""
import os
import subprocess

from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import pillow_heif

pillow_heif.register_heif_opener()

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUSH = r"H:\eventys\Video\rush"
ILLUS = r"H:\eventys\assets\illus"
LOGO = r"H:\eventys\assets\LOGO_eventys.png"
IMG = os.path.join(RACINE, "assets", "img")
VID = os.path.join(RACINE, "assets", "video")
FFMPEG = r"H:\eventys\tools\bin\ffmpeg.exe"
FFPROBE = r"H:\eventys\tools\bin\ffprobe.exe"

TONEMAP = (
    "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
    "tonemap=tonemap=hable:desat=0,"
    "zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
)

RATIOS = {"45": 4 / 5, "34": 3 / 4, "11": 1.0, "54": 5 / 4, "32": 3 / 2, "169": 16 / 9}
LARGEURS = {"45": (900, 1400), "34": (900, 1400), "11": (900, 1400),
            "54": (1000, 1600), "32": (1200, 1900), "169": (1400, 2000)}

# (fichier source, nom de sortie, ratio, ancrage vertical 0=haut 1=bas)
PHOTOS = [
    # -- chaise Napoleon
    (r"Mise en place_\IMG_6986.HEIC", "chaise-rang", "45", 0.5),
    (r"Mise en place_\IMG_6987.HEIC", "chaise-rue", "32", 0.5),
    (r"Mise en place_\IMG_7760.HEIC", "chaise-escalier", "45", 0.5),
    (r"Mise en place_\IMG_6984.HEIC", "coulisse-lavage", "32", 0.45),
    # -- transport / coulisses
    (r"Mise en place_\IMG_7016.HEIC", "van-ouvert", "32", 0.5),
    (r"Mise en place_\IMG_7013.HEIC", "van-interieur", "45", 0.5),
    (r"Mise en place_\IMG_7019.HEIC", "livraison-portage", "45", 0.5),
    (r"Mise en place_\IMG_7021.HEIC", "livraison-cour", "32", 0.5),
    # -- kit vaisselle / nappe
    (r"Mise en place_\IMG_3570.heic", "vaisselle-couverts", "45", 0.5),
    (r"Mise en place_\IMG_3566.heic", "vaisselle-couvert-complet", "11", 0.45),
    (r"Mise en place_\IMG_3573.heic", "vaisselle-verre", "45", 0.5),
    (r"Mise en place_\IMG_3574.heic", "nappe-assiettes", "54", 0.45),
    # -- tables dressees (mariage)
    (r"Mariages\IMG_4049.heic", "salle-mariage", "32", 0.5),
    (r"Mariages\IMG_4051.heic", "table-ronde-chaises", "54", 0.5),
    (r"Mariages\IMG_4055.heic", "table-ronde-dessus", "45", 0.5),
    (r"Mariages\IMG_4064.heic", "dressage-bleu", "32", 0.5),
    (r"Mariages\IMG_4065.heic", "dressage-bleu-2", "45", 0.5),
    (r"Mariages\PHOTO-2026-03-23-10-44-32.jpg", "jardin-fleurs", "45", 0.5),
    (r"Mariages\PHOTO-2026-03-23-10-44-45.jpg", "chapiteau", "32", 0.5),
    (r"Mariages\1753a7fa-6de9-488c-97c4-09168a9c48c4.jpg", "terrasse-citron", "32", 0.5),
    # -- iftar / ramadan
    (r"Ramadan_\IMG_9402.HEIC", "table-rect-dessus", "45", 0.5),
    (r"Ramadan_\IMG_9455.HEIC", "table-ronde-sauge-dessus", "11", 0.5),
    (r"Ramadan_\IMG_9446.HEIC", "couvert-sauge", "45", 0.72),
    (r"Ramadan_\IMG_9437.HEIC", "lanterne-sauge", "32", 0.5),
    (r"Ramadan_\IMG_9419.HEIC", "iftar-long", "32", 0.5),
    (r"Ramadan_\IMG_9445.HEIC", "iftar-couvert", "54", 0.5),
    # -- noel
    ("No\u00ebl\\IMG_3408.HEIC", "noel-table", "32", 0.5),
    ("No\u00ebl\\IMG_3421.HEIC", "noel-table-2", "45", 0.5),
    ("No\u00ebl\\IMG_3430.HEIC", "noel-couvert", "11", 0.5),
    # -- ajout du 2026-10-22 : salle fuchsia, arche fleurie, table chocolat
    ("Mariages\WhatsApp Image 2026-10-22 at 17.41.38 (1).jpeg", "salle-fuchsia", "32", 0.5),
    ("Mariages\WhatsApp Image 2026-10-22 at 17.41.38 (2).jpeg", "couvert-fuchsia", "45", 0.5),
    ("Mariages\WhatsApp Image 2026-10-22 at 17.41.38 (4).jpeg", "tables-fuchsia", "45", 0.5),
    ("Mariages\WhatsApp Image 2026-10-22 at 17.41.38 (5).jpeg", "arche-fleurie", "45", 0.42),
    ("Mariages\WhatsApp Image 2026-10-22 at 17.41.38.jpeg", "table-rect-fuchsia", "45", 0.5),
    ("Anniversaire_\WhatsApp Image 2026-10-22 at 12.38.29 (1).jpeg", "table-chocolat", "45", 0.5),
    ("Anniversaire_\WhatsApp Image 2026-10-22 at 12.38.29.jpeg", "couvert-chocolat", "45", 0.5),
    ("Anniversaire_\WhatsApp Image 2026-10-22 at 12.38.30 (5).jpeg", "buffet-tournesols", "45", 0.5),
    # -- anniversaire
    (r"Anniversaire_\IMG_2778.heic", "arche-ballons", "45", 0.12),
    (r"Anniversaire_\IMG_2780.heic", "arche-ballons-2", "45", 0.12),
]

# (source, nom, debut, duree, filtre de cadrage)
VIDEOS = [
    (r"Ramadan_\IMG_9450.MOV", "hero-table", 1.2, 8.0, "scale=1100:-2"),
    (r"Ramadan_\IMG_9459.MOV", "nappe", 146.0, 7.0, "scale=1200:-2"),
    (r"Mise en place_\IMG_7015.MOV", "van", 0.3, 4.4, "scale=1200:900"),
    (r"Mise en place_\IMG_6945.MOV", "jardin", 0.5, 5.0, "scale=1000:-2"),
    (r"Ramadan_\IMG_9443.MOV", "lanterne", 4.0, 7.0, "scale=1100:-2"),
]


# Zones a flouter, en coordonnees relatives (x0, y0, x1, y1) SUR L'IMAGE
# RECADREE : prenoms des maries et date peints sur l'arche. On ne publie pas
# le nom de clients sur le site.
FLOUS = {
    "salle-mariage": [(0.44, 0.00, 0.61, 0.17)],
    "table-ronde-chaises": [(0.25, 0.00, 0.46, 0.13)],
}


def floute(im, zones):
    for x0, y0, x1, y1 in zones:
        boite = (int(x0 * im.width), int(y0 * im.height),
                 int(x1 * im.width), int(y1 * im.height))
        bout = im.crop(boite)
        bout = bout.resize((max(1, bout.width // 22), max(1, bout.height // 22)))
        im.paste(bout.resize((boite[2] - boite[0], boite[3] - boite[1]),
                             Image.NEAREST), boite)
    return im


def recadre(im, ratio, ancrage):
    """Recadre au ratio voulu en gardant le centre (ou l'ancrage demande)."""
    l, h = im.size
    cible = RATIOS[ratio]
    if l / h > cible:          # trop large -> on coupe sur les cotes
        nl = int(h * cible)
        x = (l - nl) // 2
        return im.crop((x, 0, x + nl, h))
    nh = int(l / cible)        # trop haut -> on coupe en hauteur
    y = int((h - nh) * ancrage)
    return im.crop((0, y, l, y + nh))


def retouche(im):
    """Retouche douce : on remet du contraste, un rien de chaleur et de pique.

    Volontairement legere : ce sont de vraies photos de prestation, une
    retouche forte les ferait passer pour des images de banque.
    """
    im = ImageOps.autocontrast(im, cutoff=(0.4, 0.2))
    im = ImageEnhance.Color(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    r, v, b = im.split()
    r = r.point(lambda p: min(255, int(p * 1.012)))
    b = b.point(lambda p: int(p * 0.994))
    im = Image.merge("RGB", (r, v, b))
    return im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=3))


def fais_photos():
    for src, nom, ratio, ancrage in PHOTOS:
        chemin = os.path.join(RUSH, src)
        if not os.path.exists(chemin):
            print("MANQUE", chemin)
            continue
        im = Image.open(chemin)
        im = ImageOps.exif_transpose(im).convert("RGB")
        im = recadre(im, ratio, ancrage)
        if nom in FLOUS:
            im = floute(im, FLOUS[nom])
        im = retouche(im)
        for largeur in LARGEURS[ratio]:
            largeur = min(largeur, im.width)
            out = im.resize((largeur, round(largeur / RATIOS[ratio])), Image.LANCZOS)
            out.save(os.path.join(IMG, "%s-%d.webp" % (nom, largeur)), "WEBP",
                     quality=80, method=6)
        print("photo", nom, im.size)


def est_hdr(chemin):
    sortie = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=color_transfer", "-of", "csv=p=0", chemin],
        capture_output=True).stdout
    return b"arib-std-b67" in sortie or b"smpte2084" in sortie


def fais_videos():
    for src, nom, debut, duree, cadrage in VIDEOS:
        chemin = os.path.join(RUSH, src)
        if not os.path.exists(chemin):
            print("MANQUE", chemin)
            continue
        sortie = os.path.join(VID, nom + ".mp4")
        chaine = (TONEMAP + "," if est_hdr(chemin) else "") + cadrage + ",fps=25"
        subprocess.run([FFMPEG, "-v", "error", "-ss", str(debut), "-t", str(duree),
                        "-i", chemin, "-vf", chaine, "-an",
                        "-c:v", "libx264", "-profile:v", "high", "-crf", "28",
                        "-preset", "slow", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart",
                        "-colorspace", "bt709", "-color_primaries", "bt709",
                        "-color_trc", "bt709", "-color_range", "tv",
                        "-y", sortie], check=True)
        jpg = os.path.join(IMG, "poster-%s.jpg" % nom)
        subprocess.run([FFMPEG, "-v", "error", "-ss", "0.3", "-i", sortie,
                        "-frames:v", "1", "-y", jpg], check=True)
        Image.open(jpg).convert("RGB").save(
            os.path.join(IMG, "poster-%s.webp" % nom), "WEBP", quality=78, method=6)
        os.remove(jpg)
        print("video", nom, os.path.getsize(sortie) // 1024, "Ko")


def fais_illustrations():
    """Reprend les illustrations au trait de la marque (chaise, table, arche)."""
    for f, nom in [("chaise_detoure.png", "illus-chaise"),
                   ("table_detoure.png", "illus-table"),
                   ("arche_detoure.png", "illus-arche")]:
        im = Image.open(os.path.join(ILLUS, f)).convert("RGBA")
        im = im.crop(im.getbbox())
        h = 900
        im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
        im.save(os.path.join(IMG, nom + ".webp"), "WEBP", quality=90, method=6)
        print("illus", nom, im.size)

    logo = Image.open(LOGO).convert("RGBA")
    fond = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    px = logo.load()
    for y in range(logo.height):      # le logo est sur fond creme : on le detoure
        for x in range(logo.width):
            r, v, b, a = px[x, y]
            if not (r > 225 and v > 218 and b > 216):
                fond.putpixel((x, y), (r, v, b, a))
    fond = fond.crop(fond.getbbox())
    fond = fond.resize((round(fond.width * 220 / fond.height), 220), Image.LANCZOS)
    fond.save(os.path.join(IMG, "logo.webp"), "WEBP", quality=92, method=6)
    fond.save(os.path.join(IMG, "logo.png"))
    print("logo", fond.size)


if __name__ == "__main__":
    for d in (IMG, VID):
        os.makedirs(d, exist_ok=True)
    fais_illustrations()
    fais_photos()
    fais_videos()
    print("fini")
