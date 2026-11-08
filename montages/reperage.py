"""Pour une liste de clips, trouve les 2 instants les plus nets et en fait
une planche contact. Sert a reperer des plans sans aller les regarder un par un.

Usage : python montages\\reperage.py sortie.jpg
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nettete

R = r"H:\eventys\Video\rush"
FF = r"H:\eventys\tools\bin\ffmpeg.exe"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_verif")

CANDIDATS = [
    ("IMG_4046", "Mariages"), ("IMG_6946", "Mariages"),
    ("IMG_6945", "Mise en place_"), ("IMG_7015", "Mise en place_"),
    ("IMG_6867", "Mise en place_"), ("IMG_6868", "Mise en place_"),
    ("IMG_9421", "Ramadan_"), ("IMG_9422", "Ramadan_"),
    ("IMG_9424", "Ramadan_"), ("IMG_9425", "Ramadan_"),
    ("IMG_9441", "Ramadan_"), ("IMG_9449", "Ramadan_"),
    ("IMG_9452", "Ramadan_"), ("IMG_9454", "Ramadan_"),
    ("IMG_9398", "Ramadan_"), ("IMG_9400", "Ramadan_"),
    ("IMG_3428", "Noël"), ("IMG_3438", "Noël"), ("IMG_3439", "Noël"),
]


def main(nom):
    os.makedirs(OUT, exist_ok=True)
    vignettes = []
    for stem, folder in CANDIDATS:
        prof = nettete.scan(stem, folder, 0.8)
        if not prof:
            continue
        for t, s in sorted(prof, key=lambda x: -x[1])[:2]:
            f = os.path.join(OUT, f"r_{stem}_{t}.jpg")
            subprocess.run([FF, "-y", "-v", "error", "-ss", str(t), "-i",
                            nettete.src(stem, folder)[0], "-frames:v", "1",
                            "-vf", "scale=230:-2", "-q:v", "3", f],
                           capture_output=True)
            if os.path.exists(f):
                vignettes.append((f"{stem}@{t} n={s}", f))
        print(stem, "ok", flush=True)

    C, T = 8, 230
    rows = (len(vignettes) + C - 1) // C
    Hc = max(Image.open(f).height for _, f in vignettes) + 16
    cv = Image.new("RGB", (C * T, rows * Hc), "white")
    d = ImageDraw.Draw(cv)
    for i, (lab, f) in enumerate(vignettes):
        x, y = (i % C) * T, (i // C) * Hc
        cv.paste(Image.open(f), (x, y + 16))
        d.text((x + 2, y + 3), lab, fill="red")
    p = os.path.join(OUT, nom)
    cv.save(p, quality=88)
    print(p)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "reperage.jpg")
