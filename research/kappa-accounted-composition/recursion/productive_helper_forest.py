#!/usr/bin/env python3
"""Exact finite packings for productive helper-only fields.

This is a width/chronology certificate, not a native owner emission.  The full
physical cleaned-block contract permits independent helper endpoint adapters
only if each relative helper transform is certified as a rank-width Fourier
with the stated allowed monomial adapters.  That adapter obligation and the
changed data-controller endpoint closure remain separate.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True

WIDTHS = Counter({5: 28, 6: 18, 7: 56, 8: 93, 9: 213})
PROFILE = Counter({1: 2453, 2: 716, 3: 224, 4: 74, 5: 48})
HISTORICAL_IDENTITY_PROFILE = Counter({1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8})

def log_interval(r):
    e = r.bit_length() - 1
    def odd_series(x):
        z = (x - 1) / (x + 1)
        n = 80
        s = 2 * sum((z ** (2*j+1) / (2*j+1) for j in range(n)), Q(0))
        tail = 2*z**(2*n+1) / ((2*n+1)*(1-z*z))
        return s, s + tail
    a, b = odd_series(Q(2))
    c, d = odd_series(Q(r, 2**e))
    return e*a+c, e*b+d

def exp_interval(x):
    assert 0 <= x < 1
    term, s = Q(1), Q(1)
    n = 48
    for j in range(1, n+1):
        term *= x/j
        s += term
    following = term*x/(n+1)
    return s, s + following/(1-x/(n+2))

def power_interval(r, c):
    if r == 1:
        return Q(1), Q(1)
    lo, hi = log_interval(r)
    elo, _ = exp_interval(c*lo)
    _, ehi = exp_interval(c*hi)
    return Q(r)/ehi, Q(r)/elo

def encode_interval(bounds):
    scale = 10**45
    lo, hi = bounds
    a = lo.numerator*scale//lo.denominator
    b = -((-hi.numerator*scale)//hi.denominator)
    def fixed(n):
        sign = '-' if n < 0 else ''
        s = str(abs(n)).rjust(46, '0')
        return sign+s[:-45]+'.'+s[-45:]
    return {'lower': fixed(a), 'upper': fixed(b)}

def invoice(width, rank, calls, residual, c, source_profile=PROFILE):
    profile = Counter({r: Q(n*calls) for r, n in source_profile.items()})
    profile.update(residual)
    credit = power_interval(rank, c)
    lo, hi = width*credit[0], width*credit[1]
    for r, n in sorted(profile.items()):
        a, b = power_interval(r, c)
        lo -= n*b
        hi -= n*a
    return {'C': str(c), 'raw_allowance': encode_interval((lo, hi)),
            'after_8_H1_per_call': encode_interval((lo-8*calls, hi-8*calls))}

def verify_case(name, lift, width, rank, calls, hosts, templates):
    counts = [Counter() for _ in range(calls)]
    residual = Counter()
    new_hosts = 0
    for host in hosts:
        cap = host['capacity']
        used = sum(host['widths'])
        assert used <= cap
        assert all(0 <= r < rank for r in host['widths'])
        assert 0 <= cap-used < rank
        if host['kind'] == 'productive':
            new_hosts += 1
        for stage, r in zip(host['stages'], host['widths']):
            if r:
                counts[stage][r] += 1
        if cap > used:
            residual[cap-used] += 1
    for row in counts:
        assert row == Counter({r: n*lift for r, n in WIDTHS.items()})
    per = {r: Q(n, lift) for r, n in residual.items()}
    total_rank = calls*sum(r*n for r, n in PROFILE.items()) + sum(r*n for r, n in per.items())
    assert width*rank-total_rank == 224*((calls-1)//2)
    return {'name': name, 'lift': lift, 'productive_fields_per_controller': new_hosts//lift,
            'total_fields_per_controller': width, 'ambient_rank': rank, 'calls': calls,
            'helper_histogram_per_call': dict(sorted(WIDTHS.items())),
            'role_match': True, 'strict_child_rank': True,
            'residual_profile_per_controller': {str(r): str(n) for r, n in sorted(per.items())},
            'rank_bill': str(total_rank), 'rank_credit': width*rank,
            'rank_margin': str(width*rank-total_rank), 'templates': templates,
            'host_assignment_sha256': hashlib.sha256(json.dumps(hosts, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'invoices': [invoice(width, rank, calls, per, c) for c in (Q(349, 200000), Q(1, 250))],
            'historical_identity_fallback_same_helper_packing_favorable_screen': [
                {'C': str(c), 'complete_margin':invoice(width, rank, calls, per, c, HISTORICAL_IDENTITY_PROFILE)['raw_allowance']}
                for c in (Q(349, 200000), Q(1, 250))]}

def p1(all_have_nine=False):
    rows = ([(168,[9,9,7]),(54,[9,9,6]),(9,[9,9,5]),(75,[9,8,5]),(102,[9,8,8])]
            if all_have_nine else [(168,[9,9,7]),(54,[9,9,6]),(84,[9,9,5]),(27,[9,8,8]),(75,[8,8,8])])
    hosts = []
    for count, row in rows:
        for shift in range(3):
            v = [row[(s+shift)%3] for s in range(3)]
            hosts.extend({'kind':'productive','capacity':25,'stages':[0,1,2],'widths':v} for _ in range(count))
    return verify_case('p1_every_host_has_width9' if all_have_nine else 'p1',3,632,25,3,hosts,rows)

def p2(compact=False):
    lift = 1 if compact else 12
    hosts = []
    pairs = [(56,[9,7]),(56,[7,9]),(18,[9,6]),(18,[6,9]),(28,[9,5]),(28,[5,9]),(20,[8,8])]
    for stages in ([0,1],[3,4]):
        for count, row in pairs:
            hosts.extend({'kind':'original_idle','capacity':16,'stages':stages,'widths':row} for _ in range(count*lift))
    for r, count in [(8,93),(7,56),(6,18),(5,28),(0,29)]:
        hosts.extend({'kind':'original_idle','capacity':8,'stages':[2],'widths':[r]} for _ in range(count*lift))
    for zero in [0,1,3,4]:
        row = [9,9,9,9,9]
        row[zero] = 0
        hosts.extend({'kind':'productive','capacity':41,'stages':[0,1,2,3,4],'widths':row} for _ in range(35 if compact else 100*lift//3))
    extra = [(73,[8,8,9,8,8]),(6,[9,9,0,9,9])] if compact else [(73*lift,[8,8,9,8,8]),(20*lift//3,[0,0,9,0,0]),(11*lift,[9,9,0,9,9])]
    for count, row in extra:
        hosts.extend({'kind':'productive','capacity':41,'stages':[0,1,2,3,4],'widths':row} for _ in range(count))
    templates = [['140','three 9s outside stage2; stage2=9'],['73',[8,8,9,8,8]],['6',[9,9,0,9,9]]] if compact else [['400/3','three 9s outside stage2; stage2=9'],['73',[8,8,9,8,8]],['20/3',[0,0,9,0,0]],['11',[9,9,0,9,9]]]
    return verify_case('p2_219_hosts' if compact else 'p2',lift,667 if compact else 672,41,5,hosts,{'original_pair_bins':pairs,'global_zero_positions':[0,1,3,4],
        'global_templates':templates})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = {'status':'PASS', 'scope':'Exact helper-width inventory, chronological eligibility, integer replica lifts, strict recursive child ranks and outward-rational complete invoices. Native whole-block helper adapters and changed data-controller endpoint closure are not emitted by this certificate.',
        'interface_lemma':'If a cleaned physical native word is diag(DataOp,T_i), independent allowed monomial pre/post adapters on each helper change only T_i. When those adapters reduce T_i to its width-r Fourier, productive helper paths can be packed without separately preparing canonical native entrance frames. The internal word and ADDs are unchanged. Exact normal-form phases remain a native proof obligation.',
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_profile':dict(sorted(PROFILE.items())),
        'historical_identity_profile':dict(sorted(HISTORICAL_IDENTITY_PROFILE.items())),
        'p1_synchronous_entrance_debt_without_whole_block_adapters':371,
        'p2_global_field_lower_bound_in_this_unstaggered_middle_window':213,
        'p2_fixed_original_assignment_global_field_minimum': {'minimum':219,
            'ordinary_stage_nines_total':444, 'ordinary_stage_nonzero_roles_total':736,
            'middle_stage_nines':213,
            'proof':'The four other stages require736 nonzero global roles. Of213 hosts carrying middle width9, each can fit at most three other roles unless all four are width8. There are only292 other width8 roles, so at most73 hosts have four such roles. The q-213 middle-unused hosts fit at most four other roles. Thus736<=3*213+73+4*(q-213)=4q-140, so q>=219. The219-host construction attains it. Scope fixes the displayed original-bin assignments and width-only whole-helper interface.'},
        'cases':[p1(),p1(True),p2(),p2(True)]}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'cases':[{'name':c['name'],'rank_margin':c['rank_margin']} for c in result['cases']]}))

if __name__ == '__main__':
    main()
