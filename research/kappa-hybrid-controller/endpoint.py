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
DEFAULT_SOURCE = HERE.parent/'pr4359-p7-padding/source'
DEFAULT_BIT_SOURCE = HERE.parents[1]
_parameter_spec = importlib.util.spec_from_file_location('hybrid_parameters_endpoint', HERE/'parameters.py')
PARAMETERS = importlib.util.module_from_spec(_parameter_spec)
_parameter_spec.loader.exec_module(PARAMETERS)
KAPPA = PARAMETERS.KAPPA
TESTED = PARAMETERS.TESTED_SAVING
BIT_SCRIPT_SHA256 = '9993c4b695740d41f56bfac0f4d016e7c62c6fef692fc09b0c01b6d67da7da7c'
LEDGER_SHA256 = 'd097e55f06c3f244f2074ffd7c1a0a5f3c4b4b6a6accf9619d1dde5c0ae85e15' 


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
    """Explicit sufficient ambient rank for the audited cutoff, floor and ambient."""
    n = exponent
    t, z = 1-tested, 1-uniform
    z0, h = (t+z)/2, Q(1, PARAMETERS.THETA_DENOMINATOR)
    cutoff, floor, ambient = PARAMETERS.CUTOFF, PARAMETERS.TARGET_FLOOR, PARAMETERS.AMBIENT
    cutoff_log, ambient_log = PARAMETERS.CUTOFF_LOG2_UPPER, PARAMETERS.AMBIENT_LOG2_UPPER
    delta = z0-t
    need(n >= 1 and Q(1, 2) < t < z0 < z < 1, 'Strict compiler exponents')
    need(cutoff**PARAMETERS.THETA_DENOMINATOR < floor**(PARAMETERS.THETA_DENOMINATOR-1),
         'Strict source-bound logarithmic cutoff/floor separation')
    need(cutoff < 2**cutoff_log and ambient < 2**ambient_log, 'Exact power bounds for exit and complement')
    # With r_max=cutoff^n, k_min=floor^n, m=ambient^n, m*E(x)/x
    # is below 2^B*x^-h. All inactive carrier axes remain included.
    B = (cutoff_log+ambient_log*h)*n
    debt = 1+ambient_log*n*(1-z0)
    ratio = (delta*B+debt)/(h*delta)
    H0 = -((-ratio.numerator)//ratio.denominator)
    need(H0 >= ambient_log*n, 'Initial threshold covers every base rank below m')
    need(H0*h*delta >= delta*B+debt, 'Exact sufficient exit/complement inequality')
    final_ratio = H0*(1-z0)/(z-z0)
    H1 = final_ratio.numerator//final_ratio.denominator+1
    need(H1 > H0 and H1*(z-z0) > H0*(1-z0), 'Strict final uniform moment')
    need((H0-1)*h*delta < delta*B+debt, 'One lower H0 fails the stated sufficient bound')
    need((H1-1)*(z-z0) <= H0*(1-z0), 'One lower H1 fails the final strict bound')
    return {'tensor_power': n, 'target_min_encoding': str(floor)+'^'+str(n),
            'target_max_encoding': str(max(PARAMETERS.TARGETS))+'^'+str(n),
            'ambient_rank_encoding': str(ambient)+'^'+str(n),
            'paid_max_bound_encoding': str(cutoff)+'^'+str(n),
            'theta_upper': 1-h, 'h': h, 't': t, 'z0': z0, 'z': z,
            'delta': delta, 'exit_coefficient_log2_upper': B,
            'negative_log2_eta_upper': debt, 'H0': H0, 'H1': H1,
            'N_encoding': '2^'+str(H1),
            'final_strict_power_gap': H1*(z-z0)-H0*(1-z0),
            'rank_one_induction': str(PARAMETERS.TARGET_MASS)+'^n > '+str(PARAMETERS.PAID_MASS)+'^n; target padding adds equal paid and target rank, and splitting preserves rank',
            'materialized_tensor_rule_or_uniform_word': False}


def bit_certificate(source_root=DEFAULT_BIT_SOURCE):
    script = HERE/'bit/bit_p6_tensor_extension.py'
    need(sha256(script.read_bytes()).hexdigest() == BIT_SCRIPT_SHA256, 'Exact BIT tensor/native validator')
    B = module('hybrid_bit_p6_tensor', script)
    result = encode(B.run(Path(source_root).resolve()))
    need(result == json.loads((HERE/'bit/BIT-P6-TENSOR-RESULT.json').read_text()),
         'Exact ordinary BIT certificate reproduction including native replay')
    need(Q(result['admitted_BIT_saving']) == PARAMETERS.BIT_SAVING, 'Admitted ordinary BIT saving')
    return result


def run(source_root=DEFAULT_SOURCE, strict_result=None, bit_source_root=DEFAULT_BIT_SOURCE, bit_result=None, retimed_source_root=None):
    if strict_result is None:
        strict_result = module('tensor_strictification', HERE/'strictification.py').run(source_root,retimed_source_root=retimed_source_root)
    need(strict_result['strict_moment_verified'], 'Strict mixed moment was certified')
    need(strict_result['cutoff_base'] == PARAMETERS.CUTOFF and strict_result['target_floor_base'] == PARAMETERS.TARGET_FLOOR
         and Q(strict_result['tested_saving']) == TESTED,
         'Compiler inputs bind to the certified cutoff and saving')
    ledger_path = Path(source_root).resolve().parent/'dependencies/compiler-refill/endpoint.py'
    need(sha256(ledger_path.read_bytes()).hexdigest() == LEDGER_SHA256, 'Exact inherited outer ledger')
    if bit_result is None:
        bit_result = bit_certificate(bit_source_root)
    need(bit_result['native_source']['status'] == 'PASS_P6_EXACT_NATIVE_PORTS_ARBITRARY_COLUMNS_AND_WHOLE_IDLES', 'BIT native gate')
    need(Q(bit_result['admitted_BIT_saving']) == PARAMETERS.BIT_SAVING, 'BIT ordinary saving matches parameter table')
    previous = module('pr4405_outer_ledger', ledger_path)
    d = (TESTED-KAPPA)/7
    p = {'kappa': KAPPA, 'tested_saving': TESTED,
         'complex_uniform_saving': KAPPA+6*d, 'b': KAPPA+5*d,
         'a': KAPPA+4*d, 'q': KAPPA+3*d, 'bit_saving': Q(bit_result['admitted_BIT_saving']),
         'epsilon': 1-d, 'beta': 1-3*d, 'r0': d/10,
         'stop': d, 'layout': d, 'd': d}
    outer = previous.ledger(p)
    need(len(outer['functional_checks']) == 3, 'Preserve the three inherited functional checks')
    outer['functional_checks']['actual_new_BIT_stock_sublinear'] = p['beta']*(1-Q(bit_result['ordinary']['atom_power']))
    need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 4,
         'Complete preserved outer predicate set')
    need(all(v > 0 for v in outer['strict_checks'].values()), 'All 54 strict outer predicates')
    need(all(v > 0 for v in outer['functional_checks'].values()), 'All four functional predicates, including the actual new BIT atom')
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
    return encode({'schema': 'hybrid-p17-padding-outer-endpoint/1',
                   'status': 'PASS_CONDITIONAL_HYBRID_P17_OUTER_POINT', 'kappa': KAPPA,
                   'gain_over_PR4359': KAPPA-Q('0.0023'),
                   'gain_over_PR4405': KAPPA-Q('0.00230509'),
                   'gain_over_allfresh_p3': KAPPA-Q('0.00247755'),
                   'gain_over_PR4414': KAPPA-Q('0.00267987'),
                   'gain_over_PR4416': KAPPA-Q('0.00268647'),
                   'tested_saving': TESTED, 'outer': outer, 'compiler': rank,
                   'ordinary_BIT_certificate': bit_result,
                   'BIT_validator_sha256': BIT_SCRIPT_SHA256,
                   'parameters_sha256': sha256((HERE/'parameters.py').read_bytes()).hexdigest(),
                   'minimum_outer_margin': min(outer['margins'].values())-KAPPA,
                   'negative_controls': controls,
                   'ledger_source_sha256': sha256(ledger_path.read_bytes()).hexdigest(),
                   'strictification_source_sha256': sha256((HERE/'strictification.py').read_bytes()).hexdigest(),
                   'scope': 'Source-bound PR4441 retimed arbitrary-input local word, p17 native/direct geometry, a finite tensor recipe with target padding, exact moment and outer inequalities, and a specified finite uniform rank. Native tensor closure and the PR4359 inherited precision, storage, analytic, fixed-tape and recovery hypotheses are written premises, not a full formal theorem certificate.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--bit-source-root', type=Path, default=DEFAULT_BIT_SOURCE)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--retimed-source-root', type=Path)
    args = parser.parse_args()
    result = run(args.source_root, bit_source_root=args.bit_source_root,retimed_source_root=args.retimed_source_root)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({key: result[key] for key in
                      ('status', 'kappa', 'gain_over_PR4359', 'minimum_outer_margin', 'compiler')}, sort_keys=True))
