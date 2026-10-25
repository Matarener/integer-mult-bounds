"""Scientific and actual-CLI controls; active under optimized Python."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import verify as v

class Controls(unittest.TestCase):
    def test_native_width_is_not_conjugacy_invariant(self):
        c=v.rotation(1,1);h=v.hadamard(1,0);out=v.mul(v.mul(h,c),h)
        self.assertEqual(v.phi(c),1);self.assertEqual(v.phi(out),0)
        self.assertEqual(v.defect(c),v.defect(out))

    def test_unmatched_endpoints_can_invalidate_bound(self):
        original=v.ident(3);changed=v.full(3)
        self.assertEqual(v.defect(original),0)
        self.assertEqual(v.phi(changed)-v.phi(original),3)

    def test_even_label_does_not_have_odd_complement_rank(self):
        rel=v.mul(v.full(3),v.inverse(v.rotation(3,3)))
        self.assertEqual(v.defect(rel),3)
        self.assertNotEqual(v.defect(rel),2)

    def test_changed_target_endpoint_changes_progress(self):
        q=7;c=v.rotation(3,q);f=v.full(3)
        old=v.defect(v.mul(f,v.inverse(c)));new=v.defect(f)
        self.assertEqual((old,new),(2,3))
        self.assertEqual(104*8+104*9+72*9,2416)

    def test_nonsymplectic_fault_rejected(self):
        bad=list(v.ident(2));bad[0]^=2
        with self.assertRaisesRegex(ValueError,'symplectic matrix'):v.symplectic(tuple(bad))

    def cli_fault(self,kind):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);package=root/'research/p104-translated-progress'
            shutil.copytree(v.P,package,ignore=shutil.ignore_patterns('__pycache__'))
            for row in json.loads((package/'SOURCES.json').read_text())['files']:
                if row['usage']=='input':
                    p=root/row['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(v.ROOT/row['path'],p)
            baseline=subprocess.run([sys.executable,'-O','-B',str(package/'verify.py')],cwd=root,capture_output=True,text=True,timeout=40)
            self.assertEqual(baseline.returncode,0,kind+' private baseline failed: '+baseline.stderr)
            self.assertIn('PASS_P104_TRANSLATED_PROGRESS',baseline.stdout)
            result=package/'RESULT.json';result.chmod(0o600);data=json.loads(result.read_text())
            if kind=='boolean':data['schema_version']=True;result.write_text(json.dumps(data))
            elif kind=='float':data['schema_version']=1.0;result.write_text(json.dumps(data))
            elif kind=='false_cap':data['changed_full_Y_endpoint_bound']=2312;result.write_text(json.dumps(data))
            elif kind=='false_adapter':data['counterexample']['translated_entry_adapter_B_rank']=0;result.write_text(json.dumps(data))
            elif kind=='duplicate':result.write_text(result.read_text().replace('"schema_version": 1,','"schema_version": 1, "schema_version": 1,',1))
            elif kind=='missing_source':(root/'research/p104-native-channel/compile.py').unlink()
            elif kind=='altered_source':
                with (root/'research/p104-native-channel/vendor/clifford_exact.py').open('a') as out:out.write('\nchanged source\n')
            run=subprocess.run([sys.executable,'-O','-B',str(package/'verify.py')],cwd=root,capture_output=True,text=True,timeout=40)
            self.assertNotEqual(run.returncode,0,kind+' unexpectedly accepted')
            self.assertNotIn('PASS_P104_TRANSLATED_PROGRESS',run.stdout)

    def test_actual_optimized_cli_rejects_receipt_and_source_faults(self):
        for kind in ('boolean','float','false_cap','false_adapter','duplicate','missing_source','altered_source'):
            with self.subTest(kind=kind):self.cli_fault(kind)

if __name__=='__main__':unittest.main()
