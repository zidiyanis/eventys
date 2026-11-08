"""Mesure la nettete image par image d'un clip et sort les meilleurs passages.

Score = variance du laplacien sur l'image en niveaux de gris (plus haut = plus net).
Sert a choisir ou couper, au lieu de juger a l'oeil sur une vignette.

Usage : python montages\\nettete.py IMG_4045 Mariages [pas_en_s]
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

R = r"H:\eventys\Video\rush"
FF = r"H:\eventys\tools\bin\ffmpeg.exe"
TMP = os.path.join(r"H:\eventys\montages", "_net")

index = json.load(open(os.path.join(R, "_catalogue", "index.json"), encoding="utf-8"))


def src(stem, folder):
    for k, v in index.items():
        name = k.split("\\")[-1]
        if name.startswith(stem) and "(1)" not in name and v["folder"] == folder:
            return os.path.join(R, k), v
    raise SystemExit("introuvable : " + stem)


def score(path):
    a = np.asarray(Image.open(path).convert("L"), dtype=np.float64)
    lap = (-4 * a[1:-1, 1:-1] + a[:-2, 1:-1] + a[2:, 1:-1]
           + a[1:-1, :-2] + a[1:-1, 2:])
    return float(lap.var())


def scan(stem, folder, step=0.4):
    path, meta = src(stem, folder)
    os.makedirs(TMP, exist_ok=True)
    out = []
    t = 0.2
    while t < meta["duration_s"] - 0.2:
        f = os.path.join(TMP, "f.jpg")
        subprocess.run([FF, "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", path,
                        "-frames:v", "1", "-vf", "scale=540:-2", "-q:v", "2", f],
                       capture_output=True)
        if os.path.exists(f):
            out.append((round(t, 1), round(score(f))))
        t += step
    return out


if __name__ == "__main__":
    stem, folder = sys.argv[1], sys.argv[2]
    step = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
    res = scan(stem, folder, step)
    med = sorted(s for _, s in res)[len(res) // 2]
    print(f"{stem} : mediane {med}")
    print("  meilleurs :", sorted(res, key=lambda x: -x[1])[:8])
    print("  profil    :", res)
