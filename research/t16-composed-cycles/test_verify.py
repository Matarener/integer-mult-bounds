"""Observable construction failures, including partial and reversed cycles."""

import copy
import unittest
from unittest.mock import patch

import verify as v


class CycleChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.export = v.check_sources(v.ROOT)
        cls.old = v.predecessor(v.ROOT, cls.export)
        cls.ctx = v.context(v.ROOT)
        cls.new = v.compose(cls.old)

    def test_completed_cycle(self):
        before = v.audit_map(self.old, self.ctx)
        after = v.audit_map(self.new, self.ctx)
        self.assertEqual(after["idle"][1], before["idle"][1] - 6)
        self.assertEqual(after["idle"].get(2, 0), before["idle"][2] - 6)
        self.assertEqual(after["idle"][3], before["idle"][3] + 6)
        self.assertEqual(after["rank_mass"], before["rank_mass"])
        moved = [
            i
            for i, (a, b) in enumerate(zip(self.old, self.new))
            if v.bin_key(a) != v.bin_key(b)
        ]
        self.assertEqual(moved, sorted(i for cycle in v.CYCLES for i in cycle))

    def test_partial_cycle_rejects(self):
        rows = [dict(row) for row in self.old]
        rows[v.CYCLE[0]] = self.new[v.CYCLE[0]]
        with self.assertRaises((ValueError, self.ctx[0].Reject)):
            v.audit_map(rows, self.ctx)

    def test_missing_cycle_has_wrong_profile(self):
        rows = self.old
        for indices in v.CYCLES[:-1]:
            rows = v.cycle(rows, indices)
        partial = v.audit_map(rows, self.ctx)
        complete = v.audit_map(self.new, self.ctx)
        self.assertNotEqual(partial["profile"], complete["profile"])
        self.assertEqual(partial["idle"][2], 1)

    def test_overlapping_composition_rejects(self):
        for cycles in (v.CYCLES[:-1], (v.CYCLES[0],) * 6):
            with self.subTest(cycles=cycles), self.assertRaises(ValueError):
                v.compose(self.old, cycles)

    def test_wrong_physical_family_rejects(self):
        rows = [dict(row) for row in self.new]
        rows[v.CYCLE[0]]["family"] += 1
        with self.assertRaises(self.ctx[0].Reject):
            v.audit_map(rows, self.ctx)

    def test_changed_helper_width_rejects(self):
        rows = [dict(row) for row in self.new]
        rows[v.CYCLE[0]]["width"] -= 1
        with self.assertRaises(self.ctx[0].Reject):
            v.audit_map(rows, self.ctx)

    def test_cycle_boundary_rejects(self):
        for indices in ((1, 1, 2), (-1, 2, 3), (True, 2, 3), (0, 2)):
            with self.subTest(indices=indices), self.assertRaises(ValueError):
                v.cycle(self.old, indices)

    def test_corrupt_predecessor_rejects(self):
        original = v.read
        delta = copy.deepcopy(original(v.PACKAGE / "predecessor.patch.json"))
        delta[0]["before"]["width"] += 1
        with (
            patch.object(
                v,
                "read",
                side_effect=lambda p: (
                    delta if p.name == "predecessor.patch.json" else original(p)
                ),
            ),
            self.assertRaisesRegex(ValueError, "patch preimage"),
        ):
            v.predecessor(v.ROOT, self.export)

    def test_changed_complete_payload_rejects(self):
        export = dict(self.export, predecessor_canonical_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "complete owner payload"):
            v.predecessor(v.ROOT, export)

    def test_invoice_serialization_and_identifiers(self):
        old = {"charge": 1, "future": [2, 3], "template_sha256": "old"}
        new = {"template_sha256": "fresh", "future": [2, 3], "charge": 1}
        v.same_invoice(old, new)

    def test_invoice_values_types_unknown_keys_and_array_order(self):
        old = {"charge": 1, "future": [2, 3]}
        for new in (
            {"charge": True, "future": [2, 3]},
            {"charge": 1.0, "future": [2, 3]},
            {"charge": 2, "future": [2, 3]},
            {"charge": 1},
            {"charge": 1, "future": [3, 2]},
            {"charge": 1, "future": [2, 3], "new_charge": 0},
        ):
            with self.subTest(new=new), self.assertRaises(ValueError):
                v.same_invoice(old, new)


if __name__ == "__main__":
    unittest.main()
