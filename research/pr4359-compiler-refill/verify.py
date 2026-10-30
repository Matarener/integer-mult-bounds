#!/usr/bin/env python3
"""Source-bound exact checks for two conditional refinements of PR4359.

Apache-2.0. Substantial OpenAI Codex assistance. See README.md for attribution.
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


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def verify():
    manifest = json.loads((HERE / 'EXPORTED-SOURCES.json').read_text())
    need(manifest['head'] == 'da637c87c89482bc4c86be36bd0071b3d400dbed', 'Pinned source head')
    seen = set()
    for row in manifest['files']:
        name = row['path']
        rel = PurePosixPath(name)
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == name,
             'Canonical source path')
        need(name not in seen, 'Unique source path')
        seen.add(name)
        path = HERE
        for part in rel.parts:
            path /= part
            need(not path.is_symlink(), 'No source aliases')
        data = path.read_bytes()
        need(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'],
             'Exact source bytes: ' + name)
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == row['git_blob'], 'Exact source Git blob: ' + name)

    bound, endpoint = module('template_bound'), module('endpoint')
    source = HERE / 'source/research/kappa-rebuild'
    old = json.loads((source / 'controller/EXPLICIT-TEMPLATE-BOUNDS.json').read_text())
    for case, frozen in zip(bound.CASES, old['cases'], strict=True):
        need(case['family'] == frozen['family'], 'Same source family')
        for key in ('targets', 'paid'):
            need(case[key] == {int(k): v for k, v in frozen[key].items()}, 'Same ' + key)
        for key, old_key in [('tested_saving', 'tested_mixed_saving'),
                             ('uniform_saving', 'uniform_saving'), ('theta_upper', 'theta_upper')]:
            need(Q(case[key]) == Q(frozen[old_key]), 'Same ' + key)
        need(case['old_H0'] == frozen['n0']['H0'] and case['old_H1'] == frozen['N']['H1'],
             'Same original specified ranks')
    templates = bound.verify()
    refill = endpoint.run(HERE / 'source')
    case = bound.CASES[0]
    margin = bound.moment_margin(case['targets'], case['paid'], endpoint.TESTED)
    need(margin[0] > 0, 'Independent new strict mixed test')
    lower = Q('0.002305090194876170622919094755')
    upper = Q('0.002305090194876170622919094756')
    need(bound.moment_margin(case['targets'], case['paid'], lower)[0] > 0,
         'Independent lower root bracket')
    need(bound.moment_margin(case['targets'], case['paid'], upper)[1] < 0,
         'Independent upper root bracket')
    p = endpoint.family(endpoint.KAPPA, endpoint.TESTED)
    sharper = bound.rank_bound(endpoint.TESTED, p['complex_uniform_saving'], 57, Q(9, 10))
    need(sharper['H1'] < refill['compiler']['H1'], 'Sharper new-endpoint rank')
    bit = json.loads((source / 'bit/BIT-ALLSIZE-PARAMETERS.json').read_text())
    need(p['bit_saving'] == Q(bit['ordinary_saving_admitted']), 'Unchanged admitted BIT saving')
    return {'status': 'PASS_PR4359_CONDITIONAL_COMPILER_REFINEMENTS',
            'source_head': manifest['head'], 'source_files': len(seen),
            'template_refinement': templates, 'endpoint_refill': refill,
            'new_endpoint_sharper_rank': sharper,
            'independent_mixed_root_bracket': [str(lower), str(upper)],
            'scope': 'Conditional quantitative improvements. No selected frontier change, materialized winning word, or unconditional multiplication theorem.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = verify()
    expected = HERE / 'RESULT.json'
    if args.write_result:
        expected.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(expected.read_text()) == json.loads(json.dumps(result)),
             'Exact saved receipt reproduction')
    print(json.dumps({'status': result['status'], 'source_files': result['source_files'],
                      'kappa': result['endpoint_refill']['kappa'],
                      'old_savings_template_H1': [r['H1'] for r in result['template_refinement']['cases']],
                      'new_endpoint_template_H1': result['new_endpoint_sharper_rank']['H1']}))
