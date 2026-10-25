#!/usr/bin/env python3
"""Bounded integer repacking within identical, source-derived idle windows.

The retained PR3638/borrow43 aggregate method motivates this small independent
adapter. It holds every class's actual time/width demand fixed and changes only
its integer bin patterns, then realizes each accepted pattern literally.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import json
from pathlib import Path
import random
import time

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp
from local_repack import read, rank, module, REPO


WID = tuple(range(4, 10))


@lru_cache(None)
def patterns(cap):
    out = []
    def rec(i, rem, cur):
        if i == len(WID):
            out.append(tuple(cur))
            return
        for k in range(rem//WID[i]+1):
            rec(i+1, rem-k*WID[i], cur+[k])
    rec(0, cap, [])
    return out


def realize(patterns_used, demands, n, rng):
    slots = [list(p) for p, count in sorted(patterns_used.items()) for _ in range(count)]
    assert len(slots) == n
    rem = list(map(sum, slots))
    bytime = defaultdict(list)
    for (t, w), count in demands.items():
        bytime[t] += [w]*count
    out = [[] for _ in slots]
    for t in sorted(bytime, key=lambda t: (-len(bytime[t]), rng.random())):
        used = set()
        avail = {w: sum(bool(b[w-4]) for b in slots) for w in set(bytime[t])}
        widths = list(bytime[t])
        rng.shuffle(widths)
        for w in sorted(widths, key=avail.get):
            possible = [b for b in range(n) if b not in used and slots[b][w-4]]
            if not possible:
                return None
            b = max(possible, key=lambda b: (rem[b], slots[b][w-4], rng.random()))
            slots[b][w-4] -= 1
            rem[b] -= 1
            used.add(b)
            out[b].append((t, w))
    assert not any(rem)
    return out


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--followup', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds', type=float, default=120)
    args = ap.parse_args()
    began = time.monotonic()
    data = args.followup/'artifact/live-source/research/staged544-producer-return/inputs'
    inv = module(REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py', 'class_invoice')
    fill = read(data/'FILL.json.gz')
    rows = np.array(fill['rows'], dtype=np.int32)
    del fill
    order = read(data/'ORDER.json')
    clock = {tuple(v): i for i, v in enumerate(order)}
    dispatch = {(s, r): p for s, r, p in read(data/'DISPATCH.json')}
    wprovider = {}
    for tag, provider in (('base', 'gauge44'), ('extra', 'extra')):
        w = read(data/f'NATIVE-{tag}.json.gz')
        wprovider[provider] = [rank(w['frames'][w['final'][r]])-rank(w['frames'][w['start'][r]]) for r in range(224, 632)]
    widths = np.array([wprovider[dispatch[tuple(call)]] for call in order], dtype=np.int8).reshape(-1)
    template = read(data/'TEMPLATE.json.gz')
    caps = {c['child']: c['rank'] for c in template['idle_children']}
    windows = {}
    for owner in range(360):
        touched = {}
        t = None
        for ev in template['execution_schedule']:
            kind = ev['kind']
            if kind == 'local_cover_sweep':
                t = clock[ev['stage'], owner]
                pair = next(e['pair'] for e in template['recipe'] if e['kind'] == 'local' and e['stage'] == ev['stage'])
                touched[pair] = t
            elif kind == 'bridge':
                touched[ev['src']] = touched[ev['dst']] = t
            elif kind == 'idle_cover_sweep':
                for c in ev['child_indices']:
                    if c in caps:
                        windows[owner, c] = caps[c], touched.get(ev['pair'], -1)+1, t
    cls = defaultdict(list)
    for (owner, c), key in windows.items():
        cls[key] += [(owner*18+c)*112+p for p in range(112)]
    binids = ((rows[:, 2]*18+rows[:, 3])*112+rows[:, 4]).copy()
    cap = np.tile(np.repeat([caps[c] for c in range(18)], 112), 360).astype(np.int16)
    counts = np.zeros((len(cap), 6), dtype=np.int16)
    np.add.at(counts, (binids, widths-4), 1)
    remainder = cap-counts@np.array(WID)
    demands = defaultdict(Counter)
    rowsets = defaultdict(list)
    for i, bid in enumerate(binids):
        key = windows[int(rows[i, 2]), int(rows[i, 3])]
        demands[key][i//408, int(widths[i])] += 1
        rowsets[key].append(i)
    p = 1-float(inv.TARGET)
    price = np.array([r**p-r for r in range(49)])
    rng = random.Random(20261019)
    candidates = []
    keys = sorted(cls, key=lambda k: -sum(int(remainder[b]) == 1 and counts[b, 2] > 0 for b in cls[k]))
    tried = improved_lp = 0
    for key in keys:
        if time.monotonic()-began > args.seconds:
            break
        cap0, lo, hi = key
        bins = cls[key]
        if not any(remainder[b] for b in bins) or not rowsets[key]:
            continue
        ps = patterns(cap0)
        A = np.vstack([np.ones(len(ps)), np.array(ps, dtype=float).T])
        rhs = np.r_[len(bins), counts[bins].sum(axis=0)]
        c = price[cap0-np.array(ps)@np.array(WID)]
        old = float(sum(price[int(remainder[b])] for b in bins))
        lp = linprog(c, A_eq=A, b_eq=rhs, bounds=(0, None), method='highs')
        tried += 1
        if not lp.success or lp.fun >= old-1e-9:
            continue
        improved_lp += 1
        solver = milp(c*10**8, integrality=np.ones(len(ps)), bounds=Bounds(0, len(bins)),
                      constraints=LinearConstraint(A, rhs, rhs), options={'time_limit': 3})
        if solver.x is None:
            continue
        x = np.rint(solver.x).astype(np.int64)
        if not np.all(A@x == rhs) or c@x >= old-1e-9:
            continue
        used_patterns = Counter({ps[i]: int(n) for i, n in enumerate(x) if n})
        assignment = None
        for _ in range(12):
            assignment = realize(used_patterns, demands[key], len(bins), rng)
            if assignment is not None:
                break
        if assignment is None:
            continue
        stock = defaultdict(list)
        for i in rowsets[key]:
            stock[i//408, int(widths[i])].append(i)
        for b, events in zip(bins, assignment):
            for event in events:
                i = stock[event].pop()
                assert lo <= i//408 <= hi
                binids[i] = b
        assert not any(stock.values())
        candidates.append({'class': key, 'bins': len(bins), 'old_pressure': old,
                           'new_pressure': float(c@x), 'patterns': [[list(q), n] for q, n in used_patterns.items()]})
        print('ACCEPT', key, 'pressure_gain', old-float(c@x), flush=True)
        # Disjoint classes are independently realized; price and full audit come
        # after at least one actual assignment has been reconstructed.
    remainder = cap-np.bincount(binids, weights=widths, minlength=len(cap)).astype(np.int16)
    idle = Counter(map(int, remainder[remainder > 0]))
    profile = Counter({r: 3240*n for r, n in inv.LOCAL.items()})
    profile.update(idle)
    result = {'status': 'NO_IDENTICAL_WINDOW_CLASS_IMPROVEMENT' if not candidates else 'EXACTLY_PRICED_LITERAL_CLASS_CANDIDATE_PENDING_FULL_AUDIT',
              'classes_tried': tried, 'strict_lp_improvement_classes': improved_lp, 'changes': candidates,
              'full_profile': dict(sorted(profile.items())), 'idle_profile': dict(sorted(idle.items())),
              'source_fill_sha256': inv.digest(data/'FILL.json.gz'), 'search_seconds': time.monotonic()-began}
    args.out.mkdir(parents=True, exist_ok=True)
    if candidates:
        assert inv.moment(profile, 73, 896*360, inv.TARGET)[1] < inv.moment(inv.BASE, 73, 896*360, inv.TARGET)[0]
        result['root'] = inv.root(profile, 73, 896*360)
        print('CANDIDATE ROOT', result['root']['decimal'], flush=True)
        rows[:, 2] = binids//(18*112)
        rows[:, 3] = binids//112 % 18
        rows[:, 4] = binids % 112
        used = np.zeros(len(cap), dtype=np.int16)
        for i, b in enumerate(binids):
            rows[i, 5] = used[b]
            used[b] += int(widths[i])
        payload = {'columns': ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'dispatch_overrides': [], 'rows': rows.tolist()}
        raw = json.dumps(payload, separators=(',', ':')).encode()
        (args.out/'FILL.json.gz').write_bytes(gzip.compress(raw, mtime=0))
        result['emitted_fill_sha256'] = inv.digest(args.out/'FILL.json.gz')
    (args.out/'SEARCH.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'tried', tried, 'LP_improved', improved_lp, flush=True)


if __name__ == '__main__':
    main()
