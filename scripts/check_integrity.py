#!/usr/bin/env python3
"""Проверять целостность рабочей сборки по манифесту."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent.parent
manifest=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
errors=[]
for entry in manifest['files']:
 path=(ROOT/entry['path']).resolve()
 if not path.is_relative_to(ROOT) or not path.is_file():
  errors.append('Нет файла: '+entry['path']);continue
 data=path.read_bytes()
 if len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
  errors.append('Изменён без обновления манифеста: '+entry['path'])
if errors:
 print(json.dumps({'status':'ошибка','errors':errors},ensure_ascii=False,indent=2));raise SystemExit(1)
print(json.dumps({'status':'пройдено','verified_files':len(manifest['files'])},ensure_ascii=False))

