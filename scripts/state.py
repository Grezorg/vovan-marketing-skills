#!/usr/bin/env python3
"""Хранить проверяемые контрольные точки и подтверждённые уроки."""
import argparse
import hashlib
import json
import os
import re
import tempfile
import fcntl
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
KINDS={'fact','decision','correction','open-task'}
SENSITIVE=re.compile(r'\b(?:sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9]{20,}|\d{7,12}:[A-Za-z0-9_-]{20,})|(?:password|api_key|access_token|пароль)\s*[:=]\s*\S+',re.I)

def now():return datetime.now(timezone.utc).isoformat()
def blank():return {'schema_version':1,'revision':0,'updated_at':None,'projects':{},'records':[],'lessons':[]}
def load(path):
    state=json.loads(path.read_text()) if path.exists() else blank()
    if state.get('schema_version')!=1:raise ValueError('Неподдерживаемая схема состояния')
    return state
def save(path,state):
    path.parent.mkdir(parents=True,exist_ok=True)
    state['revision']+=1;state['updated_at']=now()
    fd,tmp=tempfile.mkstemp(prefix='.state-',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as handle:
            json.dump(state,handle,ensure_ascii=False,indent=2);handle.write('\n')
            handle.flush();os.fsync(handle.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def required(payload,*keys):
    for key in keys:
        if not isinstance(payload.get(key),str) or not payload[key].strip():raise ValueError(f'Обязательное непустое поле: {key}')
    if SENSITIVE.search(json.dumps(payload,ensure_ascii=False)):raise ValueError('Не сохранять секреты в памяти системы')
def apply(state,action,payload):
    if action=='checkpoint':
        required(payload,'project','goal','source')
        project={k:payload[k] for k in ['project','goal','source','done','verified','next','blocked','decisions'] if k in payload}
        project['updated_at']=now();state['projects'][payload['project']]=project
        return project,True
    if action=='remember':
        required(payload,'project','kind','text','source')
        if payload['kind'] not in KINDS:raise ValueError('Неизвестный тип записи')
        fingerprint=hashlib.sha256(json.dumps([payload[k] for k in ['project','kind','text','source']],ensure_ascii=False).encode()).hexdigest()[:20]
        previous=next((e for e in state['records'] if e['id']==fingerprint),None)
        if previous:return previous,False
        supersedes=payload.get('supersedes')
        if supersedes:
            previous=next((e for e in state['records'] if e['id']==supersedes and e['project']==payload['project']),None)
            if not previous:raise ValueError('Нельзя заменить неизвестную запись или запись другого проекта')
            previous['status']='superseded'
        entry={'id':fingerprint,**{k:payload[k] for k in ['project','kind','text','source']},'status':'active','created_at':now()}
        if supersedes:entry['supersedes']=supersedes
        state['records'].append(entry);return entry,True
    if action=='learn':
        required(payload,'project','topic','rule','evidence')
        fingerprint=hashlib.sha256(json.dumps([payload[k] for k in ['project','topic','rule']],ensure_ascii=False).encode()).hexdigest()[:20]
        entry=next((e for e in state['lessons'] if e['id']==fingerprint),None)
        if not entry:
            entry={'id':fingerprint,**{k:payload[k] for k in ['project','topic','rule']},'evidence':[],'confirmed_by_user':False,'status':'candidate'}
            state['lessons'].append(entry)
        changed=False
        if payload['evidence'] not in entry['evidence']:entry['evidence'].append(payload['evidence']);changed=True
        if payload.get('confirmed_by_user') is True and not entry['confirmed_by_user']:entry['confirmed_by_user']=True;changed=True
        entry['status']='active' if len(entry['evidence'])>=2 or entry['confirmed_by_user'] else 'candidate'
        return entry,changed
    raise ValueError('Неизвестное изменение')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['show','health','checkpoint','remember','learn','export'])
    p.add_argument('--file',type=Path,default=ROOT/'references/state/os-state.json')
    p.add_argument('--project')
    args=p.parse_args()
    try:
        if args.action in ['checkpoint','remember','learn']:
            payload=json.load(__import__('sys').stdin)
            lock_dir=Path(tempfile.gettempdir())/'vovan-os-state-locks'
            lock_dir.mkdir(exist_ok=True)
            lock_name=hashlib.sha256(str(args.file.resolve()).encode()).hexdigest()+'.lock'
            with (lock_dir/lock_name).open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                state=load(args.file)
                if 'expected_revision' in payload and payload['expected_revision']!=state['revision']:
                    raise ValueError('Состояние изменилось; прочитать его перед повтором')
                output,changed=apply(state,args.action,payload)
                if changed:save(args.file,state)
            output={'record':output,'changed':changed,'revision':state['revision'],'persistence':'Локальная запись; постоянное сохранение подтверждать после синхронизации частного хранилища'}
        else:
            state=load(args.file)
            output=state
            if args.action=='health':
                output={'schema_version':state['schema_version'],'revision':state['revision'],'projects':len(state['projects']),'records':len(state['records']),'lessons':len(state['lessons']),'active_lessons':sum(e['status']=='active' for e in state['lessons'])}
            elif args.project:
                output={**state,'projects':{k:v for k,v in state['projects'].items() if k==args.project},'records':[r for r in state['records'] if r['project']==args.project],'lessons':[r for r in state['lessons'] if r['project']==args.project]}
        print(json.dumps(output,ensure_ascii=False,indent=2))
    except (ValueError,OSError) as error:raise SystemExit(str(error))

if __name__=='__main__':main()
