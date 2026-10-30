"""Independent two-dimensional geometry and exact dual rejection tests."""
import copy
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import optimize_rational_box as tool


def problem(c,lo,hi,rows=(),seed=None):
    return {'schema':'rational-box-lp/v1','objective':c,'lower':lo,'upper':hi,
            'constraints':[{'coefficients':a,'bound':b} for a,b in rows],
            'feasible':seed if seed is not None else [0]*len(c)}


def geometric_oracle(v):
    rows=[([Q(x) for x in r['coefficients']],Q(r['bound'])) for r in v['constraints']]
    rows += [([Q(1),Q(0)],Q(v['upper'][0])),([Q(-1),Q(0)],-Q(v['lower'][0])),
             ([Q(0),Q(1)],Q(v['upper'][1])),([Q(0),Q(-1)],-Q(v['lower'][1]))]
    values=[]
    for (a,b),(c,d) in itertools.combinations(rows,2):
        det=a[0]*c[1]-a[1]*c[0]
        if not det:continue
        x=(b*c[1]-a[1]*d)/det;y=(a[0]*d-b*c[0])/det
        if all(row[0]*x+row[1]*y<=rhs for row,rhs in rows):
            values.append(Q(v['objective'][0])*x+Q(v['objective'][1])*y)
    return max(values)


class BoxTests(unittest.TestCase):
    def test_independent_geometric_oracle(self):
        rng=random.Random(810)
        for _ in range(100):
            v=problem([rng.randrange(-5,6),rng.randrange(-5,6)],[-2,-2],[3,3],
                      [([rng.randrange(-4,5),rng.randrange(-4,5)],rng.randrange(6)) for _ in range(5)])
            r=tool.optimize(v);self.assertEqual(Q(r['objective']),geometric_oracle(v));self.assertTrue(tool.verify(v,r))

    def test_fractional_triangle_optimum(self):
        v=problem([1,1,1],[0]*3,[1]*3,[([1,1,0],1),([0,1,1],1),([1,0,1],1)])
        r=tool.optimize(v);self.assertEqual(r['point'],['1/2']*3);self.assertEqual(r['objective'],'3/2')
        self.assertEqual(r['dual'][:3],['1/2']*3)

    def test_degenerate_box_and_zero_objective(self):
        v=problem([3,-1],[2,4],[2,4],[([0,0],0),([1,0],2)],[2,4])
        self.assertEqual(tool.optimize(v)['objective'],'2')
        v['objective']=[0,0];r=tool.optimize(v);self.assertEqual(r['bases_examined'],0)
        self.assertTrue(tool.verify(v,r))

    def test_certificate_mutations(self):
        v=problem([1,1],[0,0],[1,1],[([1,1],1)]);good=tool.optimize(v)
        for kind in ('point','dual','objective','negative'):
            bad=copy.deepcopy(good)
            if kind=='point':bad['point']=['2','2']
            if kind=='dual':bad['dual']=['0']*len(bad['dual'])
            if kind=='objective':bad['objective']='2'
            if kind=='negative':bad['dual'][0]='-1'
            with self.assertRaises(ValueError):tool.verify(v,bad)

    def test_six_dimensions_and_invalid_models(self):
        v=problem([1,-2,3,-4,5,-6],[-1]*6,[2]*6)
        self.assertEqual(tool.optimize(v)['objective'],'30')
        v['constraints']=[{'coefficients':[0]*6,'bound':0} for _ in range(12)]
        with self.assertRaisesRegex(ValueError,'50000'):tool.optimize(v)
        with self.assertRaisesRegex(ValueError,'incumbent'):tool.optimize(problem([1],[0],[1],seed=[2]))
        with self.assertRaises(ValueError):tool.optimize(problem([True],[0],[1]))

    def test_portable_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,c=Path(tmp)/'problem.json',Path(tmp)/'certificate.json';p.write_text(json.dumps(problem([2,1],[0,0],[1,1])))
            cmd=[sys.executable,'-O','-B',str(ROOT/'scripts/optimize_rational_box.py'),str(p)]
            out=subprocess.run(cmd,cwd=tmp,capture_output=True,text=True);self.assertEqual(out.returncode,0,out.stderr)
            c.write_text(out.stdout);self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,0)
            p.write_text(p.read_text()+'\n');self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,2)


if __name__=='__main__':unittest.main()
