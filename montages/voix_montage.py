"""Calcule la bande voix et l'ajuste au montage.

Principe : une replique n'est PAS enfermee dans son plan. Elle commence au
debut du plan concerne et peut deborder sur le suivant — c'est ce que fait
n'importe quel monteur, et ca evite de ralentir des rushes trop courts a
mi-vitesse, ce qui se verrait.

Regle : si une replique n'est pas finie quand la suivante devrait commencer,
la suivante est decalee. On ne superpose jamais deux voix.
"""
import os
import subprocess

FF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                  "tools", "bin", "ffmpeg.exe")
FP = FF.replace("ffmpeg.exe", "ffprobe.exe")
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAUSE = 0.18          # silence minimal entre deux repliques


def duree(f):
    s = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", f], capture_output=True, text=True)
    return float(s.stdout.strip())


def planning(plans, dossier_voix):
    """Rend [(fichier, debut_en_secondes, duree)] et la duree totale utile."""
    debuts, t = {}, 0.0
    for i, p in enumerate(plans):
        debuts[i] = t
        t += p[1] if p[0] == "p" else (p[4] - p[3]) / p[7]

    sortie, libre = [], 0.0
    for i in sorted(debuts):
        f = os.path.join(dossier_voix, f"{i:02d}.mp3")
        if not os.path.exists(f):
            continue
        d = duree(f)
        debut = max(debuts[i], libre)
        sortie.append((f, debut, d))
        libre = debut + d + PAUSE
    return sortie, libre


def _gain_vers(repliques, cible_lufs):
    """Mesure le niveau de l'ensemble des repliques et rend le gain a appliquer.

    On mesure sur la replique la plus longue, representative du debit.
    """
    f = max(repliques, key=lambda r: r[2])[0]
    r = subprocess.run([FF, "-hide_banner", "-i", f, "-af",
                        "loudnorm=print_format=summary", "-f", "null", "-"],
                       capture_output=True, text=True)
    mesure = None
    for ligne in r.stderr.splitlines():
        if "Input Integrated" in ligne:
            mesure = float(ligne.split(":")[1].replace("LUFS", "").strip())
    if mesure is None:
        return 0.0
    # les silences entre repliques baissent le niveau integre du montage
    # final d'environ 1 dB : on vise donc un peu plus haut.
    return max(min(cible_lufs + 0.8 - mesure, 12.0), -12.0)


def melange(video, repliques, sortie, volume=1.0, lit=None):
    """Incruste la bande voix sur la video deja montee.

    La bande son est allongee par un silence jusqu'a la duree exacte de
    l'image : sans cela, `-shortest` alignerait la video sur l'audio et
    rognerait la fin du montage.
    """
    duree_video = duree(video)
    entrees = ["-i", video]
    for f, _, _ in repliques:
        entrees += ["-i", f]
    if lit:
        entrees += ["-i", lit]
    gain = _gain_vers(repliques, -14.0)

    chaine = []
    for n, (_, debut, _) in enumerate(repliques, start=1):
        chaine.append(f"[{n}:a]adelay={int(debut*1000)}|{int(debut*1000)},"
                      f"volume={volume}[v{n}]")
    etiquettes = "".join(f"[v{n}]" for n in range(1, len(repliques) + 1))
    chaine.append(f"{etiquettes}amix=inputs={len(repliques)}:"
                  f"normalize=0:dropout_transition=0[parole]")
    if lit:
        # Le lit passe sous la voix et s'efface quand elle parle
        # (sidechaincompress) : il comble les silences sans masquer le texte.
        n_lit = len(repliques) + 1
        # La parole sert DEUX fois : une fois pour piloter la compression du
        # lit, une fois dans le melange final. ffmpeg refuse qu'une etiquette
        # soit consommee deux fois — d'ou `asplit`.
        chaine.append("[parole]asplit=2[parole_mix][parole_cle]")
        chaine.append(f"[{n_lit}:a]volume=0.55[lit0]")
        chaine.append("[lit0][parole_cle]sidechaincompress="
                      "threshold=0.04:ratio=6:attack=12:release=420[lit]")
        chaine.append("[parole_mix][lit]amix=inputs=2:normalize=0[voix]")
    else:
        chaine.append("[parole]anull[voix]")
    # loudnorm en UNE passe n'atteint pas sa cible : la premiere version
    # visait -14 LUFS et sortait a -16. On mesure donc d'abord (passe 1),
    # puis on corrige par un gain fixe (passe 2). `print_format=summary`
    # donne la mesure sans produire de fichier.
    # aresample APRES loudnorm : loudnorm travaille en interne a 192 kHz et
    # ressortait la piste en 96 kHz, taux qu'une bonne partie des lecteurs
    # refuse de decoder — d'ou une video qui paraissait muette.
    chaine.append(f"[voix]volume={gain:.2f}dB,alimiter=limit=0.9,"
                  f"aresample=48000,"
                  f"apad=whole_dur={duree_video:.3f},"
                  f"atrim=0:{duree_video:.3f},aformat=sample_fmts=fltp:"
                  f"channel_layouts=stereo[sortie]")

    subprocess.run([
        FF, "-y", "-v", "error", *entrees,
        "-filter_complex", ";".join(chaine),
        "-map", "0:v", "-map", "[sortie]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        # `concat -c copy` perd les etiquettes colorimetriques : on les
        # repose ici, au seul endroit ou le conteneur est reecrit.
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv",
        "-movflags", "+faststart", sortie,
    ], check=True)
    return sortie
