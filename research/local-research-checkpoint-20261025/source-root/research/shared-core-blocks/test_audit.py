"""Exact controls and adverse cases for block-label shared cores."""
from fractions import Fraction as Q
from pathlib import Path
import json
import unittest
import audit as A


class Controls(unittest.TestCase):
    def test_data_retreat_is_charged(self):
        base = A.shared_profile(4, 2, 1, 1, 2, {2: 3}, {2: 1}, {2: 1})
        extra = A.shared_profile(4, 2, 1, 1, 2, {2: 3}, {1: 4}, {2: 1})
        self.assertEqual(extra['data_excess'], 2)
        self.assertEqual(extra['deficit'], base['deficit']-6)
        with self.assertRaises(ValueError):
            A.shared_profile(4, 2, 1, 1, 2, {2: 2}, {2: 1}, {2: 1})

    def test_gauge_mass_cancels_but_histogram_changes(self):
        a = A.shared_profile(4, 2, 1, 1, 2, {2: 3}, {2: 1}, {2: 1})
        b = A.shared_profile(4, 2, 1, 1, 2, {1: 1, 2: 2}, {2: 1}, {2: 1}, {1: 1})
        self.assertEqual(a['rank'], b['rank'])
        self.assertNotEqual(a['child_histogram'], b['child_histogram'])
        self.assertNotEqual(A.moment(a['child_histogram'], 12, 3, Q(2, 25)),
                            A.moment(b['child_histogram'], 12, 3, Q(2, 25)))

    def test_source_block_must_be_fixed_at_stage_exchange(self):
        model = A.geometry_control(2)
        U = frozenset((0, 1))
        self.assertEqual(A.image(model['r12'], U), U)
        wrong = A.swap_perm(12, (0, 1), (4, 5))
        self.assertNotEqual(A.image(wrong, U), U)

    def test_complete_small_words_and_phase_distinction(self):
        for scale in (1, 2):
            for order in (2, 4):
                c = A.local_control(scale, order)
                self.assertTrue(c['exact_arbitrary_inputs'] and c['literal_inverse'])
                self.assertEqual(c['profile']['deficit'], -scale)
                self.assertEqual(c['omitted_complex_pauli_rejected'], order == 4)
        phase = A.complex_phase_control()
        self.assertNotEqual(phase['square'], phase['fourth_power'])

    def test_omitted_dirty_cancellation_and_cleanup_fail(self):
        for order in (2, 4):
            word = A.local_control(2, order)['local_word']
            def run(omitted):
                values = [A.unit(i, 4) for i in range(3)]
                for j, (kind, t, c, coeff, delta, cost) in enumerate(word):
                    if j == omitted:continue
                    if kind == 'move':values[t] = A.move(values[t], delta, order)
                    else:values[t] = A.plus(values[t], A.move(values[c], delta, order), coeff, order)
                return values
            self.assertTrue(any(role == 2 for role, exp in run(0)[1]))
            self.assertTrue(any(role == 0 for role, exp in run(6)[2]))

    def test_direct_sum_does_not_improve_moment(self):
        p = A.local_control(1, 2)['profile']
        q = A.local_control(2, 2)['profile']
        for s in (Q(2, 25), Q(3, 40)):
            a = A.moment(p['child_histogram'], p['m'], p['W'], s)
            b = A.moment(q['child_histogram'], q['m'], q['W'], s)
            self.assertEqual(a, b)
            # Illegally adding role capacity would make the same word look better.
            bad = A.moment(q['child_histogram'], q['m'], 2*q['W'], s)
            self.assertLess(bad[1], b[0])

    def test_modern_budget_differs_from_old_budget(self):
        s = Q(2, 25)
        old = A.H.block_budget(19, 9, s, Q(1))
        new = A.ideal_budget(19, 9, s, Q(1), Q(1, 250))
        self.assertGreater(old['moment_interval'][0], 1)
        self.assertLess(new['moment_interval'][1], 1)
        self.assertGreater(A.ideal_budget(19, 9, s, Q(1), Q(1, 100))['moment_interval'][0], 1)

    def test_full_triple_cap_and_saved_receipt(self):
        control = A.fano_screen()
        self.assertEqual(len(control['lines']), 7)
        self.assertTrue(all(lo > 1 for lo, hi in control['endpoint_moments']))
        self.assertEqual(A.encode(A.audit()), json.loads(
            (Path(__file__).parent/'certificate.json').read_text()))


if __name__ == '__main__':
    unittest.main()
