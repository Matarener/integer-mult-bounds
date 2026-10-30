#!/usr/bin/env python3
"""Full cubic-ring checks for the written four-query constant-direction gate.

No native lift is assumed. The exclusion is a written all-word proof; these
finite checks verify its normalization and deliberately excluded controls.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
Z=(Q(0),)*3
O=(Q(1),Q(0),Q(0))
N=(Q(0),Q(1),Q(0))
N2=(Q(0),Q(0),Q(1))

def need(b,m):
    if not b:raise ValueError(m)
def plus(a,b):return tuple(x+y for x,y in zip(a,b))
def neg(a):return tuple(-x for x in a)
def sub(a,b):return plus(a,neg(b))
def scale(a,c):return tuple(c*x for x in a)
def mul(a,b):return tuple(sum(a[i]*b[j] for i in range(3) for j in range(3) if (i+j)%3==k) for k in range(3))
def addall(xs):
    a=Z
    for x in xs:a=plus(a,x)
    return a
def eye():return [[O if i==j else Z for j in range(3)] for i in range(3)]
def mm(a,b):return [[addall(mul(x,y) for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def matplus(a,b):return [[plus(x,y) for x,y in zip(r,s)] for r,s in zip(a,b)]
def matsub(a,b):return [[sub(x,y) for x,y in zip(r,s)] for r,s in zip(a,b)]
def aug(a):return [[sum(x) for x in r] for r in a]
def qmm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def qeye():return [[Q(i==j) for j in range(3)] for i in range(3)]
def const(a):return [[(Q(x),Q(0),Q(0)) for x in r] for r in a]
def inv(a):
    w=[list(map(Q,r))+[Q(i==j) for j in range(3)] for i,r in enumerate(a)]
    for j in range(3):
        p=next(i for i in range(j,3) if w[i][j])
        w[p],w[j]=w[j],w[p];c=w[j][j];w[j]=[x/c for x in w[j]]
        for i in range(3):
            if i!=j:
                c=w[i][j];w[i]=[x-c*y for x,y in zip(w[i],w[j])]
    need([r[:3] for r in w]==qeye(),'exact scalar inverse')
    return [r[3:] for r in w]
def rankq(rows):
    b={}
    for r in rows:
        r=list(map(Q,r))
        for k,v in sorted(b.items()):
            c=r[k];r=[x-c*y for x,y in zip(r,v)]
        k=next((k for k,x in enumerate(r) if x),None)
        if k is not None:b[k]=[x/r[k] for x in r]
    return len(b)
def shear(i,j,a):
    e=eye();e[i][j]=plus(e[i][j],a);return e
def transvection(A,a=sub(N,O)):
    return [[plus(O if i==j else Z,scale(a,A[i][j])) for j in range(3)] for i in range(3)]
def coeff_span(T):
    return rankq([[T[i][j][k] for i in range(3) for j in range(3)] for k in range(3)])
def serial(a):return [[[str(c) for c in x] for x in r] for r in a]

def normal_form(word):
    W=eye();B=qeye();P=eye();directions=[]
    for g in word:
        if g['op']=='FREE':
            C=g['matrix'];W=mm(const(C),W);B=qmm(C,B)
        else:
            i,j,s,e=g['dst'],g['src'],g['sign'],g.get('power',1)
            need(i!=j and s in(-1,1) and e in(1,2),'actual declared mixed paid shear')
            gN=N if e==1 else N2
            W=mm(shear(i,j,scale(gN,s)),W)
            A=[[Q(s*(a==i)*(b==j)) for b in range(3)] for a in range(3)]
            A=qmm(qmm(inv(B),A),B)
            need(rankq(A)==1 and qmm(A,A)==[[Q(0)]*3 for _ in range(3)],'constant rank1 nilpotent direction')
            C=transvection(A,sub(gN,O))
            need(aug(C)==qeye(),'exact N1 augmentation of normalized query')
            P=mm(C,P);directions.append(A)
            E=qeye();E[i][j]+=s;B=qmm(E,B)
    need(mm(const(inv(B)),W)==P,'full Z[N]/(N3-1) scalar-bridge normal form')
    return {'paid_calls':len(directions),'word':word,'augmentation':[[str(x) for x in r] for r in B],
            'constant_rank1_directions':[[[str(x) for x in r] for r in A] for A in directions],
            'normalized_full_ring_matrix':serial(P)}

def controls():
    # Four transvections do exist if their bank directions depend on N. This
    # word is an excluded control, not four allowed Eij(+-N) queries.
    t=sub(N,O)
    vs=[(Z,neg(N2),neg(N)),(neg(O),Z,neg(N2)),(neg(N),neg(O),Z),(N2,N,O)]
    us=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)]
    word=[];P=eye()
    for u,v in zip(us,vs):
        T=[[plus(O if i==j else Z,scale(mul(t,v[j]),u[i])) for j in range(3)] for i in range(3)]
        D=matsub(T,eye())
        need(mm(D,D)==[[Z]*3 for _ in range(3)],'excluded control has literal unipotent inverse')
        need(coeff_span(D)>1,'N-dependent direction control is outside a one-query constant-direction class')
        P=mm(T,P);word.append(T)
    goal=[[N if i==j else Z for j in range(3)] for i in range(3)]
    need(P==goal,'excluded four-factor word checked on full cubic ring including eigen1')
    for T in reversed(word):P=mm(matsub(eye(),matsub(T,eye())),P)
    need(P==eye(),'literal inverse all three independent columns of excluded control')
    # Primitive-root-only checking would miss this false full-ring equality.
    bad=plus(N,plus(O,plus(N,N2)))
    # a+bN+cN2 maps to (a-c)+(b-c)zeta.
    prim=lambda x:(x[0]-x[2],x[1]-x[2])
    need(prim(bad)==prim(N) and bad!=N and sum(bad)==4,'eigen1 omission control rejected')
    # Treating the whole bank I3 direction as a single paid shear would make
    # N I3 cost1; it is neither rank1 nor nilpotent.
    fake=qeye()
    need(rankq(fake)==3 and qmm(fake,fake)!=[[Q(0)]*3 for _ in range(3)],'rank3 fake query rejected')
    return {'excluded_N_dependent_four_factor_word':[serial(T) for T in word],
            'each_direction_coefficient_span_rank':[coeff_span(matsub(T,eye())) for T in word],
            'full_ring_inverse_all3_inputs':True,'primitive_only_false_identity':{'actual_polynomial':[str(x) for x in bad],'augmentation':str(sum(bad))},
            'fake_rank3_one_call_rejected':True}

def receipt():
    need(mul(N,N)==N2 and mul(N2,N)==O,'exact full cubic ring')
    fixtures=[
      [{'op':'PAID','dst':0,'src':1,'sign':1}],
      [{'op':'FREE','matrix':[[1,1,0],[0,1,1],[0,0,1]]},
       {'op':'PAID','dst':0,'src':2,'sign':-1},
       {'op':'FREE','matrix':[[0,1,0],[1,0,0],[0,0,-1]]},
       {'op':'PAID','dst':2,'src':1,'sign':1}],
      [{'op':'PAID','dst':1,'src':0,'sign':1},
       {'op':'FREE','matrix':[[1,0,1],[1,1,0],[0,0,1]]},
       {'op':'PAID','dst':0,'src':2,'sign':-1},
       {'op':'FREE','matrix':[[1,1,0],[0,1,0],[0,1,1]]},
       {'op':'PAID','dst':2,'src':1,'sign':1},
       {'op':'PAID','dst':0,'src':1,'sign':1}]]
    fixtures.append([
       {'op':'FREE','matrix':[[1,1,0],[0,1,1],[0,0,1]]},
       {'op':'PAID','dst':0,'src':2,'sign':-1,'power':2},
       {'op':'FREE','matrix':[[0,1,0],[1,0,0],[0,0,-1]]},
       {'op':'PAID','dst':2,'src':1,'sign':1,'power':1},
       {'op':'FREE','matrix':[[1,0,1],[1,1,0],[0,0,1]]},
       {'op':'PAID','dst':0,'src':1,'sign':1,'power':2},
       {'op':'PAID','dst':1,'src':2,'sign':-1,'power':1}])
    k=5;m=2+5*k;W=36;H={1:8*k,2:40*k,3:16*k,5:12*k}
    mass=sum(r*n for r,n in H.items())
    need(m*W-mass==-8 and all(0<r<m for r in H),'complete favorable five-call invoice')
    return {'status':'PASS_FOUR_QUERY_CUBIC_CONSTANT_DIRECTION_OBSTRUCTION',
      'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','no_new_kappa':True,
      'coefficient_ring':'Z[N]/(N^3-1); rational constants are allowed in the lower-bound relaxation. No primitive-component equality is promoted to a full-ring equality.',
      'model':'Three arbitrary input fields; paid one-direction shears Eij(+-N) or Eij(+-N^2); any explicit constant scalar GL3(Q) bridges, ADDs, swaps and signs. Eij(N^e-1) for e=1,2 is included by a free inverse ADD. A final constant bank permutation is allowed. No bank-direction vector may depend on N.',
      'normal_form':'Normalize the complete word by its N=1 constant value. Every query becomes I+(N^e-1)u_i v_i^T, e=1 or2, with constant rational u_i,v_i and v_i^T u_i=0. The normal-form fixture checks use the full cubic ring. The written proof further allows arbitrary scalar-polynomial coefficients with constant bank directions.',
      'proof':[
        'Specialize a putative full-ring identity to a primitive cubic root zeta. Target zeta I3 has rank(target-I)=3, so the query column directions span Q^3.',
        'For at most four factors, pad identities if necessary. Some three directions are independent and form a cyclic consecutive triple. Since the target is central and all factors invertible, cyclically rotate the application order so these are the first three.',
        'Conjugate their constant rational directions to e1,e2,e3. The product P=C3 C2 C1 has P11=1 and leading principal2x2 determinant1: each factor changes only its own row and has diagonal pivot1.',
        'The fourth inverse gives P=zeta(I-alpha u v^T), with u,v constant rational. Thus alpha c1=1-zeta^-1 and alpha(c1+c2)=1-zeta^-2, where c_i=u_i v_i are rational.',
        'The ratio (c1+c2)/c1=(1-zeta^-2)/(1-zeta^-1)=-zeta is irrational, a contradiction. For the requested common coefficient alpha=zeta-1, the first equation alone already forces c1=zeta^-1.',
        'The same principal-minor ratio excludes four calls even if each query may use a scalar polynomial in N, including mixtures of N and N^2, as long as its bank direction remains constant. Operator-dependent directions are outside the theorem.'
      ],
      'coverage':'Written all-word proof; no finite covering/search claim. Normalization and controls are finite exact cubic-ring matrix certificates on all three independent columns.',
      'independent_review':{'reviewer':'/root/stabilizer_escape_1019','outcome':'PASS','scope':'Written cyclic-rotation, independent-direction, multiplication-order and principal-minor proof, including mixed N/N^2; no native-bank-code claim. See INDEPENDENT-REVIEW.md.'},
      'normalization_fixtures':[normal_form(w) for w in fixtures],
      'controls':controls(),
      'five_call_favorable_invoice':{'calls':k,'banks':3,'public_ports_per_bank':12,'m':m,'W':W,'H':H,'mass':mass,'stock_rank_mass':m*W,'D':-8,
         'formula':'For k calls and3 banks, m=2+5k,W=36,H1=8k,H2=40k,H3=16k,H5=12k. Every call uses two banks; the third takes its fresh5 idle. D=72-16k.',
         'all_positive_exponent_verdict':'FAIL: already mass>mW at exponent0; every positive contracting-child moment is larger.',
         'optimistic_assumptions':'Source diagonal code, native gauge, private/owner, scalar/address, precision and tape costs all omitted favorably. No native admission is inferred.'},
      'remaining':['A native/operator-dependent bank-direction word with its actual paid cost is outside this scalar model.',
        'More than3 public banks changes determinant, stock, arity and clearing constraints and requires a new complete invoice.',
        'No five-call synthesis is needed for this three-bank route because the favorable five-call mass already fails.'],
      'attribution':'Stabilizer lane supplies the actual common2 order3 Clifford lead and owns its native diagonal-code binding. This lane proves the scalar query lower bound and complete favorable mass gate independently of that native construction.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=receipt();out=json.loads(json.dumps(out))
    p=HERE/'CUBIC-FOUR-CALL-GATE.json'
    if args.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved cubic gate differs')
    print(out['status'])
    print('All-word constant-direction lower bound5; full cubic-ring controls; favorable3bank5call D=-8.')

if __name__=='__main__':main()
