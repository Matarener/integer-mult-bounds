#!/usr/bin/env python3
"""Bind and replay the conditional P104 twin-rung selection.

Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = 'research/p104-helper470-twin-rung-removal'
KAPPA = Q('0.003125804')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    return json.loads((ROOT / name).read_bytes())


def claim_from_sources(result, previous):
    costs = result['complete_cost']
    bit = costs['ordinary_BIT']
    atom = Q(bit['atom'])
    ordinary = (1-atom)*Q(bit['after_cover']) + atom*Q('.0000384599')
    margins = {k:Q(v) for k,v in costs['outer']['margins'].items()}
    claim = dict(previous)
    claim.update(kappa=str(Q(costs['kappa'])), source_result=PRIMARY+'/RESULT.json',
                 uniform_templates=[{'family':'complex',
                                     'rank_encoding':'2^'+str(costs['compiler']['H']),
                                     'saving':costs['compiler']['uniform_saving']},
                                    previous['uniform_templates'][1]],
                 ordinary_BIT_saving=str(ordinary), admitted_BIT_saving=bit['admitted'],
                 nine_outer_savings={k:str(v) for k,v in margins.items()},
                 limiting_outer_saving=str(min(margins.values())),
                 strict_limiting_slack=str(min(margins.values())-Q(costs['kappa'])),
                 scope='Conditional P104 helper-470 rung removal on the cumulative P104 construction and all-forward productive caller. The five inherited framework assumptions remain; no materialized uniform word or complete rounded multiplier.')
    return claim


def authenticate():
    checker = runpy.run_path(str(ROOT/'scripts/verify_selected_result.py'))
    record = read('certificates/selected-result.json')
    require(record['audited_source_head'] == '772dd10a5859a1d15f4851feb371519789213ad8',
            'Use the replay for the current selected record')
    checker['check'](record, ROOT)
    require(Q(record['kappa']) == KAPPA, 'Different selected kappa')
    require(record['assumptions'] == read('certificates/checkpoints/frontier5599.json')['assumptions'],
            'Changed inherited assumptions')
    require(read(record['certificate']) == claim_from_sources(read(PRIMARY+'/RESULT.json'),
                                                             read('certificates/frontier5599/CLAIM.json')),
            'Selected claim differs from complete source invoice')
    return record


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled for the driver')
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check-only', action='store_true')
    modes.add_argument('--work', type=Path)
    modes.add_argument('--validate-replay', type=Path,
                       help='Validate an existing exact export and its complete receipts; no new replay')
    args = parser.parse_args()
    authenticate()
    if args.check_only:
        print('PASS_FRONTIER6030_BINDINGS_ONLY (not a scientific replay)')
        return
    work = args.validate_replay or args.work
    command = [sys.executable, '-I', '-B', str(ROOT/'scripts/audit_p1046030.py'),
               '--work', str(work.resolve())]
    if args.validate_replay:
        command.append('--validate-only')
    subprocess.run(command, check=True)
    authenticate()
    print('PASS_FRONTIER6030_CONDITIONAL_REPLAY')


if __name__ == '__main__':
    main()
