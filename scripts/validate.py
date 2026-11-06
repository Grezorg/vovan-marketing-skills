#!/usr/bin/env python3
"""Проверять состав, ссылки, язык и маршруты Vovan OS."""
from pathlib import Path
import json,re,importlib.util,ast,argparse
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--private',action='store_true',help='Проверять установленную частную копию с личной памятью')
options=parser.parse_args()
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
cat=json.loads((ROOT/'references/catalog.json').read_text())
sys=json.loads((ROOT/'references/system.json').read_text())
check(len(cat)==sys['counts']['subject_modules'],'Количество процедур не совпадает.')
check(len({e['name'] for e in cat})==len(cat),'Повторяющийся идентификатор.')
check(len(list((ROOT/'references/core').glob('*.md')))==sys['counts']['core_modules'],'Количество модулей ядра не совпадает.')
check(len(list((ROOT/'references/guides').glob('*.md')))==sys['counts']['russian_guides'],'Количество справочников не совпадает.')
for e in cat:
 p=ROOT/e['path'];check(p.is_file(),'Нет файла '+e['path'])
 if p.is_file():
  t=p.read_text();check(re.match(r'^---\nname: '+re.escape(e['name'])+r'\n',t) is not None,'Имя модуля не совпадает '+e['path'])
  check(e.get('language')=='ru','Не русский модуль '+e['name'])
 for field in ['title','description']:
  check(bool(re.search('[А-Яа-яЁё]',e[field])),'Нет русского описания '+e['name'])
for p in ROOT.rglob('*.md'):
 text=p.read_text()
 text=re.sub(r'\x60\x60\x60.*?\x60\x60\x60','',text,flags=re.S)
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
  target=target.split('#',1)[0].strip()
  if not target or re.match(r'^[a-z][a-z0-9+.-]*:',target):continue
  dest=(p.parent/target).resolve()
  check(dest.is_relative_to(ROOT) and dest.exists(),'Нерабочая ссылка '+str(p.relative_to(ROOT))+': '+target)
active=[ROOT/'SKILL.md',ROOT/'references/pro-v3.md',ROOT/'references/routing.md',*list((ROOT/'references/modules').glob('*.md')),*list((ROOT/'references/core').glob('*.md')),*list((ROOT/'references/guides').glob('*.md')),*list((ROOT/'references/extensions').glob('*.md'))]
for p in active:
 t=p.read_text();check('upstream/' not in t,'Английская рабочая зависимость '+str(p.relative_to(ROOT)))
 t=re.sub(r'\x60\x60\x60.*?\x60\x60\x60','',t,flags=re.S)
 # Prose language, not identifiers, legal texts or code.
 for line in t.splitlines():
  if line.startswith(('name:','---')):continue
  clean=re.sub(r'https?://\S+|\]\([^)]*\)|[A-Za-z0-9_./-]+\.(?:md|py|json|txt|yaml)|\x60[^\x60]*\x60','',line)
  latin=len(re.findall('[A-Za-z]',clean));ru=len(re.findall('[А-Яа-яЁё]',clean))
  check(not(latin>90 and ru<latin/3),'Английская проза '+str(p.relative_to(ROOT))+': '+line[:90])
for p in (ROOT/'scripts').glob('*.py'):
 try:ast.parse(p.read_text())
 except SyntaxError as e:errors.append('Синтаксис '+p.name+': '+str(e))
spec=importlib.util.spec_from_file_location('vovan_router',ROOT/'scripts/os.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
check(mod.version_status(sys['version'])['status']=='согласовано','Проверка версии и ключевых ресурсов не пройдена.')
check(mod.version_status('0.0.0')['status']=='расхождение','Старый контекст навыка не обнаружен.')
cases={'Сделай 7 карточек товара по фото':'product-cards','Создай лендинг для услуги':'sites','Проверь текущий сайт':'sites','Создай бота записи':'software','Напомни завтра о проекте':'automations','Продолжи проект AtlasMind':'memory','Улучши наши навыки':'skill-management','Сравни телефоны по отзывам':'research','Создай таблицу экономики':'documents','Разработай рекламу услуги':'marketing','Смонтируй видео':'media'}
for q,expected in cases.items():
 r=mod.route(q);check(r['primary']==expected,'Маршрут '+q+': '+r['primary'])
 for path in r['core_paths']+r['module_paths']:check((ROOT/path).exists(),'Маршрут указывает на отсутствующий файл '+path)
required=['LICENSE','licenses/ECC-MIT.txt','licenses/ru-frontend-design-LICENSE.txt','licenses/ru-webapp-testing-LICENSE.txt','licenses/ru-design-polish-LICENSE.txt','licenses/ru-web-design-audit-LICENSE.txt']
required+=['licenses/UI-UX-Pro-Max-MIT.txt','licenses/Playwright-CLI-Apache-2.0.txt','licenses/YouTube-Agent-Skill-MIT.txt']
for p in required:check((ROOT/p).is_file(),'Нет лицензии '+p)
extension_cases={'Создай рекламный ролик Remotion':'ru-remotion','Ускорь компонент React':'ru-frontend-implementation','Проверь форму через Playwright CLI':'ru-webapp-testing','Проверь форму лендинга, но настоящую заявку не отправляй':'ru-webapp-testing','Проверь форму':'ru-webapp-testing','Выбери палитру и типографику':'ru-frontend-design','Сделай рилс для YouTube':'ru-youtube-growth','Проанализируй удержание зрителей':'ru-youtube-growth','Выбери тему для Shorts':'ru-youtube-growth'}
for query,name in extension_cases.items():
 check('references/modules/'+name+'.md' in mod.route(query)['module_paths'],'Не найдено дополнение по задаче '+query)
library=json.loads((ROOT/'references/extensions/design-library.json').read_text())
check(len(library['палитры'])==10 and len(library['шрифты'])==5,'Не совпадает состав дизайнерской подборки.')
def luminance(color):
 rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)]
 linear=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in rgb]
 return sum(a*b for a,b in zip(linear,[0.2126,0.7152,0.0722]))
for palette in library['палитры']:
 colors=palette['цвета']
 for a,b in [('основной','на основном'),('акцент','на акценте'),('фон','текст'),('карточка','на карточке'),('приглушённый фон','вторичный текст')]:
  values=[colors[a],colors[b]]
  valid=all(re.fullmatch(r'#[0-9A-Fa-f]{6}',v) for v in values)
  check(valid,'Некорректный цвет '+palette['задача'])
  if valid:
   lo,hi=sorted(map(luminance,values))
   check((hi+0.05)/(lo+0.05)>=4.5,'Недостаточный контраст '+palette['задача']+': '+a+'/'+b)
if not options.private:check(not (ROOT/'references/state/os-state.json').exists(),'Личная память не должна входить в публичный исходник.')
if errors:
 print(json.dumps({'status':'ошибка','errors':errors},ensure_ascii=False,indent=2));raise SystemExit(1)
print(json.dumps({'status':'пройдено','subject_modules':len(cat),'core_modules':18,'guides':6,'route_cases':len(cases)+len(extension_cases),'palette_pairs':50,'checks':['Состав','Русские описания и проза','Локальные ссылки','Синтаксис','Маршруты','Контраст подборки','Лицензии','Отделение личной памяти']},ensure_ascii=False,indent=2))

