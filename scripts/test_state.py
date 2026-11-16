#!/usr/bin/env python3
"""Проверка памяти на временных обезличенных данных."""
import importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('state',ROOT/'scripts/state.py')
state=importlib.util.module_from_spec(spec);spec.loader.exec_module(state)

class StateChecks(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.path=Path(self.directory.name)/'state.json'
    def tearDown(self):self.directory.cleanup()
    def call(self,action,payload=None,extra=None):
        return subprocess.run([sys.executable,str(ROOT/'scripts/state.py'),action,'--file',str(self.path),*(extra or [])],
            input=json.dumps(payload,ensure_ascii=False) if payload else None,
            text=True,encoding='utf-8',capture_output=True,env={**os.environ,'PYTHONUTF8':'1'},timeout=30)
    def test_empty_read_does_not_create(self):
        result=self.call('projects');self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['projects'],[])
        self.assertFalse(self.path.exists())
    def test_checkpoint_and_index(self):
        result=self.call('checkpoint',{'project':'Учебный','goal':'Проверить форму','source':'demo-v3','next':['Проверить доступ'],'blocked':['Нет доступа']})
        self.assertEqual(result.returncode,0,result.stderr)
        index=json.loads(self.call('projects').stdout)
        self.assertEqual(index['projects'][0]['source'],'demo-v3')
        self.assertEqual(index['projects'][0]['status'],'blocked')
    def test_deduplicate(self):
        payload={'project':'A','kind':'decision','text':'Только черновик','source':'demo'}
        a=json.loads(self.call('remember',payload).stdout);b=json.loads(self.call('remember',payload).stdout)
        self.assertTrue(a['changed']);self.assertFalse(b['changed']);self.assertEqual(a['revision'],b['revision'])
    def test_revision_conflict(self):
        payload={'project':'A','goal':'G','source':'demo','expected_revision':0}
        self.assertEqual(self.call('checkpoint',payload).returncode,0)
        self.assertNotEqual(self.call('checkpoint',payload).returncode,0)
        self.assertEqual(state.load(self.path)['revision'],1)
    def test_correction_scope(self):
        first=json.loads(self.call('remember',{'project':'A','kind':'decision','text':'X','source':'demo'}).stdout)
        result=self.call('remember',{'project':'B','kind':'correction','text':'Y','source':'demo','supersedes':first['record']['id']})
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(state.load(self.path)['records'][0]['status'],'active')
    def test_secret_rejected(self):
        result=self.call('remember',{'project':'A','kind':'fact','text':'password=DEMONSTRATION_ONLY','source':'demo'})
        self.assertNotEqual(result.returncode,0);self.assertFalse(self.path.exists())
    def test_learning_requires_evidence(self):
        payload={'project':'A','topic':'T','rule':'R','evidence':'one'}
        first=json.loads(self.call('learn',payload).stdout)
        self.assertEqual(first['record']['status'],'candidate')
        second=json.loads(self.call('learn',{**payload,'evidence':'two'}).stdout)
        self.assertEqual(second['record']['status'],'active')
    def test_concurrent_writes(self):
        processes=[]
        for i in range(5):
            p=subprocess.Popen([sys.executable,str(ROOT/'scripts/state.py'),'remember','--file',str(self.path)],
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',env={**os.environ,'PYTHONUTF8':'1'})
            p.stdin.write(json.dumps({'project':'A','kind':'fact','text':str(i),'source':'demo'}));p.stdin.close();p.stdin=None
            processes.append(p)
        for p in processes:
            _,err=p.communicate(timeout=30);self.assertEqual(p.returncode,0,err)
        result=state.load(self.path)
        self.assertEqual(result['revision'],5);self.assertEqual(len(result['records']),5)
    def test_bad_state_is_not_overwritten(self):
        self.path.write_text('{broken',encoding='utf-8')
        result=self.call('checkpoint',{'project':'A','goal':'G','source':'demo'})
        self.assertNotEqual(result.returncode,0);self.assertEqual(self.path.read_text(encoding='utf-8'),'{broken')
if __name__=='__main__':unittest.main()

