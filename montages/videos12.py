"""« Cinquante personnes ? On calcule » — Reel du 26 octobre.

Pourquoi ce montage ressemble au Reel du 20 octobre : parce que c'est le
seul contenu qui a marche. Mesure a 6 jours :

    20/10  Reel lapin « retour »        1 450 vues, 36 j'aime, 8,9 s vues
    22/10  Reel coulisses (photos)        588 vues, 13 j'aime, 6,4 s
    21/10  Carrousel                      242 vues,  9 j'aime

Le format est donc repris a l'identique : lapin present sur tous les plans,
prix des le debut, sous-titres karaoke, boucle sans couture. Ce qui change :

1. LE SUJET. Le Reel du 20 listait des prix a l'unite. Celui-ci repond a la
   question que le client se pose vraiment : « combien pour mon mariage de
   cinquante personnes ». Un total chiffre est plus partageable qu'une
   grille tarifaire.
2. TROIS PLANS SUR DIX SONT NOUVEAUX : IMG_1052, IMG_0990 et IMG_0974,
   jamais publies. C'est peu, et c'est la limite du materiel : sur les 30
   videos du dossier Mariages, 24 sont en 464x832 ou 480x848, trois en
   848x480 et deux en 720x1280. Seuls IMG_4045, IMG_4046, IMG_4054 et
   IMG_4060 sont en 1920x1080 et tiennent un 1080x1920. Les rushes de
   mariage sont donc forcement revus.
   Les fenetres de coupe sont deplacees, mais pas toutes disjointes de
   celles du 20 octobre : IMG_4054 et IMG_1716 gardent leur point
   d'entree, et IMG_4046 recouvre 2,65 s de sa fenetre precedente.
   IMG_4046 sert d'ailleurs DEUX fois ici (plans 2 et 8) : une vue large de
   piece et un detail de chemin de table, 16 s d'ecart, rien de commun a
   l'image.
   A tourner ou a reprendre avant la prochaine video, pour sortir de cette
   boucle : IMG_4060 et IMG_6946 n'ont encore jamais servi, et
   12941d2e….mov est le seul 1080x1920 natif du dossier — utilisable
   depuis le 15/10 a condition de recadrer le texte incruste.

3. PAS DE CARTE « BIENVENUE CHEZ EVENTYS ». Derogation assumee a la
   regle 5 de REGLES_EQUIPE, et posee ici comme la regle l'exige. Motif :
   ce montage reprend volontairement le gabarit du Reel du 20 octobre, qui
   ouvre sur la question du client et non sur une carte de marque. La
   signature @eventys.paris est presente sur les dix plans, et le nom est
   dit dans la legende.
4. LA LIVRAISON EST ANNONCEE APRES LE TOTAL, jamais dedans : elle est
   facturee selon la zone, le total ne la comprend pas.

Les quantites citees (50 chaises, 5 tables, 50 kits) sont une COMMANDE
type, pas le stock : Yanis a demande qu'on ne parle jamais de stock, un
chiffre affiche freine un client qui en veut davantage.
"""
import os
import subprocess

import graphismes as G
import styles as S
import styles2 as S2
import videos8 as V8
from videos11 import inverse

W, H, FPS = S.W, S.H, S.FPS
OUT, X_MAX = S.OUT, S.X_MAX
TMP = os.path.join(OUT, "_tmp_calcul")

Y_LAPIN_PIED = 1158
Y_ETIQ = 930
Y_SOUS = 1180
TAILLE_LAPIN = 200
LARG_SOUS = 505
TAILLE_SOUS = 40

# Plans tenus a la main qui n'etaient pas dans la liste de videos8.
A_STABILISER = {"IMG_1052", "IMG_0974", "IMG_0990"} | V8.STABILISER

# (stem, dossier, t0, t1, za, zb, texte_dit, etiquette, prix, pose, cote)
PLANS = [
    ("IMG_1044", "Contenue Vlog_", 0.50, 3.90, 1.03, 1.09,
     "Cinquante personnes à table ? On calcule.",
     # Le total est annonce des la premiere seconde. Le Reel du 20 octobre
     # affichait sa grille de prix a 0,8 s, et c'est le seul levier mesure
     # dans l'etude concurrentielle. Donner le resultat n'enleve rien : la
     # video explique comment on y arrive, et la legende le dit aussi.
     "50 PERSONNES", "300 €", "16_lunettes_bras_croises", "g"),
    ("IMG_1052", "Contenue Vlog_", 0.40, 4.00, 1.00, 1.06,
     "Cinquante chaises Napoléon. Trois euros pièce.",
     "50 CHAISES", "150 €", "17_lunettes_pointe", "g"),
    # IMG_4045 1,40-4,80 a d'abord ete pris ici : les images rendues sont
    # trainees (panoramique trop rapide pour la vitesse d'obturation).
    # Le controle de tremblement ne le voit pas — un file regulier bouge
    # peu d'une image a l'autre, il est seulement FLOU. D'ou la mesure de
    # nettete par plan ajoutee a meta/controle.py le meme jour.
    ("IMG_4046", "Mariages", 7.30, 10.70, 1.00, 1.06,
     "Cinq tables rondes. Dix euros la table.",
     "5 TABLES", "50 €", "03_montre_la_main", "g"),
    ("IMG_4054", "Mariages", 0.30, 3.90, 1.02, 1.08,
     "Cinquante kits vaisselle. Deux euros.",
     "50 KITS", "100 €", "02_pouce_leve", "g"),
    # IMG_6945 avait ete choisi ici (chaises dans un jardin) : mesure a
    # 7,2 de tremblement contre 2,1 pour le pire des autres plans. Le rush
    # est un panoramique rapide d'un bout a l'autre, il n'existe aucune
    # fenetre tenue dedans.
    # Remplace par la SEULE fenetre nette de IMG_4045 : 7,80 a 10,10. Avant,
    # le panoramique file ; apres, le cadre quitte la table et finit sur un
    # buffet sombre. La borne a d'abord ete posee a 10,30 : il restait
    # 12 images filees en fin de plan, mesurees au pas de 0,2 s. Ce plan est
    # court (2,3 s) a dessein — la replique dure 2,24 s et c'est la chute.
    ("IMG_4045", "Mariages", 7.80, 10.10, 1.00, 1.05,
     "Trois cents euros. Tout le mobilier.",
     "TOTAL MOBILIER", "300 €", "13_chemise_bras_croises", "g"),
    ("IMG_0990", "Contenue Vlog_", 0.40, 3.60, 1.00, 1.06,
     "Livraison en Île-de-France, selon la zone.",
     None, None, "12_chemise_debout", "d"),
    ("IMG_0974", "Contenue Vlog_", 1.00, 4.40, 1.00, 1.06,
     "On charge, on livre, on monte sur place.",
     None, None, "15_tshirt_pointe_ordre", "g"),
    ("IMG_1716", "Contenue Vlog_", 1.30, 4.50, 1.00, 1.06,
     "Enfin… lui monte. Moi je compte.",
     None, None, "16_lunettes_bras_croises", "d"),
    ("IMG_4046", "Mariages", 1.10, 3.90, 1.00, 1.06,
     "C'est pour quelle date ? Écrivez-moi.",
     None, None, "14_chemise_telephone", "d"),
    # Plan de boucle : meme rush et meme cadrage que le plan 0, lu a
    # l'envers, donc il se termine exactement sur l'image d'ouverture.
    ("IMG_1044", "Contenue Vlog_", 0.50, 3.10, 1.03, 1.09,
     "Allez. On recompte.", None, None, "17_lunettes_pointe", "g"),
]


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def monte(nom="CALCUL_50"):
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
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"cl{i}", dur - 0.05,
                                              prix=prix, taille=46)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(Y_ETIQ), "t0": 0.03, "t1": dur - 0.04,
                        "fade": 0.05})

        mots = max(len(dit.split()), 1)
        seq, lw, lh = G.karaoke_seq(dit, f"cl{i}", dur - 0.03,
                                    mots_par_sec=mots / max(dur - 0.45, 0.6),
                                    taille=TAILLE_SOUS, largeur_max=LARG_SOUS)
        cp, cw, ch = V8.carte_texte(lw, lh, f"carte_cl{i}.png")
        # Sur le PLAN DE BOUCLE, le sous-titre s'efface 0,25 s avant la fin.
        # Sinon il disparait d'un coup au rebouclage, alors que la premiere
        # image de la video n'en porte pas encore : le raccord se voyait.
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
