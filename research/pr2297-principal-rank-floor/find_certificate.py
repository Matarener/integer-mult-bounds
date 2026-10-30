#!/usr/bin/env python3
"""Provenance helper (NOT part of verification): how CERTIFICATE.json was found.

Solves the principal-rank LP relaxation's dual over a finite family of group sets
(all singletons and pairs, the full set, 3000 seeded random sets) against every
pair of flats, then rounds the weights down to integers over 10**6 and shrinks by
2 ppm.  verify.py re-checks the result exactly; any feasible certificate with
value > 553 proves the same floor.  Requires numpy 2.5.4 and scipy 1.18.1 (HiGHS);
other versions may return a different optimal vertex.  Usage:
    python3 research/pr2297-principal-rank-floor/find_certificate.py OUT.json
Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5).  Apache-2.0.
"""
import itertools
import json
import random
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

DEN = 10 ** 6


def main(out):
    labels, groups = V.sources()
    spaces, gm = V.cover(labels, groups)
    d = [len(s) for s in spaces]
    n = len(d)
    flats = sorted(V.flats_closure(gm), key=lambda F: (V.dim(F), F))
    pmap = V.closure_sets(flats, gm)
    P = [sum(1 << g for g in pmap[F]) for F in flats]
    rho = [[V.rho_elimination(L, R) for R in flats] for L in flats]
    m = len(P)
    rng = random.Random(20261019)
    cols = {1 << g for g in range(n)} | {(1 << a) | (1 << b) for a, b in itertools.combinations(range(n), 2)}
    cols |= {sum(1 << g for g in rng.sample(range(n), rng.randint(3, 20))) for _ in range(3000)}
    cols.add((1 << n) - 1)
    cols = sorted(cols)
    pairs = [(i, j) for i in range(m) for j in range(i, m)]
    hit = np.array([[(P[i] & S) != 0 for S in cols] for i in range(m)])
    A = np.array([hit[i] & hit[j] for i, j in pairs], dtype=float)
    b = np.array([rho[i][j] for i, j in pairs], dtype=float)
    c = -np.array([sum(d[g] for g in range(n) if S >> g & 1) for S in cols], dtype=float)
    res = linprog(c, A_ub=A, b_ub=b, bounds=(0, None), method='highs')
    assert res.status == 0, res.message
    print('LP value', -res.fun)
    rows = [(S, int(v * DEN * (1 - 2e-6))) for S, v in zip(cols, res.x) if v > 1e-9]
    rows = [(S, w) for S, w in rows if w > 0]
    data = {'denominator': DEN, 'sets': [{'groups': [g for g in range(n) if S >> g & 1], 'weight_numerator': w}
                                         for S, w in sorted(rows, key=lambda x: (bin(x[0]).count('1'), x[0]))]}
    Path(out).write_text(json.dumps(data, indent=1))
    print('wrote', out, len(rows), 'sets')


if __name__ == '__main__':
    main(sys.argv[1])
