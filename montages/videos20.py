"""« Livree ou a recuperer au box ? » — Reel du 4 novembre.

Idee 1 de la proposition DA du 04/11, validee par Yanis. Question de client,
sans total. Prix confirmes : chaise 3 €, table ronde 10 €, kit vaisselle 2 €.
Ni chiffre de stock, ni « livraison comprise » (« selon votre zone »).

ECARTS PAR RAPPORT A LA PROPOSITION (fenetres balayees toutes les 0,4-0,5 s
dans le cadre 9:16 final, rotation -90 deja appliquee, HDR converti) :
  - IMG_1743 0,0-4,3 (au lieu de 0,0-3,6) : la porte est levee et le box
    visible des 2,5 s ; la fenetre est allongee car la replique de boucle
    dure 4,08 s. Le repli IMG_1692 n'a PAS ete necessaire.
  - IMG_1692 : nette seulement a partir de 0,7 s (score de nettete 234 a
    0,5 s contre 1100 a 1,4 s). Fenetre 0,7-1,59 jouee aller / retour /
    aller (2,67 s) : un simple va-et-vient (1,8 s) etait plus court que la
    replique (2,32 s).
  - IMG_1005 2,5-5,5 REFUSE : 2,5-3,5 est un panoramique sur un mur vide.
    Remplace par IMG_1006 4,4-6,9 (Yanis porte la pile vers la maison, de
    dos) pour « Ou je vous la livre », et IMG_1005 4,7-6,7 (Yanis, pile sur
    le dos, de face) pour « Et je monte tout sur place ». IMG_1005 0-1,5
    ecarte aussi : un tiers en noir porte des chaises vers la maison.
  - IMG_4045 0-2,4 (cuisine du client) REFUSE : flou jusqu'a 1 s, bouteille,
    encombrement, et « MELA » (sac d'un tiers) lisible a 7,6 s.
    Kit vaisselle sur IMG_4046 1,4-3,8 (couverts dores, verres, assiettes,
    nette). IMG_4045 7,95-10,1 sert pour l'appel final (tables dressees).
  - Aucun croissant de lune sur les lanternes de 4054, 4045, 4046 : toutes
    portent un dome a pointe, pas de croissant.
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
TMP = os.path.join(OUT, "_tmp_livree")

VLOG = "Contenue Vlog_"
MAR = "Mariages"

Y_LAPIN_PIED = 1158
Y_ETIQ = 930
Y_SOUS = 1180
TAILLE_LAPIN = 200
LARG_SOUS = 505
TAILLE_SOUS = 40

A_STABILISER = {2, 3}      # index des plans portes a la main (Vlog)

# (stem, dossier, t0, t1, za, zb, texte_dit, etiquette, prix, pose, cote)
PLANS = [
    # 4,3 s : la porte du box se leve. Prix dit et ecrit (sous-titre) des 0 s.
    ("IMG_1743", VLOG, 0.10, 4.37, 1.02, 1.07,
     "Livrée ou au box ? La chaise Napoléon, trois euros.",
     "CHAISE", "3 €", "16_lunettes_bras_croises", "g"),
    ("IMG_1692", VLOG, 0.70, 1.59, 1.00, 1.06,
     "Vous la prenez au box, dans le Val-d'Oise.",
     "CHAISE", "3 €", "17_lunettes_pointe", "g"),
    ("IMG_1006", VLOG, 4.40, 6.90, 1.00, 1.04,
     "Ou je vous la livre, selon votre zone.",
     None, None, "12_chemise_debout", "d"),
    ("IMG_1005", VLOG, 4.70, 6.70, 1.00, 1.04,
     "Et je monte tout sur place.",
     None, None, "13_chemise_bras_croises", "d"),
    ("IMG_4054", MAR, 2.05, 4.05, 1.00, 1.04,
     "Table ronde, dix euros.",
     "TABLE RONDE", "10 €", "03_montre_la_main", "g"),
    ("IMG_4054", MAR, 0.00, 1.20, 1.00, 1.03,
     "Le couvert complet : deux euros.",
     "KIT VAISSELLE", "2 €", "02_pouce_leve", "g"),
    ("IMG_4046", MAR, 8.05, 8.72, 1.00, 1.04,
     "C'est pour quelle date ? Écrivez-moi.",
     None, None, "14_chemise_telephone", "d"),
    # Boucle : meme extrait et memes zooms que le plan 0, lu a l'envers.
    ("IMG_1743", VLOG, 0.10, 4.37, 1.02, 1.07,
     "Et abonnez-vous, c'est gratuit. Allez. On recommence.",
     None, None, "00_salut_pouce_leve_gauche", "g"),
]
CTA = 6
TROIS_PASSES = {1, 6}
DEUX_PASSES = {5}       # aller / retour : 1,2 s nettes -> 2,4 s
ETIQ_T0 = {0: 1.3}      # etiquette « CHAISE 3 € » des 1,3 s sur le plan 0      # aller / retour / aller : 0,89 s nettes -> 2,67 s
BOUCLE = len(PLANS) - 1


def accentue(entree, sortie, force=1.0):
    """Renforce legerement la nettete (luminance seule) : les plans de porte
    blanche unie et de nappe blanche tombent sous le seuil du controle sans
    etre flous. Meme traitement sur le plan 0 et la boucle."""
    import subprocess
    subprocess.run([
        S.FF, "-y", "-v", "error", "-i", entree,
        "-vf", f"unsharp=5:5:{force}:5:5:0.0", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", sortie], check=True)
    return sortie


ACCENTUER = {0: 0.6, 4: 1.8, 5: 1.8, 6: 1.6, 7: 1.4}


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def monte(nom="LIVREE_BOX"):
    d = _dir("plans")
    parts, durees = [], []
    for i, p in enumerate(PLANS):
        (stem, dos, t0, t1, za, zb, dit, etiq, prix, pose, cote) = p
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = S2.plan(brut, stem, dos, t0, t1, za, zb, speed=1.0)
        if i in ACCENTUER:
            brut = accentue(brut, os.path.join(d, f"{i:02d}_net.mp4"),
                            ACCENTUER[i])
        if i in A_STABILISER:
            brut = V8.stabilise(brut, os.path.join(d, f"{i:02d}_stab.mp4"))
        if i in DEUX_PASSES:
            inv = inverse(brut, os.path.join(d, f"{i:02d}_ar.mp4"))
            brut = S.concat([brut, inv], os.path.join(d, f"{i:02d}_aller.mp4"))
            dur *= 2
        if i in TROIS_PASSES:
            inv = inverse(brut, os.path.join(d, f"{i:02d}_ar.mp4"))
            brut = S.concat([brut, inv, brut],
                            os.path.join(d, f"{i:02d}_aller.mp4"))
            dur *= 3
        if i == BOUCLE:
            brut = inverse(brut, os.path.join(d, f"{i:02d}_inv.mp4"))
        durees.append(dur)
        cal = []

        if pose:
            chemin = S.sticker(pose)
            hh = V8.haut_sticker(chemin, TAILLE_LAPIN)
            gauche = cote == "g" or etiq
            x_fin = 20 if gauche else X_MAX - TAILLE_LAPIN
            cote = "g" if gauche else "d"
            cal.append({"png": chemin, "w": TAILLE_LAPIN,
                        "x": V8.entre_cote(x_fin, cote, 0.08),
                        "y": str(Y_LAPIN_PIED - hh),
                        "t0": 0.08, "t1": dur - 0.04, "fade": 0.10})

        if etiq:
            te = ETIQ_T0.get(i, 0.03)
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"vg{i}", dur - te - 0.05,
                                              prix=prix, taille=46)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(Y_ETIQ), "t0": te, "t1": dur - 0.04,
                        "fade": 0.05})

        if i == CTA:
            cp, cw, ch = G.bloc_cta("C'EST POUR QUELLE DATE ?",
                                    "@eventys.paris", nom="cta_livree.png",
                                    taille=40)
            cal.append({"png": cp, "w": None,
                        "x": str(max(min(int((W - cw) / 2), X_MAX - cw), 18)),
                        "y": str(Y_SOUS), "t0": 0.10, "t1": dur - 0.04,
                        "fade": 0.10})
            print(f"  bandeau CTA : {cw}x{ch}", flush=True)
        else:
            mots = max(len(dit.split()), 1)
            seq, lw, lh = G.karaoke_seq(dit, f"vg{i}", dur - 0.03,
                                        mots_par_sec=mots / max(dur - 0.45, 0.6),
                                        taille=TAILLE_SOUS,
                                        largeur_max=LARG_SOUS)
            cp, cw, ch = V8.carte_texte(lw, lh, f"carte_vg{i}.png")
            fin_sous = dur - (0.25 if i == BOUCLE else 0.0)
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
    import ambiance
    debuts, t = [], 0.0
    for dd in durees:
        debuts.append(t)
        t += dd
    repliques, libre = [], 0.0
    for i, deb in enumerate(debuts):
        f = os.path.join(dossier_voix, f"{i:02d}.mp3")
        dv = VM.duree(f)
        debut = max(deb, libre)
        repliques.append((f, debut, dv))
        libre = debut + dv + VM.PAUSE
        if debut > deb + 0.01:
            print(f"  replique {i} decalee de {debut - deb:+.2f}s", flush=True)
    fin = repliques[-1][1] + repliques[-1][2]
    print(f"  voix : {fin:.2f}s pour une image de {t:.2f}s", flush=True)
    if fin > t:
        raise SystemExit(f"la voix depasse l'image de {fin - t:.2f}s")
    lit = ambiance.lit_sonore(t)
    return VM.melange(video, repliques, sortie, lit=lit)


if __name__ == "__main__":
    import sys
    v, durees = monte()
    print(v, flush=True)
    if "--muet" not in sys.argv:
        s = sonorise(v, durees,
                     os.path.join(OUT, "_attente_2026-11-04", "voix",
                                  "JONATHAN"),
                     v.replace(".mp4", "_son.mp4"))
        print(s, flush=True)
        # Bruitages (valides par Yanis le 2026-11-04) : pop sur chaque
        # etiquette, whoosh a chaque coupe, ding sur le total, rien sur la
        # boucle. Voir sfx.evenements_standard.
        import sfx
        etiq_sfx = [p[7] is not None and i not in ETIQ_T0
                    for i, p in enumerate(PLANS)]
        ev = sfx.evenements_standard(
            durees, etiq_sfx,
            total=None, cta=CTA, boucle=BOUCLE, ouverture_box=False,
            extras={0: [("pop_etiquette", ETIQ_T0[0] + 0.04, -10),
                        ("rideau_box", 1.85, -16)],
                    2: [("camion_porte", 0.10, -15)]})
        ev = sorted(ev, key=lambda e: e[1])
        print(sfx.ajoute(s, ev, s.replace("_son.mp4", "_sfx.mp4")),
              flush=True)
        print("  bruitages :", len(ev), "sons sur", round(sum(durees), 1),
              "s", flush=True)
