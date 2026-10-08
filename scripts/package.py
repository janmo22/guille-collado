#!/usr/bin/env python3
"""Empaqueta la skill viva; sin configuración externa, cachés ni secretos.

--out ZIP: paquete completo para el equipo. --publico DIR: copia para el repo
público, sin fuentes con licencia, canción, SFX ni la entrega con música.
"""
import argparse,hashlib,json,re,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALLOWED=('SKILL.md','requirements.txt','agents','references','scripts','assets')
# Licencia de Jan, no redistribuible: Font Bureau, SoftMaker, Eminem, Epidemic y la entrega que lleva la canción.
PRIVADO=('assets/fonts/SloopScriptOne.ttf','assets/fonts/Toledo-Serial-BoldItalic.ttf','assets/golden/dia1-entrega-v14.mp4','assets/music/','assets/sfx/')

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and p.relative_to(ROOT).parts[0] in ALLOWED
        and '__pycache__' not in p.parts and not p.name.startswith('.env') and p.suffix!='.pyc')

def scrub(x):
    if isinstance(x,dict):return {k:scrub(v) for k,v in x.items() if k!='output_url'}
    return [scrub(v) for v in x] if isinstance(x,list) else x

def publico(dest):
    if dest.is_relative_to(ROOT):raise ValueError('La copia debe estar fuera de la skill viva')
    dest.mkdir(parents=True,exist_ok=True)
    for top in ALLOWED:
        old=dest/top
        if old.is_dir():shutil.rmtree(old)
        elif old.exists():old.unlink()
    rows=[]
    for p in files():
        rel=p.relative_to(ROOT).as_posix()
        if rel=='assets/manifest.json' or rel.startswith(PRIVADO):continue
        out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.json' and 'output_url' in p.read_text():out.write_text(json.dumps(scrub(json.loads(p.read_text())),ensure_ascii=False,indent=2))
        else:shutil.copy2(p,out)
        if out.suffix in {'.md','.json','.py','.tsx','.yaml','.txt','.srt'} and re.search(r'/Users/[A-Za-z0-9._-]+/',out.read_text()):raise ValueError(f'Ruta privada en {rel}')
        rows.append({'path':rel,'bytes':out.stat().st_size,'sha256':sha(out)})
    version=json.loads((ROOT/'assets/preset.json').read_text())['version']
    (dest/'assets/manifest.json').write_text(json.dumps({'package':'guille-collado','version':version,'provenance':'references/procedencia.md',
        'not_included':list(PRIVADO),'files':rows},ensure_ascii=False,indent=2))
    print(json.dumps({'dir':str(dest),'files':len(rows)+1,'bytes':sum(r['bytes'] for r in rows)},ensure_ascii=False))

def main():
    ap=argparse.ArgumentParser(description=__doc__);g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--out');g.add_argument('--publico');a=ap.parse_args()
    if a.publico:return publico(Path(a.publico).expanduser().resolve())
    output=Path(a.out).expanduser().resolve()
    if output.is_relative_to(ROOT):raise ValueError('El ZIP debe estar fuera de la skill viva')
    manifest=ROOT/'assets/manifest.json'
    rows=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files() if p!=manifest]
    version=json.loads((ROOT/'assets/preset.json').read_text())['version']
    manifest.write_text(json.dumps({'package':'guille-collado','version':version,'provenance':'references/procedencia.md','files':rows},ensure_ascii=False,indent=2))
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files():z.write(p,'guille-collado/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        for row in rows:assert hashlib.sha256(z.read('guille-collado/'+row['path'])).hexdigest()==row['sha256']
    print(json.dumps({'zip':str(output),'bytes':output.stat().st_size,'sha256':sha(output),'files':len(rows)+1},ensure_ascii=False))

if __name__=='__main__':main()
