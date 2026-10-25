#!/usr/bin/env python3
"""Exact remaining budget after the realized receiver-sharing native rewrite.

The additional fusions and the width-seven staging signature below are tariff
hypotheses. They are not native constructions or new admitted bounds.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE/'CURRENT-REMAINING-BUDGET.json')
    args = parser.parse_args()
    path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    spec = importlib.util.spec_from_file_location('remaining_budget_invoice', path)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    old = I.read(path.parent/'evidence/RESULT.json')
    I.need(old['script_sha256'] == I.digest(path) and old['arithmetic_engine_sha256'] == I.digest(I.ENGINE_PATH), 'retained exact arithmetic pins')
    current_path = HERE/'receiver-sharing/RESULT.json'
    current = I.read(current_path)
    I.need(current['status'] == 'PASS_LITERAL_CHANGED_NATIVE_OWNERS_AND_TWO_ENGINE_INVOICE', 'actual current invoice gate')
    I.need(current['script_sha256'] == I.digest(HERE/'native_owner_invoice.py'), 'actual invoice implementation')
    for paths in current['supplied_native_inputs'].values():
        for rel, expected in paths.items():
            I.need(I.digest(REPO/rel) == expected, 'current native source: '+rel)
    I.need((current['replicas'], current['calls'], current['productive_families']) == (360, 3240, 322560), 'actual current global geometry')
    profile = Counter({int(r): n for r, n in current['profile'].items()})
    lower, upper = map(F, current['root']['rational'])
    fee = F(1, 10**46)+F(1, 10**70)
    I.need(F(current['conditional_kappa']) == lower-fee, 'retained modern outer loss')
    delta = {1: -1, 2: -1, 3: 1}
    ceil = lambda q: -(-q.numerator//q.denominator)
    endpoints = {'retained_bit_cap': I.BIT_ROOT, 'bit_cap_plus_current_outer_loss': I.BIT_ROOT+fee}
    thresholds = {}
    for label, endpoint in endpoints.items():
        before = I.weighted(profile, 73, endpoint)
        signed = I.weighted(delta, 73, endpoint)
        saving = (-signed[1], -signed[0])
        I.need(saving[0] > 0, 'strict positive fusion saving')
        crossing = ((before[0]-322560)/saving[1], (before[1]-322560)/saving[0])
        required = ceil(crossing[1])
        I.need(ceil(crossing[0]) == required == 53876, 'exact additional occurrence threshold')
        tests = []
        for count in (required-1, required, 16*3240, 17*3240):
            changed = Counter(profile)
            changed.update({r: count*n for r, n in delta.items()})
            I.need(all(n >= 0 for n in changed.values()), 'available rank multiplicities at tariff level')
            I.need(sum(r*n for r, n in changed.items()) == current['raw_rank_mass'], 'same complete raw rank mass')
            value = I.weighted(changed, 73, endpoint)
            passes = value[1] < 322560
            fails = value[0] > 322560
            I.need(passes != fails, 'strict outward-rational sign')
            I.need(passes == (count >= required), 'sharp integer threshold sign')
            tests.append({'additional_total_occurrences': count,
                          'additional_occurrences_per_call': str(F(count, 3240)),
                          'complete_invoice_minus_productive': I.interval(value[0]-322560, value[1]-322560),
                          'strictly_passes_endpoint': passes})
        thresholds[label] = {
            'endpoint': str(endpoint),
            'fractional_additional_threshold': I.interval(*crossing),
            'minimum_additional_total_occurrences': required,
            'minimum_additional_uniform_occurrences_per_call': ceil(F(required, 3240)),
            'total_uniform_occurrences_per_call_including_realized_one': 1+ceil(F(required, 3240)),
            'sharp_tests': tests}
    # A changed-inventory signature is a necessary gate only. It includes the
    # measured local rank redistribution; a free width deletion is not used.
    proposed_local = Counter({int(r): n for r, n in current['provider_local_profiles']['gauge44'].items()})
    proposed_local.update({1: 3, 2: 1, 3: -2})
    proposed_widths = {4: 26, 5: 2, 6: 18, 7: 54, 8: 95, 9: 213}
    work = HERE/'remaining-budget'
    work.mkdir(exist_ok=True)
    local_path, widths_path = work/'HYPOTHETICAL-LOCAL.json', work/'HYPOTHETICAL-WIDTHS.json'
    local_path.write_text(json.dumps(dict(sorted(proposed_local.items())), indent=2)+'\n')
    widths_path.write_text(json.dumps(proposed_widths, indent=2)+'\n')
    width_receipt = work/'CURRENT-WIDTH-SIGNATURE-SCREEN.json'
    command = [sys.executable, '-B', str(HERE/'current_inventory_screen.py'),
               '--local-profile', str(local_path), '--width-inventory', str(widths_path), '--out', str(width_receipt)]
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         env=dict(os.environ, PYTHONOPTIMIZE='', PYTHONDONTWRITEBYTECODE='1'))
    I.need(run.returncode == 0, 'current changed-inventory necessary gate: '+run.stdout)
    width = I.read(width_receipt)
    I.need(width['status'] == 'NOT_EXCLUDED_BY_COMPLETE_INVENTORY_DUAL' and width['dual_feasible'], 'hypothetical complete width signature remains a live price lead')
    unit = I.cost(1, 73, upper)
    pi = {int(w): F(value) for w, value in width['width_dual'].items()}
    width_tax = pi[7]-pi[8]
    local_cost = I.weighted({1: 3, 2: 1, 3: -2}, 73, upper)
    I.need(width_tax > 0 and local_cost[1] < 0, 'positive width tariff and local saving')
    result = {
        'status': 'PASS_EXACT_CURRENT_REMAINING_TARIFF_BUDGET',
        'script_sha256': I.digest(Path(__file__)),
        'invoice_sha256': I.digest(current_path),
        'arithmetic_engine_sha256': I.digest(I.ENGINE_PATH),
        'current_complex_root': current['root']['rational'],
        'current_conditional_kappa': current['conditional_kappa'],
        'retained_bit_cap': str(I.BIT_ROOT),
        'bit_cap_minus_current_complex_root': I.interval(I.BIT_ROOT-upper, I.BIT_ROOT-lower),
        'bit_cap_minus_current_conditional_kappa': str(I.BIT_ROOT-lower+fee),
        'bit_gap_decimal': I.decimal(I.BIT_ROOT-lower+fee),
        'additional_fusion_delta': delta,
        'thresholds': thresholds,
        'fusion_scope': 'Only one H1+H2 to H3 fusion per local call has been realized. The additional counts assume disjoint literal width-preserving fusions with no added rank-zero, workspace, or outer cost. No such 17-additional-per-call word is asserted. Crossing this arithmetic threshold makes the retained BIT side constraint the next binding limitation; it does not establish an admissible value above that constraint.',
        'current_width_signature': {
            'native_realization_claimed': False,
            'complete_local_delta_per_call': {1: 3, 2: 1, 3: -2},
            'width_change_per_call': {'8': -1, '7': 1},
            'receipt': width_receipt.relative_to(REPO).as_posix(),
            'receipt_sha256': I.digest(width_receipt),
            'screen_implementation_sha256': I.digest(HERE/'current_inventory_screen.py'),
            'status': width['status'],
            'patterns_checked': width['patterns_checked'],
            'complete_invoice_lower_bound_decimal': width['lower_bound_decimal'],
            'dual_width_tariff_in_H1_units': I.interval(width_tax/unit[1], width_tax/unit[0]),
            'local_saving_in_H1_units': I.interval(-local_cost[1]/unit[1], -local_cost[0]/unit[0]),
            'scope': 'A proposed width 8 to 7 staging with its complete local rank redistribution is not excluded at the actual current upper endpoint. This is a dual necessary gate, with no native HPE repair, physical fill, improved kappa, or outer admission inferred.'}}
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'additional total', 53876, 'uniform per call', 17)
    print('BIT gap', result['bit_gap_decimal'])
    print('width signature', width['status'], width['lower_bound_decimal'])


if __name__ == '__main__':
    main()
