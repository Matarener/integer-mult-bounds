"""Independent finite and malformed controls for exact LP certificates."""
import copy
from fractions import Fraction as Q
from hashlib import sha256
import itertools
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'scripts/verify_rational_lp.py'
M=runpy.run_path(str(TOOL))

def problem(A,b,c):
    return {'schema':'integer-mult-rational-lp/v1','contract':'Declared test relaxation',
            'variables':[f'x{i}' for i in range(len(c))],
            'constraints':[{'id':f'row{i}','coefficients':row,'upper':v} for i,(row,v) in enumerate(zip(A,b))],
            'objective':c}

def cert(kind,**kwargs):return {'schema':'integer-mult-lp-certificate/v1','kind':kind,**kwargs}

class LPTests(unittest.TestCase):
    def test_fee_tradeoff_optimum_and_nonzero_gap(self):
        p=problem([[1,1],[1,4]],[3,6],[3,5])
        c=cert('bounds',primal=[2,1],dual=['7/3','2/3'])
        r=M['verify'](p,c)
        self.assertEqual(r['primal_value'],'11');self.assertEqual(r['gap'],'0');self.assertTrue(r['optimal'])
        candidates=[Q(3)*x+Q(5)*y for x,y in ((0,0),(3,0),(2,1),(0,Q(3,2)))]
        self.assertEqual(max(candidates),Q(r['dual_value']))
        c['primal']=[0,0];r=M['verify'](p,c)
        self.assertFalse(r['optimal']);self.assertEqual(r['gap'],'11')

    def test_81_exact_box_optima(self):
        for weights in itertools.product(range(-1,2),repeat=4):
            A=[[int(i==j) for j in range(4)] for i in range(4)];b=[1,2,3,4]
            p=problem(A,b,list(weights));x=[b[i] if c>0 else 0 for i,c in enumerate(weights)]
            r=M['verify'](p,cert('bounds',primal=x,dual=[max(0,c) for c in weights]))
            direct=max(sum(c*v for c,v in zip(weights,point)) for point in itertools.product(*[range(v+1) for v in b]))
            self.assertEqual(Q(r['dual_value']),direct);self.assertTrue(r['optimal'])

    def test_farkas_and_rejection_of_wrong_sign(self):
        p=problem([[-1],[1]],[-1,0],[1]);c=cert('infeasible',dual=[1,1])
        self.assertEqual(M['verify'](p,c)['dual_value'],'-1')
        for y in ([1,0],[0,1],[-1,1]):
            with self.assertRaises(ValueError):M['verify'](p,cert('infeasible',dual=y))
        self.assertTrue(M['verify'](problem([[1]],[-1],[0]),cert('infeasible',dual=[1]))['valid'])

    def test_unbounded_ray_needs_feasible_start_and_strict_gain(self):
        p=problem([[-1,1]],[-1],[1,1]);c=cert('unbounded',primal=[1,0],ray=[1,1])
        r=M['verify'](p,c);self.assertEqual(r['ray_gain'],'2')
        for point,ray in (([0,0],[1,1]),([1,0],[0,1]),([1,0],[0,0]),([1,0],[-1,0])):
            with self.assertRaises(ValueError):M['verify'](p,cert('unbounded',primal=point,ray=ray))

    def test_exact_rational_boundary_has_no_tolerance(self):
        p=problem([[3]],[1],[1]);c=cert('bounds',primal=['1/3'],dual=['1/3'])
        self.assertTrue(M['verify'](p,c)['optimal'])
        for bad in ('33333333333333333334/100000000000000000000',True,0.333,'1e-3','1/0'):
            with self.assertRaises(ValueError):M['verify'](p,cert('bounds',primal=[bad],dual=['1/3']))
        with self.assertRaises(ValueError):M['verify'](p,cert('bounds',primal=['1/3'],dual=['33333333333333333333/100000000000000000000']))

    def test_shape_name_and_certificate_failures(self):
        p=problem([[1]],[1],[1]);c=cert('bounds',primal=[1],dual=[1]);original=copy.deepcopy((p,c))
        M['verify'](p,c);self.assertEqual((p,c),original)
        for bad in (cert('bounds',primal=[],dual=[1]),cert('unknown'),{**c,'extra':1}):
            with self.assertRaises(ValueError):M['verify'](p,bad)
        for change in ({'variables':['x','x']},{'objective':[]},{'constraints':[]},{'contract':''}):
            with self.assertRaises(ValueError):M['verify']({**p,**change},c)

    def test_isolated_optimized_cli_exact_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/n for n in ('model.json','cert.json')]
            for path,value in zip(paths,(problem([[3]],[1],[1]),cert('bounds',primal=['1/3'],dual=['1/3']))):path.write_text(json.dumps(value))
            command=[sys.executable,'-I','-O',str(TOOL),*map(str,paths)]
            r=subprocess.run(command,capture_output=True,text=True,check=True,cwd=tmp);report=json.loads(r.stdout)
            for key,p in zip(('problem','certificate'),paths):self.assertEqual(report['inputs'][key]['sha256'],sha256(p.read_bytes()).hexdigest())
            paths[1].write_text('{"kind":1,"kind":2}');r=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')

if __name__=='__main__':unittest.main()
