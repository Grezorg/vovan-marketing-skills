import React from 'react';
import {AbsoluteFill, Composition, Sequence, interpolate, registerRoot, useCurrentFrame} from 'remotion';

const C={bg:'#090e18',fg:'#f4f5f0',muted:'#9ba7b8',orange:'#ff784f',red:'#ff686c',green:'#79e8b1'};
const Label=({children,color=C.muted}:{children:React.ReactNode;color?:string})=><div style={{fontSize:27,fontWeight:700,letterSpacing:3,color,textTransform:'uppercase'}}>{children}</div>;
const Title=({children,color=C.fg,size=102}:{children:React.ReactNode;color?:string;size?:number})=><div style={{fontSize:size,lineHeight:1.08,fontWeight:800,letterSpacing:-3,color,whiteSpace:'pre-line'}}>{children}</div>;
const Note=({children}:{children:React.ReactNode})=><div style={{fontSize:38,lineHeight:1.4,color:C.muted,marginTop:36}}>{children}</div>;
const Panel=({children,color='#364050'}:{children:React.ReactNode;color?:string})=><div style={{border:'2px solid '+color,borderRadius:28,padding:40,background:'#111926'}}>{children}</div>;
const Scene=({children}:{children:React.ReactNode})=>{const f=useCurrentFrame();return <AbsoluteFill style={{padding:'380px 96px 0',transform:`translateY(${interpolate(f,[0,9],[26,0],{extrapolateRight:'clamp'})}px)`}}>{children}</AbsoluteFill>};

const TestCard=({name}:{name:string})=><Panel><Label>{name}</Label><div style={{fontSize:49,lineHeight:1.3,fontWeight:700,marginTop:22}}>Как сделать рекламу<br/>без бюджета</div></Panel>;

const Reel=()=>{
 const f=useCurrentFrame();
 const bars=[84,156,300,390,492,600,705,780];
 return <AbsoluteFill style={{background:C.bg,color:C.fg,fontFamily:'DejaVu Sans, sans-serif'}}>
  <AbsoluteFill style={{background:`radial-gradient(ellipse at ${70-35*Math.sin(f/180)}% 45%,#24344c66,transparent 68%)`}}/>
  <div style={{position:'absolute',top:110,left:96,right:96,display:'flex',justifyContent:'space-between',alignItems:'center'}}>
   <div style={{fontSize:31,fontWeight:800,letterSpacing:2}}>НЕЙРОСЕТИ И ТВОРЧЕСТВО</div>
   <div style={{width:14,height:14,borderRadius:'50%',background:C.orange,boxShadow:'0 0 24px #ff784f'}}/>
  </div>
  <div style={{position:'absolute',top:175,left:96,fontSize:28,color:C.muted}}>@Grezorg · проверка на деле</div>

  <Sequence from={0} durationInFrames={84}><Scene>
   <Label color={C.orange}>Обещают в роликах</Label>
   <div style={{marginTop:55}}><Title size={112}>{'ИИ ВЕДЁТ\nКАНАЛ\nЗА ТЕБЯ?'}</Title></div>
   <div style={{marginTop:70,display:'inline-block',padding:'22px 30px',borderRadius:14,background:C.orange,color:C.bg,fontSize:39,fontWeight:800}}>Я ПРОВЕРИЛ</div>
  </Scene></Sequence>

  <Sequence from={84} durationInFrames={72}><Scene>
   <div style={{fontSize:350,lineHeight:1,fontWeight:800,color:C.orange,letterSpacing:-25}}>11</div>
   <Title size={83}>{'навыков\nдля YouTube'}</Title>
   <Note>Но одна проверка<br/>не справилась с русским.</Note>
  </Scene></Sequence>

  <Sequence from={156} durationInFrames={144}><Scene>
   <Title size={79}>{'ДАЮ ОДИН\nИ ТОТ ЖЕ ТЕКСТ'}</Title>
   <div style={{marginTop:48}}><TestCard name="Заголовок"/></div>
   <div style={{marginTop:24}}><TestCard name="Текст обложки"/></div>
   <Note>Повторение очевидно.</Note>
  </Scene></Sequence>

  <Sequence from={300} durationInFrames={90}><Scene>
   <Label color={C.red}>Ответ исходного инструмента</Label>
   <div style={{marginTop:48}}><Title color={C.red} size={96}>{'«СЛОВА\nРАЗНЫЕ»'}</Title></div>
   <div style={{marginTop:55}}><Panel color={C.red}><Label>Распознанные слова</Label><div style={{fontSize:160,lineHeight:1.2,fontWeight:800,marginTop:10}}>[ ]</div></Panel></div>
   <Note>Перевод результата настоящего теста.<br/>Русские слова не распознаны.</Note>
  </Scene></Sequence>

  <Sequence from={390} durationInFrames={102}><Scene>
   <Label color={C.orange}>Причина нашлась в коде</Label>
   <div style={{marginTop:48}}><Title size={88}>{'ФИЛЬТР\nТОЛЬКО ДЛЯ\nЛАТИНИЦЫ'}</Title></div>
   <div style={{marginTop:55}}><Panel color={C.orange}><div style={{fontFamily:'DejaVu Sans Mono, monospace',fontSize:72,fontWeight:700,color:C.orange}}>{"[a-z0-9']+"}</div></Panel></div>
   <Note>Кириллица просто<br/>не попадает в список слов.</Note>
  </Scene></Sequence>

  <Sequence from={492} durationInFrames={108}><Scene>
   <Label color={C.green}>Наша русская адаптация</Label>
   <div style={{marginTop:48}}><Title color={C.green} size={101}>{'ПОВТОР\nНАЙДЕН'}</Title></div>
   <div style={{marginTop:55}}><Panel color={C.green}><Label>Совпадения из реального теста</Label><div style={{fontSize:49,lineHeight:1.45,marginTop:24,fontWeight:700}}>рекламу · сделать<br/>бюджета · без</div></Panel></div>
   <Note>Исправили обработку текста.<br/>Проверили результат.</Note>
  </Scene></Sequence>

  <Sequence from={600} durationInFrames={105}><Scene>
   <Label color={C.orange}>Мой вывод</Label>
   <div style={{marginTop:55}}><Title size={101}>{'ПОЛЕЗНОЕ\nНУЖНО\nПРОВЕРЯТЬ.'}</Title></div>
   <Note>Наличие навыка<br/>ещё не доказывает результат.</Note>
  </Scene></Sequence>

  <Sequence from={705} durationInFrames={75}><Scene>
   <Title size={103}>{'ПРОВЕРЯЕМ\nСЛЕДУЮЩИЙ?'}</Title>
   <div style={{marginTop:65,padding:'27px 36px',background:C.orange,color:C.bg,borderRadius:18,fontSize:44,fontWeight:800}}>ПОДПИШИСЬ · @Grezorg</div>
   <Note>Нейросети без сказок.<br/>Только проверка делом.</Note>
  </Scene></Sequence>

  <div style={{position:'absolute',left:96,right:96,bottom:275,fontSize:22,color:'#68778d'}}>Тест проверки заголовков YouTube Agent Skill</div>
  <div style={{position:'absolute',left:96,right:96,bottom:225,display:'flex',gap:12}}>{bars.map((end,i)=><div key={end} style={{height:5,flex:1,borderRadius:4,background:f>=(i===0?0:bars[i-1])?C.orange:'#293345'}}/>)}</div>
 </AbsoluteFill>;
};
registerRoot(()=><Composition id="SkillRealityCheck" component={Reel} width={1080} height={1920} fps={30} durationInFrames={780}/>);
