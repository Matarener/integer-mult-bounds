#!/usr/bin/env python3
"""Authenticate and verify the conditional p7 native tensor and paid-target-padding construction.

Apache-2.0. Substantial OpenAI Codex assistance; source notices are retained.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def verify():
    manifest = json.loads((HERE / 'EXPORTED-SOURCES.json').read_text())
    seen = set()
    for row in manifest['files']:
        rel = PurePosixPath(row['path'])
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == row['path'],
             'Canonical source path')
        need(row['path'] not in seen, 'Unique source path')
        seen.add(row['path'])
        path = HERE
        for part in rel.parts:
            path /= part
            need(not path.is_symlink(), 'No source aliases')
        data = path.read_bytes()
        need(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'],
             'Exact exported source bytes: ' + row['path'])
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == row['git_blob'], 'Exact original Git blob')

    source = HERE / 'source'
    S = module('strictification', HERE / 'strictification.py')
    E = module('endpoint', HERE / 'endpoint.py')
    independent = module('independent_intervals', HERE / 'dependencies/compiler-refill/template_bound.py')
    strict = S.run(source)
    endpoint = E.run(source, strict)
    targets, paid = strict['targets'], strict['paid']
    saving = Q(strict['tested_saving'])
    tlo, thi = independent.moment_margin(targets, {}, saving)
    plo, phi = independent.moment_margin(paid, {}, saving)
    need(phi / tlo < Q(strict['alpha_upper']), 'Independent paid/target moment ratio')
    cutoff = Q(strict['cutoff_base'])
    loglo, loghi = independent.log_interval(cutoff)
    base_power_lo = independent.exp_interval(saving * loglo)[0]
    paid_mass = sum(k * v for k, v in paid.items())
    need(Q(paid_mass) / (base_power_lo * tlo) < Q(strict['gamma_upper']),
         'Independent original paid rank-one tail ratio')
    productive_count = sum(targets.values())
    need(Q(productive_count * strict['target_floor_base']) / (base_power_lo * tlo)
         < Q(strict['delta_upper']), 'Independent complete productive-padding tail ratio')
    n = strict['exponent']
    block = strict['decay_block_length']
    need(n % block == 0 and Q(strict['gamma_upper']) ** block < Q(1, 2),
         'Independent exact rational block decay')
    need(Q(strict['delta_upper']) ** block < Q(1, 2),
         'Independent complete padding tail block decay')
    upper = 1 / (1 + n * (1 - Q(strict['alpha_upper']))) + Q(4, 2 ** (n // block))
    need(upper == Q(strict['normalized_moment_upper_rational']), 'Exact charged-padding and cutoff bound')
    need(upper < 1, 'Independent complete strictified moment')
    need(cutoff < strict['target_floor_base'] < max(targets),
         'Completed target ranks exceed paid cutoff and fit the ambient rank')
    bit = json.loads((source / 'research/kappa-rebuild/bit/BIT-ALLSIZE-PARAMETERS.json').read_text())
    need(Q(endpoint['outer']['parameters']['bit_saving']) == Q(bit['ordinary_saving_admitted']),
         'Unchanged admitted ordinary BIT saving')
    return {'status': 'PASS_SOURCE_BOUND_CONDITIONAL_P7_PAID_PADDING_IMPROVEMENT',
            'source_files': len(seen), 'strictification': strict, 'endpoint': endpoint,
            'independent_interval_crosscheck': True,
            'scope': 'Conditional native construction and exact finite arithmetic. The finite word and inherited physical, precision, analytic and fixed-tape proofs are not formally verified or materialized by this checker.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = verify()
    normalized = json.loads(json.dumps(result))
    receipt = HERE / 'RESULT.json'
    if args.write_result:
        receipt.write_text(json.dumps(normalized, indent=2, sort_keys=True) + '\n')
    else:
        need(normalized == json.loads(receipt.read_text()), 'Exact saved certificate reproduction')
    print(json.dumps({'status': result['status'], 'kappa': result['endpoint']['kappa'],
                      'mixed_saving': result['strictification']['tested_saving'],
                      'tensor_power': result['strictification']['exponent'],
                      'uniform_rank_exponent': result['endpoint']['compiler']['H1']}))
