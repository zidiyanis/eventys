"""Planche de triage : une image par rush, DEJA recadree en 9:16.

    python montages/triage.py <dossier> <stem1> <stem2> ...
    python montages/triage.py <dossier> --tous          (tous les .MOV/.mp4)

Complement de `reperage9x16.py`, qui cartographie UN rush seconde par
seconde. Ici on fait l'inverse : une seule image par rush, mais vingt rushes
sur la meme planche, pour reponder a la question « lesquels de ces vingt
clips montrent mon sujet ? » avant d'aller regarder les trois retenus en
detail.

L'image est prise a 45 % de la duree (le debut est souvent un mouvement de
prise en main) et recadree au centre, parce que c'est ce que le montage fera
par defaut. Un clip ecarte ici peut encore etre bon a une autre hauteur
d'ancrage : la planche sert a trier, pas a juger.
"""
import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
FP = os.path.join(RACINE, "tools", "bin", "ffprobe.exe")
sys.path.insert(0, ICI)

VIGN_L, VIGN_H = 216, 384       # 1080x1920 divise par 5
COLS = 6


def planche(dossier, stems, sortie=None, part=0.45):
    import build
    from PIL import Image, ImageDraw
    tmp = os.path.join(ICI, "_check", "triage")
    os.makedirs(tmp, exist_ok=True)

    vignettes = []
    for stem in stems:
        try:
            src = build.src(stem, dossier)
        except SystemExit:
            print(f"  {stem} introuvable")
            continue
        dur = float(subprocess.run(
            [FP, "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", src], capture_output=True,
            text=True).stdout.strip() or 0)
        if dur <= 0:
            continue
        chaine = ""
        if build.est_hdr(src):
            chaine = build.TONEMAP + ","
        chaine += (f"scale={VIGN_L}:{VIGN_H}:force_original_aspect_ratio="
                   f"increase,crop={VIGN_L}:{VIGN_H}")
        p = os.path.join(tmp, f"{stem}.jpg")
        subprocess.run([FF, "-y", "-v", "error", "-ss", f"{dur*part:.2f}",
                        "-i", src, "-frames:v", "1", "-vf", chaine, p],
                       check=False)
        if os.path.exists(p):
            vignettes.append((stem, dur, p))
        print(f"  {stem} ({dur:.1f}s)", flush=True)

    if not vignettes:
        raise SystemExit("aucune vignette")
    lignes = (len(vignettes) + COLS - 1) // COLS
    img = Image.new("RGB", (COLS * (VIGN_L + 8), lignes * (VIGN_H + 30)),
                    (22, 22, 24))
    d = ImageDraw.Draw(img)
    for i, (stem, dur, p) in enumerate(vignettes):
        x = (i % COLS) * (VIGN_L + 8) + 4
        y = (i // COLS) * (VIGN_H + 30) + 4
        img.paste(Image.open(p), (x, y))
        d.text((x + 2, y + VIGN_H + 6), f"{stem}  {dur:.1f}s",
               fill=(235, 228, 214))
    sortie = sortie or os.path.join(ICI, "_check", "triage.jpg")
    img.save(sortie, quality=88)
    print(sortie)
    return sortie


if __name__ == "__main__":
    dossier = sys.argv[1]
    if "--tous" in sys.argv:
        d = os.path.join(RACINE, "Video", "rush", dossier)
        stems = sorted({os.path.splitext(f)[0] for f in os.listdir(d)
                        if f.lower().endswith((".mov", ".mp4"))
                        and "(1)" not in f})
    else:
        stems = sys.argv[2:]
    planche(dossier, stems)
