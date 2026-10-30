#!/usr/bin/env python3
"""Conditional outer endpoint from the source-bound tensor strictification.

Apache-2.0. Substantial OpenAI assistance. The native productive rule is zxv's
PR4359. Integer mixed flow is Jacob Alan Sussman's Theorem 1G. The outer ledger
is frozen from PR4405 and retains the predecessor attribution stated there.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
KAPPA = Q('0.00247755')
TESTED = Q('0.00247756')


def need(value, message):
    if not value:
        raise AssertionError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def compiler_rank(exponent, tested, uniform):
    """Explicit sufficient ambient rank after cutoff at 4^exponent."""
    n = exponent
    t, z = 1-tested, 1-uniform
    z0, h = (t+z)/2, Q(1, 8)
    delta = z0-t
    need(n >= 1 and Q(1, 2) < t < z0 < z < 1, 'Strict compiler exponents')
    need(4**8 < 5**7, 'log(4)/log(5) < 7/8')
    need(4 == 2**2 and 57 < 2**6, 'Exact power bounds for exit and complement')
    # r_max=4^n, k_min=5^n, m=57^n. Thus m*E(x)/x is strictly
    # below 2^B*x^-h, with B=(2+6h)n. Also -log2(eta)<1+6n(1-z0).
    B = (2+6*h)*n
    debt = 1+6*n*(1-z0)
    ratio = (delta*B+debt)/(h*delta)
    H0 = -((-ratio.numerator)//ratio.denominator)
    need(H0 >= 6*n, 'Initial threshold covers every base rank below m')
    need(H0*h*delta >= delta*B+debt, 'Exact sufficient exit/complement inequality')
    final_ratio = H0*(1-z0)/(z-z0)
    H1 = final_ratio.numerator//final_ratio.denominator+1
    need(H1 > H0 and H1*(z-z0) > H0*(1-z0), 'Strict final uniform moment')
    need((H0-1)*h*delta < delta*B+debt, 'One lower H0 fails the stated sufficient bound')
    need((H1-1)*(z-z0) <= H0*(1-z0), 'One lower H1 fails the final strict bound')
    return {'tensor_power': n, 'target_min_encoding': '5^'+str(n),
            'target_max_encoding': '57^'+str(n), 'paid_max_bound_encoding': '4^'+str(n),
            'theta_upper': Q(7, 8), 'h': h, 't': t, 'z0': z0, 'z': z,
            'delta': delta, 'exit_coefficient_log2_upper': B,
            'negative_log2_eta_upper': debt, 'H0': H0, 'H1': H1,
            'N_encoding': '2^'+str(H1),
            'final_strict_power_gap': H1*(z-z0)-H0*(1-z0),
            'rank_one_induction': '47075^n > 46851^n, and splitting preserves total rank',
            'materialized_tensor_rule_or_uniform_word': False}


def run(source_root, strict_result=None):
    if strict_result is None:
        strict_result = module('tensor_strictification', HERE/'strictification.py').run(source_root)
    need(strict_result['strict_moment_verified'], 'Strict mixed moment was certified')
    need(strict_result['cutoff_base'] == 4 and Q(strict_result['tested_saving']) == TESTED,
         'Compiler inputs bind to the certified cutoff and saving')
    ledger_path = HERE/'dependencies/compiler-refill/endpoint.py'
    previous = module('pr4405_outer_ledger', ledger_path)
    d = (TESTED-KAPPA)/7
    p = {'kappa': KAPPA, 'tested_saving': TESTED,
         'complex_uniform_saving': KAPPA+6*d, 'b': KAPPA+5*d,
         'a': KAPPA+4*d, 'q': KAPPA+3*d, 'bit_saving': Q('0.0027'),
         'epsilon': 1-d, 'beta': 1-3*d, 'r0': d/10,
         'stop': d, 'layout': d, 'd': d}
    outer = previous.ledger(p)
    need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 3,
         'Complete preserved outer predicate set')
    need(all(v > 0 for v in outer['strict_checks'].values()), 'All 54 strict outer predicates')
    need(all(v > 0 for v in outer['functional_checks'].values()), 'All three functional predicates')
    need(min(outer['margins'].values()) == outer['margins']['main_transform'],
         'Main transform remains limiting')
    controls = {}
    for label, updates in [('closed_epsilon', {'epsilon': Q(1)}),
                           ('closed_uniform_gap', {'complex_uniform_saving': p['b']}),
                           ('unfunded_outer_point', {'kappa': TESTED}),
                           ('insufficient_BIT', {'bit_saving': Q('0.0023')})]:
        tested = previous.ledger(dict(p, **updates))
        failed = {k: v for k, v in tested['strict_checks'].items() if v <= 0}
        need(failed, 'Reject '+label)
        controls[label] = failed
    rank = compiler_rank(strict_result['exponent'], TESTED, p['complex_uniform_saving'])
    return encode({'schema': 'native-tensor-strictification-outer-endpoint/1',
                   'status': 'PASS_CONDITIONAL_TENSOR_OUTER_POINT', 'kappa': KAPPA,
                   'gain_over_PR4359': KAPPA-Q('0.0023'),
                   'gain_over_PR4405': KAPPA-Q('0.00230509'),
                   'tested_saving': TESTED, 'outer': outer, 'compiler': rank,
                   'minimum_outer_margin': min(outer['margins'].values())-KAPPA,
                   'negative_controls': controls,
                   'ledger_source_sha256': sha256(ledger_path.read_bytes()).hexdigest(),
                   'strictification_source_sha256': sha256((HERE/'strictification.py').read_bytes()).hexdigest(),
                   'scope': 'Source-bound native edits, a finite tensor recipe, exact moment and outer inequalities, and a specified finite uniform rank. Native tensor closure and the PR4359 inherited precision, storage, analytic, fixed-tape and recovery hypotheses are written premises, not a full formal theorem certificate.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=HERE/'source')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = run(args.source_root)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({key: result[key] for key in
                      ('status', 'kappa', 'gain_over_PR4359', 'minimum_outer_margin', 'compiler')}, sort_keys=True))
