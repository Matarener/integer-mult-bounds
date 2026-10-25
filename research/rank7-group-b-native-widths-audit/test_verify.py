# SPDX-License-Identifier: Apache-2.0
"""Semantic failures at the actual group-B wrapper and owner boundaries."""

import copy
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import invoice
import native
from common import ENTRANCE, KERNEL, PACKAGE, W, WRONG_ENTRANCE, authenticate, data, decode, module


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blobs = authenticate()
        cls.word = data(cls.blobs, "data/WORD-base.json.gz")
        cls.result = decode((PACKAGE / "RESULT.json").read_bytes())
        cls.kernel = module(cls.blobs[KERNEL], "group_b_test_kernel")
        cls.tmp = tempfile.TemporaryDirectory(prefix="group-b-tests-")
        cls.canonical, cls.programs, _ = native.generate(cls.blobs, "base", Path(cls.tmp.name))
        cls.entering_key = cls.result["native_to_owner_join"]["base"]["448"]["native_pair"]
        cls.cold_key = cls.result["native_to_owner_join"]["base"]["299"]["native_pair"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def bind(self, stream, h=448, backward=False):
        return native.emitted_binding(self.word, self.canonical, stream, h, backward)

    def test_native_semantics(self):
        recipes = self.result["native"]["base"]["residuals"]
        rec = recipes[self.entering_key]["recipe"]
        native.check_recipe(self.kernel, rec, ENTRANCE, W)
        with self.assertRaisesRegex(ValueError, "phase-exact"):
            native.check_recipe(self.kernel, rec, WRONG_ENTRANCE, W)
        wrong = copy.deepcopy(rec)
        wrong["right"] = recipes[self.cold_key]["recipe"]["right"]
        with self.assertRaisesRegex(ValueError, "phase-exact"):
            native.check_recipe(self.kernel, wrong, ENTRANCE, W)
        wrong = copy.deepcopy(rec)
        wrong["left"]["phase"] = (wrong["left"]["phase"] + 1) % 4
        with self.assertRaisesRegex(ValueError, "phase-exact"):
            native.check_recipe(self.kernel, wrong, ENTRANCE, W)
        with self.assertRaisesRegex(ValueError, "width"):
            native.check_recipe(self.kernel, rec, [], W)

    def test_wrapper_and_lifetime_controls(self):
        stream = self.programs["forward"]
        self.bind(stream)
        self.bind(self.programs["backward"], backward=True)
        binding = self.result["native"]["base"]["bindings"]["448"]["forward"]
        bad = copy.deepcopy(stream)
        bad[binding["wrappers"][0][0]][3] = 0
        with self.assertRaisesRegex(ValueError, "wrapper pair"):
            self.bind(bad)
        bad = copy.deepcopy(stream)
        del bad[binding["wrappers"][1][0]]
        with self.assertRaisesRegex(ValueError, "two residual wrappers"):
            self.bind(bad)
        bad = copy.deepcopy(stream)
        free = bad.pop(binding["buffers"][1][0])
        bad.insert(binding["private_uses"][0], free)
        with self.assertRaisesRegex(ValueError, "cleanup before"):
            self.bind(bad)

    def test_scalar_clocks_and_cleanup_controls(self):
        stream = self.programs["forward"]
        binding = self.result["native"]["base"]["bindings"]["448"]["forward"]
        position = binding["private_uses"][0]
        bad = copy.deepcopy(stream)
        del bad[position]
        with self.assertRaisesRegex(ValueError, "scalar/climb clocks"):
            self.bind(bad)
        bad = copy.deepcopy(stream)
        bad[position][1][3] *= -1
        with self.assertRaisesRegex(ValueError, "scalar/climb clocks"):
            self.bind(bad)
        # Move a direct operation past a disjoint scalar, preserving its own order.
        r = binding["compact_helper"]
        later = next(i for i in range(position + 1, binding["buffers"][1][0])
                     if stream[i][0] == "scalar" and ["Z", r] not in stream[i][1][1:3])
        bad = copy.deepcopy(stream)
        moved = bad.pop(position)
        bad.insert(later, moved)
        with self.assertRaisesRegex(ValueError, "scalar/climb clocks"):
            self.bind(bad)

    def recount(self, fill=None, words=None, plan=None):
        b = self.blobs
        return invoice.recount(fill if fill is not None else data(b, "allocation/FILL.json.gz"),
            data(b, "allocation/ORDER.json"), data(b, "allocation/DISPATCH.json"),
            data(b, "allocation/vendor/TEMPLATE.json.gz"),
            plan if plan is not None else data(b, "allocation/vendor/PLAN.json.gz"),
            words if words is not None else {tag: data(b, f"data/WORD-{tag}.json.gz") for tag in ("base", "extra")},
            {tag: data(b, f"data/WORD-{tag}.json.gz")["report"]["local_profile"] for tag in ("base", "extra")})

    def test_owner_geometry_controls(self):
        good = self.recount()
        self.assertEqual(good["idle"], {1: 17310, 3: 4956, 5: 1728, 48: 28190})
        fill = data(self.blobs, "allocation/FILL.json.gz")
        bad = copy.deepcopy(fill); bad["rows"][1] = bad["rows"][0][:]
        with self.assertRaisesRegex(ValueError, "unique helper role"):
            self.recount(bad)
        bad = copy.deepcopy(fill); bad["rows"].pop()
        with self.assertRaisesRegex(ValueError, "271728 roles"):
            self.recount(bad)
        bad = copy.deepcopy(fill); bad["rows"][0][5] = 48
        with self.assertRaisesRegex(ValueError, "capacity"):
            self.recount(bad)
        plan = data(self.blobs, "allocation/vendor/PLAN.json.gz")
        plan["sides"]["0"] ^= 1
        with self.assertRaisesRegex(ValueError, "source child family"):
            self.recount(plan=plan)

    def test_entrance_width_reaches_actual_fill(self):
        words = {tag: data(self.blobs, f"data/WORD-{tag}.json.gz") for tag in ("base", "extra")}
        for word in words.values():
            del word["start_extra"]["448"]
        # Using terminal rank seven as the helper width breaks the actual packing.
        with self.assertRaisesRegex(ValueError, "capacity|compact prefix"):
            self.recount(words=words)

    def test_source_corruption_and_duplicate_keys(self):
        checks = decode((Path(self.tmp.name) / "local/LOCAL-CHECKS.json").read_bytes())
        native.bind_program_receipts(self.programs, checks)
        changed = copy.deepcopy(self.programs)
        changed["forward"].pop()
        with self.assertRaisesRegex(ValueError, "event stream digest"):
            native.bind_program_receipts(changed, checks)
        changed = copy.deepcopy(self.programs)
        changed["forward"][-1][-1] = "changed event"
        with self.assertRaisesRegex(ValueError, "event stream digest"):
            native.bind_program_receipts(changed, checks)
        first = next(iter(self.blobs))
        with tempfile.TemporaryDirectory(prefix="group-b-corruption-") as tmp:
            root = Path(tmp)
            target = root / first
            target.parent.mkdir(parents=True)
            target.write_bytes(self.blobs[first] + b"\n# corrupt\n")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                authenticate(root)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            decode(b'{"frame":0,"frame":115}')


if __name__ == "__main__":
    unittest.main()
