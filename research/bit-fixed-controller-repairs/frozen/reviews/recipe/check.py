#!/usr/bin/env python3
"""Independent fixed-recipe repair certificate. Apache-2.0.

Prepared with substantial OpenAI Codex assistance. No search is executed.
The all-parameter proof is in PROOF.md; this checker covers B=1,...,12.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

RECIPE_SHA = "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8"
HISTORICAL_SHA = "ef97f43313ccffb7a8ea5965d37b37452b70cf4ccfbafe81e9e92e46d0f1a14a"
PIN = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [1 << i for i in range(n)]


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            i = row.bit_length() - 1
            if i in pivots:
                row ^= pivots[i]
            else:
                pivots[i] = row
                break
    return len(pivots)


def dot(a, b):
    return (a & b).bit_count() & 1


def column(rows, j):
    return sum(((r >> j) & 1) << i for i, r in enumerate(rows))


def outer(u, v, n):
    return [v if (u >> i) & 1 else 0 for i in range(n)]


def add(a, b):
    need(len(a) == len(b), "matrix dimensions")
    return [x ^ y for x, y in zip(a, b)]


def multiply(a, b):
    answer = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length() - 1]
            row ^= bit
        answer.append(value)
    return answer


def inverse(a):
    n = len(a)
    z = [r | (1 << (n + i)) for i, r in enumerate(a)]
    for j in range(n):
        positions = [i for i in range(j, n) if (z[i] >> j) & 1]
        need(bool(positions), "scalar conjugator singular")
        p = positions[0]
        z[j], z[p] = z[p], z[j]
        for i in range(n):
            if i != j and (z[i] >> j) & 1:
                z[i] ^= z[j]
    return [r >> n for r in z]


def transpose(rows, n):
    return [column(rows, j) for j in range(n)]


def trace(rows):
    return sum((row >> i) & 1 for i, row in enumerate(rows)) & 1


def extract_recipe(raw):
    tree = ast.parse(raw)
    matches = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "recipe"
    ]
    need(len(matches) == 1, "recipe definition multiplicity")
    function = matches[0]
    need(not function.decorator_list, "decorated recipe excluded")
    environment = {"__builtins__": {"dict": dict, "range": range, "reversed": reversed}}
    exec(compile(ast.Module(body=[function], type_ignores=[]),
                 "<authenticated recipe function>", "exec",
                 dont_inherit=True, optimize=0), environment)
    return environment["recipe"]


def bound_bytes(path, expected, message):
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected, message)
    return raw


def evaluate(events, banks):
    """Dual-number matrices as separate constant and epsilon bit rows."""
    n = 2 * banks
    constant, epsilon = identity(n), [0] * n
    for event in events:
        kind = event["kind"]
        if kind == "local":
            i = 2 * event["pair"]
            need(0 <= i < n - 1, "local bank range")
            if event["reverse"]:
                # x <- (1+epsilon)x+y, with y unchanged.
                epsilon[i] ^= constant[i] ^ epsilon[i + 1]
                constant[i] ^= constant[i + 1]
            else:
                # y <- x+(1+epsilon)y, with x unchanged.
                epsilon[i + 1] ^= epsilon[i] ^ constant[i + 1]
                constant[i + 1] ^= constant[i]
        elif kind == "bridge":
            d, s = 2 * event["dst"], 2 * event["src"]
            need(d != s and 0 <= d < n and 0 <= s < n, "bridge bank range")
            need(event["coefficient"] in (-1, 1), "bridge coefficient")
            constant[d] ^= constant[s]
            epsilon[d] ^= epsilon[s]
            constant[s + 1] ^= constant[d + 1]
            epsilon[s + 1] ^= epsilon[d + 1]
        elif kind == "exchange":
            for i in range(0, n, 2):
                constant[i], constant[i + 1] = constant[i + 1], constant[i]
                epsilon[i], epsilon[i + 1] = epsilon[i + 1], epsilon[i]
        else:
            raise ValueError("unknown recipe event")
    return constant, epsilon


def grouped(rows, banks):
    permutation = list(range(0, 2 * banks, 2)) + list(range(1, 2 * banks, 2))
    return [
        sum(((rows[i] >> j) & 1) << k for k, j in enumerate(permutation))
        for i in permutation
    ]


def ungrouped(rows, banks):
    permutation = list(range(0, 2 * banks, 2)) + list(range(1, 2 * banks, 2))
    answer = [0] * (2 * banks)
    for i, original_i in enumerate(permutation):
        answer[original_i] = sum(
            ((rows[i] >> j) & 1) << original_j
            for j, original_j in enumerate(permutation)
        )
    return answer


def closed_form(banks):
    b = banks
    c = [sum(((b - max(i, j)) & 1) << j for j in range(b)) for i in range(b)]
    d = [(1 << i) | ((1 << (i - 1)) if i else 0) for i in range(b)]
    e = [1] + [(1 << i) - 1 for i in range(1, b)]
    a = [row << b for row in c] + [d[i] | (e[i] << b) for i in range(b)]
    m = add(a, identity(2 * b))
    return a, m, c, d, e


def projector_conjugator(u, v, n):
    need(u != 0 and v != 0 and dot(v, u) == 1, "repair is not a rank-one idempotent")
    pivot = (v & -v).bit_length() - 1
    columns = [u]
    for j in range(n):
        if j != pivot:
            columns.append((1 << j) ^ ((1 << pivot) if (v >> j) & 1 else 0))
    scalar = transpose(columns, n)
    scalar_inverse = inverse(scalar)
    need(scalar_inverse[0] == v, "conjugator first dual")
    paid = [1] + [0] * (n - 1)
    p = outer(u, v, n)
    need(multiply(multiply(scalar, paid), scalar_inverse) == p,
         "scalar conjugation projector")
    need(multiply(p, p) == p and rank(p) == 1 and trace(p) == 1,
         "projector identities")
    return scalar, scalar_inverse


def repair_projectors(m, banks):
    n, y0 = 2 * banks, banks
    result = []
    if banks & 1:
        for j in range(n):
            if j != y0:
                result.append((column(m, j), 1 << j))
        result += [(column(m, y0) ^ (1 << y0), 1 << y0),
                   (1 << y0, 1 << y0)]
    else:
        for j in range(banks):
            result.append((column(m, j), (1 << j) ^ ((1 << y0) if j & 1 else 0)))
        for j in range(banks + 1, n):
            result.append((column(m, j), 1 << j))
    return result


def validate_repair(m, projectors):
    n = len(m)
    total = [0] * n
    records = []
    for u, v in projectors:
        scalar, scalar_inverse = projector_conjugator(u, v, n)
        total = add(total, outer(u, v, n))
        records.append({"u_bits": u, "v_bits": v,
                        "scalar_rows": scalar, "scalar_inverse_rows": scalar_inverse})
    need(total == m, "repair coefficient endpoint")
    return records


def tensor(rows, n_block):
    """Kronecker product in bank-major order, bit-packed binary matrices."""
    width = len(n_block)
    answer = []
    for row in rows:
        for block_row in n_block:
            answer.append(sum(block_row << (j * width)
                              for j in range(len(rows)) if (row >> j) & 1))
    return answer


def instantiated_endpoint(a, m, projectors, base_n, spectators,
                          wrong_first_spectator_target=False):
    """Exact arbitrary-input matrix replay, including dirty identity spectators."""
    n, w = len(a), len(base_n)
    need(multiply(base_n, base_n) == identity(w), "N is not an involution")
    epsilon = add(base_n, identity(w))
    need(any(epsilon), "N identity representation excluded from obstruction")
    r = n + spectators
    enlarged_a = a[:] + [0] * spectators
    enlarged_m = m[:] + [0] * spectators
    endpoint = add(identity(r * w), tensor(enlarged_a, epsilon))
    for u, v in projectors:
        event = add(identity(r * w), tensor(outer(u, v, r), epsilon))
        endpoint = multiply(event, endpoint)
    target = tensor(identity(n) + [0] * spectators, base_n)
    for i in range(n * w, r * w):
        target[i] = 1 << i
    if wrong_first_spectator_target:
        need(spectators > 0, "spectator mutation needs a spectator")
        for i in range(w):
            target[n * w + i] = base_n[i] << (n * w)
    need(endpoint[n * w:] == target[n * w:],
         "literal dirty spectator restoration")
    need(endpoint == target, "instantiated full dirty-input endpoint")
    need(rank(tensor(enlarged_m, epsilon)) == rank(enlarged_m) * rank(epsilon),
         "instantiated tensor rank")
    return {"ports_per_bank": w, "spectators": spectators, "N_rows": base_n,
            "all_input_columns": r * w, "epsilon_rank": rank(epsilon),
            "defect_rank": rank(enlarged_m) * rank(epsilon)}


def reject(name, operation, expected):
    try:
        operation()
    except ValueError as error:
        need(str(error) == expected, "wrong rejection for " + name)
        return {"name": name, "rejection": str(error)}
    raise ValueError("negative control accepted: " + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe-source", type=Path, required=True)
    parser.add_argument("--historical-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    recipe_raw = bound_bytes(args.recipe_source, RECIPE_SHA, "recipe source hash")
    historical_raw = bound_bytes(args.historical_receipt, HISTORICAL_SHA, "historical receipt hash")
    recipe = extract_recipe(recipe_raw)
    historical = json.loads(historical_raw)
    need(historical["scientific_pin"] == PIN and historical["source_recipe_sha256"] == RECIPE_SHA,
         "historical source binding")
    cases = []
    for b in range(1, 13):
        n = 2 * b
        events = recipe(b)
        constant, epsilon = evaluate(events, b)
        a, m, c, d, e = closed_form(b)
        need(constant == identity(n), "recipe constant endpoint")
        need(grouped(epsilon, b) == a, "recipe closed-form coefficient")
        schur = add(add(e, identity(b)), multiply(d, c))
        need(schur == [c[0]] + identity(b)[1:], "Schur row formula")
        expected_rank = n if b & 1 else n - 1
        expected_count = n + 1 if b & 1 else n - 1
        need(rank(a) == n and rank(m) == expected_rank and trace(m) == 1,
             "rank and trace theorem")
        if not b & 1:
            kernel = (1 << b) | sum(1 << j for j in range(1, b, 2))
            need(all(dot(row, kernel) == 0 for row in m), "even kernel formula")
        else:
            kernel = None
        projectors = repair_projectors(m, b)
        repairs = validate_repair(m, projectors)
        need(len(projectors) == expected_count, "attaining repair count")
        need(len(projectors) >= rank(m) and len(projectors) & 1 == trace(m),
             "lower bound match")
        instantiations = []
        if b <= 8:
            for base_n in ([2, 1], [3, 2], [3, 2, 12, 8]):
                for spectators in (0, 1, 3):
                    instantiations.append(instantiated_endpoint(a, m, projectors, base_n, spectators))
        if b <= 6:
            old = historical["cases"][b - 1]
            raw_n_entries = [
                [(((constant[i] >> j) & 1) ^ ((epsilon[i] >> j) & 1))
                 | (((epsilon[i] >> j) & 1) << 1) for j in range(n)]
                for i in range(n)
            ]
            old_a = [[(epsilon[i] >> j) & 1 for j in range(n)] for i in range(n)]
            old_m = [[old_a[i][j] ^ int(i == j) for j in range(n)] for i in range(n)]
            recovered = {"B": b, "events": events, "raw_endpoint_ring_entries": raw_n_entries,
                         "epsilon_matrix_A": old_a, "relative_to_common_N_defect_M": old_m,
                         "rank_A": n, "rank_defect_M": expected_rank, "trace_defect": 1}
            need(recovered == old, "complete historical case replay")
        cases.append({"B": b, "events": events, "constant_rows": constant,
                      "epsilon_A_grouped_rows": a, "defect_M_grouped_rows": m,
                      "C_rows": c, "D_rows": d, "E_rows": e, "schur_rows": schur,
                      "rank_A": n, "rank_M": expected_rank, "trace_M": 1,
                      "even_kernel_bits": kernel, "minimum_repair_calls": expected_count,
                      "repair_projectors": repairs, "instantiations": instantiations})

    b = 4
    a, m, _, _, _ = closed_form(b)
    events = recipe(b)
    projectors = repair_projectors(m, b)
    controls = []
    bad = [dict(event) for event in events]
    bad[0]["reverse"] = True
    controls.append(reject("reverse initial local call",
                          lambda: need(evaluate(bad, b) == (identity(8), ungrouped(a, b)),
                                       "changed word endpoint"),
                          "changed word endpoint"))
    bridge_index = next(i for i, event in enumerate(events) if event["kind"] == "bridge")
    bad_bridge = events[:bridge_index] + events[bridge_index + 1:]
    controls.append(reject("omit first bridge",
                          lambda: need(evaluate(bad_bridge, b) == (identity(8), ungrouped(a, b)),
                                       "changed word endpoint"),
                          "changed word endpoint"))
    controls.append(reject("omit terminal exchange",
                          lambda: need(evaluate(events[:-1], b) == (identity(8), ungrouped(a, b)),
                                       "changed word endpoint"),
                          "changed word endpoint"))
    controls.append(reject("omit one attaining repair",
                          lambda: validate_repair(m, projectors[:-1]),
                          "repair coefficient endpoint"))
    controls.append(reject("trace-zero rank-one coupling",
                          lambda: projector_conjugator(1, 2, 8),
                          "repair is not a rank-one idempotent"))
    controls.append(reject("wrong even kernel parity",
                          lambda: need(all(dot(row, 1 << b) == 0 for row in m),
                                       "even kernel formula"),
                          "even kernel formula"))
    controls.append(reject("non-involutive N",
                          lambda: instantiated_endpoint(a, m, projectors, [2, 3], 1),
                          "N is not an involution"))
    controls.append(reject("identity N obstruction hypothesis",
                          lambda: instantiated_endpoint(a, m, projectors, [1, 2], 1),
                          "N identity representation excluded from obstruction"))
    controls.append(reject("duplicate recipe definition",
                          lambda: extract_recipe(b"def recipe(K): return []\ndef recipe(K): return []\n"),
                          "recipe definition multiplicity"))
    controls.append(reject("missing recipe definition",
                          lambda: extract_recipe(b"def another(K): return []\n"),
                          "recipe definition multiplicity"))
    controls.append(reject("changed epsilon formula",
                          lambda: need(add(a, [1] + [0] * 7) == grouped(evaluate(events, b)[1], b),
                                       "recipe closed-form coefficient"),
                          "recipe closed-form coefficient"))
    controls.append(reject("dirty spectator incorrectly receives N",
                          lambda: instantiated_endpoint(
                              a, m, projectors, [2, 1], 1,
                              wrong_first_spectator_target=True),
                          "literal dirty spectator restoration"))
    output = {
        "status": "PASS_FIXED_RECIPE_ALL_B_PROOF_CERTIFICATES",
        "scientific_pin": PIN,
        "source_hashes": {"recipe": RECIPE_SHA, "historical_receipt": HISTORICAL_SHA},
        "finite_coverage": {"B": [1, 12], "full_binary_instantiation_B": [1, 8],
                            "binary_N_matrices": 3, "spectator_counts": [0, 1, 3],
                            "historical_full_cases": 6},
        "all_parameter_written_theorem": "k(B)=2B+1 for odd B; k(B)=2B-1 for even B",
        "coordinate_order": "x0,...,x(B-1),y0,...,y(B-1)",
        "cases": cases, "negative_controls": controls,
        "formal_kernel_proof": False,
        "limits": ["Fixed recipe and scalar-GL-conjugated single-bank N repairs only.",
                   "Every finite number of independently dirty restored spectator banks is covered by the written bound.",
                   "Native scalar access, each N implementation and its price, fresh frames, helper restoration and precision remain separate."]
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(output["status"])
    print("B=1..12; all historical B=1..6 cases; 72 arbitrary-input instantiations; 12 intended rejections")


if __name__ == "__main__":
    main()
