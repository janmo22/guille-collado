#!/usr/bin/env python3
"""Compone cada línea completa con HarfBuzz; revela palabras sin cambiar posiciones.

layout: {blocks:[{id,from,to,warp?,lines:[{words:[{text,at}],x,y,width,height,
role:'yellow'|'white'|'script',layer:'back'|'front'}]}]}.
Coordenadas de tinta a1080p. El autor decide apilado y jerarquía.
"""
import argparse,json
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.basePen import BasePen

class WarpPen(BasePen):
    def __init__(self,pen,box,bounds,warp):
        super().__init__(None);self.pen=pen;self.box=box;self.bounds=bounds;self.warp=warp
    def point(self,p):
        x,y,w,h=self.box;lx,by,rx,ty=self.bounds
        px=x+(p[0]-lx)*w/(rx-lx);py=y+(ty-p[1])*h/(ty-by)
        cx,cy,arch,flare=self.warp;ux=(px-cx)/480
        return round(cx+(px-cx)*(1+flare*(py-cy)/650),3),round(py+arch*(ux*ux-1),3)
    def _moveTo(self,p):self.pen.moveTo(self.point(p))
    def _lineTo(self,p):self.pen.lineTo(self.point(p))
    def _curveToOne(self,a,b,c):self.pen.curveTo(self.point(a),self.point(b),self.point(c))
    def _qCurveToOne(self,a,b):self.pen.qCurveTo(self.point(a),self.point(b))
    def _closePath(self):self.pen.closePath()
    def _endPath(self):self.pen.endPath()

def line_words(line,warp,fontdir):
    role=line['role'];font=fontdir/('SloopScriptOne.ttf' if role=='script' else 'Anton-Regular.ttf')
    ft=TTFont(font);face=hb.Face(font.read_bytes());hf=hb.Font(face);hf.scale=(face.upem,face.upem)
    glyphs=ft.getGlyphSet();order=ft.getGlyphOrder();words=line['words']
    text=' '.join(w['text'] for w in words);spans=[];offset=0
    for word in words:spans.append((offset,offset+len(word['text'])));offset+=len(word['text'])+1
    buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(hf,buf,{'kern':True,'liga':True,'calt':True})
    bounds=BoundsPen(glyphs);recordings=[DecomposingRecordingPen(glyphs) for _ in words];own=[BoundsPen(glyphs) for _ in words];x=y=0
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        tr=(1,0,0,1,x+pos.x_offset,y+pos.y_offset);g=glyphs[order[info.codepoint]];g.draw(TransformPen(bounds,tr))
        i=next((i for i,(a,z) in enumerate(spans) if a<=info.cluster<z),None)
        if i is not None:g.draw(TransformPen(recordings[i],tr));g.draw(TransformPen(own[i],tr))
        x+=pos.x_advance;y+=pos.y_advance
    if not bounds.bounds:raise ValueError('Línea sin glifos')
    lx,by,rx,ty=bounds.bounds;scale=min(line['width']/(rx-lx),line['height']/(ty-by));w=(rx-lx)*scale;h=(ty-by)*scale
    box=(line['x']+(line['width']-w)/2,line['y']+(line['height']-h)/2,w,h);result=[]
    for word,rec,bp in zip(words,recordings,own):
        if not bp.bounds:raise ValueError(f"Palabra sin glifos: {word['text']}")
        pen=SVGPathPen(None);rec.replay(WarpPen(pen,box,bounds.bounds,warp));a,b,c,d=bp.bounds
        result.append({**word,'role':role,'layer':line.get('layer','back'),'path':pen.getCommands(),
            'box':[box[0]+(a-lx)*scale,box[1]+(ty-d)*scale,(c-a)*scale,(d-b)*scale]})
    return result

def build(layout,fontdir):
    blocks=[]
    for b in layout['blocks']:
        if not b['from']<b['to']:raise ValueError(f"Intervalo vacío: {b['id']}")
        words=[w for line in b['lines'] for w in line_words(line,b.get('warp',[540,420,10,.025]),fontdir)]
        for w in words:
            if not b['from']<=w['at']<b['to']:raise ValueError(f"Onset fuera del bloque: {w['text']}")
        blocks.append({'id':b['id'],'from':b['from'],'to':b['to'],'words':words})
    return {'fps':layout.get('fps',30),'canvas':[1080,1920],'blocks':blocks}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('layout');ap.add_argument('output');ap.add_argument('--fonts',default=str(Path(__file__).resolve().parents[1]/'assets/fonts'));a=ap.parse_args()
    result=build(json.loads(Path(a.layout).read_text()),Path(a.fonts));Path(a.output).write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
    print(f"{len(result['blocks'])} bloques; posiciones reservadas por línea")

if __name__=='__main__':main()
