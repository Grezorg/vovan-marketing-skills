"""Prepare free narration and publicly offered Pexels footage for two video tests."""
import asyncio, json, pathlib, urllib.request
import edge_tts
OUT=pathlib.Path("experiments/moving-video-trials/output")
OUT.mkdir(parents=True,exist_ok=True)
SCRIPTS={
"tech":"Нейросеть не заменяет твою идею. Она помогает быстрее её воплотить. Сначала замысел. Затем голос, кадры и монтаж. Проверяем результат, а не красивые обещания.",
"motion":"Одна картинка может стать целым миром. Добавим движение, свет и глубину. Соберём короткую историю и озвучим её по-русски. Вот так идея превращается в ролик."
}
async def narrate(name,text):
    c=edge_tts.Communicate(text,"ru-RU-DmitryNeural",rate="+0%",boundary="WordBoundary")
    events=[]
    with (OUT/f"{name}.mp3").open("wb") as f:
        async for chunk in c.stream():
            if chunk["type"]=="audio": f.write(chunk["data"])
            elif chunk["type"]=="WordBoundary": events.append(chunk)
    (OUT/f"{name}-words.json").write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding="utf-8")
async def main():
    report={}
    for name,text in SCRIPTS.items():
        try:
            await asyncio.wait_for(narrate(name,text),timeout=55)
            report[name]={"ok":True,"voice":"ru-RU-DmitryNeural","rate":"+0%","script":text}
        except Exception as e: report[name]={"ok":False,"error":type(e).__name__+": "+str(e)[:400]}
    # The public MP4 URL is supplied by the clip page's download integration.
    url="https://videos.pexels.com/video-files/6330779/6330779-hd_1920_1080_30fps.mp4"
    try:
        with urllib.request.urlopen(url,timeout=45) as r:
            (OUT/"coding.mp4").write_bytes(r.read())
        report["footage"]={"ok":True,"url":url,"page":"https://www.pexels.com/video/close-up-view-of-a-man-doing-computer-programming-6330779/","author":"Matias Mango","license":"https://www.pexels.com/license/"}
    except Exception as e: report["footage"]={"ok":False,"error":type(e).__name__+": "+str(e)[:300]}
    (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if not any(report[n]["ok"] for n in SCRIPTS): raise SystemExit(1)
asyncio.run(main())
