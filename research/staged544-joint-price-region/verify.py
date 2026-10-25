#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent tight-face certificate, not a physical supplier or kappa result.

ToikY, with substantial OpenAI Codex assistance. Predecessor source credit in README.
No predecessor executable is imported or executed.
"""
import argparse
import ast
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_model(root=HERE):
    origins = json.loads((root / 'ORIGINS.json').read_text())
    for row in origins:
        raw = (root / row['file']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == row['git_blob'], 'source Git blob')
    tree = ast.parse((root / 'retained/3815-ceiling_certificate.py').read_text())
    constants = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                constants[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    m = json.loads((root / 'MODEL.json').read_text())
    cert = json.loads((root / 'retained/3862-CERTIFICATE.json').read_text())
    need(m['widths'] == list(constants['W']), 'width source binding')
    need(m['capacities'] == list(constants['CAPS']), 'capacity source binding')
    need(m['bins'] == [constants['BINS'][c] for c in m['capacities']], 'bin source binding')
    need(m['demands'] == [9 * x for x in constants['SUPPLY']], 'inventory source binding')
    need(m['basis'] == [[c, list(p)] for c, p in constants['BASIS']], 'basis source binding')
    need(Q(m['a']) == Q(cert['ceiling']['a_hi']), 'exponent source binding')
    need(m['flows'] == [5, 6, 7, 8, 9], 'flow schema')
    need(m['extras'] == [[16, [0, 0, 0, 0, 2, 0]], [32, [0, 0, 0, 0, 4, 0]]], 'extra patterns')
    return m


def solve(matrix, rhs):
    n = len(rhs)
    need(len(matrix) == n and all(len(row) == n for row in matrix), 'square system')
    a = [[Q(x) for x in row] + [Q(v)] for row, v in zip(matrix, rhs)]
    for i in range(n):
        pivot = next((j for j in range(i, n) if a[j][i]), None)
        need(pivot is not None, 'singular basis')
        a[i], a[pivot] = a[pivot], a[i]
        q = a[i][i]
        a[i] = [v / q for v in a[i]]
        for j in range(n):
            if j != i:
                q = a[j][i]
                a[j] = [v - q * w for v, w in zip(a[j], a[i])]
    return [row[-1] for row in a]


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Q(0))


def column(m, item):
    cap, p = item
    return list(p) + [int(cap == c) for c in m['capacities']]


def remainder(m, item):
    c, p = item
    return c - dot(m['widths'], p)


def all_patterns(m):
    for cap in m['capacities']:
        for p in product(*(range(cap // w + 1) for w in m['widths'])):
            if dot(p, m['widths']) <= cap:
                yield [cap, list(p)]


def log_bounds(n):
    # log(n) = k log(2) + 2 atanh((n-2^k)/(n+2^k)); geometric tail.
    def series(t):
        t = Q(t)
        total, term = Q(0), t
        for j in range(100):
            total += term / (2 * j + 1)
            term *= t * t
        return 2 * total, 2 * (total + term / (201 * (1 - t * t)))
    k = n.bit_length() - 1
    two, rem = series(Q(1, 3)), series(Q(n - 2**k, n + 2**k))
    return tuple(k * two[i] + rem[i] for i in (0, 1))


def h_bounds(n, a):
    if n in (0, 1):
        return Q(n), Q(n)
    lo, hi = log_bounds(n)
    need(0 <= a * lo <= a * hi < 1, 'series domain')
    # Alternating e^-x: odd degree 61 lower, even degree 60 upper.
    def partial(x, degree):
        term = total = Q(1)
        for j in range(1, degree + 1):
            term *= -x / j
            total += term
        return n * total
    lower, upper = partial(a * hi, 61), partial(a * lo, 60)
    den = 10**80
    return Q(lower.numerator * den // lower.denominator, den), Q(-((-upper.numerator * den) // upper.denominator), den)


def interval(expression, table):
    lo = hi = Q(0)
    for rank, coeff in expression.items():
        lo += coeff * table[rank][0 if coeff >= 0 else 1]
        hi += coeff * table[rank][1 if coeff >= 0 else 0]
    return lo, hi


def algebra(m):
    columns = [column(m, b) for b in m['basis']]
    matrix = [list(row) for row in zip(*columns)]
    inverse = [solve(matrix, [int(i == j) for i in range(10)]) for j in range(10)]
    inverse = [list(row) for row in zip(*inverse)]
    return matrix, inverse


def linear_certificate(m, inv):
    """Check all coefficients of the universal affine elimination identities."""
    base = [Q(x) for x in ('672','448','234','162','18','15','12','7','1916/5','324/5')]
    need([dot(row, m['demands'] + m['bins']) for row in inv] == base,
         'affine baseline coefficients')
    expected = [
        [0,0,1,0,-1,0,0,0,0,0],
        [0,0,0,-1,1,Q(1,2),-Q(1,4),-Q(1,4),Q(1,20),-Q(1,20)],
        [0,0,0,1,0,-Q(1,2),-Q(1,4),-Q(1,4),Q(1,20),-Q(1,20)],
        [0,0,0,0,0,-Q(1,2),-Q(1,4),Q(3,4),Q(1,20),-Q(1,20)],
        [0,0,0,0,0,Q(1,2),-Q(1,4),-Q(1,4),Q(1,20),-Q(1,20)],
    ]
    for w, target in zip(m['flows'], expected):
        rhs = [0]*10
        rhs[w-4] = -1
        rhs[w-5] = 1
        need([dot(row, rhs) for row in inv] == target, 'affine flow coefficients')
    for item, target in zip(m['extras'],
                            ([0,1,0,0,0,1,0,-1,0,0], [0,0,0,0,0,2,0,-1,0,0])):
        need([dot(row, column(m, item)) for row in inv] == target,
             'extra-column elimination coefficients')


def classify(m):
    matrix, inv = algebra(m)
    linear_certificate(m, inv)
    residuals = [int(remainder(m, b)) for b in m['basis']]
    table = {r: h_bounds(r, Q(m['a'])) for r in range(49)}
    tight, gaps, rows = [], [], []
    for item in all_patterns(m):
        coords = [dot(row, column(m, item)) for row in inv]
        rank = int(remainder(m, item))
        expression = {rank: Q(1)} if rank else {}
        for coeff, r in zip(coords, residuals):
            if r:
                expression[r] = expression.get(r, Q(0)) - coeff
        expression = {r: q for r, q in expression.items() if q}
        if not expression:
            tight.append(item)
        else:
            low, high = interval(expression, table)
            need(low > 0, 'non-tight pattern lacks strict positive certificate')
            gaps.append(low)
        rows.append((item, coords))
    need(len(rows) == 2551 and len(tight) == 12, 'complete pattern classification')
    key = lambda b: (b[0], tuple(b[1]))
    need(set(map(key, tight)) == set(map(key, m['basis'] + m['extras'])), 'tight face differs')
    return matrix, inv, min(gaps), rows


def demands(m, flows):
    need(len(flows) == 5 and all(x >= 0 for x in flows), 'five nonnegative flows required')
    d = list(map(Q, m['demands']))
    for w, x in zip(m['flows'], flows):
        d[w - 4] -= x
        d[w - 5] += x
    need(min(d) >= 0, 'negative changed inventory')
    return d


def facets(flows):
    x5, x6, x7, x8, x9 = flows
    return [48 - x6 - x7 - x8 - x9, 18 + x6 - x5,
            30 + x6 + x9 - x7 - x8, 88 + x6 + x8 + x9 - 3 * x7]


def packing(m, inv, flows):
    rhs = demands(m, flows) + list(map(Q, m['bins']))
    y = [dot(row, rhs) for row in inv]
    # General two-extra-column elimination; not an axis-only test.
    feasible = all(y[j] >= 0 for j in range(10) if j != 7) and y[7] + y[5] >= 0 and 2*y[7] + y[1] + y[5] >= 0
    need(feasible == all(s >= 0 for s in facets(flows)), 'projected facet mismatch')
    if not feasible:
        return None
    needed = max(Q(0), -y[7])
    z1 = min(needed, y[1])
    z2 = needed - z1
    y[1] -= z1
    y[5] -= z1 + 2*z2
    y[7] += z1 + z2
    answer = y + [z1, z2]
    validate_packing(m, flows, answer)
    return answer


def validate_packing(m, flows, answer):
    need(len(answer) == 12 and min(answer) >= 0, 'nonnegative face counts')
    cols = [column(m, b) for b in m['basis'] + m['extras']]
    target = demands(m, flows) + list(map(Q, m['bins']))
    need([sum(v * c[i] for v, c in zip(answer, cols)) for i in range(10)] == target, 'packing conservation')


def result(m):
    matrix, inv, gap, rows = classify(m)
    expected_ranges = [Q(18), Q(48), Q(88, 3), Q(30), Q(48)]
    need([str(v) for v in expected_ranges] == m['expected_axis_ranges'], 'range certificate')
    witnesses, controls = [], []
    for i, bound in enumerate(expected_ranges):
        flow = [Q(0)] * 5
        flow[i] = bound
        answer = packing(m, inv, flow)
        need(answer is not None, 'axis boundary not attained')
        need(all((360*v).denominator == 1 for v in answer + demands(m, flow)),
             'T360 integral boundary witness')
        witnesses.append({'flow': list(map(str, flow)), 'counts': list(map(str, answer))})
        flow[i] += Q(1, 1000)
        try:
            outside = packing(m, inv, flow)
        except ValueError as exc:
            need(str(exc) == 'negative changed inventory', 'unexpected axis rejection')
            outside = None
        need(outside is None, 'outside axis accepted')
        controls.append('outside-axis-' + str(m['flows'][i]))
    bad = [Q(0), Q(28), Q(28), Q(0), Q(0)]
    need(packing(m, inv, bad) is None, 'independent range box incorrectly accepted')
    controls.append('joint-box-counterexample')
    # Row 6 separates the bad inventory from every tight column.
    need(dot(inv[6], demands(m, bad) + list(map(Q, m['bins']))) == -2, 'separator value')
    tight_keys = {(b[0], tuple(b[1])) for b in m['basis'] + m['extras']}
    need(all(coords[6] >= 0 for item, coords in rows if (item[0], tuple(item[1])) in tight_keys), 'separator tight face')
    mass_cap = max(-coords[6] for _, coords in rows)
    need(mass_cap > 0, 'separator bound')
    # A feasible non-tight packing for the same changed demand: shrink 28
    # distinct width-6 and 28 width-7 helpers in their original bins.
    original = [dot(row, list(map(Q, m['demands'] + m['bins']))) for row in inv]
    original[3] -= 28  # [6,8,9,9] -> [5,8,9,9]
    original[1] -= 28  # [7,9] -> [6,9]
    items = m['basis'] + [[32, [0, 1, 0, 0, 1, 2]], [16, [0, 0, 1, 0, 0, 1]]]
    counts = original + [Q(28), Q(28)]
    need(min(counts) >= 0, 'counterexample feasible counts')
    cols = [column(m, b) for b in items]
    need([sum(v * c[i] for v, c in zip(counts, cols)) for i in range(10)] == demands(m, bad) + list(map(Q, m['bins'])), 'counterexample conservation')
    corrupt = list(map(Q, witnesses[0]['counts']))
    corrupt[0] += 1
    try:
        validate_packing(m, list(map(Q, witnesses[0]['flow'])), corrupt)
    except ValueError:
        controls.append('extra-bin-count')
    else:
        raise ValueError('corrupt packing accepted')
    try:
        demands(m, [Q(-1), Q(0), Q(0), Q(0), Q(0)])
    except ValueError:
        controls.append('negative-flow')
    else:
        raise ValueError('negative flow accepted')
    # Deterministic boundary/interior coverage, not a global search theorem.
    checked = 0
    for flow in product((Q(0), Q(7), Q(18), Q(24), Q(28), Q(48)), repeat=5):
        try:
            packing(m, inv, flow)
            checked += 1
        except ValueError as exc:
            if str(exc) != 'negative changed inventory':
                raise
    return {'status': 'PASS_STAGED544_JOINT_PRICE_REGION', 'a': m['a'], 'patterns': 2551,
            'tight_patterns': 12, 'non_tight_patterns': 2539, 'strict_reduced_cost_lower': str(gap),
            'axis_ranges_helper_calls_per_replica': list(map(str, expected_ranges)),
            'axis_witnesses': witnesses, 'sampled_flow_vectors': checked, 'controls': controls,
            'universal_affine_coefficients_checked': True, 'T360_integral_axis_boundaries': 5,
            'box_counterexample': {'flows': list(map(str, bad)), 'separator': '-2',
                'non_tight_separator_magnitude_bound': str(mass_cap),
                'idle_cost_gap_above_common_dual_lower': str(2 * gap / mass_cap),
                'feasible_patterns': items, 'feasible_counts': list(map(str, counts))},
            'scope': 'Fixed-exponent fractional fixed-bin ideal only; no physical implementation or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--flows', nargs=5, type=Q, metavar=('X5','X6','X7','X8','X9'))
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    m = load_model()
    report = result(m)
    if args.flows is not None:
        answer = packing(m, algebra(m)[1], args.flows)
        print(json.dumps({'flows': list(map(str, args.flows)), 'sharp_common_price': answer is not None,
                          'face_counts': None if answer is None else list(map(str, answer))}))
        return
    if args.write_result:
        (HERE / 'RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    else:
        need(report == json.loads((HERE / 'RESULT.json').read_text()), 'result differs')
    print(report['status'] + ' patterns=2551 tight=12 axis_ranges=18,48,88/3,30,48 no_new_kappa')


if __name__ == '__main__':
    main()
