#!/usr/bin/env python3
"""Certify the exact attained ceiling of the rank-capped complex local mass, idle remainder integral.

`research/complex-local-word-ceiling` (parent, pinned unmodified) prices the selected complex local
word with two relaxations: the idle remainder sits in `1646/51` *fractional* rank-51 children, and
its rank-cap continuation reshapes the local paid mass into `5586/s` *fractional* rank-s children.
Both are upper bounds on what a real packing can do, because real packings use integer child
multisets.

This verifier computes, for every cap s = 1..51 the outer halving guard allows, the **attained
optimum over joint integer packings**: the local paid mass in integer children of rank <= s and the
idle remainder in integer children of rank <= R = 51, both by dynamic programming over the mass axis,
then bisects the bracket the two certified predicates support:

  * an explicit joint integer packing whose certified moment is < 1 witnesses the saving, and
  * the certified lower bound of every joint integer packing > 1 rejects it.

usage: verify.py [--write]
Nick Petalas, with AI assistance. Apache-2.0.
"""
import json
import random
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
import ceiling as C  # noqa: E402
import joint as J  # noqa: E402

M, PAIRS, PORTS, STAGES, CENTRE = 73, 4, 112, 9, 64
FAMILIES = 2 * PAIRS * PORTS
PAID_MASS, IDLE_MASS, IDLE_CAP = 5586, 1646, C.max_idle_rank(M)
W = Q(FAMILIES, STAGES)
GRID = Q(1, 10 ** 8)
GRID_FINE = Q(1, 10 ** 12)
ONE_99 = Q(1, 99)
CAPS = list(range(1, IDLE_CAP + 1))


def dec(x, digits=18):
    return f'{float(x):.{digits}g}'


def selected():
    """Re-derive the selected complex local word and its split from the pinned certificate."""
    rec = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    asm = json.loads((ROOT / rec['certificate']).read_text())
    ind = json.loads((ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    H = {int(r): n for r, n in asm['complex_profile'].items()}
    idle = {int(r): n for r, n in ind['owner']['idle'].items()}
    N, live = ind['price']['calls'], ind['price']['live']
    C.require(H == {int(r): n for r, n in ind['owner']['profile'].items()}, 'profile mismatch')
    C.require(N % STAGES == 0 and live == FAMILIES * (N // STAGES), 'live stock is not 2*pairs*V per replica')
    mass = sum(r * n for r, n in H.items())
    C.require(mass == (M - 1) * live + CENTRE * N, 'coverage identity mass = 72W + 64N fails')
    local = {}
    for r, n in H.items():
        k = n - idle.get(r, 0)
        C.require(k >= 0 and k % N == 0, f'local rank {r} not uniform per call')
        if k:
            local[r] = k // N
    return local, Q(rec['kappa'])


def bisect(value, grid, lo=Q(0), hi=Q(1, 20)):
    """Grid bracket [a_lo, a_hi] for a monotone certified value: value(a_lo) < 1, value(a_hi) > 1."""
    C.require(value(hi) > 1 and value(lo) < 1, 'search window does not bracket one')
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        if value(mid) < 1:
            lo = mid
        else:
            hi = mid
    return lo, hi


def ideal(cap, grid=GRID):
    """Class relaxation: fractional rank-`cap` children for the paid mass, fractional idle block.

    Same object as the parent's `ceiling()` on the reshaped profile `{cap: 5586/cap}`; re-derived
    here from `child_cost` so the two are independent paths to the same number.
    """
    return bisect(lambda a: (Q(PAID_MASS, cap) * C.child_cost(cap, M, a)[0]
                             + Q(IDLE_MASS, IDLE_CAP) * C.child_cost(IDLE_CAP, M, a)[0]) / W, grid)


def greedy_hist(cap):
    """Largest-first greedy integer paid histogram: floor(5586/cap) rank-cap children + remainder."""
    k, rem = divmod(PAID_MASS, cap)
    hist = {}
    if k:
        hist[cap] = k
    if rem:
        hist[rem] = 1
    return hist


def hist_lower(hist, a):
    return Q(sum(n * J.scaled_lower(r, M, a) for r, n in hist.items()), J.SCALE)


def greedy_frac_idle(cap, grid=GRID):
    """Greedy integer paid histogram with the *fractional* idle block: the live rank-cap table's row."""
    hist = greedy_hist(cap)
    return bisect(lambda a: (hist_lower(hist, a)
                             + Q(IDLE_MASS, IDLE_CAP) * C.child_cost(IDLE_CAP, M, a)[0]) / W, grid)


def joint_bracket(cap, lo_seed=None, hi_seed=None, grid=GRID):
    """Certified bracket [a_lo, a_hi] for the attained joint integer ceiling of the cap-`cap` class.

    The seeds are only starting points: both acceptance and rejection are re-checked by the
    certified predicates before the bisection uses them, and the generic window is the fallback.
    """
    lo = Q(0) if lo_seed is None else lo_seed
    _, high, _, _ = J.moment_bounds(PAID_MASS, cap, IDLE_MASS, IDLE_CAP, M, W, lo)
    if not high < 1:
        lo = Q(0)
        _, high, _, _ = J.moment_bounds(PAID_MASS, cap, IDLE_MASS, IDLE_CAP, M, W, lo)
    C.require(high < 1, 'no witnessed saving in the cap class')

    hi = Q(1, 20) if hi_seed is None else hi_seed
    low, _, _, _ = J.moment_bounds(PAID_MASS, cap, IDLE_MASS, IDLE_CAP, M, W, hi)
    if not low > 1:
        hi = Q(1, 20)
        low, _, _, _ = J.moment_bounds(PAID_MASS, cap, IDLE_MASS, IDLE_CAP, M, W, hi)
    C.require(low > 1, 'no rejected saving in the cap class')
    C.require(hi > lo, 'seed window is inverted')

    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        low, high, ph, ih = J.moment_bounds(PAID_MASS, cap, IDLE_MASS, IDLE_CAP, M, W, mid)
        if high < 1:
            lo = mid
        elif low > 1:
            hi = mid
        else:
            raise ValueError('enclosure too wide to separate the grid point')
    _, _, ph, ih = J.moment_bounds(PAID_MASS, cap, IDLE_MASS, IDLE_CAP, M, W, lo)
    return lo, hi, ph, ih


def sample_hist(mass, cap, rng):
    """A uniformly drawn feasible integer histogram of `mass` with ranks 1..cap."""
    hist, rest = {}, mass
    while rest:
        r = rng.randint(1, min(cap, rest))
        hist[r] = hist.get(r, 0) + 1
        rest -= r
    return hist


def main():
    local, kappa = selected()
    q = C.model(local, M, FAMILIES, STAGES, CENTRE)
    C.require(q['local_mass'].denominator == 1 and q['idle_mass'].denominator == 1,
              'paid or idle mass is not integral in this model')
    C.require(int(q['local_mass']) == PAID_MASS and int(q['idle_mass']) == IDLE_MASS,
              'mass split differs from the pinned values')
    C.require(q['w'] == W and q['R'] == IDLE_CAP, 'template quantities differ from the pinned model')

    rows, prev_lo, greedy_gap_rows = [], Q(0), 0
    rng = random.Random(20261018)
    for cap in CAPS:
        ideal_lo, ideal_hi = ideal(cap)
        g_lo, g_hi = greedy_frac_idle(cap)
        lo, hi, ph, ih = joint_bracket(cap, lo_seed=prev_lo, hi_seed=ideal_hi + GRID)
        dp_paid, dp_hist = J.best_hist(PAID_MASS, cap, M, lo)
        greedy_paid = sum(n * J.scaled_lower(r, M, lo) for r, n in greedy_hist(cap).items())
        C.require(dp_paid <= greedy_paid, 'greedy paid histogram beats the dynamic program')
        greedy_gap_rows += dp_paid < greedy_paid
        for hist, mass, rank_cap in ((ph, PAID_MASS, cap), (ih, IDLE_MASS, IDLE_CAP)):
            C.require(sum(r * n for r, n in hist.items()) == mass, 'histogram does not conserve mass')
            C.require(all(1 <= r <= rank_cap for r in hist), 'histogram uses a rank outside its cap')
        C.require(Q(hi) <= ideal_hi + GRID, 'joint bracket is not at or below the class relaxation')
        C.require(lo >= prev_lo or rows == [], 'joint bracket is not monotone in the cap')
        prev_lo = lo
        rows.append(dict(
            cap=cap,
            ideal_a=dec(ideal_hi),
            greedy_frac_idle_a=dec(g_hi),
            joint_lo=dec(lo),
            joint_hi=dec(hi),
            joint_kappa_upper=dec(hi / (1 + hi)),
            joint_scale_over_selected_kappa=dec((hi / (1 + hi)) / kappa, 6),
            paid_dp_equals_greedy=(dp_paid == greedy_paid),
            paid_dp_histogram_equals_greedy=(dp_hist == greedy_hist(cap)),
            paid_dp_histogram={str(r): n for r, n in sorted(dp_hist.items())},
            idle_histogram={str(r): n for r, n in sorted(ih.items())},
            integrality_loss_percent=dec(100 * (ideal_hi - hi) / ideal_hi, 6),
            paid_rounding_percent=dec(100 * (ideal_hi - g_hi) / ideal_hi, 6),
            idle_rounding_percent=dec(100 * (g_hi - hi) / ideal_hi, 6),
            joint_lo_fraction=str(lo),
        ))

    crossing = [r['cap'] for r in rows if Q(r['joint_lo_fraction']) > ONE_99]
    C.require(crossing == list(range(44, 52)),
              'the 1/99 crossing under the joint integer model is not cap 44')

    # The parent's own ceiling() on the reshaped fractional profile is the same object as `ideal`.
    parent_rows = {}
    for cap in (8, 16, 51):
        parent_hi = C.ceiling({cap: Q(PAID_MASS, cap)}, M, FAMILIES, STAGES, CENTRE, grid=GRID)[1]
        mine = next(Q(r['ideal_a']) for r in rows if r['cap'] == cap)
        C.require(abs(mine - parent_hi) <= GRID, 'class relaxation disagrees with the parent ceiling()')
        parent_rows[str(cap)] = [dec(parent_hi), dec(mine)]

    # Fine-grid refinement at three caps: the coarse bracket must contain the fine one.
    fine = {}
    for cap in (8, 16, 51):
        lo, hi, _, _ = joint_bracket(cap, grid=GRID_FINE)
        row = next(r for r in rows if r['cap'] == cap)
        C.require(Q(row['joint_lo_fraction']) <= lo and hi <= Q(row['joint_hi']),
                  'fine bracket escapes the coarse bracket')
        fine[str(cap)] = [dec(lo), dec(hi)]

    # Reported column of the live rank-cap table (not on main): reproduced independently at its grid.
    published = {'44': '0.0103695754', '51': '0.0135848308'}
    reproduced = {}
    for cap in (44, 51):
        mine_fine = greedy_frac_idle(cap, grid=GRID_FINE)[1]
        C.require(abs(mine_fine - Q(published[str(cap)])) < Q(1, 10 ** 10),
                  'the published rank-cap column does not reproduce')
        reproduced[str(cap)] = [dec(mine_fine), published[str(cap)]]

    # Live paid-mass-elimination package (#3799): its full-elimination endpoint is this class
    # relaxation at the guard cap. One object, two packages, re-derived here independently.
    elimination_endpoint = '0.013675160009708'
    mine_endpoint = ideal(IDLE_CAP, grid=GRID_FINE)[1]
    C.require(abs(mine_endpoint - Q(elimination_endpoint)) < Q(1, 10 ** 9),
              'the published full-elimination endpoint does not equal this class relaxation')
    reproduced['paid_mass_elimination_endpoint_vs_class_relaxation'] = [dec(mine_endpoint),
                                                                       elimination_endpoint]

    # Sampling control: no drawn joint integer packing of a class reaches the rejected saving.
    sampled = []
    for cap in (8, 16, 44, 51):
        hi = Q(next(r for r in rows if r['cap'] == cap)['joint_hi'])
        for _ in range(25):
            v = (hist_lower(sample_hist(PAID_MASS, cap, rng), hi)
                 + hist_lower(sample_hist(IDLE_MASS, IDLE_CAP, rng), hi)) / W
            C.require(v > 1, 'a sampled joint packing reaches the rejected saving')
        sampled.append(cap)

    worst = max(rows, key=lambda r: Q(r['integrality_loss_percent']))
    worst_paid = max(rows, key=lambda r: Q(r['paid_rounding_percent']))
    worst_idle = max(rows, key=lambda r: Q(r['idle_rounding_percent']))
    sel_row = next(r for r in rows if r['cap'] == 8)
    guard = rows[-1]
    out = dict(
        status='PASS_COMPLEX_JOINT_INTEGER_CAP_CEILING',
        model=dict(parent_width=M, pairs=PAIRS, ports=PORTS, stages=STAGES, families=FAMILIES,
                   centre_charge=CENTRE, paid_mass=PAID_MASS, idle_mass=IDLE_MASS,
                   idle_cap=IDLE_CAP, live_families_per_call=str(W),
                   selected_kappa=str(kappa), caps=CAPS),
        cap_sweep=rows,
        headline=dict(
            first_cap_clearing_one_99=int(crossing[0]),
            crossing_caps=crossing,
            joint_a_at_cap_44=next(r['joint_hi'] for r in rows if r['cap'] == 44),
            joint_kappa_at_cap_44=next(r['joint_kappa_upper'] for r in rows if r['cap'] == 44),
            joint_a_at_guard_cap=guard['joint_hi'],
            joint_kappa_at_guard_cap=guard['joint_kappa_upper'],
            joint_scale_over_selected_at_guard_cap=guard['joint_scale_over_selected_kappa'],
            worst_integrality_loss_percent=worst['integrality_loss_percent'],
            worst_integrality_loss_cap=worst['cap'],
            worst_paid_rounding_percent=worst_paid['paid_rounding_percent'],
            worst_paid_rounding_cap=worst_paid['cap'],
            worst_idle_rounding_percent=worst_idle['idle_rounding_percent'],
            worst_idle_rounding_cap=worst_idle['cap'],
            caps_where_paid_dp_beats_greedy=greedy_gap_rows,
            incumbent_word_cap_class=8,
            joint_a_for_incumbent_cap_class=sel_row['joint_hi'],
            joint_scale_for_incumbent_cap_class=sel_row['joint_scale_over_selected_kappa'],
        ),
        controls=dict(
            profile_rederived_from_pinned_certificate=True,
            coverage_identity_rechecked=True,
            paid_mass_and_idle_mass_pinned=[PAID_MASS, IDLE_MASS],
            class_relaxation_vs_parent_ceiling=parent_rows,
            fine_grid_bracket_inside_coarse=fine,
            sampled_joint_packings_never_reach_rejected_saving=sampled,
            histogram_mass_conserved_and_capped=True,
            joint_bracket_below_class_relaxation_every_cap=True,
            joint_lo_monotone_in_cap=True,
            greedy_paid_histogram_never_beats_dynamic_program=(greedy_gap_rows == 0),
            dynamic_program_histogram_equals_greedy_at_every_cap=all(
                r['paid_dp_histogram_equals_greedy'] for r in rows),
            live_rank_cap_column_reproduced_at_its_grid=reproduced,
            brackets_witnessed_on_both_sides=True,
            bid_ask_spread_of_every_bracket=str(GRID),
        ),
        scope='Attained-optimum bound inside the ceiling model of research/complex-local-word-ceiling, '
              'for one fixed paid local mass 5586 and idle remainder 1646 per call, m = 73, '
              '2*4*112 live data families per nine-stage replica, centre charge 64, the PR1012 '
              'coverage law and the outer halving guard R = 51. The local paid mass is delivered as '
              'integer children of rank <= cap and the idle remainder as integer children of rank '
              '<= 51; both pools are minimised jointly. It is not a bound for other local words, '
              'port counts, templates, coverage laws or outer recipes, it does not check physical '
              'realizability of any histogram, and no kappa is claimed: the selected record is '
              'unchanged.',
    )
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(text)
    else:
        C.require((HERE / 'RESULT.json').read_text() == text, 'RESULT.json differs')
    print(out['status'],
          'crossing_cap', out['headline']['first_cap_clearing_one_99'],
          'joint_a_44', out['headline']['joint_a_at_cap_44'],
          'joint_a_51', out['headline']['joint_a_at_guard_cap'],
          'worst_integrality_loss_pct', out['headline']['worst_integrality_loss_percent'],
          'paid_dp_beats_greedy_caps', out['headline']['caps_where_paid_dp_beats_greedy'])


if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print('FAIL:', e)
        sys.exit(1)
