"""Exact all-projector obstruction for the frozen alternate P112 frame.

Stdlib only. Reconstructs rational frames and physical caps; proves polynomial
identities with formal variables. No coefficient or geometry enumeration.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[1]
PINS = {'research/p112-alternate-frame-trace/FIXTURE.json': '13e1f33aa04e417968535d2b2fd4eb2b90672e117b95c0d449d3796563883578', 'research/p112-rational-decoder-gate/CANDIDATE.json': 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b', 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'}

def need(condition, message):
    if not condition:
        raise ValueError(message)

def read(name):
    raw = (WORK / name).read_bytes()
    need(sha256(raw).hexdigest() == PINS[name], 'frozen input hash: ' + name)
    return json.loads(raw)

def tr(A): return list(map(list, zip(*A)))
def mm(A, B): return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]
def eye(n): return [[F(i==j) for j in range(n)] for i in range(n)]
def sub(A, B): return [[x-y for x,y in zip(a,b)] for a,b in zip(A,B)]
def dump(A): return [[str(x) for x in row] for row in A]

def rref(A, n=None):
    n = len(A[0]) if A and n is None else (n or 0)
    rows = [list(map(F,row)) for row in A]
    pivots = []
    p = 0
    for c in range(n):
        j = next((j for j in range(p,len(rows)) if rows[j][c]), None)
        if j is None: continue
        rows[p],rows[j] = rows[j],rows[p]
        scale = rows[p][c]
        rows[p] = [v/scale for v in rows[p]]
        for j in range(len(rows)):
            if j != p and rows[j][c]:
                scale = rows[j][c]
                rows[j] = [v-scale*w for v,w in zip(rows[j],rows[p])]
        pivots.append(c)
        p += 1
    return rows, pivots

def rank(A): return len(rref(A)[1])

def independent(A):
    result = []
    for i,row in enumerate(A):
        if rank([A[j] for j in result]+[row]) > len(result): result.append(i)
    return result

def nullspace(A, n):
    rows,pivots = rref(A,n)
    result = []
    for c in range(n):
        if c in pivots: continue
        v = [F(0)]*n
        v[c] = 1
        for i,p in enumerate(pivots): v[p] = -rows[i][c]
        result.append(v)
    return result

def inverse(A):
    n = len(A)
    rows,pivots = rref([list(row)+e for row,e in zip(A,eye(n))],n)
    need(pivots == list(range(n)), 'invertible rational coordinate matrix')
    return [row[n:] for row in rows]

def binary_rank(A):
    pivots = {}
    for x in A:
        while x:
            p = x.bit_length()-1
            if p not in pivots:
                pivots[p] = x
                break
            x ^= pivots[p]
    return len(pivots)

def tariff(source, reader):
    return binary_rank(sum(((x&y).bit_count()&1)<<j for j,y in enumerate(reader)) for x in source)

class Poly:
    """Sparse Q-polynomials; monomials are sorted variable-name tuples."""
    def __init__(self,value=0):
        self.terms = value.terms.copy() if isinstance(value,Poly) else ({():F(value)} if value else {})
    @staticmethod
    def terms_result(terms):
        p = Poly(); p.terms = {m:c for m,c in terms.items() if c}; return p
    @staticmethod
    def variable(name): return Poly.terms_result({(name,):F(1)})
    def __add__(self,other):
        result = self.terms.copy()
        for m,c in Poly(other).terms.items(): result[m] = result.get(m,F(0))+c
        return Poly.terms_result(result)
    __radd__ = __add__
    def __neg__(self): return Poly.terms_result({m:-c for m,c in self.terms.items()})
    def __sub__(self,other): return self + -Poly(other)
    def __rsub__(self,other): return Poly(other) + -self
    def __mul__(self,other):
        result = {}
        for m,c in self.terms.items():
            for n,d in Poly(other).terms.items():
                k = tuple(sorted(m+n)); result[k] = result.get(k,F(0))+c*d
        return Poly.terms_result(result)
    __rmul__ = __mul__
    def __eq__(self,other): return self.terms == Poly(other).terms
    def __str__(self):
        return ' + '.join(str(c)+(('*'+'*'.join(m)) if m else '') for m,c in sorted(self.terms.items())) or '0'

def det(A):
    if not A: return 1
    return sum((-1)**j*A[0][j]*det([row[:j]+row[j+1:] for row in A[1:]]) for j in range(len(A)))

def main():
    old, candidate, data = [read(name) for name in PINS]
    previous = old
    A = [list(map(F,row)) for row in old['asymmetric_template_matrix']]
    need(rank(A) == 8, 'rank-eight literal anchor')
    I = independent(A); J = independent(tr([A[i] for i in I]))
    U = [[A[i][j] for j in J] for i in range(12)]
    V = mm(inverse([[A[i][j] for j in J] for i in I]),[A[i] for i in I])
    need(mm(U,V) == A, 'exact anchor factorization')
    groups = [1,2,27,28,3,4]
    labels = {r['port']:r['q'] for r in data['recipes']}
    E = [[labels[p] for p in candidate['groups'][g]] for g in groups]
    anchor_caps_checked = 0
    for smask in range(1,16):
        si = [3*g+a for g in range(4) if smask>>g&1 for a in range(3)]
        source = sum((E[g] for g in range(4) if smask>>g&1),[])
        for tmask in range(1,16):
            ti = [3*g+a for g in range(4) if tmask>>g&1 for a in range(3)]
            reader = sum((E[g] for g in range(4) if tmask>>g&1),[])
            need(rank([[A[i][j] for j in ti] for i in si]) <= tariff(source,reader), 'anchor rectangle domination')
            anchor_caps_checked += 1
    for g in range(4):
        need([row[3*g:3*g+3] for row in A[3*g:3*g+3]] == eye(3), 'anchor own group identity')
    caps = {}
    for mask in (22,28,34):
        q = sum((E[i] for i in range(6) if mask>>i&1),[])
        caps[str(mask)] = tariff(q,q)
    need(caps == {'22':6,'28':7,'34':4}, 'three exact physical self tariffs')
    axes = [6,1,11]
    H0 = [U[i]+[F(0)] for i in axes]
    K0 = tr([[V[i][j] for j in axes] for i in range(8)]+[[F(0)]*3])
    need(mm(H0,tr(K0)) == eye(3), 'selected source-reader complement pairing')
    X = tr(nullspace(H0,9))
    Y = inverse([row+[K0[j][i] for j in range(3)] for i,row in enumerate(X)])[:6]
    need(mm(Y,X) == eye(6), 'combined new-pair identity')

    # Regenerate individual saturated-anchor flags from physical tariffs.
    flags = []
    premises = []
    for side in range(2):
        anchor = tr(A) if side else A
        frame = tr(V) if side else U
        side_flags = []
        side_premises = []
        for added in (4,5):
            equations = []
            witnesses = []
            for smask in range(1,16):
                si = [3*g+a for g in range(4) if smask>>g&1 for a in range(3)]
                source = sum((E[g] for g in range(4) if smask>>g&1),[])
                for tmask in range(16):
                    ti = [3*g+a for g in range(4) if tmask>>g&1 for a in range(3)]
                    reader = sum((E[g] for g in range(4) if tmask>>g&1),[])+E[added]
                    rect = [[anchor[i][j] for j in ti] for i in si]
                    cap = tariff(source,reader)
                    if rank(rect) != cap: continue
                    for kernel in nullspace(tr(rect) if ti else [],len(si)):
                        row = [F(0)]*12
                        for i,c in zip(si,kernel): row[i] = c
                        if rank(equations+[row]) > len(equations):
                            equations.append(row); witnesses.append([smask,tmask,cap])
            saved = [list(map(F,row)) for row in old['saturated_rectangle_compatibility'][side]['new_group_spaces'][added-4]['equations']]
            need(rank(saved) == rank(equations) == rank(saved+equations), 'independent replay flags equal all regenerated saturated constraints')
            transformed = mm(equations,frame)
            need(rank(transformed) == 1, 'one nontrivial flag per group and side')
            side_flags.append(next(v+[F(0)] for v in transformed if any(v)))
            side_premises.append(witnesses)
        flags.append(side_flags); premises.append(side_premises)
    a = mm(flags[0],X); b = mm(Y,tr(flags[1]))
    need(mm(a,b) == [[-2,0],[0,1]], 'exact cross-flag pairings')
    common = nullspace(a,6)
    need(len(common) == 4, 'four-dimensional common flag kernel')
    D = tr([[row[1] for row in b]]+common+[[row[0] for row in b]])
    need(dump(D) == previous['coordinate_change'], 'agreement with frozen alternate coordinate fixture')
    need(mm(a,D) == [[0,0,0,0,0,-2],[1,0,0,0,0,0]], 'flags select fixed-one/fixed-zero coordinates')
    L = mm(mm([row+[F(0)] for row in U],X),D)
    R = mm(mm(inverse(D),Y),V+[[F(0)]*12])

    # Every admissible split is diag(1,Q,0), Q^2=Q and rank(Q)=2.
    Q = [[Poly.variable('q'+str(i)+str(j)) for j in range(4)] for i in range(4)]
    P = [[Poly(i==j==0) for j in range(6)] for i in range(6)]
    for i in range(4):
        for j in range(4): P[i+1][j+1] = Q[i][j]
    LB = L[3:6]; RB = [[R[i][j] for j in range(3,6)] for i in range(6)]
    T = mm(mm(LB,P),RB)
    need(T == [[Q[i][j]*(F(1,2) if j==0 else 1) for j in range(3)] for i in range(3)], 'mask34 exact top-three compression')
    need(mm(LB,RB) == [[F(i==j and i>0) for j in range(3)] for i in range(3)], 'mask34 constant defect')

    # Mask22: eliminate the new group's I3; subtract B block rows/columns.
    BC = list(range(3,9))
    correction = mm(mm([L[i] for i in BC],P),[[R[i][j] for j in BC] for i in range(6)])
    S = [[Poly(A[i][j])-correction[s][t] for t,j in enumerate(BC)] for s,i in enumerate(BC)]
    for i in range(3,6): S[i] = [x-y for x,y in zip(S[i],S[i-3])]
    for row in S:
        for j in range(3,6): row[j] = row[j]-row[j-3]
    need(all(S[i][j] == 0 for i in range(6) for j in range(6) if i>=4 or j>=4), 'mask22 leaves just four coordinates')
    S4 = [row[:4] for row in S[:4]]
    expected = [[Poly(i==j)-T[i][j] for j in range(3)]+[T[i][0]] for i in range(3)]+[T[0]+[-T[0][0]]]
    need(S4 == expected, 'mask22 four by four Schur matrix')

    # Mask28: CD own block is I6. The fixed-one direction sees zero.
    CD = list(range(6,12))
    need([[A[i][j] for j in CD] for i in CD] == eye(6), 'CD own block I6')
    Z = mm([[R[i][j] for j in CD] for i in range(6)],[L[i] for i in CD])
    need(not any(Z[0]) and not any(row[0] for row in Z), 'mask28 fixed-one direction is annihilated')
    W = [[Z[i][j] for j in range(1,5)] for i in range(1,5)]
    need(W == [[F(3,2),0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,0]], 'literal mask28 middle operator')
    residual = sub(P,mm(mm(P,Z),P))
    Qresidual = sub(Q,mm(mm(Q,W),Q))
    expected = [[Poly(i==j==0) for j in range(6)] for i in range(6)]
    for i in range(4):
        for j in range(4): expected[i+1][j+1] = Qresidual[i][j]
    need(residual == expected, 'mask28 residual has a fixed one plus Q-QWQ')

    # All rank<=1 matrices are u v^t, including zero. This is a complete
    # parameterization, not coefficient sampling. Mask34 forces this rank.
    u = [Poly.variable('u'+str(i)) for i in range(3)]
    v = [Poly.variable('v'+str(i)) for i in range(3)]
    B = [[x*y for y in v] for x in u]       # B=E00+T
    T1 = [[B[i][j]-Poly(i==j==0) for j in range(3)] for i in range(3)]
    A3 = [[T1[i][j]*(2 if j==0 else 1) for j in range(3)] for i in range(3)]
    S41 = [[Poly(i==j)-T1[i][j] for j in range(3)]+[T1[i][0]] for i in range(3)]+[T1[0]+[-T1[0][0]]]
    g22 = det(S41)
    gI = det([[Poly(i==j)-A3[i][j] for j in range(3)] for i in range(3)])
    r = B[0][0]; s = B[1][1]+B[2][2]
    need(g22 == 1-r-s, 'rank-one mask22 determinant identity')
    need(gI == 3-2*r-3*s, 'rank-one complementary minor identity')
    q33 = 2-sum(A3[i][i] for i in range(3))  # trace(Q)=rank(Q)=2 over Q.
    trace_defect = F(1,2)*A3[0][0]-q33
    need(trace_defect+7*g22-2*gI == -4, 'exact contradiction certificate')

    # Targeted arithmetic controls: the proof must depend on the physical
    # 3/2 entry and on the determinant signs used in the certificate.
    changed_trace = A3[0][0]-q33
    need(changed_trace+7*g22-2*gI != -4, 'mutation: changed mask28 diagonal is detected')
    need(trace_defect+7*g22+2*gI != -4, 'mutation: wrong certificate sign is detected')
    result = {
        'status':'PASS_ALL_PROJECTOR_ALTERNATE_FRAME_OBSTRUCTION',
        'groups':groups, 'axes':axes, 'physical_tariffs':caps,
        'scope':'Every rational split in the fixed alternate H0,K0 frame obeying the mandatory flags is excluded by masks34,22,28. Other complements and other anchor matrices remain outside the claim; no decoder bound changes.',
        'input_sha256':PINS, 'anchor_rectangles_checked':anchor_caps_checked, 'flag_premises':premises, 'flag_pairing':dump(mm(a,b)),
        'coordinate_change':dump(D), 'anchor_source_frames':dump(L), 'anchor_reader_frames':dump(R),
        'mask28_Z':dump(Z), 'mask28_W':dump(W), 'mask22_S4':dump(S4),
        'projector_form':'P=diag(1,Q,0), Q^2=Q, rank(Q)=2',
        'rank_one_parameterization':'B=E00+Q[:3,:3]diag(1/2,1,1)=u v^t',
        'g22':str(g22), 'gI':str(gI), 'trace_defect':str(trace_defect),
        'certificate':'trace((W-I)Q) + 7 det(S4) - 2 det(I3-Q[:3,:3]) = -4',
        'coefficient_samples':0, 'geometry_samples':0, 'mutation_controls_rejected':2,
    }
    import sys
    receipt = HERE/'RESULT.json'
    if sys.argv[1:] == ['--write-receipt']:
        receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(not sys.argv[1:], 'only --write-receipt is accepted')
        need(json.loads(receipt.read_text(encoding='utf-8')) == result, 'committed primary receipt matches recomputation')
    print(json.dumps({k:result[k] for k in ('status','physical_tariffs','certificate','mutation_controls_rejected','scope')},indent=2))

if __name__ == '__main__': main()
