"""Domain-region arithmetic and optimistic mechanism rejection controls."""
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import audit_sixteenth_round as audit


class SixteenthRound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.audit()

    def test_interval_negative_products_and_zero_divisor(self):
        I=audit.Interval
        self.assertEqual((I(-3,2)*I(-4,5)).record(),dict(lower='-15',upper='12'))
        self.assertEqual((I(2,3)/I(-2,-1)).record(),dict(lower='-3',upper='-1'))
        with self.assertRaises(ValueError):I(1)/I(-1,1)
        with self.assertRaises(ValueError):I(0.1)

    def test_whole_box_scope(self):
        row=self.report['domain_region']
        omitted={'literal_scalar_guard','row_product_gap','b_below_one_over32'}
        bounded=[v for k,v in row['slacks'].items() if k not in omitted]
        self.assertEqual(len(bounded),44)
        self.assertTrue(all(Q(v['lower'])>0 for v in bounded))
        self.assertLess(Q(row['slacks']['b_below_one_over32']['upper']),0)
        self.assertEqual(row['slacks']['gamma_sublinear'],
                         dict(lower='1/2000000',upper='1/2000000'))

    def test_excess_saving_fails_despite_domain_diagnostic(self):
        slacks=audit.reduced_slacks(Q(1,100),Q(3,40))
        self.assertLess(slacks['g3_above_kappa'],0)
        self.assertLess(audit.reduced_slacks(Q(2,5),Q(41,100))['alpha_below_one_fourth'],0)

    def test_gross_ledger_exclusion_and_minimum_defect(self):
        for side,r in [('complex',6),('bit',7)]:
            row=self.report['mechanisms'][side]
            m,t,s=row['dimension'],row['current_maxchild'],Q(row['saving'])
            self.assertGreater(Q(row['gross_ledger_powered_floor']),1)
            self.assertEqual(row['optimistic_minimum_defect_per_data_role'],r)
            self.assertGreaterEqual(audit.powered_floor(m,t,1-Q(r-1,m),s),1)
            self.assertLess(audit.powered_floor(m,t,1-Q(r,m),s),1)

    def test_packing_opportunity_has_strict_scope_and_depth_cost(self):
        for side,cap,depth in [('complex',65,46),('bit',71,50)]:
            row=self.report['mechanisms'][side]
            self.assertEqual(row['necessary_maxchild_at_current_mass'],cap)
            self.assertTrue(row['three_piece_packing_excluded'])
            relaxed=row['unrestricted_packing']
            self.assertIn('RELAXATION ONLY',relaxed['status'])
            self.assertLess(Q(relaxed['moment']['moment_upper']),1)
            self.assertEqual(relaxed['halving_depth'],depth)
            self.assertEqual(sum(int(t)*n for t,n in relaxed['histogram'].items()),relaxed['rank_mass'])

    def test_source_bound_receipt(self):
        saved=json.loads((ROOT/'docs/research/kappa-sixteenth-domain-round.json').read_text())
        self.assertEqual(saved,self.report)
        self.assertEqual(self.report['published_control']['strict_constraint_count'],47)


if __name__=='__main__':unittest.main()
