#!/usr/bin/env python3
"""Exact raw AB rolling residual and actual native ADDRESS impulse control.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
from mutable_rolling_search import I,Z,N,c,add,mul,mm,flip,ng,show
from physical_code import actual_routes,serial,bits

HERE=Path(__file__).resolve().parent
BASE=Path('/Users/ross/git/math')
RAW=BASE/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
CODE=BASE/'.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/recursive/BIT-THREE-COPY-INPUT-WORD.json.gz'

def need(p,m):
    if not p:raise RuntimeError(m)

def mv(A,v,p):return tuple(sum(a*b for a,b in zip(row,v))%p for row in A)
def mod(A,p):return [[x.numerator*pow(x.denominator,-1,p)%p for x in row]for row in A]

def impulse(raw,rows,pin):
    rho,P,_=actual_routes(raw);prime=101;m=15
    for i,a in enumerate(rho):
        need(sha256(json.dumps(serial(a),separators=(',',':')).encode()).hexdigest()==pin['actual_native_geometry']['ports'][i]['rho_sha256'],
             'actual upstream Weyl-BFS rho agrees with freshly checked C511 native receipt')
    r=[mod(a,prime)for a in rho];ps=[mod(a,prime)for a in P]
    q=0;v=(1,)+(0,)*(m-1);outputs=[set()for _ in range(111)]
    def toggle(j,z):
        if z in outputs[j]:outputs[j].remove(z)
        else:outputs[j].add(z)
    # phi=N+C1*N*C0, acting on bank0's x coefficient after the final
    # FULL N is factored off. C0 is the actual scalar core-chart code.
    p0=mv(ps[q],v[:8],prime)+(0,)*7
    h0=tuple((a-b)%prime for a,b in zip(v,p0))
    toggle(q,h0+p0)
    middle=[]
    for k in range(111):
        if not(rows[k]>>q)&1:continue
        tail=mv(ps[k],v[:8],prime)+(0,)*7
        head=tuple((a-b)%prime for a,b in zip(v,tail))
        middle.append((k,mv(r[k],head,prime),mv(r[k],tail,prime)))
    for dest,row in enumerate(rows):
        for k,h,t in middle:
            if(row>>k)&1:toggle(dest,mv(r[dest],h,prime)+mv(r[dest],t,prime))
    bad=[(j,z)for j,zs in enumerate(outputs)for z in sorted(zs)if any(z[m:])]
    need(bad,'raw AB three-call word fails terminal head/tail-free decoding on an actual input impulse')
    port,at=bad[0]
    packed=[[[*a]for a in sorted(zs)]for zs in outputs]
    # Any invertible head/tail-separate ADDRESS code preserves the subspace
    # of VALUE impulses with tail ADDRESS0. A nonzero output outside it is
    # therefore a concrete control against the required free-decoder code.
    return {'odd_ADDRESS_field':prime,'input_port':q,'input_HEAD':list(v),'input_TAIL':[0]*m,
            'operator':'N+C1*N*C0, the bank0<-bank0 block of N_global*R3',
            'nonzero_output_impulses':sum(map(len,outputs)),'output_impulses_with_nonzero_TAIL':len(bad),
            'first_witness':{'port':port,'HEAD':list(at[:m]),'TAIL':list(at[m:]),'VALUE_coefficient_mod2':1},
            'complete_output_sha256':sha256(json.dumps(packed,separators=(',',':')).encode()).hexdigest(),
            'conclusion':'This block is not head/tail-separate. A terminal invertible code from the admitted head/tail-separate ADDRESS/port alphabet cannot make this raw rolling word a full query on both arbitrary banks.'}

def receipt(write=False):
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','R438 scientific input pin')
    need(sha256(CODE.read_bytes()).hexdigest()=='ac8a6dcd5957f49eefd6fc945332b1c31afa26c48fc301d37bfb1338beea6847','C511 source word pin')
    raw=json.loads(gzip.decompress(RAW.read_bytes()));word=json.loads(gzip.decompress(CODE.read_bytes()))
    pin=json.loads((HERE/'MUTABLE-SOURCE-FIVE.json').read_bytes())
    rows=[1<<i for i in range(111)];count=0
    for op,d,s,coef,frame,phase in word['records']:
        if op==1 and phase in(21,22,23,24):
            need(d<111 and s<111 and frame==1,'literal SOURCE-only FULL code')
            count+=1
            if coef%2:rows[d]^=rows[s]
    need(count==1487 and rows==pin['C_binary_rows']and pin['C_order']==511,'independent binary SOURCE code loader')
    S=[(I,Z,mul(N,c(i)),I)for i in range(3)]
    R2=mm(flip(S[1]),S[0]);R3=mm(S[2],R2)
    a1=ng(c(1));a2=ng(c(2))
    expected=(add(I,mul(a1,c(0))),mul(N,c(1)),
              mul(N,add(add(c(2),mul(c(2),mul(a1,c(0)))),c(0))),
              add(I,mul(a2,c(1))))
    need(R3==expected,'all-column universal raw rolling F/B/F expansion')
    H={int(k):3*v for k,v in pin['coded_local_profile']['H'].items()}
    need(sum(k*v for k,v in H.items())==15183,'three C3 full local profile')
    actual=impulse(raw,rows,pin)
    out={'status':'PASS_RAW_ROLLING_BOUNDARY_WITH_ACTUAL_NATIVE_REJECTION','no_new_kappa':True,
         'scientific_pin':pin['scientific_pin'],'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in(RAW,CODE)},
         'source_code':'Actual THREE-COPY C511, not pruned A28. Each inverse call is preceded by its1487ADD free source C_i, so its physical source is G_i*x and target cross F_i*C_i*x.',
         'arbitrary_inputs':'Both111-port public banks arbitrary; no zero target fields and no restored source premise.',
         'normalized_two_call_residual':show(R2),'normalized_three_call_residual':show(R3),
         'exact_three_call_equation':'R3=[[I+a1*C0,N*C1],[N*(C2+C2*a1*C0+C0),I+a2*C1]], a_i=N*C_i*N.',
         'unclosed_diagonal_terms':['I+a1*C0','I+a2*C1'],
         'neighbor_cancellation_obstruction':{
             'hypothesis':'a_(i+1)*C_i=I, i.e. C_(i+1)=N*C_i^-1*N',
             'native_freshness':'C_i commutes G_(i+1), and C_(i+1) commutes F_(i+1)=N*G_(i+1).',
             'derivation':'Commutation with F_(i+1), substitution and [C_i,G_(i+1)]=0 imply [C_i,N]=0.',
             'control':'The source-bound C511 native receipt has an actual nonzero rational coefficient witnessing [C_i,N]!=0. Thus exact neighbor cancellation cannot occur for the unchanged fresh-stage code family.',
             'scope':'Only the displayed exact neighbor-cancellation mechanism is excluded; other joint free code gates or actual code relations remain outside this written argument.'},
         'actual_raw_word_control':actual,
         'failed_candidate_invoice':{'H':H,'rank_mass':15183,'ordinary_helper_occurrences':1314,
             'ordinary_helper_width':8,'private_peak':1,'private_COPY_rank':9,'public_width':22,
             'arithmetic_deficit_if_operator_had_closed':213,
             'admission':'REJECTED: actual operator has nonzero source/target remnants. The213 number is only a failed-candidate cost diagnostic; no public FULL coverage or positive moment is claimed.'},
         'limits':['One actual finite ADDRESS-field impulse is a destructive counterexample to this raw word, not an all-caller lower bound.','The universal F/B/F equations hold on every VALUE column without using a source-code polynomial relation.','Chronological whole-helper owners, source/tape lowering and rounded error remain independent gates.'],
         'attribution':'Pinned C511 source code/COPY word is predecessor work. This lane supplies the exact inverse, rolling equations and independently loaded actual chart impulse.'}
    out=json.loads(json.dumps(out));p=HERE/'MUTABLE-ROLLING-BOUNDARY.json'
    if write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved rolling-boundary receipt differs')
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();o=receipt(a.write)
    print(o['status']);print('actual bad TAIL impulses',o['actual_raw_word_control']['output_impulses_with_nonzero_TAIL'])
