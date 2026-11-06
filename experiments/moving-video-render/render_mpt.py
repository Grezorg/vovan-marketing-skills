"""Run real MoneyPrinterTurbo with prepared assets and no paid providers."""
from pathlib import Path
import subprocess,os,json,uuid,shutil
ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
env=os.environ.copy()
env['MPT_HOME']=str(ROOT/'mpt-runtime')
env['IMAGEIO_FFMPEG_EXE']='/usr/bin/ffmpeg'
env['FFMPEG_BINARY']='/usr/bin/ffmpeg'
report=json.loads((ASSETS/'report.json').read_text())
runtime=ROOT/'mpt-runtime';runtime.mkdir(exist_ok=True)
bgm=runtime/'storage/bgm/original-music.wav';bgm.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(ASSETS/'original-music.wav',bgm)
(runtime/'config.toml').write_text('''log_level = "INFO"
[app]
video_codec = "libx264"
subtitle_provider = "edge"
upload_post_enabled = false
upload_post_auto_upload = false
max_concurrent_tasks = 1
''')
tasks={name:str(uuid.uuid5(uuid.NAMESPACE_URL,'grezorg-free-trial-20261106-'+name)) for name in ['tech','motion']}
(ROOT/'task-ids.json').write_text(json.dumps(tasks))
for name,visual in [('tech','earth-portrait.mp4'),('motion','digital-motion.mp4')]:
    args=[str(ROOT/'.venv/bin/mpt'),'cli','--video-script',report[name]['script'],
        '--video-language','ru-RU','--video-source','local',
        '--video-materials',str(ASSETS/visual),'--custom-audio-file',str(ASSETS/f'{name}.mp3'),
        '--voice-name','ru-RU-DmitryNeural','--voice-rate','1',
        '--video-aspect','9:16','--video-fit-mode','cover',
        '--video-concat-mode','sequential','--video-transition-mode','none',
        '--video-clip-duration','30','--n-threads','3',
        '--no-subtitle-enabled','--bgm-type','custom','--bgm-file',str(bgm),
        '--bgm-volume','0.13','--task-id',tasks[name]]
    print('Rendering',name,flush=True)
    with (ROOT/f'mpt-{name}.log').open('w') as log:
        result=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        print((ROOT/f'mpt-{name}.log').read_text()[-5000:],flush=True)
        raise SystemExit(result.returncode)
    print('Completed',name,flush=True)
