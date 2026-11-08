"""Transforme une story en image fixe en story VIDEO sonorisee.

Une story publiee en image ne peut pas porter de son : l'API n'accepte
aucune piste audio sur une image. Pour avoir de la musique, la story doit
etre une video — meme si elle ne montre qu'une image.

On en profite pour animer legerement : un travelling avant tres lent evite
l'effet « capture d'ecran immobile » qui fait passer le doigt.
"""
import os
import subprocess

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
W, H, FPS = 1080, 1920, 30


def rendre(image, sortie, duree=6.0, lit=None, zoom=0.035,
           debut_son=0.0):
    """Image fixe -> story video sonorisee, avec un leger travelling."""
    frames = max(int(duree * FPS), 1)
    k = 1.0 + zoom
    iw = int(W * 2 * (k + 0.1)) // 2 * 2
    ih = int(H * 2 * (k + 0.1)) // 2 * 2
    z = f"1.0+{zoom:.4f}*min(on/{frames},1)"
    # `zoompan` avance par PIXELS ENTIERS : sur un travelling lent, ca se
    # voit comme un tremblement. On calcule donc le mouvement au double de
    # la definition finale, puis on reduit — le saut devient un demi-pixel,
    # invisible a l'oeil.
    vf = (f"scale={iw}:{ih}:force_original_aspect_ratio=increase:flags=lanczos,"
          f"crop={iw}:{ih}:(in_w-out_w)/2:(in_h-out_h)/2,setsar=1,"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
          f"d=1:s={W * 2}x{H * 2}:fps={FPS},"
          f"scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p,"
          # Une source PNG ne porte aucune information de colorimetrie :
          # sans `setparams`, les drapeaux -colorspace/-color_trc plus bas
          # ne sont pas ecrits et le fichier sort en « unknown ». Releve
          # par le relecteur le 31/10 sur les deux cartes fabriquees,
          # alors que les clips de rush, eux, heritent de leur source.
          f"setparams=color_primaries=bt709:color_trc=bt709:"
          f"colorspace=bt709:range=tv")

    cmd = [FF, "-y", "-v", "error",
           "-loop", "1", "-framerate", str(FPS), "-t", f"{duree:.2f}", "-i", image]
    if lit:
        cmd += ["-ss", f"{debut_son:.2f}", "-t", f"{duree:.2f}", "-i", lit]

    cmd += ["-vf", vf]
    if lit:
        cmd += ["-af", f"afade=t=in:st=0:d=0.6,"
                       f"afade=t=out:st={max(duree-0.8,0):.2f}:d=0.8,"
                       f"volume=0.9,aresample=48000",
                "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-shortest"]
    # Instagram a refuse (erreur 2207077) une premiere version a tres bas
    # debit, faite a partir d'une image fixe : peu de mouvement = presque
    # pas de donnees. On impose donc un debit plancher et une image cle
    # toutes les deux secondes, comme dans une video filmee normale.
    # Pas de `crf` ici : avec libx264 il l'emporte sur le debit cible, et
    # une image fixe compressee a crf=20 ne pesait que 1 Mb/s.
    # Debit releve le 28/10 avec `-b:v 5M` : 4,15 Mb/s reels. libx264
    # n'atteint pas sa cible sur une image presque immobile, il faut
    # viser au-dessus et surtout imposer un `minrate` superieur au
    # plancher de 5 Mb/s, pas egal.
    cmd += ["-c:v", "libx264", "-preset", "medium",
            "-b:v", "7M", "-minrate", "5500k", "-maxrate", "9M",
            "-bufsize", "14M",
            "-g", str(FPS * 2), "-keyint_min", str(FPS),
            "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
            "-colorspace", "bt709", "-color_primaries", "bt709",
            "-color_trc", "bt709", "-color_range", "tv",
            "-movflags", "+faststart", sortie]
    subprocess.run(cmd, check=True)
    return sortie


def serie(dossier_images, dossier_sortie, lit=None, duree=6.0):
    """Convertit tout un dossier d'images en stories video sonorisees.

    Chaque story pioche dans une portion DIFFERENTE du lit sonore : sinon
    trois stories d'affilee rejouent les memes quatre secondes, et ca
    s'entend tout de suite.
    """
    os.makedirs(dossier_sortie, exist_ok=True)
    images = sorted(f for f in os.listdir(dossier_images)
                    if f.lower().endswith((".png", ".jpg")))
    sorties = []
    for i, img in enumerate(images):
        out = os.path.join(dossier_sortie,
                           os.path.splitext(img)[0] + ".mp4")
        rendre(os.path.join(dossier_images, img), out, duree=duree,
               lit=lit, debut_son=i * (duree + 1.5))
        sorties.append(out)
    return sorties
