"""Complete finite grids, strict boundaries and exclusion-tree controls."""
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
import find_dyadic_parameters as tool


def problem(rows=(),max_bits=3,budget=5000):
    return {'schema':'dyadic-feasibility/v1','lower':[0,0],'upper':[1,1],
            'constraints':[{'coefficients':a,'bound':b,'strict':strict} for a,b,strict in rows],
            'max_bits':max_bits,'node_budget':budget}


def brute(v):
    for p in range(v['max_bits']+1):
        d=1<<p
        for z in itertools.product(range(d+1),repeat=2):
            ok=True
            for row in v['constraints']:
                total=sum(Q(a)*Q(x,d) for a,x in zip(row['coefficients'],z));b=Q(row['bound'])
                if not (total<b if row['strict'] else total<=b):ok=False;break
            if ok:return p
    return None


def narrow(budget=5000):
    return {'schema':'dyadic-feasibility/v1','lower':[0],'upper':[1],
            'constraints':[{'coefficients':[-1],'bound':'-1/3','strict':True},
                           {'coefficients':[1],'bound':'2/5','strict':True}],
            'max_bits':3,'node_budget':budget}


class DyadicTests(unittest.TestCase):
    def test_complete_grid_oracles(self):
        rng=random.Random(1003)
        for _ in range(120):
            v=problem([([rng.randrange(-2,3),rng.randrange(-2,3)],str(Q(rng.randrange(-2,6),4)),
                        bool(rng.randrange(2))) for _ in range(3)])
            r=tool.search(v);expected=brute(v)
            self.assertEqual(r['status'],'infeasible_through_limit' if expected is None else 'minimal')
            self.assertEqual(r['minimum_bits_upper'],expected);self.assertTrue(tool.verify(v,r))

    def test_selected_interval_minimum(self):
        v=json.loads((ROOT/'tests/fixtures/dyadic-parameters/selected-saving-interval.json').read_text())
        r=tool.search(v);self.assertEqual(r['status'],'minimal')
        self.assertEqual(r['feasible'],{'bits':20,'numerators':[3251]})
        self.assertEqual(r['infeasible'],{'bits':19,'tree':{'empty':True}})
        self.assertLess(r['nodes'],10)
        # Check signed ceiling/floor endpoints independently.
        self.assertEqual(tool.grid_box([Q(-2,3)],[Q(-1,3)],2),([-2],[-2]))

    def test_open_boundaries_and_budget_bracket(self):
        v=narrow();r=tool.search(v);self.assertEqual(r['feasible'],{'bits':3,'numerators':[3]})
        self.assertEqual(r['minimum_bits_lower'],3)
        r=tool.search(narrow(4));self.assertEqual(r['status'],'unresolved')
        self.assertEqual(r['minimum_bits_upper'],3);self.assertEqual(r['minimum_bits_lower'],0)
        r=tool.search(narrow(1));self.assertEqual(r['status'],'unresolved');self.assertIsNone(r['feasible'])

    def test_false_exclusions_and_points(self):
        v=narrow();good=tool.search(v)
        for kind in ('point','row','partition','bracket','work'):
            bad=copy.deepcopy(good)
            if kind=='point':bad['feasible']['numerators']=[4]
            if kind=='row':bad['infeasible']['tree']={'row':0}
            if kind=='partition':bad['infeasible']['tree'].pop('right')
            if kind=='bracket':bad['minimum_bits_upper']=0
            if kind=='work':bad['nodes']=1
            with self.assertRaises(ValueError):tool.verify(v,bad)

    def test_dimension_constraint_and_precision_limits(self):
        v={'schema':'dyadic-feasibility/v1','lower':['1/3']*8,'upper':['1/2']*8,
           'constraints':[{'coefficients':[0]*8,'bound':0,'strict':False} for _ in range(64)],
           'max_bits':30,'node_budget':100}
        self.assertEqual(tool.search(v)['minimum_bits_upper'],1)
        v['constraints'].append(v['constraints'][0])
        with self.assertRaises(ValueError):tool.search(v)
        v=problem();v['max_bits']=31
        with self.assertRaises(ValueError):tool.search(v)
        v=problem();v['constraints']=[{'coefficients':[1,0],'bound':1,'strict':1}]
        with self.assertRaises(ValueError):tool.search(v)

    def test_portable_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,c=Path(tmp)/'problem.json',Path(tmp)/'certificate.json';p.write_text(json.dumps(narrow()))
            cmd=[sys.executable,'-O','-B',str(ROOT/'scripts/find_dyadic_parameters.py'),str(p)]
            out=subprocess.run(cmd,cwd=tmp,capture_output=True,text=True);self.assertEqual(out.returncode,0,out.stderr)
            c.write_text(out.stdout);self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,0)
            p.write_text(p.read_text()+'\n');self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,2)


if __name__=='__main__':unittest.main()
