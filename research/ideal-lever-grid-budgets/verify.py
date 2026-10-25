#!/usr/bin/env python3
"""Verifier for the ideal combined-lever budget grid (research/ideal-lever-grid-budgets).

Checks, in order:
  1. all 24 grid cells recompute to the exact rational brackets recorded in RESULT.json;
  2. every recorded endpoint is certified (relax(a_lo) < 1 < relax(a_hi));
  3. profile invariants (local mass per centre variant, child ranks inside the guard);
  4. live control: the parent levers.py runs and its seven published rows agree with
     the matching grid cells at printed precision;
  5. lever monotonicity across the whole lattice;
  6. fail-closed guards (idle rank cap 52, unpaid 0, over-weight local profile);
  7. bracket nesting at grid 1e-8 around the 1e-12 brackets for three rows;
  8. target decision: reaching-set size and minimal reaching antichain.

usage: python3 -B verify.py [--write]
Nick Petalas, with AI assistance. Apache-2.0.
"""
import json
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grid as G  # noqa: E402
sys.path.insert(0, str(HERE.parent / 'complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

RESULT = HERE / 'RESULT.json'
CENTRE_ORDER = {'sel': 0, 'shr': 1, 'free': 2}
SHAPE_ORDER = {'word': 0, '8': 1, '16': 2, '32': 3}

PUBLISHED = {  # grid cell -> (levers.py row name, printed x-multiplier)
    ('sel', 'word', 1): ('selected word (baseline)', 1.00),
    ('free', 'word', 1): ('centre path free: no 8 rank-8 copies, centre charge 0', 2.80),
    ('shr', 'word', 1): ('centre path shared by 2 calls (copies and charge halved)', 1.90),
    ('sel', '16', 1): ('local mass delivered as rank-16 children', 2.31),
    ('sel', '8', 1): ('local mass delivered as rank-8 children', 1.62),
    ('sel', 'word', 2): ('two unpaid coordinates per live family', 3.77),
    ('free', '16', 1): ('centre free and rank-16 children combined', 6.51),
}


def key(row):
    return (row['centre'], row['shape'], row['unpaid'])


def fmt(k):
    return '|'.join((k[0], k[1], str(k[2])))


def below(a, b):
    """a strictly below b in the lever lattice (<= in every coordinate, < in one)."""
    ka, kb = key(a), key(b)
    le = (CENTRE_ORDER[ka[0]] <= CENTRE_ORDER[kb[0]]
          and SHAPE_ORDER[ka[1]] <= SHAPE_ORDER[kb[1]]
          and ka[2] <= kb[2])
    lt = (CENTRE_ORDER[ka[0]] < CENTRE_ORDER[kb[0]]
          or SHAPE_ORDER[ka[1]] < SHAPE_ORDER[kb[1]]
          or ka[2] < kb[2])
    return le and lt


def compute_result():
    rows = G.compute_rows()
    base = next(Q(r['a_hi']) for r in rows if key(r) == ('sel', 'word', 1))

    # (2) endpoint certification for every recorded bracket
    for r in rows:
        prof, charge = G.profile(r['centre'], r['shape'] if r['shape'] == 'word' else int(r['shape']))
        unpaid = r['unpaid']
        lo, hi = Q(r['a_lo']), Q(r['a_hi'])
        assert C.relax(prof, G.M, G.FAM, G.ST, charge, lo, unpaid=unpaid)[1] < 1, r
        assert C.relax(prof, G.M, G.FAM, G.ST, charge, hi, unpaid=unpaid)[0] > 1, r

    # (3) profile invariants
    q = C.model(dict(G.WORD), G.M, G.FAM, G.ST, 64)
    assert q['idle_mass'] == 1646, q  # published idle mass
    for r in rows:
        shape = r['shape'] if r['shape'] == 'word' else int(r['shape'])
        prof, charge = G.profile(r['centre'], shape)
        assert all(0 < rq < G.M and rq <= q['R'] for rq in prof), r
        assert sum(rq * n for rq, n in prof.items()) == {64: G.MASS, 32: G.MASS - 32, 0: G.MASS - 64}[charge]

    # (4) live levers.py control
    proc = subprocess.run([sys.executable, '-B', str(HERE.parent / 'complex-local-word-ceiling' / 'levers.py')],
                         capture_output=True, text=True, check=True)
    published_rows = {}
    for line in proc.stdout.splitlines():
        if 'a_cap=' in line:
            name = line.split('a_cap=')[0].strip()
            a_cap = float(line.split('a_cap=')[1].split()[0])
            published_rows[name] = a_cap
    agree = {}
    for cell, (name, mult) in PUBLISHED.items():
        assert name in published_rows, f'parent row missing: {name}'
        row = next(r for r in rows if key(r) == cell)
        a = Q(row['a_hi'])
        assert abs(float(a) - published_rows[name]) <= 1e-6 + 1e-9, (cell, float(a), published_rows[name])
        ratio = float(a / base)
        assert abs(ratio - mult) <= 0.005 + 1e-9, (cell, ratio, mult)
        agree[fmt(cell)] = {
            'parent_a_cap_printed': f'{published_rows[name]:.6f}',
            'grid_a_cap_float': f'{float(a):.9f}',
            'parent_x_printed': mult,
            'grid_x_float': f'{ratio:.6f}',
        }

    # (5) monotonicity across the lattice
    violations = [(key(a), key(b)) for a in rows for b in rows
                  if below(a, b) and Q(a['a_hi']) > Q(b['a_hi'])]
    assert not violations, violations

    # (6) fail-closed guards
    guards = {}
    try:
        C.ceiling(dict(G.WORD), G.M, G.FAM, G.ST, 64, grid=G.GRID, R=52)
        raise AssertionError('idle rank cap 52 accepted')
    except ValueError:
        guards['idle_rank_cap_52_rejected'] = True
    try:
        C.ceiling(dict(G.WORD), G.M, G.FAM, G.ST, 64, grid=G.GRID, unpaid=0)
        raise AssertionError('unpaid 0 accepted')
    except ValueError:
        guards['unpaid_zero_rejected'] = True
    try:
        C.ceiling({1: 20000}, G.M, G.FAM, G.ST, 64, grid=G.GRID, unpaid=1)
        raise AssertionError('over-weight local profile accepted')
    except ValueError:
        guards['over_weight_local_profile_rejected'] = True

    # (7) bracket nesting at a coarser grid
    nesting = {}
    for cell in [('sel', 'word', 1), ('free', '16', 1), ('shr', '32', 2)]:
        lo8, hi8 = G.row(cell[0], cell[1] if cell[1] == 'word' else int(cell[1]), cell[2], grid=Q(1, 10 ** 8))
        fine = next(r for r in rows if key(r) == cell)
        assert Q(str(lo8)) <= Q(fine['a_lo']) and Q(fine['a_hi']) <= Q(str(hi8)), cell
        nesting[fmt(cell)] = 'contains_fine_bracket'

    # (8) target decision
    reaching = [r for r in rows if Q(r['a_hi']) / (1 + Q(r['a_hi'])) >= G.TARGET]
    minimal = [key(r) for r in reaching if not any(below(x, r) for x in reaching)]
    verdict = {
        'target_kappa': str(G.TARGET),
        'target_kappa_float': f'{float(G.TARGET):.9f}',
        'reaching_rows': sorted(fmt(k) for k in map(key, reaching)),
        'reaching_count': len(reaching),
        'minimal_reaching_antichain': sorted(fmt(k) for k in minimal),
    }

    return {
        'schema_version': 1,
        'model': {'m': G.M, 'families': G.FAM, 'stages': G.ST, 'guard_R': q['R'],
                  'local_mass_word': G.MASS, 'grid': str(G.GRID), 'fractional_idle': True},
        'baseline_a_cap': str(base),
        'baseline_kappa_cap': str(base / (1 + base)),
        'rows': rows,
        'published_row_agreement': agree,
        'monotonicity_violations': len(violations),
        'guards': guards,
        'nesting': nesting,
        'verdict': verdict,
        'credit': 'Nick Petalas',
    }


def main():
    result = compute_result()
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        RESULT.write_text(text)
        print(f'wrote {RESULT}')
        return
    if RESULT.read_text() != text:
        raise SystemExit('FAIL: RESULT.json does not match recomputation')
    print('PASS_IDEAL_LEVER_GRID_BUDGETS')


if __name__ == '__main__':
    main()
