"""Prove the 112 P112 labels form one orbit under isometries s_v(x) = x + (x.v) v (v even) that preserve the label set."""
import importlib.util
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("v", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                       (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
L = set(q)
gens = []
for v in range(1, 512):
    if dot(v, v) == 0:
        img = {x ^ (v if dot(x, v) else 0) for x in L}
        if img == L:
            gens.append(v)
orbit = {q[0]}; frontier = [q[0]]
while frontier:
    x = frontier.pop()
    for v in gens:
        y = x ^ (v if dot(x, v) else 0)
        if y not in orbit:
            orbit.add(y); frontier.append(y)
print("label-preserving even reflections:", len(gens), "orbit of port 0:", len(orbit), "of", len(L))

# general isometries: images of a label basis with equal Gram matrix whose linear extension preserves L
def basis_of(vs):
    B, red = [], []
    for v in vs:
        w = v
        for b in red:
            w = min(w, w ^ b)
        if w:
            B.append(v); red.append(w)
            red.sort(reverse=True)
    return B
B = basis_of([q[0]] + q[1:])
assert len(B) == 9 and B[0] == q[0]
# coordinates of each label in basis B (solve over F2)
import itertools
def coords_table(B):
    table = {}
    for mask in range(1 << 9):
        v = 0
        for i in range(9):
            if mask >> i & 1: v ^= B[i]
        table[v] = mask
    return table
CT = coords_table(B)
Lcoords = [CT[x] for x in q]
def apply(imgs, mask):
    v = 0
    for i in range(9):
        if mask >> i & 1: v ^= imgs[i]
    return v
def find_iso(t):
    imgs = [q[t]]
    def bt(i):
        if i == 9:
            return all(apply(imgs, c) in L for c in Lcoords)
        for y in q:
            if all(dot(y, imgs[j]) == dot(B[i], B[j]) for j in range(i)):
                imgs.append(y)
                if bt(i + 1): return True
                imgs.pop()
        return False
    return list(imgs) if bt(1) else None
ok = 0
import time; t0 = time.time()
for t in range(112):
    if find_iso(t): ok += 1
    else: print("no isometry found for port", t)
print("ports reachable from port 0 by a label-preserving isometry:", ok, "of 112 (%.0fs)" % (time.time() - t0))
