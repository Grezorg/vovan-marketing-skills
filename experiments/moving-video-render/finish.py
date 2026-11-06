"""Add timed Russian captions and brand to actual MPT renders; verify files."""
from pathlib import Path
import json,subprocess,math,re
from PIL import ImageFont
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
ASSETS=ROOT/'assets'
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',66)
tasks=json.loads((ROOT/'task-ids.json').read_text())

def stamp(s):
    c=round(max(0,s)*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'

def escape(s):return s.replace('\\','').replace('{','').replace('}','')

def captions(name):
    events=json.loads((ASSETS/f'{name}-words.json').read_text())
    cues=[];group=[]
    for i,e in enumerate(events):
        group.append(e)
        next_e=events[i+1] if i+1<len(events) else None
        text=' '.join(x['text'] for x in group)
        extended=text+' '+(next_e['text'] if next_e else '')
        if len(group)>=3 or next_e is None or FONT.getlength(extended)>850 or next_e['offset']-(e['offset']+e['duration'])>3000000:
            start=group[0]['offset']/1e7
            end=(e['offset']+e['duration'])/1e7+.10
            if next_e:end=min(end,next_e['offset']/1e7-.025)
            cues.append((start,end,text));group=[]
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,DejaVu Sans,66,&H00FFFFFF,&H000000FF,&H00100A05,&H90000000,-1,0,0,0,100,100,0,0,1,4,2,5,90,90,350,1
Style: Title,DejaVu Sans,86,&H00F4F6F2,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,-1,0,1,0,0,5,70,70,0,1
Style: Brand,DejaVu Sans,33,&H00E0D7C5,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,7,80,80,100,1
Style: Credit,DejaVu Sans,25,&H00B8ACA0,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,1,80,80,195,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    duration=16.4 if name=='tech' else 14.6
    title='СНАЧАЛА —\\NТВОЯ ИДЕЯ' if name=='tech' else 'ИДЕЯ\\NОЖИВАЕТ'
    lines=[header,f'Dialogue: 0,0:00:00.00,{stamp(duration)},Brand,,0,0,0,,@GREZORG',
           f'Dialogue: 0,0:00:00.15,0:00:03.20,Title,,0,0,0,,{{\\pos(540,320)\\fad(180,400)}}{title}']
    if name=='tech':lines.append(f'Dialogue: 0,0:00:00.00,{stamp(duration)},Credit,,0,0,0,,Кадры: NASA SVS')
    for start,end,text in cues:
        text=escape(text)
        parts=text.rsplit(' ',1)
        if len(parts)==2:text=parts[0]+' {\\c&H83DFFF&}'+parts[1]
        lines.append(f'Dialogue: 1,{stamp(start)},{stamp(end)},Caption,,0,0,0,,{{\\pos(540,1430)\\fad(55,55)}}{text}')
    path=ROOT/f'{name}.ass';path.write_text('\n'.join(lines),encoding='utf-8')
    (ROOT/f'{name}-caption-check.json').write_text(json.dumps({'cues':cues,'max_width_px':max(FONT.getlength(t) for _,_,t in cues)},ensure_ascii=False,indent=2))
    return path,duration

def main():
    reports=[]
    for name,file in [('tech','grezorg-space-trial.mp4'),('motion','grezorg-digital-trial.mp4')]:
        p=ROOT/'mpt-runtime/storage/tasks'/tasks[name]/'final-1.mp4'
        if not p.is_file():raise FileNotFoundError(p)
        ass,duration=captions(name)
        clean='drawbox=x=0:y=0:w=1080:h=527:color=black:t=fill,drawbox=x=0:y=1393:w=1080:h=527:color=black:t=fill,' if name=='tech' else ''
        vf=f'tpad=stop_mode=clone:stop_duration=0.35,{clean}eq=gamma=1.08:saturation=1.10,ass={ass.as_posix()},fade=t=out:st={duration-.35}:d=0.35'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(p),'-vf',vf,
            '-af',f'apad=pad_dur=0.35,loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=out:st={duration-.3}:d=0.3',
            '-t',str(duration),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
            '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-threads','3',str(OUT/file)],check=True)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(OUT/file)]))
        subprocess.run(['ffmpeg','-v','error','-i',str(OUT/file),'-f','null','-'],check=True)
        reports.append({'name':file,'engine':'MoneyPrinterTurbo 1.3.9 + FFmpeg captions','voice':'ru-RU-DmitryNeural, +0%',
            'provenance':'NASA SVS 5570, original music' if name=='tech' else 'Original procedural 3D animation, original music; not WanGP generation',
            'probe':probe})
        print('Finished',file,flush=True)
    (ROOT/'verification.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
