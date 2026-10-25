#!/usr/bin/env python3
"""Boundary and export controls for the explicit dirty-ancilla schedules."""
from pathlib import Path
import copy,hashlib,json,shutil,subprocess,sys,tempfile,types,unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def load(path):
 m=types.ModuleType('test_subject');m.__file__=str(path)
 exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
class Boundaries(unittest.TestCase):
 def test_primitive_invoice(self):
  v=load(HERE/'verify.py')
  with self.assertRaisesRegex(ValueError,'unpriced'):v.invoice([['add','Q0','S','1/3']])
  self.assertNotEqual(v.canonical({'x':1}),v.canonical({'x':True}))
  self.assertNotEqual(v.canonical({'x':1}),v.canonical({'x':1.0}))
  with self.assertRaises(ValueError):v.canonical({'x':float('nan')})
 def test_minimal_export_failure_controls_and_readonly_replay(self):
  with tempfile.TemporaryDirectory(prefix='qq16-dirty-') as tmp:
   root=Path(tmp);dest=root/'research'/HERE.name
   shutil.copytree(HERE,dest,ignore=shutil.ignore_patterns('__pycache__'))
   for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
    if item['usage']!='input':continue
    p=root/item['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/item['path']).read_bytes())
   v=load(dest/'verify.py');v.authenticate()
   # Each pre-execution manifest/source/data failure is exercised independently.
   for path,reason in [(dest/'SOURCES.json','manifest'),(dest/'PREDECESSORS.json','manifest'),(root/'research/qq16-line-normalized-decoder/verify.py','source SHA'),(dest/'vendor/pr3985/WORD.json','retained SHA')]:
    raw=path.read_bytes();path.write_bytes(raw+b' ')
    with self.assertRaisesRegex(ValueError,reason):v.authenticate()
    path.write_bytes(raw)
   words=json.loads((dest/'WORDS.json').read_text());result=json.loads((dest/'RESULT.json').read_text())
   receipt=dest/'RESULT.json';raw=receipt.read_bytes();changed=copy.deepcopy(result);changed['borrowed_contract']['clear_operations']=False;receipt.write_text(json.dumps(changed))
   with self.assertRaisesRegex(ValueError,'typed result'):v.check_receipts(words,result)
   receipt.write_bytes(raw)
   literal=dest/'WORDS.json';raw=literal.read_bytes();changed=copy.deepcopy(words);changed['fixed_query_frame'].pop();literal.write_text(json.dumps(changed))
   with self.assertRaisesRegex(ValueError,'words mismatch'):v.check_receipts(words,result)
   literal.write_bytes(raw)
   p=subprocess.run([sys.executable,'-I','-B',str(dest/'verify.py'),'--write'],cwd=root,capture_output=True,text=True)
   self.assertNotEqual(p.returncode,0);self.assertIn('refuse overwrite',p.stderr)
   before={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
   try:
    for p in root.rglob('*'):p.chmod(0o555 if p.is_dir() else 0o444)
    root.chmod(0o555)
    for flags in ([],['-O']):
     p=subprocess.run([sys.executable,'-I',*flags,'-Werror','-B',str(dest/'verify.py')],cwd=root,capture_output=True,text=True,timeout=280)
     self.assertEqual(p.returncode,0,p.stderr)
     self.assertIn('PASS_QQ16_DIRTY_COMMUTATOR no_new_kappa',p.stdout)
    after={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
    self.assertEqual(before,after);self.assertFalse((root/'.git').exists())
   finally:
    root.chmod(0o755)
    for p in root.rglob('*'):p.chmod(0o755 if p.is_dir() else 0o644)
if __name__=='__main__':unittest.main(verbosity=2)
