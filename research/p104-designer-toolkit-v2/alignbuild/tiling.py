"""SKELGEN tiling.py: [CAVEAT: btype "coset"/"cycle" is a TILING label only; a coset-block read can be labelled cycle (P1 dim-3 Y reads) -- check slots on chains, not btype] the T=384 rank-1 meet tiling of E (QUADHUB meet.py, re-derived; EXACT). Importable, no side effects beyond constants.
Exports: P (104 port vectors = reader vectors), RES, entry->block, blocks {(kg,kh): entries}, frames fl[k]=(basis, ports), comp type per block."""
import sys, collections, itertools, numpy as np
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gen2'))
import geo, rt
P = geo.PORTS; m = geo.m; D3 = [120, 85, 75, 51, 102, 30, 45]; T = 384
cos = {i: min(P[i] ^ d for d in D3 + [0]) for i in range(m)}
oc = {i: min(cos[i], min(P[i] ^ T ^ d for d in D3 + [0])) for i in range(m)}
OCTS = sorted(set(oc.values())); octi = {i: OCTS.index(oc[i]) for i in range(m)}
mem = collections.defaultdict(list)
for i in range(m): mem[oc[i]].append(i)
frames = {}
for o, v in mem.items():
    for a, b, c in itertools.combinations(v, 3):
        f = rt.rref([P[a], P[b], P[c]])
        if len(f) != 3: continue
        S = rt.span_set(f); frames[f] = tuple(sorted(i for i in v if P[i] in S))
fl = list(frames.items())
ent = [(j, i) for j in range(m) for i in range(m) if geo.ORTH[j, i] and abs(geo.RES[j, i]) > 1e-9]
byi = collections.defaultdict(list)
for k, (f, ps) in enumerate(fl):
    for i in ps: byi[i].append(k)
blocks = collections.defaultdict(list); eblk = {}
for (j, i) in ent:
    for kg in byi[i]:
        g = fl[kg][0]
        for kh in byi[j]:
            h = fl[kh][0]
            if all(not geo.par(x, y) for x in g for y in h):
                blocks[(kg, kh)].append((j, i)); eblk[(j, i)] = (kg, kh)
adj = collections.defaultdict(set)
for (kg, kh) in blocks: adj[('g', kg)].add(('h', kh)); adj[('h', kh)].add(('g', kg))
btype = {}
for (kg, kh) in blocks:
    btype[(kg, kh)] = 'coset' if len(adj[('g', kg)]) == 1 and len(adj[('h', kh)]) == 1 else 'cycle'
pidx = {v: i for i, v in enumerate(P)}
if __name__ == '__main__':
    print('blocks', len(blocks), collections.Counter(btype.values()), 'entries', len(ent), 'covered', len(eblk))
    print('port frames: #blocks', collections.Counter(len(adj[('g', k)]) for k in range(len(fl)) if ('g', k) in adj))
