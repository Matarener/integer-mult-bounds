"""Check complete conditioned Toeplitz programs on the fixed-H grammar.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. The retained compiler and source identities belong to their
credited authors. Finite checks support the separate written argument.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dense import DenseSources, FullRoot, NativeProgram
from lowering import DENSE_PREFIX, canonical, need, norm2
from verify import basis_check, difference, exact_native, rejected, upper_report


def identity(E, n):
    return E.Mat([[int(i == j) for j in range(n)] for i in range(n)])


def multiply(E, a, b):
    return E.Mat([[sum((a[i][k] * b[k][j] for k in range(len(b))), E.C())
                   for j in range(len(b[0]))] for i in range(len(a))])


def inverse(E, matrix):
    """Separate exact elimination, with both inverse identities checked."""
    n = len(matrix)
    rows = [list(row) + list(identity(E, n)[i]) for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next(i for i in range(column, n) if rows[i][column] != 0)
        rows[column], rows[pivot] = rows[pivot], rows[column]
        value = rows[column][column]
        rows[column] = [z / value for z in rows[column]]
        for i in range(n):
            if i != column:
                value = rows[i][column]
                rows[i] = [a - value * b for a, b in zip(rows[i], rows[column])]
    result = E.Mat([row[n:] for row in rows])
    need(multiply(E, matrix, result) == multiply(E, result, matrix) == identity(E, n),
         "two exact inverse reference identities")
    return result


def apply_matrix(E, matrix, vector, indices):
    result = E.Vec(vector)
    for i, physical in enumerate(indices):
        result[physical] = sum((matrix[i][j] * vector[address]
                               for j, address in enumerate(indices)), E.C())
    return result


def operator(E, plan, n):
    columns = [E.apply(plan, E.Vec(int(i == j) for i in range(n)))[0] for j in range(n)]
    return E.Mat(zip(*columns))


def check_execution(program, vector, reference):
    E = program.e
    stored = E.apply(program.plan, vector)[0]
    output, statistics, trace = program.execute(vector)
    need(not trace, "compact execution omits per-stage hashes")
    native_error = norm2(difference(output, stored))
    upstream_error = norm2(difference(stored, reference))
    total_error = norm2(difference(output, reference))
    need(native_error <= program.native_error ** 2, "new rounded execution against stored logical program")
    need(upstream_error <= (program.upstream_error * program.radius) ** 2,
         "source coefficient defect against same exact root")
    need(total_error <= program.total_error ** 2, "complete native-to-root error")
    return dict(input_sha256=E.vector_hash(vector), stored_output_sha256=E.vector_hash(stored),
                output_sha256=E.vector_hash(output), reference_sha256=E.vector_hash(reference),
                native_squared_error_upper=upper_report(program.source, native_error, program.native_error ** 2),
                upstream_squared_error_upper=upper_report(program.source, upstream_error,
                                                         (program.upstream_error * program.radius) ** 2),
                total_squared_error_upper=upper_report(program.source, total_error, program.total_error ** 2),
                nonzero_native_error=native_error > 0, statistics=statistics)


def full_case(source, label, matrix, reverse=False, fine=False):
    E, n = source.e, len(matrix)
    indices = list(reversed(range(n))) if reverse else list(range(n))
    root = FullRoot(source, matrix, 4, 18, indices)
    inverse_matrix = inverse(E, matrix)
    incoming = 512 if fine else n.bit_length() + 6
    vector = E.Vec(E.C(Q((3 * i) % 7 - 3, 8 * n), Q((5 * i) % 7 - 2, 8 * n))
                   for i in range(n))
    if fine:
        vector[indices[0]] += E.C(Q(1, 1 << incoming))
    record = dict(label=label, **root.record(), directions=[])
    for backward, reference_matrix in ((False, matrix), (True, inverse_matrix)):
        program = root.lower(backward, incoming)
        exact = apply_matrix(E, reference_matrix, vector, indices)
        row = dict(inverse=backward, **program.record(), execution=check_execution(program, vector, exact))
        if n <= 2:
            row["complete_exact_basis_sha256"] = basis_check(program)
        record["directions"].append(row)
    print("CHECK_NATIVE_FULL", label, flush=True)
    return record


def logical_envelopes(source, plan, n):
    E, maximum = source.e, Q(1)
    for stop in range(len(plan) + 1):
        matrix = operator(E, plan[:stop], n)
        maximum = max(maximum, source.full.norm_upper(matrix), source.full.norm_upper(inverse(E, matrix)))
    return maximum, max(Q(1), source.full.norm_upper(operator(E, plan, n)))


def generic_cases(source):
    E = source.e
    specifications = [
        ("mixed-oriented", 4, [[((3, 0), E.Mat([[1, 0], [E.C(1, 2), 1]])),
                                 ((2,), E.Mat([[E.C(2, -1)]]))], []]),
        ("zero-and-tiny", 2, [[((0, 1), E.Mat([[1, 0], [0, 1]]))],
                               [((1, 0), E.Mat([[1, 0], [E.C(Q(1, 1 << 80), Q(-1, 1 << 81)), 1]]))]]),
        ("one-wire-idle", 1, [[]]),
        ("empty-program", 4, []),
    ]
    rows = []
    for label, n, plan in specifications:
        prefix, endpoint = logical_envelopes(source, plan, n)
        program = NativeProgram(source, n, plan, prefix, endpoint, 1, 18, 512)
        vector = E.Vec(E.C(Q(i + 1, 16 * n), Q(-1, 32 * n)) for i in range(n))
        vector[-1] += E.C(Q(1, 1 << 512))
        reference = E.apply(plan, vector)[0]
        need(exact_native(source, program.reference_stages, vector) == reference,
             "complete generic native endpoint")
        rows.append(dict(label=label, **program.record(), complete_exact_basis_sha256=basis_check(program),
                         execution=check_execution(program, vector, reference)))
    return rows


def segment_cases(source):
    E, records = source.e, []
    for gamma in (1, 16, 1 << 32):
        values = (E.C(0), E.C(gamma), E.C(0, -gamma), E.C(Q(1, 1 << 80), Q(-1, 1 << 81)))
        for kind in ("upper", "lower"):
            for value in values:
                word = source.ns["gateword"](kind, value, gamma)
                wanted = E.Mat([[1, value], [0, 1]]) if kind == "upper" else E.Mat([[1, 0], [value, 1]])
                need(source.word_endpoint(word) == wanted, "zero-safe exact shear endpoint")
                matrices = []
                for i, op in enumerate(word):
                    if op == "H":
                        matrices.append(E.Mat([[Q(1, 2), Q(1, 2)], [Q(1, 2), Q(-1, 2)]]))
                    else:
                        scale = 2 if i and word[i - 1] == "H" else 1
                        matrices.append(E.Mat([[scale * op[0], 0], [0, scale * op[1]]]))
                direct, reciprocal, count = Q(0), Q(0), 0
                for start in range(len(matrices)):
                    product = identity(E, 2)
                    for matrix in matrices[start:]:
                        product = multiply(E, matrix, product)
                        direct = max(direct, source.full.norm_upper(product))
                        reciprocal = max(reciprocal, source.full.norm_upper(inverse(E, product)))
                        count += 1
                need(max(direct, reciprocal) <= 4096 * gamma, "native shear segments and inverse segments")
                records.append(dict(kind=kind, gamma=str(gamma), value=value.record(), segments=count,
                                    direct_component_envelope=str(direct), inverse_component_envelope=str(reciprocal)))
    return records


def endpoint_control(source):
    E, q = source.e, 1 << 16
    plan = [[((0, 1), E.Mat([[Q(1, q), 0], [0, q]]))],
            [((0, 1), identity(E, 2))],
            [((0, 1), E.Mat([[q * q, 0], [0, Q(1, q * q)]]))]]
    prefix, endpoint = logical_envelopes(source, plan, 2)
    need(prefix == endpoint == q, "exact scaled logical prefix and endpoint bounds")
    program = NativeProgram(source, 2, plan, prefix, endpoint, 1, 18, 8)
    stop = program.layers[1]["begin"] + 5
    columns = [exact_native(source, program.reference_stages[:stop], E.Vec(int(i == j) for i in range(2)))
               for j in range(2)]
    partial = E.Mat(zip(*columns))
    c = 2 * q * q + 1
    need(partial == E.Mat([[Q(-5, 4 * c * q), 0], [0, q]]), "actual zero-shear intermediate prefix")
    suffix = multiply(E, operator(E, plan, 2), inverse(E, partial))
    suffix_bound = source.full.norm_upper(suffix)
    need(suffix_bound == Q(4 * c * q * q, 5) > program.compiled_bound,
         "unit-endpoint suffix allowance fails on admitted nonunitary program")
    need(suffix_bound <= endpoint * program.compiled_bound, "corrected endpoint suffix allowance")
    vector = E.Vec([Q(1, 16), Q(-1, 32)])
    return dict(q=q, logical_prefix=str(prefix), endpoint=str(endpoint), native_prefix=str(program.compiled_bound),
                intermediate_sha256=source.matrix_hash(partial), suffix_norm=str(suffix_bound),
                ratio_to_invalid_allowance=str(suffix_bound / program.compiled_bound),
                execution=check_execution(program, vector, E.apply(plan, vector)[0]))


def controls(source):
    E, rows = source.e, []
    rows.append(rejected(lambda: FullRoot(source, E.Mat([[0, 1], [1, 0]]), 1, 18), "singular-leading-section"))
    rows.append(rejected(lambda: FullRoot(source, E.Mat([[1, 2], [3, 4]]), 1, 18), "non-Toeplitz-root"))
    root = FullRoot(source, E.Mat([[E.C(Q(1, 3), Q(1, 7))]]), 1, 18)
    forward, backward = root.lower(False, 8), root.lower(True, 8)
    vector = E.Vec([Q(1, 16)])
    a = root.plan[0][0][1][0][0]
    need(root.inverse_plan[0][0][1][0][0] == 1 / a and a.conjugate() != 1 / a,
         "stored reciprocal differs from global adjoint")
    rows.append("stored-inverse-requires-reciprocals")
    rows.append(rejected(lambda: forward.execute(E.Vec([Q(1, 1 << 9)])), "underdeclared-incoming-grid"))
    rows.append(rejected(lambda: forward.execute(E.Vec([2])), "underdeclared-radius"))
    rows.append(rejected(lambda: root.lower(False, True), "boolean-incoming-grid"))
    rows.append(rejected(lambda: NativeProgram(source, 2, [[((0, 1), E.Mat([[1, 2], [3, 4]]))]],
                                             16, 16, 1, 18), "unsupported-two-wire-gate"))
    rows.append(rejected(lambda: NativeProgram(source, 2, [[((0, 0), identity(E, 2))]],
                                             1, 1, 1, 18), "duplicate-wire-ownership"))
    rows.append(rejected(lambda: NativeProgram(source, 2, [[]], 1, 1, 1, 18, data_bits=8), "underfunded-native-grid"))
    rows.append(rejected(lambda: NativeProgram(source, 1, [[((0,), E.Mat([[0]]))]], 1, 1, 1, 18), "zero-scalar"))
    rows.append(rejected(lambda: source.ns["u3"](E.C(0)), "unshifted-zero-shear-division"))
    z = E.C(1, 2)
    lower = source.ns["gateword"]("lower", z, 4)
    wrong = [op if op == "H" else tuple(a.conjugate() for a in op) for op in lower]
    need(source.word_endpoint(wrong) != source.word_endpoint(lower), "conjugate transpose changes complex lower shear")
    rows.append("ordinary-transpose-is-required")
    old = root.matrix[0][0]
    root.matrix[0][0] += 1
    rows.append(rejected(lambda: forward.execute(vector), "changed-admitted-root"))
    root.matrix[0][0] = old
    old = root.builder.bound["execution_bound"]
    root.builder.bound["execution_bound"] += 1
    rows.append(rejected(lambda: backward.execute(vector), "changed-full-prefix-contract"))
    root.builder.bound["execution_bound"] = old
    for name in ("lam", "q", "radius", "target"):
        old = getattr(root, name)
        setattr(root, name, old + 1)
        rows.append(rejected(lambda: root.lower(), "changed-root-" + name))
        setattr(root, name, old)
    old = root.indices[:]
    root.indices[0] = 1
    rows.append(rejected(lambda: root.lower(), "changed-root-wire-order"))
    root.indices = old
    old = backward.endpoint
    backward.endpoint = 1
    rows.append(rejected(lambda: backward.execute(vector), "changed-native-endpoint-envelope"))
    backward.endpoint = old
    old = root.plan[0][0]
    root.plan[0][0] = ((0,), E.Mat([[1]]))
    rows.append(rejected(lambda: forward.execute(vector), "changed-stored-logical-plan"))
    root.plan[0][0] = old
    old = forward.stages[0]
    forward.stages[0] = ("D", E.Vec([1]))
    rows.append(rejected(lambda: forward.execute(vector), "changed-prepared-diagonal-page"))
    forward.stages[0] = old
    rows.append(rejected(lambda: DenseSources({DENSE_PREFIX + "full.py": source.raw[DENSE_PREFIX + "full.py"] + b"\n"}),
                         "changed-frozen-full-source"))
    try:
        source.raw[DENSE_PREFIX + "full.py"] = b"changed"
    except TypeError:
        rows.append("authenticated-byte-map-is-read-only")
    else:
        raise ValueError("authenticated source map accepted a replacement")
    need(canonical({"n": 1}) != canonical({"n": True}), "typed dense receipt")
    rows.append("typed-receipt")
    return rows


def run(quick=False):
    source = DenseSources()
    E = source.e
    fixtures = [("complex-scalar", E.Mat([[E.C(Q(1, 3), Q(1, 7))]]), False, False),
                ("small-pivot", E.Mat([[Q(1, 1 << 80)]]), False, False),
                ("large-scalar", E.Mat([[E.C(1 << 30, -(1 << 28))]]), False, False)]
    for n in (2, 4, 8):
        matrix = E.Mat([[E.C(1, Q(1, 16)) if i == j else
                         E.C(Q(-1 if (i - j) % 2 else 1, 32 * n), Q(i - j, 64 * n))
                         for j in range(n)] for i in range(n)])
        fixtures.append(("complex-near-identity-" + str(n), matrix, n >= 4, n == 4))
    for n in (2, 4):
        fixtures.append(("indefinite-" + str(n), E.Mat([[1 if i == j else 2 if abs(i - j) == 1 else 0
                                                        for j in range(n)] for i in range(n)]), True, False))
    fixtures.append(("half-shift-Gaussian", E.Mat([[Q(1, 2) ** ((i - j) ** 2 - (i - j))
                                                   for j in range(4)] for i in range(4)]), False, False))
    fixtures.append(("unequal-subtrees", E.Mat([[1 if i == j else Q(1, 16) if abs(i - j) == 4
                                                else Q(1, 32) if abs(i - j) == 5 else 0
                                                for j in range(8)] for i in range(8)]), False, False))
    fixtures.append(("zero-call-identity-16", identity(E, 16), True, False))
    if quick:
        fixtures = [fixtures[0], fixtures[3]]
    cases = [full_case(source, *fixture) for fixture in fixtures]
    result = dict(schema_version=1, scope="actual conditioned full Toeplitz and stored inverse fixed-H execution",
                  sources=source.seals, cases=cases, generic_cases=generic_cases(source),
                  endpoint_factor_control=endpoint_control(source))
    if not quick:
        result.update(word_cases=segment_cases(source), controls=controls(source),
                      actual_full_source_execution=True, native_stage_arithmetic=True,
                      physical_root_execution=False, physical_tape_execution=False,
                      complete_tensor_execution=False, dyadic_programs_exact_inverse_pair=False,
                      independent_transcendental_backend=False, universal_proof_kernel=False)
        need(any(d["execution"]["nonzero_native_error"] for row in cases for d in row["directions"]),
             "nonzero complete rounded error witness")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    need(not (args.quick and args.write_result), "diagnostic cannot replace complete receipt")
    result = run(args.quick)
    if args.quick:
        print("PASS_NATIVE_FULL_DIAGNOSTIC", len(result["cases"]))
        return
    path = HERE / "DENSE-RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed conditioned native receipt")
    directions = [d for row in result["cases"] for d in row["directions"]]
    print(json.dumps(dict(status="PASS_CONDITIONED_TOEPLITZ_FIXED_H", cases=len(result["cases"]),
                          directions=len(directions), generic_cases=len(result["generic_cases"]),
                          word_cases=len(result["word_cases"]), controls=len(result["controls"]),
                          native_stages=sum(d["counts"]["primitive_stages"] for d in directions),
                          rounded_outputs=sum(d["execution"]["statistics"]["complex_roundings"] for d in directions),
                          result_sha256=sha256(canonical(result)).hexdigest()), sort_keys=True))


if __name__ == "__main__":
    main()
