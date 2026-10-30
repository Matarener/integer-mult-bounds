"""Exhaustive matching oracles and independent certificate checks."""
import copy
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import assign_compatible_resources as tool


def problem(costs): return {'schema': 'compatible-assignment/v1', 'costs': costs}


def oracle(costs):
    values = [sum(costs[i][j] for i, j in enumerate(p))
              for p in itertools.permutations(range(len(costs[0])), len(costs))
              if all(costs[i][j] is not None for i, j in enumerate(p))]
    return min(values) if values else None


class AssignmentTests(unittest.TestCase):
    def test_all_three_by_three_compatibility_graphs(self):
        for bits in itertools.product(range(2), repeat=9):
            costs = [[((i-j)**2+2*j+i) if bits[3*i+j] else None for j in range(3)] for i in range(3)]
            r = tool.assign(problem(costs)); expected = oracle(costs)
            self.assertEqual(r.get('cost'), expected)
            self.assertEqual(r['status'], 'infeasible' if expected is None else 'optimal')
            self.assertTrue(tool.verify(problem(costs), r))

    def test_rectangular_random_costs(self):
        rng = random.Random(418)
        for _ in range(80):
            costs = [[None if rng.randrange(5) == 0 else rng.randrange(30) for _ in range(5)] for _ in range(4)]
            r = tool.assign(problem(costs)); self.assertEqual(r.get('cost'), oracle(costs))

    def test_hall_failure_without_empty_rows(self):
        value = problem([[1, None, None], [2, None, None], [None, 1, 2]])
        r = tool.assign(value); self.assertEqual(r['rows'], [0, 1]); self.assertEqual(r['neighbors'], [0])
        bad = copy.deepcopy(r); bad['rows'] = [0]
        with self.assertRaises(ValueError): tool.verify(value, bad)
        self.assertEqual(tool.assign(problem([[], []]))['status'], 'infeasible')

    def test_dual_and_assignment_mutations(self):
        value = problem([[10, 1, None], [1, None, 8]])
        good = tool.assign(value); self.assertEqual(good['cost'], 2)
        for mutation in ('row', 'column', 'duplicate', 'forbidden', 'cost'):
            bad = copy.deepcopy(good)
            if mutation == 'row': bad['row_dual'][0] += 1
            if mutation == 'column': bad['column_dual'][0] = 1
            if mutation == 'duplicate': bad['assignment'][1] = bad['assignment'][0]
            if mutation == 'forbidden': bad['assignment'][0] = 2
            if mutation == 'cost': bad['cost'] = True
            with self.assertRaises(ValueError): tool.verify(value, bad)

    def test_limits_and_large_integer_costs(self):
        costs = [[0 if i == j else 10**12 for j in range(256)] for i in range(128)]
        r = tool.assign(problem(costs)); self.assertEqual(r['cost'], 0); self.assertEqual(r['assignment'], list(range(128)))
        for costs in ([[True]], [[-1]], [[1], []], [[0]]*129, [[0]*257]):
            with self.assertRaises(ValueError): tool.assign(problem(costs))

    def test_portable_cli_and_tampered_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            p, c = Path(tmp)/'problem.json', Path(tmp)/'certificate.json'
            p.write_text(json.dumps(problem([[4, 1], [2, None]])))
            cmd = [sys.executable, '-O', '-B', str(ROOT/'scripts/assign_compatible_resources.py'), str(p)]
            out = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr); c.write_text(out.stdout)
            self.assertEqual(subprocess.run(cmd+['--check',str(c)], capture_output=True).returncode, 0)
            saved = c.read_text(); c.write_text('[]')
            self.assertEqual(subprocess.run(cmd+['--check',str(c)], capture_output=True).returncode, 2)
            c.write_text(saved)
            p.write_text(p.read_text()+'\n')
            self.assertEqual(subprocess.run(cmd+['--check',str(c)], capture_output=True).returncode, 2)


if __name__ == '__main__': unittest.main()
