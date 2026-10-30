"""Behavioral controls for source rejection and the first-visit transport lemma."""

import hashlib
import importlib.util
import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("transport_cut", HERE / "verify.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TransportTests(unittest.TestCase):
    def test_arbitrary_return_histories(self):
        keys = [(i, 0, 0) for i in range(3)]
        trials = 0
        for masks in itertools.product(range(1, 4), repeat=2):
            for windows in itertools.product(range(4), repeat=3):
                eligible = {(i, 0): windows[i] for i in range(3)}
                bound, _ = module.closure(
                    keys[1:],
                    dict(zip(keys[1:], masks, strict=True)),
                    eligible,
                    {keys[0]},
                )
                pending = deque([(0, 1, 2)])
                visited = {(0, 1, 2)}
                for _step in range(6):
                    if not pending:
                        break
                    state = pending.popleft()
                    empty = state.index(0)
                    self.assertIn(keys[empty], bound)
                    for source in range(3):
                        bundle = state[source]
                        if bundle and not masks[bundle - 1] & ~windows[empty]:
                            changed = list(state)
                            changed[empty], changed[source] = bundle, 0
                            target = tuple(changed)
                            if target not in visited:
                                visited.add(target)
                                pending.append(target)
                self.assertFalse(pending, "all six bundle permutations exhausted")
                trials += 1
        self.assertEqual(trials, 576)

    def test_two_round_chain_and_partial_bundle(self):
        keys = [(i, 0, 0) for i in range(3)]
        # The first source contains only one role, not a full-capacity bundle.
        reached, rounds = module.closure(
            keys[1:],
            {keys[1]: 1, keys[2]: 2},
            {(0, 0): 1, (1, 0): 3, (2, 0): 2},
            {keys[0]},
        )
        self.assertEqual(reached, set(keys))
        self.assertEqual(rounds, [1, 1, 0])

    def test_width_bound_detects_escape(self):
        rows = [
            {"time": 0, "width": 9},
            {"time": 1, "width": 7},
            {"time": 2, "width": 32},
        ]
        bundles = {(0, 8, 0): [0, 1, 2]}
        before, _ = module.available_widths(rows, bundles, {1})
        after, _ = module.available_widths(rows, bundles, {3})
        self.assertEqual(before, {9: 1})
        self.assertEqual(after, {16: 1})

    def rejected_copy(self, mutation, expected):
        with tempfile.TemporaryDirectory(prefix="transport-control-") as directory:
            copied = Path(directory) / "package"
            shutil.copytree(HERE, copied)
            mutation(copied)
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            command = [
                sys.executable,
                "-I",
                "-Werror",
                "-B",
                str(copied / "verify.py"),
                "--package",
                str(copied),
                "--root",
                str(ROOT),
            ]
            result = subprocess.run(
                command,
                check=False,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected, result.stderr)

    def test_reject_changed_fixture(self):
        def mutate(package):
            with (package / "OWNERS.json.gz").open("ab") as stream:
                stream.write(b"changed")

        self.rejected_copy(mutate, "changed fixture: OWNERS.json.gz")

    def test_reject_changed_retained_code(self):
        def mutate(package):
            with (package / "source3388/verify.py").open("a") as stream:
                stream.write("\n# changed\n")

        self.rejected_copy(mutate, "changed retained source: source3388/verify.py")

    def test_reject_changed_result(self):
        def mutate(package):
            path = package / "RESULT.json"
            value = json.loads(path.read_text())
            value["maximum_available_width"] = 16
            path.write_text(json.dumps(value))

        self.rejected_copy(mutate, "committed result differs")

    def test_reject_repinned_order(self):
        def mutate(package):
            path = package / "PLAN.json"
            value = json.loads(path.read_text())
            value["order"][0], value["order"][2] = value["order"][2], value["order"][0]
            path.write_text(json.dumps(value))
            manifest = package / "RETAINED.json"
            value = json.loads(manifest.read_text())
            value["fixtures"]["PLAN.json"] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            manifest.write_text(json.dumps(value))

        self.rejected_copy(mutate, "retained chronology fixture")

    def test_reject_missing_live_source(self):
        def mutate(package):
            path = package / "SOURCES.json"
            value = json.loads(path.read_text())
            value["files"][2]["path"] = "research/missing-input.json"
            path.write_text(json.dumps(value))

        self.rejected_copy(mutate, "live source byte limit")


if __name__ == "__main__":
    unittest.main(verbosity=2)
