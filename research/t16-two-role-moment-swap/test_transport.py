"""Controls for the explicitly allowed invoice-serialization hash graph."""

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path

import support_checks
import transport

PACKAGE = Path(__file__).resolve().parent
FROZEN = PACKAGE / "support/construction/raw"
INVOICE = "global/audit/PREFIX-AND-INVOICE.json"
NAMES = (
    "ASSEMBLY.json",
    INVOICE,
    "global/audit/OWNERS-AND-PROFILE.json",
    "global/audit/ASYNC-AUDIT.json",
)


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name)
        self.strict = self.work / "strict"
        for name in NAMES:
            path = self.strict / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(FROZEN / name, path)

    def tearDown(self):
        self.temp.cleanup()

    def attest(self):
        with redirect_stdout(io.StringIO()):
            return transport.attest(PACKAGE, self.work)

    def write(self, name, document, **kwargs):
        (self.strict / name).write_text(json.dumps(document, **kwargs) + "\n")

    def test_nominal_and_serialization_only_relation(self):
        nominal = self.attest()
        self.assertEqual(nominal["invoice_sha256"], nominal["frozen_invoice_sha256"])
        invoice = transport.load(self.strict / INVOICE)
        self.write(INVOICE, invoice, sort_keys=True, indent=1)
        assembly = transport.load(self.strict / "ASSEMBLY.json")
        assembly["input_sha256"]["fresh_invoice"] = transport.sha(self.strict / INVOICE)
        self.write("ASSEMBLY.json", assembly, sort_keys=True, indent=1)
        graph = self.attest()
        self.assertNotEqual(graph["invoice_sha256"], graph["frozen_invoice_sha256"])
        score_path = transport.expected_score(PACKAGE, self.work, graph)
        score = transport.load(score_path)
        self.assertEqual(score["assembly_sha256"], graph["assembly_sha256"])
        self.assertEqual(
            score["source_sha256"]["PREFIX-AND-INVOICE.json"], graph["invoice_sha256"]
        )
        construction = transport.expected_construction(
            PACKAGE / "support/construction", graph
        )
        self.assertEqual(construction["artifacts"]["invoice"], graph["invoice_sha256"])
        review = transport.load(
            transport.expected_invoice(PACKAGE, self.work, graph, score_path)
        )
        self.assertEqual(
            review["independent_score_binding"]["score_sha256"],
            transport.sha(score_path),
        )
        self.assertEqual(transport.load(FROZEN / INVOICE), invoice)

    def test_changed_cost_missing_extra_field_and_type_reject(self):
        old = transport.load(FROZEN / INVOICE)
        changed_cost = deepcopy(old)
        changed_cost["selected_real_component_primitives"] -= 1
        missing = deepcopy(old)
        del missing["charged_prefix_bits"]
        extra = dict(old, unpriced_charge=0)
        wrong_type = deepcopy(old)
        wrong_type["strict_checks"]["mass"] = 1
        for mutant in (changed_cost, missing, extra, wrong_type):
            self.write(INVOICE, mutant)
            with self.assertRaisesRegex(ValueError, "complete invoice content"):
                self.attest()

    def test_changed_cap_inequality_and_unrelated_hash_reject(self):
        old = transport.load(FROZEN / "ASSEMBLY.json")
        cap = deepcopy(old)
        cap["bit_lower"] = "1/100"
        inequality = deepcopy(old)
        inequality["outer"]["bit_positive"] = "0"
        source = deepcopy(old)
        source["input_sha256"]["owner_audit"] = "0" * 64
        extra = dict(old, unknown_premise=True)
        for mutant in (cap, inequality, source, extra):
            self.write("ASSEMBLY.json", mutant)
            with self.assertRaisesRegex(ValueError, "complete assembly content"):
                self.attest()

    def test_forged_actual_invoice_binding_rejects(self):
        assembly = transport.load(FROZEN / "ASSEMBLY.json")
        assembly["input_sha256"]["fresh_invoice"] = "0" * 64
        self.write("ASSEMBLY.json", assembly)
        with self.assertRaisesRegex(ValueError, "complete assembly content"):
            self.attest()

    def test_fixed_owner_and_controller_bytes_remain_fixed(self):
        for name in NAMES[2:]:
            path = self.strict / name
            raw = path.read_bytes()
            path.write_bytes(raw + b" ")
            with self.assertRaisesRegex(ValueError, "fixed owner/controller bytes"):
                self.attest()
            path.write_bytes(raw)

    def test_bad_score_profile_field_and_unrelated_hash_reject(self):
        graph = self.attest()
        expected_path = transport.expected_score(PACKAGE, self.work, graph)
        old = transport.load(expected_path)
        profile = deepcopy(old)
        profile["complex_profile"]["1"] -= 1
        source = deepcopy(old)
        source["source_sha256"]["PR589-EXPECTED.json"] = "0" * 64
        extra = dict(old, omitted_charge=0)
        for mutant in (profile, source, extra):
            path = self.work / "bad-score.json"
            path.write_text(json.dumps(mutant, indent=2) + "\n")
            with (
                redirect_stdout(io.StringIO()),
                self.assertRaisesRegex(ValueError, "bad score"),
            ):
                support_checks.compare_reports(path, expected_path, "bad score")

    def test_bad_invoice_review_still_rejects(self):
        graph = self.attest()
        score = transport.expected_score(PACKAGE, self.work, graph)
        expected = transport.expected_invoice(PACKAGE, self.work, graph, score)
        mutant = transport.load(expected)
        mutant["physical_padding"]["row"] -= 1
        path = self.work / "bad-review.json"
        path.write_text(json.dumps(mutant, indent=2) + "\n")
        with (
            redirect_stdout(io.StringIO()),
            self.assertRaisesRegex(ValueError, "bad review"),
        ):
            support_checks.compare_reports(path, expected, "bad review")

    def test_frozen_review_score_edge_is_required(self):
        graph = self.attest()
        score = transport.expected_score(PACKAGE, self.work, graph)
        fake = self.work / "fake-package"
        for name in ("invoice", "exact-score"):
            folder = fake / "support" / name
            folder.mkdir(parents=True)
            shutil.copyfile(
                PACKAGE / "support" / name / "RESULT.json", folder / "RESULT.json"
            )
        path = fake / "support/invoice/RESULT.json"
        mutant = transport.load(path)
        mutant["independent_score_binding"]["score_sha256"] = "0" * 64
        path.write_text(json.dumps(mutant))
        with self.assertRaisesRegex(ValueError, "frozen review score dependency"):
            transport.expected_invoice(fake, self.work, graph, score)

    def test_duplicate_keys_and_nonfinite_values_reject(self):
        path = self.work / "bad.json"
        path.write_text('{"a": 1, "a": 1}')
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            transport.load(path)
        with self.assertRaises(ValueError):
            transport.canonical({"x": float("nan")})


if __name__ == "__main__":
    unittest.main()
