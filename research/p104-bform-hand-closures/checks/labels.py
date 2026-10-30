# Port data and label classes of P104 without setup9 (no networkx).  Ports: the repo's E8 line list minus the frames
# F0, F1 (same order as setup9.load('P104') and lbz.py).  Labels are E8 modulo 2: a class c = (x, eps), x in E8/2E8,
# eps in F2, (x, eps) != (0, 0), has odd set O_c = { t : <r_t, x> + eps odd } (511 classes; 9-bit index: bits 0..7 =
# coordinates of x in a basis of E8/2E8 chosen below, bit 8 = eps).  cls[c] is O_c as a 104-bit mask, as in setup9.
# Apache-2.0.
import itertools
import _paths
from common2 import E8, Gmat
from frames_data import load_frames
F0, F1 = load_frames()
L = [E8[i] for i in range(120) if i not in set(F0) | set(F1)]
v = len(L); G = Gmat(L); full = (1 << v) - 1
def dotq(a, b): return sum(x * y for x, y in zip(a, b))
# parity of <r, x> over the 120 E8 lines determines x mod 2E8 (the form is non-degenerate mod 2)
def sig(x): return sum((int(dotq(r, x)) & 1) << i for i, r in enumerate(E8))
cand = list(E8) + [[a + b for a, b in zip(r, s)] for r, s in itertools.combinations(E8, 2)]
basis, sigs = [], []
def reduce(s):
    for b in sigs:
        if s ^ b < s: s ^= b
    return s
for x in cand:
    s = reduce(sig(x))
    if s:
        basis.append(x); sigs.append(s); sigs.sort(reverse=True)
        if len(basis) == 8: break
assert len(basis) == 8
def omask(x): return sum(1 << t for t in range(v) if int(dotq(L[t], x)) & 1)
BM = [omask(x) for x in basis] + [full]
cls = {}
for c in range(1, 512):
    m = 0
    for i in range(9):
        if c >> i & 1: m ^= BM[i]
    cls[c] = m
assert len(set(cls.values())) == 511
pc = lambda x: bin(x).count('1')
