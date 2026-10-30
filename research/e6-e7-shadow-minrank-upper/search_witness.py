"""Optional: search for a rank-r F2 shadow N = U V^T on the E6 or E7 lines.

Not part of the registered replay; needs python-sat (CaDiCaL 1.5.3).  The
registered check is verify.py on the committed WITNESSES.json.  A fresh run
may return a different witness; verify.py accepts any valid one.

usage: search_witness.py {E6|E7} RANK OUT.json [SECONDS]
Prepared by Nick Petalas.  Apache-2.0.
"""
import json
import sys
import threading

from pysat.solvers import Cadical153

from verify import dot, e8_roots_doubled, line_set

ANCHORS = {"E6": [(2, 2, 0, 0, 0, 0, 0, 0), (0, -2, -2, 0, 0, 0, 0, 0)],
           "E7": [(2, 2, 0, 0, 0, 0, 0, 0)]}


def orthogonal_clique(lines):
    """A greedy set of pairwise orthogonal lines (fixes U on it: valid symmetry breaking)."""
    clique = []
    for i, v in enumerate(lines):
        if all(dot(v, lines[j]) == 0 for j in clique):
            clique.append(i)
    return clique


def main():
    unit, r, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    seconds = float(sys.argv[4]) if len(sys.argv) > 4 else 600.0
    anchors = ANCHORS[unit]
    lines = sorted(line_set(anchors))
    n = len(lines)
    count = [0]
    clauses = []

    def new():
        count[0] += 1
        return count[0]

    U = [[new() for _ in range(r)] for _ in range(n)]
    V = [[new() for _ in range(r)] for _ in range(n)]

    def entry(t, s, val):
        ands = []
        for i in range(r):
            a = new()
            clauses.extend([[-a, U[t][i]], [-a, V[s][i]], [a, -U[t][i], -V[s][i]]])
            ands.append(a)
        cur = ands[0]
        for lit in ands[1:]:
            y = new()
            clauses.extend([[-y, cur, lit], [-y, -cur, -lit], [y, -cur, lit], [y, cur, -lit]])
            cur = y
        clauses.append([cur] if val else [-cur])

    for t in range(n):
        for s in range(n):
            if t == s or dot(lines[t], lines[s]) == 0:
                entry(t, s, int(t == s))
    for k, t in enumerate(orthogonal_clique(lines)[:r]):
        clauses.extend([[U[t][i]] if i == k else [-U[t][i]] for i in range(r)])
    with Cadical153(bootstrap_with=clauses) as solver:
        timer = threading.Timer(seconds, solver.interrupt)
        timer.start()
        status = solver.solve_limited(expect_interrupt=True)
        timer.cancel()
        print(unit, r, {True: "SAT", False: "UNSAT", None: "UNKNOWN (time limit)"}[status])
        if status:
            model = {x for x in solver.get_model() if x > 0}
            item = {"anchors": [list(a) for a in anchors], "rank_cap": r, "lines": [list(v) for v in lines],
                    "U": [[int(x in model) for x in row] for row in U],
                    "V": [[int(x in model) for x in row] for row in V]}
            json.dump({"units": {unit: item}}, open(out, "w"), separators=(",", ":"))


if __name__ == "__main__":
    main()
