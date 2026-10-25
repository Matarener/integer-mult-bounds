"""Local search for large lost-free sets with free plane choices.

State: S (set of ports) and r_a for a in S. Invariant: for all a != b in S with q_a.q_b = 0, the planes
<q_a,r_a>, <q_b,r_b> are orthogonal (q_a.r_b = r_a.q_b = r_a.r_b = 0).
Move: pick t not in S; over its 128 plane choices pick r minimising the S-members it conflicts with;
insert t with that r and evict the conflicting members (accept if the size does not shrink by more than
the tabu/annealing allows). Occasionally re-choose r for a member to free neighbours.
"""
import importlib.util, json, random, sys, time
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("pr2484", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                       (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
N = 112
R = [[r for r in range(1, 512) if dot(r, q[t]) == 0 and dot(r, r) == 1] for t in range(N)]
assert all(len(x) == 128 for x in R)
adjq = [[b for b in range(N) if b != a and dot(q[a], q[b]) == 0] for a in range(N)]


def ok(a, ra, b, rb):
    return dot(q[a], rb) == 0 and dot(ra, q[b]) == 0 and dot(ra, rb) == 0


def conflicts(t, rt, S, r):
    return [b for b in adjq[t] if b in S and not ok(t, rt, b, r[b])]


def main(seed, seconds):
    rng = random.Random(seed)
    S, r = set(), {}
    best, bestS = 0, None
    t0 = time.time(); tabu = {}
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        outside = [t for t in range(N) if t not in S and tabu.get(t, 0) <= it]
        t = rng.choice(outside)
        opts = []
        for rt in R[t]:
            c = conflicts(t, rt, S, r)
            opts.append((len(c), rng.random(), rt, c))
        opts.sort()
        k, _, rt, c = opts[0]
        if k <= 1 or rng.random() < 0.02 * (2 - min(k, 2)) + (0.05 if k == 2 else 0):
            for b in c:
                S.discard(b); r.pop(b, None); tabu[b] = it + 7
            S.add(t); r[t] = rt
        if len(S) > best:
            best, bestS = len(S), {a: r[a] for a in S}
            print("t=%.0f it=%d |S|=%d" % (time.time() - t0, it, best), flush=True)
            json.dump({str(a): v for a, v in bestS.items()}, open(Path(__file__).with_name("lf-%d.json" % seed), "w"))
    print("best", best, "iterations", it)


if __name__ == "__main__":
    main(int(sys.argv[1]), float(sys.argv[2]))
