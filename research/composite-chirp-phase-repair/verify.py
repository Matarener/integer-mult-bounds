"""Exact finite corroboration; the universal proof is PROOF.md.

Produced by Nick Petalas. Apache-2.0. Normal execution writes no files.
"""

from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import sys

import chirp
import oracle


def require(condition, message):
    if not condition:
        raise ValueError(message)


def factorizations():
    cases = entries = vectors = ranks = 0
    for n in range(1, 32, 2):
        p, root = oracle.field(n)
        values = [(j * j + 3 * j + 7) % p for j in range(n)]
        for a in range(n):
            m = n // gcd(a, n)
            for b in range(n):
                rows = oracle.matrix(n, a, b, p, root)
                got = chirp.factorized(n, a, b, values, p, root)
                require(got == oracle.apply(rows, values, p), "dense factorization")
                for j in range(n):
                    for k in range(n):
                        direct = a * (j - k) ** 2 + b * (j - k)
                        folded = b * j + a * (j % m - k % m) ** 2 - b * k
                        require((direct - folded) % n == 0, "phase factorization")
                        entries += 1
                if n <= 9:
                    for k in range(n):
                        unit = [int(j == k) for j in range(n)]
                        require(chirp.factorized(n, a, b, unit, p, root)
                                == [row[k] for row in rows], "basis factorization")
                        vectors += 1
                if n <= 15 and b in {0, 1}:
                    require(oracle.rank(rows, p) == m, "literal modular rank")
                    ranks += 1
                cases += 1
    return dict(cases=cases, phase_entries=entries, basis_vectors=vectors,
                modular_ranks=ranks)


def gram_polynomials():
    entries = 0
    for n in range(1, 16, 2):
        phi = oracle.cyclotomic(n)
        for a in range(n):
            m = n // gcd(a, n)
            for b in sorted({0, 1 % n}):
                for j in range(n):
                    for ell in range(n):
                        expected = [0] * n
                        if (j - ell) % m == 0:
                            expected[(b * (j - ell)) % n] = n
                        actual = oracle.gram_entry(n, a, b, j, ell, phi)
                        require(actual == oracle.reduced(expected, phi),
                                "complex cyclotomic Gram entry")
                        entries += 1
    return dict(odd_axes_through=15, entries=entries)


def summed(rows, mask, p):
    n = len(rows[0])
    return [[sum(matrix[j][k] for b, matrix in enumerate(rows) if mask >> b & 1) % p
             for k in range(n)] for j in range(n)]


def repairs():
    subsets = inverse_entries = families = 0
    for n in range(1, 16, 2):
        p, root = oracle.field(n)
        for a in range(n):
            g, m = gcd(a, n), n // gcd(a, n)
            rows = [oracle.matrix(n, a, b, p, root) for b in range(g)]
            all_rows = summed(rows, (1 << g) - 1, p)
            stars = [oracle.matrix(n, a, b, p, pow(root, -1, p)) for b in range(g)]
            star = list(map(list, zip(*summed(stars, (1 << g) - 1, p))))
            for j in range(n):
                for k in range(n):
                    entry = sum(star[j][r] * all_rows[r][k] for r in range(n)) % p
                    require(entry == (n * g * int(j == k)) % p, "repair inverse")
                    inverse_entries += 1
            if g <= 9:
                for mask in range(1 << g):
                    require(oracle.rank(summed(rows, mask, p), p) == m * mask.bit_count(),
                            "phase-subset rank")
                    subsets += 1
            values = [(5 * j + 2) % p for j in range(n)]
            require(chirp.repair(n, a, values, p, root)
                    == oracle.apply(all_rows, values, p), "repair program")
            families += 1
    return dict(families=families, phase_subsets=subsets, inverse_entries=inverse_entries)


def controls():
    rejected = []
    arguments = [
        (0, 0, 0), (2, 0, 0), (257, 0, 0), (True, 0, 0),
        (3, True, 0), (3, 1, "1"), (3, 1 << 257, 0),
    ]
    for args in arguments:
        try:
            chirp.parameters(*args)
        except ValueError:
            rejected.append("parameters:" + repr(args))
        else:
            raise ValueError("invalid parameter accepted")
    p, root = oracle.field(9)
    for values, modulus, phase in [([], p, root), ([0] * 8 + [True], p, root),
                                   ([0] * 8 + [p], p, root), ([0] * 9, 1, root),
                                   ([0] * 9, p, p), ([0] * 9, p, 2)]:
        try:
            chirp.factorized(9, 3, 1, values, modulus, phase)
        except ValueError:
            rejected.append("invalid evaluation")
        else:
            raise ValueError("invalid evaluation accepted")
    unit = [int(j == 1) for j in range(9)]
    require(chirp.factorized(9, 3, 1, unit, p, root)
            != chirp.factorized(9, 3, 0, unit, p, root), "omitted phase hidden")
    rejected.append("omitted twist changes output")
    duplicates = [oracle.matrix(9, 3, b, p, root) for b in (0, 3, 6)]
    require(oracle.rank(summed(duplicates, 7, p), p) <= 3, "duplicate residue repair")
    rejected.append("three duplicate residues do not repair")
    require(oracle.rank(oracle.matrix(9, 3, 0, p, 1), p) == 1, "nonprimitive root")
    rejected.append("nonprimitive root cannot certify complex rank")
    require(oracle.rank(oracle.matrix(4, 1, 0, 5, 2), 5) == 2, "even-axis control")
    rejected.append("even-axis full-rank extrapolation fails")
    require(chirp.parameters(9, -6, -8) == chirp.parameters(9, 3, 1), "residue inputs")
    return rejected


def source_hashes():
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "chirp.py", "oracle.py", "verify.py")
    folder = Path(__file__).resolve().parent
    result = {}
    for name in names:
        with (folder / name).open("rb") as source:
            content = source.read(131073)
        require(len(content) <= 131072, "package source size limit")
        result[name] = sha256(content).hexdigest()
    return result


def main():
    require(len(sys.argv) == 1, "no arguments accepted")
    receipt = dict(status="PASS_COMPOSITE_CHIRP_PHASE_REPAIR",
                   factorizations=factorizations(), gram=gram_polynomials(),
                   repairs=repairs(), controls=controls(), sources=source_hashes())
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
