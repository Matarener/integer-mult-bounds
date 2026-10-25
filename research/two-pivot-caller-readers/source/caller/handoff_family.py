#!/usr/bin/env python3
"""All-pair source handoffs with one continuation per nonfinal pair.

The two terminal carrier words are retained exactly. This is a prefix,
not a claim that their native cleanup has bounded cost.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import argparse, hashlib, json, sys
sys.dont_write_bytecode=True
import free_ops as F
from plane_group import Algebra
from nested_prefix import skeleton
from nested_family import retraction, ec
HERE=Path(__file__).resolve().parent


def build(q,physical=False):
    F.need(q>=2,'handoff family starts with two new pairs')
    n,k=2*q+2,2*q+1
    A=Algebra(k+1)if physical else None
    I=A.I if physical else F.I
    Z=A.Z if physical else F.Z
    eye=A.eye if physical else F.eye
    mm=A.mm if physical else F.mm
    inv=A.inv if physical else F.inv
    es=A.es if physical else F.es
    mul=A.mul if physical else F.mul
    N=A.n(0)if physical else F.N
    M=eye(n);Mi=eye(n);events=[];stage=0
    def app(B,Bi,e):
        nonlocal M,Mi
        F.need(mm(B,Bi)==mm(Bi,B)==eye(n),'every literal event has its full inverse')
        M=mm(B,M);Mi=mm(Mi,Bi);events.append(e)
    def add(d,s,c,label):
        if not c:return
        op=A.mono(coefficient=c)if physical else F.mono((),c)
        nop=A.mono(coefficient=-c)if physical else F.mono((),-c)
        app(es(n,d,s,op),es(n,d,s,nop),{'kind':'ADD','dst':d,'src':s,'coefficient':str(c),'label':label})
    def opadd(d,s,c,label):
        F.need(not physical,'operator ADD belongs only to the retarded formal proof')
        app(es(n,d,s,c),es(n,d,s,F.neg(c)),{'kind':'FORMAL_ADD','dst':d,'src':s,'label':label})
    def unary(b,g,label,native=False):
        B=eye(n);Bi=eye(n);B[b][b]=g;Bi[b][b]=inv(g)
        if physical:
            ((bits,p),c),=g.items()
            op={'sign':int(c),'native_blocks':[j for j in range(k+1)if bits>>j&1],
                'block_permutation':list(p),'native_arity':A.native_arity(g)}
            e={'kind':'NATIVE'if native else'ADDRESS_OR_UNIT','bank':b,'operator':op,'label':label}
        else:e={'kind':'FORMAL_UNARY','bank':b,'operator':F.serial(g),'label':label}
        app(B,Bi,e)
    def swap(b,c,label):
        B=eye(n);B[b],B[c]=B[c],B[b]
        app(B,B,{'kind':'BANK_SWAP','banks':[b,c],'label':label})
    def progress(src,s,dst=None):
        if physical:
            for b in range(n):
                if b!=src:unary(b,A.n(s),f'query{s} target fresh'if b==dst else f'query{s} inactive fresh progress',True)
    # Initial direct prefix through the scalar entrance of query4. Its
    # three source retractions are the independently pinned direct ones.
    for r in range(2,q+1):add(2*r+1,3,1,'raw c-basis')
    if physical:
        unary(1,N,'shared input N exposure',True);add(2,1,1,'shared input fanout');unary(1,inv(N),'shared input N inverse',True)
    _,ops=skeleton(q,[1]+[0]*(q-1))
    for typ,d,s,z in ops:
        if typ=='a':
            if physical:
                if z[1]:
                    F.need(stage==0 and d==2 and s==1 and z[1]==1,'shared input is the only early N ADD')
                else:add(d,s,z[0],'initial nested scalar bridge')
            else:opadd(d,s,ec(z),'initial nested bridge')
        elif typ=='s':swap(d,s,'initial nested permutation')
        else:
            stage+=1;u=retraction(q,stage)
            if stage==4:
                for b,(aa,bb)in enumerate(u):
                    if b!=s:add(b,s,-aa,'query4 scalar source entrance')
                break
            if physical:
                for b,(aa,bb)in enumerate(u):
                    if b!=s:add(b,s,-aa,f'query{stage} scalar entrance')
                unary(s,N,f'query{stage} source common',True)
                for b,(aa,bb)in enumerate(u):
                    if b!=s:add(b,s,-bb,f'query{stage} source fanout')
                add(d,s,1,f'query{stage} delivery')
                unary(s,A.swap(0,stage),f'query{stage} source swap')
                progress(s,stage,d)
                if stage==3:
                    for b,(aa,bb)in enumerate(u):
                        if b!=s:add(b,s,-bb,'query3 pre-continuation fanout')
                    unary(s,N,'query3 retained source continuation',True)
                for b,(aa,bb)in enumerate(u):
                    if b!=s:add(b,s,aa,f'query{stage} scalar exit')
            else:
                for b,z in enumerate(u):
                    if b!=s:opadd(b,s,F.neg(ec(z)),f'query{stage} source entrance')
                P=F.mono((stage,));P=F.mul(N,P)if stage==3 else P
                opadd(d,s,N,f'query{stage} cross');unary(s,P,f'query{stage} source code')
                for b,z in enumerate(u):
                    if b!=s:opadd(b,s,ec(z),f'query{stage} source exit')
    # The deeper response entrances left future raw b fields on a.
    # Remove them before using a as the independent raw public input.
    for r in range(3,q+1):add(0,2*r,-1,'restore raw a from deeper response entrance')
    # Hold N*u without the raw A_r part. All its input fields are kept.
    add(3,0,-1,'held source subtract raw a')
    for r in range(2,q+1):add(3,2*r,-1,'held source subtract future raw b')
    for r in range(2,q+1):
        even,odd=2*r,2*r+1;b=2*r;c=2*r+1
        unary(1,N,f'query{even} source common',physical)
        add(1,3,-1,f'query{even} isolate raw c difference')
        swap(1,3,f'query{even} source handoff')
        if physical:unary(1,A.swap(0,even),f'query{even} source swap')
        else:unary(1,F.prod(F.mono((even,)),inv(N)),f'query{even} retarded source post')
        progress(1,even,3)
        swap(3,c,f'query{even} move finished c difference')
        unary(b,N,f'query{odd} source common',physical)
        for ell in range(r+1,q+1):add(2*ell+1,b,1,f'query{odd} future c first fanout')
        add(3,b,1,f'query{odd} delivery')
        swap(b,3,f'query{odd} source handoff')
        add(2,b,-1,f'query{odd} finish current b accumulator')
        for ell in range(r+1,q+1):add(2*ell+1,b,-1,f'query{odd} restore future raw c differences')
        if physical:unary(b,A.swap(0,odd),f'query{odd} source swap')
        else:unary(b,F.prod(F.mono((odd,)),inv(N)),f'query{odd} retarded source post')
        progress(b,odd,3)
        if r<q:
            add(2,1,1,f'query{odd} retain other carrier in b accumulator')
            nextc=2*r+3
            for ell in range(r+2,q+1):
                add(2*ell+1,nextc,-1,f'query{odd} next c difference')
                add(2*ell+1,1,1,f'query{odd} retain other carrier in future c')
            swap(1,nextc,f'query{odd} move next raw c into t')
            add(1,b,1,f'query{odd} next source preload')
            unary(b,N,f'query{odd} retained source continuation',physical)
        swap(b,3,f'query{odd} move finished b to its public slot')
    unary(0,N,'final raw a common query',physical)
    add(2,0,-1,'final b accumulator isolation')
    for r in range(3,q+1):add(2*r+1,2*r-1,1,'triangular c difference decode')
    F.need(mm(M,Mi)==mm(Mi,M)==eye(n),'every independent input and literal inverse both orders')
    return A,M,Mi,events


def evaluate(x,A):
    out=A.Z
    for w,c in x.items():
        term=A.mono(coefficient=c)
        for t in w:
            g=A.n(0)if t==0 else A.swap(0,abs(t))
            term=A.mul(term,A.inv(g)if t<0 else g)
        out=A.add(out,term)
    return out


def prove():
    fixtures=[]
    for q in(2,3,4):
        _,M,Mi,_=build(q)
        A,P,Pi,events=build(q,True);n=2*q+2;k=2*q+1
        fresh=A.prod(*(A.n(j)for j in range(1,k+1)))
        F.need(P==[[A.mul(fresh,evaluate(x,A))for x in row]for row in M],
               'all physical plane/ADDRESS phases bind every free-operator coefficient')
        E=A.mul(fresh,A.n(0));public=[i for i in range(n)if i not in(1,3)]
        F.need(all(P[i]==[E if j==i else A.Z for j in range(n)]for i in public),
               'all public rows are full native independent input outputs')
        hist=Counter(e['operator']['native_arity']for e in events if e['kind']=='NATIVE')
        F.need(hist=={2:n*k+q+2},'complete separate-progress invoice')
        H=[[M[i][j]for j in(1,3)]for i in(1,3)];L=[[M[i][j]for j in public]for i in(1,3)]
        fixtures.append({'q':q,'banks':n,'query_stages':k,'ambient_arity':2*(k+1),
                         'histogram':dict(hist),'native_rank_mass':2*sum(hist.values()),
                         'D_before_tail':2*q,'public_rows':public,'pivot_rows':[1,3],
                         'matrix':F.sm(M),'inverse':F.sm(Mi),'H':F.sm(H),'L':F.sm(L),
                         'physical_matrix':[[A.serial(x)for x in row]for row in P],
                         'physical_inverse':[[A.serial(x)for x in row]for row in Pi],
                         'events':events})
    return {'status':'PASS_ALL_PAIR_SOURCE_HANDOFF_PREFIX',
            'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','fixtures':fixtures,
            'all_pair_invariant':{'entrance':'t=u+delta C_r; held=N*u; b1=N*b1raw-v; c_r=-v-N*A_r; c_l=(C_l-C_r)+c_r for l>r; A_r=a+sum_(l>=r)b_l',
                                  'two_handoff_exit':'U=P_even*u; V=P_odd*(N*v-A_next); public b_r=N*b_rraw, c_r=N*delta C_r; b1=N*(b1raw+A_next)',
                                  'next_pair_encoder':'b1+=U; later c_l-=next raw delta C and +=U; swap t with next c; t+=V; continue source N; u_next=V, v_next=-U-N*A_next',
                                  'continuations':'Only query3 and odd handoffs before the last pair: q-1 total.',
                                  'literal_cost':'k=2q+1, n=2q+2, m=4q+4, H2=n*k+q+2 (two input exposures and one final common query included), D_before_tail=2q.'},
            'limits':['Two raw terminal carriers retain every source swap and every public reader. Their cleanup is not included.',
                      'The native cost or moment of the terminal carrier factories is not asserted bounded.',
                      'The finite all-column checks q2..4 are separate from the written all-pair invariant and are not a formal-kernel proof.'],
            'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}for p in('nested_family.py','nested_prefix.py','free_ops.py','plane_group.py')],
            'no_new_kappa':True}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=prove();out['producer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=json.loads(json.dumps(out));p=HERE/'HANDOFF-FAMILY.json'
    if args.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:F.need(json.loads(p.read_text())==out,'saved handoff family receipt differs')
    print(out['status'])
if __name__=='__main__':main()
