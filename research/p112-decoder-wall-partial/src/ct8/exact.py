# Exact tools (independent of float SVD): rank over Q of rational matrices via rank mod p = 2^61-1 after clearing
# denominators; rigorous because p exceeds the Hadamard bound of every minor (asserted).  F2 rank, maximal rects, CP-SAT check.
import itertools, math
from fractions import Fraction as Fr
P61 = (1 << 61) - 1
def qrank(M):
    """M: list of rows of Fractions/ints. exact rank over Q (mod-p elimination, Hadamard-certified)."""
    rows = [list(r) for r in M if any(x != 0 for x in r)]
    if not rows: return 0
    ints = []
    for r in rows:
        d = 1
        for x in r: d = d * Fr(x).denominator // math.gcd(d, Fr(x).denominator)
        ints.append([int(Fr(x) * d) for x in r])
    n = min(len(ints), len(ints[0])); mx = max(abs(x) for r in ints for x in r)
    rn = [math.sqrt(sum(x * x for x in r)) for r in ints]
    assert math.prod(sorted(rn)[-n:]) < P61 / 4, 'Hadamard bound too large'
    A = [[x % P61 for x in r] for r in ints]; rk = 0; cols = len(A[0])
    for c in range(cols):
        pr = next((i for i in range(rk, len(A)) if A[i][c]), None)
        if pr is None: continue
        A[rk], A[pr] = A[pr], A[rk]; iv = pow(A[rk][c], P61 - 2, P61)
        for i in range(len(A)):
            if i != rk and A[i][c]:
                f = A[i][c] * iv % P61; A[i] = [(x - f * y) % P61 for x, y in zip(A[i], A[rk])]
        rk += 1
    return rk
def f2rank_rows(rows):
    basis = []
    for v in rows:
        for b in basis: v = min(v, v ^ b)
        if v: basis.append(v)
    return len(basis)
def f2cost(B, R, A):
    return f2rank_rows([sum(1 << j for j in range(8) if A >> j & 1 and B[i][j]) for i in range(8) if R >> i & 1])
def maxrects(B, budget=7):
    f2 = {}
    def c(R, A):
        k = (R, A)
        if k not in f2: f2[k] = f2cost(B, R, A)
        return f2[k]
    out = []
    for R in range(1, 256):
        for A in range(1, 256):
            cc = c(R, A)
            if cc == 0 or cc > budget: continue
            if all(not ((not R >> i & 1 and c(R | 1 << i, A) == cc) or (not A >> i & 1 and c(R, A | 1 << i) == cc)) for i in range(8)):
                out.append((R, A, cc))
    return out
def subrank(Bp, R, A):
    return qrank([[Bp[i][j] for j in range(8) if A >> j & 1] for i in range(8) if R >> i & 1])
def cpsat_infeasible(costs, rows, budget=7, tl=1200, workers=8):
    """rows: list of (coef list, rhs) meaning sum coef_i n_i >= rhs. returns solver status name."""
    from ortools.sat.python import cp_model
    m = cp_model.CpModel(); n = len(costs)
    x = [m.NewIntVar(0, budget, f'x{i}') for i in range(n)]
    m.Add(sum(c * xi for c, xi in zip(costs, x)) <= budget)
    for coef, rhs in rows: m.Add(sum(int(c) * xi for c, xi in zip(coef, x) if c) >= rhs)
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_workers = workers
    st = s.Solve(m)
    return s.StatusName(st), ([s.Value(v) for v in x] if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None)
