#!/usr/bin/env python3
"""Generate exact row-splitting witnesses, independently of PR6198's minors.

@CubeJerry, with OpenAI Codex assistance. Apache-2.0.
The verifier imports neither this program nor a predecessor rank routine.
"""
from fractions import Fraction
from pathlib import Path
import argparse
import gzip
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import matrices


def dyadic(value):
    if value.denominator & (value.denominator - 1):
        raise ValueError("non-dyadic coefficient")
    return [value.numerator, value.denominator.bit_length() - 1]


def split(matrix):
    """Gauss-Jordan using only unit pivots in Z[1/2]; no modular arithmetic."""
    m, n = len(matrix), len(matrix[0])
    rows = [[Fraction(x) for x in row] for row in matrix]
    changes = [[Fraction(i == j) for j in range(m)] for i in range(m)]
    pivots = []
    for col in range(n):
        pos = len(pivots)
        candidates = [i for i in range(pos, m) if rows[i][col]
                      and abs(rows[i][col].numerator).bit_count() == 1]
        if not candidates:
            if any(rows[i][col] for i in range(pos, m)):
                raise ValueError("no dyadic unit pivot in this column")
            continue
        p = min(candidates, key=lambda i: (abs(rows[i][col]), i))
        rows[pos], rows[p] = rows[p], rows[pos]
        changes[pos], changes[p] = changes[p], changes[pos]
        scale = rows[pos][col]
        rows[pos] = [x/scale for x in rows[pos]]
        changes[pos] = [x/scale for x in changes[pos]]
        for i in range(m):
            if i == pos or not rows[i][col]:
                continue
            factor = rows[i][col]
            rows[i] = [a-factor*b for a, b in zip(rows[i], rows[pos])]
            changes[i] = [a-factor*b for a, b in zip(changes[i], changes[pos])]
        pivots.append(col)
        if len(pivots) == m:
            break
    rank = len(pivots)
    if any(any(row) for row in rows[rank:]):
        raise ValueError("nonzero unprocessed remainder")
    coefficients = []
    for row in changes[:rank]:
        coefficients.append([[i, *dyadic(x)] for i, x in enumerate(row) if x])
    return {"pivots": pivots, "basis": [[dyadic(x) for x in row] for row in rows[:rank]],
            "coefficients": coefficients}


def build():
    witnesses = []
    for key, matrix in matrices():
        witness = split(matrix)
        witnesses.append({"case": list(key), **witness})
    return {"schema": "e8-dyadic-row-splittings-v1", "witnesses": witnesses}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    certificate = build()
    payload = (json.dumps(certificate, separators=(",", ":")) + "\n").encode()
    args.output.write_bytes(gzip.compress(payload, mtime=0))
    print(json.dumps({"cases": len(certificate["witnesses"]), "payload_bytes": len(payload),
                      "compressed_bytes": args.output.stat().st_size}))


if __name__ == "__main__":
    main()
