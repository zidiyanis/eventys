"""« Un anniversaire pour vingt » — Reel du 27 octobre.

Demande de Yanis : « fais le meme delire mais avec d'autres rushes, c'est ce
type de montage qui fonctionne, change les rushes pour du renouveau. »

SEPT PLANS SUR NEUF VIENNENT DU DOSSIER « Anniversaire_ », jamais touche.
L'inventaire du 27/10 a montre que trois dossiers entiers dormaient —
Noël (11 clips), Ramadan_ (48) et Anniversaire_ (4) — pendant que les trois
premieres videos puisaient dans les quatre memes rushes de Mariages.

Une version Noël avait ete montee d'abord. Yanis l'a reportee a mi-novembre
(sa regle de saison), elle est gardee telle quelle dans videos13.py.
Anniversaire n'a pas de saison, d'ou ce choix.

CE QUE CE DOSSIER EST VRAIMENT, et qu'il a fallu monter pour le voir : un
tournage de BUFFET, pas de mobilier. Sur ses quatre clips, trois ne filment
que des plats, et IMG_2797 laisse voir deux bouteilles de marque. Un seul,
IMG_2796, montre la salle : chaises, tables, arche. Il fournit donc trois
plans sur neuf, separes a chaque fois par un autre rush. Le reste du
dossier sert aux deux beats ou la vaisselle et la table dressee sont
reellement le sujet. Une version a dix plans, montee d'abord, affichait des
cartes de prix de mobilier sur des assiettes de petits fours : elle a ete
jetee.

CE QUE CE REEL MONTRE POUR LA PREMIERE FOIS : l'ARCHE DOREE a 40 EUR. Elle
est au catalogue depuis le debut et n'avait jamais ete filmee en video,
faute d'avoir ouvert ce dossier.

LE CALCUL, verifiable contre le catalogue de CLAUDE.md :
    20 chaises Napoleon  x  3 EUR =  60
    20 kits vaisselle    x  2 EUR =  40
     2 tables rectang.   x 10 EUR =  20
     1 arche doree                =  40
    ---------------------------------
    TOTAL mobilier                 160 EUR
La NAPPE a ete retiree du calcul : aucune image du dossier ne la montre
comme sujet. La seule retenue d'abord (IMG_2787) etait un plan de coupelles
de bonbons pose sur une nappe — annoncer « deux nappes, neuf euros » la
dessus, c'est faire payer un prix pour ce que le spectateur ne voit pas.
Elle reviendra quand il y aura une prise ou elle est le sujet.
Prix de la chaise a 3 EUR : confirme par Yanis le 27/10, le tarif hiver a
2 EUR ne couvre pas les fetes.

CE QUI N'EST PAS A NOUS. Ces rushes montrent un buffet, des ballons, des
lettres lumineuses et un gateau. Eventys ne fait ni traiteur ni decoration.
Deux repliques le disent a l'image (« Vous l'habillez » sur l'arche, « Le
gateau et les ballons, c'est vous »), pour qu'aucun client ne croie que les
178 EUR comprennent ce qu'il voit.

CHOIX DES FENETRES — methode corrigee le 27/10. Les fenetres ne sont plus
choisies sur l'image source en paysage mais sur le CADRE FINAL 9:16, via
montages/reperage9x16.py, et a trois hauteurs d'ancrage. Trois fois de
suite, un plan avait ete retenu sur une vignette paysage puis s'etait
revele, une fois recadre, ne plus montrer le produit annonce par sa carte :
le plan « 12 kits vaisselle » filmait un sapin. La cause etait toujours la
meme — nos rushes sont filmes en paysage, la table est dans la moitie
BASSE, et un 9:16 centre garde le haut de la piece. D'ou le parametre
`ancre` ajoute a styles.plan / styles2.plan, et utilise ci-dessous.

L'OUVERTURE SUR LE BOX EST CONSERVEE (plans 0 et 9) : JOURNEE.md en fait la
seule exception a la variation des rushes, parce que c'est la signature de
la marque et que la boucle doit y revenir.
"""
import os

import graphismes as G
import styles as S
import styles2 as S2
import videos8 as V8
from videos11 import inverse

W, H, FPS = S.W, S.H, S.FPS
OUT, X_MAX = S.OUT, S.X_MAX
TMP = os.path.join(OUT, "_tmp_anniv")

ANNIV = "Anniversaire_"
VLOG = "Contenue Vlog_"

Y_LAPIN_PIED = 1158
Y_ETIQ = 930
Y_SOUS = 1180
TAILLE_LAPIN = 200
LARG_SOUS = 505
TAILLE_SOUS = 40

A_STABILISER = {"IMG_2785", "IMG_2787", "IMG_2796"} | V8.STABILISER

# (stem, dossier, t0, t1, za, zb, ancre, texte_dit, etiquette, prix, pose, cote)
# Duree de chaque plan >= duree de sa replique. Repliques mesurees :
# 3,28 / 2,80 / 2,64 / 2,96 / 1,92 / 2,88 / 4,32 / 2,64 / 1,92 / 3,12 s.
PLANS = [
    # Signature de marque, et ancre de la boucle.
    ("IMG_1044", VLOG, 0.50, 3.90, 1.03, 1.09, 0.50,
     "Vingt personnes pour un anniversaire. On compte.",
     "20 PERSONNES", "160 €", "16_lunettes_bras_croises", "g"),
    # Ancre 0,65 : les chaises Napoleon sont dans la moitie basse du cadre
    # paysage. Une premiere version a 0,40 gardait le mur et le televiseur.
    ("IMG_2796", ANNIV, 10.60, 13.50, 1.00, 1.06, 0.65,
     "Vingt chaises Napoléon. Trois euros la chaise.",
     "20 CHAISES", "60 €", "17_lunettes_pointe", "g"),
    # Verres en cristal sur nappe blanche : c'est le kit vaisselle.
    ("IMG_2785", ANNIV, 0.40, 3.20, 1.00, 1.05, 0.50,
     "Vingt kits vaisselle. Deux euros le kit.",
     "20 KITS", "40 €", "02_pouce_leve", "g"),
    # Ancre 0,85 : la table en enfilade est tout en bas du cadre source.
    ("IMG_2796", ANNIV, 4.50, 7.60, 1.00, 1.06, 0.85,
     "Deux tables rectangulaires. Dix euros pièce.",
     "2 TABLES", "20 €", "03_montre_la_main", "g"),
    # La blague est placee ICI, entre deux plans d'IMG_2796, pour les
    # separer : ce rush est le seul du dossier qui montre du mobilier, et
    # il doit fournir trois plans sur neuf sans jamais en toucher deux a
    # la suite.
    ("IMG_2787", ANNIV, 10.00, 12.80, 1.00, 1.06, 0.50,
     "Le gâteau et les ballons, c'est vous.",
     None, None, "06_bras_leves_content", "d"),
    # PREMIERE APPARITION DE L'ARCHE EN VIDEO. La replique precise « vous
    # l'habillez » : a l'image elle porte des ballons, qui ne sont pas loues.
    ("IMG_2796", ANNIV, 15.20, 18.20, 1.00, 1.06, 0.50,
     "L'arche dorée, quarante euros. Vous l'habillez.",
     "ARCHE DORÉE", "40 €", "15_tshirt_pointe_ordre", "g"),
    # Fin d'IMG_2785 : fleurs, bougies et nappe blanche. C'est la seule
    # image large du dossier qui ne soit pas un plat. Le debut du rush
    # IMG_2797, d'abord retenu ici, laisse voir deux bouteilles de marque.
    ("IMG_2785", ANNIV, 24.00, 27.60, 1.00, 1.05, 0.50,
     "Cent soixante euros. Livraison en plus, selon la zone.",
     "TOTAL MOBILIER", "160 €", "13_chemise_bras_croises", "g"),
    ("IMG_2796", ANNIV, 0.40, 2.90, 1.00, 1.05, 0.60,
     "C'est pour quelle date ? Écrivez-moi.",
     None, None, "14_chemise_telephone", "d"),
    # Boucle : meme rush et meme cadrage que le plan 0, lu a l'envers.
    # L'abonnement est demande ici, comme dans le Reel du 20 octobre —
    # arbitrage de Yanis le 27/10 : les deux appels, pas un seul.
    # 3,60 s pour une replique de 3,12 s : les repliques derivent en aval
    # parce que plusieurs durent presque la duree de leur plan, pause de
    # 0,18 s comprise. Allonger ce plan par son debut de rush est sans
    # risque pour la boucle : lu a l'envers, il finit de toute facon sur
    # l'image a 0,50 s, celle sur laquelle s'ouvre le plan 0.
    ("IMG_1044", VLOG, 0.50, 4.10, 1.03, 1.09, 0.50,
     "Et abonnez-vous. Allez, on recommence.",
     None, None, "00_salut_pouce_leve_gauche", "g"),
]


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def monte(nom="ANNIV_20"):
    d = _dir("plans")
    parts = []
    for i, p in enumerate(PLANS):
        (stem, dos, t0, t1, za, zb, ancre, dit, etiq, prix, pose, cote) = p
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = S2.plan(brut, stem, dos, t0, t1, za, zb, speed=1.0, ancre=ancre)
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
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"an{i}", dur - 0.05,
                                              prix=prix, taille=46)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(Y_ETIQ), "t0": 0.03, "t1": dur - 0.04,
                        "fade": 0.05})

        mots = max(len(dit.split()), 1)
        seq, lw, lh = G.karaoke_seq(dit, f"an{i}", dur - 0.03,
                                    mots_par_sec=mots / max(dur - 0.45, 0.6),
                                    taille=TAILLE_SOUS, largeur_max=LARG_SOUS)
        cp, cw, ch = V8.carte_texte(lw, lh, f"carte_an{i}.png")
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
