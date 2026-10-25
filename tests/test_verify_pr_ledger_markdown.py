#!/usr/bin/env python3
"""Tests for scripts/verify_pr_ledger_markdown.py.

Positive control: a consistent Markdown ledger passes.  Failure controls mutate
the fixture in each way the verifier is meant to catch, so a silently passing
checker is itself a failure.
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load():
    path = ROOT / "scripts/verify_pr_ledger_markdown.py"
    spec = importlib.util.spec_from_file_location("verify_pr_ledger_markdown", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = _load()

LEDGER = {
    "schema_version": 1,
    "counts": {"incorporated": 1, "partially_reviewed": 1},
    "pull_requests": [
        {
            "number": 1,
            "url": "https://github.com/CrocSwap/integer-mult-bounds/pull/1",
            "contributor": {"login": "alice"},
            "disposition": "incorporated",
            "evidence": [{"evidence": "research/a-audit/DISPOSITIONS.json"},
                         {"evidence": "research/b-audit/DISPOSITIONS.json"}],
        },
        {
            "number": 7,
            "url": "https://github.com/CrocSwap/integer-mult-bounds/pull/7",
            "contributor": {"login": "bob"},
            "disposition": "partially_reviewed",
            "evidence": [{"evidence": "research/a-audit/DISPOSITIONS.json"},
                         {"evidence": "research/a-audit/DISPOSITIONS.json"}],
            "reconciliation_evidence": ["research/c-audit/DISPOSITIONS.json"],
        },
    ],
}

ROWS = [
    "| [#1](https://github.com/CrocSwap/integer-mult-bounds/pull/1) | alice | incorporated | "
    "[record 1](../../research/a-audit/DISPOSITIONS.json) · [record 2](../../research/b-audit/DISPOSITIONS.json) |",
    "| [#7](https://github.com/CrocSwap/integer-mult-bounds/pull/7) | bob | partially reviewed | "
    "[record 1](../../research/a-audit/DISPOSITIONS.json) · [record 2](../../research/c-audit/DISPOSITIONS.json) |",
]

MARKDOWN = "\n".join([
    "# PR review and integration ledger",
    "",
    "| Disposition | Count |",
    "|---|---:|",
    "| incorporated | 1 |",
    "| partially reviewed | 1 |",
    "",
    "| PR | Contributor | Disposition | Evidence or remaining question |",
    "|---|---|---|---|",
    *ROWS,
]) + "\n"


class VerifyLedgerMarkdown(unittest.TestCase):
    def check(self, markdown=MARKDOWN, ledger=LEDGER):
        return verify.check(markdown, ledger)

    def assertDifference(self, report, needle):
        self.assertFalse(report["ok"])
        self.assertTrue(any(needle in d for d in report["differences"]),
                        f"expected a difference mentioning {needle!r}, got {report['differences']}")

    # Positive control.
    def test_consistent_ledger_passes(self):
        report = self.check()
        self.assertTrue(report["ok"], report["differences"])
        self.assertEqual(report["row_mismatches"], 0)
        self.assertEqual(report["markdown_rows"], 2)

    def test_deduplicates_evidence_and_appends_reconciliation(self):
        # #7 lists a-audit twice in `evidence`; the projection keeps one copy
        # and appends the reconciliation evidence in order.
        self.assertIn("[record 1](../../research/a-audit/DISPOSITIONS.json) · "
                      "[record 2](../../research/c-audit/DISPOSITIONS.json)", ROWS[1])

    def test_no_evidence_uses_declared_placeholder(self):
        ledger = json.loads(json.dumps(LEDGER))
        ledger["pull_requests"][0]["evidence"] = []
        ledger["counts"] = {"partially_reviewed": 1, "incorporated": 1}
        markdown = MARKDOWN.replace(ROWS[0], "| [#1](https://github.com/CrocSwap/integer-mult-bounds/pull/1) "
                                             "| alice | incorporated | " + verify.NO_REVIEW_DETAIL + " |")
        report = self.check(markdown, ledger)
        self.assertTrue(report["ok"], report["differences"])

    # Failure controls.
    def test_detects_dropped_evidence_record(self):
        """The failure actually observed on main: a stale row loses a record."""
        report = self.check(MARKDOWN.replace(" · [record 2](../../research/b-audit/DISPOSITIONS.json)", ""))
        self.assertDifference(report, "#1 row differs")

    def test_detects_disposition_drift(self):
        report = self.check(MARKDOWN.replace("| alice | incorporated |", "| alice | partially reviewed |"))
        self.assertDifference(report, "#1 row differs")

    def test_detects_attribution_drift(self):
        report = self.check(MARKDOWN.replace("| bob | partially reviewed |", "| mallory | partially reviewed |"))
        self.assertDifference(report, "#7 row differs")

    def test_detects_missing_row(self):
        report = self.check(MARKDOWN.replace(ROWS[1] + "\n", ""))
        self.assertDifference(report, "missing rows: [7]")

    def test_detects_count_drift(self):
        report = self.check(MARKDOWN.replace("| incorporated | 1 |", "| incorporated | 2 |"))
        self.assertDifference(report, "count 'incorporated'")

    def test_detects_duplicate_row(self):
        report = self.check(MARKDOWN + ROWS[0] + "\n")
        self.assertDifference(report, "duplicate row for #1")

    def test_detects_absent_counts_table(self):
        report = self.check("\n".join(line for line in MARKDOWN.split("\n")
                                      if line != "| Disposition | Count |"))
        self.assertDifference(report, "counts table header")

    def test_detects_missing_count_row(self):
        report = self.check(MARKDOWN.replace("| incorporated | 1 |\n", ""))
        self.assertDifference(report, "count 'incorporated'")

    def test_detects_json_counts_field_drift(self):
        ledger = json.loads(json.dumps(LEDGER))
        ledger["counts"] = {"incorporated": 2, "partially_reviewed": 1}
        self.assertDifference(self.check(ledger=ledger), "disagrees with its own pull_requests")


class VerifyLedgerMarkdownOnRepository(unittest.TestCase):
    """The committed ledgers are the real fixture; report status without asserting it."""

    def test_report_shape(self):
        ledger = json.loads((ROOT / "docs/research/pr-ledger.json").read_text(encoding="utf-8"))
        report = verify.check((ROOT / "docs/research/pr-ledger.md").read_text(encoding="utf-8"), ledger)
        self.assertEqual(report["markdown_rows"], report["json_prs"])
        self.assertEqual(report["missing_rows"], [])
        self.assertEqual(report["unexpected_rows"], [])
        self.assertEqual(report["counts"], report["markdown_counts"])


if __name__ == "__main__":
    unittest.main()