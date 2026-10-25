"""Exact maximum lost-free subset of a given port set C (CP-SAT), and density screens of substructure families.

Lost-free S (philippeVV): every q-orthogonal pair a,b in S has orthogonal planes <q_a,r_a>, <q_b,r_b>,
with r_a.q_a = 0, r_a.r_a = 1. For a family F of port sets in which every port lies in the same number
of members, |S| <= 112 * max over... averaging gives |S| <= 112 * w(C)/|C| when all members share (|C|, w).
"""
import importlib.util, json, sys, time
from pathlib import Path
from ortools.sat.python import cp_model
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("v", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                       (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
N = 112
bits = lambda v: [i for i in range(9) if v >> i & 1]


def max_lostfree(C, seconds=60, workers=4):
    C = sorted(C)
    m = cp_model.CpModel()
    x = {a: m.NewBoolVar("") for a in C}
    z = {a: [m.NewBoolVar("") for _ in range(9)] for a in C}

    def parity(lits, odd, en=None):
        k = m.NewIntVar(0, len(lits), "")
        c = m.Add(sum(lits) == 2 * k + (1 if odd else 0))
        if en: c.OnlyEnforceIf(en)
    for a in C:
        parity([z[a][i] for i in bits(q[a])], False)
        parity(z[a], True)
    for i, a in enumerate(C):
        for b in C[i + 1:]:
            if dot(q[a], q[b]) == 0:
                en = [x[a], x[b]]
                parity([z[b][t] for t in bits(q[a])], False, en)
                parity([z[a][t] for t in bits(q[b])], False, en)
                p = []
                for t in range(9):
                    v = m.NewBoolVar("")
                    m.AddBoolAnd([z[a][t], z[b][t]]).OnlyEnforceIf(v)
                    m.AddBoolOr([z[a][t].Not(), z[b][t].Not()]).OnlyEnforceIf(v.Not())
                    p.append(v)
                parity(p, False, en)
    m.Maximize(sum(x.values()))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = workers
    st = s.Solve(m)
    return int(s.ObjectiveValue()), int(s.BestObjectiveBound()), s.StatusName(st)


if __name__ == "__main__":
    # screen 1: subspaces v-perp (labels orthogonal to v), grouped by size
    t0 = time.time()
    sizes = {}
    for v in range(1, 512):
        C = [a for a in range(N) if dot(q[a], v) == 0]
        sizes.setdefault(len(C), []).append(v)
    print("v-perp label counts:", {k: len(vs) for k, vs in sorted(sizes.items())}, flush=True)
    for size, vs in sorted(sizes.items()):
        if size == 0: continue
        C = [a for a in range(N) if dot(q[a], vs[0]) == 0]
        lo, hi, st = max_lostfree(C, seconds=float(sys.argv[1]) if len(sys.argv) > 1 else 60)
        print("|C|=%d (%d vectors v): max lost-free in [%d,%d] %s, density bound %.3f -> 112*d = %.1f" % (
            size, len(vs), lo, hi, st, hi / size, 112 * hi / size), flush=True)
