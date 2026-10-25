#!/usr/bin/env python3
"""Close the equality case of the ten-term R429 cold-factor floor55.

The all-coset theorem remains the named premise, not a native reader theorem.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json
from cold_cosets import bits,bxor,inverse2,rank2,need
from cold_factor_search import qrank

HERE=Path(__file__).resolve().parent

def receipt():
    paths=[HERE/'READOUT-FLOOR.json',HERE/'COLD-COSETS.json',HERE.parent/'cold-reader/NINE-TERM-FLOOR.json']
    src,cosets,nine=[json.loads(p.read_text())for p in paths]
    R,K,roots=src['R'],src['K'],src['root_lines']
    code=[0]
    for r in R:code += [d^r for d in code]
    lookup={word:i for i,word in enumerate(code)}
    M=[bxor(R[j]for j in bits(k))for k in K]
    need(all((M[i]>>j&1)==(M[j]>>i&1)for i in range(111)for j in range(111)),
         'actual M symmetry permits transpose of full-rank factor side')
    target=nine['support_strata'][1]['rank7_rows']
    normals=[row['normal']for row in target]
    B=[sum(((k&row['mask']).bit_count()%2)<<p for p,k in enumerate(K))for row in target]
    need(set(B)==set(R)and rank2(B)==9,'all nine physical special targets form a basis of D')
    need(all(all(sum(x*y for x,y in zip(n,q))**2!=sum(x*x for x in n)*sum(y*y for y in q)
                 for q in roots)for n in normals),
         'no special target normal line is a live source root line')
    Tcols=[row['mask']for row in target]
    T=[sum((Tcols[j]>>i&1)<<j for j in range(9))for i in range(9)]
    inv=inverse2(T);C=[bxor(R[j]for j in bits(row))for row in inv]
    need([bxor(C[j]for j in range(9)if B[j]>>p&1)for p in range(111)]==M,'exact dual map for this M')
    for lam in range(512):
        if lam.bit_count()<2:continue
        word=bxor(B[j]for j in bits(lam))
        need(word in lookup and word not in B and qrank(roots[p]for p in bits(word))==8,
             'every weight>=2 target-basis combination spans8')
    proj=[]
    for n in normals:
        nn=sum(x*x for x in n)
        proj.append([[nn*x-sum(a*b for a,b in zip(n,q))*y for x,y in zip(q,n)]for q in roots])
    need(all(qrank(p[k]for k in bits(c))==7 for c,p in zip(C,proj)),'exact base pairing tariff63')
    unit_cases=[];hist=Counter()
    for a in range(111):
        z=1<<a
        costs=[qrank(p[k]for k in bits(c^z))for c,p in zip(C,proj)]
        need(all(v in(6,7)for v in costs),'all actual unit-update pairings are6 or7')
        chosen=[i for i,v in enumerate(costs)if v<7]
        for i in sorted((i for i in range(9)if i not in chosen),key=lambda i:costs[i]):
            if len(chosen)>=2:break
            chosen.append(i)
        lam=sum(1<<i for i in chosen)
        best=1+sum(costs[i]if lam>>i&1 else 7 for i in range(9))
        # Independent exhaustive check of all502 non-special target choices.
        brute=min(1+sum(costs[i]if b>>i&1 else 7 for i in range(9))
                  for b in range(512)if b.bit_count()>=2)
        need(best==brute and best>=63,'all502 generic targets for this actual unit')
        hist[best]+=1;unit_cases.append({'unit':a,'updated_pairing_ranks':costs,
                                       'minimum_generic_target_bill':best,'attaining_lambda':lam})
    need(hist==Counter({63:1,64:110}),'all111 unit cases')
    return {'status':'PASS_EVERY_TEN_TERM_SCALAR_COLD_FACTOR_PAIRING_TARIFF_GE56',
        'scientific_pin':src['scientific_pin'],'no_new_kappa':True,
        'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in paths},
        'actual_M_is_symmetric':True,'same_physical_source_target_code_D':True,
        'special_target_basis_rank':9,'all_special_normals_absent_from_live_root_lines':True,
        'all502_non_special_target_combinations_have_geometric_rank':8,
        'exact_unit_cases':unit_cases,'unit_generic_minimum_bill_histogram':dict(sorted(hist.items())),
        'optimizations_independently_checked':111*502,
        'conditional_premises':['The all-coset low-span uniqueness theorem and its E8 parabolic reduction from COLD-COSETS.md/json.',
                                'The exact nine-term pairing floor63 from the source-bound two-sided normal census.'],
        'proof':'The prior all-coset argument gives ten-term tariff>=55. If both factor ranks are9 every term pairs spans>=7, giving>=60. Otherwise orient the full-rank side as ten independent source readers; exact M symmetry justifies transposing if needed. Their span contains D with quotient dimension1, hence at most one reader has geometric rank<=6. The sum of source dimensions is>=64. Duplicate targets merge by projected-rank subadditivity to a nine-term factor of bill>=63. Otherwise distinct target directions lie in D and permit at most nine cold discounts, at most1 each. Equality55 therefore forces source ranks1,7x9 and all nine special target directions plus one generic. The rank1 source is an actual live unit. If it is attached to a special target it receives no cold discount, because that target normal is not any live root line, so the bill is>=56. If attached to the generic target, use the nine special targets as a basis: every other source has the unique form C_i+lambda_i unit_a, and the generic target is sum lambda_i B_i with lambda weight>=2. The exact111-unit by502-generic-target enumeration has minimum63, ruling out equality55. Thus every ten-term scalar factor has integer pairing bill>=56.',
        'model':'Exact binary scalar outer-product factorization KR=sum_(i=1)^10 b_i c_i^T; each nonzero term charged rational rank of the source/target root-span pairing.',
        'limits':['Not a native COPY compiler or ordinary-helper restoration theorem.',
                  'Not a bound for eleven-or-more terms, shared queries, operator coefficients or changed KR.',
                  'No new conditional exponent; whole caller/owner/rounding/tape gates remain separate.'],
        'attribution':'Root proposed the cold-target factor route and independently reviewed the equality-case argument. BIT lane supplies the complete exact unit-target enumeration and the symmetric-kernel, basis and normal certificates.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=json.loads(json.dumps(receipt()));path=HERE/'TEN-FACTOR-FLOOR56.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_bytes())==out,'saved ten-term equality-case receipt differs')
    print(out['status']);print('M symmetry; nine special target basis;111x502 exact unit targets; minimum63 excludes55')

if __name__=='__main__':main()
