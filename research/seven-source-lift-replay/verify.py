#!/usr/bin/env python3
"""Receipt integration of two frozen implementations; not a third oracle.

This bounded Python check does NOT rerun the large native lift enumeration.
Its seven-lift histogram is authenticated native-run evidence. Completeness
requires the separate projection/enumeration proof and actual native replay.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from math import comb
from pathlib import Path


EXPECTED = {
    'cpp': '225e2a8fe167864254d3f0bdc8be28820a14886ceb7e07f711d8aa8454d7d658',
    'native': 'f9e50d14b7c5f0d802af9dd15df44829dbc086d358642594df7ed786e144a2f7',
    'oracle_code': '4216bf6ae2a86194b3ad12823232fdbd86cdc8b361d06ec0b353cc8f3648243a',
    'oracle_result': '829a49e6ce0e1c17134f89db7bf8c074b92b54f32c58bb37e76fb9e25b70ae72',
    'source_census': '63c8b79685b817640ce51575c784b4355f9d0e977e65b5d7772d2f184feb79dc',
}


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def authenticate(role, data):
    need(hashlib.sha256(data).hexdigest() == EXPECTED[role], 'source SHA256: ' + role)
    return data


def histogram_total(histogram, total):
    need(all(str(int(key)) == key and type(value) is int and value >= 0
             for key, value in histogram.items()), 'invalid histogram alphabet/count')
    need(sum(histogram.values()) == total, 'histogram count does not close')


def decode_six(packed, canonical):
    need(type(packed) is int and 0 <= packed < (1 << 48), 'packed word exceeds sixteen three-bit cells')
    word = tuple((packed >> (3 * (15 - i))) & 7 for i in range(16))
    need(set(word) == set(range(6)), 'invalid six-source alphabet')
    need(canonical(word) == word, 'packed word is not first-appearance canonical')
    need(sorted(Counter(word).values()) == [2, 2, 2, 2, 4, 4], 'wrong six-source profile')
    return word


def reject(call, label):
    try:
        call()
    except RuntimeError:
        return label
    raise RuntimeError('copied-receipt control not detected: ' + label)


def integrate(native, oracle, source, functions):
    canonical = functions['first_appearance']
    pairs, intervals, targets = (functions[k] for k in ('prefix_pairs', 'literal_intervals', 'target_set'))
    need(native['status'] == 'PASS_CONTROLS_AND_FULL_FILTERED_L20_REPLAY'
         and native['quick_only'] is False, 'only a quick/incomplete native receipt was supplied')
    five = native['five_source']
    need(five['canonical_words'] == oracle['canonical_words'] == 51975
         and five['full30_words'] == oracle['full30_count'] == 1257
         and five['histogram'] == oracle['coverage_histogram'], 'independent five-source census disagreement')
    histogram_total(five['histogram'], 51975)
    full_five = set(map(tuple, oracle['full30_words']))
    need(len(full_five) == 1257 and all(targets(5) <= pairs(word) for word in full_five),
         'frozen full-five list invalid')
    six = native['six_source_candidates']
    expected_insertions = len(full_five) * comb(16, 4)
    need(six['insertions'] == expected_insertions == 2287740, 'six-source insertion count')
    histogram_total(six['filtered_candidate_histogram'], expected_insertions)
    need(six['full56_raw'] == six['filtered_candidate_histogram']['56'] == 17152
         and six['full56_canonical_unique'] == 8576
         and six['multiplicity_histogram'] == {'2': 8576}, 'six-source raw/canonical accounting')
    need(sum(int(multiplicity) * count for multiplicity, count in six['multiplicity_histogram'].items())
         == six['full56_raw'], 'six-source multiplicity sum')
    packed = six['full56_packed_canonical_words']
    need(len(packed) == 8576 and packed == sorted(set(packed)), 'packed words not sorted unique')
    words = set()
    projections = 0
    for code in packed:
        word = decode_six(code, canonical)
        available = pairs(word)
        need(available == intervals(word) and targets(6) <= available,
             'six-source word does not literally cover all56')
        words.add(word)
        for label, count in Counter(word).items():
            if count == 4:
                projected = canonical(tuple(source for source in word if source != label))
                need(projected in full_five, 'six-source four-use projection absent from full-five list')
                projections += 1
    need(len(words) == 8576 and projections == 17152, 'six-source decoded/projection count')
    seven = native['seven_source_candidates']
    expected_lifts = len(words) * comb(20, 4)
    need(seven['raw_lifts'] == expected_lifts == 41550720, 'seven-source raw insertion count')
    histogram_total(seven['histogram'], expected_lifts)
    need(max(map(int, seven['histogram'])) == seven['candidate_lift_max_coverage'] == 95
         and seven['raw_candidate_lifts_at_max'] == seven['histogram']['95'] == 940
         and seven['full98_lifts'] == seven['histogram'].get('98', 0) == 0,
         'conditional seven-source histogram conclusion mismatch')
    maximum = tuple(seven['first_max_witness'])
    need(len(maximum) == 20 and sorted(Counter(maximum).values()) == [2, 2, 2, 2, 4, 4, 4],
         'maximum witness profile')
    need(pairs(maximum) == intervals(maximum) and len(pairs(maximum) & targets(7)) == 95,
         'maximum witness literal coverage')
    need(maximum.count(6) == 4
         and canonical(tuple(label for label in maximum if label != 6)) in words,
         'maximum witness is not a lift of a retained full-six word')
    prior = next(row for row in source['runs'] if row['n'] == 6 and row['W'] == 4
                 and row['L'] == 16 and sorted(row['profile']) == [2, 2, 2, 2, 4, 4])
    need(prior['full_coverage_6source_words'] == prior['words_at_max'] == len(words)
         and prior['lift_k'] == 4 and prior['lifts'] == expected_lifts
         and prior['lift_max_coverage'] == 95 and prior['lifts_at_max'] == 940,
         'retained source local six/lift record disagreement')
    prior_six = tuple(map(int, prior['first_word_at_max'].split()))
    prior_lift = tuple(map(int, prior['first_lift_at_max'].split()))
    need(canonical(prior_six) in words and targets(6) <= pairs(prior_six), 'source six witness missing')
    need(pairs(prior_lift) == intervals(prior_lift)
         and len(pairs(prior_lift) & targets(7)) == 95
         and canonical(tuple(label for label in prior_lift if label != 6)) in words,
         'source lifted witness disagreement')
    weak = tuple(oracle['controls']['dropping_weight_four_targets_is_wrong']['word'])
    need(targets(5, 3) <= pairs(weak) and not targets(5) <= pairs(weak),
         'weight-four definition control is not discriminating')
    return {'five_canonical_words': 51975, 'five_full30_words': 1257,
            'six_individually_decoded_checked_words': len(words),
            'six_individually_checked_four_use_projections': projections,
            'six_native_candidate_insertions': expected_insertions,
            'seven_authenticated_native_raw_lifts': expected_lifts,
            'seven_conditional_filtered_maximum': 95, 'seven_raw_lifts_at_maximum': 940,
            'seven_authenticated_native_full98_lifts': 0,
            'six_and_seven_literal_maximum_witnesses_checked': 3,
            'weight_three_prefilter_is_weaker': True,
            'weight_three_prefilter_loses_no_full30_candidates': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--cpp', type=Path)
    parser.add_argument('--native', type=Path)
    parser.add_argument('--oracle-code', type=Path)
    parser.add_argument('--oracle-result', type=Path)
    parser.add_argument('--source-census', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    files = {'cpp': args.cpp or args.package_root / 'census.cpp',
             'native': args.native or args.package_root / 'NATIVE.json',
             'oracle_code': args.oracle_code or args.package_root / 'independent_oracle.py',
             'oracle_result': args.oracle_result or args.package_root / 'ORACLE-RESULT.json',
             'source_census': args.source_census or args.package_root / 'source/PR4207-CENSUS.json.txt'}
    raw = {role: authenticate(role, path.read_bytes()) for role, path in files.items()}
    functions = {'__name__': '_frozen_five_source_oracle'}
    exec(compile(raw['oracle_code'], 'independent_oracle.py', 'exec', dont_inherit=True), functions)
    native, oracle, source = (json.loads(raw[role]) for role in ('native', 'oracle_result', 'source_census'))
    checked = integrate(native, oracle, source, functions)
    bad_hist = deepcopy(native['seven_source_candidates']['histogram'])
    bad_hist['95'] += 1
    controls = [reject(lambda: histogram_total(bad_hist, 41550720), 'copied histogram count drift'),
                reject(lambda: decode_six(1 << 48, functions['first_appearance']), 'invalid packed length'),
                reject(lambda: decode_six((1 << 45) | native['six_source_candidates']['full56_packed_canonical_words'][0],
                                         functions['first_appearance']), 'noncanonical packed source labels'),
                reject(lambda: authenticate('source_census', raw['source_census'] + b' '), 'changed source checksum')]
    result = {'status': 'PASS_FROZEN_NATIVE_ORACLE_RECEIPT_INTEGRATION', 'checked': checked,
              'input_sha256': EXPECTED,
              'copied_receipt_controls_rejected': controls,
              'large_seven_histogram_reenumerated_in_python': False,
              'native_program_executed_by_this_checker': False,
              'scope': 'Integration of existing frozen native and Python oracle code, not a third independent oracle. '
                       'All8576 listed full-six words checked literally;41,550,720 raw seven-lift histogram authenticated as actual native-run evidence.',
              'maximum_scope': '95 is conditional on full56 six-source projections; it is not a global profile maximum. '
                               'Other projections imply at most97, so the separate completeness proof combines the cases to exclude98.',
              'source_record_scope': 'Only the selected6source(4,4,2,2,2,2) full-word/lift fields and literal witnesses compared. '
                                     'No earlier L14/L16/L18 global censuses or complete floor accepted.',
              'credit': 'Nick Petalas and retained nightangelflowerwin/commdata2338/Cinna Davis/Ross Richardson lineage. '
                        'James Reed cheap/sealed receipt checks remain distinct. Substantial OpenAI Codex assistance.',
              'limitations': ['Completeness is a separate finite enumeration/projection proof plus actual native replay.',
                              'Raw insertion/lift counts are not canonical seven-word counts.',
                              'No arbitrary-size/supplier/physical/precision/outer theorem or new kappa.']}
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    print(json.dumps({'status': result['status'], 'checked': checked}, sort_keys=True))


if __name__ == '__main__':
    main()
