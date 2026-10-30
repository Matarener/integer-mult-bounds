#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dense independent mask/rank check. No verifier or predecessor imports."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def rank_mod(matrix, prime):
    rows = [list(row) for row in matrix]
    rank = 0
    for column in range(112):
        pivot = next((i for i in range(rank, 112) if rows[i][column] % prime), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [(x * inverse) % prime for x in rows[rank]]
        for i in range(rank + 1, 112):
            coefficient = rows[i][column]
            rows[i] = [(x - coefficient * y) % prime for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
    return rank


def check_dense_mask(matrix, plane, labels):
    forced = 0
    for i in range(112):
        for j in range(112):
            forbidden = any(sum(x * y for x, y in zip(labels[a], labels[b], strict=True)) % 2
                            for a in plane[i] for b in plane[j])
            if i == j or forbidden:
                forced += 1
                if matrix[i][j] != int(i == j):
                    raise ValueError('dense mask')
    return forced


def main():
    source_path = ROOT / 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
    certificate_path = HERE / 'CERTIFICATE.json'
    if source_path.stat().st_size > 4_000_000 or certificate_path.stat().st_size > 100_000:
        raise ValueError('input size limit')
    source = source_path.read_bytes()
    if hashlib.sha256(source).hexdigest() != 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa':
        raise ValueError('source changed')
    rows = json.loads(source)['recipes']
    labels = {row['port']: [(row['q'] >> k) & 1 for k in range(9)] for row in rows}
    groups = json.loads(certificate_path.read_text())['orthonormal_groups']
    if not 1 <= len(groups) <= 56 or any(len(group) not in (2, 4, 6, 8) for group in groups):
        raise ValueError('group sizes')
    flattened = [port for group in groups for port in group]
    if sorted(flattened) != list(range(112)):
        raise ValueError('partition')
    count = sum(len(group) == 8 for group in groups)
    if count != 13:
        raise ValueError('thirteen frames')
    for group in groups:
        for i in group:
            for j in group:
                value = sum(x * y for x, y in zip(labels[i], labels[j], strict=True)) % 2
                if value != int(i == j):
                    raise ValueError('orthonormal group')
    pairs = [group[k:k + 2] for group in groups for k in range(0, len(group), 2)]
    plane = {port: pair for pair in pairs for port in pair}
    supports = [group[side::2] for group in groups for side in range(2)]
    matrix = [[sum(int(i in s) * int(j in s) for s in supports)
               for j in range(112)] for i in range(112)]
    forced = check_dense_mask(matrix, plane, labels)
    ranks = [rank_mod(matrix, prime) for prime in (2, 3, 1000003)]
    if ranks != [34, 34, 34]:
        raise ValueError('dense ranks')
    matrix[pairs[0][0]][pairs[0][1]] = 1
    try:
        check_dense_mask(matrix, plane, labels)
    except ValueError:
        pass
    else:
        raise ValueError('accepted an off-diagonal entry within one plane')
    print('PASS_INDEPENDENT_DENSE_FRAME_CHECK frames=13 ranks=34,34,34 forced=' + str(forced))


if __name__ == '__main__':
    main()
