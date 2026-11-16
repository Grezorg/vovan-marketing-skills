#!/usr/bin/env python3
"""Регрессии выбора результата, отрицаний и команд."""
import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('router',ROOT/'scripts/os.py')
router=importlib.util.module_from_spec(spec);spec.loader.exec_module(router)

class RoutingChecks(unittest.TestCase):
    def test_audit_cases(self):
        for case in json.loads((ROOT/'evals/routing-audit.json').read_text(encoding='utf-8')):
            with self.subTest(query=case['query']):
                self.assertEqual(router.route(case['query'])['primary'],case['expected'])
    def test_paraphrases_and_restrictions(self):
        cases=[
            ('Собери лендинг с карточками товара','sites'),
            ('Напиши пост о создании сайтов','marketing'),
            ('Сделай видео о создании Telegram-бота','media'),
            ('Создай бота для публикации постов','software'),
            ('Подготовь презентацию с фотографиями','documents'),
            ('Найди примеры лендингов','research'),
            ('Сравни видеогенераторы','research'),
            ('Не публикуй видео, подготовь пост','marketing'),
            ('Не надо видео сделай пост','marketing'),
            ('Напиши текст напоминания','marketing'),
            ('Каждый день проверяй заявки','automations'),
            ('Не напоминай завтра, нарисуй баннер','media'),
            ('Сделай баннер с текстом «напомни завтра»','media'),
            ('Покажи мои проекты','memory'),
            ('Проверь подключения','integrations'),
            ('Быстрый старт','dispatcher'),
            ('Покажи фактические затраты','context-budget'),
        ]
        for query,expected in cases:
            with self.subTest(query=query):self.assertEqual(router.route(query)['primary'],expected)
    def test_paths_exist(self):
        for case in json.loads((ROOT/'evals/routing-audit.json').read_text(encoding='utf-8')):
            result=router.route(case['query'])
            self.assertLessEqual(len(result['supporting']),3)
            self.assertTrue(result['needs_semantic_check'])
            for path in result['core_paths']+result['module_paths']:
                self.assertTrue((ROOT/path).is_file(),path)
    def test_arena_explicit_only(self):
        self.assertEqual(router.route('Арена 3: сделай пост')['module_paths'][0],'references/extensions/arena-3.md')
        self.assertNotIn('references/extensions/arena-3.md',router.route('Объясни что такое Арена 3')['module_paths'])
    def test_only_prohibition(self):
        self.assertEqual(router.route('Не публикуй и не напоминай')['primary'],'dispatcher')
    def test_command_routes(self):
        commands=json.loads((ROOT/'references/commands.json').read_text(encoding='utf-8'))['commands']
        for command in commands:
            if command['say'].startswith('Арена 3'):continue
            with self.subTest(command=command['say']):
                self.assertEqual(router.route(command['say'])['primary'],command['core'])
if __name__=='__main__':unittest.main()

