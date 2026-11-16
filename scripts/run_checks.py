#!/usr/bin/env python3
"""Выполнить проверки и при необходимости записать отчёт конкретной сборки."""
import argparse,hashlib,json,os,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def run(private=False):
    commands=[['scripts/validate.py',*(['--private'] if private else [])],['scripts/test_router.py'],['scripts/test_state.py'],['scripts/test_youtube.py'],['scripts/check_integrity.py']]
    results=[]
    for args in commands:
        process=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONUTF8':'1'},timeout=120)
        results.append({'command':'python '+ ' '.join(args),'exit_code':process.returncode,'stdout':process.stdout.strip(),'stderr':process.stderr.strip()})
    version=json.loads((ROOT/'references/system.json').read_text(encoding='utf-8'))['version']
    fingerprints={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/os.py','scripts/state.py','scripts/validate.py','evals/routing-audit.json']}
    return {'status':'пройдено' if all(r['exit_code']==0 for r in results) else 'ошибка','version':version,'checked_at':datetime.now(timezone.utc).isoformat(),'platform':platform.system(),'python':platform.python_version(),'source_sha256':fingerprints,'checks':results,'limits':['Результаты только перечисленных проверок','Браузерный пример проверяется отдельным test_demo.py','Сценарные ответы и пользовательский пилот оцениваются отдельно','Нет измерения роста продаж, популярности или расхода токенов']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--private',action='store_true');parser.add_argument('--write-report',action='store_true');args=parser.parse_args()
    report=run(args.private)
    if args.write_report:
        if report['status']!='пройдено':raise SystemExit(json.dumps(report,ensure_ascii=False,indent=2))
        (ROOT/'references/validation-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        subprocess.run([sys.executable,str(ROOT/'scripts/build_release.py')],check=True,cwd=ROOT)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['status']=='пройдено' else 1)
