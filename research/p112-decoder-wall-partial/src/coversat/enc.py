# COVERSAT encoder: exact-support cover model for C(T) with the interleaved (Ferrers) menu, as DIMACS CNF for kissat.
# Shard = (orbit, partition lam of the budget, optional cube = term-0 row-support set Rs (exact, given as bitmask)).
# Term k: S_k (8x8 0/1, exact support), Ferrers (no 2x2 crossing), rank_F2(B o S_k) <= lam_k, via B o S_k = U V with V a full-rank RREF (lam_k x 8; any rank-<=lam row space extends to one;
# U forced at pivots: U[:,i] = (B o S)[:,piv_i]; NOT exact rank: a rank-deficient M has extra slots with U col 0).  Cover: diagonal >= 1, masked off-diagonal != 1.  Redundant: F2 sum of B o S_k singular (if total < 8).
# Symmetry: G' = Aut(B) x {id, transpose}; S_0 <=lex g(S_0) for all g in G'; consecutive equal-size terms lex-sorted (S_k <=lex S_k+1).
# usage: enc.py orbit lam(e.g. 4,2,1) out.cnf [--nosing] [--cube R0]   (R0 = exact set of rows t with S_0[t] != 0)
import sys, itertools
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import orbit, brows, aut
class CNF:
    def __init__(s): s.n = 0; s.cl = []
    def v(s): s.n += 1; return s.n
    def add(s, c): s.cl.append(c)
    def AND(s, a, b):
        z = s.v(); s.add([-z, a]); s.add([-z, b]); s.add([z, -a, -b]); return z
    def xor_eq(s, lits, rhs):
        """XOR(lits) == rhs (rhs a literal, or True/False).  chunks of <= 4 via aux."""
        lits = list(lits)
        if rhs is True: lits = lits[:]; par = 1
        elif rhs is False: par = 0
        else: lits = lits + [rhs]; par = 0   # XOR(lits) ^ rhs == 0
        while len(lits) > 5:
            a = lits[:4]; z = s.v(); s._xor(a + [z], 0); lits = [z] + lits[4:]
        s._xor(lits, par)
    def _xor(s, lits, par):
        if not lits:
            if par: s.add([])
            return
        for signs in itertools.product([0, 1], repeat=len(lits)):
            if sum(signs) % 2 != par:   # forbid assignments with wrong parity: assignment x_i = signs_i
                s.add([(-l if x else l) for l, x in zip(lits, signs)])
    def lex_le(s, a, b):
        """a <=lex b (lists of literals or None-free); positions with identical literal skipped."""
        e = None   # e = 'prefix equal so far' literal; None means True
        pairs = [(x, y) for x, y in zip(a, b) if x != y]
        for idx, (x, y) in enumerate(pairs):
            pre = [] if e is None else [-e]
            s.add(pre + [-x, y])
            if idx == len(pairs) - 1: break
            e2 = s.v(); s.add(pre + [x, y, e2]); s.add(pre + [-x, -y, e2]); e = e2
def build(o, lam, sing=True, cube=None, cover=True, sym=True, ferrers=True):
    T, B = orbit(o); B = [[int(B[t][s]) for s in range(8)] for t in range(8)]; m = len(lam); c = CNF()
    S = [[[c.v() for s in range(8)] for t in range(8)] for k in range(m)]
    for k in range(m):
        Sk = S[k]
        for t, t2 in itertools.combinations(range(8) if ferrers else [], 2):          # Ferrers: rows nested
            for s, s2 in itertools.permutations(range(8), 2):
                c.add([-Sk[t][s], Sk[t][s2], Sk[t2][s], -Sk[t2][s2]])
        r = lam[k]
        V = [[c.v() for s in range(8)] for i in range(r)]; U = [[c.v() for i in range(r)] for t in range(8)]
        P = [[c.v() for s in range(8)] for i in range(r)]
        for i in range(r):
            for s in range(8):   # P[i][s] <-> V[i][s] & all earlier zero
                c.add([-P[i][s], V[i][s]])
                for s0 in range(s): c.add([-P[i][s], -V[i][s0]])
                c.add([P[i][s], -V[i][s]] + [V[i][s0] for s0 in range(s)])
            c.add([P[i][s] for s in range(8)])                       # row nonzero (exact rank)
            for s in range(8):
                for j in range(r):
                    if j != i: c.add([-P[i][s], -V[j][s]])           # pivot column clean
                if i + 1 < r:
                    for s2 in range(s + 1): c.add([-P[i][s], -P[i + 1][s2]])   # increasing pivots
                for t in range(8):                                   # U[t][i] = (B o S)[t][piv_i]
                    if B[t][s]: c.add([-P[i][s], -U[t][i], Sk[t][s]]); c.add([-P[i][s], U[t][i], -Sk[t][s]])
                    else: c.add([-P[i][s], -U[t][i]])
        for t in range(8):
            for s in range(8):
                prods = [c.AND(U[t][i], V[i][s]) for i in range(r)]
                c.xor_eq(prods, Sk[t][s] if B[t][s] else False)
    if cover:
     for t in range(8): c.add([S[k][t][t] for k in range(m)])
    for t in range(8 if cover else 0):
        for s in range(8):
            if t != s and B[t][s]:
                for k in range(m): c.add([-S[k][t][s]] + [S[k2][t][s] for k2 in range(m) if k2 != k])
    if sing and cover and sum(lam) < 8:   # F2 sum of the B o S_k has rank <= sum lam < 8: some x != 0 with M x = 0
        x = [c.v() for s in range(8)]; c.add(x)
        for t in range(8):
            terms = []
            for s in range(8):
                if not B[t][s]: continue
                for k in range(m): terms.append(c.AND(S[k][t][s], x[s]))
            c.xor_eq(terms, False)
    G = aut(B) if sym else []; flat = lambda Sk: [Sk[t][s] for t in range(8) for s in range(8)]
    for g in G:
        for tr in (0, 1):
            img = [[None] * 8 for _ in range(8)]   # img = g(S_0) [optionally transposed]
            for t in range(8):
                for s in range(8):
                    a, b = (t, s) if not tr else (s, t)
                    img[g[a]][g[b]] = S[0][t][s]
            if all(img[t][s] == S[0][t][s] for t in range(8) for s in range(8)): continue
            c.lex_le(flat(S[0]), flat(img))
    for k in range(1, m - 1):
        if sym and lam[k] == lam[k + 1]: c.lex_le(flat(S[k]), flat(S[k + 1]))
    if sym and m > 1 and lam[0] == lam[1]: c.lex_le(flat(S[0]), flat(S[1]))
    if cube is not None:
        for t in range(8):
            if cube >> t & 1: c.add([S[0][t][s] for s in range(8)])
            else:
                for s in range(8): c.add([-S[0][t][s]])
    return c, S, B
def write(c, path, comment=''):
    with open(path, 'w') as f:
        f.write(f'c {comment}\np cnf {c.n} {len(c.cl)}\n')
        for cl in c.cl: f.write(' '.join(map(str, cl)) + ' 0\n')
if __name__ == '__main__':
    o = int(sys.argv[1]); lam = [int(x) for x in sys.argv[2].split(',')]; out = sys.argv[3]
    sing = '--nosing' not in sys.argv; cube = int(sys.argv[sys.argv.index('--cube') + 1]) if '--cube' in sys.argv else None
    sym = '--nosym' not in sys.argv; fer = '--noferrers' not in sys.argv
    c, S, B = build(o, lam, sing, cube, sym=sym, ferrers=fer)
    write(c, out, f'COVERSAT orbit {o} lam {lam} sing {sing} cube {cube} sym {sym} ferrers {fer}; S vars k,t,s -> 1 + 64k + 8t + s for k < {len(lam)}')
    print(out, c.n, len(c.cl))
