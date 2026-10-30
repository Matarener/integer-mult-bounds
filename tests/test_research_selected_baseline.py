"""Productive-helper orientation, exact budgets and source-binding failures.

The numeric fixture is transcribed from zxv's selected #4359 CLAIM.json at
2a13eb1827784206202db90e5dc8327cf8a250db. It is metadata, not a new proof.
Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import research_selected_baseline as baseline


def certificate():
    return {
        "schema": "proposed-conditional-integer-multiplication-claim/1",
        "kappa": "23/10000",
        "uniform_templates": [
            {"family": "complex", "rank_encoding": "2^276540184361", "saving": "0.002304"},
            {"family": "BIT before cover", "rank_encoding": "2^6552928412", "saving": "0.002760"},
        ],
        "ordinary_BIT_saving": "0.0027418653797",
        "admitted_BIT_saving": "0.0027",
        "nine_outer_savings": {
            "boundary_algebraic_matrix": "115148849/50000000000",
            "fused_gaussian": "115596547/50000000000",
            "global_coordinate_router": "921/400000",
            "group_bit_router": "92497237/40000000000",
            "group_scans": "49999/50000",
            "main_transform": "115098849/50000000000",
            "microbox_face_corrections": "1925001/25000",
            "polynomial_products": "99999/100000",
            "sparse_union_movement": "20427648849/50000000000",
        },
        "limiting_outer_saving": "115098849/50000000000",
        "strict_limiting_slack": "98849/50000000000",
    }


def record():
    return {"kappa": "23/10000", "review": "review.md", "certificate": "CLAIM.json",
            "reproduce": "make frontier4359-verify", "scope": "Conditional fixture"}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def selected_fixture(root, claim=None):
    """A complete tiny selected closure for the real source-binding checker."""
    claim = certificate() if claim is None else claim
    source = root / "research/fixture"
    source.mkdir(parents=True)
    write_json(source / "CLAIM.json", claim)
    (source / "native-input.txt").write_text("immutable fixture source\n", encoding="utf-8")
    (root / "review.md").write_text("Fixture proof \u2014 conditional.\n", encoding="utf-8")
    write_json(root / "validation.json", {"scope": "fixture only"})
    write_json(root / "certificates/source.json", {
        "format": "repository-packages-sha256-v1",
        "package_roots": ["research/fixture"],
        "files": {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest()
                  for p in source.iterdir()},
    })
    selected = dict(record(), decimal="0.0023", certificate="research/fixture/CLAIM.json",
                    certificate_sha256=sha256((source / "CLAIM.json").read_bytes()).hexdigest(),
                    source_manifest="certificates/source.json", proof="review.md",
                    proof_supplements={"review.md": sha256((root / "review.md").read_bytes()).hexdigest()},
                    validation="validation.json")
    write_json(root / "certificates/selected-result.json", selected)
    (root / "scripts").mkdir()
    for name in ("research_selected_baseline.py", "verify_selected_result.py"):
        shutil.copyfile(ROOT / "scripts" / name, root / "scripts" / name)
    return selected


class ProductiveSummaryTests(unittest.TestCase):
    def test_current_budgets_are_separate_and_exact(self):
        result = baseline.summarize(record(), certificate())
        self.assertEqual(result["selected_kappa"], "23/10000")
        self.assertEqual(result["uniform_templates"]["complex"]["saving"], "36/15625")
        self.assertEqual(result["uniform_templates"]["BIT before cover"]["saving"], "69/25000")
        self.assertEqual(result["ordinary_BIT_saving"], "27418653797/10000000000000")
        self.assertEqual(result["admitted_BIT_saving"], "27/10000")
        self.assertEqual(result["binding_outer_rows"], ["main_transform"])
        self.assertEqual(result["limiting_outer_saving"], "115098849/50000000000")
        self.assertEqual(result["strict_limiting_slack"], "98849/50000000000")
        self.assertEqual(result["uniform_templates"]["complex"]["rank_encoding"], "2^276540184361")
        self.assertEqual(result["nine_outer_savings"]["microbox_face_corrections"], "1925001/25000")
        self.assertNotIn("ideal_balanced_cap", result)
        self.assertNotIn("binding_primitive", result)

    def test_all_tied_outer_rows_are_reported(self):
        claim = certificate()
        claim["nine_outer_savings"]["group_bit_router"] = claim["limiting_outer_saving"]
        result = baseline.summarize(record(), claim)
        self.assertEqual(result["binding_outer_rows"], ["group_bit_router", "main_transform"])

    def test_unknown_schema_does_not_fall_back_to_legacy_fields(self):
        claim = dict(certificate(), schema="future/2", bit_lower="1/100", complex_lower="1/100")
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            baseline.summarize(record(), claim)

    def test_missing_duplicate_unknown_and_unlabelled_templates_reject(self):
        original = certificate()
        variants = [[], original["uniform_templates"][:1],
                    [original["uniform_templates"][0]] * 2,
                    [dict(original["uniform_templates"][0], family="unpriced"),
                     original["uniform_templates"][1]],
                    [dict(original["uniform_templates"][0], rank_encoding=""),
                     original["uniform_templates"][1]]]
        for templates in variants:
            with self.subTest(templates=templates), self.assertRaises(ValueError):
                baseline.summarize(record(), dict(original, uniform_templates=templates))

    def test_nonexact_nonpositive_and_out_of_range_budgets_reject(self):
        for value in (None, True, 0.0027, "nan", "1/0", "0", "-1/100", "1", "2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                baseline.summarize(record(), dict(certificate(), admitted_BIT_saving=value))

    def test_bit_stage_inversions_reject(self):
        for change in ({"ordinary_BIT_saving": "1/100"}, {"admitted_BIT_saving": "0.00275"}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "out of order"):
                baseline.summarize(record(), dict(certificate(), **change))

    def test_missing_extra_and_negative_outer_rows_reject(self):
        rows = certificate()["nine_outer_savings"]
        missing = dict(rows)
        del missing["main_transform"]
        for mutant in (missing, dict(rows, extra="1/2"), dict(rows, main_transform="-1/2")):
            with self.subTest(rows=mutant), self.assertRaises(ValueError):
                baseline.summarize(record(), dict(certificate(), nine_outer_savings=mutant))

    def test_changed_row_declared_minimum_and_slack_reject(self):
        claim = certificate()
        changed_row = deepcopy(claim)
        changed_row["nine_outer_savings"]["group_bit_router"] = "1/1000"
        for mutant in (changed_row, dict(claim, limiting_outer_saving="1/10"),
                       dict(claim, strict_limiting_slack="1/1000")):
            with self.subTest(claim=mutant), self.assertRaises(ValueError):
                baseline.summarize(record(), mutant)

    def test_kappa_mismatch_and_nonstrict_endpoints_reject(self):
        claim = certificate()
        with self.assertRaisesRegex(ValueError, "kappa differs"):
            baseline.summarize(dict(record(), kappa="1/1000"), claim)
        for kappa in (claim["limiting_outer_saving"], "1/100"):
            with self.subTest(kappa=kappa), self.assertRaisesRegex(ValueError, "strict slack"):
                baseline.summarize(dict(record(), kappa=kappa), dict(claim, kappa=kappa))


class SourceBoundReportTests(unittest.TestCase):
    def test_complete_closure_and_selected_record_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected_fixture(root)
            result = baseline.report(root)
            self.assertEqual(result["status"], "PASS_RESEARCH_BASELINE_BINDINGS_ONLY")
            self.assertEqual(result["selected_record_sha256"],
                             sha256((root / "certificates/selected-result.json").read_bytes()).hexdigest())

    def test_noncertificate_source_and_proof_corruption_reject(self):
        for name in ("research/fixture/native-input.txt", "review.md"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                selected_fixture(root)
                (root / name).write_text("changed\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "bytes changed|supplement changed"):
                    baseline.report(root)

    def test_missing_source_and_unlisted_source_reject(self):
        for mutation in ("missing", "extra"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                selected_fixture(root)
                if mutation == "missing":
                    (root / "research/fixture/native-input.txt").unlink()
                else:
                    (root / "research/fixture/unlisted.txt").write_text("extra", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "inventory or bytes changed"):
                    baseline.report(root)

    def test_cli_rejects_corruption_and_authenticated_inconsistent_metadata(self):
        for optimize in ([], ["-O"]):
            with self.subTest(optimize=optimize), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                selected_fixture(root)
                command = [sys.executable, *optimize, "-B", str(root / "scripts/research_selected_baseline.py")]
                positive = subprocess.run(command, capture_output=True, timeout=30)
                self.assertEqual(positive.returncode, 0, positive.stderr)
                self.assertEqual(json.loads(positive.stdout)["binding_outer_rows"], ["main_transform"])
                (root / "research/fixture/CLAIM.json").write_text("{}", encoding="utf-8")
                negative = subprocess.run(command, capture_output=True, timeout=30)
                self.assertNotEqual(negative.returncode, 0)
                self.assertEqual(negative.stdout, b"")
                self.assertEqual(json.loads(negative.stderr)["status"], "FAIL_RESEARCH_BASELINE")
            with self.subTest(optimize=optimize, scope="authenticated metadata"), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                selected_fixture(root, dict(certificate(), strict_limiting_slack="1/100"))
                result = subprocess.run([sys.executable, *optimize, "-B",
                                         str(root / "scripts/research_selected_baseline.py")],
                                        capture_output=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, b"")
                self.assertIn("strict slack differs", json.loads(result.stderr)["error"])


if __name__ == "__main__":
    unittest.main()
