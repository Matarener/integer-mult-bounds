"""Compare partition dynamic programs with independent count-vector enumeration."""
import copy
from decimal import Decimal,localcontext
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
TOOL=ROOT/'scripts/optimize_target_partition.py'
M=runpy.run_path(str(TOOL))

def invoice(paid=None,targets=None):
    return {'schema':'integer-mult-recursive-invoice/v1',
            'contract':{'model':'test','rank_semantics':'rank','ambient_rank':1000,'boundary':'same'},
            'paid':paid or {},'targets':targets or {}}

def plan(target,limit,options):
    return {'schema':'integer-mult-target-partition/v1','target_rank':target,'max_pieces':limit,
            'options':[{'id':name,'rank':rank,'fee':invoice(fee)} for name,rank,fee in options]}

class PartitionTests(unittest.TestCase):
    def test_complete_fee_aware_best_invoice(self):
        base=invoice({'16':2},{'16':1,'100':1})
        p=plan(16,8,[('one',1,{}),('four',4,{}),('nine',9,{'1':1})])
        saved=copy.deepcopy((base,p));r=M['optimize'](base,p,Q(1,2))
        self.assertTrue(r['certified_optimal']);self.assertEqual(r['best']['partition'],{'one':4,'four':3})
        self.assertEqual(r['best']['new_minus_baseline'],{'lower':'-6','upper':'-6'})
        self.assertEqual(r['best']['invoice'],invoice({'16':2},{'1':4,'4':3,'100':1}))
        self.assertEqual(r['recommendation'],'certified_improvement');self.assertEqual((base,p),saved)

    def test_36_small_models_against_decimal_enumeration(self):
        with localcontext() as context:
            context.prec=70
            for target,limit in itertools.product(range(2,11),range(2,6)):
                options=[(str(r),r,{'1':r%2}) for r in range(1,min(target,4))]
                p=plan(target,limit,options);base=invoice(targets={str(target):1})
                r=M['optimize'](base,p,Q(1,2))
                costs=[]
                for counts in itertools.product(range(limit+1),repeat=len(options)):
                    if sum(n*o[1] for n,o in zip(counts,options))!=target or not 2<=sum(counts)<=limit:continue
                    value=Decimal(target).sqrt()+sum(Decimal(n)*(Decimal(o[1]%2)-Decimal(o[1]).sqrt()) for n,o in zip(counts,options))
                    costs.append((value,counts))
                self.assertEqual(r['feasible'],bool(costs))
                if not costs:continue
                lo,hi=(Q(r['global_optimum'][k]) for k in ('lower','upper'))
                exact=min(value for value,counts in costs)
                self.assertLessEqual(Decimal(lo.numerator)/Decimal(lo.denominator),exact)
                self.assertGreaterEqual(Decimal(hi.numerator)/Decimal(hi.denominator),exact)
                if r['certified_optimal']:
                    chosen=tuple(r['best']['partition'].get(o[0],0) for o in options)
                    value=next(value for value,counts in costs if counts==chosen)
                    self.assertLess(abs(value-exact),Decimal('1e-60'))

    def test_excluded_alternative_dp_against_enumeration(self):
        opts=[{'rank':1,'lower':-1},{'rank':2,'lower':-3},{'rank':3,'lower':-2}]
        paths=[(sum(n*o['lower'] for n,o in zip(cs,opts)),cs) for cs in itertools.product(range(6),repeat=3)
               if sum(n*o['rank'] for n,o in zip(cs,opts))==6 and 2<=sum(cs)<=5]
        for cost,excluded in paths:
            expected=min((v for v in paths if v[1]!=excluded),default=None)
            self.assertEqual(M['dynamic'](opts,6,5,'lower',excluded),expected)

    def test_precision_and_no_improvement_are_explicit(self):
        base=invoice(targets={'4':1});p=plan(4,2,[('a',2,{'2':1000000}),('b',2,{'1':1414213})])
        low=M['optimize'](base,p,Q(1,2),16);high=M['optimize'](base,p,Q(1,2),128)
        self.assertFalse(low['certified_optimal']);self.assertTrue(high['certified_optimal'])
        self.assertEqual(high['best']['partition'],{'b':2})
        self.assertEqual(high['recommendation'],'no_strict_improvement_in_this_menu')

    def test_rank_256_limit_and_infeasible_menu(self):
        r=M['optimize'](invoice(targets={'256':1}),plan(256,32,[('eight',8,{})]),Q(1,2))
        self.assertTrue(r['certified_optimal']);self.assertIsNone(r['alternative'])
        self.assertEqual(r['best']['partition'],{'eight':32})
        r=M['optimize'](invoice(targets={'7':1}),plan(7,3,[('two',2,{})]),Q(1,2))
        self.assertFalse(r['feasible'])

    def test_full_menu_boundary_attains_equal_rank_concave_bound(self):
        p=plan(256,32,[(str(i),i,{}) for i in range(1,17)])
        r=M['optimize'](invoice(targets={'256':1}),p,Q(1,2))
        # Concavity bounds a 32-piece rank-256 split by 32*sqrt(8).
        # Fewer pieces have a smaller bound. Equal rank eight attains it.
        self.assertTrue(r['certified_optimal'])
        self.assertEqual(r['best']['partition'],{'8':32})

    def test_reject_missing_target_invalid_fee_overflow_and_limits(self):
        base=invoice(targets={'4':1});good=plan(4,3,[('one',1,{})])
        with self.assertRaises(ValueError):M['optimize'](invoice(),good,Q(1,2))
        bads=[]
        p=copy.deepcopy(good);p['options'][0]['fee']['targets']={'1':1};bads.append(p)
        p=copy.deepcopy(good);p['options'][0]['fee']['paid']={'1':10**60};bads.append(p)
        p=copy.deepcopy(good);p['options'][0]['rank']=4;bads.append(p)
        p=copy.deepcopy(good);p['max_pieces']=33;bads.append(p)
        p=copy.deepcopy(good);p['options']*=2;bads.append(p)
        for p in bads:
            with self.assertRaises(ValueError):M['optimize'](base,p,Q(1,2))

    def test_isolated_optimized_cli_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/n for n in ('base.json','plan.json')]
            for path,value in zip(paths,(invoice(targets={'4':1}),plan(4,4,[('one',1,{})]))):path.write_text(json.dumps(value))
            command=[sys.executable,'-I','-O',str(TOOL),*map(str,paths),'--exponent','1/2']
            r=subprocess.run(command,capture_output=True,text=True,check=True,cwd=tmp);report=json.loads(r.stdout)
            for key,p in zip(('baseline','plan'),paths):self.assertEqual(report['inputs'][key]['sha256'],sha256(p.read_bytes()).hexdigest())
            paths[1].write_text('{}');r=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')

if __name__=='__main__':unittest.main()
