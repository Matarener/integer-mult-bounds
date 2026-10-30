"""Can the 112 P112 labels be partitioned into 14 orthonormal 8-frames (exact cover)?

Each 8-frame (8 unit labels, pairwise dot 0) gives 4 pairwise orthogonal planes, i.e. one colour class
of the plane graph; 14 frames give a perfect matching whose plane graph is 14-colourable, hence a
scalar fit with 28 disjoint supports.  4 is the largest possible orthogonal plane set in F2^9.
"""
import json, sys, time
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
sys.path.insert(0, str(ROOT / "research/paired-plane-minrank-bracket-audit"))
import verify as V

archive = (ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes()
matching = (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes()
labels, _, _ = V.load_model(archive, matching)
dot = V.parity_dot
N = 112
assert all(dot(q, q) == 1 for q in labels)
nb = [frozenset(j for j in range(N) if j != i and dot(labels[i], labels[j]) == 0) for i in range(N)]
print('orthogonal degree range', min(map(len, nb)), max(map(len, nb)), flush=True)


def cliques_containing(v, size):
    """All orthonormal size-sets whose smallest element is v."""
    out = []
    def grow(cl, cand):
        if len(cl) == size:
            out.append(tuple(cl))
            return
        for u in sorted(cand):
            if u > cl[-1]:
                grow(cl + [u], cand & nb[u])
    grow([v], frozenset(u for u in nb[v] if u > v))
    return out


t0 = time.time()
frames = []
for v in range(N):
    frames += cliques_containing(v, 8)
print('8-frames', len(frames), 'in %.1fs' % (time.time() - t0), flush=True)
by_elem = [[] for _ in range(N)]
for k, f in enumerate(frames):
    for x in f:
        by_elem[x].append(k)
print('frames per label range', min(map(len, by_elem)), max(map(len, by_elem)), flush=True)

# Algorithm X on bitmasks
masks = [sum(1 << x for x in f) for f in frames]
FULL = (1 << N) - 1
nodes = [0]
import random
def search(covered, alive, chosen):
    nodes[0] += 1
    if covered == FULL:
        return list(chosen)
    if nodes[0] > LIMIT:
        return None
    best_x, best_c = None, None
    for x in range(N):
        if not covered >> x & 1:
            c = [k for k in alive if masks[k] >> x & 1]
            if best_c is None or len(c) < len(best_c):
                best_x, best_c = x, c
                if len(c) <= 1:
                    break
    for k in best_c:
        m = masks[k]
        chosen.append(k)
        res = search(covered | m, [j for j in alive if not masks[j] & m], chosen)
        if res:
            return res
        chosen.pop()
    return None
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
sol = search(0, list(range(len(frames))), [])
print('nodes', nodes[0], 'solution', sol is not None, flush=True)
if sol:
    cover = [frames[k] for k in sol]
    pairs = [(f[2 * i], f[2 * i + 1]) for f in cover for i in range(4)]
    json.dump({'frames': cover, 'pairs': pairs}, open(Path(__file__).with_name('frames-cover.json'), 'w'))
    print('pairs written', len(pairs))
