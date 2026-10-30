#!/usr/bin/env python3
"""Exact rational all-q moment exclusion for permutation continuation routes.
Apache-2.0; substantial OpenAI Codex assistance. Component ceiling only;
all outer exponent interpretations retain their stated transfer premises.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
MAIN = HERE.parent / 'transfer'
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def run():
    # Positive atanh-series terms prove log2>2/3 and log3>1; hence
    # log16>8/3 and log24>3, with no floating-point calculation.
    finite = []
    for q in range(2, 11):
        n, h, r = 2 * q + 2, (2 * q + 2) ** 2 - q, 2 * ((q + 1) // 2) + 6
        loglower = F(2, 3) if q <= 7 else F(8, 3)
        gap = (F(-q) + F(r, 2) + F(h, 600) * loglower) / n
        need(gap > 0, 'exact positive rational moment lower bound')
        record = {'q': q, 'n': n, 'prefix_H2': h, 'optimistic_cleanup_rank': r,
                  'log_n_strict_lower': str(loglower), 'moment_minus_n_strict_lower': str(gap)}
        if q >= 8:
            left = 8 * h
            right = 1800 * (q - (q + 1) // 2 - 3)
            need(left > right, 'q8..10 exact integer comparison')
            record['integer_comparison'] = [left, '>', right]
        finite.append(record)
    A, B, C = 12, -279, 1812
    discriminant = B * B - 4 * A * C
    need(discriminant == -9135, 'positive quadratic discriminant certificate')
    center, residue = F(93, 8), F(3045, 16)
    need(-2 * A * center == B and A * center * center + residue == C,
         'exact complete square for all real q')
    for q in (11, 12, 100, 10 ** 6):
        h = (2 * q + 2) ** 2 - q
        need(3 * h - 300 * q + 1800 == A * q * q + B * q + C,
             'all-q lower polynomial algebra')
    sources = ['notes/batched-complex-rows.tex', 'notes/compact-control-note.tex']
    return {'status': 'PASS_ALL_Q_PERMUTATION_MOMENT_FAILS_AT_ONE_OVER_600',
            'scientific_pin': PIN, 'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins': [{'path': str(MAIN / p), 'sha256': hashlib.sha256((MAIN / p).read_bytes()).hexdigest()}
                            for p in sources],
            'routing_input': 'Written inverse support invariant r*=2ceil(q/2)+6, q>=2; its physical branch inventory and full original-input scope are separate artifacts.',
            'equal_volume_model': 'n=2q+2 equal-volume fields, m=4q+4=2n; individually charged prefix H2=h=n^2-q. A full output has stock n in the volume-weighted proper-child moment.',
            'optimistic_cleanup_lower_moment': 'Support/parent full-scan transfer requires total cleanup native mass>=r*. For p=1-b in(0,1), sum_i(r_i/m)^p >=(sum_i r_i/m)^p >=(r*/m)^p, so one rank-r* child is an optimistic lower bound even if no such literal joint word exists.',
            'test_b': '1/600', 'moment_lower_envelope': 'h*n^(b-1)+(r*/(2n))^(1-b)',
            'elementary_lower_bound': 'moment-n >=[-q+r*/2+(h/600)ln n]/n, by exp(x)>=1+x and x^(1-b)>=x for0<x<1.',
            'finite_exact_cases_q2_to_q10': finite,
            'all_q_tail': {'domain': 'q>=11', 'log_n_strict_lower': '3',
                           'lower_bound': '(12q^2-279q+1812)/(600n)',
                           'discriminant': discriminant,
                           'complete_square': '12*(q-93/8)^2+3045/16>0'},
            'log_proof': 'For x>1, ln x=2*sum_{j>=0} z^(2j+1)/(2j+1), z=(x-1)/(x+1). Positive omitted terms give ln2>2/3 and ln3>1. Therefore ln16>8/3 and ln24=3ln2+ln3>3.',
            'component_consequence': 'The optimistic moment is strictly>n at b0=1/600 for every integerq>=2. It is increasing in b, so no b>=b0 satisfies the required strict proper-child moment within this equal-volume fixed-site/full-scan architecture.',
            'outer_interpretation': 'This is a component b ceiling. In the retained notes/batched-complex-rows.tex transfer lambda_prime>sigma=1-b. The retained compact-control assembly has kappa<epsilon*(1-lambda_prime),epsilon<1, hence kappa<b. Applying that or any separately verified kappa<=b transfer excludes kappa>=1/600 in that specified assembly. No assertion about every possible modern transfer is made.',
            'limits': ['The native-prefix site accounting, equal volumes and parent full-scan transfer premises are essential.',
                       'Cross-cut native fusion, local/partial scan implementations, changed scalar cores/operator bridges, output/owner credits and transfer models are not covered.',
                       'No full wider physical routing word or native query-sharing invoice is inferred from individual inverse coefficient ranks.',
                       'No improved kappa is claimed.'],
            'no_new_kappa': True}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'ROUTING-MOMENT-GATE.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved routing moment gate differs')
    print(out['status'])
