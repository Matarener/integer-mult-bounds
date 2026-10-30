#!/usr/bin/env python3
"""Explicit nested source-retraction family and its one-coordinate cocycle.

The native implementation still pays 2q-1 continuations. Algebraic
telescoping alone is not permission to remove these queries.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
sys.dont_write_bytecode=True
from fractions import Fraction
import free_ops as F
from nested_prefix import skeleton, prefixes, Z, I, N, add, neg, mul, mm

HERE=Path(__file__).resolve().parent


def ec(z):return F.add(F.mono((),z[0]),F.mono((0,),z[1]))


def retraction(q,s):
    n=2*q+2;u=[Z]*n
    if s==1:
        u[0]=I;u[2]=I
    elif s==2:
        u[1]=I
        for r in range(1,q+1):u[2*r+1]=I
    elif s==2*q+2:
        u[1]=I;u[0]=N;u[2]=neg(I)
    elif s==2*q+3:
        u[0]=I;u[2]=N
    elif s%2:
        r=(s-1)//2;u[2*r]=I
        for j in range(1,r):u[2*j+1]=I
        for j in range(r+1,q+1):u[2*j+1]=neg(N)
    else:
        r=(s-2)//2;u[1]=I;u[2*(r+1)]=N
        for j in range(1,r+1):u[2*j+1]=N
        for j in range(r+1,q+1):u[2*j+1]=I
    return u


def coordinates(q,s):
    if s==1:return(neg(N),neg(N)),(N,Z)
    if s==2:return(neg(I),Z),(neg(I),I)
    if s==2*q+2:return(I,Z),(I,Z)
    if s==2*q+3:return(neg(N),Z),(N,Z)
    if s%2:return(Z,neg(N)),(Z,N)
    return(Z,I),(Z,I)


def continued(q,s):
    return (3<=s<=2*q and s!=2)or s==2*q+2


def formal(q):
    n,ops=skeleton(q,[1]+[0]*(q-1));M=F.eye(n);Mi=F.eye(n);s=0;sources=[]
    def app(A,Ai):
        nonlocal M,Mi
        F.need(F.mm(A,Ai)==F.mm(Ai,A)==F.eye(n),'each event has its full inverse')
        M=F.mm(A,M);Mi=F.mm(Mi,Ai)
    def a(d,src,c):app(F.es(n,d,src,c),F.es(n,d,src,F.neg(c)))
    for r in range(2,q+1):a(2*r+1,3,F.I)
    for typ,d,src,z in ops:
        if typ=='a':a(d,src,ec(z))
        elif typ=='s':
            B=F.eye(n);B[d],B[src]=B[src],B[d];app(B,B)
        else:
            s+=1;u=retraction(q,s)
            F.need(u[src]==I,'source normalization')
            for j,z in enumerate(u):
                if j!=src and z!=Z:a(j,src,F.neg(ec(z)))
            P=F.mono((s,));P=F.mul(F.N,P)if continued(q,s)else P
            A=F.mm(F.unary(n,src,P),F.es(n,d,src,F.N))
            Ai=F.mm(F.es(n,d,src,F.neg(F.N)),F.unary(n,src,F.inv(P)))
            app(A,Ai)
            for j,z in enumerate(u):
                if j!=src and z!=Z:a(j,src,ec(z))
            sources.append({'stage':s,'src':src,'dst':d,'u':[[str(a),str(b)]for a,b in u],
                            'source_code':('N P'if continued(q,s)else'P')+str(s)})
    for r in range(2,q+1):a(2*r+1,3,F.neg(F.I))
    F.need(F.mm(M,Mi)==F.mm(Mi,M)==F.eye(n),'all-column literal inverse in both orders')
    public=[i for i in range(n)if i not in(1,3)]
    F.need(all(M[i]==[F.N if j==i else F.Z for j in range(n)]for i in public),
           'all n-2 public outputs are exactly N times independent inputs')
    H=[[M[i][j]for j in(1,3)]for i in(1,3)];L=[[M[i][j]for j in public]for i in(1,3)]
    P={j:F.mono((j,))for j in range(1,2*q+4)}
    A3=F.prod(*(P[j]for j in range(2*q+1,2,-1)))
    if(q-1)%2:A3=F.neg(A3)
    Q1=F.prod(F.inv(F.N),P[1],F.N)
    J=[[F.add(F.add(P[2],Q1),F.neg(F.I)),F.add(F.I,F.neg(P[2]))],
       [F.add(Q1,F.neg(F.I)),F.I]]
    D=[[F.neg(F.mul(P[2*q+3],P[2*q+2])),F.Z],[F.Z,F.mul(A3,F.N)]]
    F.need(H==F.mm(D,J),'five-factory H factor for the explicit family')
    # Independently rebuild H using only the two-dimensional source-coordinate updates.
    B=F.eye(2)
    for s in range(1,2*q+4):
        w,r=coordinates(q,s);w=list(map(ec,w));r=list(map(ec,r))
        Ptilde=F.mul(F.N,P[s])if continued(q,s)else P[s]
        T=[[F.add(F.I if i==j else F.Z,F.prod(w[i],F.add(Ptilde,F.neg(F.I)),r[j]))for j in range(2)]for i in range(2)]
        B=F.mm(T,B)
    F.need(H==[[F.mul(F.N,x)for x in row]for row in B],
           'two-coordinate update proof independently reconstructs H')
    return {'q':q,'banks':n,'raw_calls':2*q+3,'public_rows':public,'pivot_rows':[1,3],
            'source_retractions':sources,'complete_matrix':F.sm(M),'complete_inverse':F.sm(Mi),
            'H':F.sm(H),'L':F.sm(L),'D':F.sm(D),'J':F.sm(J),'A3':F.serial(A3),
            'continuations':[s for s in range(1,2*q+4)if continued(q,s)],
            'separate_progress_profile':{'H2':n*(2*q+3)+2*q+1,'ambient':4*q+8,
                                         'rank_deficit_before_tail':2}}


def prefix_coordinates(q):
    n=2*q+2;_,pre=prefixes(q,[1]+[0]*(q-1))
    V=[[I if i==1 else Z,I if i>=3 and i%2 else Z]for i in range(n)]
    for s,(M,src,dst)in enumerate(pre,1):
        B=mm(M,V);w,r=coordinates(q,s)
        F.need([add(mul(row[0],w[0]),mul(row[1],w[1]))for row in B]==retraction(q,s),
               'displayed normalized source column lies in the transported fixed plane')
        F.need(tuple(B[src])==r,'displayed source functional on both pivot coordinates')


def cocycle():
    # Columns(z,A,c,d,b) are independent fields. Po and Pe do not commute.
    ZR=[F.I,F.Z,F.Z,F.Z,F.Z];AR=[F.Z,F.I,F.Z,F.Z,F.Z]
    CR=[F.Z,F.Z,F.I,F.Z,F.Z];DR=[F.Z,F.Z,F.Z,F.I,F.Z];BR=[F.Z,F.Z,F.Z,F.Z,F.I]
    def plus(*rows):return[F.summ(row[j]for row in rows)for j in range(5)]
    def left(a,row):return[F.mul(a,x)for x in row]
    Po,Pe=F.mono((1,)),F.mono((2,))
    y=plus(left(F.N,ZR),left(F.neg(F.I),AR),left(F.N,CR))
    fodd=plus(left(F.neg(F.I),AR),left(F.N,CR))
    zodd=plus(left(F.mul(Po,F.N),ZR),left(F.add(Po,F.N),fodd))
    even_source=plus(zodd,left(F.N,AR),DR)
    F.need(even_source==plus(left(Po,y),DR,left(F.neg(F.I),CR)),
           'next source is the old source through one ADDRESS plus the raw c difference')
    feven=plus(left(F.N,AR),DR)
    zeven=plus(left(F.mul(F.N,Pe),zodd),left(F.add(F.mul(F.N,Pe),F.neg(F.I)),feven))
    ynext=plus(left(F.N,zeven),left(F.N,DR),left(F.neg(F.I),AR),BR)
    rhs=plus(left(F.neg(F.mul(Pe,Po)),y),BR,left(Pe,CR),left(F.neg(Pe),DR))
    F.need(ynext==rhs,'middle two-call affine ADDRESS cocycle on every independent public/pivot column')
    return {'source_y':'y_r=N z-A_r+N c_r, A_r=a+sum_(l>r)b_l; c1 means zero public reader',
            'next_even_source':'P_o y_r+c_(r+1)-c_r',
            'next_y':'-P_e P_o y_r+b_(r+1)+P_e(c_r-c_(r+1))',
            'independent_columns':['z','A_r','c_r','c_(r+1)','b_(r+1)'],
            'covered_domain':'Arbitrary independent invertible noncommuting Po,Pe; N^2=-I; literal affine operator identity.',
            'not_native_admission':'The virtual coordinate is a literal source at the odd cut. Holding its chart through the even cut still requires an explicit invertible bank encoder, all public readers at actual frames, and restoration of the other independent dirty field.'}


def prove():
    for q in range(1,9):prefix_coordinates(q)
    fixtures=[formal(q)for q in(1,2,3,4)]
    from nested_six import formal_word
    M,Mi,_,_,_=formal_word()
    F.need(fixtures[1]['complete_matrix']==F.sm(M)and fixtures[1]['complete_inverse']==F.sm(Mi),
           'q2 direct family agrees exactly with independently compiled NESTED-SIX')
    return {'status':'PASS_EXPLICIT_NESTED_SOURCE_FAMILY_AND_ONE_COORDINATE_AFFINE_COCYCLE',
            'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','fixtures':fixtures,'affine_cocycle':cocycle(),
            'all_parameter_proof':'The ideal nested response skeleton gives N on every field after its output isolation. Its two transported pivot columns obey the displayed source-functional/retraction table. Conjugated source-code insertions therefore act by 2x2 updates I+w(Ptilde-I)r. The first two updates multiply to J(P2,Q1); all middle updates are on only the second coordinate and telescope to Ad_(N^-1)(A3), A3=(-1)^(q-1)P_(2q+1)...P3; the last two updates give the first diagonal factor. Left multiplication by the ideal final N yields H=diag(-P_last P_penult,A3 N)J. No source code or public coupling is discarded.',
            'initial_basis':'At raw ZERO, c_r+=c1 for r>=2. One common N/N^-1 exposure fanouts b1+=N*t only. The inverse c-basis is applied after the last query; its other public rows are retained.',
            'finite_checks':'Every free-operator matrix column and both inverse orders for q1..4. Exact transported-plane/source-functional table for q1..8. q2 entire matrix agrees with NESTED-SIX.',
            'native_invoice':'With the current literal compiler c=2q-1 retained N continuations, two shared input N calls and all separate fresh progress: H2=(2q+2)(2q+3)+2q+1, m=4q+8, n=2q+2, D_before_tail=2. Wide batching changes moment pressure, not this mass. No amortized query removal is asserted.',
            'limits':['H has a bounded five-factory form, but the complete L readers and their native cuts remain part of the contract.',
                      'The affine ADDRESS cocycle is an algebraic grouping target, not an implemented shared-native controller.',
                      'The finite checks and written all-parameter recurrence are not a formal-kernel proof.'],
            'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}
                           for p in('nested_prefix.py','nested_six.py','NESTED-SIX.json','free_ops.py')],
            'no_new_kappa':True}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=prove();out['producer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();path=HERE/'NESTED-FAMILY.json'
    out=json.loads(json.dumps(out))
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:F.need(json.loads(path.read_text())==out,'saved nested-family receipt differs')
    print(out['status'])


if __name__=='__main__':main()
