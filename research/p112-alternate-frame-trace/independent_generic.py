"""Formal audit over Q(s,t), c=1+st and d=c+1 both nonzero.

No coefficient samples, producer imports, or parameter search.  The literal
anchor and old flag equations are separately authenticated.  Numerators are
sparse polynomials; denominators are powers of the two declared nonzero
polynomials c,d.  The last six indeterminates parameterize every rank<=1 R.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[1]
N = 8
ZERO = (0,)*N

def need(ok, msg):
    if not ok: raise ValueError(msg)

def pa(a,b):
    out = dict(a)
    for k,v in b.items():
        out[k] = out.get(k,0)+v
        if not out[k]: del out[k]
    return out

def pm(a,b):
    out = {}
    for k,v in a.items():
        for l,w in b.items():
            m = tuple(x+y for x,y in zip(k,l))
            out[m] = out.get(m,0)+v*w
            if not out[m]: del out[m]
    return out

def pp(a,n):
    result = {ZERO:F(1)}
    for _ in range(n): result = pm(result,a)
    return result

st = list(ZERO); st[0] = st[1] = 1
CP = {ZERO:F(1),tuple(st):F(1)}
DP = {ZERO:F(2),tuple(st):F(1)}

class Q:
    def __init__(self,value=0,c=0,d=0):
        if isinstance(value,Q): self.p,self.c,self.d = value.p,value.c,value.d
        else:
            self.p = value if isinstance(value,dict) else ({ZERO:F(value)} if value else {})
            self.c,self.d = c,d
        if not self.p: self.c=self.d=0
    @staticmethod
    def variable(i):
        m = list(ZERO); m[i]=1
        return Q({tuple(m):F(1)})
    def __add__(self,other):
        b=Q(other); c=max(self.c,b.c); d=max(self.d,b.d)
        a1=pm(pm(self.p,pp(CP,c-self.c)),pp(DP,d-self.d))
        b1=pm(pm(b.p,pp(CP,c-b.c)),pp(DP,d-b.d))
        return Q(pa(a1,b1),c,d)
    __radd__=__add__
    def __neg__(self): return Q({m:-v for m,v in self.p.items()},self.c,self.d)
    def __sub__(self,other): return self+-Q(other)
    def __rsub__(self,other): return Q(other)+-self
    def __mul__(self,other):
        b=Q(other)
        return Q(pm(self.p,b.p),self.c+b.c,self.d+b.d)
    __rmul__=__mul__
    def __eq__(self,other): return not (self-Q(other)).p

def tr(A): return list(map(list,zip(*A)))
def mm(A,B): return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]
def eye(n): return [[F(i==j) for j in range(n)] for i in range(n)]
def sub(A,B): return [[x-y for x,y in zip(a,b)] for a,b in zip(A,B)]
def add(A,B): return [[x+y for x,y in zip(a,b)] for a,b in zip(A,B)]
def scale(A,c): return [[c*x for x in row] for row in A]
def part(A,I,J): return [[A[i][j] for j in J] for i in I]
def trace(A): return sum(A[i][i] for i in range(len(A)))
def rref(A,n):
    rows=[list(map(F,row)) for row in A]; piv=[]
    for c in range(n):
        p=len(piv); i=next((i for i in range(p,len(rows)) if rows[i][c]),None)
        if i is None: continue
        rows[p],rows[i]=rows[i],rows[p]; x=rows[p][c]
        rows[p]=[a/x for a in rows[p]]
        for i in range(len(rows)):
            if i!=p:
                x=rows[i][c]; rows[i]=[a-x*b for a,b in zip(rows[i],rows[p])]
        piv.append(c)
    return rows,piv
def rank(A): return len(rref(A,len(A[0]))[1]) if A else 0
def independent(A):
    out=[]
    for i,row in enumerate(A):
        if rank([A[j] for j in out]+[row])>len(out): out.append(i)
    return out
def inverse(A):
    n=len(A); rows,piv=rref([row+e for row,e in zip(A,eye(n))],n)
    need(len(piv)==n,'invertible numeric anchor minor')
    return [row[n:] for row in rows]
def det(A):
    out=Q(0); n=len(A)
    for p in permutations(range(n)):
        v=Q((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n)))
        for i,j in enumerate(p): v=v*A[i][j]
        out=out+v
    return out

def run():
    pins={'research/p112-alternate-frame-trace/FIXTURE.json':'13e1f33aa04e417968535d2b2fd4eb2b90672e117b95c0d449d3796563883578'}
    data=[]
    for path,h in pins.items():
        raw=(WORK/path).read_bytes(); need(sha256(raw).hexdigest()==h,'frozen literal '+path)
        data.append(json.loads(raw))
    A=[list(map(F,row)) for row in data[0]['asymmetric_template_matrix']]
    ri=independent(A); ci=independent(tr([A[i] for i in ri]))
    U=part(A,range(12),ci)
    V=mm(inverse(part(A,ri,ci)),[A[i] for i in ri])
    need(mm(U,V)==A and len(ri)==8,'anchor rank factorization')
    # Complete block-diagonal centralizer, independently encoded as 144
    # linear commutator equations in 36 unknowns. This supports the stated
    # scope distinction, but is not used in the obstruction below.
    atoms=[]
    for g in range(4):
        for i in range(3):
            for j in range(3):
                G=[[F(0)]*12 for _ in range(12)]; G[3*g+i][3*g+j]=1
                atoms.append(G)
    commutators=[sum(sub(mm(G,A),mm(A,G)),[]) for G in atoms]
    need(rank(tr(commutators))==29,'complete centralizer dimension seven')
    expected=[]
    for entries in ([(0,0,0),(0,1,1),(1,0,0),(2,0,0),(3,0,0),(3,1,1)],[(0,2,2)],[(3,2,2)]):
        G=[[F(0)]*12 for _ in range(12)]
        for g,i,j in entries: G[3*g+i][3*g+j]=1
        expected.append(G)
    for i in (1,2):
        for j in (1,2):
            G=[[F(0)]*12 for _ in range(12)]
            for g in (1,2): G[3*g+i][3*g+j]=1
            expected.append(G)
    need(rank([sum(G,[]) for G in expected])==7 and all(mm(G,A)==mm(A,G) for G in expected),'literal centralizer equals claimed seven-dimensional space')
    af,bf=[],[]
    for i in range(2):
        eq=data[0]['saturated_rectangle_compatibility'][0]['new_group_spaces'][i]['equations']
        rows=mm([list(map(F,row)) for row in eq],U)
        need(rank(rows)==1,'source flag rank')
        af.append(next(row+[F(0)] for row in rows if any(row)))
        eq=data[0]['saturated_rectangle_compatibility'][1]['new_group_spaces'][i]['equations']
        rows=mm([list(map(F,row)) for row in eq],tr(V))
        need(rank(rows)==1,'reader flag rank')
        bf.append(next(row+[F(0)] for row in rows if any(row)))
    U=[row+[F(0)] for row in U]; V=V+[[F(0)]*12]
    s,t=Q.variable(0),Q.variable(1); c=Q(CP); d=Q(DP)
    ci,di=Q(1,c=1),Q(1,d=1)
    H=[[x+t*y for x,y in zip(U[6],U[7])],U[1],U[11]]
    K=tr([[row[6]+s*row[7] for row in V],[row[1] for row in V],[row[11] for row in V]])
    need(mm(H,K)==[[c,0,0],[0,1,0],[0,0,1]],'all-parameter annihilator pairing')
    P0=sub(eye(9),mm(mm(K,[[ci,0,0],[0,1,0],[0,0,1]]),H))
    Pi=sub(eye(9),P0)
    ZA=mm(part(V,range(9),range(3)),U[:3])
    ZC=mm(part(V,range(9),range(6,9)),U[6:9])
    need(trace(mm(mm(mm(Pi,ZA),Pi),ZC))==ci,'formal anchor-invariant tau=1/c')
    aa=mm(af,P0); bb=mm(P0,tr(bf))
    need(mm(aa,bb)==[[-d*ci,0],[0,1]],'all-parameter flag pairings')
    fixed=mm([[row[1]] for row in bb],[aa[1]])
    killed=scale(mm([[row[0]] for row in bb],[aa[0]]),-c*di)
    middle=sub(sub(P0,fixed),killed)
    need(mm(middle,middle)==middle,'middle projector')
    u=[[1],[s],[0]]; v=[[1,t,0]]; uv=mm(u,v)
    E=scale(uv,ci); S=sub(eye(3),scale(uv,di)); Sinv=add(eye(3),uv)
    need(mm(S,Sinv)==eye(3),'invertible generic B coordinate map')
    UB=U[3:6]; VB=part(V,range(9),range(3,6))
    need(mm(mm(UB,middle),VB)==S,'literal S')
    X=mm(mm(middle,VB),Sinv)
    X=[row+[F(i==8)] for i,row in enumerate(X)]
    Y=mm(UB,middle)+[[F(i==8) for i in range(9)]]
    need(mm(Y,X)==eye(4) and mm(X,Y)==middle,'complete generic four-dimensional chart')
    need(mm(mm(UB,fixed),VB)==[[0]*3 for _ in range(3)],'fixed group3 direction misses B')
    L=mm(U,X); R=mm(Y,V)
    need(L[3:6]==[row+[0] for row in eye(3)] and part(R,range(4),range(3,6))==S+[[0]*3],'literal LB/RB normal form')
    # Combined-pair flags annihilate the H/K directions. This implies the
    # exact BC Schur reduction for every middle projector, not just samples.
    Jv=sub(eye(3),mm([[1],[0],[0]],v)); Ju=sub(eye(3),mm(u,[[1,0,0]]))
    need(L[6:9]==mm(Jv,L[3:6]),'C source dependence')
    need(part(R,range(4),range(6,9))==mm(part(R,range(4),range(3,6)),Ju),'C reader dependence')
    need(part(A,range(3,9),range(3,9))==[row+row for row in eye(3)]*2,'BC fixed matrix')
    need(mm(mm(U[3:9],fixed),part(V,range(9),range(3,9)))==[[0]*6 for _ in range(6)],'fixed direction misses BC')
    CD=range(6,12)
    Z=mm(part(R,range(4),CD),[L[i] for i in CD])
    e0=[[1],[0],[0]]; w=sub(e0,scale(u,di))
    W=add(eye(3),mm(w,[[1,0,0]]))
    need(Z==[row+[0] for row in W]+[[0]*4],'literal cap28 W')
    need(mm(mm(part(V,range(9),CD),[U[i] for i in CD]),fixed)==[[0]*9 for _ in range(9)],'cap28 kills fixed direction on right')
    need(mm(fixed,mm(part(V,range(9),CD),[U[i] for i in CD]))==[[0]*9 for _ in range(9)],'cap28 kills fixed direction on left')
    need(part(A,CD,CD)==eye(6),'CD anchor identity')
    # Complete rank<=1 R=x y^t, with no generic coefficient assumption.
    x=[[Q.variable(2+i)] for i in range(3)]; y=[[Q.variable(5+i) for i in range(3)]]
    B=mm(x,y); T=sub(B,E); Atop=mm(T,Sinv)
    S4=[row+[z[0]] for row,z in zip(sub(eye(3),T),mm(T,u))]+[mm(v,T)[0]+[-mm(mm(v,T),u)[0][0]]]
    need(det(S4)==c*(1-trace(B)),'all-parameter rank-one cap22 determinant')
    need(det(sub(eye(3),Atop))==(c+2)*(1-trace(B))+trace(mm(E,B)),'complement minor including c=-2')
    need(mm(Atop,w)==sub(mm(B,e0),scale(u,ci)),'trace reduction Aw')
    # These scalar identities make the two-case proof independent of c=-2
    # or zero coordinates in the rank-one factors.
    need(d+1+ci==d*d*ci,'nonzero forced R00=d^2/c')
    return {'status':'PASS_INDEPENDENT_GENERIC_FRAME_REDUCTION','parameters':'s,t in Q; c=1+st !=0; d=c+1 !=0',
            'literal_symbolic_reductions':True,'coefficient_samples':0,'rank_one_parameterization_complete':True,
            'block_centralizer_dimension':7,'formal_invariant':'tau=1/(1+st)',
            'input_sha256':pins,'scope':'Fixed anchor, H_t=(C0+tC1,A1,D2), K_s=(C0+sC1,A1,D2); exceptional st=-2 not covered.'}

if __name__=='__main__':
    import sys
    result=run()
    receipt=HERE/'INDEPENDENT-GENERIC-RESULT.json'
    if sys.argv[1:]==['--write-receipt']:
        receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(not sys.argv[1:],'only --write-receipt is accepted')
        need(json.loads(receipt.read_text(encoding='utf-8'))==result,'committed independent receipt matches recomputation')
    print(json.dumps(result,indent=2))
