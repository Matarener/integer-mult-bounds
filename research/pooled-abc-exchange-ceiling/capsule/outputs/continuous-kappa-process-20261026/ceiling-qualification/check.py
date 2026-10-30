#!/usr/bin/env python3
"""Exact finite certificate for the stated pooled A/B/C invoice relaxation.

Standard-library Fraction arithmetic only. No source/constructor/price imports,
logarithm engine, real powers, root search, or physical-construction replay.
The analytic implications certified by these coefficients remain paper proofs.
Credit: Ali Romman PR5544/5545; thu-nmrc PR5551; retained predecessors.
"""
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[2]
BASELINE_SHA = '3c4d8db5a9695924027f5801901b55cefe0cdc5ea07450aaf396de7e5887e608'
HEAD = '18968423711fd902aaee1099979497d55603e1dc'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def clean(histogram):
    return {int(r): Q(n) for r, n in histogram.items() if n}


def combine(*terms):
    out = {}
    for scale, histogram in terms:
        for rank, count in histogram.items():
            out[rank] = out.get(rank, Q(0)) + scale * count
    return clean(out)


def mass(histogram):
    return sum((r*n for r, n in histogram.items()), Q(0))


def display(histogram):
    return {str(r): str(n) for r, n in sorted(histogram.items()) if n}


def authenticated_baseline(raw):
    need(hashlib.sha256(raw).hexdigest() == BASELINE_SHA, 'baseline byte authentication')
    return json.loads(raw)


def log_brackets():
    brackets = {2:(Q('0.6931'), Q('0.6932')),
                3:(Q('1.0986'), Q('1.0987')),
                5:(Q('1.6094'), Q('1.6095'))}
    for n, (lower, upper) in brackets.items():
        z = Q(n-1, n+1)
        partial = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(32)), Q(0))
        tail = 2*z**65/(65*(1-z*z))
        need(lower < partial < partial+tail < upper, 'rational log bracket '+str(n))
        need(0 < tail < Q(1, 10**10), 'rational log tail '+str(n))
    return brackets


def evidence():
    return {
        'calls':18,
        'local':{1:2428, 2:557, 3:389, 4:112, 5:107, 6:17, 7:13, 9:1},
        'helpers':{4:51, 5:36, 7:24, 8:122, 9:294},
        'queries':{1:1560},
        'idles':{16:416, 24:416, 32:416, 40:416, 48:416, 56:416, 64:416, 72:208},
        'banks':{17:416, 25:416, 33:416, 41:416, 49:416, 57:416, 65:416, 73:208, 145:208},
        'generators':{'A':{1:-1, 5:-1, 6:1},
                      'B':{1:1, 2:-2, 3:1},
                      'C':{1:1, 2:-1, 4:-1, 5:1}},
        'optimum':{'A':3942, 'B':4005, 'C':2016},
        'optimal_paid':{1:47343, 3:11007, 6:4248, 7:234, 9:18,
                        16:416, 24:416, 32:416, 40:416, 48:416, 56:416, 64:416, 72:208},
    }


def qualify(saved, data, brackets):
    need(saved['schema'] == 'p104-focused-contact-audit/v1', 'baseline schema')
    need(saved['reviewed_head'] == HEAD and Q(saved['C_probe']) == Q(33,10000), 'baseline source and probe')
    need(saved['new_kappa'] is None, 'baseline does not supply a new kappa')
    interval = saved['current_moment_at_target']
    lower, upper = (Q(interval[k]) for k in ('lower_decimal_outward', 'upper_decimal_outward'))
    need(lower < upper == Q('-64.2349800489874753468185') < -64, 'inherited outward upper endpoint')
    calls = data['calls']
    local = clean(data['local'])
    helper = clean(data['helpers'])
    queries, idles, banks = (clean(data[k]) for k in ('queries','idles','banks'))
    need(calls == 18 and local == clean(saved['local_paid_after']), '18 baseline local invoices')
    need(sum(helper.values()) == 527 and sum(queries.values()) == 15*104 and
         sum(idles.values()) == 15*208 and sum(banks.values()) == 32*104,
         'independent helper/query/idle/main-bank census')
    baseline_paid = combine((calls,local),(1,queries),(1,idles))
    targets = combine((calls,helper),(1,banks))
    need(baseline_paid == clean(saved['complete_paid_after']), 'complete baseline paid reconstruction')
    need(targets == clean(saved['complete_targets']), 'complete unchanged target reconstruction')
    need(sum(baseline_paid.values()) == 69912 and sum(targets.values()) == 12814,
         'baseline complete job and productive field totals')
    need(sum(local.values()) == 3624 and mass(local) == 5894, 'local baseline census')
    gen = {name:clean(h) for name,h in data['generators'].items()}
    need(gen == {'A':clean({1:-1,5:-1,6:1}),
                 'B':clean({1:1,2:-2,3:1}),
                 'C':clean({1:1,2:-1,4:-1,5:1})}, 'charged exact A/B/C generators')
    need(all(mass(g) == 0 for g in gen.values()), 'exchange rank-mass conservation')
    # These exact saturations are the linear-program certificate. Positive
    # gains and gA+gC-gB/2>0 are justified by strict concavity in the paper.
    a,b,c = (Q(data['optimum'][k],calls) for k in ('A','B','C'))
    need(c == local[4] and a == local[5]+c and 2*b+c == local[2], 'pooled optimum saturations')
    need((a,b,c) == (Q(219),Q(445,2),Q(112)), 'unique averaged optimum coefficients')
    pooled_local = combine((1,local),(a,gen['A']),(b,gen['B']),(c,gen['C']))
    need(pooled_local == clean({1:Q(5087,2),3:Q(1223,2),6:236,7:13,9:1}), 'pooled averaged profile')
    need(sum(pooled_local.values()) == 3405 and mass(pooled_local) == 5894, 'pooled local conservation')
    # C, then B, then A is a nonnegative multiset itinerary; it is not a
    # source-chart itinerary or a witness for independent Gaussian inputs.
    running = combine((calls,local))
    for name in ('C','B','A'):
        running = combine((1,running),(Q(data['optimum'][name]),gen[name]))
        need(all(n >= 0 and n.denominator == 1 for n in running.values()), 'pooled integer inventory '+name)
    need(running == combine((calls,pooled_local)), 'sequential pooled inventory endpoint')
    paid = combine((1,running),(1,queries),(1,idles))
    need(paid == clean(data['optimal_paid']), 'complete optimal paid reconstruction')
    need(sum(paid.values()) == 65970 and mass(targets)-mass(paid) == 760, 'complete optimum conservation')
    separate_local = combine((1,local),(219,gen['A']),(222,gen['B']),(112,gen['C']))
    need(separate_local == clean({1:2543,2:1,3:611,6:236,7:13,9:1}), 'separate integer-local optimum')
    need(combine((calls,pooled_local),(-calls,separate_local)) == combine((9,gen['B'])), 'pooling grants nine extra B')
    gains = {k:combine((-1,g)) for k,g in gen.items()}
    need(combine((1,gains['A']),(1,gains['C']),(-1,gains['B'])) ==
         clean({1:1,2:-1,3:1,4:1,6:-1}), 'strong exchange-slope identity')
    # Sufficient rational comparisons for gain concavity in C. The gA
    # comparison follows from r^t(log r)^2 strictly increasing for r>1.
    need(brackets[3][0]**2 > 2*brackets[2][1]**2 and
         brackets[5][0]**2 > 5*brackets[2][1]**2, 'gain concavity coefficient comparisons')
    slopes = {'A':6*brackets[2][1]+6*brackets[3][1]-5*brackets[5][0],
              'B':3*brackets[3][1]-4*brackets[2][0],
              'C':5*brackets[5][1]-10*brackets[2][0]}
    tangent = {'A':Q(2705,1000),'B':Q(524,1000),'C':Q(1117,1000)}
    need(all(0 < slopes[k] < tangent[k] for k in slopes), 'conservative tangent bounds')
    weighted = a*tangent['A']+b*tangent['B']+c*tangent['C']
    margin_upper = -64+calls*Q(33,10000)*weighted
    need(margin_upper == Q(-72275567,5000000) < 0, 'strict pooled target-point upper bound')
    signed = combine((1,targets),(-1,paid))
    low = {r:n for r,n in signed.items() if r <= 9}
    need(low == clean({1:-47343,3:-11007,4:918,5:648,6:-4248,7:198,8:2196,9:5274}), 'signed low-rank moment')
    adverse = sum(n for r,n in low.items() if r < 9 and n > 0)
    rank_one = -signed[1]/9
    need(adverse == 3960 and rank_one > adverse, 'normalized derivative coefficient domination')
    pairs = (16,24,32,40,48,56,64,72)
    high = {r:n for r,n in signed.items() if r > 9}
    reconstructed_high = {145:Q(208)}
    for rank in pairs:
        count = Q(208 if rank == 72 else 416)
        reconstructed_high[rank],reconstructed_high[rank+1] = -count,count
        need(rank > 9 and count > 0, 'positive normalized high pair')
    need(high == reconstructed_high, 'all normalized high terms accounted')
    endpoint_zero = sum(signed.values())
    endpoint_one = mass(signed)/9
    need(endpoint_zero == -53156 and endpoint_one == Q(760,9) > 0, 'normalized opposite-sign endpoints')
    return {'baseline_paid':display(baseline_paid), 'targets':display(targets),
            'pooled_local':display(pooled_local), 'pooled_paid':display(paid),
            'signed_moment':display(signed), 'averaged_optimal_exchanges':[str(a),str(b),str(c)],
            'global_optimal_exchanges':data['optimum'], 'separate_local':display(separate_local),
            'local_rank_mass':str(mass(local)), 'pooled_paid_count':str(sum(paid.values())),
            'target_count':str(sum(targets.values())), 'rank_surplus':'760',
            'rational_log_brackets':{str(n):list(map(str,v)) for n,v in brackets.items()},
            'log_partial_terms':32, 'each_log_tail_below':'1/10000000000',
            'tangent_slope_upper':{k:str(v) for k,v in slopes.items()},
            'tangent_constants':{k:str(v) for k,v in tangent.items()},
            'weighted_tangent_upper':str(weighted), 'C_probe':'33/10000',
            'strict_margin_upper':str(margin_upper),
            'normalized_derivative':{'rank_one_coefficient_lower':str(rank_one),
                                     'adverse_coefficient_upper':str(adverse)},
            'normalized_endpoints':[str(endpoint_zero),str(endpoint_one)]}


def main():
    pins = json.loads((B/'INPUTS.json').read_text())
    for path, sha in pins['files'].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha, 'pinned input '+path)
    raw = (ROOT/pins['baseline']).read_bytes()
    saved = authenticated_baseline(raw)
    data, brackets = evidence(), log_brackets()
    certificate = qualify(saved, data, brackets)
    controls = {}
    try:
        authenticated_baseline(raw+b' ')
    except ValueError:
        controls['baseline_byte_mutation'] = 'rejected'
    else:
        raise ValueError('accepted baseline byte mutation')
    mutations = [
        ('drop_nonlocal_idle', lambda s,d:d['idles'].__setitem__(16,415)),
        ('lose_productive_helper', lambda s,d:d['helpers'].__setitem__(9,293)),
        ('seventeen_calls', lambda s,d:d.__setitem__('calls',17)),
        ('baseline_local_count', lambda s,d:d['local'].__setitem__(1,2429)),
        ('omit_B_split_debit', lambda s,d:d['generators']['B'].__setitem__(2,-1)),
        ('free_C_split', lambda s,d:d['generators']['C'].__setitem__(2,0)),
        ('unpooled_B_count', lambda s,d:d['optimum'].__setitem__('B',3996)),
        ('overdraw_A_inventory', lambda s,d:d['optimum'].__setitem__('A',3943)),
        ('omit_complete_paid_job', lambda s,d:d['optimal_paid'].__setitem__(1,47342)),
        ('wrong_baseline_probe', lambda s,d:s.__setitem__('C_probe','1/300')),
        ('weaken_baseline_interval', lambda s,d:s['current_moment_at_target'].__setitem__('upper_decimal_outward','-63')),
    ]
    for name, mutation in mutations:
        bad_saved, bad_data = deepcopy(saved), deepcopy(data)
        mutation(bad_saved,bad_data)
        try:
            qualify(bad_saved,bad_data,brackets)
        except ValueError:
            controls[name] = 'rejected'
        else:
            raise ValueError('accepted mutation '+name)
    result = {'schema':'pooled-abc-ceiling-qualification/v1',
              'status':'PASS_SCOPED_POOLED_ABC_COEFFICIENT_CERTIFICATE',
              'baseline_sha256':BASELINE_SHA, 'reviewed_baseline_head':HEAD,
              'compared_successor_head':'79072da5404a01056df2af2e4132324b01c72366',
              'certificate':certificate, 'mutation_controls':controls,
              'analytic_scope':'Fixed complete PR5545 invoice, A/B/C signed net exchanges, free pooling and real averages, 0<C<1. Paper concavity and normalized derivative implications are retained analytic premises; this is not proof-kernel acceptance.',
              'inherited_numerical_premise':'Authenticated qualified baseline outward interval; interval engine not rerun.',
              'exclusion':'At 33/10000 and every larger C below 1, the defined optimistic family fails the necessary raw margin, by the accompanying analytic proof.',
              'physical_witness':False, 'new_kappa':None, 'selected_promotion':False,
              'credit':'Ali Romman PR5544/5545; thu-nmrc PR5551; retained P104/native/controller/compiler/precision/analytic predecessors; joint inventory analysis and Codex-assisted qualification for Chris R/Clear1nsight.'}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__ == '__main__':
    main()
