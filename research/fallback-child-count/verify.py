#!/usr/bin/env python3
"""Exact finite evidence for the sharp fallback child count. Apache-2.0."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import random
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
VENDOR = ROOT / 'research/selected-bit-recursive-closure/vendor'
MAX_M = 64
WITNESS_RINGS = ((3, 1), (3, 2), (5, 1), (7, 2))
EXHAUSTIVE = ((3, 2), (3, 3), (5, 2), (7, 2))
RANDOM_HEADERS = 24


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


def fixed_swaps(m):
    """Diagonal-pair and upper-shear swap slots: (all, same-bank)."""
    return (2*m - 1) * (2*m + 2), 2 * (m*m - 1)


def predicted(m, f, r, s):
    """Children and total width for rank r with s same-bank elimination swaps."""
    every, same = fixed_swaps(m)
    swaps, same = every + r + s, same + s
    half = f // 2
    children = swaps + (2*same if half else 0)
    return children, f*swaps + 2*half*same


def sharp_maximum(m, f):
    return predicted(m, f, 1, 2*m - 2)


def profile(fp, prepared):
    """Count the program's swap slots by origin and bank orientation."""
    m = prepared.dimension
    elimination = [(i, k) for kind, i, k, _ in prepared.plan.operations if kind == 'swap']
    opposite = sum((i < m) != (k < m) for i, k in elimination)
    swaps = [op for op in prepared.operations if op.kind == 'swap']
    same = sum((op.target < m) == (op.source < m) for op in swaps)
    widths = fp.paid_children(prepared)
    return {'elimination_swaps': len(elimination), 'opposite': opposite,
            'same_elimination': len(elimination) - opposite, 'swaps': len(swaps),
            'same_swaps': same, 'children': len(widths), 'width': sum(widths)}


def header(fp, q, width, chart, rank):
    m = len(chart)
    low = tuple(tuple(x % q for x in row) for row in chart)
    high = tuple(tuple(0 for _ in row) for row in chart)
    return fp.Header(q, width, low, high, tuple(range(rank)))


def prepared_for(fp, q, width, chart, rank, f):
    prefix = fp.Prefix(f * len(chart), 1, (), header(fp, q, width, chart, rank))
    return fp.prepare(prefix)


def check_law(fp, prepared, rank):
    m, f = prepared.dimension, prepared.columns
    row = profile(fp, prepared)
    require(row['opposite'] == rank, 'opposite elimination swaps equal the rank')
    require(row['elimination_swaps'] <= 2*m - 1, 'elimination swap ceiling')
    s = row['same_elimination']
    require(s <= 2*m - 1 - rank, 'same-bank elimination ceiling')
    every, same = fixed_swaps(m)
    require(row['swaps'] == every + rank + s, 'swap slot identity')
    require(row['same_swaps'] == same + s, 'same-bank slot identity')
    require((row['children'], row['width']) == predicted(m, f, rank, s),
            'paid_children equals the closed form')
    return s


def witness_chart(m, unit):
    """G = I + (w - e0) e0^T with w = (1, unit, ..., unit); P = w e0^T."""
    return [[1 if i == j == 0 else unit if j == 0 else int(i == j)
             for j in range(m)] for i in range(m)]


def integer_replay(m):
    """Run the same elimination over Q; every entry must stay in {-1, 0, 1}.

    Then unit-ness modulo any odd prime power equals non-vanishing, and every
    modular run reduces the integer one, so the itinerary holds for all odd q.
    """
    n = 2 * m
    p = [[int(j == 0) for j in range(m)] for _ in range(m)]
    a = [[Fraction(0)] * n for _ in range(n)]
    for i in range(m):
        for j in range(m):
            a[i][j] = Fraction(int(i == j) - p[i][j])
            a[i][m+j] = Fraction(p[i][m-1-j])
            a[m+i][j] = Fraction(p[m-1-i][j])
            a[m+i][m+j] = Fraction(int(i == j) - p[m-1-i][m-1-j])
    swaps = []
    for k in range(n):
        require(all(x in (-1, 0, 1) for row in a for x in row), 'entries stay in {-1,0,1}')
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        require(pivot is not None, 'integer pivot')
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            swaps.append((k, pivot))
        for i in range(n):
            if i != k and a[i][k]:
                c = a[i][k] / a[k][k]
                a[i] = [x - c*y for x, y in zip(a[i], a[k])]
    require(swaps == [(k, k + 1) for k in range(n - 1)], 'cyclic adjacent swap chain')
    return len(swaps)


def witness_family(fp):
    rows = []
    for m in range(2, MAX_M + 1):
        require(integer_replay(m) == 2*m - 1, 'integer witness itinerary')
        rings = WITNESS_RINGS if m in (2, 3, MAX_M) else WITNESS_RINGS[:1]
        for q, width in rings:
            for f in (1, 2, 3):
                prepared = prepared_for(fp, q, width, witness_chart(m, 1), 1, f)
                s = check_law(fp, prepared, 1)
                require(s == 2*m - 2, 'witness attains every same-bank swap')
                row = profile(fp, prepared)
                require((row['children'], row['width']) == sharp_maximum(m, f),
                        'witness attains the sharp maximum')
                if m == MAX_M:
                    rows.append({'q': q, 'w': width, 'f': f, **row})
    return rows


def charts(q, m):
    for flat in itertools.product(range(q), repeat=m*m):
        chart = [list(flat[i*m:(i+1)*m]) for i in range(m)]
        try:
            fp_inverse(chart, q)
        except ValueError:
            continue
        yield chart


def fp_inverse(chart, q):
    from descriptor import inverse
    return inverse(chart, q)


def exhaustive(fp):
    """Every rank-r idempotent over F_q arises as some chart with axes 0..r-1."""
    from descriptor import projector
    out = []
    for q, m in EXHAUSTIVE:
        seen, histogram = {}, {}
        for chart in charts(q, m):
            for rank in range(1, m):
                key = (rank, tuple(map(tuple, projector(chart, tuple(range(rank)), q))))
                if key in seen:
                    continue
                s = check_law(fp, prepared_for(fp, q, 1, chart, rank, 2), rank)
                seen[key] = s
                histogram[(rank, s)] = histogram.get((rank, s), 0) + 1
        for rank in range(1, m):
            count = sum(v for (r, _), v in histogram.items() if r == rank)
            require(count == idempotent_count(q, m, rank), 'complete idempotent census')
        maxima = {r: max(s for (k, s) in histogram if k == r) for r in range(1, m)}
        require(all(maxima[r] <= 2*(m - r) for r in maxima), 'observed refined ceiling')
        out.append({'q': q, 'm': m, 'idempotents': len(seen),
                    'histogram': [[r, s, v] for (r, s), v in sorted(histogram.items())],
                    'max_same_by_rank': [[r, maxima[r]] for r in sorted(maxima)]})
    return out


def idempotent_count(q, m, r):
    def gaussian(n, k):
        num = den = 1
        for i in range(k):
            num *= q**(n - i) - 1
            den *= q**(i + 1) - 1
        return num // den
    return q**(r*(m - r)) * gaussian(m, r)


def random_large(fp):
    rng = random.Random(4215)
    rows = []
    while len(rows) < RANDOM_HEADERS:
        q = rng.choice((3, 5, 7))
        chart = [[rng.randrange(q) for _ in range(MAX_M)] for _ in range(MAX_M)]
        try:
            fp_inverse(chart, q)
        except ValueError:
            continue
        rank = rng.randrange(1, MAX_M)
        s = check_law(fp, prepared_for(fp, q, 1, chart, rank, 3), rank)
        rows.append([q, rank, s])
    return rows


def controls(fp, witness):
    from descriptor import elimination
    m, f = MAX_M, 3
    retained_swaps = (2*m - 1) + 2*(2*m - 1) + 2*m*(2*m - 1)
    require(retained_swaps == 16637, "FALLBACK.md's swap count")
    row = next(x for x in witness if (x['q'], x['w'], x['f']) == (3, 1, f))
    require(row['swaps'] == retained_swaps, 'retained swap count is attained')
    require(3*row['swaps'] == 49911 > row['children'] == 33269, 'old child bound not sharp')
    require(row['children'] < 32 * m**2, 'retained allowance still covers the count')
    # The rank law uses the residual structure: a bank interchange is invertible
    # but makes m opposite swaps, more than any rank 1 <= r < m allows.
    n = 2 * m
    flip = [[int(j == (i + m) % n) for j in range(n)] for i in range(n)]
    plan = elimination(flip, 3)
    opposite = sum((i < m) != (k < m) for kind, i, k, _ in plan.operations if kind == 'swap')
    require(opposite == m, 'non-residual control exceeds the rank law')
    return {'retained_swaps': retained_swaps, 'retained_child_bound': 3*retained_swaps,
            'sharp_children_m64_f3': row['children'], 'allowance': 32 * m**2,
            'bank_interchange_opposite_swaps': opposite}


def run():
    bindings = source_bindings()
    fp = load_fallback()
    witness = witness_family(fp)
    return {'status': 'PASS_FALLBACK_CHILD_COUNT', 'source_sha256': bindings,
            'witness_m64': witness, 'witness_dimensions': [2, MAX_M],
            'exhaustive_fields': exhaustive(fp), 'random_m64_headers': random_large(fp),
            'controls': controls(fp, witness),
            'scope': 'Written proof plus finite evidence; no physical fallback, '
                     'supplier admission or new kappa.'}


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
