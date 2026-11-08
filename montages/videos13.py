"""« Votre repas de Noël » — Reel du 27 octobre.

Troisième video du gabarit « lapin patron », et la premiere a changer
completement de matiere. Demande de Yanis : « fais le meme delire mais avec
d'autres rushes, c'est ce type de montage qui fonctionne, change les rushes
pour du renouveau ».

CE QUI CHANGE : NEUF PLANS SUR DIX VIENNENT DU DOSSIER « Noël », qui n'avait
jamais ete touche. Inventaire fait le 27/10 : les dossiers Noël (11 clips),
Ramadan_ (48 clips) et Anniversaire_ (4 clips) etaient entierement
inexploites, alors que les trois premieres videos puisaient toutes dans les
memes quatre rushes de Mariages. Le 10e plan (IMG_0981, le camion) est lui
aussi inedit.

POURQUOI NOËL MAINTENANT. Nous sommes le 27 octobre : une fin d'annee se
reserve en octobre-novembre, pas en decembre. Et ces rushes ont une lumiere
chaude, des guirlandes et du dore — l'oppose exact des rushes de mariage en
lumiere du jour. Le changement se voit des la premiere image, ce qui est
precisement le but.

LE CALCUL ANNONCE, verifiable contre le catalogue de CLAUDE.md :
    12 chaises Napoleon  x 3 EUR = 36
     2 tables rectang.   x 10 EUR = 20
    12 kits vaisselle    x 2 EUR = 24
     2 nappes            x 9 EUR = 18
    --------------------------------
    TOTAL mobilier               98 EUR
La livraison n'y est pas comprise : facturee selon la zone, annoncee APRES
le total. La nappe apparait pour la premiere fois en video.

CHOIX DES FENETRES. Les onze clips ont ete scannes au pas de 0,25 s
(nettete = variance du laplacien, mouvement = ecart entre images). Les
fenetres retenues sont les plus nettes ET les plus calmes de chaque rush.
SACS CADEAUX. Une premiere version utilisait IMG_3438, IMG_3422 et IMG_3423 :
des sacs de marque (logo bien lisible) occupaient le premier plan sur quatre
plans, dont celui d'ouverture — donc aussi la vignette et la boucle. Ce sont
les cadeaux de Noël d'un vrai client, et une marque tierce n'a rien a faire
en gros plan dans notre publicite. Ces trois rushes sont ecartes, ainsi que
IMG_3405 et IMG_3406 pour la meme raison, et IMG_3402 qui ne montre qu'un
ours en peluche. Restent cinq rushes propres : IMG_3403, IMG_3404, IMG_3428,
IMG_3429 et IMG_3439, d'ou deux fenetres distinctes prises dans trois
d'entre eux — jamais deux plans voisins issus du meme rush.

LA CONTRAINTE REELLE, mesuree en cartographiant les cinq rushes au pas
d'une seconde :
    IMG_3403  0,30 - 5,80   table longue, chemin dore
    IMG_3404  4,00 - 10,00  table rapprochee, nappe blanche, champagne
    IMG_3428  7,00 - 14,00  assiettes, verres, couverts dores
    IMG_3429  0,30 - 2,00 et 4,20 - 10,00   table blanche, chaises, sapin
    IMG_3439  0,30 - 7,00   table longue, rangee de chaises
Soit environ 32 secondes d'images propres pour une video de 31,5 s. Tout le
reste des rushes montre un televiseur, un fauteuil, un ours en peluche, le
plafond, ou des sacs de marque. D'ou deux fenetres prises dans un meme rush
pour trois d'entre eux : ce n'est pas un choix de confort, c'est tout ce que
le dossier contient. Une video de Noël supplementaire demandera de
nouvelles prises.
"""
import os

import graphismes as G
import styles as S
import styles2 as S2
import videos8 as V8
from videos11 import inverse

W, H, FPS = S.W, S.H, S.FPS
OUT, X_MAX = S.OUT, S.X_MAX
TMP = os.path.join(OUT, "_tmp_noel")

NOEL = "Noël"

Y_LAPIN_PIED = 1158
Y_ETIQ = 930
Y_SOUS = 1180
TAILLE_LAPIN = 200
LARG_SOUS = 505
TAILLE_SOUS = 40

# Tous les rushes de Noël sont tenus a la main, en interieur, a la tombee du
# jour : la stabilisation n'est pas optionnelle ici.
A_STABILISER = {"IMG_3404", "IMG_3439", "IMG_3429", "IMG_3428",
                "IMG_3403", "IMG_0981"} | V8.STABILISER

# (stem, dossier, t0, t1, za, zb, texte_dit, etiquette, prix, pose, cote)
# Duree de chaque plan >= duree de sa replique (mesurees apres generation :
# 3,36 / 2,96 / 2,88 / 2,32 / 1,84 / 2,64 / 2,40 / 3,52 / 1,92 / 2,24 s).
PLANS = [
    # Plan 0 = plan de boucle. IMG_3403 0,3-5,8 : table longue, chemin dore,
    # chaises Napoleon, verres — et aucun sac de marque dans le cadre.
    ("IMG_3403", NOEL, 0.30, 3.70, 1.02, 1.07,
     "Noël, c'est dans deux mois. Vous recevez combien ?",
     "12 PERSONNES", "98 €", "16_lunettes_bras_croises", "g"),
    # La rangee de chaises Napoleon est visible de 5 a 7 s dans IMG_3439 :
    # c'est le seul plan du dossier ou on les compte.
    ("IMG_3439", NOEL, 3.40, 7.00, 1.00, 1.06,
     "Douze chaises Napoléon. Trois euros la chaise.",
     "12 CHAISES", "36 €", "17_lunettes_pointe", "g"),
    ("IMG_3429", NOEL, 4.20, 7.60, 1.00, 1.06,
     "Deux tables rectangulaires. Dix euros pièce.",
     "2 TABLES", "20 €", "03_montre_la_main", "g"),
    # Assiettes, verres et couverts dores en gros plan : exactement le kit.
    ("IMG_3428", NOEL, 7.00, 10.60, 1.00, 1.06,
     "Douze kits vaisselle. Deux euros.",
     "12 KITS", "24 €", "02_pouce_leve", "g"),
    # La nappe n'avait jamais ete montree en video alors qu'elle est au
    # catalogue a 9 EUR. Ici elle occupe tout le cadre. 2,7 s suffisent : la
    # replique ne dure que 1,84 s.
    ("IMG_3404", NOEL, 4.00, 6.70, 1.00, 1.05,
     "Deux nappes. Neuf euros.",
     "2 NAPPES", "18 €", "04_pointe_du_doigt", "g"),
    # Vue la plus large de la table complete : c'est l'image du total.
    ("IMG_3439", NOEL, 0.30, 3.30, 1.00, 1.05,
     "Quatre-vingt-dix-huit euros. La table est mise.",
     "TOTAL MOBILIER", "98 €", "13_chemise_bras_croises", "g"),
    # Seul plan hors Noël : il faut bien montrer que la livraison existe.
    # IMG_0991 aurait fait doublon avec le camion du 26/10 (IMG_0990) ;
    # IMG_0981 montre le camion en mouvement dans une rue, c'est inedit.
    ("IMG_0981", "Contenue Vlog_", 0.50, 3.70, 1.00, 1.06,
     "Livraison en Île-de-France, selon la zone.",
     None, None, "12_chemise_debout", "d"),
    ("IMG_3428", NOEL, 10.60, 14.20, 1.00, 1.06,
     "La déco, c'est vous. Je ne fais pas les guirlandes.",
     None, None, "06_bras_leves_content", "d"),
    ("IMG_3429", NOEL, 7.60, 10.00, 1.00, 1.05,
     "C'est pour quelle date ? Écrivez-moi.",
     None, None, "14_chemise_telephone", "d"),
    # Boucle : meme rush et meme cadrage que le plan 0, lu a l'envers, donc
    # il se termine exactement sur l'image d'ouverture.
    ("IMG_3403", NOEL, 0.30, 2.90, 1.02, 1.07,
     "Allez. On recommence.", None, None, "00_salut_pouce_leve_gauche", "g"),
]


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def monte(nom="NOEL_12"):
    d = _dir("plans")
    parts = []
    for i, p in enumerate(PLANS):
        (stem, dos, t0, t1, za, zb, dit, etiq, prix, pose, cote) = p
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = S2.plan(brut, stem, dos, t0, t1, za, zb, speed=1.0)
        if stem in A_STABILISER:
            brut = V8.stabilise(brut, os.path.join(d, f"{i:02d}_stab.mp4"))
        if i == len(PLANS) - 1:
            brut = inverse(brut, os.path.join(d, f"{i:02d}_inv.mp4"))
        cal = []

        if pose:
            chemin = S.sticker(pose)
            taille = TAILLE_LAPIN
            hh = V8.haut_sticker(chemin, taille)
            gauche = cote == "g" or etiq
            x_fin = 20 if gauche else X_MAX - taille
            cote = "g" if gauche else "d"
            cal.append({"png": chemin, "w": taille,
                        "x": V8.entre_cote(x_fin, cote, 0.08),
                        "y": str(Y_LAPIN_PIED - hh),
                        "t0": 0.08, "t1": dur - 0.04, "fade": 0.10})

        if etiq:
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"nl{i}", dur - 0.05,
                                              prix=prix, taille=46)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(Y_ETIQ), "t0": 0.03, "t1": dur - 0.04,
                        "fade": 0.05})

        mots = max(len(dit.split()), 1)
        seq, lw, lh = G.karaoke_seq(dit, f"nl{i}", dur - 0.03,
                                    mots_par_sec=mots / max(dur - 0.45, 0.6),
                                    taille=TAILLE_SOUS, largeur_max=LARG_SOUS)
        cp, cw, ch = V8.carte_texte(lw, lh, f"carte_nl{i}.png")
        # Sur le plan de boucle, le sous-titre s'efface avant la derniere
        # image : sinon il disparait d'un coup au rebouclage, alors que la
        # premiere image de la video n'en porte pas encore.
        fin_sous = dur - (0.25 if i == len(PLANS) - 1 else 0.0)
        cal.append({"png": cp, "w": None, "x": str(int((W - cw) / 2)),
                    "y": str(Y_SOUS - 18), "t0": 0.02, "t1": fin_sous,
                    "fade": 0.08})
        cal.append({"seq": seq, "png": None, "w": None,
                    "x": str(int((W - lw) / 2)), "y": str(Y_SOUS),
                    "t0": 0.02, "t1": fin_sous, "fade": 0.08})

        sp, sw, sh = G.signature()
        cal.append({"png": sp, "w": None, "x": "46", "y": "250",
                    "t0": 0.0, "t1": dur, "fade": 0.3})

        parts.append(S2.pose(brut, cal, os.path.join(d, f"{i:02d}.mp4"), dur))
        print(f"  plan {i} ok ({dur:.2f}s)", flush=True)

    final = os.path.join(OUT, nom + ".mp4")
    S.concat(parts, final)
    return final


if __name__ == "__main__":
    print(monte(), flush=True)
