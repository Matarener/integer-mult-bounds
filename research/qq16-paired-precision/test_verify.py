"""Authentication, typed receipts and Git-free normal/optimized replay controls.
Chris R / Clear1nsight with OpenAI Codex assistance. Apache-2.0.
"""
import hashlib,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def snapshot(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
class Boundary(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='qq16-precision-export-');self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)/'checkout';self.package=self.root/'research'/HERE.name
  shutil.copytree(HERE,self.package,ignore=shutil.ignore_patterns('__pycache__'))
  for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
   if row['usage']=='input':
    dest=self.root/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],dest)
 def replay(self,*args,optimized=True,ok=True,needle='PASS_QQ16_PAIRED_PRECISION_CONDITIONAL'):
  result=subprocess.run([sys.executable,'-I','-Werror','-B',*(['-O'] if optimized else []),str(self.package/'verify.py'),*args],cwd=self.root,capture_output=True,text=True,timeout=120)
  output=result.stdout+result.stderr;self.assertEqual(result.returncode==0,ok,output)
  if needle:self.assertIn(needle,output)
  return output
 def test_normal_and_optimized_readonly_export(self):
  for p in self.root.rglob('*'):
   if p.is_file():p.chmod(0o444)
  before=snapshot(self.root);self.replay(optimized=False);self.replay()
  self.assertFalse((self.root/'.git').exists());self.assertEqual(before,snapshot(self.root))
 def test_source_authentication_before_analyzers(self):
  source=self.root/'research/qq16-line-normalized-decoder/verify.py';raw=source.read_bytes()
  source.write_bytes(b"raise RuntimeError('SOURCE_EXECUTION_SENTINEL')\n"+raw)
  analyzer=self.package/'range.py';analyzer.write_text("raise RuntimeError('ANALYZER_EXECUTION_SENTINEL')\n")
  output=self.replay(ok=False,needle='source integrity:')
  self.assertNotIn('SOURCE_EXECUTION_SENTINEL',output);self.assertNotIn('ANALYZER_EXECUTION_SENTINEL',output)
 def test_manifest_vendor_and_exclusive_write(self):
  for name,needle in [('SOURCES.json','source manifest integrity'),('PREDECESSORS.json','predecessor manifest integrity'),('vendor/PR4106-WORD.json','retained source integrity:'),('vendor/PR4015-PROOF.md','retained source integrity:')]:
   p=self.package/name;raw=p.read_bytes();p.write_bytes(raw+b' ');self.replay(ok=False,needle=needle);p.write_bytes(raw)
  before=snapshot(self.root);self.replay('--write',ok=False,needle='refuse overwrite');self.assertEqual(before,snapshot(self.root))
 def test_whole_typed_receipts_and_duplicate_keys(self):
  mutations=[('RESULT.json',lambda r:r['exact_format'].__setitem__('new_minus_baseline_bits',False),'whole typed receipt mismatch:RESULT.json'),('RANGE.json',lambda r:r.__setitem__('same_sufficient_width',False),'range receipt mismatch'),('ROUNDING.json',lambda r:r.__setitem__('all_224_endpoint_envelopes_equal',False),'rounding receipt mismatch'),('COST.json',lambda r:r.__setitem__('forged_saving',800),'whole typed receipt mismatch:COST.json'),('POLYNOMIAL.json',lambda r:r.__setitem__('forged_degree',2),'whole typed receipt mismatch:POLYNOMIAL.json')]
  for name,mutate,needle in mutations:
   p=self.package/name;raw=p.read_bytes();obj=json.loads(raw);mutate(obj);p.write_text(json.dumps(obj));self.replay(ok=False,needle=needle);p.write_bytes(raw)
  p=self.package/'RESULT.json';raw=p.read_bytes();p.write_bytes(b'{"status":false,'+raw.lstrip()[1:]);self.replay(ok=False,needle='duplicate JSON key:status')
if __name__=='__main__':unittest.main()
