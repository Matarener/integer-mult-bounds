# SPDX-License-Identifier: Apache-2.0
"""Behavioural tests for the f7 functional-independent-check primitives.

These assert what a reader of the receipt can observe: the walk, the three
predicates, the budget arithmetic, the false-prune decision on the published
fixture word, the canonical form, the domain guards and the internal
consistency of one full domain classification.  Roughly one second in total.
"""

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify  # noqa: E402


class WalkTests(unittest.TestCase):
    def test_fixture_prefix_states(self):
        word = verify.PUBLISHED_FIXTURE["word"]
        self.assertEqual(verify.prefix_states(word),
                         verify.PUBLISHED_FIXTURE["prefix_states"])

    def test_walk_starts_at_zero(self):
        self.assertEqual(verify.prefix_states((0, 1))[0], 0)

    def test_labelled_steps_xor_basis_vectors(self):
        self.assertEqual(verify.prefix_states((0, 2, 0)), (0, 1, 5, 4))

    def test_restoration_is_even_label_counts(self):
        self.assertTrue(verify.is_restored(verify.PUBLISHED_FIXTURE["word"]))
        self.assertFalse(verify.is_restored((0, 0, 1)))
        self.assertTrue(verify.is_restored(()))


class PredicateTests(unittest.TestCase):
    def test_fixture_is_simple_universal_restored(self):
        word = verify.PUBLISHED_FIXTURE["word"]
        self.assertTrue(verify.is_simple(word))
        self.assertTrue(verify.is_universal(word, 4))
        self.assertEqual(verify.sumset_size(word, 4), 16)

    def test_repeated_state_is_not_simple(self):
        self.assertFalse(verify.is_simple((0, 0, 0, 0)))

    def test_non_universal_word_is_rejected(self):
        word = verify.PUBLISHED_FIXTURE["word"]
        self.assertFalse(verify.is_universal(word, 5))


class BudgetTests(unittest.TestCase):
    def test_published_budgets(self):
        for (n, length), row in verify.PUBLISHED_TABLE.items():
            self.assertEqual(verify.base_budget(n, length), row[2],
                             f"base budget {(n, length)}")

    def test_odd_length_rejected(self):
        with self.assertRaises(ValueError):
            verify.base_budget(4, 9)

    def test_fixture_budget_arithmetic(self):
        s, t = verify.PUBLISHED_FIXTURE["bit0_split"]
        base = verify.base_budget(4, 8)
        self.assertEqual(base, 5)
        self.assertEqual(base + ((s - t) // 2) ** 2, 9)


class FalsePruneTests(unittest.TestCase):
    def test_fixture_word_fires_for_bit_zero(self):
        word = verify.PUBLISHED_FIXTURE["word"]
        states = verify.prefix_states(word)[:-1]
        fired, detail = verify.false_prune(4, 8, states, 0b0001)
        self.assertTrue(fired)
        self.assertEqual(detail, (8, 6, 2, 5, 2))

    def test_fixture_word_is_sound_for_all_ones(self):
        word = verify.PUBLISHED_FIXTURE["word"]
        states = verify.prefix_states(word)[:-1]
        fired, detail = verify.false_prune(4, 8, states, 0b1111)
        self.assertFalse(fired)
        self.assertEqual(detail[0], 0)

    def test_shifting_the_budget_changes_the_decision(self):
        word = verify.PUBLISHED_FIXTURE["word"]
        states = verify.prefix_states(word)[:-1]
        self.assertTrue(verify.false_prune(4, 8, states, 0b0001, extra=-3)[0] is False)

    def test_excess_routes_agree(self):
        word = verify.PUBLISHED_FIXTURE["word"]
        states = verify.prefix_states(word)[:-1]
        for mask in range(1, 16):
            self.assertEqual(verify.excess_by_counter(states, mask),
                             verify.excess_by_set(states, mask))


class CanonicalFormTests(unittest.TestCase):
    def test_canonical_form_relabels_by_first_occurrence(self):
        self.assertEqual(verify.canonical_form((3, 3, 7, 3, 7)), (0, 0, 1, 0, 1))

    def test_canonical_form_is_idempotent(self):
        word = (0, 1, 0, 2, 1, 3, 2, 3)
        self.assertEqual(verify.canonical_form(verify.canonical_form(word)), word)

    def test_canonical_words_start_with_zero(self):
        words, _ = verify.enumerate_canonical(4, 8)
        self.assertTrue(all(w[0] == 0 for w in words))


class EnumeratorTests(unittest.TestCase):
    def test_published_word_counts(self):
        for (n, length) in ((3, 6), (3, 8), (4, 8), (4, 10), (5, 10)):
            words, _ = verify.enumerate_canonical(n, length)
            self.assertEqual(len(words), verify.PUBLISHED_TABLE[(n, length)][0],
                             f"word count {(n, length)}")

    def test_unconstrained_route_agrees(self):
        canonical, _ = verify.enumerate_canonical(4, 8)
        unconstrained, _ = verify.enumerate_unconstrained(4, 8)
        self.assertEqual(set(canonical), unconstrained)

    def test_domain_guards(self):
        for bad in ((8, 8), (4, 15), (4, 9), (0, 8)):
            with self.assertRaises(ValueError):
                verify.enumerate_canonical(*bad)

    def test_every_word_is_simple_and_restored(self):
        words, _ = verify.enumerate_canonical(5, 10)
        self.assertTrue(all(verify.is_simple(w) for w in words))
        self.assertTrue(all(verify.is_restored(w) for w in words))


class DomainRecordTests(unittest.TestCase):
    def setUp(self):
        self.record = verify.classify_domain(4, 8)

    def test_record_matches_published_row(self):
        simple, universal, base, prunes = verify.PUBLISHED_TABLE[(4, 8)]
        self.assertEqual(self.record["simple_closed_words"], simple)
        self.assertEqual(self.record["universal_words"], universal)
        self.assertEqual(self.record["base_budget"], base)
        self.assertEqual(self.record["false_prunes"], prunes)

    def test_per_mask_counts_close_the_total(self):
        self.assertEqual(sum(self.record["per_mask_counts"].values()),
                         self.record["false_prunes"])
        self.assertEqual(self.record["bit0_false_prunes"],
                         self.record["per_mask_counts"]["1"])

    def test_sound_and_firing_masks_partition_the_functionals(self):
        self.assertEqual(len(self.record["firing_masks"]) + len(self.record["sound_masks"]),
                         self.record["masks_total"])


class ReceiptTests(unittest.TestCase):
    def test_committed_receipt_matches_a_fresh_run(self):
        fresh = verify.run(selected_new=[(4, 12)])
        committed = json.loads(verify.RESULT_PATH.read_text())
        self.assertEqual(committed["published_domains"], fresh["published_domains"])
        self.assertEqual(committed["fixture"], fresh["fixture"])
        self.assertEqual(committed["cross_check"], fresh["cross_check"])
        self.assertEqual(committed["new_domains"][1]["n"], 4)
        self.assertEqual(committed["new_domains"][1]["L"], 12)

    def test_new_domains_are_present_and_distinct(self):
        committed = json.loads(verify.RESULT_PATH.read_text())
        seen = {(row["n"], row["L"]) for row in committed["new_domains"]}
        self.assertEqual(seen, set(verify.NEW_DOMAINS))
        published = {(row["n"], row["L"]) for row in committed["published_domains"]}
        self.assertEqual(published & seen, set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
