import React from 'react';
import {AbsoluteFill, Composition, registerRoot, useCurrentFrame, interpolate} from 'remotion';

const Promo = () => {
  const frame = useCurrentFrame();
  const stage = frame < 60 ? 0 : frame < 120 ? 1 : 2;
  const local = frame % 60;
  const opacity = interpolate(local, [0, 9, 50, 59], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const titles = ['Есть задача?', 'Собираем решение', 'Проверяем результат'];
  const notes = ['Сайт · карточки товара · видео', 'От брифа до рабочего проекта', 'VOVAN OS'];
  return <AbsoluteFill style={{background: '#0b1020', color: '#f8fafc', fontFamily: 'DejaVu Sans, sans-serif', padding: 64}}>
    <div style={{position: 'absolute', width: 620, height: 620, borderRadius: '50%', background: 'radial-gradient(circle, #1d4ed855, transparent 70%)', left: -100 + frame * 0.8, top: 280}} />
    <div style={{fontSize: 25, letterSpacing: 5, color: '#60a5fa', marginTop: 50}}>VOVAN OS</div>
    <div style={{fontSize: 18, letterSpacing: 2, color: '#94a3b8', marginTop: 18}}>ТЕСТ ВИДЕО ИЗ КОДА</div>
    <div style={{position: 'absolute', top: 420, left: 64, right: 64, opacity, transform: 'translateY(' + interpolate(local, [0, 12], [35, 0], {extrapolateRight:'clamp'}) + 'px)'}}>
      <div style={{fontSize: 70, fontWeight: 800, lineHeight: 1.12}}>{titles[stage]}</div>
      <div style={{fontSize: 28, lineHeight: 1.6, marginTop: 42, color: '#93c5fd'}}>{notes[stage]}</div>
    </div>
    <div style={{position: 'absolute', bottom: 140, left: 64, right: 64, display: 'flex', gap: 16}}>
      {[0,1,2].map(i => <div key={i} style={{height: 6, flex: 1, borderRadius: 4, background: stage >= i ? '#60a5fa' : '#263249'}} />)}
    </div>
    <div style={{position: 'absolute', bottom: 88, left: 64, color: '#64748b', fontSize: 18}}>Короткий рекламный макет • 6 секунд</div>
  </AbsoluteFill>;
};
registerRoot(() => <Composition id="VovanPromo" component={Promo} width={720} height={1280} fps={30} durationInFrames={180} />);

