#!/usr/bin/env python3
"""Inventario y arranque local. No genera vídeo ni gasta créditos."""
import argparse, hashlib, json, re, shutil, subprocess
from datetime import date
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]

def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def doctor():
    report = {'tools': {name: shutil.which(name) for name in ['ffmpeg','ffprobe','node']},
              'fonts': {p.name: p.exists() for p in [SKILL/'assets/fonts'/name for name in
                ['Anton-Regular.ttf','SloopScriptOne.ttf','Toledo-Serial-BoldItalic.ttf']]},
              'song': (SKILL/'assets/music/without-me-inst.flac').exists(),
              'sfx': sorted(p.name for p in (SKILL/'assets/sfx').glob('*.*')),
              'note': 'Higgsfield/transcripción se comprueban solo cuando el encargo los necesita.'}
    if not all(report['fonts'].values()) or not report['song'] or not report['sfx']:
        report['copia_publica'] = ('Sloop ScriptOne, Toledo-Serial BoldItalic, canción y SFX tienen licencia y no viajan: '
            'pedir al usuario sus archivos (fuentes en assets/fonts/, canción por ruta, SFX en assets/sfx/).')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(report['tools'].values()) and all(report['fonts'].values()) else 1

def initialize(args):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.name):
        raise ValueError('--name debe ser un slug con minúsculas, números y guiones')
    inputs = [Path(p).expanduser().resolve(strict=True) for p in args.input]
    if len(inputs) != len(set(inputs)):
        raise ValueError('Archivos repetidos')
    inventory=[]
    for p in inputs:
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
        if not any(s['codec_type']=='video' for s in probe['streams']):
            raise ValueError(f'No contiene vídeo: {p.name}')
        inventory.append({'path':str(p),'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p),'probe':probe})
    root=Path(args.workspace).expanduser().resolve()
    base=root/'negocios/contenido/proyectos-video' if (root/'negocios/contenido').is_dir() else root/'proyectos-video'
    out=base/f'{date.today().isoformat()}-{args.name}'
    out.mkdir(parents=True,exist_ok=False)
    for folder in ['01-tomas','02-transcripciones','03-guion','04-direccion','05-assets','06-audio','07-montaje','08-final','09-qa']:
        (out/folder).mkdir()
    (out/'01-tomas/inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
    shutil.copy2(SKILL/'assets/preset.json',out/'04-direccion/preset.json')
    shutil.copytree(SKILL/'assets/runtime',out/'07-montaje/runtime')
    (out/'05-assets/guille-pack').symlink_to(SKILL/'assets',target_is_directory=True)
    production={'schema':1,'preset':'guille-collado-jan-aprobado-2026-09-21','skill':str(SKILL),
        'canvas':[1080,1920],'fps':30,'inputs':[x['path'] for x in inventory],
        'state':'inventariado','budget_credits':None,
        'next':'Transcribir cada toma, reconstruir guion y seleccionar interpretaciones; no trasplantar el EDL Día1.'}
    (out/'production.json').write_text(json.dumps(production,ensure_ascii=False,indent=2))
    print(json.dumps({'project':str(out),'inputs':len(inputs),'generated_video':False},ensure_ascii=False))

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    init=sub.add_parser('init');init.add_argument('--workspace',required=True);init.add_argument('--name',required=True);init.add_argument('--input',action='append',required=True)
    sub.add_parser('doctor');args=parser.parse_args()
    if args.command=='doctor':raise SystemExit(doctor())
    initialize(args)

if __name__=='__main__':main()
