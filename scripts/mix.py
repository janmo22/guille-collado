#!/usr/bin/env python3
"""Mezcla voz ya desreverberada, cama continua alineada a promesa y cues por ataque.

events.json: [{file,at,peak_dbfs,pre,post,purpose}]; at/pre/post en segundos.
No selecciona eventos ni limpia reverberación; parte de la dirección del editor.
"""
import argparse,json,subprocess
from pathlib import Path
from functools import lru_cache
import numpy as np
from scipy.signal import butter,sosfilt
SR=48000

@lru_cache(maxsize=24)
def read(path):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar',str(SR),'-ac','2','-f','f32le','-']),np.float32).reshape(-1,2).copy()

def write(path,a):
    subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s24le',str(path)],input=a.astype(np.float32).tobytes(),check=True)

def sfx_bus(cues,n,root):
    result=np.zeros((n,2),np.float32);resolved=[]
    for c in sorted(cues,key=lambda x:x['at']):
        if not 0<=c['at']<n/SR:raise ValueError(f"Cue fuera de entrega: {c}")
        if any(abs(c['at']-z['at'])<.025 and c['peak_dbfs']<z['peak_dbfs']-3 for z in resolved):continue
        file=(root/c['file']).resolve();q=read(file).copy();whoosh='whoosh' in file.name or 'swoosh' in file.name
        q=sosfilt(butter(2,160 if whoosh else 42 if 'boom' in file.name else 75,fs=SR,btype='highpass',output='sos'),q,axis=0)
        if whoosh:q=sosfilt(butter(2,5200,fs=SR,btype='lowpass',output='sos'),q,axis=0)
        energy=np.convolve(np.mean(q*q,axis=1),np.ones(192)/192,mode='same');peak=int(np.argmax(energy))
        left=max(0,peak-round(c.get('pre',.025)*SR));right=min(len(q),peak+round(c.get('post',.14)*SR));q=q[left:right].copy();peak-=left
        if not len(q):raise ValueError('Cue de duración nula')
        fade=min(720,len(q)//4);attack=min(384,fade)
        if attack:q[:attack]*=np.linspace(0,1,attack)[:,None]
        if fade:q[-fade:]*=np.linspace(1,0,fade)[:,None]
        q*=10**(c['peak_dbfs']/20)/max(np.max(np.abs(q)),1e-8)
        start=round(c['at']*SR)-peak;end=min(n,start+len(q));result[max(0,start):end]+=q[max(0,-start):end-start];resolved.append(c)
    return result,resolved

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--voice',required=True);p.add_argument('--song',required=True);p.add_argument('--events',required=True);p.add_argument('--asset-root',required=True);p.add_argument('--outdir',required=True);p.add_argument('--frames',type=int,required=True);p.add_argument('--fps',type=int,default=30);p.add_argument('--welcome',type=float,required=True);p.add_argument('--source-beat',type=float,required=True);a=p.parse_args()
    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True);n=round(a.frames/a.fps*SR)
    if not 0<=a.welcome<n/SR:raise ValueError('Promesa fuera de entrega')
    offset=a.source_beat-a.welcome
    if offset<0:raise ValueError('Elegir un ataque posterior en la canción: offset negativo')
    subprocess.run(['ffmpeg','-v','error','-y','-i',a.voice,'-af','highpass=f=85,acompressor=threshold=0.125:ratio=2:attack=12:release=140:makeup=1.25,loudnorm=I=-16:TP=-2:LRA=7','-ar',str(SR),'-c:a','pcm_s24le',str(out/'voice.wav')],check=True)
    voice=read(out/'voice.wav')
    if len(voice)<n:raise ValueError('Voz más corta que el timeline; no rellenar automáticamente')
    voice=voice[:n];song=read(Path(a.song));start=round(offset*SR);music=song[start:start+n].copy()
    if len(music)!=n:raise ValueError('Canción insuficiente: dirigir empalme musical, no loop ciego')
    music*=10**(-24/20)/max(np.sqrt(np.mean(music*music)),1e-8);t=np.arange(n)/SR;y=a.welcome
    gain=np.interp(t,[0,max(0,y-.1),y,y+.2,y+.75,n/SR],[1.16,1.16,1.88,1.88,.94,.94]);music*=gain[:,None]
    music[:min(480,n)]*=np.linspace(0,1,min(480,n))[:,None];music[-min(3840,n):]*=np.linspace(1,0,min(3840,n))[:,None]
    effects,resolved=sfx_bus(json.loads(Path(a.events).read_text()),n,Path(a.asset_root))
    write(out/'music.wav',music);write(out/'sfx.wav',effects);write(out/'premaster.wav',voice+music+effects)
    r=subprocess.run(['ffmpeg','-hide_banner','-i',str(out/'premaster.wav'),'-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0]
    filters='loudnorm=I=-14:TP=-1.5:LRA=9:linear=true:'+':'.join(f'{k}={m[v]}' for k,v in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')])
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(out/'premaster.wav'),'-af',filters,'-ar',str(SR),'-c:a','pcm_s24le',str(out/'master.wav')],check=True)
    (out/'mix.json').write_text(json.dumps({'frames':a.frames,'fps':a.fps,'offset':offset,'welcome':y,'cues':resolved,'normalization_input':m},ensure_ascii=False,indent=2))
    print(str(out/'master.wav'))

if __name__=='__main__':main()
