"""Behavioral oracles, positive fixtures, failure paths and actual CLI mutants."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PRIMARY = load("verify")
SEPARATE = load("independent")


def subset_oracle(groups, n, slots):
    reachable = {(1 << n) - 1}
    for _ in range(slots):
        reachable |= {
            remaining ^ group
            for remaining in reachable
            for group in groups
            if group & remaining == group
        }
    return 0 in reachable


def dense_groups(labels):
    result = []
    for mask in range(1, 1 << len(labels)):
        vertices = [i for i in range(len(labels)) if mask >> i & 1]
        if len(vertices) % 2 == 0 and all(
            (labels[i] & labels[j]).bit_count() % 2 == 0
            for i, j in combinations(vertices, 2)
        ):
            result.append(mask)
    return result


class Controls(unittest.TestCase):
    def test_every_four_port_group_family(self):
        possible = [m for m in range(1, 16) if m.bit_count() % 2 == 0]
        self.assertEqual(len(possible), 7)
        for family in range(1 << len(possible)):
            groups = [g for j, g in enumerate(possible) if family >> j & 1]
            for slots in range(3):
                expected = subset_oracle(groups, 4, slots)
                self.assertEqual(PRIMARY.cover(groups, 4, slots)[0], expected)
                self.assertEqual(SEPARATE.cover_masks(groups, 4, slots)[0], expected)

    def test_complete_small_geometry_oracles(self):
        labels, _, _ = PRIMARY.inputs()
        fixtures = [[1 << i for i in range(n)] for n in (0, 2, 4, 6, 8)]
        fixtures += [labels[start : start + 8] for start in range(0, 40, 5)]
        for fixture in fixtures:
            vectors = [[q >> j & 1 for j in range(9)] for q in fixture]
            expected = dense_groups(fixture)
            groups = PRIMARY.even_groups(fixture)
            self.assertEqual(sorted(groups), expected)
            self.assertEqual(sorted(SEPARATE.group_masks(vectors)), expected)
            for slots in range(5):
                answer = subset_oracle(groups, len(fixture), slots)
                self.assertEqual(PRIMARY.cover(groups, len(fixture), slots)[0], answer)
                self.assertEqual(
                    SEPARATE.cover_masks(groups, len(fixture), slots)[0], answer
                )

    def test_attaining_sixteen_group_partition(self):
        labels, old, upper = PRIMARY.inputs()
        PRIMARY.partition(labels, upper, 16)
        retained = sum(sorted(g) in [sorted(h) for h in old[:13]] for g in upper)
        self.assertEqual(retained, 11)
        changed = [
            v
            for g in upper
            if sorted(g) not in [sorted(h) for h in old[:13]]
            for v in g
        ]
        self.assertEqual(len(changed), 24)
        groups = PRIMARY.even_groups([labels[v] for v in sorted(changed)])
        self.assertTrue(PRIMARY.cover(groups, 24, 5)[0])
        self.assertTrue(SEPARATE.cover_masks(groups, 24, 5)[0])

    def test_budget_exhaustion_is_an_error(self):
        pairs = [sum(1 << i for i in pair) for pair in combinations(range(6), 2)]
        with self.assertRaisesRegex(ValueError, "budget exhausted"):
            PRIMARY.cover(pairs, 6, 3, budget=1)
        with self.assertRaisesRegex(ValueError, "search exhausted"):
            SEPARATE.cover_masks(pairs, 6, 3, budget=1)

    def test_invalid_inputs_and_semantic_mutants(self):
        for labels in ([0], [3], [1, 1], [512], [1] * 33):
            with self.assertRaises(ValueError):
                PRIMARY.even_groups(labels)
        for groups, n, slots in [
            ([1], 2, 1),
            ([3, 3], 2, 1),
            ([16], 4, 1),
            ([], 33, 1),
            ([], 4, -1),
        ]:
            with self.assertRaises(ValueError):
                PRIMARY.cover(groups, n, slots)
            with self.assertRaises(ValueError):
                SEPARATE.cover_masks(groups, n, slots)
        labels, old, upper = PRIMARY.inputs()
        upper[0][0] = upper[0][1]
        with self.assertRaisesRegex(ValueError, "partition"):
            PRIMARY.partition(labels, upper, 16)
        labels[old[0][0]] ^= 1
        with self.assertRaisesRegex(ValueError, "Gram"):
            PRIMARY.partition(labels, old, 17)

    def test_actual_optimized_cli_failures(self):
        with tempfile.TemporaryDirectory(
            prefix="p112-three-frame-controls-"
        ) as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            shutil.copytree(
                HERE,
                package,
                ignore=shutil.ignore_patterns("__pycache__"),
                copy_function=shutil.copyfile,
            )
            # Only this new private directory changes mode. No source links do.
            package.chmod(0o700, follow_symlinks=False)
            source = root / PRIMARY.INPUT
            source.parent.mkdir(parents=True)
            shutil.copyfile(PRIMARY.ROOT / PRIMARY.INPUT, source)
            original = source.read_bytes()
            source.write_bytes(original + b" ")
            self.cli_fails(package / "verify.py", "source SHA256")
            source.write_bytes(original)
            receipt = package / "RESULT.json"
            expected = json.loads(receipt.read_bytes())
            expected["cases"].pop()
            receipt.write_text(json.dumps(expected))
            self.cli_fails(package / "independent.py", "primary case inventory")
            shutil.copyfile(HERE / "RESULT.json", receipt)
            upper = package / "UPPER16.json"
            upper.write_bytes(upper.read_bytes() + b" ")
            self.cli_fails(package / "verify.py", "source SHA256")

    def cli_fails(self, script, message):
        result = subprocess.run(
            [sys.executable, "-I", "-O", "-Werror", "-B", str(script)],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)
        self.assertNotIn("PASS_P112", result.stdout)


if __name__ == "__main__":
    # The invoking session supplies TMPDIR to contain disposable exports.
    if "TMPDIR" in os.environ:
        PRIMARY.need(
            Path(os.environ["TMPDIR"]).is_dir(), "existing session temp directory"
        )
    unittest.main(verbosity=2)
