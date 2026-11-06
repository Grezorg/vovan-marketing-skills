"""Создать оригинальное ритмическое сопровождение без чужих записей."""
import math, random, wave, array
RATE=44100
DURATION=26
BPM=124
rng=random.Random(20261106)
data=array.array('h')
notes=[55,55,65.406,49]
cuts=[0,2.8,5.2,10,13,16.4,20,23.5]
for i in range(RATE*DURATION):
 t=i/RATE
 beat=t*BPM/60
 frac=beat%1
 kick=math.sin(2*math.pi*(48*t+6*(1-math.exp(-frac*40))))*math.exp(-frac*18)*0.37
 half=(beat*2)%1
 hat=(rng.random()*2-1)*math.exp(-half*55)*0.04
 freq=notes[int(beat//4)%4]
 bass=(math.sin(2*math.pi*freq*t)+0.22*math.sin(4*math.pi*freq*t))*0.15*min(1,frac*30)*math.exp(-frac*2)
 tick=0
 for cut in cuts:
  x=t-cut
  if 0<=x<0.2:
   tick+=math.sin(2*math.pi*(600*x+1600*x*x))*math.exp(-x*28)*0.16
 fade=min(1,t*10,max(0,(DURATION-t)*2))
 sample=max(-1,min(1,(kick+hat+bass+tick)*fade))
 data.append(int(sample*25000))
with wave.open('soundtrack.wav','wb') as out:
 out.setnchannels(1);out.setsampwidth(2);out.setframerate(RATE);out.writeframes(data.tobytes())
