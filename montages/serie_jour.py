"""La serie de stories du jour — trois natures melangees.

Yanis a demande deux fois la meme chose : « utilise d'autres videos, d'autre
contenu des rushes, et que ce soit plus varie ». Une serie de stories faite
uniquement de cartes fabriquees ressemble a un catalogue, et une serie faite
uniquement de captures du Reel ne donne aucune raison de la regarder.

La regle retenue, a appliquer tous les jours :
  - au moins TROIS clips de rush differents, habilles (story_clip.py),
  - au plus DEUX cartes fabriquees (stories2.py),
  - et jamais un rush deja utilise dans le Reel du meme jour.

Depuis le 28/10, `meta/publier.py` ecarte en plus automatiquement toute
story dont le fichier a deja ete publie ces quatorze derniers jours : la
regle n'est plus seulement une intention, elle est verifiee.

Les teintes alternent beige / bordeaux : deux fonds identiques a la suite se
confondent quand on fait defiler. L'ordre du jour est donc
beige, bordeaux, beige, bordeaux, beige — le relecteur avait releve deux
bordeaux de suite le 28/10.

    python H:/eventys/montages/serie_jour.py
"""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

import story_clip as C  # noqa: E402
import story_video as V  # noqa: E402
import stories2 as S  # noqa: E402

RACINE = os.path.dirname(ICI)
LIT = os.path.join(RACINE, "assets", "son", "lit_stories.wav")
SRC = os.path.join(ICI, "_stories", "src")

VLOG = "Contenue Vlog_"

RAM = "Ramadan_"
MEP = "Mise en place_"

# Les rushes du Reel du jour (« La table dressee a 59 € », videos16.py).
# Aucun ne doit reapparaitre ici : une story qui rejoue le Reel ne donne
# aucune raison d'etre regardee.
DANS_LE_REEL = {"IMG_9459", "IMG_9458", "IMG_9414", "IMG_9422",
                "IMG_6945"}


def serie(dossier):
    """Serie du 31/10, en prolongement du Reel « La table se dresse ».

    Le Reel montre une table finie chez un client. La serie montre d'ou
    elle sort : le box, le camion, puis un detail que le Reel n'a pas pris.
    Aucun des trois clips n'est dans le Reel, et les deux premiers ne sont
    pas non plus ceux de la serie du 29/10 (qui venaient du Vlog).

    AUCUN PRIX DE CHAISE AUJOURD'HUI, ni ici ni dans le Reel : le catalogue
    prevoit 2 EUR en hiver et la date de bascule n'est pas fixee. On est le
    31 octobre. Les trois prix affiches (table 10, nappe 9, kit 2) n'ont
    pas de tarif saisonnier.
    """
    os.makedirs(dossier, exist_ok=True)
    out = []
    for stem in ("IMG_6868", "IMG_9441", "IMG_7015"):
        assert stem not in DANS_LE_REEL, stem

    # 1. Le box, les piles de chaises ET les tables pliantes contre le mur.
    # Fenetre courte : apres 2 s la camera part sur le mur du couloir.
    out.append(C.clip(
        "IMG_6868", MEP, 0.10, 2.00,
        "LE STOCK", "Chaises et tables pliantes",
        os.path.join(dossier, "1_stock.mp4"),
        teinte="beige", lit=LIT, debut_son=0.0, va_et_vient=True))

    # 2. Le detail : verres en cristal et chemin de table, sur la table du
    # Reel mais sous un angle que le Reel ne prend pas.
    out.append(C.clip(
        "IMG_9441", RAM, 0.50, 3.00,
        "LE DÉTAIL", "Verres en cristal",
        os.path.join(dossier, "2_detail.mp4"),
        teinte="bordeaux", lit=LIT, debut_son=6.0, va_et_vient=True))

    # 3. Le van charge de chaises et de tables rondes pliantes : la nature
    # « coulisses » que les deux autres clips n'ont pas.
    out.append(C.clip(
        "IMG_7015", MEP, 0.30, 2.80,
        "ON CHARGE", "Livraison en Île-de-France",
        os.path.join(dossier, "3_camion.mp4"),
        teinte="beige", lit=LIT, debut_son=12.0, va_et_vient=True))

    # 4. Carte fabriquee : la table du Reel, pour qui tombe sur la story
    # sans avoir vu la video.
    fiche = S.fiche_produit(
        os.path.join(SRC, "longue.jpg"), "TABLE 70x180", "10 €",
        "8 à 10 personnes · nappe 9 €",
        nom="_jour_longue.png", teinte="bordeaux")
    out.append(V.rendre(fiche, os.path.join(dossier, "4_table.mp4"),
                        duree=5.5, lit=LIT, debut_son=17.0))

    # 5. La grille de prix, pour qui arrive en cours de serie. La chaise
    # n'y figure pas : voir la note sur le tarif d'hiver, en tete.
    # `ronde.jpg` a ete retiree de la grille : le relecteur a releve le
    # 31/10 qu'on n'y voit pas que le plateau est rond, alors que la
    # vignette annonce « TABLE RONDE ». On ne montre pas ce qu'on ne
    # prouve pas.
    grille = S.grille_catalogue([
        (os.path.join(SRC, "longue.jpg"), "TABLE 70x180", "10 €"),
        (os.path.join(SRC, "couvert.jpg"), "KIT VAISSELLE", "2 €"),
        (os.path.join(SRC, "camion.jpg"), "LIVRAISON", "IDF"),
        (os.path.join(SRC, "box.jpg"), "RETRAIT AU BOX", "VAL-D'OISE"),
    ], nom="_jour_grille.png", teinte="beige")
    out.append(V.rendre(grille, os.path.join(dossier, "5_grille.mp4"),
                        duree=6.5, lit=LIT, debut_son=23.0))

    return out


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ICI, "_stories",
                                                           "jour")
    for p in serie(d):
        print(" ", os.path.basename(p), flush=True)
