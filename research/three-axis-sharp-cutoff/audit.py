#!/usr/bin/env python3
"""Separate enumeration: permutations, rational solves, base-four forms, tuples.

Joseph Anglada with substantial OpenAI Codex assistance. Apache-2.0.
Written separately in the same agent context; not an independent human audit.
Imports neither verify.py nor any predecessor arithmetic/executable.
"""
from collections import Counter
from fractions import Fraction
from itertools import permutations, product
from math import lcm
import json

def check(value, label):
    if not value:
        raise ValueError(label)

def span(items):
    space = {0}
    for x in items:
        space |= {y ^ x for y in space}
    return space

def cycle_order(g):
    unseen, order = set(range(8)), 1
    while unseen:
        start = min(unseen)
        x, length = start, 0
        while x in unseen:
            unseen.remove(x)
            x, length = g[x], length + 1
        check(x == start, 'permutation cycle')
        order = lcm(order, length)
    return order

def solve(rows, size):
    rows = [[Fraction(x) for x in row] for row in rows]
    pivot = 0
    for col in range(size):
        hit = next((k for k in range(pivot, len(rows)) if rows[k][col]), None)
        check(hit is not None, 'unique rational coefficient solution')
        rows[pivot], rows[hit] = rows[hit], rows[pivot]
        divisor = rows[pivot][col]
        rows[pivot] = [x / divisor for x in rows[pivot]]
        for k in range(len(rows)):
            if k != pivot:
                factor = rows[k][col]
                rows[k] = [x - factor * y for x, y in zip(rows[k], rows[pivot])]
        pivot += 1
    check(all(not any(row[:-1]) and not row[-1] for row in rows[size:]), 'rational consistency')
    return [rows[k][-1] for k in range(size)]

def main():
    group = []
    for tail in permutations(range(1, 8)):
        g = (0,) + tail
        if all(g[x ^ y] == (g[x] ^ g[y]) for x in range(8) for y in range(8)):
            group.append(g)
    check(len(group) == 168, 'independent GL3 inventory')
    orders = {g: cycle_order(g) for g in group}
    subgroup = [g for g in group if g[:4] == (0, 1, 2, 3)]
    seen, patterns = set(), Counter()
    for g in group:
        if g in seen:
            continue
        coset = {tuple(g[h[x]] for x in range(8)) for h in subgroup}
        seen |= coset
        patterns[tuple(sorted(orders[h] for h in coset))] += 1
    classes = (1, 2, 3, 4, 7)
    equations = [[1, 0, 0, 0, 0, 6]]
    equations += [[pattern.count(order) for order in classes] + [0] for pattern in sorted(patterns)]
    solution = solve(equations, 5)
    check(solution == list(map(Fraction, (6, -2, 0, 2, -1))), 'rederived coefficients')
    coefficient = {g: solution[classes.index(orders[g])] for g in group}
    minima = {}
    for a in product(range(4), repeat=8):
        points = [x for x, count in enumerate(a) if count]
        affine = (len(span([x ^ points[0] for x in points])).bit_length() - 1) if points else -1
        key = (sum(a) & 3, sum(a[x] for x in (1, 3, 5, 7)) & 3,
               sum(a[x] for x in (2, 3, 6, 7)) & 3, sum(a[x] for x in (4, 5, 6, 7)) & 3,
               (a[3] + a[7]) & 1, (a[5] + a[7]) & 1, (a[6] + a[7]) & 1)
        length = sum(a) + 4 * (3 - affine)
        minima[key] = min(minima.get(key, 100), length)
    check(len(minima) == 2048, 'independent phase census')
    check([max(v for k, v in minima.items() if k[0] == r) for r in range(4)] == [8, 9, 10, 7],
          'independent full-span thresholds')
    words = accepted = output_fibers = 0
    for width in range(7):
        for word in product(range(8), repeat=width):
            words += 1
            rows = [sum(((x >> j) & 1) << bit for bit, x in enumerate(word)) for j in range(3)]
            if any(row.bit_count() % 4 for row in rows):
                continue
            if any((rows[j] & rows[k]).bit_count() % 2 for j, k in ((0, 1), (0, 2), (1, 2))):
                continue
            accepted += 1
            check(len(span(rows)) <= 4, 'doubly-even length-six bound')
            images = Counter()
            for g in group:
                images[tuple(g[x] for x in word)] += coefficient[g]
            check(not any(images.values()), 'literal short tensor column')
            output_fibers += len(images)
    check(words == sum(8 ** f for f in range(7)), 'complete ordered word census')
    for residue, width in enumerate((8, 9, 10, 7)):
        word = (0,) * (width - 7) + tuple(range(1, 8))
        check(sum(coefficient[g] for g in group if tuple(g[x] for x in word) == word) == 6,
              'literal threshold diagonal')
    print('PASS_THREE_AXIS_SEPARATE_AUDIT ' + json.dumps(dict(
        group_elements=len(group), normal_forms=65536, characters=len(minima),
        ordered_words=words, zero_phase_words=accepted, exact_output_fibers=output_fibers,
        rederived_coefficients=[str(x) for x in solution], cutoff=7), sort_keys=True))

if __name__ == '__main__':
    main()
