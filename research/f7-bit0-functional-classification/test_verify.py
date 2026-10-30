"""Behavioural tests for the fixed-L/2 functional classification.

Nick Petalas, with substantial automated assistance.  Apache-2.0.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify as V  # noqa: E402


class ModelTest(unittest.TestCase):
    def test_01021323_is_restored_and_universal(self):
        word = (0, 1, 0, 2, 1, 3, 2, 3)
        states = V.prefix_states(word)
        self.assertTrue(V.restored(word))
        self.assertEqual(len(set(states[:-1])), 8)
        self.assertEqual(len(states), 9)
        self.assertTrue(V.is_universal(states, 4))

    def test_prefix_states_close_to_zero(self):
        for word in [(0, 1, 0, 1), (0, 0), (0, 1, 2, 0, 1, 2)]:
            self.assertEqual(V.prefix_states(word)[-1], 0)

    def test_non_restored_word_is_rejected(self):
        self.assertFalse(V.restored((0, 1, 2)))
        self.assertFalse(V.restored((0, 1)))

    def test_all_labels_even_but_a_label_used_once_fails(self):
        self.assertTrue(V.restored((0, 0, 1, 1)))
        self.assertFalse(V.restored((0, 0, 1, 2)))

    def test_split_stats_ignores_the_closing_repeat(self):
        word = (0, 1, 0, 2, 1, 3, 2, 3)
        raw = V.prefix_states(word)
        self.assertEqual(V.split_stats(raw, 0b0001), V.split_stats(raw[:-1], 0b0001))
        self.assertEqual(V.split_stats(raw[:-1], 0b0001), (6, 2, 8))

    def test_fixture_matches_the_published_numbers(self):
        f = V.fixture_01021323()
        self.assertEqual(f["weight_split"], [4, 4])
        self.assertEqual(f["weight_excess"], 0)
        self.assertEqual(f["bit0_split"], [6, 2])
        self.assertEqual(f["bit0_excess"], 8)
        self.assertEqual(f["substituted_budget"], 5)
        self.assertEqual(f["correct_bit0_budget"], 9)

    def test_budget_terms(self):
        self.assertEqual(V.budget_terms(4, 8), 5)
        self.assertEqual(V.budget_terms(7, 18), 9)
        self.assertEqual(V.budget_terms(7, 20), 27)
        self.assertEqual(V.budget_terms(7, 14), -21)


class AlternationTest(unittest.TestCase):
    def test_lemma_holds_on_every_word_at_4_8(self):
        self.assertGreater(V.alternation_holds(4, 8), 0)

    def test_all_ones_functional_alternates_every_step(self):
        word = (0, 1, 0, 2, 1, 3, 2, 3)
        states = V.prefix_states(word)
        vals = [V.parity(p & 0b1111) for p in states]
        self.assertEqual(vals, [i % 2 for i in range(len(states))])

    def test_non_all_ones_functional_need_not_alternate(self):
        word = (0, 1, 0, 2, 1, 3, 2, 3)
        states = V.prefix_states(word)
        vals = [V.parity(p & 0b0001) for p in states]
        self.assertNotEqual(vals, [i % 2 for i in range(len(states))])


class CensusTest(unittest.TestCase):
    def test_small_domain_is_non_trivial(self):
        r = V.survey(3, 6)
        self.assertEqual(r["simple_closed_words"], 4)
        self.assertEqual(r["universal_words"], 4)
        self.assertEqual(r["false_prunes"], 0)

    def test_all_15_functionals_are_tested_at_n4(self):
        r = V.survey(4, 8)
        self.assertEqual(len(r["firing_masks"]) + len(r["sound_masks"]), 15)

    def test_bit0_counterexample_is_present(self):
        r = V.survey(4, 8)
        self.assertIn(1, r["firing_masks"])
        self.assertEqual(r["records"][1]["count"], 6)

    def test_cross_check_enumerator_agrees(self):
        for n, L in V.CROSS_CHECK:
            fast = V.survey(n, L)
            words, universal = V.brute_survey(n, L)
            self.assertEqual(words, fast["simple_closed_words"], f"{n},{L}")
            self.assertEqual(universal, fast["universal_words"], f"{n},{L}")

    def test_canonical_filter(self):
        self.assertTrue(V.canonical((0, 1, 0, 2)))
        self.assertFalse(V.canonical((1, 0, 0)))
        self.assertFalse(V.canonical((0, 2, 0)))

    def test_bounds_are_enforced(self):
        for bad in [(0, 8), (9, 8), (4, 1), (4, 17)]:
            with self.assertRaises(ValueError):
                list(V.enumerate_words(*bad))


class ReceiptTest(unittest.TestCase):
    def test_receipt_is_reproducible(self):
        r = V.run()
        self.assertGreater(r["alternation_checks"], 0)
        for d in r["domains"]:
            self.assertEqual(
                d["false_prunes"], sum(v["count"] for v in d["records"].values())
            )

    def test_stored_receipt_is_valid_json(self):
        stored = json.loads((V.PACKAGE / "RESULT.json").read_bytes())
        self.assertEqual(stored["schema"], 1)
        self.assertTrue(stored["domains"])


if __name__ == "__main__":
    unittest.main()