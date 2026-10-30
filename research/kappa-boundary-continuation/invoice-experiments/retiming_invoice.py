#!/usr/bin/env python3
"""Price each actual helper identity under a one-line entry-retiming hypothesis.

The hypothetical local change is -1 H1 and -1 hosted width per affected call.
All physical owners are retained, and repeated appearances in a single bin
are combined before that bin's new terminal remainder is priced. No native
word is asserted by this screen. Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as F
from argparse import ArgumentParser
import json
from pathlib import Path
import numpy as np
from local_repack import read, rank, module, REPO


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--followup', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    data = args.followup/'artifact/live-source/research/staged544-producer-return/inputs'
    I = module(REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py', 'retiming_price')
    frozen_path = REPO/'research/kappa-global-continuation/invoice-analysis/evidence/RESULT.json'
    frozen = I.read(frozen_path)
    I.need(frozen['script_sha256'] == I.digest(Path(I.__file__)), 'frozen invoice interface binding')
    I.need(frozen['arithmetic_engine_sha256'] == I.digest(I.ENGINE_PATH), 'outward-rational engine binding')
    for rel, expected in frozen['m73_literal_allocation']['input_sha256'].items():
        path = args.followup/rel
        I.need(I.digest(path) == expected, 'frozen allocation input binding: '+rel)
    fill = read(data/'FILL.json.gz')
    rows = np.array(fill['rows'], dtype=np.int32)
    del fill
    order = read(data/'ORDER.json')
    dispatch = {(s, r): p for s, r, p in read(data/'DISPATCH.json')}
    wprovider = {}
    origins = {}
    for tag, provider in (('base', 'gauge44'), ('extra', 'extra')):
        word = read(data/f'NATIVE-{tag}.json.gz')
        wprovider[provider] = [rank(word['frames'][word['final'][r]])-rank(word['frames'][word['start'][r]]) for r in range(224, 632)]
        origins[provider] = word['helper_origin']
    widths = np.array([wprovider[dispatch[tuple(c)]] for c in order], dtype=np.int8).reshape(-1)
    binids = (rows[:, 2]*18+rows[:, 3])*112+rows[:, 4]
    template = read(data/'TEMPLATE.json.gz')
    caps = {c['child']: c['rank'] for c in template['idle_children']}
    cap = np.tile(np.repeat([caps[c] for c in range(18)], 112), 360)
    remaining = cap-np.bincount(binids, weights=widths, minlength=len(cap)).astype(np.int64)
    I.need(min(remaining) >= 0, 'original exact capacities')
    original_idle = Counter(map(int, remaining[remaining > 0]))
    baseline = Counter({r: 3240*n for r, n in I.LOCAL.items()})
    baseline.update(original_idle)
    I.need(baseline == I.BASE, 'actual retained baseline composition')
    original_target_moment = I.moment(baseline, 73, 896*360, I.TARGET)
    cases = []
    for helper in range(408):
        bids, counts = np.unique(binids[helper::408], return_counts=True)
        delta = Counter({1: -3240})
        stock = Counter()
        for b0, k0 in zip(bids, counts):
            b, k = int(b0), int(k0)
            old, new = int(remaining[b]), int(remaining[b])+k
            I.need(new <= cap[b], 'shrinking positive helper widths preserves capacity')
            if old:
                delta[old] -= 1
            delta[new] += 1
            stock[old, k] += 1
        delta = Counter({r: n for r, n in delta.items() if n})
        full = Counter(baseline)
        full.update(delta)
        I.need(min(full.values()) >= 0 and sum(r*n for r, n in full.items()) == 65088*360,
               'complete unchanged raw mass')
        price = I.moment(full, 73, 896*360, I.TARGET)
        item = {'helper': helper, 'native_register': 224+helper,
                'borrowed_word_origin_by_provider': {p: labels[helper] for p, labels in origins.items()},
                'old_width_by_provider': {p: w[helper] for p, w in wprovider.items()},
                'changed_calls': 3240, 'distinct_affected_bins': len(bids),
                'maximum_same_helper_multiplicity_in_one_bin': int(max(counts)),
                'original_remainder_and_multiplicity': [[r, k, n] for (r, k), n in sorted(stock.items())],
                'complete_profile_delta': {str(r): n for r, n in sorted(delta.items())},
                'target_residual': I.interval(price[0]-1, price[1]-1),
                'beats_target': price[1] < 1,
                'strictly_beats_actual_baseline': price[1] < original_target_moment[0],
                'price_lower_sort_key': price[0]}
        cases.append(item)
    cases.sort(key=lambda x: x['price_lower_sort_key'])
    # Exact root brackets for the leading identities and the retained544 role.
    selected = set(x['helper'] for x in cases[:12]) | {labels.index(544) for labels in origins.values()}
    for item in cases:
        item.pop('price_lower_sort_key')
        if item['helper'] in selected:
            h = Counter(I.BASE)
            h.update({int(r): n for r, n in item['complete_profile_delta'].items()})
            item['root'] = I.root(h, 73, 896*360)
    result = {'status': 'PASS_EXACT_ACTUAL_OWNER_ENTRY_RETIMING_PRICE_SCREEN',
              'script_sha256': I.digest(Path(__file__)), 'frozen_invoice_receipt_sha256': I.digest(frozen_path),
              'shared_utility_sha256': I.digest(Path(__file__).with_name('local_repack.py')),
              'target': str(I.TARGET), 'retained_bit_cap': str(I.BIT_ROOT),
              'hypothesis': 'For both providers, each call loses exactly one native H1 child and the selected helper residual width decreases exactly one; all other local child counts, roles, geometry and arbitrary-dirty endpoint contracts remain unchanged.',
              'owner_construction': 'Retain every actual time/helper/owner/child/port assignment and compact chronological offsets using the new widths. Decreasing widths preserves every strict source interval, physical-family injection and capacity. Repeated selected-helper occurrences in one bin enlarge one terminal remainder by their full multiplicity.',
              'helpers_passing_target': sum(x['beats_target'] for x in cases),
              'helpers_strictly_improving_baseline': sum(x['strictly_beats_actual_baseline'] for x in cases),
              'cases_sorted_by_exact_price': cases,
              'limitations': ['This screen does not emit or prove any changed native local word.',
                              'A real candidate must supply its exact incoming frame, complete native child profile, arbitrary-helper restoration, both orientations and phase proof.',
                              'The existing physical stock and all-size/precision/tape premises are retained; no free helper state or denominator is introduced.']}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'target_pass', result['helpers_passing_target'],
          'baseline_improvement', result['helpers_strictly_improving_baseline'], flush=True)
    for item in cases[:8]:
        print('native_register', item['native_register'], 'width', item['old_width_by_provider'],
              'root', item.get('root', {}).get('decimal'), 'target', item['beats_target'], flush=True)


if __name__ == '__main__':
    main()
