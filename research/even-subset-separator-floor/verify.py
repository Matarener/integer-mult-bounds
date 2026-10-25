#!/usr/bin/env python3
"""Check the exact binary separator class, not a complete native circuit.

Ali Romman, substantial OpenAI Codex assistance; Apache-2.0.
The even-subset kernel is from Cinna Davis's PR2225. The common-span
obstruction and historical frame limits retain their prior attribution.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def dot(x, y):
    return parity(x & y)


def basis(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return list(pivots.values())


def contains(rows, x):
    return len(basis(rows + [x])) == len(basis(rows))


def gram_rank(rows):
    return len(basis([sum(dot(x, y) << j for j, y in enumerate(rows)) for x in rows]))


def solve(equations, rhs):
    pivots = {}
    for x, value in zip(equations, rhs):
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                row, bit = pivots[p]
                x ^= row
                value ^= bit
            else:
                pivots[p] = (x, value)
                break
        if not x:
            need(not value, 'Consistent binary constraints')
    out = 0
    for p in sorted(pivots):
        row, bit = pivots[p]
        out |= (bit ^ dot(row, out)) << p
    need(all(dot(row, out) == bit for row, bit in zip(equations, rhs)), 'Binary solution')
    return out


def label(k, selector, constant=True):
    return int(constant) | sum(1 << (1 + 2*i + ((selector >> i) & 1)) for i in range(k))


def delta(k, selector):
    return sum(3 << (1 + 2*i) for i in range(k) if (selector >> i) & 1)


def choose(x, d):
    out = F(1)
    for j in range(d):
        out *= (x - j) / (j + 1)
    return out


def kernel(k, distance):
    return choose(F(k-distance, 2), k//2)


def matrix_rank(matrix):
    rows = [row[:] for row in matrix]
    rank = 0
    for j in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][j]
        rows[rank] = [x/scale for x in rows[rank]]
        for i in range(rank+1, len(rows)):
            if rows[i][j]:
                value = rows[i][j]
                rows[i] = [x-value*y for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def cube(k):
    need(k >= 2 and k % 2 == 0, 'Even k at least two')
    halves = [[s for s in range(1 << k) if parity(s) == p] for p in (0, 1)]
    return halves, [[-kernel(k, (a^b).bit_count()) for b in halves[1]] for a in halves[0]]


def support(k, selectors):
    directions = basis([s ^ selectors[0] for s in selectors])
    labels = [label(k, s) for s in selectors]
    radicals = [delta(k, v) for v in directions]
    need(all(parity(v) == 0 for v in directions), 'One parity support')
    need(len(basis(labels)) == len(directions)+1, 'Support span dimension')
    need(gram_rank(basis(labels)) == 1, 'Support form rank one')
    need(all(dot(r, q) == 0 for r in radicals for q in labels), 'Support radical')
    return {'selectors': selectors, 'labels': labels, 'radicals': radicals, 'd': len(directions)}


def all_supports(k, selectors):
    return [support(k, [s for j, s in enumerate(selectors) if (mask >> j) & 1])
            for mask in range(1, 1 << len(selectors))]


def feasible(e, f):
    return len(basis(e['radicals'] + f['radicals'])) == e['d'] + f['d']


def check_hulls(e, f, u, v):
    need(len(basis(u)) == len(u) == gram_rank(u), 'Nondegenerate source hull')
    need(len(basis(v)) == len(v) == gram_rank(v), 'Nondegenerate target hull')
    need(all(contains(u, x) for x in e['labels']), 'Source containment')
    need(all(contains(v, x) for x in f['labels']), 'Target containment')
    need(all(dot(x, y) == 0 for x in u for y in v), 'Orthogonal endpoint hulls')


def hulls(e, f):
    need(feasible(e, f), 'Disjoint support radicals')
    q, t = e['labels'][0], f['labels'][0]
    re, rf = e['radicals'], f['radicals']
    u = [q] + re
    equations = [q, t] + rf + re
    for i in range(len(re)):
        u.append(solve(equations, [0]*(2+len(rf)) + [int(i == j) for j in range(len(re))]))
    v = [t] + rf
    equations = [t] + u + rf
    for i in range(len(rf)):
        v.append(solve(equations, [0]*(1+len(u)) + [int(i == j) for j in range(len(rf))]))
    check_hulls(e, f, u, v)
    need((len(u), len(v)) == (2*e['d']+1, 2*f['d']+1), 'Minimum endpoint dimensions')
    return u, v


def row_hull(k, selector):
    def swap(x):
        for i in range(k):
            if (selector >> i) & 1 and dot(x, 3 << (1+2*i)):
                x ^= 3 << (1+2*i)
        return x
    b = label(k, 0)
    last = delta(k, 1 << (k-1))
    rows = [b ^ last]
    for i in range(k-1):
        rows.extend([1 << (2+2*i), (1 << (1+2*i)) ^ last])
    return [swap(b)], [swap(x) for x in rows]


def check_row_stars(k, corrupt=None):
    halves, block = cube(k)
    n = len(halves[0])
    factors = []
    charge = 0
    for i, s in enumerate(halves[0]):
        e, f = support(k, [s]), support(k, halves[1])
        u, v = row_hull(k, s)
        if corrupt == 'missing_partner' and i == 0:
            v.pop()
        check_hulls(e, f, u, v)
        need(all(dot(x, y) == int(a == b) for a, x in enumerate(u+v)
                 for b, y in enumerate(u+v)), 'Explicit orthonormal hull basis')
        charge += len(u)+len(v)
        source = [F(int(j == i)) for j in range(n)]
        target = block[i][:]
        if corrupt == 'coefficient' and i == 0:
            target[0] += 1
        if corrupt != 'missing_row' or i != 0:
            factors.append((source, target))
    actual = [[sum(a[i]*b[j] for a, b in factors) for j in range(n)] for i in range(n)]
    need(actual == block, 'Exact row-star reconstruction')
    need(len(factors) == n and charge == 2*k*n, 'Sharp row-star counts')
    return {'k': k, 'terms': n, 'endpoint_dimension_sum': charge}


def walsh(k):
    values = [kernel(k, z.bit_count()) for z in range(1 << k)]
    step = 1
    while step < len(values):
        for start in range(0, len(values), 2*step):
            for i in range(start, start+step):
                a, b = values[i], values[i+step]
                values[i], values[i+step] = a+b, a-b
        step *= 2
    expected = [F(2 if s.bit_count() < k//2 else 1 if s.bit_count() == k//2 else 0)
                for s in range(1 << k)]
    need(values == expected, 'Exact Walsh spectrum')
    return {'k': k, 'kernel_eigenvalue_multiplicities': dict(sorted(Counter(map(str, values)).items()))}


def support_census(k):
    halves, block = cube(k)
    need(all(x for row in block for x in row), 'Full cross-block support')
    left, right = [all_supports(k, half) for half in halves]
    histogram, max_area = Counter(), 0
    n = len(halves[0])
    for e in left:
        for f in right:
            common = (len(basis(e['labels'])) + len(basis(f['labels']))
                      - len(basis(e['labels']+f['labels'])))
            need((common == 0) == feasible(e, f), 'Literal common-span criterion')
            if not feasible(e, f):
                continue
            u, v = hulls(e, f)
            area = len(e['selectors'])*len(f['selectors'])
            need(area <= n, 'Rectangle capacity')
            need((len(u)+len(v))*n >= 2*k*area, 'Endpoint dimension density')
            histogram[f"{e['d']},{f['d']}"] += 1
            max_area = max(max_area, area)
    return {'k': k, 'rectangles': len(left)*len(right), 'feasible_rectangles': sum(histogram.values()),
            'maximum_area': max_area, 'direction_dimension_histogram': dict(sorted(histogram.items()))}


def subspace_oracle():
    # This oracle enumerates vector sets. It does not use the radical criterion.
    spaces, frontier = {frozenset([0])}, [frozenset([0])]
    while frontier:
        old = frontier.pop()
        for x in range(32):
            new = old | frozenset(v^x for v in old)
            if new not in spaces:
                spaces.add(new)
                frontier.append(new)
    need(len(spaces) == 374, 'Complete five-dimensional subspace count')
    good = []
    for space in spaces:
        rows = basis(sorted(space))
        if gram_rank(rows) == len(rows):
            good.append((space, rows))
    halves, _ = cube(2)
    left, right = [all_supports(2, half) for half in halves]
    accepted = 0
    for e in left:
        for f in right:
            minimum = None
            for us, u in good:
                if not all(x in us for x in e['labels']):
                    continue
                for vs, v in good:
                    if (all(x in vs for x in f['labels'])
                            and all(dot(x, y) == 0 for x in u for y in v)):
                        cost = len(u)+len(v)
                        minimum = cost if minimum is None else min(minimum, cost)
            need((minimum is not None) == feasible(e, f), 'Independent separator existence')
            if minimum is not None:
                need(minimum == 2*(e['d']+f['d'])+2, 'Independent minimum hull charge')
                accepted += 1
    return {'ambient_dimension': 5, 'all_subspaces': len(spaces),
            'nondegenerate_subspaces': len(good), 'support_pairs': 9, 'feasible_pairs': accepted}


def star_targets():
    cases = []
    for n in range(3, 9):
        for k in range(2, n, 2):
            ports = [sum(1 << i for i in item) for item in combinations(range(n), k)]
            stars = 0
            for a in range(k):
                for item in combinations(range(n), a):
                    j = sum(1 << i for i in item)
                    sources = [s for s in ports if s & j == j]
                    actual = [t for t in ports if all(dot(s, t) == 1 for s in sources)]
                    count = comb(a, n-k) if n % 2 and a >= n-k else 0
                    need(len(actual) == count, 'Exact star-readable target count')
                    outside = ((1 << n)-1) ^ j
                    expected = [t for t in ports if n % 2 and t & outside == outside]
                    need(actual == expected, 'Exact star-readable target set')
                    stars += 1
            cases.append({'n': n, 'k': k, 'stars': stars})
    return cases


def controls():
    failures = []
    def reject(name, action, reason):
        try:
            action()
        except ValueError as exc:
            need(str(exc) == reason, 'Wrong control rejection: '+name+': '+str(exc))
            failures.append({'mutation': name, 'reason': reason})
        else:
            raise ValueError('Accepted false control: '+name)
    reject('odd_k', lambda: cube(3), 'Even k at least two')
    reject('zero_k', lambda: cube(0), 'Even k at least two')
    reject('omit_constant_coordinate',
           lambda: need(dot(label(4, 0, False), label(4, 0, False)) == 1, 'Norm-one label'),
           'Norm-one label')
    halves, _ = cube(4)
    e, f = [support(4, half) for half in halves]
    need(all(dot(x, y) == 0 for x in e['labels'] for y in f['labels']), 'Orthogonality-only fixture')
    reject('orthogonality_without_separation', lambda: hulls(e, f), 'Disjoint support radicals')
    reject('accept_degenerate_hulls', lambda: check_hulls(e, f, basis(e['labels']), basis(f['labels'])),
           'Nondegenerate source hull')
    reject('omit_hull_partner', lambda: check_row_stars(4, 'missing_partner'), 'Target containment')
    reject('wrong_scalar_coefficient', lambda: check_row_stars(4, 'coefficient'), 'Exact row-star reconstruction')
    reject('omit_row_star', lambda: check_row_stars(4, 'missing_row'), 'Exact row-star reconstruction')
    return failures


def authenticate():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    checked = []
    for record in manifest['files']:
        if record['usage'] == 'input':
            need(sha256((ROOT/record['path']).read_bytes()).hexdigest() == record['sha256'],
                 'Changed live input: '+record['path'])
            checked.append(record['path'])
    return checked


def result():
    sources = authenticate()
    ranks = []
    for k in (2, 4, 6):
        halves, block = cube(k)
        rank = matrix_rank(block)
        n = len(halves[0])
        need(rank == n-comb(k, k//2)//2, 'Literal rational cross-block rank')
        for a in range(1 << k):
            for b in range(1 << k):
                need(dot(label(k, a), label(k, b)) == (1 ^ parity(a^b)), 'Literal cube Gram identity')
        ranks.append({'k': k, 'block_size': n, 'scalar_rank': rank,
                      'minimum_factors': n, 'minimum_endpoint_dimension_sum': 2*k*n})
    return {'status': 'PASS_EVEN_SUBSET_SEPARATOR_FLOOR',
            'scope': 'Separate scalar rank-one factors with orthogonal nondegenerate binary endpoint hulls; no full native circuit or kappa claim.',
            'live_inputs': sources, 'rational_rank_checks': ranks,
            'walsh_spectra': [walsh(k) for k in range(2, 13, 2)],
            'support_censuses': [support_census(k) for k in (2, 4)],
            'independent_subspace_oracle': subspace_oracle(),
            'attaining_row_stars': [check_row_stars(k) for k in (2, 4, 6)],
            'star_readability': star_targets(), 'rejected_controls': controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    computed = result()
    payload = json.dumps(computed, sort_keys=True, indent=2)+'\n'
    if args.write_result:
        need(args.write_result.resolve() != (HERE/'RESULT.json').resolve(), 'Write to a separate review path')
        args.write_result.write_text(payload)
    else:
        need(computed == json.loads((HERE/'RESULT.json').read_text()), 'Saved exact receipt differs')
    print(computed['status'])


if __name__ == '__main__':
    main()
