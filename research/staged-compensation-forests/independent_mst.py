#!/usr/bin/env python3
"""Independent Fraction audit of the fixed C01 forest and helper basis.

No builder or producer code is imported or executed. The producer's default
frame expressions are read from its pinned AST. All outputs must be external
to the two input directories. Prepared with substantial OpenAI Codex assistance.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import heapq
import json
from pathlib import Path

Q = Fraction
SOURCE_PINS = {
    "base": "735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653",
    "extra": "886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f",
}
TRANSPORT_PIN = "9818e08b819310b40f1441b89be8c4369584a5b3fa5dfe9b86b1df9a7f5d6a76"
TARGETS = tuple(range(112, 224))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path, bindings, label, pin=None):
    raw = path.read_bytes()
    if pin is not None:
        require(digest(raw) == pin, "pinned input: " + label)
    decoded = gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw
    bindings[label] = {"sha256": digest(raw), "decoded_sha256": digest(decoded)}
    return json.loads(decoded)


@lru_cache(maxsize=None)
def tariff(q):
    """Count a literal cleared-work Horner program, using exact rationals."""
    if not q:
        return 0
    work, count = Q(0), 1  # initial private CLEAR
    digits = bin(abs(q.numerator))[2:]
    for position, bit in enumerate(digits):
        if position:
            work *= 2
            count += 1
        if bit == "1":
            work += 1
            count += 1
    denominator = q.denominator
    while denominator != 1:
        require(denominator % 2 == 0, "non-dyadic price")
        work /= 2
        denominator //= 2
        count += 1
    require(work == abs(q), "Horner coefficient reconstruction")
    return count + 2  # signed target ADD and final private CLEAR


def accumulate(dst, src, q):
    for column, coefficient in src.items():
        value = dst.get(column, Q(0)) + q * coefficient
        if value:
            dst[column] = value
        else:
            dst.pop(column, None)


def difference(left, right, sign):
    row = dict(left)
    accumulate(row, right, -sign)
    return row


def row_price(row):
    return sum(tariff(q) for q in row.values())


def gate(dst, src, q):
    return ["add", dst, src, q.numerator, q.denominator, []]


def coefficient(event):
    require(type(event) is list and len(event) == 6 and event[0] == "add"
            and event[5] == [], "addition and ZERO-frame schema")
    require(all(type(x) is int for x in event[1:5])
            and event[1] != event[2] and event[4] > 0, "addition coordinates")
    q = Q(event[3], event[4])
    require(q != 0 and q.denominator & (q.denominator - 1) == 0,
            "nonzero dyadic addition")
    return q


def inverse(events):
    return [gate(e[1], e[2], -coefficient(e)) for e in reversed(events)]


def sparse_matrix(events, helpers):
    result = {t: {} for t in TARGETS}
    for e in events:
        q = coefficient(e)
        require(e[1] in result and e[2] in helpers, "residual injection coordinates")
        accumulate(result[e[1]], {e[2]: Q(1)}, q)
    return result


def matrix_serial(matrix):
    return [[r, [[c, str(q)] for c, q in sorted(row.items())]]
            for r, row in sorted(matrix.items())]


def bill(events):
    values = [coefficient(e) for e in events]
    return {"logical_additions": len(events),
            "component_primitives": sum(map(tariff, values)),
            "coefficient_histogram": dict(sorted(Counter(map(str, values)).items()))}


def frame_contract(raw):
    """Bind the reviewed default-frame formulas without running the producer."""
    require(digest(raw) == TRANSPORT_PIN, "pinned transport source")
    tree = ast.parse(raw)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run"]
    require(len(functions) == 1, "unique producer run")
    expected = {
        "start": "[fid([p]) for p in ports] + [0] * (v + R)",
        "final": "[1] * v + [fid(x for x in range(1, 1 << h) if (x & p).bit_count() % 2 == 0) for p in ports] + [1] * R",
    }
    for name, expression in expected.items():
        nodes = [n.value for n in functions[0].body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
        require(len(nodes) == 1, "unique default frame assignment")
        require(ast.dump(nodes[0]) == ast.dump(ast.parse(expression, mode="eval").body),
                "producer default frame expression")
    return {"transport_sha256": TRANSPORT_PIN,
            "helper_default_entrance": "ZERO",
            "helper_default_terminal": "FULL",
            "producer_executed": False}


def eligible_helpers(word, helpers):
    require(word["report"]["v"] == 112 and word["report"]["h"] == 9,
            "source geometry")
    n = 224 + word["report"]["R"]
    require(n == 704 and len(set(word["removed"])) == len(word["removed"]),
            "source register inventory")
    require(all(224 <= r < n for r in word["removed"]), "removed helper domain")
    unavailable = set(word["removed"])
    extra = {int(k) for k in word["start_extra"]}
    nonfull = {int(k) for k in word["helper_final"]}
    require(all(224 <= h < n and h not in unavailable for h in helpers),
            "active helper availability")
    require(not (set(helpers) & extra), "helper ZERO entrance")
    require(not (set(helpers) & nonfull), "helper FULL terminal")
    return list(helpers)


def graph_certificate(C, record):
    edges = []
    for t in TARGETS:
        edges.append([row_price(C[t]), -1, t, 0])
    for t in TARGETS:
        for p in TARGETS:
            if p >= t:
                break
            for sign in (-1, 1):
                edges.append([8 + row_price(difference(C[t], C[p], sign)),
                              p, t, sign])
    edges.sort()
    require(len(edges) == 112 + 2 * (112 * 111 // 2) == 12544, "all signed graph edges")
    require(record["edge_count"] == len(edges)
            and record["edge_census_sha256"] == digest(canonical(edges)),
            "builder edge census differs")
    prices = {(a, b, s): cost for cost, a, b, s in edges}
    nodes = (-1,) + TARGETS
    adjacency = {v: [] for v in nodes}
    tree = record["tree"]
    require(len(tree) == 112 and len({tuple(e[1:]) for e in tree}) == 112,
            "tree inventory")
    for cost, a, b, sign in tree:
        require(prices.get((a, b, sign)) == cost, "tree edge price")
        adjacency[a].append((b, sign, cost))
        adjacency[b].append((a, sign, cost))
    parents, depths = {-1: None}, {-1: 0}
    queue = [-1]
    for node in queue:
        for child, sign, cost in sorted(adjacency[node]):
            if child not in parents:
                parents[child] = [node, sign, cost]
                depths[child] = depths[node] + 1
                queue.append(child)
    require(len(parents) == 113, "tree spans every target")
    require({str(k): v for k, v in parents.items()} == record["parent"], "tree parent record")
    pathmax = {}
    for start in nodes:
        maximum, todo = {start: 0}, [start]
        for node in todo:
            for nxt, sign, cost in adjacency[node]:
                if nxt not in maximum:
                    maximum[nxt] = max(maximum[node], cost)
                    todo.append(nxt)
        pathmax[start] = maximum
    slacks = [cost - pathmax[a][b] for cost, a, b, sign in edges]
    require(all(s >= 0 for s in slacks), "MST cycle inequality")
    # Independently solve with a heap-based Prim traversal of our priced graph.
    graph = {v: [] for v in nodes}
    for cost, a, b, sign in edges:
        graph[a].append((cost, b))
        graph[b].append((cost, a))
    seen, heap, prim = {-1}, list(graph[-1]), 0
    heapq.heapify(heap)
    while len(seen) < len(nodes):
        require(bool(heap), "Prim graph connectivity")
        cost, nxt = heapq.heappop(heap)
        if nxt in seen:
            continue
        prim += cost
        seen.add(nxt)
        for item in graph[nxt]:
            if item[1] not in seen:
                heapq.heappush(heap, item)
    require(prim == sum(e[0] for e in tree) == record["prim_cost"] == 13716,
            "independent forest minimum")
    return parents, depths, {
        "edge_count": len(edges), "root_edges": 112, "signed_pair_edges": len(edges) - 112,
        "edge_census_sha256": digest(canonical(edges)),
        "all_cycle_inequalities_checked": len(slacks),
        "cycle_slack_histogram": dict(sorted(Counter(slacks).items())),
        "cycle_slacks_sha256": digest(canonical(slacks)),
        "independent_heap_Prim_price": prim,
        "tree": tree, "roots": sum(parents[t][0] == -1 for t in TARGETS),
        "target_edges": sum(parents[t][0] != -1 for t in TARGETS),
        "maximum_forest_depth": max(depths.values()) - 1,
    }


def target_preparation(events, parents):
    expected = {(t, parents[t][0], Q(-parents[t][1])) for t in TARGETS
                if parents[t][0] != -1}
    actual = [(e[1], e[2], coefficient(e)) for e in events]
    require(set(actual) == expected and len(actual) == len(expected),
            "target forest basis gates")
    positions = {t: i for i, (t, p, q) in enumerate(actual)}
    for t, p, q in actual:
        require(p not in positions or positions[t] < positions[p],
                "leaf before parent preparation")


def transformed_rows(C, parents):
    return {t: dict(C[t]) if parents[t][0] == -1
            else difference(C[t], C[parents[t][0]], parents[t][1]) for t in TARGETS}


def helper_certificate(D, helpers, record):
    columns = {h: {t: D[t][h] for t in TARGETS if h in D[t]} for h in helpers}
    candidates = []
    for a in helpers:
        for b in helpers:
            if a == b:
                continue
            for sign in (-1, 1):
                gain = row_price(columns[b]) - row_price(difference(columns[b], columns[a], sign)) - 8
                candidates.append([gain, a, b, sign])
    require(len(candidates) == 2 * 207 * 206 == 85284, "all helper candidate scores")
    require(record["helper_candidate_count"] == len(candidates)
            and record["helper_candidates_sha256"] == digest(canonical(candidates)),
            "builder helper score census differs")
    positive = sorted((e for e in candidates if e[0] > 0),
                      key=lambda e: (-e[0], e[1:]))
    used, pairs = set(), []
    for gain, a, b, sign in positive:
        if a not in used and b not in used:
            pairs.append([gain, a, b, sign])
            used.update((a, b))
    require(pairs == record["pairs"] and len(pairs) == 88 and len(used) == 176,
            "88 disjoint attaining helper pairs")
    E = {t: dict(row) for t, row in D.items()}
    for gain, a, b, sign in pairs:
        for t in TARGETS:
            value = D[t].get(b, Q(0)) - sign * D[t].get(a, Q(0))
            if value:
                E[t][b] = value
            else:
                E[t].pop(b, None)
    return pairs, E, {
        "candidate_count": len(candidates), "candidate_sha256": digest(canonical(candidates)),
        "positive_candidates": len(positive), "pairs": pairs,
        "disjoint_helpers": len(used), "total_additive_saving": sum(e[0] for e in pairs),
        "joint_optimum_claimed": False,
    }


def endpoint(events, live, mode):
    rows = {r: {r: Q(1)} for r in live}
    stream = inverse(events) if mode == "inverse" else events
    for e in stream:
        q, dst, src = coefficient(e), e[1], e[2]
        if mode == "dual":
            dst, src, q = src, dst, -q
        require(dst in rows and src in rows, "panel live register")
        accumulate(rows[dst], rows[src], q)
    return rows


def expected_endpoint(C, live, mode):
    rows = {r: {r: Q(1)} for r in live}
    for target, row in C.items():
        for helper, q in row.items():
            if mode == "dual":
                rows[helper][target] = -q
            else:
                rows[target][helper] = q if mode == "forward" else -q
    return rows


def defect(actual, expected):
    for row in sorted(expected):
        if actual[row] != expected[row]:
            for column in sorted(set(actual[row]) | set(expected[row])):
                if actual[row].get(column, 0) != expected[row].get(column, 0):
                    return {"row": row, "column": column,
                            "actual": str(actual[row].get(column, Q(0))),
                            "expected": str(expected[row].get(column, Q(0)))}
    return None


def complete_endpoint_gate(actual, expected):
    require(defect(actual, expected) is None, "complete arbitrary-input panel endpoint")


def rejects(label, action, expected_error):
    try:
        action()
    except ValueError as error:
        require(str(error) == expected_error, "wrong rejection for " + label + ": " + str(error))
        return {"name": label, "intended_gate": expected_error}
    raise ValueError("control accepted: " + label)


def panel_controls(C, live, T, H, injection, Hi, Ti, parents, word, helpers):
    global require
    expected = expected_endpoint(C, live, "forward")
    def flipped(events, index):
        answer = [list(e) for e in events]
        answer[index] = gate(events[index][1], events[index][2], -coefficient(events[index]))
        return answer
    original = [gate(t, h, q) for t, row in C.items() for h, q in row.items()]
    variants = {
        "omit_target_preparation": H + injection + Hi + Ti,
        "wrong_target_basis_sign": flipped(T, 0) + H + injection + Hi + Ti,
        "parent_before_child": list(reversed(T)) + H + injection + Hi + Ti,
        "omit_helper_preparation": T + injection + Hi + Ti,
        "wrong_helper_basis_sign": T + flipped(H, 0) + injection + Hi + Ti,
        "stale_untransformed_residual": T + H + original + Hi + Ti,
        "wrong_residual_sign": T + H + flipped(injection, 0) + Hi + Ti,
        "omit_helper_restoration": T + H + injection + Ti,
        "omit_target_restoration": T + H + injection + Hi,
        "wrong_target_restoration_order": T + H + injection + Hi + list(reversed(Ti)),
    }
    controls = []
    for label, events in variants.items():
        actual = endpoint(events, live, "forward")
        witness = defect(actual, expected)
        require(witness is not None, "effective mathematical mutation: " + label)
        record = rejects(label, lambda: complete_endpoint_gate(actual, expected),
                         "complete arbitrary-input panel endpoint")
        record["witness"] = witness
        controls.append(record)
    controls.append(rejects("explicit_leaf_order_check",
                            lambda: target_preparation(list(reversed(T)), parents),
                            "leaf before parent preparation"))
    changed = dict(word)
    changed["start_extra"] = dict(word["start_extra"], **{str(helpers[0]): [1]})
    controls.append(rejects("nonzero_helper_entrance",
                            lambda: eligible_helpers(changed, helpers), "helper ZERO entrance"))
    changed = dict(word)
    changed["helper_final"] = dict(word["helper_final"], **{str(helpers[0]): [1]})
    controls.append(rejects("nonfull_helper_terminal",
                            lambda: eligible_helpers(changed, helpers), "helper FULL terminal"))
    # Deliberately remove precisely the named endpoint requirement. The
    # negative-control helper must then fail because the mutant was accepted.
    saved = require
    actual = endpoint(variants["omit_helper_restoration"], live, "forward")
    try:
        require = lambda ok, message: None if message == "complete arbitrary-input panel endpoint" else saved(ok, message)
        try:
            rejects("deleted_endpoint_gate", lambda: complete_endpoint_gate(actual, expected),
                    "complete arbitrary-input panel endpoint")
        except ValueError as error:
            saved(str(error) == "control accepted: deleted_endpoint_gate", "check-deletion sensitivity")
        else:
            raise ValueError("deleted endpoint gate was not detected")
    finally:
        require = saved
    full = T + H + injection + Hi + Ti
    paid_pair = [gate(TARGETS[0], helpers[0], Q(1)), gate(TARGETS[0], helpers[0], Q(-1))]
    for mode in ("forward", "inverse", "dual"):
        complete_endpoint_gate(endpoint(full + paid_pair, live, mode), expected_endpoint(C, live, mode))
    require(bill(full + paid_pair)["component_primitives"] == bill(full)["component_primitives"] + 8,
            "positive cancelling pair must be paid")
    omitted = endpoint(variants["omit_target_preparation"], live, "forward")
    outside = [c for c in live if c not in TARGETS]
    require(all(omitted[r].get(c, 0) == expected[r].get(c, 0) for r in live for c in outside),
            "helper-only projection counterexample")
    return {"rejections": controls, "named_endpoint_check_deletion_detected": True,
            "paid_cancelling_pair": {"accepted_all_three_orientations": True,
                                    "added_component_primitives": 8},
            "omitted_target_preparation_passes_helper_only_projection": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--transport-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not any(args.output.resolve().is_relative_to(p.resolve())
                    for p in (args.source_dir, args.candidate_dir)), "output must be external")
    bindings = {}
    transport = args.transport_source.read_bytes()
    defaults = frame_contract(transport)
    bindings["transport"] = {"sha256": digest(transport)}
    design = load(args.candidate_dir / "DESIGN.json", bindings, "DESIGN")
    require(design["head"] == "3efbb5de06a49ffeea6684482f2d3fe48cdca3fb", "source Git pin")
    providers, common, common_C = {}, None, None
    for provider in ("base", "extra"):
        word = load(args.source_dir / f"SOURCE-{provider}.json.gz",
                    bindings, "source-" + provider, SOURCE_PINS[provider])
        active = sorted({e[2] for e in word["compensation"]})
        require(len(active) == 207, "all active helper columns")
        C = sparse_matrix(word["compensation"], set(active))
        require(sum(map(len, C.values())) == len(word["compensation"]) == 5736,
                "unaggregated fixed compensation")
        eligible = eligible_helpers(word, active)
        record = design["providers"][provider]
        require(record["active_helpers"] == active == record["eligible_helpers"],
                "helper frame eligibility record")
        if common is None:
            parents, depths, graph = graph_certificate(C, record)
            D = transformed_rows(C, parents)
            pairs, E, helper = helper_certificate(D, eligible, record)
            common = {"matrix_sha256": digest(canonical(matrix_serial(C))),
                      "target_residual_sha256": digest(canonical(matrix_serial(D))),
                      "two_sided_residual_sha256": digest(canonical(matrix_serial(E))),
                      "graph": graph, "helper_construction": helper}
            common_C = C
            core_record = {k: record[k] for k in ("tree", "parent", "pairs", "edge_census_sha256",
                                                 "helper_candidates_sha256", "prim_cost")}
        else:
            require(C == common_C, "same C in both providers")
            require(core_record == {k: record[k] for k in core_record}, "same fixed construction")
        live = sorted(set(range(704)) - set(word["removed"]))
        nt, nh, ni = 95, 88, 1922
        panels, audits = {}, {}
        for variant, M in (("FOREST", D), ("TWO-SIDED", E)):
            panel = load(args.candidate_dir / f"{variant}-COMPENSATION-{provider}.json.gz",
                         bindings, variant + "-panel-" + provider)
            candidate = load(args.candidate_dir / f"{variant}-WORD-{provider}.json.gz",
                             bindings, variant + "-word-" + provider)
            require(set(candidate) == set(word)
                    and all(candidate[k] == word[k] for k in word if k != "compensation"),
                    "outside compensation unchanged")
            require(candidate["compensation"] == panel, "whole word uses audited compensation")
            T = panel[:nt]
            target_preparation(T, parents)
            # Applying the literal T to C independently recovers the stated TC.
            literal_D = {t: dict(row) for t, row in C.items()}
            for e in T:
                accumulate(literal_D[e[1]], literal_D[e[2]], coefficient(e))
            require(literal_D == D, "literal target basis gives TC")
            if variant == "FOREST":
                injection, Ti = panel[nt:-nt], panel[-nt:]
                require(Ti == inverse(T), "literal target inverse")
            else:
                H = panel[nt:nt+nh]
                injection = panel[nt+nh:nt+nh+ni]
                Hi = panel[nt+nh+ni:nt+2*nh+ni]
                Ti = panel[nt+2*nh+ni:]
                require(H == [gate(a, b, Q(sign)) for gain, a, b, sign in pairs],
                        "literal disjoint helper basis")
                require(Hi == inverse(H) and Ti == inverse(T), "literal two-sided inverses")
            require(sparse_matrix(injection, set(active)) == M
                    and len(injection) == sum(map(len, M.values())),
                    "complete residual TCH^-1")
            checks = {}
            for mode in ("forward", "inverse", "dual"):
                rows = endpoint(panel, live, mode)
                complete_endpoint_gate(rows, expected_endpoint(C, live, mode))
                checks[mode] = {"all_input_columns": len(live),
                                "operator_sha256": digest(canonical(matrix_serial(rows)))}
            invoice = bill(panel)
            name = "target_only_bill" if variant == "FOREST" else "two_sided_bill"
            require(invoice == record[name], "complete literal bill")
            audits[variant] = {"bill": invoice, "orientations": checks,
                               "residual_nonzeros": len(injection)}
            panels[variant] = panel
        require(bill(word["compensation"]) == record["original_bill"], "original full bill")
        require([record[k]["component_primitives"] for k in
                 ("original_bill", "target_only_bill", "two_sided_bill")] == [31214, 13716, 10633],
                "fixed price comparison")
        require(13716 - common["helper_construction"]["total_additive_saving"] == 10633,
                "helper scores include both basis directions")
        controls = panel_controls(C, live, T, H, injection, Hi, Ti, parents, word, active)
        providers[provider] = {"live_registers": len(live), "active_and_eligible_helpers": active,
                               "original_bill": bill(word["compensation"]),
                               "audits": audits, "controls": controls}
    result = {"status": "PASS_INDEPENDENT_FRACTION_FOREST_AND_BASES",
              "source_head": design["head"], "source_bindings": bindings,
              "producer_default_frames": defaults, "common": common, "providers": providers,
              "tariffs": {str(q): tariff(q) for q in sorted(
                  {coefficient(e) for panel in panels.values() for e in panel})},
              "scope": "Fixed single-parent signed-unit target forest minimum and a disjoint helper construction. All live input columns; no joint basis optimum, whole-word precision or new kappa claim."}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], "edges=12544", "helper_scores=85284", "pairs=88",
          "prices=31214,13716,10633")


if __name__ == "__main__":
    main()
