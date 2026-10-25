#!/usr/bin/env python3
"""Independent rational block identities and destructive private-copy controls.

Apache-2.0. Prepared by ToikY with substantial OpenAI Codex assistance.
This same-session check is not independent human review or native admission.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def plus(left, right, coefficient=1):
    return [a + coefficient*b for a, b in zip(left, right)]


def product(matrix, vectors):
    """Dense row multiplication, unrelated to the production sparse replay."""
    width = len(vectors[0])
    return [[sum(coefficient*vectors[j][k] for j, coefficient in enumerate(row))
             for k in range(width)] for row in matrix]


def generic_identity(matrix):
    """Check both chronological identities on independent encoded coordinates."""
    pivots, nonpivots = len(matrix), len(matrix[0])
    need(all(len(row) == nonpivots for row in matrix), "rectangular B")
    # q, w_J, w_N, v_N, then three independent dirty helper coordinates.
    dimension = 2*pivots + 2*nonpivots + 3
    basis = [[Fraction(i == j) for j in range(dimension)] for i in range(dimension)]
    q = basis[:pivots]
    wj = basis[pivots:2*pivots]
    w = basis[2*pivots:2*pivots+nonpivots]
    v = basis[2*pivots+nonpivots:2*pivots+2*nonpivots]
    helpers = basis[-3:]
    transpose = list(map(list, zip(*matrix)))
    residual = product(transpose, q)
    want_xn = [plus(plus(wi, vi, -1), ri) for wi, vi, ri in zip(w, v, residual)]
    want_xj = [plus(qi, bi, -1) for qi, bi in zip(q, product(matrix, want_xn))]
    wanted = want_xj, wj, want_xn, w, helpers

    # PR3940 block chronology: obtain -x_N, restore q, then three unit shears.
    old_x, old_y = deepcopy(w), deepcopy(v)
    old_y = [plus(yi, xi, -1) for yi, xi in zip(old_y, old_x)]
    old_y = [plus(yi, ri, -1) for yi, ri in zip(old_y, residual)]
    old_q = [plus(qi, bi) for qi, bi in zip(q, product(matrix, old_y))]
    for n in range(nonpivots):
        old_x[n] = plus(old_x[n], old_y[n], -1)
        old_y[n] = plus(old_y[n], old_x[n])
        old_x[n] = plus(old_x[n], old_y[n], -1)
    need((old_q, wj, old_x, old_y, helpers) == wanted, "old arbitrary-B block identity")

    # PR3943 block chronology: obtain y_N, two shears, then restore q.
    new_x, new_y = deepcopy(w), deepcopy(v)
    new_y = [plus(yi, ri, -1) for yi, ri in zip(new_y, residual)]
    for n in range(nonpivots):
        new_x[n] = plus(new_x[n], new_y[n], -1)
        new_y[n] = plus(new_y[n], new_x[n])
    new_q = [plus(qi, bi, -1) for qi, bi in zip(q, product(matrix, new_x))]
    need((new_q, wj, new_x, new_y, helpers) == wanted, "new arbitrary-B block identity")
    need(2*sum(x != 0 for row in matrix for x in row)+4*nonpivots
         - (2*sum(x != 0 for row in matrix for x in row)+2*nonpivots)
         == 2*nonpivots, "generic direct-ADD difference")
    # The same symbolic equality implies equality on these non-basis values.
    values = [Fraction((-1)**i*(i+2), i%5+1) for i in range(dimension)]
    evaluate = lambda rows: [sum(x*v for x, v in zip(row, values)) for row in rows]
    for produced, expected in zip((new_q, wj, new_x, new_y, helpers), wanted):
        need(evaluate(produced) == evaluate(expected), "arbitrary rational payload")


def independent_blocks():
    cases = [
        [[Fraction(1, 2)]],
        [[Fraction(1, 3), 0, Fraction(-2, 7)],
         [Fraction(-5, 4), Fraction(3, 2), Fraction(7, 5)]],
        [[0, Fraction(-1, 3)], [Fraction(2, 5), Fraction(4, 7)],
         [Fraction(-9, 2), Fraction(1, 11)]],
        [[Fraction(-2, 3), Fraction(5, 7), 0, Fraction(7, 2)]],
        [[0, 0], [0, 0]],
    ]
    for matrix in cases:
        generic_identity(matrix)
    return len(cases)


def load_primary():
    spec = importlib.util.spec_from_file_location("return_match_primary", HERE / "verify.py")
    need(spec is not None and spec.loader is not None, "primary import loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rejected(name, action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("mutation survived: " + name)


def behavioral_controls(primary):
    primary.sources()
    matrix, pivots, nonpivots = primary.geometry()
    programs = {which: primary.build_program(which, matrix, pivots, nonpivots)
                for which in ("caller", "consumer")}
    for which, program in programs.items():
        primary.check_program(which, program, matrix, pivots, nonpivots)
    original = programs["consumer"]
    mutations = {}

    first_add = next(i for i, op in enumerate(original) if op[0] == "add")
    changed = original.copy()
    del changed[first_add]
    mutations["missing_add"] = changed

    changed = original.copy()
    kind, target, donor, sign = changed[first_add]
    changed[first_add] = kind, target, donor, -sign
    mutations["wrong_sign"] = changed

    # Reversing these adjacent shears reads a value before its required update.
    pair = original.index(("add", nonpivots[0], 104+nonpivots[0], -1))
    need(original[pair+1] == ("add", 104+nonpivots[0], nonpivots[0], 1),
         "chronology mutation binding")
    changed = original.copy()
    changed[pair], changed[pair+1] = changed[pair+1], changed[pair]
    mutations["wrong_chronology"] = changed

    changed = original.copy()
    del changed[next(i for i, op in enumerate(changed) if op[0] == "double")]
    mutations["missing_restoring_double"] = changed

    mutations["clobbered_dirty_helper"] = original + [("add", 208, pivots[0], 1)]

    # Same values and counts, but the terminal descent is assigned to X rather than Y.
    changed = original.copy()
    descent = next(i for i, op in enumerate(changed) if op[0] == "drop")
    changed[descent] = "drop", nonpivots[0]
    mutations["wrong_physical_return_frame"] = changed

    changed = original.copy()
    del changed[next(i for i, op in enumerate(changed) if op[0] == "lift")]
    mutations["missing_transport"] = changed

    # This pair is the identity, so only the complete bill can reject undercharging it.
    undercharged = original + [("add", 208, pivots[0], 1), ("add", 208, pivots[0], -1)]
    initial, frames, expected, final_frames = primary.boundary(matrix, pivots, nonpivots)
    actual, returned_frames, counts = primary.run(undercharged, initial, frames)
    need(actual == expected and returned_frames == final_frames,
         "invoice-only control must preserve the complete endpoint")
    need(counts["add"] == 962, "invoice-only control actual bill")
    mutations["undercounted_identity_pair"] = undercharged

    for name, program in mutations.items():
        rejected(name, lambda p=program: primary.check_program(
            "consumer", p, matrix, pivots, nonpivots))
    return len(mutations)


def source_byte_control(primary):
    """Actual isolated CLI calls, with writable copies even from a 0444 export."""
    names = list(primary.PINS)
    originals = {name: (HERE / "sources" / name).read_bytes() for name in names}
    with tempfile.TemporaryDirectory(prefix="p104-return-controls-") as directory:
        private = Path(directory) / "package"
        (private / "sources").mkdir(parents=True)
        shutil.copyfile(HERE / "verify.py", private / "verify.py")
        for name in names:
            shutil.copyfile(HERE / "sources" / name, private / "sources" / name)
        command = [sys.executable, "-I", "-B", str(private / "verify.py")]
        baseline = subprocess.run(command, capture_output=True, text=True, check=False)
        need(baseline.returncode == 0, "private-copy baseline: " + baseline.stderr)
        victim = private / "sources" / "consumer-PROOF.md"
        victim.write_bytes(victim.read_bytes() + b"\n")
        for flags in ([], ["-O"]):
            process = subprocess.run([sys.executable, "-I", "-B", *flags,
                                      str(private / "verify.py")],
                                     capture_output=True, text=True, check=False)
            need(process.returncode != 0, "changed authenticated source accepted")
            need("source bytes: consumer-PROOF.md" in process.stderr,
                 "source-byte mutation must fail at authentication")
    need(all((HERE / "sources" / name).read_bytes() == content
             for name, content in originals.items()), "retained originals changed")
    return 1


def main():
    cases = independent_blocks()
    primary = load_primary()
    controls = behavioral_controls(primary) + source_byte_control(primary)
    print("PASS_P104_RETURN_MATCH_TESTS", "generic_rational_B_cases="+str(cases),
          "semantic_controls="+str(controls), "source_cli_modes=normal,optimized")


if __name__ == "__main__":
    main()
