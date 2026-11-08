"""Cartographie un rush DANS LE CADRE FINAL 9:16, pas en paysage.

Pourquoi ce fichier existe : trois fois de suite, une fenetre de coupe a ete
choisie en regardant l'image source en paysage, puis le montage n'a garde
qu'une bande verticale centree — et le sujet annonce par la carte de prix
n'y etait pas. Le plan « 12 kits vaisselle » montrait un sapin.

Nos rushes sont filmes en paysage, la table est dans la MOITIE BASSE, et le
9:16 centre garde le haut de la piece. Il faut donc regarder le cadre reel,
et a plusieurs hauteurs d'ancrage, avant de choisir.

    python montages/reperage9x16.py <stem> <dossier> [pas_en_s]
"""
import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
sys.path.insert(0, ICI)

ANCRES = (0.25, 0.50, 0.80)     # haut de piece / centre / table


def carte(stem, dossier, pas=1.0, sortie=None):
    import build
    from PIL import Image, ImageDraw
    src = build.src(stem, dossier)
    dur = float(subprocess.run(
        [FF.replace("ffmpeg", "ffprobe"), "-v", "error", "-show_entries",
         "format=duration", "-of", "csv=p=0", src],
        capture_output=True, text=True).stdout.strip())

    tmp = os.path.join(ICI, "_check", "r916", stem)
    os.makedirs(tmp, exist_ok=True)
    chaine = "fps=1"
    if build.est_hdr(src):
        chaine = "fps=1," + build.TONEMAP

    vign, t = [], 0.4
    while t < dur - 0.1:
        for a in ANCRES:
            f = os.path.join(tmp, f"{t:05.1f}_{a:.2f}.jpg")
            subprocess.run([
                FF, "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", src,
                "-frames:v", "1",
                "-vf", chaine + (
                    f",scale=1080:1920:force_original_aspect_ratio=increase,"
                    f"crop=1080:1920:(in_w-out_w)/2:(in_h-out_h)*{a:.3f},"
                    f"scale=118:-1"),
                f], check=False)
            if os.path.exists(f):
                vign.append((t, a, f))
        t += pas

    cols = len(ANCRES)
    lignes = sorted({v[0] for v in vign})
    s = Image.new("RGB", (len(lignes) * 122, cols * 228), (238, 236, 232))
    d = ImageDraw.Draw(s)
    for t, a, f in vign:
        im = Image.open(f)
        x = lignes.index(t) * 122
        y = ANCRES.index(a) * 228
        s.paste(im, (x + 2, y))
        d.text((x + 3, y + 212), f"{t:.0f}s a{a:.2f}", fill=(20, 20, 20))
    out = sortie or os.path.join(ICI, "_check", f"r916_{stem}.jpg")
    s.save(out, quality=90)
    return out, len(vign)


if __name__ == "__main__":
    pas = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    print(carte(sys.argv[1], sys.argv[2], pas))
