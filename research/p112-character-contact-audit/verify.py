#!/usr/bin/env python3
"""Binding integration only, not a second independent phase enumeration.

Authenticates both frozen implementations/receipts, then checks source recipe
shape, finite descriptor metadata and aggregate accounting. No checker imports.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

HASHES = {
    'geometry': '353220f1edf3a3afda11cd5073c5e55446c23c242969b16a361fa53b8e45dd7e',
    'primary_code': 'cf145bb25c77be08f92a94273bd15937a8833bd55bba297a015a834a791c696e',
    'primary_result': '1da2b3ef97bcaf47d9657c5c0d9ec132d8df0823341497f794e556e437b42473',
    'oracle_code': '6a17511710a9c2fba251419970e72bae066aff454910ddf13ca78f3b3d1ce578',
    'oracle_result': '573766407f3fad64351cdf61f06dac0d7f53fc6225191ec28d291c9b9016bcc4',
}


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def authenticated(role, data):
    need(hashlib.sha256(data).hexdigest() == HASHES[role], 'input SHA256: ' + role)
    return data


def hexadecimal(value):
    return type(value) is str and len(value) == 64 and set(value) <= set('0123456789abcdef')


def span_rank(rows):
    # Deliberately set-span growth, not the primary checker's pivot elimination.
    span = {0}
    for row in rows:
        if row not in span:
            span |= {value ^ row for value in span}
    return len(span).bit_length() - 1


def descriptor_metadata(key, record):
    need(hexadecimal(key) and record['sha256'] == key, 'descriptor digest naming')
    need(type(record['constant_Z4']) is int and 0 <= record['constant_Z4'] < 4,
         'constant exponent alphabet')
    linear, rows = record['linear_Z4'], record['quadratic_rows']
    need(len(linear) == len(rows) == 9 and all(type(v) is int and 0 <= v < 4 for v in linear)
         and all(type(v) is int and 0 <= v < 512 for v in rows), 'descriptor coordinate alphabet')
    need(all(((rows[i] >> j) & 1) == ((rows[j] >> i) & 1) for i in range(9) for j in range(9)),
         'quadratic polar symmetry')
    need(all(((rows[i] >> i) & 1) == (linear[i] & 1) for i in range(9)),
         'Z4 polar diagonal/linear compatibility')
    need(record['native_rank'] == span_rank(rows), 'descriptor stored binary rank')


def recipe(edge):
    rank = edge['minimal_rank']
    need(rank in (1, 2, 3) and len(edge['frame']) == rank, 'contact rank shape')
    ops = edge['operations_coefficient_plus_one']
    if rank == 1:
        skeleton = [('add', (1, 0, 1)), ('native', (0, 'source_exit', 7)),
                    ('native', (1, 'target_exit', 7))]
        histogram = {7: 2}
    else:
        skeleton = [('add', (1, 2, -1)), ('native', (0, 'source_prepare', rank - 1)),
                    ('native', (1, 'target_prepare', rank - 1)), ('native', (2, 'helper_prepare', rank - 1)),
                    ('add', (2, 0, 1)), ('add', (1, 2, 1)), ('add', (2, 0, -1)),
                    ('native', (2, 'helper_return', rank - 1)),
                    ('native', (0, 'source_exit', 8 - rank)), ('native', (1, 'target_exit', 8 - rank))]
        histogram = {rank - 1: 4, 8 - rank: 2}
    need(len(ops) == len(skeleton), 'ordered recipe length')
    actual_hist = Counter()
    for operation, (kind, shape) in zip(ops, skeleton):
        if kind == 'add':
            need(set(operation) == {'add'} and tuple(operation['add']) == shape, 'ordered signed ADD shape')
        else:
            need(set(operation) == {'field', 'native', 'rank', 'phase_sha256'}
                 and (operation['field'], operation['native'], operation['rank']) == shape
                 and hexadecimal(operation['phase_sha256']), 'ordered native typed operation shape')
            actual_hist[operation['rank']] += 1
    need(dict(actual_hist) == histogram == {int(k): v for k, v in edge['native_histogram'].items()},
         'source native histogram')
    need(edge['rank_mass'] == sum(rank * count for rank, count in histogram.items())
         and edge['whole_field_signed_adds'] == (1 if rank == 1 else 4)
         and edge['both_coefficients'] == [-1, 1] and edge['physical_helper_return'] is True,
         'source invoice metadata')
    if rank == 1:
        need(ops[1]['phase_sha256'] == edge['phase_ids'][5]
             and ops[2]['phase_sha256'] == edge['phase_ids'][6], 'rank-one exit phase metadata')
    else:
        need(ops[2]['phase_sha256'] == ops[3]['phase_sha256'], 'target/helper entrance phases disagree')
    return len(ops), sum(actual_hist.values())


def receipt_counts(primary, observed):
    for key, value in observed.items():
        need(primary[key] == value, 'primary aggregate mismatch: ' + key)


def integrate(data, primary, oracle):
    inventory, edges = data['phase_operators'], data['edge_witnesses']
    ports, partners = data['ports'], data['partners']
    need(data['dimension'] == 9 and len(ports) == len(partners) == 112
         and len(inventory) == 8880 and len(edges) == 5824, 'source finite domain')
    need(all(type(x) is int and 0 < x < 512 and x.bit_count() % 2 for x in ports + partners),
         'provided odd port/partner encodings')
    need(all((p & q).bit_count() % 2 == 0 for p, q in zip(ports, partners)), 'provided paired perpendicularity')
    phase_rank_hist = Counter()
    constant_hist = Counter()
    for key, record in inventory.items():
        descriptor_metadata(key, record)
        phase_rank_hist[record['native_rank']] += 1
        constant_hist[record['constant_Z4']] += 1
    legal = {(i, j) for i, p in enumerate(ports) for j, q in enumerate(ports)
             if (p & q).bit_count() % 2 == 0}
    seen, rank_counts, native_counts, op_count = set(), Counter(), Counter(), 0
    serialized = set(inventory)
    for edge in edges:
        pair = edge['source'], edge['target']
        need(pair in legal and pair not in seen, 'actual edge enumeration metadata')
        seen.add(pair)
        p, q = ports[pair[0]], partners[pair[1]]
        expected_rank = 1 if p == q else 2 if (p & q).bit_count() % 2 == 0 else 3
        need(edge['minimal_rank'] == expected_rank, 'source contact-case metadata')
        need(len(edge['phase_ids']) == 8 and all(key in inventory for key in edge['phase_ids']),
             'source phase-ID inventory metadata')
        total, native_total = recipe(edge)
        op_count += total
        rank_counts[expected_rank] += 1
        native_counts[expected_rank] += native_total
        serialized |= {op['phase_sha256'] for op in edge['operations_coefficient_plus_one'] if 'phase_sha256' in op}
    need(seen == legal, 'source edges do not close legal pairs')
    need(dict(rank_counts) == {1: 104, 2: 2912, 3: 2808}, 'source contact rank histogram')
    identity_phase = hashlib.sha256(bytes(512)).hexdigest()
    need(identity_phase not in serialized and len(serialized) == 22547, 'serialized phase union/auxiliary identity metadata')
    observed = {'dimension': 9, 'characters': 512, 'edges': len(edges),
                'contact_rank_counts': {str(k): v for k, v in sorted(rank_counts.items())},
                'inventory_records_reconstructed': len(inventory),
                'inventory_character_exponents': len(inventory) * 512,
                'serialized_inventory_and_native_phase_union': len(serialized),
                'distinct_generated_phase_arrays_including_transition_only': len(serialized) + 1,
                'auxiliary_identity_preparation_phase_arrays': 1,
                'ordered_typed_plus_one_operations_checked': op_count,
                'native_occurrences_by_case': {str(k): v for k, v in sorted(native_counts.items())},
                'both_sign_edge_character_cases': len(edges) * 512 * 2,
                'three_raw_input_column_cases': len(edges) * 512 * 2 * 3,
                'cache_occurrences_by_case': {str(k): v * 512 * 2 for k, v in sorted(rank_counts.items())}}
    receipt_counts(primary, observed)
    need(primary['source_sha256'] == HASHES['geometry']
         and primary['checker_sha256'] == HASHES['primary_code'], 'primary provenance metadata')
    need(len(primary['controls']) == 4 and {row['mutation'] for row in primary['controls']}
         == {'omit_helper_return', 'omit_precompensation', 'wrong_delivery', 'global_i'}, 'primary control record set')
    for record in primary['controls']:
        need((record['source'], record['target']) in seen and 0 <= record['character'] < 512
             and record['input_column'] in (0, 1, 2) and record['output_field'] in (0, 1, 2)
             and record['actual_Gaussian'] != record['expected_Gaussian']
             and record['input_Gaussian'] == [1, 0] and record['observed_raw_address'] == 0,
             'primary fault witness metadata')
    need(oracle['status'] == 'PASS_FREE_NONCOMMUTATIVE_DIRTY_HELPER_IDENTITY'
         and [row['sign'] for row in oracle['signs']] == [-1, 1]
         and oracle['symbolic_wrong_programs_detected'] == 10, 'universal oracle receipt boundary')
    return observed, dict(sorted(phase_rank_hist.items())), dict(sorted(constant_hist.items()))


def reject(call, label):
    try:
        call()
    except RuntimeError:
        return label
    raise RuntimeError('copied corruption escaped: ' + label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--primary-code', type=Path)
    parser.add_argument('--primary-result', type=Path)
    parser.add_argument('--oracle-code', type=Path)
    parser.add_argument('--oracle-result', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    files = {'geometry': args.source or args.package_root / 'source/PR4204-GEOMETRY.json.gz',
             'primary_code': args.primary_code or args.package_root / 'primary_verify.py',
             'primary_result': args.primary_result or args.package_root / 'PHASE-RESULT.json',
             'oracle_code': args.oracle_code or args.package_root / 'independent_oracle.py',
             'oracle_result': args.oracle_result or args.package_root / 'ORACLE-RESULT.json'}
    raw = {role: authenticated(role, path.read_bytes()) for role, path in files.items()}
    data = json.loads(gzip.decompress(raw['geometry']))
    primary, oracle = json.loads(raw['primary_result']), json.loads(raw['oracle_result'])
    observed, ranks, constants = integrate(data, primary, oracle)
    bad_receipt = deepcopy(primary)
    bad_receipt['edges'] -= 1
    bad_edge = deepcopy(data['edge_witnesses'][0])
    bad_edge['operations_coefficient_plus_one'][0], bad_edge['operations_coefficient_plus_one'][1] = (
        bad_edge['operations_coefficient_plus_one'][1], bad_edge['operations_coefficient_plus_one'][0])
    key, original_phase = next(iter(data['phase_operators'].items()))
    bad_phase = deepcopy(original_phase)
    bad_phase['native_rank'] = (bad_phase['native_rank'] + 1) % 10
    controls = [reject(lambda: receipt_counts(bad_receipt, observed), 'copied primary aggregate mismatch'),
                reject(lambda: recipe(bad_edge), 'copied ordered operation swap'),
                reject(lambda: descriptor_metadata(key, bad_phase), 'copied polar rank mismatch'),
                reject(lambda: authenticated('geometry', raw['geometry'] + b' '), 'changed immutable geometry checksum')]
    result = {'status': 'PASS_P112_SOURCE_AND_FROZEN_PROOF_RECEIPT_BINDING_INTEGRATION',
              'input_sha256': HASHES, 'source_observed_aggregate_metadata': observed,
              'phase_record_binary_rank_histogram': ranks, 'phase_record_constant_Z4_histogram': constants,
              'copied_corruption_controls_rejected': controls,
              'phase_characters_recomputed_by_this_integration': 0,
              'primary_or_predecessor_checker_imported': False,
              'scope': 'Third binding layer: source ordered recipe/descriptor metadata and counts matched to authenticated '
                       'primary full-phase and independently frozen universal free-group receipts. No second independent all-phase enumeration.',
              'boundary': 'Universal abstract noncommuting dirty-helper identity is separate from primary finite P112 phase/source binding. '
                          'Operation physical_helper_return is source metadata, not executed native/compiler transport.',
              'limits': ['No original port reconstruction, full port/circuit caller, B4/DP, physical invoice, precision, supplier/outer theorem or new kappa.',
                         'Binary polar metadata rank checks do not establish complex phase values; those remain authenticated primary replay evidence.'],
              'credit': 'Ross Richardson PR4204; retained PR425/433/523/531/kernel92 lineage. Classical change-of-frame identity; '
                        'no broad priority claim. Substantial OpenAI Codex assistance.'}
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    print(json.dumps({'status': result['status'], 'edges': observed['edges'],
                      'ordered_operations': observed['ordered_typed_plus_one_operations_checked'],
                      'descriptor_metadata_records': observed['inventory_records_reconstructed'],
                      'corruption_controls': len(controls)}, sort_keys=True))


if __name__ == '__main__':
    main()
