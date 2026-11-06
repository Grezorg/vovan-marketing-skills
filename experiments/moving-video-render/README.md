# Две бесплатные пробы Shorts

Проверено на Linux CPU: MoneyPrinterTurbo 1.3.9, FFmpeg, Python 3.12, Pillow, NumPy. Выход: 1080×1920, 30 кадров/с, H.264/AAC. Озвучка: ru-RU-DmitryNeural, скорость +0%.

- Космическая проба: готовая визуализация Земли NASA SVS, https://svs.gsfc.nasa.gov/5570/ . Указать NASA's Scientific Visualization Studio. Исходное аудио не используется. Правила использования: https://svs.gsfc.nasa.gov/help/ .
- Цифровая проба: собственная процедурная 3D-анимация. Это НЕ проверка WanGP или нейросетевого image-to-video.
- Сборка обеих проб действительно выполнена MoneyPrinterTurbo с локальными материалами. Субтитры и оформление добавлены FFmpeg по временным меткам Edge TTS. Платные API и публикация отключены.

## Повторение

1. Создать локальное окружение .venv рядом со скриптами, установить mpt==1.3.9, numpy, pillow; системный FFmpeg и DejaVu Sans.
2. Поместить tech.mp3, motion.mp3, tech-words.json, motion-words.json, report.json из workflow «Пробы роликов с движением» в assets/. Сценарии и подготовка озвучки: ../moving-video-trials/prepare.py.
3. Скачать https://svs.gsfc.nasa.gov/vis/a000000/a005500/a005570/Earth_wAtmos_spin_02_1080p60.mp4 как assets/earth.mp4. Публичная ссылка Pexels в исходной подготовке вернула 403 и в результатах не использовалась.
4. Выполнить prepare_visuals.py, render_mpt.py, finish.py последовательно. Скрипты используют только локальные материалы и свежий MPT_HOME в соседней папке. Автопубликация выключена.
5. Готовые файлы находятся в output/, техническая проверка — verification.json. Для другого сценария нужны новые временные метки и проверка продолжительности.

Эти скрипты — воспроизводимый эксперимент, а не универсальная установка для Windows. WanGP в этой среде без GPU не запускался.
