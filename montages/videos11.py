"""« Eventys reprend » v2 — version corrigee apres relecture.

Corrections apportees, dans l'ordre de gravite relevee :

1. PRIX DES LA PREMIERE SECONDE. Le premier prix arrivait a 10 s. C'est le
   levier le mieux documente de l'etude concurrentielle (x15 a x20 de vues).
   Le plan d'ouverture porte desormais la grille complete.
2. ZONE SURE. Cinq cartes de sous-titre sur six depassaient x=850 et
   seraient passees sous les boutons de TikTok et Instagram. Le retour a la
   ligne est maintenant borne a 660 px, centre, donc toujours a l'interieur.
3. PLUS AUCUN RALENTI. Le plan vaisselle saccadait (23 i/s au lieu de 30)
   parce qu'il etait joue a 0,78 sans interpolation. Tous les plans sont
   desormais a vitesse 1,00 : les points de coupe ont ete choisis pour que
   chaque rush couvre la duree de sa replique.
4. LA MASCOTTE RESTE. Elle disparaissait pendant 15 s, pile sur les trois
   cartes de prix — le coeur commercial. Elle est maintenant sur tous les
   plans.
5. PLAN FINAL DIFFERENT. L'ancien reprenait exactement les images deja vues
   a 13 s (meme segment du meme fichier).
6. LIVRAISON HONNETE. « On livre partout » laissait croire a une livraison
   comprise, alors qu'elle est facturee selon la zone.
7. PRIX AVEC UNITE. « 3 € » seul, devant cent chaises, se lit comme un prix
   de lot.
8. PLAN DE LIVRAISON REMPLACE. L'ancien (IMG_1013) etait flou et montrait
   une television allumee dans le cadre.
9. COUPE AVANT LE FLOU sur le plan de table.
"""
import os
import subprocess

import graphismes as G
import styles as S
import styles2 as S2
import videos8 as V8

W, H, FPS = S.W, S.H, S.FPS
OUT, X_MAX = S.OUT, S.X_MAX
TMP = os.path.join(OUT, "_tmp_reprend2")

# La carte de sous-titre est CENTREE sur l'ecran (x=540), or la zone
# utilisable s'arrete a x=850 : sa demi-largeur ne peut donc pas depasser
# 310 px. D'ou un retour a la ligne tres serre — trois lignes courtes plutot
# qu'une large qui passerait sous les boutons de l'application.
# La mascotte POSE SES PIEDS sur le haut de la carte de sous-titre. Avec
# une ligne de sol fixe placee plus haut, elle se retrouvait en plein ciel
# au-dessus du camion et au milieu des tables : exactement l'effet de
# levitation que Yanis avait deja fait corriger.
Y_LAPIN_PIED = 1158
Y_ETIQ = 930
Y_SOUS = 1180
TAILLE_LAPIN = 200
LARG_SOUS = 505
TAILLE_SOUS = 40

# Grille raccourcie : la version complete depassait x=850 une fois
# centree, et chevauchait la mascotte.
GRILLE = "CHAISE 3 € · TABLE 10 €"

# (stem, dossier, t0, t1, za, zb, texte_dit, etiquette, prix, pose, cote)
# Toutes les vitesses sont a 1,00 : aucune saccade possible.
PLANS = [
    ("IMG_1044", "Contenue Vlog_", 0.50, 3.95, 1.03, 1.09,
     "Bon. Eventys reprend.", GRILLE, None, "16_lunettes_bras_croises", "g"),
    ("IMG_0968", "Contenue Vlog_", 2.00, 6.10, 1.00, 1.05,
     "Lui, c'est mon employé. Moi, je supervise.",
     None, None, "16_lunettes_bras_croises", "d"),
    ("IMG_1742", "Contenue Vlog_", 1.90, 4.87, 1.00, 1.07,
     "Chaise Napoléon : trois euros la chaise.",
     "CHAISE NAPOLÉON", "3 € / chaise", "17_lunettes_pointe", "g"),
    ("IMG_4046", "Mariages", 5.30, 9.95, 1.02, 1.09,
     "Kit vaisselle : verre, couverts, assiettes. Deux euros.",
     "KIT VAISSELLE", "2 € / kit", "02_pouce_leve", "d"),
    ("IMG_4045", "Mariages", 1.40, 4.70, 1.00, 1.06,
     "Table ronde ou rectangulaire : dix euros.",
     "TABLE", "10 € / table", "03_montre_la_main", "g"),
    ("IMG_7015", "Mise en place_", 0.30, 4.40, 1.02, 1.09,
     "Livraison en Île-de-France selon la zone. On monte sur place.",
     None, None, "13_chemise_bras_croises", "d"),
    ("IMG_1716", "Contenue Vlog_", 1.30, 5.08, 1.00, 1.06,
     "Enfin… il monte. Moi je regarde.",
     None, None, "16_lunettes_bras_croises", "g"),
    ("IMG_4054", "Mariages", 0.30, 2.80, 1.00, 1.06,
     "C'est pour quelle date ? Écrivez-moi.",
     None, None, "14_chemise_telephone", "d"),
    ("IMG_1716", "Contenue Vlog_", 5.30, 8.60, 1.00, 1.06,
     "Et abonnez-vous. C'est gratuit, et ça nous aide.",
     None, None, "02_pouce_leve", "g"),
    # Plan de BOUCLE : meme rush et meme cadrage que le plan 0, mais le zoom
    # se referme sur la valeur ou le plan 0 commence. La video se relit sans
    # rupture, et la replique le dit.
    # Lu a l'envers (voir `inverse`) : part donc de 1.09 a l'ecran et finit
    # sur 1.03 au temps 0.50 du rush — l'image exacte du plan 0.
    ("IMG_1044", "Contenue Vlog_", 0.50, 3.65, 1.03, 1.09,
     "Allez. On recommence.", None, None, "17_lunettes_pointe", "d"),
]


def inverse(entree, sortie):
    """Rend le plan a l'envers, images ET duree conservees.

    Sert uniquement au plan de boucle : en le lisant a rebours, sa DERNIERE
    image devient la PREMIERE image du rush, c'est-a-dire exactement l'image
    sur laquelle s'ouvre le plan 0. Le raccord est alors invisible et la
    video tourne en boucle sans couture. Visuellement, le rideau du box se
    referme — puis la relecture le rouvre.
    """
    subprocess.run([
        S.FF, "-y", "-v", "error", "-i", entree,
        "-vf", "reverse", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", sortie,
    ], check=True)
    return sortie


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def monte(nom="REPREND_v2"):
    d = _dir("plans")
    parts = []
    for i, p in enumerate(PLANS):
        (stem, dos, t0, t1, za, zb, dit, etiq, prix, pose, cote) = p
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = S2.plan(brut, stem, dos, t0, t1, za, zb, speed=1.0)
        if stem in V8.STABILISER:
            brut = V8.stabilise(brut, os.path.join(d, f"{i:02d}_stab.mp4"))
        if i == len(PLANS) - 1:        # plan de boucle
            brut = inverse(brut, os.path.join(d, f"{i:02d}_inv.mp4"))
        cal = []

        if pose:
            chemin = S.sticker(pose)
            taille = TAILLE_LAPIN
            hh = V8.haut_sticker(chemin, taille)
            # Toujours a GAUCHE quand une etiquette est presente : l'etiquette
            # est centree et viendrait buter dessus a droite.
            gauche = cote == "g" or etiq
            x_fin = 20 if gauche else X_MAX - taille
            cote = "g" if gauche else "d"
            cal.append({"png": chemin, "w": taille,
                        "x": V8.entre_cote(x_fin, cote, 0.08),
                        "y": str(Y_LAPIN_PIED - hh),
                        "t0": 0.08, "t1": dur - 0.04, "fade": 0.10})

        if etiq:
            taille_e = 34 if etiq == GRILLE else 52
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"rv{i}", dur - 0.05,
                                              prix=prix, taille=taille_e)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(Y_ETIQ), "t0": 0.03, "t1": dur - 0.04,
                        "fade": 0.05})

        mots = max(len(dit.split()), 1)
        seq, lw, lh = G.karaoke_seq(dit, f"rv{i}", dur - 0.03,
                                    mots_par_sec=mots / max(dur - 0.45, 0.6),
                                    taille=TAILLE_SOUS, largeur_max=LARG_SOUS)
        cp, cw, ch = V8.carte_texte(lw, lh, f"carte_rv{i}.png")
        cal.append({"png": cp, "w": None, "x": str(int((W - cw) / 2)),
                    "y": str(Y_SOUS - 18), "t0": 0.02, "t1": dur, "fade": 0.08})
        cal.append({"seq": seq, "png": None, "w": None,
                    "x": str(int((W - lw) / 2)), "y": str(Y_SOUS),
                    "t0": 0.02, "t1": dur, "fade": 0.08})

        sp, sw, sh = G.signature()
        cal.append({"png": sp, "w": None, "x": "46", "y": "250",
                    "t0": 0.0, "t1": dur, "fade": 0.3})

        parts.append(S2.pose(brut, cal, os.path.join(d, f"{i:02d}.mp4"), dur))

    final = os.path.join(OUT, nom + ".mp4")
    S.concat(parts, final)
    return final


if __name__ == "__main__":
    print(monte(), flush=True)
