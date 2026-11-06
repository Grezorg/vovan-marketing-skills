# Grezorg: бесплатный лимит Google Vids

Короткий редакционный рилс с русской озвучкой ru-RU-DmitryNeural +0%, титрами и собственной музыкой. Монтаж использует короткие фрагменты официальных демонстраций Google. Генерация через бесплатный аккаунт Vids и доступ в РФ не проверялись; в ролике и описании это обозначено. Публикация отключена.

Лимит взят из официального анонса от 5 ноября 2026: https://blog.google/products-and-platforms/products/workspace/omni-1-2-flash-google-vids/ . Видеопримеры: https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-omni-1-2-flash/ . Полные демонстрационные файлы не включены в репозиторий.

Для повторения: Python 3.12, numpy, pillow, FFmpeg, DejaVu Sans, MoneyPrinterTurbo 1.3.9; путь к mpt через GREZORG_MPT_BIN. Положить narration.mp3, words.json и script.txt из workflow «Бесплатные ролики Google Vids» в assets/. В этой же папке нужны background.mp4, outfits.mp4, pantheon.mp4, island.mp4, type.mp4 — соответствующие официальные демонстрации из анонса модели. Запустить build.py. Выход: MP4 1080×1920, обложка, verification.json. Временные метки относятся к этой конкретной озвучке.
