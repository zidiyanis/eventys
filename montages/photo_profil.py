"""Photo de profil Eventys — la tete du lapin, lisible en tout petit.

Une photo de profil s'affiche en rond, souvent a 40 px de cote dans un fil.
Une silhouette entiere y devient une tache. On ne garde donc que la TETE,
cadree large, sur un fond uni de la charte.
"""
import os

from PIL import Image, ImageDraw, ImageFilter

import da

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "PHOTO_PROFIL.png")
TAILLE = 1000


def construire(pose="16_lunettes_bras_croises", fond=(243, 239, 230)):
    src = os.path.join(ICI, "_cartes", "stickers", pose + ".png")
    lapin = Image.open(src).convert("RGBA")

    # On isole la tete : les oreilles tombantes occupent le haut du sticker,
    # la tete se trouve dans le premier tiers de la hauteur.
    w, h = lapin.size
    tete = lapin.crop((0, 0, w, int(h * 0.46)))

    img = Image.new("RGBA", (TAILLE, TAILLE), fond + (255,))
    d = ImageDraw.Draw(img)

    # lueur chaude centrale, pour que le fond ne soit pas un aplat mort
    lueur = Image.new("L", (TAILLE, TAILLE), 0)
    ImageDraw.Draw(lueur).ellipse([80, 80, TAILLE - 80, TAILLE - 80], fill=90)
    img = Image.composite(Image.new("RGBA", (TAILLE, TAILLE), (253, 250, 244, 255)),
                          img, lueur.filter(ImageFilter.GaussianBlur(160)))

    # anneau dore, legerement rentre pour survivre au masque circulaire
    d = ImageDraw.Draw(img)
    d.ellipse([26, 26, TAILLE - 26, TAILLE - 26],
              outline=(198, 162, 86, 255), width=9)

    # la tete, cadree large et centree
    cible = int(TAILLE * 0.74)
    r = cible / tete.width
    tete = tete.resize((cible, int(tete.height * r)), Image.LANCZOS)
    # centre dans le cercle : cale en haut, la moitie basse restait vide
    img.alpha_composite(tete, ((TAILLE - tete.width) // 2,
                               (TAILLE - tete.height) // 2))

    img.convert("RGB").save(SORTIE, quality=97)
    return SORTIE


if __name__ == "__main__":
    p = construire()
    # apercu tel qu'il apparaitra : rond et tres petit
    im = Image.open(p).convert("RGBA")
    masque = Image.new("L", im.size, 0)
    ImageDraw.Draw(masque).ellipse([0, 0, im.size[0], im.size[1]], fill=255)
    im.putalpha(masque)
    for t in (160, 48):
        a = im.resize((t, t), Image.LANCZOS)
        fond = Image.new("RGB", (t, t), (255, 255, 255))
        fond.paste(a, (0, 0), a)
        fond.save(os.path.join(ICI, "_apercu", f"profil_{t}.png"))
    print(p)
