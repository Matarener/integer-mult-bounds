#!/usr/bin/env python3
"""Check shorter native phase witnesses with exact binary arithmetic.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product, combinations
import json


def require(c, message):
    if not c:
        raise ValueError(message)


def rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            k = v.bit_length() - 1
            if k in pivots:
                v ^= pivots[k]
            else:
                pivots[k] = v
                break
    return len(pivots)


def affine_dimension(points):
    return rank([x ^ points[0] for x in points]) if points else -1


def pairing(rows, x, y):
    return sum(((rows[j] & y).bit_count() & 1) for j in range(len(rows)) if x >> j & 1) & 1


def gram(columns, n):
    return [sum((sum(((v >> j) & 1) * ((v >> k) & 1) for v in columns) & 1) << k
                for k in range(n)) for j in range(n)]


def factor_nonalternating(rows):
    n = len(rows)
    require(any(rows[j] >> j & 1 for j in range(n)), 'alternating input')
    todo = [1 << j for j in range(n)]
    units, pairs = [], []
    while todo:
        pivot = next((x for x in todo if pairing(rows, x, x)), None)
        if pivot is not None:
            units.append(pivot)
            todo.remove(pivot)
            todo = [x ^ pivot if pairing(rows, x, pivot) else x for x in todo]
            continue
        pair = next(((x, y) for x, y in combinations(todo, 2) if pairing(rows, x, y)), None)
        if pair is None:
            break
        x, y = pair
        todo.remove(x)
        todo.remove(y)
        todo = [z ^ (x if pairing(rows, z, y) else 0) ^ (y if pairing(rows, z, x) else 0) for z in todo]
        pairs.append(pair)
    for x, y in pairs:
        z = units.pop()
        units.extend((z ^ x, z ^ y, z ^ x ^ y))
    columns = [sum(((row & v).bit_count() & 1) << j for j, row in enumerate(rows)) for v in units]
    require(len(columns) == rank(rows) and gram(columns, n) == rows, 'binary factorization')
    return columns


def statistics(points, n):
    u = tuple(sum(x >> j & 1 for x in points) % 4 for j in range(n))
    v = tuple(sum((x >> j & 1) * (x >> k & 1) for x in points) % 2 for j, k in combinations(range(n), 2))
    return len(points) % 4, u, v


def witness(n, u, v, width):
    require(n >= 2 and width >= 2 * n + 3, 'outside general witness domain')
    columns = [1 << j for j in range(n)]
    parity = sum((x & 1) << j for j, x in enumerate(u))
    if parity == (1 << n) - 1:
        columns[0] ^= 2
    points = [0] + columns
    M = [(u[j] & 1) << j for j in range(n)]
    for bit, (j, k) in zip(v, combinations(range(n), 2)):
        M[j] |= bit << k
        M[k] |= bit << j
    start = gram(columns, n)
    points += factor_nonalternating([a ^ b for a, b in zip(M, start)])
    current = statistics(points, n)[1]
    z = sum((((u[j] - current[j]) % 4) // 2) << j for j in range(n))
    if z:
        points += [z, z]
    require(len(points) <= 2 * n + 3, 'witness width')
    points += [0] * (width - len(points))
    return points


def count_statistics(counts):
    return (sum(counts) % 4,
            tuple(sum(counts[x] * (x >> j & 1) for x in range(8)) % 4 for j in range(3)),
            tuple(sum(counts[x] * (x >> j & 1) * (x >> k & 1) for x in range(8)) % 2
                  for j, k in combinations(range(3), 2)))


def three_axis_minima():
    minima, chosen = {}, {}
    for counts in product(range(4), repeat=8):
        support = [x for x in range(8) if counts[x]]
        length = sum(counts) + 4 * (3 - affine_dimension(support))
        key = count_statistics(counts)
        if length < minima.get(key, 100):
            minima[key], chosen[key] = length, counts
    require(len(minima) == 2048, 'complete character inventory')
    for key, counts in chosen.items():
        counts = list(counts)
        support = [x for x in range(8) if counts[x]]
        while affine_dimension(support) < 3:
            x = next(x for x in range(8) if affine_dimension(support + [x]) > affine_dimension(support))
            counts[x] += 4
            support.append(x)
        require(sum(counts) == minima[key] and count_statistics(counts) == key, 'minimum witness')
    direct = {}
    compositions = 0
    for width in range(11):
        for bars in combinations(range(width + 7), 7):
            endpoints = (-1,) + bars + (width + 7,)
            counts = tuple(endpoints[i + 1] - endpoints[i] - 1 for i in range(8))
            compositions += 1
            if affine_dimension([x for x in range(8) if counts[x]]) == 3:
                direct.setdefault(count_statistics(counts), width)
    require(direct == minima, 'independent total-width census')
    thresholds = [max(value for key, value in minima.items() if key[0] == r) for r in range(4)]
    require(thresholds == [8, 9, 10, 7], 'three-axis residue thresholds')
    return thresholds, compositions


def phase(points, n, c, a, b):
    return sum(c + sum(a[j] * (x >> j & 1) for j in range(n))
               + 2 * sum(bit * (x >> j & 1) * (x >> k & 1)
                         for bit, (j, k) in zip(b, combinations(range(n), 2))) for x in points) % 4


def general_checks():
    factors = characters = phase_checks = 0
    for n in range(1, 5):
        positions = list(combinations(range(n), 2)) + [(j, j) for j in range(n)]
        for bits in product(range(2), repeat=len(positions)):
            rows = [0] * n
            for bit, (j, k) in zip(bits, positions):
                rows[j] |= bit << k
                rows[k] |= bit << j
            if any(rows[j] >> j & 1 for j in range(n)):
                factor_nonalternating(rows)
                factors += 1
    for n in (2, 3):
        for u in product(range(4), repeat=n):
            for v in product(range(2), repeat=n * (n - 1) // 2):
                for r in range(4):
                    F = 2 * n + 3
                    width = F + (r - F) % 4
                    points = witness(n, u, v, width)
                    require(statistics(points, n) == (r, u, v) and affine_dimension(points) == n, 'complete witness contract')
                    characters += 1
                    for seed in range(8):
                        c = seed % 4
                        a = [(seed + 3 * j) % 4 for j in range(n)]
                        b = [(seed + j) % 2 for j in range(len(v))]
                        expected = (r * c + sum(x * y for x, y in zip(u, a)) + 2 * sum(x * y for x, y in zip(v, b))) % 4
                        require(phase(points, n, c, a, b) == expected, 'literal Gaussian phase')
                        phase_checks += 1
    for n in range(4, 18):
        for seed in range(32):
            u = tuple((seed * (j + 1) + j * j) % 4 for j in range(n))
            v = tuple(((seed + 1) * (j + 3) + j // 3) % 2 for j in range(n * (n - 1) // 2))
            width = 2 * n + 3 + seed % 4
            points = witness(n, u, v, width)
            require(statistics(points, n) == (width % 4, u, v) and affine_dimension(points) == n, 'larger witness')
            characters += 1
    return factors, characters, phase_checks


def main():
    factors, characters, phase_checks = general_checks()
    thresholds, compositions = three_axis_minima()
    controls = 0
    try:
        factor_nonalternating([2, 1])
    except ValueError:
        controls += 1
    else:
        raise ValueError('alternating input accepted')
    for n in (2, 3, 9):
        u, v = (1,) * n, (0,) * (n * (n - 1) // 2)
        points = witness(n, u, v, 2 * n + 3)
        require(phase(points, n, 1, [0] * n, [0] * len(v)) == len(points) % 4, 'constant phase')
        controls += 1
        changed = points + [1, 1]
        require(statistics(changed, n)[1] != u and gram(changed, n) == gram(points, n), 'parity-only false witness')
        controls += 1
    print('PASS_SHORTER_NATIVE_PHASE_WITNESS ' + json.dumps(dict(binary_factorizations=factors,
        constructed_characters=characters, literal_phase_checks=phase_checks, normal_forms=65536,
        independent_compositions=compositions, three_axis_characters=2048,
        three_axis_residue_thresholds=thresholds, controls=controls), sort_keys=True))


if __name__ == '__main__':
    main()
