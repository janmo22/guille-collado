from pathlib import Path
import cv2,numpy as np,subprocess,json
P=Path(__file__).resolve().parents[2];V=P.parents[1]/'remotion-studio/public-dia1-v12';B=P/'05-brolls/v12'
for name,a,b in [('inicio',95,147),('genial',1034,1041)]:
 cap=cv2.VideoCapture(str(B/('genial-quad-seedance.mp4' if name=='genial' else f'{name}-seedance.mp4')));frames=[]
 while True:
  ok,im=cap.read()
  if not ok:break
  frames.append(cv2.resize(im,(1080,1920),interpolation=cv2.INTER_CUBIC))
 cap.release();dest=V/f'{name}-ia-v12.mp4';dest.unlink(missing_ok=True)
 enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-crf','16','-preset','veryfast','-pix_fmt','yuv420p',str(dest)],stdin=subprocess.PIPE)
 # Spend most of the 16-frame window on actual travel, without long generated holds.
 positions=np.interp(np.linspace(0,1,16),[0,.15,.76,1],[0,.18,.70,1])*(len(frames)-1)
 for i,p in enumerate(positions):
  frame=frames[round(p)]
  if i==0:frame=cv2.imread(str(B/'genial-quad-start.jpg' if name=='genial' else V/'base-frames'/f'{a:05}.jpg'))
  if i==15:frame=cv2.imread(str(B/'genial-quad-end.jpg' if name=='genial' else V/'base-frames'/f'{b:05}.jpg'))
  enc.stdin.write(frame.tobytes())
 enc.stdin.close();assert enc.wait()==0;print(name,flush=True)
