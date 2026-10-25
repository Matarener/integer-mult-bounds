"""Behavioral certificate, chronology, source and literal owner controls."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reconstruct as r  # noqa: E402 - isolated-script bootstrap

ROOT = Path(os.environ.get("T8_RESEARCH_ROOT", r.HERE / "source-inputs")).resolve()


class CertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.plan, cls.audit = r.reconstruct(ROOT)
        cls.cert = r.read(r.HERE / "CERTIFICATE.json")
        cls.auditor, cls.geo, cls.widths, cls.local = r.sources(ROOT)

    def rejected(self, change, message):
        cert = copy.deepcopy(self.cert)
        change(cert)
        with self.assertRaisesRegex(ValueError, message):
            r.reconstruct(ROOT, certificate=cert)

    def test_positive_literal_and_both_provider_contract(self):
        self.assertEqual(len(self.rows), 29376)
        self.assertEqual(self.audit["rank_mass"], 520704)
        self.assertEqual(self.audit["idle"], {1: 1964, 3: 534, 5: 172, 7: 2, 48: 3050})

    def test_duplicate_and_missing_flow(self):
        self.rejected(lambda c: c["flow"].append(c["flow"][0][:]), "duplicate flow")
        self.rejected(lambda c: c["flow"].pop(), "demand|supply")

    def test_fractional_and_boolean_counts(self):
        self.rejected(lambda c: c["flow"][0].__setitem__(3, 1.5), "integer domain")
        self.rejected(
            lambda c: c["allocation"][0].__setitem__(2, True), "integer domain"
        )

    def test_width_and_bin_corruption(self):
        self.rejected(
            lambda c: c["patterns"][0][1].__setitem__(5, 12), "overfull pattern"
        )
        self.rejected(
            lambda c: c["allocation"][0].__setitem__(2, c["allocation"][0][2] - 1),
            "integer domain|group bin",
        )

    def test_window_corruption(self):
        def change(c):
            # Find a known forbidden time from authenticated literal plan windows.
            grouped = {}
            for key, (capacity, times) in self.plan["windows"].items():
                grouped.setdefault((capacity, tuple(times)), []).append(key)
            groups = sorted(grouped)
            for row in c["flow"]:
                group = c["allocation"][row[0]][0]
                bad = next((t for t in range(72) if t not in groups[group][1]), None)
                if bad is not None:
                    row[1] = bad
                    return
            self.fail("missing negative window control")

        self.rejected(change, "flow outside window")

    def test_literal_time_width_and_family_controls(self):
        for field, value in [("time", 71), ("width", 10), ("family", 8 * 896)]:
            rows = copy.deepcopy(self.rows)
            rows[0][field] = value
            with self.assertRaises(self.auditor.Reject):
                self.auditor.audit(
                    self.geo,
                    self.widths,
                    self.local,
                    rows,
                    self.plan,
                    self.audit["idle"],
                    8,
                )

    def test_local_source_corruption_precedes_reconstruction(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(r.HERE, package)
            with (package / "CERTIFICATE.json").open("a") as handle:
                handle.write("\n")
            with self.assertRaisesRegex(ValueError, "source hash"):
                r.reconstruct(ROOT, package=package)

    def test_modern_two_provider_dispatch(self):
        fill, order, dispatch, audit = r.modern_inputs(ROOT, self.rows, self.plan)
        self.assertEqual(len(fill["rows"]), 29376)
        self.assertEqual(dispatch[0], [0, 0, "extra"])
        self.assertTrue(all(row[2] == "gauge44" for row in dispatch[1:]))
        bad = copy.deepcopy(self.rows)
        bad[0]["width"] += 1
        with self.assertRaisesRegex(ValueError, "actual provider width"):
            r.modern_inputs(ROOT, bad, self.plan)

    def test_fixed_replica_and_source_projection_controls(self):
        source = r.read(r.HERE / "PLAN-3413.json")
        mutations = [
            (lambda plan: plan["order"].pop(), "call inventory"),
            (lambda plan: plan["order"][0].__setitem__(1, 8), "call inventory"),
            (lambda plan: plan["order"][0].__setitem__(1, False), "integer T8 calls"),
            (lambda plan: plan.__setitem__("T", 16), "fixed T8 geometry"),
            (lambda plan: plan.__setitem__("T", 8.0), "integer geometry"),
        ]
        for change, message in mutations:
            with self.subTest(message=message):
                plan = copy.deepcopy(self.plan)
                change(plan)
                with self.assertRaisesRegex(ValueError, message):
                    r.projected_order(source, plan)
        plan = copy.deepcopy(self.plan)
        second = next(i for i, call in enumerate(plan["order"]) if call == [1, 0])
        plan["order"][0], plan["order"][second] = (
            plan["order"][second],
            plan["order"][0],
        )
        with self.assertRaisesRegex(ValueError, "retained-replica projection"):
            r.projected_order(source, plan)

    def test_retained_t8_window_is_rederived(self):
        plan = copy.deepcopy(self.plan)
        key = next(iter(plan["windows"]))
        plan["windows"][key][1].append(71)
        with self.assertRaises(self.auditor.Reject):
            self.auditor.audit(
                self.geo,
                self.widths,
                self.local,
                self.rows,
                plan,
                self.audit["idle"],
                8,
            )

    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"schema":1,"schema":2}', object_pairs_hook=r.unique)


if __name__ == "__main__":
    unittest.main()
