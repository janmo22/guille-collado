#!/usr/bin/env python3
"""Conforma una selección editorial de tomas independientes, sin separar voz/labios.

Uso: guille_conform.py edl.json --outdir directorio [--render]
Contrato y selección: estilos/guille-collado/montaje-limpio.md.
No elige interpretaciones ni certifica semántica o calidad de sonido.
"""
import argparse
import json
import math
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text())


def probe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-show_streams",
        "-show_format", "-of", "json", str(path)]))


def conform(doc, base):
    fps = doc["fps"]
    require(type(fps) is int and fps in (24, 25, 30, 50, 60), "fps entero: 24/25/30/50/60")
    units = doc["script_units"]
    require(units and len({u["id"] for u in units}) == len(units), "Unidades vacías o IDs duplicados")
    rank = {u["id"]: i for i, u in enumerate(units)}
    require(all(u.get("text", "").strip() for u in units), "Unidad sin texto de guion")
    require(doc["clips"], "No hay clips seleccionados")
    takes, canvas = {}, None
    for take, data in doc["takes"].items():
        media = (base / data["media"]).resolve()
        transcript = (base / data["words"]).resolve()
        require(media.is_file() and transcript.is_file(), f"{take}: falta media o transcript")
        info = probe(media)
        video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
        audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
        require(video and audio, f"{take}: hacen falta vídeo y audio")
        require(Fraction(video["avg_frame_rate"]) == fps and Fraction(video["r_frame_rate"]) == fps,
                f"{take}: normalizar a CFR {fps} antes de transcribir y seleccionar")
        require(abs(float(video.get("start_time", 0))) < 1 / fps and
                abs(float(audio.get("start_time", 0))) < 1 / fps, f"{take}: normalizar origen de PTS")
        dims = [video["width"], video["height"]]
        require(canvas is None or canvas == dims, "Normalizar las tomas al mismo lienzo sin deformar")
        canvas = dims
        count = int(video.get("nb_read_frames") or video["nb_frames"])
        words = read_json(transcript)["words"]
        previous = -1
        for i, w in enumerate(words):
            a, b = w["start"], w["end"]
            require(math.isfinite(a) and math.isfinite(b) and 0 <= a < b <= count / fps + 1 / fps,
                    f"{take}: timestamp inválido en palabra {i}")
            require(a >= previous, f"{take}: palabras fuera de orden")
            require(isinstance(w["word"], str) and w["word"].strip(), f"{take}: palabra vacía")
            previous = a
        takes[take] = {"media": str(media), "words_path": str(transcript),
                       "words": words, "frames": count}
    timeline, final_words, seen_units, ranges = [], [], [], {}
    cursor = 0
    for i, c in enumerate(doc["clips"]):
        label = f"clip {i + 1}"
        take = c["take"]
        require(take in takes, f"{label}: toma desconocida")
        a, b = c["in_frame"], c["out_frame"]
        require(type(a) is int and type(b) is int and 0 <= a < b <= takes[take]["frames"],
                f"{label}: intervalo inválido; out_frame es exclusivo")
        require(c.get("reason", "").strip(), f"{label}: falta motivo editorial")
        require(c["unit_ids"] and all(u in rank for u in c["unit_ids"]), f"{label}: unidades desconocidas")
        seen_units.extend(c["unit_ids"])
        require(all(b <= x or a >= y for x, y in ranges.get(take, [])),
                f"{label}: reutiliza fotogramas fuente; posible repetición accidental")
        ranges.setdefault(take, []).append((a, b))
        words = takes[take]["words"]
        ids = c["word_indices"]
        require(ids and all(type(n) is int and 0 <= n < len(words) for n in ids), f"{label}: índices inválidos")
        require(ids == sorted(set(ids)), f"{label}: índices repetidos o desordenados")
        intersecting = [n for n, w in enumerate(words)
                        if w["end"] > a / fps + 1e-7 and w["start"] < b / fps - 1e-7]
        require(ids == intersecting, f"{label}: el rango contiene palabras no declaradas o faltan palabras")
        for n in ids:
            w = words[n]
            require(w["start"] >= a / fps - 1e-7 and w["end"] <= b / fps + 1e-7,
                    f"{label}: corta la palabra {n} ({w['word']}); revisar audio y límites")
            final_words.append({"word": w["word"],
                                "start": round((cursor - a) / fps + w["start"], 6),
                                "end": round((cursor - a) / fps + w["end"], 6),
                                "take": take, "source_word_index": n, "clip_index": i})
        timeline.append({**c, "media": takes[take]["media"], "from_frame": cursor,
                         "duration_frames": b - a, "until_frame": cursor + b - a})
        cursor += b - a
    require(set(seen_units) == set(rank), "Faltan unidades del guion; no ocultar omisiones")
    require(all(rank[a] <= rank[b] for a, b in zip(seen_units, seen_units[1:])),
            "Unidades repetidas fuera de orden o guion desordenado")
    return {"fps": fps, "canvas": canvas, "duration_frames": cursor,
            "clips": timeline, "script_units": units,
            "status": "estructura_validada_pendiente_QA_audiovisual"}, {
                "text": " ".join(w["word"] for w in final_words), "words": final_words}


def render(timeline, out):
    """Cortes AV del mismo archivo, duraciones enteras y PCM intermedio sin deriva AAC."""
    fps = timeline["fps"]
    with tempfile.TemporaryDirectory(prefix="guille-conform-") as temp:
        temp = Path(temp)
        parts = []
        for i, c in enumerate(timeline["clips"]):
            path = temp / f"clip-{i:04}.mov"
            a, b = c["in_frame"], c["out_frame"]
            samples = round((b - a) * 48000 / fps)
            # Microfades dentro del clip: no solapan ni acortan el timeline.
            dur = (b - a) / fps
            fade = min(0.005, dur / 4)
            vf = f"trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,setsar=1,format=yuv420p"
            af = (f"aresample=48000,atrim=start_sample={round(a * 48000 / fps)}:"
                  f"end_sample={round(b * 48000 / fps)},asetpts=PTS-STARTPTS,"
                  f"apad=whole_len={samples},atrim=end_sample={samples},"
                  f"afade=t=in:d={fade},afade=t=out:st={dur - fade}:d={fade}")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", c["media"],
                            "-map", "0:v:0", "-map", "0:a:0", "-vf", vf, "-af", af,
                            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", str(fps),
                            "-video_track_timescale", "60000", "-c:a", "pcm_s16le", "-ac", "2",
                            str(path)], check=True)
            parts.append(f"file '{path.name}'")
        listing = temp / "concat.txt"
        listing.write_text("\n".join(parts) + "\n")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                        "-i", str(listing), "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                        "-movflags", "+faststart", str(out / "montaje-base.mp4")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                        "-i", str(listing), "-vn", "-c:a", "pcm_s24le",
                        str(out / "dialogo.wav")], check=True)
    result = probe(out / "montaje-base.mp4")
    video = next(s for s in result["streams"] if s["codec_type"] == "video")
    require(int(video["nb_read_frames"]) == timeline["duration_frames"], "Render con número de frames incorrecto")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("edl", type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--render", action="store_true")
    args = ap.parse_args()
    try:
        timeline, words = conform(read_json(args.edl), args.edl.resolve().parent)
        args.outdir.mkdir(parents=True, exist_ok=True)
        for name, data in (("timeline.json", timeline), ("master.words.json", words)):
            (args.outdir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        if args.render:
            render(timeline, args.outdir)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as e:
        ap.exit(1, f"ERROR de conformado: {e}\n")
    print(f"{len(timeline['clips'])} clips · {timeline['duration_frames']} frames · {len(words['words'])} palabras")
    print("Selección semántica, costuras, interpretación y sincronía labial requieren revisión audiovisual.")


if __name__ == "__main__":
    main()
