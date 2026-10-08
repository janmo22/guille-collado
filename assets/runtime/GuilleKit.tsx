import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate, Easing} from 'remotion';

const clamp={extrapolateLeft:'clamp' as const,extrapolateRight:'clamp' as const};
export const ease=(f:number,a:number,b:number,x:number,y:number)=>interpolate(f,[a,b],[x,y],{...clamp,easing:Easing.bezier(.22,.8,.2,1)});
export const COLORS={cream:'#eee9df',paper:'#faf6ec',yellow:'#FBDD48',white:'#FFFFFC',ink:'#302e29'};
export const Fonts:React.FC<{base?:string}>=({base='guille/fonts'})=><style>{`
@font-face{font-family:Anton;src:url('${staticFile(`${base}/Anton-Regular.ttf`)}')}
@font-face{font-family:Sloop;src:url('${staticFile(`${base}/SloopScriptOne.ttf`)}')}
@font-face{font-family:SubtitleGuille;src:url('${staticFile(`${base}/Toledo-Serial-BoldItalic.ttf`)}');font-weight:700;font-style:italic}
`}</style>;

export type Material={fill:string;nearBlur:number;nearOpacity:number;farBlur:number;farOpacity:number;shadowBlur:number;shadowOpacity:number;shadowY:number};
export const MATERIALS:Record<'yellow'|'white',Material>={
 yellow:{fill:COLORS.yellow,nearBlur:4.8,nearOpacity:.92,farBlur:19,farOpacity:.54,shadowBlur:11,shadowOpacity:.23,shadowY:5},
 white:{fill:COLORS.white,nearBlur:3.8,nearOpacity:.9,farBlur:9,farOpacity:.48,shadowBlur:10,shadowOpacity:.2,shadowY:4},
};
export type Word={text:string;at:number;path:string;role:string;layer:'back'|'front';box:number[]};
export type Block={id:string;from:number;to:number;words:Word[]};
const MaterialFilter:React.FC<{id:string;m:Material}>=({id,m})=><filter id={id} x='-15%' y='-20%' width='130%' height='140%' colorInterpolationFilters='sRGB'>
 <feGaussianBlur in='SourceAlpha' stdDeviation={m.shadowBlur} result='sb'/><feOffset in='sb' dy={m.shadowY} result='off'/><feFlood floodColor='#000' floodOpacity={m.shadowOpacity}/><feComposite in2='off' operator='in' result='shadow'/>
 <feGaussianBlur in='SourceAlpha' stdDeviation={m.farBlur} result='fb'/><feFlood floodColor={m.fill} floodOpacity={m.farOpacity}/><feComposite in2='fb' operator='in' result='far'/>
 <feGaussianBlur in='SourceAlpha' stdDeviation={m.nearBlur} result='nb'/><feFlood floodColor={m.fill} floodOpacity={m.nearOpacity}/><feComposite in2='nb' operator='in' result='near'/>
 <feGaussianBlur in='SourceGraphic' stdDeviation='.55' result='core'/><feMerge><feMergeNode in='shadow'/><feMergeNode in='far'/><feMergeNode in='near'/><feMergeNode in='core'/></feMerge>
</filter>;

/** Geometry is authored as one complete phrase; onset changes visibility only. */
export const Typography:React.FC<{blocks:Block[];layer:'front'|'back';id:string;frame?:number;materials?:typeof MATERIALS}>=({blocks,layer,id,frame,materials=MATERIALS})=>{
 const current=useCurrentFrame(),f=frame??current;
 const words=blocks.filter(b=>f>=b.from&&f<b.to).flatMap(b=>b.words.filter(w=>w.layer===layer&&f>=w.at));
 return <svg width={1080} height={1920} viewBox='0 0 1080 1920' style={{position:'absolute',inset:0,overflow:'visible',pointerEvents:'none'}}>
  <defs>{(['yellow','white'] as const).map(role=><MaterialFilter key={role} id={`${id}-${role}`} m={materials[role]}/>)}</defs>
  {(['yellow','white'] as const).map(role=><g key={role} fill={materials[role].fill} filter={`url(#${id}-${role})`}>
   {words.filter(w=>(w.role==='yellow'?'yellow':'white')===role).map((w,i)=><path key={i} d={w.path} stroke={w.role==='script'?COLORS.white:undefined} strokeWidth={w.role==='script'?Math.min(5.2,w.box[3]*.04):0} strokeLinejoin='round' paintOrder='stroke fill'/>)}
  </g>)}
 </svg>;
};

/** src/mask are staticFile results or URLs. Same frame, same full-frame transform. */
export const SubjectLayers:React.FC<{src:string;mask:string;behind?:React.ReactNode;front?:React.ReactNode}>=({src,mask,behind,front})=>{
 const cover:React.CSSProperties={position:'absolute',inset:0,width:'100%',height:'100%',objectFit:'cover'};
 return <AbsoluteFill><Img src={src} style={cover}/>{behind}<Img src={mask} style={{...cover,opacity:0}}/><Img src={src} style={{...cover,maskImage:`url("${mask}")`,WebkitMaskImage:`url("${mask}")`,maskSize:'100% 100%',WebkitMaskSize:'100% 100%'}}/>{front}</AbsoluteFill>;
};

export const Camera:React.FC<{children:React.ReactNode;from:number;to:number;start?:number;end?:number;frame?:number}>=({children,from,to,start=1.012,end=1.067,frame})=>{
 const f=useCurrentFrame();const scale=interpolate(frame??f,[from,Math.max(from+1,to)],[start,end],clamp);
 return <AbsoluteFill style={{transform:`scale(${scale})`,transformOrigin:'50% 46%'}}>{children}</AbsoluteFill>;
};

export const CreamCard:React.FC<{children:React.ReactNode;x?:number;y?:number;width?:number;height?:number;radius?:number;tilt?:number}>=({children,x=105,y=170,width=870,height=1547,radius=55,tilt=-1.5})=><AbsoluteFill style={{background:COLORS.cream}}>
 <AbsoluteFill style={{transform:`perspective(2000px) rotateY(${tilt}deg) rotateX(2deg)`,transformOrigin:'50% 45%'}}>
 <div style={{position:'absolute',left:x,top:y,width,height,borderRadius:radius,overflow:'hidden',border:`13px solid ${COLORS.paper}`,boxShadow:'0 20px 55px #483f3026'}}>{children}</div>
 </AbsoluteFill></AbsoluteFill>;

export type Caption={from:number;to:number;text:string;y?:number};
export const Subtitles:React.FC<{captions:Caption[];resource?:boolean;frame?:number}>=({captions,resource=false,frame})=>{
 const current=useCurrentFrame(),f=frame??current,c= captions.find(v=>f>=v.from&&f<v.to);if(!c)return null;
 return <div style={{position:'absolute',left:95,right:95,top:c.y??(resource?1440:1035),transform:'translateY(-50%)',textAlign:'center',color:'#F8D850',fontFamily:'SubtitleGuille',fontSize:44,fontWeight:700,fontStyle:'italic',lineHeight:1.08,whiteSpace:'pre-line',WebkitTextStroke:'3.5px #17130d',paintOrder:'stroke fill',textShadow:'1px 5px 0 #100b06,2px 7px 3px #000c,0 2px 9px #0008'}}>{c.text}</div>;
};
