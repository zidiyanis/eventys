"""Fabrique le lit sonore des videos Eventys.

Pourquoi pas une musique telechargee : une musique incrustee dans le fichier
ne compte pas comme « son tendance » sur Instagram ni TikTok, donc elle
n'apporte aucun benefice d'algorithme — alors qu'elle ajoute un risque de
droits. Le lit est donc construit a partir de deux matieres qui appartiennent
a Yanis ou ne appartiennent a personne :

  1. l'AMBIANCE de ses propres rushes (rideau du box, gravier, chaises) ;
  2. une NAPPE harmonique de synthese, generee ici meme — quatre sinusoides
     formant un accord chaud, filtrees et noyees de reverberation.

Le tout reste tres bas sous la voix : il s'agit de supprimer le silence
numerique entre les repliques, pas de faire de la musique. Le relecteur
avait releve que la voix posee sur du vide est un signal que les plateformes
associent au contenu genere.
"""
import os
import subprocess

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
FP = os.path.join(RACINE, "tools", "bin", "ffprobe.exe")
SON = os.path.join(RACINE, "assets", "son")

# Accord de fa majeur avec neuvieme : chaud, ouvert, sans tension.
ACCORD = [174.61, 220.00, 261.63, 392.00]


def duree(f):
    r = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", f], capture_output=True, text=True)
    return float(r.stdout.strip())


def nappe(secondes, sortie=None):
    """Nappe harmonique de synthese, douce et sans attaque."""
    sortie = sortie or os.path.join(SON, "nappe.wav")
    os.makedirs(SON, exist_ok=True)
    entrees, etiquettes = [], []
    for i, f in enumerate(ACCORD):
        entrees += ["-f", "lavfi", "-t", f"{secondes:.2f}",
                    "-i", f"sine=frequency={f}:sample_rate=48000"]
        # chaque voix respire a une vitesse differente : evite l'orgue fige
        # `tremolo` n'accepte pas de frequence sous 0,1 Hz : on part de 0,12
        # et on ecarte chaque voix, pour qu'elles ne respirent pas ensemble.
        etiquettes.append(
            f"[{i}:a]tremolo=f={0.12 + i * 0.05:.2f}:d=0.35,"
            f"volume={0.5 - i * 0.07:.2f}[v{i}]")
    mix = "".join(f"[v{i}]" for i in range(len(ACCORD)))
    chaine = ";".join(etiquettes + [
        f"{mix}amix=inputs={len(ACCORD)}:normalize=0[somme]",
        # passe-bas : enleve la durete des sinusoides pures
        "[somme]lowpass=f=900,highpass=f=90,"
        # reverberation simple : deux echos courts et sourds
        "aecho=0.7:0.6:180|420:0.35|0.22,"
        f"afade=t=in:st=0:d=2.5,afade=t=out:st={max(secondes-3,0):.2f}:d=3,"
        "volume=0.5[out]",
    ])
    subprocess.run([FF, "-y", "-v", "error", *entrees,
                    "-filter_complex", chaine, "-map", "[out]",
                    "-ar", "48000", "-ac", "2", sortie], check=True)
    return sortie


def ambiance_rushes(secondes, sortie=None):
    """Colle bout a bout l'ambiance de plusieurs rushes, puis boucle."""
    sortie = sortie or os.path.join(SON, "ambiance.wav")
    os.makedirs(SON, exist_ok=True)
    sources = [
        ("Contenue Vlog_/IMG_1044.MOV", 0.6, 3.4),
        ("Contenue Vlog_/IMG_0968.MOV", 2.0, 7.0),
        ("Contenue Vlog_/IMG_1716.MOV", 1.4, 5.0),
        ("Mise en place_/IMG_7015.MOV", 0.3, 4.4),
    ]
    morceaux = []
    for i, (rel, a, b) in enumerate(sources):
        src = os.path.join(RACINE, "Video", "rush", *rel.split("/"))
        if not os.path.exists(src):
            continue
        m = os.path.join(SON, f"_amb{i}.wav")
        subprocess.run([FF, "-y", "-v", "error", "-ss", str(a), "-to", str(b),
                        "-i", src, "-vn", "-ar", "48000", "-ac", "2",
                        "-af", "highpass=f=70,lowpass=f=7000,"
                               "afade=t=in:d=0.3,afade=t=out:st="
                               f"{max(b-a-0.3,0.1):.2f}:d=0.3",
                        m], check=True)
        morceaux.append(m)

    liste = os.path.join(SON, "_liste.txt")
    with open(liste, "w", encoding="utf-8") as f:
        for m in morceaux:
            f.write(f"file '{os.path.basename(m)}'\n")
    brut = os.path.join(SON, "_amb_brut.wav")
    subprocess.run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", os.path.basename(liste), "-c", "copy",
                    os.path.basename(brut)], check=True, cwd=SON)

    subprocess.run([FF, "-y", "-v", "error", "-stream_loop", "-1", "-i", brut,
                    "-t", f"{secondes:.2f}",
                    "-af", "volume=0.9,afade=t=in:st=0:d=1.2,"
                           f"afade=t=out:st={max(secondes-1.8,0):.2f}:d=1.8",
                    "-ar", "48000", "-ac", "2", sortie], check=True)
    for m in morceaux + [brut, liste]:
        try:
            os.remove(m)
        except OSError:
            pass
    return sortie


def lit_sonore(secondes, sortie=None, part_nappe=0.30, part_ambiance=0.22):
    """Melange nappe et ambiance en une seule piste, prete a glisser
    sous la voix."""
    sortie = sortie or os.path.join(SON, "lit.wav")
    n = nappe(secondes)
    a = ambiance_rushes(secondes)
    subprocess.run([
        FF, "-y", "-v", "error", "-i", n, "-i", a,
        "-filter_complex",
        f"[0:a]volume={part_nappe}[n];[1:a]volume={part_ambiance}[a];"
        f"[n][a]amix=inputs=2:normalize=0,"
        f"alimiter=limit=0.6,aresample=48000[out]",
        "-map", "[out]", "-ar", "48000", "-ac", "2", sortie,
    ], check=True)
    return sortie


if __name__ == "__main__":
    import sys
    d = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
    print(lit_sonore(d))
