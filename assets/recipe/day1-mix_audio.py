"""Mezcla v12 en reloj de entrega: voz real limpia, música desde 0 y cues visuales."""
from pathlib import Path
import json,subprocess,math
from functools import lru_cache
import numpy as np
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parents[2];S=P.parents[1]/'remotion-studio';O=P/'06-audio/v12';V=S/'public-dia1-v12';SR=48000;FPS=30
edit=json.loads((P/'04-plan-director/revision-v12/edit.json').read_text());plan=json.loads((P/'04-plan-director/plan-v12.json').read_text());N=edit['duration']*1600

@lru_cache(maxsize=24)
def read(path):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar',str(SR),'-ac','2','-f','f32le','-']),np.float32).reshape(-1,2).copy()
def write(path,a):
 subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s24le',str(path)],input=a.astype(np.float32).tobytes(),check=True)
def mapf(f):
 for seg in edit['segments']:
  if seg['source']<=f<seg['end']:return seg['from']+f-seg['source']
 for seg in edit['segments']:
  if seg['source']>=f:return seg['from']
 return edit['duration']
def at(t):return mapf(round(t*FPS))/FPS
raw=read(O/'voz-sin-eco.wav');parts=[]
for seg in edit['segments']:
 q=raw[seg['source']*1600:seg['end']*1600].copy();assert len(q)==seg['duration']*1600
 # 3ms fades only inside confirmed low-energy edit boundaries; no voice time stretch.
 if parts:q[:144]*=np.linspace(0,1,144)[:,None]
 q[-144:]*=np.linspace(1,0,144)[:,None];parts.append(q)
voice=np.concatenate(parts);assert len(voice)==N
write(O/'voz-entrega-pre.wav',voice)
# Consistent close speech dynamics before adding music/SFX.
subprocess.run(['ffmpeg','-v','error','-y','-i',str(O/'voz-entrega-pre.wav'),'-af','highpass=f=85,agate=threshold=0.012:ratio=1.6:attack=4:release=95:range=0.18,acompressor=threshold=0.125:ratio=2:attack=12:release=140:makeup=1.25,loudnorm=I=-16:TP=-2:LRA=7','-ar',str(SR),'-c:a','pcm_s24le',str(O/'voz-entrega.wav')],check=True)
voice=read(O/'voz-entrega.wav')[:N]
# Stem musical aprobado: misma señal y posición temporal, solo se recorta el final.
music=read(P/'06-audio/v10/musica.wav')[:N].copy()
# Restore the exact attenuation applied in v10; keep the approved song clock.
e10=json.loads((P/'04-plan-director/revision-v10/edit.json').read_text())
def map10(f):
 for seg in e10['segments']:
  if seg['source']<=f<seg['end']:return seg['from']+f-seg['source']
 return next(seg['from'] for seg in e10['segments'] if seg['source']>=f)
musicDipA,musicDipB=[round(map10(round(t*FPS))/FPS*SR) for t in (43.08,43.30)]
music[musicDipA:musicDipB]/=.12
music[-3840:]*=np.linspace(1,0,3840)[:,None]
sections=json.loads((P/'06-audio/v10/mezcla-v10.json').read_text())['music_sections']
# Audible human breaths and room tone no longer carry long inter-cut waits.
kit=S/'public/sfx';ref=P/'06-audio/sfx-referencia';cues=[]
def cue(file,time,db,purpose,pre=.045,post=.16):
 if 0<=time<N/SR:cues.append({'file':str(file),'at':time,'peak_dbfs':db,'purpose':purpose,'pre':pre,'post':post})
# No impact or shimmer at second zero: explicitly rejected by Jan.
for ev in edit['transitions']:
 if ev['kind']=='hand':cue(kit/'swoosh/whoosh-soft.mp3',ev['at']/FPS,-26,'Mano sobre lente',.045,.12)
# Every editorial text arrival gets a short accent, including script. Simultaneous words share one attack.
seen=[]
for b in plan['blocks']:
 for w in b['words']:
  time=mapf(w['at'])/FPS
  if w['at']<20 or 'BOOM' in w['text'] or any(abs(time-x)<.04 for x in seen):continue
  if w['role']=='yellow':cue(ref/'pop-B.wav',time,-14.5,'Keyword '+w['text'],.012,.095)
  else:cue(kit/'clicks/click-soft-tap.mp3',time,-17.5,'Texto '+w['text'],.008,.07)
  seen.append(time)
for f,label in [(183,'Vídeo de Guille'),(519,'Solo mis brutos'),(904,'Cuatro posiciones'),(1622,'Un plano entre los dos'),(1960,'Perfil de Guille'),(2400,'Claude lo edita')]:
 cue(kit/'pop/pop-clean.mp3',mapf(f)/FPS,-23,label,.012,.09)
# Action sounds are tied to exact local animation frames.
for start,offset in [(519,0),(2400,15)]:
 for loc,file,db,note in [(22,'clicks/mouse-click.mp3',-21,'Agarra cuatro brutos'),(49,'swoosh/whoosh-soft.mp3',-29,'Arrastra archivos'),(72,'pop/pop-clean.mp3',-19,'Suelta en Claude')]:
  cue(kit/file,mapf(start+loc-offset)/FPS,db,note,.025,.14)
for start,offset in [(519,0),(2400,15)]:
 cue(kit/'clicks/mouse-click.mp3',mapf(start+104-offset)/FPS,-19,'Pulsa enviar',.008,.07)
 cue(kit/'pop/pop-clean.mp3',mapf(start+110-offset)/FPS,-22,'Archivos enviados',.01,.085)
for i in range(4):
 cue(kit/'pop/pop-clean.mp3',mapf(2301+i*3)/FPS,-25,'Sticker '+str(i+1),.01,.07)
 cue(kit/'epi/card-flip.mp3',mapf(2301+51+i*8)/FPS,-24,'Sticker entra en carpeta',.035,.13)
cue(kit/'clicks/click-soft-tap.mp3',mapf(2381)/FPS,-19,'Cierra carpeta',.01,.15)
cue(kit/'impact/boom-deep.mp3',mapf(2285)/FPS,-11,'BOOM: cuerpo grave sincronizado',.012,.70)
cue(kit/'snap/finger-snap.mp3',at(43.05),-18,'Cambio de ritmo visible',.025,.14)
# El golpe de bienvenida pertenece a la propia canción, sin sub-drop añadido.
cue(kit/'pop/pop-clean.mp3',mapf(2501)/FPS,-23,'Claude: Aquí lo tienes + vídeo',.025,.18)
for frame in [318,320,322,324,326]:cue(kit/'pop/pop-clean.mp3',mapf(frame)/FPS,-22,'Perfil incógnito',.01,.07)
cue(kit/'shimmer/shimmer-glow.mp3',mapf(343)/FPS,-21,'Guille se revela y brilla',.015,.23)
cue(kit/'swoosh/whoosh-soft.mp3',mapf(1793)/FPS,-21,'Limpieza de CLEAN: aire largo',.06,.42)
cue(kit/'shimmer/shimmer-glow.mp3',mapf(1797)/FPS,-19,'Destello limpio prolongado',.025,.90)
for frame in [147,1041,1106,1817,2176]:cue(kit/'swoosh/whoosh-soft.mp3',mapf(frame)/FPS,-24,'Movimiento físico de cámara',.035,.16)
cue(kit/'swoosh/whoosh-soft.mp3',mapf(1699)/FPS,-27,'Tarjeta a plano vivo',.025,.13)
# Layered action accents, every sound follows its visual action.
cue(kit/'pop/pop-clean.mp3',mapf(2285)/FPS,-18,'BOOM: ataque corto',.008,.10)
cue(kit/'swoosh/whoosh-soft.mp3',mapf(1490)/FPS,-22,'TRANSICIONES entra',.06,.16)
cue(kit/'epi/card-flip.mp3',mapf(1501)/FPS,-20,'Mano tapa TRANSICIONES',.035,.22)
for frame in [852,860,869]:cue(kit/'pop/pop-clean.mp3',mapf(frame)/FPS,-18,'SÍ O SÍ frente a Jan',.012,.11)
for frame in [904,909,914,919]:cue(kit/'epi/card-flip.mp3',mapf(frame)/FPS,-23,'Entra posición de cámara',.02,.12)
for frame in [1960,2016,2070,2124]:cue(kit/'swoosh/whoosh-soft.mp3',mapf(frame)/FPS,-29,'Desplazamiento del feed',.02,.11)
sfx=np.zeros((N,2),np.float32);resolved=[]
for c in sorted(cues,key=lambda z:z['at']):
 # Keep one dominant attack when several graphical events land together.
 if any(abs(c['at']-z['at'])<.025 and c['peak_dbfs']<z['peak_dbfs']-3 for z in resolved):continue
 q=read(Path(c['file']));
 q=sosfilt(butter(2,160 if 'swoosh' in c['file'] else 42 if 'boom-deep' in c['file'] else 75,fs=SR,btype='highpass',output='sos'),q,axis=0)
 if 'swoosh' in c['file']:q=sosfilt(butter(2,5200,fs=SR,btype='lowpass',output='sos'),q,axis=0)
 energy=np.convolve(np.mean(q*q,axis=1),np.ones(192)/192,mode='same');peak=int(np.argmax(energy));left=max(0,peak-round(c['pre']*SR));right=min(len(q),peak+round(c['post']*SR));q=q[left:right].copy();peak-=left
 n=min(720,len(q)//4);attack=min(384,n);q[:attack]*=np.linspace(0,1,attack)[:,None];q[-n:]*=np.linspace(1,0,n)[:,None];q*=10**(c['peak_dbfs']/20)/max(np.max(np.abs(q)),1e-8)
 start=round(c['at']*SR)-peak;end=min(N,start+len(q));sfx[max(0,start):end]+=q[max(0,-start):end-start];resolved.append(c)
sfx*=1
write(O/'musica.wav',music);write(O/'efectos.wav',sfx);write(O/'pre-master.wav',voice+music+sfx)
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(O/'pre-master.wav'),'-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
m=json.JSONDecoder().raw_decode(r[r.rfind('{'):])[0];flt='loudnorm=I=-14:TP=-1.5:LRA=9:linear=true:'+':'.join([f'measured_I={m["input_i"]}',f'measured_TP={m["input_tp"]}',f'measured_LRA={m["input_lra"]}',f'measured_thresh={m["input_thresh"]}',f'offset={m["target_offset"]}'])
subprocess.run(['ffmpeg','-v','error','-y','-i',str(O/'pre-master.wav'),'-af',flt,'-ar',str(SR),'-c:a','pcm_s24le',str(O/'master-v12-entrega.wav')],check=True)
dest=V/'master-v12-entrega.wav';dest.unlink(missing_ok=True);dest.hardlink_to((O/'master-v12-entrega.wav').resolve())
(O/'mezcla-v12.json').write_text(json.dumps({'duration':N/SR,'song':'Without Me, misma instrumental de referencia','music_sections':sections,'music_from_start':True,'sfx':resolved,'sfx_bus_gain_db':0,'sfx_count':len(resolved),'music_dip_removed_samples':[musicDipA,musicDipB],'master_analysis':m},ensure_ascii=False,indent=2));print('Mezcla completa',len(resolved),'cues;',N/SR,'s')
