# COVERSAT stage 2: cover model + exact Lemma-B rank cuts over Q, via finite-field rank witnesses.
# Cut (X,Y) (PROVED valid on exact supports): sum_k D(q_k) A_k D(p_k) = I_8 with A_k = B o S_k (free cells are 0 in B o S), so
#   sum_k rank_Q(A_k[X,Y]) >= rank I[X,Y] = |X & Y|.
# (UPDATED: levels >= 6 now witnessed exactly with F5/F7; the free-claim relaxation below is superseded.)
# Witness of rank_Q(A[X,Y]) >= i: rows r_1<..<r_i in X and R (cols in Y) over F_p with A[r,:] R = I_i mod p  (=> rank_Fp >= i => rank_Q >= i).
# COMPLETENESS (so no real decoder is cut off): for a 0/1 matrix with rank_Q >= i, i <= 5, some nonzero i-minor m has |m| <= maxdet01(i) <= 5,
# so 6 does not divide m: rank_F2 >= i or rank_F3 >= i.  Levels i >= 6 are CLAIMED freely once level 5 is witnessed (a relaxation: rank_Q >= 6
# implies rank_Q >= 5).  So each term gets u_1 >= u_2 >= ... (unary claimed level), u_i -> (F2 or F3 witness of level i) for i <= 5,
# u_i -> u_5 for i >= 6, and sum_{k,i} u_{k,i} >= |X & Y| (sequential counter).
# usage: cutenc.py orbit lam out.cnf cutsfile    (cutsfile: lines "X Y")
import sys, itertools
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enc import build, write
def bits(M): return [t for t in range(8) if M >> t & 1]
def witness(c, a, X, Y, L, p):
    """a[t][s]: literal (or None = constant 0) for A entries.  returns alpha[0..L-1] literals: alpha_i => level i+1 witnessed over F_p."""
    Xs, Ys = bits(X), bits(Y); al = [c.v() for i in range(L)]
    for i in range(L - 1): c.add([-al[i + 1], al[i]])
    sel = [{t: c.v() for t in Xs} for i in range(L)]
    for i in range(L):
        c.add([-al[i]] + list(sel[i].values()))
        for t in Xs: c.add([-sel[i][t], al[i]])
        for t, t2 in itertools.combinations(Xs, 2): c.add([-sel[i][t], -sel[i][t2]])
        if i + 1 < L:
            for t in Xs:
                for t2 in Xs:
                    if t2 <= t: c.add([-sel[i][t], -sel[i + 1][t2]])
    As = [{} for i in range(L)]   # As[i][s] <-> OR_t sel[i][t] & a[t][s]
    for i in range(L):
        for s in Ys:
            zs = [c.AND(sel[i][t], a[t][s]) for t in Xs if a[t][s] is not None]
            x = c.v(); As[i][s] = x
            for z in zs: c.add([-z, x])
            c.add([-x] + zs)
    if p == 2:
        R = [{s: c.v() for s in Ys} for j in range(L)]
        for i in range(L):
            for j in range(L):
                prods = [c.AND(As[i][s], R[j][s]) for s in Ys]
                g = [-al[i], -al[j]]
                # guarded XOR(prods) == delta: encode via aux z = XOR(prods); then guard z
                z = c.v(); c.xor_eq(prods, z)
                c.add(g + ([z] if i == j else [-z]))
    else:
        R = [{s: [c.v() for _ in range(p - 1)] for s in Ys} for j in range(L)]   # R[j][s][b-1] <-> value b (b=1..p-1); all false = 0
        for j in range(L):
            for s in Ys:
                for b1, b2 in itertools.combinations(range(p - 1), 2): c.add([-R[j][s][b1], -R[j][s][b2]])
        for i in range(L):
            for j in range(L):
                g = [-al[i], -al[j]]
                st = None   # None = state 0 (constant)
                for s in Ys:
                    new = [c.v() for _ in range(p)]
                    for a0 in range(p):
                        if st is None and a0 != 0: continue
                        pre = [] if st is None else [-st[a0]]
                        c.add(g + pre + [As[i][s], new[a0]])                         # not selected: keep
                        c.add(g + pre + [-As[i][s]] + R[j][s] + [new[a0]])          # R = 0: keep
                        for b in range(1, p): c.add(g + pre + [-As[i][s], -R[j][s][b - 1], new[(a0 + b) % p]])
                    st = new
                want = 1 if i == j else 0
                if st is None:
                    if want: c.add(g)
                else:
                    for b in range(p):
                        if b != want: c.add(g + [-st[b]])
    return al
def add_cut(c, S, B, lam, X, Y):
    # EXACT levels: rank_Q(A) = max_{p in {2,3,5,7}} rank_Fp(A) for 0/1 matrices up to 8x8 (a nonzero i-minor has |m| <= maxdet01(8) = 56 < 210,
    # so some p in {2,3,5,7} does not divide it).  F5/F7 only needed for levels >= 6 (i <= 5: |m| <= 5, 6 does not divide m).
    need = bin(X & Y).count('1'); mx = min(bin(X).count('1'), bin(Y).count('1')); us = []
    for k in range(len(lam)):
        a = [[(S[k][t][s] if (B[t][s] and Y >> s & 1 and X >> t & 1) else None) for s in range(8)] for t in range(8)]
        ws = [witness(c, a, X, Y, mx, p) for p in ((2, 3, 5, 7) if mx >= 6 else (2, 3))]
        u = [c.v() for i in range(mx)]
        for i in range(mx - 1): c.add([-u[i + 1], u[i]])
        for i in range(mx): c.add([-u[i]] + [w[i] for w in ws])
        us += u
    # at least `need` of us true: r[j][q] => among first j at least q true
    N = len(us); r = [[None] * (need + 1) for _ in range(N + 1)]
    for j in range(N + 1):
        for q in range(need + 1):
            if q == 0: continue
            if q > j: r[j][q] = False; continue
            v = c.v(); r[j][q] = v
            prev_q = r[j - 1][q]; prev_q1 = r[j - 1][q - 1] if q - 1 > 0 else True
            # v -> prev_q or (lit_j and prev_q1)
            A = [] if prev_q is False else [prev_q]
            c.add([-v] + A + [us[j - 1]])
            if prev_q1 is not True: c.add([-v] + A + [prev_q1])
    if need > N: c.add([])
    else: c.add([r[N][need]])
def build_cuts(o, lam, cuts, sing=True, ratio=True):
    c, S, B = build(o, lam, sing)
    if ratio: ratio_lemma(c, S, B, len(lam))
    for X, Y in cuts: add_cut(c, S, B, lam, X, Y)
    return c, S, B
if __name__ == '__main__':
    o = int(sys.argv[1]); lam = [int(x) for x in sys.argv[2].split(',')]; out = sys.argv[3]
    cuts = [tuple(map(int, l.split())) for l in open(sys.argv[4]) if l.strip()]
    c, S, B = build_cuts(o, lam, cuts)
    write(c, out, f'COVERSAT-CUT orbit {o} lam {lam} cuts {len(cuts)}; S vars k,t,s -> 1 + 64k + 8t + s')
    print(out, c.n, len(c.cl))
# ---- RATIO LEMMA (PROVED; see NOTES).  For lines a != b (rows; columns by transpose) and terms k,l covering cells in both lines, the ratio
# rho_k = x_k(a)/x_k(b) is defined (exact supports: nonzero).  Seed: a position c with (a,c),(b,c) both masked, both targets 0, both covered by
# exactly {k,l} gives rho_k = rho_l (x_k(a)y_k(c) = -x_l(a)y_l(c), same at b, divide).  Equality is transitive.  Contradiction: a position d with
# (a,d),(b,d) masked, exactly one of them diagonal, the same cover set K at both cells and all of K pairwise ratio-equal: row a = rho * row b on
# column d gives delta_ad = rho delta_bd with rho != 0 and exactly one delta = 1.  Real decoders satisfy the clauses with E := [rho equal].
def ratio_lemma(c, S, B, m):
    for tr in (0, 1):
        cell = (lambda k, a, s: S[k][a][s]) if not tr else (lambda k, a, s: S[k][s][a])
        msk = (lambda a, s: B[a][s]) if not tr else (lambda a, s: B[s][a])
        for a, b in itertools.combinations(range(8), 2):
            E = {}
            for k, l in itertools.combinations(range(m), 2): E[k, l] = E[l, k] = c.v()
            for cc in range(8):
                if cc in (a, b) or not (msk(a, cc) and msk(b, cc)): continue
                # GENERALISED seed: same cover set K at (a,cc),(b,cc) (targets 0); j,k in K; all pairs of K minus j ratio-equal => E[j,k]
                # (common ratio rho of K-j; the two zero sums give x_j(a) y_j = rho x_j(b) y_j, so rho_j = rho = rho_k).  |K| = 2: plain seed.
                ne = []
                for j in range(m):
                    v = c.v(); c.add([-v, cell(j, a, cc), cell(j, b, cc)]); c.add([-v, -cell(j, a, cc), -cell(j, b, cc)]); ne.append(v)
                gg = {}
                for i, i2 in itertools.combinations(range(m), 2):
                    v = c.v(); c.add([-v, cell(i, a, cc)]); c.add([-v, cell(i2, a, cc)]); c.add([-v, -E[i, i2]]); gg[i, i2] = v
                for j, k in itertools.permutations(range(m), 2):
                    if j > k and False: continue
                    c.add(ne + [-cell(j, a, cc), -cell(k, a, cc)] + [gg[p] for p in gg if j not in p] + [E[j, k]])
            for k, l, n in itertools.permutations(range(m), 3):
                if k < n: c.add([-E[k, l], -E[l, n], E[k, n]])
            for d in (a, b):
                if not (msk(a, d) and msk(b, d)): continue
                cl = []
                for j in range(m):
                    ne = c.v(); c.add([-ne, cell(j, a, d), cell(j, b, d)]); c.add([-ne, -cell(j, a, d), -cell(j, b, d)]); cl.append(ne)
                for k, l in itertools.combinations(range(m), 2):
                    g = c.v(); c.add([-g, cell(k, a, d)]); c.add([-g, cell(l, a, d)]); c.add([-g, -E[k, l]]); cl.append(g)
                c.add(cl)
