#!/usr/bin/env python3
"""Exact finite corroboration of the joint-bank spectral obstruction."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    require(0 <= n <= 32, "dense matrix capacity")
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b, prime=13):
    require(len(a[0]) == len(b), "matrix product shape")
    out = [[sum(x * y for x, y in zip(row, col))
            for col in zip(*b)] for row in a]
    return out if prime is None else [[x % prime for x in row] for row in out]


def subtract(a, b, prime=13):
    require(len(a) == len(b) and len(a[0]) == len(b[0]), "difference shape")
    out = [[x - y for x, y in zip(u, v)] for u, v in zip(a, b)]
    return out if prime is None else [[x % prime for x in row] for row in out]


def kron(a, b):
    return [[x * y for x in ar for y in br] for ar in a for br in b]


def diagonal(a, b):
    return ([row + [0] * len(b) for row in a]
            + [[0] * len(a) + row for row in b])


def rank(a, prime):
    require(1 <= len(a) <= 32 and 1 <= len(a[0]) <= 32, "rank capacity")
    work = [[x % prime for x in row] for row in a]
    pivot = 0
    for col in range(len(work[0])):
        hit = next((i for i in range(pivot, len(work)) if work[i][col]), None)
        if hit is None:
            continue
        work[pivot], work[hit] = work[hit], work[pivot]
        inverse = pow(work[pivot][col], -1, prime)
        work[pivot] = [x * inverse % prime for x in work[pivot]]
        for i in range(len(work)):
            if i != pivot:
                factor = work[i][col]
                work[i] = [(x - factor * y) % prime
                           for x, y in zip(work[i], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def gram_pair(a, prime=13):
    """Literal upper(-I tensor A) times lower(A tensor I)."""
    n = len(a)
    b, c = kron(a, eye(n)), kron(eye(n), a)
    size = n * n
    upper, lower = eye(2 * size), eye(2 * size)
    for i, j in product(range(size), repeat=2):
        upper[i][size + j] = -c[i][j]
        lower[size + i][j] = b[i][j]
    return multiply(upper, lower, prime), b, c


def rectangular_pair(a, b, prime):
    left, right = kron(a, eye(len(b))), kron(eye(len(a)), b)
    size = len(a) * len(b)
    upper, lower = eye(2 * size), eye(2 * size)
    for i, j in product(range(size), repeat=2):
        upper[i][size + j] = -right[i][j]
        lower[size + i][j] = left[i][j]
    actual = subtract(multiply(upper, lower, prime), eye(2 * size), prime)
    joint = multiply(right, left, prime)
    formula = ([[-x for x in u] + [-x for x in v]
                for u, v in zip(joint, right)]
               + [row + [0] * size for row in left])
    require(actual == [[x % prime for x in row] for row in formula],
            "literal product and block formula disagree")
    return actual


def local_blocks():
    blocks = {1: [[0]], 2: [[0, 1], [0, 0]]}
    result = {}
    for prime, p, q in product((2, 3, 5, 13, 17), (1, 2), (1, 2)):
        nilpotent = rectangular_pair(blocks[p], blocks[q], prime)
        square = multiply(nilpotent, nilpotent, prime)
        cube = multiply(square, nilpotent, prime)
        ranks = (rank(nilpotent, prime), rank(square, prime), rank(cube, prime))
        expected = (int(p == 2) * q + int(q == 2) * p,
                    2 * int(p == q == 2), 0)
        require(ranks == expected, "atomic tensor ranks")
        result[f"{prime}:{p}x{q}"] = [2 * p * q, *ranks]
    return result


def assemble(n, r, atoms):
    require(0 <= 2 * r <= n <= 104, "square-zero source parameters")
    parts = [2] * r + [1] * (n - 2 * r)
    counts = Counter()
    totals = [0, 0, 0, 0]
    for p, q in product(parts, repeat=2):
        data = atoms[f"13:{p}x{q}"]
        counts[f"{p}x{q}"] += 1
        totals = [x + y for x, y in zip(totals, data)]
    dimension, first, second, third = totals
    require(totals == [2 * n * n, 2 * n * r, 2 * r * r, 0], "assembled ranks")
    jordan = {"3": second, "2": first - 2 * second,
              "1": dimension - 2 * first + second}
    require(all(x >= 0 for x in jordan.values()), "Jordan multiplicities")
    return {"n": n, "r": r, "components": dict(sorted(counts.items())),
            "dimension": dimension, "ranks": [first, second, third],
            "jordan_blocks": jordan}


def matching_rank(mapping):
    require(len(set(mapping.values())) == len(mapping), "distinct arrow images")
    return len(mapping)


def optimal_modular_repair(data):
    """Enumerate Jordan arrows, and match an actual projector's arrows to them."""
    original, chosen = {}, {}
    cursor = 0
    target_rank = data["n"] * data["r"]
    for size in (3, 2, 1):
        for _ in range(data["jordan_blocks"][str(size)]):
            for offset in range(1, size):
                original[cursor + offset] = cursor + offset - 1
            if size >= 2 and len(chosen) < target_rank:
                chosen[cursor + 1] = cursor
            cursor += size
    require(cursor == data["dimension"], "complete Jordan coordinates")
    require(len(chosen) == target_rank, "enough disjoint Jordan chains")
    require(all(dest not in chosen for dest in chosen.values()), "square-zero target")
    correction = {col: row for col, row in original.items() if col not in chosen}
    require(matching_rank(original) == data["ranks"][0], "Jordan source rank")
    require(matching_rank(correction) == target_rank, "attaining repair rank")
    n, r = data["n"], data["r"]
    target = {n * n + i * n + j: i * n + j
              for i, j in product(range(n), range(r))}
    permutation = {}
    for (col, row), (new_col, new_row) in zip(target.items(), chosen.items()):
        permutation[col], permutation[row] = new_col, new_row
    remaining = sorted(set(range(cursor)) - set(permutation.values()))
    old_remaining = sorted(set(range(cursor)) - set(permutation))
    permutation.update(zip(old_remaining, remaining))
    require(len(set(permutation.values())) == cursor, "full coordinate permutation")
    require({permutation[c]: permutation[v] for c, v in target.items()} == chosen,
            "projector conjugacy witness")
    return {"asymmetric_minimum_modular_rank": matching_rank(correction),
            "balanced_minimum_modular_rank": matching_rank(original),
            "enumerated_coordinates": cursor, "projector_arrows": len(target)}


def stable_fixtures():
    source, _, _ = gram_pair([[0, 1], [0, 0]])
    cases = 0
    for scratch in (0, 1, 3):
        extended = diagonal(source, eye(scratch))
        size = len(extended)
        code, inverse = eye(size), eye(size)
        for i in range(size - 1):
            step, back = eye(size), eye(size)
            step[i][i + 1], back[i][i + 1] = 1, -1
            code = multiply(step, code)
            inverse = multiply(inverse, back)
        require(multiply(code, inverse) == eye(size), "joint mixing inverse")
        mixed = multiply(multiply(code, extended), inverse)
        require(rank(subtract(mixed, eye(size)), 13) == 4, "restored scratch invariant")
        for alpha, beta in product(range(13), repeat=2):
            if alpha * beta % 13:
                continue
            p = [[1, 0], [0, 0]]
            left, right = kron(p, eye(2)), kron(eye(2), p)
            target = eye(8)
            for i, j in product(range(4), repeat=2):
                target[i][4 + j] = -alpha * right[i][j]
                target[4 + i][j] = beta * left[i][j]
            target = diagonal(target, eye(scratch))
            trank = rank(subtract(target, eye(size)), 13)
            require(trank == (2 if alpha or beta else 0), "projector target rank")
            require(rank(subtract(mixed, target), 13) >= 4 - trank,
                    "stable correction lower bound")
            cases += 1
    return cases


def rational_escape():
    source, _, _ = gram_pair([[13, 1], [0, 0]], None)
    t = [[1, Q(1, 13)], [0, 1]]
    inverse = [[1, Q(-1, 13)], [0, 1]]
    code = diagonal(kron(t, t), kron(t, t))
    back = diagonal(kron(inverse, inverse), kron(inverse, inverse))
    target, _, _ = gram_pair([[13, 0], [0, 0]], None)
    require(multiply(code, back, None) == eye(8), "rational code inverse")
    require(multiply(multiply(code, source, None), back, None) == target,
            "odd-denominator escape must remain possible")
    require(any(isinstance(x, Q) and x.denominator % 13 == 0
                for row in code for x in row), "escape leaves dyadic ring")


def return_controls():
    source, b, _ = gram_pair([[0, 1], [0, 0]])
    lower = eye(8)
    for i, j in product(range(4), repeat=2):
        lower[4 + i][j] = b[i][j]
    require(rank(subtract(lower, eye(8)), 13) == 2, "omitted stage changes invariant")
    extended = diagonal(source, eye(8))
    swap = [[int((i + 8) % 16 == j) for j in range(16)] for i in range(16)]
    moved = multiply(multiply(swap, extended), swap)
    require(moved == diagonal(eye(8), source), "discarded scratch escape")
    require(moved != eye(16), "scratch return must be checked")


def source_binding():
    path = HERE / "SOURCES.json"
    require(path.stat().st_size <= 16384, "source manifest capacity")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    require(len(manifest["files"]) == 3, "source inventory capacity")
    bound = {}
    for item in manifest["files"]:
        if item["usage"] == "input":
            require(item["path"] == "research/p104-tensor-code/PROOF.md",
                    "declared premise path")
            path = ROOT / item["path"]
            require(not path.is_symlink() and path.stat().st_size <= 16 * 1024 * 1024,
                    "bounded regular source")
            digest = sha256(path.read_bytes()).hexdigest()
            require(digest == item["sha256"], "cited premise source changed")
            bound[item["path"]] = digest
    require(len(bound) == 1, "one cited premise source")
    return bound


def main():
    bound = source_binding()
    atoms = local_blocks()
    small = [assemble(n, r, atoms) for n in range(1, 17)
             for r in range(n // 2 + 1)]
    actual = assemble(104, 8, atoms)
    repair = optimal_modular_repair(actual)
    rational_escape()
    return_controls()
    invalid = 0
    for n, r in ((1, 1), (104, 53), (105, 1), (2, -1)):
        try:
            assemble(n, r, atoms)
        except ValueError:
            invalid += 1
    require(invalid == 4, "invalid parameter controls")
    report = {"schema": "p104-joint-spectral-obstruction/1",
              "claim_type": "scoped proof with finite exact corroboration",
              "p104": actual, "repair": repair, "local_block_cases": len(atoms),
              "small_assemblies": len(small), "stable_cases": stable_fixtures(),
              "controls": ["invalid_square_zero_parameters", "odd_denominator_escape",
                           "omitted_stage", "unreturned_scratch_escape"],
              "cited_premise_hashes": bound,
              "scope": "The predecessor Gram identities are premises, not replayed results. Sharpness is over F13, not an exact dyadic repair.",
              "package_hashes": {name: sha256((HERE / name).read_bytes()).hexdigest()
                                 for name in ("verify.py", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json", "README.md")}}
    print(json.dumps(report, sort_keys=True))
    print("PASS_P104_JOINT_SPECTRAL_OBSTRUCTION modular_repair=832 balanced=1664 no_new_kappa")


if __name__ == "__main__":
    main()
