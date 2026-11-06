"""Produce a publishable multi-shot Russian reel from credited NASA footage."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,os,uuid,shutil,wave,math,re
import numpy as np
from PIL import ImageFont

ROOT=Path(__file__).resolve().parent
A=ROOT/'assets';O=ROOT/'output';S=ROOT/'shots'
O.mkdir(exist_ok=True);S.mkdir(exist_ok=True)
MPT=Path(os.environ.get('GREZORG_MPT_BIN',str(ROOT.parent/'trial-videos/.venv/bin/mpt')))
END=31.95
# Output boundaries follow actual narration; source times avoid English labels.
SHOTS=[
 ('earth.mp4',12,0,.95,'planet',1.6),
 ('sun-square.mp4',8,.95,1.90,'cover',1.5),
 ('moon-4k.mp4',230,1.90,3.65,'cover',1.15),
 ('earth.mp4',24,3.65,6.10,'macro',1.7),
 ('sun-square.mp4',9,6.10,8.25,'cover',1.8),
 ('moon-4k.mp4',232,8.25,10.40,'cover',1.25),
 ('moon-4k.mp4',83,10.40,13.85,'cover',1.1),
 ('moon-4k.mp4',252,13.85,15.70,'cover',1.25),
 ('earth.mp4',57,15.70,17.05,'macro',1.5),
 ('sun-square.mp4',17,17.05,19.15,'cover',1.65),
 ('moon-4k.mp4',235,19.15,20.80,'cover',1.3),
 ('earth.mp4',74,20.80,22.35,'planet',1.5),
 ('moon-4k.mp4',269,22.35,25.35,'moon-wide',1.05),
 ('sun-square.mp4',15,25.35,28.65,'cover',1.5),
 ('earth.mp4',4,28.65,END,'planet',1.7),
]

def execute(args,log=None,env=None):
    if log:
        with Path(log).open('w') as f:subprocess.run(args,check=True,stdout=f,stderr=subprocess.STDOUT,env=env)
    else:subprocess.run(args,check=True,env=env)

def shot(item):
    i,(src,seek,start,end,mode,speed)=item
    duration=end-start
    if mode=='planet':
        fit='crop=960:1080:(iw-960)/2:0,scale=1080:1216,pad=1080:1920:0:352:color=black'
    elif mode=='moon-wide':
        fit='crop=1920:2160:(iw-1920)/2:0,scale=1080:1216,pad=1080:1920:0:352:color=black'
    elif mode=='macro':
        fit="scale=-2:2304,crop=1080:1920:(iw-1080)/2:(ih-1920)/2"
    else:
        fit="scale=-2:1920,crop=1080:1920:(iw-1080)/2+70*sin(t*0.45):0"
    vf=f'setpts=(PTS-STARTPTS)/{speed},fps=30,{fit},setsar=1,eq=contrast=1.025:saturation=1.08'
    target=S/f'{i:02}.mp4'
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
    tid=str(uuid.uuid5(uuid.NAMESPACE_URL,'grezorg-nasa-studio-reel-20261106-v1'))
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
      f'Dialogue: 1,0:00:00.00,{ts(END)},Source,,0,0,0,,Кадры: NASA’s Scientific Visualization Studio',
      'Dialogue: 2,0:00:00.06,0:00:03.55,Hook,,0,0,0,,{\\pos(510,330)\\fad(120,160)}ЭТИ КАДРЫ\\N{\\c&H83DFFF&}БЕСПЛАТНО',
      'Dialogue: 2,0:00:10.50,0:00:13.75,Hook,,0,0,0,,{\\pos(510,320)\\fs69\\fad(140,180)}ИСТОЧНИК — NASA',
      'Dialogue: 2,0:00:10.60,0:00:13.75,Link,,0,0,0,,{\\pos(510,450)\\fad(140,180)}svs.gsfc.nasa.gov',
      'Dialogue: 2,0:00:22.55,0:00:25.20,Hook,,0,0,0,,{\\pos(510,325)\\fs72\\fad(150,180)}МОЯ ИИ-СТУДИЯ',
      'Dialogue: 2,0:00:28.65,0:00:31.95,Hook,,0,0,0,,{\\pos(510,310)\\fs82\\fad(130,180)}ИСТОЧНИК\\N{\\c&H83DFFF&}В ОПИСАНИИ',
    ]
    cues=[];group=[]
    for i,x in enumerate(words):
        x=dict(x);x['text']='NASA' if x['text']=='НАСА' else x['text']
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
    ass=subtitles();out=O/'grezorg-detailed-reel.mp4'
    # Readable overlays without a flat opaque panel hiding the detailed footage.
    vf=f'tpad=stop_mode=clone:stop_duration=0.7,ass={ass},fade=t=out:st={END-.3}:d=0.3'
    execute(['ffmpeg','-v','error','-y','-i',str(p),'-vf',vf,'-af',
        f'apad=pad_dur=0.7,loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=out:st={END-.3}:d=0.3',
        '-t',str(END),'-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-threads','3',str(out)])
    execute(['ffmpeg','-v','error','-y','-ss','0.55','-i',str(out),'-frames:v','1','-q:v','2',str(O/'grezorg-reel-cover.jpg')])
    execute(['ffmpeg','-v','error','-i',str(out),'-f','null','-'])
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
    (ROOT/'verification.json').write_text(json.dumps({'probe':probe,'shots':SHOTS,'voice':'ru-RU-DmitryNeural +0%','paid_generation':False,'published':False},ensure_ascii=False,indent=2))
    print('FINAL',out,flush=True)

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:shots=list(pool.map(shot,enumerate(SHOTS)))
    music_file=music();raw=mpt(shots,music_file);finish(raw)
