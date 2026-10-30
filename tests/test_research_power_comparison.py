"""Exact rational-power inequalities and signed invoice controls."""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import evaluate_recursive_power as power
sys.path.pop(0)


def invoice(paid=None, targets=None):
    return {'schema': 'integer-mult-recursive-invoice/v1',
            'contract': {'model': 'fixture', 'rank_semantics': 'rank', 'ambient_rank': 10**9, 'boundary': 'same'},
            'paid': {str(r): n for r, n in (paid or {}).items()},
            'targets': {str(r): n for r, n in (targets or {}).items()}}


class PowerComparisonTests(unittest.TestCase):
    def test_bounds_by_independent_integer_power_comparison(self):
        for rank in (1, 2, 3, 8, 17, 10**9):
            for denominator in range(2, 10):
                for numerator in range(1, denominator):
                    exponent = Q(numerator, denominator)
                    lo, hi = power.power_bounds(rank, exponent, 32)
                    target = Q(rank) ** numerator
                    self.assertLessEqual(lo ** denominator, target)
                    self.assertGreaterEqual(hi ** denominator, target)

    def test_exact_binary_power_cases(self):
        for rank, exponent, expected in ((9, Q(1, 2), 3), (81, Q(3, 4), 27), (1, Q(1, 3), 1)):
            self.assertEqual(power.power_bounds(rank, exponent), (Q(expected), Q(expected)))

    def test_large_denominator_and_precision_control(self):
        exponent = power.parse_exponent('0.99689955')
        lo, hi = power.power_bounds(145, exponent)
        with localcontext() as ctx:
            ctx.prec = 100
            reference = Decimal(145) ** (Decimal(exponent.numerator) / Decimal(exponent.denominator))
            self.assertLessEqual(Decimal(lo.numerator) / Decimal(lo.denominator), reference)
            self.assertGreaterEqual(Decimal(hi.numerator) / Decimal(hi.denominator), reference)
        self.assertLess(hi - lo, Q(1, 10**30))
        coarse = power.power_bounds(145, exponent, 16)
        self.assertLess(hi - lo, coarse[1] - coarse[0])

    def test_inconclusive_concave_order_can_have_a_strict_power_sign(self):
        old, new = invoice({2: 2}), invoice({1: 1, 4: 1})
        self.assertEqual(power.compare_invoices(old, new)['classification'], 'inconclusive')
        self.assertEqual(power.evaluate(old, new, Q(1, 2))['classification'], 'new_cost_higher')
        self.assertEqual(power.evaluate(new, old, Q(1, 2))['classification'], 'new_cost_lower')

    def test_targets_cancel_before_interval_work_and_near_zero_stays_unresolved(self):
        same = invoice({2: 10**60}, {2: 10**60})
        result = power.evaluate(invoice(), same, Q(1, 3))
        self.assertEqual(result['classification'], 'equal'); self.assertEqual(result['terms'], [])
        self.assertEqual(power.evaluate(invoice({1: 2}), invoice({8: 1}), Q(1, 3), 16)['classification'], 'unresolved')
        owned = power.evaluate(invoice({1: 1, 8: 1}, {9: 1}), invoice(), Q(99, 100))
        self.assertEqual(owned['classification'], 'new_cost_lower')

    def test_invalid_parameters_and_contract_fail(self):
        for text in ('0', '1', '-1/2', '1/0', 'NaN', '1e-999999999', '2' * 129):
            with self.assertRaises((ValueError, ZeroDivisionError)):
                power.parse_exponent(text)
        for bits in (0, 15, 257, True):
            with self.assertRaises(ValueError):power.evaluate(invoice(), invoice(), Q(1, 2), bits)
        changed = invoice(); changed['contract']['model'] = 'different'
        with self.assertRaisesRegex(ValueError, 'contracts differ'):
            power.evaluate(invoice(), changed, Q(1, 2))

    def test_support_limit_applies_after_exact_cancellation(self):
        many = invoice({r: 10**60 for r in range(1, 514)})
        self.assertEqual(power.evaluate(many, many, Q(99, 100))['classification'], 'equal')
        with self.assertRaisesRegex(ValueError, 'at most 512'):
            power.evaluate(invoice(), many, Q(99, 100))
        del many['paid']['513']
        result = power.evaluate(invoice(), many, Q(99, 100), 256)
        self.assertEqual(len(result['terms']), 512)
        self.assertEqual(result['classification'], 'new_cost_higher')

    def test_isolated_optimized_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / name for name in ('old.json', 'new.json')]
            for path, value in zip(paths, (invoice({2: 2}), invoice({1: 1, 4: 1}))):path.write_text(json.dumps(value))
            run = subprocess.run([sys.executable, '-I', '-O', '-B', str(ROOT / 'scripts/evaluate_recursive_power.py'),
                                  *map(str, paths), '--exponent', '1/2'], capture_output=True, text=True, check=True)
            result = json.loads(run.stdout)
            self.assertEqual(result['classification'], 'new_cost_higher')
            self.assertIn('sha256', result['inputs']['old'])


if __name__ == '__main__':
    unittest.main()
