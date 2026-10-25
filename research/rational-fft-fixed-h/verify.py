"""Check retained fixed-H words, routing and complete rounded FFT executions.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. This is finite evidence for the separately written proof.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lowering import FFT, K, Sources, TENSOR, canonical, need, norm2, stage_hash


def rejected(operation, label):
    try:
        operation()
    except (ValueError, AssertionError):
        return label
    raise ValueError("control unexpectedly passed: " + label)


def exact_native(source, stages, vector, raw=False):
    E = source.e
    state = E.Vec(vector)
    for kind, value in stages:
        if kind == "D":
            need(len(value) == len(state), "complete coefficient page")
            state = E.Vec(a * x for a, x in zip(value, state))
        else:
            step = 1 << value
            for i in range(len(state)):
                if not i & step:
                    a, b = state[i], state[i + step]
                    denominator = 1 if raw else 2
                    state[i], state[i + step] = (a + b) / denominator, (a - b) / denominator
    return state


def difference(a, b):
    need(len(a) == len(b), "complete output comparison")
    return [x - y for x, y in zip(a, b)]


def upper_report(source, value, allowance):
    need(0 <= value <= allowance, "reported exact error allowance")
    if allowance == 0:
        return "0"
    bits = max(160, source.e.ceil_log2(1 / allowance) + 16)
    return str(min(allowance, source.e.upper(value, bits)))


def scale_interval(interval, scalar):
    ends = [x * scalar for x in interval]
    return min(ends), max(ends)


def add_interval(a, b):
    return a[0] + b[0], a[1] + b[1]


def ideal_squared_error(program, vector, output):
    source, indices = program.source, program.indices
    n = len(indices)
    normalization = source.engine.inverse_sqrt_box(n, program.phases.working_bits)
    boxes = {i: ((z.re, z.re), (z.im, z.im)) for i, z in enumerate(vector)}
    for row, physical_row in enumerate(indices):
        real, imaginary = (Q(0), Q(0)), (Q(0), Q(0))
        for col, physical_col in enumerate(indices):
            phase = program.phases.box(n, (1 if program.adjoint else -1) * row * col)
            z = vector[physical_col]
            real = add_interval(real, add_interval(scale_interval(phase[0], z.re),
                                                   scale_interval(phase[1], -z.im)))
            imaginary = add_interval(imaginary, add_interval(scale_interval(phase[0], z.im),
                                                             scale_interval(phase[1], z.re)))
        intervals = []
        for part in (real, imaginary):
            corners = [a * b for a in part for b in normalization]
            intervals.append((min(corners), max(corners)))
        boxes[physical_row] = tuple(intervals)
    error = Q(0)
    for i, z in enumerate(output):
        for value, interval in zip((z.re, z.im), boxes[i]):
            error += max(abs(value - interval[0]), abs(value - interval[1])) ** 2
    return error


def basis_check(program):
    E, source = program.e, program.source
    columns = []
    for j in range(program.size):
        vector = E.Vec(int(i == j) for i in range(program.size))
        expected = E.apply(program.plan, vector)[0]
        actual = exact_native(source, program.reference_stages, vector)
        need(actual == expected, "complete exact native matrix equals retained FFT")
        columns.append(actual)
    return E.vector_hash(z for column in columns for z in column)


def one_case(source, label, size, indices, target=18, incoming=0, radius=1, adjoint=False):
    incoming = max(incoming, size.bit_length() + 2)
    program = FFT(source, size, indices, radius, target, incoming, adjoint=adjoint)
    E = source.e
    vector = E.Vec(E.C(Q((3 * i) % 7 - 3, 8 * size), Q((5 * i) % 7 - 3, 8 * size))
                   for i in range(size))
    if radius >= 2:
        vector = E.Vec(z * (Q(radius) / 2) for z in vector)
    if incoming >= 512:
        fine = next((i for i in range(size) if i not in indices), 0)
        vector[fine] = E.C(Q(1, 1 << incoming))
    expected = E.apply(program.plan, vector)[0]
    exact = exact_native(source, program.reference_stages, vector)
    need(exact == expected, "exact complete forward or stored-adjoint lowering")
    output, statistics, trace = program.execute(vector, capture=True)
    rational_error = norm2(difference(output, expected))
    need(rational_error <= program.native_error ** 2, "complete native error against rational FFT")
    ideal_error = ideal_squared_error(program, vector, output)
    need(ideal_error <= program.total_error ** 2, "complete independent-formula Fourier enclosure")
    matrix_hash = basis_check(program) if size <= 8 else None
    spectators = [i for i in range(size) if i not in indices]
    spectator_error = norm2([output[i] - vector[i] for i in spectators])
    record = program.record()
    record.update(label=label, input_sha256=E.vector_hash(vector), output_sha256=E.vector_hash(output),
                  rational_target_sha256=E.vector_hash(expected), exact_matrix_sha256=matrix_hash,
                  rounded_rational_error_squared_upper=upper_report(source, rational_error, program.native_error ** 2),
                  ideal_error_squared_upper=upper_report(source, ideal_error, program.total_error ** 2),
                  nonzero_rounded_error=rational_error > 0,
                  nonzero_spectator_error=spectator_error > 0,
                  spectator_error_squared_upper=upper_report(source, spectator_error, program.native_error ** 2),
                  statistics=statistics, trace=trace)
    print("CHECK_FIXED_H_FFT", label, flush=True)
    return record, program, vector, output


def segment_envelopes(source, word):
    E, matrices = source.e, []
    for i, operation in enumerate(word):
        if operation == "H":
            matrices.append(E.Mat([[Q(1, 2), Q(1, 2)], [Q(1, 2), Q(-1, 2)]]))
        else:
            scale = 2 if i and word[i - 1] == "H" else 1
            matrices.append(E.Mat([[scale * operation[0], 0], [0, scale * operation[1]]]))
    forward, inverse, count = Q(0), Q(0), 0
    for first in range(len(matrices)):
        product = E.Mat([[1, 0], [0, 1]])
        for matrix in matrices[first:]:
            product = E.Mat([[sum((matrix[i][k] * product[k][j] for k in range(2)), E.C())
                              for j in range(2)] for i in range(2)])
            a, b = product[0]
            c, d = product[1]
            determinant = a * d - b * c
            need(determinant != 0, "invertible exact native segment")
            inv = E.Mat([[d / determinant, -b / determinant], [-c / determinant, a / determinant]])
            forward = max(forward, sum(z.norm2() for row in product for z in row))
            inverse = max(inverse, sum(z.norm2() for row in inv for z in row))
            count += 1
    need(max(forward, inverse) <= 4096 ** 2, "independent Frobenius segment envelope")
    return dict(segments=count, forward_frobenius_squared_upper=str(E.upper(forward)),
                inverse_frobenius_squared_upper=str(E.upper(inverse)))


def word_cases(source):
    E, records = source.e, []
    for a, b in ((Q(3, 5), Q(4, 5)), (Q(33, 65), Q(56, 65))):
        for w in (E.C(1), E.C(-1), E.C(0, 1), E.C(3, 4) / 5):
            for inverse in (False, True):
                word = source.butterfly_word(a, b, w, inverse)
                wanted = E.Mat([[a, b * w], [b, -a * w]])
                if inverse:
                    wanted = E.adjoint(wanted)
                need(source.word_endpoint(word) == wanted, "standalone six-H butterfly identity")
                coefficients = [z for op in word if op != "H" for z in op]
                need(all(z.norm2() <= 9 and (1 / z).norm2() <= 400 ** 2 for z in coefficients),
                     "raw direct and reciprocal coefficient bounds")
                records.append(dict(a=str(a), b=str(b), phase=w.record(), adjoint=inverse,
                                    endpoint_sha256=source.matrix_hash(wanted),
                                    envelopes=segment_envelopes(source, word)))
    return records


def controls(source, cases):
    E, results = source.e, []
    program = next(row[1] for row in cases if row[1].size == 4 and not row[1].adjoint
                   and len(row[1].indices) == 4)
    row = next(row for row in cases if row[1] is program)
    vector = row[2]
    expected = E.apply(program.plan, vector)[0]
    wrong = exact_native(source, program.raw_stages, vector)
    results.append(rejected(lambda: need(wrong == expected, "missing H0 compensation"),
                            "omitted-native-scale-restoration"))
    a, b, w = Q(3, 5), Q(4, 5), E.C(3, 4) / 5
    actual = E.Mat([[a, b * w], [b, -a * w]])
    old_word = source.ns["gateword"]("fft", w)
    results.append(rejected(lambda: need(source.word_endpoint(old_word) == actual, "old FFT shape"),
                            "unnormalized-source-fft-word-is-not-rational-butterfly"))
    wrong_adjoint = source.butterfly_word(a, b, w.conjugate())
    results.append(rejected(lambda: need(source.word_endpoint(wrong_adjoint) == E.adjoint(actual), "adjoint orientation"),
                            "twiddle-conjugation-alone-is-not-the-adjoint"))
    pairs = [(3, 1), (0, 2)]
    words = [source.butterfly_word(a, b, w), source.ns["gateword"]("diag", (1, 1))]
    routed = source.ns["local_layer"](4, pairs, words)
    expected_partial = E.apply([[(pairs[0], actual)]], vector)[0]
    need(exact_native(source, routed, vector, raw=True) == expected_partial, "oriented noninvolutive route")
    sorted_route = source.ns["local_layer"](4, [tuple(sorted(p)) for p in pairs], words)
    results.append(rejected(lambda: need(exact_native(source, sorted_route, vector, raw=True)
                                         == expected_partial, "sorted pair changes gate"), "discarded-pair-orientation"))
    all_one = [(E.C(1), E.C(1)) if op != "H" else op for op in words[1]]
    bad_idle = source.ns["local_layer"](4, pairs, [words[0], all_one])
    results.append(rejected(lambda: need(exact_native(source, bad_idle, vector, raw=True)
                                         == expected_partial, "idle word needs compensation"), "all-one-idle-padding"))
    missing_half = list(routed)
    half_index = next(i for i, (kind, value) in enumerate(missing_half)
                      if kind == "D" and all(z == Q(1, 2) for z in value))
    missing_half[half_index] = ("D", E.Vec([1] * 4))
    results.append(rejected(lambda: need(exact_native(source, missing_half, vector, raw=True)
                                         == expected_partial, "switch half"), "omitted-switch-half"))
    results.append(rejected(lambda: source.ns["u3"](E.C(0)), "source-zero-shear-assertion-active"))
    results.append(rejected(lambda: source.ns["gateword"]("diag", (0, 1)), "source-zero-diagonal-assertion-active"))
    results.append(rejected(lambda: FFT(source, 4, [0, 0], 1, 18), "duplicate-active-wire"))
    results.append(rejected(lambda: FFT(source, 4, [False, 1], 1, 18), "boolean-wire-id"))
    results.append(rejected(lambda: FFT(source, 4, [-1, 1], 1, 18), "negative-wire-id"))
    results.append(rejected(lambda: FFT(source, 4, [0, 4], 1, 18), "out-of-range-wire-id"))
    results.append(rejected(lambda: FFT(source, 3, [0, 1], 1, 18), "nondyadic-field"))
    results.append(rejected(lambda: FFT(source, 4, [0, 1, 2], 1, 18), "nondyadic-active-FFT"))
    results.append(rejected(lambda: FFT(source, 4, [0, 1], 1.0, 18), "floating-radius"))
    results.append(rejected(lambda: FFT(source, 4, [0, 1], 1, 18, phase_bits=3), "underfunded-phase-precision"))
    results.append(rejected(lambda: FFT(source, 4, [0, 1], 1, 18, data_bits=8), "underfunded-native-grid"))
    bad_input = E.Vec(vector)
    bad_input[0] = E.C(Q(1, 1 << (program.incoming + 1)))
    results.append(rejected(lambda: program.execute(bad_input), "underdeclared-incoming-grid"))
    bad_input[0] = E.C(2)
    results.append(rejected(lambda: program.execute(bad_input), "underdeclared-input-radius"))
    first_diagonal = next(i for i, (kind, _) in enumerate(program.stages) if kind == "D")
    old_page = program.stages[first_diagonal]
    replacement = E.Vec(old_page[1])
    replacement[0] += 1
    program.stages[first_diagonal] = ("D", replacement)
    results.append(rejected(lambda: program.execute(vector), "changed-prepared-coefficient-page"))
    program.stages[first_diagonal] = old_page
    results.append(rejected(lambda: Sources({TENSOR: source.raw[TENSOR] + b"\n# changed\n"}),
                            "source-byte-corruption"))
    fine = next(row for row in cases if row[0]["label"] == "spectator-fine")
    need(fine[0]["nonzero_spectator_error"], "inactive rounding has a nonzero error witness")
    results.append("inactive-word-error-is-paid")
    need(canonical({"count": 1}) != canonical({"count": True}), "typed scientific receipt")
    return results + ["typed-receipt"]


def run(quick=False):
    source = Sources()
    specifications = [
        ("singleton", 1, [0], 18, 0, 1, False),
        ("two-forward", 2, [0, 1], 18, 0, 1, False),
        ("two-adjoint", 2, [0, 1], 18, 0, 1, True),
        ("spectator-fine", 4, [3, 1], 18, 512, 1, False),
        ("four-forward", 4, [0, 1, 2, 3], 18, 0, 1, False),
        ("four-reversed-adjoint", 4, [3, 2, 1, 0], 24, 0, 1, True),
        ("eight-permuted", 8, [5, 1, 7, 3, 0, 6, 2, 4], 22, 0, 1, False),
        ("eight-partial-adjoint", 8, [6, 1, 4, 3], 20, 0, 1, True),
        ("sixteen-forward", 16, list(range(16)), 24, 0, 1, False),
        ("thirtytwo-adjoint", 32, list(reversed(range(32))), 20, 0, 1, True),
        ("sixtyfour-forward", 64, list(range(64)), 18, 0, 1, False),
        ("large-radius", 8, list(range(8)), 18, 0, 1 << 20, False),
        ("idle-field", 4, [2], 18, 0, 1, True),
    ]
    if quick:
        specifications = specifications[:4]
    cases = [one_case(source, *spec) for spec in specifications]
    if quick:
        return dict(cases=[row[0] for row in cases])
    need(any(row[0]["nonzero_rounded_error"] for row in cases), "nonzero native rounding evidence")
    return dict(schema_version=1, scope="retained rational FFT and stored-adjoint fixed-H stage lowering",
                sources=source.seals, tensor_ast_sha256=source.tensor_ast,
                word_cases=word_cases(source), cases=[row[0] for row in cases],
                controls=controls(source, cases),
                source_FFT_execution=True, source_Benes_execution=True, native_stage_arithmetic=True,
                physical_root_execution=False, physical_tape_execution=False,
                complete_tensor_execution=False, dyadic_programs_exact_inverse_pair=False,
                independent_transcendental_backend=False, universal_proof_kernel=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    need(not (args.quick and args.write_result), "diagnostic replay cannot replace the full receipt")
    result = run(args.quick)
    if args.quick:
        print(json.dumps(dict(status="PASS_FIXED_H_DIAGNOSTIC", cases=len(result["cases"]))))
        return
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed native FFT receipt")
    print(json.dumps(dict(status="PASS_RATIONAL_FFT_FIXED_H", cases=len(result["cases"]),
                          word_cases=len(result["word_cases"]), controls=len(result["controls"]),
                          native_stages=sum(row["counts"]["primitive_stages"] for row in result["cases"]),
                          rounded_outputs=sum(row["statistics"]["complex_roundings"] for row in result["cases"]),
                          result_sha256=sha256(canonical(result)).hexdigest()), sort_keys=True))


if __name__ == "__main__":
    main()
