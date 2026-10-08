"""Acabado angular a precisión flotante. Evita escalones del displacement SVG de 8 bits."""
from pathlib import Path
import argparse,json,subprocess
import cv2,numpy as np
from concurrent.futures import ThreadPoolExecutor
from collections import deque
cv2.setNumThreads(1)
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('output');ap.add_argument('--start',type=int,default=0);ap.add_argument('--proof',action='store_true');ap.add_argument('--preview',action='store_true');ap.add_argument('--plan',required=True);ap.add_argument('--edit',required=True);args=ap.parse_args()
plan=json.loads(Path(args.plan).read_text());edit=json.loads(Path(args.edit).read_text());cap=cv2.VideoCapture(args.source)
w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
y,x=np.mgrid[:h,:w].astype(np.float32);cx=w*.5;cy=h*.49
r2=((x-cx)**2+(y-cy)**2)/(cx**2+max(cy,h-cy)**2);k=(1+.16*r2)/1.16/1.025
mx=cx+(x-cx)*k;my=cy+(y-cy)*k
# Pantallas: abombamiento menor, sin ampliación añadida.
ks=(1+.105*r2)/1.105;sx=cx+(x-cx)*ks;sy=cy+(y-cy)*ks
# Se evalúa una sola vez por píxel. Interpolación cúbica, sin mapa cuantizado.
tmp=Path(args.output).with_suffix('.lens-silent.mp4');enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-crf','21' if args.preview else '16','-preset','veryfast','-threads','2','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(tmp)],stdin=subprocess.PIPE)
edge=np.clip((np.abs(x-cx)/cx-.54)/.46,0,1)**1.65
def process(f,im):
 outf=f+args.start;segment=next(s for s in edit['segments'] if s['from']<=outf<s['from']+s['duration']);absf=segment['source']+outf-segment['from'];resource=next((r for r in plan['resources'] if r['from']<=absf<r['to']),None)
 hero=args.proof or not resource or resource['kind']=='hand'
 screen=resource and not hero
 if hero:im=cv2.remap(im,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
 elif screen:
  join=np.clip((absf-resource['from']-73)/18,0,1) if resource['kind']=='bridge' else 0
  im=cv2.remap(im,sx*(1-join)+mx*join if join else sx,sy*(1-join)+my*join if join else sy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
  # Edge softness follows horizontal optical distance, leaving middle 54% sharp.
  age=absf-resource['from'];moving=max(0,1-age/15)
  blurred=cv2.GaussianBlur(im,(0,0),w/1080*(7+moving*6))
  alpha=(edge*(.84+moving*.12)*(1-join))[:,:,None]
  im=np.clip(im*(1-alpha)+blurred*alpha,0,255).astype(np.uint8)
 return im
last=-1;pending=deque()
with ThreadPoolExecutor(max_workers=3) as pool:
 for f in range(n):
  ok,im=cap.read()
  if not ok:raise RuntimeError(f'No se pudo decodificar {f}/{n}')
  pending.append(pool.submit(process,f,im))
  if len(pending)>=6:enc.stdin.write(pending.popleft().result().tobytes())
  progress=f*10//n
  if progress!=last:print('lente',progress*10,'%',flush=True);last=progress
 while pending:enc.stdin.write(pending.popleft().result().tobytes())
enc.stdin.close();assert enc.wait()==0;cap.release()
subprocess.run(['ffmpeg','-v','error','-y','-i',str(tmp),'-i',args.source,'-map','0:v:0','-map','1:a?','-c','copy','-movflags','+faststart',args.output],check=True);tmp.unlink();print('Lente aplicada a',args.output,flush=True)
