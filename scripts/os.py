#!/usr/bin/env python3
"""Выбирать и читать русские процедуры Vovan OS."""
import argparse,json,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
ROUTES=[
('product-cards',['карточк','товар','маркетплейс']),
('automations',['напомн','по расписанию','ежеднев','каждый день','регулярно','автоматизац']),
('learning',['урок','усвоенные','полезный приём','обучение на']),
('memory',['сохрани состояние','продолжи проект','запомни','память','паспорт проекта','передачу проекта','передай проект']),
('skill-management',['наши навыки','нашу систему','навык','скилл','объедини систему']),
('marketing',['маркет','реклам','оффер','конверси','тариф','цены','продвиж','контент','пост','аналитик','покупател','текст','объявлен']),
('research',['найди','сравни','исслед','отзыв','проанализ','прогноз']),
('media',['видео','изображ','фото','картин','монтаж','клип','remotion','youtube','ютуб','shorts','рилс','reels','удержание зрителей','логотип','баннер','озвуч']),
('sites',['сайт','лендинг','интерфейс','веб','ui','react','next.js','playwright','палитр','типограф','проверь форм','проверка форм']),
('documents',['документ','презентац','таблиц','pdf','docx','xlsx','pptx','word','excel','договор']),
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
'ru-copywriting':['продающий текст','тексты лендинг','текст объявления'],
'ru-copy-editing':['сократи текст','отредактируй текст','перепиши текст'],
'ru-social':['пост','сообщество','vk','вк','telegram-канал'],
'ru-analytics':['аналитик','метрика'],
'ru-ab-testing':['эксперимент','a/b'],
'ru-frontend-design':['создай сайт','собери сайт','создай лендинг','дизайн','интерфейс','палитр','типограф','ui ux pro max'],
'ru-frontend-implementation':['react','next.js','nextjs','производительность интерфейса','ускорь сайт'],
'ru-webapp-testing':['проверь сайт','кнопк','форм','мобильн','playwright'],
'ru-image-production':['изображ','картин','фото','логотип','баннер','обложк'],
'ru-storyboard':['видео','сцен','раскадров'],
'ru-media-editing':['монтаж','склей','обрежь видео'],
'ru-remotion':['remotion'],
'ru-youtube-growth':['youtube','ютуб','shorts','рилс','reels','удержание зрителей','обложка ролика'],
'ru-python-bot':['бот','python'],
'ru-api-integration':['api','вебхук'],
'ru-docker-deploy':['vps','docker','деплой','сервер'],
'ru-github-workflow':['github','репозитор'],
'ru-database':['база данных','миграц','postgres','supabase'],
'ru-spreadsheet-economics':['таблиц','xlsx'],
'ru-document-check':['документ','презентац','pdf','word','договор'],
'ru-model-evaluation':['сравни навыки','сравни модели','оценка моделей'],
'ru-probabilistic-review':['прогноз','винрейт','экспресс'],
'ru-comparative-research':['сравни','сравнение']}
def catalog():return json.loads((ROOT/'references/catalog.json').read_text(encoding='utf-8'))
def version_status(expected_version=None):
 """Проверять сохранённые ресурсы, не считать описание навыка источником версии."""
 errors=[];version=None
 try:
  system=json.loads((ROOT/'references/system.json').read_text(encoding='utf-8'))
  version=system['version']
  if not isinstance(version,str) or not re.fullmatch(r'\d+\.\d+\.\d+',version):
   raise ValueError('Некорректная версия сборки.')
  skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
  marker=re.search(r'^Версия сборки: `([^`]+)`\.$',skill,re.M)
  if not marker or marker.group(1)!=version:errors.append('Версии SKILL.md и system.json не совпадают.')
  if len(catalog())!=system['counts']['subject_modules']:errors.append('Каталог не соответствует составу сборки.')
  manifest=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
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
def intent_text(query):
 """Отделять отказ и цитируемый материал от активного поручения; это эвристика."""
 q=query.casefold().replace('ё','е')
 q=re.sub(r'«[^»]*»|"[^"\n]*"',' ',q)
 if not q.strip():q=query.casefold().replace('ё','е')
 parts=re.split(r'[,;.!?\n]+|\b(?:но|вместо этого|а лучше)\b',q)
 active=[];excluded=[]
 for part in parts:
  part=part.strip()
  if not part:continue
  if re.search(r'\bне\s+(?:нужн\w*|надо|хочу|публику\w*|отправ\w*|создав\w*|создай|делай|напомина\w*|запуска\w*|покупа\w*|устанавлива\w*)\b',part):
   # Preserve a later explicit positive request even without punctuation.
   positive=re.search(r'\b(?:сделай|создай|подготовь|напиши|нарисуй|собери)\b',part)
   if positive and not re.search(r'\bне\s*$',part[:positive.start()]):
    excluded.append(part[:positive.start()]);active.append(part[positive.start():])
   else:excluded.append(part)
  else:active.append(part)
 return ' '.join(active),excluded

ARTIFACTS=[
 ('product-cards',r'\bкарточ\w*'),
 ('sites',r'\b(?:сайт\w*|лендинг\w*|интерфейс\w*|форм[уыа]\b|палитр\w*|типограф\w*|react\b|next\.js\b)'),
 ('documents',r'\b(?:документ\w*|договор\w*|презентац\w*|таблиц\w*|pdf\b|docx\b|xlsx\b|pptx\b|word\b|excel\b)'),
 ('software',r'\b(?:бот\w*|приложени\w*|код\b|сервер\w*|api\b|репозитор\w*|docker\b)'),
 ('media',r'\b(?:видео\w*|изображ\w*|фото\w*|картин\w*|ролик\w*|клип\w*|логотип\w*|баннер\w*|обложк\w*|озвучк\w*|shorts\b|рилс\w*|reels\b|remotion\b)'),
 ('marketing',r'\b(?:пост\w*|текст\w*|объявлен\w*|оффер\w*|кампани\w*|рекламу\b|контент\w*|стратеги\w*)')]
ACTION=r'\b(?:сделай|создай|собери|подготовь|напиши|нарисуй|разработай|спроектируй|сократи|перепиши|отредактируй|смонтируй|обрежь|исправь|проверь|ускорь|выбери|построй|оформи)\b'

def route(query):
 q,excluded=intent_text(query)
 scores=[(sum(w in q for w in words),d) for d,words in ROUTES]
 domains=[d for s,d in sorted(scores,key=lambda x:-x[0]) if s]
 primary=None;reason='Ключевые слова; подтвердить по смыслу.'
 memory=re.search(r'\b(?:паспорт\w* проект\w*|передач\w* проект\w*|передай проект|продолжи проект|покажи мои проекты|список проект\w*|перенеси (?:состояние )?проект\w*|сохрани состояние|запомни)',q)
 learning=any(w in q for w in ['полезный прием','усвоенные','усвоенных','урок','обучение на'])
 meta=re.search(r'\b(?:создай|обнови|улучши|исправь|проверь|объедини|добавь)\b.{0,35}\b(?:наш\w* систем\w*|навык\w*|навыки|скилл\w*)',q)
 first_action=re.search(ACTION,q)
 research=re.search(r'\b(?:найди|сравни|исследуй|поищи|проанализируй)\b',q)
 text_request=first_action and first_action.group() in ['напиши','сократи','перепиши','отредактируй']
 if any(w in q for w in ['быстрый старт','как начать','начать работу']):
  primary='dispatcher';reason='Первый запуск.'
 elif any(w in q for w in ['доступные возможности','что доступно','проверь подключения']):
  primary='integrations';reason='Проверка возможностей.'
 elif any(w in q for w in ['фактические затраты','расход токенов','покажи расходы']):
  primary='context-budget';reason='Измеримые затраты.'
 elif learning:
  primary='learning';reason='Подтвержденные уроки.'
 elif memory:
  primary='memory';reason='Продолжение и состояние проекта.'
 elif meta:
  primary='skill-management';reason='Изменение самой системы.'
 elif not text_request and (re.search(r'\b(?:напомни|напоминание|отмени напоминание|повторяющуюся задачу|по расписанию)\b',q) or re.search(r'\b(?:ежедневно|каждый день|каждую неделю|раз в месяц)\b',q)):
  primary='automations';reason='Будущее действие; требуется настоящий планировщик.'
 elif research and (not first_action or research.start()<first_action.start()) and not re.search(r'\b(?:удержание зрителей|ошибки в коде)\b',q):
  primary='research';reason='Запрошен поиск или сравнение.'
 elif first_action:
  tail=q[first_action.end():]
  hits=[(match.start(),domain) for domain,pattern in ARTIFACTS if (match:=re.search(pattern,tail))]
  if hits:
   primary=min(hits,key=lambda x:x[0])[1];reason='Первый явно запрошенный результат.'
 if primary is None:
  if any(w in q for w in ['youtube','ютуб','shorts','рилс','reels','удержание зрителей']):primary='media'
  else:primary=domains[0] if domains else 'dispatcher'
 supporting=[d for d in domains if d not in [primary,'quality','planning']][:3]
 selected=sorted([(sum(w in q for w in ws),n) for n,ws in MODULE_RULES.items()],key=lambda x:-x[0])
 entries={e['name']:e for e in catalog()}
 eligible={primary,*supporting}
 mods=[entries[n]['path'] for score,n in selected if score and entries[n]['domain'] in eligible][:6]
 if primary=='product-cards':
  mods=['references/modules/ru-product-cards.md']+[p for p in mods if p!='references/modules/ru-product-cards.md']
 if primary=='sites' and not mods:mods=['references/modules/ru-frontend-design.md']
 if primary=='media' and not mods:mods=['references/modules/ru-image-production.md' if any(w in q for w in ['логотип','баннер','картин','изображ']) else 'references/modules/ru-storyboard.md']
 if re.match(r'^\s*(?:(?:включи|запусти|примени)\s+)?[«"]?арен[ау]\s+3\b',query.casefold()):
  mods=['references/extensions/arena-3.md',*mods]
 cores=list(dict.fromkeys([primary,*supporting,'events','quality']))
 return {'primary':primary,'supporting':supporting,'core_paths':['references/core/'+d+'.md' for d in cores],'module_paths':mods,'reason':reason,'excluded_clauses':excluded,'needs_semantic_check':True,'note':'Рекомендация, не разрешение на действие. Сверить конечный результат, отрицания и ограничения; при конфликте выбрать по смыслу.'}
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
 elif a.stats:out=json.loads((ROOT/'references/system.json').read_text(encoding='utf-8'))
 elif a.commands:out=json.loads((ROOT/'references/commands.json').read_text(encoding='utf-8'))
 elif a.read:
  path=(ROOT/a.read).resolve()
  if not path.is_relative_to(ROOT) or path.suffix not in ['.md','.json'] or not path.is_file():raise SystemExit('Нужен существующий файл .md или .json внутри системы.')
  print(path.read_text(encoding='utf-8'));return
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

