"""Complete export replay, authentication and receipt boundary controls."""
import hashlib,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def snapshot(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
class Boundary(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='qq16-native-export-');self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)/'checkout';self.package=self.root/'research'/HERE.name
  shutil.copytree(HERE,self.package,ignore=shutil.ignore_patterns('__pycache__'))
  for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
   if r['usage']=='input':
    target=self.root/r['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/r['path'],target)
 def replay(self,*args,optimized=True,ok=True,needle='PASS_QQ16_ACTUAL_RECURSIVE_BRIDGE_CONTRACT'):
  r=subprocess.run([sys.executable,'-I','-Werror','-B',*(['-O'] if optimized else []),str(self.package/'verify.py'),*args],cwd=self.root,capture_output=True,text=True,timeout=180)
  out=r.stdout+r.stderr;self.assertEqual(r.returncode==0,ok,out)
  if needle:self.assertIn(needle,out)
  if ok:self.assertFalse(r.stderr,out)
  return out
 def test_normal_optimized_readonly_export(self):
  for p in self.root.rglob('*'):
   if p.is_file():p.chmod(0o444)
  before=snapshot(self.root);self.replay(optimized=False);self.replay()
  self.assertFalse((self.root/'.git').exists());self.assertEqual(before,snapshot(self.root))
 def test_source_first_and_retained_executable(self):
  source=self.root/'research/physical-complex-controller/machine.py';raw=source.read_bytes()
  source.write_bytes(b"raise RuntimeError('UNAUTHENTICATED_MACHINE_EXECUTED')\n"+raw)
  (self.package/'construction.py').write_text("raise RuntimeError('ANALYZER_EXECUTED')\n")
  out=self.replay(ok=False,needle='source integrity:')
  self.assertNotIn('UNAUTHENTICATED_MACHINE_EXECUTED',out);self.assertNotIn('ANALYZER_EXECUTED',out)
  source.write_bytes(raw)
  p=self.package/'vendor/PR3884-tapes.py';p.write_bytes(b"raise RuntimeError('AXIS_EXECUTED')\n"+p.read_bytes())
  out=self.replay(ok=False,needle='source integrity:');self.assertNotIn('AXIS_EXECUTED',out)
 def test_manifest_word_and_exclusive_write(self):
  for name,needle in [('SOURCES.json','manifest integrity:SOURCES.json'),('PREDECESSORS.json','manifest integrity:PREDECESSORS.json'),('vendor/PR4106-WORD.json','source integrity:')]:
   p=self.package/name;raw=p.read_bytes();p.write_bytes(raw+b' ');self.replay(ok=False,needle=needle);p.write_bytes(raw)
  before=snapshot(self.root);self.replay('--write',ok=False,needle='refuse overwrite');self.assertEqual(before,snapshot(self.root))
 def test_whole_typed_receipt_and_duplicate_keys(self):
  for name,key,val in [('RESULT.json','actual73D_recipe_count',False),('CONTRACT.json','schema',False),('BILL.json','status',False),('BATCH.json','two_level_pool_224_impossible',False),('PHYSICAL.json','recursive_H1_tariff_admitted',True),('COVERAGE.json','positive',119)]:
   p=self.package/name;raw=p.read_bytes();r=json.loads(raw);r[key]=val;p.write_text(json.dumps(r));self.replay(ok=False,needle='whole typed receipt mismatch:'+name);p.write_bytes(raw)
  p=self.package/'RESULT.json';raw=p.read_bytes();p.write_bytes(b'{"status":false,'+raw.lstrip()[1:]);self.replay(ok=False,needle='duplicate JSON key:status')
if __name__=='__main__':unittest.main()
