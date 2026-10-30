#!/usr/bin/env python3
"""Boundary tests for the source-bound same-output fusion package."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def run_at(root,*extra,opt=True,env=None):
 argv=[sys.executable,'-I']+(['-O'] if opt else [])+['-Werror','-B',str(root/'research/qq16-streaming-recovery/verify.py'),*extra]
 return subprocess.run(argv,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=300)
def snapshot(root):
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
class Boundary(unittest.TestCase):
 def export(self):
  td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);root=Path(td.name)
  shutil.copytree(HERE,root/'research/qq16-streaming-recovery',ignore=shutil.ignore_patterns('__pycache__'))
  for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
   if r['usage']=='input':
    p=root/r['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/r['path'],p)
  return root
 def test_normal_and_optimized_readonly(self):
  before=snapshot(HERE)
  for opt in (False,True):
   p=run_at(ROOT,opt=opt);self.assertEqual(p.returncode,0,p.stdout);self.assertIn('PASS_QQ16_HOSTED_STREAMING_RECOVERY',p.stdout)
  self.assertEqual(snapshot(HERE),before)
 def test_git_free_readonly_export(self):
  root=self.export();before=snapshot(root)
  for p in root.rglob('*'):
   if p.is_file():p.chmod(0o444)
  env=dict(os.environ,PATH='/nonexistent',PYTHONDONTWRITEBYTECODE='1')
  p=run_at(root,env=env);self.assertEqual(p.returncode,0,p.stdout);self.assertEqual(snapshot(root),before)
 def test_source_authenticated_before_execution(self):
  root=self.export();p=root/'research/qq16-line-normalized-decoder/verify.py';p.write_text('raise RuntimeError("EXECUTED_CORRUPT_SOURCE")\n')
  out=run_at(root);self.assertNotEqual(out.returncode,0);self.assertIn('source hash:',out.stdout);self.assertNotIn('RuntimeError: EXECUTED',out.stdout)
 def test_full_word_and_typed_receipt(self):
  root=self.export();word=root/'research/qq16-streaming-recovery/WORD.json';original=word.read_bytes();w=json.loads(original);w[0][2]='identity';word.write_text(json.dumps(w))
  out=run_at(root);self.assertNotEqual(out.returncode,0);self.assertIn('whole word mismatch',out.stdout)
  word.write_bytes(original);receipt=root/'research/qq16-streaming-recovery/RESULT.json';r=json.loads(receipt.read_text());r['new_full_invoice']['line']=224.0;receipt.write_text(json.dumps(r))
  out=run_at(root);self.assertNotEqual(out.returncode,0);self.assertIn('whole typed receipt mismatch',out.stdout)
 def test_retained_word_integrity(self):
  root=self.export();p=root/'research/qq16-streaming-recovery/vendor/PR3985-WORD.json';p.write_bytes(p.read_bytes()+b' ')
  out=run_at(root);self.assertNotEqual(out.returncode,0);self.assertIn('retained PR3985 word hash',out.stdout)
 def test_generation_refuses_overwrite(self):
  before=snapshot(HERE);out=run_at(ROOT,'--write');self.assertNotEqual(out.returncode,0);self.assertIn('refuse overwrite',out.stdout);self.assertEqual(snapshot(HERE),before)
if __name__=='__main__':unittest.main(verbosity=2)
