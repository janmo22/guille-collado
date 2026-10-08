from pathlib import Path
import json,cv2,mediapipe as mp,numpy as np,subprocess
cv2.setNumThreads(1)
from concurrent.futures import ThreadPoolExecutor
import threading
local=threading.local()
P=Path(__file__).resolve().parents[2];S=P.parents[1]/'remotion-studio';V=S/'public-dia1-v12';C=S/'src/compositions/proyectos/2026-09-16-dia1-guille-collado'
plan=json.loads((C/'v12-plan.json').read_text());edit=json.loads((C/'v12-edit.json').read_text());used={f for s in edit['segments'] for f in range(s['source'],s['end'])}
(V/'person-masks').mkdir(exist_ok=True);(V/'hand-frames').mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(V/'g01-bridge.mp4'),'-vf','setpts=PTS/3,fps=30,scale=1080:1920','-frames:v','30','-q:v','2','-start_number','0',str(V/'hand-frames/%05d.jpg')],check=True)

frames=[]
for f in sorted(used):
 r=next((r for r in plan['resources'] if r['from']<=f<r['to']),None)
 if r and r['kind']!='hand':continue
 visible=any(b['from']<=f<b['to'] and any(w['at']<=f and w['layer']=='back' for w in b['words']) for b in plan['blocks'])
 if visible or 318<=f<381:frames.append(f)
def process(f):
 if (V/'person-masks'/f'{f:05}.png').exists():return f
 if not hasattr(local,'model'):local.model=mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0)
 hand=1490<=f<1520
 path=V/'hand-frames'/f'{f-1490:05}.jpg' if hand else V/'base-frames'/f'{f:05}.jpg'
 rgb=cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB)
 prob=local.model.process(cv2.resize(rgb,(540,960),interpolation=cv2.INTER_AREA)).segmentation_mask
 alpha=np.clip((prob-.32)/.38,0,1)
 alpha=cv2.resize(alpha,(1080,1920),interpolation=cv2.INTER_LINEAR)
 binary=(alpha>.5).astype(np.uint8);n,labels,stats,_=cv2.connectedComponentsWithStats(binary,8)
 if n>1:
  main=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);keep=cv2.dilate((labels==main).astype(np.uint8),np.ones((7,7),np.uint8));alpha*=keep
 if hand:
  # Close palm fills lens: person segmentation loses it, so add its skin matte.
  ycc=cv2.cvtColor(rgb,cv2.COLOR_RGB2YCrCb).astype(np.float32);hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV).astype(np.float32)
  skin=np.clip((ycc[:,:,1]-134)/10,0,1)*np.clip((139-ycc[:,:,2])/10,0,1)*np.clip((hsv[:,:,1]-18)/20,0,1)
  skin=cv2.morphologyEx(skin,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8));alpha=np.maximum(alpha,skin)
 alpha=cv2.GaussianBlur(alpha,(0,0),.65)
 # PNG carries white RGB and real alpha: compact, same source RGB reused by compositor.
 mask=np.full((1920,1080,4),255,np.uint8);mask[:,:,3]=(alpha*255).astype(np.uint8)
 cv2.imwrite(str(V/'person-masks'/f'{f:05}.png'),mask,[cv2.IMWRITE_PNG_COMPRESSION,3])
 return f
with ThreadPoolExecutor(max_workers=3) as pool:
 for i,f in enumerate(pool.map(process,frames)):
  if i%100==0:print(i,'/',len(frames),flush=True)
(C/'v12-mask-frames.json').write_text(json.dumps(frames));print('Máscaras listas',len(frames),flush=True)
