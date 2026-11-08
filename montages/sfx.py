"""Place des bruitages sur l'audio d'une video DEJA montee et sonorisee.

    import sfx
    sfx.ajoute("in.mp4", [("pop_etiquette", 0.03, -14), ("ding_total", 11.7, -10)], "out.mp4")

Chaque evenement = (nom du son dans assets/son/sfx, instant en secondes, PIC voulu en dBFS).
Les sons ElevenLabs sortent a des niveaux tres differents (ding_total culmine a
-19,8 dB, oups a -0,1 dB) : on mesure le pic de chaque son et on le ramene au
pic demandé. Pour comparaison, la voix culmine vers -3 dB : un pic de -10 dB
se sent sans couvrir la parole.
La video n'est PAS reencodee (`-c:v copy`) : seule la piste audio est refaite,
les bruitages sont ajoutes SOUS la voix (gains negatifs) et le niveau global
est ramene a celui d'origine pour rester dans la plage du controle (-16 a -12 LUFS).

Regles apprises a l'ecoute :
  - jamais de bruitage sur le tout dernier instant : la video boucle, un son
    qui coupe net ou qui sonne a la derniere image se repete a chaque boucle ;
  - un bruitage tombe sur un CHANGEMENT d'image (etiquette, coupe, geste),
    jamais au milieu d'une phrase sans raison ;
  - pas plus d'un son par seconde environ, sinon ca fait du bruit, pas du rythme.
"""
import os
import subprocess

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
FF = os.path.join(RACINE, "tools", "bin", "ffmpeg.exe")
BANQUE = os.path.join(RACINE, "assets", "son", "sfx")


_PICS = {}


def pic(nom):
    """Pic du son en dBFS (mesure ffmpeg `volumedetect`, mise en cache)."""
    if nom not in _PICS:
        f = os.path.join(BANQUE, nom + ".mp3")
        r = subprocess.run([FF, "-v", "info", "-i", f, "-af", "volumedetect",
                            "-f", "null", "-"], capture_output=True, text=True)
        for ligne in r.stderr.splitlines():
            if "max_volume" in ligne:
                _PICS[nom] = float(ligne.split("max_volume:")[1].split("dB")[0])
                break
        else:
            raise SystemExit(f"pic introuvable pour {nom}")
    return _PICS[nom]


def ajoute(video, evenements, sortie):
    entrees = ["-i", video]
    filtres = []
    etiquettes = ["[0:a]"]
    for i, (nom, t, pic_voulu) in enumerate(evenements, start=1):
        gain = pic_voulu - pic(nom)
        f = os.path.join(BANQUE, nom + ".mp3")
        if not os.path.exists(f):
            raise SystemExit(f"bruitage introuvable : {f}")
        entrees += ["-i", f]
        ms = int(round(t * 1000))
        filtres.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                       f"volume={gain:.2f}dB,adelay={ms}|{ms}[s{i}]")
        etiquettes.append(f"[s{i}]")
    n = len(etiquettes)
    filtres.append("".join(etiquettes) +
                   f"amix=inputs={n}:normalize=0:duration=first:dropout_transition=0[m]")
    cmd = [FF, "-y", "-v", "error", *entrees,
           "-filter_complex", ";".join(filtres),
           "-map", "0:v", "-map", "[m]", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", sortie]
    subprocess.run(cmd, check=True)
    return sortie


def evenements_standard(durees, etiquettes, total=None, cta=None, boucle=None,
                        ouverture_box=True, extras=None):
    """Bruitages places comme dans l'essai valide par Yanis le 2026-11-04.

    durees     : duree de chaque plan (secondes), dans l'ordre
    etiquettes : liste de booleens, un plan porte-t-il une etiquette de prix ?
    total      : index du plan « TOTAL » (ding au lieu du pop), ou None
    cta        : index du plan de l'appel final (pop double), ou None
    boucle     : index du plan de boucle : AUCUN son dessus ni juste avant
    extras     : {index_plan: [(son, decalage_s, pic_dBFS), ...]}
    """
    debuts, t = [], 0.0
    for d in durees:
        debuts.append(t)
        t += d
    ev = []
    if ouverture_box:
        ev.append(("rideau_box", 0.15, -16))
    for i, deb in enumerate(debuts):
        if boucle is not None and i >= boucle:
            break
        if i > 0:
            ev.append(("whoosh_transition", max(deb - 0.12, 0.0), -16))
        if i == total:
            ev.append(("ding_total", deb + 0.03, -8))
        elif etiquettes[i]:
            ev.append(("pop_etiquette", deb + 0.04, -10))
        if i == cta:
            ev.append(("pop_double", deb + 0.05, -10))
        for son, dec, pic_ in (extras or {}).get(i, []):
            ev.append((son, deb + dec, pic_))
    return sorted(ev, key=lambda e: e[1])
