#!/usr/bin/env python3
"""Generate CERTIFICATES.json for the three-plane rank dual (needs scipy; the verifier does not).

For each tariff class of plane triples it records the best principal block-rank functional weights (LP over
w_X, X a nonempty union of planes), an exact dual covering certificate y bounding that family, and, for classes
whose block-rank value is below 12, the exact minimum COPY mass over F2 rank-one atoms (parity ILP, HiGHS).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import KEYS, OFFDIAG, UNIONS, classes_of_triples, phi_bound, pop  # noqa: E402


def lp(T):
    c = [-2 * pop(X) for X in UNIONS]
    A = [[1.0 if (S & X and U & X) else 0.0 for X in UNIONS] for S, U in KEYS]
    r = linprog(c, A_ub=A, b_ub=[T[k] for k in KEYS], bounds=[(0, None)] * 7, method="highs")
    w = [Q(x).limit_denominator(100) for x in r.x]
    y = [Q(-m).limit_denominator(100) for m in r.ineqlin.marginals]
    return w, y


def phi_lp(T):
    """best zeroed-block functional sum_X w_X rank(Phi_Z(M)_XX) over all 64 zero sets Z"""
    best = None
    for mask in range(1 << 6):
        Z = [OFFDIAG[i] for i in range(6) if mask >> i & 1]
        c = [-2 * pop(X) for X in UNIONS]
        A = [[phi_bound(S, U, X, Z) for X in UNIONS] for S, U in KEYS]
        r = linprog(c, A_ub=A, b_ub=[T[k] for k in KEYS], bounds=[(0, None)] * 7, method="highs")
        if best is None or -r.fun > best[0] + 1e-9:
            best = (-r.fun, Z, [Q(x).limit_denominator(100) for x in r.x])
    return best


def f2_minimum(T):
    def closure(vec):
        return sum(1 << k for k in range(3) if vec[2 * k] or vec[2 * k + 1])
    vecs = [v for v in itertools.product((0, 1), repeat=6) if any(v)]
    atoms = [(u, v) for u in vecs for v in vecs]
    n = len(atoms)
    A = np.zeros((36, n + 36))
    b = np.array([1.0 if k // 6 == k % 6 else 0.0 for k in range(36)])
    for a, (u, v) in enumerate(atoms):
        for i in range(6):
            if u[i]:
                for j in range(6):
                    if v[j]:
                        A[6 * i + j, a] = 1
    for k in range(36):
        A[k, n + k] = -2
    cost = np.array([T[closure(u), closure(v)] for u, v in atoms] + [0] * 36, float)
    res = milp(cost, constraints=LinearConstraint(A, b, b), integrality=np.ones(n + 36),
               bounds=Bounds(np.zeros(n + 36), np.concatenate([np.ones(n), np.full(36, 40)])))
    return int(round(res.fun))


def main():
    classes = classes_of_triples()
    path = Path(__file__).resolve().parent / "CERTIFICATES.json"
    old = {}
    if path.exists():
        old = {tuple(r["tariffs"]): r for r in json.loads(path.read_text(encoding="utf-8"))["classes"]}
    out = []
    for tt, triples in sorted(classes.items(), key=lambda kv: kv[1][0]):
        T = dict(zip(KEYS, tt))
        w, y = lp(T)
        value = sum(2 * pop(X) * w[i] for i, X in enumerate(UNIONS))
        row = {"example": list(triples[0]), "triples": len(triples), "tariffs": list(tt),
               "weights": [str(x) for x in w], "covering": [str(x) for x in y], "value": str(value)}
        if value < 12:
            pv, Z, pw = phi_lp(T)
            row["phi_zero_blocks"] = [list(z) for z in Z]
            row["phi_weights"] = [str(x) for x in pw]
            row["phi_value"] = str(sum(2 * pop(X) * pw[i] for i, X in enumerate(UNIONS)))
            if Q(row["phi_value"]) < 12:
                prev = old.get(tt, {}).get("f2_minimum_mass")
                row["f2_minimum_mass"] = prev if prev is not None else f2_minimum(T)
        out.append(row)
    path.write_text(json.dumps({"schema": "three-plane-rank-dual/1", "classes": out}, indent=1) + "\n",
                    encoding="utf-8", newline="\n")
    print("wrote", path, len(out))


if __name__ == "__main__":
    main()
