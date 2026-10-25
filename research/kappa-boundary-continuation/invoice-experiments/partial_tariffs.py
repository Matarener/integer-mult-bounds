#!/usr/bin/env python3
"""Independent exact price screen for the stated partial uniform-chart census.

This prices its explicit gap children and fractionally relaxes the remaining
idle bill. It supplies neither a mixed native trace nor a residual consumer.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def main():
    inv_path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    spec = importlib.util.spec_from_file_location('partial_exact_invoice', inv_path)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    frozen_path = inv_path.parent/'evidence/RESULT.json'
    frozen = I.read(frozen_path)
    I.need(frozen['script_sha256'] == I.digest(inv_path), 'frozen arithmetic interface')
    I.need(frozen['arithmetic_engine_sha256'] == I.digest(I.ENGINE_PATH), 'outward-rational engine pin')
    nb = HERE.parent/'native-boundary'
    census_path = nb/'evidence/PARTIAL-GEOMETRY-CENSUS.json'
    census = I.read(census_path)
    template_path = REPO/'research/kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return/inputs/TEMPLATE.json.gz'
    source_key = 'artifact/live-source/research/staged544-producer-return/inputs/TEMPLATE.json.gz'
    I.need(I.digest(template_path) == frozen['m73_literal_allocation']['input_sha256'][source_key], 'actual source clock')
    template = I.read(template_path)
    intervals = [(e['from_level'], e['to_level']) for e in template['execution_schedule']
                 if e['kind'] == 'idle_cover_sweep']
    I.need(intervals == [tuple(v) for v in census['interval_clock']], 'independent actual idle clock')
    local = {r: 9*n for r, n in I.LOCAL.items() if r != 8}
    I.need(sum(r*n for r, n in local.items()) == 45630, 'local child charge with all72 repair children removed')
    rows = []
    for mask, src in enumerate(census['patterns']):
        selected = {j for j in range(1, 9) if mask >> (j-1) & 1}
        I.need(sorted(selected) == src['common_stages'], 'complete bitmask census order')
        dims = [9]
        for j in range(1, 9):
            dims.append(dims[-1]+8+(j in selected))
        normal = [j if j in selected else 0 for j in range(9)]
        m, z, W = dims[-1], 16, 1024
        old, zero, gaps = Counter(), Counter(), Counter()
        for start, end in intervals:
            before = 0 if start == -1 else dims[start]
            base = dims[end]-before
            zero[base] += 2
            if start == -1:
                old[base-1] += 2
            else:
                old[base] += 1
                destination_normal = 0 if end == 8 else normal[end]
                closure = 2 if destination_normal == 0 and normal[start] != 0 else 0
                old[base+closure] += 1
        old.pop(0, None)
        zero.pop(0, None)
        for j in range(1, 9):
            if j in selected:
                gaps[1] += 224
            else:
                gaps[1] += 2*z
                if j-1 in selected:
                    gaps[2] += 112
        I.need(dict(sorted(old.items())) == {int(r): n for r, n in src['old_idle_histogram'].items()}, 'independent old idle histogram')
        I.need(dict(sorted(zero.items())) == {int(r): n for r, n in src['zero_idle_histogram'].items()}, 'independent zero idle histogram')
        I.need(dict(sorted(gaps.items())) == {int(r): n for r, n in src['gap_native_histogram'].items()}, 'literal common and return child tariffs')
        idle_mass = 112*sum(r*n for r, n in old.items())+z*sum(r*n for r, n in zero.items())-9*(3278-18*z)
        raw = sum(r*n for r, n in local.items())+sum(r*n for r, n in gaps.items())+idle_mass
        I.need(raw == src['complete_preconsumer_rank_mass'], 'complete raw preconsumer bill')
        I.need(m*W-raw == src['raw_deficit'], 'productive normalizer')
        geometry_cap = max(max(old), max(zero))
        guard = I.C.max_idle_rank(m)
        I.need(geometry_cap <= guard, 'every stated idle rank meets retained outer guard')
        h = Counter(local)
        h.update(gaps)
        h[geometry_cap] += F(idle_mass, geometry_cap)
        I.need(sum(r*n for r, n in h.items()) == raw, 'fractional relaxation conserves every paid rank unit')
        residual = I.moment(h, m, W, I.TARGET)
        price = I.tariffs(h, m, W, I.TARGET)
        item = {'common_stages': sorted(selected), 'dimension': m,
                'raw_deficit': m*W-raw, 'literal_gap_profile': dict(sorted(gaps.items())),
                'paid_idle_mass': idle_mass, 'maximum_genuine_idle_rank': geometry_cap,
                'retained_outer_guard': guard,
                'optimistic_complete_profile': {str(r): str(n) for r, n in sorted(h.items())},
                'target_residual_without_consumer': I.interval(residual[0]-1, residual[1]-1),
                'free_consumer_passes_target_screen': residual[1] < 1,
                'additional_H8_allowance': price['by_rank']['8'],
                'additional_H1_allowance': price['by_rank']['1'],
                'eight_H8': I.test_added(h, m, W, {8: 8}),
                'proven_query_child_deletions': src['proven_query_child_deletions']}
        rows.append(item)
    I.need(len(rows) == 256, 'all partial chart patterns')
    ranking = sorted(rows, key=lambda r: F(r['additional_H8_allowance']['rational'][0]), reverse=True)
    result = {'status': 'PASS_EXACT_PARTIAL_UNIFORM_CHART_PRICE_SCREEN',
              'script_sha256': I.digest(Path(__file__)),
              'source_census_sha256': I.digest(census_path),
              'source_census_script_sha256': I.digest(nb/'partial_geometry.py'),
              'source_template_sha256': I.digest(template_path),
              'frozen_invoice_receipt_sha256': I.digest(frozen_path),
              'target': str(I.TARGET), 'retained_bit_cap': str(I.BIT_ROOT),
              'patterns': rows,
              'best_by_additional_H8_allowance': [r['common_stages'] for r in ranking[:12]],
              'free_consumer_target_pass_count': sum(r['free_consumer_passes_target_screen'] for r in rows),
              'eight_H8_target_pass_count': sum(r['eight_H8']['passes_price'] for r in rows),
              'bound_direction': 'The explicit common stages cost224 H1; common-to-fixed returns cost112 H2. All remaining paid idle rank mass is fractionally placed at the largest actual idle rank. For a>0, r^(1-a)/r decreases with r, so every physical packing has a bill at least this large.',
              'scope': 'Conditional on the stated partial chart endpoint formulas. Only its all-fixed73 and all-uniform81 endpoint traces are independently available. No mixed helper allocation, query-child deletion, native residual inverse, or new kappa is certified.'}
    (HERE/'PARTIAL-TARIFFS.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'free-consumer target passes', result['free_consumer_target_pass_count'],
          'eight-H8 target passes', result['eight_H8_target_pass_count'])
    for row in ranking[:6]:
        print(row['common_stages'], 'm', row['dimension'], 'raw deficit', row['raw_deficit'],
              'H8 allowance', row['additional_H8_allowance']['decimal'][0])


if __name__ == '__main__':
    main()
