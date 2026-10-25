"""Check parity gates, macro identities, both directions and one data grid.

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
from exact import (C, Mat, Vec, adjoint, apply, ceil_log2, component_l1, eye, inverse_gate,
                   multiply, need, norm2, qheight, upper, vector_hash)
from triangular import Plan, Triangle, allocation
from verify import (CIRCUIT, ORACLE, authenticate, canonical, mv, operator,
                    plan_hash, rejected)


def reference(symbol, indices):
    n = len(symbol)
    result = eye(n)
    for i in range(n):
        for j in range(n):
            result[indices[i]][indices[j]] = symbol[i - j] if i >= j else C()
    return result


def eliminate(matrix):
    """Separate exact Gauss-Jordan inverse; no series routine from the compiler."""
    n = len(matrix)
    rows = [list(row) + list(unit) for row, unit in zip(matrix, eye(n))]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j] != 0)
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [x / scale for x in rows[j]]
        for i in range(n):
            if i != j:
                scale = rows[i][j]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[j])]
    need(Mat([row[:n] for row in rows]) == eye(n), "Gauss-Jordan inverse reference")
    return Mat([row[n:] for row in rows])


def frobenius_error(left, right):
    return sum(((a - b).norm2() for x, y in zip(left, right)
                for a, b in zip(x, y)), Q(0))


def macro_reference(block, n):
    result, used = eye(n), set()
    for piece in block["pieces"]:
        ids, wanted = piece["ids"], piece["ideal"]
        need(not used.intersection(ids), "disjoint macro reference supports")
        used.update(ids)
        if piece["kind"] == "leaf":
            result[ids[0]][ids[0]] = wanted[0][0]
        else:
            m = len(ids) // 2
            for i in range(m):
                for j in range(m):
                    result[ids[m + i]][ids[j]] = wanted[i][j]
    need(len(used) == n, "complete macro wire coverage")
    return result


def macro_check(plan, wanted, bound):
    n, cursor, product = len(wanted), 0, eye(len(wanted))
    partitions = []
    for block in plan.blocks:
        need(block["start"] == cursor and block["stop"] > cursor,
             "consecutive nonempty macro partitions")
        cursor = block["stop"]
        need(max(piece["error"] for piece in block["pieces"]) <= bound["epsilon"],
             "direct-sum macro defect")
        product = multiply(macro_reference(block, n), product)
        partitions.append([block["start"], block["stop"],
                           [piece["ids"] for piece in block["pieces"]]])
    need(cursor == len(plan) and product == wanted, "exact retained parity factorization")
    need(len(partitions) == bound["macro_layers"], "macro depth certificate")
    return partitions


def structure(plan, bound):
    height = 0
    for layer in plan:
        used = set()
        for ids, gate in layer:
            need(len(ids) == len(gate) in (1, 2), "one/two-wire parity gate")
            need(len(set(ids)) == len(ids) and not used.intersection(ids),
                 "disjoint physical parity layer")
            need(all(0 <= i < bound["n"] for i in ids), "owned parity wires")
            used.update(ids)
            need(multiply(inverse_gate(gate), gate) == eye(len(gate)), "stored gate inverse")
            for row in gate:
                for entry in row:
                    height = max(height, qheight(entry.re), qheight(entry.im))
    need(height <= bound["coefficient_height_bound"], "forward/inverse coefficient width")
    return height


def one_case(symbol, raw, reverse=False, fine=False, label=""):
    n = len(symbol)
    indices = list(reversed(range(n))) if reverse else list(range(n))
    vectors = [
        Vec(C(Q((3 * i + 1) % 7 - 3, 8), Q((5 * i + 2) % 9 - 4, 8)) for i in range(n)),
        Vec(C((-1) ** i * (1 << 12), (1 << 10) * (i % 2)) for i in range(n)),
    ]
    if fine:
        vectors.append(Vec([C(Q(1, 1 << 100))] + [C()] * (n - 1)))
    radius = max(Q(1), *(component_l1(v) for v in vectors))
    incoming = max(x.denominator.bit_length() - 1 for v in vectors for z in v
                   for x in (z.re, z.im))
    bound = allocation(n, radius, 20, incoming)
    builder = Triangle(bound, raw[CIRCUIT], raw[ORACLE])
    plan = builder.plan(symbol, indices)
    phase_count = len(builder.phases.certificates)
    inverse = builder.inverse(plan)
    need(len(builder.phases.certificates) == phase_count, "inverse reuses phase coefficients")
    wanted = reference(symbol, indices)
    intended_inverse = eliminate(wanted)
    partitions = macro_check(plan, wanted, bound)
    height = max(structure(plan, bound), structure(inverse, bound))
    actual = operator(plan, n)
    actual_inverse = operator(inverse, n)
    need(multiply(actual_inverse, actual) == eye(n), "exact stored circuit inverse")
    forward_error = frobenius_error(actual, wanted)
    inverse_error = frobenius_error(actual_inverse, intended_inverse)
    need(max(forward_error, inverse_error) <= n * bound["coefficient_error"] ** 2,
         "two-sided independent endpoint references")
    vectors.append(Vec([C(Q(2, 1 << bound["data_bits"]))] + [C()] * (n - 1)))
    final_bound = allocation(n, radius, 20, bound["data_bits"])
    need(all(final_bound[key] == value for key, value in bound.items()
             if key != "incoming_bits"), "micro fixture preserves triangular allocation")
    bound = final_bound
    states = []
    for direction, program, actual_matrix, ideal_matrix in (
            ("forward", plan, actual, wanted),
            ("inverse", inverse, actual_inverse, intended_inverse)):
        for vector in vectors:
            need(norm2(vector) <= radius ** 2, "triangle input radius")
            output, stats = apply(program, vector, bound["data_bits"])
            rational = mv(actual_matrix, vector)
            ideal = mv(ideal_matrix, vector)
            coeff = norm2(rational - ideal)
            rounding = norm2(output - rational)
            total = norm2(output - ideal)
            need(coeff <= (bound["coefficient_error"] * radius) ** 2,
                 "triangle coefficient error")
            need(rounding <= bound["rounding_error"] ** 2, "triangle global data error")
            need(total <= bound["total_error"] ** 2, "triangle complete target error")
            need(stats["max_observed_height"] <= bound["temporary_bits"],
                 "triangle observed temporary width")
            need(stats["max_grid_numerator_bits"] + 1 <= bound["data_bits"] + bound["integer_bits"]
                 and stats["max_reduced_fractional_bits"] <= bound["data_bits"],
                 "triangle signed canonical grid width")
            states.append(dict(direction=direction, input_sha256=vector_hash(vector),
                               output_sha256=vector_hash(output),
                               coefficient_squared_upper=str(upper(coeff)),
                               rounding_squared_upper=str(upper(rounding)),
                               total_squared_upper=str(upper(total)), statistics=stats))
    rounded_forward, _ = apply(plan, vectors[0], bound["data_bits"])
    restored, roundtrip_stats = apply(inverse, rounded_forward, bound["data_bits"])
    roundtrip = norm2(restored - vectors[0])
    allowance = (2 * bound["total_error"] + bound["coefficient_error"]
                 * (2 * radius + bound["total_error"]) + bound["rounding_error"])
    need(roundtrip <= allowance ** 2, "charged rounded round trip")
    roundtrip_radius = 2 * radius + bound["total_error"]
    roundtrip_amplitude = (bound["physical_prefix_suffix_bound"] * roundtrip_radius
                           + bound["layer_bound"] * bound["segment_bound"] * n
                           * Q(1, 1 << bound["data_bits"]))
    roundtrip_integer = max(1, ceil_log2(max(Q(1), roundtrip_amplitude))) + 2
    roundtrip_temporary = (2 * bound["data_bits"] + 8 * bound["coefficient_height_bound"]
                           + 2 * roundtrip_integer + 32)
    need(roundtrip_stats["max_grid_numerator_bits"] + 1
         <= bound["data_bits"] + roundtrip_integer
         and roundtrip_stats["max_observed_height"] <= roundtrip_temporary,
         "enlarged second-pass round-trip width")
    record_bound = {k: str(v) if isinstance(v, Q) else v for k, v in bound.items()}
    return dict(label=label, n=n, indices=indices, symbol=[x.record() for x in symbol],
                budget=record_bound, partitions=partitions, layers=len(plan),
                gates=sum(map(len, plan)), children=len(builder.children),
                leaves=len(builder.leaves), triangle_nodes=builder.stats["triangle_nodes"],
                source_ast_sha256=builder.original_ast, adapted_ast_sha256=builder.adapted_ast,
                plan_sha256=plan_hash(plan), inverse_sha256=plan_hash(inverse),
                max_coefficient_height=height,
                forward_frobenius_squared_upper=str(upper(forward_error)),
                inverse_frobenius_squared_upper=str(upper(inverse_error)),
                rounded_roundtrip_squared_upper=str(upper(roundtrip)),
                rounded_roundtrip_bound=str(allowance),
                roundtrip_width=dict(radius=str(roundtrip_radius),
                                     integer_bits=roundtrip_integer,
                                     temporary_bits=roundtrip_temporary,
                                     statistics=roundtrip_stats), states=states,
                phases=builder.phases.record())


def controls(raw):
    symbol = Vec([C(Q(3, 4), Q(1, 16)), C(Q(1, 16)), C(Q(-1, 32)), C(Q(1, 32))])
    bound = allocation(4, Q(4), 20)
    def new():
        return Triangle(bound, raw[CIRCUIT], raw[ORACLE])
    out = []
    out.append(rejected(lambda: new().plan(Vec([Q(1, 4), 0, 0, 0])), "near-identity-admission"))
    out.append(rejected(lambda: allocation(3, 1, 20), "nondyadic-size"))
    out.append(rejected(lambda: new().plan([1.0, 0, 0, 0]), "floating-coefficients"))
    out.append(rejected(lambda: new().leaf([0], Vec([0])), "zero-leaf-margin"))
    builder = new()
    plan = builder.plan(symbol)
    wanted = reference(symbol, list(range(4)))
    wrong_inverse = [[(ids, adjoint(gate) if len(ids) == 1 else inverse_gate(gate))
                      for ids, gate in layer] for layer in reversed(plan)]
    need(frobenius_error(operator(wrong_inverse, 4), eliminate(wanted))
         > 4 * bound["coefficient_error"] ** 2, "adjoint leaf must fail inverse reference")
    out.append("leaf-adjoint-instead-of-reciprocal")
    wrong_order = [[(ids, inverse_gate(gate)) for ids, gate in layer] for layer in plan]
    need(frobenius_error(operator(wrong_order, 4), eliminate(wanted))
         > 4 * bound["coefficient_error"] ** 2, "wrong inverse order must fail")
    out.append("inverse-layer-order")
    builder = new()
    original_conv = builder.namespace["conv"]
    calls = [0]
    def missing_shift(a, b, n):
        result = original_conv(a, b, n)
        calls[0] += 1
        # The second convolution feeds [0, conv(...)[:-1]] in s.
        # Changing it changes the exact Schur complement while retaining topology.
        return Vec(result) * 0 if calls[0] == 2 else result
    builder.namespace["conv"] = missing_shift
    mutant = builder.plan(symbol)
    out.append(rejected(lambda: macro_check(mutant, wanted, bound), "omitted-schur-correction"))
    builder = new()
    original_parallel = builder.parallel
    def serial(a, b):
        merged = original_parallel(a, b)
        return Plan(list(a) + list(b), merged.blocks)
    builder.namespace["parallel"] = serial
    out.append(rejected(lambda: macro_check(builder.plan(symbol), wanted, bound),
                        "serialized-parallel-middle"))
    builder = new()
    original_shear = builder.shear
    builder.namespace["toeplitz_shear"] = lambda target, source, matrix: original_shear(source, target, matrix)
    out.append(rejected(lambda: macro_check(builder.plan(symbol), wanted, bound),
                        "swapped-parity-bank-routing"))
    need(Vec([1, 2]).copy() * 0 == Vec([0, 0]), "NumPy copy/scalar semantics")
    out.append("exact-vector-copy-zero-semantics")
    out.append(rejected(lambda: apply(plan, Vec([Q(1, 1 << 90), 0, 0, 0]), 20),
                        "discarded-incoming-grid"))
    out.append(rejected(lambda: need(
        32 * bound["layer_bound"] * bound["ideal_bound"] * 4 * Q(1, 1 << 4)
        <= Q(1, 1 << 20), "rounding budget"), "underfunded-global-grid"))
    return out


def run():
    raw, sources = authenticate()
    cases = []
    for n in (1, 2, 4, 8):
        symbol = Vec([C(Q(4, 5), Q(1, 35))]
                     + [C(Q((-1) ** j, 32 * n), Q(1, 64 * n)) for j in range(1, n)])
        cases.append(one_case(symbol, raw, reverse=n >= 4, fine=n == 8, label="complex-rational"))
        boundary = Vec([Q(1, 2)] + [0] * (n - 1))
        cases.append(one_case(boundary, raw, label="half-identity-boundary"))
    n = 16
    symbol = Vec([1] + [C(Q((-1) ** j, 128), Q(1, 256)) for j in range(1, n)])
    cases.append(one_case(symbol, raw, reverse=True, label="deep-parity"))
    symbol = Vec([1, 0, Q(1, 8), 0, Q(-1, 16), 0, Q(1, 32), 0])
    cases.append(one_case(symbol, raw, label="zero-odd-polynomial"))
    need(any(Q(row["rounded_roundtrip_squared_upper"]) > 0 for row in cases),
         "nonzero rounded inverse-restoration witness")
    return dict(schema_version=1, scope="retained parity recursion and inverse on one data grid",
                sources=sources, cases=cases, controls=controls(raw),
                physical_tape_execution=False, full_generator_execution=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    path = HERE / "TRIANGLE-RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed triangular receipt")
    print(json.dumps(dict(status="PASS_RATIONAL_PARITY_TRIANGLE", cases=len(result["cases"]),
                          gates=sum(row["gates"] for row in result["cases"]),
                          rounded_states=sum(len(row["states"]) for row in result["cases"]),
                          result_sha256=sha256(canonical(result)).hexdigest()), sort_keys=True))


if __name__ == "__main__":
    main()
