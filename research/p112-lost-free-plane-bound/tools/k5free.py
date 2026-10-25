"""Largest set of P112 labels with no five pairwise orthogonal members (necessary for lost-free)."""
import importlib.util, json, random, sys, time, itertools
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("pr2484", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                       (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
N = 112
nb = [frozenset(j for j in range(N) if j != i and dot(q[i], q[j]) == 0) for i in range(N)]
K5 = []
def grow(cl, cand):
    if len(cl) == 5:
        K5.append(frozenset(cl)); return
    for u in sorted(cand):
        if u > cl[-1]: grow(cl + [u], cand & nb[u])
for v in range(N): grow([v], frozenset(u for u in nb[v] if u > v))
print("5-cliques", len(K5), flush=True)
by = [[] for _ in range(N)]
for i, c in enumerate(K5):
    for x in c: by[x].append(i)
rng = random.Random(int(sys.argv[1])); T = float(sys.argv[2])
inS = [False] * N; cnt = [0] * len(K5)  # members of each 5-clique inside S
size = 0; best = 0; t0 = time.time()
def can_add(x):
    return all(cnt[i] < 4 for i in by[x])
while time.time() - t0 < T:
    cand = [x for x in range(N) if not inS[x] and can_add(x)]
    if cand:
        x = rng.choice(cand); inS[x] = True; size += 1
        for i in by[x]: cnt[i] += 1
        if size > best:
            best = size; print("t=%.0f size=%d" % (time.time() - t0, best), flush=True)
            json.dump([y for y in range(N) if inS[y]], open(Path(__file__).with_name("k5free-%s.json" % sys.argv[1]), "w"))
        continue
    # swap: add x (blocked), remove one member from each saturated clique it would complete
    x = rng.choice([y for y in range(N) if not inS[y]])
    rem = set()
    for i in by[x]:
        if cnt[i] == 4:
            if not (K5[i] & rem):
                rem.add(rng.choice([y for y in K5[i] if inS[y]]))
    if len(rem) <= 1 or rng.random() < 0.01:
        for y in rem:
            inS[y] = False; size -= 1
            for i in by[y]: cnt[i] -= 1
        if can_add(x):
            inS[x] = True; size += 1
            for i in by[x]: cnt[i] += 1
print("best", best)
