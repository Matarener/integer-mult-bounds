#!/usr/bin/env python3
"""Find exact BIT words with two early helper queries per port."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import time

import z3


def xor(xs):
    xs = list(xs)
    if not xs:
        return z3.BoolVal(False)
    out = xs[0]
    for x in xs[1:]:
        out = z3.Xor(out, x)
    return out


def matrix_vector(rows, x):
    return [xor(z3.And(v, b) for v, b in zip(row, x)) for row in rows]


def parity_dot(row, vector):
    return (row & vector).bit_count() & 1


def apply(rows, vector):
    return sum(parity_dot(row, vector) << j for j, row in enumerate(rows))


def rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            j = v.bit_length() - 1
            if j in pivots:
                v ^= pivots[j]
            else:
                pivots[j] = v
                break
    return len(pivots)


def literal_product_check(rows, supports):
    """Multiply the native stage matrices in the exact group ring."""
    n = len(rows[0])
    state = [[{0} if a == b else set() for b in range(n)] for a in range(n)]
    for i, (matrix, support) in enumerate(zip(rows, supports)):
        stage = [[set() for _ in range(n)] for _ in range(n)]
        for a in range(n):
            d = (1 << (i + 1)) if a in support else 0
            stage[a][a].add(d)
            for b in range(n):
                if matrix[a] >> b & 1:
                    stage[a][b].add(d | 1)
        out = [[set() for _ in range(n)] for _ in range(n)]
        for a, b, c in itertools.product(range(n), repeat=3):
            for left in stage[a][b]:
                for right in state[b][c]:
                    if left & right & 1:
                        continue
                    term = left ^ right
                    if term in out[a][c]:
                        out[a][c].remove(term)
                    else:
                        out[a][c].add(term)
        state = out
    for a, b in itertools.product(range(n), repeat=2):
        d = sum((1 << (i + 1)) for i, support in enumerate(supports) if a in support)
        expected = {d, d | 1} if a == b else set()
        if state[a][b] != expected:
            raise ValueError("The literal native-stage product fails")


def make_case(name, edges, order, timeout_ms):
    f = len(order)
    position = {v: i for i, v in enumerate(order)}
    edges = sorted(tuple(sorted(edge)) for edge in edges)
    fields = [{"name": f"e{a}{b}", "vertices": [a, b]} for a, b in edges]
    for v in order:
        degree = sum(v in e for e in edges)
        if degree > 4:
            raise ValueError("A call has more than four fields")
        for j in range(4 - degree):
            fields.append({"name": f"a{v}_{j}", "vertices": [v]})
    n = len(fields)
    supports = [tuple(j for j, fld in enumerate(fields) if v in fld["vertices"])
                for v in order]
    if any(len(s) != 4 for s in supports):
        raise ValueError("A call does not have rank four")
    memberships = [[int(j in support) for j in range(n)] for support in supports]
    prefix = [[sum(memberships[k][j] << k for k in range(i)) for j in range(n)]
              for i in range(f)]
    false = z3.BoolVal(False)
    matrices = [[[false for _ in range(n)] for _ in range(n)] for _ in range(f)]
    variables = []
    for b, field in enumerate(fields):
        sites = sorted(position[v] for v in field["vertices"])
        if len(sites) == 1:
            matrices[sites[0]][b][b] = z3.BoolVal(True)
        elif len(sites) == 2:
            i, j = sites
            for a in range(n):
                if prefix[i][a] ^ prefix[i][b] == prefix[j][a] ^ prefix[j][b]:
                    v = z3.Bool(f"x_{b}_{a}")
                    variables.append(v)
                    matrices[i][a][b] = v
                    matrices[j][a][b] = z3.Not(v) if a == b else v
        else:
            raise ValueError("Only one-call and two-call fields are in this model")
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    chain_vars = []
    for i, support in enumerate(supports):
        u = [z3.Bool(f"u_{i}_{j}") for j in range(4)]
        w = [z3.Bool(f"w_{i}_{j}") for j in range(4)]
        solver.add(z3.Or(*u))
        local_rows = [[matrices[i][a][b] for b in support] for a in range(n)]
        ru = matrix_vector(local_rows, u)
        rw = matrix_vector(local_rows, w)
        for a in range(n):
            solver.add(z3.Not(ru[a]))
            solver.add(rw[a] == (u[support.index(a)] if a in support else false))
        chain_vars.append((u, w))
    started = time.monotonic()
    status = solver.check()
    elapsed = time.monotonic() - started
    result = {"name": name, "order": order, "edges": edges, "fields": fields,
              "supports": supports, "calls": f, "active_fields": n,
              "private_fields": sum(len(x["vertices"]) == 1 for x in fields),
              "edge_fields": len(edges), "status": str(status),
              "solver_seconds": round(elapsed, 6), "boolean_code_variables": len(variables),
              "all_active_outputs_have_Q": True,
              "formal_group_bits": f, "native_full_calls_per_port": f,
              "unused_helpers_per_full": 217,
              "paid_profile": {"1": 1323*f, "2": 1342*f, "3": 79*f,
                               "4": 44*f, "5": 102*f, "6": 11*f, "7": 19*f},
              "target_profile": {"8": 217*f + 111*sum(len(x["vertices"]) == 1 for x in fields),
                                 "15": 111*len(edges)},
              "rank_surplus": 217*f*8 +111*(4*f*7+n)-5129*f}
    if status == z3.unknown:
        result["reason_unknown"] = solver.reason_unknown()
    if status != z3.sat:
        return result
    model = solver.model()
    evaluate = lambda v: z3.is_true(model.eval(v, model_completion=True))
    rows = [[sum(evaluate(v) << b for b, v in enumerate(row)) for row in mat]
            for mat in matrices]
    chains = []
    for i, ((u, w), support) in enumerate(zip(chain_vars, supports)):
        ub = sum(evaluate(v) << support[j] for j, v in enumerate(u))
        wb = sum(evaluate(v) << support[j] for j, v in enumerate(w))
        if ub == 0 or apply(rows[i], ub) or apply(rows[i], wb) != ub:
            raise ValueError("The model has a bad native main chain")
        basis = [ub, wb]
        for b in support:
            if rank(basis + [1 << b]) > len(basis):
                basis.append(1 << b)
        if len(basis) != 4:
            raise ValueError("The main chain has no basis completion")
        # The first two columns are the native main chain. The last two are
        # early helper columns. The early q update changes only those columns.
        early_columns = [apply(rows[i], basis[j]) ^ basis[j] for j in (2, 3)]
        chains.append({"u": ub, "w": wb, "basis": basis,
                       "early_q_column_updates": early_columns})
    for a, b in itertools.product(range(n), repeat=2):
        coeffs = {}
        for i in range(f):
            if rows[i][a] >> b & 1:
                signature = prefix[i][a] ^ prefix[i][b]
                coeffs[signature] = coeffs.get(signature, 0) ^ 1
        coeffs = {key: value for key, value in coeffs.items() if value}
        if coeffs != ({0: 1} if a == b else {}):
            raise ValueError("The model fails the exact formal endpoint")
    literal_product_check(rows, supports)
    result.update({"R_rows": rows, "native_chains": chains,
                   "literal_stage_product_check": "PASS",
                   "exact_endpoint_check": "PASS",
                   "all_native_chain_checks": "PASS",
                   "witness_scope": "Abstract native-call word; fixed cover-route tariff is not certified"})
    return result


def distinct_orders(edges, count):
    # These orders are all supplied to the solver. The receipt has no
    # isomorphism claim about a skipped order.
    return itertools.permutations(range(count))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--all-orders", action="store_true")
    parser.add_argument("--suite", choices=("simple", "parallel", "control"), default="simple")
    args = parser.parse_args()
    k4 = list(itertools.combinations(range(4), 2))
    suites = {
        "simple": [("K4-minus-01", [e for e in k4 if e != (0, 1)], 4), ("K4", k4, 4)],
        "parallel": [
            ("two-full-double-edge", [(0, 1)]*2, 2),
            ("three-full-double-path", [(0, 1)]*2 + [(1, 2)]*2, 3),
            ("four-full-double-single-double", [(0, 1)]*2 + [(1, 2)] + [(2, 3)]*2, 4),
        ],
        "control": [("two-full-complement-control", [(0, 1)]*4, 2)],
    }
    results = []
    for name, edges, count in suites[args.suite]:
        orders = distinct_orders(edges, count) if args.all_orders else [tuple(range(count))]
        for order in orders:
            result = make_case(name, edges, list(order), args.timeout_ms)
            results.append(result)
            print(json.dumps({k: result[k] for k in ("name", "order", "status", "solver_seconds", "rank_surplus")}), flush=True)
            args.out.write_text(json.dumps({"model": "Coordinate rank-four D supports; two early q helper columns; all Q outputs",
                                            "results": results}, indent=2) + "\n")
            if result["status"] == "sat":
                break


if __name__ == "__main__":
    main()
