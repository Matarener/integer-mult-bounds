#!/usr/bin/env python3
"""Source-bound serial P104 review; successful execution is not promotion.

Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REVIEW = 'docs/research/pr-intake-evidence/pr5599'
PRIMARY = 'research/p104-helper-subspace-splits'
HEAD = '09dd0965711ca7eeb169057a420abab1c9052137'
KAPPA = Q('0.00310045')
CONTROL_SHA = 'b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def authenticate_export(work):
    export = read(ROOT / REVIEW / 'EXPORT.json')
    require(export['head'] == HEAD, 'Changed reviewed head')
    for folder, files in (
            ('source', export['files']),
            ('caller-source', read(ROOT / REVIEW / 'CALLER-EXPORT.json'))):
        for name, digest in files.items():
            require(sha256((work / folder / name).read_bytes()).hexdigest() == digest,
                    'Changed replay input: ' + name)


def validate(work):
    guards = {}
    for name in ('primary', 'control', 'candidate', 'optimized'):
        guard = read(work / 'review-evidence' / (name + '.json'))
        raw = (work / 'review-evidence' / (name + '.log')).read_bytes()
        require(guard['exit'] == 0 and guard['resource_stop'] is None,
                'Incomplete ' + name + ' run')
        require(sha256(raw).hexdigest() == guard['log_sha256'], 'Changed log')
        guards[name] = guard
    primary = (work / 'review-evidence/primary.log').read_bytes()
    require(primary == (work / 'review-evidence/optimized.log').read_bytes(),
            'Normal/optimized scientific outputs differ')
    require(b'PASS_P104_HELPER_SUBSPACE_KAPPA_00310045\n' in primary,
            'Missing complete primary marker')
    footer = json.loads(primary.splitlines()[-1])
    require(Q(footer['kappa']) == KAPPA and footer['productive_fields'] == 13048
            and footer['paid_calls'] == 66726, 'Wrong primary claim')
    control = (work / 'review-evidence/control.log').read_bytes()
    require(sha256(control).hexdigest() == CONTROL_SHA,
            'Independent caller adapter fails exact original positive control')
    candidate = read(work / 'review-evidence/candidate.log')
    require(candidate['status'] == 'PASS_SCOPED_CALLER_AND_TARGET_BINDING',
            'Incomplete independent caller')
    expected = read(work / 'source' / PRIMARY / 'RESULT.json')
    costs = expected['complete_cost']
    require(candidate['paid'] == costs['paid'] and candidate['targets'] == costs['targets'],
            'Independent invoice differs from primary')
    require(candidate['native_checks']['fresh_helpers'] == 9720
            and len(candidate['field_maps']) == 18
            and all(len(x['local_to_global']) == 748 for x in candidate['field_maps'])
            and len(candidate['controls']) == 10, 'Incomplete ownership/controls')
    require(candidate['ordinary']['abstract_address_phase_scalar_pass_upper']
            <= candidate['ordinary']['retained_raw_scalar_upper'], 'Unfunded ordinary passes')
    authenticate_export(work)
    result = dict(status='PASS_SOURCE_BOUND_P1045599_FINITE_REPLAYS',
                  source_head=HEAD, kappa=str(KAPPA), guards=guards,
                  original_caller_positive_control_sha256=CONTROL_SHA,
                  caller_summary={k:candidate[k] for k in ('native_checks','ordinary','controls')},
                  five_framework_assumptions_retained=True,
                  selected_frontier_changed=False,
                  scope='Finite implementation and numeric replays. Mathematical application review and selected-frontier publication are separate; no full uniform word or rounded multiplier is materialized.')
    (work / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    require(not sys.flags.optimize, 'Run the audit driver with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    work = args.work.resolve()
    if not args.validate_only:
        subprocess.run([sys.executable, '-I', '-B', str(ROOT / REVIEW / 'prepare.py'),
                        '--work', str(work)], check=True)
        env = dict(os.environ)
        for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'LEAN_AUDIT_BIN',
                    'P104_WORD', 'P104_RESULT'):
            env.pop(key, None)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        runs = [('primary', 3600, ['-I', 'source/' + PRIMARY + '/verify.py']),
                ('control', 1800, ['-I', 'run_caller.py', 'control']),
                ('candidate', 1800, ['-I', 'run_caller.py', 'candidate']),
                ('optimized', 3600, ['-I', '-O', 'source/' + PRIMARY + '/verify.py'])]
        for name, timeout, arguments in runs:
            print('START ' + name, flush=True)
            subprocess.run([sys.executable, '-I', '-B', str(work / 'run_bounded.py'),
                            name, str(timeout), *arguments], cwd=work, env=env, check=True)
    print(validate(work)['status'])


if __name__ == '__main__':
    main()
