"""Break-even price of a carrier for a third frame-593 rung removal.

Prices hypothetical edits of the complete target/paid profile published by
DreamingOfClouds's PR #6030 with the raw moment crossing used by that line:
the root of sum_r T_r r^(1-k) - sum_r P_r r^(1-k). Every sign is certified
with correctly rounded decimal ln/exp and an explicit error allowance.
Standard library only. Nick Petalas. Apache-2.0.
"""
import json
import sys
from decimal import Decimal as D, localcontext
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREC = 60
# Relative error allowance per moment: ln, one product and exp are each
# correctly rounded at PREC digits, and |t ln r| < 6, so every term has
# relative error below 10^(8-PREC); summing nonnegative terms keeps that bound.
REL = D(10) ** (10 - PREC)

# Complete profile of PR #6030, head 772dd10a5859a1d15f4851feb371519789213ad8,
# research/p104-helper470-twin-rung-removal/RESULT.json, complete_cost.
T6030 = {1: 252, 2: 144, 3: 72, 4: 1926, 5: 252, 6: 36, 7: 162, 8: 342, 9: 6930,
         17: 416, 25: 416, 33: 416, 41: 416, 49: 416, 57: 416, 65: 416, 73: 208,
         145: 208}
P6030 = {1: 41502, 2: 8226, 3: 8928, 4: 1800, 5: 2934, 6: 198, 7: 108, 8: 18,
         16: 416, 24: 416, 32: 416, 40: 416, 48: 416, 56: 416, 64: 416, 72: 208}
LOCALS = 18
# PR #6030's stated per-LOCAL deltas against #5907 (paid profile, credited helpers).
DP = {1: -2, 2: 1, 3: -2, 4: 1, 6: 1, 7: -1, 8: 1}
DT = {1: -1, 2: 1, 3: -1, 6: 1, 7: -1, 8: 1}
# Published raw crossing enclosures used as positive controls.
C6030 = (D('0.00312581155791'), D('0.00312581155792'))
C5907 = (D('0.00312528909884'), D('0.00312528909885'))


def need(ok, label):
    if not ok:
        raise SystemExit(f'FAIL: {label}')


def edit(prof, delta, times):
    out = dict(prof)
    for r, c in delta.items():
        out[r] = out.get(r, 0) + times * c
        need(out[r] >= 0, f'nonnegative count at rank {r}')
    return {r: n for r, n in out.items() if n}


def moment(prof, t):
    with localcontext() as ctx:
        ctx.prec = PREC
        return sum((n * (t * D(r).ln()).exp() for r, n in prof.items()), D(0))


def sign(T, P, k):
    """Certified sign of sum T r^(1-k) - sum P r^(1-k) at a decimal k."""
    with localcontext() as ctx:
        ctx.prec = PREC
        t = 1 - k
        a, b = moment(T, t), moment(P, t)
        gap, slack = a - b, REL * (a + b)
    need(abs(gap) > slack, f'sign resolved at k={k}')
    return 1 if gap > 0 else -1


def crossing(T, P, digits=14):
    """Certified enclosure (lo, lo+10^-digits) of the unique raw crossing in (0, 1/20)."""
    step = D(10) ** -digits
    lo, hi = 0, 5 * 10 ** (digits - 2)
    need(sign(T, P, D(0)) > 0 and sign(T, P, hi * step) < 0, 'crossing bracketed')
    while hi - lo > 1:
        m = (lo + hi) // 2
        if sign(T, P, m * step) > 0:
            lo = m
        else:
            hi = m
    return lo * step, hi * step


def below(T, P, k):
    """True when the crossing of (T, P) is certified to lie below k."""
    return sign(T, P, k) < 0


def run(mutate=None):
    T, P = dict(T6030), dict(P6030)
    if mutate:
        mutate(T, P)
    need(sum(T.values()) == 13444 and sum(P.values()) == 66834, 'published field and call counts')
    need(sum(r * n for r, n in T.items()) - sum(r * n for r, n in P.items()) == 760,
         'published rank surplus')
    need(sum(DP.values()) == -1 and sum(DT.values()) == 0, 'stated per-LOCAL deltas')
    need(not below(T, P, C6030[0]) and below(T, P, C6030[1]), 'reproduces #6030 crossing')
    prev = (edit(T, {r: LOCALS * c for r, c in DT.items()}, -1),
            edit(P, {r: LOCALS * c for r, c in DP.items()}, -1))
    need(not below(*prev, C5907[0]) and below(*prev, C5907[1]), 'reproduces #5907 crossing')

    twin = (edit(T, {r: LOCALS * c for r, c in DT.items()}, 1),
            edit(P, {r: LOCALS * c for r, c in DP.items()}, 1))
    twin_cross = crossing(*twin)
    need(twin_cross[0] > C6030[1], 'a free repeat of the twin delta would gain')

    # Any one added paid call, of any rank 1..145, defeats a twin-sized repeat.
    ranks = range(1, 146)
    total_fail = [r for r in ranks if not below(twin[0], edit(twin[1], {r: 1}, 1), C6030[0])]
    need(total_fail == [], 'one added paid call of every rank defeats the repeat')
    local_fail = [r for r in ranks if not below(twin[0], edit(twin[1], {r: LOCALS}, 1), C6030[0])]
    need(local_fail == [], 'one added paid call per LOCAL of every rank defeats the repeat')

    one_call = crossing(T, edit(P, {1: 1}, 1))
    need(one_call[1] < C6030[0], 'one added rank-1 call lowers the crossing')
    per_local = crossing(T, edit(P, {1: LOCALS}, 1))
    return {
        'claim': 'Raw-moment relaxation only; hypothetical edits of the PR #6030 published profile.',
        'controls': {'pr6030_crossing': [str(x) for x in C6030],
                     'pr5907_crossing': [str(x) for x in C5907]},
        'free_twin_repeat_crossing': [str(x) for x in twin_cross],
        'free_twin_repeat_gain_lower': str(twin_cross[0] - C6030[1]),
        'one_extra_rank1_call_crossing': [str(x) for x in one_call],
        'one_extra_rank1_call_per_local_crossing': [str(x) for x in per_local],
        'ranks_checked_for_added_call': [1, 145],
        'one_extra_rank1_call_loss_over_twin_gain_lower': str(
            ((C6030[0] - one_call[1]) / (twin_cross[1] - C6030[0])).quantize(D('0.01'), rounding='ROUND_FLOOR')),
    }


def controls():
    """Each damaged input must fail a named check."""
    damages = {
        'paid_count': lambda T, P: P.__setitem__(1, P[1] + 1),
        'target_rank_moved': lambda T, P: (T.__setitem__(9, T[9] - 1), T.__setitem__(10, 1)),
        'paid_rank_swapped': lambda T, P: (P.__setitem__(2, P[2] - 1), P.__setitem__(3, P[3] + 1),
                                           P.__setitem__(1, P[1] + 1), P.__setitem__(4, P[4] - 1)),
    }
    rejected = []
    for name, damage in damages.items():
        try:
            run(damage)
        except SystemExit:
            rejected.append(name)
    need(rejected == list(damages), 'every damaged profile is rejected')
    return rejected


def main():
    result = run()
    result['rejected_controls'] = controls()
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text())
        need(result == expected, 'RESULT.json matches the recomputation')
    print(json.dumps(result, indent=2, sort_keys=True))
    print('PASS_P104_RUNG_CARRIER_BREAK_EVEN')


if __name__ == '__main__':
    main()
