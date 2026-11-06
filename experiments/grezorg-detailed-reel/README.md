# Grezorg: детализированный рилс с несколькими сценами

Проверенный результат: 31.9667 секунды, 1080×1920, 30 кадров/с, H.264/AAC. 15 смонтированных планов. Голос ru-RU-DmitryNeural, скорость +0%. Итоговая громкость -15.9 LUFS, истинный пик -3.0 dBFS. Полное декодирование и визуальная выборка прошли. Публикация не выполнялась.

Сюжет: где автор берёт детализированные материалы для своих рилсов. Это монтаж визуализаций NASA SVS и материалов SDO, с оригинальной синтезированной музыкой и русской нейроозвучкой. WanGP и платная генерация не использовались. Исходные аудиодорожки NASA в итог не включены.

## Источники

- Земля, NASA SVS 5570: https://svs.gsfc.nasa.gov/5570/
- Солнце, NASA SVS 4380: https://svs.gsfc.nasa.gov/4380/
- Луна, NASA SVS 4619, версия без титров/музыки: https://svs.gsfc.nasa.gov/4619/
- Правила использования: https://svs.gsfc.nasa.gov/help/
- Авторство: NASA’s Scientific Visualization Studio.

## Воспроизведение

Проверено на Linux CPU. Нужны FFmpeg, DejaVu Sans, Python 3.12, numpy, pillow, MoneyPrinterTurbo 1.3.9. Указать GREZORG_MPT_BIN — полный путь к установленному mpt. Соседняя папка assets/ должна содержать:

- narration.mp3, words.json, script.txt из workflow «Озвучка готового рилса Grezorg» этой ветки;
- earth.mp4: https://svs.gsfc.nasa.gov/vis/a000000/a005500/a005570/Earth_wAtmos_spin_02_1080p60.mp4
- sun-square.mp4: https://svs.gsfc.nasa.gov/vis/a000000/a004300/a004380/May2015SeeSawFilament_304A_2048p30.mp4
- moon-4k.mp4: https://svs.gsfc.nasa.gov/vis/a000000/a004600/a004619/moontour_notitle_2160p30.mp4

Запуск build.py. Локальные данные MPT изолированы в mpt-runtime/. Автопубликация выключена. На выходе MP4, обложка и техническая проверка. Монтажный план привязан к конкретной озвучке; при смене текста требуется пересборка временных меток и планов.

Редакционная гипотеза основана на интересе к личным творческим проектам с ИИ и полезным рабочим процессам. Источник: официальный отчёт YouTube от 20 октября 2026, https://blog.youtube/culture-and-trends/youtube-generative-ai-video-creativity-report/ . Это не доказательство будущего охвата и не рейтинг русскоязычных Shorts.
