#!/usr/bin/env python3
"""Проверять русские тексты, числовые форматы и пределы YouTube-помощника."""
import unittest
from datetime import date
from youtube import package, tokens, number, read_retention, retention, outliers

class YouTubeChecks(unittest.TestCase):
    def test_russian_duplicate(self):
        text = 'Как сделать рекламу без бюджета'
        self.assertIn('рекламу', package(text, text)['совпадения'])

    def test_yo_case_and_unicode(self):
        self.assertEqual(tokens('ЁЖ ＡＩ'), ['еж', 'ai'])
        self.assertIn('еж', package('Ёж говорит', 'ЕЖ')['совпадения'])

    def test_pair_without_duplicate(self):
        self.assertEqual(package('Проверка навыка на русском', 'РЕЗУЛЬТАТ УДИВИЛ')['совпадения'], [])

    def test_no_ctr_score(self):
        self.assertNotIn('score', package('Тест', 'Результат'))

    def test_semicolon_decimal_comma(self):
        self.assertEqual(read_retention('позиция;удержание\n0;100\n10;72,5\n'), [(0, 100), (10, 72.5)])

    def test_quoted_decimal_comma(self):
        self.assertEqual(read_retention('position,retention\n0,100\n10,"72,5"\n')[-1][1], 72.5)

    def test_malformed_csv(self):
        with self.assertRaises(ValueError):
            read_retention('position,retention\n0,100\n10,72,5\n')

    def test_increasing_axis(self):
        with self.assertRaises(ValueError):
            read_retention('position,retention\n1,100\n1,70\n')

    def test_explicit_seconds_for_short_video(self):
        result = retention([(0, 100), (15, 90), (30, 70)], 'seconds', 30)
        self.assertEqual(result['потеря_в_начале_пп'], 30)

    def test_percent_axis_needs_duration(self):
        with self.assertRaises(ValueError):
            retention([(0, 100), (100, 70)], 'percent')

    def test_rewatch_and_partial_curve(self):
        self.assertEqual(retention([(0, 120), (100, 110)], 'percent', 30)['потеря_в_начале_пп'], 10)
        self.assertIsNone(retention([(5, 100), (30, 70)], 'seconds', 30)['потеря_в_начале_пп'])

    def test_nonfinite_values(self):
        for value in ['nan', 'inf', '-inf']:
            with self.assertRaises(ValueError):
                number(value)
        with self.assertRaises(ValueError):
            retention([(0, 100), (30, 70)], 'seconds', float('nan'))

    def fixture(self):
        return [{'channel': 'Синтетический канал', 'title': 'Пример', 'views': value,
                 'published_at': '2026-10-20', 'format': 'shorts', 'video_id': str(i)}
                for i, value in enumerate([100, 100, 100, 500])]

    def test_channel_relative_outlier(self):
        result = outliers(self.fixture(), date(2026, 11, 6))
        self.assertEqual(len(result['выбросы']), 1)
        self.assertEqual(result['выбросы'][0]['кратность'], 5)

    def test_missing_dates_formats_and_duplicates(self):
        rows = self.fixture()
        rows += [dict(rows[0]), {'channel': 'Синтетический канал', 'views': 99999},
                 dict(rows[1], video_id='long', format='long'),
                 dict(rows[2], video_id='old', published_at='2025-01-01')]
        result = outliers(rows, date(2026, 11, 6))
        self.assertEqual(len(result['пропущено']), 4)
        self.assertEqual(result['выбросы'][0]['медиана_выборки'], 100)

    def test_thin_zero_and_rounded_counts(self):
        self.assertEqual(outliers(self.fixture()[:3], date(2026, 11, 6))['выбросы'], [])
        rows = [dict(r, views=0) for r in self.fixture()]
        self.assertEqual(outliers(rows, date(2026, 11, 6))['выбросы'], [])
        rows = [dict(r, views='1.8K') for r in self.fixture()]
        self.assertEqual(len(outliers(rows, date(2026, 11, 6))['пропущено']), 4)

if __name__ == '__main__':
    unittest.main(verbosity=2)
