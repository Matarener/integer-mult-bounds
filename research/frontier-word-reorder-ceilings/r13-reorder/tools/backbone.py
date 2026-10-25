"""Exact backbone ceiling: frames forced in EVERY linear extension of the conflict poset
(fixed warps, pinned C0 ops) form a chain per register segment; any valid chain contains
them and, by subadditivity of x^(1-C), costs at least the backbone chain. Valid lower bound
on the local paid cost of any reorder+frame lever (same ADD program, same warps/interfaces)."""
import sys, json
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from sdom import *
from price import root

def backbone(S):
    dom, Fm = S['dom'], S['Fm']; prof = Counter(); chains = {}
    for key in set(S['members']) | set(S['ends']):
        fs = set(S['ends'][key])
        for i in S['members'].get(key, []):
            if len(dom[i]) == 1: fs |= dom[i]
        ch = sorted(fs, key=lambda X: Fm.dims[X])
        for a, b in zip(ch, ch[1:]):
            assert Fm.dims[a] < Fm.dims[b] and Fm.spans[a] < Fm.spans[b], (key, a, b)
            prof[Fm.dims[b]-Fm.dims[a]] += 1
        chains[key] = ch
    return prof, chains

if __name__ == '__main__':
    w = load()
    for side, rw in (('forward', False), ('forward', True), ('backward', True)):
        S = domains(w, side, relax_warps=rw); prof, _ = backbone(S); C = 0.00302
        cost = sum(n*r**(1-C) for r, n in prof.items())
        print(side, 'relax_warps', rw, 'backbone profile', dict(sorted(prof.items())), 'mass', sum(k*v for k, v in prof.items()), 'cost', cost, 'root(if mass-padded)', root(prof) if sum(k*v for k,v in prof.items())==5263 else None, flush=True)
