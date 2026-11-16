#!/usr/bin/env python3
"""Проверять учебную страницу в Chromium; не отправлять внешние заявки."""
import argparse,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent

def run():
    checks=[];errors=[];external=[]
    with sync_playwright() as runtime:
        executable=shutil.which('chromium')
        browser=runtime.chromium.launch(**({'executable_path':executable} if executable else {}))
        for width in [1366,390,320]:
            page=browser.new_page(viewport={'width':width,'height':900})
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
            page.on('request',lambda request:external.append(request.url) if request.url.startswith(('http:','https:')) else None)
            page.goto((ROOT/'examples/service-launch/landing.html').as_uri())
            assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),f'Переполнение при {width}'
            page.get_by_role('link',name='Обсудить уборку').click()
            assert page.url.endswith('#request')
            page.get_by_role('button',name='Проверить учебную заявку').click()
            assert not page.locator('#result').inner_text()
            page.get_by_label('Учебный телефон').fill('+70000000000')
            page.get_by_label('Площадь, м²').fill('45')
            page.get_by_role('checkbox').check()
            assert page.locator('#lead-form').evaluate('(form)=>form.checkValidity()')
            page.get_by_role('button',name='Проверить учебную заявку').click()
            assert 'Никуда не отправлено' in page.locator('#result').inner_text()
            page.get_by_label('Площадь, м²').fill('0')
            page.get_by_role('button',name='Проверить учебную заявку').click()
            assert not page.locator('#result').inner_text()
            assert not page.locator('#lead-form').evaluate('(form)=>form.checkValidity()')
            checks.append({'viewport':width,'horizontal_overflow':False,'anchor':True,'empty_rejected':True,'valid_demo':True,'invalid_area_rejected':True})
            page.close()
        browser.close()
    assert not errors,errors
    assert not external,external
    return {'status':'пройдено','checked_at':datetime.now(timezone.utc).isoformat(),'browser':'Chromium через Playwright','checks':checks,'console_errors':errors,'external_requests':external,'limits':['Учебные данные','Внешняя доставка не подключена и не проверена','Другие браузеры не проверены']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write-report',action='store_true');args=parser.parse_args()
    result=run()
    if args.write_report:(ROOT/'examples/service-launch/checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
