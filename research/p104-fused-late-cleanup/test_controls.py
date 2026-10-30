#!/usr/bin/env python3
"""Run real optimized verifier processes against corrupted private fixtures."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile,unittest
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
class Controls(unittest.TestCase):
    def reject(self,kind):
        with tempfile.TemporaryDirectory(prefix='fused-cleanup-control-') as temp:
            root=Path(temp);package=root/'research/p104-fused-late-cleanup'
            shutil.copytree(P,package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            # Only private fixture copies become writable; read-only exports stay unchanged.
            package.chmod(0o700)
            for entry in package.rglob('*'):
                entry.chmod(0o700 if entry.is_dir() else 0o600)
            for row in json.loads((P/'SOURCES.json').read_text())['files']:
                if row['usage']=='input':
                    target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],target)
            path=root/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
            # Establish this private fixture can pass before each corruption.
            valid=subprocess.run([sys.executable,'-O','-B',str(package/'verify.py')],text=True,capture_output=True,timeout=60)
            self.assertEqual(valid.returncode,0,valid.stderr)
            result=package/'RESULT.json'
            if kind=='boolean':
                value=json.loads(result.read_text());value['schema_version']=True;result.write_text(json.dumps(value))
            elif kind=='float':
                value=json.loads(result.read_text());value['old_cleanup_unit_adds']=832.0;result.write_text(json.dumps(value))
            elif kind=='mass':
                value=json.loads(result.read_text());value['unit_adds_saved_against3981']=0;result.write_text(json.dumps(value))
            elif kind=='duplicate':
                result.write_text(result.read_text().replace('{','{"schema_version":1,',1))
            elif kind=='source':path.write_bytes(path.read_bytes()+b' ')
            elif kind=='missing':path.unlink()
            elif kind=='tail':
                target=package/'inputs/pr3882_verify.py';target.write_bytes(target.read_bytes()+b'\n# changed\n')
            done=subprocess.run([sys.executable,'-O','-B','-X','pycache_prefix='+str(root/'cache'),str(package/'verify.py')],text=True,capture_output=True,timeout=60)
            self.assertNotEqual(done.returncode,0,kind+' accepted')
            self.assertNotIn('PASS_P104_FUSED_LATE_CLEANUP',done.stdout)
    def test_boolean(self):self.reject('boolean')
    def test_float(self):self.reject('float')
    def test_false_mass(self):self.reject('mass')
    def test_duplicate_json(self):self.reject('duplicate')
    def test_source_bytes(self):self.reject('source')
    def test_missing_source(self):self.reject('missing')
    def test_tail_bytes(self):self.reject('tail')
if __name__=='__main__':unittest.main()
