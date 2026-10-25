#!/usr/bin/env python3
"""Exact certificates for the sharp three-axis monomial cutoff.

Joseph Anglada with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable or floating-point acceptance.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
THRESHOLDS = (8, 9, 10, 7)
WEIGHTS = {1: 6, 2: -2, 3: 0, 4: 2, 7: -1}
IDENTITY = tuple(range(8))
SOURCE_PINS = {
    'research/native-tensor-cutoff/PROOF.md': 'b2d31ea52b652f43cc8576affde6092a884d2832820221a43933e7e27dc07041',
    'research/three-axis-sharp-cutoff/inputs/PR5529-README.md': 'abc1224cb79a7056d476636522100a375dbe7d51f2e9a985e667d0d7729f3212',
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)

def compose(g, h):
    return tuple(g[h[x]] for x in range(8))

def linear_group():
    result = []
    for columns in product(range(1, 8), repeat=3):
        if binary_rank(columns) != 3:
            continue
        result.append(tuple((columns[0] if x & 1 else 0)
                            ^ (columns[1] if x & 2 else 0)
                            ^ (columns[2] if x & 4 else 0) for x in range(8)))
    require(len(result) == len(set(result)) == 168, 'GL3 inventory')
    return result

def element_order(g):
    power = IDENTITY
    for order in range(1, 8):
        power = compose(power, g)
        if power == IDENTITY:
            return order
    raise ValueError('unexpected GL3 order')

def planes():
    return [tuple(x for x in range(8) if (x & normal).bit_count() % 2 == 0)
            for normal in range(1, 8)]

def coefficient_certificate(group, weights=WEIGHTS):
    coefficients = {g: weights[element_order(g)] for g in group}
    expected = {(1, 2, 2, 2): 1, (2, 2, 4, 4): 3,
                (2, 3, 3, 4): 12, (3, 3, 3, 3): 2, (3, 4, 7, 7): 24}
    coset_checks = 0
    for plane in planes():
        subgroup = [g for g in group if all(g[x] == x for x in plane)]
        require(len(subgroup) == 4, 'plane stabilizer')
        unseen, types = set(group), Counter()
        while unseen:
            g = min(unseen)
            coset = {compose(g, h) for h in subgroup}
            require(len(coset) == 4 and coset <= unseen, 'coset partition')
            unseen -= coset
            types[tuple(sorted(element_order(h) for h in coset))] += 1
            require(sum(coefficients[h] for h in coset) == 0, 'nonzero plane coset sum')
            coset_checks += 1
        require(types == expected, 'coset order census')
    convolution = Counter()
    for g, a in coefficients.items():
        for h, b in coefficients.items():
            convolution[compose(g, h)] += a * b
    require(all(convolution[g] == 56 * coefficients[g] for g in group), 'idempotent identity')
    require(coefficients[IDENTITY] == 6, 'nonzero identity coefficient')
    return coefficients, coset_checks, expected

def statistics(counts):
    return (sum(counts) % 4,
            *(sum(counts[x] for x in range(8) if x >> j & 1) % 4 for j in range(3)),
            *(sum(counts[x] for x in range(8) if (x >> j & 1) and (x >> k & 1)) % 2
              for j, k in combinations(range(3), 2)))

def multiplicities(width):
    for bars in combinations(range(width + 7), 7):
        ends = (-1,) + bars + (width + 7,)
        yield tuple(ends[j + 1] - ends[j] - 1 for j in range(8))

def support(counts):
    return tuple(x for x in range(8) if counts[x])

def affine_rank(points):
    return binary_rank([x ^ points[0] for x in points]) if points else -1

def literal_coset_sums(group, coefficients, points):
    sums = Counter()
    for g in group:
        sums[tuple(g[x] for x in points)] += coefficients[g]
    return sums

def phase_projector(counts, residue, quadratic=True):
    total = [0, 0]
    for constant, a0, a1, a2 in product(range(4), repeat=4):
        for b01, b02, b12 in product(range(2), repeat=3):
            exponent = -residue * constant
            for x, count in enumerate(counts):
                bits = [(x >> j) & 1 for j in range(3)]
                q = constant + a0 * bits[0] + a1 * bits[1] + a2 * bits[2]
                if quadratic:
                    q += 2 * (b01 * bits[0] * bits[1] + b02 * bits[0] * bits[2]
                              + b12 * bits[1] * bits[2])
                exponent += count * q
            re, im = ((1, 0), (0, 1), (-1, 0), (0, -1))[exponent % 4]
            total[0] += re
            total[1] += im
    return tuple(total)

def census(group, coefficients):
    minima = {}
    total = zero_phase = literal_fibers = 0
    quadratic_control = None
    for width in range(11):
        for counts in multiplicities(width):
            total += 1
            key, points = statistics(counts), support(counts)
            if affine_rank(points) == 3:
                minima.setdefault(key, width)
            if width <= 6 and not any(key[1:]):
                zero_phase += 1
                weights = [sum(counts[x] for x in range(8) if (x & word).bit_count() % 2)
                           for word in range(1, 8)]
                require(all(w % 4 == 0 for w in weights), 'doubly even code')
                require(sum(weights) == 4 * sum(counts[1:]), 'codeword mass identity')
                require(binary_rank(points) <= 2, 'short code rank')
                sums = literal_coset_sums(group, coefficients, points)
                require(not any(sums.values()), 'lower-width operator fiber')
                literal_fibers += len(sums)
            if width == 6 and not any(key[1:4]) and any(key[4:]) and binary_rank(points) == 3:
                quadratic_control = counts
    require(total == 43758 and len(minima) == 2048, 'complete composition/character census')
    maxima = tuple(max(v for k, v in minima.items() if k[0] == r) for r in range(4))
    require(maxima == THRESHOLDS, 'full-span upper thresholds')
    require(quadratic_control is not None, 'quadratic control fixture')
    return minima, zero_phase, literal_fibers, quadratic_control

def main():
    for name, digest in SOURCE_PINS.items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'source drift: ' + name)
    group = linear_group()
    require(Counter(map(element_order, group)) == {1: 1, 2: 21, 3: 56, 4: 42, 7: 48}, 'element orders')
    coefficients, coset_checks, types = coefficient_certificate(group)
    minima, zero_phase, fibers, bad_quadratic = census(group, coefficients)
    for residue, width in enumerate(THRESHOLDS):
        counts = (width - 7,) + (1,) * 7
        require(statistics(counts) == (residue, 0, 0, 0, 0, 0, 0), 'threshold phase')
        require(phase_projector(counts, residue) == (2048, 0), 'literal phase projector')
        require(phase_projector(counts, (residue + 1) % 4) == (0, 0), 'wrong-residue rejection')
        require(literal_coset_sums(group, coefficients, support(counts))[support(counts)] == 6,
                'nonzero threshold matrix entry')
    controls = 0
    for order in (1, 2, 3, 4, 7):
        try:
            coefficient_certificate(group, {**WEIGHTS, order: WEIGHTS[order] + 1})
        except ValueError:
            controls += 1
        else:
            raise ValueError('coefficient mutation escaped')
    require(phase_projector(bad_quadratic, 2) == (0, 0), 'quadratic rejection')
    require(phase_projector(bad_quadratic, 2, quadratic=False) == (2048, 0), 'quadratic omission control')
    require(literal_coset_sums(group, coefficients, support(bad_quadratic))[support(bad_quadratic)] == 6,
            'quadratic omission changes operator')
    controls += 1
    report = dict(status='PASS_THREE_AXIS_SHARP_CUTOFF', cutoff=7,
                  residue_thresholds=list(THRESHOLDS), sufficient_and_sharp_window=[7, 8, 9, 10],
                  gl3_elements=168, plane_cosets=coset_checks,
                  coset_order_types={','.join(map(str, k)): v for k, v in sorted(types.items())},
                  multiplicities=43758, phase_characters=len(minima), lower_zero_phase_multisets=zero_phase,
                  exact_lower_image_fibers=fibers, threshold_entries=4,
                  rejection_controls=controls, no_new_kappa=True)
    require(report == json.loads((PACKAGE / 'RESULT.json').read_text(encoding='utf-8')), 'complete result mismatch')
    print('PASS_THREE_AXIS_SHARP_CUTOFF ' + json.dumps(report, sort_keys=True))

if __name__ == '__main__':
    main()
