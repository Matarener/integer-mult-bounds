"""Exact controls for target budgeting and research-only moment enclosures."""
from copy import deepcopy
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import prepare_kappa_sixteenth as prep


class SixteenthPreparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = prep.prepare()

    def test_paid_wrapper_boundary_is_strict(self):
        threshold = Q(self.report['target']['coarse_bit_saving_strictly_above'])
        self.assertEqual(threshold / (1 + threshold - prep.OLD), Q(1, 15))
        budget = self.report['illustrative_supplier_budget']
        a, effective, atom = map(Q, (budget['admitted_bit'], budget['effective_bit'], budget['atom']))
        self.assertLess(Q(1, 15), a)
        self.assertLess(a, effective)
        self.assertLess(effective, atom)
        self.assertLess(atom, 1 - effective)

    def test_production_domain_remains_rejected(self):
        diagnostic = self.report['assembly_diagnostic']
        self.assertEqual(diagnostic['failed_slacks'], {'b_below_one_over32': '-7/160'})
        self.assertTrue(diagnostic['strict_arithmetic_rejects_with_assumed_bridge'])
        self.assertEqual(diagnostic['other_slacks_strictly_positive'], 46)
        self.assertLess(Q(diagnostic['gaussian_r']), Q(1, 4))
        self.assertGreater(Q(diagnostic['balance_margin']), prep.TARGET)
        self.assertEqual(self.report['published_control']['strict_constraint_count'], 47)

    def test_retained_histograms_fail_target(self):
        for side in ('bit', 'complex'):
            row = self.report['retained_profile_screens'][side]
            self.assertGreater(Q(row['moment_lower']), 1)
            self.assertLessEqual(Q(row['moment_lower']), Q(row['moment_upper']))
            self.assertTrue(row['excluded_by_raw_moment'])

    def test_enclosures_across_range_reductions(self):
        for ratio, saving in ((Q(66), Q(3, 40)), (Q(72), Q(2, 25)),
                              (Q(1000), Q(9, 10)), (Q(1), Q(0))):
            L, U = prep.enclosure_tools()['log_interval'](ratio)
            E, F = prep.extended_exp(saving * L, saving * U)
            self.assertLessEqual(E**saving.denominator, ratio**saving.numerator)
            self.assertGreaterEqual(F**saving.denominator, ratio**saving.numerator)
        with self.assertRaises(ValueError):
            prep.extended_exp(0.0, Q(1))
        with self.assertRaises(ValueError):
            prep.extended_exp(Q(-1), Q(1))

    def test_synthetic_pass_and_corrupted_ledger(self):
        # Arithmetic-only toy, deliberately not represented as a real circuit.
        toy = dict(m=4, W_per_vertex=1, child_histogram={'1': 1},
                   rank_per_vertex=1, deficit_per_vertex=3, maxchild=1)
        self.assertLess(Q(prep.moment_screen(toy, Q(1, 2))['moment_upper']), 1)
        bad = deepcopy(toy)
        bad['rank_per_vertex'] = 2
        with self.assertRaisesRegex(ValueError, 'Rank ledger mismatch'):
            prep.moment_screen(bad, Q(1, 2))

    def test_compression_exclusion_and_receipt(self):
        row = self.report['fixed_complex_ledger_screen']
        self.assertEqual(Q(row['minimum_mass_fraction']), Q(131, 132))
        self.assertEqual(Q(row['powered_moment_lower']), Q(131, 132)**15 * Q(33, 10))
        self.assertGreater(Q(row['powered_moment_lower']), 1)
        saved = json.loads((ROOT / 'docs/research/kappa-sixteenth-preparation.json').read_text())
        self.assertEqual(saved, self.report)


if __name__ == '__main__':
    unittest.main()
