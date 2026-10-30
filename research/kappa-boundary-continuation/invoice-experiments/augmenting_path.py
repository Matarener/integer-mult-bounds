#!/usr/bin/env python3
"""Bounded remainder-token path search on the literal retained helper owners.

A path swaps width w with width w+1 within one actual call, moving one unit
of idle remainder through full bins until it reaches another nonempty bin.
Interior bins never reuse the incoming changed slot. Search uses one visit
per(call,width) context; failure is bounded and is not a global obstruction.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from argparse import ArgumentParser
from collections import Counter, deque
from pathlib import Path
import gzip
import json
import time
from local_repack import read, rank, module, REPO


def main():
    import numpy as np
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--followup', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds', type=float, default=60)
    ap.add_argument('--max-depth', type=int, default=32)
    args = ap.parse_args()
    data = args.followup/'artifact/live-source/research/staged544-producer-return/inputs'
    inv_path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    I = module(inv_path, 'path_invoice')
    frozen_path = inv_path.parent/'evidence/RESULT.json'
    frozen = I.read(frozen_path)
    for rel, expected in frozen['m73_literal_allocation']['input_sha256'].items():
        I.need(I.digest(args.followup/rel) == expected, 'actual source binding: '+rel)
    source = read(data/'FILL.json.gz')
    rows = np.array(source['rows'], dtype=np.int32)
    del source
    order = read(data/'ORDER.json')
    dispatch = {(s, r): p for s, r, p in read(data/'DISPATCH.json')}
    width_by_provider = {}
    for tag, p in (('base', 'gauge44'), ('extra', 'extra')):
        w = read(data/f'NATIVE-{tag}.json.gz')
        width_by_provider[p] = [rank(w['frames'][w['final'][r]])-rank(w['frames'][w['start'][r]]) for r in range(224, 632)]
    widths = np.array([width_by_provider[dispatch[tuple(call)]] for call in order], dtype=np.int8).reshape(-1)
    I.need(len(rows) == len(widths) == 3240*408, 'all physical helper roles')
    template = read(data/'TEMPLATE.json.gz')
    caps = {x['child']: x['rank'] for x in template['idle_children']}
    cap = np.tile(np.repeat([caps[c] for c in range(18)], 112), 360).astype(np.int16)
    binids = ((rows[:, 2]*18+rows[:, 3])*112+rows[:, 4]).copy()
    original_binids = binids.copy()
    remainder = cap-np.bincount(binids, weights=widths, minlength=len(cap)).astype(np.int16)
    I.need(int(min(remainder)) >= 0, 'retained capacities')
    profile = Counter({r: 3240*n for r, n in I.LOCAL.items()})
    profile.update(Counter(map(int, remainder[remainder > 0])))
    I.need(profile == I.BASE, 'complete original invoice')
    ordering = np.argsort(binids, kind='stable')
    offsets = np.r_[0, np.cumsum(np.bincount(binids, minlength=len(cap)))]
    contexts = {(t, w): np.flatnonzero(widths[t*408:(t+1)*408] == w)+t*408
                for t in range(3240) for w in range(4, 10)}
    start_rows = np.flatnonzero((remainder[binids] > 0) & (widths < 9))
    start_bins = sorted(set(map(int, binids[start_rows])),
                        key=lambda b: not any(widths[i] == 6 for i in ordering[offsets[b]:offsets[b+1]]))
    # State: bin, incoming removed original row, parent state, swap pair, depth.
    states = [(b, -1, -1, None, 0) for b in start_bins]
    queue = deque(range(len(states)))
    seen_contexts, seen_states = set(), set()
    began = time.monotonic()
    found, explored, maximum_depth = None, 0, 0
    def chain_bins(si):
        out = set()
        while si != -1:
            out.add(states[si][0])
            si = states[si][2]
        return out
    while queue and time.monotonic()-began < args.seconds:
        si = queue.popleft()
        b, incoming, parent, edge, depth = states[si]
        explored += 1
        maximum_depth = max(maximum_depth, depth)
        if depth >= args.max_depth:
            continue
        ancestors = None
        for a0 in ordering[offsets[b]:offsets[b+1]]:
            a = int(a0)
            if a == incoming:
                continue
            w, t = int(widths[a]), a//408
            if w >= 9 or (t, w) in seen_contexts:
                continue
            seen_contexts.add((t, w))
            if ancestors is None:
                ancestors = chain_bins(si)
            for d0 in contexts[t, w+1]:
                d = int(d0)
                target = int(binids[d])
                if target in ancestors or (target, d) in seen_states:
                    continue
                ns = len(states)
                states.append((target, d, si, (a, d), depth+1))
                seen_states.add((target, d))
                if remainder[target] > 0:
                    found = ns
                    break
                queue.append(ns)
            if found is not None:
                break
        if found is not None:
            break
    swaps = []
    first_step_barrier = None
    if found is None and not queue:
        initial_contexts = {(int(i)//408, int(widths[i])) for i in start_rows}
        expected_donors = {int(d) for t, w in initial_contexts for d in contexts[t, w+1]}
        actual_donors = {incoming for b, incoming, parent, edge, depth in states if depth == 1}
        untouched = Counter()
        for b, incoming, parent, edge, depth in states:
            if depth == 1:
                I.need(remainder[b] == 0, 'every first donor was originally full')
                untouched.update(int(widths[i]) for i in ordering[offsets[b]:offsets[b+1]] if i != incoming)
        if (expected_donors == actual_donors and initial_contexts == seen_contexts
                and set(untouched) <= {9}):
            I.need({w for t, w in initial_contexts} == {4, 6}, 'all possible starting widths')
            I.need({int(remainder[b]) for b in start_bins} == {1}, 'each starting bin has one remainder unit')
            first_step_barrier = {
                'all_initial_contexts': len(initial_contexts),
                'all_first_donor_rows': len(expected_donors),
                'untouched_width_census_over_first_donor_states': dict(sorted(untouched.items())),
                'complete_first_step_coverage_checked': True,
                'proof': 'Every positive-remainder bin with an outgoing unit swap has remainder1 and supplies width4 or width6. All same-call width5 or width7 donor rows are covered. Every donor bin is initially full, so a first step merely changes remainders(1,0) to(0,1), preserving price. After removing that donor, its untouched slots all have maximal width9. Thus no second unit step can use an untouched slot; no simple remainder-token path with a distinct incoming and outgoing slot can have length at least two.',
                'scope': 'The proposed same-call one-unit token path, with the incoming changed slot excluded at each interior bin. Multi-item exchanges, multiple interacting tokens, changed clocks, and arbitrary other move families are not excluded.'}
    if found is not None:
        si = found
        while states[si][2] != -1:
            swaps.append(states[si][3])
            si = states[si][2]
        swaps.reverse()
        visited = {int(binids[swaps[0][0]])}
        last_target = None
        for a, d in swaps:
            ba, bd = int(binids[a]), int(binids[d])
            I.need(a//408 == d//408 and int(widths[d])-int(widths[a]) == 1, 'literal same-call unit swap')
            I.need(ba != bd and bd not in visited, 'simple distinct-bin path')
            if last_target is not None:
                I.need(ba == last_target, 'token path continuity after prior mutation')
            I.need(remainder[ba] >= 1, 'available remainder token')
            binids[a], binids[d] = bd, ba
            remainder[ba] -= 1
            remainder[bd] += 1
            visited.add(bd)
            last_target = bd
        I.need(np.all(remainder == cap-np.bincount(binids, weights=widths, minlength=len(cap)).astype(np.int16)), 'fresh complete resulting capacities')
        # Every swap permutes owner families inside one call; the original
        # exact eligible family set and same-call injection are preserved.
        affected_calls = sorted({a//408 for pair in swaps for a in pair})
        for t in affected_calls:
            I.need(sorted(map(int, binids[t*408:(t+1)*408])) == sorted(map(int, original_binids[t*408:(t+1)*408])), 'same complete eligible owner multiset for every changed call')
        profile = Counter({r: 3240*n for r, n in I.LOCAL.items()})
        profile.update(Counter(map(int, remainder[remainder > 0])))
        I.need(sum(r*n for r, n in profile.items()) == 65088*360, 'unchanged complete raw invoice')
        before, after = I.moment(I.BASE, 73, 896*360, I.TARGET), I.moment(profile, 73, 896*360, I.TARGET)
        I.need(after[1] < before[0], 'strict exact moment improvement')
    result = {'status': 'NO_BOUNDED_AUGMENTING_PATH_FOUND' if found is None else 'PASS_LITERAL_AUGMENTING_PATH_AND_EXACT_INVOICE',
              'script_sha256': I.digest(Path(__file__)), 'source_fill_sha256': I.digest(data/'FILL.json.gz'),
              'frozen_invoice_receipt_sha256': I.digest(frozen_path),
              'parameters': {'seconds': args.seconds, 'maximum_depth': args.max_depth},
              'start_bins': len(start_bins), 'states_explored': explored,
              'states_discovered': len(states), 'contexts_expanded': len(seen_contexts),
              'maximum_depth_explored': maximum_depth, 'queue_exhausted': not queue,
              'search_seconds': time.monotonic()-began,
              'swaps': swaps, 'complete_profile': dict(sorted(profile.items())),
              'scope': 'Bounded one-visit-per-call/width context discovery. Each emitted path is subsequently checked as a literal simple-bin sequence of same-call owner swaps, preserving actual source eligibility and same-call physical-family injection. A search failure does not certify all possible augmenting paths.'}
    if first_step_barrier is not None:
        result['status'] = 'PASS_EXACT_FRESH_SLOT_UNIT_TOKEN_PATH_OBSTRUCTION'
        result['complete_first_step_obstruction'] = first_step_barrier
    args.out.mkdir(parents=True, exist_ok=True)
    if swaps:
        result['root'] = I.root(profile, 73, 896*360)
        result['target_residual'] = I.interval(after[0]-1, after[1]-1)
        result['strictly_passes_target'] = after[1] < 1
        result['affected_calls'] = affected_calls
        result['productive_families'] = 322560
        result['physical_family_upper'] = 323069
        rows[:, 2] = binids//(18*112)
        rows[:, 3] = binids//112 % 18
        rows[:, 4] = binids % 112
        used = np.zeros(len(cap), dtype=np.int16)
        for i, bid in enumerate(binids):
            rows[i, 5] = used[bid]
            used[bid] += int(widths[i])
        I.need(np.all(cap-used == remainder), 'all1321920 compact integer offsets')
        raw = json.dumps({'columns': ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'dispatch_overrides': [], 'rows': rows.tolist()}, separators=(',', ':')).encode()
        (args.out/'FILL.json.gz').write_bytes(gzip.compress(raw, mtime=0))
        result['fill_payload_sha256'] = __import__('hashlib').sha256(raw).hexdigest()
    (args.out/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'contexts', len(seen_contexts), 'depth', maximum_depth, 'swaps', len(swaps))
    if swaps:
        print('root', result['root']['decimal'], 'target', result['strictly_passes_target'])


if __name__ == '__main__':
    main()
