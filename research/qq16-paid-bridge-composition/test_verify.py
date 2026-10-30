#!/usr/bin/env python3
"""Read-only and negative boundary controls; Chris R/OpenAI, Apache-2.0.
Export/replay test structure follows credited sibling same-output fusion review.
"""
import hashlib,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACKAGE='research/qq16-paid-bridge-composition'
def run_at(root,*extra,opt=True,env=None):
 argv=[sys.executable,'-I']+(['-O'] if opt else [])+['-Werror','-B',str(root/PACKAGE/'verify.py'),*extra]
 return subprocess.run(argv,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
def snapshot(root):
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
class Boundary(unittest.TestCase):
 def export(self):
  td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);root=Path(td.name)
  shutil.copytree(HERE,root/PACKAGE,ignore=shutil.ignore_patterns('__pycache__'))
  for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
   if r['usage']=='input':
    p=root/r['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/r['path'],p)
  return root
 def reject(self,root,reason,*extra):
  out=run_at(root,*extra);self.assertNotEqual(out.returncode,0,out.stdout);self.assertIn(reason,out.stdout)
 def test_normal_optimized_readonly(self):
  before=snapshot(HERE)
  for opt in (False,True):
   out=run_at(ROOT,opt=opt);self.assertEqual(out.returncode,0,out.stdout);self.assertIn('PASS_QQ16_PAID_BRIDGE_COMPOSITION',out.stdout)
  self.assertEqual(snapshot(HERE),before)
 def test_git_free_readonly_export(self):
  root=self.export();before=snapshot(root)
  for p in root.rglob('*'):
   if p.is_file():p.chmod(0o444)
  out=run_at(root,env=dict(os.environ,PATH='/nonexistent',PYTHONDONTWRITEBYTECODE='1'))
  self.assertEqual(out.returncode,0,out.stdout);self.assertEqual(snapshot(root),before)
 def test_source_byte_authentication(self):
  root=self.export();p=root/'research/joint-query/certificate.json.gz';p.write_bytes(b'corrupt compressed input')
  self.reject(root,'input hash research/joint-query/certificate.json.gz')
 def test_source_blob_authentication(self):
  root=self.export();p=root/PACKAGE/'SOURCES.json';v=json.loads(p.read_text());next(r for r in v['files'] if r['usage']=='input')['git_blob']='0'*40;p.write_text(json.dumps(v));self.reject(root,'input Git blob')
 def test_pending_word_authentication(self):
  root=self.export();p=root/PACKAGE/'vendor/pr3952/WORD.json';p.write_bytes(p.read_bytes()+b' ');self.reject(root,'retained word SHA256')
 def test_whole_word_and_typed_receipt(self):
  root=self.export();p=root/PACKAGE/'WORDS.json';original=p.read_bytes();v=json.loads(original);v['direct_bridge'].append(['invented_event']);p.write_text(json.dumps(v));self.reject(root,'complete word mismatch')
  p.write_bytes(original);p=root/PACKAGE/'RESULT.json';v=json.loads(p.read_text());v['no_new_kappa']=1;p.write_text(json.dumps(v));self.reject(root,'complete typed receipt mismatch')
 def test_generation_refuses_overwrite(self):
  before=snapshot(HERE);self.reject(ROOT,'refuse overwrite','--write');self.assertEqual(snapshot(HERE),before)
if __name__=='__main__':unittest.main(verbosity=2)
