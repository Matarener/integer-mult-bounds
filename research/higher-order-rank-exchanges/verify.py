# SPDX-License-Identifier: Apache-2.0
"""Read-only, Git-free source-bound higher-order exchange certificate."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
from certificate import certify,credit,need,stencil
ROOT=Path(__file__).resolve().parent

def result():
    pins=json.loads((ROOT/'INPUTS.json').read_text(encoding='utf-8'))
    for name,digest in pins.items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'source hash '+name)
    profile={int(r):n for r,n in json.loads((ROOT/'inputs/current-profile.json').read_text()).items()}
    lower,upper=F(17,10000),F(18,10000)
    rows=[]
    for order in (3,4):
        L=credit(order,1,1,lower,upper,16)
        copies=L.denominator//L.numerator+1
        row=certify(profile,73,[{'order':order,'start':1,'step':1,'copies':copies}],
                    lower,upper,{1:1},16)
        caps=row['moves'][0]['capped_sums']
        need(any(v>0 for v in caps.values()) and any(v<0 for v in caps.values()),
             'example must lie outside all-concave capped-mass dominance')
        row['largest_inventory_feasible_copies']=min(profile.get(r,0)//(-v)
            for r,v in stencil(order).items() if v<0)
        rows.append(row)
    return {'schema_version':1,'status':'PASS_HIGHER_ORDER_RANK_EXCHANGES',
            'scope':'Sufficient power-profile and paid-cost comparison, not a circuit or new kappa.',
            'current_profile_head':'ef4315b8caa605e47a2515004845eb2d2ed71a86','examples':rows}

if __name__=='__main__':
    actual=result();need(actual==json.loads((ROOT/'RESULT.json').read_text(encoding='utf-8')),'result drift')
    print(actual['status'])
