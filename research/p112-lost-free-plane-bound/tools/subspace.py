"""Lost-free sets from subspaces: S = labels orthogonal to a small subspace U = W^perp, planes <q, r_c>
with r_c from an orthonormal set inside U assigned by a proper colouring of the q-orthogonality graph on S.
Every r in U is orthogonal to every q in S, distinct orthonormal r's are orthogonal, so adjacent ports
(q-orthogonal) get orthogonal planes: S is lost-free. Enumerate U of dimension 1..4.
"""
import importlib.util, itertools, json, sys
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("pr2484", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                       (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
N = 112


def span(vs):
    out = {0}
    for v in vs:
        out |= {x ^ v for x in out}
    return out


def max_orthonormal(vecs):
    odd = [v for v in vecs if v and dot(v, v) == 1]
    best = []
    def grow(cl, cand):
        nonlocal best
        if len(cl) > len(best): best = list(cl)
        for i, u in enumerate(cand):
            grow(cl + [u], [w for w in cand[i + 1:] if dot(u, w) == 0])
    grow([], odd)
    return best


def colour(S, k):
    """Exact k-colouring of the q-orthogonality graph on S (backtracking, DSATUR order)."""
    adj = {a: [b for b in S if b != a and dot(q[a], q[b]) == 0] for a in S}
    col = {}
    order = sorted(S, key=lambda a: -len(adj[a]))
    def bt(i):
        if i == len(order): return True
        a = order[i]
        used = {col[b] for b in adj[a] if b in col}
        for c in range(k):
            if c not in used:
                col[a] = c
                if bt(i + 1): return True
                del col[a]
        return False
    return dict(col) if bt(0) else None


seen = set(); best = (0,)
results = []
for d in (1, 2, 3, 4):
    for basis in itertools.combinations(range(1, 512), d):
        U = span(basis)
        if len(U) != 2 ** d: continue
        key = frozenset(U)
        if key in seen: continue
        seen.add(key)
        S = [a for a in range(N) if all(dot(q[a], u) == 0 for u in basis)]
        if len(S) <= best[0] and len(S) < 37: continue
        R = max_orthonormal(sorted(U))
        if not R: continue
        col = colour(S, len(R))
        if col is None: continue
        if len(S) > best[0]:
            best = (len(S), d, sorted(basis), R, col)
            print("d=%d |S|=%d colours=%d" % (d, len(S), len(R)), flush=True)
    print("done d", d, "best", best[0], flush=True)
if best[0]:
    n, d, basis, R, col = best
    json.dump({"U_basis": basis, "orthonormal_r": R, "S": sorted(col), "colour": {str(a): c for a, c in col.items()}},
              open(Path(__file__).with_name("subspace-best.json"), "w"))
