"""SPAN5 library: per-octet bottom (dims 1..LO) extraction from a SUBOPT census, x-only per-frame span law, octets, catalogue.
Read-only on census pickles.  No env vars set here."""
import pickle, sys, collections
from fractions import Fraction as Q
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'alignbuild'))
from life import tax
CENS = {}      # census pickles of #5907 / r104 (2.4 MB each) are not shipped; load(word) needs them in ext/
PAIRS = [(0, 27), (1, 26), (2, 3), (4, 5), (6, 17), (7, 16), (8, 25), (9, 22), (10, 24), (11, 23), (12, 15), (13, 14), (18, 21), (19, 20)]
LO = 4

def spanset(b):
    S = {0}
    for v in b: S |= {x ^ v for x in S}
    return frozenset(S)
def dimof(S): return len(S).bit_length() - 1

def octets():
    cl = pickle.load(open(os.path.join(HERE, 'data', 'clus_7.pkl'), 'rb'))['cls']
    oc = {}
    for k, (a, b) in enumerate(PAIRS):
        for c in cl[a] + cl[b]: oc[c] = k
    return oc

def xv(v):
    """x-part (port columns are ints) as a normalised direction key: tuple of (col, Fraction) with first coef 1 (exact rational scaling)"""
    v = {c: Q(x) for c, x in v.items() if isinstance(c, int) and x}
    return v

def dirkey(v):
    if not v: return ()
    ks = sorted(v); c0 = v[ks[0]]
    return tuple((k, v[k] / c0) for k in ks)

def rank(rows):
    basis = []
    for r in rows:
        v = dict(r)
        for (k, b) in basis:
            if k in v:
                c = v[k]
                for kk, x in b.items():
                    y = v.get(kk, 0) - c * x
                    if y: v[kk] = y
                    else: v.pop(kk, None)
        if v:
            k = min(v); c = v[k]; basis.append((k, {kk: x / c for kk, x in v.items()}))
    return len(basis)

def span_eq(A, B):
    A = [a for a in A if a]; B = [b for b in B if b]
    ra, rb, rab = rank(A), rank(B), rank(A + B)
    return ra == rb == rab, (ra, rb, rab)

def load(word):
    return pickle.load(open(CENS[word], 'rb'))

def bottom(R, lo=LO):
    """per register (non-owned): birth dim, bottom stops [(dim, framekey, arr_x, dep_x)], fate ('CROSS', g framekey, gdim, topchain dims) / ('END',) / ('DONE',)
    dep_x of the last bottom stop = arrival x at the next stop (or final)."""
    st, dimf, ro, F = R['stops'], R['dimf'], R['roles'], R['F']
    SP = {}
    def fk(i):
        if i not in SP: SP[i] = spanset(F[i])
        return SP[i]
    out = {}
    for r, S in st.items():
        if ro[r] == 'O': continue
        ds = [dimf[s['f']] for s in S]
        bot = [i for i in range(len(S)) if ds[i] <= lo]
        stops = []
        for i in bot:
            nxt = xv(S[i + 1]['arr']) if i + 1 < len(S) else xv(R['final'][r])
            stops.append((ds[i], fk(S[i]['f']), xv(S[i]['arr']), nxt))
        nx = bot[-1] + 1 if bot else 0
        if nx < len(S):
            if ds[nx] == 9 and nx == len(S) - 1: fate = ('DONE',)
            else: fate = ('CROSS', fk(S[nx]['f']), ds[nx], tuple(ds[nx:]))
        else: fate = ('END',)
        out[r] = dict(role=ro[r], born=ds[0], stops=stops, fate=fate, ds=ds)
    return out

def chain_cost(I):
    return tax(I['ds'])
