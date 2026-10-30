"""Independent finite oracles for invoice search-pool reduction."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import prune_recursive_invoices as tool


def invoice(paid=None, targets=None):
    return {'schema': 'integer-mult-recursive-invoice/v1', 'contract': {
        'model': 'test', 'rank_semantics': 'rank', 'ambient_rank': 10**9, 'boundary': 'same'},
        'paid': paid or {}, 'targets': targets or {}}


class FrontierTests(unittest.TestCase):
    def test_exhaustive_small_pools(self):
        candidates = [invoice(dict(zip(('1', '2', '3'), counts)))
                      for counts in itertools.product(range(2), repeat=3)]
        for inds in itertools.combinations(range(8), 4):
            pool = [candidates[i] for i in inds]
            result = tool.frontier(pool)
            # Direct dense tariff table, independent of the sparse sweep.
            scores = [[sum(int(r) if int(r) < k else k for r, n in v['paid'].items() for _ in range(n))
                       for k in range(1, 4)] for v in pool]
            expected = [i for i in range(4) if not any(j != i and scores[j] != scores[i]
                        and all(a <= b for a, b in zip(scores[j], scores[i])) for j in range(4))]
            self.assertEqual(result['retained'], expected)
            self.assertTrue(tool.verify_frontier(pool, result))

    def test_targets_and_equal_net_with_different_gross_bill(self):
        pool = [invoice({'2': 1}), invoice({'2': 1, '3': 5}, {'3': 5}),
                invoice({'1': 2}), invoice({'1': 1}, {'4': 1})]
        r = tool.frontier(pool)
        self.assertEqual(r['retained'], [3])
        equal = tool.frontier(pool[:2])
        self.assertEqual(equal['discarded'][0]['relation'], 'equal')

    def test_incomparable_candidates_survive(self):
        pool = [invoice({'1': 2}), invoice({'3': 1})]
        self.assertEqual(tool.frontier(pool)['retained'], [0, 1])
        self.assertEqual(len(tool.frontier(pool)['discarded']), 0)

    def test_receipt_mutations_reject(self):
        pool = [invoice({'3': 3}), invoice({'3': 2}), invoice({'3': 1})]
        good = tool.frontier(pool)
        for edit in ('missing', 'fake_hinge', 'duplicate', 'wrong_witness', 'extra_retained'):
            bad = copy.deepcopy(good)
            if edit == 'missing': bad['discarded'].pop()
            if edit == 'fake_hinge': bad['discarded'][0]['hinges'][-1]['value'] = 0
            if edit == 'duplicate': bad['discarded'].append(bad['discarded'][0])
            if edit == 'wrong_witness': bad['discarded'][0]['retained'] = True
            if edit == 'extra_retained': bad['retained'].append(0); bad['discarded'].pop(0)
            with self.assertRaises(ValueError): tool.verify_frontier(pool, bad)

    def test_full_pool_and_sparse_huge_ranks(self):
        pool = [invoice({'1000000000': n + 1}) for n in range(256)]
        r = tool.frontier(pool)
        self.assertEqual(r['retained'], [0]); self.assertEqual(len(r['discarded']), 255)
        self.assertEqual(r['union_knots'], 1)
        with self.assertRaises(ValueError): tool.frontier(pool + [pool[0]])
        self.assertEqual(tool.frontier([invoice(), invoice()])['retained'], [0])

    def test_contract_and_input_rejection(self):
        a, b = invoice(), invoice(); b['contract']['boundary'] = 'different'
        with self.assertRaises(ValueError): tool.frontier([a, b])
        with self.assertRaises(ValueError): tool.frontier([])
        with self.assertRaises(ValueError): tool.frontier([invoice({'1': True})])

    def test_cli_hashes_and_optimized_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i, v in enumerate([invoice({'2': 2}), invoice({'2': 1})]):
                p = Path(tmp) / f'{i}.json'; p.write_text(json.dumps(v)); paths.append(str(p))
            p = subprocess.run([sys.executable, '-O', '-B', str(ROOT / 'scripts/prune_recursive_invoices.py'), *paths],
                               cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            r = json.loads(p.stdout); self.assertEqual(r['retained'], [1])
            for path, source in zip(paths, r['inputs']):
                self.assertEqual(source['sha256'], hashlib.sha256(Path(path).read_bytes()).hexdigest())
            Path(paths[0]).write_text('{"paid":{},"paid":{}}')
            p = subprocess.run([sys.executable, str(ROOT / 'scripts/prune_recursive_invoices.py'), *paths], capture_output=True)
            self.assertEqual(p.returncode, 2); self.assertEqual(p.stdout, b'')


if __name__ == '__main__': unittest.main()
