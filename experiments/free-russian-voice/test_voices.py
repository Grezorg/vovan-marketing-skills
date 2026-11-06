"""Проверка двух русских голосов без платного API; без обхода ограничений сервиса."""
import asyncio,json
from pathlib import Path
from importlib.metadata import version
import edge_tts

TEXT="Проверяем русскую озвучку для коротких видео. Живой голос, понятная речь и правильные ударения. Сначала смотрим результат, потом делаем выводы."
OUT=Path(__file__).parent/'output'
async def main():
    OUT.mkdir(exist_ok=True)
    results=[]
    for name,voice in [('dmitry','ru-RU-DmitryNeural'),('svetlana','ru-RU-SvetlanaNeural')]:
        target=OUT/(name+'.mp3')
        try:
            async with asyncio.timeout(45):
                await edge_tts.Communicate(TEXT,voice,rate='+5%').save(str(target))
            if not target.is_file() or target.stat().st_size==0:
                raise ValueError('Пустой результат')
            results.append({'voice':voice,'status':'получен MP3','file':target.name,'bytes':target.stat().st_size})
        except Exception as error:
            target.unlink(missing_ok=True)
            results.append({'voice':voice,'status':'не получен','error':type(error).__name__+': '+str(error)[:240]})
    report={'edge_tts':version('edge-tts'),'text':TEXT,'results':results,'note':'Это онлайн-сервис Edge через открытый сторонний клиент; тест не даёт гарантии постоянной доступности.'}
    (OUT/'test-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if not any(r['status']=='получен MP3' for r in results):
        raise SystemExit(1)
asyncio.run(main())
