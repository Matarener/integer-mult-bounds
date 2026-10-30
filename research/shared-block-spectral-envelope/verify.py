#!/usr/bin/env python3
"""Exact corroboration of the written shared-block spectral theorem."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

MAX_DIMENSION = 33
CENSUS_DIMENSION = 4


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def domain(r: int, k: int) -> None:
    need(type(r) is int and type(k) is int, "dimensions must be integers")
    need(1 <= r <= MAX_DIMENSION and 0 <= k <= r, "dimension outside replay domain")


def envelope(r: int, k: int) -> int:
    domain(r, k)
    if k == r:
        return r
    return 2 * r - (k % 2)


def identity(r: int) -> tuple[int, ...]:
    return tuple(1 << i for i in range(r))


def diagonal(r: int, k: int) -> tuple[int, ...]:
    return tuple((1 << i) if i < k else 0 for i in range(r))


def add(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    need(len(a) == len(b), "matrix shape mismatch")
    return tuple(x ^ y for x, y in zip(a, b))


def multiply(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    n = len(a)
    need(len(b) == n, "matrix shape mismatch")
    rows = [0] * n
    for i in range(n):
        for j in range(n):
            if (a[i] >> j) & 1:
                rows[i] ^= b[j]
    return tuple(rows)


def power(a: tuple[int, ...], exponent: int) -> tuple[int, ...]:
    need(0 <= exponent <= MAX_DIMENSION, "power outside replay domain")
    result = identity(len(a))
    base = a
    for bit in range(exponent.bit_length()):
        if (exponent >> bit) & 1:
            result = multiply(result, base)
        base = multiply(base, base)
    return result


def rank(a: tuple[int, ...]) -> int:
    n = len(a)
    rows = list(a)
    pivot = 0
    for col in range(n):
        chosen = next((i for i in range(pivot, n) if (rows[i] >> col) & 1), None)
        if chosen is None:
            continue
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        for i in range(pivot + 1, n):
            if (rows[i] >> col) & 1:
                rows[i] ^= rows[pivot]
        pivot += 1
    return pivot


def inverse(a: tuple[int, ...]) -> tuple[int, ...]:
    n = len(a)
    rows = [a[i] | (1 << (n + i)) for i in range(n)]
    for col in range(n):
        chosen = next((i for i in range(col, n) if (rows[i] >> col) & 1), None)
        need(chosen is not None, "singular basis")
        rows[col], rows[chosen] = rows[chosen], rows[col]
        for i in range(n):
            if i != col and (rows[i] >> col) & 1:
                rows[i] ^= rows[col]
    return tuple(row >> n for row in rows)


def zero_multiplicity(a: tuple[int, ...]) -> int:
    return len(a) - rank(power(a, len(a)))


def characteristic(a: tuple[int, ...]) -> int:
    """Leibniz determinant in F2[t], independent of elimination/powers."""
    n = len(a)
    need(n <= CENSUS_DIMENSION, "characteristic oracle exceeds its bound")
    result = 0
    for perm in itertools.permutations(range(n)):
        term = 1
        for i, j in enumerate(perm):
            coefficient = (a[i] >> j) & 1
            if i == j:
                term = (term << 1) ^ (term if coefficient else 0)
            elif coefficient == 0:
                term = 0
        result ^= term
    need(result.bit_length() == n + 1, "characteristic polynomial must be monic")
    return result


def polynomial_order(polynomial: int) -> int:
    need(polynomial > 0, "zero polynomial has no finite order")
    return (polynomial & -polynomial).bit_length() - 1


def even_core(k: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Conjugate the strict triangular halves of I+J_(k+1)."""
    need(k >= 0 and k % 2 == 0 and k + 1 <= MAX_DIMENSION, "bad even core")
    n = k + 1
    upper = tuple(sum(1 << j for j in range(i + 1, n)) for i in range(n))
    lower = tuple((1 << i) - 1 for i in range(n))
    # Columns are e_i+e_(n-1), followed by the all-ones kernel vector.
    basis = tuple(((1 << i) if i < k else (1 << k) - 1) | (1 << k)
                  for i in range(n))
    back = inverse(basis)
    a = multiply(multiply(back, upper), basis)
    b = multiply(multiply(back, lower), basis)
    need(add(a, b) == diagonal(n, k), "core does not have the coordinate endpoint")
    return a, b


def witness(r: int, k: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    domain(r, k)
    if k == r:
        return (0,) * r, identity(r)
    if k % 2 == 0:
        a, b = even_core(k)
        return a + (0,) * (r - len(a)), b + (0,) * (r - len(b))
    # Put one eigenvalue-one block next to a rank-(k-1) even core.
    a, b = even_core(k - 1)
    a = a + (0,) * (r - len(a))
    b = b + (0,) * (r - len(b))
    # The core's zero coordinate is k-1; place the one block at k,
    # then swap those two coordinates to obtain diag(I_k,0).
    b = tuple(row ^ ((1 << k) if i == k else 0) for i, row in enumerate(b))
    swap = list(identity(r))
    swap[k - 1], swap[k] = swap[k], swap[k - 1]
    return multiply(multiply(tuple(swap), a), tuple(swap)), \
        multiply(multiply(tuple(swap), b), tuple(swap))


def check_witness(r: int, k: int, a: tuple[int, ...], b: tuple[int, ...]) -> None:
    domain(r, k)
    need(len(a) == r and len(b) == r, "witness size mismatch")
    need(all(type(row) is int and 0 <= row < (1 << r) for row in a + b),
         "invalid binary row")
    need(add(a, b) == diagonal(r, k), "wrong endpoint")
    need(zero_multiplicity(a) + zero_multiplicity(b) == envelope(r, k),
         "witness misses sharp envelope")
    if k == r - 1 and k > 0 and k % 2 == 0:
        for matrix in (a, b):
            need(rank(matrix) == r - 1, "corank-one extremizer has extra Jordan blocks")
            need(power(matrix, r) == (0,) * r, "extremizer not nilpotent")
            need(power(matrix, r - 1) != (0,) * r, "nilpotent chain is too short")


def census() -> list[dict[str, object]]:
    summaries = []
    for r in range(1, CENSUS_DIMENSION + 1):
        size = 1 << (r * r)
        mask = (1 << r) - 1
        z_values = [0] * size
        for code in range(size):
            a = tuple((code >> (i * r)) & mask for i in range(r))
            z_values[code] = zero_multiplicity(a)
            need(z_values[code] == polynomial_order(characteristic(a)),
                 "power and characteristic oracles disagree")
        for k in range(r + 1):
            d_code = sum(1 << (i * r + i) for i in range(k))
            scores = [z_values[code] + z_values[code ^ d_code] for code in range(size)]
            maximum = max(scores)
            need(maximum == envelope(r, k), "complete census disagrees with theorem")
            # Check the forced regular chains for every binary corank-one maximizer.
            if k == r - 1 and k > 0 and k % 2 == 0:
                for code in range(size):
                    if scores[code] == maximum:
                        a = tuple((code >> (i * r)) & mask for i in range(r))
                        b = tuple((code ^ d_code) >> (i * r) & mask for i in range(r))
                        check_witness(r, k, a, b)
            summaries.append({"r": r, "k": k, "matrices": size,
                              "maximum": maximum, "maximizers": scores.count(maximum)})
    return summaries


def rejection_controls() -> int:
    bad = [(0, 0), (34, 0), (3, -1), (3, 4), (True, 1), (3, False)]
    count = 0
    for r, k in bad:
        try:
            envelope(r, k)
        except ValueError:
            count += 1
    need(count == len(bad), "invalid domain accepted")
    a, b = witness(5, 4)
    mutants = [((a[0] ^ 1,) + a[1:], b), ((0,) * 5, diagonal(5, 4)),
               (a[:-1], b), (a, (True,) + b[1:])]
    for x, y in mutants:
        try:
            check_witness(5, 4, x, y)
        except ValueError:
            count += 1
    need(count == len(bad) + len(mutants), "bad witness accepted")
    return count


def report() -> dict[str, object]:
    constructed = 0
    for r in range(1, MAX_DIMENSION + 1):
        for k in range(r + 1):
            check_witness(r, k, *witness(r, k))
            constructed += 1
    rows = census()
    a, b = witness(5, 4)
    return {"status": "PASS_SHARED_BLOCK_SPECTRAL_ENVELOPE",
            "claim_type": "scoped algebraic proof with finite corroboration",
            "constructed_cases": constructed,
            "complete_binary_matrix_pairs": sum(row["matrices"] for row in rows),
            "independent_characteristic_checks": sum(1 << (r * r) for r in range(1, 5)),
            "rejection_controls": rejection_controls(),
            "five_coordinate_witness_rows": {"A": a, "B": b},
            "census": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new external hash-bound receipt")
    args = parser.parse_args()
    if args.receipt is not None:
        need(not args.receipt.exists(), "receipt already exists")
        need(Path(__file__).resolve().parent not in args.receipt.resolve().parents,
             "receipt must be outside the package")
    result = report()
    if args.receipt is not None:
        package = Path(__file__).resolve().parent
        files = sorted(path for path in package.iterdir() if path.is_file())
        need(len(files) <= 16, "package inventory exceeds receipt bound")
        need(all(path.stat().st_size <= 1024 * 1024 for path in files),
             "package file exceeds receipt byte bound")
        hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
        payload = {"result": result, "package_sha256": hashes}
        with args.receipt.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
