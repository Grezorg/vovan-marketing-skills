"""Сравнить мужские голоса на русском слове видео; только бесплатные короткие пробы."""
import asyncio,json
from pathlib import Path
import edge_tts
OUT=Path(__file__).parent/'output'
TEXT="Это видео о создании коротких роликов. В этом видео важны правильные ударения. Готовое видео можно публиковать."
async def main():
 OUT.mkdir(exist_ok=True)
 results=[]
 variants=[('dmitry-normal','ru-RU-DmitryNeural',TEXT),('dmitry-stress','ru-RU-DmitryNeural',TEXT.replace('видео','ви́део')),('andrew-multilingual','en-US-AndrewMultilingualNeural',TEXT)]
 for name,voice,text in variants:
  target=OUT/(name+'.mp3')
  try:
   async with asyncio.timeout(45):
    await edge_tts.Communicate(text,voice,rate='+0%').save(str(target))
   if not target.is_file() or target.stat().st_size==0:raise ValueError('Empty result')
   results.append({'variant':name,'voice':voice,'text':text,'status':'получен MP3','file':target.name,'bytes':target.stat().st_size})
  except Exception as error:
   target.unlink(missing_ok=True)
   results.append({'variant':name,'status':'не получен','error':type(error).__name__+': '+str(error)[:240]})
 report={'results':results,'note':'Правильность произношения оценивать прослушиванием, не по успешному выполнению запроса.'}
 (OUT/'test-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2))
 if not any(r['status']=='получен MP3' for r in results):raise SystemExit(1)
asyncio.run(main())
