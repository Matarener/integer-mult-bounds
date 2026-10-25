#!/usr/bin/env python3
"""Exact actual-owner screen for joint one-unit helper entry retimings.

Input cases list helpers by borrowed-word origin and the actual common local
profile. Shared donor climbs are already reflected in that supplied profile;
shared physical owner bins are independently combined here before pricing.
Native residual completion is granted zero cost. Apache-2.0; substantial
OpenAI Codex assistance under the user's direction.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json
import numpy as np
from local_repack import read, rank, module, REPO


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--followup', type=Path, required=True)
    ap.add_argument('--cases', type=Path)
    ap.add_argument('--out', type=Path, default=Path(__file__).with_name('JOINT-PROFILE-SCREEN.json'))
    args = ap.parse_args()
    inv_path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    I = module(inv_path, 'joint_profile_invoice')
    frozen_path = inv_path.parent/'evidence/RESULT.json'
    frozen = I.read(frozen_path)
    I.need(frozen['script_sha256'] == I.digest(inv_path), 'frozen invoice source')
    I.need(frozen['arithmetic_engine_sha256'] == I.digest(I.ENGINE_PATH), 'directed arithmetic source')
    for rel, expected in frozen['m73_literal_allocation']['input_sha256'].items():
        I.need(I.digest(args.followup/rel) == expected, 'actual retained source: '+rel)
    data = args.followup/'artifact/live-source/research/staged544-producer-return/inputs'
    order = read(data/'ORDER.json')
    dispatch = {(s, r): p for s, r, p in read(data/'DISPATCH.json')}
    wprovider, origins = {}, {}
    for tag, p in (('base', 'gauge44'), ('extra', 'extra')):
        word = read(data/f'NATIVE-{tag}.json.gz')
        origins[p] = word['helper_origin']
        wprovider[p] = [rank(word['frames'][word['final'][r]])-rank(word['frames'][word['start'][r]]) for r in range(224, 632)]
    I.need(origins['gauge44'] == origins['extra'], 'same actual helper origins')
    widths = np.array([wprovider[dispatch[tuple(c)]] for c in order], dtype=np.int8).reshape(-1)
    rows = np.array(read(data/'FILL.json.gz')['rows'], dtype=np.int32)
    binids = (rows[:, 2]*18+rows[:, 3])*112+rows[:, 4]
    template = read(data/'TEMPLATE.json.gz')
    caps = {c['child']: c['rank'] for c in template['idle_children']}
    cap = np.tile(np.repeat([caps[c] for c in range(18)], 112), 360)
    rem = cap-np.bincount(binids, weights=widths, minlength=len(cap)).astype(np.int32)
    I.need(min(rem) >= 0, 'exact original capacities')
    old_idle = Counter(map(int, rem[rem > 0]))
    check = Counter({r: 3240*n for r, n in I.LOCAL.items()})
    check.update(old_idle)
    I.need(check == I.BASE, 'complete original source invoice')
    if args.cases:
        inputs = read(args.cases)
        cases = inputs.get('cases', inputs.get('candidates')) if isinstance(inputs, dict) else inputs
        I.need(isinstance(cases, list), 'literal joint case list')
        source = {'path': str(args.cases), 'sha256': I.digest(args.cases)}
    else:
        folder = Path(__file__).resolve().parents[1]/'coupled-boundary/combined484584'
        files = [folder/f'COMBINED-{p}.json.gz' for p in ('base', 'extra')]
        words = [read(p) for p in files]
        I.need(words[0]['report']['local_profile'] == words[1]['report']['local_profile'], 'both supplied combined profiles agree')
        cases = [{'helpers': [484, 584], 'local_profile': words[0]['report']['local_profile']}]
        source = {str(p.relative_to(REPO)): I.digest(p) for p in files}
    baseline_price = I.moment(I.BASE, 73, 896*360, I.TARGET)
    output = []
    for case in cases:
        helpers = sorted(case['helpers'])
        I.need(len(helpers) == len(set(helpers)), 'distinct joint helper identities')
        indices = [origins['gauge44'].index(h) for h in helpers]
        I.need(all(wprovider[p][h] > 1 for p in wprovider for h in indices), 'positive residual width after shrink')
        new_local = {int(r): n for r, n in case['local_profile'].items()}
        I.need(all(r > 0 and type(n) is int and n >= 0 for r, n in new_local.items()), 'nonnegative local child counts')
        if 'native_helpers' in case:
            I.need(sorted(case['native_helpers']) == sorted(224+i for i in indices), 'actual native helper numbering')
        if 'width_decrements' in case:
            I.need({int(r): n for r, n in case['width_decrements'].items()} == {224+i: 1 for i in indices}, 'actual joint width decrements')
        I.need(sum(r*n for r, n in new_local.items()) == 5134-len(helpers), 'actual combined local rank mass')
        bids, multiplicities = np.unique(np.concatenate([binids[h::408] for h in indices]), return_counts=True)
        delta, stock = Counter(), Counter()
        for b0, k0 in zip(bids, multiplicities):
            b, k = int(b0), int(k0)
            old, new = int(rem[b]), int(rem[b])+k
            I.need(new <= cap[b], 'joint positive width shrink preserves capacity')
            if old:
                delta[old] -= 1
            delta[new] += 1
            stock[old, k] += 1
        h = Counter({r: 3240*n for r, n in new_local.items()})
        h.update(old_idle)
        h.update(delta)
        h = +h
        I.need(sum(r*n for r, n in h.items()) == 65088*360, 'full unchanged raw bill with all shared-owner multiplicities')
        price = I.moment(h, 73, 896*360, I.TARGET)
        item = {'helpers': helpers, 'native_registers': [224+i for i in indices],
                'actual_local_profile_hypothesis': new_local,
                'old_remainder_and_joint_multiplicity': [[r, k, n] for (r, k), n in sorted(stock.items())],
                'complete_profile': dict(sorted(h.items())),
                'target_residual': I.interval(price[0]-1, price[1]-1),
                'moment_difference_from_actual_baseline': I.interval(price[0]-baseline_price[1], price[1]-baseline_price[0]),
                'strictly_improves_actual_baseline': price[1] < baseline_price[0],
                'strictly_worsens_actual_baseline': price[0] > baseline_price[1],
                'strictly_passes_target': price[1] < 1, 'root': I.root(h, 73, 896*360)}
        if 'providers' in case:
            item['supplied_provider_word_references'] = case['providers']
        output.append(item)
    result = {'status': 'PASS_EXACT_JOINT_RETIMING_OWNER_TAIL_PRICE_SCREEN',
              'script_sha256': I.digest(Path(__file__)),
              'shared_utility_sha256': I.digest(Path(__file__).with_name('local_repack.py')),
              'supplied_profile_source': source, 'frozen_invoice_receipt_sha256': I.digest(frozen_path),
              'cases': output, 'baseline_improvement_count': sum(c['strictly_improves_actual_baseline'] for c in output),
              'strict_baseline_worsening_count': sum(c['strictly_worsens_actual_baseline'] for c in output),
              'target_pass_count': sum(c['strictly_passes_target'] for c in output),
              'scope': 'Conditional supplied common native profiles; each identified helper width decreases one in both providers. Every shared owner-bin multiplicity is independently combined from the pinned physical fill. All HPE/native residual completion is optimistically free. Passing arithmetic alone would not prove a changed native word or a new kappa.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'cases', len(output), 'actual gains', result['baseline_improvement_count'], 'target passes', result['target_pass_count'])
    for item in output:
        print(item['helpers'], item['root']['decimal'][0], 'gain', item['strictly_improves_actual_baseline'])


if __name__ == '__main__':
    main()
