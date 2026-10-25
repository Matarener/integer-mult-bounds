#!/usr/bin/env python3
"""Independent GL3(F2) support-cone oracle. Python 3.12, stdlib only.

No files are written unless --output is supplied. Stdout is a short receipt.
Group elements are always serialized as literal binary-matrix row tuples.
"""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path


I = (1, 2, 4)
TARGETS = ((1, 4, 3), (2, 4, 3), I)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def key(matrix):
    return "(" + ",".join(map(str, matrix)) + ")"


def multiply(a, b):
    """Composition a*b: apply b first, then a, to column vectors."""
    return tuple(
        (b[0] if mask & 1 else 0)
        ^ (b[1] if mask & 2 else 0)
        ^ (b[2] if mask & 4 else 0)
        for mask in a
    )


def enumerate_group():
    """Construct by ordered independent COLUMNS, independently of row scans."""
    result = []
    for a in range(1, 8):
        for b in range(1, 8):
            if b == a:
                continue
            span_ab = {0, a, b, a ^ b}
            for c in range(1, 8):
                if c in span_ab:
                    continue
                columns = (a, b, c)
                rows = tuple(
                    sum(((columns[j] >> i) & 1) << j for j in range(3))
                    for i in range(3)
                )
                result.append(rows)
    require(len(result) == len(set(result)) == 168, "column enumeration count")
    return tuple(sorted(result))


def generators():
    result = {}
    for i in range(3):
        for j in range(3):
            if i != j:
                rows = list(I)
                rows[i] ^= 1 << j
                result[f"g{i}{j}"] = tuple(rows)
    return result


def distances(group, gens):
    seen = {I: 0}
    word = {I: ()}
    pending = deque([I])
    while pending:
        h = pending.popleft()
        for name, g in gens.items():
            nxt = multiply(g, h)
            if nxt not in seen:
                seen[nxt] = seen[h] + 1
                word[nxt] = word[h] + (name,)
                pending.append(nxt)
    require(set(seen) == set(group), "generators do not reach all column matrices")
    for h in group:
        product = I
        for name in word[h]:
            product = multiply(gens[name], product)
        require(product == h and len(word[h]) == seen[h], "word certificate")
        for g in gens.values():
            require(abs(seen[multiply(g, h)] - seen[h]) <= 1, "BFS certificate")
    return seen, word


def rank_one_idempotents():
    result = []
    for u in range(1, 8):
        for v in range(1, 8):
            if (u & v).bit_count() % 2:
                rows = tuple(v if (u >> i) & 1 else 0 for i in range(3))
                require(multiply(rows, rows) == rows, "N squared")
                result.append(rows)
    require(len(result) == len(set(result)) == 28, "idempotent count")
    return tuple(sorted(result))


def toggle(cell, value):
    if value in cell:
        cell.remove(value)
    else:
        cell.add(value)


def factor(g, n):
    """3-by-3 matrix over F2[G], coefficient cells are exact parity sets."""
    result = [[set() for _ in range(3)] for _ in range(3)]
    for r in range(3):
        for c in range(3):
            if r == c:
                toggle(result[r][c], I)
            if (n[r] >> c) & 1:
                toggle(result[r][c], I)
                toggle(result[r][c], g)
    return result


def algebra_identity():
    return [[{I} if r == c else set() for c in range(3)] for r in range(3)]


def algebra_multiply(a, b):
    result = [[set() for _ in range(3)] for _ in range(3)]
    for r in range(3):
        for c in range(3):
            for k in range(3):
                for x in a[r][k]:
                    for y in b[k][c]:
                        toggle(result[r][c], multiply(x, y))
    return result


def module_action(a, vector):
    result = [set() for _ in range(3)]
    for r in range(3):
        for c in range(3):
            for x in a[r][c]:
                for y in vector[c]:
                    toggle(result[r], multiply(x, y))
    return result


def serialize_algebra(a):
    return [[sorted(map(key, cell)) for cell in row] for row in a]


def diag_algebra(targets):
    return [[{targets[r]} if r == c else set() for c in range(3)] for r in range(3)]


def check_factor_involutions(group, gens, ns):
    """Both symbolic products and all 504 basis inputs, for every factor."""
    ident = algebra_identity()
    factors = basis_checks = 0
    for g in gens.values():
        for n in ns:
            f = factor(g, n)
            require(algebra_multiply(f, f) == ident, "factor-square failed")
            factors += 1
            for c in range(3):
                for h in group:
                    basis = [set(), set(), set()]
                    basis[c].add(h)
                    require(module_action(f, module_action(f, basis)) == basis,
                            "regular-module involution failed")
                    basis_checks += 1
    return {"factors": factors, "regular_module_dimension": 504,
            "basis_inputs_checked": basis_checks,
            "symbolic_squares": "all identity", "basis_actions": "all identity"}


def cones(n, balls):
    return {
        (t, c): balls[t] & {multiply(x, TARGETS[c]) for x in balls[n - t]}
        for t in range(n + 1) for c in range(3)
    }


def cone_rows(n, cone):
    return [
        {"length": n, "cut": t, "row": r, "column": c,
         "target": key(TARGETS[c]),
         "allowed_support": {key(h): True for h in sorted(cone[t, c])}}
        for t in range(n + 1) for r in range(3) for c in range(3)
    ]


def cut_edges(n, cone, gens):
    """Group-level paths only: a stay or a left generator step at each cut.

    These are an over-approximation of possible algebra coefficient transitions;
    register mixing and parity cancellation are deliberately not inferred.
    """
    labels = {"stay": I, **gens}
    return [
        [n, t, c, key(h), name, key(multiply(g, h))]
        for t in range(n) for c in range(3)
        for h in sorted(cone[t, c]) for name, g in sorted(labels.items())
        if multiply(g, h) in cone[t + 1, c]
    ]


def execute_word(word, gs):
    prefix = [algebra_identity()]
    for name, n in word:
        prefix.append(algebra_multiply(factor(gs[name], n), prefix[-1]))
    return prefix


def diagnose_word(word, gs, balls, label):
    prefixes = execute_word(word, gs)
    endpoint = prefixes[-1]
    require(all(not endpoint[r][c] for r in range(3) for c in range(3) if r != c),
            "example is not diagonal")
    require(all(len(endpoint[c][c]) == 1 for c in range(3)), "example diagonal terms")
    targets = tuple(next(iter(endpoint[c][c])) for c in range(3))
    n = len(word)
    checks = []
    for t, prefix in enumerate(prefixes):
        right = [balls[t] & {multiply(x, target) for x in balls[n - t]}
                 for target in targets]
        for r in range(3):
            for c in range(3):
                require(prefix[r][c] <= right[c], "positive word escaped right cone")
                checks.append({"cut": t, "row": r, "column": c,
                               "actual": sorted(map(key, prefix[r][c])),
                               "allowed": sorted(map(key, right[c]))})
    # Check endpoint on every basis in all three registers, including dirty inputs.
    basis_checks = 0
    for input_register in range(3):
        for h in balls[8]:
            vector = [set(), set(), set()]
            vector[input_register].add(h)
            actual = vector
            for name, projector in word:
                actual = module_action(factor(gs[name], projector), actual)
            expected = [set(), set(), set()]
            expected[input_register].add(multiply(targets[input_register], h))
            require(actual == expected, "positive full-module endpoint failed")
            basis_checks += 1
    return {"label": label, "length": n,
            "word": [{"generator": name, "N_rows": list(n)} for name, n in word],
            "endpoint_targets": list(map(key, targets)),
            "prefix_algebra": [serialize_algebra(p) for p in prefixes],
            "support_checks": checks, "full_regular_basis_checks": basis_checks,
            "dirty_register_restoration": "verified by exact full algebra and 504 basis inputs"}


def make_result():
    group = enumerate_group()
    gs = generators()
    ns = rank_one_idempotents()
    distance, words = distances(group, gs)
    diameter = max(distance.values())
    radius_limit = max(8, sum(distance[target] for target in TARGETS))
    balls = [{h for h in group if distance[h] <= t} for t in range(radius_limit + 1)]
    for a in group:
        for b in group:
            require(multiply(a, b) in distance, "closure failed")
    for g in gs.values():
        require(g != I and multiply(g, g) == I, "generator involution")
    require(all(t in distance for t in TARGETS), "target membership")

    bfs_edges = [
        [distance[h], key(h), name, key(multiply(g, h))]
        for h in group for name, g in sorted(gs.items())
        if distance[multiply(g, h)] == distance[h] + 1
    ]
    ball_boundary = [
        {"radius": t, "directed_outward_edge_count": len(edges),
         "directed_outward_edges_sha256": digest(edges)}
        for t in range(diameter + 1)
        for edges in [[
            [key(h), name, key(multiply(g, h))]
            for h in sorted(balls[t]) for name, g in sorted(gs.items())
            if multiply(g, h) not in balls[t]
        ]]
    ]
    support = []
    cone_data = []
    for n in (7, 8):
        cone = cones(n, balls)
        rows = cone_rows(n, cone)
        edges = cut_edges(n, cone, gs)
        support.extend(rows)
        cone_data.append({
            "length": n,
            "counts_by_cut_and_column": [[len(cone[t, c]) for c in range(3)]
                                         for t in range(n + 1)],
            "support_row_count": len(rows), "support_rows_sha256": digest(rows),
            "cut_frontier_edge_count": len(edges),
            "cut_frontier_edges_sha256": digest(edges),
            "cut_frontier_edges": edges,
        })

    e0 = (1, 0, 0)
    e1 = (0, 2, 0)
    e2 = (0, 0, 4)
    noncommuting_word = [("g01", e0), ("g12", e0)]
    positive = diagnose_word(noncommuting_word, gs, balls, "noncommuting two-call")
    t = multiply(gs["g12"], gs["g01"])
    require(t == (3, 6, 4), "noncommuting target mismatch")
    correct = balls[1] & {multiply(x, t) for x in balls[1]}
    incorrect = balls[1] & {multiply(t, x) for x in balls[1]}
    require(gs["g01"] in correct and gs["g01"] not in incorrect,
            "left-translation defect witness missing")
    require(positive["prefix_algebra"][1][0][0] == [key(gs["g01"])],
            "positive prefix support")
    positive["right_translation_witness"] = {
        "target": key(t), "actual_cut1_support": [key(gs["g01"])],
        "correct_B1_intersect_B1_times_T": sorted(map(key, correct)),
        "incorrect_B1_intersect_T_times_B1": sorted(map(key, incorrect)),
        "incorrect_omits_actual_support": True,
    }
    # Same legal core, with involutory calls on dirty registers; both restore.
    padded = [("g20", e1)] + noncommuting_word + [("g20", e1),
              ("g02", e2), ("g02", e2)]
    positive_padded = diagnose_word(padded, gs, balls, "dirty-register restoration six-call")
    require(positive_padded["endpoint_targets"] == positive["endpoint_targets"],
            "padded endpoint differs")
    # A mixed-register idempotent produces off-diagonal I+g terms at the prefix.
    mixed = (3, 0, 0)  # u=e0, v=e0+e1; v*u=1.
    mixed_word = [("g10", mixed), ("g10", mixed)]
    positive_mixed = diagnose_word(mixed_word, gs, balls, "mixed-register cancellation two-call")
    require(positive_mixed["endpoint_targets"] == list(map(key, (I, I, I))),
            "mixed example fails restoration")

    fixed_target_word = []
    for c, target in enumerate(TARGETS):
        projection = tuple((1 << c) if r == c else 0 for r in range(3))
        fixed_target_word.extend((name, projection) for name in words[target])
    fixed_example = diagnose_word(fixed_target_word, gs, balls, "fixed target diagonal attaining word")
    require(fixed_example["endpoint_targets"] == list(map(key, TARGETS)),
            "fixed-target positive endpoint mismatch")

    result = {
        "schema": "independent-gl3-f2-support-cones-v1",
        "independence": {
            "implementation": "from task contract only; no predecessor source, checker, or model read",
            "group_enumeration": "ordered independent columns in F2^3",
            "dependencies": "Python 3.12 standard library only",
            "serialization": "canonical JSON: sort_keys; separators comma/colon; ASCII",
            "matrix_keys": "literal (row0,row1,row2), with bits j selecting input coordinate j",
        },
        "conventions": {
            "action": "column vectors; multiplication a*b applies b first",
            "word_order": "time order; each new factor multiplies on the left",
            "factor": "I+(g+1)N over M3(F2[G]); rank-one binary idempotent N",
            "cone": "B_t intersection (B_(n-t)*T_c), RIGHT translate",
            "support_scope": "exact sets defined by the cone formula, necessary constraints only",
            "row_scope": "same universal group cone for every matrix row r",
            "cut_frontier_edges": "[n,t,column,h,step,h_next], h_next=step*h; stay included; rows not duplicated",
            "bfs_frontier_edges": "[distance(h),h,generator,generator*h] with distance increasing by one",
            "edge_order": "ascending n,t,column,literal row tuples,step name; BFS ascending row tuples,step name",
            "no_claims": ["free-mixing normalization", "minimal attaining length", "SAT", "proof replay", "Lean", "native admission"],
        },
        "group_order": len(group), "diameter": diameter,
        "generators": {name: list(g) for name, g in gs.items()},
        "group": {key(h): {"distance": distance[h], "shortest_word": list(words[h])}
                  for h in group},
        "distance_histogram": [sum(d == t for d in distance.values())
                               for t in range(diameter + 1)],
        "ball_counts": [len(b) for b in balls],
        "balls": [{key(h): True for h in sorted(b)} for b in balls],
        "targets": list(map(key, TARGETS)),
        "rank_one_idempotents": [list(n) for n in ns],
        "factor_involutions": check_factor_involutions(group, gs, ns),
        "bfs_frontier_edge_count": len(bfs_edges),
        "bfs_frontier_edges_sha256": digest(bfs_edges),
        "bfs_frontier_edges": bfs_edges,
        "ball_boundary_edges": ball_boundary,
        "support_rows": support,
        "support_rows_sha256": digest(support),
        "cone_diagnostics": cone_data,
        "positive_examples": [positive, positive_padded, positive_mixed, fixed_example],
        "RESULT": "PASS: exact universal right-translate support-cone oracle; no model-normalization claim",
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write full canonical JSON here")
    args = parser.parse_args()
    result = make_result()
    serialized = canonical(result) + "\n"
    if args.output is not None:
        args.output.write_text(serialized, encoding="ascii")
    receipt = {
        "RESULT": result["RESULT"], "group_order": result["group_order"],
        "ball_counts": result["ball_counts"],
        "support_rows": len(result["support_rows"]),
        "support_rows_sha256": result["support_rows_sha256"],
        "bfs_frontier_edge_count": result["bfs_frontier_edge_count"],
        "bfs_frontier_edges_sha256": result["bfs_frontier_edges_sha256"],
        "cut_frontier_edge_counts": {str(row["length"]): row["cut_frontier_edge_count"]
                                     for row in result["cone_diagnostics"]},
        "canonical_json_sha256": hashlib.sha256(serialized.encode("ascii")).hexdigest(),
    }
    print(canonical(receipt))


if __name__ == "__main__":
    main()
