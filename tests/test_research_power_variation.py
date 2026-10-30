# SPDX-License-Identifier: Apache-2.0
"""Independent factored and Sturm oracles for general-rank certificates.

Ali Romman with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import compare_power_variation as V
import compare_power_polynomial as S
sys.path.pop(0)


def invoice(paid=None,targets=None):
    return {'schema':'integer-mult-recursive-invoice/v1','contract':{
        'model':'power-variation-fixture','rank_semantics':'r^t',
        'ambient_rank':10**9,'boundary':'same'},
        'paid':{str(r):n for r,n in (paid or {}).items()},
        'targets':{str(r):n for r,n in (targets or {}).items()}}


def compare_delta(delta,**options):
    return V.compare(invoice({r:-n for r,n in delta.items() if n<0}),
                     invoice({r:n for r,n in delta.items() if n>0}),**options)


def multiply(a,b):
    out={}
    for r,n in a.items():
        for s,m in b.items():out[r*s]=out.get(r*s,0)+n*m
    return {r:n for r,n in out.items() if n}


def factor_sign(base,threshold,t):
    # Integer exponentiation is independent of the directed square-root engine.
    a,b=t.numerator,t.denominator
    value=base**a*threshold.denominator**b-threshold.numerator**b
    return (value>0)-(value<0)


class PowerVariationTests(unittest.TestCase):
    def test_mixed_rank_endpoint_double_roots_settle_inconclusive_hinges(self):
        for delta,endpoint in [({1:1,2:-1,3:-1,6:1},'0'),
                               ({1:6,2:-3,3:-2,6:1},'1')]:
            old=invoice({r:-n for r,n in delta.items() if n<0})
            new=invoice({r:n for r,n in delta.items() if n>0})
            self.assertEqual(V.compare_invoices(old,new)['classification'],'inconclusive')
            with self.assertRaisesRegex(ValueError,'not powers'):S.compare(old,new)
            result=V.compare(old,new)
            self.assertEqual(result['classification'],'uniformly_higher')
            self.assertEqual(result['endpoint_multiplicity_lower_bounds'][endpoint],2)
            self.assertEqual(result['interior_roots'],0)
            self.assertEqual(V.compare(new,old)['classification'],'uniformly_lower')

    def test_two_crossings_with_matching_endpoint_signs_and_coarse_grid_rejection(self):
        delta={1:6,2:-4,3:-3,6:2}
        self.assertEqual(sum(delta.values()),1)
        self.assertEqual(sum(r*n for r,n in delta.items()),1)
        self.assertEqual(compare_delta(delta,grid=2)['classification'],'inconclusive')
        result=compare_delta(delta)
        self.assertEqual((result['classification'],result['interior_roots']),('crossing',2))
        for root,(base,threshold) in zip(result['root_witnesses'],[(2,Q(3,2)),(3,Q(2))]):
            self.assertEqual(factor_sign(base,threshold,Q(root['left']['t'])),-1)
            self.assertEqual(factor_sign(base,threshold,Q(root['right']['t'])),1)

    def test_16_mixed_rank_factored_profiles_have_independent_integer_root_witnesses(self):
        certified=0
        for a,b in product([Q(5,4),Q(3,2),Q(7,4),Q(15,8)],[Q(5,4),Q(3,2),Q(2),Q(5,2)]):
            delta=multiply({1:-a.numerator,2:a.denominator},
                           {1:-b.numerator,3:b.denominator})
            result=compare_delta(delta)
            if result['classification']=='inconclusive':continue
            certified+=1
            self.assertEqual(result['interior_roots'],2)
            for root in result['root_witnesses']:
                left,right=Q(root['left']['t']),Q(root['right']['t'])
                changes=sum(factor_sign(base,threshold,left)*factor_sign(base,threshold,right)<0
                            for base,threshold in [(2,a),(3,b)])
                self.assertEqual(changes,1)
        self.assertGreaterEqual(certified,12)

    def test_610_common_base_profiles_against_exact_sturm_not_sampling(self):
        fixtures=list(product(range(-3,4),repeat=3))+list(product(range(-1,2),repeat=5))
        fixtures += [tuple(int.from_bytes(sha256(f'{seed}:{i}'.encode()).digest(),'big')%7-3
                           for i in range(10)) for seed in range(24)]
        self.assertEqual(len(fixtures),610)
        certified=0
        for coefficients in fixtures:
            truth=S.classify_polynomial(coefficients,2)
            result=compare_delta({2**i:n for i,n in enumerate(coefficients) if n})
            if result['classification']=='inconclusive':
                self.assertLessEqual(result['interior_root_lower_bound'],truth['interior_roots'])
                self.assertGreaterEqual(result['interior_root_upper_bound'],truth['interior_roots'])
                continue
            certified+=1
            self.assertEqual(result['classification'],truth['classification'],coefficients)
            self.assertEqual(result['interior_roots'],truth['interior_roots'],coefficients)
        self.assertGreater(certified,200)

    def test_touching_roots_and_roots_outside_domain_remain_inconclusive(self):
        square=multiply({1:-3,2:2},{1:-3,2:2})
        result=compare_delta(square)
        self.assertEqual(result['classification'],'inconclusive')
        self.assertIsNone(result['interior_roots'])
        mixed=multiply(square,multiply({1:-2,3:1},{1:-2,3:1}))
        self.assertEqual(compare_delta(mixed)['classification'],'inconclusive')
        self.assertEqual(compare_delta(multiply({1:-3,2:1},{1:-4,3:1}))['classification'],'inconclusive')
        # This simple root is exactly on the power grid, not a sign-change pair.
        result=compare_delta({1:-2,4:1})
        self.assertEqual(result['interior_roots'],1)
        self.assertEqual(result['root_witnesses'][0]['exact']['t'],'1/2')
        tangent=compare_delta({1:4,4:-4,16:1})
        self.assertEqual(tangent['classification'],'inconclusive')
        self.assertEqual(tangent['interior_root_lower_bound'],1)
        self.assertEqual(tangent['unspent_root_budget'],1)
        unresolved=compare_delta({1:-2,8:1},bits=16,grid=3)
        self.assertEqual(unresolved['classification'],'inconclusive')
        self.assertEqual(unresolved['root_witnesses'],[])

    def test_endpoint_multiplicity_uses_exact_prime_valuations_at_large_counts(self):
        scale=10**60
        result=compare_delta({1:scale,2:-scale,3:-scale,6:scale})
        self.assertEqual(result['classification'],'uniformly_higher')
        self.assertEqual(V.endpoint_multiplicity({1:3,2:-2,3:-1},0),1)
        self.assertEqual(V.endpoint_multiplicity({1:7,2:-9,3:2},1),0)
        self.assertEqual(V.prime_factors(999999937),((999999937,1),))

    def test_target_debits_exact_cancellation_limits_and_contracts(self):
        old=invoice({2:1,3:1},{6:1});new=invoice({1:1})
        self.assertEqual(V.compare(old,new)['classification'],'uniformly_higher')
        same=invoice({r:10**60 for r in range(1,514)})
        self.assertEqual(V.compare(same,same)['classification'],'equal')
        with self.assertRaisesRegex(ValueError,'512'):V.compare(invoice(),same)
        for bits,grid in [(15,64),(257,64),(True,64),(128,1),(128,257),(128,True)]:
            with self.assertRaises(ValueError):V.compare(invoice(),invoice(),bits,grid)
        different=invoice();different['contract']['boundary']='changed'
        with self.assertRaisesRegex(ValueError,'contracts differ'):V.compare(invoice(),different)

    def test_real_cli_isolated_optimized_and_input_byte_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            old,new=Path(tmp)/'old.json',Path(tmp)/'new.json'
            old.write_text(json.dumps(invoice({2:1,3:1})))
            new.write_text(json.dumps(invoice({1:1,6:1})))
            command=[sys.executable,'-I','-O','-B',str(ROOT/'scripts/compare_power_variation.py'),str(old),str(new)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads(result.stdout)
            self.assertEqual(report['classification'],'uniformly_higher')
            self.assertEqual(report['inputs']['new']['sha256'],sha256(new.read_bytes()).hexdigest())
            new.write_text(json.dumps(invoice({1:True})))
            failed=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(failed.returncode,2)
            self.assertEqual(failed.stdout,'')


if __name__=='__main__':
    unittest.main()
