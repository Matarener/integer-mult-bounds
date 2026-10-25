#!/usr/bin/env python3
"""Bounded asynchronous-clock pattern nomination for the seven-call geometry.

Each owner window receives224 physical bins (112 ports on both sides).
Demand is imposed at each literal call time. A per-owner-window time cap224
is necessary for family injectivity, but this LP is only a nomination screen:
it does not expand pattern slots into a literal physical assignment.
Apache-2.0; substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from pathlib import Path
import json
import time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

from seven_geometry import schedule, need

WIDTHS = tuple(range(4, 10))
DEMAND = (26, 2, 18, 53, 96, 213)
CAPS = (16, 8, 32, 8, 32, 16)


def patterns(cap):
    def recurse(i, left, prefix):
        if i == len(WIDTHS):
            yield prefix, left
            return
        for count in range(left//WIDTHS[i]+1):
            yield from recurse(i+1, left-count*WIDTHS[i], prefix+(count,))
    return list(recurse(0, cap, ()))


def order_for(replicas, slope):
    # The tie order is explicit and source order is strict in each replica.
    return sorted(((s, r) for s in range(7) for r in range(replicas)),
                  key=lambda item: (slope*item[0]+item[1], item[0], item[1]))


def windows_for(order, replicas):
    clock = {call: t for t, call in enumerate(order)}
    windows = []
    for owner in range(replicas):
        touched, t, window_id = {}, None, 0
        need(all(clock[s, owner] < clock[s+1, owner] for s in range(6)), 'source stage order')
        for event in schedule():
            kind = event['kind']
            if kind == 'local':
                t = clock[event['stage'], owner]
                touched[event['pair']] = t
            elif kind == 'bridge':
                touched[event['src']] = touched[event['dst']] = t
            elif kind == 'idle':
                cap = (8*(event['to_level']+1) if event['from_level'] == -1 else
                       8*(event['to_level']-event['from_level']))
                need(cap == CAPS[window_id], 'geometry rank binding')
                windows.append(dict(owner=owner, group=window_id, pair=event['pair'],
                                    rank=cap, lo=touched.get(event['pair'], -1), hi=t))
                window_id += 1
        need(window_id == 6, 'all idle intervals emitted')
    return windows


def screen(replicas, slope, a, out, seconds):
    begin = time.monotonic()
    order = order_for(replicas, slope)
    windows = windows_for(order, replicas)
    P = {cap: patterns(cap) for cap in set(CAPS)}
    variables = []
    time_rows = []
    for j, window in enumerate(windows):
        variables.extend(('p', j, counts, left) for counts, left in P[window['rank']])
        for t in range(window['lo']+1, window['hi']+1):
            time_rows.append((j, t))
            variables.extend(('y', j, t, w) for w in range(6))
    nw, nt = len(windows), len(order)
    rows = 7*nw+6*nt
    A = lil_matrix((rows, len(variables)), dtype=float)
    rhs = np.zeros(rows)
    rhs[:nw] = 224
    for t in range(nt):
        rhs[7*nw+6*t:7*nw+6*t+6] = DEMAND
    B = lil_matrix((len(time_rows), len(variables)), dtype=float)
    br = {key: j for j, key in enumerate(time_rows)}
    objective = np.zeros(len(variables))
    for col, item in enumerate(variables):
        if item[0] == 'p':
            _, j, counts, left = item
            A[j, col] = 1
            for wi, count in enumerate(counts):
                A[nw+6*j+wi, col] = count
            objective[col] = left**(1-a)-left if left else 0
        else:
            _, j, t, wi = item
            A[nw+6*j+wi, col] = -1
            A[7*nw+6*t+wi, col] = 1
            B[br[j, t], col] = 1
    lp = linprog(objective, A_eq=A.tocsr(), b_eq=rhs, A_ub=B.tocsr(),
                 b_ub=np.full(len(time_rows), 224), bounds=(0, None), method='highs',
                 options={'time_limit': seconds})
    result = dict(status='FLOATING_ASYNC_CLOCK_CANDIDATE' if lp.success else 'NO_ASYNC_CLOCK_CANDIDATE',
                  replicas=replicas, slope=str(slope), source_order=order, windows=windows,
                  variables=len(variables), equations=rows, necessary_family_caps=len(time_rows),
                  solver_status=int(lp.status), solver_message=lp.message, seconds=time.monotonic()-begin,
                  scope='Floating-point nomination with exact window endpoints and all time/width demand. No literal pattern-slot matching or whole-call physical allocation is claimed.')
    if lp.success:
        idle = Counter()
        primal = []
        for item, value in zip(variables, lp.x):
            if value > 1e-7:
                primal.append([item, float(value)])
                if item[0] == 'p' and item[3]:
                    idle[item[3]] += float(value)
        result['idle_per_replica'] = {str(r): n/replicas for r, n in sorted(idle.items())}
        result['raw_idle_mass_error'] = sum(r*n for r, n in idle.items())-2142*replicas
        result['floating_primal'] = primal
        result['floating_profile_residual_at_a'] = (sum(7*replicas*n*(r/57)**(1-a) for r, n in
                                                     {1:2440, 2:725, 3:224, 4:102, 5:20, 8:8}.items())+
                                                  sum(n*(r/57)**(1-a) for r, n in idle.items()))/(672*replicas)-1
    out.mkdir(parents=True, exist_ok=True)
    name = 'CLOCK-T%d-S%s.json' % (replicas, str(slope).replace('/', '_'))
    (out/name).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ('status','replicas','slope','variables','seconds','solver_status','floating_profile_residual_at_a','idle_per_replica')}, sort_keys=True), flush=True)
    return result


if __name__ == '__main__':
    p = ArgumentParser(description=__doc__)
    p.add_argument('--replicas', type=int, default=8)
    p.add_argument('--slopes', nargs='+', default=['1/2','1','2','4'])
    p.add_argument('--endpoint', type=float, default=0.0017334270395898442)
    p.add_argument('--seconds', type=float, default=20)
    p.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'clock-nominations')
    args = p.parse_args()
    for slope in args.slopes:
        screen(args.replicas, Fraction(slope), args.endpoint, args.out.resolve(), args.seconds)
