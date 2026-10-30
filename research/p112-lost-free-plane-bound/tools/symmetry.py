"""Isometries of (F2^9, dot) that preserve the 112 P112 labels, as permutations of ports.

An isometry is fixed by the images of a label basis B (images: labels with the same Gram matrix).
Pruning: as soon as basis vectors 0..i are placed, every label whose B-coordinates use only those
vectors must map to a label. Output: symmetry.json with a list of port permutations and a proof that
port 0 reaches every port (one orbit).
"""
import importlib.util, json, random, sys, time
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("v", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                       (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
N = 112
L = {v: i for i, v in enumerate(q)}
HERE = Path(__file__).resolve().parent
LOG = open(HERE / "symmetry.log", "w", encoding="utf-8")


def say(s):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), s)
    print(line, flush=True); LOG.write(line + "\n"); LOG.flush()


# basis of labels, starting with port 0
B, red = [], []
for v in q:
    w = v
    for b in red:
        w = min(w, w ^ b)
    if w:
        B.append(v); red.append(w); red.sort(reverse=True)
assert len(B) == 9
coord = {}
for mask in range(1 << 9):
    v = 0
    for i in range(9):
        if mask >> i & 1: v ^= B[i]
    coord[v] = mask
by_top = {}
for i, v in enumerate(q):
    c = coord[v]
    by_top.setdefault(c.bit_length() - 1, []).append(c)
G = [[dot(B[i], B[j]) for j in range(9)] for i in range(9)]


def image(imgs, mask):
    v = 0
    for i in range(len(imgs)):
        if mask >> i & 1: v ^= imgs[i]
    return v


def find(target0, rng):
    """One isometry sending B[0]=q[0] to q[target0], random choice order; returns port permutation."""
    imgs = [q[target0]]
    cands = list(q)

    def bt(i):
        if not all(image(imgs, c) in L for c in by_top.get(i - 1, [])):
            return False
        if i == 9:
            return True
        order = cands[:]; rng.shuffle(order)
        for y in order:
            if all(dot(y, imgs[j]) == G[i][j] for j in range(i)):
                imgs.append(y)
                if bt(i + 1): return True
                imgs.pop()
        return False
    if not bt(1):
        return None
    perm = [L[image(imgs, coord[v])] for v in q]
    assert sorted(perm) == list(range(N))
    return perm


def is_isometry_perm(perm):
    # check: the linear map defined on B extends and preserves all dots among labels
    return all(dot(q[perm[a]], q[perm[b]]) == dot(q[a], q[b]) for a in range(N) for b in range(a, N))


if __name__ == "__main__":
    rng = random.Random(1)
    perms = []
    t0 = time.time()
    reach = set()
    for t in range(N):
        p = find(t, rng)
        if p is None:
            say("порт 0 -> порт %d: изометрии НЕТ" % t)
            continue
        assert is_isometry_perm(p)
        perms.append(p); reach.add(t)
        if t % 8 == 7:
            say("найдено изометрий: %d, достижимо портов: %d из %d, %.0f с" % (len(perms), len(reach), t + 1, time.time() - t0))
    say("ИТОГ: порт 0 переводится в %d портов из 112" % len(reach))
    # extra random elements for the stabiliser / lex-leader constraints
    for k in range(int(sys.argv[1]) if len(sys.argv) > 1 else 200):
        p = find(rng.randrange(N), rng)
        if p: perms.append(p)
    json.dump({"orbit_of_0": sorted(reach), "perms": perms}, open(HERE / "symmetry.json", "w"))
    say("сохранено перестановок: %d" % len(perms))
