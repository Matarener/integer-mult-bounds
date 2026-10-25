#!/usr/bin/env python3
"""Exact two-axis minimum-width certificate and separate literal witness replay.

Hiroki KUMAZAKI, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor verifier is imported. The all-width argument is in PROOF.md.
"""
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
THRESHOLDS = (8, 9, 6, 7)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def character(counts):
    """Point order 00,10,01,11; phases are evaluated on input addresses."""
    a, b, c, d = counts
    return (sum(counts) % 4, (b+d) % 4, (c+d) % 4, d % 2)


def spanning(counts):
    # Any three distinct points form an affine basis of the two-axis space.
    return sum(x != 0 for x in counts) >= 3


def minimum_formula(chi):
    r, u1, u2, v = chi
    candidates = []
    for z in (v, v+2):
        a = [(r-u1-u2+z) % 4, (u1-z) % 4, (u2-z) % 4, z]
        missing = max(0, 3-sum(x != 0 for x in a))
        cost = sum(a)+4*missing
        # Realize the displayed cost without changing the residue or character.
        counts = a[:]
        for index in [i for i, value in enumerate(a) if value == 0][:missing]:
            counts[index] = 4
        need(character(counts) == chi and spanning(counts) and sum(counts) == cost,
             'Residue-formula witness is a genuine full-span tuple')
        candidates.append((cost, tuple(counts)))
    return min(candidates)


def compositions(width):
    for a in range(width+1):
        for b in range(width-a+1):
            for c in range(width-a-b+1):
                yield a, b, c, width-a-b-c


def minimum_checks():
    characters = list(itertools.product(range(4), range(4), range(4), range(2)))
    # A positive count can be reduced by four until it lies in 1..4;
    # this preserves both character and support. Thus this is a complete
    # minimum census, not a guessed maximum-width search cutoff.
    census = {}
    for counts in itertools.product(range(5), repeat=4):
        if spanning(counts):
            chi = character(counts)
            candidate = (sum(counts), counts)
            if chi not in census or candidate < census[chi]:
                census[chi] = candidate
    need(set(census) == set(characters), 'All 128 phase characters occur')
    minima = {}
    histograms = []
    for chi in characters:
        cost, witness = minimum_formula(chi)
        need(cost == census[chi][0], 'Formula matches independent bounded count census')
        minima[chi] = cost
    for r in range(4):
        histogram = Counter(value for chi, value in minima.items() if chi[0] == r)
        need(max(histogram) == THRESHOLDS[r] and sum(histogram.values()) == 32,
             'Exact worst character in each central residue')
        histograms.append({'residue': r, 'first_faithful_width': THRESHOLDS[r],
                           'minimum_width_histogram': {str(k): histogram[k] for k in sorted(histogram)},
                           'attaining_character': [r, 0, 0, 0],
                           'attaining_minimum': minima[r, 0, 0, 0]})
        need(minima[r, 0, 0, 0] == THRESHOLDS[r], 'Zero nonconstant character attains worst case')
    fixed_widths = []
    for width in range(1, 14):
        actual = {character(counts) for counts in compositions(width) if spanning(counts)}
        predicted = {chi for chi, lower in minima.items() if chi[0] == width % 4 and lower <= width}
        need(actual == predicted, 'Exact fixed-width realization agrees with minimum and four-zero padding')
        fixed_widths.append({'width': width, 'full_span_characters': len(actual),
                            'central_quotient_injective': len(actual) == 32})
    need([row['full_span_characters'] for row in fixed_widths[:9]] == [0, 0, 4, 13, 28, 32, 32, 32, 32],
         'Small-width boundary counts')
    need(all(row['central_quotient_injective'] for row in fixed_widths[5:])
         and not fixed_widths[4]['central_quotient_injective'], 'First uniform threshold is six')
    # Affine span is essential: one zero point realizes the late residue-one
    # phase character, but cannot distinguish affine coefficient vectors.
    need(character((1, 0, 0, 0)) == (1, 0, 0, 0)
         and not spanning((1, 0, 0, 0)) and minima[1, 0, 0, 0] == 9,
         'Phase realization alone is not a kernel certificate')
    return {'phase_character_count': len(characters), 'count_normal_forms': 5**4,
            'formula_matches_complete_minimum_census': True,
            'per_residue': histograms, 'fixed_width_corroboration': fixed_widths,
            'uniform_cutoff': 6, 'complete_four_width_window': [6, 7, 8, 9],
            'phase_only_false_positive_width': 1}


def test_set_checks():
    def detects(widths):
        return all(any(f % 4 == r and f >= THRESHOLDS[r] for f in widths) for r in range(4))
    need(detects([6, 7, 8, 9]) and detects([8, 9, 10, 11]), 'Both sharp and inherited windows suffice')
    need(not detects(range(1, 9)), 'No set below width nine can suffice')
    # The four explicit sign-projectors provide the necessity witnesses.
    checked = 0
    for size in range(4):
        for widths in itertools.combinations(range(1, 14), size):
            need(not detects(widths), 'At least four distinct residues are required')
            checked += 1
    return {'test_sets_with_at_most_three_widths_checked': checked,
            'first_sufficient_consecutive_window_start': 6,
            'all_widths_one_through_eight_fail': True,
            'criterion': 'For each r, include an f congruent to r modulo 4 with f >= (8,9,6,7)[r]',
            'fixed_external_coefficients_required': True}


def authenticate():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    paths = []
    for row in manifest['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Pinned input bytes: '+row['path'])
            paths.append(row['path'])
    return paths


def run():
    sources = authenticate()
    spec = importlib.util.spec_from_file_location('two_axis_literal', HERE/'literal.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {'status': 'PASS_SHARP_TWO_AXIS_NATIVE_CUTOFF',
            'scope': 'Two-axis affine/quadratic Gaussian monomials over Q(i) or C; group-algebra kernel modulo central phase',
            'authenticated_inputs': sources,
            'minimum_widths': minimum_checks(),
            'test_set_criterion': test_set_checks(),
            'literal_obstructions': module.run(),
            'proof': 'PROOF.md supplies the all-width necessity/sufficiency and analytic upper-bound argument',
            'general_n_cutoff_claimed': False, 'physical_supplier_claimed': False,
            'selected_frontier_changed': False}


def main():
    need(sys.argv[1:] in ([], ['--write']), 'Use no arguments or --write')
    result = run()
    encoded = json.dumps(result, sort_keys=True, indent=2)+'\n'
    receipt = HERE/'RESULT.json'
    if sys.argv[1:]:
        need(not receipt.exists(), 'Refuse to overwrite receipt')
        receipt.write_text(encoded)
    else:
        need(receipt.read_text() == encoded, 'Exact deterministic receipt differs')
    print(result['status'])
    print(json.dumps({'cutoff': 6, 'residue_thresholds': list(THRESHOLDS),
                      'minimal_window': [6, 7, 8, 9], 'late_witness_first_width': 9}))


if __name__ == '__main__':
    main()
