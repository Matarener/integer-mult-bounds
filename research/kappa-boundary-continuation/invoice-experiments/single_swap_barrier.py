#!/usr/bin/env python3
"""Exact integer obstruction to improving the retained fill by one helper swap.

The obstruction ignores all clock and physical-family restrictions, so it
also excludes every admissible single swap. It does not exclude multi-item
moves, zero-cost preparatory swaps, a changed clock, or a changed native word.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json
from local_repack import read, rank, module, REPO


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--followup', type=Path, required=True)
    ap.add_argument('--out', type=Path, default=Path(__file__).with_name('SINGLE-SWAP-BARRIER.json'))
    args = ap.parse_args()
    data = args.followup/'artifact/live-source/research/staged544-producer-return/inputs'
    inv_path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    I = module(inv_path, 'single_swap_invoice')
    frozen_path = inv_path.parent/'evidence/RESULT.json'
    frozen = I.read(frozen_path)
    I.need(frozen['script_sha256'] == I.digest(inv_path), 'frozen invoice source pin')
    for rel, expected in frozen['m73_literal_allocation']['input_sha256'].items():
        I.need(I.digest(args.followup/rel) == expected, 'actual owner source pin: '+rel)
    order = read(data/'ORDER.json')
    dispatch = {(s, r): p for s, r, p in read(data/'DISPATCH.json')}
    width = {}
    for tag, p in (('base', 'gauge44'), ('extra', 'extra')):
        w = read(data/f'NATIVE-{tag}.json.gz')
        width[p] = [rank(w['frames'][w['final'][j]])-rank(w['frames'][w['start'][j]])
                    for j in range(224, 632)]
    by_time = [width[dispatch[tuple(call)]] for call in order]
    template = read(data/'TEMPLATE.json.gz')
    cap = {x['child']: x['rank'] for x in template['idle_children']}
    fill = read(data/'FILL.json.gz')
    rows = fill['rows']
    I.need(len(rows) == 3240*408, 'all actual helper roles')
    used = Counter()
    for i, (t, h, owner, child, port, offset) in enumerate(rows):
        I.need((t, h) == (i//408, i % 408), 'complete ordered source identities')
        bid = (owner*18+child)*112+port
        I.need(offset == used[bid], 'literal source compact offsets')
        used[bid] += by_time[t][h]
        I.need(used[bid] <= cap[child], 'exact original capacity')
    rem = {}
    hist = Counter()
    for owner in range(360):
        for child, capacity in cap.items():
            for port in range(112):
                bid = (owner*18+child)*112+port
                rem[bid] = capacity-used[bid]
                if rem[bid]:
                    hist[rem[bid]] += 1
    baseline = Counter({r: 3240*n for r, n in I.LOCAL.items()})
    baseline.update(hist)
    I.need(baseline == I.BASE, 'independent exact complete source profile')
    types = Counter()
    for t, h, owner, child, port, offset in rows:
        types[by_time[t][h], rem[(owner*18+child)*112+port]] += 1
    comparisons = []
    keys = sorted(types)
    for i, (wa, ra) in enumerate(keys):
        for wb, rb in keys[i:]:
            delta = wb-wa
            after_a, after_b = ra-delta, rb+delta
            if min(after_a, after_b) < 0:
                continue
            # For fixed total remainder, strict concavity makes the moment
            # strictly smaller exactly when the two remainders become more
            # unequal. This comparison is an exact integer statement.
            old_spread = abs(ra-rb)
            new_spread = abs(after_a-after_b)
            I.need(new_spread <= old_spread, 'no single feasible exchange improves any concave power')
            comparisons.append({'type_a': [wa, ra], 'type_b': [wb, rb],
                                'after_remainders': [after_a, after_b],
                                'old_spread': old_spread, 'new_spread': new_spread})
    result = {'status': 'PASS_EXACT_SINGLE_HELPER_SWAP_OBSTRUCTION',
              'script_sha256': I.digest(Path(__file__)),
              'shared_utility_sha256': I.digest(Path(__file__).with_name('local_repack.py')),
              'source_fill_sha256': I.digest(data/'FILL.json.gz'),
              'frozen_invoice_receipt_sha256': I.digest(frozen_path),
              'actual_helper_rows': len(rows), 'physical_idle_bins': len(rem),
              'actual_width_remainder_types': [[w, r, n] for (w, r), n in sorted(types.items())],
              'full_profile': dict(sorted(baseline.items())),
              'feasible_relaxed_type_pair_checks': comparisons,
              'proof': 'Let f(r)=r^p with0<p<1 and f(0)=0. For fixed s=x+y, f(x)+f(y) strictly decreases with |x-y|. Swapping helpers of widths wa,wb changes remainder pair(ra,rb) to(ra-(wb-wa),rb+(wb-wa)). Every feasible pair of actual width/remainder types has new spread no larger than the old spread, by the emitted integer census. Thus no such swap decreases the idle moment for any0<a<1, where p=1-a.',
              'scope': 'Every single two-helper owner exchange from this exact retained allocation, even with all source-time and physical-family restrictions dropped. The result does not exclude two or more exchanges, multi-item substitutions, changed clocks, changed helper identities/widths, or another allocation.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'types', len(types), 'feasible type pairs', len(comparisons))
    print('positive remainder types', [[w, r, n] for (w, r), n in sorted(types.items()) if r])


if __name__ == '__main__':
    main()
