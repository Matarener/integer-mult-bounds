#!/usr/bin/env python3
"""Exact E6/D6 coset certificates for the actual binary R429 reader code.

Written consequences use ordinary E8 parabolic classification and explicitly
price a separate scalar factor by rational source/target pairing rank.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE=Path(__file__).resolve().parent
BASE=Path('/Users/ross/git/math')
RAW=BASE/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
FULL=BASE/'integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz'
COMP=BASE/'.research-automation/runs/kappa-major-20261018T1330Z/bit-endpoint/BIT-FULL-COMPENSATION.json'
PRIME=65537

def need(b,m):
    if not b:raise ValueError(m)
def bits(x):
    while x:
        z=x&-x;yield z.bit_length()-1;x^=z
def bxor(xs):
    z=0
    for x in xs:z^=x
    return z
def rank2(rows):
    b={}
    for x in rows:
        while x:
            j=x.bit_length()-1
            if j in b:x^=b[j]
            else:b[j]=x;break
    return len(b)
def inverse2(rows):
    n=len(rows);a=[row|(1<<(n+i))for i,row in enumerate(rows)]
    for j in range(n):
        p=next(i for i in range(j,n)if a[i]>>j&1)
        a[p],a[j]=a[j],a[p]
        for i in range(n):
            if i!=j and a[i]>>j&1:a[i]^=a[j]
    need([r&((1<<n)-1)for r in a]==[1<<i for i in range(n)],'binary inverse')
    return [r>>n for r in a]

def rankmod(mask,roots,stop=8):
    b={}
    for p in bits(mask):
        v=[x%PRIME for x in roots[p]]
        for k,a in sorted(b.items()):
            f=v[k]
            if f:v=[(x-f*y)%PRIME for x,y in zip(v,a)]
        k=next((i for i,x in enumerate(v)if x),None)
        if k is not None:
            f=pow(v[k],-1,PRIME);b[k]=[(x*f)%PRIME for x in v]
            if len(b)>=stop:return len(b)
    return len(b)

def receipt():
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','raw pin')
    w=json.loads(gzip.decompress(RAW.read_bytes()))
    full=json.loads(gzip.decompress(FULL.read_bytes()))['lines']
    comp=json.loads(COMP.read_bytes());roots=w['lines']
    rows=[1<<i for i in range(660)]
    for phase in('D','A'):
        for _,d,srcs in w[phase]:
            for s in srcs:rows[d]^=rows[s]
    R=[rows[h]&((1<<111)-1)for h in w['ret']]
    K=[sum(1<<j for j in col)for col in w['scatter']]
    need(R==comp['R']and K==comp['K']and rank2(R)==9,'actual rank9 factor')
    code=[0]
    for row in R:code += [x^row for x in code]
    need(min(x.bit_count()for x in code[1:])==48,'actual code distance48')
    lookup={v:k for k,v in enumerate(code)}
    # Self-pairing certificate used in the separate nine-term floor.
    Hcols=[lookup[sum((row>>j&1)<<p for p,row in enumerate(K))]for j in range(9)]
    Hrows=[sum((Hcols[j]>>i&1)<<j for j in range(9))for i in range(9)]
    dual=inverse2(Hrows)
    need(all(dual[j]>>j&1 for j in range(9)),'all nine special readers have self-pairing1')
    orth=[sum((not sum(a*b for a,b in zip(q,r)))<<p for p,r in enumerate(roots))for q in full]
    families={name:{}for name in('E6','D6')}
    for i in range(120):
        for j in range(i):
            dot=sum(a*b for a,b in zip(full[i],full[j]))
            name='E6'if abs(dot)==2 else'D6'if dot==0 else None
            if name:families[name].setdefault(orth[i]&orth[j],(i,j))
    need(len(families['E6'])==1120 and len(families['D6'])==3780,'complete A2/A1^2 normal-plane flats')
    out={};total=0
    for name,flats in families.items():
        sizes=Counter();minimum=8
        for S,pair in flats.items():
            need(rankmod(S,roots)==6,'retained root flat has rank6')
            sizes[S.bit_count()]+=1
            for d in code[1:]:
                r=rankmod(d&~S,roots,7)
                need(r>=7,'a nonzero actual codeword fits two rank<=6 flats')
                minimum=min(minimum,r);total+=1
        out[name]={'flats':len(flats),'live_support_sizes':dict(sorted(sizes.items())),
            'minimum_modular_rank_outside_flat':minimum,
            'canonical_flat_data_sha256':sha256(json.dumps(sorted((S,list(pair))for S,pair in flats.items()),separators=(',',':')).encode()).hexdigest()}
    need(total==2503900,'all4900 flat/511 nonzero codeword tests')
    # A wrong reader outside the code is actually admitted by the low-rank
    # support condition, demonstrating that code membership is essential.
    fake=(1<<0)|(1<<1)
    need(fake not in lookup and rankmod(fake,roots)<=2,'two-source non-code control')
    return {'status':'PASS_R429_LOW_RANK_FLAT_COSET_UNIQUENESS_AND_TEN_FACTOR_COLD_FLOOR55',
        'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','no_new_kappa':True,
        'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in(RAW,FULL,COMP)},
        'R':R,'K':K,'live_roots':roots,'full_E8_root_lines':full,
        'minimum_D_word_weight':48,'self_pairing_inverse_form_rows':dual,
        'all_nine_special_self_pairings':1,'families':out,
        'rank_field':PRIME,'flat_codeword_tests':total,
        'coset_theorem':'Every coset z+D contains at most one nonzero scalar readout whose source-root support has rational span<=6. E6/D6 frames are covered by the exact4900-flat certificates. Every other rank<=6 root flat has at most21 lines, so two cover at most42<48 source coordinates.',
        'nine_term_floor':'Both sides lie in D; their only span7 directions are the same nine special reader lines. In dual bases a shared label must occupy the same factor because its self-pairing is1. Pairing rank total>=72−union_of_special_labels>=63.',
        'ten_term_floor':'By Sylvester, at least one side has rank9. If both do, every term pairs two spans>=7 and total>=60. Otherwise orient the full-rank side as10 independent source readers spanning D+1: all low<=6 readers lie in its sole nonzero quotient coset, so at most one; full source-span sum>=64. The target side lies in D; generic targets span8 and special targets span7 can each discount at most1. At most9 distinct special targets occur, so total pairing-rank>=55. A duplicate target merges to9 terms without raising projected source rank and instead gives floor63.',
        'cost_model':'Exact binary scalar factorization KR=sum b_i c_i^T; term cost is at least rational rank of pairing between the source-root span U_i and target-root span V_i. This necessary tariff is not a native COPY compiler or a complete supplier.',
        'scope':['No attaining55-cost factorization or word.','The proof uses standard E8 parabolic classification and orthogonal-complement types E6/A2 and D6/A1^2, not a formal-kernel proof.','No restriction on11-or-more terms, shared native queries, operator-valued readers, changed KR or changed caller.'],
        'negative_control':'A two-source non-code word has span<=2 and violates the required outside-span condition; code membership is essential.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=json.loads(json.dumps(receipt()));path=HERE/'COLD-COSETS.json'
    if args.write:path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    else:need(json.loads(path.read_bytes())==out,'stored cold-coset receipt differs')
    print(out['status']);print('4900 E6/D6 flats;2503900 rank lower certificates; no two low-span readers in one coset; nine-term63 and ten-term55 necessary floors')
if __name__=='__main__':main()
