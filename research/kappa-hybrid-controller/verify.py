#!/usr/bin/env python3
"""Regenerate the complete conditional native/direct p17 and p6 BIT certificates."""
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


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(source_root=DEFAULT_SOURCE, bit_source_root=DEFAULT_BIT_SOURCE, retimed_source_root=None):
    source_root = Path(source_root).resolve()
    strictifier = load(HERE/'strictification.py', 'hybrid_p17_strict_verify')
    endpoint_module = load(HERE/'endpoint.py', 'hybrid_p17_endpoint_verify')
    strict = strictifier.run(source_root,retimed_source_root=retimed_source_root)
    endpoint = endpoint_module.run(source_root, strict, bit_source_root)
    independent_path = source_root.parent/'dependencies/compiler-refill/template_bound.py'
    need(sha256(independent_path.read_bytes()).hexdigest() ==
         '25d409726cd867f7584fbd52e1b846335debdab42d24377e00c5653aaf12c0fb',
         'Exact independently implemented interval engine')
    independent = load(independent_path, 'hybrid_p17_independent_interval')
    targets, paid = strict['targets'], strict['paid']
    saving = Q(strict['tested_saving'])
    tlo, thi = independent.moment_margin(targets, {}, saving)
    plo, phi = independent.moment_margin(paid, {}, saving)
    need(phi/tlo < Q(strict['alpha_upper']), 'Independent strict raw mixed moment')
    loglo, loghi = independent.log_interval(strict['cutoff_base'])
    power_lo = independent.exp_interval(saving*loglo)[0]
    paid_mass = sum(k*v for k,v in paid.items())
    need(paid_mass/(power_lo*tlo) < Q(strict['gamma_upper']),
         'Independent full original paid-tail charge')
    need(sum(targets.values())*strict['target_floor_base']/(power_lo*tlo) < Q(strict['delta_upper']),
         'Independent paid completion and split-tail charge')
    n, block = strict['exponent'], strict['decay_block_length']
    need(n % block == 0 and Q(strict['gamma_upper'])**block < Q(1,2),
         'Exact original paid-tail decay blocks')
    need(Q(strict['delta_upper'])**block < Q(1,2), 'Exact completion-tail decay blocks')
    upper = 1/(1+n*(1-Q(strict['alpha_upper'])))+Q(4,2**(n//block))
    need(upper == Q(strict['normalized_moment_upper_rational']) < 1,
         'Independent complete padded and split moment')
    bit = endpoint['ordinary_BIT_certificate']
    need(bit['native_source']['status'] == 'PASS_P6_EXACT_NATIVE_PORTS_ARBITRARY_COLUMNS_AND_WHOLE_IDLES',
         'Native BIT arbitrary-input certificate included')
    need(Q(bit['admitted_BIT_saving']) == Q(endpoint['outer']['parameters']['bit_saving']),
         'Outer BIT premise is exactly the newly certified ordinary saving')
    source_files = {str(path.relative_to(HERE)):sha256(path.read_bytes()).hexdigest()
                    for path in (HERE/'parameters.py', HERE/'native_inventory.py', HERE/'native_geometry.py',
                                 HERE/'local_supplier.py', HERE/'controller/make_direct_case.py',
                                 HERE/'strictification.py', HERE/'endpoint.py', HERE/'verify.py',
                                 HERE/'bit/bit_tensor_extension.py', HERE/'bit/bit_p6_tensor_extension.py')}
    return dict(schema='hybrid-p17-complete-conditional-certificate/1',
                status='PASS_SOURCE_BOUND_HYBRID_P17_AND_ORDINARY_BIT_P6',
                strictification=strict, endpoint=endpoint,
                independent_interval_crosscheck=True,
                implementation_sha256=source_files,
                scope='Fresh finite retimed native replay, all helper phases, full native/direct p17 geometry, two independent interval engines, explicit uniform ranks, native BIT and all outer inequalities. All-column tensor, route-cost, precision, stock, analytic, fixed-tape and recovery assumptions remain the inherited written premises.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--bit-source-root', type=Path, default=DEFAULT_BIT_SOURCE)
    parser.add_argument('--write-result', action='store_true')
    parser.add_argument('--retimed-source-root', type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(run(args.source_root, args.bit_source_root,args.retimed_source_root)))
    path = HERE/'RESULT.json'
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        certificates = HERE/'certificates'
        certificates.mkdir(exist_ok=True)
        for name, value in (('NATIVE',result['strictification']['native_inventory']),
                            ('STRICTIFICATION',result['strictification']),
                            ('ENDPOINT',result['endpoint'])):
            (certificates/(name+'.json')).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads(path.read_text()), 'Exact complete saved receipt reproduction')
    print(json.dumps(dict(status=result['status'], kappa=result['endpoint']['kappa'],
                          tested_saving=result['strictification']['tested_saving'],
                          ordinary_BIT=result['endpoint']['ordinary_BIT_certificate']['admitted_BIT_saving'],
                          tensor_power=result['strictification']['exponent'],
                          uniform_rank_exponent=result['endpoint']['compiler']['H1']), sort_keys=True))
