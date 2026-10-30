#!/usr/bin/env python3
"""Generalized-support floor53 and its fixed three-seed pressure consequence.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE=Path(__file__).resolve().parent
BASE=Path('/Users/ross/git/math')
RAW=BASE/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
COMP=HERE.parents[1]/'kappa-major-20261018T1330Z/bit-endpoint/BIT-FULL-COMPENSATION.json'
CAP=(0,1,3,6,12,20,36,63,120)

def need(b,m):
    if not b:raise ValueError(m)

def rank(rows):
    piv={}
    for x in rows:
        while x:
            j=x.bit_length()-1
            if j in piv:x^=piv[j]
            else:piv[j]=x;break
    return len(piv)

def profiles(budget,bounds):
    checked=0;survivors=[]
    def rec(d,left,rows):
        nonlocal checked
        if d==9:
            checked+=1;t=len(rows)
            if t<9:return
            sums=[0]
            for r in rows:sums.append(sums[-1]+CAP[r])
            if all(sums[t-9+k]>=bounds[k]for k in range(1,10)):
                survivors.append({'cost':sum(rows),'ranks':rows})
            return
        for count in range(left//d+1):rec(d+1,left-count*d,rows+[d]*count)
    rec(1,budget,[])
    return checked,survivors

def lower_log(x):
    need(x>1,'positive logarithm')
    z=(x-1)/(x+1)
    return 2*sum((z**(2*j+1)/Q(2*j+1)for j in range(32)),Q(0))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','raw source pin')
    need(sha256(COMP.read_bytes()).hexdigest()=='1ee06005d3b82ff592640d9aa4be2021b6de0a0b27fba5723aa06c36a6adbd20','full compensation pin')
    raw=json.loads(gzip.decompress(RAW.read_bytes()));comp=json.loads(COMP.read_bytes())
    rows=[1<<i for i in range(660)]
    for phase in('D','A'):
        for _,dst,srcs in raw[phase]:
            for src in srcs:rows[dst]^=rows[src]
    R=[rows[h]&((1<<111)-1)for h in raw['ret']]
    K=[sum(1<<j for j in row)for row in raw['scatter']]
    need(R==comp['R']and K==comp['K']and rank(R)==rank(K)==9,'source-bound rank9 factor')
    code=[0]
    for r in R:code += [x^r for x in code]
    need(len(set(code))==512,'complete independent code')
    weights=Counter(x.bit_count()for x in code[1:]);need(min(weights)==48,'code distance48')
    union=0
    for r in R:union|=r
    need(union.bit_count()==111,'all111 columns active')
    bounds=[0]
    for k in range(1,9):
        numerator=48*((1<<k)-1);denominator=1<<(k-1)
        bounds.append((numerator+denominator-1)//denominator)
    bounds.append(111)
    need(bounds==[0,48,72,84,90,93,95,96,96,111],'integer generalized-support bounds')
    checked,survivors=profiles(52,bounds)
    need(checked==340260 and survivors==[{'cost':52,'ranks':[4]*13}],
         'complete cost<=52 profile census')
    # Any six of the13 rank4 readers span a subspace meeting D in dim>=2.
    # Their support union must have72 coordinates, its capacity maximum;
    # hence every six, and therefore every pair, have disjoint full supports.
    need(6*CAP[4]==bounds[2] and 13*CAP[4]>111,'unique equality case impossible')
    weak=[0]+[44*((1<<k)-1)//(1<<(k-1))for k in range(1,9)]+[111]
    _,weak_survivors=profiles(52,weak)
    need(weak_survivors!=survivors,'weakened actual distance premise changes screen')
    # Frozen R429 bulk: remove the111 actual rank1 target-to-FULL lifts.
    # The remaining direct FULL readout/scatter ADDs have no native children.
    bulk={int(r):c for r,c in comp['forward']['profile'].items()}
    bulk[1]-=111
    need(bulk=={1:1295,2:1342,3:79,4:44,5:93,6:11,7:9},'unmodified R429 native bulk profile')
    need(sum(r*c for r,c in bulk.items())==4986==14*111+8*429,'bulk mass and coverage')
    a=Q(1,500);m=22
    pressure=3*a*sum(r*c*lower_log(Q(m,r))for r,c in bulk.items())
    deficit=2*111-3*53
    need(deficit==63 and pressure>deficit,'all-L fixed bulk/flat-reader seed contradiction')
    need(pressure<2*111-3*49,'old49 floor alone does not give this owner-free contradiction')
    out={'status':'PASS_OVERCOMPLETE_READOUT_COST_GE53_AND_FIXED_THREE_SEED_A002_REJECTION',
         'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
         'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in(RAW,COMP)},
         'R':R,'K':K,'code_weights':dict(sorted(weights.items())),'flat_capacities':CAP,
         'generalized_support_lower_bounds':bounds,'profiles_checked':checked,
         'relaxed_survivors':survivors,'equality_case':'13 rank4 readers: any6 require72 support entries, so all13 are disjoint/full12;156>111.',
         'readout_cost_lower':53,
         'readout_model':'Binary R=B C, arbitrary number of readouts, row i charged at least the rational E8-flat dimension containing its support. Prune dependent C rows first. No shared native queries or COPY into nonzero target frames is covered.',
         'bulk_profile':bulk,'bulk_mass':4986,
         'seed_consequence':{'L_min':3,'parent_arity':'m=1+7L','primitive_exponent_min':'1/500','seed_calls':3,
            'deficit_upper':63,'pressure_strict_lower':str(pressure),'excess_lower':str(pressure-deficit),
            'hypotheses':['Three unchanged R429 native bulk profiles, each repaired in the separate linear flat-reader model.',
                'The seeded star credits common-axis progress2*111 and charges at least the three readout bills; subsequent FULL-target fanout contributes no extra deficit.',
                'Every other child has rank<=m, so ignored native/owner/padding/repair terms have nonnegative pressure.'],
            'proof':'At a>=1/500,m>=22, keep only three bulk profiles and use exp(t)-1>=t and32 positive atanh logarithm terms. This lower bound exceeds D<=222-3*53. No stock/helper-count assumption is needed.'},
         'controls':['weaken distance48 premise','replace53 floor by49 and observe loss of contradiction'],
         'limits':['No attaining53-cost factorization.','No unrestricted native-circuit lower bound.','Changed bulk, shared readers, changed codes, nonzero copied frames and different callers remain outside scope.','No new kappa.'],
         'attribution':'BIT lane supplies actual R/K reconstruction, support-span model and E8 capacities. Root supplies generalized-support intersection bound, full <=52 profile census, equality rejection and pressure transfer.'}
    out=json.loads(json.dumps(out));path=HERE/'OVERCOMPLETE-PRESSURE.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'receipt mismatch')
    print(out['status'])
    print(f'340260 profiles; reader cost>=53; three-bulk pressure>{float(pressure):.8f}>D63; controls PASS')

if __name__=='__main__':main()
