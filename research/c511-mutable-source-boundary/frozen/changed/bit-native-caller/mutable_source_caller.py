#!/usr/bin/env python3
"""Actual three-copy source code in a restored five-call native BIT caller.

The finite/native identity succeeds; its complete local rank deficit is-33.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
from cold_cosets import need,bits
from helper_tail_retime import plus
from kernel_entrances import parity
from old_kernel_boost import old_word,replay
from physical_code import actual_routes,mm,eye,tr,serial,mul2,rank2

HERE=Path(__file__).resolve().parent
BASE=Path('/Users/ross/git/math')
RAW=BASE/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
CODE=BASE/'.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/recursive/BIT-THREE-COPY-INPUT-WORD.json.gz'
FULL=BASE/'integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz'

def reduce_word(w):
    z=[]
    for c in w:
        if z and ((z[-1]==c=='N')or(z[-1],c)in[('C','c'),('c','C')]):z.pop()
        else:z.append(c)
    return tuple(z)

def p(*ws):
    out=set()
    for w in ws:
        w=reduce_word(w)
        if w in out:out.remove(w)
        else:out.add(w)
    return frozenset(out)

def add(a,b):return a^b
def product(a,b):return p(*(x+y for x in a for y in b))
ZERO=p();ONE=p(())
N=p(('N',));C=p(('C',));Ci=p(('c',))

def bmm(A,B):return [[add(product(A[i][0],B[0][j]),product(A[i][1],B[1][j]))for j in range(2)]for i in range(2)]
def dumpmat(A):return [[[''.join(w)or'I'for w in sorted(v)]for v in r]for r in A]

def formal():
    F=[[ONE,ZERO],[N,ONE]];B=[[ONE,N],[ZERO,ONE]];SWAP=[[ZERO,ONE],[ONE,ZERO]]
    Qc=[[product(product(N,C),N),ZERO],[product(C,N),ONE]]
    seed=bmm(SWAP,bmm(F,bmm(B,F)))
    need(seed==[[N,ZERO],[ZERO,N]],'three CLEAN calls and bank swap seed both commonN factors')
    result=bmm(F,bmm(Qc,seed))
    expected=[[product(N,C),ZERO],[ZERO,N]]
    need(result==expected,'four CLEAN plus one coded residual has N*C orientation')
    # The tempting first-coded three-call word has the wrong C*N orientation.
    first=bmm(F,bmm(B,Qc));wrong=[[ZERO,N],[product(N,C),ZERO]]
    need(first==[[ZERO,N],[product(C,N),ZERO]]and first!=wrong,'wrong-side free decoder control')
    invnorm=[[Ci,ZERO],[N,ONE]]
    preC=[[C,ZERO],[ZERO,ONE]]
    consuming=bmm(invnorm,preC)
    need(consuming==[[ONE,ZERO],[product(N,C),ONE]],'inverse source-consuming interface has N*C orientation')
    # Exact expansion of the always-source prefix update, with a fresh generic
    # code B standing for the preceding free head/tail code.
    return {'clean_F':dumpmat(F),'clean_B':dumpmat(B),'coded_F_C':dumpmat(Qc),
            'seed_after_swap':dumpmat(seed),'five_call_residual':dumpmat(result),
            'first_coded_three_call_control':dumpmat(first),
            'inverse_coded_normalized':dumpmat(invnorm),'inverse_after_free_source_C':dumpmat(consuming),
            'inverse_physical_interface':'B_C^-1 = [[G*C^-1,0],[F,G]], since F=G*N, F^2=G^2=N^2=I and F commutes C. A free source C precode gives (x,y)->(G*x,F*C*x+G*y). For one full local parent F and y=0, a free target C^-1 decoder gives (G*x,F*x).',
            'all_parameter_identity':'Gamma5 * F_clean * F_C * N_global = Gamma5 * diag(N*C,N) = T_parent * diag(C,I). The actual full parent T commutes C, so a final free physical C^-1 on bank0 gives diag(T,T).',
            'relations':'N^2=I only for the residual word. Every fresh G_t with t!=coded_stage commutes C_coded, proved below using actual rho. Full parent T commutes the head/tail-separate code C_coded.'}

def actual_geometry(raw,Crows):
    rhos,Ps,_=actual_routes(raw);I8=eye(8);Z7=[[Q(0)]*7 for _ in range(7)]
    E=[[Q(i==j and i>=8)for j in range(15)]for i in range(15)]
    H=[[Q(i==j and i<8)for j in range(15)]for i in range(15)]
    records=[]
    for p,rho in enumerate(rhos):
        P=Ps[p];K=[[I8[i][j]-P[i][j]for j in range(8)]for i in range(8)]
        G0=[K[i]+[Q(0)]*7 for i in range(8)]+[[Q(0)]*15 for _ in range(7)]
        Np=[P[i]+[Q(0)]*7 for i in range(8)]+[[Q(0)]*15 for _ in range(7)]
        Fs=[[Np[i][j]+E[i][j]for j in range(15)]for i in range(15)]
        need(mm(mm(rho,G0),rho)==E,'actual rho maps old capG0 to common freshE')
        need(mm(mm(rho,Fs),rho)==H,'actual rho maps native localFULL to common core8')
        need(mm(rho,eye(15))==mm(eye(15),rho),'actual full head/tail exchange conjugation')
        records.append({'port':p,'rho_sha256':sha256(json.dumps(serial(rho),separators=(',',':')).encode()).hexdigest(),
                        'G0_conjugate':'E_fresh7','local_FULL_conjugate':'I_core8'})
    # All C[p,q] coefficients are scalar in local coordinates. The two
    # preceding per-port conjugations prove EVERY nonzero routed coefficient
    # intertwines both G0 and localFULL, not merely a sample edge.
    edge_count=sum(v.bit_count()for v in Crows)
    need(edge_count>111,'nontrivial actual source code')
    witness=None
    for p,v in enumerate(Crows):
        for q in bits(v):
            if p==q:continue
            R=mm(rhos[p],rhos[q]);P,Qp=Ps[p],Ps[q]
            PN=[P[i]+[Q(0)]*7 for i in range(8)]+[[Q(0)]*15 for _ in range(7)]
            QN=[Qp[i]+[Q(0)]*7 for i in range(8)]+[[Q(0)]*15 for _ in range(7)]
            a,b=mm(PN,R),mm(R,QN)
            if a!=b:
                i,j=next((i,j)for i in range(15)for j in range(15)if a[i][j]!=b[i][j])
                witness={'edge':[p,q],'ADDRESS_entry':[i,j],'left':str(a[i][j]),'right':str(b[i][j])};break
        if witness:break
    need(witness is not None,'actual C does not commute commonN: wrong orientation is observable')
    return {'ports':records,'all_nonzero_C_coefficients_covered':edge_count,
            'all_stage_intertwining':'For coded stage s>=1, every rho_s,p G0,p rho_s,p=E_s and rho_s,p F_s,p rho_s,p=H8. Scalar C commutes commonE_s and H8, so routed C_s commutes G0 and F_s exactly. Fresh G_t for t>=1,t!=s is disjoint from rho_s support and commutes every coefficient. T_parent is a full exchange on all used axes and commutes every diag(rho,rho) ADDRESS adapter.',
            'commonN_noncommutation_control':witness}

def receipt(write=False):
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','actual R438 pin')
    need(sha256(CODE.read_bytes()).hexdigest()=='ac8a6dcd5957f49eefd6fc945332b1c31afa26c48fc301d37bfb1338beea6847','actual three-source-copy word pin')
    raw=json.loads(gzip.decompress(RAW.read_bytes()));coded=json.loads(gzip.decompress(CODE.read_bytes()));old=old_word(raw)
    rows,codebill=replay(coded,raw);oldrows,oldbill=replay(old,raw)
    need(all(rows[h]=={h:1}for h in range(222,660))and not rows[660],'all438 arbitrary helper and zero private integer rows restored')
    need(all(all(j<111 for j in row)for row in rows[:111]),'coded SOURCE has no target/helper contamination overZ')
    Crows=parity(rows[:111]);need(rank2(Crows)==111 and rank2([r^(1<<i)for i,r in enumerate(Crows)])==9,'actual C is invertible with rank9 scalar defect')
    expected=[1<<j for j in range(660)]+[0]
    expected[:111]=Crows
    for i in range(111):expected[111+i]^=Crows[i]
    need(parity(rows)==expected,'every661 binary endpoint column: SOURCE Cx,targety+Cx,helpersidentity')
    literal=[];Cr=[{i:1}for i in range(111)]
    for op,d,s,c,f,ph in coded['records']:
        if op==1 and ph in(21,22,23,24):
            need(d<111 and s<111 and f==1,'actual SOURCE-only FULL code ADD')
            literal.append([d,s,c]);Cr[d]=plus(Cr[d],Cr[s],c)
    need(Cr==rows[:111]and len(literal)==1487,'actual1487ADD integer code equals SOURCE endpoint')
    for d,s,c in reversed(literal):Cr[d]=plus(Cr[d],Cr[s],-c)
    need(Cr==[{i:1}for i in range(111)],'literal inverse SOURCE decoder overZ')
    closed,invbill=replay(coded,raw,rows,True)
    need(closed==[{i:1}for i in range(660)]+[{}],'every661 coded local column literal integer roundtrip')
    invrows,rawinvbill=replay(coded,raw,back=True)
    need(all(invrows[h]=={h:1}for h in range(222,660))and not invrows[660],
         'raw inverse all438 arbitrary helper and private integer restoration')
    need(all(all(j<111 for j in row)for row in invrows[:111]),'raw inverse SOURCE has no helper/target contamination')
    invparity=parity(invrows)
    need(all(invparity[111+i]==(1<<(111+i))^(1<<i)for i in range(111)),
         'raw inverse target cross is identity independent of source C on every column')
    need(codebill['H']=={1:1325,2:1342,3:79,4:44,5:102,6:11,7:9}and codebill['COPYs']==3,'actual C3 entire native profile')
    order=0;power=[1<<i for i in range(111)]
    for i in range(1,512):
        power=mul2(Crows,power)
        if power==[1<<j for j in range(111)]:order=i;break
    need(order==511,'actual C order511 distinct from later pruned A order28')
    H=Counter({int(k):4*v for k,v in oldbill['H'].items()});H.update(codebill['H'])
    n=2;V=111;L=5;m=1+7*L;helpers=5*438;private=4*63+3
    mass=sum(k*v for k,v in H.items());public=n*V*m;helper_mass=helpers*8
    need(mass==25545 and public+helper_mass-mass==n*V-private==-33,'complete native coverage deficit before owner padding')
    geom=actual_geometry(raw,Crows);ident=formal()
    recipe={'format':'five-stage-two-bank-C3-native-caller-v1','public_banks':2,'ports_per_bank':111,'parent_width':m,
            'calls':[{'stage':0,'kind':'CLEAN_F','source_bank':0,'target_bank':1,'helpers':'fresh438_0'},
                     {'stage':1,'kind':'CLEAN_B','source_bank':1,'target_bank':0,'helpers':'fresh438_1'},
                     {'stage':2,'kind':'CLEAN_F','source_bank':0,'target_bank':1,'helpers':'fresh438_2'},
                     {'cut':'after stage2','kind':'ordinary bankSWAP','XOR_ADDs':333},
                     {'stage':3,'kind':'C3_CODED_F','source_bank':0,'target_bank':1,'helpers':'fresh438_3'},
                     {'stage':4,'kind':'CLEAN_F','source_bank':0,'target_bank':1,'helpers':'fresh438_4'}],
            'final_source_decoder':{'bank':0,'coded_stage':3,'inverse_ADDs':[[d,s,-c]for d,s,c in reversed(literal)],
                                    'address_adapter':'Each source ADD is routed by actual rho_(3,d)*rho_(3,s), acting separately on head and tail; parentFULL commutes every adapter.'}}
    out={'status':'PASS_ACTUAL_C3_RESTORED_FIVE_CALL_NATIVE_WORD_ZERO_RATE_REJECTED','no_new_kappa':True,
         'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in(RAW,CODE,FULL)},
         'C_binary_rows':Crows,'C_rank':111,'C_defect_rank':9,'C_order':511,'C_source_CODE_ADDs':len(literal),
         'coded_local_profile':codebill,'coded_literal_inverse':invbill,'clean_local_profile':oldbill,
         'raw_inverse_local_profile':rawinvbill,
         'actual_native_geometry':geom,'formal_all_VALUE_columns':ident,'recipe':recipe,
         'complete_local_call_histogram':dict(sorted(H.items())),'native_query_count':sum(H.values()),'rank_mass':mass,
         'ordinary_helper_occurrences':helpers,'ordinary_helper_residual_width':8,'private_fields_peak':1,
         'private_COPY_rank':private,'public_progress':public,'ordinary_helper_progress':helper_mass,
         'uncovered_deficit_before_owner_padding':-33,'source_decoder_scalar_ADDs':1487,'ordinary_bank_SWAP_ADDs':333,
         'complete_local_scalar_ADDs_including_decoder_and_SWAP':4*oldbill['ADDs']+codebill['ADDs']+1487+333,
         'source_consuming_inverse_contract':{
             'input':'111 arbitrary public source streams x,111 caller-supplied zero target streams,438 arbitrary dirty helpers and one internal zero private field.',
             'word':'Free1487ADD source code C; literal inverse of frozen C3 word; free1487ADD target decoder C^-1 at a full local parent output.',
             'output':'Target111 streams equal exact nativeFULL F*x. Original source bank contains cap-progress G*x. All438 ordinary helpers obey their width8 native residual and the internal private field is erased.',
             'native_query_histogram':codebill['H'],'rank_mass':5061,'internal_COPY_rank':3,
             'additional_zero_output_fields':111,'unrestored_consumed_source_fields':111,
             'covered_independent_public_full_query_rank':111*8,
             'ordinary_helper_rank':438*8,'deficit_if_source_remnant_uncredited':111*8+438*8-5061,
             'gate':'The caller must price111 zero output fields and consume/recycle the111 G*x source remnants. The same111 arbitrary input streams cannot be credited twice as independent FULL and cap query families. No reversible restored-source or restored-zero-buffer interface follows from this one-carrier map.'},
         'contract':'Two arbitrary public DATA banks receive exact parentFULL native BIT queries; all2190 independent ordinary helper occurrences retain their exact dirty-helper return contract and one zero private field is literally erased for every COPY. Source code is removed by its actual1487ADD inverse at a full parent cut. Local scalar identities are verified on every660 public/ordinary column and the zero private column; native composition is a universal noncommutative F2 operator identity with actual rational rho intertwiners.',
         'negative_controls':['First-coded three-call replacement has C*N rather than N*C and fails the free-decoder orientation.','An actual source-code edge does not commute commonN, so the failed substitution is not merely syntactic.'],
         'limits':['No positive-rate moment can be claimed from the D=-33 local invoice.','The old CLEAN R438 native child implementation remains a pinned imported premise.','No chronological owner, rounded child-defect or physical source/tape lowering theorem is supplied.','This finite/source-bound native binding is not a formal-kernel proof.'],
         'attribution':'C3 word and source-code/COPY ancestry are pinned predecessor work. This lane independently replays every signed local column, identifies actual order511 C, proves the mutable-source five-call identity with actual rho and supplies the complete failed budget.'}
    out=json.loads(json.dumps(out));p=HERE/'MUTABLE-SOURCE-FIVE.json'
    if write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved mutable-source certificate differs')
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();o=receipt(a.write)
    print(o['status']);print('C order511; fivecallH',o['complete_local_call_histogram'],'mass',o['rank_mass'],'private',o['private_COPY_rank'],'D',o['uncovered_deficit_before_owner_padding'])

if __name__=='__main__':main()
