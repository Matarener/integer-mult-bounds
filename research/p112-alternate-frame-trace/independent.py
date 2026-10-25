"""Independent exact audit of one alternate annihilator chart, no search.

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


def run():
    hashes = {'research/p112-alternate-frame-trace/FIXTURE.json': '13e1f33aa04e417968535d2b2fd4eb2b90672e117b95c0d449d3796563883578', 'research/p112-rational-decoder-gate/CANDIDATE.json': 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b', 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'}
    inputs = {p:read(p, sha) for p, sha in hashes.items()}
    anchor = inputs[next(iter(hashes))]['asymmetric_template_matrix']
    A = [list(map(F, row)) for row in anchor]
    flags = inputs['research/p112-alternate-frame-trace/FIXTURE.json']['saturated_rectangle_compatibility']
    ri = independent(A)
    ci = independent(tr([A[i] for i in ri]))
    U = part(A, range(12), ci)
    V = mm(inverse(part(A, ri, ci)), [A[i] for i in ri])
    need(mm(U, V) == A and rank(A) == 8, 'independent anchor factorization')
    axes = [6,1,11]
    H = [U[i]+[F(0)] for i in axes]
    K = tr(part(V, range(8), axes)+[[F(0)]*3])
    need(mm(H, tr(K)) == eye(3), 'chosen alternate annihilators')
    X = tr(kernel(H, 9))
    Y = inverse([row+col for row, col in zip(X, tr(K))])[:6]
    af, bf = [], []
    for i in range(2):
        eq = [list(map(F, row)) for row in flags[0]['new_group_spaces'][i]['equations']]
        rows = mm(eq, U)
        need(rank(rows) == 1, 'source flag dimension')
        af.append(next(row+[F(0)] for row in rows if any(row)))
        eq = [list(map(F, row)) for row in flags[1]['new_group_spaces'][i]['equations']]
        rows = mm(eq, tr(V))
        need(rank(rows) == 1, 'reader flag dimension')
        bf.append(next(row+[F(0)] for row in rows if any(row)))
    aa, bb = mm(af, X), mm(Y, tr(bf))
    need(mm(aa, bb) == [[-2,0],[0,1]], 'two nondegenerate flag pairings')
    b3, b4 = [row[0] for row in bb], [row[1] for row in bb]
    D = tr([b4]+kernel(aa, 6)+[b3])
    need(rank(D) == 6 and mm(aa, D) == [[0,0,0,0,0,-2],[1,0,0,0,0,0]], 'complete flag-normal form chart')
    L = mm(mm([row+[F(0)] for row in U], X), D)
    R = mm(mm(inverse(D), Y), V+[[F(0)]*12])
    LB, RB = L[3:6], part(R, range(6), range(3,6))
    Q = [[var(4*i+j) for j in range(4)] for i in range(4)]
    P = lift([[int(i == j == 0) for j in range(6)] for i in range(6)])
    for i in range(4):
        for j in range(4):
            P[i+1][j+1] = Q[i][j]
    T = pm(pm(lift(LB), P), lift(RB))
    expected_T = [[mul(Q[i][j], const(F(1,2) if j == 0 else 1)) for j in range(3)] for i in range(3)]
    need(T == expected_T and mm(LB,RB) == [[int(i == j and i > 0) for j in range(3)] for i in range(3)], 'cap34 residual E00+T')
    BC = list(range(3,9))
    S = subtract(lift(part(A, BC, BC)), pm(pm(lift([L[i] for i in BC]), P), lift(part(R, range(6), BC))))
    for i in range(3,6):
        S[i] = [add(x,neg(y)) for x,y in zip(S[i],S[i-3])]
    for row in S:
        for j in range(3,6):
            row[j] = add(row[j],neg(row[j-3]))
    need(all(not S[i][j] for i in range(6) for j in range(6) if i >= 4 or j >= 4), 'cap22 exact two zero directions')
    S4 = [row[:4] for row in S[:4]]
    IT = subtract(lift(eye(3)), T)
    expected_S4 = [row+[T[i][0]] for i,row in enumerate(IT)]+[T[0]+[neg(T[0][0])]]
    need(S4 == expected_S4, 'cap22 Schur form for all sixteen independent Q entries')
    need(determinant(S4) == add(determinant(IT), neg(determinant([row[1:] for row in IT[1:]]))), 'cap22 determinant identity without inverses')
    # Every rank<=1 residual is x*y^t, including its zero boundary.
    residual = [[mul(var(i), var(3+j)) for j in range(3)] for i in range(3)]
    E = lift([[int(i == j == 0) for j in range(3)] for i in range(3)])
    t = subtract(residual, E)
    it = subtract(lift(eye(3)), t)
    delta = add(determinant(it), neg(determinant([row[1:] for row in it[1:]])))
    trace_residual = add(add(residual[0][0], residual[1][1]), residual[2][2])
    need(delta == add(const(1), neg(trace_residual)), 'rank-one boundary gives trace residual=1')
    qtop = [[mul(t[i][j], const(2 if j == 0 else 1)) for j in range(3)] for i in range(3)]
    expected_det = const(3)
    for i, coefficient in enumerate((2,3,3)):
        expected_det = add(expected_det, neg(mul(const(coefficient), residual[i][i])))
    need(determinant(subtract(lift(eye(3)), qtop)) == expected_det, 'idempotent complement minor identity')
    CD = list(range(6,12))
    need(part(A, CD, CD) == eye(6), 'cap28 fixed anchor block I6')
    Z = mm(part(R, range(6), CD), [L[i] for i in CD])
    active = part(Z, range(5), range(5))
    need(active == [[(F(3,2),F(1),F(1),F(0))[i-1] if i == j and i else F(0)
                     for j in range(5)] for i in range(5)], 'cap28 active Z=diag(0,3/2,1,1,0)')
    W = part(Z, range(1,5), range(1,5))
    # Variables r00, r11+r22, q00, q33. No selected coefficient values
    # enter these consequences of the determinant identities and trace(Q)=2.
    equations = [[1,1,0,0], [2,3,0,0], [-2,0,1,0], [0,1,1,1]]
    rhs = [[F(1)], [F(3)], [F(-2)], [F(2)]]
    forced = mm(inverse([list(map(F,row)) for row in equations]), rhs)
    need(forced == [[0],[1],[-2],[3]], 'all-Q scalar consequences')
    need(F(1,2)*forced[2][0]-forced[3][0] == -4, 'forced trace cannot be zero')
    fixture = [list(map(F,row)) for row in [[-2,0,0,1],[0,1,0,0],[0,0,0,0],[-6,0,0,3]]]
    need(mm(fixture,fixture) == fixture and rank(fixture) == 2, 'known two-cap positive fixture')
    trace_defect = F(1,2)*fixture[0][0]-fixture[3][3]
    need(trace_defect == -4, 'exact nonzero trace contradiction')
    fixture_T = [[fixture[i][j]*(F(1,2) if j == 0 else 1) for j in range(3)] for i in range(3)]
    fixture_B = [[fixture_T[i][j]+int(i == j == 0) for j in range(3)] for i in range(3)]
    need(rank(fixture_B) <= 1, 'positive fixture satisfies literal cap34')
    fixture_S4 = [[F(i == j)-fixture_T[i][j] for j in range(3)]+[fixture_T[i][0]] for i in range(3)]+[fixture_T[0]+[-fixture_T[0][0]]]
    need(rank(fixture_S4) <= 3, 'positive fixture satisfies literal cap22')
    need(mm(mm(fixture,W),fixture) != fixture, 'omitting cap28 admits prior two-cap fixture')
    need(rank(subtract_numeric(eye(4),fixture)) == 2, 'fixture complement rank')
    candidate = inputs['research/p112-rational-decoder-gate/CANDIDATE.json']
    data = inputs['research/adaptive-kernel-demotion/inputs/DATA-PHASES.json']
    labels = {r['port']:r['q'] for r in data['recipes']}
    groups = [1,2,27,28,3,4]
    caps = {}
    for mask in (22,28,34):
        q = [labels[p] for i,g in enumerate(groups) if mask >> i & 1 for p in candidate['groups'][g]]
        caps[mask] = binary_rank([[(x&y).bit_count()%2 for y in q] for x in q])
    need(caps == {22:6,28:7,34:4}, 'authenticated three physical caps')
    return {'status':'PASS_INDEPENDENT_ALL_Q_ALTERNATE_CHART_OBSTRUCTION',
            'input_sha256':hashes, 'axes':axes, 'physical_caps':caps,
            'symbolic_variables':16, 'coefficient_samples':0,
            'cap28_W':[[str(x) for x in row] for row in W],
            'forced_Q00':-2,'forced_Q33':3,'required_trace':0,'forced_trace':-4,
            'degenerate_rank_one_residuals_included':True,
            'scope':'Selected [6,1,11] annihilator chart only; all rational rank-two idempotents Q and all flag-compatible splits. Other H/K choices and the general fixed-anchor problem remain open.'}


def subtract_numeric(A,B):
    return [[x-y for x,y in zip(ar,br)] for ar,br in zip(A,B)]


if __name__ == '__main__':
    import sys
    result = run()
    receipt = HERE/'INDEPENDENT-RESULT.json'
    if sys.argv[1:] == ['--write-receipt']:
        receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(not sys.argv[1:], 'only --write-receipt is accepted')
        need(json.loads(receipt.read_text(encoding='utf-8')) == json.loads(json.dumps(result)), 'committed independent receipt matches recomputation')
    print(result['status'])
