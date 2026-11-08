"""« La table se dresse » — Reel du 31 octobre.

LA DEMANDE. Yanis, le 31/10 : « vas-y lance une video ». Le journal montre
deux jours vides (30 et 31/10, « pas de video aujourd'hui ») : la derniere
publication est TABLE_59 le 29/10.

CE QU'ON A TROUVE, ET QUI MANQUAIT DEPUIS LE DEBUT. `PRISES_A_TOURNER.md`
reclamait depuis le 29/10 « un plan large FIXE de la table entiere avec ses
chaises ». Il existe : `Ramadan_/IMG_9459`, 240 secondes, 1080x1920,
camera POSEE, cadre immobile du debut a la fin. Le rush filme le
DE-dressage d'une table en fin de soiree. Lu a l'envers et accelere, il
montre donc une table qui SE DRESSE toute seule — ce qui etait sur la
liste des formats a essayer (timelapse d'installation + avant/apres) et
qu'aucun rush ne permettait jusqu'ici.

LA PREMIERE VERSION A ETE REFUSEE, ET ELLE AVAIT RAISON DE L'ETRE. Le
montage d'origine lisait ce rush a l'envers et a x5 : la table se dressait
toute seule. Le relecteur a montre qu'une SECONDE personne, dont on n'a
pas l'accord, est dans le cadre a 3-5 s, 9,5-10,8 s et apres 14,5 s du
rush — son visage etait lisible dans le montage fini a 2,1 s et 24,1 s.
Mon releve (« elle entre a 20 s ») etait faux : fait sur une planche a
1,5 s d'intervalle, pas sur la fenetre. C'est la DEUXIEME fois en trois
jours que je commets exactement cette erreur.

J'ai alors balaye les 240 secondes entieres : les seules plages ou Yanis
est seul font 3 a 4 secondes. Un timelapse a besoin de dizaines de
secondes. Le concept attend donc l'accord de cette personne — il est note
dans PRISES_A_TOURNER.md. En attendant, on garde la meme table et le meme
plan large, a vitesse reelle (x1,1), sur la seule fenetre verifiee PLEIN
CADRE toutes les 0,2 secondes : 11,00 a 14,30 s, Yanis seul.

LE SUJET EST DONC LE SERVICE, pas l'addition : qui porte, qui monte, qui
dresse. Le relecteur avait releve le 29/10 que c'etait le troisieme calcul
en quatre jours ; ici trois prix passent en cours de route et il n'y a pas
de total. Le premier tombe dans la premiere seconde, comme l'exige
JOURNEE.md.

PAS D'OUVERTURE SUR LE BOX, ET C'EST UN ECART ASSUME. REGLES_EQUIPE.md §5
demande une ouverture « box qui s'ouvre » ou une carte « Bienvenue chez
EVENTYS ». Elle est incompatible avec la regle de boucle de JOURNEE.md :
le dernier plan doit ramener a la premiere image, et une carte de titre
fixe en ouverture casse la boucle en plus de bruler les deux secondes ou
le prix doit apparaitre. L'ecart est signale a Yanis, c'est lui qui
tranche.

LA TABLE. Rectangulaire, nappe blanche, chemin vert sauge, assiettes a
filet dore, couverts dores, verres en cristal, chaises Napoleon. C'est la
SECONDE table du dossier Ramadan_ — celle que le montage du 29/10 avait
ecartee parce qu'elle porte des lanternes dorees a croissant de lune.

ET C'EST UN ARBITRAGE, PAS UN OUBLI. Les lanternes sont sur la table dans
la quasi-totalite des rushes de cette table : on ne peut pas les en
sortir. Le choix etait entre (a) montrer cette table-la avec la
decoration de son client, ou (b) remonter pour la troisieme fois une
table deja publiee. Le relecteur a mesure ce que ca coute, et il faut le
dire sans l'arrondir : le croissant lui-meme ne fait que 33 x 53 px, mais
la LANTERNE — arche, moucharabieh, bougie — fait environ 250 x 500 px et
elle est au centre du cadre sur la moitie de la video. N'importe qui lit
« Ramadan » sans avoir besoin du croissant, et on est a trois mois et demi
de la fenetre de saison. C'est a Yanis de trancher pour les prochaines.

LES VISAGES. Toutes les fenetres retenues ont ete verifiees sur TOUTE
leur duree, image par image, et non sur une image de planche :
IMG_9459 11,00-14,30 au pas de 0,2 s (plein cadre), IMG_9458 0,10-9,76 au
pas de 0,42 s. La plage propre d'IMG_9458 va de 5,10 a 9,50 s ; elle est
partagee entre les plans 1 et 2 sans recouvrement. Le bras du tiers qui
traverse le cadre a 0,5 s et 4,3 s d'IMG_9458 est hors de ces fenetres.

LE GABARIT NE BOUGE PAS. Neuf plans, une replique par plan, etiquette de
prix, sous-titre karaoke, lapin, signature, plan de boucle. Deux ajouts
par rapport a videos16.py, tous deux pour le timelapse :
  - `speed` par plan (styles2.plan sait deja le faire) ;
  - `inv` par plan, au lieu d'inverser automatiquement le dernier plan.
Le plan 0 est lu A L'ENVERS (la table se dresse) et le plan de boucle est
le MEME extrait lu a l'endroit : sa derniere image est donc exactement la
premiere image du plan 0, et la boucle est sans couture.

PAS DE STABILISATION SUR 9459 NI 9458 : la camera est posee. Stabiliser un
plan deja fixe ne ferait qu'ajouter du recadrage. Les quatre autres plans
sont portes a la main et passent tous par vidstab.

NOTE SUR L'ANCRAGE. Comme tous les rushes Ramadan_, ces fichiers portent
`rotation=-90` : ffprobe annonce 1920x1080 mais ils se decodent en
1080x1920, soit du 9:16 exact. Rien n'est recadre ; seul le zoom (za, zb)
peut sortir quelque chose du cadre.
"""
import os

import graphismes as G
import styles as S
import styles2 as S2
import videos8 as V8
import voix_montage as VM
from videos11 import inverse

W, H, FPS = S.W, S.H, S.FPS
OUT, X_MAX = S.OUT, S.X_MAX
TMP = os.path.join(OUT, "_tmp_dresser")

RAM = "Ramadan_"
MEP = "Mise en place_"

Y_LAPIN_PIED = 1158
Y_ETIQ = 930
Y_SOUS = 1180
TAILLE_LAPIN = 200
LARG_SOUS = 505
TAILLE_SOUS = 40

# IMG_9459 et IMG_9458 sont filmes camera posee : les stabiliser n'aurait
# rien a corriger et couterait du recadrage. Les trois autres sont des
# travellings tenus a la main.
A_STABILISER = {"IMG_9422", "IMG_9414", "IMG_9398",
                "IMG_6945"} | V8.STABILISER

# (stem, dossier, t0, t1, za, zb, speed, inv, texte_dit, etiquette, prix,
#  pose, cote)
# Duree de chaque plan >= duree de sa replique. Repliques mesurees :
# 2,40 / 1,68 / 3,36 / 2,16 / 3,60 / 3,04 / 2,40 / 1,92 / 2,56 s.
PLANS = [
    # 3,00 s (3,3 s de source a x1,1), LUE A L'ENVERS. Plan large, camera
    # posee, table entiere et ses chaises Napoleon : c'est la prise que
    # PRISES_A_TOURNER.md reclamait depuis le 29/10. Fenetre 11,00-14,30
    # verifiee PLEIN CADRE toutes les 0,2 s : Yanis y est seul.
    # L'etiquette porte un prix des la premiere seconde (JOURNEE.md).
    ("IMG_9459", RAM, 11.00, 14.30, 1.00, 1.02, 1.1, True,
     "Une table pour huit, montée chez vous.",
     "TABLE 70x180", "10 €", "16_lunettes_bras_croises", "g"),
    # 2,00 s. Second angle fixe : Yanis porte une chaise Napoleon. C'est
    # l'image qui justifie « vous, vous ne portez rien ».
    ("IMG_9458", RAM, 5.15, 7.15, 1.00, 1.04, 1.0, False,
     "Vous, vous ne portez rien.",
     None, None, "02_pouce_leve", "g"),
    # 2,20 s. Suite immediate : Yanis pose le couvert, toujours seul dans
    # le cadre. La fenetre propre d'IMG_9458 va de 5,10 a 9,50 s et elle
    # est partagee entre ce plan et le precedent, sans recouvrement.
    ("IMG_9458", RAM, 7.20, 9.40, 1.00, 1.04, 1.0, False,
     "C'est moi qui monte et qui dresse.",
     None, None, "15_tshirt_pointe_ordre", "g"),
    # 2,40 s. Le TISSU comme sujet : nappe blanche et couverts dores,
    # aucune lanterne dans le cadre.
    ("IMG_9422", RAM, 0.30, 2.70, 1.00, 1.05, 1.0, False,
     "La nappe blanche, neuf euros.",
     "NAPPE", "9 €", "17_lunettes_pointe", "g"),
    # 3,80 s. Le couvert complet : deux assiettes, verre en cristal,
    # couverts dores — exactement ce que contient le kit a 2 EUR. Seconde
    # fenetre d'IMG_9422, non voisine de la premiere.
    ("IMG_9422", RAM, 4.30, 8.10, 1.00, 1.05, 1.0, False,
     "Assiette, verre, couverts : deux euros la personne.",
     "KIT VAISSELLE", "2 €", "13_chemise_bras_croises", "g"),
    # 3,50 s. Les chaises Napoleon alignees derriere les assiettes : le
    # plan qui montre combien de monde tient autour. Pas de prix sur
    # l'etiquette — le tarif de la chaise n'est pas affiche aujourd'hui.
    ("IMG_9414", RAM, 5.40, 8.90, 1.00, 1.05, 1.0, False,
     "Huit à dix personnes autour, sans serrer.",
     "8 À 10 PERS.", None, "03_montre_la_main", "g"),
    # 3,40 s. Le camion ouvert et les chaises deposees sur l'herbe : une
    # livraison reelle. Seul plan qui ne soit pas la table, et la replique
    # est la seule qui parle de livraison. Rush de `Mise en place_`,
    # jamais publie.
    ("IMG_6945", MEP, 0.40, 3.80, 1.00, 1.05, 1.0, False,
     "Livraison en Île-de-France, ou retrait au box.",
     None, None, "12_chemise_debout", "d"),
    # 2,40 s. Gros plan du verre en cristal : la derniere image avant
    # l'appel est le produit, pas un camion. Fenetre de debut, la seule
    # d'IMG_9398 ou la lanterne n'est pas dans le cadre.
    ("IMG_9398", RAM, 0.20, 2.60, 1.00, 1.05, 1.0, False,
     "C'est pour quelle date ? Écrivez-moi.",
     None, None, "14_chemise_telephone", "d"),
    # Boucle : meme extrait que le plan 0, mais lu A L'ENDROIT. Sa
    # derniere image est donc la premiere image de la video.
    ("IMG_9459", RAM, 11.00, 14.30, 1.00, 1.02, 1.1, False,
     "Abonnez-vous. Allez, on recommence.",
     None, None, "00_salut_pouce_leve_gauche", "g"),
]


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def monte(nom="DRESSER_31"):
    d = _dir("plans")
    parts, durees = [], []
    for i, p in enumerate(PLANS):
        (stem, dos, t0, t1, za, zb, speed, inv, dit, etiq, prix,
         pose, cote) = p
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = S2.plan(brut, stem, dos, t0, t1, za, zb, speed=speed)
        if stem in A_STABILISER:
            brut = V8.stabilise(brut, os.path.join(d, f"{i:02d}_stab.mp4"))
        if inv:
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
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"dr{i}", dur - 0.05,
                                              prix=prix, taille=46)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(Y_ETIQ), "t0": 0.03, "t1": dur - 0.04,
                        "fade": 0.05})

        mots = max(len(dit.split()), 1)
        seq, lw, lh = G.karaoke_seq(dit, f"dr{i}", dur - 0.03,
                                    mots_par_sec=mots / max(dur - 0.45, 0.6),
                                    taille=TAILLE_SOUS, largeur_max=LARG_SOUS)
        cp, cw, ch = V8.carte_texte(lw, lh, f"carte_dr{i}.png")
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
    """Pose la bande voix sur le montage, calee sur les plans reels."""
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
                         f"rallonge un plan du MILIEU, jamais celui de boucle")
    lit = ambiance.lit_sonore(t)
    return VM.melange(video, repliques, sortie, lit=lit)


if __name__ == "__main__":
    import sys
    v, durees = monte()
    print(v, flush=True)
    if "--muet" not in sys.argv:
        s = sonorise(v, durees,
                     os.path.join(os.path.dirname(OUT), "voix", "dresser",
                                  "JONATHAN"),
                     v.replace(".mp4", "_son.mp4"))
        print(s, flush=True)
