"""Behavioral controls for the scatter boundary decision. Apache-2.0."""

import copy
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = verify.sources(verify.ROOT)
        cls.word = verify.load_word(cls.data[verify.WORD])
        cls.archived = json.loads(cls.data[verify.ARCHIVED])

    def test_multipicity_census_and_guard(self):
        self.assertEqual(verify.census(self.word)["max_multiplicity"], 1)
        self.assertTrue(verify.simple_support(self.word["scatter"]))
        synthetic = {"v": 2, "scatter": [[0, 0], [1]]}
        census = verify.census(synthetic)
        self.assertEqual((census["rows_with_repeats"], census["max_multiplicity"]), (1, 2))
        for row in ([4, 4], [4, 4, 4], [True], [-1], [9], [1.0], ["1"], list(range(10))):
            self.assertFalse(verify.simple_support([row]), row)
        for row in ([], [0], [0, 1, 2, 8]):
            self.assertTrue(verify.simple_support([row]), row)

    def test_exact_condition_table(self):
        for m in range(7):
            rows = [[4, 5] + [0] * m]
            self.assertEqual(verify.multiplicity_agrees(rows), m == 0 or m % 2 == 1, m)
        self.assertTrue(verify.multiplicity_agrees(self.word["scatter"]))
        pair = copy.deepcopy(self.word["scatter"])
        pair[0] = pair[0] + [0, 0]
        self.assertFalse(verify.multiplicity_agrees(pair))

    def test_pair_mutant_reproduction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checker = verify.deploy(self.data[verify.CHECKER], root, "xcheck_p.py")
            exporter = verify.deploy(self.data[verify.EXPORTER], root, "export_records.py")
            mutant = copy.deepcopy(self.word)
            mutant["scatter"][0] = mutant["scatter"][0] + [0, 0]
            verdict = verify.run_checker(checker, mutant, root, "pair")
            self.assertEqual(verdict["verdict"], "accept")
            records = verify.run_export(exporter, mutant, root, "pair")
            self.assertEqual(len(records) // verify.RECORD.size, self.archived["mutant"]["records"])
            differences = verify.interpret(records, mutant)
            self.assertEqual(len(differences), 1)
            register, mask = differences[0]
            self.assertEqual(register, self.word["v"])
            support = [i for i in range(verify.COLUMNS) if mask >> i & 1]
            self.assertEqual(support, self.archived["mutant"]["witness"]["difference_support"])
            self.assertTrue(mask >> 472 & 1)

    def test_checker_rejects_odd_occurrence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checker = verify.deploy(self.data[verify.CHECKER], root, "xcheck_p.py")
            mutant = copy.deepcopy(self.word)
            mutant["scatter"][0].append(0)
            verdict = verify.run_checker(checker, mutant, root, "single")
            self.assertEqual(verdict["verdict"], "reject")
            self.assertIn("targets not y + x: [0]", verdict["message"])

    def test_interpreter_lifecycle(self):
        word = {"v": 111, "R": 439, "ret": [0] * 9}
        n = 661
        good = b"".join(verify.RECORD.pack(1, 111 + i, i, 1, 0, 3) for i in range(111))
        self.assertEqual(verify.interpret(good, word), [])
        extra = verify.RECORD.pack(1, 111, 472, 1, 0, 3)
        self.assertEqual(verify.interpret(good + extra, word), [(111, 1 << 472)])
        for raw in (
            verify.RECORD.pack(4, 0, 0, 0, 0, 0),
            verify.RECORD.pack(1, 111, 661, 1, 0, 0),
            verify.RECORD.pack(2, 472, 661, 0, 0, 0) + verify.RECORD.pack(2, 471, 661, 0, 0, 0),
            verify.RECORD.pack(2, 472, 661, 0, 0, 0),
            verify.RECORD.pack(3, 472, 661, 0, 0, 0),
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                verify.interpret(raw, word)
        self.assertEqual(n, 661)

    def test_source_corruption_rejects(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path, body in self.data.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
            self.assertEqual(verify.sources(root), self.data)
            first = sorted(self.data)[0]
            (root / first).write_bytes(self.data[first] + b" ")
            with self.assertRaisesRegex(ValueError, "source:"):
                verify.sources(root)

    def test_tampered_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("verify.py", "SOURCES.json", "RESULT.json"):
                shutil.copyfile(verify.PACKAGE / name, root / name)
            receipt = json.loads((root / "RESULT.json").read_bytes())
            receipt["columns"] = 660
            (root / "RESULT.json").write_text(json.dumps(receipt))
            run = subprocess.run(
                [sys.executable, "-I", "-O", "-B", str(root / "verify.py"), "--root", str(verify.ROOT)],
                check=False, capture_output=True, text=True, timeout=180,
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("typed deterministic receipt", run.stderr)


if __name__ == "__main__":
    unittest.main()
