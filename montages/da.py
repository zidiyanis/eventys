"""Charte graphique Eventys : fabrique les cartes de texte en PNG.

Les couleurs et la typo sont relevees sur les affiches de Yanis
(`rushes\\Affiches - infos_`) :
  - fond creme des fiches        -> CREME
  - "EVENT" du logo, bordeaux    -> BORDEAUX
  - "YS" du logo, rouge terracotta -> ROUGE
  - titres en Didone tres espacee -> Bodoni MT (installe sur le poste)

On passe par Pillow et non par drawtext de ffmpeg : drawtext ne sait pas
faire d'interlettrage ni de bicolore, et c'est justement ce qui fait la DA.

Refonte 2026-10-14 (moteur d'effets) :
- `carte()` accepte maintenant un `taille_prix` optionnel (defaut 92, donc
  comportement identique si on ne le precise pas) pour pouvoir marquer un
  prix plus fort sur une carte precise (ex. carte "Total" d'un pack
  chiffre), demande explicite du script valide.
- `carte_compteur()` est nouveau : fabrique une petite suite d'images pour
  un effet de compteur de prix (0 -> prix final sur quelques crans), a
  partir de la meme fonction `carte()`. Ne fonctionne que pour des prix du
  type "<nombre> <suffixe>" (ex. "120 €") ; leve une erreur sinon plutot
  que d'inventer un affichage.
"""
import os

from PIL import Image, ImageDraw, ImageFont

CREME = (246, 242, 240)
BORDEAUX = (111, 47, 47)
ROUGE = (175, 68, 68)
ENCRE = (43, 34, 32)

F = "C:/Windows/Fonts/"
BODONI = F + "BOD_R.TTF"
BODONI_I = F + "BOD_I.TTF"
BODONI_B = F + "BOD_B.TTF"

W, H = 1080, 1920
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cartes")


def _font(path, size):
    return ImageFont.truetype(path, size)


def _largeur(draw, texte, font, espace=0):
    """Largeur d'un texte avec interlettrage ajoute."""
    total = sum(draw.textlength(c, font=font) for c in texte)
    return total + espace * max(0, len(texte) - 1)


def _ecrire(draw, x, y, texte, font, fill, espace=0):
    """Ecrit lettre par lettre pour pouvoir espacer (drawtext ne sait pas)."""
    for c in texte:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + espace


def intro(nom="intro.png"):
    """Carte d'ouverture commune aux trois videos : Bienvenue chez EVENTYS."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    bande_h = 500
    y0 = 1130
    # bande creme, legerement transparente pour laisser voir le box
    d.rounded_rectangle([70, y0, W - 70, y0 + bande_h], radius=18,
                        fill=CREME + (238,))

    f_petit = _font(BODONI_I, 54)
    t = "Bienvenue chez"
    d.text(((W - d.textlength(t, font=f_petit)) / 2, y0 + 58), t,
           font=f_petit, fill=ENCRE)

    # EVENTYS bicolore comme le logo : EVENT bordeaux + YS rouge
    f_logo = _font(BODONI_B, 136)
    esp = 14
    g, h = "EVENT", "YS"
    lg = _largeur(d, g, f_logo, esp) + esp
    lh = _largeur(d, h, f_logo, esp)
    x = (W - (lg + lh)) / 2
    _ecrire(d, x, y0 + 152, g, f_logo, BORDEAUX, esp)
    _ecrire(d, x + lg, y0 + 152, h, f_logo, ROUGE, esp)

    d.line([W / 2 - 70, y0 + 352, W / 2 + 70, y0 + 352],
           fill=BORDEAUX + (140,), width=2)

    f_sous = _font(BODONI, 40)
    s = "LOCATION ÉVÉNEMENTIELLE"
    esp2 = 9
    ls = _largeur(d, s, f_sous, esp2)
    _ecrire(d, (W - ls) / 2, y0 + 392, s, f_sous, BORDEAUX, esp2)

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, nom)
    im.save(p)
    return p


MAXL = W - 200  # largeur de texte disponible dans la carte


def _ajuster(d, titre, esp):
    """Reduit le corps puis coupe en deux lignes pour que le titre tienne.

    Sans ca les titres longs ("Île-de-France · message privé") depassaient
    de la carte et se faisaient rogner par le bord de l'image.
    """
    for taille in (58, 54, 50, 46):
        f = _font(BODONI, taille)
        if _largeur(d, titre, f, esp) <= MAXL:
            return f, [titre]
    f = _font(BODONI, 50)
    mots = titre.split()
    # coupure a l'endroit qui equilibre le mieux les deux lignes
    best, ecart = 1, None
    for i in range(1, len(mots)):
        a = _largeur(d, " ".join(mots[:i]), f, esp)
        b = _largeur(d, " ".join(mots[i:]), f, esp)
        if ecart is None or abs(a - b) < ecart:
            best, ecart = i, abs(a - b)
    return f, [" ".join(mots[:best]), " ".join(mots[best:])]


def carte(titre, prix, nom, position="bas", taille_prix=92):
    """Carte produit : titre en capitales espacees + prix en rouge.

    `taille_prix` (defaut 92, comportement inchange) permet de marquer un
    prix plus fort sur une carte precise (ex. "Total" d'un pack chiffre) ;
    c'est une demande du script valide, pas une initiative de mise en page.
    """
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    esp = 7
    f_prix = _font(BODONI_B, taille_prix)
    titre = titre.upper()
    f_titre, lignes = _ajuster(d, titre, esp)

    lt = max(_largeur(d, l, f_titre, esp) for l in lignes)
    lp = d.textlength(prix, font=f_prix) if prix else 0
    larg = min(max(lt, lp) + 108, W - 120)

    bloc = len(lignes) * (f_titre.size + 16)
    haut = bloc + 48 + (120 if prix else 36) + max(0, taille_prix - 92)

    x0 = (W - larg) / 2
    # 480 (pas 430) : le bas de la carte "bas" doit rester a y<=1440
    # (zone sure Reels/TikTok), quelle que soit la hauteur du bloc de texte.
    y0 = 300 if position == "haut" else H - haut - 480

    d.rounded_rectangle([x0, y0, x0 + larg, y0 + haut], radius=14,
                        fill=CREME + (242,))

    y = y0 + 36
    for l in lignes:
        ll = _largeur(d, l, f_titre, esp)
        _ecrire(d, x0 + (larg - ll) / 2, y, l, f_titre, ENCRE, esp)
        y += f_titre.size + 16

    if prix:
        # filet fin, comme les cercles des couvertures de stories
        yf = y + 14
        d.line([x0 + larg / 2 - 48, yf, x0 + larg / 2 + 48, yf],
               fill=BORDEAUX + (150,), width=2)
        d.text((x0 + (larg - lp) / 2, yf + 12), prix, font=f_prix, fill=ROUGE)

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, nom)
    im.save(p)
    return p


def carte_compteur(titre, prix_final, nom_base, position="bas", crans=4,
                    taille_prix=92):
    """Suite de PNG pour un effet de compteur 0 -> prix_final (~0.4 s).

    `prix_final` doit etre "<nombre> <suffixe>" (ex. "120 €", "3 €").
    Retourne la liste des chemins, dans l'ordre (le dernier == le prix
    final, identique a `carte(titre, prix_final, ...)`).
    """
    morceaux = prix_final.strip().split(maxsplit=1)
    if len(morceaux) != 2 or not morceaux[0].isdigit():
        raise ValueError(
            f"carte_compteur ne sait pas animer ce prix : {prix_final!r} "
            "(format attendu : '<nombre> <suffixe>', ex. '120 €')")
    valeur, suffixe = int(morceaux[0]), morceaux[1]
    chemins = []
    for i in range(crans):
        v = round(valeur * (i + 1) / crans)
        texte = f"{v} {suffixe}"
        chemins.append(carte(titre, texte, f"{nom_base}_c{i}.png", position,
                              taille_prix))
    return chemins


if __name__ == "__main__":
    print(intro())
    print(carte("Chaise Napoléon", "3 €", "test.png"))
