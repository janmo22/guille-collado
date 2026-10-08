"""Dos correcciones locales sobre v13; conservar sus relojes y el resto del máster."""
from pathlib import Path
import json, subprocess, math
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, correlate, correlation_lags
from scipy.interpolate import PchipInterpolator
import cv2
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[2]
A = P/'06-audio/v14'; B = P/'05-brolls/v14'; Q = P/'09-auditoria/v14'
SR = 48000

def run(args):
    subprocess.run(args, check=True)

def read(p):
    x,sr=sf.read(p,always_2d=True,dtype='float32')
    if sr != SR:
        g=math.gcd(sr,SR);x=resample_poly(x,SR//g,sr//g,axis=0)
    return x

def wav(name,x):
    sf.write(A/name,x,SR,subtype='PCM_24')

def audio():
    raw=read(A/'alternativas-contexto.wav').mean(axis=1)
    dry=read(A/'clean/alternativas-contexto_(No Reverb)_UVR-DeEcho-DeReverb.wav').mean(axis=1)
    n=min(len(raw),len(dry));raw=raw[:n];dry=dry[:n]
    cc=correlate(dry,raw,method='fft');lags=correlation_lags(n,n)
    valid=np.abs(lags)<int(.15*SR);lag=int(lags[valid][np.argmax(cc[valid])])
    if lag>0:dry=np.pad(dry[lag:],(0,lag))
    elif lag<0:dry=np.pad(dry[:lag],(-lag,0))
    # Real Jan take D 222.78–223.45, relative to context beginning at 221.80.
    take=(.88*dry+.12*raw)[round(.98*SR):round(1.65*SR)]
    wav('basic-alternativa-limpia.wav',take)
    run(['ffmpeg','-v','error','-y','-i',str(A/'basic-alternativa-limpia.wav'),
        '-af','highpass=f=85,acompressor=threshold=0.125:ratio=2:attack=12:release=140:makeup=1.25,atempo=1.16',
        '-ar',str(SR),'-c:a','pcm_s24le',str(A/'basic-alternativa-ajustada.wav')])
    candidate=read(A/'basic-alternativa-ajustada.wav')
    voice=read(P/'06-audio/v12/voz-entrega.wav');master=read(P/'06-audio/v12/master-v12-entrega.wav')
    old=voice[round(66.8*SR):round(67.32*SR)]
    # Match body of the word; ignore isolated peaks and residual breath.
    def active_rms(x):
        m=x.mean(axis=1);chunks=m[:len(m)//480*480].reshape(-1,480)
        v=np.sqrt(np.mean(chunks**2,axis=1));return float(np.sqrt(np.mean(v[v>v.max()*.25]**2)))
    gain=active_rms(old)/active_rms(candidate)
    candidate*=gain
    fade=round(.005*SR);candidate[:fade]*=np.linspace(0,1,fade)[:,None];candidate[-fade:]*=np.linspace(1,0,fade)[:,None]
    fixed=voice.copy();lo=round(66.65*SR);hi=round(67.3375*SR)
    remove=np.ones(hi-lo);f=round(.004*SR);remove[:f]=np.linspace(0,1,f);remove[-f:]=np.linspace(1,0,f)
    fixed[lo:hi]*=(1-remove[:,None])
    at=round(66.75*SR);assert at+len(candidate)<hi
    fixed[at:at+len(candidate)]+=candidate
    wav('voz-entrega.wav',fixed)
    premix=read(P/'06-audio/v12/pre-master.wav')+(fixed-voice)
    wav('pre-master.wav',premix)
    stats=json.loads((P/'06-audio/v12/mezcla-v12.json').read_text())['master_analysis']
    flt='loudnorm=I=-14:TP=-1.5:LRA=9:linear=true:'+':'.join([
        f'measured_I={stats["input_i"]}',f'measured_TP={stats["input_tp"]}',
        f'measured_LRA={stats["input_lra"]}',f'measured_thresh={stats["input_thresh"]}',f'offset={stats["target_offset"]}'])
    run(['ffmpeg','-v','error','-y','-i',str(A/'pre-master.wav'),'-af',flt,'-ar',str(SR),'-c:a','pcm_s24le',str(A/'master-candidato.wav')])
    revised=read(A/'master-candidato.wav');assert len(revised)==len(master)
    # Keep the approved PCM sample-identical outside a local mastering window.
    a,b=round(66.55*SR),round(67.58*SR);fade=round(.05*SR)
    env=np.ones(b-a);env[:fade]=np.linspace(0,1,fade);env[-fade:]=np.linspace(1,0,fade)
    delivered=master.copy();delivered[a:b]=master[a:b]*(1-env[:,None])+revised[a:b]*env[:,None]
    wav('master-v14-entrega.wav',delivered)
    wav('revision-frase-voz.wav',fixed[round(65.7*SR):round(69.1*SR)])
    wav('revision-frase-mezcla.wav',delivered[round(65.7*SR):round(69.1*SR)])
    assert np.array_equal(delivered[:a],master[:a]) and np.array_equal(delivered[b:],master[b:])
    report={'source':'toma-D-h264.mp4','source_word':[222.78,223.45],'final_onset':66.75,
        'candidate_duration':len(candidate)/SR,'atempo_pitch_preserved':1.16,'gain':gain,
        'dereverb_model':'UVR-DeEcho-DeReverb','dry_blend':.88,'alignment_samples':lag,
        'word_replace_window':[lo/SR,hi/SR],'master_local_window':[a/SR,b/SR],
        'pcm_unchanged_outside_patch':True,'other_voice_music_sfx_timing':'unchanged'}
    (Q/'audio-correccion.json').write_text(json.dumps(report,indent=2));print(report,flush=True)

def transition():
    source=B/'inicio-seedance.mp4'
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=width,height','-of','json',str(source)]))['streams'][0]
    # FFmpeg respects source colour matrices when decoding; do not mix RGB
    # from different decoders before encoding the patch back into the master.
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),
        '-an','-f','rawvideo','-pix_fmt','bgr24','-threads','3','-'])
    frames=np.frombuffer(data,np.uint8).reshape(-1,meta['height'],meta['width'],3)
    assert len(frames)>60
    # This is already the finished composite, including the lens and text.
    # Do not apply another CameraMove or finish_lens transform.
    data_ends=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'08-final/dia1-guille-v13.mp4'),
        '-vf','select=eq(n\\,89)+eq(n\\,112)','-fps_mode','passthrough','-frames:v','2',
        '-an','-f','rawvideo','-pix_fmt','bgr24','-threads','3','-'])
    first,last=np.frombuffer(data_ends,np.uint8).reshape(2,1920,1080,3)
    count=22
    curve=PchipInterpolator([0,.18,.72,1],[0,.10,.86,1])
    phase=curve(np.linspace(0,1,count))*(len(frames)-1)
    out=B/'inicio-patch-v14.mp4'
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24',
        '-s','1080x1920','-r','30','-i','-','-an',
        '-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p',
        '-c:v','libx264','-crf','14','-preset','fast','-threads','3',
        '-colorspace','bt709','-color_range','tv','-color_primaries','bt709','-color_trc','bt709',str(out)],stdin=subprocess.PIPE)
    sheet=Image.new('RGB',(6*216,4*404),'#202020');draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(phase):
        f=cv2.resize(frames[int(round(p))],(1080,1920),interpolation=cv2.INTER_LANCZOS4)
        # Exact endpoints, no dissolves: dissolving displaced type makes ghosts.
        if i==0:f=first
        if i==count-1:f=last
        proc.stdin.write(f.tobytes())
        im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)).resize((216,384))
        x=i%6*216;y=i//6*404;sheet.paste(im,(x,y+20));draw.text((x+4,y+3),f'f{90+i} / src{p:.1f}',fill='white')
    proc.stdin.close();assert proc.wait()==0;sheet.save(Q/'intro-patch-contacto.jpg')
    (Q/'transicion-correccion.json').write_text(json.dumps({'replace_frames':[90,112],
        'previous_real_frame':89,'next_real_frame':112,'duration_frames':count,
        'generated_source_frames':len(frames),'sampled_positions':phase.tolist(),
        'finished_composite_endpoints':True,'extra_lens_applied':False,'timeline_shift':0,
        'rgb_conversion':'full RGB -> limited YUV BT709; explicit matrix and tags'},indent=2))
    pin_native_endpoints()
    print('Transición de 22 frames preparada',flush=True)

def pin_native_endpoints():
    # Preserve decoded YUV at the two joins. RGB roundtrips can accumulate a
    # few luma/chroma levels even with explicit, matching BT.709 matrices.
    out=B/'inicio-patch-v14.mp4';tmp=B/'inicio-patch-native.mp4'
    filters='[0:v]split=2[a][b];[a]trim=start_frame=89:end_frame=90,setpts=PTS-STARTPTS[start];[b]trim=start_frame=112:end_frame=113,setpts=PTS-STARTPTS[end];[1:v]trim=start_frame=1:end_frame=21,setpts=PTS-STARTPTS[mid];[start][mid][end]concat=n=3:v=1:a=0[v]'
    run(['ffmpeg','-v','error','-y','-t','3.8','-i',str(P/'08-final/dia1-guille-v13.mp4'),
        '-i',str(out),'-filter_complex',filters,'-map','[v]','-an','-c:v','libx264',
        '-crf','14','-preset','fast','-threads','3','-pix_fmt','yuv420p',str(tmp)])
    tmp.replace(out)
    path=Q/'transicion-correccion.json';j=json.loads(path.read_text());j['final_endpoints']='native YUV from approved base; no RGB roundtrip';path.write_text(json.dumps(j,indent=2))

if __name__=='__main__':
    import sys
    if 'audio' in sys.argv:audio()
    elif 'transition' in sys.argv:transition()
    elif 'pin' in sys.argv:pin_native_endpoints()
    else:audio();transition()
