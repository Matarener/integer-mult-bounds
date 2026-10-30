#!/usr/bin/env python3
"""Local, method-independent SAT cross-check of the same relaxation (not registered;
needs python-sat). Used for the F3 length-five row, which the stdlib branching
search does not finish in reasonable time.

Encoding: one variable per unordered node pair (equal classes); transitivity
clauses; each cancellation rule as an equivalence of two pair variables; each
forbidden equality as a negative unit; and, for every equation E and every node
u in E, a one-hot mod-p counter forcing sum_{v in E} w_v [v ~ u] = 0 (mod p),
i.e. u's class has total weight zero in E. A model is exactly a partition that
survives the relaxation; UNSAT refutes the projector tuple.

Usage: sat_crosscheck.py P KMAX [--no-cancel] [--jobs N]
"""
import importlib.util
import itertools
import multiprocessing
import os
import sys
import time

from pysat.solvers import Cadical153

_spec = importlib.util.spec_from_file_location(
    "dpca_verify", os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)


def satisfiable(tup, p, cancel=True):
    k = len(tup)
    prob = V.Problem(k, p, cancellation=cancel)
    eqs = prob.equations(tup)
    n = (1 << k) + 2
    ids = {}
    top = [0]

    def pair(u, v):
        key = (min(u, v), max(u, v))
        if key not in ids:
            top[0] += 1
            ids[key] = top[0]
        return ids[key]

    def fresh():
        top[0] += 1
        return top[0]

    cl = []
    for u, v, w in itertools.combinations(range(n), 3):
        a, b, c = pair(u, v), pair(v, w), pair(u, w)
        cl += [[-a, -b, c], [-a, -c, b], [-b, -c, a]]
    for U, W, U2, W2 in prob.rules:
        x, y = pair(U, W), pair(U2, W2)
        cl += [[-x, y], [-y, x]]
    for x, y in prob.forbidden:
        cl.append([-pair(x, y)])
    for E in eqs:
        for u, wu in E:
            cur = [fresh() for _ in range(p)]
            for r in range(p):
                cl.append([cur[r]] if r == wu % p else [-cur[r]])
            for v, wv in E:
                if v == u:
                    continue
                x = pair(u, v)
                nxt = [fresh() for _ in range(p)]
                for r in range(p):
                    s = (r + wv) % p
                    cl += [[x, -cur[r], nxt[r]], [x, cur[r], -nxt[r]],
                           [-x, -cur[r], nxt[s]], [-x, cur[r], -nxt[s]]]
                cur = nxt
            cl.append([cur[0]])
    with Cadical153(bootstrap_with=cl) as solver:
        return solver.solve()


def _work(args):
    p, k, head, cancel = args
    return [(head,) + rest for rest in itertools.product(V.projectors(p), repeat=k - 1)
            if satisfiable((head,) + rest, p, cancel)]


def main(argv):
    p, kmax = int(argv[0]), int(argv[1])
    cancel = "--no-cancel" not in argv
    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 8
    E00, E11 = (1, 0, 0, 0), (0, 0, 0, 1)
    assert satisfiable((E00,) * 3 + (E11,) * 3, p), "six-call construction must be SAT"
    t0 = time.time()
    with multiprocessing.Pool(jobs) as pool:
        for k in range(1, kmax + 1):
            parts = pool.map(_work, [(p, k, h, cancel) for h in V.projectors(p)])
            surv = [t for part in parts for t in part]
            print("p=%d k=%d cancel=%s tuples=%d sat_survivors=%d seconds=%d"
                  % (p, k, cancel, len(V.projectors(p)) ** k, len(surv), time.time() - t0),
                  flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
