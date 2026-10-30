"""SKELCLASS fcls.py: tiling-relative frame classes (importable; no env, no side effects beyond constants).
Classes (EXACT, from E / the T=384 tiling of SKELGEN tiling.py):
  dim1 'p' port line | dim2 'pr' D3 pair (2 ports, same coset) | dim3 'g' tiling 2+2/3-port frame | dim4 'O' octet frame
  dim5 'G' octet dual | dim6 'hp' h^perp of a tiling frame | dim7 'pp' perp of a reader D3 pair | dim8 'Q' a Y final frame q^perp
  otherwise 'd<dim>' with suffix: '<' if inside some octet frame (port-laminar), '>' if containing some octet dual (reader-laminar)."""
import sys, itertools, collections
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # alignbuild/: tiling.py and life.py are copies here
if HERE not in sys.path: sys.path.insert(0, HERE)
import tiling as TL
from life import rref, perp, dot
P = list(TL.P); m = len(P); D3 = TL.D3
OCTS = TL.OCTS; octi = TL.octi
Ospan = {};
for i in range(m): Ospan.setdefault(octi[i], []).append(P[i])
Ospan = {r: rref(v) for r, v in Ospan.items()}
Gspan = {r: perp(b) for r, b in Ospan.items()}
Oinv = {b: r for r, b in Ospan.items()}; Ginv = {b: r for r, b in Gspan.items()}
G3 = {rref(list(f)): k for k, (f, ps) in enumerate(TL.fl)}
HP = {perp(rref(list(f))): k for k, (f, ps) in enumerate(TL.fl)}
PR = {}
for i in range(m):
    for d in D3:
        v = P[i] ^ d
        if v in TL.pidx: PR[rref([P[i], v])] = (i, TL.pidx[v])
PP = {perp(b): ij for b, ij in PR.items()}
QQ = {perp((P[j],)): j for j in range(m)}
PL = {(P[i],): i for i in range(m)}
def contains(big, small):
    return rref(list(big) + list(small)) == tuple(big)
def cls(b):
    b = rref(b); d = len(b)
    if d == 1 and b in PL: return ('p', PL[b])
    if d == 2 and b in PR: return ('pr', PR[b])
    if d == 3 and b in G3: return ('g', G3[b])
    if d == 4 and b in Oinv: return ('O', Oinv[b])
    if d == 5 and b in Ginv: return ('G', Ginv[b])
    if d == 6 and b in HP: return ('hp', HP[b])
    if d == 7 and b in PP: return ('pp', PP[b])
    if d == 8 and b in QQ: return ('Q', QQ[b])
    s = 'd%d' % d
    if d and d < 9:
        if any(contains(O, b) for O in Ospan.values()): s += '<'
        if any(contains(b, G) for G in Gspan.values()): s += '>'
    return (s, None)
def ports_in(b):
    b = rref(b); return [i for i in range(m) if contains(b, (P[i],))]
def readers_of(b):
    """readers j with frame b inside Q_j (q_j perp to all of b)"""
    return [j for j in range(m) if all(not dot(P[j], x) for x in b)]
