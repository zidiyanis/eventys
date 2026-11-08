"""« 20 personnes a table ? 120 € » — Reel du 2 novembre.

Idee 1 de la proposition DA du 02/11, validee par Yanis. Format calcul (celui
qui a fait 17 162 vues le 26/10), gabarit lapin, une replique par plan.

Calcul, avec les seuls prix confirmes par Yanis : 20 chaises x 3 € = 60 € ;
2 tables x 10 € = 20 € ; 20 kits vaisselle x 2 € = 40 € ; total 120 €.
Nappes en plus. Ni chiffre de stock, ni « livraison comprise ».

ECARTS PAR RAPPORT A LA PROPOSITION (releves en balayant les fenetres sur
toute leur duree, pas sur les vignettes de triage) :
  - IMG_1013 REFUSE : une television allumee avec des sous-titres roses
    incrustes, un homme au visage lisible en haut du cadre, et un tiers de
    dos au premier plan. IMG_1727 refuse pour les memes raisons (television
    sous-titree, sac en tissu a texte).
    Remplace par IMG_1012 (Vlog) : Yanis porte DEUX tables pliantes vers une
    maison, chaise Napoleon + peluche au sol. Propre sur 3 s.
  - IMG_9425 16,6-19,4 REFUSE : la proposition le disait « verifie sans
    croissant ». FAUX : les lanternes y portent un croissant de lune
    dore, bien visible sur toute la fenetre, plus un avant-bras. Remplace.
  - IMG_9407 ecarte aussi (croissant au sommet de la lanterne).
  - Ordre modifie : IMG_9420 (vue de dessus de la table, plan le plus
    « dressee ») porte maintenant « Total : cent vingt euros » ; la
    replique « je livre et je monte » passe sur IMG_9425 3,8-6,4 (une main
    pose l'assiette : on dresse) ; l'appel final passe sur le plan large
    d'IMG_9428 (fin du travelling, table complete avec chaises).
  - Fenetre de boucle allongee a 0,5-4,1 s (3,6 s au lieu de 3,4) : la
    replique de cloture dure 3,44 s.
  - Plan 6 : le bandeau bordeaux remplace le sous-titre (il porte deja la
    meme phrase), pour tenir dans la zone sure.
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
TMP = os.path.join(OUT, "_tmp_vingt")

VLOG = "Contenue Vlog_"
RAM = "Ramadan_"

Y_LAPIN_PIED = 1158
Y_ETIQ = 930
Y_SOUS = 1180
TAILLE_LAPIN = 200
LARG_SOUS = 505
TAILLE_SOUS = 40

A_STABILISER = {"IMG_9428", "IMG_9429"}

# (stem, dossier, t0, t1, za, zb, texte_dit, etiquette, prix, pose, cote)
PLANS = [
    # 3,6 s : box qui s'ouvre. Prix des la premiere seconde.
    ("IMG_1044", VLOG, 0.50, 4.10, 1.03, 1.09,
     "Vingt personnes à table ? Cent vingt euros de mobilier.",
     "20 PERSONNES", "120 €", "16_lunettes_bras_croises", "g"),
    ("IMG_1745", VLOG, 0.00, 2.50, 1.00, 1.05,
     "Vingt chaises Napoléon : soixante euros.",
     "20 CHAISES", "60 €", "17_lunettes_pointe", "g"),
    ("IMG_1012", VLOG, 0.00, 3.00, 1.00, 1.05,
     "Deux tables de dix : vingt euros.",
     "2 TABLES", "20 €", "03_montre_la_main", "g"),
    ("IMG_9428", RAM, 2.60, 5.20, 1.00, 1.04,
     "Vingt couverts complets : quarante euros.",
     "20 KITS", "40 €", "02_pouce_leve", "g"),
    ("IMG_1003", VLOG, 0.60, 2.80, 1.00, 1.04,
     "Total : cent vingt euros.",
     "TOTAL", "120 €", "13_chemise_bras_croises", "g"),
    ("IMG_1714", VLOG, 0.00, 2.50, 1.00, 1.05,
     "Je livre et je monte, selon votre zone.",
     None, None, "12_chemise_debout", "d"),
    ("IMG_9429", RAM, 4.10, 5.20, 1.00, 1.03,
     "C'est pour quelle date ? Écrivez-moi.",
     None, None, "14_chemise_telephone", "d"),
    # Boucle : meme extrait et memes zooms que le plan 0, lu a l'envers.
    ("IMG_1044", VLOG, 0.50, 4.10, 1.03, 1.09,
     "Et abonnez-vous. Allez. On recommence.",
     None, None, "00_salut_pouce_leve_gauche", "g"),
]
CTA = 6
ALLER_RETOUR = {6}
BOUCLE = len(PLANS) - 1


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def monte(nom="VINGT_120"):
    d = _dir("plans")
    parts, durees = [], []
    for i, p in enumerate(PLANS):
        (stem, dos, t0, t1, za, zb, dit, etiq, prix, pose, cote) = p
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        dur = S2.plan(brut, stem, dos, t0, t1, za, zb, speed=1.0)
        if stem in A_STABILISER:
            brut = V8.stabilise(brut, os.path.join(d, f"{i:02d}_stab.mp4"))
        if i in ALLER_RETOUR:
            # 1 s nette seulement : on la joue puis on la rejoue a l'envers
            inv = inverse(brut, os.path.join(d, f"{i:02d}_ar.mp4"))
            brut = S.concat([brut, inv], os.path.join(d, f"{i:02d}_aller.mp4"))
            dur *= 2
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
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"vg{i}", dur - 0.05,
                                              prix=prix, taille=46)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(Y_ETIQ), "t0": 0.03, "t1": dur - 0.04,
                        "fade": 0.05})

        if i == CTA:
            cp, cw, ch = G.bloc_cta("C'EST POUR QUELLE DATE ?",
                                    "@eventys.paris", nom="cta_vingt.png",
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
                     os.path.join(OUT, "_attente_2026-11-02", "voix",
                                  "JONATHAN"),
                     v.replace(".mp4", "_son.mp4"))
        print(s, flush=True)
        # Bruitages (valides par Yanis le 2026-11-04) : pop sur chaque
        # etiquette, whoosh a chaque coupe, ding sur le total, rien sur la
        # boucle. Voir sfx.evenements_standard.
        import sfx
        ev = sfx.evenements_standard(
            durees, [p[7] is not None for p in PLANS],
            total=4, cta=CTA, boucle=BOUCLE,
            extras={3: [("vaisselle", 0.45, -15)],
                    5: [("camion_porte", 0.10, -15)]})
        print(sfx.ajoute(s, ev, s.replace("_son.mp4", "_sfx.mp4")),
              flush=True)
