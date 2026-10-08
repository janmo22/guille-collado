import React from 'react';
import {AbsoluteFill,OffthreadVideo,Sequence,staticFile,useCurrentFrame,interpolate} from 'remotion';
import edit from './v12-edit.json';
const map=(source:number)=>{const s=edit.segments.find(x=>source>=x.source&&source<x.end)??edit.segments.find(x=>x.source>=source);return s?s.from+Math.max(0,source-s.source):edit.duration;};
const Move:React.FC<{file:string;startScale:number;endScale:number}>=({file,startScale,endScale})=>{const f=useCurrentFrame();return <AbsoluteFill style={{transform:`scale(${interpolate(f,[0,15],[startScale,endScale],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})})`,transformOrigin:'50% 46%'}}><OffthreadVideo src={staticFile(file)} muted style={{width:'100%',height:'100%',objectFit:'cover'}}/></AbsoluteFill>;};
export const CameraTransitions:React.FC<{children:React.ReactNode}>=({children})=>{
 const f=useCurrentFrame();let zoom=1,tilt=0;
 for(const source of [1817,2176]){const t=f-map(source);if(t>=-4&&t<8){const p=(t+4)/12;const pulse=Math.sin(p*Math.PI);zoom=1+.022*pulse;tilt=.32*pulse*(t<0?1:-1);}}
 return <AbsoluteFill><AbsoluteFill style={{transform:`scale(${zoom}) rotate(${tilt}deg)`,transformOrigin:'50% 46%'}}>{children}</AbsoluteFill>
 <Sequence from={map(147)-6} durationInFrames={16}><Move file='inicio-ia-v12.mp4' startScale={1.076} endScale={1.018}/></Sequence>
 <Sequence from={map(1041)-6} durationInFrames={16}><Move file='genial-ia-v12.mp4' startScale={1} endScale={1}/></Sequence>
 <Sequence from={map(1106)-6} durationInFrames={16}><Move file='camara-transicion.mp4' startScale={1.026} endScale={1.030}/></Sequence>
 </AbsoluteFill>;
};
