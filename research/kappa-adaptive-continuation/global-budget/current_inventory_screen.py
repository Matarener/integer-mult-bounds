#!/usr/bin/env python3
"""Exact necessary gate at the new receiver-sharing endpoint by default.

This is a rejection test over every packing/clock, not an admission or a gain
claim. Input either a native canonical word, or explicit complete local and
helper histograms. The dual is freshly checked over all width 4..9 patterns.
The width-price interpretation follows PR3862 (thakrarsagar) and PR3815
(ChaloupeMusic); no new staging mechanism is asserted here.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
from packing_certificate import certify
from native_owner_invoice import basis

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PACKAGE = HERE.parent/'sources/PR3815/research/staged544-clock-ceiling'


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--native-word', type=Path)
    ap.add_argument('--local-profile', type=Path)
    ap.add_argument('--width-inventory', type=Path)
    ap.add_argument('--endpoint', type=F, help='Explicit rational screening endpoint; default is the actual current root upper endpoint.')
    ap.add_argument('--anchor-invoice', type=Path, default=HERE/'receiver-sharing/RESULT.json')
    ap.add_argument('--out', type=Path, default=HERE/'CURRENT-INVENTORY-SCREEN.json')
    args = ap.parse_args()
    inv = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    spec = importlib.util.spec_from_file_location('changed_inventory_invoice', inv)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    receipt_path = HERE/'PR3815-INDEPENDENT-REVIEW.json'
    receipt = I.read(receipt_path)
    I.need(receipt['status'] == 'PASS_FRESH_PR3815_OWNERS_AND_INDEPENDENT_EXACT_PRICE_DUAL', 'source review gate')
    for rel, expected in receipt['input_sha256'].items():
        I.need(I.digest(REPO/rel) == expected, 'source/engine pin: '+rel)
    anchor = I.read(args.anchor_invoice)
    I.need(anchor['status'] == 'PASS_LITERAL_CHANGED_NATIVE_OWNERS_AND_TWO_ENGINE_INVOICE', 'current complete physical invoice')
    I.need(anchor['script_sha256'] == I.digest(HERE/'native_owner_invoice.py'), 'current invoice implementation')
    I.need(anchor['source_review_sha256'] == I.digest(receipt_path), 'current invoice source review')
    for paths in anchor['supplied_native_inputs'].values():
        for rel, expected in paths.items():
            I.need(I.digest(REPO/rel) == expected, 'current native source: '+rel)
    I.need((anchor['replicas'], anchor['calls'], anchor['productive_families']) == (360, 3240, 322560), 'current physical geometry')
    I.need(anchor['helper_widths_unchanged_in_order'] and anchor['all_native_endpoint_subspaces_unchanged'], 'current ordered inventory contract')
    native_paths = [REPO/rel for rel in anchor['supplied_native_inputs']['gauge44'] if rel.endswith('/CANONICAL-WORD.json.gz')]
    I.need(len(native_paths) == 1, 'one bound current canonical provider')
    current_word = I.read(native_paths[0])
    I.need((current_word['v'], current_word['h'], current_word['R']) == (112, 9, 408), 'current native geometry and helper count')
    baseline_local = {int(r): n for r, n in current_word['local_profile'].items()}
    I.need(all({int(r): n for r, n in p.items()} == baseline_local for p in anchor['provider_local_profiles'].values()), 'both current providers have the same complete profile')
    baseline_widths = Counter(len(basis(current_word['frames'][current_word['final'][r]]))-
                             len(basis(current_word['frames'][current_word['start'][r]])) for r in range(224, 632))
    I.need(baseline_widths == {4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}, 'actual unchanged helper histogram')
    current_endpoint = F(anchor['root']['rational'][1])
    endpoint = current_endpoint if args.endpoint is None else args.endpoint
    I.need(0 < endpoint < 1, 'concave-power screening domain')
    if args.native_word:
        I.need(not args.local_profile and not args.width_inventory, 'one candidate input mode')
        word = I.read(args.native_word)
        I.need((word['v'], word['h']) == (112, 9), 'candidate belongs to the screened local data geometry')
        local = {int(r): n for r, n in word['local_profile'].items()}
        widths = Counter(len(basis(word['frames'][word['final'][r]]))-
                         len(basis(word['frames'][word['start'][r]]))
                         for r in range(2*word['v'], 2*word['v']+word['R']))
        source_paths = [args.native_word]
        mode = 'Width inventory derived from actual native endpoint subspaces; complete local profile is the word receipt. Operator correctness requires a separate native gate.'
    elif args.local_profile and args.width_inventory:
        local = {int(r): n for r, n in I.read(args.local_profile).items()}
        widths = {int(r): n for r, n in I.read(args.width_inventory).items()}
        source_paths = [args.local_profile, args.width_inventory]
        mode = 'Explicit proposed complete histograms. No native realization is inferred.'
    else:
        I.need(not args.local_profile and not args.width_inventory, 'both explicit histograms required')
        source = native_paths[0]
        word = current_word
        local = {int(r): n for r, n in word['local_profile'].items()}
        widths = Counter(len(basis(word['frames'][word['final'][r]]))-
                         len(basis(word['frames'][word['start'][r]])) for r in range(224, 632))
        source_paths = [source]
        mode = 'Pinned current receiver-sharing supplier positive rejection control.'
    I.need(all(type(n) is int and n >= 0 and 0 < r < 73 for r, n in local.items()), 'complete local profile schema')
    I.need(all(type(n) is int and n >= 0 and 4 <= w <= 9 for w, n in widths.items()), 'certified width alphabet4..9')
    widths = {w: widths.get(w, 0) for w in range(4, 10)}
    source_dual = I.module(PACKAGE/'ceiling_certificate.py', 'changed_inventory_basis')
    common = dict(dimension=73, productive=896, calls=9,
                  bins={8: 672, 16: 448, 32: 448, 48: 448}, basis=source_dual.BASIS)
    baseline = certify(I, endpoint=current_endpoint, local=baseline_local, supply=baseline_widths, **common)
    I.need(baseline['strictly_excludes_endpoint'], 'unchanged supplier is capped at upper endpoint')
    fused = Counter(baseline_local)
    fused.update({1: -2, 2: 1})
    positive = certify(I, endpoint=current_endpoint, local=fused, supply=baseline_widths, **common)
    I.need(positive['dual_feasible'] and F(positive['paid_invoice_minus_productive_lower_bound']) < 0,
           'width-preserving fusion strictly lowers the complete lower bound')
    result = certify(I, endpoint=endpoint, local=local, supply=widths, **common)
    I.need(result['dual_feasible'], 'every bin pattern is certified for this screening dual')
    result.update({
        'status': 'REJECTED_BY_COMPLETE_INVENTORY_DUAL' if result['strictly_excludes_endpoint'] else 'NOT_EXCLUDED_BY_COMPLETE_INVENTORY_DUAL',
        'script_sha256': I.digest(Path(__file__)), 'source_review_sha256': I.digest(receipt_path),
        'current_anchor_invoice_sha256': I.digest(args.anchor_invoice),
        'current_anchor_root': anchor['root']['rational'],
        'explicit_endpoint_override': args.endpoint is not None,
        'dual_implementation_sha256': I.digest(HERE/'packing_certificate.py'),
        'candidate_input_sha256': {str(p.resolve().relative_to(REPO)): I.digest(p) for p in source_paths},
        'complete_local_profile': local, 'width_inventory_per_call': widths,
        'helpers_per_call': sum(widths.values()),
        'local_raw_mass': sum(r*n for r, n in local.items()),
        'hosted_width_per_call': sum(w*n for w, n in widths.items()),
        'input_scope': mode,
        'controls': {'endpoint': str(current_endpoint),
                     'unchanged_current_supplier_lower_bound': baseline['paid_invoice_minus_productive_lower_bound'],
                     'one_per_call_two_H1_to_H2_lower_bound': positive['paid_invoice_minus_productive_lower_bound']},
        'decision_scope': ('A positive lower bound excludes reaching the screening endpoint '
                           'under every packing and clock of the same rank73 productive geometry '
                           'and idle-bin template, even if all additional implementation costs '
                           'are free. A nonpositive bound only means NOT EXCLUDED; it supplies '
                           'no native word, owner fill, improved root or outer admission. '
                           'The certified input helper alphabet is 4..9; widths 1..3 are not silently extrapolated. '
                           'The predecessor changed_inventory_screen.py and its old-endpoint receipts are retained unchanged.')
    })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'lower bound', result['lower_bound_decimal'], 'patterns', result['patterns_checked'])


if __name__ == '__main__':
    main()
