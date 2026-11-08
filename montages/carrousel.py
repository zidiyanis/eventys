"""Carrousel Instagram — « Les détails qui font la table ».

Format 1080x1350 (4:5) : c'est le ratio qui occupe le plus de hauteur dans
le fil, donc celui qui retient le plus longtemps.

Les photos sont des HEIC iPhone en HDR : sans conversion vers bt709, les
blancs partent en laiteux. La chaine de tonemap est la meme que pour les
videos.

Le texte est volontairement bref : sur un carrousel, l'image porte, le
texte confirme. Un pave annule l'interet du format.
"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import da

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
RUSH = os.path.join(RACINE, "Video", "rush")
CONV = os.path.join(RUSH, "_catalogue", "converted")
SORTIE = os.path.join(ICI, "_carrousel")

# Deux formats, deux plateformes :
#   Instagram affiche un carrousel en 4:5  (1080 x 1350)
#   TikTok affiche un diaporama en 9:16    (1080 x 1920)
# Recadrer l'un dans l'autre decale tout. On produit donc les deux, a
# partir de la MEME composition : le sujet et le texte sont places dans
# une bande centrale commune aux deux rapports, et seul le fond s'etire.
W, H = 1080, 1350
W_TT, H_TT = 1080, 1920
PAPIER = (240, 237, 236)
TERRA = (191, 87, 85)
BORDEAUX = (111, 47, 47)
CREME = da.CREME
OR = (198, 162, 86)

# Teinte des pastilles sur fond photo : creme, qui reste lisible sur du
# clair comme sur du sombre une fois l'ombre portee posee.
LOGO = os.path.join(RACINE, "assets", "LOGO_eventys.png")


def convertir(nom, dossier):
    """HEIC HDR -> JPG bt709, dans _catalogue/converted (originaux intacts)."""
    os.makedirs(CONV, exist_ok=True)
    src = os.path.join(RUSH, dossier, nom + ".heic")
    dst = os.path.join(CONV, nom + ".jpg")
    if os.path.exists(dst):
        return dst
    subprocess.run([
        FF, "-y", "-v", "error", "-i", src,
        "-vf", "zscale=t=linear:npl=100,format=gbrpf32le,"
               "zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
               "zscale=t=bt709:m=bt709:r=tv,format=yuv420p",
        "-frames:v", "1", "-q:v", "2", dst,
    ], check=False)
    if not os.path.exists(dst):
        # Certaines photos ne sont pas en HDR : la chaine zscale echoue
        # alors sans raison. On retombe sur une conversion simple.
        subprocess.run([FF, "-y", "-v", "error", "-i", src,
                        "-frames:v", "1", "-q:v", "2", dst], check=True)
    return dst


def _larg(d, t, f, esp=0):
    return sum(d.textlength(c, font=f) for c in t) + esp * max(len(t) - 1, 0)


def _ecrire(d, x, y, t, f, coul, esp=0):
    for c in t:
        d.text((x, y), c, font=f, fill=coul)
        x += d.textlength(c, font=f) + esp


def _logo_detoure(haut, blanc=False):
    import numpy as np
    im = Image.open(LOGO).convert("RGB")
    a = np.array(im).astype(int)
    alpha = np.clip((236 - a.mean(axis=2)) * 8, 0, 255).astype(np.uint8)
    out = Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), "RGBA")
    out = out.crop(out.getbbox())
    if blanc:
        plein = Image.new("RGBA", out.size, CREME + (255,))
        plein.putalpha(out.split()[3])
        out = plein
    r = haut / out.height
    return out.resize((int(out.width * r), haut), Image.LANCZOS)


def vignette_photo(source, texte, nom, accent=False, signer=False,
                   entiere=False, ancre=0.5):
    """Une photo ENTIERE, posee sur un fond flou tire d'elle-meme.

    Premiere version : la photo etait recadree au centre en 4:5. Comme les
    originaux sont verticaux (9:16), ca coupait les tables et les couverts
    — Yanis l'a refuse, a juste titre.

    Ici l'image n'est JAMAIS rognee : elle est mise a l'echelle pour tenir
    entiere, et le vide autour est comble par une version agrandie et
    floutee de la meme photo. C'est le traitement classique des magazines,
    et il a un avantage : la couleur du fond vient toujours de l'image, donc
    rien ne jure.
    """
    im = Image.open(source).convert("RGB")

    if not entiere:
        # Plein cadre, avec un point de recadrage CHOISI photo par photo.
        # Un recadrage centre automatique coupait les tables en deux : sur
        # une photo verticale, le sujet n'est presque jamais au milieu
        # exact. `ancre` dit quelle part de la hauteur garder au-dessus
        # (0.3 = on garde le haut, 0.7 = on garde le bas).
        r = max(W / im.width, H / im.height)
        gr = im.resize((int(im.width * r) + 1, int(im.height * r) + 1),
                       Image.LANCZOS)
        gx = (gr.width - W) // 2
        gy = int((gr.height - H) * ancre)
        img = gr.crop((gx, gy, gx + W, gy + H)).convert("RGBA")
        d = ImageDraw.Draw(img)
        f = ImageFont.truetype(da.BODONI_B, 54 if accent else 44)
        esp = 4
        lt = _larg(d, texte, f, esp)
        bw, bh = int(lt) + 76, (110 if accent else 92)
        bx, by = (W - bw) // 2, H - bh - 76
        ombre = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ombre).rounded_rectangle(
            [bx + 6, by + 8, bx + bw + 6, by + bh + 8], radius=18,
            fill=(20, 14, 12, 130))
        img.alpha_composite(ombre.filter(ImageFilter.GaussianBlur(14)))
        d = ImageDraw.Draw(img)
        fond_p = TERRA if accent else CREME + (248,)
        encre = CREME if accent else BORDEAUX
        d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=18,
                            fill=fond_p, outline=OR if accent else None,
                            width=3 if accent else 0)
        _ecrire(d, bx + (bw - lt) / 2, by + (bh - f.size) / 2 - 6, texte, f,
                encre, esp)
        if signer:
            lg = _logo_detoure(96, blanc=True)
            img.alpha_composite(lg, ((W - lg.width) // 2, 64))
        os.makedirs(SORTIE, exist_ok=True)
        p2 = os.path.join(SORTIE, nom)
        img.convert("RGB").save(p2, quality=94)
        return p2

    # fond : la meme photo, agrandie et floutee
    rf = max(W / im.width, H / im.height) * 1.25
    fond = im.resize((int(im.width * rf) + 1, int(im.height * rf) + 1),
                     Image.LANCZOS)
    gx, gy = (fond.width - W) // 2, (fond.height - H) // 2
    fond = fond.crop((gx, gy, gx + W, gy + H))
    fond = fond.filter(ImageFilter.GaussianBlur(38))
    # assombri, pour que la photo nette ressorte
    fond = Image.blend(fond, Image.new("RGB", (W, H), (24, 18, 16)), 0.28)
    img = fond.convert("RGBA")

    # La photo entiere, AUSSI GRANDE QUE POSSIBLE. Premiere version : des
    # marges trop larges la reduisaient a une bande etroite au milieu d'un
    # fond flou. Ici on ne laisse qu'un filet, et le texte se pose SUR la
    # photo au lieu d'en dessous — ce qui rend 180 px de hauteur.
    marge_h, marge_b = 40, 40
    dispo_w, dispo_h = W - 2 * 30, H - marge_h - marge_b
    r = min(dispo_w / im.width, dispo_h / im.height)
    photo = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

    cadre = Image.new("RGBA", (photo.width + 20, photo.height + 20),
                      CREME + (255,))
    cadre.paste(photo, (10, 10))
    masque = Image.new("L", cadre.size, 0)
    ImageDraw.Draw(masque).rounded_rectangle(
        [0, 0, cadre.width - 1, cadre.height - 1], radius=16, fill=255)
    cadre.putalpha(masque)

    px, py = (W - cadre.width) // 2, marge_h
    ombre = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o = Image.new("RGBA", cadre.size, (12, 8, 7, 150))
    o.putalpha(cadre.split()[3].point(lambda v: int(v * 150 / 255)))
    ombre.alpha_composite(o, (px + 8, py + 12))
    img.alpha_composite(ombre.filter(ImageFilter.GaussianBlur(22)))
    img.alpha_composite(cadre, (px, py))

    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(da.BODONI_B, 54 if accent else 44)
    esp = 4
    lt = _larg(d, texte, f, esp)
    bw, bh = int(lt) + 76, (110 if accent else 92)
    bx, by = (W - bw) // 2, py + cadre.height - bh - 34

    ombre = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ombre).rounded_rectangle(
        [bx + 6, by + 8, bx + bw + 6, by + bh + 8], radius=18,
        fill=(20, 14, 12, 120))
    img.alpha_composite(ombre.filter(ImageFilter.GaussianBlur(14)))

    d = ImageDraw.Draw(img)
    fond = TERRA if accent else CREME + (248,)
    encre = CREME if accent else BORDEAUX
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=18, fill=fond,
                        outline=OR if accent else None,
                        width=3 if accent else 0)
    _ecrire(d, bx + (bw - lt) / 2, by + (bh - f.size) / 2 - 6, texte, f,
            encre, esp)

    if signer:
        lg = _logo_detoure(96, blanc=True)
        img.alpha_composite(lg, ((W - lg.width) // 2, 72))

    os.makedirs(SORTIE, exist_ok=True)
    p = os.path.join(SORTIE, nom)
    img.convert("RGB").save(p, quality=94)
    return p


def en_tiktok(source, sortie):
    """Decline une vignette Instagram (4:5) en diaporama TikTok (9:16).

    On ne recadre pas : la vignette 4:5 est posee entiere, centree, et le
    haut et le bas sont combles par elle-meme agrandie et floutee. Le
    cadrage du sujet reste donc EXACTEMENT celui qu'on a verifie.
    """
    im = Image.open(source).convert("RGB")
    rf = max(W_TT / im.width, H_TT / im.height) * 1.3
    fond = im.resize((int(im.width * rf), int(im.height * rf)), Image.LANCZOS)
    gx, gy = (fond.width - W_TT) // 2, (fond.height - H_TT) // 2
    fond = fond.crop((gx, gy, gx + W_TT, gy + H_TT))
    fond = fond.filter(ImageFilter.GaussianBlur(44))
    fond = Image.blend(fond, Image.new("RGB", (W_TT, H_TT), (22, 16, 15)), 0.3)

    r = min((W_TT - 40) / im.width, (H_TT - 360) / im.height)
    vig = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    fond.paste(vig, ((W_TT - vig.width) // 2, (H_TT - vig.height) // 2))
    fond.save(sortie, quality=94)
    return sortie


def vignette_finale(nom, titre="VOTRE DEVIS EN UN MESSAGE",
                    sous="Dites-nous votre date et le nombre d'invités"):
    """Dernière vignette : fond bordeaux, logo, appel à l'action."""
    img = Image.new("RGB", (W, H), TERRA).convert("RGBA")
    lueur = Image.new("L", (W, H), 0)
    ImageDraw.Draw(lueur).ellipse([-160, 120, W + 160, H - 60], fill=96)
    img = Image.composite(Image.new("RGBA", (W, H), (205, 104, 102, 255)),
                          img, lueur.filter(ImageFilter.GaussianBlur(170)))

    lg = _logo_detoure(190, blanc=True)
    img.alpha_composite(lg, ((W - lg.width) // 2, 300))

    d = ImageDraw.Draw(img)
    d.line([(W / 2 - 150, 560), (W / 2 + 150, 560)], fill=(238, 214, 196),
           width=3)

    f_t = ImageFont.truetype(da.BODONI_B, 54)
    f_s = ImageFont.truetype(da.BODONI, 34)
    lt = _larg(d, titre, f_t, 6)
    _ecrire(d, (W - lt) / 2, 640, titre, f_t, CREME, 6)

    mots, lignes, cur = sous.split(), [], []
    for m in mots:
        if d.textlength(" ".join(cur + [m]), font=f_s) > 760 and cur:
            lignes.append(" ".join(cur)); cur = [m]
        else:
            cur.append(m)
    lignes.append(" ".join(cur))
    y = 730
    for l in lignes:
        ls = _larg(d, l, f_s)
        _ecrire(d, (W - ls) / 2, y, l, f_s, (246, 232, 226))
        y += 52

    f_c = ImageFont.truetype(da.BODONI_B, 36)
    cpt = "@eventys.paris"
    lc = _larg(d, cpt, f_c, 3)
    bw, bh = int(lc) + 58, 72
    bx, by = (W - bw) // 2, 900
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=CREME)
    _ecrire(d, bx + (bw - lc) / 2, by + 16, cpt, f_c, TERRA, 3)

    os.makedirs(SORTIE, exist_ok=True)
    p = os.path.join(SORTIE, nom)
    img.convert("RGB").save(p, quality=95)
    return p
