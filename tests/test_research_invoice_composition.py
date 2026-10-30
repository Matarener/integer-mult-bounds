"""Composition preserves paid/target accounting and exact transport receipts."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import combine_recursive_invoices as combine
from compare_recursive_invoices import parse_invoice, compare_invoices
sys.path.pop(0)


def invoice(paid=None, targets=None):
    return {'schema': 'integer-mult-recursive-invoice/v1',
            'contract': {'model': 'fixture', 'rank_semantics': 'rank', 'ambient_rank': 145, 'boundary': 'same'},
            'paid': {str(r): n for r, n in (paid or {}).items()},
            'targets': {str(r): n for r, n in (targets or {}).items()}}


def cost(value, tariff):
    return sum(n * tariff(int(r)) for r, n in value['paid'].items()) - sum(
        n * tariff(int(r)) for r, n in value['targets'].items())


class InvoiceCompositionTests(unittest.TestCase):
    def test_paid_and_target_sums_replay_under_independent_tariffs(self):
        terms = [(3, invoice({1: 2, 8: 1}, {9: 1})), (7, invoice({2: 5}, {4: 2}))]
        before = copy.deepcopy(terms); result = combine.combine_invoices(terms)
        self.assertEqual(result['paid'], {'1': 6, '2': 35, '8': 3})
        self.assertEqual(result['targets'], {'4': 14, '9': 3})
        for tariff in (lambda r: r, lambda r: min(r, 3), lambda r: r*r):
            self.assertEqual(cost(result, tariff), sum(n * cost(value, tariff) for n, value in terms))
        self.assertEqual(terms, before)

    def test_duplicate_components_equal_one_combined_multiplicity(self):
        value = invoice({1: 1}, {8: 1})
        self.assertEqual(combine.combine_invoices([(2, value), (3, value)]), combine.combine_invoices([(5, value)]))

    def test_limits_and_contract_mismatch_reject(self):
        for terms in ([], [(1, invoice())] * 129, [(True, invoice())], [(0, invoice())],
                      [(-1, invoice())], [(10**60+1, invoice())], [(2, invoice({1: 10**60}))]):
            with self.subTest(terms=terms[:1]), self.assertRaises(ValueError):combine.combine_invoices(terms)
        changed = invoice(); changed['contract']['boundary'] = 'another caller'
        with self.assertRaisesRegex(ValueError, 'contracts differ'):
            combine.combine_invoices([(1, invoice()), (1, changed)])

    def run_cli(self, values, counts):
        with tempfile.TemporaryDirectory() as tmp:
            args = []; raw_inputs = []
            for i, (value, count) in enumerate(zip(values, counts)):
                path = Path(tmp) / f'input-{i}.json'; raw = json.dumps(value).encode(); path.write_bytes(raw)
                raw_inputs.append(raw); args.extend(['--term', str(count), str(path)])
            run = subprocess.run([sys.executable, '-I', '-O', '-B', str(ROOT / 'scripts/combine_recursive_invoices.py'), *args],
                                  capture_output=True)
            return run, raw_inputs

    def test_cli_output_is_comparator_input_and_receipt_matches_exact_bytes(self):
        values = [invoice({1: 1}, {8: 1}), invoice({2: 2}, {4: 1})]
        run, raw_inputs = self.run_cli(values, [2, 3])
        self.assertEqual(run.returncode, 0, run.stderr)
        result = parse_invoice(run.stdout); receipt = json.loads(run.stderr)
        self.assertEqual(receipt['output_sha256'], sha256(run.stdout).hexdigest())
        self.assertEqual(receipt['output_bytes'], len(run.stdout))
        self.assertEqual([r['input']['sha256'] for r in receipt['terms']], [sha256(r).hexdigest() for r in raw_inputs])
        self.assertEqual(compare_invoices(result, combine.combine_invoices(list(zip([2, 3], values))))['classification'], 'equal')

    def test_late_failure_emits_no_partial_invoice(self):
        changed = invoice(); changed['contract']['model'] = 'other'
        run, _ = self.run_cli([invoice({1: 1}), changed], [1, 1])
        self.assertEqual(run.returncode, 2); self.assertEqual(run.stdout, b'')
        self.assertEqual(json.loads(run.stderr)['status'], 'INVALID_INVOICE_COMBINATION')


if __name__ == '__main__':
    unittest.main()
