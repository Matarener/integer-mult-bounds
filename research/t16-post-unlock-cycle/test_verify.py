"""Behavioral failures at the post-unlock cycle and complete invoice boundaries."""

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
        cls.new, cls.before, cls.after = v.construct(cls.old, cls.ctx)

    def test_paid_delta_and_exact_roles(self):
        self.assertEqual(self.after["idle"][1], self.before["idle"][1] - 1)
        self.assertEqual(self.after["idle"].get(2, 0), self.before["idle"][2] - 1)
        self.assertEqual(self.after["idle"][3], self.before["idle"][3] + 1)
        self.assertEqual(self.after["rank_mass"], self.before["rank_mass"])
        changed = [i for i, (a, b) in enumerate(zip(self.old, self.new))
                   if v.bin_key(a) != v.bin_key(b)]
        self.assertEqual(changed, sorted(v.CYCLE))

    def test_partial_exchange_rejects(self):
        rows = [dict(z) for z in self.old]
        rows[v.CYCLE[0]] = self.new[v.CYCLE[0]]
        with self.assertRaises((ValueError, self.ctx[0].Reject)):
            v.audit_map(rows, self.ctx)

    def test_reverse_triple_rejects(self):
        rows = v.rotate(self.old, tuple(reversed(v.CYCLE)))
        with self.assertRaises((ValueError, self.ctx[0].Reject)):
            v.audit_map(rows, self.ctx)

    def test_wrong_family_and_width_reject(self):
        for field, delta in (("family", 1), ("width", -1)):
            rows = [dict(z) for z in self.new]
            rows[v.CYCLE[0]][field] += delta
            with self.subTest(field=field), self.assertRaises(self.ctx[0].Reject):
                v.audit_map(rows, self.ctx)

    def test_cycle_and_role_boundaries(self):
        for indices in ((1, 1, 2), (-1, 2, 3), (True, 2, 3), (0,), (0, 1, 2, 3)):
            with self.subTest(indices=indices), self.assertRaises(ValueError):
                v.construct(self.old, self.ctx, indices)

    def test_valid_map_with_wrong_delta_rejects(self):
        with self.assertRaisesRegex(ValueError, "idle delta"):
            v.construct(self.old, self.ctx, (0, 1, 2))

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
