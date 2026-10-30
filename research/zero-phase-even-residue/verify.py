#!/usr/bin/env python3
"""Exact finite corroboration for the new zero-phase length theorem.

Produced by Nick Petalas. Apache-2.0. Standard library only.
"""
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import sys

MAX_AXES = 130
MAX_WIDTH = 265
PACKAGE = Path(__file__).resolve().parent
SOURCE = "research/nine-axis-cutoff-sharpness/PROOF.md"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_rank(words):
    """Internal bounded input, at most MAX_AXES+1 words of MAX_WIDTH bits."""
    basis = [0] * MAX_WIDTH
    result = 0
    for original in words:
        word = original
        for pivot in range(MAX_WIDTH - 1, -1, -1):
            if not (word >> pivot) & 1:
                continue
            if basis[pivot]:
                word ^= basis[pivot]
            else:
                basis[pivot] = word
                result += 1
                break
    return result


def witness(n, width, rows):
    require(type(n) is int and 1 <= n <= MAX_AXES, "axis capacity")
    require(type(width) is int and 1 <= width <= MAX_WIDTH, "width capacity")
    require(len(rows) == n, "coordinate row count")
    require(all(type(r) is int and 0 <= r < 1 << width for r in rows),
            "row range")
    require(all(r.bit_count() % 4 == 0 for r in rows), "linear phase")
    require(all((rows[j] & rows[l]).bit_count() % 2 == 0
                for j in range(n) for l in range(j)), "quadratic phase")
    require(binary_rank([*rows, (1 << width) - 1]) == n + 1,
            "full affine span")


def construct(n):
    require(type(n) is int and 2 <= n <= MAX_AXES and n % 4 == 2,
            "constructor domain")
    rows = []
    for block in range((n - 2) // 4):
        rows.extend(r << (8 * block)
                    for r in (0b11111111, 0b10101010, 0b11001100, 0b11110000))
    offset = 2 * (n - 2)
    rows.extend(r << offset for r in (0b111100, 0b110011))
    return rows


def points(rows, width):
    return [sum(((r >> t) & 1) << j for j, r in enumerate(rows))
            for t in range(width)]


def literal_witness(n, width, rows):
    """Independent column-oriented phase sums and affine-difference rank."""
    require(1 <= n <= 18 and 1 <= width <= 41, "literal capacity")
    xs = points(rows, width)
    for j in range(n):
        require(sum((x >> j) & 1 for x in xs) % 4 == 0, "literal linear")
        for l in range(j):
            require(sum(((x >> j) & 1) * ((x >> l) & 1) for x in xs) % 2 == 0,
                    "literal quadratic")
    differences = [x ^ xs[0] for x in xs[1:]]
    # The alternate rank implementation grows a set only for n<=18.
    span = {0}
    for word in differences:
        if word not in span:
            span.update([word ^ x for x in span])
    require(len(span) == 1 << n, "literal affine span")


def family_checks():
    cases = literal = codewords = 0
    for n in range(2, MAX_AXES + 1, 4):
        rows = construct(n)
        for pad in range(4):
            width = 2 * n + 2 + pad
            witness(n, width, rows)
            cases += 1
            if n <= 18:
                literal_witness(n, width, rows)
                literal += 1
        if n <= 10:
            for mask in range(1 << n):
                word = 0
                for j in range(n):
                    if (mask >> j) & 1:
                        word ^= rows[j]
                require(word.bit_count() % 4 == 0, "literal code weight")
                codewords += 1
    return {"padded_witnesses": cases, "literal_column_witnesses": literal,
            "explicit_codewords": codewords}


def two_axis_census():
    counts = []
    total = phase_tests = 0
    for width in range(7):
        zero = full = 0
        for xs in product(range(4), repeat=width):
            rows = [sum(((x >> j) & 1) << t for t, x in enumerate(xs))
                    for j in range(2)]
            packed = all(r.bit_count() % 4 == 0 for r in rows)
            packed = packed and (rows[0] & rows[1]).bit_count() % 2 == 0
            literal = True
            for a, b, c in product(range(4), range(4), range(2)):
                exponent = sum(a * (x & 1) + b * ((x >> 1) & 1)
                               + 2 * c * (x & 1) * ((x >> 1) & 1) for x in xs)
                literal = literal and exponent % 4 == 0
                phase_tests += 1
            require(packed == literal, "phase character equivalence")
            total += 1
            if not literal:
                continue
            zero += 1
            differences = {x ^ xs[0] for x in xs} if xs else {0}
            closure = {a ^ b for a in differences for b in differences}
            affine = len(closure | differences) == 4
            homogeneous = binary_rank([*rows, (1 << width) - 1]) == 3
            require(affine == homogeneous, "two affine criteria")
            if affine:
                require(width == 6 and sorted(xs) == [1, 1, 2, 2, 3, 3],
                        "two-axis minimal tuple classification")
                full += 1
        counts.append({"width": width, "zero_phase": zero, "full_span": full})
    require(sum(row["full_span"] for row in counts) == 90, "minimal permutation count")
    return {"ordered_tuples": total, "literal_phase_tests": phase_tests,
            "by_width": counts}


def gaussian_sum(width):
    """Literal binomial expansion, no floating point or complex numbers."""
    powers = ((1, 0), (0, 1), (-1, 0), (0, -1))
    real = imag = 0
    for weight in range(width + 1):
        a, b = powers[weight % 4]
        real += comb(width, weight) * a
        imag += comb(width, weight) * b
    return real, imag


def gauss_checks():
    cases = 0
    for n in range(2, MAX_AXES + 1, 4):
        width = 2 * n + 1
        actual = gaussian_sum(width)
        required = (1 << n, 1 << n)
        require(actual == (-required[0], -required[1]), "Gauss obstruction sign")
        require(actual != required, "Gauss contradiction")
        cases += 1
    # These genuine witnesses show why the residue hypothesis matters.
    witness(3, 7, [0b1010101, 0b1100110, 0b1111000])
    witness(4, 9, [0b11111111, 0b10101010, 0b11001100, 0b11110000])
    require(gaussian_sum(7) == (8, -8), "compatible odd residue")
    require(gaussian_sum(9) == (16, 16), "compatible even residue")
    return {"gauss_contradictions": cases, "other_residue_controls": 2}


def rejection_checks():
    rejected = 0
    for invalid in (-2, 0, 1, 3, 4, 5, 131, True):
        try:
            construct(invalid)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("accepted invalid constructor input")
    rows = construct(6)
    bad_rows = [rows[:-1], [*rows[:-1], rows[0]],
                [rows[0] ^ 1, *rows[1:]], [-1, *rows[1:]],
                [1 << 14, *rows[1:]]]
    fixtures = [(6, 14, r) for r in bad_rows]
    fixtures.extend([(2, 8, [0b11110000, 0b00001111]),
                     (2, 6, [0b111100, 0b111010]),
                     (2, 6, [0b110000, 0b001100]),
                     (6, 266, rows), (6, 0, rows)])
    for n, width, fixture in fixtures:
        try:
            witness(n, width, fixture)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("accepted invalid witness")
    return {"rejection_controls": rejected}


def bindings():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    records = [r for r in manifest["files"] if r["path"] == SOURCE]
    require(len(records) == 1 and records[0]["usage"] == "input", "source declaration")
    source_hash = sha256((PACKAGE.parents[1] / SOURCE).read_bytes()).hexdigest()
    require(source_hash == records[0]["sha256"], "cited source proof hash")
    files = sorted(p for p in PACKAGE.iterdir() if p.is_file())
    require(len(files) <= 10, "package receipt file capacity")
    return {**{p.name: sha256(p.read_bytes()).hexdigest() for p in files},
            SOURCE: source_hash}


def main():
    require(len(sys.argv) == 1, "this bounded verifier takes no arguments")
    hashes = bindings()
    result = {"status": "PASS_ZERO_PHASE_EVEN_RESIDUE", "family": family_checks(),
              "two_axis": two_axis_census(), "gauss": gauss_checks(),
              "controls": rejection_checks(), "file_sha256": hashes,
              "claim_type": "scoped proof with finite corroboration"}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
