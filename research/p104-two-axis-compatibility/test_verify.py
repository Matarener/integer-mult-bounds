#!/usr/bin/env python3
"""Behavioral and isolated CLI controls for the scoped two-axis audit."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('axis_primary',P/'verify.py')
V=importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labels,cls.D,cls.Di,_=V.geometry()

    def test_omitted_residual_update_rejects(self):
        r,b=[(0,0)]*104,[(0,0)]*104
        r[8]=(16,0)
        t=[0]*104
        self.assertNotEqual(V.physical_correct(r,b,self.D,self.Di,t),
                            V.conjugated(r,b,self.Di,t,wrong=True))

    def test_identity_inverse_reader_rejects(self):
        w=[(0,0)]*104
        w[8]=(16,0)
        self.assertNotEqual(V.halfmat(self.D,w),w)
        with self.assertRaises(ValueError):
            V.check_reader(self.D,V.reader_word(self.D)[:-1])

    def test_wrong_port_phase_rejects(self):
        r,b=[(0,0)]*104,[(0,0)]*104
        r[8]=(16,0)
        t=[(q&1).bit_count()%2 for q in self.labels]
        self.assertNotEqual(V.conjugated(r,b,self.Di,t),
                            V.conjugated(r,b,self.Di,[-v for v in t]))

    def test_homogeneous_axis_positive_control(self):
        # A common Fourier phase acts on every role, so any dyadic
        # bank matrix commutes with it. This is deliberately a positive case.
        a=[(16*i,-16*(i%3)) for i in range(104)]
        for k in range(4):
            self.assertEqual(V.halfmat(self.D,V.phase(a,[k]*104)),
                             V.phase(V.halfmat(self.D,a),[k]*104))

    def test_cost_and_fully_paid_banks(self):
        profile={1:1282,2:58,3:86,4:104,5:48,6:24,7:8,8:8}
        for b in (0,1,104,10000):
            self.assertEqual(V.cost_gate(profile,paid_banks=b)['excess'],44096)
        self.assertEqual(V.cost_gate(profile,extras=23)['excess'],44119)
        with self.assertRaises(ValueError):
            V.cost_gate(profile,extras=-1)
        with self.assertRaises(ValueError):
            V.cost_gate(profile,paid_banks=-1)

    def test_fixed_weight_nine_phase_rejects(self):
        counts=json.loads((P/'RESULT.json').read_text())['tensor_weights_mod_four']
        self.assertEqual(counts,{'1':5440,'3':5376})
        self.assertEqual((9-3)%4,2)
        self.assertEqual((2*(9-3))%4,0)

    def test_noncommutative_order(self):
        spec=importlib.util.spec_from_file_location('axis_independent',P/'independent.py')
        I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
        I.algebra()
        self.assertNotEqual(I.norm(('D','T')),I.norm(('T','D')))
        self.assertNotEqual(I.atom('H','d'),{})

    def test_git_free_read_only_and_real_cli_faults(self):
        sources=json.loads((P/'SOURCES.json').read_text())['files']
        with tempfile.TemporaryDirectory(prefix='two-axis-cli-') as d:
            root=Path(d)
            dest=root/'research'/P.name
            shutil.copytree(P,dest,ignore=shutil.ignore_patterns('__pycache__'))
            for row in sources:
                if row['usage']=='input':
                    q=root/row['path'];q.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(V.ROOT/row['path'],q)
            originals={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
            for p in originals:p.chmod(0o444)
            cmd=[sys.executable,'-I','-O','-B',str(dest/'verify.py')]
            def run():
                return subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=120)
            result=run()
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in originals.items()))
            receipt=dest/'RESULT.json';saved=receipt.read_bytes();receipt.chmod(0o644)
            x=json.loads(saved);x['schema_version']=True;receipt.write_text(json.dumps(x))
            self.assertNotEqual(run().returncode,0)
            receipt.write_bytes(saved)
            x=json.loads(saved);x['gate']['excess']-=1;receipt.write_text(json.dumps(x))
            self.assertNotEqual(run().returncode,0)
            receipt.write_bytes(saved)
            q=root/next(row['path'] for row in sources if row['usage']=='input')
            q.chmod(0o644);saved=q.read_bytes();q.write_bytes(saved+b'\n')
            self.assertNotEqual(run().returncode,0)
            q.write_bytes(saved);q.rename(q.with_suffix(q.suffix+'.missing'))
            self.assertNotEqual(run().returncode,0)

if __name__=='__main__':
    unittest.main()
