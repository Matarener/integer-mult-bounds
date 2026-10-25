#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Uniform all-replica-count lower bound, attained by the new pool5 blocks.

This specializes mightyOil/PR1281's slack concentration to the actual all-width8
R437 inventory and replaces its replica-domain restriction by an all-T bound.
It certifies arithmetic and a fixed-slot optimum, not a native supplier.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
ENGINE=REPO/'research/native-complex-moment552/engines/moment.py'
ENGINE_PIN='81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482'
PRECEDENT=REPO/'research/bit-partial-width7-optimum/verify.py'
PRECEDENT_PIN='bb8c2d0459e16415aab6f67360b57da1d22623d7564d45b876ccc05dbf436540'
LIMIT=Q(1,100)


def need(ok,reason):
    if not ok:raise ValueError(reason)


def uniform_positive(coeff,E):
    need(sum(r*n for r,n in coeff.items())==0,'zero constant term')
    slope=Q(0);remainder=Q(0)
    for r,n in coeff.items():
        lo,hi=E.logarithm(Q(64,r))
        slope+=r*n*(lo if n>0 else hi)
        remainder+=Q(abs(n)*r,2)*LIMIT*hi*hi*E.exponential(LIMIT*lo,LIMIT*hi)[1]
    need(slope>remainder,'strict uniform Taylor lower bound')
    return dict(coefficients=coeff,slope_lower=str(slope),remainder_upper=str(remainder),
                positive_margin_lower=str(slope-remainder),positive_margin_decimal=E.decimal(slope-remainder))


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=HERE/'pool35')
    parser.add_argument('--out',type=Path,default=HERE/'POOL5-ALL-T-CEILING.json')
    args=parser.parse_args()
    need(__debug__,'assertions required by pinned arithmetic dependency')
    need(not args.out.exists(),'fresh output path required')
    need(sha256(ENGINE.read_bytes()).hexdigest()==ENGINE_PIN,'exact interval engine pin')
    need(sha256(PRECEDENT.read_bytes()).hexdigest()==PRECEDENT_PIN,'credited precedent pin')
    spec=importlib.util.spec_from_file_location('pool5_ceiling_engine',ENGINE)
    E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
    receipt=json.loads((args.candidate/'RESULT.json').read_text())
    template=json.loads(gzip.decompress((args.candidate/'GLOBAL-TEMPLATE.json.gz').read_bytes()))
    expected_payload=json.dumps(template,sort_keys=True,separators=(',',':')).encode()
    need(sha256(expected_payload).hexdigest()==receipt['template_content_sha256'],'actual candidate binding')
    T=receipt['replicas'];need(T>0 and T%5==0,'attaining replica count')
    caps=Counter()
    for pair,cap,stages in template['hosting']['windows'].values():caps[cap]+=222
    need(dict(caps)=={7:666,14:444,28:444,42:444},'actual source slot capacities')
    need(all(x[3]==8 for x in template['hosting']['slots']),'actual helper alphabet exactly width8')
    helper_count=len(template['hosting']['slots'])
    need(helper_count==9*437,'complete nine-call inventory')
    maximum_places=sum((c//8)*n for c,n in caps.items())
    need(maximum_places-helper_count==63,'exact unused helper places per replica')
    rows=[]
    for c in (14,28,42):
        for u in range(1,c//8+1):
            coeff=Counter({c%8+8*u:5})
            coeff[c%8]-=5;coeff[42]-=u;coeff[2]+=u
            coeff={r:n for r,n in sorted(coeff.items()) if n}
            if coeff:
                row=uniform_positive(coeff,E);row.update(capacity=c,unused_places=u);rows.append(row)
            else:need((c,u)==(42,5),'only empty-capacity42 equality')
    need(len(rows)==8,'all nontrivial pure-width8 patterns checked')
    profile={int(r):Q(n,T) for r,n in receipt['profile'].items()}
    local={int(r):n for r,n in receipt['local_profile'].items()}
    idle={7:Q(666),6:Q(444),4:Q(444),2:Q(2157,5),42:Q(63,5)}
    required=Counter({r:9*n for r,n in local.items()});required.update(idle)
    need(dict(sorted(required.items()))==profile,'actual profile exactly attains all-T fractional lower bound')
    integer_profile={r:int(n*5) for r,n in profile.items()}
    need(all(Q(integer_profile[r],5)==n for r,n in profile.items()),'five replicas clear all denominators')
    lo,hi=Q(receipt['bit_endpoint_lower']),Q(receipt['bit_endpoint_upper'])
    need(0<lo<hi<LIMIT and hi-lo==Q(1,10**24),'certified endpoint range')
    lower_bounds=E.moment(integer_profile,64,4440,lo,True)
    upper_bounds=E.moment(integer_profile,64,4440,hi,True)
    need(lower_bounds[1]<1<upper_bounds[0],'exact strict all-T ceiling and attaining lower endpoint')
    # Positive and negative controls check the inequality direction and inventory.
    bad={14:-5,6:5,42:1,2:-1}
    rejected=False
    try:uniform_positive(bad,E)
    except ValueError:rejected=True
    need(rejected,'reversed price inequality rejected')
    need(sum(r*n for r,n in idle.items())==41958-8*9*437,'idle raw-rank identity')
    result=dict(status='PASS_UNIFORM_R437_ALL_REPLICA_COUNT_FIXED_SLOT_CEILING',
        interval='0 < a <= 1/100',slot_capacities_per_replica=dict(caps),helper_width=8,
        helpers_per_call=437,calls_per_replica=9,unused_places_per_replica=63,
        pattern_inequalities=rows,equality_patterns='u=0 for any capacity, or capacity42/u5',
        optimum_idle_profile_per_replica={r:str(n) for r,n in idle.items()},
        optimum_complete_profile_per_replica={r:str(n) for r,n in profile.items()},
        optimum_attained_exactly_when_five_divides_T=True,actual_attaining_T=T,
        endpoint_lower=str(lo),endpoint_upper=str(hi),
        lower_endpoint_moment_upper=str(lower_bounds[1]),upper_endpoint_moment_lower=str(upper_bounds[0]),
        fallback='All1998T idle remainders stay positive; unchanged local paid count givesN28233T. The full 32m^2*N/10^16 rank1 envelope is therefore identical across placements and scales linearly withT.',
        source_sha256={str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),ENGINE,PRECEDENT,args.candidate/'RESULT.json')},
        controls={'reversed_price_inequality_rejected':True,'eight_strict_and_one_equality_cases':True},
        scope='All integerT>=1, every clock and owner arrangement with this exact R437 local profile, all-width8 inventory, capacities7/14/28/42 at multiplicities666/444/444/444 perreplica, one nonempty remainder child, and unchanged fallback rule. This is not an exclusion for changed native words, helperwidths, banktemplates, slotcapacities or controllers. Physical/native admission is separate.')
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],'8strict pattern inequalities; optimum attained by every positive T divisible by5')


if __name__=='__main__':main()
