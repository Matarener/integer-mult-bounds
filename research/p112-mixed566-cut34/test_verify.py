"""Observable proof-boundary, source corruption and receipt controls."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V = ModuleType("cut34_checker")
V.__file__ = str(HERE / "verify.py")
exec(compile((HERE / "verify.py").read_bytes(), V.__file__, "exec"), V.__dict__)


class ProofControls(unittest.TestCase):
    def test_strict_cut34_and_predecessor_cut33(self):
        self.assertEqual(V.arithmetic(34)["D6"]["82"]["coverage_upper"], 46)
        self.assertTrue(all(x["contradiction"] for x in V.arithmetic(33)["D6"].values()))

    def test_cut35_has_no_certificate_here(self):
        with self.assertRaises(ValueError):
            V.arithmetic(35)  # E6 equality86 supplies no strict contradiction.
        with self.assertRaises(ValueError):
            V.d6_case(82, 35)  # N>=47 does not force capacity equality48.

    def test_refined_rank6_capacities_make_axis_split_strict(self):
        # After equality confines the rank5 piece, even the simpler two-axis
        # bound47 is strict. The inherited pair-union28 improves it to46.
        self.assertEqual(V.axis_upper((0, 1, 0), (12, 18, 18), 29), 46)
        self.assertEqual(min(29, 12 + 18) + 18, 47)
        self.assertGreaterEqual(29 + 20, 48)  # Unrefined rank6 capacity loses the gap.
        self.assertEqual(12 + 18 + 18, 48)

    def test_json_types_and_missing_new_union_reject(self):
        wanted = V.json_bytes(HERE / "RESULT.json")
        bad = json.loads(json.dumps(wanted))
        bad["arithmetic"]["cut"] = True
        with self.assertRaises(ValueError):
            V.same_receipt(bad, wanted)
        bad = json.loads(json.dumps(wanted))
        del bad["arithmetic"]["D6"]["86"]
        with self.assertRaises(ValueError):
            V.same_receipt(bad, wanted)

    def copied_cli(self, kind):
        with tempfile.TemporaryDirectory(prefix="cut34-control-") as temp:
            root = Path(temp)
            package = root / "research/p112-mixed566-cut34"
            package.mkdir(parents=True)
            for name in ("verify.py", "SOURCES.json", "RESULT.json"):
                (package / name).write_bytes((HERE / name).read_bytes())
            for relative in V.INPUTS:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            if kind == "corrupt":
                target = root / "research/p112-root-simplex-exclusion/geometry.py"
                target.write_bytes(target.read_bytes() + b"\n")
            elif kind == "reclassify":
                path = package / "SOURCES.json"
                data = json.loads(path.read_text())
                data["files"][-1]["usage"] = "provenance"
                path.write_text(json.dumps(data))
            else:
                self.fail("unknown private control")
            result = subprocess.run([sys.executable, "-O", "-W", "error", "-B",
                                     str(package / "verify.py")], cwd=root,
                                    capture_output=True, text=True, timeout=20,
                                    env={**os.environ, "PYTHONPYCACHEPREFIX": str(root / "pycache")})
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("PASS_CONDITIONAL", result.stdout)
            return result.stderr

    def test_actual_optimized_corrupt_source_rejects(self):
        self.assertIn("source SHA256", self.copied_cli("corrupt"))

    def test_executable_cannot_be_reclassified_as_provenance(self):
        self.assertIn("exact proof and executable input pins", self.copied_cli("reclassify"))


if __name__ == "__main__":
    unittest.main()
