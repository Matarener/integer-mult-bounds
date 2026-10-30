"""F2 feasibility of a decoder whose totals are confined to given line sets: R_j <= X_j, A_j <= Y_j.
B = sum_j w_j u_j^T must have B_TT = 1 and B_TS = 0 for K-non-orthogonal T != S.  Returns SAT model or None."""
import sys, itertools
from pysat.formula import IDPool
from pysat.solvers import Solver
from lines import views
S = views()['Gauss']; NO = S.NO

def encode(pairs, extra_or=None):
    pool = IDPool(); cl = []
    W = {}; U = {}
    for j, (X, Y) in enumerate(pairs):
        for T in X: W[T, j] = pool.id(('w', T, j))
        for T in Y: U[T, j] = pool.id(('u', T, j))
    def AND(a, b):
        z = pool.id(('and', a, b)); cl.extend([[-z, a], [-z, b], [z, -a, -b]]); return z
    def XOR(a, b):
        z = pool.id(('xor', a, b)); cl.extend([[-z, a, b], [-z, -a, -b], [z, -a, b], [z, a, -b]]); return z
    for T in range(60):
        for S_ in range(60):
            if not (T == S_ or NO[T, S_]): continue
            terms = [AND(W[T, j], U[S_, j]) for j in range(len(pairs)) if (T, j) in W and (S_, j) in U]
            if not terms:
                if T == S_: return None, None, None, None
                continue
            acc = terms[0]
            for t in terms[1:]: acc = XOR(acc, t)
            cl.append([acc] if T == S_ else [-acc])
    return cl, pool, W, U

def solve(pairs, solver='cadical153'):
    cl, pool, W, U = encode(pairs)
    if cl is None: return False, None
    with Solver(name=solver, bootstrap_with=cl) as s:
        r = s.solve()
        if not r: return False, None
        mod = set(x for x in s.get_model() if x > 0)
    R = [sorted(T for T in X if W[T, j] in mod) for j, (X, Y) in enumerate(pairs)]
    A = [sorted(T for T in Y if U[T, j] in mod) for j, (X, Y) in enumerate(pairs)]
    return True, (R, A)

def check_decoder(R, A):
    import numpy as np
    B = np.zeros((60, 60), int)
    for r, a in zip(R, A):
        for T in r:
            for S_ in a: B[T, S_] ^= 1
    ok = all(B[T, T] == 1 for T in range(60)) and all(B[T, S_] == 0 for T in range(60) for S_ in range(60) if T != S_ and NO[T, S_])
    return ok

if __name__ == '__main__':
    # calibration: identity decoder (60 singleton totals) and the 21-dumbbell cover of S8
    ok, sol = solve([([T], [T]) for T in range(60)]); print('identity', ok, check_decoder(*sol))
    perp = lambda l: [T for T in range(60) if T != l and not NO[l, T]]
    D = [(0,13),(4,22),(5,50),(6,19),(6,28),(7,38),(8,19),(11,56),(12,17),(18,37),(18,58),(20,30),(21,33),(25,26),(35,55),(36,45),(37,47),(41,44),(42,51),(44,51),(48,53)]
    import time; t = time.time()
    ok, sol = solve([(perp(a), perp(b)) for a, b in D]); print('S8 dumbbell cover, fixed orientation:', ok, '%.1fs' % (time.time() - t))

def solve_opts(opts, solver='cadical153', assumptions=()):
    """opts[j] = list of (X, Y) alternatives for total j (one is selected)."""
    pool = IDPool(); cl = []
    W = {}; U = {}; SEL = {}
    for j, alts in enumerate(opts):
        sels = [pool.id(('s', j, k)) for k in range(len(alts))]
        cl.append(sels)
        for a in range(len(sels)):
            for b in range(a + 1, len(sels)): cl.append([-sels[a], -sels[b]])
        SEL[j] = sels
        allX = set().union(*[set(X) for X, Y in alts]); allY = set().union(*[set(Y) for X, Y in alts])
        for T in allX:
            W[T, j] = pool.id(('w', T, j)); cl.append([-W[T, j]] + [sels[k] for k, (X, Y) in enumerate(alts) if T in X])
        for T in allY:
            U[T, j] = pool.id(('u', T, j)); cl.append([-U[T, j]] + [sels[k] for k, (X, Y) in enumerate(alts) if T in Y])
    def AND(a, b):
        z = pool.id(('and', a, b)); cl.extend([[-z, a], [-z, b], [z, -a, -b]]); return z
    def XOR(a, b):
        z = pool.id(('xor', a, b)); cl.extend([[-z, a, b], [-z, -a, -b], [z, -a, b], [z, a, -b]]); return z
    for T in range(60):
        for S_ in range(60):
            if not (T == S_ or NO[T, S_]): continue
            terms = [AND(W[T, j], U[S_, j]) for j in range(len(opts)) if (T, j) in W and (S_, j) in U]
            if not terms:
                if T == S_: return False, None
                continue
            acc = terms[0]
            for t in terms[1:]: acc = XOR(acc, t)
            cl.append([acc] if T == S_ else [-acc])
    with Solver(name=solver, bootstrap_with=cl) as s:
        if not s.solve(): return False, None
        mod = set(x for x in s.get_model() if x > 0)
    R = [sorted(T for (T, jj), v in W.items() if jj == j and v in mod) for j in range(len(opts))]
    A = [sorted(T for (T, jj), v in U.items() if jj == j and v in mod) for j in range(len(opts))]
    return True, (R, A)
