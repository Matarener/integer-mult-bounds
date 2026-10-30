"""Independent exceptional st=-2 chart audit, no search.

Only frozen literal data are consumed. No producer algebra is imported.
The polynomial identities below are identities, not coefficient samples.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path, digest):
    raw = (WORK / path).read_bytes()
    need(sha256(raw).hexdigest() == digest, 'input authentication: ' + path)
    return json.loads(raw)


def tr(A):
    return list(map(list, zip(*A)))


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mm(A, B):
    return [[sum((a*b for a, b in zip(row, col)), F(0)) for col in zip(*B)] for row in A]


def part(A, rows, cols):
    return [[A[i][j] for j in cols] for i in rows]


def rref(A, n):
    A = [list(map(F, row)) for row in A]
    pivots = []
    for col in range(n):
        p = len(pivots)
        i = next((i for i in range(p, len(A)) if A[i][col]), None)
        if i is None:
            continue
        A[i], A[p] = A[p], A[i]
        scale = A[p][col]
        A[p] = [x/scale for x in A[p]]
        for i in range(len(A)):
            if i != p:
                scale = A[i][col]
                A[i] = [x-scale*y for x, y in zip(A[i], A[p])]
        pivots.append(col)
    return A, pivots


def rank(A):
    return len(rref(A, len(A[0]) if A else 0)[1])


def inverse(A):
    n = len(A)
    B, pivots = rref([row+unit for row, unit in zip(A, eye(n))], n)
    need(len(pivots) == n, 'nonsingular coordinate change')
    return [row[n:] for row in B]


def kernel(A, n):
    R, pivots = rref(A, n)
    out = []
    for free in range(n):
        if free not in pivots:
            v = [F(i == free) for i in range(n)]
            for i, pivot in enumerate(pivots):
                v[pivot] = -R[i][free]
            out.append(v)
    return out


def independent(rows):
    out = []
    for i, row in enumerate(rows):
        if rank([rows[j] for j in out]+[row]) > len(out):
            out.append(i)
    return out


def binary_rank(A):
    basis = {}
    for row in A:
        v = sum((int(x)&1) << i for i, x in enumerate(row))
        while v:
            b = v.bit_length()-1
            if b not in basis:
                basis[b] = v
                break
            v ^= basis[b]
    return len(basis)


# Sparse rational polynomials in sixteen indeterminates.
ZERO = (0,)*16


def const(x):
    return {ZERO:F(x)} if x else {}


def var(i):
    degree = list(ZERO)
    degree[i] = 1
    return {tuple(degree):F(1)}


def add(a, b):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0)+value
        if not out[key]:
            del out[key]
    return out


def neg(a):
    return {m:-c for m, c in a.items()}


def mul(a, b):
    out = {}
    for x, p in a.items():
        for y, q in b.items():
            key = tuple(i+j for i, j in zip(x, y))
            out[key] = out.get(key, 0)+p*q
            if not out[key]:
                del out[key]
    return out


def pm(A, B):
    C = []
    for row in A:
        new = []
        for col in zip(*B):
            value = {}
            for a, b in zip(row, col):
                value = add(value, mul(a, b))
            new.append(value)
        C.append(new)
    return C


def lift(A):
    return [[const(x) for x in row] for row in A]


def subtract(A, B):
    return [[add(a, neg(b)) for a, b in zip(ar, br)] for ar, br in zip(A, B)]


def determinant(A):
    n = len(A)
    total = {}
    for p in permutations(range(n)):
        term = const((-1)**sum(p[i] > p[j] for i in range(n) for j in range(i+1, n)))
        for i, j in enumerate(p):
            term = mul(term, A[i][j])
        total = add(total, term)
    return total


def sub(A,B):
    return [[x-y for x,y in zip(a,b)] for a,b in zip(A,B)]


def run():
    pins={'research/p112-alternate-frame-trace/FIXTURE.json': '13e1f33aa04e417968535d2b2fd4eb2b90672e117b95c0d449d3796563883578', 'research/p112-rational-decoder-gate/CANDIDATE.json': 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b', 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'}
    old,candidate,data=[read(p,h) for p,h in pins.items()]
    flags=old
    A=[list(map(F,row)) for row in old['asymmetric_template_matrix']]
    ri=independent(A); ci=independent(tr([A[i] for i in ri]))
    U=part(A,range(12),ci)
    V=mm(inverse(part(A,ri,ci)),[A[i] for i in ri])
    need(rank(A)==8 and mm(U,V)==A,'literal anchor factorization')
    af,bf=[],[]
    for i in range(2):
        eq=flags['saturated_rectangle_compatibility'][0]['new_group_spaces'][i]['equations']
        rows=mm([list(map(F,row)) for row in eq],U)
        need(rank(rows)==1,'source flag rank')
        af.append(next(row+[F(0)] for row in rows if any(row)))
        eq=flags['saturated_rectangle_compatibility'][1]['new_group_spaces'][i]['equations']
        rows=mm([list(map(F,row)) for row in eq],tr(V))
        need(rank(rows)==1,'reader flag rank')
        bf.append(next(row+[F(0)] for row in rows if any(row)))
    U=[row+[F(0)] for row in U]; V=V+[[F(0)]*12]
    H=[[x+y for x,y in zip(U[6],U[7])],U[1],U[11]]
    K=tr([[row[6]-2*row[7] for row in V],[row[1] for row in V],[row[11] for row in V]])
    need(mm(H,K)==[[-1,0,0],[0,1,0],[0,0,1]],'exceptional nondegenerate combined frame')
    X=tr(kernel(H,9))
    Y=inverse([x+k for x,k in zip(X,K)])[:6]
    need(mm(Y,X)==eye(6),'combined pair own identity')
    aa=mm(af,X); bb=mm(Y,tr(bf))
    need(mm(aa,bb)==[[0,0],[0,1]],'zero first flag pairing is retained')
    b3,b4=tr(bb)
    common=[b3]
    for z in kernel(aa,6):
        if rank(common+[z])>len(common): common.append(z)
    need(len(common)==4,'flag kernel includes nonzero killed b3')
    last=[F(0)]*6; pivot=next(i for i,x in enumerate(aa[0]) if x)
    last[pivot]=1/aa[0][pivot]
    last=[x-sum(a*b for a,b in zip(aa[1],last))*z for x,z in zip(last,b4)]
    D=tr([b4]+common+[last])
    need(rank(D)==6,'exceptional full coordinate chart')
    need(mm(aa,D)==[[0,0,0,0,0,1],[1,0,0,0,0,0]],'literal exceptional row flags')
    need(mm(inverse(D),bb)==[[0,1],[1,0],[0,0],[0,0],[0,0],[0,0]],'literal exceptional column flags')
    L=mm(mm(U,X),D); R=mm(mm(inverse(D),Y),V)
    LB=L[3:6]; RB=part(R,range(6),range(3,6))
    CD=range(6,12); Z=mm(part(R,range(6),CD),[L[i] for i in CD])
    need(part(A,CD,CD)==eye(6),'CD anchor own identity')
    need(not any(Z[0]) and not any(row[0] for row in Z),'fixed image direction annihilated by CD')
    expectedZ=[[1,0,0,0,0],[0,1,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[1,-1,0,0,1]]
    need(part(Z,range(1,6),range(1,6))==expectedZ,'literal exceptional Z5')
    # Full rank-two factorization of the five-dimensional residual projector.
    # Its first column and last row are zero by the exact flags.  Full-rank
    # X5,Y5 imply those zero rows/columns also hold in this factorization.
    X5=[[var(2*i+j) for j in range(2)] for i in range(4)]+[[{},{}]]
    Y5=[[{}]+[var(8+2*j+i) for j in range(4)] for i in range(2)]
    alpha,x0,x1,x2=X5[:4]
    y0,y1,y2,beta=tr(Y5)[1:]
    Xbar=[x0,alpha,x1]
    Yprime=tr([[add(a,neg(b)) for a,b in zip(y0,beta)],beta,y1])
    need(pm(Yprime,Xbar)==pm(pm(Y5,lift(expectedZ)),X5),'cap28 makes Yprime Xbar=I2')
    F3=pm(Xbar,Yprime)
    P=lift([[int(i==j==0) for j in range(6)] for i in range(6)])
    P5=pm(X5,Y5)
    for i in range(5):
        for j in range(5): P[i+1][j+1]=P5[i][j]
    E=sub(eye(3),mm(LB,RB))
    residual=[[add(const(E[i][j]),v) for j,v in enumerate(row)] for i,row in enumerate(pm(pm(lift(LB),P),lift(RB)))]
    L0=[[1,-1,0],[0,2,0],[0,0,1]]
    N0=[[0,F(-1,2),0],[-1,F(-3,2),0],[0,0,1]]
    shifted=[[add(v,const(int(i==1 and j==0)-int(i==j==1))) for j,v in enumerate(row)] for i,row in enumerate(F3)]
    need(residual==pm(pm(lift(L0),shifted),lift(N0)),'literal all-variable cap34 rank-drop form')
    need(rank(L0)==rank(N0)==3,'cap34 transformations invertible')
    # Exact invariant minor forced after F e1=e1.  The extra coordinate of
    # b3+mu*external is invisible to every anchor row, for any mu.
    need(all(row[4]==0 for row in L),'external image coordinate invisible to anchor')
    AC=list(range(3))+list(range(6,9))
    minor=[ [A[i][j] for j in (6,7,8,9)]+[L[i][0],L[i][1]] for i in AC ]
    need(determinant(lift(minor))==const(-1),'forced constant six-dimensional minor')
    labels={r['port']:r['q'] for r in data['recipes']}
    groups=[1,2,27,28,3,4]
    qs=[[labels[p] for p in candidate['groups'][g]] for g in groups]
    def tariff(sm,tm):
        a=[q for i,rows in enumerate(qs) if sm>>i&1 for q in rows]
        b=[q for i,rows in enumerate(qs) if tm>>i&1 for q in rows]
        return binary_rank([[(x&y).bit_count()%2 for y in b] for x in a])
    need(tariff(5,28)==5 and tariff(34,34)==4 and tariff(28,28)==7,'physical contradiction tariffs')
    # The st=-2 orbit reduction is a block-diagonal gauge: simultaneously
    # scale B,C axis1 by r and inverse-scale their reader coordinates.
    weight=[int(i in (4,7)) for i in range(12)]
    need(all(not A[i][j] or weight[i]==weight[j] for i in range(12) for j in range(12)),'all nonzero gauge scalings preserve literal anchor')
    # One declared three-cap positive control, not a parameter search.
    Pn=[[F(0)]*6 for _ in range(6)]
    for i,j in ((0,0),(1,4),(1,5),(3,3),(4,4),(4,5)): Pn[i][j]=1
    need(mm(Pn,Pn)==Pn and rank(Pn)==3,'literal three-cap projector')
    need(mm(mm(aa,D),Pn)==[[0]*6,mm(aa,D)[1]],'control source flags')
    bn=mm(inverse(D),bb)
    need(mm(Pn,bn)==[[0,row[1]] for row in bn],'control reader flags')
    Pc=sub(eye(6),Pn)
    split=tr([tr(Pn)[i] for i in independent(tr(Pn))]+[tr(Pc)[i] for i in independent(tr(Pc))])
    Ls=mm(L,split); Rs=mm(inverse(split),R)
    M=[A[i]+Ls[i] for i in range(12)]+[Rs[i]+eye(6)[i] for i in range(6)]
    need(rank(M)==9 and part(M,range(12,18),range(12,18))==eye(6),'control full rank and new own identity')
    failures=[]; caps={}
    for sm in range(1,64):
        si=[3*g+a for g in range(6) if sm>>g&1 for a in range(3)]
        for tm in range(1,64):
            ti=[3*g+a for g in range(6) if tm>>g&1 for a in range(3)]
            r=rank(part(M,si,ti)); c=tariff(sm,tm)
            if r>c: failures.append([sm,tm,r,c])
            if sm==tm and sm in (22,28,34): caps[str(sm)]=[r,c]
    need(caps=={'22':[6,6],'28':[7,7],'34':[4,4]},'all three claimed control caps pass')
    need(len(failures)==12 and [5,28,6,5] in failures,'control is not a valid complete lift')
    need(determinant(lift([row[:-1]+[F(0)] for row in minor]))==const(0),'deleting forced b3 anchor direction destroys this minor')
    return {'status':'PASS_INDEPENDENT_EXCEPTIONAL_FRAME_OBSTRUCTION','parameter_orbit':'st=-2, represented by t=1,s=-2',
            'input_sha256':pins,'complete_factorization':'P=diag(1,X5Y5); Y5X5=I2; first column and last row of P5 vanish',
            'symbolic_variables':16,'coefficient_samples':0,'forced_rectangle':[5,28],'forced_minor_determinant':-1,'physical_tariff':5,
            'control_full_rank':9,'control_rectangles_checked':3969,'control_three_caps':caps,'control_failures':failures,
            'scope':'Fixed anchor and this one two-parameter common-frame family only; other common frames remain open.'}


if __name__=='__main__':
    import sys
    result=run()
    receipt=HERE/'INDEPENDENT-EXCEPTIONAL-RESULT.json'
    if sys.argv[1:]==['--write-receipt']:
        receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(not sys.argv[1:],'only --write-receipt is accepted')
        need(json.loads(receipt.read_text(encoding='utf-8'))==result,'committed independent receipt matches recomputation')
    print(json.dumps(result,indent=2))


