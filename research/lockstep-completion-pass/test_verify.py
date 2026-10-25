#!/usr/bin/env python3
"""Rejecting controls for the pass, the LIFO bank allocator and the counting formulas."""
import sys
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import counts as C  # noqa: E402
import executor as E  # noqa: E402


def selected_rule(adversarial="centre", seed=1):
    roles, rounds, owned, nm = E.selected_shaped(seed, adversarial=adversarial)
    return E.RawRule(nm, roles, rounds, owned)


class Controls(unittest.TestCase):
    def rejects(self, rule, n, **kw):
        with self.assertRaises(E.Violation):
            E.audit(rule, n, **kw)

    def test_overlapping_rule_is_not_a_lockstep_rule_before_the_pass(self):
        roles, rounds = E.overlapping_toy()
        raw = E.RawRule("overlapping toy", roles, rounds)
        self.assertFalse(raw.separated)
        with self.assertRaises(AssertionError):
            E.Rule("overlapping toy", roles, rounds)
        self.assertTrue(E.complete_and_split(raw, J=4, L=5))

    def test_cutoff_must_be_below_floor(self):
        with self.assertRaises(AssertionError):
            E.complete_and_split(selected_rule(), J=21, L=21)

    def test_dropping_a_split_remainder_loses_paid_mass(self):
        raw = selected_rule()
        good = E.complete_and_split(raw, J=20, L=21)
        bad = E.complete_and_split(raw, J=20, L=21, drop_remainder=True)
        self.assertEqual(sum(r for r, _ in good.rounds), sum(r for r, _ in raw.rounds) + sum(21 - k for _, k in raw.roles if k < 21))
        self.assertLess(sum(r for r, _ in bad.rounds), sum(r for r, _ in good.rounds))

    def test_short_completion_breaks_the_equal_mass_law(self):
        raw = selected_rule()
        bad = E.complete_and_split(raw, J=20, L=21, completion_rank_shift=-1)
        added_target = sum(21 - k for _, k in raw.roles if k < 21)
        added_paid = sum(r for r, _ in bad.rounds) - sum(r for r, _ in raw.rounds)
        self.assertNotEqual(added_target, added_paid)

    def test_completion_on_a_foreign_owner_is_rejected_by_ownership(self):
        # completing every small role on the owned centre instead of on the role's own array:
        # the centre then carries several completions while the roles keep rank L unpaid on
        # their own axes; the pass refuses to build such a rule (no owner but the role itself)
        raw = selected_rule()
        with self.assertRaises(AssertionError):
            E.complete_and_split(raw, J=20, L=21, completion_owner="not-a-field")

    def test_release_early_allocator_is_rejected(self):
        rule = E.complete_and_split(selected_rule("centre"), J=20, L=21)
        self.rejects(rule, 3045, owned_policy="release_early")

    def test_owned_bank_per_depth_is_rejected(self):
        rule = E.complete_and_split(selected_rule("centre"), J=20, L=21)
        self.rejects(rule, 3045, owned_policy="depth")
        self.rejects(E.toy(), 16, owned_policy="depth")

    def test_eager_parent_and_repeated_exit_field_are_rejected(self):
        rule = E.complete_and_split(selected_rule(), J=20, L=21)
        self.rejects(rule, 3045, eager=True)
        self.rejects(E.toy(), 28, bad_exit=True)

    def test_same_rules_pass_with_the_stack_allocator(self):
        E.audit(E.toy(), 16, owned_policy="stack")
        E.audit(E.complete_and_split(selected_rule("centre"), J=20, L=21), 3045, owned_policy="stack")

    def test_peak_formula_without_nested_term_is_too_small(self):
        rule = E.toy()
        cc = C.Counts(rule, executed=lambda m, cost: cost <= 3_000_000)
        tot, pk = cc.banks(28)
        F = cc.flow(28)
        B, a, P, cost = cc.compile(28)
        self.assertGreater(pk, a * F.peak_units)          # nested exit programs are live too
        self.assertEqual(E.audit(rule, 28, owned_policy="stack")["peak_banks"], pk)

    def test_peak_pairs_exit_with_its_own_path(self):
        # largest live path and largest nested exit peak sit on different paths here
        raw = E.RawRule("two ranks", (("a", 3), ("b", 5)), ((1, "C0"), (2, "C0")))
        rule = E.complete_and_split(raw, J=2, L=3)
        cc = C.Counts(rule)
        F = cc.flow(45)
        B, a, P, cost = cc.compile(45)
        run = E.audit(rule, 45, owned_policy="stack")
        self.assertTrue(run["full_width_executed"])
        self.assertEqual(F.G, 2)
        decoupled = a * F.peak_units * len(rule.owned) + max(cc.banks(e)[1] for e in F.exits)
        self.assertEqual(decoupled, 2050)                 # unconditioned sum overestimates
        self.assertEqual(cc.banks(45)[1], run["peak_banks"])
        self.assertEqual(run["peak_banks"], 2048)

    def test_identity_fails_for_a_wrong_tax(self):
        T, P = Counter({4: 3, 9: 2}), Counter({1: 5, 7: 2})
        left, right = C.gap_identity(T, P, 3, 5, Fraction(99, 100))
        self.assertLess(abs(left - right), Fraction(1, 10 ** 40))
        # omit the completion tax: the identity breaks
        wrong = right + sum(cnt * C.completion_tax(k, 5, 3, Fraction(99, 100)) for k, cnt in T.items() if k < 5)
        self.assertGreater(abs(left - wrong), Fraction(1, 10 ** 6))

    def test_tampered_result_rejected(self):
        import json
        import subprocess
        import tempfile
        import shutil
        here = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "pkg"
            shutil.copytree(here, dst)
            res = json.loads((dst / "RESULT.json").read_text(encoding="utf-8"))
            res["bindings"] += 1
            (dst / "RESULT.json").write_text(json.dumps(res), encoding="utf-8")
            # the verifier resolves ROOT from its own location; copy keeps the two-level layout
            root = Path(tmp) / "research" / "x"
            root.parent.mkdir()
            shutil.move(str(dst), str(root))
            for name in ("research/kappa-rebuild", "research/higher-moment-strictification", "research/net-tax-rank-compiler",
                         "research/lockstep-live-role-audit", "research/coupled-helper-neutral-completion"):
                src = here.parents[1] / name
                (Path(tmp) / name).parent.mkdir(parents=True, exist_ok=True)
                if not (Path(tmp) / name).exists():
                    try:
                        (Path(tmp) / name).symlink_to(src, target_is_directory=True)
                    except OSError:
                        self.skipTest("symlinks unavailable")
            p = subprocess.run([sys.executable, "-B", str(root / "verify.py")], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("RESULT.json differs", p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
