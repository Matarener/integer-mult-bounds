#!/usr/bin/env python3
"""Bounded same-call exchange search on the exact retained T360 helper fill.

Each move swaps two actual helper owners within one call. Thus source windows
and same-call physical-family uniqueness are preserved without a new clock.
Only a strictly better full invoice is emitted. Apache-2.0; substantial OpenAI
assistance under the user's direction, October2026.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
import gzip
import importlib.util
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def module(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def rank(v):
    p = {}
    for x in v:
        while x:
            b = x.bit_length()
            if b in p:
                x ^= p[b]
            else:
                p[b] = x
                break
    return len(p)


def main():
    import numpy as np

    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--followup', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds', type=float, default=60)
    ap.add_argument('--lookahead', action='store_true', help='Try exact two-swap augmenting moves through a full32 bin')
    ap.add_argument('--cross-first', action='store_true', help='Allow the first augmenting exchange across two eligible calls')
    args = ap.parse_args()
    data = args.followup/'artifact/live-source/research/staged544-producer-return/inputs'
    inv = module(REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py', 'repack_invoice')
    fill = read(data/'FILL.json.gz')
    rows = np.array(fill['rows'], dtype=np.int32)
    del fill
    order = read(data/'ORDER.json')
    dispatch = {(s, r): pid for s, r, pid in read(data/'DISPATCH.json')}
    width_by_provider = {}
    for tag, provider in (('base', 'gauge44'), ('extra', 'extra')):
        w = read(data/f'NATIVE-{tag}.json.gz')
        width_by_provider[provider] = [rank(w['frames'][w['final'][r]])-rank(w['frames'][w['start'][r]]) for r in range(224, 632)]
    widths = np.array([width_by_provider[dispatch[tuple(call)]] for call in order], dtype=np.int8).reshape(-1)
    template = read(data/'TEMPLATE.json.gz')
    caps = {c['child']: c['rank'] for c in template['idle_children']}
    binids = ((rows[:, 2]*18+rows[:, 3])*112+rows[:, 4]).copy()
    cap = np.tile(np.repeat([caps[c] for c in range(18)], 112), 360).astype(np.int16)
    remainder = cap-np.bincount(binids, weights=widths, minlength=len(cap)).astype(np.int16)
    assert min(remainder) >= 0
    start_hist = Counter(map(int, remainder[remainder > 0]))
    expected = Counter(inv.BASE)
    expected.subtract({r: 3240*n for r, n in inv.LOCAL.items()})
    assert +expected == start_hist
    # Floating-point comparisons only choose proposals. The emitted profile is
    # subsequently certified by the exact outward-rational engine.
    p = 1-float(inv.TARGET)
    prices = np.array([r**p for r in range(49)])
    moves = []
    began = time.monotonic()
    passes = 0
    if args.lookahead:
        # Existing obstructed16-bin [6,9] -> full16 [7,9].
        # A full32 [7,8,8,9] accepts that6, then upgrades an8 to9
        # from a positive-remainder bin. Both swaps are within their own
        # actual calls, so all window and nonalias predicates are preserved.
        ordering = np.argsort(binids, kind='stable')
        starts = np.r_[0, np.cumsum(np.bincount(binids, minlength=len(cap)))]
        altered = {}
        lower = np.zeros(len(cap), dtype=np.int32)
        upper = np.zeros(len(cap), dtype=np.int32)
        physical = np.zeros(len(cap), dtype=np.int32)
        if args.cross_first:
            clock = {tuple(v): i for i, v in enumerate(order)}
            plan = read(data/'PLAN.json.gz')
            family = {c: 2*plan['pairs'][str(c)]+plan['sides'][str(c)] for c in caps}
            for owner in range(360):
                touched = {}
                curtime = None
                for ev in template['execution_schedule']:
                    if ev['kind'] == 'local_cover_sweep':
                        curtime = clock[ev['stage'], owner]
                        pair = next(e['pair'] for e in template['recipe'] if e['kind'] == 'local' and e['stage'] == ev['stage'])
                        touched[pair] = curtime
                    elif ev['kind'] == 'bridge':
                        touched[ev['src']] = touched[ev['dst']] = curtime
                    elif ev['kind'] == 'idle_cover_sweep':
                        for child in ev['child_indices']:
                            if child not in caps:
                                continue
                            first = (owner*18+child)*112
                            lower[first:first+112] = touched.get(ev['pair'], -1)+1
                            upper[first:first+112] = curtime
                            physical[first:first+112] = owner*896+family[child]*112+np.arange(112)
            all_sevens = np.flatnonzero(widths == 7)
        def members(b):
            return altered.get(b, ordering[starts[b]:starts[b+1]].tolist())
        def replace_member(b, old, new):
            items = members(b)
            items.remove(old)
            items.append(new)
            altered[b] = items
        sixes = np.flatnonzero((widths == 6) & (remainder[binids] == 1))
        for a0 in sixes:
            a = int(a0)
            ba = int(binids[a])
            if remainder[ba] != 1:
                continue
            t = a//408
            done = False
            candidates = range(t*408, (t+1)*408)
            if args.cross_first:
                bids = binids[all_sevens]
                times = all_sevens//408
                candidates = all_sevens[(times >= lower[ba]) & (times <= upper[ba]) &
                                       (lower[bids] <= t) & (upper[bids] >= t) &
                                       (cap[bids] == 32) & (remainder[bids] == 0)]
            for b0 in candidates:
                b = int(b0)
                bb = int(binids[b])
                if widths[b] != 7 or cap[bb] != 32 or remainder[bb] != 0:
                    continue
                tb = b//408
                if args.cross_first and tb != t:
                    if (np.any(physical[binids[t*408:(t+1)*408]] == physical[bb]) or
                        np.any(physical[binids[tb*408:(tb+1)*408]] == physical[ba])):
                        continue
                for c in members(bb):
                    if widths[c] != 8:
                        continue
                    tc = c//408
                    ds = [d for d in range(tc*408, (tc+1)*408) if widths[d] == 9 and remainder[binids[d]] > 0 and binids[d] not in (ba, bb)]
                    if not ds:
                        continue
                    d = max(ds, key=lambda d: int(remainder[binids[d]]))
                    bd = int(binids[d])
                    assert len({ba, bb, bd}) == 3 and (args.cross_first or a//408 == b//408) and c//408 == d//408
                    binids[a], binids[b] = bb, ba
                    binids[c], binids[d] = bd, bb
                    remainder[ba] -= 1
                    remainder[bd] += 1
                    replace_member(ba, a, b)
                    replace_member(bb, b, a)
                    replace_member(bb, c, d)
                    replace_member(bd, d, c)
                    moves += [[a, b], [c, d]]
                    done = True
                    break
                if done:
                    break
        print('two-swap augmentations', len(moves)//2, flush=True)
    while time.monotonic()-began < args.seconds:
        added = 0
        for t in range(3240):
            begin = t*408
            stop = begin+408
            while True:
                groups = {}
                for i in range(begin, stop):
                    groups.setdefault((int(widths[i]), int(remainder[binids[i]])), i)
                best = None
                gain = 1e-12
                keys = list(groups)
                for wa, ra in keys:
                    for wb, rb in keys:
                        delta = wb-wa
                        if not (0 < delta <= ra):
                            continue
                        after_a, after_b = ra-delta, rb+delta
                        improvement = prices[ra]+prices[rb]-prices[after_a]-prices[after_b]
                        if improvement > gain:
                            gain = improvement
                            best = groups[wa, ra], groups[wb, rb], delta
                if best is None:
                    break
                a, b, delta = best
                ba, bb = int(binids[a]), int(binids[b])
                assert a//408 == b//408 and ba != bb
                remainder[ba] -= delta
                remainder[bb] += delta
                binids[a], binids[b] = bb, ba
                moves.append([a, b])
                added += 1
            if time.monotonic()-began >= args.seconds:
                break
        passes += 1
        print('pass', passes, 'new_moves', added, 'total_moves', len(moves), flush=True)
        if not added:
            break
    after_hist = Counter(map(int, remainder[remainder > 0]))
    profile = Counter({r: 3240*n for r, n in inv.LOCAL.items()})
    profile.update(after_hist)
    before = inv.moment(inv.BASE, 73, 896*360, inv.TARGET)
    after = inv.moment(profile, 73, 896*360, inv.TARGET)
    result = {'status': 'NO_SAME_CALL_EXCHANGE_IMPROVEMENT' if not moves else 'EXACTLY_PRICED_FEASIBLE_EXCHANGE_CANDIDATE_PENDING_FULL_AUDIT',
              'moves': moves, 'passes': passes, 'search_seconds': time.monotonic()-began,
              'before_idle_profile': dict(sorted(start_hist.items())),
              'after_idle_profile': dict(sorted(after_hist.items())),
              'full_profile': dict(sorted(profile.items())),
              'before_target_residual': inv.interval(before[0]-1, before[1]-1),
              'after_target_residual': inv.interval(after[0]-1, after[1]-1),
              'source_fill_sha256': inv.digest(data/'FILL.json.gz')}
    if moves:
        assert after[1] < before[0]
        result['root'] = inv.root(profile, 73, 896*360)
        print('CANDIDATE ROOT', result['root']['decimal'], flush=True)
        rows[:, 2] = binids//(18*112)
        rows[:, 3] = binids//112 % 18
        rows[:, 4] = binids % 112
        used = np.zeros(len(cap), dtype=np.int16)
        for i, bid in enumerate(binids):
            rows[i, 5] = used[bid]
            used[bid] += int(widths[i])
        assert np.all(cap-used == remainder)
        args.out.mkdir(parents=True, exist_ok=True)
        payload = {'columns': ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'],
                   'dispatch_overrides': [], 'rows': rows.tolist()}
        raw = json.dumps(payload, separators=(',', ':')).encode()
        (args.out/'FILL.json.gz').write_bytes(gzip.compress(raw, mtime=0))
        result['emitted_fill_sha256'] = inv.digest(args.out/'FILL.json.gz')
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'SEARCH.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
