#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify the rank-shape ceiling curve of the selected #1094 complex local word.

Restates the incumbent packing ceiling as a function of the largest paid local
child rank, and asks how far the *shape* of the paid local child histogram alone
can move it. Writes or checks RESULT.json.

usage: verify.py [--write]

All arithmetic is the sibling package's unchanged exact interval arithmetic
(`research/complex-local-word-ceiling/ceiling.py`), reused through `rankshape.py`.
No new kappa is claimed, no local word is constructed, and the selected record is
unchanged.

Nick Petalas, donated inference session (worker 3), with substantial AI
assistance. Apache-2.0.
"""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import rankshape as S  # noqa: E402  (puts the sibling package on sys.path)
import ceiling as C  # noqa: E402

M, PAIRS, PORTS, STAGES, CENTRE = 73, 4, 112, 9, 64
FAMILIES = 2 * PAIRS * PORTS                      # live data families per replica
TARGET = Q(1, 99)
DP_CAPS = (1, 2, 3, 4, 8, 16, 32, 43, 44, 48, 51)
DP_A = (Q(1, 20000), Q(1, 200), Q(1375, 100000))      # 0.00005, mid, endpoint scale
BIMO_CAPS = (8, 16, 32, 43, 44, 48, 51)


def dec(x, digits=12):
    return f'{float(x):.{digits}g}'


def fr(x):
    return f'{x.numerator}/{x.denominator}'


def selected():
    """Per-call local profile of #1094, recomputed from the pinned assembly inputs."""
    asm = json.loads((ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json').read_text())
    ind = json.loads((ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    rec = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    H = {int(r): n for r, n in asm['complex_profile'].items()}
    idle = {int(r): n for r, n in ind['owner']['idle'].items()}
    N, W = ind['price']['calls'], ind['price']['live']
    C.require(H == {int(r): n for r, n in ind['owner']['profile'].items()}, 'profile mismatch')
    C.require(N % STAGES == 0 and W == FAMILIES * (N // STAGES), 'live stock is not 2*pairs*V per replica')
    mass = sum(r * n for r, n in H.items())
    C.require(mass == (M - 1) * W + CENTRE * N, 'coverage identity mass = 72W + 64N fails')
    local = {}
    for r, n in H.items():
        k = n - idle.get(r, 0)
        C.require(k >= 0 and k % N == 0, f'local rank {r} not uniform per call')
        if k:
            local[r] = k // N
    return local, rec


def cap(local):
    return S.cap_ceiling(local, M, FAMILIES, STAGES, CENTRE)


def curve(local_mass, base, R):
    """frac_s (upper bound) and int_s (lower bound) for every rank cap s = 1..R."""
    rows = []
    for s in range(1, R + 1):
        H = S.greedy(local_mass, s)
        a_int = cap(H)
        a_frac = cap(S.frac_profile(local_mass, s))
        C.require(a_int <= a_frac, f'integer cap {s} exceeds its fractional relaxation')
        rows.append(dict(s=s, histogram={str(r): n for r, n in sorted(H.items())},
                         a_int=fr(a_int), a_frac=fr(a_frac),
                         ratio_int_over_base=dec(a_int / base),
                         ratio_frac_over_base=dec(a_frac / base),
                         kappa_upper_int=dec(a_int / (1 + a_int)),
                         integrality_loss_percent=dec(100 * (a_frac - a_int) / a_frac, 4)))
    for u, v in zip(rows, rows[1:]):
        C.require(Q(u['a_int']) <= Q(v['a_int']), 'integer ceiling is not monotone in the rank cap')
        C.require(Q(u['a_frac']) <= Q(v['a_frac']), 'fractional ceiling is not monotone in the rank cap')
    return rows


def first_clear(rows, key):
    for row in rows:
        if Q(row[key]) >= TARGET:
            return row['s']
    return None


def bimodal(local_mass):
    """How much local mass must be carried by large children to clear a = 1/99.

    Bimodal model: k integer children of rank s plus the remaining mass as rank-1
    children. `k_min` is bisected over integers and then *bracketed* by two
    certified ceilings: k = k_min clears 1/99 and k = k_min - 1 does not.
    """
    out = []
    for s in BIMO_CAPS:
        top = local_mass // s
        a_top = cap({s: top, 1: local_mass - top * s})
        if a_top < TARGET:
            out.append(dict(s=s, reachable=False, a_at_max_children=fr(a_top)))
            continue
        lo, hi = 0, top
        while lo < hi:
            mid = (lo + hi) // 2
            if cap({s: mid, 1: local_mass - mid * s}) >= TARGET:
                hi = mid
            else:
                lo = mid + 1
        k = lo
        a_hit = cap({s: k, 1: local_mass - k * s})
        a_miss = cap({s: k - 1, 1: local_mass - (k - 1) * s})
        C.require(a_hit >= TARGET > a_miss, f's={s}: k={k} bracket does not straddle 1/99')
        out.append(dict(s=s, reachable=True, k_min=k, children_at_k_minus_1=k - 1,
                        mass_fraction_percent=dec(100 * Q(k * s, local_mass)),
                        a_at_k=fr(a_hit), a_at_k_minus_1=fr(a_miss),
                        kappa_upper=dec(a_hit / (1 + a_hit))))
    return out


def dp_checks(local_mass, R):
    """Independent check that greedy is the exact integer optimum, at screening values."""
    out = []
    for a in DP_A:
        table = S.dp_histograms(local_mass, DP_CAPS, M, R, a)
        entry = dict(a=dec(a))
        entry['all_caps_match_greedy'] = all(
            table[s][0] == S.greedy(local_mass, s) for s in DP_CAPS)
        entry['ambiguous_comparisons_by_cap'] = {str(s): table[s][1] for s in DP_CAPS}
        out.append(entry)
    return out


def controls(local, local_mass, R, rows, base):
    out = {}

    def rejects(name, f):
        try:
            f()
            out[name] = 'ACCEPTED'
        except ValueError as e:
            out[name] = 'rejected: ' + str(e)
    rejects('idle_rank_52_violates_halving_guard', lambda: C.model(local, M, FAMILIES, STAGES, CENTRE, R=52))
    rejects('local_mass_exceeds_coverage', lambda: C.model({1: 7300}, M, FAMILIES, STAGES, CENTRE))
    rejects('local_child_at_or_above_m_rejected', lambda: C.model({M: 1}, M, FAMILIES, STAGES, CENTRE))
    # R is the largest idle rank the outer halving guard admits, not a free choice
    out['halving_guard_boundary'] = 'yes' if 2 * R * R < M * M <= 2 * (R + 1) ** 2 else 'NO'
    # At a = 0 every child costs exactly r/m, so the per-call moment is total local mass / m
    # whatever the shape: the whole ceiling model is second-order in a and prefers no rank shape.
    def moment_at_zero(H):
        return sum(Q(r, M) * n for r, n in H.items())
    out['moment_independent_of_shape_at_a_zero'] = 'yes' if (
        moment_at_zero(S.greedy(int(local_mass), R)) == moment_at_zero({1: int(local_mass)})
        == Q(int(local_mass), M)) else 'NO'
    # where the cap divides the local mass, greedy is exact and the two bounds must coincide
    out['int_equals_frac_when_cap_divides_mass'] = 'yes' if all(
        Q(row['a_int']) == Q(row['a_frac']) for row in rows if int(local_mass) % row['s'] == 0) else 'NO'
    out['curve_stops_at_halving_guard'] = 'yes' if rows[-1]['s'] == R else 'NO'
    out['histograms_integer_and_exact_mass'] = 'yes' if all(
        all(isinstance(n, int) and n > 0 for n in row['histogram'].values())
        and sum(int(k) * v for k, v in row['histogram'].items()) == local_mass
        and max(int(k) for k in row['histogram']) <= row['s'] for row in rows) else 'NO'
    # the selected word is itself a cap-8 word, so the cap-8 optimum cannot be below it
    cap8 = Q([r for r in rows if r['s'] == 8][0]['a_int'])
    out['selected_word_at_or_below_cap8_optimum'] = 'yes' if base <= cap8 else 'NO'
    # monotone in the rank cap (asserted in curve()); restated as a recorded control
    out['monotone_in_rank_cap'] = 'yes'
    C.require(all(v.startswith('rejected') or v == 'yes' for v in out.values()), f'control failed: {out}')
    return out


def main():
    local, rec = selected()
    q = C.model(local, M, FAMILIES, STAGES, CENTRE)
    R, local_mass = q['R'], q['local_mass']
    base = cap(local)
    # This package re-derives the incumbent ceiling instead of trusting a stored
    # number, and cross-checks the recomputation against the pinned sibling result.
    sib = json.loads((ROOT / 'research/complex-local-word-ceiling/RESULT.json').read_text())
    C.require(Q(sib['ceiling']['a_ceiling']) == base, 'recomputed base ceiling differs from the sibling RESULT.json')

    rows = curve(local_mass, base, R)
    frac_min, int_min = first_clear(rows, 'a_frac'), first_clear(rows, 'a_int')
    C.require(int_min is not None, 'no rank cap in the guard range reaches the target')
    below = [r for r in rows if r['s'] == int_min - 1][0]
    out = dict(
        status='PASS_LOCAL_WORD_RANK_SHAPE_CEILING',
        base=dict(
            local_profile_per_call={str(r): n for r, n in sorted(local.items())},
            local_mass_per_call=fr(local_mass), idle_mass_per_call=fr(q['idle_mass']),
            live_families_per_call=fr(q['w']), idle_rank_cap=R,
            a_ceiling=fr(base), a_ceiling_decimal=dec(base), kappa=rec['kappa'],
            sibling_result_json_agrees=True),
        curve=rows,
        headroom=dict(
            target=str(TARGET),
            first_cap_clearing_target_fractional=frac_min,
            first_cap_clearing_target_integer=int_min,
            last_cap_below_target=int_min - 1,
            a_at_last_cap_below_target=below['a_int'],
            a_at_first_cap_clearing=below and [r for r in rows if r['s'] == int_min][0]['a_int'],
            best_cap=R, a_at_best_cap=rows[-1]['a_int'], a_frac_at_best_cap=rows[-1]['a_frac'],
            kappa_upper_at_best_cap=rows[-1]['kappa_upper_int'],
            ratio_best_cap_over_base=rows[-1]['ratio_int_over_base'],
            max_integrality_loss_percent=dec(max(Q(r['integrality_loss_percent']) for r in rows))),
        bimodal_min_children_at_target=bimodal(local_mass),
        independent_dp_checks=dp_checks(local_mass, R),
        controls=controls(local, local_mass, R, rows, base),
        scope='Exact ceiling arithmetic for the #1094 local word restated as a function of the '
              'largest paid local child rank, on the selected template (2*4*112 live data families, '
              'nine stages, centre charge 64), the PR1012 coverage law and the outer halving guard '
              'R = 51. a_frac is an ideal relaxation with fractional child counts and upper-bounds '
              'the cap-s class; a_int uses exact integer child counts and lower-bounds it. Neither '
              'models physical realisation. This is a scoped obstruction and a planning table, not a '
              'construction, not a new kappa, not a bound for other local words, port counts, '
              'templates, coverage laws or outer recipes, and not a supplier for the selected record.')
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(text)
    else:
        C.require((HERE / 'RESULT.json').read_text() == text, 'RESULT.json differs')
    h = out['headroom']
    print(out['status'], '| first cap clearing 1/99:', h['first_cap_clearing_target_integer'],
          '| at guard cap', R, 'a =', Q(h['a_at_best_cap']), 'kappa <=', h['kappa_upper_at_best_cap'],
          '| max integrality loss', h['max_integrality_loss_percent'], '%')


if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print('FAIL:', e)
        sys.exit(1)