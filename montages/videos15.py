"""« Juste des chaises » — Reel du 29 octobre.

LA DEMANDE. Yanis, le 28/10 : « on veut pas Noël, trouve des scénarios plus
originaux, du genre regarder ce qu'on peut faire avec juste des chaises.
Garde le même type de montage, change de scénario et de rush. »

LE SCENARIO, ET POURQUOI CELUI-LA. Les trois Reels precedents racontaient
tous une ADDITION : tant de chaises + tant de tables + tant de couverts =
un total. Celui-ci raconte une ECHELLE : vingt, quarante, soixante. Deux
raisons, toutes deux tirees de nos propres chiffres (analyse/ENSEIGNEMENTS.md) :

  1. Le visionnage moyen est de 13,7 s sur une video de 31,5 s. Avec une
     addition, l'argument tombe a la fin — donc apres le decrochage. Avec
     une echelle, le spectateur trouve SON chiffre des la huitieme seconde,
     et il en arrive un autre toutes les trois secondes.
  2. L'etude concurrentielle a releve que personne, sur les huit comptes
     observes, ne repond aux objections. « Je ne veux que des chaises » en
     est une : on la prend de front.

AUCUNE PROMESSE QU'ON NE PEUT PAS TENIR. L'ouverture POSE une question
(« vous voulez juste des chaises ? ») et ne repond pas « sans minimum de
commande » : personne ne m'a dit qu'il n'y en avait pas. Les seuls chiffres
annonces sont des multiplications verifiables contre le catalogue —
20x3=60, 40x3=120, 60x3=180, au tarif de 3 EUR confirme par Yanis le 27/10.
Aucun chiffre de stock n'est annonce (regle de JOURNEE.md : annoncer
« 100 chaises » fixe un plafond), d'ou le « soixante » comme dernier
echelon plutot que le stock reel.

LES RUSHES SONT TOUS NEUFS. Neuf plans, huit rushes, aucun deja publie.
Les trois Reels en ligne puisaient dans IMG_1044, 1052, 1716, 0990, 0974 et
quatre clips de Mariages ; ici, rien de tout cela. La matiere vient d'une
sequence du Vlog jamais ouverte (IMG_1692-1745 : le box, les piles, le
chargement) et du dossier « Mise en place_ », que je n'avais jamais ouvert
du tout.

LA CONTRAINTE QUI A TAILLE LE SCRIPT. Les gros plans de chaises les plus
spectaculaires (IMG_1050-1055) sont MOUS : variance du laplacien 223 a 300,
contre 1100 a 2200 pour la famille IMG_1696-1720. Les melanger ferait
echouer le controle de nettete, et a raison — ca se voit. Le script est
donc ecrit sur les fenetres nettes, et non l'inverse.

POURQUOI LES PLANS 4 ET 6 SONT PLUS LONGS QUE LEUR REPLIQUE. Une
replique qui deborde decale la suivante, d'ou une derive : a la fin du
premier essai, la voix depassait l'image de 0,41 s. On ne corrige pas
ca sur le plan de boucle — l'allonger par son debut ferait finir la
video sur la porte fermee, et la boucle ne retomberait plus sur
l'image d'ouverture. On l'absorbe donc au milieu, sur les deux rushes
assez longs et assez nets pour le supporter.

LE PLAN DE BOUCLE. IMG_1742, la porte du box qui se leve sur les chaises.
Ses deux premieres secondes montrent la porte FERMEE : une surface blanche
plate, variance 31, et surtout rien a regarder dans les deux secondes ou
tout se joue. La fenetre commence donc a 2,20 s, ou la porte est deja
levee et ou les chaises apparaissent.

NOTE SUR L'ANCRAGE. Le parametre `ancre` ne sert a rien ici et c'est
normal : il deplace le recadrage VERTICAL, or une source 16:9 agrandie pour
couvrir du 9:16 est exactement a la bonne hauteur — c'est la LARGEUR qui
est coupee, au centre. L'ancre ne compte que pour les sources 4:3 ou
verticales (Noël, Mise en place IMG_6867) ou il reste de la hauteur a
choisir.
"""
import os
import subprocess

import graphismes as G
import styles as S
import styles2 as S2
import videos8 as V8
import voix_montage as VM
from videos11 import inverse

W, H, FPS = S.W, S.H, S.FPS
OUT, X_MAX = S.OUT, S.X_MAX
TMP = os.path.join(OUT, "_tmp_chaises")

VLOG = "Contenue Vlog_"
MEP = "Mise en place_"

Y_LAPIN_PIED = 1158
Y_ETIQ = 930
Y_SOUS = 1180
TAILLE_LAPIN = 200
LARG_SOUS = 505
TAILLE_SOUS = 40

# Tout est tenu a la main, en exterieur, en marchant : rien ne peut sauter
# la stabilisation.
A_STABILISER = {"IMG_1742", "IMG_1049", "IMG_1700", "IMG_1697", "IMG_1707",
                "IMG_1696", "IMG_1704"} | V8.STABILISER

# (stem, dossier, t0, t1, za, zb, texte_dit, etiquette, prix, pose, cote)
# Duree de chaque plan >= duree de sa replique. Repliques mesurees :
# 2,00 / 2,72 / 2,88 / 2,88 / 3,36 / 2,08 / 2,96 / 2,00 / 2,88 s.
PLANS = [
    # 2,91 s. La porte levee, le box plein de chaises empilees. Nettete
    # 678 -> 1757 sur la fenetre ; avant 2,20 s c'est la porte fermee.
    ("IMG_1742", VLOG, 2.20, 5.11, 1.02, 1.07,
     "Vous voulez juste des chaises ?",
     "CHAISE NAPOLÉON", "3 €", "16_lunettes_bras_croises", "g"),
    # 2,80 s. Gros plan sur une chaise qu'on empile. C'est le seul gros plan
    # NET de la serie IMG_1047-1055 (mediane 585 contre 223-300).
    ("IMG_1049", VLOG, 0.10, 2.90, 1.00, 1.05,
     "La Napoléon blanche. Trois euros pièce.",
     "1 CHAISE", "3 €", "02_pouce_leve", "g"),
    # 3,00 s. Les piles a l'arriere du camion ouvert, en contre-plongee.
    # IMG_6945 (chaises POSEES dans un jardin) avait ete retenu ici : c'est
    # la seule image de toute la reserve ou les chaises sont installees et
    # pretes, et c'etait donc le plan ideal pour le mot « ceremonie ». Il a
    # ete jete apres mesure : il tremble de 4 a 13 sur TOUTE sa longueur,
    # et la stabilisation ne le rattrape pas (elle le laisse a 5,4 quand
    # elle ramene IMG_1696 de 6,9 a 0,18). C'est un plan filme en marchant.
    # Il manque donc toujours une prise de chaises installees, tenue fixe :
    # c'est la premiere ligne de PRISES_A_TOURNER.md.
    ("IMG_1700", VLOG, 0.70, 3.70, 1.00, 1.06,
     "Vingt chaises pour une cérémonie. Soixante euros.",
     "20 CHAISES", "60 €", "17_lunettes_pointe", "g"),
    # 3,00 s. Dechargement : les piles sortent du camion. 15 s de rush
    # exploitables, nettete tres stable (1472-1655).
    ("IMG_1697", VLOG, 2.00, 5.60, 1.00, 1.06,
     "Quarante, pour un mariage. Cent vingt euros.",
     "40 CHAISES", "120 €", "03_montre_la_main", "g"),
    # 4,10 s. Le plan qui donne l'ECHELLE : une pile haute au premier plan,
    # d'autres derriere. Nettete plate a 1180 sur tout le rush, donc on
    # peut l'allonger sans rien degrader — et il le faut : voir ci-dessous.
    ("IMG_1707", VLOG, 0.10, 4.80, 1.00, 1.05,
     "Soixante, pour une grande salle. Cent quatre-vingts.",
     "60 CHAISES", "180 €", "13_chemise_bras_croises", "g"),
    # 2,20 s. Une pile portee a bout de bras vers le camion. Le plan le plus
    # net de tout le montage (2155).
    ("IMG_1696", VLOG, 0.00, 2.20, 1.00, 1.05,
     "Elles arrivent propres et empilées.",
     None, None, "06_bras_leves_content", "d"),
    # 3,10 s. Deuxieme fenetre d'IMG_1697, a l'autre bout du rush : on
    # marche le long de la rangee de piles. QUATRE plans ont ete jetes
    # avant celui-ci, et la liste vaut d'etre gardee :
    #   IMG_0967 — l'interieur du camion VIDE. Annoncer la livraison sur un
    #     camion vide, c'est illustrer a cote.
    #   IMG_0968 — un camion tiers floque « …Portugal » occupe le tiers
    #     droit du cadre et reste LISIBLE meme zoome a 1,30.
    #   IMG_1721 et IMG_1720 — releves par le relecteur : on y porte deux
    #     TABLES PLIANTES. La video dit « juste des chaises, sans rien
    #     d'autre a louer » et livrait des tables, au moment meme du
    #     message final. C'est la contradiction la plus couteuse qu'on
    #     pouvait publier.
    # Deux fenetres d'un meme rush sont admises tant qu'elles ne sont pas
    # voisines : ici les plans 3 et 6.
    ("IMG_1697", VLOG, 11.00, 14.10, 1.00, 1.06,
     "Livrées en Île-de-France, ou à récupérer au box.",
     None, None, "12_chemise_debout", "d"),
    # 2,60 s. La peluche au premier plan regarde le chargement. C'est le
    # VRAI lapin, celui dont le sticker des Reels est tire : la mascotte
    # dessinee et son modele sont dans la meme image, juste avant le
    # message final. Rush de 72 s, donc large choix de fenetre ; celle-ci
    # ne contient ni table ni vehicule tiers.
    ("IMG_1704", VLOG, 18.50, 21.10, 1.00, 1.05,
     "C'est pour quelle date ? Écrivez-moi.",
     None, None, "14_chemise_telephone", "d"),
    # Boucle : meme rush et meme fenetre que le plan 0, lu a l'envers, donc
    # la derniere image est l'image d'ouverture. Les deux appels, comme le
    # Reel du 20/10 (arbitrage de Yanis du 27/10).
    ("IMG_1742", VLOG, 2.20, 5.11, 1.02, 1.07,
     "Abonnez-vous. Allez, on recommence.",
     None, None, "00_salut_pouce_leve_gauche", "g"),
]


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def monte(nom="CHAISES_60"):
    d = _dir("plans")
    parts, durees = [], []
    for i, p in enumerate(PLANS):
        (stem, dos, t0, t1, za, zb, dit, etiq, prix, pose, cote) = p
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = S2.plan(brut, stem, dos, t0, t1, za, zb, speed=1.0)
        if stem in A_STABILISER:
            brut = V8.stabilise(brut, os.path.join(d, f"{i:02d}_stab.mp4"))
        if i == len(PLANS) - 1:
            brut = inverse(brut, os.path.join(d, f"{i:02d}_inv.mp4"))
        durees.append(dur)
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
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"ch{i}", dur - 0.05,
                                              prix=prix, taille=46)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(Y_ETIQ), "t0": 0.03, "t1": dur - 0.04,
                        "fade": 0.05})

        mots = max(len(dit.split()), 1)
        seq, lw, lh = G.karaoke_seq(dit, f"ch{i}", dur - 0.03,
                                    mots_par_sec=mots / max(dur - 0.45, 0.6),
                                    taille=TAILLE_SOUS, largeur_max=LARG_SOUS)
        cp, cw, ch = V8.carte_texte(lw, lh, f"carte_ch{i}.png")
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
    return final, durees


def sonorise(video, durees, dossier_voix, sortie):
    """Pose la bande voix sur le montage, calee sur les plans reels.

    `voix_montage.planning` attend le format de plans de styles.py ; ici on
    connait les durees exactes rendues par le montage, donc on construit le
    planning directement. Une replique commence au debut de son plan, sauf
    si la precedente n'est pas finie — on ne superpose jamais deux voix.
    """
    import ambiance
    debuts, t = [], 0.0
    for d in durees:
        debuts.append(t)
        t += d
    repliques, libre = [], 0.0
    for i, deb in enumerate(debuts):
        f = os.path.join(dossier_voix, f"{i:02d}.mp3")
        if not os.path.exists(f):
            raise SystemExit(f"replique manquante : {f}")
        dv = VM.duree(f)
        debut = max(deb, libre)
        repliques.append((f, debut, dv))
        libre = debut + dv + VM.PAUSE
        if debut > deb + 0.01:
            print(f"  replique {i} decalee de {debut - deb:+.2f}s", flush=True)
    fin = repliques[-1][1] + repliques[-1][2]
    print(f"  voix : {fin:.2f}s pour une image de {t:.2f}s", flush=True)
    if fin > t:
        raise SystemExit(f"la voix depasse l'image de {fin - t:.2f}s — "
                         f"rallonge le dernier plan par son DEBUT de rush")
    lit = ambiance.lit_sonore(t)
    return VM.melange(video, repliques, sortie, lit=lit)


if __name__ == "__main__":
    import sys
    v, durees = monte()
    print(v, flush=True)
    if "--muet" not in sys.argv:
        s = sonorise(v, durees,
                     os.path.join(os.path.dirname(OUT), "voix", "chaises",
                                  "JONATHAN"),
                     v.replace(".mp4", "_son.mp4"))
        print(s, flush=True)
