import React from 'react';
import {AbsoluteFill,Audio,Img,OffthreadVideo,Sequence,staticFile,useCurrentFrame,interpolate,Easing} from 'remotion';
import plan from './v13-plan.json';
import edit from './v12-edit.json';
import typeCache from './v12-type-cache.json';
import maskFrames from './v12-mask-frames.json';
const maskSet=new Set<number>(maskFrames);
import precomposed from './v12-precomposed.json';
const preSet=new Set<number>(precomposed.filter(f=>f<2608||f>=2717));
import {CameraTransitions} from './V12Transitions';
import anchors from './v12-anchor-units.json';
import {DragScene,StickerFolder,SoundDemo,Subtitles,CameraMove,CreatorProfiles,CleanShine} from './V12Scenes';

const W=1080,H=1920;
const clamp={extrapolateLeft:'clamp' as const,extrapolateRight:'clamp' as const};
const motion=(f:number,a:number,b:number,x:number,y:number)=>interpolate(f,[a,b],[x,y],{...clamp,easing:Easing.bezier(.2,.78,.2,1)});
const cover:React.CSSProperties={width:'100%',height:'100%',objectFit:'cover'};
type Word=(typeof plan.blocks)[number]['words'][number];

const Material:React.FC=()=> <defs>{Object.entries(plan.materials).map(([key,m])=><filter key={key} id={'v12-'+key} x='-15%' y='-20%' width='130%' height='140%' colorInterpolationFilters='sRGB'>
  <feGaussianBlur in='SourceAlpha' stdDeviation={m.shadowBlur} result='shadowblur'/><feOffset in='shadowblur' dx='0' dy={m.shadowY} result='offset'/><feFlood floodColor='#000' floodOpacity={m.shadowOpacity}/><feComposite in2='offset' operator='in' result='shadow'/>
  <feGaussianBlur in='SourceAlpha' stdDeviation={m.farBlur} result='far'/><feFlood floodColor={m.fill} floodOpacity={m.farOpacity}/><feComposite in2='far' operator='in' result='farcolor'/>
  <feGaussianBlur in='SourceAlpha' stdDeviation={m.nearBlur} result='near'/><feFlood floodColor={m.fill} floodOpacity={m.nearOpacity}/><feComposite in2='near' operator='in' result='nearcolor'/>
  <feGaussianBlur in='SourceGraphic' stdDeviation='0.55' result='core'/><feMerge><feMergeNode in='shadow'/><feMergeNode in='farcolor'/><feMergeNode in='nearcolor'/><feMergeNode in='core'/></feMerge>
</filter>)}</defs>;

export const TypographyVectorV13:React.FC<{layer:'front'|'back';frame?:number}>=({layer,frame})=>{
 const current=useCurrentFrame();const f=frame??(current>=2766?0:current);
 if(frame===undefined&&current>=2744&&current<2766)return null;
 const active=plan.blocks.filter(b=>f>=b.from&&f<b.to);
 let words=active.flatMap(b=>b.words.filter(w=>w.layer===layer&&f>=w.at).map(w=>({...w,block:b.id})));
 if(active.some(b=>b.id==='instalar'))words=words.filter(w=>!(w.block==='cta'&&['te','la','MANDO'].includes(w.text)));
 const brief=active.find(b=>['entera'].includes(b.id));const target=brief?anchors[brief.id==='entera'?'u05':'u07a'].y-18:0;const shift=brief?target-Math.max(...brief.words.map(w=>w.box[1]+w.box[3])):0;
 return <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position:'absolute',inset:0,overflow:'visible',pointerEvents:'none',transform:shift?`translateY(${shift}px)`:undefined}}><Material/>
  {['yellow','white'].map(role=><g key={role} filter={`url(#v12-${role})`} fill={plan.materials[role as 'yellow'|'white'].fill}>
   {words.filter(w=>(w.role==='yellow'?'yellow':'white')===role).map((w,i)=><path key={`${w.block}-${i}`} d={w.path} stroke={w.role==='script'?'#FFFFFC':undefined} strokeWidth={w.role==='script'?Math.min(5.2,w.box[3]*.04):0} strokeLinejoin='round' paintOrder='stroke fill' transform={w.motion?`translate(${motion(f,w.at,w.at+3,15,0)},0)`:undefined}/>)}
  </g>)}
 </svg>;
};

export const TypographyV13:React.FC<{layer:'front'|'back';frame?:number}>=({layer,frame})=><TypographyVectorV13 layer={layer} frame={frame}/>;

// Perspectiva en composición; la curvatura óptica se calcula en finish_lens.py.
const ScreenWarp:React.FC<{children:React.ReactNode;tilt?:number;scale?:number}>=({children,tilt=-3,scale=1})=><AbsoluteFill style={{overflow:'hidden'}}>
 <AbsoluteFill style={{transform:`perspective(2000px) rotateY(${tilt}deg) rotateX(2deg) scale(${scale})`,transformOrigin:'50% 45%'}}>{children}</AbsoluteFill>
</AbsoluteFill>;

const Caption:React.FC<{children:React.ReactNode;top?:number;bottom?:number;size?:number}>=({children,top,bottom,size=31})=><div style={{position:'absolute',left:55,right:55,top,bottom,fontFamily:'Arial',fontSize:size,fontWeight:700,letterSpacing:-.5,color:'#fff',textShadow:'0 2px 8px #0009'}}>{children}</div>;
const WindowBar:React.FC<{title:string}>=({title})=><div style={{height:83,background:'#ececeb',display:'flex',alignItems:'center',gap:13,padding:'0 35px',color:'#565652',fontFamily:'Arial',fontSize:28}}><i style={{width:17,height:17,borderRadius:20,background:'#ff6057'}}/><i style={{width:17,height:17,borderRadius:20,background:'#ffbd2f'}}/><i style={{width:17,height:17,borderRadius:20,background:'#29ca42'}}/><span style={{marginLeft:40}}>{title}</span></div>;

const Reference:React.FC<{study?:boolean}>=({study=false})=>{
 const f=useCurrentFrame();
 return <AbsoluteFill style={{background:'#eee9df'}}><ScreenWarp tilt={motion(f,0,12,-5,-1.5)} scale={motion(f,0,15,.96,1)}>
 <div style={{position:'absolute',left:105,top:170,width:870,height:1547,borderRadius:55,overflow:'hidden',boxShadow:'0 20px 55px #483f3026',border:'13px solid #faf6ec'}}>
 <OffthreadVideo src={staticFile('referencia.mp4')} trimBefore={study?2181:1108} muted style={cover}/>
 </div></ScreenWarp></AbsoluteFill>;
};

const Quad:React.FC=()=>{
 const f=useCurrentFrame();
 return <AbsoluteFill style={{background:'#efefec'}}><ScreenWarp tilt={-2} scale={1.03}>
  <WindowBar title='4 posiciones del mismo vídeo'/>
  {['A','B','C','D'].map((t,i)=>{
   const entering=motion(f,i*5,i*5+6,0,1);const x=66+(i%2)*487;const y=174+Math.floor(i/2)*783;
   return <div key={t} style={{position:'absolute',left:x,top:y+12*(1-entering),width:452,height:749,overflow:'hidden',opacity:entering,background:'#d6d6d2',boxShadow:'0 5px 14px #0002'}}>
    <OffthreadVideo src={staticFile(`bruto-${t}.mp4`)} muted style={{...cover,height:682}}/>
    <div style={{height:67,paddingTop:18,fontFamily:'Arial',fontSize:28,fontWeight:700,textAlign:'center',color:'#252524'}}>{['Frontal','Picado','Contrapicado','Plano entero'][i]}</div>
   </div>;
  })}
 </ScreenWarp></AbsoluteFill>;
};

const Laptop:React.FC=()=> <AbsoluteFill><OffthreadVideo src={staticFile('g02-laptop.mp4')} muted style={cover}/></AbsoluteFill>;
const Output:React.FC=()=> <AbsoluteFill><OffthreadVideo src={staticFile('resultado-v7.mp4')} trimBefore={24} muted style={cover}/></AbsoluteFill>;

const SubjectCutout:React.FC<{frame:number;src?:string}>=({frame,src})=>{
 if(!maskSet.has(frame))return null;
 const mask=staticFile(`person-masks/${String(frame).padStart(5,'0')}.png`);
 return <AbsoluteFill><Img src={mask} style={{...cover,position:'absolute',inset:0,opacity:0}}/><Img src={staticFile(src??`base-frames/${String(frame).padStart(5,'0')}.jpg`)} style={{...cover,position:'absolute',inset:0,maskImage:`url("${mask}")`,WebkitMaskImage:`url("${mask}")`,maskSize:'100% 100%',WebkitMaskSize:'100% 100%'}}/></AbsoluteFill>;
};
const HandTransition:React.FC=()=>{const f=useCurrentFrame(),source=1490+f,src=`hand-frames/${String(Math.min(29,f)).padStart(5,'0')}.jpg`;return preSet.has(source)?<AbsoluteFill><Img src={staticFile(`precomposed/${String(source).padStart(5,'0')}.jpg`)} style={cover}/></AbsoluteFill>:<AbsoluteFill><Img src={staticFile(src)} style={cover}/><TypographyV13 layer='back' frame={source}/><SubjectCutout frame={source} src={src}/></AbsoluteFill>;};
const Bridge:React.FC=()=>{
 const f=useCurrentFrame();const join=motion(f,73,90,0,1);
 return <AbsoluteFill style={{background:'#eee9df'}}><AbsoluteFill style={{transform:`perspective(2000px) rotateY(${-2*(1-join)}deg) rotateX(${2*(1-join)}deg)`,transformOrigin:"50% 45%"}}>
  <div style={{position:'absolute',top:250,opacity:1-join,width:1080,textAlign:'center',fontFamily:'Sloop',fontSize:116,color:'#333'}}>un plano entre los dos</div>
  {['bridge-start.jpg','bridge-mid.jpg','bridge-end.jpg'].map((src,i)=><div key={src} style={{position:'absolute',left:i===2?(54+i*329)*(1-join):54+i*329,top:i===2?550*(1-join):550+motion(f,i*3,i*3+7,40,0),width:i===2?308+772*join:308,height:i===2?700+1220*join:700,zIndex:i===2?4:1,overflow:'hidden',borderRadius:i===2?28*(1-join):28,border:i===2?`${5*(1-join)}px solid #fffaf0`:i===1?'6px solid #FBDD48':'5px solid #fffaf0',boxShadow:'0 12px 28px #45391f26',opacity:i===2?motion(f,6,12,0,1):motion(f,i*3,i*3+6,0,1)*(1-join)}}>
   <Img src={staticFile(src)} style={cover}/>
  </div>)}
  <div style={{position:'absolute',top:335,opacity:1-join,width:1080,textAlign:'center',fontFamily:'Sloop',fontSize:80,color:'#333'}}>y todo encaja</div>
 </AbsoluteFill></AbsoluteFill>;
};

const Direction:React.FC=()=>{
 const f=useCurrentFrame();const scroll=motion(f,24,191,0,1170);
 return <AbsoluteFill style={{background:'#eee9df',clipPath:`circle(${motion(f,0,10,0,125)}% at 50% 42%)`}}><ScreenWarp tilt={motion(f,0,16,-5,-1.5)} scale={motion(f,0,16,.96,1)}>
 <div style={{position:'absolute',left:85,top:190,width:910,height:1520,background:'#fff',border:'13px solid #faf6ec',borderRadius:48,overflow:'hidden',boxShadow:'0 20px 55px #483f3026'}}>
 <Img src={staticFile('instagram-scroll-real.png')} style={{position:'absolute',width:1540,maxWidth:'none',height:'auto',left:-315,top:-scroll}}/>
 </div></ScreenWarp></AbsoluteFill>;
};

const Resource:React.FC<{kind:string;again?:boolean}>=({kind,again=false})=>kind==='creators'?<CreatorProfiles/>:kind==='reference'?<Reference/>:kind==='study'?<Reference study/>:kind==='quad'?<Quad/>:kind==='laptop'?<Laptop/>:kind==='output'?<Output/>:kind==='hand'?<HandTransition/>:kind==='bridge'?<Bridge/>:kind==='direction'?<Direction/>:kind==='package'?<StickerFolder/>:kind==='drag'?<DragScene again={again}/>:null;

// El acabado angular se aplica a precisión flotante en finish_lens.py.
// Se mantiene una sola transformación final para persona, matte, fondo y texto.
const HeroLens:React.FC<{children:React.ReactNode;enabled?:boolean}>=({children})=><>{children}</>;

export const TimelineV13:React.FC<{proof?:boolean}>=({proof=false})=>{
 const f=useCurrentFrame();const resource=!proof&&plan.resources.find(r=>f>=r.from&&f<r.to);
 const hero=!resource||['hand','laptop','emphasis'].includes(resource.kind);const emphasis=!!resource&&resource.kind==='emphasis';
 return <AbsoluteFill style={{background:'#151614',overflow:'hidden'}}>
 <CameraMove><HeroLens enabled={hero}>
  <Img src={staticFile(preSet.has(f)?`precomposed/${String(f).padStart(5,'0')}.jpg`:`base-frames/${String(f).padStart(5,'0')}.jpg`)} style={cover}/>
  {(!resource||emphasis)?<>{!preSet.has(f)&&<><TypographyV13 layer='back'/><CleanShine/></>}
   <Sequence from={318} durationInFrames={63}><CreatorProfiles/></Sequence>
   {!preSet.has(f)&&<SubjectCutout frame={f}/>}<TypographyV13 layer='front'/><SoundDemo/>
  </>:<Sequence from={resource.from} durationInFrames={resource.to-resource.from}><Resource kind={resource.kind} again={resource.id==='brutos2'}/></Sequence>}
 </HeroLens></CameraMove><Subtitles resource={!!resource}/>
 </AbsoluteFill>;
};
export const V13_DURATION=edit.duration;
export const VideoV13:React.FC<{proof?:boolean}>=({proof=false})=><AbsoluteFill style={{background:'#eee9df'}}>
<style>{`@font-face{font-family:Sloop;src:url('${staticFile('fonts/SloopScriptOne.ttf')}')}@font-face{font-family:SubtitleGuille;src:url('${staticFile('fonts/Toledo-Serial-BoldItalic.ttf')}');font-weight:700;font-style:italic}@font-face{font-family:Anton;src:url('${staticFile('fonts/Anton-Regular.ttf')}')}`}</style>
<CameraTransitions>{edit.segments.map(seg=><Sequence key={seg.source} from={seg.from} durationInFrames={seg.duration}><Sequence from={-seg.source}><TimelineV13 proof={proof}/></Sequence></Sequence>)}</CameraTransitions>
<Audio src={staticFile('master-v12-entrega.wav')}/>
</AbsoluteFill>;
