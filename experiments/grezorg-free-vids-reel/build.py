"""Produce a Russian editorial news reel using excerpts of official Google demonstrations."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,os,uuid,shutil,wave,math,re
import numpy as np
from PIL import ImageFont

ROOT=Path(__file__).resolve().parent
A=ROOT/'assets';O=ROOT/'output';S=ROOT/'shots'
O.mkdir(exist_ok=True);S.mkdir(exist_ok=True)
MPT=Path(os.environ.get('GREZORG_MPT_BIN',str(ROOT.parent/'trial-videos/.venv/bin/mpt')))
END=28.2
# Output boundaries follow actual narration; source times avoid English labels.
SHOTS=[
 ('island.mp4',9,0,2.80,'cover',1),
 ('pantheon.mp4',6,2.80,4.45,'cover',1),
 ('outfits.mp4',13,4.45,8.45,'outfit',1),
 ('background.mp4',20,8.45,11.80,'compare',1),
 ('type.mp4',8,11.80,14.80,'type',1),
 ('island.mp4',9,14.80,17.80,'cover',1),
 ('pantheon.mp4',11.2,17.80,21.60,'cover',1),
 ('background.mp4',20,21.60,24.60,'compare',1),
 ('pantheon.mp4',6,24.60,28.20,'cover',1),
]

def execute(args,log=None,env=None):
    if log:
        with Path(log).open('w') as f:subprocess.run(args,check=True,stdout=f,stderr=subprocess.STDOUT,env=env)
    else:subprocess.run(args,check=True,env=env)

def shot(item):
    i,(src,seek,start,end,mode,speed)=item
    duration=end-start
    if mode=='outfit':
        fit='crop=448:800:1284:170,scale=900:1608,pad=1080:1920:90:200:color=0x050811'
    elif mode=='type':
        fit='crop=460:840:1370:170,scale=900:1644,pad=1080:1920:90:180:color=0x050811'
    elif mode=='castle':
        fit='crop=500:282:1350:580,scale=1080:608,pad=1080:1920:0:640:color=0x050811'
    else:
        fit='scale=-2:1920,crop=1080:1920:(iw-1080)/2:0'
    vf=f'setpts=(PTS-STARTPTS)/{speed},fps=30,{fit},setsar=1,eq=contrast=1.025:saturation=1.08'
    target=S/f'{i:02}.mp4'
    if mode=='compare':
        graph='[0:v]split=2[a][b];[a]crop=690:388:60:325,scale=1000:562,pad=1080:600:40:25:color=0x050811[a];[b]crop=510:288:802:180,scale=1000:562,pad=1080:600:40:25:color=0x050811[b];[a][b]vstack,pad=1080:1920:0:400:color=0x050811,fps=30,setsar=1[v]'
        execute(['ffmpeg','-v','error','-y','-ss',str(seek),'-i',str(A/src),'-filter_complex',graph,'-map','[v]',
            '-t',f'{duration:.3f}','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-threads','2',str(target)])
        print('Shot',i,'ready',flush=True)
        return target
    execute(['ffmpeg','-v','error','-y','-ss',str(seek),'-i',str(A/src),
        '-vf',vf,'-t',f'{duration:.3f}','-an','-c:v','libx264','-preset','fast','-crf','17',
        '-pix_fmt','yuv420p','-threads','2',str(target)])
    print('Shot',i,'ready',flush=True)
    return target

def music():
    sr=44100;t=np.arange(int(sr*(END+1)))/sr
    out=np.zeros_like(t)
    for k,f in enumerate([130.8128,155.5635,195.9977,261.6256]):
        env=.6+.4*np.sin(t*.35+k)**2
        out+=.023*env*np.sin(2*np.pi*f*t+.22*np.sin(t*.5+k))
    # Original quiet bass pulse and restrained percussion, no borrowed song.
    for b in np.arange(0,END,.535714):
        x=t-b;sel=(x>=0)&(x<.3)
        out[sel]+=.16*np.sin(2*np.pi*(47*x[sel]+2.9*(1-np.exp(-x[sel]*17))))*np.exp(-x[sel]*17)
    rng=np.random.default_rng(20261106)
    for _,_,s,_,_,_ in SHOTS[1:]:
        x=t-(s-.10);sel=(x>=0)&(x<.20)
        env=np.sin(np.pi*x[sel]/.20)**2
        noise=rng.normal(0,1,sel.sum());noise=np.convolve(noise,np.ones(10)/10,'same')
        out[sel]+=.09*noise*env
    out*=np.minimum(1,t/.25)*np.minimum(1,np.maximum(0,(END+.4-t)/1.2))
    stereo=np.stack([out,out*.96],axis=1)
    dest=A/'original-score.wav'
    with wave.open(str(dest),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((stereo*32767).astype('<i2').tobytes())
    return dest

def mpt(shots,bgm):
    runtime=ROOT/'mpt-runtime';runtime.mkdir(exist_ok=True)
    target=runtime/'storage/bgm/original-score.wav';target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(bgm,target)
    (runtime/'config.toml').write_text('''log_level = "INFO"
[app]
video_codec = "libx264"
upload_post_enabled = false
upload_post_auto_upload = false
''')
    env=os.environ.copy();env['MPT_HOME']=str(runtime)
    env['FFMPEG_BINARY']='/usr/bin/ffmpeg';env['IMAGEIO_FFMPEG_EXE']='/usr/bin/ffmpeg'
    tid=str(uuid.uuid5(uuid.NAMESPACE_URL,'grezorg-free-vids-reel-20261106-v1'))
    args=[str(MPT),'cli','--video-script',(A/'script.txt').read_text(),
        '--video-language','ru-RU','--video-source','local','--video-materials',','.join(str(p) for p in shots),
        '--custom-audio-file',str(A/'narration.mp3'),'--voice-name','ru-RU-DmitryNeural','--voice-rate','1',
        '--video-aspect','9:16','--video-fit-mode','cover','--video-concat-mode','sequential',
        '--video-clip-duration','30','--video-transition-mode','none','--no-subtitle-enabled',
        '--bgm-type','custom','--bgm-file',str(target),'--bgm-volume','0.20','--n-threads','3','--task-id',tid]
    execute(args,ROOT/'mpt.log',env=env)
    return runtime/'storage/tasks'/tid/'final-1.mp4'

def ts(s):
    c=round(s*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'

def subtitles():
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',65)
    words=json.loads((A/'words.json').read_text())
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Caption,DejaVu Sans,65,&H00FFFFFF,&H000000FF,&H00110A05,&H90000000,-1,0,0,0,100,100,0,0,1,4,2,5,110,160,350,1
Style: Hook,DejaVu Sans,94,&H00F5F5F1,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,-1,0,1,2,1,5,90,150,0,1
Style: Label,DejaVu Sans,32,&H00EFECE6,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,7,80,150,105,1
Style: Source,DejaVu Sans,26,&H00D9D4CB,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,1,80,150,230,1
Style: Link,DejaVu Sans,48,&H0083DFFF,&H000000FF,&H00120B04,&H00000000,-1,0,0,0,100,100,0,0,1,4,0,5,85,150,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
    lines=[header,
      f'Dialogue: 1,0:00:00.00,{ts(END)},Label,,0,0,0,,@GREZORG',
      f'Dialogue: 1,0:00:00.00,{ts(END)},Source,,0,0,0,,Официальные примеры модели Google • Фрагменты',
      'Dialogue: 2,0:00:00.04,0:00:02.75,Hook,,0,0,0,,{\\pos(510,285)\\fs86\\fad(100,160)}ИИ-РОЛИКИ\\N{\\c&H83DFFF&}БЕСПЛАТНО',
      'Dialogue: 2,0:00:02.85,0:00:04.40,Hook,,0,0,0,,{\\pos(510,285)\\fs83\\fad(100,140)}GOOGLE VIDS',
      'Dialogue: 2,0:00:04.45,0:00:08.45,Hook,,0,0,0,,{\\pos(510,270)\\fs82\\fad(100,140)}3 ГЕНЕРАЦИИ\\N{\\c&H83DFFF&}В МЕСЯЦ',
      'Dialogue: 2,0:00:04.50,0:00:08.45,Link,,0,0,0,,{\\pos(510,420)\\fs38\\fad(100,140)}ДО 15 СЕКУНД КАЖДАЯ',
      'Dialogue: 2,0:00:08.75,0:00:11.75,Hook,,0,0,0,,{\\pos(510,280)\\fs67\\fad(100,140)}ЛИМИТ ИЗ АНОНСА\\N{\\c&H83DFFF&}5 НОЯБРЯ 2026',
      'Dialogue: 2,0:00:12.05,0:00:17.75,Hook,,0,0,0,,{\\pos(510,285)\\fs100\\fad(100,140)}vids.new',
      'Dialogue: 2,0:00:12.05,0:00:17.75,Link,,0,0,0,,{\\pos(510,425)\\fs37\\fad(100,140)}КОМПЬЮТЕР + GOOGLE-АККАУНТ',
      'Dialogue: 2,0:00:18.10,0:00:21.65,Hook,,0,0,0,,{\\pos(510,285)\\fs56\\fad(100,140)}ДОСТУП ЗАВИСИТ\\N{\\c&H83DFFF&}ОТ АККАУНТА И СТРАНЫ',
      'Dialogue: 2,0:00:18.10,0:00:21.65,Link,,0,0,0,,{\\pos(510,440)\\fs30\\fad(100,140)}ДОСТУП В РФ НЕ ПРОВЕРЕН',
      'Dialogue: 2,0:00:24.90,0:00:28.20,Hook,,0,0,0,,{\\pos(510,280)\\fs82\\fad(100,160)}СОХРАНИ\\N{\\c&H83DFFF&}ПОПРОБУЙ САМ',
    ]
    cues=[];group=[]
    for i,x in enumerate(words):
        x=dict(x);x['text']={'Гугл':'Google','Видс':'Vids'}.get(x['text'],x['text'])
        group.append(x);n=words[i+1] if i+1<len(words) else None
        text=' '.join(z['text'] for z in group)
        extended=text+' '+(n['text'] if n else '')
        gap=(n['offset']-(x['offset']+x['duration']))/1e7 if n else 9
        if len(group)>=3 or n is None or f.getlength(extended)>815 or gap>.30:
            start=group[0]['offset']/1e7;end=(x['offset']+x['duration'])/1e7+.13
            if n:end=min(end,n['offset']/1e7-.025)
            cues.append([round(start,3),round(end,3),text])
            s=text.rsplit(' ',1)
            display=s[0]+' {\\c&H83DFFF&}'+s[1] if len(s)==2 else text
            lines.append(f'Dialogue: 3,{ts(start)},{ts(end)},Caption,,0,0,0,,{{\\pos(510,1435)\\fad(45,60)}}{display}')
            group=[]
    (ROOT/'captions.json').write_text(json.dumps({'cues':cues,'max_caption_width_px':max(f.getlength(c[2]) for c in cues)},ensure_ascii=False,indent=2))
    ass=ROOT/'reel.ass';ass.write_text('\n'.join(lines),encoding='utf-8');return ass

def finish(p):
    ass=subtitles();out=O/'grezorg-free-vids-reel.mp4'
    # Readable overlays without a flat opaque panel hiding the detailed footage.
    vf=f'tpad=stop_mode=clone:stop_duration=0.7,ass={ass},fade=t=out:st={END-.3}:d=0.3'
    execute(['ffmpeg','-v','error','-y','-i',str(p),'-vf',vf,'-af',
        f'apad=pad_dur=0.7,loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=out:st={END-.3}:d=0.3',
        '-t',str(END),'-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-threads','3',str(out)])
    execute(['ffmpeg','-v','error','-y','-ss','0.55','-i',str(out),'-frames:v','1','-q:v','2',str(O/'grezorg-free-vids-cover.jpg')])
    execute(['ffmpeg','-v','error','-i',str(out),'-f','null','-'])
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
    (ROOT/'verification.json').write_text(json.dumps({'probe':probe,'shots':SHOTS,'voice':'ru-RU-DmitryNeural +0%','paid_generation':False,'published':False},ensure_ascii=False,indent=2))
    print('FINAL',out,flush=True)

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:shots=list(pool.map(shot,enumerate(SHOTS)))
    music_file=music();raw=mpt(shots,music_file);finish(raw)
