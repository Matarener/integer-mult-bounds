"""Compare exact fee polygons with direct tariff inequalities."""
import copy
from fractions import Fraction as Q
from hashlib import sha256
import itertools
import json
from pathlib import Path
import random
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'scripts/recursive_fee_region.py'
M=runpy.run_path(str(TOOL))

def invoice(paid=None,targets=None):
    return {'schema':'integer-mult-recursive-invoice/v1',
            'contract':{'model':'test','rank_semantics':'rank','ambient_rank':1000,'boundary':'same'},
            'paid':paid or {},'targets':targets or {}}

class RegionTests(unittest.TestCase):
    def test_exact_tradeoff_polygon_and_integer_budget(self):
        args=(invoice({'2':3}),invoice(),invoice({'1':1}),invoice({'4':1}))
        r=M['region'](*args,fixed_a=2)
        points={(Q(v['a']),Q(v['b'])) for v in r['vertices']}
        self.assertEqual(points,{(0,0),(3,0),(2,1),(0,Q(3,2))})
        self.assertEqual(r['fixed_a']['max_whole_b'],1)
        self.assertTrue(r['fixed_a']['next_b_rejected_at'])
        self.assertFalse(M['region'](*args,fixed_a=4)['fixed_a']['feasible'])

    def test_independent_integer_grid_and_pair_intersections(self):
        rng=random.Random(104)
        for case in range(30):
            old=invoice({str(r):rng.randrange(5) for r in (1,2,3,5)})
            new=invoice({str(r):rng.randrange(3) for r in (1,2,4)},{'2':rng.randrange(3)})
            fees=[invoice({str(rng.randrange(1,7)):rng.randrange(1,4)}) for _ in range(2)]
            r=M['region'](old,new,*fees)
            def cost(bill,cap):return sum(n*min(int(k),cap) for k,n in bill['paid'].items())-sum(n*min(int(k),cap) for k,n in bill['targets'].items())
            for x,y in itertools.product(range(6),repeat=2):
                direct=all(cost(new,k)-cost(old,k)+x*cost(fees[0],k)+y*cost(fees[1],k)<=0 for k in range(1,8))
                reported=all(row['a']*x+row['b']*y<=row['budget'] for row in r['constraints'])
                self.assertEqual(direct,reported,(case,x,y))
            if not r['feasible']:continue
            lines=[(Q(row['a']),Q(row['b']),Q(row['budget'])) for row in r['constraints']]+[(-Q(1),Q(0),Q(0)),(Q(0),-Q(1),Q(0))]
            vertices=set()
            for (a,b,c),(d,e,f) in itertools.combinations(lines,2):
                determinant=a*e-b*d
                if not determinant:continue
                x=(c*e-b*f)/determinant;y=(a*f-c*d)/determinant
                if all(A*x+B*y<=C for A,B,C in lines):vertices.add((x,y))
            actual={(Q(v['a']),Q(v['b'])) for v in r['vertices']}
            self.assertEqual(actual,vertices)

    def test_zero_slack_and_initial_obstruction(self):
        fee=invoice({'1':1})
        r=M['region'](invoice({'2':2}),invoice({'4':1}),fee,fee)
        self.assertEqual(r['vertices'],[{'a':'0','b':'0','binding_ranks':[4]}])
        self.assertEqual(M['region'](invoice(),fee,fee,fee)['obstruction']['budget'],-1)
        self.assertEqual(M['region'](fee,fee,fee,fee)['axis_bounds'],{'a':'0','b':'0'})

    def test_invalid_fee_contract_counts_and_support(self):
        fee=invoice({'1':1});old=invoice({'2':3})
        for bad in (invoice(),invoice({'1':1},{'1':1})):
            with self.assertRaises(ValueError):M['region'](old,invoice(),bad,fee)
        bad=copy.deepcopy(fee);bad['contract']['boundary']='other'
        with self.assertRaises(ValueError):M['region'](old,invoice(),bad,fee)
        with self.assertRaises(ValueError):M['region'](old,invoice(),fee,fee,True)
        old=invoice({str(r):1 for r in range(1,514)})
        with self.assertRaisesRegex(ValueError,'512'):M['region'](old,invoice(),fee,fee)

    def test_exact_large_counts_and_nonmutation(self):
        args=[invoice({'2':10**60}),invoice(),invoice({'1':10**60}),invoice({'4':10**60})]
        saved=copy.deepcopy(args);r=M['region'](*args,fixed_a=0)
        self.assertEqual(r['axis_bounds'],{'a':'1','b':'1/2'})
        self.assertEqual(args,saved)

    def test_isolated_optimized_cli_byte_bindings(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/f'{i}.json' for i in range(4)]
            for p,v in zip(paths,(invoice({'2':3}),invoice(),invoice({'1':1}),invoice({'4':1}))):p.write_text(json.dumps(v))
            command=[sys.executable,'-I','-O',str(TOOL),*map(str,paths),'--fixed-a','2']
            r=subprocess.run(command,capture_output=True,text=True,check=True,cwd=tmp)
            report=json.loads(r.stdout)
            for name,p in zip(('old','new','fee_a','fee_b'),paths):self.assertEqual(report['inputs'][name]['sha256'],sha256(p.read_bytes()).hexdigest())
            paths[2].write_text('{}')
            r=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')

if __name__=='__main__':unittest.main()
