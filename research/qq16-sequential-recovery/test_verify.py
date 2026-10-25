"""Meaningful boundary controls and normal/optimized Git-free read-only replay."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def snapshot(root):
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
class Boundary(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='qq16-paired-export-')
  self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)/'checkout';self.package=self.root/'research'/HERE.name
  shutil.copytree(HERE,self.package,ignore=shutil.ignore_patterns('__pycache__'))
  for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
   if row['usage']=='input':
    target=self.root/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],target)
 def run_verify(self,*args,optimized=True,ok=True,needle='PASS_QQ16_PAIRED_SOURCE_RECOVERY'):
  flags=['-I','-Werror','-B']+(['-O'] if optimized else [])
  result=subprocess.run([sys.executable,*flags,str(self.package/'verify.py'),*args],cwd=self.root,capture_output=True,text=True,timeout=300)
  output=result.stdout+result.stderr
  self.assertEqual(result.returncode==0,ok,output)
  if needle:self.assertIn(needle,output)
  return output
 def test_normal_and_optimized_readonly_export(self):
  for p in self.root.rglob('*'):
   if p.is_file():p.chmod(0o444)
  before=snapshot(self.root)
  self.run_verify(optimized=False)
  self.run_verify(optimized=True)
  self.assertFalse((self.root/'.git').exists())
  self.assertEqual(before,snapshot(self.root))
 def test_source_first_and_copied_executable(self):
  source=self.root/'research/qq16-line-normalized-decoder/verify.py';raw=source.read_bytes()
  source.write_bytes(b"raise RuntimeError('EXECUTED_UNAUTHENTICATED_SOURCE')\n"+raw)
  output=self.run_verify(ok=False,needle='source hash:')
  self.assertNotIn('EXECUTED_UNAUTHENTICATED_SOURCE',output)
  source.write_bytes(raw)
  replay=self.package/'replay.py';raw=replay.read_bytes()
  replay.write_bytes(b"raise RuntimeError('EXECUTED_UNAUTHENTICATED_REPLAY')\n"+raw)
  output=self.run_verify(ok=False,needle='copied executable integrity:')
  self.assertNotIn('EXECUTED_UNAUTHENTICATED_REPLAY',output)
 def test_manifests_vendor_word_and_exclusive_write(self):
  for filename,needle in [('SOURCES.json','source manifest integrity'),('PREDECESSORS.json','predecessor manifest integrity'),('vendor/PR4015-WORD.json','retained word integrity:')]:
   p=self.package/filename;raw=p.read_bytes();p.write_bytes(raw+b' ')
   self.run_verify(ok=False,needle=needle);p.write_bytes(raw)
  p=self.package/'WORD.json';raw=p.read_bytes();word=json.loads(raw);word.pop();p.write_text(json.dumps(word))
  self.run_verify(ok=False,needle='whole word mismatch');p.write_bytes(raw)
  before=snapshot(self.root)
  self.run_verify('--write',ok=False,needle='refuse overwrite')
  self.assertEqual(before,snapshot(self.root))
 def test_typed_receipt_and_duplicate_keys(self):
  p=self.package/'RESULT.json';raw=p.read_bytes();result=json.loads(raw)
  result['storage']['additional_owned']=False;p.write_text(json.dumps(result))
  self.run_verify(ok=False,needle='whole typed receipt mismatch')
  p.write_bytes(b'{"status":false,'+raw.lstrip()[1:])
  self.run_verify(ok=False,needle='duplicate JSON key:status')
if __name__=='__main__':unittest.main()
