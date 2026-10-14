#!/usr/bin/env python3
"""Выбирать и читать русские процедуры Vovan OS."""
import argparse,json,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
ROUTES=[
('product-cards',['карточк','товар','маркетплейс']),
('automations',['напомн','по расписанию','ежеднев','каждый день','регулярно','автоматизац']),
('learning',['урок','усвоенные','полезный приём','обучение на']),
('memory',['сохрани состояние','продолжи проект','запомни','память']),
('skill-management',['наши навыки','нашу систему','навык','скилл','объедини систему']),
('marketing',['маркет','реклам','оффер','конверси','тариф','цены','продвиж','контент','пост','аналитик','покупател']),
('research',['найди','сравни','исслед','отзыв','проанализ','прогноз']),
('media',['видео','изображ','фото','картин','монтаж','клип','remotion']),
('sites',['сайт','лендинг','интерфейс','веб','ui']),
('documents',['документ','презентац','таблиц','pdf','docx','xlsx','pptx']),
('software',['бот','сервер','vps','код','программ','api','docker','python','приложен','репозитор']),
('integrations',['подключ','интеграц','доступные возможности']),
('quality',['проверь результат','проверь качество','тест','ошибк','ревью']),
('planning',['составь план','спланируй','требования'])]
MODULE_RULES={
'ru-product-cards':['карточки товара','карточк','маркетплейс'],
'ru-pricing':['тариф','цены','цену','экономика'],
'ru-cro':['конверси','аудит лендинг','проверь лендинг'],
'ru-customer-research':['покупател','аудитори','отзывы клиентов'],
'ru-competitor-profiling':['конкурент'],
'ru-copywriting':['продающий текст','тексты лендинг'],
'ru-social':['пост','сообщество','vk','вк','telegram-канал'],
'ru-analytics':['аналитик','метрика'],
'ru-ab-testing':['эксперимент','a/b'],
'ru-frontend-design':['создай сайт','собери сайт','создай лендинг','дизайн','интерфейс'],
'ru-webapp-testing':['проверь сайт','кнопк','форма','мобильн'],
'ru-image-production':['изображ','картин','фото'],
'ru-storyboard':['видео','сцен','раскадров'],
'ru-media-editing':['монтаж','склей','обрежь видео'],
'ru-remotion':['remotion'],
'ru-python-bot':['бот','python'],
'ru-api-integration':['api','вебхук'],
'ru-docker-deploy':['vps','docker','деплой','сервер'],
'ru-github-workflow':['github','репозитор'],
'ru-database':['база данных','миграц','postgres','supabase'],
'ru-spreadsheet-economics':['таблиц','xlsx'],
'ru-document-check':['документ','презентац','pdf'],
'ru-model-evaluation':['сравни навыки','сравни модели','оценка моделей'],
'ru-probabilistic-review':['прогноз','винрейт','экспресс'],
'ru-comparative-research':['сравни','сравнение']}
def catalog():return json.loads((ROOT/'references/catalog.json').read_text())
def version_status(expected_version=None):
 """Проверять сохранённые ресурсы, не считать описание навыка источником версии."""
 errors=[];version=None
 try:
  system=json.loads((ROOT/'references/system.json').read_text())
  version=system['version']
  if not isinstance(version,str) or not re.fullmatch(r'\d+\.\d+\.\d+',version):
   raise ValueError('Некорректная версия сборки.')
  skill=(ROOT/'SKILL.md').read_text()
  marker=re.search(r'^Версия сборки: `([^`]+)`\.$',skill,re.M)
  if not marker or marker.group(1)!=version:errors.append('Версии SKILL.md и system.json не совпадают.')
  if len(catalog())!=system['counts']['subject_modules']:errors.append('Каталог не соответствует составу сборки.')
  manifest=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
  if manifest['version']!=version:errors.append('Версия манифеста не совпадает с system.json.')
  entries={e['path']:e for e in manifest['files']}
  for name in ['SKILL.md','references/system.json','references/catalog.json','scripts/os.py']:
   data=(ROOT/name).read_bytes();entry=entries.get(name)
   if not entry or len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
    errors.append('Нарушена целостность: '+name)
 except (OSError,ValueError,KeyError,TypeError) as e:
  errors.append('Не удалось проверить сборку: '+str(e))
 mismatch=expected_version is not None and expected_version!=version
 status='ошибка' if errors else ('расхождение' if mismatch else 'согласовано')
 return {'status':status,'installed_version':version,'loaded_version':expected_version,
         'errors':errors,'action':'Заново прочитать текущие ресурсы; не смешивать версии.' if status!='согласовано' else 'Использовать проверенную установленную сборку.',
         'cache_cleared':False}
def route(query):
 q=query.casefold()
 scores=[(sum(w in q for w in words),d) for d,words in ROUTES]
 domains=[d for s,d in sorted(scores,key=lambda x:-x[0]) if s]
 priority=[
 ('automations',any(w in q for w in ['напомн','ежеднев','каждый день','по расписанию'])),
 ('memory',any(w in q for w in ['сохрани состояние','продолжи проект','запомни'])),
 ('skill-management',any(w in q for w in ['создай навык','объедини навыки','улучши наши навыки'])),
 ('product-cards','карточк' in q and any(w in q for w in ['товар','ozon','wildberries','фото','маркетплейс'])),
 ('software','бот' in q and any(w in q for w in ['создай','сделай','исправь','запуст','собери'])),
 ('sites',any(w in q for w in ['сайт','лендинг']) and any(w in q for w in ['создай','собери','проверь','исправь','аудит'])),
 ('documents',any(w in q for w in ['docx','xlsx','pptx','таблиц','презентац']))]
 for domain,condition in priority:
  if condition:domains=[domain]+[d for d in domains if d!=domain];break
 primary=domains[0] if domains else 'dispatcher'
 supporting=[d for d in domains[1:] if d not in ['quality','planning']][:3]
 selected=sorted([(sum(w in q for w in ws),n) for n,ws in MODULE_RULES.items()],key=lambda x:-x[0])
 entries={e['name']:e for e in catalog()}
 # Selection is advisory; the outcome and core procedure decide whether it applies.
 eligible={primary,*supporting}
 mods=[entries[n]['path'] for score,n in selected if score and entries[n]['domain'] in eligible][:6]
 if primary=='product-cards':
  mods=['references/modules/ru-product-cards.md']+[p for p in mods if p!='references/modules/ru-product-cards.md']
 cores=list(dict.fromkeys([primary,*supporting,'events','quality']))
 return {'primary':primary,'supporting':supporting,'core_paths':['references/core/'+d+'.md' for d in cores],'module_paths':mods,'note':'Маршрут рекомендательный: читать только материалы, необходимые для результата.'}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 g=p.add_mutually_exclusive_group()
 g.add_argument('--route',help='Выбрать маршрут по поручению')
 g.add_argument('--search',nargs='+',help='Найти русскую процедуру')
 g.add_argument('--read',help='Прочитать файл внутри системы')
 g.add_argument('--exact',help='Найти по идентификатору или названию')
 g.add_argument('--stats',action='store_true',help='Показать состав')
 g.add_argument('--commands',action='store_true',help='Показать команды')
 g.add_argument('--version',action='store_true',help='Проверить версию и ключевые ресурсы')
 p.add_argument('--expected-version',help='Версия из прочитанного навыка; использовать с --version')
 p.add_argument('--kind',choices=['skills'])
 p.add_argument('--limit',type=int,default=12)
 a=p.parse_args()
 if a.expected_version and not a.version:p.error('--expected-version применять с --version')
 if a.version:
  out=version_status(a.expected_version)
  print(json.dumps(out,ensure_ascii=False,indent=2))
  raise SystemExit(1 if out['status']=='ошибка' else (2 if out['status']=='расхождение' else 0))
 if a.route:out=route(a.route)
 elif a.stats:out=json.loads((ROOT/'references/system.json').read_text())
 elif a.commands:out=json.loads((ROOT/'references/commands.json').read_text())
 elif a.read:
  path=(ROOT/a.read).resolve()
  if not path.is_relative_to(ROOT) or path.suffix not in ['.md','.json'] or not path.is_file():raise SystemExit('Нужен существующий файл .md или .json внутри системы.')
  print(path.read_text());return
 else:
  query=' '.join(a.search or []).casefold();terms=query.split();matches=[]
  for e in catalog():
   if a.exact and a.exact.casefold() not in [e['name'].casefold(),e['name'].removeprefix('ru-').casefold(),e['title'].casefold()]:continue
   fields=' '.join(str(e.get(k,'')) for k in ['name','title','description','keywords','domain']).casefold()
   score=sum(t in fields for t in terms)
   if terms and not score:continue
   matches.append((score,e))
  matches.sort(key=lambda x:-x[0]);out=[e for _,e in matches[:max(0,a.limit)]]
  if not out:raise SystemExit('Подходящий модуль не найден.')
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

