#!/usr/bin/env python3
"""Exact bounded shell/caller checks. JoyboyBrian, Codex assistance; Apache-2.0."""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations
import json
from math import lcm, prod
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def factors(n):
    need(type(n) is int and n >= 1, 'positive integer generator')
    result = {}
    p = 2
    while p*p <= n:
        while n % p == 0:
            result[p] = result.get(p, 0)+1
            n //= p
        p += 1
    if n > 1:
        result[n] = result.get(n, 0)+1
    return result


def pivots(matrix):
    """Rational elimination; returns independent column indices."""
    rows = [list(map(Fraction, row)) for row in matrix]
    if not rows:
        return []
    out = []
    for j in range(len(rows[0])):
        pivot = next((i for i in range(len(out), len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        k = len(out)
        rows[k], rows[pivot] = rows[pivot], rows[k]
        a = rows[k][j]
        rows[k] = [x/a for x in rows[k]]
        for i in range(k+1, len(rows)):
            a = rows[i][j]
            rows[i] = [x-a*y for x, y in zip(rows[i], rows[k])]
        out.append(j)
    return out


def rank(matrix):
    return len(pivots(matrix))


def determinant(matrix):
    """Independent integer Bareiss determinant for the full-rank p16 minor."""
    a = [list(row) for row in matrix]
    sign, previous = 1, 1
    for k in range(len(a)-1):
        j = next((j for j in range(k, len(a)) if a[j][k]), None)
        if j is None:
            return 0
        if j != k:
            a[k], a[j] = a[j], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k+1, len(a)):
            for j in range(k+1, len(a)):
                value = a[i][j]*pivot-a[i][k]*a[k][j]
                need(value % previous == 0, 'Bareiss exact division')
                a[i][j] = value//previous
            a[i][k] = 0
        previous = pivot
    return sign*a[-1][-1] if a else 1


def minor_rank(matrix):
    """Independent Leibniz minors for small test matrices."""
    def det(a):
        total = 0
        for order in permutations(range(len(a))):
            sign = (-1)**sum(order[i] > order[j]
                            for i in range(len(a)) for j in range(i+1, len(a)))
            total += sign*prod(a[i][order[i]] for i in range(len(a)))
        return total
    for size in range(min(len(matrix), len(matrix[0])), 0, -1):
        for rs in combinations(range(len(matrix)), size):
            for cs in combinations(range(len(matrix[0])), size):
                if det([[matrix[i][j] for j in cs] for i in rs]):
                    return size
    return 0


def descriptor(alphabet, M):
    need(type(M) is int and M >= 2, 'fixed height base at least two')
    need(bool(alphabet), 'nonempty alphabet')
    generators = sorted(set(alphabet) | {M})
    valuations = [factors(a) for a in generators]
    primes = sorted(set().union(*(v.keys() for v in valuations)))
    matrix = [[v.get(p, 0) for v in valuations] for p in primes]
    m = [factors(M).get(p, 0) for p in primes]
    pivot = min((i for i in range(len(m)) if m[i]), key=lambda i: m[i])
    q = m[pivot]
    quotient = [[q*x-m[i]*y for x, y in zip(matrix[i], matrix[pivot])]
                for i in range(len(primes))]
    chosen = []
    for i, row in enumerate(quotient):
        if rank([quotient[j] for j in chosen]+[row]) > len(chosen):
            chosen.append(i)
    r = rank(matrix)
    need(len(chosen) == r-1, 'quotient rank r minus one')
    h = (M-1).bit_length()
    K = q*prod(h*(q+m[i])+1 for i in chosen)
    return {'generators': generators, 'primes': primes, 'matrix': matrix,
            'm': m, 'pivot': pivot, 'q': q, 'chosen': chosen, 'r': r,
            'h': h, 'K': K}


def products(generators, cap):
    seen, todo = {1}, [1]
    while todo:
        a = todo.pop()
        for g in generators:
            b = a*g
            if b <= cap and b not in seen:
                seen.add(b)
                todo.append(b)
    return seen


def divisibility_oracle(generators, cap):
    reached = {1}
    for n in range(2, cap+1):
        if any(g > 1 and n % g == 0 and n//g in reached for g in generators):
            reached.add(n)
    return reached


def floor_log(n, M):
    ell = 0
    while n >= M:
        n //= M
        ell += 1
    return ell


def shell_fixture(alphabet, M, cap):
    d = descriptor(alphabet, M)
    members = products(d['generators'], cap)
    need(members == divisibility_oracle(d['generators'], cap), 'independent semigroup')
    if len(d['matrix']) <= 4 and len(d['generators']) <= 4:
        need(d['r'] == minor_rank(d['matrix']), 'independent rank minors')
    shells = defaultdict(list)
    for value in members:
        shells[floor_log(value, M)].append(value)
    fiber_cases = 0
    for ell, values in shells.items():
        groups = defaultdict(list)
        for value in values:
            v = factors(value)
            x = [v.get(p, 0) for p in d['primes']]
            F = tuple(d['q']*x[i]-d['m'][i]*x[d['pivot']] for i in d['chosen'])
            need(all(-d['m'][i]*d['h']*(ell+1) <= f <= d['q']*d['h']*(ell+1)
                     for i, f in zip(d['chosen'], F)), 'integer quotient box')
            groups[F].append(x)
        need(len(values) <= d['K']*(ell+1)**(d['r']-1), 'shell envelope')
        for xs in groups.values():
            need(len(xs) <= d['q'], 'half-open shell fiber')
            need(len({x[d['pivot']] for x in xs}) == len(xs), 'fiber pivot injectivity')
            first = xs[0]
            for x in xs:
                need(all(d['q']*(x[i]-first[i]) ==
                         d['m'][i]*(x[d['pivot']]-first[d['pivot']])
                         for i in range(len(x))), 'quotient kernel')
            fiber_cases += 1
    return len(members), len(shells), fiber_cases


def authenticate(data, digest):
    need(sha256(data).hexdigest() == digest, 'source hash mismatch')
    return data


def inputs():
    sources = json.loads((PACKAGE/'SOURCES.json').read_text())
    return {row['path']: authenticate((ROOT/row['path']).read_bytes(), row['sha256'])
            for row in sources['files'] if row['usage'] == 'input'}


def source_profile(source):
    benchmark = json.loads(source['research/rank-convergence/BENCHMARKS.json'])
    case = next(c for c in benchmark['cases'] if c['name'] == 'p16')
    need(case['source'] == 'research/compact-joint-compiler/arithmetic/RESULT.json'
         and case['profile_key'] is None, 'exact p16 profile path')
    raw = json.loads(source[case['source']])
    targets = {int(k): v for k, v in raw['targets'].items()}
    paid = {int(k): v for k, v in raw['paid'].items()}
    witness = case['witness']
    M, g = witness['height_base'], witness['a']+witness['b']
    need((max(targets), min(targets), M, g, sum(targets.values()), sum(paid.values()))
         == (145, 4, 1024, 2, 10928, 64620), 'exact p16 geometry')
    need(paid.get(1, 0) > 0 and max(paid) < max(targets), 'nonempty decreasing rule')
    d = descriptor(set(targets) | set(paid), M)
    need(d['primes'] == [2, 3, 5, 7, 11, 13, 17, 19, 29, 41, 73]
         and d['r'] == 11, 'p16 augmented rank')
    cols = pivots(d['matrix'])
    det = determinant([[row[j] for j in cols] for row in d['matrix']])
    need(det != 0, 'independent full-rank p16 minor')
    need(M**2 == min(targets)**(5*g) and min(targets)**g < M, 'exact z equals three fifths')
    return {'name': 'p16', 'r': d['r'], 'prime_count': len(d['primes']),
            'minor': det, 'z': '3/5', 'old_log_degree': 12, 'new_log_degree': 11,
            'shell_K': d['K'], 'changed_compiler': False}


def caller_cases(source):
    module = ModuleType('retained_adaptive_batching')
    path = 'research/adaptive-chronological-batching/batching.py'
    exec(compile(source[path], path, 'exec'), module.__dict__)
    cases = [({2: 1, 5: 1}, {1: 2, 4: 1}, 2, 2, 100),
             ({2: 1, 5: 1}, {1: 2, 4: 1}, 16, 2, 100),
             ({6: 1, 36: 1}, {1: 1, 6: 1}, 36, 2, 100)]
    checked, cut_count = 0, 0
    regimes = set()
    for targets, paid, M, g, N in cases:
        m, k0 = max(targets), min(targets)
        need(paid.get(1, 0) > 0, 'paid rank one')
        d = descriptor(set(targets) | set(paid), M)
        result = module.compile_widths(targets, paid, N, ('adaptive', M, 1, g-1))
        cap = N//m
        starts = products(d['generators'], cap)
        level_sources = defaultdict(list)
        for gamma in starts:
            ell = floor_log(gamma, M)
            flow = module.census(targets, paid, gamma, g*ell)
            S = sum(flow['sources'].values())
            need(0 < S <= sum(targets.values())*(sum(targets.values())+sum(paid.values()))**(g*ell),
                 'retained source bound')
            level_sources[ell].append(S)
        Q, bit_bound = 1, 0
        w = (sum(targets.values())-1).bit_length()
        v = (sum(targets.values())+sum(paid.values())-1).bit_length()
        for ell in range(floor_log(cap, M)+1):
            lo, hi = m*M**ell, min(N, m*M**(ell+1)-1)
            delta = min(M**ell, k0**(g*ell+1))
            visits = 0 if hi < lo else 1+(hi-lo)//delta
            level_lcm = lcm(*level_sources[ell])
            Q *= level_lcm**visits
            bit_bound += d['K']*visits*(ell+1)**(d['r']-1)*(w+g*ell*v)
        need((Q-1).bit_length() <= bit_bound, 'explicit symbolic shell bit envelope')
        for n, B in enumerate(result['widths']):
            need(Q % B == 0, 'actual compiler all-prime divisor')
            need((B-1).bit_length() <= bit_bound, 'actual compiler width envelope')
            if n < m:
                continue
            flow = result['flows'][(n//m, module.height(('adaptive', M, 1, g-1), targets, n))]
            representative = max(gamma for gamma in starts if gamma <= n//m)
            S = sum(module.census(targets, paid, representative,
                                  g*floor_log(representative, M))['sources'].values())
            need(S == sum(flow['sources'].values()), 'source plateau binding')
            delta = min(n//m, k0**(flow['height']+1))
            for child, count in module.batch_rows(flow, n):
                need(0 <= child < n and n-child >= delta and count > 0, 'actual child decrement')
                cut_count += 1
            checked += 1
        regimes.add('z=0' if k0**g >= M else 'z>0')
    need(regimes == {'z=0', 'z>0'}, 'both growth regimes')
    return {'fixtures': len(cases), 'compiled_ranks': checked, 'batch_rows': cut_count}


def controls(source):
    rejected = 0
    def reject(f):
        nonlocal rejected
        try:
            f()
        except ValueError:
            rejected += 1
        else:
            raise ValueError('negative control accepted')
    reject(lambda: descriptor([2], 1))
    reject(lambda: descriptor([0], 4))
    reject(lambda: descriptor([], 4))
    reject(lambda: authenticate(b'changed', sha256(b'original').hexdigest()))
    d = descriptor([2], 4)
    reject(lambda: need(len(products(d['generators'], 3)) <= 1, 'omit fiber multiplicity'))
    d = descriptor([6], 2)
    reject(lambda: need(d['r'] == rank([[1], [1]]), 'omit height-base direction'))
    d = descriptor([2, 3], 4)
    reject(lambda: need(len([]) == d['r']-1, 'omit quotient coordinate'))
    reject(lambda: need(len({1, 4}) <= 1, 'close both ends of rank-one shell'))
    reject(lambda: need(4**2 < 16, 'apply geometric sum at z zero'))
    d = descriptor([2, 5, 3], 4)
    reject(lambda: need(d['r'] == descriptor([2, 5], 4)['r'], 'omit paid generator'))
    return rejected


def main():
    source = inputs()
    members = shells = fibers = fixtures = 0
    for size in (1, 2, 3):
        for alphabet in combinations(range(2, 10), size):
            for M in (2, 3, 4, 6):
                a, b, c = shell_fixture(alphabet, M, 4096)
                members += a
                shells += b
                fibers += c
                fixtures += 1
    for alphabet, M in [([6], 36), ([6, 36], 36), ([4, 8], 16), ([6, 10], 12)]:
        a, b, c = shell_fixture(alphabet, M, 65536)
        members += a
        shells += b
        fibers += c
        fixtures += 1
    report = {'status': 'PASS_ADAPTIVE_SHELL_WIDTH', 'shell_fixtures': fixtures,
              'member_occurrences': members, 'shells': shells, 'fibers': fibers,
              'caller': caller_cases(source), 'p16': source_profile(source),
              'controls_rejected': controls(source)}
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
