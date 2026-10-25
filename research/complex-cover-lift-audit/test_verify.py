#!/usr/bin/env python3
"""Rejecting controls for verify.py."""
import random
import unittest
from fractions import Fraction as Q

import verify as v


class Controls(unittest.TestCase):
    def test_non_orthogonal_breaks_defect_identity(self):
        rng = random.Random(1)
        fails = 0
        for _ in range(40):
            g = [rng.randrange(1, 32) for _ in range(5)]
            if v.is_orthogonal(g, 5):
                continue
            # only invertible g give a permutation P_g
            if len({v.mat_vec(g, x) for x in range(32)}) < 32:
                continue
            fails += not v.defect_holds(g, 5)
        self.assertGreater(fails, 0)
        for g in v.orthogonal_matrices(5):
            if v.delta_of(list(g)):
                break
        rows = list(g)
        ginv = v.transpose(rows, 5)
        self.assertFalse(all(v.popcount(v.mat_vec(ginv, z)) % 4 == v.popcount(z) % 4
                             for z in range(32)), "delta = 0 must fail when delta != 0")

    def test_padded_range_exceeds_q_bits(self):
        M = (322560 * v.sp_order(36)) ** v.depth(73)
        q = (M - 1).bit_length()
        R = -(-2 ** q // M) * M
        self.assertGreater(R, 2 ** q)

    def test_signs_read_as_phases_break_lift(self):
        w = v.load_word("THREE-base")
        rng = random.Random(2)
        rep = {k: v.random_mono(4, rng).tensor_power(2) for k in range(1, len(w["warps"]) + 1)}
        e = v.run_word(w, rep, False, rng, 16, scalar_hook=lambda q: abs(q))
        self.assertGreater(e, 1.0)

    def test_non_representation_breaks_lift(self):
        w = v.load_word("FOUR-base")
        rng = random.Random(3)
        gens = range(1, len(w["warps"]) + 1)
        rep = {k: v.random_mono(4, rng).tensor_power(2) for k in gens}
        bad = {k: v.random_mono(4, rng).tensor_power(2) for k in gens}
        e = v.run_word(w, rep, False, rng, 16, inv=bad)
        self.assertGreater(e, 1e-3)

    def test_lift_passes_at_f1(self):
        w = v.load_word("FOUR-extra")
        rng = random.Random(4)
        rep = {k: v.random_mono(4, rng) for k in range(1, len(w["warps"]) + 1)}
        self.assertLess(v.run_word(w, rep, True, rng, 4), 1e-9)


if __name__ == "__main__":
    unittest.main()
