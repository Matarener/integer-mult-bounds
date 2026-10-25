# SPDX-License-Identifier: Apache-2.0
"""Read-only source-bound certificate replay. Python 3.12, standard library."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json
from certificate import budget, admissible, need
ROOT=Path(__file__).resolve().parent

def result():
    pins=json.loads((ROOT/'INPUTS.json').read_text(encoding='utf-8'))
    for name,digest in pins.items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'source hash '+name)
    rows=[]
    for h in (23,25):
        old,new=[json.loads((ROOT/'inputs'/f'pair-{kind}-{h}-receipt.json').read_text(encoding='utf-8'))
                 for kind in ('original','ranked')]
        need(old['profile']['R']==new['profile']['R'],'unchanged role normalizer')
        a,b=old['profile']['blocks'],new['profile']['blocks']
        row=budget(a,b,F(17,10000),F(18,10000))
        charge={23:1,25:3}[h]
        admissible(a,b,F(17,10000),F(18,10000),{1:charge})
        rows.append(dict(h=h,roles=old['profile']['R'],
                         saving_interval=['17/10000','9/5000'],
                         pays_rank_one_children=charge,**row))
    # A priced, physically conditional target on the actual current full histogram.
    raw=json.loads((ROOT/'inputs/staged544-profile.json').read_text(encoding='utf-8'))
    old=[0]*49
    for r,n in raw.items():old[int(r)]=n
    N=1775
    need(old[2]>=2*N,'actual source has enough rank-2 children')
    new=list(old);new[1]+=N;new[2]-=2*N;new[3]+=N
    modern=admissible(old,new,F(17,10000),F(18,10000),{1:1})
    modern.update(exchange_copies=N,removed_rank_two_children=2*N,
                  positive_rank_one_overhead=1,
                  physical_status='Pricing target only; no operator realization, stock or chronology claim.')
    return {'schema_version':1,'status':'PASS_CHARGED_RANK_DOMINANCE',
            'scope':'Uniform sufficient paid moment comparison; no physical construction or new kappa.',
            'axes':rows,'current_staged_pricing_target':modern}

if __name__=='__main__':
    actual=result()
    expected=json.loads((ROOT/'RESULT.json').read_text(encoding='utf-8'))
    need(actual==expected,'result changed')
    print(actual['status'])
