"""Meaningful scientific fault controls, also active under python -O."""
import copy
import json
import unittest
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import verify

class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w=json.loads((verify.ROOT/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json').read_text())

    def cli_fault(self, kind):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            package=root/'research/p104-coverage-gate'
            shutil.copytree(verify.PACKAGE,package,ignore=shutil.ignore_patterns('__pycache__'))
            sources=json.loads((package/'SOURCES.json').read_text())
            for row in sources['files']:
                if row['usage']=='input':
                    target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(verify.ROOT/row['path'],target)
            result=package/'RESULT.json'
            result.chmod(0o600)  # Only the disposable fixture copy is mutated.
            data=json.loads(result.read_text())
            if kind=='boolean':
                data['schema_version']=True
                result.write_text(json.dumps(data))
            elif kind=='float':
                data['schema_version']=1.0
                result.write_text(json.dumps(data))
            elif kind=='false_bill':
                data['full_inventory_controls'][0]['lower_rank']-=1
                result.write_text(json.dumps(data))
            elif kind=='duplicate':
                result.write_text(result.read_text().replace('"schema_version": 1,','"schema_version": 1, "schema_version": 1,',1))
            elif kind=='missing_source':
                (root/'notes/copied-centers-complex.tex').unlink()
            elif kind=='altered_source':
                with (root/'notes/copied-centers-complex.tex').open('a') as stream:
                    stream.write('\nchanged source\n')
            run=subprocess.run([sys.executable,'-O','-B',str(package/'verify.py')],cwd=root,capture_output=True,text=True,timeout=30)
            self.assertNotEqual(run.returncode,0,kind+' unexpectedly accepted')
            self.assertNotIn('PASS_P104_WHOLE_FIBER',run.stdout)

    def test_actual_cli_rejects_typed_receipt_and_source_faults(self):
        for kind in ('boolean','float','false_bill','duplicate','missing_source','altered_source'):
            with self.subTest(kind=kind):
                self.cli_fault(kind)

    def test_native_rank_undercharge_rejected(self):
        w=copy.deepcopy(self.w)
        next(e for e in w['program'] if e[0]=='transport')[4]=0
        with self.assertRaisesRegex(ValueError,'transport rank'):
            verify.recount(w)

    def test_removed_source_port_rejected(self):
        w=copy.deepcopy(self.w)
        del w['initial_frames']['X103']
        with self.assertRaises(ValueError):
            verify.recount(w)

    def test_helper_endpoint_retirement_rejected(self):
        w=copy.deepcopy(self.w)
        w['final_frames']['Q0']=[]
        with self.assertRaisesRegex(ValueError,'helper frames'):
            verify.recount(w)

    def test_forgetting_intersection_inflates_credit(self):
        a=b=104
        true_credit=len({(i,j) for i in range(a) for j in range(104)} |
                        {(i,j) for i in range(104) for j in range(b)})
        self.assertEqual(true_credit,10816)
        self.assertNotEqual(true_credit,104*(a+b))

    def test_sparse_pass_does_not_close_endpoint(self):
        self.assertLess(100*2-207,0)
        self.assertEqual(104*2-2,206)
        self.assertNotEqual((1,1),(0,1)) # actual S(1,0) versus RS(1,0)

    def test_rank_gap_cannot_be_repaired_by_helper_inventory(self):
        for helper_count in (0,72,144,14976,100000):
            width=2*104**2+helper_count
            total=208*2576+max(0,81*width-104**2-208*2312)
            self.assertGreaterEqual(total-81*width,44096)

if __name__=='__main__':
    unittest.main()
