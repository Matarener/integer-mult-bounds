#!/usr/bin/env python3
"""Literal position enumeration and matrices; independent of period formulas.
SHIN09-git with OpenAI Codex assistance. Apache-2.0.
"""
from bisect import bisect_left, bisect_right
from collections import Counter
from itertools import combinations
from math import factorial


def words(n):
    positions = tuple(range(3 * n))
    for ones in combinations(positions, n):
        one_set = set(ones)
        remaining = tuple(x for x in positions if x not in one_set)
        for twos in combinations(remaining, n):
            two_set = set(twos)
            threes = tuple(x for x in remaining if x not in two_set)
            word = tuple(1 if x in one_set else 2 if x in two_set else 3
                         for x in positions)
            # Sum over the middle-letter positions; no chronological DP.
            pairs = [(bisect_left(ones, j), n - bisect_right(threes, j))
                     for j in twos]
            yield word, (sum(a for a, b in pairs), sum(b for a, b in pairs),
                         sum(a * b for a, b in pairs))


def matrix_counts(word):
    # Full lower unitriangular action on the four arbitrary scalar input roles.
    matrix = [[int(i == j) for j in range(4)] for i in range(4)]
    for letter in word:
        matrix[letter] = [a + b for a, b in
                          zip(matrix[letter], matrix[letter - 1])]
    return matrix[2][0], matrix[3][1], matrix[3][0]


def least_period(word):
    # Search all possible shifts, without the theorem's divisor restriction.
    for k in range(1, len(word) + 1):
        if word == word[k:] + word[:k]:
            return k
    raise ValueError("missing identity rotation")


def literal_census(m):
    rows = [0] * m
    fixed = {d: [0] * m for d in range(1, m + 1) if m % d == 0}
    periods = [Counter() for _ in range(m)]
    necklaces = [set() for _ in range(m)]
    total = checked_rotations = matrix_checks = 0
    for word, (a, b, t) in words(m):
        total += 1
        if m <= 3:
            if matrix_counts(word) != (a, b, t):
                raise ValueError("position/matrix count disagreement")
            matrix_checks += 1
        if a % m or b % m:
            continue
        c = t % m
        rows[c] += 1
        period = least_period(word)
        periods[c][len(word) // period] += 1
        rotations = [word[k:] + word[:k] for k in range(len(word))]
        necklaces[c].add(min(rotations))
        for rotated in rotations:
            ra, rb, rt = matrix_counts(rotated)
            if ra % m or rb % m or rt % m != c:
                raise ValueError("literal rotation changed correctness")
            checked_rotations += 1
        for d in fixed:
            k = len(word) // d
            if word == word[k:] + word[:k]:
                fixed[d][c] += 1
    expected = factorial(3 * m) // factorial(m)**3
    if total != expected:
        raise ValueError("literal multinomial mass")
    return dict(counts=rows, fixed=fixed, exact=periods,
                orbits=[len(x) for x in necklaces], total=total,
                rotations=checked_rotations, matrix_checks=matrix_checks)


def chronological_counts(word):
    n1 = n2 = a = b = t = 0
    for letter in word:
        if letter == 1:
            n1 += 1
        elif letter == 2:
            n2 += 1
            a += n1
        else:
            b += n2
            t += a
    return a, b, t


def residue_dp(m):
    # Rolling first-letter layers, retaining all three residues and all masses.
    previous = {}
    for i in range(m + 1):
        current = {}
        for j in range(m + 1):
            for k in range(m + 1):
                result = Counter()
                if i == j == k == 0:
                    result[(0, 0, 0)] = 1
                if i:
                    result.update(previous[j, k])
                if j:
                    for (a, b, t), value in current[j - 1, k].items():
                        result[((a + i) % m, b, t)] += value
                if k:
                    for (a, b, t), value in current[j, k - 1].items():
                        result[(a, (b + j) % m, (t + a) % m)] += value
                mass = factorial(i + j + k) // (factorial(i) * factorial(j) * factorial(k))
                if sum(result.values()) != mass:
                    raise ValueError("DP multinomial mass")
                current[j, k] = result
        previous = current
    return [previous[m, m][0, 0, c] for c in range(m)]
