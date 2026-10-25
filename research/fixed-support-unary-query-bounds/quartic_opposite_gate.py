#!/usr/bin/env python3
"""Exact opposite-character compact matrices for z^4=-1 unary calls.

The written all-n proof retains arbitrary scalar final bridges and dirty
helpers. No nonexistent +/-1 augmentation character is used.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as F
import argparse,json
HERE=Path(__file__).resolve().parent
Z=(F(0),)*4;I=(F(1),F(0),F(0),F(0))
def need(b,m):
    if not b:raise ValueError(m)
def mon(r=0,c=F(1)):
    a=[F(0)]*4;a[r%4]=c*(-1 if (r//4)&1 else 1);return tuple(a)
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def neg(a):return tuple(-x for x in a)
def mul(a,b):
    c=[F(0)]*4
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            if x and y:c[(i+j)%4]+=x*y*(-1 if i+j>=4 else 1)
    return tuple(c)
def scale(a,c):return tuple(c*x for x in a)
def opposite(a):return tuple(c*(-1 if r&1 else 1) for r,c in enumerate(a))
def scalar_inverse(a):
    M=[[mul(a,mon(j))[i] for j in range(4)]+[I[i]] for i in range(4)]
    for j in range(4):
        p=next((i for i in range(j,4) if M[i][j]),None);need(p is not None,'nonzero cyclotomic scalar inverse')
        M[j],M[p]=M[p],M[j];x=M[j][j];M[j]=[c/x for c in M[j]]
        for i in range(4):
            if i!=j:
                x=M[i][j];M[i]=[a-x*b for a,b in zip(M[i],M[j])]
    out=tuple(M[i][4] for i in range(4));need(mul(a,out)==mul(out,a)==I,'exact cyclotomic inverse');return out
def eye(n):return [[I if i==j else Z for j in range(n)] for i in range(n)]
def zeros(n,m):return [[Z]*m for _ in range(n)]
def mm(a,b):
    c=zeros(len(a),len(b[0]))
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x==Z:continue
            for j,y in enumerate(b[k]):
                if y!=Z:c[i][j]=add(c[i][j],mul(x,y))
    return c
def ma(a,b):return [[add(x,y) for x,y in zip(r,s)] for r,s in zip(a,b)]
def mn(a):return [[neg(x) for x in r] for r in a]
def opmat(a):return [[opposite(x) for x in r] for r in a]
def query(n,u,v,e):
    q=eye(n);qi=eye(n);a=add(mon(e),neg(I));ai=add(mon(-e),neg(I))
    need(sum(x*y for x,y in zip(u,v))==1,'rank1 source projection')
    for i in range(n):
        for j in range(n):q[i][j]=add(q[i][j],scale(a,u[i]*v[j]));qi[i][j]=add(qi[i][j],scale(ai,u[i]*v[j]))
    need(mm(q,qi)==mm(qi,q)==eye(n),'literal quartic query inverse');return q,qi,a
def compact(n,k):
    us=[];vs=[];aa=[];W=eye(n);ais=[]
    for j in range(k):
        s=j%n;u=[F(int(i==s)) for i in range(n)];v=u[:]
        if n>1:v[(s+1)%n]=F((-1)**j)
        q,qi,a=query(n,u,v,1 if j%3 else -1);W=mm(q,W);ais.append(qi);us.append(u);vs.append(v);aa.append(a)
    U=[[mon(c=us[j][i]) for j in range(k)] for i in range(n)];V=[[mon(c=vs[i][j]) for j in range(n)] for i in range(k)]
    D=zeros(k,k);Di=zeros(k,k);L=zeros(k,k)
    for i in range(k):
        D[i][i]=aa[i];Di[i][i]=scalar_inverse(aa[i])
        for j in range(i):L[i][j]=mon(c=sum(x*y for x,y in zip(vs[i],us[j])))
    DL=mm(D,L);term=eye(k);series=zeros(k,k)
    for _ in range(k):series=ma(series,term);term=mm(DL,term)
    need(term==zeros(k,k),'finite chronological series')
    G=mm(series,D);Gi=ma(Di,mn(L));need(mm(G,Gi)==mm(Gi,G)==eye(k),'compact G inverse')
    need(ma(W,mn(eye(n)))==mm(U,mm(G,V)),'full quartic compact coefficient coverage')
    Gop=opmat(G);Gopi=opmat(Gi);Delta=ma(G,mn(Gop));J=ma(opmat(Di),mn(Di));Ji=zeros(k,k)
    for i in range(k):Ji[i][i]=scalar_inverse(J[i][i])
    need(Delta==mm(G,mm(J,Gop)),'opposite-character resolvent identity')
    Deltai=mm(Gopi,mm(Ji,Gi));need(mm(Delta,Deltai)==mm(Deltai,Delta)==eye(k),'opposite-character difference is invertible')
    for qi in reversed(ais):W=mm(qi,W)
    need(W==eye(n),'all independent inputs restored by literal inverse')
    return {'banks':n,'calls':k,'all_four_coefficients':True,'literal_inverse':True,'G_opposite_difference_invertible':True}
def sharp(n,h=0):
    b=n+h;W=eye(b);ais=[]
    for j in range(n):
        u=[F(int(i==j)) for i in range(b)]
        for _ in range(2):q,qi,_=query(b,u,u,1);W=mm(q,W);ais.append(qi)
    T=[[mon(2) if i==j and i<n else (I if i==j else Z) for j in range(b)] for i in range(b)]
    need(W==T,'sharp 2n construction with arbitrary helpers restored')
    need(mm(ais[-1],W)!=T,'one missing call is detected')
    for qi in reversed(ais):W=mm(qi,W)
    need(W==eye(b),'sharp literal inverse')
    return {'public_banks':n,'restored_arbitrary_helpers':h,'calls':2*n,'all_public_A_squared':True,'literal_inverse':True,'missing_call_rejected':True,'m':2,'H':{1:2*n},'D':0}
def receipt():
    return {'status':'PASS_NEW_QUARTIC_OPPOSITE_CHARACTER_SHARP_2N_GATE',
            'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','ring':'Q[z]/(z^4+1), with all four primitive eighth-root characters and no +/-1 character.',
            'compact_cases':[compact(n,k) for n,k in ((1,2),(2,3),(3,4),(4,6))],'sharp_cases':[sharp(1),sharp(2),sharp(3,2)],
            'all_n_proof':'Pull scalar bridges to a constant C. Target W(z)=C^-1 diag(z^2 I_n,I_h). Compact W-I=U G(z)V. At roots with squares+i and-i, W(z)-W(w) has rankn, so rankU,rankV>=n. At opposite roots z,-z target equal. The resolvent difference G(z)-G(-z)=G(z)[D(-z)^-1-D(z)^-1]G(-z) is invertible because its middle diagonal entries are +/-2z/(z^2-1), all nonzero. Hence U DeltaG V=0 gives rankV<=k-rankU, proving k>=2n. Arbitrary scalar rational/Gaussian final bridges and restored independent dirty helpers are retained.',
            'native_binding':'For odd f, the new common1/fresh1 carrier A_f=(U_f tensor I)SWAP has U_f^2=(-i)^f, A_f^4=-I, all four roots of z^4+1 present, native A^+/- arity1 and A^2 arity2. At fixed support m=2,W=n,H1=k, D=2n-k<=0. Evenf uses the separately preserved order4 proof.',
            'independent_review':'Root and stabilizer independently passed the opposite-character argument, including the arbitrary final bridge and dirty-helper rank step. Actual odd-f spectrum/phase is externally pinned.',
            'scope_limit':'Scalar constant bank GL only. Operator-valued ADDRESS/Pauli internal-coordinate bridges are outside the factorization premise. No primitive-cost or general arbitrary-support lower bound is asserted.',
            'no_new_kappa':True}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    out=json.loads(json.dumps(receipt()));p=HERE/'QUARTIC-OPPOSITE-GATE.json'
    if a.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved quartic opposite gate differs')
    print(out['status']);print('No +/-1 augmentation; all-n floor with arbitrary scalar final bridge and restored dirty helpers, sharp construction and exact difference inverse.')
if __name__=='__main__':main()
