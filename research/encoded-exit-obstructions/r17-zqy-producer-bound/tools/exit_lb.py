"""R17: lower bound on the number of paid jobs in ANY producer of b = Z Q Y (and of the whole #5415 exit)
from post-return data.  Uses the repository's exact Clifford evaluator (tableau + absolute phase).

Potential (see ../notes/README.md, Lemma 2): track every field as a formal sum over (operator, input
variable); quotient each operator x by right monomial cosets x*Mon (key = x applied to the Z-Lagrangian).
Free operations (monomials, scalar ADD/SCALE/COPY/CLEAR) fix the base class Mon and permute the others;
a paid job (ANY invertible operator, any rank) adds at most one new vector to
    S = span{ value at a non-base class : over all fields ever computed }.
So #paid jobs >= dim(S_target) - dim(S_target ∩ S_0); S_0 = 0 when every available field is a base
variable (true for X, Y, H, helpers, owned zeros at the FULL return in coordinates xi=X, eta=Y, zeta=H).
"""
import gzip, json, sys, importlib.util
from fractions import Fraction as F
from pathlib import Path
from collections import defaultdict

ROOT = Path.home() / 'imb-r17'
cp = ROOT / 'research/coded-native-caller/clifford_exact.py'
spec = importlib.util.spec_from_file_location('ce', cp); ce = importlib.util.module_from_spec(spec)
sys.modules['ce'] = ce; spec.loader.exec_module(ce)
normal = json.loads((ROOT / 'research/coded-native-caller/NORMALIZERS.json').read_text())
prov = json.loads((ROOT / 'research/native-rank8-helper-provider/PROVIDER.json').read_text())
M = normal['mode_columns']                      # 8 x 112, entries in {-1,0,1}
n = 9

def literal(word):
    op = ce.ident(n)
    for e in word:
        if e[0] == 'P': part = ce.perm(n, tuple(e[1]))
        elif e[0] == 'D': part = ce.diag(n, tuple(e[1]), tuple(e[2]))
        elif e[0] == 'X': part = ce.xgate(n, e[1])
        elif e[0] == 'phase': part = ce.Op(n, ce.identity(n), [('phase', e[1])])
        else: raise ValueError(e)
        op = op.then(part)
    return op

def after(*ops):
    """Operator product in the rightmost-first convention: after(A, B, C) = A B C (C applied first)."""
    out = ce.ident(n)
    for o in reversed(ops): out = out.then(o)
    return out

def rank(op): return ce.rank([x for x, _, _ in op.tab[n:]])

def echelon(vecs):
    piv = {}
    for v in vecs:
        while v:
            b = v.bit_length() - 1
            if b not in piv: piv[b] = v; break
            v ^= piv[b]
    # fully reduce for a canonical basis
    keys = sorted(piv, reverse=True)
    for i, b in enumerate(keys):
        for c in keys[:i]:
            if piv[c] >> b & 1: piv[c] ^= piv[b]
    return tuple(sorted(piv.values()))

def cls(op):
    """Right monomial coset x*Mon  <->  the Lagrangian x(L_Z) (signs/phases forgotten)."""
    return echelon([x | (z << n) for x, z, _ in op.tab[n:]])

BASE = cls(ce.ident(n))

def qrank(rows):
    """Exact rank over Q of a list of dict-vectors."""
    rows = [dict(r) for r in rows if any(r.values())]
    r = 0; cols = sorted({c for row in rows for c in row})
    for c in cols:
        p = next((i for i in range(r, len(rows)) if rows[i].get(c, 0)), None)
        if p is None: continue
        rows[r], rows[p] = rows[p], rows[r]
        pv = rows[r][c]
        for i in range(len(rows)):
            if i != r and rows[i].get(c, 0):
                f = rows[i][c] / pv
                for k, v in rows[r].items(): rows[i][k] = rows[i].get(k, 0) - f * v
        r += 1
    return r

def s_target(outputs):
    """outputs: list of formal sums [(operator, variable, coefficient)]. Returns (dim S_target, #classes)."""
    vals = []
    ncls = 0
    for terms in outputs:
        per = defaultdict(lambda: defaultdict(F))
        for op, var, c in terms:
            k = cls(op)
            if k != BASE: per[k][var] += c
        ncls += len(per)
        vals += [dict(v) for v in per.values()]
    return qrank(vals), ncls

def main():
    global R, Dop, Q, Kp, Km
    canonical = json.loads(gzip.decompress((ROOT / 'research/native-center-free-code/SOURCE-WORD.json.gz').read_bytes()))['canonical']
    R = ce.canonical_frame(n, canonical['frames'][1])
    Dop = ce.fourier(n, range(1, 9))
    Q = Dop.adjoint().then(R)
    assert ce.rank([x for x, _, _ in R.tab[n:]]) == 9 and rank(Dop) == 8 and rank(Q) == 1
    RR = Dop.then(Q); assert RR.tab == R.tab and RR.zero_state() == R.zero_state()   # R = Q D exactly (absolute phase)
    Kp = [literal(r['K_word']) for r in normal['ports']]
    Km = [None] * 8
    for rec in prov['mode_boundaries']: Km[rec['mode']] = literal(rec['input_K']['literal_word'])
    inv = lambda o: o.adjoint()
    assert all(rank(k) == 0 for k in Kp + Km), 'port/mode maps are monomial'
    assert all(any(M[k][j] for k in range(8)) for j in range(112)), 'every port is supported'

    report = {}
    # 1. b = Z Q Y, all four K conventions (b_k = sum_j M_kj/2 Km_k^{+-1} Kp_j^{+-1} Q eta_j).
    for sp in (1, -1):
        for sm in (1, -1):
            kp = Kp if sp == 1 else [inv(k) for k in Kp]
            km = [inv(k) for k in Km] if sm == 1 else Km
            outs = [[(after(km[k], kp[j], Q), ('eta', j), F(M[k][j], 2)) for j in range(112) if M[k][j]] for k in range(8)]
            dim, ncls = s_target(outs)
            per_mode = [len({cls(after(km[k], kp[j], Q)) for j in range(112) if M[k][j]}) for k in range(8)]
            report[f'b=ZQY Kp^{sp} Km^{-sm}'] = dict(dim_S_target=dim, nonbase_classes=ncls, classes_per_mode=per_mode)
            print(f'b = Z Q Y  (Kp^{sp:+d}, Km^{-sm:+d}):  dim S_target = {dim}  classes {ncls}  per mode {per_mode}')

    # 2. whole #5415 exit from (xi=X, eta=Y, zeta=H):  H_o = Q zeta + Z Q eta ; X_o = xi - W H_o ; Y_o = eta
    #    W = Kp^-1 M Km / 2 , Z = Km^-1 M^T Kp / 2.
    Ho = [[(Q, ('zeta', k), F(1))] + [(after(inv(Km[k]), Kp[j], Q), ('eta', j), F(M[k][j], 2)) for j in range(112) if M[k][j]] for k in range(8)]
    Xo = []
    for i in range(112):
        t = [(ce.ident(n), ('xi', i), F(1))]
        for k in range(8):
            if not M[k][i]: continue
            for op, var, c in Ho[k]:
                t.append((after(inv(Kp[i]), Km[k], op), var, -F(M[k][i], 2) * c))
        Xo.append(t)
    dimH, _ = s_target(Ho); dimAll, ncls = s_target(Ho + Xo)
    report['exit H_o only'] = dimH; report['exit all outputs'] = dimAll
    print('whole exit: dim S_target from H_o =', dimH, '; from (X_o, Y_o, H_o) =', dimAll, '(nonbase classes', ncls, ')')

    # 3. controls
    #  (a) if the port maps were trivial, the 56 terms of a mode share one class: bound collapses to 8
    outs = [[(after(inv(Km[k]), Q), ('eta', j), F(M[k][j], 2)) for j in range(112) if M[k][j]] for k in range(8)]
    print('control trivial ports: dim S_target =', s_target(outs)[0], '(expect 8)')
    #  (b) same target in y-coordinates (pre-return y retained as a base variable): b = Km^-1 R Kp y -> 8
    outs = [[(after(inv(Km[k]), Kp[j], R), ('y', j), F(M[k][j], 2)) for j in range(112) if M[k][j]] for k in range(8)]
    print('control y-coordinates (8 R jobs on Zy suffice): dim S_target =', s_target(outs)[0], '(expect 8)')
    #  (c) a monomial target has no non-base class: bound 0
    outs = [[(after(inv(Km[k]), Kp[j]), ('eta', j), F(M[k][j], 2)) for j in range(112) if M[k][j]] for k in range(8)]
    print('control monomial target Z Y: dim S_target =', s_target(outs)[0], '(expect 0)')
    #  (d) rank of every target term and of pairwise quotients inside a mode
    rk = {rank(after(inv(Km[k]), Kp[j], Q)) for k in range(8) for j in range(112) if M[k][j]}
    q2 = {rank(after(inv(after(inv(Km[0]), Kp[a], Q)), inv(Km[0]), Kp[b], Q)) for a in range(112) for b in range(112) if a != b and M[0][a] and M[0][b]}
    print('target term ranks', rk, '; quotient ranks inside mode 0', q2)
    json.dump(report, open(Path(__file__).with_suffix('.json'), 'w'), indent=1)

if __name__ == '__main__':
    main()
