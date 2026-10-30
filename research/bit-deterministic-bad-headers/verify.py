#!/usr/bin/env python3
"""Exact finite evidence for the deterministic bad-header proof. Apache-2.0."""
import argparse
import ast
import hashlib
import importlib.util
import itertools
import json
import math
import re
from fractions import Fraction
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
CASES = ((2, 3), (2, 5), (2, 7), (2, 11), (3, 3))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    require(1 <= n <= 4, 'bounded matrix dimension')
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b, modulus):
    n = len(a)
    require(1 <= n <= 4 and len(b) == n, 'bounded product')
    return [[sum(a[i][k] * b[k][j] for k in range(n)) % modulus
             for j in range(n)] for i in range(n)]


def determinant(a, modulus):
    n = len(a)
    require(1 <= n <= 4 and all(len(row) == n for row in a), 'square determinant')
    total = 0
    for perm in itertools.permutations(range(n)):
        inversions = sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        total += (-1)**inversions * math.prod(a[i][perm[i]] for i in range(n))
    return total % modulus


def inverse(a, modulus):
    n = len(a)
    rows = [list(row) + unit for row, unit in zip(a, identity(n))]
    for j in range(n):
        candidates = [i for i in range(j, n) if math.gcd(rows[i][j], modulus) == 1]
        require(bool(candidates), 'invertible header')
        pivot = candidates[0]
        rows[j], rows[pivot] = rows[pivot], rows[j]
        unit = pow(rows[j][j], -1, modulus)
        rows[j] = [x * unit % modulus for x in rows[j]]
        for i in range(n):
            if i != j:
                coefficient = rows[i][j]
                rows[i] = [(x - coefficient*y) % modulus
                           for x, y in zip(rows[i], rows[j])]
    require([row[:n] for row in rows] == identity(n), 'inverse endpoint')
    return [row[n:] for row in rows]


def projector(g, gi, axes, modulus):
    n = len(g)
    return [[sum(g[i][k] * gi[k][j] for k in axes) % modulus
             for j in range(n)] for i in range(n)]


def minors(p, rank, modulus):
    return [determinant([row[:k] for row in p[:k]], modulus)
            for k in range(1, rank + 1)]


def numerator(g, axes, k, modulus):
    """Replace the first k rows of G by the corresponding rows of G E_axes."""
    return determinant([[x if i >= k or j in axes else 0
                         for j, x in enumerate(row)] for i, row in enumerate(g)], modulus)


def dot_pairs(dimension, value, q):
    require(1 <= dimension <= 3 and 0 <= value < q, 'dot-pair domain')
    nonzero = (q**dimension - 1) * q**(dimension - 1)
    return nonzero + (q**dimension if value == 0 else 0)


def first_pivot_distribution(n, rank, q):
    denominator = dot_pairs(n, 1, q)
    return [Fraction(dot_pairs(rank, t, q) * dot_pairs(n-rank, (1-t) % q, q),
                     denominator) for t in range(q)]


def gaussian_binomial(n, r, q):
    require(0 <= r <= n <= 64 and q >= 2, 'Gaussian binomial domain')
    top = math.prod(q**(n-r+i)-1 for i in range(1, r+1))
    bottom = math.prod(q**i-1 for i in range(1, r+1))
    value, remainder = divmod(top, bottom)
    require(remainder == 0, 'Gaussian binomial integrality')
    return value


def good_fraction(n, r, q):
    require(1 <= r < n <= 64 and q >= 2, 'exact good-fraction domain')
    s = n-r
    return Fraction(((q-1)*q**s+1)**r, q**r * gaussian_binomial(n, r, q))


def projector_count(n, r, q):
    return q**(r*(n-r)) * gaussian_binomial(n, r, q)


def schur(p, q):
    n = len(p)
    require(2 <= n <= 4 and p[0][0] % q != 0, 'Schur pivot domain')
    inv = pow(p[0][0], -1, q)
    result = [[(p[i][j] - p[i][0]*inv*p[0][j]) % q
               for j in range(1, n)] for i in range(1, n)]
    require(multiply(result, result, q) == result, 'Schur idempotence')
    return tuple(tuple(row) for row in result)


def field_case(n, q):
    gl_size = math.prod(q**n - q**i for i in range(n))
    axes_sets = [a for r in range(1, n) for a in itertools.combinations(range(n), r)]
    counts = {a: {'bad': 0, 'first': [0]*q} for a in axes_sets}
    schur_counts = {a: {} for a in axes_sets}
    headers = identities = later_pivot_controls = 0
    for flat in itertools.product(range(q), repeat=n*n):
        g = [list(flat[i*n:(i+1)*n]) for i in range(n)]
        dg = determinant(g, q)
        if not dg:
            continue
        headers += 1
        gi = inverse(g, q)
        for axes in axes_sets:
            p = projector(g, gi, axes, q)
            require(multiply(p, p, q) == p, 'conjugated idempotent')
            ds = minors(p, len(axes), q)
            for k, value in enumerate(ds, 1):
                require(numerator(g, axes, k, q) == dg * value % q,
                        'degree-m determinant numerator identity')
                identities += 1
            counts[axes]['bad'] += int(0 in ds)
            counts[axes]['first'][p[0][0]] += 1
            if p[0][0]:
                small = schur(p, q)
                table = schur_counts[axes]
                table[small] = table.get(small, 0) + 1
            later_pivot_controls += int(ds[0] != 0 and 0 in ds[1:])
    require(headers == gl_size, 'complete GL header count')
    summary = []
    for axes in axes_sets:
        r = len(axes)
        table = schur_counts[axes]
        require(len(table) == projector_count(n-1, r-1, q) and len(set(table.values())) == 1,
                'uniform complete Schur fibres')
        require(Fraction(counts[axes]['bad'], headers) == 1-good_fraction(n, r, q),
                'exact all-leading-minor law')
        require(all(Fraction(value, headers) == expected for value, expected in
                    zip(counts[axes]['first'], first_pivot_distribution(n, r, q))),
                'exact first-pivot distribution')
        require(counts[axes]['bad'] * q < 2*n*r*headers, 'conditioned polynomial bound')
        summary.append({'axes': list(axes), 'schur_fibres': len(table), **counts[axes]})
    return {'m': n, 'q': q, 'raw_matrices': q**(n*n), 'headers': headers,
            'projectors': headers*len(axes_sets), 'numerator_identities': identities,
            'later_pivot_controls': later_pivot_controls, 'counts': summary}


def image_bases(n, r, q):
    require(n == 4 and 1 <= r < n and q in (2, 3), 'bounded canonical image census')
    for pivots in itertools.combinations(range(n), r):
        free = [(i, j) for i in range(r) for j in range(n)
                if j not in pivots and j > pivots[i]]
        for values in itertools.product(range(q), repeat=len(free)):
            basis = [[0]*r for _ in range(n)]
            for i, pivot in enumerate(pivots):
                basis[pivot][i] = 1
            for (i, j), value in zip(free, values):
                basis[j][i] = value
            yield pivots, basis


def projector_from_left_inverse(basis, pivots, free_values, q):
    n, r = len(basis), len(pivots)
    remaining = [j for j in range(n) if j not in pivots]
    y = [[0]*n for _ in range(r)]
    for i in range(r):
        for j, column in enumerate(remaining):
            y[i][column] = free_values[i*len(remaining)+j]
        for k, column in enumerate(pivots):
            y[i][column] = (int(i == k) - sum(y[i][j]*basis[j][k] for j in remaining)) % q
    return [[sum(basis[i][k]*y[k][j] for k in range(r)) % q
             for j in range(n)] for i in range(n)]


def four_coordinate_census():
    tables = []
    for q in (2, 3):
        n = 4
        for r in range(1, n):
            images = total = good = 0
            for pivots, basis in image_bases(n, r, q):
                images += 1
                for values in itertools.product(range(q), repeat=r*(n-r)):
                    p = projector_from_left_inverse(basis, pivots, values, q)
                    require(multiply(p, p, q) == p, 'image/left-inverse projector')
                    total += 1
                    good += int(0 not in minors(p, r, q))
            expected = q**(r*(n-r-1)) * ((q-1)*q**(n-r)+1)**r
            require(images == gaussian_binomial(n, r, q), 'complete RREF image census')
            require(total == projector_count(n, r, q), 'complete projector census')
            require(good == expected and Fraction(good, total) == good_fraction(n, r, q),
                    'exact four-coordinate good count')
            tables.append({'m': n, 'q': q, 'rank': r, 'images': images,
                           'projectors': total, 'good': good, 'bad': total-good})
    return tables


def source_module():
    path = ROOT / 'research/selected-bit-recursive-closure/vendor/controlled_normalizer.py'
    spec = importlib.util.spec_from_file_location('bad_headers_retained_normalizer', path)
    require(spec is not None and spec.loader is not None, 'retained module loader')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check_source_classification(module, g, axes, q, high, weights):
    n = len(g)
    prefix = module.ParentPrefix(q=q, width=2, low=tuple(map(tuple, g)),
                                high=tuple(map(tuple, high)),
                                ancestor_weights=weights, atom_columns=1)
    full = [[g[i][j] + q*high[i][j] for j in range(n)] for i in range(n)]
    p = projector(full, inverse(full, q*q), axes, q*q)
    ds = minors(p, len(axes), q*q)
    good = all(math.gcd(d, q) == 1 for d in ds)
    try:
        prepared = module.prepare(prefix, axes)
    except ValueError as error:
        require(not good and str(error) == 'nongeneric low class', 'source bad-class rejection')
    else:
        require(good, 'source admits only good classes')
        require(prepared.projector == p and len(prepared.pivots) == len(ds),
                'source projector and complete pivot extent')
        previous = 1
        for d, pivot in zip(ds, prepared.pivots):
            require(pivot == d * pow(previous, -1, q*q) % (q*q), 'source pivot ratio')
            previous = d
    return good, int(all(d != 0 for d in ds) and not good)


def prime_power_case():
    module = source_module()
    q = 3
    cases = good_cases = nonunit_controls = simultaneous_bad = 0
    by_axis = [0, 0]
    for flat in itertools.product(range(q), repeat=4):
        g = [list(flat[:2]), list(flat[2:])]
        if determinant(g, q) == 0:
            continue
        low_good = []
        for axis in range(2):
            p = projector(g, inverse(g, q), (axis,), q)
            low_good.append(p[0][0] != 0)
        simultaneous_bad += int(not all(low_good))
        for high_flat in itertools.product(range(q), repeat=4):
            high = [list(high_flat[:2]), list(high_flat[2:])]
            weights = tuple(1 + q*high_flat[i] for i in range(2))
            for axis in range(2):
                good, wrong_nonzero = check_source_classification(module, g, (axis,), q, high, weights)
                require(good == low_good[axis], 'every high lift has its low-class decision')
                cases += 1
                good_cases += good
                by_axis[axis] += int(not good)
                nonunit_controls += wrong_nonzero
    require(nonunit_controls > 0, 'nonzero is not a unit control exercised')
    require(simultaneous_bad == 40 and by_axis == [1620, 1620], 'per-request versus union control')
    return {'m': 2, 'q': 3, 'w': 2, 'charts': cases, 'good': good_cases,
            'bad': cases-good_cases, 'nonzero_nonunit_controls': nonunit_controls,
            'low_headers_bad_for_either_request': simultaneous_bad,
            'bad_lifts_per_axis': by_axis}


def source_three_coordinate_case():
    module = source_module()
    cases = good_cases = headers = 0
    axes_sets = [a for r in (1, 2) for a in itertools.combinations(range(3), r)]
    for flat in itertools.product(range(3), repeat=9):
        g = [list(flat[3*i:3*i+3]) for i in range(3)]
        if determinant(g, 3) == 0:
            continue
        headers += 1
        for axes in axes_sets:
            good, _ = check_source_classification(module, g, axes, 3,
                                                  [[0]*3 for _ in range(3)], (1, 4, 7))
            cases += 1
            good_cases += good
        if headers == 256:
            break
    require(headers == 256 and 0 < good_cases < cases, 'bounded three-coordinate source check')
    return {'low_headers': headers, 'charts': cases, 'good': good_cases, 'bad': cases-good_cases}


def arithmetic_and_controls(fields):
    q = 2**89 - 1
    m = 64
    bit = (ROOT / 'research/unconditional-batched-crt/BIT.md').read_text()
    match = re.search(r'H=(\{[^\n]+\})', bit)
    require(match is not None and 'q=2^89-1' in bit, 'retained profile and prime statement')
    profile = ast.literal_eval(match.group(1))
    require(len(profile) == 8 and all(type(k) is int and type(v) is int and v > 0
                                    for k, v in profile.items()), 'paid profile grammar')
    r = max(profile)
    require(r == 42, 'retained maximum paid rank')
    stronger, retained = Fraction(r+1, q), Fraction(2*m**3, q)
    exact_bad = 1-good_fraction(m, r, q)
    require(0 < exact_bad < stronger, 'exact all-pivot fraction beats rank-plus-one bound')
    require(stronger < retained < Fraction(1, 10**16), 'both complete-cover bounds fit eta')
    small = fields[0]
    require(Fraction(small['counts'][0]['bad'], small['headers']) == Fraction(5, 12),
            'exact small-field first-pivot failure')
    require(Fraction(5, 12) > Fraction(1, 3), 'incorrect one-over-q control rejected')
    require(sum(x['later_pivot_controls'] for x in fields) > 0, 'later-minor omission rejected')
    first_good = 1-first_pivot_distribution(3, 2, 3)[0]
    require(first_good**2 != good_fraction(3, 2, 3), 'identically distributed pivot shortcut rejected')
    # A restricted low cover consisting only of the identity is always bad for axis 1.
    p = projector(identity(2), identity(2), (1,), 3)
    require(minors(p, 1, 3) == [0], 'adversarial-subcover counterexample')
    return {'q': q, 'm': m, 'max_paid_rank': r,
            'bad_fraction_upper_bound': str(stronger), 'retained_upper_bound': str(retained),
            'controls': ['omit later minor', 'nonzero instead of unit',
                         'one-over-q first-pivot claim', 'arbitrary header subcover',
                         'simultaneous intersection instead of requestwise charging',
                         'identically distributed pivots']}


def compare_predecessor(fields):
    path = ROOT / 'research/r437-uniform-copy-reduction/MINOR-BOUND.json'
    old = json.loads(path.read_text())['complete_small_GL_tables']
    matched = []
    for row in old:
        for case in fields:
            if (case['m'], case['q']) != (row['dimension'], row['q']):
                continue
            axes = list(range(row['rank']))
            values = [x for x in case['counts'] if x['axes'] == axes]
            require(len(values) == 1 and values[0]['bad'] == row['bad']
                    and case['headers'] == row['GL'], 'shared predecessor count agrees')
            matched.append({'m': case['m'], 'q': case['q'], 'rank': row['rank'],
                            'headers': case['headers'], 'bad': row['bad']})
    require(len(matched) == 4, 'four overlapping predecessor rows compared')
    return matched


def source_bindings():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    bindings = {}
    require(len(sources['files']) <= 12, 'bounded source inventory')
    for row in sources['files']:
        if row['usage'] == 'input':
            path = ROOT / row['path']
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            require(digest == row['sha256'], 'source SHA256: ' + row['path'])
            bindings[row['path']] = digest
    return bindings


def run():
    bindings = source_bindings()
    fields = [field_case(n, q) for n, q in CASES]
    lifts = prime_power_case()
    return {'status': 'PASS_BIT_DETERMINISTIC_BAD_HEADERS', 'source_sha256': bindings,
            'field_cases': fields, 'four_coordinate_census': four_coordinate_census(),
            'prime_power_case': lifts,
            'source_three_coordinate_case': source_three_coordinate_case(),
            'arithmetic': arithmetic_and_controls(fields),
            'predecessor_shared_counts': compare_predecessor(fields),
            'scope': 'Finite evidence plus a written counting proof, no full GL64 or supplier replay.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path)
    arguments = parser.parse_args()
    result = run()
    result['package_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    encoded = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if arguments.receipt is not None:
        arguments.receipt.write_text(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
