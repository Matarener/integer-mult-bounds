"""Behavioral controls for the two-role map and its complete finite census."""

import base64
import gzip
import io
import json
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import support_checks
import swap
import verify


class SwapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.package = verify.ROOT, verify.PACKAGE
        export = verify.check_sources(cls.root, cls.package)
        cls.old = verify.predecessor(cls.root, cls.package, export)
        cls.auditor, cls.geo, cls.widths, cls.local = verify.geometry(cls.root)
        cls.plan = verify.read_json(cls.package / "data/PLAN.json")
        cls.new = swap.exchange(cls.old, 1863, 1514)
        cls.idle = swap.idle_profile(cls.new, cls.geo, cls.plan, cls.auditor)

    def audit(self, rows, idle=None):
        return self.auditor.audit(
            self.geo,
            self.widths,
            self.local,
            rows,
            self.plan,
            self.idle if idle is None else idle,
            16,
        )

    def test_literal_change_and_complete_map(self):
        self.assertEqual(
            self.new, verify.read_json(self.package / "data/OWNERS.json.gz")
        )
        changed = [i for i, (a, b) in enumerate(zip(self.old, self.new)) if a != b]
        moved = [
            i for i in changed if swap.bin_key(self.old[i]) != swap.bin_key(self.new[i])
        ]
        self.assertEqual(moved, [1514, 1863])
        self.assertEqual(len(changed), 6)
        for a, b in zip(self.old, self.new):
            self.assertEqual(
                {k: a[k] for k in swap.ROLE_KEYS}, {k: b[k] for k in swap.ROLE_KEYS}
            )
        self.assertEqual(self.audit(self.new)["rank_mass"], 1_041_408)

    def test_source_is_not_mutated(self):
        before = verify.canonical(self.old)
        swap.exchange(self.old, 1863, 1514)
        self.assertEqual(verify.canonical(self.old), before)
        self.assertEqual(self.old[1514]["width"], 4)
        self.assertEqual(self.old[1863]["width"], 5)

    def test_one_sided_move_is_rejected(self):
        for index in (1514, 1863):
            mutant = list(self.old)
            mutant[index] = self.new[index]
            with self.assertRaises(self.auditor.Reject):
                self.audit(mutant)

    def test_wrong_role_or_uncompacted_slice_is_rejected(self):
        for key, value in (("width", 4), ("offset", 100), ("family", 99_999)):
            mutant = list(self.new)
            mutant[1863] = dict(mutant[1863], **{key: value})
            with self.assertRaises(self.auditor.Reject):
                self.audit(mutant)

    def test_stale_idle_or_profile_cannot_certify_gain(self):
        stale = swap.idle_profile(self.old, self.geo, self.plan, self.auditor)
        with self.assertRaises(self.auditor.Reject):
            self.audit(self.new, stale)
        difference = Counter(self.idle)
        difference.subtract(stale)
        self.assertEqual(dict(+difference), {3: 1})
        self.assertEqual(sum(k * v for k, v in difference.items()), 0)
        self.assertEqual(sum(difference.values()), -1)

    def test_complete_census_and_exhaustion(self):
        result = swap.census(self.old, self.geo, self.plan, self.auditor)
        self.assertEqual(len(result["winners"]), 8)
        self.assertEqual(result["winners"][-1], [1863, 1514])
        self.assertEqual(
            result["counts"],
            {
                "family": 72,
                "legal": 8,
                "moment_improving_pairs": 19372,
                "type_pairs": 3,
                "window": 19292,
            },
        )
        with (
            patch.object(swap, "MAX_PAIR_CHECKS", 0),
            self.assertRaisesRegex(ValueError, "budget"),
        ):
            swap.census(self.old, self.geo, self.plan, self.auditor)

    def test_input_boundaries(self):
        for rows in ([], self.old[:-1]):
            with self.assertRaises(ValueError):
                swap.validate_rows(rows)
        for value in (True, -1, 100_000, "5"):
            rows = list(self.old)
            rows[0] = dict(rows[0], width=value)
            with self.assertRaises(ValueError):
                swap.validate_rows(rows)
        for first, second in ((0, 0), (-1, 0), (0, swap.ROWS)):
            with self.assertRaises(ValueError):
                swap.exchange(self.old, first, second)

    def test_parser_budget_and_invalid_compression(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json.gz"
            path.write_bytes(gzip.compress(json.dumps(self.old[:1]).encode(), mtime=0))
            with patch.object(verify, "MAX_FILE", 1), self.assertRaises(ValueError):
                verify.read_json(path)
            with patch.object(verify, "MAX_JSON", 1), self.assertRaises(ValueError):
                verify.read_json(path)
            path.write_bytes(b"not gzip")
            with self.assertRaises(gzip.BadGzipFile):
                verify.read_json(path)

    def test_wrong_predecessor_delta_is_rejected(self):
        export = verify.read_json(self.package / "SOURCE-EXPORT.json")
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "predecessor").mkdir()
            delta = verify.read_json(
                self.package / "predecessor/DIFF-vs-predecessor.json"
            )
            mutant = deepcopy(delta)
            mutant[0]["before"]["offset"] += 1
            (package / "predecessor/DIFF-vs-predecessor.json").write_text(
                json.dumps(mutant)
            )
            with self.assertRaisesRegex(ValueError, "preimage"):
                verify.predecessor(self.root, package, export)

    def test_report_diagnostics_preserve_faulty_bytes_and_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            actual, frozen = (
                Path(directory) / "actual.json",
                Path(directory) / "frozen.json",
            )
            frozen.write_text(
                json.dumps({"kappa": "1/1000", "assembly_sha256": "f" * 64})
            )
            support_checks.compare_reports(frozen, frozen, "changed report")
            for field, value in (("kappa", "1/999"), ("assembly_sha256", "0" * 64)):
                mutant = json.loads(frozen.read_text())
                mutant[field] = value
                actual.write_text(json.dumps(mutant))
                stdout = io.StringIO()
                with (
                    redirect_stdout(stdout),
                    self.assertRaisesRegex(ValueError, "changed report"),
                ):
                    support_checks.compare_reports(actual, frozen, "changed report")
                lines = stdout.getvalue().splitlines()
                encoded = lines[0].split(" ", 1)[1]
                self.assertEqual(
                    gzip.decompress(base64.b64decode(encoded)), actual.read_bytes()
                )
                self.assertIn(field, lines[1])
            full = (self.package / "support/exact-score/RESULT.json").read_bytes()
            frozen.write_bytes(full)
            mutant = json.loads(full)
            mutant["assembly_sha256"] = "0" * 64
            actual.write_text(json.dumps(mutant, indent=2))
            stdout = io.StringIO()
            with (
                redirect_stdout(stdout),
                self.assertRaisesRegex(ValueError, "changed report"),
            ):
                support_checks.compare_reports(actual, frozen, "changed report")
            encoded = stdout.getvalue().splitlines()[0].split(" ", 1)[1]
            self.assertGreater(len(encoded), 32768)
            self.assertEqual(
                gzip.decompress(base64.b64decode(encoded)), actual.read_bytes()
            )

    def test_raw_artifact_diagnostics_are_complete(self):
        names = (
            "ASSEMBLY.json",
            "global/audit/PREFIX-AND-INVOICE.json",
            "global/audit/OWNERS-AND-PROFILE.json",
            "global/audit/ASYNC-AUDIT.json",
        )
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            for name in names:
                target = work / "strict" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(
                    (self.package / "support/construction/raw" / name).read_bytes()
                )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                support_checks.preserve_raw_artifacts(work)
            lines = stdout.getvalue().splitlines()
            self.assertEqual(len(lines), len(names))
            for line, name in zip(lines, names):
                marker, recorded_name, digest, encoded = line.split(" ", 3)
                self.assertEqual(marker, "INDEPENDENT_RAW_ARTIFACT_GZIP_BASE64")
                self.assertEqual(recorded_name, name)
                raw = (work / "strict" / name).read_bytes()
                self.assertEqual(gzip.decompress(base64.b64decode(encoded)), raw)
                self.assertEqual(digest, verify.replay.sha(work / "strict" / name))

    def test_independent_owner_controls(self):
        controls = self.auditor.controls(
            self.geo, self.widths, self.local, self.new, self.plan, self.idle, 16
        )
        self.assertEqual(len(controls), 11)
        self.assertEqual(len({item["name"] for item in controls}), 11)


if __name__ == "__main__":
    unittest.main()
