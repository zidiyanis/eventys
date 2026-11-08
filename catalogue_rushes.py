"""Extrait une planche d'images clés par vidéo et écrit index.json.

Usage : python catalogue_rushes.py "H:\\eventys\\Video\\rush" [dossier1 dossier2 ...]
Sans noms de dossiers, traite tout. Reprend là où il s'est arrêté.
Ne modifie jamais les originaux : tout est écrit dans <racine>\\_catalogue.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

MAX_FRAMES = 6
FRAME_WIDTH = 320
COLS = 3
TOOLS = Path(__file__).parent / "tools" / "bin"
FFMPEG = str(TOOLS / "ffmpeg.exe")
FFPROBE = str(TOOLS / "ffprobe.exe")
VIDEO_EXT = {".mov", ".mp4", ".m4v"}
PHOTO_EXT = {".heic", ".jpg", ".jpeg", ".png"}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def probe(path):
    r = run([FFPROBE, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not v:
        return None
    w, h = v.get("width"), v.get("height")
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = abs(int(sd["rotation"]))
    rot = rot or abs(int(v.get("tags", {}).get("rotate", 0) or 0))
    if rot in (90, 270):
        w, h = h, w
    fmt = data.get("format", {})
    return {
        "duration_s": round(float(fmt.get("duration") or v.get("duration") or 0), 1),
        "width": w,
        "height": h,
        "orientation": "vertical" if h and w and h > w else "horizontal",
        "date": (fmt.get("tags", {}) or {}).get("creation_time") or (fmt.get("tags", {}) or {}).get("com.apple.quicktime.creationdate"),
    }


def make_sheet(path, info, out_dir):
    dur = info["duration_s"]
    n = 1 if dur < 2 else min(MAX_FRAMES, max(2, int(dur // 3) + 1))
    times = [round(dur * (i + 0.5) / n, 1) for i in range(n)]
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for i, t in enumerate(times):
        f = out_dir / f"f{i}.jpg"
        run([FFMPEG, "-y", "-v", "error", "-ss", str(t), "-i", str(path), "-frames:v", "1",
             "-vf", f"scale={FRAME_WIDTH}:-2", "-q:v", "4", str(f)])
        if f.exists():
            frames.append(f)
    if not frames:
        return None, times
    rows = (len(frames) + COLS - 1) // COLS
    sheet = out_dir / "planche.jpg"
    run([FFMPEG, "-y", "-v", "error", "-framerate", "1", "-i", str(out_dir / "f%d.jpg"),
         "-vf", f"tile={min(COLS, len(frames))}x{rows}:padding=4:color=black", "-frames:v", "1",
         "-q:v", "4", str(sheet)])
    for f in frames:
        f.unlink(missing_ok=True)
    return (str(sheet) if sheet.exists() else None), times


def make_photo_thumb(path, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    thumb = out_dir / "photo.jpg"
    if path.suffix.lower() == ".heic":
        try:
            from PIL import Image, ImageOps
            import pillow_heif
            pillow_heif.register_heif_opener()
            im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
            im.thumbnail((FRAME_WIDTH * 2, FRAME_WIDTH * 4))
            im.save(thumb, quality=80)
        except Exception:
            return None
        return str(thumb)
    run([FFMPEG, "-y", "-v", "error", "-i", str(path), "-frames:v", "1",
         "-vf", f"scale={FRAME_WIDTH * 2}:-2", "-q:v", "4", str(thumb)])
    return str(thumb) if thumb.exists() else None


def main():
    root = Path(sys.argv[1]).resolve()
    only = set(sys.argv[2:])
    cat = root / "_catalogue"
    cat.mkdir(exist_ok=True)
    index_path = cat / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    files = [p for p in sorted(root.rglob("*")) if p.is_file() and "_catalogue" not in p.parts
             and p.suffix.lower() in VIDEO_EXT | PHOTO_EXT]
    if only:
        files = [p for p in files if p.relative_to(root).parts[0] in only]
    total = len(files)
    for n, p in enumerate(files, 1):
        rel = str(p.relative_to(root))
        if rel in index and index[rel].get("sheet") is not None:
            continue
        key = f"{hashlib.md5(rel.encode('utf-8')).hexdigest()[:8]}_{p.stem[:30]}".replace(" ", "_")
        out_dir = cat / "sheets" / key
        entry = {"file": rel, "folder": p.relative_to(root).parts[0], "size_mo": round(p.stat().st_size / 1e6, 1)}
        if p.suffix.lower() in VIDEO_EXT:
            info = probe(p)
            if info:
                entry.update(info)
                entry["sheet"], entry["frame_times_s"] = make_sheet(p, info, out_dir)
            else:
                entry["sheet"] = None
                entry["error"] = "illisible"
        else:
            entry["kind"] = "photo"
            entry["sheet"] = make_photo_thumb(p, out_dir)
        index[rel] = entry
        if n % 10 == 0 or n == total:
            index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{n}/{total}", flush=True)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print("terminé", len(index), "entrées")


if __name__ == "__main__":
    main()
