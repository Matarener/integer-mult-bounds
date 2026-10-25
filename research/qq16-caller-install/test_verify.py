"""Whole export replay and semantic authentication/receipt boundary controls.
Chris R, substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def snapshot(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}
class Boundary(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='qq16-caller-export-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'checkout';self.package=self.root/'research'/HERE.name
        shutil.copytree(HERE,self.package,ignore=shutil.ignore_patterns('__pycache__'))
        for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if r['usage']=='input':
                target=self.root/r['path'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/r['path'],target)
    def replay(self,*args,optimized=True,ok=True,needle='PASS_QQ16_ACTUAL_CALLER_INSTALLATION_CONTRACT'):
        env=dict(os.environ,PATH='/nonexistent-qq16-git-free')
        r=subprocess.run([sys.executable,'-I','-Werror','-B',*(['-O'] if optimized else []),
             str(self.package/'verify.py'),*args],cwd=self.root,env=env,capture_output=True,text=True,timeout=240)
        out=r.stdout+r.stderr;self.assertEqual(r.returncode==0,ok,out)
        if needle:self.assertIn(needle,out)
        if ok:self.assertFalse(r.stderr,out)
        return out
    def test_normal_optimized_readonly_export(self):
        for p in self.root.rglob('*'):
            if p.is_file():p.chmod(0o444)
        before=snapshot(self.root);self.replay(optimized=False);self.replay()
        self.assertFalse((self.root/'.git').exists());self.assertEqual(before,snapshot(self.root))
    def test_source_before_inherited_execution(self):
        source=self.root/'research/physical-complex-controller/machine.py';raw=source.read_bytes()
        source.write_bytes(b"raise RuntimeError('UNAUTHENTICATED_MACHINE_EXECUTED')\n"+raw)
        (self.package/'connection.py').write_text("raise RuntimeError('CONNECTION_EXECUTED')\n")
        out=self.replay(ok=False,needle='source integrity:')
        self.assertNotIn('UNAUTHENTICATED_MACHINE_EXECUTED',out)
        self.assertNotIn('CONNECTION_EXECUTED',out)
        source.write_bytes(raw)
        p=self.package/'inputs/PR4129-construction.py'
        p.write_bytes(b"raise RuntimeError('SIGNED_EXECUTED')\n"+p.read_bytes())
        out=self.replay(ok=False,needle='source integrity:');self.assertNotIn('SIGNED_EXECUTED',out)
    def test_manifest_word_and_exclusive_generation(self):
        for name,needle in [('SOURCES.json','manifest integrity:SOURCES.json'),
                ('PREDECESSORS.json','manifest integrity:PREDECESSORS.json'),
                ('inputs/PR4106-WORD.json','source integrity:')]:
            p=self.package/name;raw=p.read_bytes();p.write_bytes(raw+b' ')
            self.replay(ok=False,needle=needle);p.write_bytes(raw)
        before=snapshot(self.root)
        self.replay('--write',ok=False,needle='refuse receipt overwrite')
        self.assertEqual(before,snapshot(self.root))
    def test_whole_typed_receipt_validation(self):
        # Exercise the actual comparison used after fresh computation, using
        # complete expected objects. This avoids rerunning physical arithmetic
        # for mutations of transport metadata; full exports above recompute it.
        sys.path.insert(0,str(self.package))
        spec=importlib.util.spec_from_file_location('qq16_boundary_verifier',self.package/'verify.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        for name in m.NAMES:
            p=self.package/name;raw=p.read_bytes();expected=json.loads(raw)
            m.check_receipt(name,expected,self.package)
            changed=json.loads(raw)
            key=next(iter(changed));changed[key]=False
            p.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError,'whole typed receipt mismatch:'):
                m.check_receipt(name,expected,self.package)
            p.write_bytes(raw)
        self.assertNotEqual(m.A.typed(1),m.A.typed(True))
        p=self.package/'RESULT.json';raw=p.read_bytes()
        p.write_bytes(b'{"status":false,'+raw.lstrip()[1:])
        with self.assertRaisesRegex(ValueError,'duplicate JSON key:status'):
            m.check_receipt('RESULT.json',json.loads(raw),self.package)
if __name__=='__main__':unittest.main()
