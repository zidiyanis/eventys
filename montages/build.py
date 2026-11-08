"""Monte les 3 Reels Eventys a partir des rushes. N'ecrit que dans montages.

Usage : python montages\\build.py [nom_video ...]

Regles qualite :
1. N'utiliser que des sources >= 1080 px de large. Les clips 720p
   (IMG_1534, b82025e7, 4da75381) sont ecartes : les agrandir se voyait.
2. Couper sur les passages les plus NETS de chaque clip, mesures avec
   nettete.py (variance du laplacien). Pieges evites :
   - IMG_7752 (kit vaisselle) : nettete mediane 6, macro quasi flou.
   - IMG_2796 8.0-10.4s : score 17-69, le pire du clip.
   - IMG_4060 : pic a 5.8-6.6s, et lumiere violette -> ecarte.
3. Les rushes iPhone sont en HDR Dolby Vision : il FAUT convertir en SDR
   (voir est_hdr / TONEMAP), sinon le rendu est completement crame.
4. Terminer sur un plan net pour ne pas finir mou.
5. JAMAIS de clip portant deja du texte incruste (regle de Yanis). Sont
   donc exclus : `12941d2e` (« Location de chaise Napoleon a partir de 3€ »),
   tout `Contenu tiktok _`, tout `Affiches - infos_` (texte + filigrane
   « Ys.evenement »), et `Ramadan_\\Promo special Aid\\Video promo.mov`.
6. Finir chaque video par une sequence de mise en place FINALE (tables
   dressees), pas seulement les produits un par un.

Les cartes de texte sont des PNG fabriques par da.py (charte Eventys :
creme, bordeaux, rouge, Bodoni espacee). drawtext ne sait faire ni
interlettrage ni bicolore, d'ou le passage par Pillow.

Pas d'arche ni de mange-debout : aucun plan video exploitable.

Extensions (reel "annonce-retour", 2026-10-07) :
- `segment()` accepte un 9e champ optionnel `speed` dans le tuple de coupe
  (stem, folder, t0, t1, titre, prix, pos, zoom, speed). speed=1.5 accelere
  le plan x1.5 via setpts, sans toucher au son (il n'y en a pas).
- `freeze_finale()` fabrique une carte finale tenue sur l'image figee de fin
  d'un plan (dernier plan du montage), pour un CTA sans repartir sur un
  nouveau rush. Déclarée par video dans le dict `FINALES`.
"""
import json
import os
import subprocess
import sys

import da

R = r"H:\eventys\Video\rush"
FF = r"H:\eventys\tools\bin\ffmpeg.exe"
FFPROBE = r"H:\eventys\tools\bin\ffprobe.exe"
OUT = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(OUT, "_tmp")
W, H = 1080, 1920

index = json.load(open(os.path.join(R, "_catalogue", "index.json"), encoding="utf-8"))


def src(stem, folder):
    for k, v in index.items():
        name = k.split("\\")[-1]
        if name.startswith(stem) and "(1)" not in name and v["folder"] == folder:
            if min(v["width"], v["height"]) < 1080:
                raise SystemExit(f"{stem} fait {v['width']}x{v['height']} : trop petit")
            return os.path.join(R, k)
    raise SystemExit("introuvable : " + stem)


def est_hdr(path):
    """Les rushes iPhone sont en Dolby Vision / HLG (bt2020 + arib-std-b67).

    Sans conversion, ffmpeg recopie ces etiquettes sur une image 8 bits SDR :
    le lecteur croit avoir du HDR et crame toute l'image.
    """
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=color_transfer,color_primaries", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout
    return "arib-std-b67" in out or "smpte2084" in out or "bt2020" in out


TONEMAP = (
    "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
    "tonemap=tonemap=hable:desat=0,"
    "zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
)

# Ouverture commune aux trois videos : le rideau du box qui s'ouvre.
INTRO = ("IMG_1044", "Contenue Vlog_", 0.8, 3.4)

# Sequence de mise en place finale, commune aux trois videos.
# Fenetres calees sur les pics de nettete (nettete.py) :
# IMG_9454 net de 0.2 a 3.0 (mediane 316) ; IMG_9425 net de 16.6 a 19.4 ;
# IMG_4046 n'est net qu'autour de 8.2-8.6, d'ou un plan court.
FINAL = [
    ("IMG_9452", "Ramadan_", 0.2, 2.0, "", "", "bas", 1.0),
    ("IMG_9441", "Ramadan_", 10.4, 12.6, "", "", "bas", 1.0),
    ("IMG_4046", "Mariages", 7.9, 9.0, "", "", "bas", 1.0),
    ("IMG_9425", "Ramadan_", 16.6, 19.4, "", "", "bas", 1.0),
]

# (stem, dossier, debut, fin, titre, prix, position, zoom[, speed])
# zoom > 1 recadre dans l'image : sort le sac de courses du champ. Source 4K.
# speed > 1 accelere le plan (setpts=PTS/speed), optionnel, defaut 1.0.
VIDEOS = {
    "01_tout_ce_que_je_loue": [
        ("IMG_1742", "Contenue Vlog_", 3.5, 5.1, "", "", "bas", 1.0),
        ("IMG_1049", "Contenue Vlog_", 1.0, 3.4, "Chaise Napoléon", "3 €", "bas", 1.0),
        ("IMG_4045", "Mariages", 1.6, 3.9, "Table ronde", "10 €", "bas", 1.0),
        ("IMG_1727", "Contenue Vlog_", 1.3, 2.9, "Table rectangulaire", "10 €", "bas", 1.35),
        ("IMG_1013", "Contenue Vlog_", 2.4, 3.6, "Table rectangulaire", "10 €", "bas", 1.35),
        ("IMG_4054", "Mariages", 0.2, 2.3, "Kit vaisselle", "2 €", "bas", 1.0),
        ("IMG_9422", "Ramadan_", 0.2, 2.0, "Le résultat", "", "bas", 1.0),
    ] + FINAL + [
        ("IMG_9454", "Ramadan_", 0.2, 3.0, "Message privé pour un devis", "", "bas", 1.0),
    ],
    "02_du_box_a_ta_table": [
        ("IMG_1742", "Contenue Vlog_", 3.4, 5.1, "Mon stock", "", "bas", 1.0),
        ("IMG_0968", "Contenue Vlog_", 13.5, 16.5, "Je charge", "", "bas", 1.0),
        ("IMG_1716", "Contenue Vlog_", 1.5, 5.0, "Je livre", "", "bas", 1.0),
        ("IMG_1727", "Contenue Vlog_", 1.3, 2.9, "Je monte", "", "bas", 1.35),
        ("IMG_1013", "Contenue Vlog_", 2.4, 3.6, "", "", "bas", 1.35),
        ("IMG_9422", "Ramadan_", 0.2, 2.0, "Tu profites", "", "bas", 1.0),
    ] + FINAL + [
        ("IMG_9454", "Ramadan_", 0.2, 3.0, "Île-de-France · message privé", "", "bas", 1.0),
    ],
    "03_40_personnes": [
        ("IMG_9454", "Ramadan_", 0.2, 2.6, "40 personnes, combien ?", "", "bas", 1.0),
        ("IMG_1049", "Contenue Vlog_", 1.0, 3.2, "40 chaises", "120 €", "bas", 1.0),
        ("IMG_4045", "Mariages", 1.6, 3.8, "4 tables", "40 €", "bas", 1.0),
        ("IMG_4054", "Mariages", 0.2, 2.2, "40 couverts", "80 €", "bas", 1.0),
        ("IMG_9452", "Ramadan_", 0.2, 2.0, "Total", "240 €", "bas", 1.0),
    ] + FINAL[1:] + [
        ("IMG_1716", "Contenue Vlog_", 1.5, 4.0, "Livré et monté", "", "bas", 1.0),
    ],
    # Reel "annonce retour", script valide par Yanis le 2026-10-07.
    # Timecodes verifies un a un avec ffprobe (durees reelles des rushes) :
    # tous les chapitres tiennent dans la duree reelle des clips sources,
    # aucune fenetre n'a du etre raccourcie.
    "2026-10-07_reel_annonce-retour": [
        # Chapitre 1 : "Eventys est de retour"
        ("IMG_1742", "Contenue Vlog_", 1.3, 3.0, "Eventys est de retour", "", "bas", 1.0),
        ("IMG_1049", "Contenue Vlog_", 1.1, 2.6, "", "", "bas", 1.0),
        # Chapitre 2 : "Chaises, tables, décoration complète"
        ("IMG_1049", "Contenue Vlog_", 2.6, 4.3, "Chaises, tables, décoration complète", "", "bas", 1.0),
        ("IMG_1742", "Contenue Vlog_", 3.0, 4.4, "", "", "bas", 1.0),
        ("IMG_4054", "Mariages", 0.0, 2.0, "", "", "bas", 1.0),
        # Chapitre 3 : plan rapide, sans carte (demande de Yanis le 2026-10-07 :
        # la TV en fond n'est pas genante, mais pas besoin de la nommer/habiller)
        ("IMG_1013", "Contenue Vlog_", 1.0, 2.2, "", "", "bas", 1.0),
        # Chapitre 4 : "Livré directement chez vous" (plans acceleres)
        ("IMG_0968", "Contenue Vlog_", 2.0, 8.0, "Livré directement chez vous", "", "bas", 1.0, 1.5),
        ("IMG_1716", "Contenue Vlog_", 1.5, 4.5, "", "", "bas", 1.0, 1.3),
        # Chapitre 5 : rendu final, sans texte
        ("IMG_4045", "Mariages", 3.7, 8.0, "", "", "bas", 1.0),
        ("IMG_4046", "Mariages", 5.0, 8.0, "", "", "bas", 1.0),
    ],
    # Reel "catalogue", script v2 valide par Yanis le 2026-10-07 (remplace
    # la premiere version narrative "annonce-retour"). Chapitres courts,
    # un article par plan, carte finale figee sur IMG_4054.
    "2026-10-07_reel_catalogue": [
        ("IMG_4045", "Mariages", 1.2, 3.2, "On loue ça aussi", "", "bas", 1.0),
        ("IMG_9422", "Ramadan_", 1.3, 3.3, "Tu peux louer ça", "", "bas", 1.0),
        ("IMG_4046", "Mariages", 8.0, 10.0, "Chaises Napoléon aussi dispo", "", "bas", 1.0),
        ("IMG_7748", "Ramadan_", 0.9, 2.6, "Verres en location aussi", "", "bas", 1.0),
        ("IMG_7749", "Ramadan_", 1.3, 3.3, "Lanternes dispo en déco", "", "bas", 1.0),
        ("IMG_1049", "Contenue Vlog_", 1.1, 3.1, "Ça se loue chez nous", "", "bas", 1.0),
        ("IMG_9425", "Ramadan_", 2.4, 4.4, "Encore plus à découvrir", "", "bas", 1.0),
        ("IMG_4054", "Mariages", 0.5, 4.0, "", "", "bas", 1.0),
    ],
    # Reel "Du box a votre table", concept 1 (narration chronologique)
    # valide par Yanis le 2026-10-08. Deux ajustements de rushes faits par
    # le monteur par rapport au script du directeur, car le contenu reel
    # differait de la description :
    # - "En route vers vous" : IMG_6867 (coffre + chaises) remplace IMG_6945
    #   (IMG_6945 ne montre pas de van a ce moment-la).
    # - "Dechargement sur place" : IMG_6945 2.0-4.5s (chaises/table deja
    #   posees dans l'herbe) remplace IMG_6867, pour la raison inverse.
    "2026-10-08_reel_du-box-a-votre-table": [
        ("IMG_1049", "Contenue Vlog_", 1.5, 3.0, "Des chaises en stock", "", "bas", 1.0),
        ("IMG_1047", "Contenue Vlog_", 0.2, 1.0, "Prêtes en un instant", "", "bas", 1.0),
        ("IMG_0963", "Contenue Vlog_", 0.1, 0.8, "On charge tout", "", "bas", 1.0),
        ("IMG_6867", "Mise en place_", 2.2, 3.2, "En route vers vous", "", "bas", 1.0),
        ("IMG_0985", "Contenue Vlog_", 0.2, 1.7, "Direction votre événement", "", "bas", 1.0),
        ("IMG_6945", "Mise en place_", 2.0, 4.5, "Déchargement sur place", "", "bas", 1.0),
        ("IMG_1013", "Contenue Vlog_", 0.3, 1.5, "Installation en cours", "", "bas", 1.0),
        ("IMG_4046", "Mariages", 7.9, 8.7, "Chaque détail compte", "", "bas", 1.0),  # fenetre reduite : 7.8-10.0 est flou hors de 8.0-8.6 (nettete.py), voir compte-rendu monteur
        ("IMG_4054", "Mariages", 0.3, 3.3, "Votre table, prête à recevoir", "", "bas", 1.0),
        # Extension demandee par Yanis le 2026-10-08 : +10s de tables deja
        # montees/decorees en fin de video, avec un evenement pas encore vu
        # dans cette video (Mariages/Ramadan deja utilises au-dessus). Yanis
        # a valide l'usage de Noel malgre le sapin visible (choix 1 sur 3
        # propositions : accepter Noel / repeter Mariages-Ramadan / arreter
        # l'extension). Plans 4K, sans croissant de lune.
        ("IMG_3428", "Noël", 10.5, 13.0, "", "", "bas", 1.0),
        ("IMG_3438", "Noël", 5.0, 7.5, "", "", "bas", 1.0),
        ("IMG_3439", "Noël", 15.0, 17.8, "", "", "bas", 1.0),  # 13.0-14.5 = suspension floue, net seulement a partir de 15.0
    ],
}

# Chapitre 6 de certaines videos : carte finale tenue sur l'image figee de
# fin du dernier plan (pas un nouveau rush). (stem, folder, t_frame, duree,
# titre, prix, position)
FINALES = {
    "2026-10-07_reel_annonce-retour":
        ("IMG_4046", "Mariages", 8.0, 2.5, "Message privé pour ton devis", "", "bas"),
    "2026-10-07_reel_catalogue":
        ("IMG_4054", "Mariages", 4.0, 2.0, "Devis en message privé", "", "bas"),
    # Carte finale tenue sur la derniere image du chapitre 9 (IMG_4054 a 3.3s).
    "2026-10-08_reel_du-box-a-votre-table":
        ("IMG_4054", "Mariages", 3.3, 2.0, "Message privé pour un devis", "", "bas"),
}


def _chaine_cadrage(zoom):
    zw, zh = int(W * zoom), int(H * zoom)
    oy = "0" if zoom > 1 else "(in_h-out_h)/2"
    return (f"scale={zw}:{zh}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{H}:(in_w-out_w)/2:{oy},setsar=1")


def segment(part, stem, folder, t0, t1, zoom, carte_png, speed=1.0):
    path = src(stem, folder)
    chaine = _chaine_cadrage(zoom) + ",fps=30"
    if speed != 1.0:
        chaine += f",setpts=PTS/{speed}"
    if est_hdr(path):
        chaine = TONEMAP + "," + chaine

    cmd = [FF, "-y", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", path]
    if carte_png:
        # -loop 1 : sans ca le PNG ne donne qu'UNE image, et le fondu alpha
        # la rend transparente a t=0 -> la carte n'apparait jamais.
        cmd += ["-loop", "1", "-framerate", "30", "-i", carte_png,
                "-filter_complex",
                f"[0:v]{chaine}[v];"
                "[1:v]format=rgba,fade=t=in:st=0:d=0.25:alpha=1[c];"
                "[v][c]overlay=0:0:format=auto:shortest=1,format=yuv420p"]
    else:
        cmd += ["-vf", chaine + ",format=yuv420p"]
    # etiquettes bt709 forcees : sinon ffmpeg recopie celles du HDR
    cmd += ["-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-colorspace", "bt709", "-color_primaries", "bt709",
            "-color_trc", "bt709", "-color_range", "tv", part]
    subprocess.run(cmd, check=True)


def freeze_finale(name, stem, folder, t_frame, duree, titre, prix, pos="bas"):
    """Carte finale tenue sur l'image figee de fin d'un plan (pas un nouveau rush)."""
    path = src(stem, folder)
    chaine = _chaine_cadrage(1.0)
    if est_hdr(path):
        chaine = TONEMAP + "," + chaine

    os.makedirs(TMP, exist_ok=True)
    still = os.path.join(TMP, f"{name}_finale.png")
    subprocess.run([FF, "-y", "-v", "error", "-ss", str(t_frame), "-i", path,
                     "-frames:v", "1", "-vf", chaine, still], check=True)

    png = da.carte(titre, prix, f"{name}_finale_carte.png", pos)
    part = os.path.join(TMP, f"{name}_finale.mp4")
    subprocess.run([
        FF, "-y", "-v", "error",
        "-loop", "1", "-framerate", "30", "-i", still,
        "-loop", "1", "-framerate", "30", "-i", png,
        "-filter_complex",
        "[0:v]format=yuv420p[v];"
        "[1:v]format=rgba,fade=t=in:st=0:d=0.25:alpha=1[c];"
        "[v][c]overlay=0:0:format=auto,format=yuv420p",
        "-t", str(duree), "-an", "-c:v", "libx264", "-preset", "slow",
        "-crf", "18", "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", part,
    ], check=True)
    return part


def build(name, cuts, extra_parts=None):
    os.makedirs(TMP, exist_ok=True)
    parts = []

    p0 = os.path.join(TMP, f"{name}_intro.mp4")
    segment(p0, *INTRO, 1.0, da.intro())
    parts.append(p0)

    for i, cut in enumerate(cuts):
        stem, folder, t0, t1, titre, prix, pos, zoom = cut[:8]
        speed = cut[8] if len(cut) > 8 else 1.0
        part = os.path.join(TMP, f"{name}_{i:02d}.mp4")
        png = da.carte(titre, prix, f"{name}_{i:02d}.png", pos) if titre else None
        segment(part, stem, folder, t0, t1, zoom, png, speed)
        parts.append(part)

    if extra_parts:
        parts.extend(extra_parts)

    lst = os.path.join(TMP, f"{name}.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts:
            f.write("file '" + p.replace("\\", "/") + "'\n")
    final = os.path.join(OUT, name + ".mp4")
    subprocess.run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", final], check=True)
    return final


# ---------------------------------------------------------------------------
# Refonte 2026-10-14 : nouveau moteur d'effets (Ken Burns, xfade, vignette +
# grain, compteur de prix anime). Tout ce qui precede cette ligne N'EST PAS
# MODIFIE : les 6 anciens montages restent reproductibles a l'identique.
#
# Ce qui suit AJOUTE des fonctions et des cut-lists, sous des noms distincts
# (segment2, build2, VIDEOS2, FINALES2, TRANSITIONS2), pour les 3 videos
# reconduites + ameliorees (catalogue, coulisses, pack chiffre). La 4e video
# (mascotte) N'EST PAS construite : les 12 PNG detoures annonces dans
# `PROMPT_MONTEUR_retour_eventys.md` (`_cartes\\stickers\\...`) n'existent
# pas sur le disque, verifie le 2026-10-14 (seule la planche complete, non
# detouree, est presente). Idem pour le choix de grade couleur : les essais
# `_verif\\*_da*.jpg` annonces n'existent pas non plus -> aucun grade
# supplementaire n'est applique, voir effets.py.
# ---------------------------------------------------------------------------
import effets  # noqa: E402


def _width_of(stem, folder):
    for k, v in index.items():
        name = k.split("\\")[-1]
        if name.startswith(stem) and "(1)" not in name and v["folder"] == folder:
            return v["width"]
    raise SystemExit("introuvable pour largeur : " + stem)


def kb_auto(stem, folder, zoom_base=1.0):
    """Amplitude Ken Burns raisonnable selon la resolution source.

    1080p : zoom_base -> zoom_base + 0.08 (plafond 1.15).
    4K (Contenue Vlog_) : zoom_base -> zoom_base + 0.15 (plafond 1.35).
    Si zoom_base est deja au plafond ou au-dela (crop compositionnel
    existant, ex. 1.35 pour sortir un sac de courses du champ dans
    02_du_box_a_ta_table), l'amplitude est ramenee a 0 : pas de marge pour
    animer sans depasser le plafond documente par la refonte.
    """
    w = _width_of(stem, folder)
    plafond = effets.zoom_ceiling(w)
    extra = 0.15 if w >= 2000 else 0.08
    zoom_end = min(zoom_base + extra, plafond)
    return zoom_base, max(zoom_end, zoom_base)


def segment2(part, stem, folder, t0, t1, zoom_start, zoom_end, carte_spec,
             speed=1.0):
    """Version refonte de `segment()` : Ken Burns + vignette/grain, et
    `carte_spec` qui peut etre :
      - None : pas de carte
      - un chemin PNG (str) : carte simple, comme l'ancien comportement
      - une liste [(png, duree_ou_None), ...] : suite d'images (compteur de
        prix), la derniere avec duree=None tient le reste du segment.
    Retourne la duree du plan produit (apres vitesse), pour le calcul des
    offsets de xfade en aval.
    """
    path = src(stem, folder)
    dur_in = t1 - t0
    dur_out = dur_in / speed
    chaine = effets.chaine_cadrage_kb(zoom_start, zoom_end, dur_in) + ",fps=30"
    if speed != 1.0:
        chaine += f",setpts=PTS/{speed}"
    chaine += "," + effets.VIGNETTE_GRAIN
    if est_hdr(path):
        chaine = TONEMAP + "," + chaine

    cmd = [FF, "-y", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", path]

    if carte_spec is None:
        cmd += ["-vf", chaine + ",format=yuv420p"]
    else:
        frames = [(carte_spec, None)] if isinstance(carte_spec, str) else list(carte_spec)
        fixe = sum(d for _, d in frames if d is not None)
        img_inputs = []
        for png, d in frames:
            dd = d if d is not None else max(dur_out - fixe, 0.05)
            img_inputs += ["-loop", "1", "-framerate", "30", "-t", f"{dd:.3f}", "-i", png]
        n = len(frames)
        parts_f = "".join(f"[{i + 1}:v]format=rgba[c{i}];" for i in range(n))
        concat_in = "".join(f"[c{i}]" for i in range(n))
        # La carte doit etre invisible pendant les fondus croises d'entree ET
        # de sortie du plan : sinon la carte sortante et la carte entrante se
        # superposent pendant le xfade et le texte devient illisible
        # ("40 TABLESS", deux prix l'un sur l'autre). On la fait donc vivre
        # seulement au milieu du plan, avec une marge a chaque bout >= a la
        # plus longue transition (0.4 s).
        marge = min(0.40, dur_out * 0.22)
        d_fade = max(0.12, min(0.25, marge * 0.8))
        st_out = max(dur_out - marge - d_fade, marge + d_fade + 0.05)
        filt = (
            f"[0:v]{chaine}[v];"
            f"{parts_f}"
            f"{concat_in}concat=n={n}:v=1:a=0[cc];"
            f"[cc]fade=t=in:st={marge:.3f}:d={d_fade:.3f}:alpha=1,"
            f"fade=t=out:st={st_out:.3f}:d={d_fade:.3f}:alpha=1[c];"
            "[v][c]overlay=0:0:format=auto:shortest=1,format=yuv420p"
        )
        cmd += img_inputs + ["-filter_complex", filt]

    cmd += ["-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-colorspace", "bt709", "-color_primaries", "bt709",
            "-color_trc", "bt709", "-color_range", "tv", part]
    subprocess.run(cmd, check=True)
    return dur_out


def freeze_finale2(name, stem, folder, t_frame, duree, titre, prix,
                    pos="bas", taille_prix=92, zoom_fin=1.05):
    """Equivalent `freeze_finale`, avec un leger Ken Burns sur l'image figee
    et le grain/vignette du nouveau moteur. Fichiers distincts
    (`_finale2*`) : ne touche pas aux sorties de `freeze_finale()`.
    """
    path = src(stem, folder)
    chaine_still = _chaine_cadrage(1.0)
    if est_hdr(path):
        chaine_still = TONEMAP + "," + chaine_still

    os.makedirs(TMP, exist_ok=True)
    still = os.path.join(TMP, f"{name}_finale2.png")
    subprocess.run([FF, "-y", "-v", "error", "-ss", str(t_frame), "-i", path,
                     "-frames:v", "1", "-vf", chaine_still, still], check=True)

    png = da.carte(titre, prix, f"{name}_finale2_carte.png", pos, taille_prix)
    zoom_chain = effets.chaine_cadrage_kb(1.0, zoom_fin, duree) + "," + effets.VIGNETTE_GRAIN
    part = os.path.join(TMP, f"{name}_finale2.mp4")
    subprocess.run([
        FF, "-y", "-v", "error",
        "-loop", "1", "-framerate", "30", "-t", str(duree), "-i", still,
        "-loop", "1", "-framerate", "30", "-t", str(duree), "-i", png,
        "-filter_complex",
        f"[0:v]{zoom_chain},format=yuv420p[v];"
        "[1:v]format=rgba,fade=t=in:st=0:d=0.25:alpha=1[c];"
        "[v][c]overlay=0:0:format=auto,format=yuv420p",
        "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", part,
    ], check=True)
    return part, duree


def _c(stem, folder, t0, t1, titre="", prix="", pos="bas", zoom_base=1.0,
       speed=1.0, taille_prix=92, compteur=False):
    """Raccourci pour ecrire une entree de cut-list refonte : calcule
    l'amplitude Ken Burns automatiquement (kb_auto) a partir du zoom de
    depart deja valide dans les cut-lists d'origine (zoom_base)."""
    zs, ze = kb_auto(stem, folder, zoom_base)
    return (stem, folder, t0, t1, titre, prix, pos, zs, ze, speed, taille_prix, compteur)


# --- Video 1 : catalogue (reprend 2026-10-07_reel_catalogue) ---------------
# Corrections appliquees (PROMPT_REFONTE_CATALOGUE.md) :
# - carte 4 (IMG_7748, "Verres en location aussi") devient "Kit vaisselle"
#   2 € : seul le prix du kit vaisselle complet existe dans la grille de
#   Yanis (CLAUDE.md), pas de prix "verre seul". Le clip montre des verres,
#   pas le kit complet (assiettes+couverts) : ecart a confirmer avec Yanis.
# - carte "Lanternes" : AUCUN prix ajoute. Yanis n'a pas tranche si les
#   lanternes sont un article a part ou incluses dans une formule -- la
#   question est explicitement ouverte dans PROMPT_REFONTE_CATALOGUE.md.
VIDEOS2_CATALOGUE = [
    _c("IMG_4045", "Mariages", 1.2, 3.2, "On loue ça aussi"),
    _c("IMG_9422", "Ramadan_", 1.3, 3.3, "Tu peux louer ça"),
    _c("IMG_4046", "Mariages", 8.0, 10.0, "Chaises Napoléon aussi dispo"),
    _c("IMG_7748", "Ramadan_", 0.9, 2.6, "Kit vaisselle", "2 €", compteur=True),
    _c("IMG_7749", "Ramadan_", 1.3, 3.3, "Lanternes dispo en déco"),
    _c("IMG_1049", "Contenue Vlog_", 1.1, 3.1, "Ça se loue chez nous"),
    _c("IMG_9425", "Ramadan_", 2.4, 4.4, "Encore plus à découvrir"),
    _c("IMG_4054", "Mariages", 0.5, 4.0),
]
TRANSITIONS_CATALOGUE = [("fondu", 0.3)] * (len(VIDEOS2_CATALOGUE) + 1)  # +intro, +finale

# --- Video 2 : coulisses (reprend 2026-10-08_reel_du-box-a-votre-table) ---
# REGLES_EQUIPE.md, section Saison : "Noel (4K) : reserve a decembre." --
# sans condition ni exception, contrairement a la regle du croissant de
# lune. Nous sommes le 2026-10-14 : les 3 plans Noel (IMG_3428/3438/3439)
# de l'extension du 2026-10-08 sont donc RETIRES de cette passe, decision
# prise sans attendre Yanis puisque la regle est deja ecrite sans
# condition -- a rouvrir en decembre si une version "saison" est voulue.
# Plan final hero (IMG_4054, "Votre table, prete a recevoir") : ralenti
# x0.85, demande explicite du script de refonte ("point 7 : ralenti sur le
# plan hero de fin").
VIDEOS2_COULISSES = [
    _c("IMG_1049", "Contenue Vlog_", 1.5, 3.0, "Des chaises en stock"),
    _c("IMG_1047", "Contenue Vlog_", 0.2, 1.0, "Prêtes en un instant"),
    _c("IMG_0963", "Contenue Vlog_", 0.1, 0.8, "On charge tout"),
    _c("IMG_6867", "Mise en place_", 2.2, 3.2, "En route vers vous"),
    _c("IMG_0985", "Contenue Vlog_", 0.2, 1.7, "Direction votre événement"),
    _c("IMG_6945", "Mise en place_", 2.0, 4.5, "Déchargement sur place"),
    _c("IMG_1013", "Contenue Vlog_", 0.3, 1.5, "Installation en cours", zoom_base=1.35),
    _c("IMG_4046", "Mariages", 7.9, 8.7, "Chaque détail compte"),
    _c("IMG_4054", "Mariages", 0.3, 3.3, "Votre table, prête à recevoir", speed=0.85),
]
TRANSITIONS_COULISSES = [
    ("fondu", 0.3),  # intro -> clip1
    ("coupe", 0), ("coupe", 0), ("coupe", 0), ("coupe", 0),
    ("coupe", 0), ("coupe", 0), ("coupe", 0),  # clip1..clip8, coulisses energiques
    ("fondu", 0.4),  # clip8 -> clip9 (plan hero ralenti)
    ("fondu", 0.4),  # clip9 -> CTA figee
]

# --- Video 3 : pack chiffre (reprend 03_40_personnes) ----------------------
# Correction appliquee (PROMPT_REFONTE_CATALOGUE.md, trou n°1) : carte CTA
# finale ajoutee (absente dans 03_40_personnes). Texte reutilise a
# l'identique des deux autres videos ("Message privé pour un devis"), pas
# de nouveau texte invente.
VIDEOS2_PACK = [
    _c("IMG_9454", "Ramadan_", 0.2, 2.6, "40 personnes, combien ?"),
    _c("IMG_1049", "Contenue Vlog_", 1.0, 3.2, "40 chaises", "120 €", compteur=True),
    _c("IMG_4045", "Mariages", 1.6, 3.8, "4 tables", "40 €", compteur=True),
    _c("IMG_4054", "Mariages", 0.2, 2.2, "40 couverts", "80 €", compteur=True),
    _c("IMG_9452", "Ramadan_", 0.2, 2.0, "Total", "240 €", taille_prix=130, compteur=True),
    _c("IMG_9441", "Ramadan_", 10.4, 12.6),
    _c("IMG_4046", "Mariages", 7.9, 9.0),
    _c("IMG_9425", "Ramadan_", 16.6, 19.4),
    _c("IMG_1716", "Contenue Vlog_", 1.5, 4.0, "Livré et monté"),
]
TRANSITIONS_PACK = [("fondu", 0.3)] * (len(VIDEOS2_PACK) + 1)  # +intro, +finale

VIDEOS2 = {
    "2026-10-14_reel_catalogue": VIDEOS2_CATALOGUE,
    "2026-10-14_reel_du-box-a-votre-table": VIDEOS2_COULISSES,
    "2026-10-14_reel_40-personnes": VIDEOS2_PACK,
}

TRANSITIONS2 = {
    "2026-10-14_reel_catalogue": TRANSITIONS_CATALOGUE,
    "2026-10-14_reel_du-box-a-votre-table": TRANSITIONS_COULISSES,
    "2026-10-14_reel_40-personnes": TRANSITIONS_PACK,
}

# Cartes finales figees (stem, folder, t_frame, duree, titre, prix, pos) --
# reutilisent les textes deja valides ailleurs, aucun nouveau CTA invente.
FINALES2 = {
    "2026-10-14_reel_catalogue":
        ("IMG_4054", "Mariages", 4.0, 2.0, "Devis en message privé", "", "bas"),
    "2026-10-14_reel_du-box-a-votre-table":
        ("IMG_4054", "Mariages", 3.3, 2.0, "Message privé pour un devis", "", "bas"),
    "2026-10-14_reel_40-personnes":
        ("IMG_1716", "Contenue Vlog_", 3.5, 2.0, "Message privé pour un devis", "", "bas"),
}


def build2(name, cuts, transitions, finale_spec):
    """Assemble une video avec le moteur refonte (Ken Burns + xfade +
    vignette/grain + compteur de prix). N'ecrit jamais sur les anciennes
    videos : noms de sortie distincts (prefixe 2026-10-14)."""
    os.makedirs(TMP, exist_ok=True)
    parts = []

    p0 = os.path.join(TMP, f"{name}_intro.mp4")
    dur0 = segment2(p0, *INTRO, 1.0, 1.0, da.intro())
    parts.append((p0, dur0))

    for i, cut in enumerate(cuts):
        stem, folder, t0, t1, titre, prix, pos, zs, ze, speed, taille_prix, compteur = cut
        part = os.path.join(TMP, f"{name}_{i:02d}.mp4")
        carte_spec = None
        if titre and prix and compteur:
            frames = da.carte_compteur(titre, prix, f"{name}_{i:02d}", pos,
                                        taille_prix=taille_prix)
            pas = 0.4 / (len(frames) - 1)
            carte_spec = [(p, pas) for p in frames[:-1]] + [(frames[-1], None)]
        elif titre:
            carte_spec = da.carte(titre, prix, f"{name}_{i:02d}.png", pos, taille_prix)
        dur = segment2(part, stem, folder, t0, t1, zs, ze, carte_spec, speed)
        parts.append((part, dur))

    fpart, fdur = freeze_finale2(name, *finale_spec)
    parts.append((fpart, fdur))

    assert len(transitions) == len(parts) - 1, (
        f"{name} : {len(transitions)} transitions pour {len(parts)} plans "
        f"(il en faut {len(parts) - 1})")
    final = os.path.join(OUT, name + ".mp4")
    effets.assemble_xfade(parts, transitions, final)
    return final


if __name__ == "__main__":
    only = sys.argv[1:] or list(VIDEOS)
    for name in only:
        if name in VIDEOS2:
            print(build2(name, VIDEOS2[name], TRANSITIONS2[name], FINALES2[name]), flush=True)
            continue
        extra = None
        if name in FINALES:
            extra = [freeze_finale(name, *FINALES[name])]
        print(build(name, VIDEOS[name], extra_parts=extra), flush=True)
