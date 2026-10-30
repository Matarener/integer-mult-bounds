#!/usr/bin/env python3
"""Bind the exact all-character operator proof to the actual composed T360 fill.

Independent global chronology/phase check; source-bound local native receipts
are reused rather than rerun. The old template's numerical stock, old local
programs, T37 plan order and old profile are not used as the T360 supplier.
Apache-2.0; substantial OpenAI assistance; predecessor attribution in README.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import full_operator as F

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
OWNER = SCOPE / 'sources/PR3945/research/staged544-terminal-gap-fill/owner'
PROVIDERS = SCOPE / 'composed-supplier'


def blocks(template):
    result, current = {}, None
    for event in template['execution_schedule']:
        if event['kind'] in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if event['kind'] == 'local_cover_sweep':
            current = event['stage']
            F.require(current not in result, 'unique local stage')
            result[current] = []
        F.require(current is not None, 'all data events follow a stage')
        result[current].append(event)
    F.require(sorted(result) == list(range(9)), 'nine exact stage blocks')
    return result


def touches(event, local):
    kind = event['kind']
    if kind == 'local_cover_sweep':
        p = local[event['stage']]
        return 2 * p, 2 * p + 1
    if kind == 'bridge':
        return tuple(2 * p + s for p in (event['src'], event['dst']) for s in (0, 1))
    if kind == 'terminal':
        return tuple(range(8))
    F.require(kind in ('idle_cover_sweep', 'terminal_Y_translations'), 'unknown observer kind')
    return ()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=HERE / 'T360-OPERATOR-ADMISSION.json')
    args = ap.parse_args()
    F.authenticate()
    paths = [OWNER / 'inputs' / name for name in ('TEMPLATE.json.gz', 'PLAN.json.gz', 'ORDER.json', 'DISPATCH.json')]
    paths += [OWNER / 'FILL.json.gz', F.PHASES, F.TEMPLATE, Path(F.__file__), Path(__file__)]
    template, plan, order, dispatch_rows = [F.read(p) for p in paths[:4]]
    fill = F.read(OWNER / 'FILL.json.gz')
    phases = F.read(F.PHASES)
    F.require(template['exact_data_phase_recipe_sha256'] == F.sha(F.PHASES), 'actual template exact phase recipe')
    normals = [F.normalize(template, recipe) for recipe in phases['recipes']]
    old = F.normalize(F.read(F.TEMPLATE), phases['recipes'][0])
    F.require(all(n['events'] == old['events'] for n in normals), 'actual normalized graph equals proved baseline')
    F.require(order and len(order) == 3240, 'actual T360 order length')
    stage_time = {tuple(sr): time for time, sr in enumerate(order)}
    F.require(set(stage_time) == {(stage, owner) for stage in range(9) for owner in range(360)}, 'all actual calls exactly once')
    F.require(all(stage_time[s, r] < stage_time[s + 1, r] for s in range(8) for r in range(360)), 'each owner stage chronology')
    dispatch = {(s, r): tag for s, r, tag in dispatch_rows}
    F.require(len(dispatch_rows) == len(dispatch) == 3240 and set(dispatch) == set(stage_time), 'complete literal dispatch')
    F.require(set(dispatch.values()) == {'gauge44', 'extra'}, 'actual source provider tags')
    substitution = {'gauge44': 'base', 'extra': 'extra'}
    dispatch = {key: substitution[tag] for key, tag in dispatch.items()}
    F.require(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'fill columns')
    F.require(fill['dispatch_overrides'] == [], 'no unprocessed dispatch override')

    widths, provider_pins, native_sources = {}, {}, []
    for tag in ('base', 'extra'):
        root = PROVIDERS / ('native-' + tag)
        candidate = PROVIDERS / 'candidate' / ('BORROW-WORD-43' + tag + '.json.gz')
        input_path, word_path, receipt_path = root / 'INPUT.json.gz', root / 'native/local/CANONICAL-WORD.json.gz', root / 'RESULT.json'
        candidate_data, input_data, word, receipt = map(F.read, (candidate, input_path, word_path, receipt_path))
        F.require(candidate_data == input_data, 'native input is exact composed candidate')
        F.require(receipt['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY', 'completed inherited provider replay')
        F.require(all(s['exit_code'] == 0 for s in receipt['steps']) and len(receipt['steps']) == 5, 'all five native stages')
        F.require(receipt['word_sha256'] == F.sha(input_path), 'native receipt input binding')
        for name, digest in receipt['source_sha256'].items():
            source = root / 'source' / name
            F.require(F.sha(source) == digest, 'native source receipt binding')
            native_sources.append(source)
        F.require(word['R'] == 408 and word['h'] == 9 and word['v'] == 112, 'actual canonical dimensions')
        F.require(word['ports'] == [int(r['q']) for r in phases['recipes']], 'ordered source/target ports')
        frames = word['frames']
        widths[tag] = [len(frames[word['final'][224 + helper]]) - len(frames[word['start'][224 + helper]])
                       for helper in range(408)]
        F.require(all(1 <= width <= 9 for width in widths[tag]), 'positive residual widths')
        adapter_path = root / 'native/local/RESIDUAL-ADAPTERS.json'
        adapters = F.read(adapter_path)['recipes']
        for helper, width in enumerate(widths[tag]):
            key = str(word['start'][224 + helper]) + ':' + str(word['final'][224 + helper])
            if key in adapters:
                F.require(adapters[key]['rank'] == width, 'exact native boundary recipe width')
            else:
                # The inherited emitter uses its ordinary nested completion
                # recipe for full terminal frame1; the separate residual
                # adapter table contains the partial-terminal cases only.
                F.require(word['final'][224 + helper] == 1 and frames[1] == [256,128,64,32,16,8,4,2,1],
                          'only standard full-frame completion may omit an extra residual adapter')
        paths += [candidate, input_path, word_path, receipt_path, adapter_path]
        provider_pins[tag] = {'candidate_sha256': F.sha(candidate), 'canonical_native_sha256': F.sha(word_path),
                              'native_receipt_sha256': F.sha(receipt_path),
                              'actual_width_inventory': dict(sorted(Counter(widths[tag]).items()))}
    paths += native_sources

    stage_blocks = blocks(template)
    local = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    windows = {}
    for owner in range(360):
        last = [(-1, -1)] * 8
        for stage in range(9):
            time = stage_time[stage, owner]
            for index, event in enumerate(stage_blocks[stage]):
                if event['kind'] == 'idle_cover_sweep':
                    for side, child in enumerate(event['child_indices']):
                        stream = 2 * event['pair'] + side
                        if str(child) in plan['pairs']:
                            F.require(stream == 2 * plan['pairs'][str(child)] + plan['sides'][str(child)], 'plan stream routing')
                        else:
                            F.require(all(r['idle_children'][child]['rank'] == 0 for r in phases['recipes']), 'unused zero slot')
                        windows[owner, child] = last[stream], (time, index), stream
                for stream in touches(event, local):
                    last[stream] = time, index

    seen = bytearray(3240 * 408)
    occupied = defaultdict(int)
    width_mass = 0
    for row in fill['rows']:
        time, helper, owner, child, port, offset = row
        F.require(all(type(x) is int for x in row), 'integer hosting row')
        F.require(0 <= time < 3240 and 0 <= helper < 408 and 0 <= owner < 360 and 0 <= port < 112, 'host row dimensions')
        index = 408 * time + helper
        F.require(seen[index] == 0, 'one owner per literal helper occurrence')
        seen[index] = 1
        start, end, stream = windows[owner, child]
        F.require(start < (time, -1) < end, 'host phase crosses a physical stream observation')
        width = widths[dispatch[tuple(order[time])]][helper]
        axes = phases['recipes'][port]['idle_children'][child]['orthogonal_axes']
        F.require(0 <= offset and offset + width <= len(axes), 'literal native width fits original child axes')
        mask = ((1 << width) - 1) << offset
        key = owner, child, port
        F.require(occupied[key] & mask == 0, 'disjoint actual hosted cells')
        occupied[key] |= mask
        width_mass += width
    F.require(len(fill['rows']) == len(seen) == 1321920 and all(seen), 'every actual helper occurrence checked')
    residual = Counter()
    residual_mass = 0
    for owner in range(360):
        for port, recipe in enumerate(phases['recipes']):
            for child, record in enumerate(recipe['idle_children']):
                rank = len(record['orthogonal_axes']) - occupied[owner, child, port].bit_count()
                F.require(rank >= 0, 'nonnegative residual')
                if rank:
                    residual[rank] += 1
                    residual_mass += rank
    total_mass = sum(len(c['orthogonal_axes']) for r in phases['recipes'] for c in r['idle_children']) * 360
    F.require(width_mass + residual_mass == total_mass, 'every original axis assigned exactly once')
    invoice_path = PROVIDERS / 'invoice/RESULT.json'
    invoice = F.read(invoice_path)
    F.require(invoice['status'] == 'PASS_FRESH_NATIVE_LITERAL_OWNERS_AND_THREE_ENGINE_COMPLEX_INVOICE',
              'current complete native owner invoice')
    F.require(invoice['helper_rows'] == len(fill['rows']) and invoice['calls'] == len(order), 'same literal invoice dimensions')
    F.require(invoice['idle_profile'] == {str(k): v for k, v in sorted(residual.items())}, 'independent residual profile agrees with invoice')
    for path, digest in invoice['source_pins'].items():
        F.require(F.sha(F.REPO / path) == digest, 'invoice source binding')
        paths.append(F.REPO / path)
    paths.append(invoice_path)
    result = {
        'status': 'PASS_ACTUAL_T360_ALL_CHARACTER_OPERATOR_ADMISSION',
        'actual_calls': 3240, 'actual_hosted_rows': len(fill['rows']), 'owner_child_windows': len(windows),
        'actual_provider_bindings': provider_pins,
        'explicit_source_dispatch_substitution': substitution,
        'original_axis_mass': total_mass, 'hosted_width_mass': width_mass, 'residual_rank_mass': residual_mass,
        'actual_residual_profile': dict(sorted(residual.items())),
        'symbolic_ports': len(normals), 'exact_phase_identities': sum(n['phase_identities'] for n in normals),
        'normalized_graph_equals_historical_proved_graph': True,
        'all_Fourier_characters': True, 'all_positive_tensor_multiplicities': True,
        'operator_argument': 'Each actual helper residual is placed on distinct original child axes within its observer-free physical stream interval. Move it to that child endpoint by commutation, combine with the literal complementary residual, and obtain the original full child exactly. The current provider widths and every literal hosting row are checked. The exact Z4 gauge proof then gives C_all on all eight streams, with global phase and arbitrary correlated dirty inputs retained.',
        'no_axis_transfer_overlay': True,
        'complete_owner_invoice_sha256': F.sha(invoice_path),
        'independent_residual_profile_matches_complete_invoice': True,
        'retained_interfaces': ['Native provider endpoint/canonicalization correctness as source-bound by the five-stage receipts', 'the owner adapter realizes the declared orthonormal axis-cell embedding in the common cover', 'common-cover conjugation and final all-live translation identity', 'uniform tape/precision/recurrence interfaces; this is not a full multiplication theorem'],
        'old_template_metadata_not_reused': ['T37 stock, old local programs, bank padding, old replica count and numerical profile'],
        'input_files': {str(p.relative_to(F.REPO)): F.sha(p) for p in sorted(set(paths))},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'], len(fill['rows']), 'rows', len(normals), 'symbolic ports')


if __name__ == '__main__':
    main()
