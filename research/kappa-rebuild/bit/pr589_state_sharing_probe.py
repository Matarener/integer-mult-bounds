#!/usr/bin/env python3
"""Exact, fully invoiced helper-coalescing probe on the actual PR589 word.

The pinned predecessors are only read. This searches every pair of helper
roles whose complete forward frame timelines can share one monotone physical
register. Scalar endpoint validity is a separate exact gate; successful
candidates have their old-dirt compensation rebuilt and every arbitrary input
column replayed. Owned COPY ranks remain paid. Apache-2.0; substantial OpenAI
assistance. The retained PR589 source has its own eumemic/Claude attribution.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import time

import mixed_productive_bit as B

HERE = Path(__file__).resolve().parent


def load():
    path = HERE/'sources/pr589-regenerated/WORD.json.gz'
    data = path.read_bytes()
    B.need(sha256(data).hexdigest() == B.WORD_HASH, 'Exact PR589 source')
    w = json.loads(gzip.decompress(data))
    metadata = json.loads((path.parent/'records/frames.json').read_text())['frames']
    dimensions = [metadata[str(i)]['dim'] for i in range(len(w['frames']))]
    masks = [sum(1 << i for i in frame) for frame in w['frames']]
    return w, masks, dimensions


def alias_gates(gates, a, b):
    out = []
    for f, d, ss in gates:
        d = a if d == b else d
        src = set()
        for s in ss:
            s = a if s == b else s
            if s in src:
                src.remove(s)
            else:
                src.add(s)
        if d in src:
            return None
        if src:
            out.append([f, d, sorted(src)])
    return out


def raw_replay(w, A, BB, ret, val):
    for _, d, ss in A:
        for s in ss:
            val[d] ^= val[s]
    snap = [val[r] for r in ret]
    for t, ks in enumerate(w['scatter']):
        for k in ks:
            val[w['v']+t] ^= snap[k]
    for _, d, ss in BB:
        for s in ss:
            val[d] ^= val[s]
    return val


def rebuild(w, a, b, A, BB, ret):
    v, n = w['v'], 2*w['v']+w['R']
    full = next(i for i, f in enumerate(w['frames']) if len(f) == v)
    zero = next(i for i, f in enumerate(w['frames']) if not f)
    val = raw_replay(w, A, BB, ret, [1 << i for i in range(n)])
    helper_mask = ((1 << n)-1) ^ ((1 << (2*v))-1)
    D = []
    for t in range(v):
        B.need(val[v+t] & ((1 << (2*v))-1) == (1 << (v+t)) | (1 << t),
               'Raw source and target response')
        dirt = val[v+t] & helper_mask
        src = [i for i in range(2*v, n) if dirt >> i & 1]
        if src:
            D.append([zero, v+t, src])
    C = [[full, d, list(ss)] for f, d, ss in reversed(A+BB)
         if not v <= d < 2*v]
    rid = lambda r: r-int(r > b)
    def compact(gates):
        return [[f, rid(d), [rid(s) for s in ss]] for f, d, ss in gates]
    out = {k: value for k, value in w.items() if k not in ('A', 'B', 'C', 'D')}
    out.update(R=w['R']-1, A=compact(A), B=compact(BB), C=compact(C), D=compact(D),
               ret=[rid(r) for r in ret], start=w['start'][:b]+w['start'][b+1:],
               final=w['final'][:b]+w['final'][b+1:])
    return out


def exact_audit(w, masks, dims):
    v, n = w['v'], 2*w['v']+w['R']
    current = list(w['start'])
    values = [1 << i for i in range(n)]
    invoice, adds = Counter(), 0
    def climb(r, f):
        old = current[r]
        B.need(masks[old] & ~masks[f] == 0, 'Every frame transition remains nested')
        if old != f:
            B.need(dims[f] > dims[old], 'Every nontrivial transition increases rank')
            invoice[dims[f]-dims[old]] += 1
            current[r] = f
    for section in ('D', 'A', 'scatter', 'B', 'C'):
        if section == 'scatter':
            snapshot = [values[r] for r in w['ret']]
            invoice.update(dims[current[r]] for r in w['ret'])
            for t, ks in enumerate(w['scatter']):
                for k in ks:
                    values[v+t] ^= snapshot[k]
                    adds += 1
            continue
        for f, d, ss in w[section]:
            B.need(d not in ss and len(ss) == len(set(ss)), 'Invertible primitive operands')
            for r in [d]+ss:
                climb(r, f)
            for s in ss:
                values[d] ^= values[s]
                adds += 1
    for r, f in enumerate(w['final']):
        climb(r, f)
    expected = [(1 << i) ^ ((1 << (i-v)) if v <= i < 2*v else 0)
                for i in range(n)]
    B.need(values == expected, 'All arbitrary original/source/helper columns')
    return dict(paid=dict(sorted(invoice.items())), unit_ADDs=adds,
                arbitrary_columns=n, dirty_helpers=w['R'],
                owned_COPY_episodes=len(w['ret']),
                all_original_helpers_restored=True)


def price(audit, case):
    paid = Counter({int(r): 7*n for r, n in audit['paid'].items()})
    paid[7] += 2*B.V*sum(len(row['stages']) for row in case['idle_events'] if row['retained'])
    targets = Counter({8: 7*audit['dirty_helpers']})
    for term in case['factorization']['diagonal_monomials']:
        targets[(term & 1)+7*(term >> 1).bit_count()] += B.V
    B.need(max(paid) < min(targets), 'Strict child/job separation')
    def margin(c):
        return sum(n*r**(1-c) for r, n in targets.items())-sum(n*r**(1-c) for r, n in paid.items())
    lo, hi = 0., .01
    for _ in range(60):
        mid = (lo+hi)/2
        if margin(mid) > 0:
            lo = mid
        else:
            hi = mid
    return dict(paid=dict(sorted(paid.items())), targets=dict(sorted(targets.items())),
                rank_margin=sum(r*n for r, n in targets.items())-sum(r*n for r, n in paid.items()),
                floating_root_for_screen=lo,
                exact_margin_at_004=B.interval_row(B.margin_interval(paid, targets, Q(1, 250))))


def run():
    start = time.monotonic()
    w, masks, dims = load()
    v, n = w['v'], 2*w['v']+w['R']
    case = next(c for c in json.loads((HERE/'MIXED-PRODUCTIVE-BIT.json').read_text())['candidates']
                if c['pairs'] == 3)
    baseline = exact_audit(w, masks, dims)
    B.need(baseline['paid'] == dict(B.LOCAL), 'Pinned complete original tariff')
    uses = {r: [] for r in range(2*v, n)}
    forward = w['A']+w['B']
    for k, (f, d, ss) in enumerate(forward):
        for r in [d]+ss:
            if r in uses:
                uses[r].append((k, f))
    # Include the snapshot cut as a use, without fabricating a new frame.
    for r in w['ret']:
        prior = [f for k, f in uses[r] if k < len(w['A'])]
        uses[r].append((len(w['A'])-0.5, prior[-1] if prior else w['start'][r]))
    for r in uses:
        uses[r].sort()
    candidates, disjoint = [], []
    for a in uses:
        for b in range(a+1, n):
            previous = 0
            ok = True
            timeline = sorted(uses[a]+uses[b])
            for _, f in timeline:
                if previous & ~masks[f]:
                    ok = False
                    break
                previous = masks[f]
            if ok:
                candidates.append((a, b))
                if not uses[a] or not uses[b] or uses[a][-1][0] < uses[b][0][0] or uses[b][-1][0] < uses[a][0][0]:
                    disjoint.append((a, b))
    counts = Counter(total_helper_pairs=w['R']*(w['R']-1)//2,
                     monotone_frame_candidates=len(candidates),
                     disjoint_forward_lifetimes=len(disjoint))
    accepted, rejections = [], []
    for a, b in candidates:
        A, BB = alias_gates(w['A'], a, b), alias_gates(w['B'], a, b)
        if A is None or BB is None:
            counts['self_gate_reject'] += 1
            continue
        ret = [a if r == b else r for r in w['ret']]
        out = raw_replay(w, A, BB, ret, [1 << r if r < v else 0 for r in range(n)])
        failed = [t for t in range(v) if out[v+t] != 1 << t]
        if failed:
            counts['source_response_reject'] += 1
            if len(rejections) < 12:
                rejections.append(dict(pair=[a, b], wrong_targets=failed,
                                       wrong_source_coefficients=sum((out[v+t] ^ (1 << t)).bit_count() for t in failed)))
            continue
        new = rebuild(w, a, b, A, BB, ret)
        audit = exact_audit(new, masks, dims)
        counts['full_arbitrary_input_pass'] += 1
        invoice = price(audit, case)
        accepted.append(dict(pair=[a, b], audit=audit, global_p3=invoice,
                             canonical_word_sha256=B.digest(new)))
    # Consumer-only and producer-only rank lower bounds for the owned totals.
    values = [1 << r for r in range(n)]
    for _, d, ss in w['A']:
        for s in ss:
            values[d] ^= values[s]
    centers = [values[r] for r in w['ret']]
    source_mask = (1 << v)-1
    scatter = [sum(1 << k for k in row) for row in w['scatter']]
    center_audit = dict(owned_center_count=len(centers),
                        consumer_matrix_rank=B.bit_rank(scatter, len(centers)),
                        center_source_response_rank=B.bit_rank([x & source_mask for x in centers], v),
                        center_full_arbitrary_response_rank=B.bit_rank(centers, n),
                        current_center_rank_bill=63,
                        conclusion='The nine actual center signals are independent, and their consumer map is injective. A same-cut linear compression to eight signals cannot preserve all responses even before its frame-conversion and cleanup cost is charged.')
    accepted.sort(key=lambda row: row['global_p3']['floating_root_for_screen'], reverse=True)
    return dict(schema='actual-PR589-monotone-helper-state-sharing/1',
                status='PASS_EXHAUSTIVE_FINITE_PROBE',
                source_word_sha256=B.WORD_HASH,
                source_generator_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                baseline=baseline, baseline_global_p3=price(baseline, case),
                coverage=dict(counts), accepted=accepted, sample_response_rejections=rejections,
                owned_center_independence=center_audit,
                not_claimed=['No unrestricted scheduling lower bound.',
                             'No decoder-COPY charge removed without a new operator identity.',
                             'No exponent gain from a finite helper count alone.'],
                runtime_seconds=time.monotonic()-start)


if __name__ == '__main__':
    result = run()
    out = HERE/'PR589-STATE-SHARING-PROBE.json'
    out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'coverage', 'owned_center_independence', 'runtime_seconds')}, indent=2))
    if result['accepted']:
        print(json.dumps(result['accepted'][0], indent=2))
