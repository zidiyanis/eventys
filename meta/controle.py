"""Controle automatique avant publication — bloque ce qui ne va pas.

Pourquoi ce fichier existe : l'API Instagram ne permet PAS de supprimer une
publication. Une erreur publiee reste en ligne jusqu'a ce que Yanis la
supprime a la main. Le 21 et le 22 octobre, trois carrousels et deux Reels
ont du etre supprimes manuellement.

La seule protection possible est donc en amont. Ce module mesure ce qui a
reellement echoue par le passe, et `publier.py` refuse de publier un fichier
qui ne passe pas.

    python H:/eventys/meta/controle.py <video.mp4>
"""
import os
import subprocess
import sys

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
FP = os.path.join(RACINE, "tools", "bin", "ffprobe.exe")

# Seuils tires des echecs reels, pas choisis au hasard.
# Le seuil 0,20 avait ete calibre sur des montages faits de PHOTOS fixes,
# ou tout mouvement vient de `zoompan`. Applique a un montage fait de vrais
# rushes tenus a la main, il rejette tout : mesure sur le Reel du 20 octobre
# — celui que Yanis designe comme son meilleur contenu — les dix plans vont
# de 0,50 a 4,34. Un seuil absolu ne distingue donc pas un defaut d'un
# simple mouvement de camera.
#
# La question utile n'est pas « ce plan bouge-t-il » mais « ce plan
# bouge-t-il bien plus que les autres du meme montage ». D'ou une regle
# relative : un plan est signale s'il depasse a la fois 5 fois la mediane du
# montage et le plancher absolu ci-dessous. Verifie sur les deux cas reels :
#   - Reel du 20/10 (publie, juge bon) : mediane 1,42 — pire plan 4,34, donc
#     accepte ;
#   - IMG_6945 du 26/10 (panoramique incontrolable, ecarte a l'oeil) :
#     mediane 0,70 — plan a 7,22, donc refuse.
SECOUSSE_MAX = 0.20     # montages photo : sans zoom 0,005, avec zoompan 0,50
SECOUSSE_PLANCHER = 3.0  # en dessous, aucun plan n'est signale
SECOUSSE_FACTEUR = 5.0   # multiple de la mediane du montage
# Un critere purement relatif ne se declenche JAMAIS sur une video
# entierement secouee : la mediane monte avec le defaut. D'ou un plafond
# absolu, place au-dessus du pire plan du Reel publie (4,34) et en dessous
# du panoramique ecarte le 26 octobre (7,22).
SECOUSSE_PLAFOND = 6.0

# Un panoramique trop rapide pour la vitesse d'obturation donne une image
# TRAINEE : elle bouge peu d'une image a l'autre, donc la mesure de
# tremblement la trouve calme, et elle est pourtant inregardable. C'est
# passe le 26 octobre sur deux plans de dix. Il faut donc mesurer aussi la
# NETTETE (variance du laplacien), et signaler un plan nettement moins net
# que les autres du meme montage.
NETTETE_FACTEUR = 0.45   # moyenne du plan, en fraction de la mediane
# Et un seuil sur le CREUX a l'interieur du plan : le 26 octobre, un plan
# net sur 95 % de sa duree et file sur sa derniere demi-seconde passait a
# 47 % de la mediane, juste au-dessus du seuil ci-dessus. La moyenne dilue
# un defaut de douze images dans soixante-douze.
NETTETE_CREUX = 0.25
LUFS_MIN, LUFS_MAX = -16.0, -12.0
DUREE_MAX = 90.0        # limite des Reels


def _sonde(video, cle, flux="v:0"):
    r = subprocess.run([FP, "-v", "error", "-select_streams", flux,
                        "-show_entries", f"stream={cle}", "-of", "csv=p=0",
                        video], capture_output=True, text=True)
    return r.stdout.strip().strip(",")


def duree(video):
    r = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", video], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def coupes(video, seuil=0.25):
    """Positions des changements de plan, pour ne pas les confondre avec
    du tremblement."""
    r = subprocess.run([FF, "-hide_banner", "-i", video,
                        "-vf", f"select='gt(scene,{seuil})',showinfo",
                        "-f", "null", "-"], capture_output=True, text=True)
    t = []
    for ligne in r.stderr.splitlines():
        if "pts_time:" in ligne:
            try:
                t.append(float(ligne.split("pts_time:")[1].split()[0]))
            except (ValueError, IndexError):
                pass
    return t


def secousse(video, debut, duree_fen=1.2):
    """Ecart moyen entre images consecutives sur une fenetre."""
    b = subprocess.run([FF, "-v", "error", "-ss", f"{debut:.2f}",
                        "-t", f"{duree_fen:.2f}", "-i", video,
                        "-vf", "scale=200:-1,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    # Le nombre d'images rendues n'est pas exactement duree x 30 : on le
    # DEDUIT de la taille des donnees plutot que de le supposer.
    larg = 200
    haut = int(_sonde(video, "height") or 1920)
    lg = int(_sonde(video, "width") or 1080)
    haut = max(int(round(haut * larg / lg / 2)) * 2, 2)
    taille = larg * haut
    n = len(b) // taille
    if n < 6:
        return None
    a = np.frombuffer(b[:n * taille], dtype=np.uint8).reshape(
        n, haut, larg).astype(float)
    d = np.array([np.abs(a[i + 1] - a[i]).mean() for i in range(n - 1)])
    # On ecarte le quart le plus fort : un bandeau qui apparait en fondu ou
    # une etiquette qui se pose produisent un pic unique, qui n'est pas un
    # tremblement. Le saut de `zoompan`, lui, est PERIODIQUE — il survit a
    # ce filtrage.
    d = np.sort(d)[: max(int(len(d) * 0.75), 4)]
    return float(d.std())


def nettete(video, debut, duree_fen=1.0):
    """Variance du laplacien, moyennee sur une fenetre.

    Mesure le FLOU, que la mesure de tremblement ne voit pas : un file
    regulier est calme d'une image a l'autre et pourtant trainé.
    """
    larg = 320
    haut = int(_sonde(video, "height") or 1920)
    lg = int(_sonde(video, "width") or 1080)
    haut = max(int(round(haut * larg / lg / 2)) * 2, 2)
    b = subprocess.run([FF, "-v", "error", "-ss", f"{debut:.2f}",
                        "-t", f"{duree_fen:.2f}", "-i", video,
                        "-vf", f"fps=6,scale={larg}:{haut},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    n = len(b) // (larg * haut)
    if n < 2:
        return None
    a = np.frombuffer(b[:n * larg * haut],
                      dtype=np.uint8).reshape(n, haut, larg).astype(float)
    v = []
    for g in a:
        lap = (g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:]
               - 4 * g[1:-1, 1:-1])
        v.append(lap.var())
    # On rend la moyenne ET le minimum. La moyenne seule dilue le defaut :
    # un plan net a 95 % mais file sur sa derniere demi-seconde est passe
    # a 47 % de la mediane, pour un seuil a 45 %. Or ce plan est a
    # recouper. Le minimum, lui, le voit.
    return float(np.mean(v)), float(np.min(v))


def zone_sure(video, instants):
    """Boite englobante de l'habillage, mesuree par DIFFERENCE d'images.

    On compare une image portant un habillage a une image du meme plan qui
    ne l'a pas encore : ce qui change est l'habillage. C'est la seule facon
    fiable de connaitre sa boite — un calcul theorique se trompe des qu'un
    element est plus large que la zone sure et se fait borner.

    Le 22 octobre, un bandeau de 1050 px a ete publie dans une zone de
    850 px : recentre, il debordait quand meme de 229 px.
    """
    def image(t):
        b = subprocess.run([FF, "-v", "error", "-ss", f"{t:.2f}", "-i", video,
                            "-frames:v", "1", "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"],
                           capture_output=True).stdout
        h = int(_sonde(video, "height") or 1920)
        w = int(_sonde(video, "width") or 1080)
        if len(b) < w * h * 3:
            return None
        return np.frombuffer(b[:w * h * 3],
                             dtype=np.uint8).reshape(h, w, 3).astype(int)

    pires = []
    for t_avec, t_sans in instants:
        a, s_ = image(t_avec), image(t_sans)
        if a is None or s_ is None:
            continue
        d = np.abs(a - s_).sum(axis=2) > 40
        cols = np.where(d.sum(axis=0) > 6)[0]
        lig = np.where(d.sum(axis=1) > 6)[0]
        if len(cols) and len(lig):
            pires.append((int(cols.max()), int(lig.max()), t_avec))
    return pires


def controler(video, zones=None):
    """Rend (liste des problemes, liste des mesures)."""
    pbs, mesures = [], []

    d = duree(video)
    mesures.append(f"duree            {d:.1f} s")
    if d > DUREE_MAX:
        pbs.append(f"duree {d:.0f} s : au-dela des {DUREE_MAX:.0f} s "
                   f"acceptes par Instagram")
    if d < 3:
        pbs.append(f"duree {d:.1f} s : trop courte")

    pix = _sonde(video, "pix_fmt")
    prof = _sonde(video, "profile")
    mesures.append(f"image            {prof}, {pix}")
    if pix != "yuv420p":
        pbs.append(f"format d'image {pix} : Instagram et TikTok exigent "
                   f"yuv420p")

    sr = _sonde(video, "sample_rate", "a:0")
    mesures.append(f"son              {sr or 'AUCUN'} Hz")
    if not sr:
        pbs.append("aucune piste audio")
    elif sr != "48000":
        pbs.append(f"son a {sr} Hz : beaucoup de lecteurs refusent, "
                   f"il faut 48000")

    if sr:
        r = subprocess.run([FF, "-hide_banner", "-i", video, "-af",
                            "loudnorm=print_format=summary", "-f", "null", "-"],
                           capture_output=True, text=True)
        lufs = None
        for ligne in r.stderr.splitlines():
            if "Input Integrated" in ligne:
                try:
                    lufs = float(ligne.split(":")[1].replace("LUFS", "").strip())
                except ValueError:
                    pass
        if lufs is not None:
            mesures.append(f"niveau sonore    {lufs:.1f} LUFS")
            if not (LUFS_MIN <= lufs <= LUFS_MAX):
                pbs.append(f"niveau {lufs:.1f} LUFS : viser entre "
                           f"{LUFS_MIN} et {LUFS_MAX}")

    # Tremblement, mesure A L'INTERIEUR des plans : une coupe produit un
    # grand ecart qui n'est pas un defaut.
    c = [0.0] + coupes(video) + [d]
    pires = []
    for i in range(len(c) - 1):
        a, b_ = c[i], c[i + 1]
        if b_ - a < 1.6:
            continue
        s = secousse(video, a + 0.25, min(1.2, b_ - a - 0.4))
        if s is not None:
            pires.append((s, a))
    if pires:
        pire, quand = max(pires)
        valeurs = sorted(s for s, _ in pires)
        med = valeurs[len(valeurs) // 2]
        mesures.append(f"tremblement max  {pire:.3f} (vers {quand:.1f} s), "
                       f"mediane {med:.3f}")
        if med <= SECOUSSE_MAX:
            # Montage de photos : le mouvement ne peut venir que de zoompan.
            limite, cause = SECOUSSE_MAX, ("Supprimer le zoom — `zoompan` "
                                           "avance par pixels entiers et saute.")
        else:
            # Relatif, mais borne : au-dela du plafond un plan est signale
            # quoi qu'il arrive, meme si tout le montage bouge autant.
            limite = min(max(med * SECOUSSE_FACTEUR, SECOUSSE_PLANCHER),
                         SECOUSSE_PLAFOND)
            cause = ("Ce plan bouge bien plus que les autres du montage : "
                     "rush tenu a la main ou panoramique trop rapide. "
                     "Choisir un autre passage, ou un autre rush.")
        if pire > limite:
            pbs.append(f"tremblement {pire:.3f} vers {quand:.1f} s : "
                       f"au-dela de {limite:.2f}. {cause}")
    # Nettete par plan, sur les memes fenetres que le tremblement.
    nets = []
    for i in range(len(c) - 1):
        a, b_ = c[i], c[i + 1]
        if b_ - a < 1.6:
            continue
        v = nettete(video, a + 0.2, max(b_ - a - 0.3, 0.4))
        if v is not None:
            nets.append((v[0], v[1], a))
    if len(nets) >= 4:
        vals = sorted(v for v, _, _ in nets)
        med_n = vals[len(vals) // 2]
        moy_n, mini_n, quand_n = min(nets, key=lambda n: n[1])
        mesures.append(f"nettete          moyenne mini {min(n[0] for n in nets):.0f}, "
                       f"creux {mini_n:.0f} (vers {quand_n:.1f} s), "
                       f"mediane {med_n:.0f}")
        for moy, mini, quand in nets:
            if moy < med_n * NETTETE_FACTEUR:
                pbs.append(f"plan a {quand:.1f} s : nettete {moy:.0f} contre "
                           f"{med_n:.0f} de mediane. Image trainee sur tout "
                           f"le plan — panoramique trop rapide. Choisir une "
                           f"autre fenetre dans le rush, ou un autre rush.")
            elif mini < med_n * NETTETE_CREUX:
                pbs.append(f"plan a {quand:.1f} s : creux de nettete a "
                           f"{mini:.0f} contre {med_n:.0f} de mediane. Le "
                           f"plan est net dans l'ensemble mais file sur une "
                           f"partie : resserrer la fenetre de coupe.")

    if zones:
        for xmax, ymax, quand in zone_sure(video, zones):
            mesures.append(f"habillage a {quand:.1f}s   x jusqu'a {xmax}, "
                           f"y jusqu'a {ymax}")
            if xmax > 850:
                pbs.append(f"habillage a {quand:.1f} s : deborde de "
                           f"{xmax - 850} px a droite. Les boutons de "
                           f"l'application recouvrent au-dela de x=850.")
            if ymax > 1440:
                pbs.append(f"habillage a {quand:.1f} s : descend {ymax - 1440} "
                           f"px trop bas. La barre de legende recouvre "
                           f"au-dela de y=1440.")
    return pbs, mesures


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    pbs, mesures = controler(sys.argv[1])
    print("MESURES")
    for m in mesures:
        print("  " + m)
    if pbs:
        print("\nPROBLEMES — publication deconseillee")
        for p in pbs:
            print("  - " + p)
        sys.exit(1)
    print("\nAucun probleme detecte.")
