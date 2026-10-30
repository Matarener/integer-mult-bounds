#!/usr/bin/env python3
"""Exact complete-profile prices for physically motivated native rewrite goals.

Rank substitutions are tariff hypotheses until a native word proves them.
Apache-2.0. Substantial OpenAI Codex assistance under the user's direction.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
INV_PATH = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--profile', type=Path)
    ap.add_argument('--dimension', type=int, default=73)
    ap.add_argument('--productive', type=int, default=322560)
    ap.add_argument('--calls', type=int, default=3240)
    ap.add_argument('--out', type=Path, default=HERE/'BASELINE-REWRITE-PRICES.json')
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('adaptive_profile_prices', INV_PATH)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    frozen_path = INV_PATH.parent/'evidence/RESULT.json'
    frozen = I.read(frozen_path)
    I.need(frozen['script_sha256'] == I.digest(INV_PATH), 'retained exact interface')
    I.need(frozen['arithmetic_engine_sha256'] == I.digest(I.ENGINE_PATH), 'outward-rational arithmetic source')
    if args.profile:
        raw = I.read(args.profile)
        profile = Counter({int(r): int(n) for r, n in raw.items()})
        source = {'path': str(args.profile.resolve().relative_to(REPO)), 'sha256': I.digest(args.profile)}
    else:
        profile = Counter(I.BASE)
        I.need((args.dimension, args.productive, args.calls) == (73, 322560, 3240), 'default actual PR3734 dimensions')
        source = {'retained_invoice_receipt_sha256': I.digest(frozen_path)}
    m, W = args.dimension, args.productive
    I.need(all(0 < r < m and n >= 0 for r, n in profile.items()), 'positive proper-rank complete histogram')
    raw_mass = sum(r*n for r, n in profile.items())
    baseline_price = I.weighted(profile, m, I.TARGET)
    ceil = lambda q: -(-q.numerator//q.denominator)
    goals = {'two_H1_to_H2': (1, 1), 'H1_plus_H2_to_H3': (1, 2),
             'two_H2_to_H4': (2, 2), 'H1_plus_H3_to_H4': (1, 3),
             'two_H3_to_H6': (3, 3), 'two_H4_to_H8': (4, 4),
             'two_H8_to_H16': (8, 8)}
    rows = {}
    for label, (a, b) in goals.items():
        delta = Counter()
        delta[a] -= 1
        delta[b] -= 1
        delta[a+b] += 1
        c1, c2, c3 = I.cost(a, m, I.TARGET), I.cost(b, m, I.TARGET), I.cost(a+b, m, I.TARGET)
        saved = (c1[0]+c2[0]-c3[1], c1[1]+c2[1]-c3[0])
        I.need(saved[0] > 0, 'strict concave-power price benefit')
        if baseline_price[1] < W:
            required, threshold = 0, None
        else:
            threshold = ((baseline_price[0]-W)/saved[1], (baseline_price[1]-W)/saved[0])
            lo, hi = ceil(threshold[0]), ceil(threshold[1])
            I.need(lo == hi, 'exact integer crossing threshold')
            required = hi
        bit_base = I.weighted(profile, m, I.BIT_ROOT)
        b1, b2, b3 = (I.cost(r, m, I.BIT_ROOT) for r in (a, b, a+b))
        bit_saved = (b1[0]+b2[0]-b3[1], b1[1]+b2[1]-b3[0])
        if bit_base[1] < W:
            bit_required, bit_threshold = 0, None
        else:
            bit_threshold = ((bit_base[0]-W)/bit_saved[1], (bit_base[1]-W)/bit_saved[0])
            low_count, high_count = ceil(bit_threshold[0]), ceil(bit_threshold[1])
            I.need(low_count == high_count, 'exact BIT-cap integer crossing threshold')
            bit_required = high_count
        counts = sorted({1, args.calls, 2*args.calls, max(1, required), max(1, bit_required)})
        prices = []
        for count in counts:
            changed = Counter(profile)
            changed.update({r: count*n for r, n in delta.items()})
            if min(changed.values()) < 0:
                continue
            I.need(sum(r*n for r, n in changed.items()) == raw_mass, 'width-preserving raw mass')
            at_target = I.moment(changed, m, W, I.TARGET)
            at_bit = I.moment(changed, m, W, I.BIT_ROOT)
            prices.append({'total_occurrences': count, 'root': I.root(changed, m, W),
                           'target_residual': I.interval(at_target[0]-1, at_target[1]-1),
                           'strictly_passes_target': at_target[1] < 1,
                           'complex_price_passes_retained_bit_cap': at_bit[1] < 1})
        rows[label] = {'profile_delta_per_occurrence': dict(sorted(delta.items())),
                       'normalized_saving_per_occurrence_at_target': I.interval(*saved),
                       'minimum_total_occurrences_for_target': required,
                       'fractional_crossing_threshold': None if threshold is None else I.interval(*threshold),
                       'minimum_uniform_occurrences_per_call_for_target': ceil(F(required, args.calls)),
                       'minimum_total_occurrences_for_bit_cap': bit_required,
                       'bit_fractional_crossing_threshold': None if bit_threshold is None else I.interval(*bit_threshold),
                       'minimum_uniform_occurrences_per_call_for_bit_cap': ceil(F(bit_required, args.calls)),
                       'within_retained_outer_rank_guard': a+b <= I.C.max_idle_rank(m),
                       'prices': prices,
                       'native_status': 'Tariff hypothesis. A literal changed native word, unchanged ordered widths/owned stock and both provider contracts must be proved before a resulting root is a construction claim.'}
    result = {'status': 'PASS_EXACT_COMPLETE_PROFILE_REWRITE_PRICE_GOALS',
              'script_sha256': I.digest(Path(__file__)), 'source': source,
              'exact_engine_sha256': I.digest(I.ENGINE_PATH),
              'dimension': m, 'productive_fields': W, 'local_calls': args.calls,
              'complete_profile': dict(sorted(profile.items())),
              'complete_raw_mass': raw_mass, 'raw_deficit': m*W-raw_mass,
              'actual_profile_root': I.root(profile, m, W),
              'requested_target': str(I.TARGET), 'retained_bit_cap': str(I.BIT_ROOT),
              'rewrite_goals': rows,
              'outer_scope': 'PR3734 uses the retained modern near-lossless outer release, kappa=a-10^-46-10^-70, under its inherited premises. The older selected certificate uses a different balanced conversion. This arithmetic does not interchange those interfaces or prove either all-size hypothesis.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'])
    for label, row in rows.items():
        one = next((p for p in row['prices'] if p['total_occurrences'] == args.calls), None)
        print(label, 'minimum target occurrences', row['minimum_total_occurrences_for_target'],
              'one per call root', None if one is None else one['root']['decimal'][0],
              'minimum BIT occurrences', row['minimum_total_occurrences_for_bit_cap'])


if __name__ == '__main__':
    main()
