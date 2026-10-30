#!/usr/bin/env python3
"""Exact witnesses accompanying written mixed-cubic caller lower bounds.

These are finite identity/negative-control checks, not an exhaustive search.
The all-n claims are proved in README.md. Apache-2.0; OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
Z=(Q(0),Q(0));O=(Q(1),Q(0));N=(Q(0),Q(1))
N2=(Q(-1),Q(-1))

def need(b,m):
    if not b:raise ValueError(m)
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def sub(a,b):return add(a,neg(b))
def mul(a,b):
    return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]-a[1]*b[1])
def conj(a):return (a[0]-a[1],-a[1])
def kinv(a):
    b=conj(a);d=mul(a,b)
    need(d[1]==0 and d[0]!=0,'nonzero exact cyclotomic inverse')
    return (b[0]/d[0],b[1]/d[0])
def scale(a,s):return (a[0]*s,a[1]*s)
def total(xs):
    a=Z
    for x in xs:a=add(a,x)
    return a
def eye(n):return [[O if i==j else Z for j in range(n)] for i in range(n)]
def zero(n,m):return [[Z for j in range(m)] for i in range(n)]
def const(a):return [[(Q(x),Q(0)) for x in r] for r in a]
def mm(a,b):return [[total(mul(x,y) for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def ma(a,b):return [[add(x,y) for x,y in zip(r,s)] for r,s in zip(a,b)]
def ms(a,b):return [[sub(x,y) for x,y in zip(r,s)] for r,s in zip(a,b)]
def scalar(a,s):return [[mul(x,s) for x in r] for r in a]
def mc(a):return [[conj(x) for x in r] for r in a]
def trace(a):return total(a[i][i] for i in range(len(a)))
def rank(a):
    b={}
    for r in a:
        r=list(r)
        for j,v in sorted(b.items()):
            c=r[j];r=[sub(x,mul(c,y)) for x,y in zip(r,v)]
        j=next((j for j,x in enumerate(r) if x!=Z),None)
        if j is not None:
            c=kinv(r[j]);b[j]=[mul(x,c) for x in r]
    return len(b)
def inv(a):
    n=len(a);w=[list(r)+s for r,s in zip(a,eye(n))]
    for j in range(n):
        p=next(i for i in range(j,n) if w[i][j]!=Z)
        w[p],w[j]=w[j],w[p];c=kinv(w[j][j]);w[j]=[mul(x,c) for x in w[j]]
        for i in range(n):
            if i!=j:
                c=w[i][j];w[i]=[sub(x,mul(c,y)) for x,y in zip(w[i],w[j])]
    need([r[:n] for r in w]==eye(n),'field inverse exact')
    return [r[n:] for r in w]
def power(a,k):
    b=eye(len(a))
    for _ in range(k):b=mm(b,a)
    return b
def ser(a):return [[[str(x) for x in c] for c in r] for r in a]

def interaction_fixture(n,k):
    uc=[[Q(0) for j in range(k)] for i in range(n)]
    vr=[[Q(0) for j in range(n)] for i in range(k)]
    for i in range(k):
        j=i%n;uc[j][i]=1;uc[(j+1)%n][i]=i+1
        vr[i][(j+2)%n]=Q((-1)**i)
    U=const(uc);V=const(vr)
    need(rank(U)==rank(V)==n,'full-rank rational directions fixture')
    B=mm(V,U);need(all(B[i][i]==Z for i in range(k)),'nilpotent direction diagonals')
    lo=[[B[i][j] if i>j else Z for j in range(k)] for i in range(k)]
    up=[[B[i][j] if i<j else Z for j in range(k)] for i in range(k)]
    types=[1 if i%2==0 else 2 for i in range(k)]
    al=[sub(N if e==1 else N2,O) for e in types];t=sub(N,O)
    gi=negmat(lo)
    for i in range(k):gi[i][i]=kinv(al[i])
    G=inv(gi);W=eye(n)
    for h in range(k):
        D=[[scale(al[h],uc[i][h]*vr[h][j]) for j in range(n)] for i in range(n)]
        need(mm(D,D)==zero(n,n),'fixture paid direction nilpotent')
        W=mm(ma(eye(n),D),W)
    need(W==ma(eye(n),mm(mm(U,G),V)),'exact interaction resolvent formula')
    C=ms(B,scalar(gi,t))
    A=[list(r) for r in up];B2=[list(r) for r in lo]
    for i,e in enumerate(types):
        if e==1:A[i][i]=neg(O)
        else:B2[i][i]=O
    need(C==ma(A,scalar(B2,N)),'rational/primitive coefficient split')
    defect=ms(W,scalar(eye(n),N))
    need(mm(mm(U,G),C)==mm(defect,U),'target-sensitive rank identity')
    need(rank(C)<=k-n+rank(mm(defect,U)),'defect-sensitive rank bound')
    # No fixture is alleged to solve the central target. Dropping the defect
    # term must fail in these intentionally noncentral words.
    need(rank(C)>k-n and rank(defect)>0,'noncentral-word negative control')
    return {'n':n,'k':k,'types':types,'rank_U':rank(U),'rank_V':rank(V),
      'rank_C':rank(C),'r_if_central':k-n,'target_defect_rank':rank(defect),
      'resolvent_identity':True,'coefficient_split':True,'defect_identity':True,
      'not_a_central_factorization':True}

def negmat(a):return [[neg(x) for x in r] for r in a]

def projection_control():
    A=const([[-1,2,0,0],[0,0,0,0],[0,0,-1,3],[0,0,0,0]])
    B=const([[0,0,0,0],[1,1,0,0],[0,0,0,0],[0,0,2,1]])
    pa=ms(eye(4),power(ma(eye(4),A),4))
    pb=ms(eye(4),power(ms(eye(4),B),4))
    need(rank(A)==rank(B)==2,'diagonal-count rank equality fixture')
    for p,m in ((pa,A),(pb,B)):
        need(mm(p,p)==p and mm(p,m)==m and mm(m,p)==m,'unique image-kernel projection')
        need(rank(p)==rank(m),'projection rank agreement')
    need([pa[i][i] for i in range(4)]==[O,Z,O,Z],'upper projection support')
    need([pb[i][i] for i in range(4)]==[Z,O,Z,O],'lower projection support')
    need(pa!=pb,'complementary spectral projections cannot agree')
    return {'upper_projection':ser(pa),'lower_projection':ser(pb),'complementary_diagonals':True,
      'warning':'This fixture does not assert equal row/column spaces. Their equality is the contradictory hypothesis in the written all-word proof.'}

def layer_control(n):
    layers=[]
    for h in range(3):
        D=zero(n,n)
        for j in range(0,n-1,2):
            dst,src=(j,j+1) if h%2==0 else (j+1,j)
            D[dst][src]=scale(sub(N if (h+j)%3 else N2,O),Q((-1)**(h+j//2)))
        # A constant conjugation is allowed between matching layers.
        C=eye(n)
        for j in range(n-1):C[j][j+1]=(Q(h+j+1),Q(0))
        D=mm(mm(inv(C),D),C)
        need(mm(D,D)==zero(n,n),'whole matching-layer normalized perturbation squarezero')
        layers.append(D)
    P=mm(ma(eye(n),layers[1]),ma(eye(n),layers[0]))
    Pi=mm(ms(eye(n),layers[0]),ms(eye(n),layers[1]))
    need(mm(P,Pi)==eye(n),'literal two-layer inverse')
    need(trace(P)==trace(Pi),'two-squarezero-layer reciprocal trace')
    forced=sub(scale(N,n),scale(N2,n))
    need(forced!=Z,'nonreal cubic central trace contradiction')
    return {'n':n,'layer_squarezero_ranks':[rank(x) for x in layers],
      'trace_two_layers':list(map(str,trace(P))),
      'trace_inverse_two_layers':list(map(str,trace(Pi))),
      'central_target_forced_trace_difference':list(map(str,forced))}

def pure_four_layer_control():
    n=3
    A=const([[0,1,0],[0,0,0],[0,0,0]])
    B=const([[0,0,0],[-1,0,0],[0,0,0]])
    C=const([[0,0,0],[0,0,1],[0,0,0]])
    D=const([[0,0,0],[0,0,0],[1,0,0]])
    for m in (A,B,C,D):need(mm(m,m)==zero(n,n),'pure layer fixture squarezero')
    t=sub(N,O);t2=sub(N2,O);I=eye(n)
    Qm=mm(ma(I,scalar(D,t2)),ma(I,scalar(C,t)))
    target=scalar(mm(ms(I,scalar(A,t)),ms(I,scalar(B,t2))),N)
    F=ma(ma(ma(I,scalar(A,(Q(2),Q(0)))),B),scalar(mm(A,B),(Q(3),Q(0))))
    G=ms(F,I);M=ma(A,mm(A,B))
    q0=ma(ms(ms(I,C),scalar(D,(Q(2),Q(0)))),scalar(mm(D,C),(Q(3),Q(0))))
    q1=ms(C,D)
    need(Qm==ma(q0,scalar(q1,N)),'pure left-pair rational/primitive coefficient formula')
    need(target==ma(ms(A,B),scalar(F,N)),'pure right-inverse coefficient formula')
    e=ms(q0,ms(A,B));f=ms(q1,F)
    rhs=scalar(ms(ma(e,f),scalar(mm(D,f),(Q(3),Q(0)))),(Q(1,3),Q(0)))
    need(ms(mm(D,G),M)==rhs,'target-defect-aware alternating four-layer identity')
    need(mm(G,B)==scalar(mm(A,B),(Q(2),Q(0))) and mm(M,B)==mm(A,B),'right multiplication gives forced D eigenvalue1/2')
    need(rank(ms(Qm,target))>0,'noncentral four-pure-layer fixture rejected')
    return {'n':n,'pure_coefficients_in_application_order':['N-1','N^2-1','N-1','N^2-1'],
      'coefficient_identity':True,'target_defect_omission_rejected':True,
      'forced_hypothetical_relation':'If target defect vanishes, D(2A+B+3AB)=A+AB, so 2DAB=AB; D^2=0 forces AB=0.',
      'warning':'The finite fixture does not solve the target. It checks the algebra used in the written all-n obstruction.'}

def receipt():
    need(mul(N,N)==N2 and mul(N2,N)==O,'exact primitive specialization')
    cases=[]
    for n in (3,6,9,12,24,48):
        k=n+(n+3)//3
        need(3*(k-n)>=n+1 and 3*(k-1-n)<n+1,'sharp integer form of strict rank gate')
        cases.append({'n':n,'minimum_calls_from_written_bound':k,
          'favorable_mass_deficit_at_that_call_count':24*n-16*k})
    return {'status':'PASS_WRITTEN_WIDE_MIXED_CUBIC_RANK_AND_THREE_LAYER_GATES',
      'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','no_new_kappa':True,
      'coefficient_ring':'The proposed word must be valid over Z[N]/(N^3-1), or its rational extension. The lower bound uses the necessary specialization to Q(zeta). No positive primitive-component identity is promoted to a full-ring identity.',
      'model':'n independent banks; each paid query is Eij(+-N) or Eij(+-N^2); constant rational GL_n bridges are free. Equivalently normalized directions u_i,v_i are constant rational and v_i^T u_i=0. Arbitrary operator-dependent directions, or unrelated polynomial query coefficients, are outside this wide bound.',
      'general_bound':{'statement':'k>=n+ceil((n+1)/3)','strict_rank_form':'For r=k-n, k<4r.',
        'written_proof':'README.md, general interaction-matrix argument. Valid for every finite n and k in the stated model, not a search result.'},
      'three_matching_layer_gate':{'statement':'No three normalized layers I+A_l with A_l^2=0 can multiply to zeta I_n in characteristic0.',
        'scope':'Constant scalar bridges may occur between layers. Arbitrary mixing inside a nominal layer is outside the squarezero-layer premise unless that premise is separately proved.',
        'proof':'For P=(I+A2)(I+A1), tr(P)=tr(P^-1). The target gives P=zeta(I-A3), hence tr(P)=n*zeta and tr(P^-1)=n*zeta^-1, a contradiction.'},
      'four_pure_layer_gate':{'statement':'No four layers, each entirely I+(zeta-1)A_l or entirely I+(zeta^2-1)A_l with rational A_l^2=0, multiply to zeta I_n for n>0.',
        'proof':'Every adjacent two-layer product must have trace0. Equal-type neighboring layers have trace n-3*zeta*s or n-3*zeta^2*s with rational s, impossible. Types must alternate. Coefficient comparison gives D(2A+B+3AB)=A+AB; multiply right by B and use D^2=0 to force AB=0, contradicting the first pair trace0.',
        'scope':'Mixed N and N^2 coefficients within a layer are outside this pure-layer argument.'},
      'cases':cases,
      'finite_identity_checks':[interaction_fixture(n,k) for n,k in ((3,5),(6,8),(9,11),(12,17))],
      'projection_control':projection_control(),
      'layer_controls':[layer_control(n) for n in (3,6,12)],
      'pure_four_layer_control':pure_four_layer_control(),
      'coverage':'Written all-word/all-n proofs, with finite exact identity and negative-control fixtures. No exhaustive search, formal-kernel proof, positive scalar caller, or native admission is claimed.',
      'independent_review':{'reviewer':'/root/stabilizer_escape_1019','general_rank_gate':'PASS','three_layer_trace_gate':'PASS','four_pure_layer_gate':'See INDEPENDENT-REVIEW.md','record':'INDEPENDENT-REVIEW.md'},
      'remaining':['Four matching layers with mixed N/N^2 coefficients inside a layer are not excluded by these gates.',
        'A four-layer construction must still give every bank its full native endpoint, source-code transport, literal inverse and complete scalar/native/idle invoice.']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    out=receipt();p=HERE/'WIDE-MIXED-CUBIC-GATES.json'
    if a.write:p.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved wide gate differs')
    print(out['status'])
    print('Written k>=n+ceil((n+1)/3); three matching layers excluded; four mixed layers remain open.')

if __name__=='__main__':main()
