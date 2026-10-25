"""Behavioral controls for the actual finite-hosting and source boundaries."""

import copy
import itertools
import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan, cls.spec = v.sources()
        cls.model = v.source_model(cls.plan, cls.spec)
        cls.cert = v.read_json(v.HERE / "CERTIFICATE.json")
        cls.rows = v.expand(cls.cert["profiles"]["old"], cls.model)

    def test_small_colour_domains(self):
        checked = 0
        for n in range(1, 4):
            for counts in ((1, 1), (2, 1), (1, 2)):
                for flat in itertools.product(range(n + 1), repeat=6):
                    rows = [flat[2 * t : 2 * t + 2] for t in range(3)]
                    if any(sum(row) > n for row in rows):
                        continue
                    if any(
                        sum(row[k] for row in rows) != n * counts[k] for k in range(2)
                    ):
                        continue
                    demands = {t: [*row, 0, 0, 0] for t, row in enumerate(rows)}
                    bins = v.colour_pattern(demands, [*counts, 0, 0, 0], n)
                    self.assertEqual(len(bins), n)
                    actual = Counter((t, k) for values in bins for t, k in values)
                    self.assertEqual(
                        actual,
                        Counter(
                            {(t, k): rows[t][k] for t in range(3) for k in range(2)}
                        ),
                    )
                    for values in bins:
                        self.assertEqual(len({t for t, _ in values}), sum(counts))
                        self.assertEqual(
                            Counter(k for _, k in values), dict(enumerate(counts))
                        )
                    checked += 1
        self.assertGreater(checked, 100)
        print("tiny feasible pattern systems", checked)

    def test_matching_oracle(self):
        checked = 0
        for flat in itertools.product(range(3), repeat=9):
            matrix = [flat[3 * i : 3 * i + 3] for i in range(3)]
            degree = sum(matrix[0])
            if degree == 0 or any(sum(row) != degree for row in matrix):
                continue
            if any(sum(row[j] for row in matrix) != degree for j in range(3)):
                continue
            possible = [
                p
                for p in itertools.permutations(range(3))
                if all(matrix[i][p[i]] > 0 for i in range(3))
            ]
            self.assertTrue(possible)
            self.assertIn(tuple(v.perfect_matching(matrix)), possible)
            checked += 1
        with self.assertRaises(ValueError):
            v.perfect_matching([[1, 0], [1, 0]])
        print("tiny regular multigraphs", checked)

    def test_flow_rejections(self):
        for mutation in (
            "duplicate",
            "missing",
            "boolean",
            "degree",
            "window",
            "profile",
        ):
            cert = copy.deepcopy(self.cert["profiles"]["old"])
            if mutation == "duplicate":
                cert["flow"].append(cert["flow"][0])
            elif mutation == "missing":
                cert["flow"].pop()
            elif mutation == "boolean":
                cert["flow"][0][3] = True
            elif mutation == "degree":
                row = cert["flow"][0]
                row[3] = cert["allocation"][row[0]][2] + 1
            elif mutation == "window":
                row = cert["flow"][0]
                group = cert["allocation"][row[0]][0]
                row[1] = next(
                    t for t in range(144) if t not in self.model.groups[group].times
                )
            else:
                cert["patterns"][0][1][3] = 2
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                v.check_certificate(cert, self.model, v.EXPECTED["old"])

    def test_literal_rejections(self):
        for mutation in ("family", "width", "overlap", "missing", "duplicate", "time"):
            rows = list(self.rows)
            row = list(rows[1])
            if mutation == "family":
                row[2:5] = rows[0][2:5]
                row[5] = rows[0][6]
            elif mutation == "width":
                row[6] += 1
            elif mutation == "overlap":
                row[5] += 1
            elif mutation == "missing":
                rows.pop()
            elif mutation == "duplicate":
                rows[1] = rows[0]
            else:
                row[0] = 143
            if mutation not in ("missing", "duplicate"):
                rows[1] = tuple(row)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                v.check_rows(rows, self.model)

    def test_geometry_rejections(self):
        for field in ("pairs", "sides"):
            plan = copy.deepcopy(self.plan)
            plan[field] = {k: 0 for k in plan[field]}
            with self.subTest(field=field), self.assertRaises(ValueError):
                v.check_geometry(v.source_model(plan, self.spec))

    def test_optimized_cli_and_source_bytes(self):
        with tempfile.TemporaryDirectory(prefix="t16-controls-") as temporary:
            temp = Path(temporary)
            cert = copy.deepcopy(self.cert)
            cert["profiles"]["old"]["flow"][0][3] = True
            bad = temp / "bad.json"
            bad.write_text(json.dumps(cert))
            self.run_rejected(["--certificate", str(bad)])
            pins = v.read_json(v.HERE / "SOURCES.json")
            for pin in pins["files"]:
                if pin["usage"] == "input":
                    p = temp / pin["path"]
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes((v.ROOT / pin["path"]).read_bytes())
            target = temp / (v.PREFIX + "PLAN.json")
            target.write_bytes(target.read_bytes() + b" ")
            self.run_rejected(["--root", str(temp)])
            target.unlink()
            target.symlink_to(v.ROOT / (v.PREFIX + "PLAN.json"))
            self.run_rejected(["--root", str(temp)])
            duplicate = temp / "duplicate.json"
            duplicate.write_text('{"schema_version":1,"schema_version":1}')
            with self.assertRaises(ValueError):
                v.read_json(duplicate)

    def run_rejected(self, args):
        env = dict(os.environ)
        env["PYTHONPYCACHEPREFIX"] = str(
            Path(tempfile.gettempdir()) / "unused-private-pycache"
        )
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(v.HERE / "verify.py"),
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("PASS_T16", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
