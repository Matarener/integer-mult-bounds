"""gen2/dyadic.py -- exact factorisation of a det-1 matrix over Z[1/2] into dyadic elementary row additions (copy of planbuild/build.py _decompose /
_decompose1, PLANBUILD5 F9-repair factoriser: Euclid on odd parts per connected component + the SL2 scale identity diag(d,1/d) = W(d)W(-1)).
Copied (not imported) because build.py pulls HUBCOST/PAIRMIX at import.  Used by purex2 --dyfix (GENUPGRADE).  No env at import."""
import collections
from fractions import Fraction as Fr
def _decompose(A):
    for extra in (24, 88, 216, 472):
        try: return _decompose1(A, extra)
        except AssertionError as e:
            if str(e) != 'scale overflow': raise
    raise AssertionError('scale overflow')

def _decompose1(A, extra):
    """A: rows over Z[1/2] (m x m, list of lists of Fractions, det 1). Returns elementary row ops (i, j, t), t DYADIC Fraction [row_i += t row_j], that reduce A to I.
    Integer-scaled sparse rows (value = n / 2^SC); connected components eliminated independently; Euclid on the odd parts only when no unit pivot exists (a unit pivot, the diagonal
    first, needs no division); the leftover unit diagonal (product 1) is fixed across components by diag(d, 1/d) = W(d) W(-1), W(t) = U(t) L(-1/t) U(t)."""
    m = len(A); SC = max([(v.denominator.bit_length() - 1) for r in A for v in r if v] + [0]) + extra
    one = 1 << SC
    R = [{c: int(v * one) for c, v in enumerate(r) if v} for r in A]; ops = []
    for r in R:
        pass
    def odd(n):
        low = (n & -n).bit_length() - 1
        return low, n >> low
    par = list(range(m))
    def find(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(m):
        for c in R[i]: par[find(i)] = find(c)
    comp = collections.defaultdict(list)
    for i in range(m): comp[find(i)].append(i)
    def add(i, j, t):                                  # row_i += t row_j, t dyadic Fraction
        if t == 0: return
        tn, td = t.numerator, t.denominator
        assert (td & (td - 1)) == 0, ('non-dyadic', t)
        sh = td.bit_length() - 1; Ri = R[i]
        for c, v in R[j].items():
            w = v * tn
            if sh:
                assert w & (td - 1) == 0, 'scale overflow'
                w >>= sh
            x = Ri.get(c, 0) + w
            if x: Ri[c] = x
            else: Ri.pop(c, None)
        ops.append((i, j, t))
    for members in comp.values():
        members.sort(key=lambda i: len(R[i]))            # sparse rows first (less fill)
        for jj, j in enumerate(members):
            while True:
                nz = [i for i in members[jj:] if R[i].get(j)]
                assert nz, 'singular'
                if len(nz) == 1: break
                p = min(nz, key=lambda i: (abs(odd(R[i][j])[1]), i != j))      # a unit pivot (prefer the diagonal) if there is one
                sp, op = odd(R[p][j])
                for i in nz:
                    if i == p: continue
                    si, oi = odd(R[i][j])
                    qq = oi // op                           # floor division on the odd parts: remainder |r| < |op|
                    if qq: add(i, p, -Fr(qq) * Fr(2) ** (si - sp))
            p = nz[0]
            if p != j:
                assert not R[j].get(j), 'pivot'
                add(j, p, Fr(1)); add(p, j, -Fr(R[p][j], R[j][j]))
        for j in members:
            assert abs(odd(R[j][j])[1]) == 1, ('pivot not a unit', R[j][j])
        for j in reversed(members):
            for i in members:
                if i != j and R[i].get(j): add(i, j, -Fr(R[i][j], R[j][j]))
    P = Fr(1)
    for j in range(m): P *= Fr(R[j][j], one)
    assert P == 1, ('det', P)
    def W(i, j, t): add(i, j, t); add(j, i, -1 / t); add(i, j, t)
    for j in range(m - 1):
        d = Fr(R[j][j], one)
        if d != 1:
            W(j, j + 1, Fr(-1)); W(j, j + 1, 1 / d)       # diag(1/d, d) = W(1/d) W(-1)
    assert all(R[i] == {i: one} for i in range(m)), 'decompose'
    return ops
