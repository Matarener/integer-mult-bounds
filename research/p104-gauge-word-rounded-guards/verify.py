#!/usr/bin/env python3
"""Completed-operation rounded-error guards for the two PR5833 P104 words.

Applies PR5838's causal forward-defect bound (causal.py and transfer.py,
imported unchanged from research/p104-gauge-error-covariance) to the two
complete words emitted by PR5833 (research/p104-priced-amplification).
Every physical MOVE, ADD and SCALE instruction is a relative defect site,
as in PR5838's physical timeline after its exact virtual identities are
deleted. The PR5830 word is replayed under the same adapter and must equal
PR5838's recorded 20-bit causal case exactly.

Default mode recomputes everything and compares with RESULT.json.
--write regenerates RESULT.json. Standard library only.
"""
from fractions import Fraction as F
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
COVARIANCE = 'research/p104-gauge-error-covariance'
AMPLIFICATION = 'research/p104-priced-amplification'
WORDS = (
    ('pr5830_gauge_word', f'{COVARIANCE}/inputs/WORD.json.gz'),
    ('pr5833_budget_word', f'{AMPLIFICATION}/BUDGET-WORD.json.gz'),
    ('pr5833_minimum_word', f'{AMPLIFICATION}/MINIMUM-WORD.json.gz'),
)
# Ideal amplification peaks published by PR5830/PR5838 and PR5833.
PUBLISHED_PEAKS = {'pr5830_gauge_word': 65537, 'pr5833_budget_word': 96, 'pr5833_minimum_word': 2}
TOP_GUARD = 22


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate():
    rows = json.loads((P / 'SOURCES.json').read_text())['files']
    inputs = [r for r in rows if r['usage'] == 'input']
    need(len(inputs) == 6, 'six live inputs pinned')
    for r in inputs:
        need(sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'], 'source hash ' + r['path'])
    return {r['path']: r['sha256'] for r in inputs}


def read_word(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def defect_sites(word):
    return {j for j, e in enumerate(word['program']) if e[0] in ('MOVE', 'ADD', 'SCALE')}


def guard_scan(causal, word, weights, sites):
    """Causal cases from TOP_GUARD down to the first guard whose public bound reaches B."""
    cases = []
    for guard in range(TOP_GUARD, 0, -1):
        case = causal.bound(word, weights, sites, guard)
        cases.append(case)
        if max(case['final'][:word['public']]) >= 1:
            return cases
    raise ValueError('no failing guard above zero')


def analyse(causal, transfer, word):
    sites = defect_sites(word)
    weights, ideal_peak = transfer.ideal(word, sites)
    cases = guard_scan(causal, word, weights, sites)
    need(len(cases) >= 2, 'top guard already fails')
    accepted, rejected = cases[-2], cases[-1]
    public = word['public']
    final_max = max(accepted['final'][:public])
    need(final_max < 1 <= max(rejected['final'][:public]), 'least accepted causal guard bracket')
    need(all(v == 0 for v in accepted['final'][public:]), 'reset-owned fields return with zero error')
    counts = {op: sum(1 for e in word['program'] if e[0] == op) for op in ('MOVE', 'ADD', 'SCALE', 'COPY', 'INIT', 'CLEAR')}
    identity_scales = sum(1 for e in word['program'] if e[0] == 'SCALE' and F(e[-2]) == 1)
    return {
        'instructions': len(word['program']),
        'public_fields': public,
        'owned_fields': word['owned_fields'],
        'operation_counts': counts,
        'identity_scale_sites': identity_scales,
        'defect_sites': len(sites),
        'ideal_peak': ideal_peak,
        'least_causal_guard': accepted['guard'],
        'final_public_bound': final_max,
        'intermediate_error_bound': accepted['peak'],
        'intermediate_error_at': accepted['peak_at'],
        'field_norm_plus_error_bound': ideal_peak + accepted['peak'],
        'rejected_guard': rejected['guard'],
        'rejected_final_public_bound': max(rejected['final'][:public]),
        'scan': [{'guard': c['guard'], 'final_public_bound': max(c['final'][:public]), 'intermediate_error_bound': c['peak']} for c in cases],
    }, accepted


def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    return x


def rejection(label, fn):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('accepted control: ' + label)


def controls(causal, transfer, words):
    out = []
    budget = words['pr5833_budget_word']
    sites = defect_sites(budget)

    def truncated():
        w = dict(budget)
        w['program'] = budget['program'][:-1]
        transfer.ideal(w, defect_sites(w))
    out.append(rejection('drop the last instruction of the budget word', truncated))

    def doubled_scale():
        w = dict(budget)
        program = [list(e) for e in budget['program']]
        j = next(i for i, e in enumerate(program) if e[0] == 'SCALE')
        program[j][-2] = str(2 * F(program[j][-2]))
        w['program'] = program
        transfer.ideal(w, defect_sites(w))
    out.append(rejection('double one SCALE coefficient of the budget word', doubled_scale))

    weights, _ = transfer.ideal(budget, sites)
    case19 = causal.bound(budget, weights, sites, 19)
    out.append(rejection('accept guard 19 on the budget word',
                         lambda: need(max(case19['final'][:budget['public']]) < 1, 'guard 19 exceeds B')))
    fewer = set(sorted(sites)[:-1000])
    weights_fewer, _ = transfer.ideal(budget, fewer)
    case_fewer = causal.bound(budget, weights_fewer, fewer, 20)
    case_full = causal.bound(budget, weights, sites, 20)
    out.append(rejection('omit the last 1000 defect sites without changing the bound',
                         lambda: need(case_fewer['final'] == case_full['final'], 'sites change the bound')))
    return out


def calculate():
    hashes = authenticate()
    causal = load_module('p104_causal', f'{COVARIANCE}/causal.py')
    transfer = load_module('p104_transfer', f'{COVARIANCE}/transfer.py')
    words = {name: read_word(rel) for name, rel in WORDS}
    results, accepted = {}, {}
    for name, _ in WORDS:
        results[name], accepted[name] = analyse(causal, transfer, words[name])
        need(results[name]['ideal_peak'] == PUBLISHED_PEAKS[name], 'published ideal peak ' + name)

    # Adapter control: PR5830's word under this site convention equals PR5838's
    # recorded 20-bit causal case, field by field, exactly.
    recorded = json.loads((ROOT / COVARIANCE / 'RESULT.json').read_text())
    need(recorded['causal_final_guard'] == 20, 'PR5838 recorded guard')
    rec20 = next(c for c in recorded['causal_cases'] if c['guard'] == 20)
    ours = accepted['pr5830_gauge_word']
    need(ours['guard'] == 20, 'PR5830 word least guard under this adapter')
    need([str(v) for v in ours['final']] == rec20['final'], 'PR5830 final coefficients equal PR5838 record')
    # PR5838's timeline also holds exact virtual identities, so only its
    # instruction index differs; value, field and site count must agree.
    need(str(ours['peak']) == rec20['peak'] and ours['peak_at'][1] == rec20['peak_at'][1], 'PR5830 peak equals PR5838 record')
    need(rec20['sites'] == results['pr5830_gauge_word']['defect_sites'], 'PR5830 defect-site count equals PR5838 record')

    budget, minimum = results['pr5833_budget_word'], results['pr5833_minimum_word']
    for r in (budget, minimum):
        need(r['least_causal_guard'] == 20, 'twenty-bit causal guard')
        need(r['final_public_bound'] < F(978, 1000), 'final error below 0.978B')
        need(r['intermediate_error_bound'] < F(978, 1000), 'intermediate error below 0.978B')
    need(budget['field_norm_plus_error_bound'] < 97, 'budget word field norm plus error below 97B')
    need(minimum['field_norm_plus_error_bound'] < 3, 'minimum word field norm plus error below 3B')
    old = results['pr5830_gauge_word']
    need(old['intermediate_error_bound'] > 26 and old['field_norm_plus_error_bound'] < 2 ** 17, 'PR5838 displayed envelope')

    return {
        'schema_version': 1,
        'claim': 'Finite certificate: under PR5838\'s completed-operation relative-error contract and causal bound, both PR5833 words accept a 20-bit guard; intermediate error stays below 0.978B and field norm plus error below 97B (budget word) and 3B (minimum word).',
        'unit': 'B, the bound on every initial field Hilbert norm; u = 2^-guard',
        'source_hashes': hashes,
        'words': results,
        'adapter_control': 'PR5830 word, every physical MOVE/ADD/SCALE a site: 20-bit causal case equals PR5838 RESULT.json causal_cases[guard=20] in every final coefficient, the peak value, its field and the 26271 defect sites. Only the peak instruction index differs, because PR5838 also numbers exact virtual identities.',
        'rejected_controls': controls(causal, transfer, words),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='regenerate RESULT.json')
    args = parser.parse_args()
    result = encode(calculate())
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    path = P / 'RESULT.json'
    if args.write:
        path.write_text(text)
    else:
        need(path.read_text() == text, 'committed RESULT.json matches recomputation')
    for name, r in result['words'].items():
        print(f"{name}: peak={r['ideal_peak']} guard={r['least_causal_guard']} "
              f"final<{float(F(r['final_public_bound'])):.6f}B inter<{float(F(r['intermediate_error_bound'])):.6f}B "
              f"norm+err<{float(F(r['field_norm_plus_error_bound'])):.4f}B")
    print('PASS_P104_GAUGE_WORD_ROUNDED_GUARDS')


if __name__ == '__main__':
    main()
