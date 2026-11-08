"""« Le retour » v3 — deux corrections demandees par Yanis.

1. LE LAPIN NE VOLE PLUS. En v2 il flottait (sinusoide verticale) et montait
   en rebondissant : a l'ecran ca donnait un personnage en levitation. Ici il
   ENTRE PAR LE COTE, en glissade horizontale pure, et il se fige a sa place.
   Plus aucun mouvement vertical.

2. LES PLANS SANS RUSH NE SONT PLUS VIDES. Fond evenementiel : arche doree
   (un de ses produits), confettis qui tombent sur trois profondeurs, lueur
   chaude. Le lapin se tient au sol, sous l'arche.
"""
import os
import subprocess

import decor as D
import graphismes as G
import styles as S
import styles2 as S2

W, H, FPS = S.W, S.H, S.FPS
FF, OUT, X_MAX = S.FF, S.OUT, S.X_MAX
TMP = os.path.join(OUT, "_tmp_retour3")

# Plans portes a la main, qui tremblent une fois acceleres.
STABILISER = {"IMG_1716", "IMG_0968", "IMG_0963"}

SOL = 1500          # ligne de sol du decor : le lapin pose ses pieds dessus
BASE_RUSH = 1395    # pied du lapin sur les plans filmes


def _dir(n):
    d = os.path.join(TMP, n)
    os.makedirs(d, exist_ok=True)
    return d


def entre_cote(x_fin, cote, t0, duree=0.34):
    """Glissade horizontale pure, sans la moindre composante verticale.

    `cote` : "g" il entre par la gauche, "d" par la droite.
    """
    hors = -700 if cote == "g" else W + 60
    return (f"({x_fin})+(({hors})-({x_fin}))*"
            f"pow(1-min(max((t-{t0:.3f})/{duree:.3f},0),1),3)")


def haut_sticker(chemin, largeur):
    from PIL import Image
    w, h = Image.open(chemin).size
    return int(largeur * h / w)


SCENE_JARDIN = os.path.join(OUT, "_cartes", "generes", "scene_jardin.png")


def stabilise(entree, sortie):
    """Stabilisation vidstab en 2 passes.

    Les plans portes a la main et acceleres (porter dix chaises a x1.3)
    tremblent : accelerer multiplie la secousse. vidstab mesure le mouvement
    reel (passe 1) puis le compense (passe 2). Le leger zoom de la passe 2
    masque les bords vides laisses par la compensation.
    """
    # Nom de fichier NU + cwd : un chemin absolu Windows casse la syntaxe du
    # filtre, le « : » de « H: » etant lu comme separateur d'options ffmpeg.
    dossier = os.path.dirname(os.path.abspath(sortie))
    trf = os.path.basename(sortie) + ".trf"
    subprocess.run([
        FF, "-y", "-v", "error", "-i", os.path.abspath(entree),
        "-vf", f"vidstabdetect=shakiness=10:accuracy=15:result={trf}",
        "-f", "null", "-",
    ], check=True, cwd=dossier)
    subprocess.run([
        FF, "-y", "-v", "error", "-i", os.path.abspath(entree),
        "-vf", (f"vidstabtransform=input={trf}:smoothing=40:zoom=5:"
                f"optzoom=1:interpol=bicubic,unsharp=5:5:0.6:3:3:0.4"),
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv",
        os.path.basename(sortie),
    ], check=True, cwd=dossier)
    return sortie


def plan_scene(sortie, dur, image=None, za=1.00, zb=1.07):
    """Plan plein cadre sur une scene generee, avec travelling avant lent.

    Remplace l'ancien fond beige + sticker colle : Yanis voulait une vraie
    scene (le lapin assis sur une chaise Napoleon, jardin dresse en fond) et
    pas un PNG pose sur un aplat.
    """
    img = image or SCENE_JARDIN
    frames = max(int(round(dur * FPS)), 1)
    k = max(za, zb, 1.0) * 1.15
    iw, ih = int(W * k) // 2 * 2, int(H * k) // 2 * 2
    z = f"{za:.4f}+({zb - za:.4f})*min(on/{frames},1)"
    subprocess.run([
        FF, "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS),
        "-t", f"{dur:.3f}", "-i", img,
        "-vf", (f"scale={iw}:{ih}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={iw}:{ih}:(in_w-out_w)/2:(in_h-out_h)/2,setsar=1,"
                f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d=1:s={W}x{H}:fps={FPS},setsar=1,"
                f"eq=contrast=1.03:saturation=1.02,format=yuv420p"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", sortie,
    ], check=True)
    return dur


def carte_texte(larg, haut, nom):
    """Carte creme derriere le texte : sur un jardin ensoleille, l'encre
    seule devient illisible."""
    from PIL import Image, ImageDraw
    p = os.path.join(TMP, nom)
    os.makedirs(TMP, exist_ok=True)
    img = Image.new("RGBA", (larg + 56, haut + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, larg + 55, haut + 39], radius=26,
                        fill=S.CREME + (242,))
    img.save(p)
    return p, larg + 56, haut + 40


def plan_decor(sortie, dur):
    """Fond evenementiel fixe (les confettis sont ajoutes en calques)."""
    fond = D.fond_evenement()
    frames = max(int(round(dur * FPS)), 1)
    z = f"1.0+0.030*on/{frames}"
    subprocess.run([
        FF, "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS),
        "-t", f"{dur:.3f}", "-i", fond,
        "-vf", (f"scale={int(W * 1.2) // 2 * 2}:{int(H * 1.2) // 2 * 2}:flags=lanczos,"
                f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d=1:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", sortie,
    ], check=True)
    return dur


# ("p", duree, phrase, pose, taille)
# ("r", stem, dossier, t0, t1, za, zb, vit, phrase, pose, cote, taille, etiq, prix)
PLANS = [
    ("r", "IMG_1044", "Contenue Vlog_", 0.9, 3.4, 1.04, 1.10, 1.0,
     "Ouvre. J'ai pas de mains.", "17_lunettes_pointe", "d", 300,
     "ÎLE-DE-FRANCE", None),
    ("r", "IMG_1049", "Contenue Vlog_", 1.0, 2.9, 1.00, 1.08, 1.0,
     "Lui il lave. Moi je supervise.", "02_pouce_leve", "g", 260,
     "CHAISE NAPOLÉON", "3 €"),
    ("r", "IMG_4054", "Mariages", 0.3, 2.2, 1.02, 1.10, 1.0,
     None, None, None, 0, "KIT VAISSELLE", "2 €"),
    ("r", "IMG_4045", "Mariages", 1.7, 3.6, 1.00, 1.07, 1.0,
     None, "03_montre_la_main", "d", 250, "TABLE RONDE", "10 €"),
    ("r", "IMG_0963", "Contenue Vlog_", 0.1, 0.8, 1.00, 1.06, 1.0,
     "Plus vite.", "17_lunettes_pointe", "g", 300, None, None),
    ("r", "IMG_0968", "Contenue Vlog_", 2.5, 6.5, 1.00, 1.05, 1.6,
     "J'ai dit plus vite.", "16_lunettes_bras_croises", "d", 330, None, None),
    ("r", "IMG_0985", "Contenue Vlog_", 0.2, 1.7, 1.00, 1.06, 1.0,
     "Il conduit. J'ai pas le permis.", "05_timide_main_bouche", "g", 260,
     "LIVRÉ CHEZ VOUS", None),
    ("r", "IMG_1716", "Contenue Vlog_", 1.6, 4.75, 1.00, 1.07, 1.1,
     "Dix d'un coup. Bon employé.", "16_lunettes_bras_croises", "d", 280, None, None),
    ("p", 4.9, "Chemise. Donc sérieusement : je livre et je monte.",
     "12_chemise_debout", 430),
    ("r", "IMG_1013", "Contenue Vlog_", 0.4, 2.2, 1.06, 1.14, 1.0,
     None, "13_chemise_bras_croises", "g", 250, "MONTÉ SUR PLACE", None),
    ("r", "IMG_4046", "Mariages", 7.95, 8.85, 1.00, 1.06, 1.0,
     None, None, None, 0, None, None),
    ("r", "IMG_4054", "Mariages", 0.4, 2.9, 1.00, 1.07, 1.0,
     None, "14_chemise_telephone", "d", 260, None, None),
    ("r", "IMG_1044", "Contenue Vlog_", 0.9, 4.2, 1.10, 1.04, 1.0,
     "Allez. On recommence.", "17_lunettes_pointe", "d", 300, None, None),
]


def monte(nom="RETOUR_v5"):
    d = _dir("plans")
    parts = []
    couches = D.couches_confettis()

    for i, p in enumerate(PLANS):
        brut = os.path.join(d, f"{i:02d}_brut.mp4")
        cal = []

        if p[0] == "p":
            _, duree, phrase, pose_nom, taille = p
            dur = plan_scene(brut, duree)
            # confettis legers par-dessus la scene, deux profondeurs
            for c in couches[1:]:
                cal.append({"png": c["png"], "w": None, "x": "0",
                            "y": D.expr_chute(c["vitesse"]),
                            "t0": 0.0, "t1": dur, "fade": 0.25})
            seq, lw, lh = G.karaoke_seq(phrase, f"r4_{i}", dur - 0.08,
                                        mots_par_sec=2.8)
            cp, cw, ch = carte_texte(lw, lh, f"carte_{i}.png")
            cal.append({"png": cp, "w": None,
                        "x": str(int((W - cw) / 2)), "y": "286",
                        "t0": 0.04, "t1": dur - 0.04, "fade": 0.10})
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(int((W - lw) / 2)), "y": "306",
                        "t0": 0.04, "t1": dur - 0.04, "fade": 0.10})
            sp, sw, sh = G.signature()
            cal.append({"png": sp, "w": None, "x": "46", "y": "250",
                        "t0": 0.0, "t1": dur, "fade": 0.3})
            parts.append(S2.pose(brut, cal, os.path.join(d, f"{i:02d}.mp4"), dur))
            continue

        (_, stem, dos, t0, t1, za, zb, vit, phrase, pose_nom, cote,
         taille, etiq, prix) = p
        dur = S2.plan(brut, stem, dos, t0, t1, za, zb, speed=vit)
        if stem in STABILISER:
            stab = os.path.join(d, f"{i:02d}_stab.mp4")
            brut = stabilise(brut, stab)
        tdeb, tfin = 0.10, dur - 0.05

        # Trois bandes qui ne se chevauchent jamais. Quand une etiquette est
        # presente, le lapin "pose ses pieds" plus haut (1175) pour rester
        # AU-DESSUS d'elle : sinon il mord sur la boite et le cadre est sale.
        if etiq:
            taille = min(taille, 230)
            y_bulle, y_etiq, base = 690, 1230, 1175
        elif i == len(PLANS) - 2:
            # plan du CTA : le bandeau occupe le bas, le lapin se pose dessus
            y_bulle, y_etiq, base = 870, 1210, 1090
        else:
            y_bulle, y_etiq, base = 870, 1210, BASE_RUSH

        cx_lapin, hh = None, 0
        if pose_nom:
            chemin = S.sticker(pose_nom)
            hh = haut_sticker(chemin, taille)
            # Il se tient AU BORD du cadre, legerement rogne a gauche,
            # comme accroche au rebord de l'ecran (idee de Yanis). A droite
            # on reste en deca de X_MAX : au-dela, l'interface Instagram
            # recouvre.
            x_fin = -int(taille * 0.16) if cote == "g" else X_MAX - taille
            cx_lapin = max(x_fin + taille // 2, 150)
            cal.append({"png": chemin, "w": taille,
                        "x": entre_cote(x_fin, cote, tdeb),
                        "y": str(base - hh),   # pose au sol, aucune oscillation
                        "t0": tdeb, "t1": tfin, "fade": 0.10})

        if etiq:
            seq, lw, lh = G.etiquette_pop_seq(etiq, f"r3_{i}", dur - 0.06,
                                              prix=prix, taille=58)
            cal.append({"seq": seq, "png": None, "w": None,
                        "x": str(max(min(int((W - lw) / 2), X_MAX - lw), 24)),
                        "y": str(y_etiq), "t0": 0.04, "t1": tfin, "fade": 0.05})

        if phrase:
            # La bulle se cale sur la mascotte. On MESURE la bulle avant de
            # la dessiner, on choisit x pour qu'elle soit centree au-dessus
            # du lapin, on borne au cadre, puis on redessine la pointe a la
            # bonne abscisse. Avant, x etait fige a 360 ou 60 : des que le
            # lapin passait a droite, la bulle pointait dans le vide.
            lw, lh = S.mesure_bulle(phrase, None)
            if cx_lapin is None:
                x = max(min(int((W - lw) / 2), X_MAX - lw), 20)
            else:
                x = int(max(min(cx_lapin - lw // 2, X_MAX - lw), 20))
            qx = (cx_lapin - x) if cx_lapin is not None else None
            y_haut = max(base - hh - lh - 26, 300) if pose_nom else y_bulle

            # dernier plan : bulle posee d'un coup, sinon elle finit de
            # s'ecrire au moment ou la video se coupe et on ne lit rien.
            if dur < 1.3 or i == len(PLANS) - 1:
                png, lw, lh = S.bulle(phrase, None, f"r4_{i}.png", queue_x=qx)
                cal.append({"png": png, "w": None, "x": str(x),
                            "y": str(y_haut),
                            "t0": 0.04, "t1": tfin, "fade": 0.04})
            else:
                seq, lw, lh = S2.bulle_seq(phrase, None, f"r4_{i}",
                                           max(dur - tdeb, 0.4), vitesse=55.0,
                                           queue_x=qx)
                cal.append({"seq": seq, "png": None, "w": None, "x": str(x),
                            "y": str(y_haut),
                            "t0": tdeb + 0.03, "t1": tfin, "fade": 0.10})

        if i == len(PLANS) - 2:
            cp, cw, ch = G.bloc_cta("C'EST POUR QUELLE DATE ?", "@eventys.paris")
            cal.append({"png": cp, "w": None,
                        "x": str(max(min(int((W - cw) / 2), X_MAX - cw), 18)),
                        "y": "1120", "t0": 0.10, "t1": tfin, "fade": 0.10})

        sp, sw, sh = G.signature()
        cal.append({"png": sp, "w": None, "x": "46", "y": "250",
                    "t0": 0.0, "t1": dur, "fade": 0.3})

        parts.append(S2.pose(brut, cal, os.path.join(d, f"{i:02d}.mp4"), dur))

    final = os.path.join(OUT, nom + ".mp4")
    S.concat(parts, final)
    return final


if __name__ == "__main__":
    print(monte(), flush=True)
