"""Independent operation counts for an explicit common-width numeric reference.

This is not the recursive child tariff and does not price owner addressing.
No runtime inputs beyond caller-authenticated literal words are consumed.
"""
from collections import Counter
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def count(word):
    c = Counter()
    active = 0
    peak = 0
    for e in word:
        op = e[0]
        if op == 'add':
            alpha = abs(Q(e[3]))
            need(alpha in (Q(1), Q(1, 4)), 'unpriced scalar coefficient')
            c['unit_ADD' if alpha == 1 else 'quarter_ADD'] += 1
        elif op == 'clear':
            c['CLEAR'] += 1
        elif op == 'line':
            need(active == 0 and e[3] in (-1, 1), 'native scope/sign')
            c['H1'] += 1
            c['monomial_wrappers'] += 2
        elif op == 'map':
            need(active == 0, 'cover inside private scope')
            c['cover_maps'] += 1
        elif op == 'begin':
            need(active == 0 and e[2] in (8, 16), 'private begin')
            active = e[2]
            peak = max(peak, active)
        elif op == 'end':
            need(active == e[2], 'private end')
            active = 0
        elif op == 'checkpoint':
            pass
        else:
            raise ValueError('unknown opcode')
    need(active == 0, 'live private scope')
    c['private_peak'] = peak
    c['scalar_allowance'] = 8*c['unit_ADD'] + 12*c['quarter_ADD'] + 2*c['CLEAR']
    # Per complex payload coordinate; subtract and add have the same tariff.
    c['scalar_numeric_ops_per_N'] = 2*c['unit_ADD'] + 4*c['quarter_ADD'] + 2*c['CLEAR']
    c['wrapper_numeric_ops_per_N'] = 6*c['monomial_wrappers']
    c['cover_numeric_ops_per_N'] = 4*c['cover_maps']
    c['native_numeric_ops_per_lambda_N'] = 10*c['H1']
    c['numeric_constant_per_N'] = c['scalar_numeric_ops_per_N'] + c['wrapper_numeric_ops_per_N'] + c['cover_numeric_ops_per_N']
    return dict(sorted(c.items()))


def audit(baseline, candidate):
    b, c = count(baseline), count(candidate)
    for key in ('H1', 'monomial_wrappers', 'cover_maps', 'private_peak', 'quarter_ADD', 'CLEAR'):
        need(b[key] == c[key], 'changed common bill '+key)
    need((b['unit_ADD'], c['unit_ADD']) == (1920,1820), 'unit ADD invoice')
    need((b['scalar_allowance'],c['scalar_allowance']) == (26944,26144), 'logical invoice')
    need((b['numeric_constant_per_N'],c['numeric_constant_per_N']) == (12352,12152), 'numeric reference invoice')
    need(c['native_numeric_ops_per_lambda_N'] == 2240, 'native numeric reference invoice')
    return {
        'status': 'PASS_CONDITIONAL_COMMON_WIDTH_NUMERIC_REFERENCE_COMPARISON',
        'baseline': b, 'candidate': c,
        'N': '2^(73 lambda) complex payload coordinates per owner, lambda positive integer',
        'reference_lowering': {
            'unit_ADD': '2N real-component additions or subtractions',
            'quarter_ADD': '2N exact binary shifts by two (one W-bit shift primitive per component) plus 2N additions/subtractions',
            'CLEAR': '2N zero stores',
            'signed_H1': 'lambda coordinate Gaussian lines; each at most4N additions,2N exact halves,4N copies',
            'wrapper': '2N component sign operations plus2N outward copies and2N copies back to the fixed destination bank',
            'cover': '2N outward copies plus2N copies back to the fixed destination bank',
            'buffer_protocol': 'Two-leg out-of-place permutation returns to its fixed external bank; address/control work is outside numeric count.',
        },
        'numeric_bound_per_owner': {'baseline': '(12352+2240 lambda)N', 'candidate': '(12152+2240 lambda)N', 'difference': '200N numeric word operations'},
        'numeric_storage_bound': '(930N+12) signed W-bit component slots, including448 persistent complexfields,16 privatefields,one complex permutation buffer,and12 scalar native temporaries',
        'logical_allowance_difference': '800 allowance units; distinct from200N numeric operations',
        'common_width_tariff': 'For each reference primitive priced at any common positive tau(W), candidate prescribed bill is200N tau(W) smaller; logical allowance model separately gives800 tau_L(W). These are comparisons of prescribed bounds, not lower bounds on optimal implementations.',
        'width_mismatch_break_even': {
            'general': 'tau(W_candidate)/tau(W_baseline) < (12352+2240 lambda)/(12152+2240 lambda)',
            'linear_tau_W': 'Delta < 200 W_baseline/(12152+2240 lambda), forW_candidate=W_baseline+Delta',
            'logical_allowance_only': 'tau_L(W_candidate)/tau_L(W_baseline) < 26944/26144',
            'equal_width': 'Delta=0 satisfies bothstrictinequalities for everylambda>=1 andW>0',
        },
        'premises': ['Common sufficient range/grid certificate for every numerical reference interior.',
                     'Exact dyadic divisions and no overflow/underflow at the stated common W.',
                     'Pair-first coordinate Gaussian reference is permitted for this numerical bill; it is not inferred to implement a paid recursive child tariff.'],
        'unpriced': ['Owner/payload address generation and control', 'physical movement and placement tariffs',
                     'actual recursive native child error/width/cost contract', 'native workspace exclusivity in a recursive implementation',
                     'caller entry-format conversion', 'recursive usage and supplier caps'],
    }
