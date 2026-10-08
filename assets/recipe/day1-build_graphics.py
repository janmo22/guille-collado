"""Geometría tipográfica v7: HarfBuzz, encaje óptico y curvatura del bloque."""
from pathlib import Path
import json, re, unicodedata
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
S=P.parents[1]/'remotion-studio'
FONTS=S/'public-dia1-v12/fonts'
OUT=S/'src/compositions/proyectos/2026-09-16-dia1-guille-collado/v12-plan.json'
edl=json.loads((HERE/'edl-candidato.json').read_text())
WORDS=json.loads((HERE/'conform/master.words.json').read_text())['words']
fonts={}
for key,file in [('sans','Anton-Regular.ttf'),('script','SloopScriptOne.ttf')]:
    path=FONTS/file;ft=TTFont(path);face=hb.Face(path.read_bytes());hf=hb.Font(face);hf.scale=(face.upem,face.upem)
    fonts[key]=(ft,hf)

def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode())
def at(text,unit,near=None):
    match=[w for w in WORDS if w['unit']==unit and norm(w['word'])==norm(text)]
    if not match:raise ValueError((text,unit))
    w=min(match,key=lambda w:abs(w['start']-near)) if near is not None else match[0]
    return round(w['start']*30)

def shape(text,role):
    ft,hf=fonts['script' if role=='script' else 'sans'];gs=ft.getGlyphSet();order=ft.getGlyphOrder()
    buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(hf,buf,{'kern':True,'liga':True,'calt':True})
    rec=DecomposingRecordingPen(gs);bounds=BoundsPen(gs);x=y=0
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        tr=(1,0,0,1,x+pos.x_offset,y+pos.y_offset)
        gs[order[info.codepoint]].draw(TransformPen(rec,tr));gs[order[info.codepoint]].draw(TransformPen(bounds,tr))
        x+=pos.x_advance;y+=pos.y_advance
    return rec,bounds.bounds

class WarpPen(BasePen):
    def __init__(self,pen,box,bounds,warp):
        super().__init__(None);self.pen=pen;self.box=box;self.bounds=bounds;self.warp=warp
    def p(self,p):
        x,y,w,h=self.box;lx,by,rx,ty=self.bounds
        px=x+(p[0]-lx)*w/(rx-lx);py=y+(ty-p[1])*h/(ty-by)
        # Bloque compacto sobre una superficie suavemente convexa.
        cx,cy,arch,flare=self.warp
        ux=(px-cx)/480
        return (round(cx+(px-cx)*(1+flare*(py-cy)/650),3),round(py+arch*(ux*ux-1),3))
    def _moveTo(self,p):self.pen.moveTo(self.p(p))
    def _lineTo(self,p):self.pen.lineTo(self.p(p))
    def _curveToOne(self,a,b,c):self.pen.curveTo(self.p(a),self.p(b),self.p(c))
    def _qCurveToOne(self,a,b):self.pen.qCurveTo(self.p(a),self.p(b))
    def _closePath(self):self.pen.closePath()
    def _endPath(self):self.pen.endPath()

blocks=[]
def block(id,start,end,warp=(540,420,14,.055)):
    b={'id':id,'from':round(start*30),'to':round(end*30),'warp':warp,'words':[]};blocks.append(b);return b
def word(b,text,x,y,w,h,role='yellow',unit=None,anchor=None,near=None,when=None,layer='front',motion=False,xscale=None):
    rec,bounds=shape(text,role);lx,by,rx,ty=bounds
    # Las proporciones pertenecen a la fuente; la keyword admite el ancho óptico de v6.
    aspect=(rx-lx)/(ty-by);stretch=xscale if xscale is not None else (1.10 if role!='script' else 1.0)
    rh=min(h,w/(aspect*stretch));rw=rh*aspect*stretch
    x+=(w-rw)/2;y+=(h-rh)/2
    pen=SVGPathPen(None);rec.replay(WarpPen(pen,(x,y,rw,rh),bounds,b['warp']))
    frame=round(when*30) if when is not None else at(anchor or text,unit,near) if unit else b['from']
    b['words'].append({'text':text,'at':max(b['from'],frame),'path':pen.getCommands(),'role':role,'layer':layer,'box':[x,y,rw,rh],'motion':motion})
def center(b,text,y,w,h,**kwargs):word(b,text,(1080-w)/2,y,w,h,**kwargs)


def row(b,items,y,width,height,role='script',unit=None,layer='front',gap=14,near=None):
    # Shape the full phrase once. Each word keeps its real baseline, kerning and
    # reserved place while its glyph group is revealed at the spoken onset.
    text=' '.join(items);ft,hf=fonts['script' if role=='script' else 'sans'];gs=ft.getGlyphSet();order=ft.getGlyphOrder()
    _,bounds=shape(text,role);lx,by,rx,ty=bounds;h=min(height,width*(ty-by)/(rx-lx));w=h*(rx-lx)/(ty-by);x=(1080-w)/2
    buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(hf,buf,{'kern':True,'liga':True,'calt':True})
    spans=[];pos=0
    for t in items:spans.append((pos,pos+len(t)));pos+=len(t)+1
    recs=[DecomposingRecordingPen(gs) for _ in items];bps=[BoundsPen(gs) for _ in items];px=py=0
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        i=next((i for i,(a,z) in enumerate(spans) if a<=info.cluster<z),None)
        if i is not None:
            tr=(1,0,0,1,px+pos.x_offset,py+pos.y_offset);gs[order[info.codepoint]].draw(TransformPen(recs[i],tr));gs[order[info.codepoint]].draw(TransformPen(bps[i],tr))
        px+=pos.x_advance;py+=pos.y_advance
    for text,rec,bp in zip(items,recs,bps):
        pen=SVGPathPen(None);rec.replay(WarpPen(pen,(x,y,w,h),bounds,b['warp']));a,z,c,d=bp.bounds
        box=[x+(a-lx)*w/(rx-lx),y+(ty-d)*h/(ty-by),(c-a)*w/(rx-lx),(d-z)*h/(ty-by)]
        frame=at(text,unit,near) if unit else b['from']
        b['words'].append({'text':text,'at':max(b['from'],frame),'path':pen.getCommands(),'role':role,'layer':layer,'box':box,'motion':False})

b=block('portada',0,4.72,(540,440,11,.025))
word(b,'Este',205,182,240,100,'script',layer='back');word(b,'VÍDEO',460,173,405,121,'white',layer='back')
center(b,'lo ha editado',316,680,105,role='script',layer='back');center(b,'CLAUDE',487,875,242,layer='back')
b=block('efectivamente',4.95,6.08);center(b,'Efectivamente',258,810,112,role='script',unit='u02',anchor='efectivamente')
b=block('dia-uno',8.08,10.60,(540,390,10,.03))
word(b,'DÍA',236,172,365,150,'white',unit='u03',anchor='día');word(b,'1',632,142,155,207,unit='u03',anchor='uno')
row(b,['haciendo','que'],363,730,80,unit='u03');center(b,'CLAUDE',458,840,125,unit='u03',anchor='Claude')
b=block('creador',10.60,13.10,(540,400,10,.025))
row(b,['el','creador'],195,775,90,unit='u03');
row(b,['que','a','mí','me','dé'],306,790,62,role='white',unit='u03',near=12.3)
row(b,['la'],385,180,60,unit='u03');center(b,'GANA',455,775,135,unit='u03',anchor='gana',motion=True)
b=block('entrenado',13.10,14.85)
center(b,'He',175,205,90,role='script',unit='u04a');center(b,'ENTRENADO',286,840,151,unit='u04a',anchor='entrenado')
word(b,'a la',277,462,204,88,'script',when=13.76);word(b,'IA',541,455,273,160,unit='u04a')
b=block('entera',21.20,22.65)
center(b,'Sí,',385,228,106,role='script',unit='u05',anchor='Sí');center(b,'ENTERA',512,675,187,unit='u05',anchor='entera',motion=True)
b=block('cambios-plano',22.83,26.60)
center(b,'CAMBIOS',175,835,171,unit='u06',anchor='cambios');center(b,'de',377,165,75,role='script',unit='u06');center(b,'PLANO',483,680,191,role='white',unit='u06',anchor='plano')
b=block('si-o-si',28.42,30.10)
center(b,'SÍ',230,920,445,unit='u07a',anchor='sí',near=28.7);center(b,'o',700,240,150,role='script',unit='u07a');center(b,'SÍ',875,920,445,unit='u07a',anchor='sí',near=29.1)
b=block('ahora-que',34.70,36.83,(540,340,7,.018))
# Two optical rows; y/ahora share the same ink baseline and don't drift as words reveal.
row(b,['¿y','ahora'],170,650,108,unit='u08');center(b,'QUÉ?',296,715,233,unit='u08',anchor='qué')
b=block('palabras-clave',36.97,40.97,(540,460,10,.025))
row(b,['Cómo','pone'],137,689,99,unit='u09');center(b,'las',258,180,78,role='script',unit='u09')
center(b,'PALABRAS',347,892,175,unit='u09',anchor='palabras',layer='back');center(b,'CLAVE',541,764,217,unit='u09',anchor='clave',layer='back')
word(b,'detrás',95,760,320,95,'script',unit='u09');word(b,'SUYA',670,760,315,108,'white',unit='u09',anchor='suya')
b=block('efectos-sonido',41.15,42.93,(540,380,9,.025))
center(b,'EFECTOS',156,780,181,unit='u10',anchor='efectos');center(b,'de',353,160,75,role='script',unit='u10',anchor='de',near=41.95)
center(b,'SONIDO',454,772,210,role='white',unit='u10',anchor='sonido')
b=block('cambios-ritmo',42.93,44.27)
center(b,'cambios de',175,730,105,role='script',when=42.93);center(b,'RITMO',305,870,260,unit='u10',anchor='ritmo',motion=True)
b=block('estilo-musica',44.27,46.0)
center(b,'el estilo de',175,740,102,role='script',when=44.27);center(b,'MÚSICA',300,850,245,role='white',unit='u10',anchor='música')
b=block('coordinado',46.0,48.0)
center(b,'Todo',175,430,110,role='script',unit='u10',anchor='todo');center(b,'COORDINADO',316,870,145,unit='u10',anchor='coordinado',motion=True)
b=block('transiciones',48.13,50.67,(540,365,7,.02))
row(b,['¿y','las'],173,430,105,unit='u11');center(b,'TRANSICIONES?',294,888,151,unit='u11',anchor='transiciones')
b=block('facil',50.65,52.10)
center(b,'Muy',173,410,111,role='script',unit='u12a',anchor='muy');center(b,'FÁCIL',314,600,233,unit='u12a',anchor='fácil')
b=block('super-clean',59.40,60.30)
center(b,'SUPER',230,930,245,role='white',unit='u12c',anchor='super',layer='back');center(b,'CLEAN',520,970,315,unit='u12c',anchor='clean',layer='back')
b=block('sepa-hacer',61.55,63.24)
center(b,'que sepa',190,615,76,role='script',when=61.55);center(b,'HACER',287,768,124,when=62.05);center(b,'las cosas',433,619,63,role='script',when=62.35)
b=block('criterio',63.24,65.30)
center(b,'SI LUEGO',210,940,215,role='white',when=63.24);row(b,['No','hay'],455,480,85,unit='u13',near=63.9);center(b,'CRITERIO',565,920,170,unit='u13',anchor='criterio',motion=True)
b=block('dirigir',72.37,75.87)
word(b,'Le',207,173,138,90,'script',unit='u14b');word(b,'enseñé',366,171,407,97,'script',unit='u14b');word(b,'a',802,189,70,77,'white',unit='u14b');center(b,'DIRIGIR',308,796,245,unit='u14b',anchor='dirigir',motion=True)
b=block('boom',75.87,76.68);center(b,'¡BOOM!',365,940,335,unit='u15_16',anchor='boom',layer='back')
b=block('minutos',85.07,86.83)
word(b,'en',173,176,128,79,'white',unit='u18');word(b,'cuestión',327,158,512,104,'script',unit='u18');center(b,'de',284,150,68,role='script',unit='u18');center(b,'MINUTOS',381,824,202,unit='u18',anchor='minutos',motion=True)
b=block('cta',86.93,88.18,(540,450,10,.025))
row(b,['si','comentas'],205,730,92,unit='u19_20');center(b,'SKILL',328,836,333,unit='u19_20',anchor='skill',near=87.7,layer='back')
b=block('mando',88.18,89.34,(540,450,10,.025))
word(b,'te',330,205,150,105,'white',unit='u19_20',near=88.2);word(b,'la',590,205,150,105,'white',unit='u19_20',near=88.7);center(b,'MANDO',340,860,235,role='white',unit='u19_20',anchor='mando')
b=block('instalar',89.34,90.58,(540,450,10,.025));center(b,'y cómo',205,570,105,role='script',when=89.34);center(b,'INSTALARLA',340,850,160,role='white',unit='u19_20',anchor='instalarla')
b=block('loop',90.58,93.0333);center(b,'Porque',184,580,112,role='script',unit='u19_20',anchor='porque');center(b,'SÍ.',340,600,255,unit='u19_20',anchor='sí',near=91)

resources=[
 {'id':'ref','kind':'reference','from':183,'to':241},
 {'id':'study','kind':'study','from':446,'to':517},
 {'id':'brutos','kind':'drag','from':519,'to':639},
 {'id':'quad','kind':'quad','from':904,'to':1041},
 {'id':'hand','kind':'hand','from':1490,'to':1520},
 {'id':'bridge','kind':'bridge','from':1622,'to':1713},
 {'id':'direction','kind':'direction','from':1960,'to':2176},
 {'id':'skill','kind':'package','from':2301,'to':2400},
 {'id':'brutos2','kind':'drag','from':2400,'to':2552},
]
from fontTools.svgLib.path import parse_path
for b in blocks:
 if b['id']=='si-o-si':continue
 for low,high in [(0,900),(900,1900)]:
  words=[w for w in b['words'] if low<=w['box'][1]<high]
  rows=[]
  for w in sorted(words,key=lambda q:q['box'][1]):
   pen=BoundsPen(None);parse_path(w['path'],pen);w['_ink']=pen.bounds
   if rows and w['box'][1]<max(z['box'][1]+z['box'][3] for z in rows[-1])-20:rows[-1].append(w)
   else:rows.append([w])
  bottom=None
  for r in rows:
   top=min(w['_ink'][1] for w in r);end=max(w['_ink'][3] for w in r)
   shift=0 if bottom is None else bottom+9-top
   for w in r:
    if shift:
     pen=SVGPathPen(None);parse_path(w['path'],TransformPen(pen,(1,0,0,1,0,shift)));w['path']=pen.getCommands();w['box'][1]+=shift
    w.pop('_ink',None)
   bottom=end+shift
# Desplazamientos pedidos; también los adopta la portada de cierre.
blocks=[b for b in blocks if b['id']!='creador']
for b in blocks:
 shift={'portada':75,'coordinado':135,'dirigir':105}.get(b['id'],0)
 if shift:
  for w in b['words']:
   pen=SVGPathPen(None);parse_path(w['path'],TransformPen(pen,(1,0,0,1,0,shift)));w['path']=pen.getCommands();w['box'][1]+=shift
for b in blocks:
 for w in b['words']:w['layer']='front' if b['id']=='si-o-si' else 'back'
plan={'version':11,'fps':30,'duration':edl.get('delivery_out_frame',edl['duration']),'blocks':blocks,'resources':resources,'materials':{
 'yellow':{'fill':'#FBDD48','nearBlur':4.8,'nearOpacity':.92,'farBlur':19,'farOpacity':.54,'shadowBlur':11,'shadowOpacity':.23,'shadowY':5},
 'white':{'fill':'#FFFFFC','nearBlur':3.8,'nearOpacity':.90,'farBlur':9,'farOpacity':.48,'shadowBlur':10,'shadowOpacity':.20,'shadowY':4}},
 'script_font':{'family':'Sloop ScriptOne','file':'fonts/SloopScriptOne.ttf','source':'Archivo proporcionado por Jan en Downloads el 21-09-2026; cotejado con la muestra oficial de Adobe y referencia.'},
 'notes':['Curvatura vectorial sobre el bloque, shaping HarfBuzz con ligaduras.','Material propuesto: calibración por comparación visual antes de aprobación.','Tiempos del conformado candidato: regenerar tras cualquier cambio de voz.']}
OUT.write_text(json.dumps(plan,ensure_ascii=False,separators=(',',':')))
(P/'04-plan-director/plan-v12.json').write_text(json.dumps({**plan,'blocks':[{**b,'words':[{k:v for k,v in w.items() if k!='path'} for w in b['words']]} for b in blocks]},ensure_ascii=False,indent=2))
print('V12 (reloj fuente):',len(blocks),'bloques;',sum(len(b['words']) for b in blocks),'palabras;',edl['duration'],'frames')

