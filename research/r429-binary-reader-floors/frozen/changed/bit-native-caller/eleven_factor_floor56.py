#!/usr/bin/env python3
"""Complete eleven-term scalar cold-factor floor56, with explicit premises.

Apache-2.0. Substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement
from pathlib import Path
import argparse
import json
from cold_cosets import bxor,bits,need

HERE=Path(__file__).resolve().parent

def receipt():
    paths=[HERE/f for f in('READOUT-FLOOR.json','COLD-COSETS.json','TEN-FACTOR-FLOOR56.json','UNIT-COLD-EXTENSION.json')]
    src,cosets,ten,units=[json.loads(p.read_text())for p in paths]
    need(ten['status']=='PASS_EVERY_TEN_TERM_SCALAR_COLD_FACTOR_PAIRING_TARIFF_GE56','ten-term premise')
    need(units['status']=='PASS_TWO_UNIT_ELEVEN_TERM_SCALAR_COLD_PAIRING_TARIFF_GE56','two-unit premise')
    R,K,roots,full=src['R'],src['K'],src['root_lines'],cosets['full_E8_root_lines']
    code=[0]
    for r in R:code += [d^r for d in code]
    M=[bxor(R[j]for j in bits(k))for k in K]
    need(all((M[i]>>j&1)==(M[j]>>i&1)for i in range(111)for j in range(111)),
         'actual symmetry for rank-case transposition')
    caps=[];small=Counter();other_min=111
    for q in full:
        cap=sum((not sum(a*b for a,b in zip(q,p)))<<j for j,p in enumerate(roots))
        live=next((j for j,p in enumerate(roots)if p==q),None)
        expected=cap if live is None else M[live]
        need(expected in code,'actual cap or affine-live reader in D')
        for d in code[1:]:
            outside=d&~cap;w=outside.bit_count()
            if d!=expected:other_min=min(other_min,w)
            if w<=3:
                small[w]+=1
                need(d==expected and outside==(0 if live is None else 1<<live),
                     'only old cap or live affine reader can toggle into this E7 cap')
        caps.append({'normal':q,'live_coordinate':live,'cap':cap,'unique_D_word_with_outside_weight_le3':expected})
    need(small==Counter({0:9,1:111})and other_min==18,'complete120x511 near-cap certificate')
    capacities=[0,1,3,6,12,20,36]
    profiles=[p for p in combinations_with_replacement(range(1,7),3)
              if sum(capacities[d]for d in p)>=48]
    low_min=min(map(sum,profiles));need(low_min==11,'three-low support-capacity lower bound')
    return {'status':'PASS_EVERY_ELEVEN_TERM_SCALAR_COLD_FACTOR_PAIRING_TARIFF_GE56',
        'scientific_pin':src['scientific_pin'],'no_new_kappa':True,
        'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in paths},
        'near_cap_cases':120*511,'all120_caps':caps,'small_outside_weight_histogram':dict(sorted(small.items())),
        'other_outside_weight_minimum':other_min,'E8_rank_le6_line_capacities':capacities,
        'three_low_rank_capacity_feasible_profiles':profiles,'minimum_three_low_dimension_sum':low_min,
        'rank_cases':['By Sylvester the rank pair is(9,9),(9,10),(9,11),(10,9),(10,10),or(11,9).',
                      'Any duplicate source or target direction merges without raising pairing bill; a resulting<=10-term factor has bill>=56.',
                      'Both rank9: every term has two spans>=7, bill>=66.',
                      'Rank9/10: orient rank9 as targets; at most one low source by coset uniqueness, so source-span sum>=71 and at most9 cold discounts, bill>=62.',
                      'Rank9/11: independent sources span D plus quotient dimension2. At most3 lows. If<=2, source-span sum>=65, bill>=56. If3, their three distinct nonzero quotient classes sum to0; the actual source sum is a nonzero D word by independence. Weight48 and root capacities force low dimension sum>=11; eight other sources have rank>=7, so source-span sum>=67 and bill>=58.',
                      'Rank10/10: choose on each side the direct-sum code projection D+<z> ->D along its actual low row z (and similarly w). Thus both low tails have zero D component and the nine high/high projected terms alone factor rank9 M. A bill<=55 forces exactly9 high/high terms and2 distinct low tails. If the same low direction occurs twice it merges to<=10; if a low/low term occurs the other10 terms are high/high and already cost>=60. Let the low dimensions be a,b. Each low/high tail costs>=a-1 or b-1. The9 high/high terms cost>=54, so a+b<=3. The unit/unit case is in UNIT-COLD-EXTENSION. Only unit/rank2 remains.'],
        'unit_rank2_case':'A rank2 scalar reader has at most3 root coordinates. Toggling it into a nonzero D word leaves weight>=45. Any rank7 root-spanned flat other than E7 has at most42 lines, so a rank7 result must lie in one of the120 E7 caps. The complete near-cap certificate shows every new generic hyperplane code label is f_p for a coordinate p in the rank2 readout support, hence there are at most3 such labels. The low-tail minimum is1, so all9 high/high terms in a putative bill<=55 must have both spans7. Orient the unit extension as sources. The638 source-hyperplane bases in UNIT-COLD-EXTENSION have9 generic target dual code labels; at most3 can become rank7 in the rank2 extension, a contradiction.',
        'premises':['All-coset low-span uniqueness in COLD-COSETS, with its explicit E8 parabolic reduction.',
                    'Root-system capacities M(d)=(1,3,6,12,20,36) for d<=6 and maximum42 for a rank7 subsystem other than E7. These follow the standard finite E8 parabolic classification; not a formal-kernel certificate.',
                    'Ten-term floor56 and the exact638 unit-extension dual bases, each with separate reproducible certificates.'],
        'model':'Exact binary scalar factorization KR=sum_(i=1)^11 b_i c_i^T, with arbitrary binary factors. Every term charged the rational rank of its source/target root-span pairing.',
        'limits':['No native COPY/gathering compiler, source/target cut admission or arbitrary-dirty helper restoration.',
                  'No restriction on12-or-more terms, shared native queries, operator coefficients, changed KR or changed caller.',
                  'No new kappa, precision theorem, whole owner schedule or physical source/tape realization.'],
        'review_targets':['Check duplicate-factor projected-rank subadditivity.','Check the three distinct nonzero quotient classes in the rank9/11 case and independence preventing zero sum.','Check low-tail classification and a+b<=3 in rank10/10.','Check the standard rank7 non-E7 capacity42 and the exact near-cap certificate.'],
        'attribution':'Root proposed the cold-contact and two-unit repair routes and requested all rank cases. BIT lane supplies the coset certificates, equality-case exclusions, rank-case proof and exact near-cap data.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=json.loads(json.dumps(receipt()));path=HERE/'ELEVEN-FACTOR-FLOOR56.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_bytes())==out,'saved eleven-factor receipt differs')
    print(out['status']);print('all Sylvester rank cases;61320 near-cap cases; explicit finite-root premises')

if __name__=='__main__':main()
