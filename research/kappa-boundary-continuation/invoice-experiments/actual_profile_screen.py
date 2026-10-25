#!/usr/bin/env python3
"""Exact actual-owner prices for the five bare HPE release profiles.

Each profile is a stated native tariff hypothesis with a one-unit width
decrease. Native HPE completion is granted zero cost in this screen.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from pathlib import Path
import importlib.util
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DELTAS = {h: ({1: 3, 2: 1, 3: -2} if h in (484, 584, 556)
              else {1: 3, 2: -1, 3: 2, 4: -2})
          for h in (484, 584, 556, 508, 532)}


def main():
    path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    spec = importlib.util.spec_from_file_location('actual_hpe_invoice', path)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    census_path = HERE/'RETIMING-SCREEN.json'
    census = I.read(census_path)
    I.need(census['script_sha256'] == I.digest(HERE/'retiming_invoice.py'), 'owner-tail census source binding')
    cases = {}
    for item in census['cases_sorted_by_exact_price']:
        labels = set(item['borrowed_word_origin_by_provider'].values())
        I.need(len(labels) == 1, 'provider helper labels agree')
        cases[next(iter(labels))] = item
    old_price = I.moment(I.BASE, 73, 896*360, I.TARGET)
    rows = []
    for helper, local_delta in DELTAS.items():
        case = cases[helper]
        I.need(sum(r*n for r, n in local_delta.items()) == -1, 'one-unit actual local mass decrease')
        h = Counter(I.BASE)
        h.update({int(r): n for r, n in case['complete_profile_delta'].items()})
        h[1] += 3240  # Remove the earlier screen's hypothetical -H1.
        h.update({r: 3240*n for r, n in local_delta.items()})
        I.need(min(h.values()) >= 0 and sum(r*n for r, n in h.items()) == 65088*360, 'complete positive unchanged raw invoice')
        price = I.moment(h, 73, 896*360, I.TARGET)
        I.need(price[0] > old_price[1], 'bare candidate already strictly worsens the actual baseline')
        rows.append({'borrowed_helper': helper, 'native_register': case['native_register'],
                     'actual_local_profile_delta_hypothesis': local_delta,
                     'hosted_width_delta_per_call': -1, 'free_completion_granted': True,
                     'complete_profile': dict(sorted(h.items())),
                     'target_residual': I.interval(price[0]-1, price[1]-1),
                     'moment_excess_above_actual_baseline': I.interval(price[0]-old_price[1], price[1]-old_price[0]),
                     'root': I.root(h, 73, 896*360),
                     'strictly_worsens_actual_baseline': True})
    result = {'status': 'PASS_EXACT_REJECTION_OF_FIVE_BARE_HPE_TARIFFS',
              'script_sha256': I.digest(Path(__file__)),
              'owner_tail_census_sha256': I.digest(census_path),
              'frozen_invoice_script_sha256': I.digest(path),
              'target': str(I.TARGET), 'actual_baseline_lower': str(I.BASE_ROOT),
              'cases': rows,
              'scope': 'The stated local profiles and a width decrease of one on the identified helper are priced on every actual retained owner. HPE completion is optimistically free. All five profiles already worsen the complete baseline. This is a tariff rejection, not a native correctness proof or a universal obstruction to another entry-retiming profile.'}
    (HERE/'ACTUAL-PROFILE-SCREEN.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'])
    for item in rows:
        print('borrowed helper', item['borrowed_helper'], 'root', item['root']['decimal'])


if __name__ == '__main__':
    main()
