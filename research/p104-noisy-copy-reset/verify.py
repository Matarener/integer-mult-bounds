#!/usr/bin/env python3
"""Replay the declared completed-operation precision contract."""
from fractions import Fraction as F
from hashlib import sha256
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for row in json.loads((P / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            data = (P.parent.parent / row['path']).read_bytes()
            need(sha256(data).hexdigest() == row['sha256'], 'source hash')
    original = (P / 'inputs/prior-analysis.py').read_text()
    for before, after in json.loads((P / 'PRECISION-EDITS.json').read_text()):
        need(original.count(before) == 1, 'unique declared edit')
        original = original.replace(before, after)
    need(original == (P / 'precision.py').read_text(), 'declared edit bytes')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def guards(J, K, scores):
    # A strict inequality gives error less than B at t=0, and less than
    # B*2^-t when each unit roundoff has t more bits.
    prefix = next(g for g in range(100) if J + K < 2**g)
    def valid(g):
        u = F(1, 2**g)
        return u*K < 1 and all(u*(a+b*u*J/(1-u*K)) < 1 for a,b,_ in scores)
    final = next(g for g in range(100) if valid(g))
    need(not valid(final-1), 'previous final guard must fail this formula')
    return dict(prefix=prefix, final=final)


def rejection(label, action):
    try:
        action()
    except (ValueError, AssertionError):
        return label
    raise ValueError('accepted negative control: ' + label)


def calculate():
    authenticate()
    a = module('noisy_precision', P / 'precision.py')
    word = json.loads(gzip.decompress((P / 'inputs/WORD.json.gz').read_bytes()))
    source = json.loads((P / 'inputs/caller-RESULT.json').read_text())
    need(a.digest(word) == source['canonical_word_sha256'], 'caller word binding')
    ideal, weights = a.ideal(word)
    rounded = set(ideal['counts'])
    trace, witnesses = a.error_trace(word, weights, rounded)
    scores, hashes = a.reverse_all(word, weights, rounded)
    need(scores == trace['final_scores'], 'all final transpose scores')
    need(hashes == trace['final_coefficient_hashes'], 'all final signed coefficients')
    for k, peak in enumerate(trace['peaks']):
        _, row = a.reverse_cut(word, rounded, peak['cut'], peak['role'])
        need(row == witnesses[k], 'prefix signed transpose')
        errors = {j:(1 if v > 0 else -1) for j,v in row.items()}
        value = a.execute(word, {}, errors, peak['cut'])[peak['role']]
        need(value == sum(map(abs, row.values()), F(0)), 'literal aligned defects')
        if k == 2:
            need(value == peak['value'], 'attained independent defect gain')
    peak = ideal['input_peak']
    initial = {r:(1 if v > 0 else -1) for r,v in peak['row'].items()}
    need(a.execute(word, initial, {}, peak['cut'])[peak['role']] == peak['value'],
         'attained input gain')
    J,K = [v['value'] for v in trace['peaks'][:2]]
    public = word['public']
    gp = guards(J,K,scores[:public])
    go = guards(J,K,scores[public:])
    need(gp['prefix'] == go['prefix'], 'one uniform prefix guard')

    # A reset residual at the destination survives the next additive COPY.
    j = next(i for i,e in enumerate(word['program']) if e[0] == 'COPY')
    r = word['program'][j][1]
    reset = max(i for i,e in enumerate(word['program'][:j]) if e[1] == r)
    need(word['program'][reset][0] == 'INIT', 'copy fixture starts at reset')
    actual = a.execute(word, {}, {reset:F(1)}, j+1)[r]
    prior = module('prior_precision', P / 'inputs/prior-analysis.py')
    overwrite = prior.execute(word, {}, {reset:F(1)}, j+1)[r]
    need(actual == 1 and overwrite == 0, 'overwrite extension loses reset residual')
    _, error_row = a.reverse_cut(word, rounded, j+1, r)
    need(error_row[reset] == 1, 'transpose retains reset residual')

    controls = []
    bad = copy.deepcopy(word)
    bad['program'].insert(j, ['ADD', r, word['program'][j][2], 1, word['program'][j][-1]])
    controls.append(rejection('nonzero ideal COPY destination', lambda:a.ideal(bad)))
    bad = copy.deepcopy(word)
    bad['program'][j][-2] = '1/3'
    controls.append(rejection('nondyadic COPY scalar', lambda:a.ideal(bad)))
    bad = copy.deepcopy(word)
    bad['program'][j][2] = r
    controls.append(rejection('self COPY', lambda:a.ideal(bad)))
    controls.append(rejection('overwrite extension to residual reset',
                               lambda:need(actual == overwrite, 'residual omitted')))
    last_clear = max(i for i,e in enumerate(word['program']) if e[0] == 'CLEAR')
    owned_role = word['program'][last_clear][1]
    residual = a.execute(word, {}, {last_clear:F(1)}, len(word['program']))[owned_role]
    need(residual == 1, 'final reset residual fixture')
    controls.append(rejection('exact owned zero from bounded residual',
                               lambda:need(residual == 0, 'owned residual')))
    g = gp['prefix']
    controls.append(rejection('one fewer uniform guard bit', lambda:need(J+K < 2**(g-1), 'guard')))
    public_peak = [max((scores[r][k],r) for r in range(public)) for k in range(3)]
    owned_peak = [max((scores[r][k],r) for r in range(public,len(scores))) for k in range(3)]
    return a.encode(dict(
        source_pr=5811, source_head='33d7760d0a6fea6394aefd014eea68f0af02a92e',
        contract='Additive COPY; bounded reset residual; all completed operations have defects',
        ideal=ideal, weights_sha256=a.digest(weights), trace=trace,
        public_final_peaks=public_peak, owned_final_peaks=owned_peak,
        sufficient_guard_bits=dict(prefix=gp['prefix'], public=gp['final'], owned=go['final']),
        copy_residual_control=dict(reset=reset, copy=j, role=r, additive=actual, overwrite=overwrite),
        rejected_controls=controls,
        limits=['Unitary decoded native maps remain a premise.',
                'This contract does not prove exact owned zero return.',
                'No implementation or fee for a residual reset is supplied.',
                'The guards are sufficient for this formula, not optimal physical precision.',
                'No kappa or selected frontier change.']))


if __name__ == '__main__':
    result = calculate()
    if sys.argv[1:] == ['--write']:
        (P / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(not sys.argv[1:], 'unknown argument')
        need(result == json.loads((P / 'RESULT.json').read_text()), 'recorded result')
    print('PASS_P104_ADDITIVE_COPY_RESET_PRECISION')
    print(json.dumps({'events':result['ideal']['events'], 'guard_bits':result['sufficient_guard_bits'],
                      'controls':len(result['rejected_controls'])}, sort_keys=True))
