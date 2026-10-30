"""Exact full-recursion frontiers and rounded forward/inverse execution.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from exact import (C, Mat, Vec, adjoint, apply, component_l1, eye, inverse_gate,
                   multiply, need, norm2, upper, vector_hash)
from full import Full, Matrix, Plan, admission, allocation, solve
from frontier import Frontier, embed
from verify import authenticate, canonical, mv, operator, plan_hash, rejected
from verify_generator import exact_rank
from verify_triangle import eliminate, frobenius_error, structure


def one_case(label, matrix, raw, reverse=False, fine=False):
    n = len(matrix)
    lam, q, leading = admission(matrix)
    vectors = [
        Vec(C(Q((3 * i + 1) % 7 - 3, 8), Q((5 * i + 2) % 11 - 5, 8)) for i in range(n)),
        Vec(C((-1) ** i * (1 << 10), (i % 2) * (1 << 8)) for i in range(n)),
    ]
    if fine:
        vectors.append(Vec([C(Q(1, 1 << 512))] + [C()] * (n - 1)))
    radius = max(Q(1), *(component_l1(v) for v in vectors))
    incoming = max(part.denominator.bit_length() - 1 for v in vectors for z in v
                   for part in (z.re, z.im))
    bound = allocation(n, lam, q, radius, 20, incoming)
    if fine:
        coarse = allocation(n, lam, q, radius, 20, 0)
        need(bound["data_bits"] > coarse["data_bits"], "nonzero fine-grid caller overrides required grid")
    builder = Full(bound, raw)
    indices = list(reversed(range(n))) if reverse else list(range(n))
    plan = builder.plan(matrix, indices)
    inverse = builder.inverse(plan)
    bound = builder.bound
    need(all(len(a["generator_items"]) == exact_rank(a["displacement"])
             for a in plan.atoms if a["kind"] != "leaf"), "full-call exact generator ranks")
    wanted = embed(matrix, indices, n)
    wanted_inverse = eliminate(wanted)
    actual, actual_inverse = operator(plan, n), operator(inverse, n)
    need(multiply(actual, actual_inverse) == eye(n), "full exact stored-program inverse")
    forward_squared = frobenius_error(actual, wanted)
    inverse_squared = frobenius_error(actual_inverse, wanted_inverse)
    need(max(forward_squared, inverse_squared) <= n * bound["coefficient_error"] ** 2,
         "full matrix and separate inverse references")
    height = max(structure(plan, bound), structure(inverse, bound))
    frontier = Frontier(builder, plan)
    timing = frontier.schedule()
    downsets = (frontier.downsets() if n <= 4 else
                [{a["id"] for a in plan.atoms if a["stop"] <= cut}
                 for cut in sorted({0, len(plan)} |
                                   {a["start"] for a in plan.atoms} |
                                   {a["stop"] for a in plan.atoms})])
    unique = {tuple(sorted(x)): x for x in downsets}
    downset_records = [frontier.check_downset(unique[key]) for key in sorted(unique)]
    physical = []
    if n in (2, 4) or label == "unequal-subtrees":
        candidates = list(range(len(plan) + 1))
        def score(cut):
            active = [a for a in plan.atoms if a["start"] < cut < a["stop"]]
            return len(active), sum(cut - a["start"] for a in active)
        selected = max(candidates, key=score)
        cuts = {len(plan) // 2, selected}
        physical = [frontier.physical_cut(cut) for cut in sorted(cuts)]
    vectors.append(Vec([C(Q(2, 1 << bound["data_bits"]))] + [C()] * (n - 1)))
    final = allocation(n, lam, q, radius, 20, bound["data_bits"])
    need(all(final[k] == value for k, value in bound.items()
             if k not in ("incoming_bits", "coefficient_height_bound", "temporary_bits")),
         "micro data preserves full allocation")
    bound["incoming_bits"] = bound["data_bits"]
    states = []
    for direction, program, stored, intended in (
            ("forward", plan, actual, wanted),
            ("inverse", inverse, actual_inverse, wanted_inverse)):
        for vector in vectors:
            need(norm2(vector) <= radius ** 2, "full input radius")
            output, stats = apply(program, vector, bound["data_bits"])
            exact_stored, exact_target = mv(stored, vector), mv(intended, vector)
            coefficient = norm2(exact_stored - exact_target)
            rounding = norm2(output - exact_stored)
            total = norm2(output - exact_target)
            need(coefficient <= (bound["coefficient_error"] * radius) ** 2,
                 "full coefficient error")
            need(rounding <= bound["rounding_error"] ** 2 and total <= bound["total_error"] ** 2,
                 "full rounded forward/inverse budget")
            need(stats["max_observed_height"] <= bound["temporary_bits"]
                 and stats["max_grid_numerator_bits"] + 1 <= bound["data_bits"] + bound["integer_bits"]
                 and stats["max_reduced_fractional_bits"] <= bound["data_bits"],
                 "full signed grid and temporary widths")
            states.append(dict(direction=direction, input_sha256=vector_hash(vector),
                               output_sha256=vector_hash(output),
                               coefficient_squared_upper=str(upper(coefficient)),
                               rounding_squared_upper=str(upper(rounding)),
                               total_squared_upper=str(upper(total)), statistics=stats))
    atoms = []
    for atom in plan.atoms:
        row = {k: atom[k] for k in ("id", "kind", "indices", "start", "stop", "coefficient_height")}
        row.update(interval=list(atom["interval"]), operator_error=str(atom["error"]),
                   ideal_sha256=vector_hash([x for r in atom["ideal"] for x in r]))
        if atom["kind"] != "leaf":
            row.update(rank=len(atom["generator_items"]),
                       child_budget={k: str(v) if isinstance(v, Q) else v
                                     for k, v in atom["program"].bound.items()})
        atoms.append(row)
    return dict(label=label, n=n, indices=indices,
                input_sha256=vector_hash([x for row in matrix for x in row]),
                leading_bounds=[dict(size=b, inverse_component_bound=str(v)) for b, v in leading],
                source_ast_sha256=builder.source_ast, nodes=len(builder.nodes),
                layers=len(plan), gates=sum(map(len, plan)), atoms=atoms, timing=timing,
                downsets=downset_records, physical_cuts=physical,
                plan_sha256=plan_hash(plan), inverse_sha256=plan_hash(inverse),
                budget={k: str(v) if isinstance(v, Q) else v for k, v in bound.items()},
                max_coefficient_height=height,
                forward_frobenius_squared_upper=str(upper(forward_squared)),
                inverse_frobenius_squared_upper=str(upper(inverse_squared)),
                phase_oracles=[builder.phase_pool[p].record() for p in sorted(builder.phase_pool)],
                states=states)


def controls(raw):
    results = []
    results.append(rejected(lambda: admission(Mat([[0, 1], [1, 0]])),
                            "invertible-full-matrix-with-singular-leading-section"))
    results.append(rejected(lambda: admission(Mat([[1, 2], [3, 4]])), "non-Toeplitz-root"))
    results.append(rejected(lambda: admission(Mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]])),
                            "nondyadic-full-size"))
    results.append(rejected(lambda: admission([[1.0]]), "floating-full-input"))
    matrix = Mat([[C(1, Q(1, 4)), C(Q(1, 16), Q(1, 8))],
                  [C(Q(1, 8), Q(-1, 16)), C(1, Q(1, 4))]])
    lam, q, _ = admission(matrix)
    bound = allocation(2, lam, q, 4, 20, 0)
    builder = Full(bound, raw)
    plan = builder.plan(matrix)
    first = next(a for a in plan.atoms if a["id"] == "R:0:2")
    mutant = plan[first["stop"]:]
    need(frobenius_error(operator(mutant, 2), matrix) > 2 * bound["coefficient_error"] ** 2,
         "missing root upper shear changes full operator")
    results.append("omitted-root-upper-call")
    wrong_order = [[(ids, inverse_gate(gate)) for ids, gate in layer] for layer in plan]
    need(frobenius_error(operator(wrong_order, 2), eliminate(matrix))
         > 2 * bound["coefficient_error"] ** 2, "wrong full inverse order")
    results.append("full-inverse-layer-order")
    builder = Full(bound, raw)
    calls = [0]
    def wrong_solve(left, right):
        calls[0] += 1
        if calls[0] == 2:
            left = Matrix([[x.conjugate() for x in row] for row in left])
        return solve(left, right)
    builder.namespace["np"].linalg.solve = wrong_solve
    wrong = builder.plan(matrix)
    need(frobenius_error(operator(wrong, 2), matrix) > 2 * bound["coefficient_error"] ** 2,
         "one-sided conjugation in complex lower solve")
    results.append("one-sided-conjugation-in-lower-solve")
    builder = Full(bound, raw)
    builder.namespace["parallel"] = lambda a, b: a + b
    serial = builder.plan(matrix)
    results.append(rejected(lambda: Frontier(builder, serial).schedule(), "serialized-full-siblings"))
    identity = Mat(eye(4))
    identity_bound = allocation(4, 1, 1, 4, 20, 0)
    builder = Full(identity_bound, raw)
    identity_plan = builder.plan(identity)
    changed = [dict(a, stop=1) if a["id"] == "R:0:4" else dict(a) for a in identity_plan.atoms]
    results.append(rejected(lambda: Frontier(builder, Plan(identity_plan, changed)).schedule(),
                            "delayed-zero-layer-identity-call"))
    scalar = Mat([[C(Q(1, 3), Q(1, 7))]])
    lam, q, _ = admission(scalar)
    scalar_bound = allocation(1, lam, q, 1, 20, 0)
    scalar_plan = Full(scalar_bound, raw).plan(scalar)
    adjoints = [[(ids, adjoint(gate)) for ids, gate in layer] for layer in reversed(scalar_plan)]
    need(frobenius_error(operator(adjoints, 1), eliminate(scalar))
         > scalar_bound["coefficient_error"] ** 2, "full scalar adjoint is not reciprocal")
    results.append("full-scalar-adjoint-instead-of-reciprocal")
    coarse, _ = apply(scalar_plan, Vec([1]), 4)
    need(norm2(coarse - Vec([scalar[0][0]])) > Q(1, 1 << 40), "coarse full grid misses target")
    results.append("underfunded-full-data-grid")
    tiny = Mat([[Q(1, 1 << 40)]])
    lam, q, _ = admission(tiny)
    tiny_bound = dict(allocation(1, lam, q, 1, 20, 0), child_target_bits=4, eta=Q(1, 16))
    results.append(rejected(lambda: Full(tiny_bound, raw).plan(tiny), "rounded-zero-full-pivot"))
    results.append(rejected(lambda: apply(scalar_plan, Vec([Q(1, 1 << 512)]), 20),
                            "discarded-full-incoming-grid"))
    matrix4 = Mat([[C(1, Q(1, 8)) if i == j
                    else C(Q(1, 32 * (1 + abs(i - j))), Q(i - j, 128))
                    for j in range(4)] for i in range(4)])
    lam, q, _ = admission(matrix4)
    builder = Full(allocation(4, lam, q, 4, 20, 0), raw)
    p4 = builder.plan(matrix4)
    f = Frontier(builder, p4)
    _, _, up, intervals = f._partial({"R:0:4"}, 0, 4)
    front = eye(4)
    for a, b in intervals:
        for i in range(a, b):
            for j in range(a, b):
                front[i][j] = f.factors[a, b][2][i - a][j - a]
    need(multiply(front, f.factors[0, 4][2]) != up, "upper frontier requires its inverse")
    results.append("missing-upper-frontier-inverse")
    need(canonical({"nodes": 1}) != canonical({"nodes": True}), "typed full receipt")
    return results + ["typed-full-receipt"]


def run():
    raw, sources = authenticate(include_generator=True, include_full=True)
    fixtures = [
        ("complex-scalar", Mat([[C(Q(1, 3), Q(1, 7))]]), False, False),
        ("small-pivot", Mat([[Q(1, 1 << 80)]]), False, False),
        ("large-scalar", Mat([[C(1 << 30, -(1 << 28))]]), False, False),
    ]
    for n in (2, 4, 8):
        matrix = Mat([[C(1, Q(1, 16)) if i == j
                       else C(Q(-1 if (i - j) % 2 else 1, 32 * n), Q(i - j, 64 * n))
                       for j in range(n)] for i in range(n)])
        fixtures.append((f"complex-near-identity-{n}", matrix, n >= 4, n == 4))
    for n in (2, 4):
        matrix = Mat([[1 if i == j else 2 if abs(i - j) == 1 else 0
                       for j in range(n)] for i in range(n)])
        fixtures.append((f"indefinite-{n}", matrix, True, False))
    n = 4
    matrix = Mat([[Q(1, 2) ** ((i - j) ** 2 - (i - j)) for j in range(n)] for i in range(n)])
    fixtures.append(("half-shift-Gaussian", matrix, False, False))
    n = 8
    matrix = Mat([[1 if i == j else Q(1, 16) if abs(i - j) == 4
                   else Q(1, 32) if abs(i - j) == 5 else 0
                   for j in range(n)] for i in range(n)])
    fixtures.append(("unequal-subtrees", matrix, False, False))
    fixtures.append(("zero-call-identity-16", Mat(eye(16)), True, False))
    records = []
    for label, matrix, reverse, fine in fixtures:
        records.append(one_case(label, matrix, raw, reverse, fine))
        print("CHECK_FULL_CASE", label, flush=True)
    need(any(row["timing"]["unequal_sibling_nodes"] for row in records), "unequal sibling execution witness")
    need(any(row["timing"]["simultaneous_nonempty_fragments"] for row in records),
         "simultaneous unfinished child fragments")
    need(any(cut["nonempty_active_prefixes"] >= 2
             for row in records for cut in row["physical_cuts"]),
         "checked exact factorization with simultaneous nonempty fragments")
    need(next(row for row in records if row["label"] == "unequal-subtrees")
         ["timing"]["unequal_sibling_nodes"] > 0, "designed unequal-subtree fixture")
    need(any(row["timing"]["zero_layer_calls"] for row in records), "zero-call schedule witness")
    return dict(schema_version=1, scope="actual full Toeplitz recursion and stored inverse",
                sources=sources, cases=records, controls=controls(raw),
                full_toeplitz_gate_execution=True, physical_tape_execution=False,
                complete_gaussian_execution=False, universal_proof_kernel=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    parser.add_argument("--with-gaussian", action="store_true")
    parser.add_argument("--with-raw", action="store_true")
    parser.add_argument("--with-core", action="store_true")
    args = parser.parse_args()
    need(not args.with_raw or args.with_gaussian, "raw verification follows normalized verification")
    need(not args.with_core or args.with_raw, "core verification follows raw verification")
    result = run()
    path = HERE / "FULL-RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed full receipt")
    print(json.dumps(dict(status="PASS_RATIONAL_FULL_TOEPLITZ", cases=len(result["cases"]),
                          gates=sum(x["gates"] for x in result["cases"]),
                          rounded_states=sum(len(x["states"]) for x in result["cases"]),
                          downsets=sum(len(x["downsets"]) for x in result["cases"]),
                          physical_cuts=sum(len(x["physical_cuts"]) for x in result["cases"]),
                          result_sha256=sha256(canonical(result)).hexdigest()), sort_keys=True))
    if args.with_gaussian:
        from verify_gaussian import verify_result
        verify_result(args.write_result)
    if args.with_raw:
        from verify_raw_gaussian import verify_result as verify_raw_result
        verify_raw_result(args.write_result)
    if args.with_core:
        from verify_core import verify_result as verify_core_result
        verify_core_result(args.write_result)


if __name__ == "__main__":
    main()
