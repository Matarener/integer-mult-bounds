#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavior controls and code-disjoint small exact arithmetic oracles."""
import json
import runpy
import unittest
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / 'verify.py'))
CERT = json.loads((HERE / 'CERTIFICATE.json').read_text())
RESULT = json.loads((HERE / 'RESULT.json').read_text())


class Controls(unittest.TestCase):
    def test_integer_power_oracle(self):
        for rank, exponent in product(range(74), (Q(1, 2), Q(2, 3), Q(6, 7))):
            lo, hi = V['power_interval'](rank, exponent)
            exact = rank ** exponent.numerator
            self.assertLessEqual(lo ** exponent.denominator, exact)
            self.assertGreaterEqual(hi ** exponent.denominator, exact)
        for rank in range(74):
            self.assertEqual(V['power_interval'](rank, Q(1)), (Q(rank), Q(rank)))
        with self.assertRaisesRegex(ValueError, 'power domain'):
            V['power_interval'](74, Q(1, 2))

    def test_separate_enumeration(self):
        # A bounded width-by-width frontier, independent of Cartesian product.
        frontier = {(0, ())}
        for width in V['WIDTHS']:
            frontier = {(mass + n * width, counts + (n,))
                        for mass, counts in frontier for n in range(49)
                        if mass + n * width <= 48}
        expected = {(c, ns) for c in V['CAPS'] for mass, ns in frontier if mass <= c}
        actual = {(c, ns) for c, ns, *_ in V['patterns'](CERT)}
        self.assertEqual(expected, actual)
        self.assertEqual(len(actual), 1163)

    def test_inventory_controls(self):
        for mode in ('missing', 'fractional', 'overfull', 'changed_width'):
            cert = deepcopy(CERT)
            if mode == 'missing':
                cert['integer_patterns'].pop()
            elif mode == 'fractional':
                cert['integer_patterns'][0]['multiplicity'] = '10752'
            elif mode == 'overfull':
                cert['integer_patterns'][0]['counts'][0] = 3
            else:
                cert['integer_patterns'][-1]['counts'][2] = 0
            with self.assertRaises(ValueError, msg=mode):
                V['check_witness'](cert, V['INVENTORY'])
        self.assertEqual(V['check_witness'](CERT, V['INVENTORY']), V['IDLE'])

    def test_potential_forgeries(self):
        rows = V['patterns'](CERT)
        cert = deepcopy(CERT)
        cert['residue_paths'][1] = []
        with self.assertRaisesRegex(ValueError, 'destination'):
            V['potentials'](cert, rows)
        cert = deepcopy(CERT)
        # Two edges form a positive-cost cycle of total B=37.
        first = next(j for j, r in enumerate(rows) if r[0] == 8 and r[1] == (0, 0, 0, 0, 0))
        second = next(j for j, r in enumerate(rows) if r[0] == 48 and r[1] == (0, 0, 0, 1, 0))
        cert['residue_paths'][1] += [first, second]
        values = V['potentials'](cert, rows)
        powers = {r: V['power_interval'](r, 1 - Q(RESULT['root_bracket'][0])) for r in range(74)}
        with self.assertRaisesRegex(ValueError, 'potential inequality'):
            V['check_potentials'](rows, values, powers)

    def test_dual_source_and_paid_controls(self):
        cert = deepcopy(CERT)
        cert['fractional_dual_constant'][4] += 1
        with self.assertRaisesRegex(ValueError, 'rank-mass'):
            V['patterns'](cert)
        data = V['pinned_inputs']()
        bad = deepcopy(data)
        bad['research/complex-t16-rare-pattern-exchanges/data/PLAN.json']['per_call_widths'][0]['widths'][0] += 1
        with self.assertRaisesRegex(ValueError, 'width inventory'):
            V['source_inventory'](bad)
        idle = dict(V['IDLE'])
        idle[1] -= 1
        with self.assertRaisesRegex(ValueError, 'paid rank mass'):
            V['complete_terms'](idle)

    def test_false_root_sign(self):
        lo, hi = map(Q, RESULT['root_bracket'])
        with self.assertRaisesRegex(ValueError, 'lower root sign'):
            V['verify'](CERT, [str(hi), str(hi + hi - lo)])


if __name__ == '__main__':
    unittest.main()
