#!/usr/bin/env python3
"""Counterexamples to the conjectured same-bank swap bound s <= 2(m-r). Apache-2.0."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
VENDOR = ROOT / 'research/selected-bit-recursive-closure/vendor'
MAX_M = 64
# Rank-3 chart over F_3 with axes 0, 1, 2; it makes s = 7 > 6 = 2(m - r).
CHART6 = ((1, 2, 1, 0, 0, 0), (2, 0, 0, 0, 2, 0), (0, 0, 2, 0, 2, 0),
          (1, 2, 0, 0, 0, 2), (2, 1, 1, 2, 1, 0), (1, 2, 0, 0, 2, 2))
RINGS = ((3, 1), (3, 2), (3, 3))
CENSUS = ((3, 2), (3, 3), (3, 4), (5, 3), (3, 5))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_bindings():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    require(len(sources['files']) <= 12, 'bounded source inventory')
    bindings = {}
    for row in sources['files']:
        if row['usage'] == 'input':
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            require(digest == row['sha256'], 'source SHA256: ' + row['path'])
            bindings[row['path']] = digest
    return bindings


def load_fallback():
    """Import the unchanged retained program; its siblings use bare imports."""
    require(VENDOR.is_dir(), 'retained vendor directory')
    sys.path.insert(0, str(VENDOR))
    spec = importlib.util.spec_from_file_location('fallback_program',
                                                  VENDOR / 'fallback_program.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def children_closed_form(m, f, r, s):
    """#4237's closed forms: (swaps, children) for rank r with s same-bank swaps."""
    swaps = (2*m - 1) * (2*m + 2) + r + s
    return swaps, (8*m*m + 2*m - 6 + r + 3*s) if f >= 2 else swaps


def conjectured_children(m, r):
    """#4237's conjectured rank-r maximum for f >= 2."""
    return 8*m*m + 8*m - 6 - 5*r


def block_chart(first, m):
    """Block-diagonal chart diag(first, I_{m - len(first)})."""
    k = len(first)
    return tuple(tuple(first[i][j] if i < k and j < k else int(i == j)
                       for j in range(m)) for i in range(m))


def rank_one_chart(k):
    """#4237's witness chart I + (1 - e0) e0^T, whose projector is 1 e0^T."""
    return tuple(tuple(1 if j == 0 else int(i == j) for j in range(k)) for i in range(k))


def stacked_chart(first, second):
    a, b = len(first), len(second)
    return tuple(tuple(first[i][j] if j < a else 0 for j in range(a + b)) for i in range(a)) + \
        tuple(tuple(second[i][j - a] if j >= a else 0 for j in range(a + b)) for i in range(b))


def vendor_profile(fp, q, width, chart, axes, f):
    """Run the unchanged prepare/paid_children path and count swap orientations."""
    m = len(chart)
    header = fp.Header(q, width, tuple(tuple(x % q for x in row) for row in chart),
                       tuple(tuple(0 for _ in row) for row in chart), tuple(axes))
    prepared = fp.prepare(fp.Prefix(f * m, 1, (), header))
    elimination = [(i, k) for kind, i, k, _ in prepared.plan.operations if kind == 'swap']
    opposite = sum((i < m) != (k < m) for i, k in elimination)
    swaps = sum(op.kind == 'swap' for op in prepared.operations)
    children = len(fp.paid_children(prepared))
    return {'r': len(axes), 'opposite': opposite, 's': len(elimination) - opposite,
            'swaps': swaps, 'children': children}


def check_counterexample(fp, q, width, chart, axes, f):
    """The rank law holds, #4237's closed forms hold, and s exceeds 2(m - r)."""
    m, row = len(chart), vendor_profile(fp, q, width, chart, axes, f)
    r, s = row['r'], row['s']
    require(row['opposite'] == r, 'opposite swaps equal the rank (#4237 rank law)')
    require(s <= 2*m - 1 - r, '#4237 proved ceiling')
    require((row['swaps'], row['children']) == children_closed_form(m, f, r, s),
            'paid_children matches #4237 closed forms')
    require(s > 2*(m - r), 'conjectured bound s <= 2(m-r) fails')
    if f >= 2:
        require(row['children'] > conjectured_children(m, r), 'children exceed conjecture')
    return row


# Independent field elimination for the censuses (cross-checked against vendor).
def inverse_mod(a, q):
    n = len(a)
    rows = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(a)]
    for k in range(n):
        p = next((i for i in range(k, n) if rows[i][k] % q), None)
        if p is None:
            return None
        rows[k], rows[p] = rows[p], rows[k]
        inv = pow(rows[k][k], -1, q)
        rows[k] = [x * inv % q for x in rows[k]]
        for i in range(n):
            if i != k and rows[i][k]:
                c = rows[i][k]
                rows[i] = [(x - c*y) % q for x, y in zip(rows[i], rows[k])]
    return [row[n:] for row in rows]


def residual(p, q):
    n = len(p)
    out = [[0] * (2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            out[i][j] = (int(i == j) - p[i][j]) % q
            out[i][n+j] = p[i][n-1-j]
            out[n+i][j] = p[n-1-i][j]
            out[n+i][n+j] = (int(i == j) - p[n-1-i][n-1-j]) % q
    return out


def field_swaps(p, q, split=False):
    """(opposite, same-bank) swaps of the retained first-unit elimination over F_q.

    With split=True also return the same-bank swaps made in the tail phase.
    """
    a, n = residual(p, q), 2*len(p)
    m, opposite, same, tail = len(p), 0, 0, 0
    for k in range(n):
        piv = next(i for i in range(k, n) if a[i][k])
        if piv != k:
            a[k], a[piv] = a[piv], a[k]
            if k < m <= piv:
                opposite += 1
            else:
                same += 1
                tail += k >= m
        inv = pow(a[k][k], -1, q)
        for i in range(n):
            if i != k and a[i][k]:
                c = a[i][k] * inv % q
                a[i] = [(x - c*y) % q for x, y in zip(a[i], a[k])]
    return (opposite, same, tail) if split else (opposite, same)


def subspaces(q, m, d):
    """Every d-dimensional subspace of F_q^m, once, as an RREF basis."""
    for pivots in itertools.combinations(range(m), d):
        free = [(i, j) for i in range(d) for j in range(pivots[i] + 1, m) if j not in pivots]
        for values in itertools.product(range(q), repeat=len(free)):
            basis = [[0] * m for _ in range(d)]
            for i, j in enumerate(pivots):
                basis[i][j] = 1
            for (i, j), v in zip(free, values):
                basis[i][j] = v
            yield basis


def gaussian_binomial(q, m, r):
    num = den = 1
    for i in range(r):
        num *= q**(m - i) - 1
        den *= q**(i + 1) - 1
    return num // den


def census(q, m):
    """Max same-bank swaps per rank over every rank-r idempotent of M_m(F_q)."""
    out = {}
    for r in range(1, m):
        images, kernels = list(subspaces(q, m, r)), list(subspaces(q, m, m - r))
        count, best = 0, -1
        for image in images:
            for kernel in kernels:
                basis = [list(col) for col in zip(*(image + kernel))]
                inv = inverse_mod(basis, q)
                if inv is None:
                    continue
                p = [[sum(basis[i][k] * inv[k][j] for k in range(r)) % q
                      for j in range(m)] for i in range(m)]
                opposite, same = field_swaps(p, q)
                require(opposite == r, 'census rank law')
                count, best = count + 1, max(best, same)
        require(count == q**(r*(m - r)) * gaussian_binomial(q, m, r), 'idempotent count')
        require(best == 2*(m - r), 'census maximum equals 2(m-r)')
        out[r] = {'idempotents': count, 'max_s': best}
    return out


def projector_of(chart, axes, q):
    inv = inverse_mod(chart, q)
    require(inv is not None, 'invertible chart')
    m = len(chart)
    return [[sum(chart[i][k] * inv[k][j] for k in axes) % q for j in range(m)]
            for i in range(m)]


def run(quick):
    bindings = source_bindings()
    fp = load_fallback()
    base = []
    for q, width in RINGS:
        for f in (1, 2, 3):
            row = check_counterexample(fp, q, width, CHART6, (0, 1, 2), f)
            base.append({'q': q, 'width': width, 'f': f, **row})
    require({(b['s'], b['children'] if b['f'] >= 2 else None) for b in base
             if b['f'] >= 2} == {(7, 318)}, 'base counterexample: s = 7, 318 children')
    # Mutation control: drop the rank-three part; the rank-one witness obeys the bound.
    row = vendor_profile(fp, 3, 1, rank_one_chart(6), (0,), 2)
    require(row['s'] == 2*(6 - 1), 'rank-one witness attains, not exceeds, 2(m-r)')
    # Field elimination agrees with the vendor path on the counterexample.
    require(field_swaps(projector_of(CHART6, (0, 1, 2), 3), 3, split=True) == (3, 7, 4),
            'field replay: 3 head-phase and 4 tail-phase same-bank swaps')

    family_a, family_b = [], []
    for m in range(6, MAX_M + 1):
        axes = (0, 1, 2) + tuple(range(6, m))
        row = check_counterexample(fp, 3, 1, block_chart(CHART6, m), axes, 2)
        require(row['s'] == 7 and row['r'] == m - 3, 'family A: rank m-3, s = 7')
        family_a.append(row['children'] - conjectured_children(m, m - 3))
        if m >= 8:
            chart = stacked_chart(CHART6, rank_one_chart(m - 6))
            row = check_counterexample(fp, 3, 1, chart, (0, 1, 2, 6), 2)
            require(row['s'] == 2*(m - 4) + 1, 'family B: rank 4, s = 2(m-4)+1')
            family_b.append(row['children'] - conjectured_children(m, 4))
    require(set(family_a) == {3} and set(family_b) == {3}, 'three extra children')

    lower = []
    for q in (3, 5):
        for m in range(2, 13):
            for r in range(1, m):
                chart = stacked_chart(rank_one_chart(m - r + 1), tuple(
                    tuple(int(i == j) for j in range(r - 1)) for i in range(r - 1)))
                axes = (0,) + tuple(range(m - r + 1, m))
                p = projector_of(chart, axes, q)
                require(field_swaps(p, q) == (r, 2*(m - r)), 'diag(W, I) attains 2(m-r)')
                lower.append((q, m, r))
    censuses = {f'{q},{m}': census(q, m) for q, m in CENSUS if not (quick and (q, m) == (3, 5))}
    return {
        'status': 'PASS_FALLBACK_SWAP_RANK_BOUND_REFUTED',
        'source_sha256': bindings,
        'base_counterexample': base,
        'family_a_rank_m_minus_3': {'m': [6, MAX_M], 's': 7, 'bound': 6, 'extra_children': 3},
        'family_b_rank_4': {'m': [8, MAX_M], 's': '2(m-4)+1', 'extra_children': 3},
        'diag_w_i_attains_2_m_minus_r': {'q': [3, 5], 'm_max': 12, 'cases': len(lower)},
        'censuses_bound_holds': censuses,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true',
                        help='skip the (q,m) = (3,5) census (about 100 s)')
    print(json.dumps(run(parser.parse_args().quick), indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
