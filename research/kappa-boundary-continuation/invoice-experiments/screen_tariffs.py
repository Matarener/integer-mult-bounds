#!/usr/bin/env python3
"""Exact native-consumer price targets on source-bound complete invoices.

No hypothetical rank grouping is admitted as a native implementation. These
receipts identify the minimum useful construction and its remaining budget.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from collections import Counter
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def main():
    path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    s = importlib.util.spec_from_file_location('tariff_invoice', path)
    I = importlib.util.module_from_spec(s)
    s.loader.exec_module(I)
    receipt_path = path.parent/'evidence/RESULT.json'
    frozen = I.read(receipt_path)
    I.need(frozen['script_sha256'] == I.digest(path), 'frozen invoice script binding')
    I.need(frozen['arithmetic_engine_sha256'] == I.digest(I.ENGINE_PATH), 'exact arithmetic source binding')
    base = {r: F(n, 360) for r, n in I.BASE.items()}
    cases = {}
    changes = {
        'one_global_pair': {8: -F(2, 360), 16: F(1, 360)},
        'one_pair_per_replica': {8: -2, 16: 1},
        'two_pairs_per_replica': {8: -4, 16: 2},
        'one_triple_per_replica': {8: -3, 24: 1},
        'one_quadruple_per_replica': {8: -4, 32: 1},
        'one_sixfold_per_replica': {8: -6, 48: 1},
        'all_pairs_per_replica': {8: -72, 16: 36},
        'all_triples_per_replica': {8: -72, 24: 24},
        'two_equal_halves_per_replica': {8: -72, 36: 16},
        'all_nine_per_replica_outside_retained_rank_guard': {8: -72, 72: 8},
    }
    guard = I.C.max_idle_rank(73)
    I.need(guard == 51 and 2*guard*guard < 73*73 <= 2*(guard+1)*(guard+1), 'retained outer halving guard')
    for label, delta in changes.items():
        h = Counter(base)
        h.update(delta)
        I.need(sum(r*n for r, n in h.items()) == 65088, 'raw rank mass retained exactly')
        target = I.moment(h, 73, 896, I.TARGET)
        at_bit = I.moment(h, 73, 896, I.BIT_ROOT)
        got_root = I.root(h, 73, 896)
        extra = I.tariffs(h, 73, 896, I.TARGET)
        cases[label] = {
            'change_per_replica': {str(r): str(n) for r, n in delta.items()},
            'change_in_complete_T360_profile': {str(r): str(360*n) for r, n in delta.items()},
            'root': got_root, 'target_residual': I.interval(target[0]-1, target[1]-1),
            'bit_cap_residual': I.interval(at_bit[0]-1, at_bit[1]-1),
            'beats_actual_baseline': F(got_root['rational'][0]) > I.BASE_ROOT,
            'beats_target': target[1] < 1,
            'all_ranks_within_retained_outer_cap': all(r <= guard for r, n in h.items() if n),
            'additional_H1_allowance_at_target': extra['by_rank']['1'],
            'native_status': 'Price hypothesis only. A direct sum of independent H8 operations is not thereby a single native higher-rank operation. Actual geometry, owned field hosting, and complete scalar/phase charges must be supplied.',
        }
    sym = frozen['m73_literal_allocation']
    per_rep = {int(r): F(n, 360) for r, n in sym['complete_preconsumer_profile'].items()}
    actual = I.tariffs(per_rep, 73, 1024, I.TARGET)
    caps = {}
    for cap in (49, 50, 51):
        h = {r: 9*n for r, n in I.LOCAL.items() if r != 8}
        h[1] += 256
        h[cap] = F(28482, cap)
        I.need(sum(r*n for r, n in h.items()) == 74368, 'unchanged symmetric raw profile')
        price = I.tariffs(h, 73, 1024, I.TARGET)
        eight = I.test_added(h, 73, 1024, {8: 8})
        I.need(not eight['passes_price'], 'eight H8 rejected even at widened idle cap')
        caps[str(cap)] = {'fractional_idle_rank': cap, 'tariffs': price, 'eight_H8': eight}
    result = {
        'status': 'PASS_EXACT_BOUNDARY_CONSUMER_PRICE_TARGETS',
        'script_sha256': I.digest(Path(__file__)),
        'frozen_invoice_receipt_sha256': I.digest(receipt_path),
        'target': str(I.TARGET), 'actual_baseline': str(I.BASE_ROOT), 'retained_bit_cap': str(I.BIT_ROOT),
        'original_896_contract': cases,
        'symmetric_m73': {
            'actual_retained_allocation_H8_allowance': actual['by_rank']['8'],
            'relaxed_idle_caps': caps,
            'all_T_scope': 'With the same per-call profile,256 H1 boundary charge,1024 productive fields per replica, and28482 units of paid idle mass, every T and every repacking with idle ranks at most51 has moment at least the rank51 relaxation. That relaxation cannot pay8 H8. Moving endpoints changes this conclusion only if it changes one of those charged quantities or the admitted guard.',
        },
        'replication_identity': 'Repeating an entire admissible T360 allocation k times scales both its complete child histogram and productive denominator by k, so its moment and root are exactly unchanged. Better packing requires an actual different allocation or clock.',
        'retained_outer_guard': {'dimension': 73, 'maximum_rank': guard, 'H72_eligible_under_this_guard': False,
            'scope': 'This is the retained outer halving guard, not a theorem that every possible recursion must impose rank<=51.'},
        'limitations': ['No hypothetical grouped tariff is a emitted native transform.',
                        'These screens do not change the selected result or discharge inherited all-size, precision/tape, or outer analytic premises.'],
    }
    (HERE/'TARIFF-SCREEN.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'])
    for key in ('one_global_pair', 'one_pair_per_replica', 'two_pairs_per_replica', 'one_triple_per_replica'):
        print(key, cases[key]['root']['decimal'], 'target', cases[key]['beats_target'])
    print('symmetric best rank51 H8 allowance', caps['51']['tariffs']['by_rank']['8']['decimal'][0])


if __name__ == '__main__':
    main()
