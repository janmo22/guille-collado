import React from 'react';
import {AbsoluteFill,Img,OffthreadVideo,Sequence,staticFile,useCurrentFrame,interpolate,Easing} from 'remotion';
import captions from './v12-subtitles.json';
import plan from './v12-plan.json';
import edit from './v12-edit.json';
import anchors from './v12-anchor-units.json';
import units from './v12-units.json';
const clamp={extrapolateLeft:'clamp' as const,extrapolateRight:'clamp' as const};
const m=(f:number,a:number,b:number,x:number,y:number)=>interpolate(f,[a,b],[x,y],{...clamp,easing:Easing.bezier(.22,.8,.2,1)});
const cream='#eee9df',ink='#302e29',yellow='#FBDD48';
const shadow='0 7px 16px #41372424';
const panel:React.CSSProperties={background:'#faf7f0',borderRadius:38,boxShadow:shadow};
const Hand:React.FC<{x:number;y:number;closed:boolean}>=({x,y,closed})=><svg width="110" height="125" viewBox="0 0 90 110" style={{position:'absolute',left:x,top:y,filter:'drop-shadow(0 3px 2px #0004)'}}><path d={closed?'M22 55 L22 29 Q22 19 30 20 Q38 20 38 29 L38 42 L38 24 Q40 17 47 21 L49 42 L50 28 Q54 21 61 26 L64 45 Q70 35 76 42 L78 61 Q77 76 64 86 L63 98 L32 98 L29 86 Q12 73 10 63 Q10 53 18 53 Z':'M26 60 L26 18 Q26 8 34 8 Q43 8 43 18 L43 49 L46 32 Q53 24 58 34 L58 51 L62 39 Q69 33 73 43 L74 58 Q79 48 84 56 L83 75 Q80 89 64 96 L64 105 L34 105 L29 95 Q10 79 8 69 Q7 59 15 57 Z'} fill='#fff' stroke='#181818' strokeWidth='3.3' strokeLinejoin='round'/><path d="M39 70 L39 84 M51 66 L51 85 M63 65 L62 81" stroke="#aaa" strokeWidth="2"/></svg>;

export const DragScene:React.FC<{again?:boolean}>=({again=false})=>{
 const current=useCurrentFrame();const f=current+(again?15:0);const grab=22,drop=72,p=m(f,grab+4,drop,0,1),s=m(f,grab+4,drop,1,.50);const attached=f>=drop;const sent=f>=104;const sending=m(f,104,116,0,1);const cameraScale=f<grab?m(f,0,grab,1,1.055):f<drop?m(f,grab,drop,1.055,1.12):m(f,drop,drop+13,1.12,1.07);const cameraY=f<grab?m(f,0,grab,12,28):f<drop?m(f,grab,drop,28,-72):m(f,drop,drop+13,-72,-48);
 if(again&&f>=116){const reveal=m(f,116,123,0,1),zoom=m(f,142,161,0,1);return <AbsoluteFill style={{background:cream,color:ink}}><AbsoluteFill style={{transform:`perspective(2000px) rotateY(${-3+zoom*2}deg) rotateX(${1-zoom}deg)`}}>
  <div style={{position:'absolute',top:120,width:1080,textAlign:'center',fontFamily:'Sloop',fontSize:91}}>el vídeo, listo</div>
  <div style={{position:'absolute',left:110,right:110,top:300,bottom:210,...panel,opacity:1-zoom}}/>
  <div style={{position:'absolute',left:160,top:350,fontFamily:'Georgia',fontSize:53,opacity:1-zoom}}><span style={{color:'#c56b4d'}}>✳</span> Claude</div>
  <div style={{position:'absolute',left:160,top:428,fontFamily:'Arial',fontSize:46,opacity:reveal*(1-zoom),transform:`translateY(${(1-reveal)*12}px)`}}>Aquí lo tienes.</div>
  <div style={{position:'absolute',left:298-70*zoom,top:530-290*zoom,width:484+140*zoom,height:860+250*zoom,borderRadius:32+10*zoom,border:'10px solid #faf6ec',boxShadow:shadow,overflow:'hidden',opacity:reveal,transform:`translateY(${(1-reveal)*24}px)`}}><Sequence from={101} layout='none'><OffthreadVideo src={staticFile('resultado-v12.mp4')} muted style={{width:'100%',height:'100%',objectFit:'cover'}}/></Sequence></div>
 </AbsoluteFill></AbsoluteFill>;}

 return <AbsoluteFill style={{background:cream,color:ink}}><div style={{position:'absolute',top:210,width:1080,textAlign:'center',fontFamily:'Sloop',fontSize:105,zIndex:2}}>{again?'y Claude lo edita':'solo mis brutos'}</div><AbsoluteFill style={{transform:`perspective(2000px) rotateY(${m(f,0,15,-5,-1)}deg) rotateX(${m(f,grab,drop,3,-1)}deg) translateY(${cameraY}px) scale(${cameraScale})`}}>
 
 <div style={{position:'absolute',left:80,top:740,width:920,height:630,...panel,padding:45,boxSizing:'border-box'}}>
  <div style={{fontFamily:'Georgia',fontSize:61,marginBottom:40}}><span style={{color:'#c56b4d'}}>✳</span> Claude</div>
  <div style={{fontFamily:'Georgia',fontSize:39,color:'#6a645b',marginBottom:38,opacity:1-sending}}>¿Qué vamos a crear?</div>
  <div style={{position:'relative',height:310-70*sending,borderRadius:28,transform:`translateY(${-sending*95}px) scale(${1-sending*.08})`,transformOrigin:'50% 0%',background:sent?'#eee7dc':'#fffdf8',border:`2px solid ${f>=grab&&f<drop?'#c56b4d':'#d7d0c4'}`,boxShadow:f>=grab&&f<drop?'0 0 0 5px #c56b4d17':'none'}}>
   {attached&&<div style={{position:'absolute',left:23,top:21,display:'flex',gap:16}}>{['A','B','C','D'].map(t=><div key={t} style={{width:152,height:112,border:'1px solid #d8d0c2',borderRadius:14,overflow:'hidden',background:cream}}><Img src={staticFile(`bruto-${t}.jpg`)} style={{width:152,height:76,objectFit:'cover'}}/><div style={{fontFamily:'Arial',fontSize:19,padding:'6px 10px'}}>toma-{t}.mp4</div></div>)}</div>}
   <div style={{position:'absolute',left:28,top:attached?160:45,fontFamily:'Arial',fontSize:30,color:attached?ink:'#9a9387'}}>{sent?'✓ Enviado a Claude':attached?'Edita estos 4 brutos con mi skill.':'Arrastra aquí los archivos'}</div>
   {!sent&&<div style={{position:'absolute',left:30,bottom:25,fontFamily:'Arial',fontSize:35}}>＋</div>}<div style={{position:'absolute',right:22,bottom:20,width:54,height:54,borderRadius:13,background:sent?'#787c61':'#c56b4d',color:'#fff',fontFamily:'Arial',fontSize:38,textAlign:'center',transform:`scale(${f>=102&&f<106?.88:1})`}}>{sent?'✓':'↑'}</div>
  </div>
 </div>
 {!attached&&<div style={{position:'absolute',left:m(f,grab+4,drop,85,307),top:m(f,grab+4,drop,375,863),width:910,height:500,transform:`scale(${s}) rotate(${Math.sin(p*Math.PI)*-4}deg)`,transformOrigin:'0 0'}}>
 {['A','B','C','D'].map((t,i)=><div key={t} style={{position:'absolute',left:i*225,top:Math.sin(i)*13,width:206,height:395,borderRadius:18,border:f>=grab?'4px solid #4b8df6':'4px solid #fff',background:'#fff',boxShadow:shadow,transform:`rotate(${[-4,2,-2,5][i]}deg)`}}><Img src={staticFile(`bruto-${t}.jpg`)} style={{width:'100%',height:336,objectFit:'cover',borderRadius:'14px 14px 0 0'}}/><div style={{fontFamily:'Arial',fontSize:22,textAlign:'center',paddingTop:14}}>toma-{t}.mp4</div></div>)}
 </div>}
 <div style={{opacity:f>108?m(f,108,119,1,0):1}}><Hand x={f>=drop?m(f,78,102,655,855):f<grab?m(f,0,grab,920,520):m(f,grab+4,drop,520,655)} y={f>=drop?m(f,78,102,1100,1235):f<grab?m(f,0,grab,790,585):m(f,grab+4,drop,585,1100)} closed={(f>=grab&&f<drop)||(f>=102&&f<106)}/></div>
 {again&&f>106&&<div style={{position:'absolute',left:148,right:148,top:1280,height:75,borderRadius:18,background:'#faf7f0',fontFamily:'Georgia',fontSize:31,color:'#625a4e',display:'flex',alignItems:'center',gap:20,padding:'0 25px'}}><span style={{display:'inline-block',transform:`rotate(${f*4}deg)`,color:'#c56b4d',fontSize:43}}>✳</span>Aplicando la skill a las cuatro tomas…</div>}
 </AbsoluteFill></AbsoluteFill>;
};

const symbols=['♫','Aa','✦','≋'];
export const StickerFolder:React.FC=()=>{
 const f=useCurrentFrame();const closed=f>=77;
 return <AbsoluteFill style={{background:cream,color:ink}}><div style={{position:'absolute',top:190,width:1080,textAlign:'center',fontFamily:'Sloop',fontSize:130}}>todo en una skill</div>
 <svg width="900" height="670" viewBox="0 0 900 670" style={{position:'absolute',left:90,top:900,filter:'drop-shadow(0 12px 7px #0002)'}}><path d="M105 92 Q105 54 144 56 L345 58 L399 115 L747 115 Q789 112 790 159 L779 548 Q778 581 743 581 L139 579 Q98 578 99 537Z" fill="#e4c564" stroke="white" strokeWidth="22" strokeLinejoin="round"/><path d="M105 92 Q105 54 144 56 L345 58 L399 115 L747 115 Q789 112 790 159 L779 548 Q778 581 743 581 L139 579 Q98 578 99 537Z" fill="none" stroke="#443a28" strokeWidth="4"/></svg>
 {['música','texto','estilo','volumen'].map((name,i)=>{
 const p=m(f,32+i*8,57+i*8,0,1);const x0=85+(i%2)*500,y0=430+Math.floor(i/2)*325;return <div key={name} style={{position:'absolute',left:x0+(400-x0)*p,top:y0+(1240-y0)*p,width:410,height:245,background:['#e9ebf7','#fff','#e6efd3','#f4e0d1'][i],border:'13px solid white',borderRadius:[45,29,55,32][i],boxShadow:shadow,transform:`rotate(${[-7,6,4,-5][i]+p*18}deg) scale(${1-p*.62})`,opacity:p>.94?m(p,.94,1,1,0):m(f,i*3,i*3+4,0,1),display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column'}}><span style={{fontFamily:i===1?'Sloop':'Georgia',fontSize:110,lineHeight:1}}>{symbols[i]}</span><span style={{fontFamily:'Sloop',fontSize:64}}>{name}</span></div>;
 })}
 <svg width="900" height="670" viewBox="0 0 900 670" style={{position:'absolute',left:90,top:900,transform:`scaleY(${m(f,74,84,.8,1)})`,transformOrigin:'50% 85%',filter:'drop-shadow(0 6px 4px #0002)'}}><path d="M93 264 Q91 227 133 229 L771 221 Q812 222 807 265 L778 548 Q774 581 741 581 L133 579 Q97 578 93 541Z" fill="#f6d975" stroke="white" strokeWidth="21" strokeLinejoin="round"/><path d="M93 264 Q91 227 133 229 L771 221 Q812 222 807 265 L778 548 Q774 581 741 581 L133 579 Q97 578 93 541Z" fill="none" stroke="#443a28" strokeWidth="4"/><text x="450" y="454" textAnchor="middle" fontFamily="Sloop" fontSize="117" fill="#393321">guille-collado</text></svg>
 {closed&&<div style={{position:'absolute',left:785,top:1320,transform:`rotate(12deg) scale(${m(f,77,82,.6,1)})`,fontSize:97,color:'#76914d',textShadow:'-5px 0 white,5px 0 white,0 -5px white,0 5px white'}}>✦</div>}
 </AbsoluteFill>;
};

export const SoundDemo:React.FC=()=>{
 const f=useCurrentFrame();if(f<1239||f>=1398)return null;
 const rhythm=f>=1288&&f<1328;const music=f>=1328;const local=f-1239;
 return <div style={{position:'absolute',left:335,top:1345,width:410,height:100,borderRadius:32,background:'#f7f1e8eb',boxShadow:shadow,transform:`rotate(-3deg) scale(${m(local,0,5,.8,1)})`,display:'flex',alignItems:'center',justifyContent:'center',gap:9}}>
 {Array.from({length:23},(_,i)=><div key={i} style={{width:10,borderRadius:8,height:rhythm?(i%6===Math.floor((f-1288)/16)%6?68:16):music?20+Math.abs(Math.sin(f*.25+i*.75))*62:14+Math.exp(-(((i-11)/5)**2))*95*Math.abs(Math.sin(f*.41+i)),background:rhythm?'#c56b4d':ink}}/>)}
 </div>;
};

export const Subtitles:React.FC<{resource?:boolean}>=({resource=false})=>{
 const f=useCurrentFrame();const c=captions.find(q=>f>=q.from&&f<q.to);if(!c)return null;
 const text=c.words.map(w=>w.text).join(' ');const subtitleTop=f>=1897&&f<1959?1490:c.from<1398&&c.to>1239?1270:1035;
 return <div style={{position:'absolute',left:95,right:95,top:resource?1440:subtitleTop,textAlign:'center',color:'#F8D850',fontFamily:'SubtitleGuille',fontSize:44,fontStyle:'italic',fontWeight:700,lineHeight:1.08,letterSpacing:0,whiteSpace:'nowrap',WebkitTextStroke:'3.5px #17130d',paintOrder:'stroke fill',textShadow:'1px 5px 0px #100b06, 2px 7px 3px #000c, 0px 2px 9px #0008',transform:'translateY(-50%)'}}>{text}</div>;
};

export const CameraMove:React.FC<{children:React.ReactNode}>=({children})=>{
 const f=useCurrentFrame();let u=units.find(q=>f>=q.from&&f<q.to)??units[0];let start=u.from,end=u.to;const index=units.indexOf(u);
 for(let i=index-1;i>=0&&units[i].take===u.take;i--)start=units[i].from;
 for(let i=index+1;i<units.length&&units[i].take===u.take;i++)end=units[i].to;
 if(f>=2605)end=2780;
 const progress=Math.max(0,Math.min(1,(f-start)/Math.max(1,end-start)));
 const scale=f>=1622&&f<1713?1.012:f<147?1.055+progress*.035:f>=2605?1+progress*.055:1.012+progress*.055;
 return <AbsoluteFill style={{transform:`scale(${scale})`,transformOrigin:'50% 46%'}}>{children}</AbsoluteFill>;
};

export const CreatorProfiles:React.FC=()=>{
 const f=useCurrentFrame(),reveal=m(f,25,35,0,1);const points=[[180,470],[900,470],[540,430],[180,860],[900,860]];
 return <AbsoluteFill style={{color:ink}}>
  <AbsoluteFill style={{transform:`perspective(2200px) rotateY(${m(f,0,18,-4,0)}deg) scale(${m(f,0,62,.98,1.045)})`}}>
  {points.map(([x,y],i)=>{const chosen=i===2,size=chosen?260+200*reveal:230;const enter=m(f,i*2,i*2+7,0,1);return <div key={i} style={{position:'absolute',left:x-size/2,top:y-size/2,width:size,height:size,opacity:enter*(chosen?1:1-.65*reveal),transform:`translateY(${(1-enter)*25}px)`,filter:chosen?'none':`blur(${reveal*4}px)`,zIndex:chosen?4:1}}>
   <div style={{width:'100%',height:'100%',borderRadius:'50%',overflow:'hidden',background:'#d5d0c7',border:`${chosen?8:5}px solid ${chosen&&reveal>0?'#FBDD48':'#fffaf0'}`,boxShadow:chosen?`0 0 ${reveal*40}px #FBDD48,0 8px 25px #40372222`:shadow}}>
   {chosen?<Img src={staticFile('guille-avatar.jpg')} style={{width:'100%',height:'100%',objectFit:'cover',filter:`blur(${(1-reveal)*22}px) grayscale(${1-reveal})`,opacity:.35+.65*reveal}}/>:<svg width='100%' height='100%' viewBox='0 0 230 230'><rect width='230' height='230' fill={['#c8c2b3','#bab9b0','#c8c2b3','#b8bdc3','#cbb9ad'][i]}/><circle cx='115' cy='87' r='43' fill='#6f706b'/><ellipse cx='115' cy='217' rx='82' ry='79' fill='#6f706b'/></svg>}
   <div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',fontFamily:'Anton',fontSize:140,color:'#fffaf0',textShadow:'0 3px 8px #0005',opacity:chosen?1-reveal:1}}>?</div>
   </div>
  </div>})}</AbsoluteFill>
 </AbsoluteFill>;
};

export const CleanShine:React.FC=()=>{
 const f=useCurrentFrame(),start=1793;if(f<start||f>start+20)return null;const p=m(f,start,start+16,0,1);
 return <AbsoluteFill style={{pointerEvents:'none',overflow:'hidden'}}>
 <div style={{position:'absolute',left:-300+p*1700,top:320,width:110,height:630,transform:'rotate(22deg)',background:'linear-gradient(90deg,transparent,#fffdf8cc,transparent)',filter:'blur(7px)',opacity:Math.sin(p*Math.PI),mixBlendMode:'screen'}}/>
 {[0,1,2].map((i)=><svg key={i} width={85-i*10} height={85-i*10} viewBox='0 0 100 100' style={{position:'absolute',left:[220,820,740][i],top:[460,710,350][i],opacity:Math.max(0,Math.sin((f-start-i*3)/13*Math.PI)),transform:`scale(${Math.max(0,Math.sin((f-start-i*3)/13*Math.PI))})`,filter:'drop-shadow(0 0 8px white)'}}><path d='M50 0 Q54 44 100 50 Q54 55 50 100 Q45 55 0 50 Q44 45 50 0' fill='white'/></svg>)}
 </AbsoluteFill>;
};
