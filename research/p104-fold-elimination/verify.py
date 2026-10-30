"""Check canonical solutions and complete accepted fold-variant equivalence."""

import gzip
import hashlib
import itertools
import json
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

import numpy as np

from runtime import PACKAGE, authenticate, install
from solver import P, solve

EXPECTED_WORD = "6a3d8a88b41cec6d2e6d5a1315b16448478a32c60157c0f036d89b65e702f13b"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def extract(root):
    manifest = json.loads((PACKAGE / "RETAINED.json").read_text())
    archive = PACKAGE / "toolkit-closure.tar.gz"
    require(hashlib.sha256(archive.read_bytes()).hexdigest()
            == manifest["archive_sha256"], "changed source archive")
    with tarfile.open(archive) as source:
        members = source.getmembers()
        require(len(members) == len(manifest["files"]), "archive member count")
        expected = {record["path"] for record in manifest["files"]}
        require({member.name for member in members} == expected, "archive names")
        for member in members:
            require(member.isfile() and not member.name.startswith("/")
                    and ".." not in member.name.split("/"), "unsafe member")
        source.extractall(root, filter="data")
    return authenticate(root)


def check_system(original, matrix, rhs):
    before_matrix, before_rhs = matrix.copy(), rhs.copy()
    expected = original(matrix, rhs)
    actual = solve(matrix, rhs)
    require((actual is None) == (expected is None), "consistency disagreement")
    if actual is not None:
        require(np.array_equal(actual, expected), "canonical solution disagreement")
        residual = ((matrix % P) * actual[None, :]) % P
        require(np.array_equal(residual.sum(axis=1) % P, rhs % P), "bad solution")
    require(np.array_equal(before_matrix, matrix) and np.array_equal(before_rhs, rhs),
            "input mutation")


def integer_formats(original):
    for dtype in (np.int8, np.int64, np.uint64):
        for bound in (np.iinfo(dtype).min, np.iinfo(dtype).max):
            matrix = np.array([[bound, 1], [1, 0]], dtype=dtype)
            rhs = np.array([1, 2], dtype=dtype)
            normalized = np.array([[int(value) % P for value in row]
                                   for row in matrix], dtype=np.int64)
            require(np.array_equal(solve(matrix, rhs),
                                   original(normalized, rhs.astype(np.int64))),
                    "integer format boundary disagreement")
    return 6


def controls(root):
    original = install(root, "baseline").solve
    count = integer_formats(original)
    for bits in itertools.product(range(2), repeat=8):
        matrix = np.array(bits[:6], dtype=np.int64).reshape(2, 3)
        check_system(original, matrix, np.array(bits[6:], dtype=np.int64))
        count += 1
    random = np.random.default_rng(20261029)
    for rows in range(9):
        for columns in range(9):
            for trial in range(12):
                matrix = random.integers(0, P, (rows, columns), dtype=np.int64)
                if trial % 3 == 0:
                    matrix %= 3
                if trial % 4 == 0 and columns > 1:
                    matrix[:, columns - 1] = matrix[:, 0]
                rhs = random.integers(0, P, rows, dtype=np.int64)
                if trial % 2 == 0:
                    weights = random.integers(0, 100, columns)
                    rhs = (matrix * weights).sum(axis=1) % P
                check_system(original, matrix, rhs)
                count += 1
    invalid = [(np.zeros(2, dtype=np.int64), np.zeros(2, dtype=np.int64)),
               (np.zeros((2, 2), dtype=np.int64), np.zeros(1, dtype=np.int64)),
               (np.zeros((4097, 0), dtype=np.int64), np.zeros(4097, dtype=np.int64)),
               (np.zeros((1, 1), dtype=float), np.zeros(1, dtype=np.int64))]
    for matrix, rhs in invalid:
        try:
            solve(matrix, rhs)
        except ValueError:
            continue
        raise ValueError("invalid solver input accepted")
    changed = root / "alignbuild/rp.py"
    saved = changed.read_bytes()
    changed.write_bytes(saved + b"\n# mutation\n")
    try:
        try:
            authenticate(root)
        except ValueError:
            return count, len(invalid) + 1
        raise ValueError("changed source accepted")
    finally:
        changed.write_bytes(saved)


def integration(root, scratch):
    reports = []
    for mode in ("baseline", "candidate"):
        output = scratch / f"{mode}.json.gz"
        optimize = ["-O"] if sys.flags.optimize else []
        command = [sys.executable, *optimize, "-B", str(PACKAGE / "run.py"), mode,
                   str(root), str(output)]
        started = time.perf_counter()
        result = subprocess.run(command, capture_output=True, text=True, timeout=240)
        elapsed = time.perf_counter() - started
        (scratch / f"{mode}.log").write_text(result.stdout + result.stderr)
        require(result.returncode == 0, "solver command failed")
        require("RESULT: LEGAL " in result.stdout, "variant did not pass source checks")
        word = json.loads(gzip.decompress(output.read_bytes()))
        canonical = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
        require(hashlib.sha256(canonical).hexdigest() == EXPECTED_WORD,
                "complete output word changed")
        reports.append({"mode": mode, "seconds": elapsed,
                        "events": len(word["program"]), "word_sha256": EXPECTED_WORD})
    return reports


def check_benchmark():
    receipt = json.loads((PACKAGE / "BENCHMARK.json").read_text())
    require(receipt["errors"] == 0 and len(receipt["runs"]) >= 10, "benchmark coverage")
    for name, expected in receipt["hashes"].items():
        require(hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() == expected,
                "benchmark implementation changed: " + name)
    for index, run in enumerate(receipt["runs"]):
        require(run["mode"] == ("baseline", "candidate")[index % 2], "run order")
        require(run["word_sha256"] == EXPECTED_WORD and run["exit_code"] == 0
                and run["events"] == 22821, "benchmark output disagreement")


def main():
    check_benchmark()
    with tempfile.TemporaryDirectory(prefix="p104-fold-") as directory:
        scratch = Path(directory)
        root = scratch / "toolkit"
        root.mkdir()
        manifest = extract(root)
        cases, rejections = controls(root)
        runs = integration(root, scratch)
        print(json.dumps({"status": "PASS_P104_FOLD_ELIMINATION",
                          "canonical_systems": cases, "rejection_controls": rejections,
                          "retained_files": len(manifest["files"]), "runs": runs},
                         sort_keys=True))


if __name__ == "__main__":
    main()
