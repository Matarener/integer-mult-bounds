#!/usr/bin/env python3
"""Source-bound independent B SAT replay with checked binary DRAT certificates."""

import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("occupancy_model", HERE / "model.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
MAX_PROOF = 256 * 1024 * 1024


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for _ in range(257):
            chunk = stream.read(1024 * 1024)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)
    raise ValueError("file digest byte budget exhausted")


def sources():
    rows = json.loads((HERE / "SOURCES.json").read_text())["files"]
    M.need(isinstance(rows, list) and len(rows) <= 32, "source inventory bound")
    for row in rows:
        if row["usage"] == "input":
            path = (ROOT / row["path"]).resolve()
            M.need(
                path.is_relative_to(ROOT) and path.is_file(), "contained source file"
            )
            M.need(
                sha(ROOT / row["path"]) == row["sha256"],
                "changed source " + row["path"],
            )
    vendor = json.loads((HERE / "vendor/SOURCE.json").read_text())
    M.need(set(vendor["sha256"]) == {"drat-trim.c", "LICENSE"}, "vendor inventory")
    for name, expected in vendor["sha256"].items():
        M.need(sha(HERE / "vendor" / name) == expected, "changed DRAT checker " + name)
    return vendor


def dimacs(formula, path):
    M.need(len(formula.variables) <= M.MAX_VARIABLES, "DIMACS variable limit")
    with path.open("w") as stream:
        stream.write(f"p cnf {len(formula.variables)} {len(formula.clauses)}\n")
        for clause in formula.clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")
    M.need(path.stat().st_size <= 16 * 1024 * 1024, "DIMACS byte limit")


def native_flush():
    flush = ctypes.CDLL(None).fflush
    flush.argtypes = [ctypes.c_void_p]
    flush.restype = ctypes.c_int
    M.need(flush(None) == 0, "native proof flush failed")


def binary_proof(solver, path):
    # The pinned Cadical195 adapter exposes its binary trace as prfile.
    # Stream that exact trace instead of expanding it into a large Python list.
    M.need(solver.prfile is not None, "proof tracing is required")
    # Native proof output has its own C buffer. Finalize the solver before
    # reading the duplicated file descriptor, so the last clause is present.
    native_flush()
    descriptor = os.dup(solver.prfile.fileno())
    with os.fdopen(descriptor, "rb") as stream:
        solver.delete()
        stream.seek(0, 2)
        M.need(0 < stream.tell() <= MAX_PROOF, "binary proof byte limit")
        stream.seek(0)
        with path.open("wb") as output:
            for _ in range(257):
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    return
                output.write(chunk)
    raise ValueError("proof copy byte limit")


def solve_one(identifier, directory, budget=300_000):
    import pysat
    from pysat.solvers import Cadical195

    M.need(pysat.__version__ == "1.8.dev24", "python-sat must be 1.8.dev24")
    low = M.templates()[identifier - 1]
    formula = M.build(low)
    cnf, proof = directory / "input.cnf", directory / "proof.drat"
    dimacs(formula, cnf)
    with Cadical195(bootstrap_with=formula.clauses, with_proof=True) as solver:
        solver.conf_budget(budget)
        result = solver.solve_limited()
        if result is not False:
            native_flush()
            if result is True:
                word = M.word_from(formula, low, solver.get_model())
                M.check_word(word, (4, 4, 4), True)
            raise ValueError(
                "SAT witness or incomplete solver result is not an exclusion"
            )
        binary_proof(solver, proof)
    return {
        "template": identifier,
        "low": low,
        "status": "UNSAT",
        "variables": len(formula.variables),
        "clauses": len(formula.clauses),
        "cnf_sha256": sha(cnf),
        "proof_sha256": sha(proof),
        "proof_bytes": proof.stat().st_size,
    }


def compile_checker(directory):
    compiler = shutil.which(os.environ.get("CC", "cc"))
    M.need(compiler is not None, "an installed C99 compiler is required")
    binary = directory / "drat-trim"
    command = [
        compiler,
        "-O2",
        "-std=c99",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        str(HERE / "vendor/drat-trim.c"),
        "-o",
        str(binary),
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=60, check=False
    )
    (directory / "compiler.log").write_text(result.stdout + result.stderr)
    M.need(result.returncode == 0, "DRAT checker compilation failed")
    return binary


def check_proof(binary, cnf, proof, log, expect=True):
    result = subprocess.run(
        [str(binary), str(cnf), str(proof), "-t", "60"],
        capture_output=True,
        text=True,
        timeout=75,
        check=False,
    )
    log.write_text(result.stdout + result.stderr)
    accepted = result.returncode == 0 and "s VERIFIED" in result.stdout
    M.need(
        accepted is expect,
        "DRAT verification outcome differs from expectation: "
        + result.stdout[-1500:]
        + result.stderr[-500:],
    )
    return accepted


def checker_controls(binary, directory):
    cnf, proof = directory / "control.cnf", directory / "control.drat"
    cnf.write_text("p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n")
    proof.write_text("1 0\n0\n")
    check_proof(binary, cnf, proof, directory / "valid-control.log")
    for name, text in (("empty", ""), ("forged", "2 1 0\n0\n")):
        proof.write_text(text)
        check_proof(binary, cnf, proof, directory / (name + "-control.log"), False)
    return 3


def replay(identifiers, directory, controls):
    sources()
    binary = compile_checker(directory)
    if controls:
        checker_controls(binary, directory)
    results = []
    for identifier in identifiers:
        case = directory / f"B{identifier:02}"
        case.mkdir()
        command = [
            sys.executable,
            "-I",
            "-B",
            str(HERE / "verify.py"),
            "--solve-one",
            str(identifier),
            "--work",
            str(case),
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=90, check=False
        )
        (case / "solver.log").write_text(result.stdout + result.stderr)
        M.need(
            result.returncode == 0, "solver failed/incomplete for B" + str(identifier)
        )
        row = json.loads(result.stdout)
        M.need(
            row["template"] == identifier and row["status"] == "UNSAT", "child status"
        )
        M.need(sha(case / "input.cnf") == row["cnf_sha256"], "child CNF binding")
        M.need(sha(case / "proof.drat") == row["proof_sha256"], "child proof binding")
        check_proof(binary, case / "input.cnf", case / "proof.drat", case / "check.log")
        row["proof_checked"] = True
        results.append(row)
        print("VERIFIED_B", identifier, flush=True)
        (case / "proof.drat").unlink()
        (case / "input.cnf").unlink()
    return {
        "status": "PASS_CONNECTOR_B_OCCUPANCY_SAT",
        "cases": results,
        "ordered_high_paths": 112,
        "low_templates": 77,
        "scope": (
            "Only the named simple22 B templates; no full f7 or supplier admission."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solve-one", type=int)
    parser.add_argument("--templates", default="1,2,3,4")
    parser.add_argument("--work", type=Path)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--retain", type=Path)
    parser.add_argument("--controls", action="store_true")
    arguments = parser.parse_args()
    if arguments.solve_one is not None:
        M.need(
            1 <= arguments.solve_one <= 77 and arguments.work is not None,
            "case arguments",
        )
        print(
            json.dumps(solve_one(arguments.solve_one, arguments.work), sort_keys=True)
        )
        return
    identifiers = [int(value) for value in arguments.templates.split(",")]
    M.need(
        identifiers == sorted(set(identifiers))
        and all(1 <= value <= 77 for value in identifiers),
        "ordered distinct template IDs 1..77 required",
    )
    M.need(len(identifiers) <= 77, "case count bound")
    if arguments.retain is not None:
        arguments.retain.mkdir()
        result = replay(identifiers, arguments.retain, arguments.controls)
    else:
        with tempfile.TemporaryDirectory(
            prefix="connector-sat-", dir=arguments.work
        ) as temporary:
            result = replay(identifiers, Path(temporary), arguments.controls)
    if not arguments.emit:
        expected = json.loads((HERE / "RESULT.json").read_text())
        # A checked proof can vary across supported compiler/solver environments.
        for row in result["cases"]:
            row.pop("proof_sha256")
            row.pop("proof_bytes")
        M.need(result == expected, "source-bound result receipt differs")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
