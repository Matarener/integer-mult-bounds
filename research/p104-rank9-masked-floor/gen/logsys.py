"""Hand route for T1, multiplicative relations (no search).
For orthogonal t, s in Z and a frame F inside Z with T_F(t) cap T_F(s) = {a, b}, the expansion over F gives
  M_ta M_as / M_aa = - M_tb M_bs / M_bb   and (transposed)   M_sa M_at / M_aa = - M_sb M_bt / M_bb,
so multiplying:   N{t,a} N{s,a} = N{t,b} N{s,b}      (exact, N{t,x} = M_tx M_xt / (M_tt M_xx)).
(1) zeros: w{t,x} = [N{t,x} = 0];  (w_ta or w_sa) <-> (w_tb or w_sb);  frame sums: the <= 4 terms of t on F are not all 0.
    SAT goal: some w true.  UNSAT => no extra zero on Z x Z.
(2) no zeros: l = log N satisfies l_ta + l_sa - l_tb - l_sb = 0; nullity 1 (constants) => N constant => N = 1/4 by the
    frame sums.  Rank mod p.   usage: logsys.py rep ..."""
import json, sys, time, numpy as np
from pysat.solvers import Cadical153
from p104lib import *
T0 = time.time()
def log(*a): print('[%7.1fs]' % (time.time() - T0), *a, flush=True)
pr = 2**31 - 1
def rankp(M):
    M = M % pr; r = 0; rows, cols = M.shape
    for c in range(cols):
        nzr = np.nonzero(M[r:, c])[0]
        if len(nzr) == 0: continue
        piv = r + nzr[0]; M[[r, piv]] = M[[piv, r]]
        inv = pow(int(M[r, c]), pr - 2, pr); M[r] = (M[r] * inv) % pr
        nz = np.nonzero(M[:, c])[0]; nz = nz[nz != r]
        if len(nz): M[nz] = (M[nz] - (M[nz, c][:, None] * M[r][None, :]) % pr) % pr
        r += 1
        if r == rows: break
    return r
FR = [tuple(IDX[q] for q in f) for f in frames()]
reps = [r for r in json.load(open('orbitsW.json')) if r['frame']]
def P(a, b): return (min(a, b), max(a, b))
for k in map(int, sys.argv[1:]):
    m = int(reps[k]['mask']); Z = [i for i in range(N) if m >> i & 1]; Zs = set(Z)
    FZ = [f for f in FR if all(i in Zs for i in f)]
    pairs = [(a, b) for a in Z for b in Z if a < b and not ORTH[a][b]]; pos = {p: j for j, p in enumerate(pairs)}
    rel = set(); sums = []
    for F in FZ:
        Fs = set(F)
        for t in Z:
            if t in Fs: continue
            Tt = [f for f in F if not ORTH[t][f]]
            sums.append(tuple(pos[P(t, f)] for f in Tt))
            for s in Z:
                if s <= t or s in Fs or not ORTH[t][s]: continue
                Ts = [f for f in F if not ORTH[s][f]]
                com = [f for f in Tt if f in Ts]
                if len(com) == 2:
                    a, b = com
                    rel.add((pos[P(t, a)], pos[P(s, a)], pos[P(t, b)], pos[P(s, b)]))
    log('rep', k, '|Z|', len(Z), 'frames', len(FZ), 'unknowns', len(pairs), 'relations', len(rel), 'sums', len(set(sums)))
    # (2) log-linear system
    A = np.zeros((len(rel), len(pairs)), dtype=np.int64)
    for i, (ta, sa, tb, sb) in enumerate(rel):
        A[i, ta] += 1; A[i, sa] += 1; A[i, tb] -= 1; A[i, sb] -= 1
    rk = rankp(A.copy()); log('  (2) log system rank', rk, 'nullity', len(pairs) - rk, '(1 = only constants)')
    # (1) zeros
    cls = []
    for (ta, sa, tb, sb) in rel:
        x, y, u, v = ta + 1, sa + 1, tb + 1, sb + 1
        # (x or y) -> (u or v) and back
        cls += [[-x, u, v], [-y, u, v], [-u, x, y], [-v, x, y]]
    for s in set(sums): cls.append([-(j + 1) for j in s])
    cls.append([j + 1 for j in range(len(pairs))])
    with Cadical153(bootstrap_with=cls) as S:
        res = S.solve(); log('  (1) zero model with goal:', 'SAT' if res else 'UNSAT')
        if res:
            mod = [j for j in range(len(pairs)) if S.get_model()[j] > 0]; log('     zeros in model', len(mod))
log('DONE')
