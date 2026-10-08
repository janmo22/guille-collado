from pathlib import Path
import subprocess,sys,shutil
P=Path(__file__).resolve().parents[2]
preview='--preview' in sys.argv
base=P/'08-final/dia1-guille-v13.mp4'
patch=P/'05-brolls/v14/inicio-patch-v14.mp4'
master=P/'06-audio/v14/master-v14-entrega.wav'
out=P/('09-auditoria/v14/inicio-revision.mp4' if preview else '08-final/dia1-guille-v14.mp4')
working=out if preview else out.with_name('dia1-guille-v14-render.mp4')
filters='[0:v]split=2[a][b];[a]trim=end_frame=90,setpts=PTS-STARTPTS[before];[1:v]trim=end_frame=22,setpts=PTS-STARTPTS[patch];[b]trim=start_frame=112,setpts=PTS-STARTPTS[after];[before][patch][after]concat=n=3:v=1:a=0[assembled]'
filters+=';[assembled]scale=540:960[out]' if preview else ';[assembled]null[out]'
cmd=['ffmpeg','-v','error','-y','-i',str(base),'-i',str(patch),'-i',str(master),'-filter_complex',filters,'-map','[out]','-map','2:a:0']
if preview:cmd+=['-t','5.2']
cmd+=['-c:v','libx264','-crf','16','-preset','veryfast','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',str(working)]
subprocess.run(cmd,check=True)
if not preview:working.replace(out)
if preview:
    subprocess.run(['ffmpeg','-v','error','-y','-ss','65.7','-i',str(base),'-ss','65.7','-i',str(master),'-t','3.4','-map','0:v:0','-map','1:a:0','-vf','scale=540:960','-c:v','libx264','-crf','18','-preset','veryfast','-threads','3','-c:a','aac','-b:a','256k',str(P/'09-auditoria/v14/frase-revision.mp4')],check=True)
else:
    shutil.copy(P/'08-final/dia1-guille-v13.srt',P/'08-final/dia1-guille-v14.srt')
print(out,flush=True)
