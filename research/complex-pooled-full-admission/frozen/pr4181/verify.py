#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Literal owner audit and exact root for the 1,080-call fourth-entry fill (standard library only).

The four words, their native receipts, the clock (ORDER), template, plan and the owner walk are PR4088's
(research/staged544-mixed-fourth-entry), imported unchanged. Only the dispatch selector and the fill change:
tick t < 1080 uses the four-entry word of its orientation, every later tick the three-entry word.
"""
import gzip, json, sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED = HERE.parent / 'staged544-mixed-fourth-entry'
sys.path.insert(0, str(PRED))
_argv = sys.argv; sys.argv = [sys.argv[0]]
import owner_verify as OV          # PR4088 literal owner walk (unchanged)
from verify import read, need      # PR4088 helpers
from vendor import exact_root as E # PR3945/4076 rational log/exp enclosures
sys.argv = _argv
FOURTH = 1080


def reject(name, fn):
    try: fn()
    except (ValueError, AssertionError): return name
    raise ValueError('accepted mutant: ' + name)


def context(selector=lambda t: t < FOURTH):
    P = PRED
    order = read(P / 'owner/ORDER.json'); clock = {tuple(v): t for t, v in enumerate(order)}
    need(len(order) == 3240 and set(clock) == {(s, r) for s in range(9) for r in range(360)}, 'all calls')
    need(all(clock[s, r] < clock[s + 1, r] for r in range(360) for s in range(8)), 'source order')
    template = read(P / 'owner/TEMPLATE.json.gz'); plan = read(P / 'owner/PLAN.json.gz')
    children = {x['child']: x['rank'] for x in template['idle_children']}
    pair = {x['stage']: x['pair'] for x in template['recipe'] if x['kind'] == 'local'}
    family = {c: 2 * plan['pairs'][str(c)] + plan['sides'][str(c)] for c in children}
    windows = {}
    for o in range(360):
        touched = {}; tick = None
        for e in template['execution_schedule']:
            k = e['kind']
            if k == 'local_cover_sweep': tick = clock[e['stage'], o]; touched[pair[e['stage']]] = tick
            elif k == 'bridge': touched[e['src']] = tick; touched[e['dst']] = tick
            elif k == 'idle_cover_sweep':
                for c in e['child_indices']:
                    if c in children:
                        need((o, c) not in windows, 'duplicate owner child'); windows[o, c] = (children[c], touched.get(e['pair'], -1), tick)
            else: need(k in ['bank_padding_cover_sweep', 'translate_every_live_family', 'terminal_Y_translations', 'terminal'], 'schedule kind')
    old = read(P / 'owner/DISPATCH.json')
    expected = [[s, r, pid + ('-four' if selector(clock[s, r]) else '')] for s, r, pid in old]
    provider = {(s, r): pid for s, r, pid in expected}
    I = OV.I; widths = {}; local = {}
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        origin = read(P / f'owner/old-NATIVE-{tag}.json.gz')['helper_origin']
        for kind, suffix in [('THREE', ''), ('FOUR', '-four')]:
            w = read(P / f'inputs/{kind}-{tag}.json.gz')
            need(origin == sorted(set(range(224, 704)) - set(w['removed'])), 'native helper order')
            widths[pid + suffix] = [len(I.b(w['helper_final'].get(str(r), I.FULL))) - len(I.b(w['start_extra'].get(str(r), []))) for r in origin]
            local[pid + suffix] = {int(k): v for k, v in w['report']['local_profile'].items()}
    return (order, provider, windows, family, widths, local), expected


def main():
    if not __debug__: raise SystemExit('assertions required')
    ctx, dispatch = context()
    need(read(HERE / 'owner/MIXED-DISPATCH.json') == dispatch, 'committed dispatch equals the t < 1080 rule')
    need(sum(p.endswith('-four') for p in ctx[1].values()) == FOURTH, 'exactly 1080 fourth-entry calls')
    rows = read(HERE / 'owner/FILL.json.gz')['rows']
    profile, idle = OV.walk(rows, ctx)
    r = read(HERE / 'RESULT.json')
    need(profile == {int(k): v for k, v in r['profile'].items()} and idle == {int(k): v for k, v in r['idle'].items()}, 'declared histogram')
    lo, hi = Q(r['root_lower']), Q(r['root_upper'])
    need(hi - lo == Q(1, 10 ** 24), 'grid bracket')
    E.certify_bracket(profile, lo, hi)
    pred = read(PRED / 'RESULT.json')
    pl, pu = Q(pred['root_lower']), Q(pred['root_upper'])
    E.certify_bracket({int(k): v for k, v in pred['profile'].items()}, pl, pu)
    kappa = lo - Q(1, 10 ** 46) - Q(1, 10 ** 70)
    need(Q(r['conditional_kappa']) == kappa and kappa > pu, 'strict improvement over PR4088')
    need(E.moment(E.signed(profile), kappa)[1] < 0, 'padded endpoint')
    need(sum(k * v for k, v in profile.items()) == 65088 * 360, 'rank mass')
    out = []
    if '--controls' in sys.argv:
        ctx109, _ = context(lambda t: t * 109 % 324 < 109)
        out.append(reject('pr4088_selector_with_this_fill', lambda: OV.walk(rows, ctx109)))
        ctx1079, _ = context(lambda t: t < FOURTH - 1)
        out.append(reject('one_fourth_call_reverted', lambda: OV.walk(rows, ctx1079)))
        bad = [list(x) for x in rows[:2]] + rows[2:]; bad[1][2:5] = bad[0][2:5]
        out.append(reject('same_call_family', lambda: OV.walk(bad, ctx)))
        bad = [list(rows[0])] + rows[1:]; bad[0][5] += 1
        out.append(reject('offset_hole', lambda: OV.walk(bad, ctx)))
        out.append(reject('next_grid_point', lambda: E.certify_bracket(profile, hi, hi + Q(1, 10 ** 24))))
        out.append(reject('pr4088_profile_at_new_root', lambda: E.certify_bracket({int(k): v for k, v in pred['profile'].items()}, lo, hi)))
    print(json.dumps({'status': 'PASS_POOLED_CEILING_FILL', 'fourth_calls': FOURTH, 'roles': len(rows), 'idle': idle,
                      'root_bracket': [r['root_lower_decimal'], r['root_upper_decimal']], 'gain_over_pr4088_upper': str(kappa - pu),
                      'controls': out}, sort_keys=True))


if __name__ == '__main__':
    main()
