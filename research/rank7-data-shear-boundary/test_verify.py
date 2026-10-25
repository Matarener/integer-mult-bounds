# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the all-data observer and its reused covectors."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("data_boundary", Path(__file__).with_name("verify.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
MOD = verify.modules(verify.authenticate())


class DataBoundaryTests(unittest.TestCase):
    def endpoint(self, events, role="L0", backward=False):
        return MOD["cone"].endpoint(events, role, len(events) - 1, backward)

    def test_four_shear_blocks(self):
        self.assertEqual(verify.expected(0, False), [["L0", [], "1"]])
        self.assertEqual(verify.expected(112, False), [["L0", [], "1"], ["L112", [], "1"]])
        self.assertEqual(verify.expected(0, True), [["L0", [], "1"], ["L112", [], "-1"]])
        self.assertEqual(verify.expected(112, True), [["L112", [], "1"]])

    def test_target_only_fault_escapes_helper_observation(self):
        events = [["scalar", ["add", "L112", "L0", 2, 1], []]]
        self.assertEqual(self.endpoint(events, "L249"), [["L249", [], "1"]])
        self.assertNotEqual(self.endpoint(events, "L112"), verify.expected(112, False))

    def test_copy_overwrites_and_clear_erases(self):
        events = [["scalar", ["copy", "L0", "L1"], []],
                  ["scalar", ["add", "L0", "L2", 1, 2], []]]
        self.assertEqual(self.endpoint(events), [["L1", [], "1"], ["L2", [], "1/2"]])
        self.assertEqual(self.endpoint(events + [["scalar", ["clear", "L0"], []]]), [])

    def test_private_zero_is_not_arbitrary_dirty(self):
        events = [["zero_buffer", "alloc", "Z249"],
                  ["scalar", ["add", "L0", "Z249", 3, 1], []],
                  ["zero_buffer", "free", "Z249"]]
        self.assertEqual(self.endpoint(events), [["L0", [], "1"]])
        dirty = [["scalar", ["add", "L0", "L249", 3, 1], []]]
        self.assertEqual(self.endpoint(dirty), [["L0", [], "1"], ["L249", [], "3"]])

    def test_noncommuting_warp_order_and_dual_namespace(self):
        events = [["warp", "L0", 1], ["warp", "L0", 2]]
        self.assertEqual(self.endpoint(events), [["L0", [2, 1], "1"]])
        self.assertEqual(self.endpoint(events, backward=True), [["L0", [1000002, 1000001], "1"]])
        self.assertEqual(self.endpoint(events + [["warp", "L0", -2]]), [["L0", [1], "1"]])

    def test_forward_helper_and_free_observer(self):
        original = ["L" + str(r) for r in range(632)]
        alloc = [["zero_buffer", "alloc", "Z" + str(r)] for r in range(224, 315)]
        free = [["zero_buffer", "free", "Z" + str(r)] for r in range(224, 315)]
        body = [["scalar", ["add", "L224", "L0", 1, 2], []],
                ["scalar", ["add", "L224", "L0", -1, 2], []]]
        result = verify.restored_rows(MOD, alloc + body + free, original, False)
        self.assertEqual(result["helper_outputs"], 408)
        self.assertEqual(len(result["frees"]), 91)
        with self.assertRaises(ValueError):
            verify.restored_rows(MOD, alloc + body[:1] + free, original, False)
        dirty = [["scalar", ["add", "Z224", "L0", 1, 1], []]]
        with self.assertRaises(ValueError):
            verify.restored_rows(MOD, alloc + dirty + free, original, False)

    def test_boundary_rejects_invalid_roles_and_indices(self):
        for output in (-1, 224, "0", True):
            with self.assertRaises(ValueError):
                verify.expected(output, False)
        with self.assertRaises(ValueError):
            MOD["cone"].endpoint([], "L0", 0, False)


if __name__ == "__main__":
    unittest.main()
