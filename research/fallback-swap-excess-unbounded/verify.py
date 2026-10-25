#!/usr/bin/env python3
"""Direct-sum additivity and unbounded excess of fallback same-bank swaps. Apache-2.0."""
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
# #4247's rank-3 chart over F_3 (axes 0, 1, 2): s = 7, excess 1.
G6 = ((1, 2, 1, 0, 0, 0), (2, 0, 0, 0, 2, 0), (0, 0, 2, 0, 2, 0),
      (1, 2, 0, 0, 0, 2), (2, 1, 1, 2, 1, 0), (1, 2, 0, 0, 2, 2))
# New rank-4 chart over F_3 (axes 0..3): s = 10 = 2(m - r) + 2, excess 2.
H8 = ((2, 0, 1, 2, 0, 0, 0, 0), (0, 0, 1, 0, 1, 0, 2, 2), (1, 1, 1, 0, 2, 0, 1, 1),
      (0, 0, 1, 2, 1, 0, 2, 2), (0, 1, 0, 1, 0, 2, 1, 2), (0, 1, 2, 2, 2, 1, 0, 0),
      (1, 1, 2, 0, 0, 1, 1, 2), (2, 2, 2, 2, 2, 0, 2, 2))
# New rank-7 chart over F_3 (axes 0, 1, 2, 6, 7, 8, 12): s = 17 = 2(m - r) + 5, excess 5.
K13 = ((1, 2, 2, 0, 0, 0, 2, 1, 1, 0, 0, 0, 1),
       (2, 1, 2, 2, 1, 0, 2, 0, 1, 0, 0, 0, 0),
       (0, 2, 1, 2, 1, 1, 0, 0, 0, 0, 1, 0, 0),
       (1, 2, 1, 2, 1, 1, 0, 1, 2, 0, 2, 0, 2),
       (1, 1, 1, 1, 1, 0, 2, 1, 1, 2, 1, 0, 2),
       (1, 2, 1, 2, 2, 0, 2, 0, 2, 1, 0, 0, 2),
       (0, 1, 2, 0, 0, 2, 2, 2, 0, 0, 2, 0, 1),
       (1, 2, 1, 1, 2, 2, 2, 0, 1, 0, 0, 0, 2),
       (0, 0, 0, 1, 2, 0, 0, 0, 2, 0, 1, 0, 0),
       (0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 1, 2, 1),
       (0, 0, 0, 2, 0, 1, 2, 1, 1, 1, 2, 1, 1),
       (0, 0, 0, 0, 2, 0, 1, 2, 0, 0, 0, 2, 2),
       (0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 0, 1))
K13_AXES = (0, 1, 2, 6, 7, 8, 12)
RINGS = ((3, 1), (3, 2), (3, 3))


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


# Headers are (chart, axes) pairs; block sums stay in that form.
def identity(k):
    return tuple(tuple(int(i == j) for j in range(k)) for i in range(k))


def rank_one(k):
    """#4237's witness chart I + (1 - e0) e0^T with axis 0; projector 1 e0^T."""
    return tuple(tuple(1 if j == 0 else int(i == j) for j in range(k)) for i in range(k)), (0,)


def direct_sum(*headers):
    """Block-diagonal chart; the axes of each block are shifted to its offset."""
    n = sum(len(chart) for chart, _ in headers)
    rows, axes, offset = [], [], 0
    for chart, block_axes in headers:
        k = len(chart)
        rows += [(0,) * offset + tuple(row) + (0,) * (n - offset - k) for row in chart]
        axes += [offset + a for a in block_axes]
        offset += k
    return tuple(rows), tuple(axes)


def h8_family(m, k, r):
    """H8^{+k} + W_a + I_b with a + b = m - 8k and rank r (4k < r <= m - 4k, or m = 8k)."""
    rest, extra = m - 8*k, r - 4*k
    blocks = [(H8, (0, 1, 2, 3))] * k
    if extra == rest:
        blocks.append((identity(rest), tuple(range(rest))))
    else:
        require(1 <= extra and rest - extra + 1 >= 2, 'family rank range')
        blocks += [rank_one(rest - extra + 1), (identity(extra - 1), tuple(range(extra - 1)))]
    return direct_sum(*[b for b in blocks if b[0]])


def children_closed_form(m, f, r, s):
    """#4237's closed forms: (swaps, children) for rank r with s same-bank swaps."""
    swaps = (2*m - 1) * (2*m + 2) + r + s
    return swaps, (8*m*m + 2*m - 6 + r + 3*s) if f >= 2 else swaps


def conjectured_children(m, r):
    """#4237's refuted conjecture for the rank-r maximum at f >= 2."""
    return 8*m*m + 8*m - 6 - 5*r


def vendor_profile(fp, q, width, header, f):
    """Run the unchanged prepare/paid_children path and count swap orientations."""
    chart, axes = header
    m = len(chart)
    prefix_header = fp.Header(q, width, tuple(tuple(x % q for x in row) for row in chart),
                              tuple(tuple(0 for _ in row) for row in chart), tuple(axes))
    prepared = fp.prepare(fp.Prefix(f * m, 1, (), prefix_header))
    elimination = [(i, k) for kind, i, k, _ in prepared.plan.operations if kind == 'swap']
    opposite = sum((i < m) != (k < m) for i, k in elimination)
    swaps = sum(op.kind == 'swap' for op in prepared.operations)
    children = len(fp.paid_children(prepared))
    return {'m': m, 'r': len(axes), 'opposite': opposite, 's': len(elimination) - opposite,
            'swaps': swaps, 'children': children}


def check_vendor(fp, q, width, header, f, excess):
    """Rank law, #4237's closed forms and ceiling, and the stated excess over 2(m - r)."""
    row = vendor_profile(fp, q, width, header, f)
    m, r, s = row['m'], row['r'], row['s']
    require(row['opposite'] == r, 'opposite swaps equal the rank (#4237 rank law)')
    require(s <= 2*m - 1 - r, '#4237 proved ceiling')
    require((row['swaps'], row['children']) == children_closed_form(m, f, r, s),
            'paid_children matches #4237 closed forms')
    require(s - 2*(m - r) == excess, 'stated excess')
    if f >= 2:
        require(row['children'] - conjectured_children(m, r) == 3*excess, 'three children per unit')
    require(field_swaps(projector_of(header, q), q)[:2] == (r, s), 'field model agrees')
    return row


# Independent field model of the first-unit elimination.
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


def projector_of(header, q):
    chart, axes = header
    inv = inverse_mod(chart, q)
    require(inv is not None, 'invertible chart')
    m = len(chart)
    return [[sum(chart[i][k] * inv[k][j] for k in axes) % q for j in range(m)]
            for i in range(m)]


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


def field_swaps(p, q):
    """(opposite, same-bank, tail-phase same-bank) swaps of first-unit elimination over F_q."""
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
    return opposite, same, tail


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


def all_headers(q, m):
    """One (chart, axes) header per idempotent of M_m(F_q), every rank 0..m."""
    out = []
    for r in range(m + 1):
        for image in subspaces(q, m, r):
            for kernel in subspaces(q, m, m - r):
                chart = tuple(tuple(col) for col in zip(*(image + kernel)))
                if inverse_mod(chart, q) is not None:
                    out.append((chart, tuple(range(r))))
    return out


def check_additivity(q, dims, others=None):
    """Every ordered pair of idempotents with sizes in dims x others and others x dims
    (dims x dims when others is None): all three counts add."""
    sizes = set(dims) | set(others or ())
    pools = {m: [(h, field_swaps(projector_of(h, q), q)) for h in all_headers(q, m)]
             for m in sizes}
    size_pairs = set(itertools.product(dims, repeat=2)) if others is None else \
        set(itertools.product(dims, others)) | set(itertools.product(others, dims))
    pairs = 0
    for m1, m2 in sorted(size_pairs):
        for (h1, c1), (h2, c2) in itertools.product(pools[m1], pools[m2]):
            total = field_swaps(projector_of(direct_sum(h1, h2), q), q)
            require(total == tuple(x + y for x, y in zip(c1, c2)), 'direct-sum additivity')
            pairs += 1
    return {'q': q, 'size_pairs': sorted(size_pairs), 'headers': {m: len(pools[m]) for m in sizes},
            'ordered_pairs': pairs}


def run(quick):
    bindings = source_bindings()
    fp = load_fallback()
    atoms = []
    for name, header, excess in (('G6', (G6, (0, 1, 2)), 1), ('H8', (H8, (0, 1, 2, 3)), 2),
                                 ('K13', (K13, K13_AXES), 5)):
        for q, width in RINGS:
            for f in (1, 2, 3):
                row = check_vendor(fp, q, width, header, f, excess)
                atoms.append({'atom': name, 'q': q, 'width': width, 'f': f, **row})
    require(field_swaps(projector_of((H8, (0, 1, 2, 3)), 3), 3) == (4, 10, 6),
            'H8: 4 head-phase and 6 tail-phase same-bank swaps')
    # Controls: an excess-zero block adds nothing; a rank-zero block costs 2 per coordinate.
    require(field_swaps(projector_of(direct_sum((H8, (0, 1, 2, 3)), rank_one(3)), 3), 3)[1]
            == 10 + 4, 'H8 + W3 keeps excess 2')
    require(field_swaps(projector_of(direct_sum((H8, (0, 1, 2, 3)), (identity(2), ())), 3), 3)[1]
            == 10, 'H8 + 0_2: same s, excess drops by 4')
    additivity = [check_additivity(3, (1, 2, 3)), check_additivity(5, (1, 2))]
    if not quick:
        additivity.append(check_additivity(3, (4,), (1, 2)))

    family_c, family_d = [], []
    for m in range(8, MAX_M + 1):
        k = m // 8
        row = check_vendor(fp, 3, 1, h8_family(m, k, m - 4*k), 2, 2*k)
        family_c.append([m, row['r'], row['s'], row['children']])
        if m - 8*k >= 2:
            row = check_vendor(fp, 3, 1, h8_family(m, k, 4*k + 1), 2, 2*k)
            family_d.append([m, row['r'], row['s'], row['children']])
    family_e = []
    for m in range(13, MAX_M + 1):
        k = m // 13
        header = direct_sum(*[(K13, K13_AXES)] * k, (identity(m - 13*k), tuple(range(m - 13*k))))
        row = check_vendor(fp, 3, 1, header, 2, 5*k)
        family_e.append([m, row['r'], row['s'], row['children']])
    best64 = direct_sum(*[(K13, K13_AXES)] * 4, (H8, (0, 1, 2, 3)), (identity(4), (0, 1, 2, 3)))
    row = check_vendor(fp, 3, 1, best64, 2, 22)
    require([row['r'], row['s'], row['children']] == [36, 78, 33160], 'm = 64 best: s = 78')
    grid = 0
    for m in range(8, 25 if quick else 33):
        for k in range(1, m // 8 + 1):
            for r in range(4*k + (m > 8*k), m - 4*k + 1):
                header = h8_family(m, k, r)
                require(len(header[1]) == r, 'grid rank')
                require(field_swaps(projector_of(header, 3), 3)[:2] == (r, 2*(m - r) + 2*k),
                        'grid excess 2k')
                grid += 1
    require(family_c[-1] == [64, 32, 80, 33162], 'm = 64: s = 80, 33162 children')
    return {
        'status': 'PASS_FALLBACK_SWAP_EXCESS_UNBOUNDED',
        'source_sha256': bindings,
        'atoms': atoms,
        'additivity_exhaustive_pairs': additivity,
        'family_c_h8k_plus_identity': {'m_r_s_children_f2': family_c},
        'family_d_h8k_plus_rank_one': {'m_r_s_children_f2': family_d},
        'family_e_k13k_plus_identity': {'m_r_s_children_f2': family_e},
        'm64_k13x4_h8_i4': {'r': 36, 's': 78, 'excess': 22, 'children_f2': 33160},
        'field_grid_cases': grid,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true',
                        help='skip the size-4 additivity pairs and the grid for 25 <= m <= 32')
    print(json.dumps(run(parser.parse_args().quick), indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
