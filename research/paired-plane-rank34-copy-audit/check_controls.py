#!/usr/bin/env python3
"""Failure-sensitive controls and a separate coordinate-vector reconstruction."""
import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rank34_subject", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def vector(value):
    return [(value >> i) & 1 for i in range(9)]


def inner(left, right):
    return sum(a * b for a, b in zip(left, right)) % 2


def dense_rank(matrix):
    rows = [list(row) for row in matrix]
    count = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(count, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        for i in range(count + 1, len(rows)):
            if rows[i][col]:
                rows[i] = [(a + b) % 2 for a, b in zip(rows[i], rows[count])]
        count += 1
    return count


class ScientificControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        V.check_sources()
        cls.labels = V.load_labels()
        cls.cert = json.loads((HERE / "PR3335-CERTIFICATE.json").read_text())
        cls.planes, cls.owner, cls.orth = V.plane_model(cls.labels, cls.cert["pairs"])
        cls.matrix = V.fitting_matrix(cls.cert["supports"], 112)

    def test_separate_coordinate_model(self):
        planes = [[vector(self.labels[i]) for i in p] for p in self.cert["pairs"]]
        # Enumerate all three nonzero vectors of each plane, rather than just
        # reusing the four packed basis pairings from the primary checker.
        spans = [[a, b, [(x + y) % 2 for x, y in zip(a, b)]] for a, b in planes]
        orth = [[all(inner(x, y) == 0 for x in a for y in b) for b in spans] for a in spans]
        self.assertEqual(orth, self.orth)
        invoice = 0
        for support in self.cert["supports"]:
            complete = [v for i in support for v in planes[self.owner[i]]]
            rank = dense_rank([[inner(a, b) for b in complete] for a in complete])
            self.assertEqual(rank, 2 * len(support))
            invoice += rank
        self.assertEqual(invoice, 224)

    def test_all_binary_three_by_three_ranks(self):
        for encoding in range(512):
            rows = [(encoding >> (3 * i)) & 7 for i in range(3)]
            self.assertEqual(len(V.binary_basis(rows)),
                             dense_rank([[(r >> j) & 1 for j in range(3)] for r in rows]))

    def test_identity_baseline_and_support_splitting(self):
        singleton = V.channel_invoice(self.labels, self.cert["pairs"], [[i] for i in range(112)])
        self.assertEqual(sum(c["copy_rank"] for c in singleton), 224)
        supports = copy.deepcopy(self.cert["supports"])
        support = supports.pop()
        supports.extend([[i] for i in support])
        split = V.channel_invoice(self.labels, self.cert["pairs"], supports)
        self.assertGreater(len(split), 34)
        self.assertEqual(sum(c["copy_rank"] for c in split), 224)

    def test_same_plane_cross_entry_is_forbidden(self):
        i, j = self.cert["pairs"][0]
        self.assertEqual(V.dot(self.labels[i], self.labels[j]), 0)
        bad = copy.deepcopy(self.matrix)
        bad[i][j] = 1  # This passes a singleton-label zero mask.
        with self.assertRaisesRegex(V.CheckFailure, "strict mask entry"):
            V.check_mask(bad, self.owner, self.orth)

    def test_old_binary_gram_is_not_the_new_fit(self):
        gram = [[V.dot(a, b) for b in self.labels] for a in self.labels]
        with self.assertRaisesRegex(V.CheckFailure, "strict mask entry"):
            V.check_mask(gram, self.owner, self.orth)

    def test_missing_diagonal(self):
        bad = copy.deepcopy(self.matrix)
        bad[0][0] = 0
        with self.assertRaisesRegex(V.CheckFailure, "strict mask entry"):
            V.check_mask(bad, self.owner, self.orth)

    def test_duplicate_port_or_omitted_support(self):
        bad = copy.deepcopy(self.cert)
        bad["pairs"][0][0] = bad["pairs"][1][0]
        with self.assertRaisesRegex(V.CheckFailure, "perfect matching"):
            V.evaluate(self.labels, bad)
        bad = copy.deepcopy(self.cert)
        bad["supports"].pop()
        with self.assertRaisesRegex(V.CheckFailure, "support partition"):
            V.evaluate(self.labels, bad)

    def test_nonorthonormal_rematch(self):
        bad = copy.deepcopy(self.cert)
        found = False
        for p, (a, b) in enumerate(bad["pairs"]):
            for q in range(p + 1, 56):
                c, d = bad["pairs"][q]
                if V.dot(self.labels[a], self.labels[c]):
                    bad["pairs"][p], bad["pairs"][q] = [a, c], [b, d]
                    found = True
                    break
            if found:
                break
        self.assertTrue(found)
        with self.assertRaisesRegex(V.CheckFailure, "Gram-I2"):
            V.evaluate(self.labels, bad)

    def test_false_lower_witness(self):
        bad = copy.deepcopy(self.cert)
        first = bad["clique_planes"][0]
        other = next(j for j in range(56) if self.orth[first][j])
        bad["clique_planes"][1] = other
        with self.assertRaises(V.CheckFailure):
            V.evaluate(self.labels, bad)

    def test_channel_count_and_singleton_invoice_are_not_copy_cost(self):
        channels = V.channel_invoice(self.labels, self.cert["pairs"], self.cert["supports"])
        V.require_invoice(channels, 224)
        for claimed in (34, 112):
            with self.assertRaisesRegex(V.CheckFailure, "copy invoice"):
                V.require_invoice(channels, claimed)

    def test_asymmetric_free_entries_remain_allowed(self):
        i, j = next((i, j) for i in range(112) for j in range(112)
                    if self.orth[self.owner[i]][self.owner[j]])
        changed = copy.deepcopy(self.matrix)
        changed[i][j], changed[j][i] = 17, -3
        self.assertEqual(V.check_mask(changed, self.owner, self.orth), 11440)

    def test_rational_half_weights_preserve_the_fit_and_cost(self):
        result = V.half_weight_fixture(self.labels, self.cert["pairs"], self.cert["supports"])
        self.assertEqual(result, {"plane_groups": 17, "terms": 34, "copy_rank_mass": 224})

    def test_signed_asymmetric_free_cancellation(self):
        factors = [(1, {i: 1}, {i: 1}) for i in range(112)]
        i, j = next((i, j) for i in range(112) for j in range(112)
                    if self.orth[self.owner[i]][self.owner[j]])
        factors.extend([(Fraction(1, 3), {i: 2}, {j: 1}),
                        (-Fraction(1, 3), {i: 2}, {j: 1})])
        cost, matrix = V.orthogonal_local_factor_check(self.labels, self.cert["pairs"], factors)
        self.assertEqual(cost, 224)  # The two cross terms have zero pairing rank.
        self.assertEqual(matrix, [[int(i == j) for j in range(112)] for i in range(112)])

    def test_nonorthogonal_term_is_outside_the_floor_hypothesis(self):
        factors = [(1, {i: 1}, {i: 1}) for i in range(112)]
        i, j = next((i, j) for i in range(112) for j in range(112)
                    if self.owner[i] != self.owner[j] and not self.orth[self.owner[i]][self.owner[j]])
        # Cancelling terms leave the scalar fit unchanged; the checker rejects
        # only their declared support class, not the possibility of such fits.
        factors.extend([(1, {i: 1}, {j: 1}), (-1, {i: 1}, {j: 1})])
        with self.assertRaisesRegex(V.CheckFailure, "mutually orthogonal"):
            V.orthogonal_local_factor_check(self.labels, self.cert["pairs"], factors)

    def test_source_bytes_authenticated(self):
        row = json.loads((HERE / "VENDOR.json").read_text())["files"][0]
        raw = (HERE / row["local_file"]).read_bytes()
        V.authenticate(raw, row)
        with self.assertRaisesRegex(V.CheckFailure, "SHA256"):
            V.authenticate(raw + b" ", row)
        wrong = dict(row, git_blob="0" * 40)
        with self.assertRaisesRegex(V.CheckFailure, "Git blob"):
            V.authenticate(raw, wrong)


class ExportControls(unittest.TestCase):
    def test_git_free_read_only_replay_and_failures(self):
        with tempfile.TemporaryDirectory(prefix="rank34-export-") as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            sources = json.loads((HERE / "SOURCES.json").read_text())
            for row in sources["files"]:
                if row["usage"] == "input":
                    target = root / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(V.ROOT / row["path"], target)
            paths = [p for p in root.rglob("*") if p.is_file()]
            before = {p.relative_to(root): V.digest(p.read_bytes()) for p in paths}
            # POSIX permissions supplement the byte inventory. The replay makes
            # no network requests and has no Git repo or predecessor branch.
            for path in paths:
                path.chmod(0o444)
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            env = dict(os.environ, PYTHONPYCACHEPREFIX=str(root / "unused-bytecode"))
            run = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30, env=env)
            self.assertEqual(run.returncode, 0, run.stderr)
            after = {p.relative_to(root): V.digest(p.read_bytes()) for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            receipt = package / "RESULT.json"
            receipt.chmod(0o644)
            original = receipt.read_text()
            data = json.loads(original)
            data["complete_plane_copy_invoice"] = "224"  # A JSON type mutation.
            receipt.write_text(json.dumps(data))
            run = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30, env=env)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("exact recomputed receipt", run.stderr)
            receipt.write_text(original)
            run = subprocess.run(command + ["--output", str(receipt)], cwd=root,
                                 capture_output=True, text=True, timeout=30, env=env)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(receipt.read_text(), original)
            fixture = package / "PR3335-CERTIFICATE.json"
            fixture.chmod(0o644)
            fixture.write_bytes(fixture.read_bytes() + b" ")
            run = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30, env=env)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source SHA256", run.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
