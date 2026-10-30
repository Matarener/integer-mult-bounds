# SPDX-License-Identifier: Apache-2.0
"""Brute-force small covers and bounded selected-dimension indexing fixtures."""
from hashlib import sha256
import json
from math import prod
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cover import OrthogonalCover, is_orthogonal, multiply, parity, transpose


def brute(dimension, prefix=()):
    if len(prefix) == dimension:
        yield prefix
        return
    for row in range(1 << dimension):
        if parity(row) and all(not parity(row & old) for old in prefix):
            yield from brute(dimension, prefix + (row,))


def run():
    counts = {}
    for dimension in range(1, 6):
        cover = OrthogonalCover(dimension)
        expected = tuple(brute(dimension))
        if len(expected) != cover.size:
            raise ValueError("independent small-cover count")
        for index, rows in enumerate(expected):
            if cover.unrank(index) != rows or cover.rank(rows) != index:
                raise ValueError("lexicographic rank/unrank")
        counts[dimension] = len(expected)
    cover = OrthogonalCover(73)
    gamma = (1 << 1296) * prod((1 << (2 * i)) - 1 for i in range(1, 37))
    if cover.size != gamma:
        raise ValueError("selected symplectic cardinality")
    identity = tuple(1 << i for i in range(73))
    matrix = identity
    matrices = [identity]
    for step in range(8):
        # An even-weight transvection is orthogonal in characteristic two.
        v = (1 << step) ^ (1 << (step + 1)) ^ (1 << (step + 2)) ^ (1 << (step + 3))
        transvection = tuple((1 << i) ^ (v if v >> i & 1 else 0) for i in range(73))
        matrix = multiply(transvection, matrix)
        matrices.append(matrix)
    digest = sha256()
    for rows in matrices:
        if not is_orthogonal(rows) or multiply(rows, transpose(rows)) != identity:
            raise ValueError("selected fixture orthogonality")
        index = cover.rank(rows)
        if cover.unrank(index) != rows:
            raise ValueError("selected cover round trip")
        digest.update(str(index).encode())
    return {"small_complete_covers": counts, "selected_matrix_fixtures": len(matrices),
            "selected_cover_bits": gamma.bit_length(), "sha256": digest.hexdigest(),
            "scope": "Exact finite-control cover indexing; no selected payload execution."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
