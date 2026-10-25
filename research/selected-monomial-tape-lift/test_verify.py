#!/usr/bin/env python3
"""Rejecting controls for the record grammar and its lift."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lift as L  # noqa: E402


def port0():
    return L.wrappers()[0][1]


class Controls(unittest.TestCase):
    def test_grammar_realizes_every_wrapper_at_f1(self):
        m = port0()
        ok, info = L.check_monomial(m, 1, L.all_addresses(L.N9, 1))
        self.assertTrue(ok)
        self.assertLessEqual(info["total"], 171)

    def test_unlifted_global_phase_fails_at_f2(self):
        """SPECIALIZATION s3: keeping a single constant phase a instead of a*f violates the lift."""
        m = port0()
        recs = m.records()
        self.assertGreater(m.a, 0)
        keep = [r for r in recs if r[0] != "I"] + [("I",)] * m.a
        bad = []
        for X in L.random_addresses(L.N9, 2, 20, 3):
            got_X, got_ph, _ = L.execute([r for r in keep if r[0] != "I"], X, 2, 0)
            got_ph = (got_ph + m.a) % 4            # constant phase a, not a*f
            want = m.lift(X, 2)
            bad.append((got_X, got_ph) != want)
        self.assertTrue(all(bad))

    def test_dropped_row_addition_breaks_the_lift(self):
        m = port0()
        recs = m.records()
        idx = next(i for i, r in enumerate(recs) if r[0] == "XROW")
        mutated = recs[:idx] + recs[idx + 1:]
        fails = 0
        for X in L.all_addresses(L.N9, 1):
            got_X, got_ph, _ = L.execute(mutated, X, 1, 0)
            fails += (got_X, got_ph) != m.lift(X, 1)
        self.assertGreater(fails, 0)

    def test_single_column_cz_is_not_the_lift(self):
        """A phase record that only reads column 0 fails at f=2 whenever a CZ or S is present."""
        m = port0()
        recs = m.records()
        self.assertTrue(any(r[0] in ("S", "CZ") for r in recs))

        def execute_col0(recs, X, f):
            X = list(X)
            ph = 0
            for r in recs:
                if r[0] == "XROW":
                    for j in range(f):
                        X[j] ^= ((X[j] >> r[2]) & 1) << r[1]
                elif r[0] == "NOT":
                    for j in range(f):
                        X[j] ^= 1 << r[1]
                elif r[0] == "S":
                    ph = (ph + ((X[0] >> r[1]) & 1)) % 4
                elif r[0] == "CZ":
                    ph = (ph + 2 * (((X[0] >> r[1]) & 1) & ((X[0] >> r[2]) & 1))) % 4
                else:
                    ph = (ph + f) % 4
            return X, ph
        fails = sum(execute_col0(recs, X, 2) != tuple(m.lift(X, 2)) for X in L.random_addresses(L.N9, 2, 40, 9))
        self.assertGreater(fails, 0)

    def test_spectators_untouched(self):
        m = port0()
        recs = m.records()
        for X in L.random_addresses(L.N9, 3, 10, 2):
            _, _, spec = L.execute(recs, X, 3, 0b101)
            self.assertEqual(spec, 0b101)

    def test_swap_word_with_one_swap_removed_is_rejected(self):
        w = L.plan_words()[0]
        ok, conv, _ = L.check_word(w["pre"], w["perm"], w["inv"], 2, 6, 1)
        self.assertTrue(ok)
        ok2, _, _ = L.check_word(w["pre"][1:], w["perm"], w["inv"], 2, 6, 1)
        self.assertFalse(ok2)

    def test_transposition_chain_realizes_permutation(self):
        import random
        rng = random.Random(4)
        perm = list(range(12))
        rng.shuffle(perm)
        ok, info = L.check_permutation(tuple(perm), 2, 20, 3)
        self.assertTrue(ok)
        self.assertEqual(info["XROW"] % 3, 0)

    def test_asymmetric_Q_rejected(self):
        with self.assertRaises(AssertionError):
            L.Monomial(3, [1, 2, 4], 0, [2, 0, 0], [0, 0, 0], 0)

    def test_body_word_read_off_rejects_wrong_words(self):
        ce = L.load_clifford()
        word = [["P", [2, 1, 4, 8, 16, 32, 64, 128, 256]], ["D", [0] * 9, [2, 0, 0, 0, 0, 0, 0, 0, 0]], ["X", 3], ["phase", 1]]
        m = L.from_engine(ce, L.literal_op(ce, word))
        ok, _ = L.check_monomial(m, 2, L.random_addresses(L.N9, 2, 48, 3))
        self.assertTrue(ok)
        with self.assertRaises(ValueError):           # a Gaussian is not a monomial: no record list is claimed
            L.from_engine(ce, ce.cgate(L.N9, 1, 1))
        with self.assertRaises(ValueError):           # unknown primitive
            L.literal_op(ce, [["H", 0]])

    def test_tampered_result_rejected(self):
        here = Path(__file__).resolve().parent
        res = json.loads((here / "RESULT.json").read_text(encoding="utf-8"))
        self.assertEqual(res["status"], "PASS")
        res["wrappers"]["count"] = 895
        self.assertNotEqual(res["wrappers"]["count"], 896)


if __name__ == "__main__":
    unittest.main()
