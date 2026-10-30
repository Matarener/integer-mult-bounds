#!/usr/bin/env python3
"""Exact compressed ambient ranks for the finite mixed-job precompiler.

This certifies inequalities in a written constructive proof. It does not
materialize the enormous finite word or formally verify the proof itself.
Apache-2.0. Substantial OpenAI assistance. The integer lockstep flow is
Jacob Alan Sussman's Theorem 1G; see ../architecture/FINITE-PRECOMPILATION.md.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent/'architecture'))
import mixed_target_probe as E


def need(value, message):
    if not value:
        raise AssertionError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def ceil(value):
    value = Q(value)
    return -((-value.numerator)//value.denominator)


def one_case(name, targets, paid, tested_saving, uniform_saving, theta_bar):
    targets = {int(k): int(v) for k,v in targets.items()}
    paid = {int(k): int(v) for k,v in paid.items()}
    m, kmin, rmax = max(targets), min(targets), max(paid)
    need(1 <= rmax < kmin <= m, 'Strict mixed separation')
    t, z = 1-tested_saving, 1-uniform_saving
    z0 = (t+z)/2
    delta, h = z0-t, 1-theta_bar
    need(0 < t < z0 < z < 1 and delta > 0 and h > 0, 'Strict rational exponents')
    signed = Counter(targets)
    signed.subtract(paid)
    margin = E.moment(signed, tested_saving)
    need(margin[0] > 0, 'Strict unit superpotential at the chosen rational t')
    rank_margin = sum(k*v for k,v in signed.items())
    need(rank_margin > 0, 'Rank-one superpotential gives L(n) <= n')
    a,b = theta_bar.numerator,theta_bar.denominator
    need(rmax**b < kmin**a, 'Integer proof theta=log(rmax)/log(kmin) < theta_bar')
    need(m**h.numerator < 2**h.denominator, 'Integer proof m^h < 2')
    need(2*rmax <= 16, 'm E(n)/n < 16 n^-h')
    ln_m = E.log_interval(m)
    ln_two = E.log_interval(2)
    need(z0 > Q(1,2) and (1-z0)*ln_m[1] < ln_two[0],
         'eta=z0*m^(z0-1) > 1/4')
    H0 = ceil((3+4*delta)/(h*delta))
    need(H0 >= m.bit_length(), 'n0=2^H0 exceeds the entire finite base range')
    need(H0*h*delta >= 3+4*delta,
         'Every n >= n0 has exit coefficient <= 1/8 < eta/2')
    ratio = H0*(1-z0)/(z-z0)
    H1 = ratio.numerator//ratio.denominator+1
    need(H1 > H0 and H1*(z-z0) > H0*(1-z0),
         'Explicit N=2^H1 has L(N) < N^z')
    controls = {
        'one_less_H0_fails_chosen_exit_bound': (H0-1)*h*delta < 3+4*delta,
        'one_less_H1_fails_strict_final_bound': (H1-1)*(z-z0) <= H0*(1-z0),
        'requested_004_not_supported_by_this_unit': E.moment(signed,Q('0.004'))[1] < 0,
    }
    need(all(controls.values()), 'All deliberate negative controls reject')
    return {
        'family':name, 'targets':targets, 'paid':paid,
        'm':m, 'k_min':kmin, 'r_max':rmax,
        'tested_mixed_saving':str(tested_saving), 'strict_test_margin':E.show(margin),
        'uniform_saving':str(uniform_saving),
        't':str(t), 'z0':str(z0), 'z':str(z), 'delta':str(delta),
        'theta_upper':str(theta_bar), 'h':str(h), 'rank_one_surplus':rank_margin,
        'theta_integer_comparison':{'left':rmax**b, 'right':kmin**a},
        'm_to_h_integer_comparison':{'left':m**h.numerator, 'right':2**h.denominator},
        'eta_strict_lower':'1/4',
        'n0':{'encoding':'2^H0','H0':H0},
        'N':{'encoding':'2^H1','H1':H1},
        'induction_constant_A':'n0^(1-z0)',
        'exit_power_gap':str(H0*h*delta-(3+4*delta)),
        'final_strict_power_gap':str(H1*(z-z0)-H0*(1-z0)),
        'proven_uniform_moment':'P_N/B_N < N^z',
        'exact_integer_test':{'P_and_B_exponent':z.denominator,'N_exponent':z.numerator},
        'negative_controls':controls,
        'materialized_winning_word':False,
        'template_definition':'Apply the integer, ordered, denominator-cleared compiler to this exact N. Keep every scalar/route operation and one owned bank per finite unit instance; only final rank-one leaves remain paid.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE/'EXPLICIT-TEMPLATE-BOUNDS.json')
    args = parser.parse_args()
    cpath = HERE/'P3-NATIVE-COVER.json.gz'
    bpath = HERE.parent/'bit/MIXED-PRODUCTIVE-BIT.json'
    c = read(cpath)['cover']
    b = next(row for row in read(bpath)['candidates'] if row['pairs']==3 and row['keep_idle_mask']==43)
    cases = [
        one_case('complex',c['targets'],c['paid'],Q('0.002305'),Q('0.002304'),Q(9,10)),
        one_case('BIT',b['targets'],b['paid'],Q('0.002769'),Q('0.00276'),Q(15,16)),
    ]
    sources = [Path(__file__),cpath,bpath,HERE.parent/'architecture/mixed_target_probe.py',
               HERE.parent/'architecture/FINITE-PRECOMPILATION.md',
               HERE.parent/'transfer-audit/finite_dag_audit.py',
               HERE.parent/'transfer-audit/AUDIT.md']
    result = {
        'schema':'explicit-compressed-uniform-template-ranks/1',
        'status':'PASS_EXACT_SUPERPOTENTIAL_AND_COMPRESSED_RANK_BOUNDS',
        'cases':cases,
        'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
        'proof_dependency':'The written native finite-precompilation theorem, including arbitrary-input closure and every exact ordered batch. This receipt checks its quantitative sufficient inequalities, not the theorem as a formal proof.',
        'scope':'Explicit fixed ranks are specified in compressed form. No near-threshold word, GL cover, B_N, P_N or U_N is materialized. Their exact finite algorithms and replacement constants remain part of the construction.',
        'new_kappa_claimed_by_this_file':False,
    }
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'families':[
        {key:row[key] for key in ('family','uniform_saving','n0','N','final_strict_power_gap')}
        for row in cases]}))


if __name__ == '__main__':
    main()
