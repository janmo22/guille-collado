#!/usr/bin/env python3
"""Verifica archivo completo; no sustituye revisión de estilo, palabra y movimiento."""
import argparse,json,subprocess,hashlib
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('video');ap.add_argument('--output',required=True);a=ap.parse_args()
    video=Path(a.video).resolve(strict=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
    v=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next((s for s in probe['streams'] if s['codec_type']=='audio'),None)
    if audio is None:raise ValueError('La entrega hablada no contiene audio')
    r=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-vf','blackdetect=d=0.12:pix_th=0.08:pic_th=0.98','-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr[-3000:])
    stats=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0]
    black=[line for line in r.stderr.splitlines() if 'black_start:' in line]
    duration=float(v.get('duration',probe['format']['duration']));audio_duration=float(audio.get('duration',probe['format']['duration']))
    issues=[]
    if abs(duration-audio_duration)>.05:issues.append('Duraciones AV difieren más de50ms')
    if float(stats['input_tp'])>-1:issues.append('True peak del archivo supera−1dBTP')
    if not -16<=float(stats['input_i'])<=-12:issues.append('Revisar sonoridad frente al objetivo≈−14LUFS')
    if black:issues.append('Revisar intervalos negros: pueden ser intencionados')
    with video.open('rb') as handle:sha=hashlib.file_digest(handle,'sha256').hexdigest()
    report={'file':str(video),'sha256':sha,'decode_exit':0,'video':v,'audio':audio,
            'loudness_measured':{k:stats[k] for k in ['input_i','input_tp','input_lra']},
            'black_intervals':black,'review':issues,'artistic_review':'required separately'}
    dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'duration':duration,'review':issues,'report':str(dest)},ensure_ascii=False))

if __name__=='__main__':main()
