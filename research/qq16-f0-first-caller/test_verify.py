"""Failure controls and a separate small-domain arithmetic check.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
"""
from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
V = types.ModuleType("caller_audit_source")
V.__file__ = str(HERE / "verify.py")
exec(compile((HERE / "verify.py").read_bytes(), V.__file__, "exec"), V.__dict__)


class CallerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = V.load()
        cls.T = V.source_module(HERE, "vendor/tapes.py", V.TAPES_SHA)

    def test_wrong_f0_embedding_rejected(self):
        data = deepcopy(self.data)
        data[0]["programs"]["F_0"][0][1] = "backward"
        with self.assertRaisesRegex(ValueError, "F0 retained-core binding"):
            V.bind_first(data)

    def test_changed_first_child_rejected(self):
        data = deepcopy(self.data)
        data[0]["core_words"]["forward"][9894][2] = 547
        with self.assertRaisesRegex(ValueError, "literal first caller changed"):
            V.bind_first(data)

    def test_changed_prefix_rejected(self):
        data = deepcopy(self.data)
        data[0]["core_words"]["forward"][262][1][3] = -1
        with self.assertRaisesRegex(ValueError, "literal prefix changed"):
            V.bind_first(data)

    def test_changed_recipe_phase_rejected(self):
        data = deepcopy(self.data)
        child = next(x for x in data[2]["children"] if (x["old"], x["new"]) == (0, 4))
        child["left"]["phase"] = 1
        with self.assertRaisesRegex(ValueError, "literal native recipe changed"):
            V.bind_first(data)

    def test_changed_private_scope_in_suffix_rejected(self):
        data = deepcopy(self.data)
        data[0]["core_words"]["forward"][10000] = [
            "scalar", ["add", ["C", 0], ["L", 546], 1, 1], 4]
        with self.assertRaisesRegex(ValueError, "private field reused"):
            V.bind_first(data)

    def test_source_authentication_precedes_execution(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            raw = b"raise RuntimeError('must not execute changed source')\n"
            (root / "bad.py").write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                V.source_module(root, "bad.py", "0" * 64)
            with self.assertRaisesRegex(ValueError, "source file/size"):
                V.source_bytes(root, "bad.py", hashlib.sha256(raw).hexdigest(), cap=1)

    def test_source_parent_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "real").mkdir()
            (root / "real/x").write_bytes(b"input")
            (root / "alias").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "source symlink"):
                V.source_bytes(root, "alias/x", hashlib.sha256(b"input").hexdigest())

    def test_both_live_sources_reject_corruption(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            for path in V.PINS:
                file = root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b"not the pinned source")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                V.load(root)
            first = next(iter(V.PINS))
            (root / first).write_bytes((V.ROOT / first).read_bytes())
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                V.load(root)

    def test_complete_receipt_comparison_rejects_mutation(self):
        result = json.loads((HERE / "RESULT.json").read_text())
        V.compare_result(result)
        result["physical_obligations"]["grid_refinement"] = "free"
        with self.assertRaisesRegex(ValueError, "complete RESULT.json mismatch"):
            V.compare_result(result)

    def test_receipt_bool_integer_and_duplicate_keys_rejected(self):
        result = json.loads((HERE / "RESULT.json").read_text())
        changed = deepcopy(result)
        changed["conditional_arithmetic_repair"]["minimum_extra_fractional_bits_for_arbitrary_integer_mantissas"] = True
        with self.assertRaisesRegex(ValueError, "complete RESULT.json mismatch"):
            V.compare_result(changed)
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "RESULT.json"
            path.write_text('{"supplier_admitted":true,"supplier_admitted":false}')
            with self.assertRaisesRegex(ValueError, "duplicate RESULT.json key"):
                V.compare_result(result, path)

    def test_all_81_signed_pair_inputs_on_changed_grid(self):
        # Independent direct formulas on a pair, with no native-vector imports.
        # All original components lie in {-1,0,1}; grid q+1 stores twice them.
        for a, b, c, d in product((-1, 0, 1), repeat=4):
            tapes = self.T.fixture([2*a, 2*c], [2*b, 2*d], 5,
                                   origins=[-2, 3, 11, -19, 23, 41])
            self.T.axis_kernel(tapes, 1, 5, 0)
            self.assertEqual(self.T.decode(tapes[0], 5), [a-b+c+d, c-d+a+b])
            self.assertEqual(self.T.decode(tapes[1], 5), [b+a+d-c, d+c+b-a])
            self.assertTrue(all(t.head == t.origin for t in tapes))
            self.assertTrue(all(not any(t.cells) for t in tapes[2:]))
            self.assertEqual(V.tariff(tapes), {"read": 60, "write": 60, "move": 200})

    def test_exact_unchanged_grid_pair_domain(self):
        for a, b, c, d in product((0, 1), repeat=4):
            tapes = self.T.fixture([a, c], [b, d], 5)
            if (a+b+c+d) % 2:
                with self.assertRaisesRegex(ValueError, "nonexact half"):
                    self.T.axis_kernel(tapes, 1, 5, 0)
            else:
                self.T.axis_kernel(tapes, 1, 5, 0)
                self.assertEqual(self.T.decode(tapes[0], 5),
                                 [(a-b+c+d)//2, (c-d+a+b)//2])
                self.assertEqual(self.T.decode(tapes[1], 5),
                                 [(b+a+d-c)//2, (d+c+b-a)//2])

    def test_increasing_magnitude_width_does_not_fix_parity(self):
        for width in (2, 5, 17, 65):
            tapes = self.T.fixture([1, 0], [0, 0], width)
            with self.assertRaisesRegex(ValueError, "nonexact half"):
                self.T.axis_kernel(tapes, 1, width, 0)

    def test_evenness_does_not_guarantee_signed_numerator_range(self):
        # +8 is outside signed four-bit range even though the inputs fit.
        self.assertEqual(V.preconditions([2, 2], [-2, 2], 4),
                         {"even": True, "signed_range": False})
        tapes = self.T.fixture([2, 2], [-2, 2], 4)
        self.T.axis_kernel(tapes, 1, 4, 0)
        self.assertEqual(self.T.decode(tapes[0], 4)[0], -4)
        wider = self.T.fixture([2, 2], [-2, 2], 5)
        self.T.axis_kernel(wider, 1, 5, 0)
        self.assertEqual(self.T.decode(wider[0], 5)[0], 4)

    def test_borrowed_scratch_cannot_be_discarded(self):
        tapes = self.T.fixture([2, 0], [0, 0], 5)
        tapes[2].discardable = False
        with self.assertRaisesRegex(ValueError, "owned scratch required"):
            self.T.axis_kernel(tapes, 1, 5, 0)


if __name__ == "__main__":
    unittest.main()
