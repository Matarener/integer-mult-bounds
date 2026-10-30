"""For a fixed port set S, find r_a (plane <q_a, r_a>) making S lost-free, by backtracking with
forward checking (MRV). Constraints for each q-orthogonal pair a,b in S: q_a.r_b = r_a.q_b = r_a.r_b = 0."""
import importlib.util, json, sys, time
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("pr2484", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                       (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
S = json.load(open(sys.argv[1]))
S = list(S) if isinstance(S, list) else [int(k) for k in S]
adj = {a: [b for b in S if b != a and dot(q[a], q[b]) == 0] for a in S}
# unary filtering: r_a must be orthogonal to q_b for every neighbour b
dom = {}
for a in S:
    dom[a] = [r for r in range(1, 512) if dot(r, q[a]) == 0 and dot(r, r) == 1 and all(dot(r, q[b]) == 0 for b in adj[a])]
print("|S|", len(S), "min domain", min(len(v) for v in dom.values()), "max deg", max(len(v) for v in adj.values()), flush=True)
if min(len(v) for v in dom.values()) == 0:
    print("UNSAT by unary filtering"); sys.exit()
assign = {}; nodes = [0]; t0 = time.time()
def bt(domains):
    nodes[0] += 1
    if nodes[0] % 200000 == 0: print("nodes", nodes[0], "assigned", len(assign), "t=%.0f" % (time.time() - t0), flush=True)
    if len(assign) == len(S): return True
    a = min((x for x in S if x not in assign), key=lambda x: len(domains[x]))
    for r in domains[a]:
        new = dict(domains); okk = True
        for b in adj[a]:
            if b in assign: continue
            nd = [s for s in new[b] if dot(r, s) == 0]
            if not nd: okk = False; break
            new[b] = nd
        if not okk: continue
        assign[a] = r
        if bt(new): return True
        del assign[a]
    return False
res = bt(dom)
print("SAT" if res else "UNSAT", "nodes", nodes[0])
if res:
    json.dump({str(a): assign[a] for a in S}, open(sys.argv[1].replace('.json', '-planes.json'), 'w'))
