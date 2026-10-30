#!/usr/bin/env python3
"""Exact checks for the span-(m+1) lemma in every address dimension.

Produced by Nick Petalas. Apache-2.0.
Standard library only. No predecessor executable, network, Git or output file.
The written proof is PROOF.md; these checks cover its finite combinatorial
step, its 2x2 minor identity and an exact rank-one grid with controls.
"""

import itertools
import json

MAX_SUPPORT_DIMENSION = 7


def need(condition, message):
    if not condition:
        raise ValueError(message)


def edges(m, supp_u, supp_v):
    return {(i, l) for i in supp_u for l in supp_v if i != l}


def strongly_connected_components(m, arcs):
    reach = [[i == l for l in range(m)] for i in range(m)]
    for i, l in arcs:
        reach[i][l] = True
    for mid in range(m):
        for i in range(m):
            if reach[i][mid]:
                for l in range(m):
                    if reach[mid][l]:
                        reach[i][l] = True
    return {frozenset(l for l in range(m) if reach[i][l] and reach[l][i])
            for i in range(m)}


def has_robust_minor(i, supp_u, supp_v):
    return any(k != l and k != i and l != i
               for k in supp_u for l in supp_v)


def check_supports():
    """Lemma 2/4 combinatorics for every pair of nonempty supports."""
    tally = {}
    for m in range(1, MAX_SUPPORT_DIMENSION + 1):
        subsets = [frozenset(c) for r in range(1, m + 1)
                   for c in itertools.combinations(range(m), r)]
        counts = {"K>=3": 0, "K=2": 0, "K<=1": 0}
        for supp_u in subsets:
            for supp_v in subsets:
                core = supp_u & supp_v
                arcs = edges(m, supp_u, supp_v)
                components = strongly_connected_components(m, arcs)
                nontrivial = [c for c in components if len(c) > 1]
                if len(core) >= 3:
                    counts["K>=3"] += 1
                    need(all(has_robust_minor(i, supp_u, supp_v)
                             for i in range(m)),
                         "robust minor missing for |K|>=3")
                    need(nontrivial == [core], "|K|>=3 component mismatch")
                elif len(core) == 2:
                    counts["K=2"] += 1
                    need(nontrivial == [core], "|K|=2 component mismatch")
                else:
                    counts["K<=1"] += 1
                    need(not nontrivial, "|K|<=1 digraph has a cycle")
        need(sum(counts.values()) == len(subsets) ** 2, "support count")
        tally[str(m)] = counts
    return tally


def poly_mul(left, right):
    out = {}
    for a, x in left.items():
        for b, y in right.items():
            key = tuple(p + q for p, q in zip(a, b))
            out[key] = out.get(key, 0) + x * y
    return {k: v for k, v in out.items() if v}


def poly_add(left, right, sign=1):
    out = dict(left)
    for k, v in right.items():
        out[k] = out.get(k, 0) + sign * v
    return {k: v for k, v in out.items() if v}


def monomial(**powers):
    order = ("d", "t", "ui", "uk", "vi", "vl")
    return {tuple(powers.get(name, 0) for name in order): 1}


def check_minor_identity():
    """det [[d+t ui vi, t ui vl], [t uk vi, t uk vl]] == d t uk vl."""
    a = poly_add(monomial(d=1), monomial(t=1, ui=1, vi=1))
    b = monomial(t=1, ui=1, vl=1)
    c = monomial(t=1, uk=1, vi=1)
    e = monomial(t=1, uk=1, vl=1)
    det = poly_add(poly_mul(a, e), poly_mul(b, c), sign=-1)
    need(det == monomial(d=1, t=1, uk=1, vl=1), "minor identity fails")
    return "d*t*uk*vl"


def rank_at_most_one(matrix, m):
    for r0, r1 in itertools.combinations(range(m), 2):
        for c0, c1 in itertools.combinations(range(m), 2):
            if (matrix[r0][c0] * matrix[r1][c1]
                    != matrix[r0][c1] * matrix[r1][c0]):
                return False
    return True


def grid(m, entries, diagonal, scalars):
    """Rank-one D + tB with t != 0 on an exact integer grid."""
    stats = {"pairs": 0, "matrices": 0, "violations": 0}
    vectors = [v for v in itertools.product(entries, repeat=m) if any(v)]
    for u in vectors:
        for v in vectors:
            core = {i for i in range(m) if u[i] and v[i]}
            if len(core) < 3:
                continue
            stats["pairs"] += 1
            for t in scalars:
                b = [[t * u[i] * v[l] for l in range(m)] for i in range(m)]
                for d in itertools.product(diagonal, repeat=m):
                    if not any(d):
                        continue
                    stats["matrices"] += 1
                    matrix = [row[:] for row in b]
                    for i in range(m):
                        matrix[i][i] += d[i]
                    if rank_at_most_one(matrix, m):
                        stats["violations"] += 1
    need(stats["violations"] == 0, f"off-line rank-one element at m={m}")
    return stats


def control_two_core():
    """|K|=2 admits off-line rank-one elements: the hypothesis is needed."""
    u = (1, 1, 0)
    v = (1, 1, 0)
    # D = diag(2, 2, 0), t = -1 gives [[1,-1,0],[-1,1,0],[0,0,0]], rank one.
    found = []
    for t in (1, -1, 2):
        for d in itertools.product((-1, 0, 1, 2), repeat=3):
            if not any(d):
                continue
            matrix = [[t * u[i] * v[l] + (d[i] if i == l else 0)
                       for l in range(3)] for i in range(3)]
            if any(any(row) for row in matrix) and rank_at_most_one(matrix, 3):
                found.append({"t": t, "D": list(d)})
    need(found, "control: expected an off-line rank-one element for |K|=2")
    return {"u": list(u), "v": list(v), "first": found[0],
            "count": len(found)}


def control_detector():
    """The rank test rejects a rank-two matrix and accepts a rank-one one."""
    need(rank_at_most_one([[1, 2, 3], [2, 4, 6], [0, 0, 0]], 3), "rank one")
    need(not rank_at_most_one([[1, 0, 0], [0, 1, 0], [0, 0, 0]], 3), "rank two")
    return True


def main():
    result = {
        "supports": check_supports(),
        "minor_identity": check_minor_identity(),
        "grid_m3": grid(3, (-1, 0, 1, 2), (-1, 0, 1, 2), (1, -1, 2)),
        "grid_m4": grid(4, (0, 1, 2), (-1, 0, 1), (1, -1)),
        "grid_m5": grid(5, (0, 1), (-1, 0, 1), (1, -1)),
        "control_two_core": control_two_core(),
        "control_detector": control_detector(),
    }
    print(json.dumps(result, sort_keys=True, indent=1))
    print("PASS_SPAN_LEMMA_EVERY_DIMENSION")


if __name__ == "__main__":
    main()
