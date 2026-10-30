#!/usr/bin/env python3
"""Authenticate and check the exact full G20 boundary; no circuit search."""
from hashlib import sha256
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def apply(word, n):
    rows = [1 << i for i in range(n)]
    for d, s in word:
        require(0 <= d < n and 0 <= s < n and d != s, 'invalid ADD')
        rows[d] ^= rows[s]
    return rows


def partition(rows):
    unseen = set(range(len(rows)))
    parts = []
    while unseen:
        todo = [unseen.pop()]
        part = []
        while todo:
            i = todo.pop()
            part.append(i)
            neighbors = {j for j in unseen if ((rows[i] >> j) | (rows[j] >> i)) & 1}
            unseen -= neighbors
            todo.extend(neighbors)
        parts.append(sorted(part))
    return sorted(parts)


def independent_component_count(rows):
    labels = list(range(len(rows)))
    for i, row in enumerate(rows):
        for j in range(len(rows)):
            if row >> j & 1:
                a, b = labels[i], labels[j]
                labels = [a if label == b else label for label in labels]
    return len(set(labels))


def bound(rows):
    return len(rows) - len(partition(rows)) + sum(not (row >> i & 1) for i, row in enumerate(rows))


def main():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for item in manifest['files']:
        if item['usage'] == 'input':
            require(sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], 'source mismatch')
    source = json.loads((ROOT / 'research/g20-isolated-exchange-floor/inputs/CONTROLLER.json').read_text())['boundaries']
    expected = [list(range(0, 16, 2)) + [31], list(range(1, 16, 2)) + [30], [16, 28], [17, 29], [18, 26], [19, 27], [20, 24], [21, 25], [22], [23]]
    words = {}
    rejected = 0
    for side in ('left', 'right'):
        word = []
        for op, a, b in source[side + '_program']:
            require(op in ('ADD', 'SWAP'), 'unknown opcode')
            word.extend([(a, b)] if op == 'ADD' else [(a, b), (b, a), (a, b)])
        words[side] = word
        rows = apply(word, 32)
        require(rows == source[side + '_rows'], 'literal endpoint mismatch')
        require(partition(rows) == expected, 'support partition mismatch')
        require(independent_component_count(rows) == 10, 'independent partition mismatch')
        zero_diagonal = [i for i, row in enumerate(rows) if not (row >> i & 1)]
        require(zero_diagonal == list(range(14, 22)) + list(range(24, 32)), 'diagonal mismatch')
        require(bound(rows) == len(word) == 38, 'sharpness mismatch')
        for k in range(len(word)):
            require(apply(word[:k] + word[k + 1:], 32) != rows, 'omission admitted')
            rejected += 1
        # Independently execute each source input column as individual bits.
        for column in range(32):
            state = [int(i == column) for i in range(32)]
            for d, s in word:
                state[d] ^= state[s]
            require(state == [(row >> column) & 1 for row in rows], 'column mismatch')
        print(side, 'n=32 components=10 zero_diagonal=16 lower=38 witness=38')
    require(apply(words['left'] + words['right'], 32) == [1 << i for i in range(32)], 'inverse mismatch')
    require(bound([1 << i for i in range(32)]) == 0, 'identity control')
    require(bound([2, 1]) == 3, 'swap control')
    require(bound([3, 2]) == 1, 'ADD control')
    require(bound([2, 1, 4]) == 3, 'untouched-wire control')
    print('PASS_G20_FULL_BOUNDARY_FLOOR sides=2 floor=38 omitted_gates_rejected=' + str(rejected))


if __name__ == '__main__':
    main()
