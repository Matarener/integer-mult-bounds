#!/usr/bin/env python3
"""Literal six-bank nested caller prefix with its paid source continuations.

All six input columns are independent. Four public rows finish; two pivot
rows retain the displayed H/L. This is an expensive first recursive prefix,
not a claimed complete supplier or a promised constant terminal tail.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import argparse
import hashlib
import json
import sys
sys.dont_write_bytecode = True
import free_ops as F
from plane_group import Algebra
from nested_prefix import skeleton, probe

HERE = Path(__file__).resolve().parent


def ec(z):
    return F.add(F.mono((), z[0]), F.mono((0,), z[1]))


def formal_word():
    q,n=2,6
    _,ops=skeleton(q,(1,0))
    choices=probe(q,(1,1),(1,0))
    F.need(all(c is not None for _,_,c in choices), 'every normalized source retraction exists')
    M=F.eye(n);Mi=F.eye(n);s=0
    def app(A,Ai):
        nonlocal M,Mi
        F.need(F.mm(A,Ai)==F.mm(Ai,A)==F.eye(n),'formal event inverse')
        M=F.mm(A,M);Mi=F.mm(Mi,Ai)
    def a(d,src,c):app(F.es(n,d,src,c),F.es(n,d,src,F.neg(c)))
    a(5,3,F.I) # inverse of the final constant c-basis change
    source_rows=[]
    for typ,d,src,z in ops:
        if typ=='a':a(d,src,ec(z))
        elif typ=='s':
            P=F.eye(n);P[d],P[src]=P[src],P[d];app(P,P)
        else:
            s+=1;u=choices[s-1][2][1]
            cont=(s!=7 and any(v[1] for v in u))
            # G E(N) G^-1=E(N), because source functional is fixed,
            # target differs from source, and every coefficient lies in E.
            for j,v in enumerate(u):
                if j!=src and v!=(0,0):a(j,src,F.neg(ec(v)))
            P=F.mono((s,))
            if cont:P=F.mul(F.N,P)
            A=F.mm(F.unary(n,src,P),F.es(n,d,src,F.N))
            Ai=F.mm(F.es(n,d,src,F.neg(F.N)),F.unary(n,src,F.inv(P)))
            app(A,Ai)
            for j,v in enumerate(u):
                if j!=src and v!=(0,0):a(j,src,ec(v))
            source_rows.append({'stage':s,'src':src,'dst':d,
                                'u':[[str(x),str(y)]for x,y in u],
                                'source_code':('N P'if cont else'P')+str(s),
                                'continued':cont})
    a(5,3,F.neg(F.I))
    F.need(F.mm(M,Mi)==F.mm(Mi,M)==F.eye(n),'formal literal inverse both orders')
    public=(0,2,4,5);pivots=(1,3)
    for i in public:
        F.need(M[i]==[F.N if j==i else F.Z for j in range(n)],
               'every independent finished public row is exactly N times its own input')
    H=[[M[i][j]for j in pivots]for i in pivots]
    L=[[M[i][j]for j in public]for i in pivots]
    return M,Mi,source_rows,H,L


def evaluate(q,A):
    out=A.Z
    for w,c in q.items():
        term=A.mono(coefficient=c)
        for k in w:
            op=A.n(0)if k==0 else A.swap(0,abs(k))
            term=A.mul(term,A.inv(op)if k<0 else op)
        out=A.add(out,term)
    return out


def physical_word(wrong_continuation_sign=False):
    banks,planes=6,8
    A=Algebra(planes);M=A.eye(banks);Mi=A.eye(banks);events=[];s=0
    _,ops=skeleton(2,(1,0));choices=probe(2,(1,1),(1,0))
    def app(B,Bi,e):
        nonlocal M,Mi
        F.need(A.mm(B,Bi)==A.mm(Bi,B)==A.eye(banks),'physical event inverse')
        M=A.mm(B,M);Mi=A.mm(Mi,Bi);events.append(e)
    def add(d,src,c,label):
        if not c:return
        app(A.es(banks,d,src,A.mono(coefficient=c)),
            A.es(banks,d,src,A.mono(coefficient=-c)),
            {'kind':'ADD','dst':d,'src':src,'coefficient':str(c),'label':label})
    def unary(i,g,kind,label):
        B=A.eye(banks);B[i][i]=g;Bi=A.eye(banks);Bi[i][i]=A.inv(g)
        ((bits,p),c),=g.items()
        F.need(c in(-1,1),'native/ADDRESS operator is a Gaussian unit word')
        op={'sign':int(c),'native_blocks':[j for j in range(planes)if bits>>j&1],
            'block_permutation':list(p),'native_arity':A.native_arity(g)}
        app(B,Bi,{'kind':kind,'bank':i,'operator':op,'label':label})
    add(5,3,Fraction(1),'raw c-basis inverse')
    unary(1,A.n(0),'NATIVE','shared input N exposure')
    add(2,1,Fraction(1),'shared input fanout b1+=N*t')
    unary(1,A.inv(A.n(0)),'NATIVE','shared input N inverse')
    for typ,d,src,z in ops:
        if typ=='a':
            if z[1]:
                F.need(z[0]==0 and ((s==0 and d==2 and src==1)or(s==7 and d==2 and src==1)),
                       'only the explicitly compiled shared input/output N-ADDs occur')
                continue
            add(d,src,z[0],'scalar nested response bridge')
        elif typ=='s':
            B=A.eye(banks);B[d],B[src]=B[src],B[d]
            app(B,B,{'kind':'BANK_SWAP','banks':[d,src],'label':'nested response permutation'})
        else:
            s+=1;u=choices[s-1][2][1];cont=s!=7 and any(v[1]for v in u)
            for j,(a,b)in enumerate(u):
                if j!=src:add(j,src,-a,f'query{s} scalar source-retraction entrance')
            unary(src,A.n(0),'NATIVE',f'query{s} source common')
            for j,(a,b)in enumerate(u):
                if j!=src:add(j,src,-b,f'query{s} entrance fanout from existing source N')
            add(d,src,Fraction(1),f'query{s} delivery')
            unary(src,A.swap(0,s),'ADDRESS_OR_UNIT',f'query{s} source swap')
            for j in range(banks):
                if j!=src:
                    unary(j,A.n(s),'NATIVE',f'query{s} target fresh'if j==d else f'query{s} inactive fresh progress')
            if cont:
                for j,(a,b)in enumerate(u):
                    if j!=src:
                        coefficient=b if wrong_continuation_sign else -b
                        add(j,src,coefficient,f'query{s} pre-continuation fanout')
                unary(src,A.n(0),'NATIVE',f'query{s} retained source N continuation')
            for j,(a,b)in enumerate(u):
                if j!=src:add(j,src,a,f'query{s} scalar source-retraction exit')
            if not cont and any(v[1]for v in u):
                F.need(s==7 and u[2][1]==1 and all(not v[1]for j,v in enumerate(u)if j!=2),
                       'last post-N fanout cancels exactly the final shared output isolation')
    add(5,3,Fraction(-1),'final c-basis change')
    F.need(A.mm(M,Mi)==A.mm(Mi,M)==A.eye(banks),'all six physical columns, literal inverse in both orders')
    return A,M,Mi,events


def prove():
    M,Mi,sources,H,L=formal_word()
    A,physical,physical_inverse,events=physical_word()
    fullfresh=A.prod(*(A.n(j)for j in range(1,8)))
    expected=[[A.mul(fullfresh,evaluate(x,A))for x in row]for row in M]
    F.need(physical==expected,'actual N-plane/ADDRESS event list binds every free-operator coefficient and its phase')
    E=A.mul(fullfresh,A.n(0));public=[0,2,4,5]
    for i in public:
        F.need(physical[i]==[E if j==i else A.Z for j in range(6)],'physical full native public endpoints')
    _,mutant,_,_=physical_word(True)
    F.need(mutant!=physical,'wrong continuation sign is detected on the complete matrix')
    Hhist=Counter(e['operator']['native_arity']for e in events if e['kind']=='NATIVE')
    F.need(Hhist=={2:47},'complete prefix histogram')
    touches={i:[]for i in range(6)}
    for index,e in enumerate(events):
        if e['kind']=='ADD':active=(e['dst'],e['src'])
        elif e['kind']=='BANK_SWAP':active=e['banks']
        else:active=(e['bank'],)
        # Every fresh progress is paid; its label lets an independent
        # scheduler delay it only across an exact commutation contract.
        if e['kind']=='NATIVE'and('target fresh'in e['label']or'inactive fresh progress'in e['label']):continue
        for i in active:touches[i].append(index)
    return {
        'status':'PASS_EXACT_NESTED_SIX_BANK_PREFIX_FOUR_PUBLIC_TWO_PIVOTS',
        'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
        'domain':'Every f>=1 under exact Ni^2=-I, commuting distinct native planes and ADDRESS plane permutations; six arbitrary independent input fields. Free-operator proof allows arbitrary independent invertible Pi.',
        'changed_premise':'Repeated first-query response replacement with coupled source-retraction columns in a fixed two-dimensional E-plane; genuine common-N source continuations are retained at stages3,4,6.',
        'source_sequence':[e['src']for e in sources],'target_sequence':[e['dst']for e in sources],
        'source_retractions':sources,'events':events,
        'complete_matrix':F.sm(M),'complete_inverse':F.sm(Mi),
        'public_rows':public,'pivot_rows':[1,3], 'pivot_H':F.sm(H),'public_L':F.sm(L),
        'physical_matrix':[[A.serial(x)for x in row]for row in physical],
        'physical_inverse':[[A.serial(x)for x in row]for row in physical_inverse],
        'histogram':dict(Hhist),'native_rank_mass':94,'ambient_arity':16,'public_banks_including_pivots':6,
        'stock_if_pivots_finish':96,'D_before_pivot_tail':2,
        'query_count':7,'source_continuation_count':3,'shared_input_N_calls':2,
        'mandatory_nondeferred_touches':touches,
        'inverse':'Reverse every physical event; negate ADDs, invert each signed native/ADDRESS operator, reverse swaps. Checked both matrix orders without any initialized field.',
        'folds':['All pre-N retraction fanouts use the already-paid source N query.',
                 'At a retained continuation, N(NP)=-P makes every N-valued exit a scalar fanout before the continuation.',
                 'Final post-N b1 fanout cancels the shared output isolation after the final bank swap.'],
        'limits':['This is a six-bank PREFIX. H and L have not been cleared or given the five-factory tail schema.',
                  'The complete invoice is not the optimistic two-continuation planning case: stages3,4,6 are all explicitly paid.',
                  'No source exposure sharing or three-stage public touch window is assumed.',
                  'The exact signed group algebra proves positive identities for every f; it is not a formal-kernel certificate.'],
        'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}
                       for p in('nested_prefix.py','free_ops.py','plane_group.py')],
        'negative_control':'Wrong pre-continuation fanout sign changes the actual all-column matrix.',
        'no_new_kappa':True}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=prove();out['producer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out=json.loads(json.dumps(out));path=HERE/'NESTED-SIX.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:F.need(json.loads(path.read_text())==out,'saved nested-six receipt differs')
    print(out['status'],out['histogram'],'prefix only')


if __name__=='__main__':main()
