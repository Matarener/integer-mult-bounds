"""ysink.py: census of the 'Y as its own sink at G' interface relaxation, all 14 duals of #6030. For each served Y (receives ADDs from G's members):
its chain, whether G nests into it (lower frames inside G, upper frames containing G), and the reads (ADD/COPY into Y) at each lower frame that would
have to move if the Y were re-routed through G."""
import os
import json, gzip, collections, sys
sys.path[:0] = [os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/surgery']
import swlib as S
w = json.load(gzip.open(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/words/6030.json.gz'))
dim = [len(b) for b in w['frames']]; n = len(w['initial']); role = S.roles_of(w)
def sp(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
SP = [sp(b) for b in w['frames']]
cur = list(w['initial']) + [None] * 40; chain = {r: [(w['initial'][r], 0)] for r in range(n)}; reads = collections.Counter(); adds = []
for t, e in enumerate(w['program']):
    if e[0] == 'MOVE':
        if e[1] < n: chain[e[1]].append((e[3], t))
        cur[e[1]] = e[3]
    elif e[0] == 'INIT': cur[e[1]] = e[2]
    elif e[0] in ('ADD', 'COPY'):
        adds.append((t, e[1], e[2], e[-1])); reads[(e[1], e[-1])] += 1
for G in [118, 1050, 116, 1048, 114, 1052, 1049, 1051, 1053, 120, 1027, 115, 1031, 117]:
    M = [r for r in range(n) if role(r) == 'H' and any(f == G for f, _ in chain[r])]; Ms = set(M)
    served = sorted(set(d for t, d, s, f in adds if s in Ms and role(d) == 'Y'))
    print('dual', G, 'members', len(M), 'served', served)
    for y in served:
        ch = [(f, dim[f]) for f, _ in chain[y]]
        lo = [f for f, d in ch if d < dim[G]]; hi = [f for f, d in ch if d > dim[G]]; at = [f for f, d in ch if d == dim[G]]
        okl = all(SP[f] <= SP[G] for f in lo); okh = all(SP[G] <= SP[f] for f in hi)
        bad = [(f, dim[f], reads[(y, f)]) for f in lo if not SP[f] <= SP[G]] + [(f, dim[f], reads[(y, f)]) for f in at]
        print('   Y', y, ch, 'lower-in-G', okl, 'upper-contain-G', okh, '| frames to move (f, dim, reads into Y there):', bad)
