#!/usr/bin/env python3
"""Extended receiver/source sharing with reusable canonical frame components.

Uses the exact covector/transposed identities of the adaptive continuation
(Nick Petalas and retained contributor credit), with a larger observation
window and previously unsearched transpose-A branch. Floating frame prices
only nominate candidates; no emitted word is admitted without full checks.
Apache-2.0. Prepared with substantial OpenAI assistance.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OLD = REPO / 'research/kappa-adaptive-continuation/native-alternatives'
sys.path.insert(0, str(OLD))
import fanout_search as F
import opt_frames as O
import joint_fanout_search as J


def install_cache():
    original = O.solve_component
    cache = {}
    stats = Counter()

    def solve(comp, edges, lo, hi, max_bucket):
        renumber = {old: new for new, old in enumerate(comp)}
        owned = []
        for _, a, af, b, bf in edges:
            if a not in renumber and b not in renumber:
                continue
            na = renumber.get(a, -1)
            nb = renumber.get(b, -1)
            left = () if na >= 0 else (lo[a] if a >= 0 else af)
            right = () if nb >= 0 else (lo[b] if b >= 0 else bf)
            owned.append((0, na, left, nb, right))
        low = tuple(lo[i] for i in comp)
        high = tuple(hi[i] for i in comp)
        key = (tuple(owned), low, high, max_bucket)
        if key in cache:
            stats['hits'] += 1
            normalized, count = cache[key]
        else:
            stats['misses'] += 1
            normalized, count = original(tuple(range(len(comp))), owned, low, high, max_bucket)
            cache[key] = normalized, count
        return {old: normalized[new] for old, new in renumber.items()}, count

    O.solve_component = solve
    O.phi = F.phi = lambda r: r ** (1 - 0.001745) if r else 0.0
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--word', type=Path, default=OLD / 'candidate/BORROW-WORD-43base.json.gz')
    ap.add_argument('--section', choices=['A', 'B', 'restore'], default='A')
    ap.add_argument('--transpose', action='store_true')
    ap.add_argument('--max-gap', type=int, default=1000)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--limit', type=int, default=100000)
    ap.add_argument('--seconds', type=float, default=900)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    w = F.read(args.word)
    sections = F.expand(w)
    events = J.transposed(sections[args.section]) if args.transpose else sections[args.section]
    groups, reads, writes = F.pair_catalog(events, args.max_gap)
    indexed = []
    for (a, b, q, ae, be), pairs in groups.items():
        for chosen, lo, hi in F.clusters(pairs, a, b, reads, writes):
            if args.section == 'A' and (len(events) - hi if args.transpose else lo) < w['prelude_events']:
                continue
            indexed.append((a, b, q, chosen, lo, hi))
    print('INDEXED', len(indexed), 'seconds', round(time.monotonic() - started, 3), flush=True)
    cache_stats = install_cache()
    # Cache/canonicalization positive control is checked against uncached output.
    baseline, base_result = O.optimize(w)
    if base_result['delta']:
        raise ValueError(('baseline must reproduce current optimal profile', base_result))
    stats = Counter()
    records = []
    attempted_indices = []
    selected = indexed[args.start:args.start + args.limit]
    for index, (a, b, q, chosen, lo, hi) in enumerate(selected, args.start):
        if time.monotonic() - started > args.seconds:
            stats['time_bound_reached'] = 1
            break
        attempted_indices.append(index)
        stats['attempted'] += 1
        if args.transpose:
            changed, _, _ = J.transpose_mutation(w, args.section, events, chosen, lo, hi, a, b, q)
        else:
            changed, _, _ = F.mutation(w, sections, args.section, chosen, lo, hi, a, b, q, (), ())
        try:
            changed, result = O.optimize(changed)
        except (ValueError, AssertionError) as exc:
            stats['infeasible_or_capacity'] += 1
            tag = str(exc.args[0][0] if exc.args and isinstance(exc.args[0], tuple) else exc.args[0])
            stats['reject_' + tag] += 1
            continue
        stats['feasible'] += 1
        if result['saving'] > 1e-9:
            name = 'WORD-' + str(index) + '.json.gz'
            payload = json.dumps(changed, sort_keys=True, separators=(',', ':')).encode()
            (args.out / name).write_bytes(gzip.compress(payload, mtime=0))
            record = {'index': index, 'source_a': a, 'source_b': b, 'coefficient': str(q),
                      'chosen': chosen, 'lo': lo, 'hi': hi, 'optimization': result,
                      'word': name, 'word_payload_sha256': hashlib.sha256(payload).hexdigest()}
            records.append(record)
            (args.out / ('CANDIDATE-' + str(index) + '.json')).write_text(json.dumps(record, indent=2) + '\n')
            print('CANDIDATE', index, json.dumps(result, sort_keys=True), flush=True)
        if stats['attempted'] % 100 == 0:
            print('PROGRESS', index, dict(stats), dict(cache_stats), 'seconds', round(time.monotonic() - started, 2), flush=True)
            (args.out / 'PROGRESS.json').write_text(json.dumps({'last_index': index, 'stats': dict(stats), 'candidates': records}, indent=2) + '\n')
    receipt = {'status': 'BOUNDED_EXACT_GRAPH_IDENTITIES_WITH_FLOAT_FRAME_NOMINATION',
               'new_supplier_admitted': False, 'section': args.section, 'transpose': args.transpose,
               'max_gap': args.max_gap, 'start': args.start, 'limit': args.limit,
               'total_indexed': len(indexed), 'completed_indices': attempted_indices,
               'stats': dict(stats), 'cache_stats': dict(cache_stats), 'candidates': records,
               'seconds': time.monotonic() - started,
               'source_pins': {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [Path(__file__), args.word, OLD/'fanout_search.py', OLD/'opt_frames.py', OLD/'joint_fanout_search.py']},
               'scope': 'Literal covector or transpose identity on the named section; all initial states preserved algebraically. Native phases, exact prices, complete owner/precision bill and supplier admission remain separate. Uncompleted indices and capacity failures are not exclusions.'}
    (args.out / 'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print('FINISHED', json.dumps({'stats': dict(stats), 'candidates': len(records), 'total_indexed': len(indexed)}), flush=True)


if __name__ == '__main__':
    main()
