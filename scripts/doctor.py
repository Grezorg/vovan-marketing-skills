#!/usr/bin/env python3
"""Проверить местную среду без сети, чтения ключей и платных вызовов."""
import importlib.util
import json
import platform
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

def inspect():
    spec=importlib.util.spec_from_file_location('vovan_router',ROOT/'scripts/os.py')
    router=importlib.util.module_from_spec(spec);spec.loader.exec_module(router)
    return {
        'version':router.version_status(),
        'python':platform.python_version(),
        'platform':platform.system(),
        'local_commands':{name:bool(shutil.which(name)) for name in ['python3','git','node','ffmpeg','ffprobe']},
        'external_services':'Не проверены. Наличие команды или инструмента не подтверждает доступ к аккаунту.',
        'quota_and_cost':'Неизвестны до проверки конкретного сервиса; ничего не покупать и не запускать ради диагностики.',
        'guidance':'references/capability-check.md'
    }

if __name__=='__main__':
    result=inspect();print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if result['version']['status']=='ошибка' else 0)
