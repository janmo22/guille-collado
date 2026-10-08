from pathlib import Path
import json,cv2,numpy as np
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
cv2.setNumThreads(1)
P=Path(__file__).resolve().parents[2];S=P.parents[1]/'remotion-studio';C=S/'src/compositions/proyectos/2026-09-16-dia1-guille-collado';V=S/'public-dia1-v12';(V/'precomposed').mkdir(exist_ok=True)
cache=json.loads((C/'v12-type-cache.json').read_text());maskframes=json.loads((C/'v12-mask-frames.json').read_text());frames=[f for f in maskframes if cache['back'][f] and not 318<=f<381 and not 1782<=f<1814]
@lru_cache(maxsize=10)
def typography(name):
 im=cv2.imread(str(V/'type-cache'/name),cv2.IMREAD_UNCHANGED).astype(np.float32);return im[:,:,:3],im[:,:,3:4]/255

def work(f):
 hand=1490<=f<1520;src=V/'hand-frames'/f'{f-1490:05}.jpg' if hand else V/'base-frames'/f'{f:05}.jpg'
 raw=cv2.imread(str(src));text,alpha=typography(cache['back'][f]);mask=cv2.imread(str(V/'person-masks'/f'{f:05}.png'),cv2.IMREAD_UNCHANGED)[:,:,3:4].astype(np.float32)/255
 a=alpha*(1-mask);im=np.clip(raw.astype(np.float32)*(1-a)+text*a,0,255).astype(np.uint8)
 cv2.imwrite(str(V/'precomposed'/f'{f:05}.jpg'),im,[cv2.IMWRITE_JPEG_QUALITY,98]);return f
with ThreadPoolExecutor(max_workers=3) as pool:
 for i,f in enumerate(pool.map(work,frames)):
  if i%150==0:print(i,'/',len(frames),flush=True)
(C/'v12-precomposed.json').write_text(json.dumps(frames));print('Precomposición terminada',len(frames),flush=True)
