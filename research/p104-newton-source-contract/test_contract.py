"""Behavioral rejection controls for the P104 Newton source contract."""

import sys
import unittest
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.archive = v.sources(v.ROOT)
        cls.uses, _ = v.bind(cls.word, cls.archive)
        cls.certificate = v.source_certificate(cls.word)

    def test_encoder_and_signed_negative_pair(self):
        coefficients = tuple((((x * 5) % 7) - 3, ((x * 3) % 11) - 5)
                             for x in range(v.SIZE))
        encoded = v.encode(coefficients)
        self.assertEqual(v.member(encoded), coefficients)
        for bit in range(v.BITS):
            self.assertEqual(v.butterfly(v.butterfly(encoded, bit), bit, -1), encoded)

    def test_component_integrality_does_not_admit_the_newton_domain(self):
        nonmember = ((1, 0),) + v.ZERO[1:]
        with self.assertRaisesRegex(ValueError, 'Newton membership'):
            v.member(nonmember)

    def test_lost_collector_compensation_is_rejected(self):
        changed = deepcopy(self.word)
        changed['program'][2038][3] = '1'
        with self.assertRaisesRegex(ValueError, 'exact private erasure'):
            v.source_certificate(changed)

    def test_changed_half_requires_a_different_product_domain(self):
        changed = deepcopy(self.word)
        index = self.certificate['first_witnesses']['N100']['event']
        self.assertEqual(changed['program'][index][3], '1/2')
        changed['program'][index][3] = '1/4'
        with self.assertRaises(ValueError):
            v.source_certificate(changed)

    def test_singular_wrapper_and_wrong_occurrence_are_rejected(self):
        wrapper = deepcopy(self.archive['transports'][0]['recipe']['left'])
        wrapper['matrix_rows'][1] = wrapper['matrix_rows'][0]
        with self.assertRaisesRegex(ValueError, 'invertible affine wrapper'):
            v.plan(wrapper)
        changed = deepcopy(self.archive)
        changed['transports'][0]['events'].append(0)
        with self.assertRaisesRegex(ValueError, 'native occurrence binding'):
            v.bind(self.word, changed)

    def test_phase_preserves_domain_but_breaks_private_cleanup(self):
        states = dict.fromkeys(('D31', 'D30', 'D29', 'D28', 'D27', 'Q7'), v.ZERO)
        states['D31'] = ((1, 0),) * v.SIZE
        good = dict(states)
        for index in range(2025, 2040):
            v.physical_step(self.word['program'][index], index, good, self.uses)
        self.assertNotIn('C', good)
        changed = dict(self.uses)
        rank, left, right = changed[2031]
        changed[2031] = rank, tuple((y, (phase + 2) % 4) for y, phase in left), right
        with self.assertRaisesRegex(ValueError, 'physical exact erasure'):
            for index in range(2025, 2040):
                v.physical_step(self.word['program'][index], index, states, changed)
                if self.word['program'][index][0] != 'erase':
                    v.member(states[self.word['program'][index][1]])

    def test_every_restricted_source_has_a_reverse_lower_witness(self):
        for source, witness in self.certificate['first_witnesses'].items():
            v.reverse_witness(self.word, source, witness)
            self.assertEqual(v.pi_valuation(Fraction(witness['coefficient'])),
                             -self.certificate['pi_exponents'][source])


if __name__ == '__main__':
    unittest.main()
