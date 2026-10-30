#!/usr/bin/env python3
"""Check the new six-frame cut certificate; do not replay predecessor circuits."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


ZERO = (0, 0, 0, 0)
IDENTITY = (1, 0, 0, 1)
J = (0, 1, -1, 0)
B = (0, 0, -1, 1)
FRAMES = (ZERO, IDENTITY, J, (1, 1, -1, 1), B, (1, 0, -1, 2))
LABELS = ((0, 0), (1, 1), (0, 0), (1, 1), (0, 1), (1, 0))
FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
SOURCE = "research/nonlinear-frame-cut-bound/README.md"
SOURCE_HASH = "411b78a56180e835bb97e59b9845968d84ad3fb8f5658acde684e4491b3b1c3e"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def difference(left, right):
    return tuple(left[i] - right[i] for i in range(4))


def determinant(matrix):
    return matrix[0] * matrix[3] - matrix[1] * matrix[2]


def rank(matrix):
    return 2 if determinant(matrix) else int(any(matrix))


def elimination_rank(matrix):
    """A separate rational elimination oracle for the 2-by-2 differences."""
    rows = [[Fraction(matrix[2 * i + j]) for j in range(2)] for i in range(2)]
    pivots = 0
    for column in range(2):
        candidates = [i for i in range(pivots, 2) if rows[i][column]]
        if not candidates:
            continue
        pivot = candidates[0]
        rows[pivots], rows[pivot] = rows[pivot], rows[pivots]
        scale = rows[pivots][column]
        rows[pivots] = [entry / scale for entry in rows[pivots]]
        for i in range(2):
            if i != pivots:
                scale = rows[i][column]
                rows[i] = [rows[i][j] - scale * rows[pivots][j] for j in range(2)]
        pivots += 1
    return pivots


def multiply(left, right):
    return tuple(sum(left[2 * i + k] * right[2 * k + j] for k in range(2))
                 for i in range(2) for j in range(2))


def hamming(left, right):
    return sum(left[i] != right[i] for i in range(2))


def check_certificate(labels, ranks, demands):
    require(len(labels) == 6, "six labels required")
    require(all(len(label) == 2 for label in labels), "two bits per label required")
    require(all(type(bit) is int and bit in (0, 1) for label in labels for bit in label),
            "labels must contain integer bits")
    require(len(ranks) == 6 and all(len(row) == 6 for row in ranks), "rank table shape")
    require(all(type(ranks[i][j]) is int and 0 <= ranks[i][j] <= 2
                for i in range(6) for j in range(6)), "rank range")
    for i in range(6):
        for j in range(6):
            require(hamming(labels[i], labels[j]) <= ranks[i][j], "edge budget")
    require(tuple(demands) == ((0, 1), (2, 3), (4, 5)), "complete identity demands")
    for i, j in demands:
        require(hamming(labels[i], labels[j]) == 2, "endpoint separation")


def check_algebra():
    require(len(set(FRAMES)) == 6, "distinct frames")
    for i in (0, 2, 4):
        require(difference(FRAMES[i + 1], FRAMES[i]) == IDENTITY, "identity translate")
    ranks = tuple(tuple(rank(difference(a, b)) for b in FRAMES) for a in FRAMES)
    for i in range(6):
        for j in range(6):
            require(ranks[i][j] == elimination_rank(difference(FRAMES[i], FRAMES[j])),
                    "independent rank oracle")
    demands = tuple((i, j) for i in range(6) for j in range(6)
                    if difference(FRAMES[j], FRAMES[i]) == IDENTITY)
    commutator = difference(multiply(J, B), multiply(B, J))
    require(commutator == (-1, 1, 1, 1), "commutator entries")
    require(determinant(commutator) == -2, "no common invariant line")
    check_certificate(LABELS, ranks, demands)
    return ranks, demands


def enumerate_labels(ranks, demands):
    """Enumerate all 4^6 assignments, including translated/complemented cuts."""
    solutions = []
    bits = tuple(product((0, 1), repeat=2))
    checked = 0
    for labels in product(bits, repeat=6):
        checked += 1
        if not all(hamming(labels[i], labels[j]) == 2 for i, j in demands):
            continue
        if all(hamming(labels[i], labels[j]) <= ranks[i][j]
               for i in range(6) for j in range(6)):
            solutions.append(labels)
    require(checked == 4096, "complete finite label domain")
    require(len(solutions) == 16 and LABELS in solutions, "attaining cut assignments")
    return checked, len(solutions)


def rejection_controls(ranks, demands):
    bad_labels = [LABELS[:5], ((0,),) + LABELS[1:], ((False, 0),) + LABELS[1:]]
    bad_labels += [((2, 0),) + LABELS[1:]]
    for i, j in ((1, 0), (4, 3), (5, 3)):
        changed = list(LABELS)
        changed[i] = ((j >> 1) & 1, j & 1)
        bad_labels.append(tuple(changed))
    cases = [(labels, ranks, demands) for labels in bad_labels]
    for i, j in ((0, 1), (0, 4)):
        changed = [list(row) for row in ranks]
        changed[i][j] -= 1
        cases.append((LABELS, changed, demands))
    cases += [(LABELS, ranks, demands[:2]), (LABELS, ranks, tuple(reversed(demands)))]
    for labels, table, endpoints in cases:
        try:
            check_certificate(labels, table, endpoints)
        except ValueError:
            continue
        raise ValueError("a corrupt certificate was accepted")
    return len(cases)


def receipt(package, ranks, checked, solutions, controls):
    source = package.parent.parent / SOURCE
    require(sha256(source.read_bytes()).hexdigest() == SOURCE_HASH, "source bytes changed")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in FILES}
    return {
        "status": "PASS_SIX_FRAME_SEED_CUT",
        "claim_type": "scoped mathematical proof with exact finite certificate",
        "rank_table": ranks,
        "labels": LABELS,
        "ordered_rank_pairs": 36,
        "identity_shift_demands": 3,
        "label_assignments_enumerated": checked,
        "valid_two_cut_assignments": solutions,
        "rejection_controls": controls,
        "five_role_lower_bound": 10,
        "rank_mass_bound": "s >= 2W",
        "commutator_determinant": -2,
        "source_sha256": SOURCE_HASH,
        "package_sha256": hashes,
    }


def main():
    require(len(sys.argv) == 1, "no arguments are accepted")
    ranks, demands = check_algebra()
    checked, solutions = enumerate_labels(ranks, demands)
    controls = rejection_controls(ranks, demands)
    print(json.dumps(receipt(Path(__file__).resolve().parent, ranks, checked,
                             solutions, controls), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
