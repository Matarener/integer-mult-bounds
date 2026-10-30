#!/usr/bin/env python3
"""Rejecting controls for verify.py."""
import random
import unittest

import verify as v


class Controls(unittest.TestCase):
    def test_non_involution_breaks_square(self):
        rng = random.Random(5)
        p, m, n = 5, 25, 5
        broke = 0
        for _ in range(20):
            S, Si = v.unit(n, p, m, rng)
            P = v.mm(v.mm(S, [[int(i == j and i < 2) for j in range(n)] for i in range(n)], m), Si, m)
            C, _ = v.unit(n, p, m, rng)
            if v.mm(C, C, m) == v.eye(n):
                continue
            NP = v.N(P, C, m)
            broke += v.mm(NP, NP, m) != v.eye(2 * n)
        self.assertGreater(broke, 10)

    def test_overlapping_projectors_do_not_add(self):
        rng = random.Random(6)
        p, m, n = 7, 49, 5
        S, Si = v.unit(n, p, m, rng)
        proj = lambda idx: v.mm(v.mm(S, [[int(i == j and i in idx) for j in range(n)]
                                         for i in range(n)], m), Si, m)
        C = v.reversal(n)
        P, Q = proj([0, 1]), proj([1, 2])
        self.assertNotEqual(v.N(v.add(P, Q, m), C, m), v.mm(v.N(P, C, m), v.N(Q, C, m), m))

    def test_wrong_stock_factor_fails(self):
        Nq = v.gl_order(64, v.q)
        K = 269241600 * Nq
        U, r = divmod(K ** 2, v.W * Nq)
        self.assertEqual(r, 0)
        self.assertNotEqual(U, 9474 * K)

    def test_moment_with_extra_rank_one_child_fails(self):
        saved = dict(v.H)
        try:
            v.H[1] += 1
            self.assertGreater(v.mu(1 - float(v.c)), 1.0)  # #4330's sensitivity remark
        finally:
            v.H.clear()
            v.H.update(saved)

    def test_wrapper_fails_for_small_widths(self):
        e, w, k = v.wrapper_k(10)
        self.assertFalse(2 * k < e)

    def test_carry_omitted_breaks_route(self):
        p, m = 5, 125
        x, A = [7, 99], [[13, 88], [41, 3]]
        y = [sum(x[i] * A[i][j] for i in range(2)) % m for j in range(2)]
        xl, xh = [t % p for t in x], [t // p for t in x]
        Al, Ah = [[t % p for t in r] for r in A], [[t // p for t in r] for r in A]
        lo = [sum(xl[i] * Al[i][j] for i in range(2)) % p for j in range(2)]
        hi = [sum(xl[i] * Ah[i][j] + xh[i] * A[i][j] for i in range(2)) % 25 for j in range(2)]
        self.assertNotEqual(y, [a + p * b for a, b in zip(lo, hi)])


if __name__ == "__main__":
    unittest.main()
