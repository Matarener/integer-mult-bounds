"""Behavioral controls for complete maps, chronology, concavity and source binding."""

import copy
import tempfile
import unittest
from pathlib import Path

import independent
import verify as v


class RepackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = v.predecessor(v.ROOT, v.check_sources(v.ROOT))
        cls.ctx = v.context(v.ROOT)

    def test_complete_maps(self):
        final, before, after = v.construct(self.old, self.ctx)
        self.assertEqual(before["rank_mass"], after["rank_mass"])
        self.assertEqual(
            v.digest(final), v.read(v.PACKAGE / "RESULT.json")["owner_canonical_sha256"]
        )
        self.assertEqual(after["deficit"], 5120)

    def test_rotation_without_swap_rejects(self):
        with self.assertRaises((ValueError, self.ctx[0].Reject)):
            v.audit_map(v.rotate(self.old, v.CYCLE), self.ctx)

    def test_reversed_rotation_rejects(self):
        with self.assertRaises((ValueError, self.ctx[0].Reject)):
            v.construct(self.old, self.ctx, tuple(reversed(v.CYCLE)))

    def test_missing_cycle_role_rejects(self):
        with self.assertRaises(ValueError):
            v.construct(self.old, self.ctx, v.CYCLE[:-1])

    def test_duplicate_cycle_role_rejects(self):
        with self.assertRaises(ValueError):
            v.construct(self.old, self.ctx, (v.CYCLE[0],) * 8)

    def test_intermediate_profile_is_worse(self):
        before = v.audit_map(self.old, self.ctx)
        middle = v.audit_map(v.rotate(self.old, v.SWAP), self.ctx)
        delta = {
            k: middle["idle"].get(k, 0) - before["idle"].get(k, 0) for k in (1, 2, 3)
        }
        self.assertEqual(delta, {1: 1, 2: 1, 3: -1})

    def test_wrong_helper_width_rejects(self):
        bad = [dict(row) for row in self.old]
        bad[v.CYCLE[0]]["width"] -= 1
        with self.assertRaises((ValueError, self.ctx[0].Reject)):
            v.audit_map(bad, self.ctx)

    def test_typed_invoice_rejects_charge_change(self):
        good = {"charge": {"rows": 16469}, "owner_audit_sha256": "old"}
        other = copy.deepcopy(good)
        other["charge"]["rows"] -= 1
        with self.assertRaises(ValueError):
            v.same_invoice(good, other)
        other = dict(good, owner_audit_sha256="new")
        v.same_invoice(good, other)

    def test_actual_source_byte_mutation_rejects(self):
        first = next(
            x
            for x in v.read(v.PACKAGE / "SOURCES.json")["files"]
            if x["usage"] == "input"
        )
        with tempfile.TemporaryDirectory(prefix="ten-helper-source-") as directory:
            fake = Path(directory)
            target = fake / first["path"]
            target.parent.mkdir(parents=True)
            target.write_bytes((v.ROOT / first["path"]).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "changed input"):
                v.check_sources(fake)

    def test_independent_payload(self):
        old, middle, final = independent.reconstruct()
        direct = v.rotate(v.rotate(old, v.SWAP), v.CYCLE)
        self.assertEqual(final, direct)
        self.assertNotEqual(old, middle)


if __name__ == "__main__":
    unittest.main()
