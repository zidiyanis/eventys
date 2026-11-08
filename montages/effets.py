"""Moteur d'effets (refonte 2026-10-14) : Ken Burns, xfade, vignette/grain,
helper mascotte. Vient en plus de `build.py`, ne modifie rien d'existant.

Deux points annonces comme prets dans les scripts de la refonte NE LE SONT
PAS sur le disque, verifie le 2026-10-14 avant d'ecrire ce module :

1. Grade couleur. `PROMPT_MONTEUR_retour_eventys.md` demande de choisir
   entre des essais `_verif\\*_da.jpg`, `*_da2.jpg`, `*_da3.jpg` : AUCUN de
   ces fichiers n'existe dans `montages\\_verif\\` (dossier verifie en
   entier). Consequence : ce module n'applique AUCUN reglage supplementaire
   (pas d'eq=, pas de curves=) au-dela du TONEMAP + etiquettes bt709 deja
   dans build.py. Decision renvoyee a la direction artistique.

2. Mascotte. Le script annonce 12 PNG detoures dans
   `montages\\_cartes\\stickers\\` (ex. `02_pouce_leve.png`,
   `08_au_telephone.png`). Ce dossier n'existe pas ; seule la planche
   complete et NON detouree `_cartes\\Planche d'autocollants de lapins
   EVENTYS.png` est presente. `overlay_mascotte()` ci-dessous est ecrit et
   verifie mecaniquement (glissade + fondu) mais n'est utilise dans AUCUNE
   video livree : il n'y a pas d'asset valide a poser.

Note technique (trouvee en testant) : le build ffmpeg installe
(`tools\\bin\\ffmpeg.exe`, 9.0.2-essentials) n'a PAS d'option `eval` sur le
filtre `crop` (seulement sur `scale`). Le Ken Burns ci-dessous anime donc
le zoom via un `scale` en `eval=frame`, suivi d'un `crop` de taille FIXE
(W x H) qui n'a donc pas besoin de reevaluation par frame.

Deuxieme bug trouve en testant (assemble_xfade) : si `offset + duration`
tombe EXACTEMENT sur la duree du flux amont (ce que donne la formule
"manuel" offset = cumul - duree), `xfade` tronque toute la suite de la
chaine au lieu d'enchainer avec le plan suivant -- verifie en isolant un
chainage a 2 etages (3 plans) : sans marge, la sortie s'arrete pile a la
fin du 1er xfade (3.8 s au lieu de ~4.57 s attendues) ; avec 0.1 s de
marge, la suite s'enchaine normalement. D'ou `MARGE_SECURITE` ci-dessous.
"""
import subprocess

FF = r"H:\eventys\tools\bin\ffmpeg.exe"
W, H = 1080, 1920

# Vignette + grain tres leger, demande explicite de la refonte. Teste sur
# source 4K (Contenue Vlog_) et 1080p avant application generale : voir
# compte-rendu du monteur, pas de pixelisation ni de banding observes.
VIGNETTE_GRAIN = "vignette=PI/6:mode=backward,noise=alls=4:allf=t"

# Marge de securite pour le chainage xfade (voir note technique ci-dessus).
# ~2 images a 30 fps : invisible, mais evite que l'offset tombe pile sur la
# fin du flux amont (bug constate avec ce build ffmpeg).
MARGE_SECURITE = 2.0 / 30


def zoom_ceiling(width_px):
    """Amplitude max de Ken Burns : 1.35 sur les sources ~4K, 1.15 sinon."""
    return 1.35 if width_px >= 2000 else 1.15


def chaine_cadrage_kb(zoom_start, zoom_end, dur, w=W, h=H):
    """Cadrage + Ken Burns : zoom anime zoom_start -> zoom_end sur `dur` s.

    Remplace le zoom statique de `build.py::_chaine_cadrage`. Si
    zoom_start == zoom_end, reproduit exactement l'ancien crop fixe (donc
    retro-compatible pour les plans ou le zoom servait a recadrer un detail
    hors champ, pas a animer).

    Methode : cadrage de reference W x H (comme l'ancien code), puis un
    `scale` dont la taille grandit dans le temps (`eval=frame`, zoom_t),
    puis un `crop` de taille FIXE W x H ancre en haut (comme l'ancien code
    pour zoom>1) qui cadre la fenetre "zoomee" du moment.
    """
    base = (f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={w}:{h}:(in_w-out_w)/2:(in_h-out_h)/2,setsar=1")
    if max(zoom_start, zoom_end) <= 1.0 + 1e-6:
        return base
    zoom_t = f"({zoom_start}+({zoom_end}-{zoom_start})*t/{dur})"
    zoomed = f"scale=w='{w}*{zoom_t}':h='{h}*{zoom_t}':eval=frame:flags=lanczos"
    # y=0 (pas centre) : reproduit le choix de l'ancien _chaine_cadrage, qui
    # ancrait le crop en haut pour les plans zoomes (sortir un sac de
    # courses du bas du champ, par ex.).
    cropfix = f"crop={w}:{h}:(in_w-out_w)/2:0"
    return f"{base},{zoomed},{cropfix},setsar=1"


def assemble_xfade(parts, transitions, out_path, ffmpeg=FF):
    """Remplace le concat `-c copy` par un chainage de xfade.

    parts : liste de (chemin_mp4, duree_s), deja au format W x H / 30fps /
    yuv420p (comme produit par segment2()).
    transitions : liste de (kind, duree_s), longueur len(parts)-1.
        kind == "fondu" : vrai fondu croise (duree_s, ex. 0.3-0.4).
        kind == "coupe" : coupe seche. Implementee comme un xfade de la
            duree d'une frame (1/30 s) : visuellement indiscernable d'une
            coupe franche, mais garde un seul mecanisme d'assemblage au
            lieu de brancher deux outils differents (concat demuxer +
            filter_complex). Simplification technique, pas de fond change.

    Chaque offset est calcule avec MARGE_SECURITE de marge avant la fin du
    flux amont (voir note technique en tete de fichier) : la duree finale
    est donc legerement plus courte que la somme brute des plans moins les
    recouvrements (de l'ordre de quelques dixiemes de seconde sur toute la
    video), sans consequence visible.
    """
    assert len(transitions) == len(parts) - 1, "une transition entre chaque paire de plans"
    inputs = []
    for p, _ in parts:
        inputs += ["-i", p]

    filt = []
    cum = parts[0][1]
    label_prev = "0:v"
    for i in range(1, len(parts)):
        kind, d = transitions[i - 1]
        d = (1.0 / 30) if kind == "coupe" else float(d)
        offset = max(cum - d - MARGE_SECURITE, 0.0)
        out_label = "vout" if i == len(parts) - 1 else f"v{i}"
        filt.append(
            f"[{label_prev}][{i}:v]xfade=transition=fade:duration={d:.4f}:"
            f"offset={offset:.4f}[{out_label}]"
        )
        label_prev = out_label
        # Duree de sortie d'un xfade = offset + duree du 2e flux (le
        # recouvrement est DEJA compris dedans). Ajouter `d` ici surestimait
        # `cum` de `d` a chaque plan : l'erreur s'accumulait, et vers le 4e
        # plan l'offset tombait au-dela de la fin reelle du flux amont ->
        # ffmpeg tronquait tout le reste (video a 10.8 s au lieu de 21 s).
        cum = offset + parts[i][1]

    graph = ";".join(filt)
    cmd = [
        ffmpeg, "-y", "-v", "error", *inputs,
        "-filter_complex", graph, "-map", f"[{label_prev}]",
        "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv", out_path,
    ]
    subprocess.run(cmd, check=True)


def overlay_mascotte(video_in, sticker_png, t_entree, t_sortie, duree_segment,
                      cote="droite", y=1250, largeur=260):
    """Filtre d'overlay mascotte : glissade depuis le bord + fondu alpha.

    ECRIT ET VERIFIE MECANIQUEMENT (avec la planche complete en guise de
    PNG de test), MAIS PAS UTILISE dans les videos livrees : les 12 poses
    detourees annoncees par le script n'existent pas sur le disque
    (`_cartes\\stickers\\`). Garde ici pour le jour ou elles existeront.

    `video_in` : label du flux video dans le filter_complex (ex. "v").
    Retourne (filtre, label_sortie) a inserer dans un filter_complex plus
    large, en supposant [2:v] (ou l'index approprie) == sticker_png charge
    en entree avec -loop 1 -framerate 30.
    """
    x_hors = W if cote == "droite" else f"-{largeur}"
    x_pose = W - largeur - 40 if cote == "droite" else 40
    glisse = 0.25  # duree de la glissade, s
    x_expr = (
        f"if(lt(t,{t_entree}),{x_hors},"
        f"if(lt(t,{t_entree + glisse}),"
        f"{x_hors}+({x_pose}-({x_hors}))*(t-{t_entree})/{glisse},"
        f"{x_pose}))"
    )
    fade_in = f"fade=t=in:st={t_entree}:d={glisse}:alpha=1"
    fade_out = f"fade=t=out:st={max(t_sortie - glisse, 0)}:d={glisse}:alpha=1"
    sticker = f"[STK]format=rgba,{fade_in},{fade_out}[stk]"
    overlay = (
        f"[{video_in}][stk]overlay=x='{x_expr}':y={y}:"
        f"enable='between(t,{t_entree},{t_sortie})':format=auto[{video_in}m]"
    )
    return sticker, overlay, f"{video_in}m"
