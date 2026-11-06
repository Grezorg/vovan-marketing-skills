#!/usr/bin/env python3
"""Локально проверять русские заголовки, выбросы просмотров и удержание; без публикации и сети."""
import argparse
import csv
import io
import json
import math
import re
import statistics
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

STOP = set('и а но или в во на по для с со из от до к у о об это как что ты вы я мы он она они ваш твой мой the a an and or of for to in on with you your my how what'.split())

def tokens(text):
    text = unicodedata.normalize('NFKC', text).casefold().replace('ё', 'е')
    return re.findall(r'[^\W_]+', text, re.UNICODE)

def package(title, thumbnail):
    title = title.strip()
    thumb = thumbnail.strip()
    shared = sorted((set(tokens(title)) - STOP) & (set(tokens(thumb)) - STOP))
    issues = []
    if not title:
        issues.append('Пустой заголовок.')
    if not thumb:
        issues.append('Текст обложки не указан; изображение проверять отдельно.')
    if len(title) > 100:
        issues.append('Заголовок длиннее 100 символов.')
    if len(title) > 60:
        issues.append('Длинный заголовок: проверить реальное отображение на странице и телефоне.')
    if shared:
        issues.append('Есть повторяющиеся значимые слова: ' + ', '.join(shared))
    if len(tokens(thumb)) > 4:
        issues.append('На обложке много слов; проверить читаемость в уменьшенном виде.')
    return {'заголовок': title, 'обложка': thumb, 'символов': len(title),
            'совпадения': shared, 'замечания': issues,
            'границы': 'Лексическая проверка без лемматизации; смысловой повтор и качество картинки проверять отдельно. Числового прогноза CTR нет.'}

def number(value):
    value = str(value).strip().replace('\u00a0', '').replace(' ', '').replace('%', '')
    if ',' in value and '.' in value:
        raise ValueError('Неоднозначное число с точкой и запятой: ' + value)
    result = float(value.replace(',', '.'))
    if not math.isfinite(result):
        raise ValueError('Нужно конечное число.')
    return result

def read_retention(text):
    lines = [line for line in text.lstrip('\ufeff').splitlines() if line.strip()]
    if not lines:
        raise ValueError('Пустой CSV.')
    delimiter = ';' if ';' in lines[0] else ','
    rows = list(csv.reader(io.StringIO('\n'.join(lines)), delimiter=delimiter))
    header = [v.strip().casefold() for v in rows[0]]
    aliases = [('position', 'позиция', 'seconds', 'секунды', 'percent', 'процент'),
               ('retention', 'удержание', 'audience_retention')]
    indexes = [next((header.index(a) for a in group if a in header), None) for group in aliases]
    if None in indexes:
        raise ValueError('Нужны именованные столбцы position и retention (или позиция и удержание).')
    points = []
    for row in rows[1:]:
        if len(row) != len(header):
            raise ValueError('Количество полей CSV не совпадает с заголовком; десятичную запятую заключить в кавычки или выбрать ;.')
        x, y = (number(row[i]) for i in indexes)
        if x < 0 or y < 0:
            raise ValueError('Отрицательная позиция или удержание.')
        points.append((x, y))
    if len(points) < 2 or any(b[0] <= a[0] for a, b in zip(points, points[1:])):
        raise ValueError('Нужны минимум две точки со строго возрастающей позицией.')
    return points

def retention(points, axis, duration=None):
    if duration is not None and (not math.isfinite(duration) or duration <= 0):
        raise ValueError('Длительность должна быть конечной и положительной.')
    if axis == 'percent':
        if duration is None or not math.isfinite(duration) or duration <= 0:
            raise ValueError('Для процентной оси нужна фактическая длительность --duration.')
        if any(x > 100 for x, _ in points):
            raise ValueError('Процентная позиция выходит за 100.')
        points = [(x / 100 * duration, y) for x, y in points]
    elif duration is not None and any(x > duration for x, _ in points):
        raise ValueError('Позиция выходит за фактическую длительность.')
    end = min(30, duration if duration is not None else points[-1][0])
    start = points[0][1]
    def value_at(t):
        if t < points[0][0] or t > points[-1][0]:
            return None
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if x1 <= t <= x2:
                return y1 + (y2 - y1) * (t - x1) / (x2 - x1)
        return points[-1][1]
    opening = value_at(end)
    drops = sorted([{'начало_сек': a[0], 'конец_сек': b[0],
                     'потеря_пп': round(a[1] - b[1], 3)}
                    for a, b in zip(points, points[1:]) if b[1] < a[1]],
                   key=lambda d: d['потеря_пп'], reverse=True)
    complete_start = points[0][0] == 0
    return {'точек': len(points), 'окно_до_сек': end,
            'потеря_в_начале_пп': round(start - opening, 3) if opening is not None and complete_start else None,
            'падения': drops[:5],
            'границы': 'Падение локализовано между точками, причина не установлена. Удержание может превышать 100% из-за повторных просмотров. Для неполного начала потеря не вычисляется.'}

def outliers(rows, as_of, min_age=7, max_age=90, format_name='shorts', min_videos=4, multiple=2):
    if min_age < 0 or max_age < min_age or min_videos < 2 or not math.isfinite(multiple) or multiple <= 0:
        raise ValueError('Некорректное окно возраста, размер выборки или порог.')
    groups = defaultdict(list)
    skipped = []
    seen = set()
    for index, row in enumerate(rows):
        try:
            published = date.fromisoformat(row['published_at'][:10])
            age = (as_of - published).days
            if not isinstance(row['views'], (int, float)) or isinstance(row['views'], bool):
                raise ValueError('Просмотры должны быть точным числом JSON, не строкой/округлённым счётчиком.')
            views = number(row['views'])
            channel = str(row['channel']).strip()
            if not channel or views < 0:
                raise ValueError('Нет канала или просмотры отрицательны.')
            if row.get('format') != format_name or not min_age <= age <= max_age:
                skipped.append({'строка': index, 'причина': 'Другой формат или возраст вне выбранного окна.'})
                continue
            identity = row.get('video_id') or row.get('url')
            if identity and identity in seen:
                skipped.append({'строка': index, 'причина': 'Повтор ролика.'})
                continue
            if identity:
                seen.add(identity)
            groups[channel].append((row, views, age))
        except (KeyError, TypeError, ValueError) as error:
            skipped.append({'строка': index, 'причина': 'Неполные/некорректные данные: ' + str(error)})
    result = []
    thin = []
    for channel, videos in groups.items():
        median = statistics.median(v for _, v, _ in videos)
        if len(videos) < min_videos or median <= 0:
            thin.append({'канал': channel, 'роликов': len(videos), 'медиана': median})
            continue
        for row, views, age in videos:
            ratio = views / median
            if ratio >= multiple:
                result.append({'канал': channel, 'название': row.get('title', ''),
                               'просмотры': views, 'медиана_выборки': median,
                               'кратность': round(ratio, 3), 'возраст_дней': age, 'url': row.get('url', '')})
    return {'выбросы': sorted(result, key=lambda r: -r['кратность']),
            'недостаточная_база': thin, 'пропущено': skipped,
            'границы': 'Медиана относится к собранной выборке одного формата и окна возраста. Размер выборки и разный возраст ограничивают сравнение; причин успеха и прогноза вирусности нет.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('package', help='Проверить пару заголовок/текст обложки')
    p.add_argument('--title', required=True); p.add_argument('--thumbnail', required=True)
    p = sub.add_parser('retention', help='Прочитать подготовленный CSV удержания')
    p.add_argument('file', type=Path); p.add_argument('--axis', choices=['seconds', 'percent'], required=True)
    p.add_argument('--duration', type=float)
    p = sub.add_parser('outliers', help='Сравнить сопоставимые ролики из JSON')
    p.add_argument('file', type=Path); p.add_argument('--as-of', type=date.fromisoformat, required=True)
    p.add_argument('--min-age', type=int, default=7); p.add_argument('--max-age', type=int, default=90)
    p.add_argument('--format', default='shorts'); p.add_argument('--min-videos', type=int, default=4)
    p.add_argument('--multiple', type=float, default=2)
    args = parser.parse_args()
    try:
        if args.command == 'package':
            result = package(args.title, args.thumbnail)
        elif args.command == 'retention':
            result = retention(read_retention(args.file.read_text(encoding='utf-8-sig')), args.axis, args.duration)
        else:
            rows = json.loads(args.file.read_text(encoding='utf-8'))
            if not isinstance(rows, list):
                raise ValueError('Ожидается JSON-массив роликов.')
            result = outliers(rows, args.as_of, args.min_age, args.max_age, args.format, args.min_videos, args.multiple)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, 'Ошибка: ' + str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
