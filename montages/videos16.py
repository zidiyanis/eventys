"""« La table dressée à 59 € » — Reel du 29 octobre.

LA DEMANDE. Yanis, le 29/10 : « nan laisse tomber, il faut des tables
dressées, c'est important. Pour l'instant fais le même type de montage mais
avec des rushes différents et des phrases différentes. » C'est la reponse
a la question que le relecteur m'avait fait poser sur « Juste des chaises »,
qui ne montrait aucune table finie. Ce montage remplace CHAISES_60, qui
n'a jamais ete publie.

LE GABARIT NE BOUGE PAS. Neuf plans, une replique par plan, etiquette de
prix, sous-titre karaoke, lapin, signature, plan de boucle inverse a la
fin : exactement videos15.py. Ce qui change, c'est le scenario, les
repliques et les rushes — les trois choses demandees.

LE SCENARIO. Retour au CALCUL, le format qui fait 11x les vues et 57x les
enregistrements du format coulisses (analyse/ENSEIGNEMENTS.md), mais pose
cette fois sur une table FINIE du premier plan au dernier. Le detail du
calcul et sa verification contre le catalogue sont dans voix/table.py.

LES RUSHES : UNE TABLE QU'ON N'AVAIT JAMAIS MONTEE. Huit des neuf plans
viennent de `Ramadan_`, un dossier note 5/5 au catalogue et dont PAS UN
clip n'est entre dans un montage jusqu'ici. Ce sont les seules tables
dressees de la reserve en 1080x1920 natif : `ffprobe` annonce 1920x1080
mais les fichiers portent `rotation=-90`, donc ils se decodent en vertical
exact et rien n'est recadre (voir la note d'ancrage plus bas).

POURQUOI CETTE TABLE-LA ET PAS L'AUTRE. Le dossier contient deux tables.
La premiere — nappe blanche, chemin DORE, lanternes a croissant de lune —
est magnifique et clairement marquee Ramadan : hors saison le 29 octobre,
et elle reduit le public. La seconde — table RONDE, nappe blanche, chemin
VERT SAUGE, couverts dores, verres en cristal, chaises Napoleon — est
neutre et sert n'importe quelle occasion. C'est elle, et elle seule : un
calcul qui annonce « cette table » doit montrer la meme table a chaque
plan.

LE CROISSANT DE LUNE. Un bougeoir dore en forme de minaret, surmonte d'un
petit croissant, est pose sur cette table-la aussi. Il entre dans le cadre
par le HAUT sur une partie des rushes. Les fenetres ci-dessous ont ete
choisies pour qu'il n'y soit pas — c'est le critere qui a elimine le plus
de candidats, avant meme la nettete.

ET IL FAUT LE VERIFIER SUR TOUTE LA FENETRE, PAS SUR UNE IMAGE. Au premier
rendu, le plan des kits vaisselle etait propre a son milieu et montrait le
croissant en grand pendant ses 1,5 dernieres secondes. Une planche de
triage prend UNE image par rush : elle sert a ecarter, jamais a valider.

UN PLAN QUI N'EST PAS LA TABLE. Le plan 6 (« livree en Ile-de-France »)
montre le dechargement du camion, pas la table : la regle de JOURNEE.md
est de ne jamais vendre ce qu'on ne montre pas. IMG_1697 est le seul rush
neuf et net qui montre une livraison reelle.

CE QUI MANQUE, ET QUI SE VOIT. Il n'existe dans toute la reserve AUCUN
plan large de cette table entiere avec ses huit chaises : tous les rushes
sont des travellings a hauteur de table. Le plan d'ouverture est donc le
moins serre qu'on ait, pas celui qu'on voudrait. Une prise fixe, debout,
de la table entiere est a ajouter a PRISES_A_TOURNER.md.

NOTE SUR L'ANCRAGE. `ancre` et `ancre_x` ne servent a rien sur les rushes
Ramadan : une source qui se decode deja en 9:16 exact n'est jamais
recadree. Seul le zoom (za, zb) peut sortir quelque chose du cadre ici.
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
TMP = os.path.join(OUT, "_tmp_table")

RAM = "Ramadan_"
VLOG = "Contenue Vlog_"

Y_LAPIN_PIED = 1158
Y_ETIQ = 930
Y_SOUS = 1180
TAILLE_LAPIN = 200
LARG_SOUS = 505
TAILLE_SOUS = 40

# Tous les rushes Ramadan sont des travellings tenus a la main autour de la
# table : aucun ne peut sauter la stabilisation.
A_STABILISER = {"IMG_9432", "IMG_9454", "IMG_9430", "IMG_9449",
                "IMG_9433", "IMG_9448", "IMG_1697"} | V8.STABILISER

# (stem, dossier, t0, t1, za, zb, texte_dit, etiquette, prix, pose, cote)
# Duree de chaque plan >= duree de sa replique. Repliques mesurees :
# 2,64 / 2,72 / 2,00 / 2,64 / 3,20 / 2,72 / 2,88 / 1,92 / 2,72 s.
PLANS = [
    # 3,00 s. Le plan le moins serre de la serie : la table dressee et les
    # chaises Napoleon derriere. Nettete 765-788 sur cette fenetre, contre
    # 496 au milieu du rush ; et pas de croissant, qui entre dans le cadre
    # avant 6 s.
    ("IMG_9432", RAM, 6.20, 9.20, 1.00, 1.05,
     "Cette table dressée, elle coûte combien ?",
     "TABLE DRESSÉE", "8 PERS.", "16_lunettes_bras_croises", "g"),
    # 2,90 s. Le BORD ROND du plateau sous la nappe, avec un pied de chaise
    # Napoleon. C'est le seul plan de la reserve ou l'on voit que la table
    # est ronde : partout ailleurs la camera est trop pres. IMG_9452, qui
    # la montrait mieux encore, porte le croissant pendant ses 1,7
    # premieres secondes et a ete ecarte pour cette seule raison.
    ("IMG_9430", RAM, 3.00, 5.90, 1.00, 1.06,
     "La table ronde, pour huit. Dix euros.",
     "TABLE RONDE Ø120", "10 €", "02_pouce_leve", "g"),
    # 2,60 s. Le TISSU comme sujet : la nappe blanche occupe la moitie du
    # cadre. Fenetre tardive du rush le plus calme du dossier (tremblement
    # 25-31 contre 36 ailleurs), et sans croissant.
    ("IMG_9454", RAM, 4.40, 7.00, 1.00, 1.05,
     "La nappe blanche, neuf euros.",
     "NAPPE", "9 €", "17_lunettes_pointe", "g"),
    # 2,90 s. Les dossiers des chaises Napoleon, de l'autre cote de la
    # table. Ils ne sont dans le cadre que pendant les deux premieres
    # secondes du rush — la camera descend ensuite sur l'assiette — d'ou
    # cette fenetre de debut, et non la plus nette (0,1-3,0 : 291-454,
    # contre 509 vers 6 s, mais a 6 s le croissant est entre dans le cadre
    # et les chaises en sont sorties).
    ("IMG_9449", RAM, 0.10, 3.00, 1.00, 1.05,
     "Huit chaises Napoléon. Vingt-quatre euros.",
     "8 CHAISES", "24 €", "03_montre_la_main", "g"),
    # 3,40 s. Gros plan du couvert complet : assiette, assiette creuse,
    # serviette, couverts dores, verre en cristal. C'est exactement ce que
    # contient le kit a 2 EUR, donc le plan qui justifie l'etiquette.
    # IMG_9453 occupait cette place au premier rendu : le relecteur y a vu
    # le croissant, en plein cadre et dans le tiers superieur, pendant les
    # 1,5 derniere secondes du plan. Ma note « les fenetres ont ete
    # choisies pour qu'il n'y soit pas » etait donc fausse pour ce
    # plan-la : je l'avais verifiee sur une image, pas sur la fenetre.
    # Deuxieme fenetre d'IMG_9454, non voisine de la premiere (plan 2) :
    # le croissant n'entre dans ce rush qu'a partir de 12 s.
    ("IMG_9454", RAM, 8.40, 11.80, 1.00, 1.05,
     "Assiettes, verres, couverts. Seize euros.",
     "8 KITS VAISSELLE", "16 €", "13_chemise_bras_croises", "g"),
    # 2,90 s. Le centre de table, bougie allumee : le plan d'ambiance qui
    # porte le total. La fenetre 1,80-4,90 a servi au premier rendu et a
    # ete refusee : la fenetre de la piece y est CRAMEE en haut de cadre
    # (plus de 2 % de l'image au-dessus de luma 250, pendant 1,8 s, contre
    # 0,02 a 1,07 % partout ailleurs). Plus loin dans le rush la camera
    # s'est tournee vers l'interieur et il n'y a plus de fenetre du tout.
    ("IMG_9433", RAM, 9.60, 12.50, 1.00, 1.06,
     "Cinquante-neuf euros. La table complète.",
     "LA TABLE COMPLÈTE", "59 €", "06_bras_leves_content", "g"),
    # 3,20 s. Le dechargement des piles de chaises a l'arriere du camion.
    # Seul plan du montage qui ne soit pas la table, et seul rush neuf et
    # net (1472-1655) qui montre une livraison reelle.
    ("IMG_1697", VLOG, 2.00, 5.20, 1.00, 1.06,
     "Livrée en Île-de-France, ou à récupérer au box.",
     None, None, "12_chemise_debout", "d"),
    # 2,40 s. Retour sur le couvert, juste avant le message final : la
    # derniere image avant l'appel est le produit, pas un camion.
    ("IMG_9448", RAM, 0.30, 2.70, 1.00, 1.05,
     "C'est pour quelle date ? Écrivez-moi.",
     None, None, "14_chemise_telephone", "d"),
    # Boucle : meme rush et meme fenetre que le plan 0, lu a l'envers, donc
    # la derniere image est l'image d'ouverture.
    ("IMG_9432", RAM, 6.20, 9.20, 1.00, 1.05,
     "Abonnez-vous. Allez, on recommence.",
     None, None, "00_salut_pouce_leve_gauche", "g"),
]


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def monte(nom="TABLE_59"):
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
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"tb{i}", dur - 0.05,
                                              prix=prix, taille=46)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(Y_ETIQ), "t0": 0.03, "t1": dur - 0.04,
                        "fade": 0.05})

        mots = max(len(dit.split()), 1)
        seq, lw, lh = G.karaoke_seq(dit, f"tb{i}", dur - 0.03,
                                    mots_par_sec=mots / max(dur - 0.45, 0.6),
                                    taille=TAILLE_SOUS, largeur_max=LARG_SOUS)
        cp, cw, ch = V8.carte_texte(lw, lh, f"carte_tb{i}.png")
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
                     os.path.join(os.path.dirname(OUT), "voix", "table",
                                  "JONATHAN"),
                     v.replace(".mp4", "_son.mp4"))
        print(s, flush=True)
