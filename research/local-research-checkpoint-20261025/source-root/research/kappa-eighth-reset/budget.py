#!/usr/bin/env python3
"""Research milestone budget; no supplier or multiplication bound. Apache-2.0."""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
import audit_assembly_domain as domain


def budget():
    kappa = Q(1,256)
    leaf = Q(384599,10**10)
    effective_threshold = kappa/(1-kappa)
    coarse_threshold = effective_threshold*(1-leaf)/(1-effective_threshold)
    coarse, stopping = Q(9,2000), Q(1,200)
    effective = (1-stopping)*coarse + stopping*leaf
    admitted, complex_saving = Q(21,5000), Q(9,2000)
    assert effective_threshold == Q(1,255)
    assert coarse_threshold == (1-leaf)/254
    assert admitted < effective < stopping < 1-effective
    arithmetic = domain.diagnostic_case(admitted, complex_saving, kappa,
                                       beta=Q(1,100), backoff=Q(1,10**6))
    assert not arithmetic['failed_slacks']
    assert not arithmetic['strict_arithmetic_rejects_with_assumed_bridge']
    # Hypothetical m=3,W=64,191 rank-one children; exact raw moment test.
    assert Q(191,192)**coarse.denominator * 3**coarse.numerator < 1
    return dict(
        status='ACTIVE RESEARCH MILESTONE, not a new supplier or multiplication bound',
        set_by='Douglas Colkitt', date='2026-10-10',
        kappa=str(kappa), log_exponent=str(1-kappa),
        admitted_bit_strictly_above=str(effective_threshold),
        coarse_bit_strictly_above=str(coarse_threshold),
        illustrative_budget=dict(coarse_bit=str(coarse), stopping_fraction=str(stopping),
            ordinary_leaf=str(leaf), effective_bit=str(effective), admitted_bit=str(admitted),
            complex_saving=str(complex_saving), beta='1/100', backoff='1/1000000'),
        hypothetical_rank_one_benchmark=dict(m=3,W=64,children=191,
            moment_below_one_at=str(coarse),
            status='Numerical specification only; no circuit or bit/complex suppliers supplied'),
        arithmetic=arithmetic, source_sha256=domain.PINS,
        strategy=[
            'Use 2^-8 as the next milestone; 2^-4 is not the admission threshold for this round.',
            'Keep the balanced 40-call inventory and its repair campaign retired.',
            'Compare at most two explicit code/frame or recursive-boundary mechanisms before selecting one.',
            'Reprice target-specific numerical exclusions at the new budget; preserve structural impossibility results.',
            'Require complete role accounting, a uniform operator identity, and a bit/complex counterpart assessment.',
            'The illustrative complex budget is within b<1/32; no extension of that guard is needed for this parameter point.',
        ],
        missing=['Actual bit and complex suppliers', 'Complete finite bridge and compiler costs',
                 'Verification of the candidate-specific uniform and all-size interfaces'])


if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--write',action='store_true'); args=ap.parse_args()
    result=budget(); dest=Path(__file__).with_name('budget.json')
    if args.write: dest.write_text(json.dumps(result,indent=2)+'\n')
    else: assert json.loads(dest.read_text())==result,'budget drift'
    print('PASS: hypothetical 2^-8 budget, including retained bit wrapper and assembly domain; no suppliers certified')
