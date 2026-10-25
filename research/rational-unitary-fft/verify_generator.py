"""Source-bound complete compensated-generator gate replay.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0.
"""
import argparse
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from exact import (C, Mat, Vec, apply, component_l1, eye, inverse_gate, multiply, need,
                   norm2, upper, vector_hash)
from engine import Builder, Phases
from generator import (ORACLE, SOURCE, PairedNegative, Program, allocation,
                       load_producer, lower, prepare)
from verify import authenticate, canonical, mv, operator, plan_hash, rejected
from verify_triangle import frobenius_error, structure
from triangular import allocation as triangle_allocation


def collect(raw, producer):
    source = raw[SOURCE + "check_exact_algebra.py"]
    namespace = {"__name__": "_retained_exact_subject", "__file__": "<retained exact algebra>"}
    exec(compile(source, "<authenticated exact algebra>", "exec", optimize=0), namespace)
    tree = ast.parse(source)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    walk = copy.deepcopy(next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == "walk"))
    index = next(i for i, node in enumerate(walk.body) if isinstance(node, ast.Assign)
                 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "S")
    walk.body.insert(index + 1, ast.Expr(value=ast.Call(func=ast.Name(id="capture", ctx=ast.Load()),
        args=[ast.Name(id=x, ctx=ast.Load()) for x in ("K", "L", "n", "depth")], keywords=[])))
    collected = []
    def capture(k, l, n, depth):
        for label, matrix in (("K", k), ("L", l)):
            collected.append((f"source-{label}-n{n}-d{depth}",
                              Mat([[C(x.re, x.im) if isinstance(x, producer["C"]) else C(x)
                                    for x in row] for row in matrix])))
    namespace.update(trace=[], capture=capture)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[walk], type_ignores=[])),
                 "<retained Schur walk with collection hook>", "exec", optimize=0), namespace)
    old_c, old_matrix = producer["C"], producer["Matrix"]
    for size in (2, 4, 8):
        for complex_case in (False, True):
            column = [old_c(1)] + [old_c(Q((-1) ** i, 64 * size),
                                       Q(i, 128 * size) if complex_case else 0)
                                  for i in range(1, size)]
            row = [old_c(1)] + [old_c(Q(1, 64 * size),
                                    Q((-1) ** j, 128 * size) if complex_case else 0)
                               for j in range(1, size)]
            matrix = old_matrix([[column[i - j] if i >= j else row[j - i]
                                  for j in range(size)] for i in range(size)])
            namespace["walk"](matrix)
    matrix = old_matrix([[int(i == j) for j in range(4)] for i in range(4)])
    matrix[0][2] = matrix[1][3] = old_c(Q(1, 16))
    matrix[0][3] = old_c(0, Q(1, 16))
    namespace["walk"](matrix)
    return collected, namespace["trace"], sha256(ast.dump(walk).encode()).hexdigest()

def exact_rank(matrix):
    rows, pivot_row = [list(row) for row in matrix], 0
    for column in range(len(matrix)):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][column] != 0), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        divisor = rows[pivot_row][column]
        rows[pivot_row] = [x / divisor for x in rows[pivot_row]]
        for i in range(pivot_row + 1, len(rows)):
            multiplier = rows[i][column]
            rows[i] = [x - multiplier * y for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
    return pivot_row


def shear_matrix(matrix):
    m = len(matrix)
    return Mat([[int(i == j) if i < m or j >= m else matrix[i - m][j]
                 for j in range(2 * m)] for i in range(2 * m)])


def reconstruct(items, displacement, matrix):
    m = len(matrix)
    e = Mat([[0] * m for _ in range(m)])
    t = Mat([[0] * m for _ in range(m)])
    for item in items:
        g, row = item["g"], item["row"]
        term = multiply(lower(g), Mat(zip(*lower(row))))
        for i in range(m):
            for j in range(m):
                e[i][j] = e[i][j] + g[i] * row[j]
                t[i][j] = t[i][j] + term[i][j]
    need(e == displacement and t == matrix, "exact producer and Stein reconstruction")

def checkpoint_check(program, plan, actual, bound):
    n = 2 * bound["m"]
    prefix, inverse_prefix = eye(n), eye(n)
    final_inverse = Mat([[int(i == j) if i < n // 2 or j >= n // 2 else -actual[i][j]
                         for j in range(n)] for i in range(n)])
    peak = Q(0)
    for stage in program.stages:
        fragment = plan[stage["start"]:stage["stop"]]
        reverse = [[(ids, inverse_gate(gate)) for ids, gate in layer] for layer in reversed(fragment)]
        prefix = multiply(operator(fragment, n), prefix)
        inverse_prefix = multiply(inverse_prefix, operator(reverse, n))
        need(multiply(prefix, inverse_prefix) == eye(n), "exact checkpoint inverse")
        suffix = multiply(actual, inverse_prefix)
        inverse_suffix = multiply(prefix, final_inverse)
        for matrix in (prefix, inverse_prefix, suffix, inverse_suffix):
            squared = sum((x.norm2() for row in matrix for x in row), Q(0))
            peak = max(peak, squared)
            need(squared <= n * bound["checkpoint_bound"] ** 2,
                 "checkpoint Frobenius consequence")
    need(prefix == actual, "checkpoint sequence reaches actual endpoint")
    return dict(checkpoints=len(program.stages), max_frobenius_squared_upper=str(upper(peak)))


def one_case(label, matrix, raw, producer, fine=False):
    m = len(matrix)
    items, displacement, bound_e, heights = prepare(matrix, producer)
    need(len(items) == exact_rank(displacement), "separate exact rank reference")
    reconstruct(items, displacement, matrix)
    vectors = [
        Vec(C(Q((5 * i + 2) % 11 - 5, 8), Q((3 * i + 1) % 7 - 3, 8))
            for i in range(2 * m)),
        Vec(C((-1) ** i * (1 << 12), (i % 2) * (1 << 10)) for i in range(2 * m)),
    ]
    if fine:
        vectors.append(Vec([C(Q(1, 1 << 100))] + [C()] * (2 * m - 1)))
    radius = max(Q(1), *(component_l1(v) for v in vectors))
    incoming = max(part.denominator.bit_length() - 1 for v in vectors
                   for entry in v for part in (entry.re, entry.im))
    bound, triangular = allocation(m, len(items), bound_e, radius, 20, incoming)
    program = Program(bound, triangular, raw)
    plan = program.plan(items)
    actual = operator(plan, 2 * m)
    expected = shear_matrix(matrix)
    for i in range(2 * m):
        for j in range(2 * m):
            if i < m or j >= m:
                need(actual[i][j] == int(i == j), "exact unrounded source restoration")
    coefficient_squared = frobenius_error(actual, expected)
    need(coefficient_squared <= m * bound["coefficient_error"] ** 2,
         "independent full-matrix endpoint reference")
    height = structure(plan, dict(bound, n=2 * m))
    checkpoints = (checkpoint_check(program, plan, actual, bound)
                   if label in ("dense-complex", "large-scale", "source-K-n8-d0")
                   else None)
    need(len(program.stages) == 4 * len(items), "complete actual macro checkpoints")
    cursor = 0
    stage_records = []
    for stage in program.stages:
        need(stage["start"] == cursor and stage["stop"] > cursor, "consecutive nonempty macro stages")
        cursor = stage["stop"]
        entry = {k: str(v) if isinstance(v, Q) else v for k, v in stage.items()
                 if k not in ("matrix", "symbol")}
        if "matrix" in stage:
            entry["matrix_sha256"] = vector_hash([x for row in stage["matrix"] for x in row])
        if "symbol" in stage:
            entry["symbol"] = [x.record() for x in stage["symbol"]]
        stage_records.append(entry)
    need(cursor == len(plan), "complete actual stage coverage")
    vectors.append(Vec([C(Q(2, 1 << bound["data_bits"]))] + [C()] * (2 * m - 1)))
    final, _ = allocation(m, len(items), bound_e, radius, 20, bound["data_bits"])
    need(all(final[k] == v for k, v in bound.items() if k != "incoming_bits"),
         "micro fixture preserves global allocation")
    bound = final
    states = []
    for vector in vectors:
        need(norm2(vector) <= radius ** 2, "dirty input radius")
        output, stats = apply(plan, vector, bound["data_bits"])
        unrounded, intended = mv(actual, vector), mv(expected, vector)
        coefficient = norm2(unrounded - intended)
        rounding = norm2(output - unrounded)
        total = norm2(output - intended)
        source_error = norm2(Vec(output[:m]) - Vec(vector[:m]))
        need(coefficient <= (bound["coefficient_error"] * radius) ** 2, "additive coefficient defect")
        need(rounding <= bound["rounding_error"] ** 2, "global rounded gate error")
        need(total <= bound["total_error"] ** 2 and source_error <= bound["rounding_error"] ** 2,
             "complete compensated error and rounded restoration")
        need(stats["max_observed_height"] <= bound["temporary_bits"]
             and stats["max_grid_numerator_bits"] + 1 <= bound["data_bits"] + bound["integer_bits"]
             and stats["max_reduced_fractional_bits"] <= bound["data_bits"],
             "global signed grid and temporary widths")
        states.append(dict(input_sha256=vector_hash(vector), output_sha256=vector_hash(output),
                           coefficient_squared_upper=str(upper(coefficient)),
                           rounding_squared_upper=str(upper(rounding)),
                           total_squared_upper=str(upper(total)),
                           source_squared_upper=str(upper(source_error)),
                           source_restoration_exact=source_error == 0, statistics=stats))
    return dict(label=label, m=m, rank=len(items),
                input_sha256=vector_hash([x for row in matrix for x in row]),
                stein_sha256=vector_hash([x for row in displacement for x in row]),
                generators=[dict(column=x["column"], gamma=str(x["gamma"]), scale=str(x["scale"]),
                                 g=[z.record() for z in x["g"]], row=[z.record() for z in x["row"]])
                            for x in items],
                producer_heights=heights, macro_ast_sha256=program.macro_ast,
                budget={k: str(v) if isinstance(v, Q) else v for k, v in bound.items()},
                layers=len(plan), gates=sum(map(len, plan)), stages=stage_records,
                plan_sha256=plan_hash(plan), max_coefficient_height=height,
                endpoint_frobenius_squared_upper=str(upper(coefficient_squared)),
                checkpoints=checkpoints, phases=program.phases.record(), states=states), program, plan, expected


def controls(raw, producer):
    matrix = Mat([[C(Q(1, 8)), C(0, Q(1, 16))], [C(), C(Q(1, 8))]])
    items, e, be, _ = prepare(matrix, producer)
    bound, triangular = allocation(2, len(items), be, 4, 20, 0)
    program = Program(bound, triangular, raw)
    plan = program.plan(items)
    wanted = shear_matrix(matrix)
    result = []
    for kind in ("inverse", "compensation"):
        stage = next(s for s in program.stages if s["kind"] == kind)
        mutant = plan[:stage["start"]] + plan[stage["stop"]:]
        need(frobenius_error(operator(mutant, 4), wanted) > 2 * bound["coefficient_error"] ** 2,
             "omitted generator stage changes endpoint")
        result.append("omitted-" + kind)
    wrong = [dict(item, row=Vec(x.conjugate() for x in item["row"])) for item in items]
    result.append(rejected(lambda: reconstruct(wrong, e, matrix), "extra-row-conjugation"))
    tiny = Mat([[Q(1, 1 << 200), 0], [0, Q(1, 1 << 200)]])
    tiny_items, tiny_e, _, _ = prepare(tiny, producer)
    need(len(tiny_items) == 1, "retain tiny exact rank before approximation")
    result.append(rejected(lambda: reconstruct([], tiny_e, tiny), "omitted-tiny-exact-generator"))
    result.append(rejected(lambda: prepare([[1.0]], producer), "floating-generator-input"))
    result.append(rejected(lambda: prepare([[1, 0, 0], [0, 1, 0], [0, 0, 1]], producer),
                           "nondyadic-generator-size"))
    result.append(rejected(lambda: apply(plan, Vec([Q(1, 1 << 100), 0, 0, 0]), 20),
                           "discarded-generator-input-grid"))
    bad = dict(bound, phase_bits=4)
    bad_triangle = dict(triangular, phase_bits=4)
    result.append(rejected(lambda: Program(bad, bad_triangle, raw).plan(items),
                           "underfunded-common-phases"))
    large = Mat([[1 << 80, 1 << 80], [0, 1 << 80]])
    large_items, _, large_e, _ = prepare(large, producer)
    large_bound, large_triangle = allocation(2, len(large_items), large_e, 4, 20, 0)
    triangle_only = triangle_allocation(2, 1, large_bound["child_target_bits"])["phase_bits"]
    need(triangle_only < large_bound["phase_bits"], "large shear needs additional phase precision")
    try:
        Program(dict(large_bound, phase_bits=triangle_only),
                dict(large_triangle, phase_bits=triangle_only), raw).plan(large_items)
    except ValueError as error:
        need(str(error) == "scaled shear absolute operator allowance",
             "scale control reaches and fails the scaled shear contract")
    else:
        raise ValueError("uncharged scale control unexpectedly passed")
    result.append("uncharged-scaled-shear-phase-precision")
    # At a half tie, independent nearest-up rounding of +/- is not odd.
    bits = 8
    phases = Phases(12, raw[ORACLE])
    source = raw[SOURCE + "check_circuits.py"]
    kernel = Mat([[Q(1, 1 << bits)]])
    positive = Builder(phases, bits, source)
    plus = positive.plan(kernel)
    negative = PairedNegative(positive, source)
    paired = negative.plan(-1 * kernel)
    independent = Builder(phases, bits, source).plan(-1 * kernel)
    need(operator(plus + paired, 2) == eye(2), "paired half-tie compensation")
    need(operator(plus + independent, 2) != eye(2), "independent half ties lose exact compensation")
    result.append("independent-half-tie-compensation")
    need(Vec([1, 2]) / 2 == Vec([Q(1, 2), 1]), "fresh exact macro vector division")
    result.append("exact-fresh-vector-division")
    need(canonical({"rank": 1}) != canonical({"rank": True}), "typed full receipt")
    return result + ["typed-generator-receipt"]


def run():
    raw, sources = authenticate(include_generator=True)
    producer = load_producer(raw)
    fixtures, trace, collector_ast = collect(raw, producer)
    tiny = Q(1, 1 << 200)
    fixtures += [
        ("zero", Mat([[0, 0], [0, 0]])),
        ("scalar", Mat([[Q(1, 32)]])),
        ("tiny-diagonal", Mat([[tiny, 0], [0, tiny]])),
        ("near-dependent", Mat([[1, 1], [0, 1 + tiny]])),
        ("complex-row", Mat([[C(Q(1, 16)), C(0, Q(1, 16))], [0, Q(1, 16)]])),
        ("large-scale", Mat([[1 << 80, 1 << 80], [0, 1 << 80]])),
        ("dense-complex", Mat([[C(Q(1 + (3 * i + j) % 7, 32),
                                    Q((i + 2 * j) % 5 - 2, 64))
                                for j in range(4)] for i in range(4)])),
    ]
    records = [one_case(label, matrix, raw, producer, fine=label == "zero")[0]
               for label, matrix in fixtures]
    need(any(not state["source_restoration_exact"] for row in records for state in row["states"]),
         "nonzero full-program rounded restoration witness")
    return dict(schema_version=1, scope="actual compensated generator gates on one data grid",
                sources=sources, collector_ast_sha256=collector_ast, source_schur_trace=trace,
                cases=records, controls=controls(raw, producer),
                physical_tape_execution=False, complete_gaussian_execution=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    path = HERE / "GENERATOR-RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed generator receipt")
    print(json.dumps(dict(status="PASS_RATIONAL_GENERATOR_GATES", cases=len(result["cases"]),
                          generators=sum(x["rank"] for x in result["cases"]),
                          gates=sum(x["gates"] for x in result["cases"]),
                          rounded_states=sum(len(x["states"]) for x in result["cases"]),
                          result_sha256=sha256(canonical(result)).hexdigest()), sort_keys=True))


if __name__ == "__main__":
    main()
