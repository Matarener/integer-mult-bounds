"""Finite independent schedule oracles and certificate rejection controls."""
import copy
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import plan_reversible_pebbles as tool


def instance(parents, space, widths=None):
    return {'schema': 'reversible-pebble-problem/v1', 'space': space,
            'targets': [len(parents)-1], 'nodes': [
                {'parents': p, 'width': (widths or [1]*len(parents))[i], 'compute': i+1, 'erase': 1}
                for i, p in enumerate(parents)]}


def oracle(v):
    n = len(v['nodes']); states = [frozenset(i for i in range(n) if m >> i & 1) for m in range(1 << n)]
    d = {frozenset(): 0}
    for _ in states:
        changed = False
        for s in states:
            if s not in d: continue
            for i, row in enumerate(v['nodes']):
                t = s ^ {i}
                if not set(row['parents']) <= s or sum(v['nodes'][j]['width'] for j in t) > v['space']: continue
                c = d[s] + row['erase' if i in s else 'compute']
                if t not in d or c < d[t]: d[t] = c; changed = True
        if not changed: break
    return d.get(frozenset(v['targets']))


class PebbleTests(unittest.TestCase):
    def test_all_four_node_dags_and_budgets(self):
        edges = [(i, j) for j in range(4) for i in range(j)]
        for bits in itertools.product(range(2), repeat=6):
            parents = [[i for bit, (i, dst) in zip(bits, edges) if bit and dst == j] for j in range(4)]
            for budget in range(1, 5):
                v = instance(parents, budget); r = tool.plan(v)
                self.assertEqual(r['cost'], oracle(v)); self.assertTrue(tool.verify(v, r))

    def test_recomputation_cleanup_and_weighted_cost(self):
        v = instance([[], [0], [1], [2]], 4, [1, 2, 1, 1])
        r = tool.plan(v); self.assertEqual(r['cost'], oracle(v))
        self.assertGreater(len(r['schedule']), 7)
        self.assertEqual(r['status'], 'optimal')
        v['space'] = 3; self.assertEqual(tool.plan(v)['status'], 'infeasible')

    def test_certificate_mutations(self):
        v = instance([[], [0], [0, 1]], 3); good = tool.plan(v)
        for mutation in ('potential', 'closure', 'schedule', 'cost', 'infeasible'):
            bad = copy.deepcopy(good)
            if mutation == 'potential': bad['potential']['0'] = 1
            if mutation == 'closure': del bad['potential']['1']
            if mutation == 'schedule': bad['schedule'][0] = 2
            if mutation == 'cost': bad['cost'] += 1
            if mutation == 'infeasible': bad.update(status='infeasible', cost=None, schedule=[])
            with self.assertRaises(ValueError): tool.verify(v, bad)

    def test_full_state_bound(self):
        v = instance([[] for _ in range(16)], 16)
        r = tool.plan(v); self.assertEqual(len(r['potential']), 65536); self.assertEqual(r['cost'], 16)
        v['nodes'].append(v['nodes'][0])
        with self.assertRaises(ValueError): tool.plan(v)

    def test_zero_space_and_no_targets(self):
        v = instance([[]], 0); self.assertEqual(tool.plan(v)['status'], 'infeasible')
        v['targets'] = []; self.assertEqual(tool.plan(v)['cost'], 0)
        v['nodes'][0]['parents'] = [0]
        with self.assertRaises(ValueError): tool.plan(v)
        v = instance([[]], True)
        with self.assertRaises(ValueError): tool.plan(v)

    def test_portable_cli_and_source_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            p, c = Path(tmp)/'problem.json', Path(tmp)/'certificate.json'
            p.write_text(json.dumps(instance([[], [0], [1]], 3)))
            cmd = [sys.executable, '-O', '-B', str(ROOT/'scripts/plan_reversible_pebbles.py'), str(p)]
            out = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr); c.write_text(out.stdout)
            check = subprocess.run(cmd + ['--check', str(c)], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            saved = c.read_text(); c.write_text('[]')
            self.assertEqual(subprocess.run(cmd+['--check',str(c)], capture_output=True).returncode, 2)
            c.write_text(saved)
            p.write_text(p.read_text()+'\n')
            self.assertEqual(subprocess.run(cmd+['--check',str(c)], capture_output=True).returncode, 2)


if __name__ == '__main__': unittest.main()
