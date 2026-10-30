"""Check interval certificates against exact powers and independent decimals."""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('interval_cover', ROOT/'scripts/compare_recursive_intervals.py')
M = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)


def invoice(paid=None, targets=None):
    return {'schema': 'integer-mult-recursive-invoice/v1',
            'contract': {'model': 'fixture', 'rank_semantics': 'dimension', 'ambient_rank': 10**9, 'boundary': 'fixed'},
            'paid': paid or {}, 'targets': targets or {}}


class IntervalCoverTests(unittest.TestCase):
    def test_selected_complete_bill_unique_crossing(self):
        bill=json.loads((ROOT/'tests/fixtures/recursive-invoice-selected5599.json').read_text())
        zero={**bill,'paid':{},'targets':{}}
        self.assertEqual(sum(bill['paid'].values()),66726)
        self.assertEqual(sum(bill['targets'].values()),13048)
        result=M.cover(zero,bill,Q(99,100),Q(1),128,511,30)
        self.assertTrue(result['resolved_everywhere'])
        crossing=[c for c in result['cells'] if c['classification']=='single_crossing']
        self.assertEqual(len(crossing),1)
        self.assertEqual((crossing[0]['left'],crossing[0]['right']),
                         ('53520636719/53687091200','107041273439/107374182400'))

    def test_log_bounds_against_independent_decimal(self):
        with localcontext() as ctx:
            ctx.prec = 140
            for rank in (1, 2, 3, 4, 7, 31, 127, 65521, 10**9):
                exact = Decimal(rank).ln()
                for bits in (16, 64, 128, 256):
                    lo, hi = M.log_bounds(rank, bits)
                    self.assertLessEqual(Decimal(lo.numerator)/lo.denominator, exact)
                    self.assertGreaterEqual(Decimal(hi.numerator)/hi.denominator, exact)
                    self.assertLessEqual(hi-lo, Q(128, 2**bits))

    def test_every_box_bounds_independent_power_values(self):
        with localcontext() as ctx:
            ctx.prec = 110
            for coefficients in ((2,-3,1), (-4,1,1), (5,-7,2), (0,3,-2)):
                delta = dict(zip(('1','2','3'), coefficients))
                engine = M.Kernel(delta, 96)
                for a,b in ((Q(0),Q(1)), (Q(1,8),Q(3,8)), (Q(7,8),Q(1))):
                    bounds, derivative, _, _ = engine.bounds(a,b)
                    for j in range(9):
                        t=a+(b-a)*Q(j,8); td=Decimal(t.numerator)/t.denominator
                        value=sum(Decimal(c)*Decimal(r)**td for r,c in delta.items())
                        slope=sum(Decimal(c)*Decimal(r)**td*Decimal(r).ln() for r,c in delta.items())
                        for actual,(lo,hi) in ((value,bounds),(slope,derivative)):
                            self.assertLessEqual(Decimal(lo.numerator)/lo.denominator,actual+Decimal('1e-100'))
                            self.assertGreaterEqual(Decimal(hi.numerator)/hi.denominator,actual-Decimal('1e-100'))

    def test_noncommensurate_unique_crossing_and_full_cover(self):
        old,new=invoice({'1':4}),invoice({'2':1,'3':1})
        coarse=M.cover(old,new,max_boxes=1)
        self.assertEqual(coarse['cells'][0]['classification'],'single_crossing')
        refined=M.cover(old,new,max_boxes=255,max_depth=18)
        cells=refined['cells']; self.assertEqual(Q(cells[0]['left']),0);self.assertEqual(Q(cells[-1]['right']),1)
        for a,b in zip(cells,cells[1:]):self.assertEqual(a['right'],b['left'])
        crossing=[c for c in cells if c['classification']=='single_crossing']
        self.assertEqual(len(crossing),1)
        self.assertLessEqual(Q(crossing[0]['right'])-Q(crossing[0]['left']),Q(1,2**18))
        self.assertTrue(refined['resolved_everywhere'])

    def test_target_debits_equality_and_unresolved_are_distinct(self):
        self.assertEqual(M.cover(invoice(),invoice())['cells'][0]['classification'],'equal')
        out=M.cover(invoice(targets={'2':1}),invoice(),Q(1,4),Q(3,4))
        self.assertEqual(out['cells'][0]['classification'],'new_cost_higher')
        out=M.cover(invoice({'2':4}),invoice({'4':1,'1':4}),max_boxes=1)
        self.assertEqual(out['cells'][0]['classification'],'unresolved')
        self.assertFalse(out['resolved_everywhere'])

    def test_invalid_budget_contract_and_support_fail(self):
        for kwargs in ({'left':Q(1),'right':Q(0)}, {'max_boxes':True}, {'max_boxes':2048},
                       {'max_depth':41}, {'bits':15}, {'left':0.1}):
            with self.assertRaises(ValueError):M.cover(invoice(),invoice(),**kwargs)
        with self.assertRaises(ValueError):M.cover(invoice(),invoice({str(r):1 for r in range(1,66)}))
        other=invoice();other['contract']['boundary']='other'
        with self.assertRaises(ValueError):M.cover(invoice(),other)

    def test_cli_binds_exact_bytes_and_runs_optimized(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'a.json',Path(d)/'b.json'
            a.write_bytes(json.dumps(invoice({'1':4})).encode());b.write_bytes(json.dumps(invoice({'2':1,'3':1})).encode())
            p=subprocess.run([sys.executable,'-I','-O','-B',str(ROOT/'scripts/compare_recursive_intervals.py'),str(a),str(b),'--max-boxes','1'],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr);result=json.loads(p.stdout)
            self.assertEqual(result['inputs']['old']['sha256'],hashlib.sha256(a.read_bytes()).hexdigest())
            self.assertEqual(result['cells'][0]['classification'],'single_crossing')


if __name__=='__main__':unittest.main()
