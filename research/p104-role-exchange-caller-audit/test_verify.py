#!/usr/bin/env python3
"""Behavioral and actual export/CLI controls. Apache-2.0; same-session AI checks."""
import gzip
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
M = runpy.run_path(str(HERE / "verify.py"))


class CallerControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.A, cls.J, cls.N, cls.B = M["geometry"]()
        cls.final = M["load"](ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json")["final_frames"]

    def accepted(self, ops, consume=False):
        state, frames, bill = M["replay"](self.A, ops, self.final)
        M["endpoint"](state, frames, self.final, consume)
        return bill

    def test_equivalent_binary_frame_bases(self):
        self.assertEqual(M["space"]([1, 2, 4]), M["space"]([3, 6, 4]))
        self.assertNotEqual(M["space"]([1, 2]), M["space"]([1, 4]))

    def test_missing_source_return_is_detected(self):
        good = M["fused"](self.J, self.N, self.B)
        restore = M["pivot_stream"](self.J, self.N, self.B, restore=True)
        # Delete the complete restoration block; all sum outputs still exist.
        start = 104+len(M["pivot_stream"](self.J, self.N, self.B))+len(M["scatter"](self.J, self.N, self.B, 104))
        bad = good[:start]+good[start+len(restore):]
        with self.assertRaisesRegex(ValueError, "X caller endpoint"):
            self.accepted(bad)

    def test_wrong_pivot_scatter_coefficient(self):
        ops = M["fused"](self.J, self.N, self.B)
        target = next(i for i, op in enumerate(ops) if op[0] == "add" and op[1] >= 104)
        ops[target][3] *= -1
        with self.assertRaisesRegex(ValueError, "Y caller endpoint"):
            self.accepted(ops)

    def test_illegal_early_descent(self):
        ops = M["fused"](self.J, self.N, self.B, True)
        first_read = next(i for i, op in enumerate(ops) if op == ["add", 0, 104, -1])
        ops.insert(first_read, ["drop", 104])
        with self.assertRaisesRegex(ValueError, "source frame"):
            self.accepted(ops, True)

    def test_reader_sign_and_missing_swap(self):
        ops = M["fused"](self.J, self.N, self.B, True)
        i = next(i for i, op in enumerate(ops) if op == ["add", 0, 104, -1])
        ops[i][3] = 1
        with self.assertRaisesRegex(ValueError, "X caller endpoint"):
            self.accepted(ops, True)
        old = M["role_tail"](self.J, self.N, self.B)
        adapter = M["return_adapter"](self.J, self.N, self.B)
        index = next(i for i, op in enumerate(adapter) if op == ["add", self.N[0], 104+self.N[0], -1])
        del adapter[index]
        with self.assertRaisesRegex(ValueError, "caller endpoint"):
            self.accepted(old+adapter)

    def test_dirty_bank_is_not_clean_workspace(self):
        state, frames, _ = M["replay"](self.A, M["fused"](self.J, self.N, self.B), self.final)
        state[208] = {}
        with self.assertRaisesRegex(ValueError, "dirty helper return"):
            M["endpoint"](state, frames, self.final)
        ops = [["half", 208]]
        with self.assertRaisesRegex(ValueError, "public arithmetic target"):
            M["replay"](self.A, ops, self.final)

    def test_residual_relabelling_does_not_supply_inverse_shear(self):
        # Even grant free logical gathering to residual-bank order (q,v_N).
        x = [int(i == self.N[0]) for i in range(104)]
        y = [0]*104
        q = [x[j]+sum(self.B[b][a]*x[i] for a, i in enumerate(self.N))
             for b, j in enumerate(self.J)]
        v = [sum(self.A[i][j]*x[j] for j in range(104)) for i in range(104)]
        residual = v[:]
        for b, j in enumerate(self.J):
            residual[j] = q[b]
        naive = [residual[i]-x[i]-y[i] for i in range(104)]
        self.assertNotEqual(naive, [-v for v in y])
        self.assertTrue(any(naive[j] for j in self.J))

    def test_adapter_tariff_is_counted(self):
        role = M["role_tail"](self.J, self.N, self.B)
        complete = self.accepted(role+M["return_adapter"](self.J, self.N, self.B))
        self.assertEqual(complete["added_H1"], 400)
        self.assertNotEqual(complete["added_H1"], 208)
        reader = self.accepted(M["fused"](self.J, self.N, self.B, True), True)
        self.assertEqual(reader["operation_counts"],
                         {"add":1736,"double":200,"drop":104,"half":200,"lift":104})

    def export(self, root):
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in M["load"](HERE / "VERIFY.json")["inputs"]:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        return package

    def cli(self, package, expect=True, script="verify.py"):
        command = [sys.executable, "-I", "-O", "-B", str(package/script)]
        result = subprocess.run(command, cwd=package.parents[1], capture_output=True,
                                text=True, timeout=90, env={**os.environ, "PYTHONDONTWRITEBYTECODE":"1"})
        self.assertEqual(result.returncode == 0, expect, result.stdout+result.stderr)
        return result

    def test_real_git_free_read_only_replays_and_cli_rejections(self):
        with tempfile.TemporaryDirectory(prefix="p104-caller-controls-") as temporary:
            root = Path(temporary)
            package = self.export(root)
            before = {p.relative_to(root):p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.cli(package)
            self.cli(package, script="independent.py")
            after = {p.relative_to(root):p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            source = root / "research/p104-native-channel/inputs/P104-FIXTURE.json"
            original = source.read_bytes()
            source.write_bytes(original+b" ")
            self.cli(package, False)
            source.write_bytes(original)
            source.rename(source.with_suffix(".missing"))
            self.cli(package, False)
            source.with_suffix(".missing").rename(source)
            result_path = package / "RESULT.json"
            original_result = result_path.read_bytes()
            receipt = json.loads(original_result)
            receipt["physical_or_all_size_supplier_admitted"] = 0
            result_path.write_text(json.dumps(receipt))
            self.cli(package, False)
            result_path.write_bytes(original_result)
            program_path = package / "PROGRAMS.json.gz"
            original_program = program_path.read_bytes()
            programs = json.loads(gzip.decompress(original_program))
            programs["fused_return_and_reader"][0][1] = 105
            program_path.write_bytes(gzip.compress(json.dumps(programs).encode(), mtime=0))
            self.cli(package, False)
            program_path.write_bytes(original_program)
            self.cli(package)


if __name__ == "__main__":
    unittest.main(verbosity=2)
