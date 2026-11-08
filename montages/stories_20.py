# -*- coding: utf-8 -*-
"""Stories du 4 novembre : beige / bordeaux / beige. Aucun rush du Reel."""
import os
import sys
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import story_clip as C  # noqa: E402

LIT = os.path.join(os.path.dirname(ICI), "assets", "son", "lit_stories.wav")
VLOG, RAM = "Contenue Vlog_", "Ramadan_"
SORTIE = os.path.join(ICI, "_attente_2026-11-04", "stories")
os.makedirs(SORTIE, exist_ok=True)

if __name__ == "__main__":
    C.clip("IMG_1055", VLOG, 0.10, 1.60, "À LA MAIN", "Chaise Napoléon · 3 €",
           os.path.join(SORTIE, "1_a_la_main.mp4"), teinte="beige",
           lit=LIT, debut_son=0.0, va_et_vient=True)
    C.clip("IMG_1054", VLOG, 0.00, 1.60, "ON PORTE", "Livraison en Île-de-France",
           os.path.join(SORTIE, "2_on_porte.mp4"), teinte="bordeaux",
           lit=LIT, debut_son=6.0, va_et_vient=True)
    C.clip("IMG_9453", RAM, 2.00, 3.40, "LE COUVERT", "Table ronde · kit 2 €",
           os.path.join(SORTIE, "3_le_couvert.mp4"), teinte="beige",
           lit=LIT, debut_son=12.0, va_et_vient=True)
    import subprocess
    FF = os.path.join(os.path.dirname(ICI), "tools", "bin", "ffmpeg.exe")
    for f in sorted(os.listdir(SORTIE)):
        if not f.endswith(".mp4") or f.startswith("_"):
            continue
        p = os.path.join(SORTIE, f)
        tmp = os.path.join(SORTIE, "_" + f)
        # le lit sonore sort a -34/-47 LUFS : on le ramene a ~-15 LUFS
        subprocess.run([FF, "-y", "-v", "error", "-i", p, "-map", "0:v",
                        "-map", "0:a", "-c:v", "copy",
                        "-af", "loudnorm=I=-15:TP=-1.5:LRA=7,aresample=48000",
                        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                        "-movflags", "+faststart", tmp], check=True)
        os.replace(tmp, p)
    print("ok")
