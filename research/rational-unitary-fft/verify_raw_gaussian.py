"""Verify common Gaussian pages, raw factors and complete stored inverses.

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
from exact import (C, Mat, Vec, apply, component_l1, eye, multiply, need,
                   norm2, upper, vector_hash)
from gaussian_reference import Entry, Reference
from raw_gaussian import RawGaussian
from verify import authenticate, canonical, mv, operator, plan_hash, rejected
from verify_triangle import eliminate, frobenius_error, structure


def reference_check(ref):
    """Three explicit windings plus analytic tails; shared interval backend."""
    size, alpha, source_size = ref.target_size, ref.spec.alpha, ref.spec.source_size
    need(len(set(ref.selected)) == source_size and len(ref.holes) == ref.spec.excess
         and all(Q(-1, 2) <= beta < Q(1, 2) for beta in ref.betas), "complete finite geometry")
    bits = 2 * (ref.spec.entry_bits + 24) + 32
    records = []
    for kind in ("narrow", "broad"):
        matrix, errors = [], []
        for row in range(size):
            values, differences = [], []
            for column in range(size):
                entry = ref.entry(kind, row, column)
                values.append(C(entry.value))
                i, j = ref.source_at.get(row), ref.source_at.get(column)
                if j is None or (kind == "narrow" and i is None):
                    need(entry.value == int(row == column), "exact hole completion")
                    differences.append(Q(0))
                    continue
                lo = hi = Q(0)
                for winding in (-1, 0, 1):
                    if kind == "narrow":
                        factor = alpha ** 2 * ((ref.rho * (j + winding * source_size)
                                                 - ref.selected[i]) ** 2 - ref.betas[j] ** 2)
                        scale = Q(1)
                    else:
                        factor = (j + winding * source_size - ref.lam * row) ** 2 / alpha ** 2
                        scale = Q(1, alpha)
                    box = ref.exp.decay_box(factor, bits)
                    lo += scale * Q(box.lo, box.scale)
                    hi += scale * Q(box.hi, box.scale)
                differences.append(max(abs(entry.value - lo), abs(entry.value - hi)))
            matrix.append(values)
            errors.append(differences)
        if kind == "narrow":
            remainder = ref.exp.geometric_tail(alpha ** 2 * source_size * (source_size + 1),
                                                2 * alpha ** 2 * (source_size + 1), 2, bits)
        else:
            c = 1 / (alpha ** 2 * ref.rho ** 2)
            remainder = ref.exp.geometric_tail(c * (size + Q(1, 2)) ** 2,
                                                2 * c * (size + 1), Q(2, alpha), bits)
        measured = max(max(map(sum, errors)), max(map(sum, zip(*errors)))) + remainder
        need(measured <= ref.errors[kind], "periodic reference row and column error")
        if kind == "narrow":
            ref.require_narrow_gap()
            gap = min(1 - sum((matrix[i][j].re for j in range(size) if i != j), Q(0))
                      for i in range(size))
            need(gap >= ref.narrow_gap, "actual common reference row gap")
        for i in range(size):
            for j in range(size):
                distance = min(abs(i - j), size - abs(i - j))
                width = 2 * ref.spec.source_halfwidth + 2 if kind == "narrow" else ref.spec.target_halfwidth
                need(distance <= width or matrix[i][j] == 0, "physical reference bandwidth")
        records.append(dict(kind=kind, entries=size ** 2,
                            winding_terms=3 * source_size * (source_size if kind == "narrow" else size),
                            matrix_sha256=vector_hash([z for row in matrix for z in row]),
                            measured_error_upper=str(upper(measured)), allowance=str(ref.errors[kind])))
    need(any(ref.entry("broad", h, q).value != 0 for h in ref.holes for q in ref.selected),
         "broad Gaussian outputs at hole rows")
    need(all(ref.entry("narrow", h, q).value == 0 for h in ref.holes for q in ref.selected),
         "narrow direct-sum hole completion")
    wrap = ref.entry("narrow", ref.selected[-1], ref.selected[0])
    need(wrap.kind == "cross-period" and wrap.lift == 1, "original period cut retained")
    first = ref.window("narrow", ref.selected[1:5])
    second = ref.window("narrow", ref.selected[3:7])
    need(all(first[i + 2][j + 2] == second[i][j] for i in range(2) for j in range(2)),
         "overlapping pages use identical global entries")
    principal = ref.window("narrow", list(ref.selected[13:17]) + list(ref.holes[:1]))
    inverse = eliminate(principal)
    row_bound = max(component_l1(row) for row in inverse)
    column_bound = max(component_l1(column) for column in zip(*inverse))
    need(row_bound <= ref.narrow_inverse_bounds[0] and column_bound <= ref.narrow_inverse_bounds[1],
         "principal inverse across a cell boundary and a hole")
    return dict(reference=ref.record(), matrices=records, overlap_entries=4,
                wrap_kind=wrap.kind, weights=len(ref.weights), kernels=len(ref.kernel),
                principal_inverse_bounds=[str(row_bound), str(column_bound)])


def one_case(label, raw, ref, kind, start, n, fine=False):
    vectors = [Vec(C(Q((3 * i + 1) % 7 - 3, 8), Q((5 * i + 2) % 9 - 4, 8))
                   for i in range(n)),
               Vec(C((-1) ** i * 8, i % 2) for i in range(n))]
    incoming = 512 if fine else 3
    if fine:
        vectors.append(Vec([C(Q(1, 1 << incoming))] + [C()] * (n - 1)))
    radius = max(Q(1), *(component_l1(v) for v in vectors))
    caller = RawGaussian(raw, ref, kind, start, n, radius, 16, incoming)
    if ref.allocation is not None:
        need(n <= ref.allocation["cap"] and radius <= Q(ref.allocation["radius"])
             and caller.raw_inverse_bound <= Q(ref.allocation["inverse_bound"]),
             "uniform reference allocation covers this caller")
    plan = caller.compile()
    inverse = caller.inverse_plan
    actual, actual_inverse = operator(plan, n), operator(inverse, n)
    need(multiply(actual, actual_inverse) == eye(n), "exact inverse of stored raw program")
    reference, reference_inverse = caller.reference_matrix, eliminate(caller.reference_matrix)
    height = max(structure(plan, caller.bound), structure(inverse, caller.bound))
    states = []
    for direction, program, wanted, allowance in (
            ("forward", plan, reference, caller.forward_error),
            ("inverse", inverse, reference_inverse, caller.inverse_error)):
        for vector in vectors:
            need(norm2(vector) <= radius ** 2 and all((part * (1 << incoming)).denominator == 1
                 for z in vector for part in (z.re, z.im)), "raw incoming contract")
            output, stats = apply(program, vector, caller.data_bits)
            error = norm2(output - mv(wanted, vector))
            need(error <= allowance ** 2 and allowance < Q(1, 1 << caller.target),
                 "rounded raw forward/inverse error against common reference")
            need(stats["max_observed_height"] <= caller.bound["temporary_bits"]
                 and stats["max_grid_numerator_bits"] + 1 <= caller.data_bits + caller.bound["integer_bits"]
                 and stats["max_reduced_fractional_bits"] <= caller.data_bits, "raw online record widths")
            states.append(dict(direction=direction, input_sha256=vector_hash(vector),
                               output_sha256=vector_hash(output), statistics=stats,
                               error_squared_upper=str(upper(error))))
    record = caller.record()
    record.update(label=label, layers=len(plan), gates=sum(map(len, plan)),
                  plan_sha256=plan_hash(plan), inverse_sha256=plan_hash(inverse),
                  coefficient_height=height, states=states)
    print("CHECK_RAW_GAUSSIAN_CASE", label, flush=True)
    return record, caller


def controls(raw, ref, caller):
    results = []
    results.append(rejected(lambda: ref.interior(ref.spec.source_size - 2, 4), "interior-crosses-period-cut"))
    results.append(rejected(lambda: ref.interior(14, 4), "interior-crosses-original-cell"))
    results.append(rejected(lambda: Reference(raw, 32, 1, 3, 16, 14, 96), "ambiguous-periodic-lift"))
    results.append(rejected(lambda: Reference(raw, 32, 1, 3.0, 3, 14, 96), "floating-reference-parameter"))
    results.append(rejected(lambda: Reference.for_cap(raw, 32, 1, 3, 4, 64, 64),
                            "period-too-short-for-uniform-reference-accuracy"))
    poor = Reference(raw, 32, 1, 3, 3, 2, 96)
    results.append(rejected(lambda: RawGaussian(raw, poor, "broad", 2, 2, 1, 16),
                            "unpaid-common-reference-tail"))
    coarse = Reference(raw, 32, 1, 3, 3, 14, 8)
    results.append(rejected(lambda: RawGaussian(raw, coarse, "broad", 2, 2, 1, 16),
                            "underfunded-common-reference-coefficients"))
    fresh = Reference(raw, 32, 1, 3, 3, 14, 96)
    pending = RawGaussian(raw, fresh, "narrow", 2, 2, 1, 16)
    key = "narrow", fresh.selected[2], fresh.selected[2]
    fresh.entries[key] = Entry(Q(2), "unit-diagonal", 0, Q(0))
    results.append(rejected(pending.compile, "changed-reference-after-preparation"))
    weight = ref.weight(0)
    wrong, _ = ref.exp.absolute(ref.weight_exponent_bound, 16)
    need(wrong == 0 and weight > 0, "online precision can zero a setup weight")
    results.append("zero-weight-at-online-precision")
    results.append(rejected(lambda: ref.exp.relative(ref.weight_exponent_bound,
                            ref.weight_exponent_bound, 16, 16), "underfunded-positive-weight-grid"))
    weak = Reference(raw, 32, 1, 1, 0, 2, 32)
    results.append(rejected(weak.require_narrow_gap, "uncertified-global-row-gap"))
    need(any(ref.entry("broad", h, q).value > 0 for h in ref.holes for q in ref.selected),
         "broad hole rows cannot use narrow direct sum")
    results.append("erased-broad-hole-output")
    need(any(ref.entry("broad", q, q).value != 1 for q in ref.selected),
         "raw broad diagonal retains alpha and displacement")
    results.append("forced-unit-broad-diagonal")
    finer = Reference(raw, 32, 1, 3, 3, 14, 112)
    original_caller = RawGaussian(raw, ref, "broad", 2, 2, 1, 16)
    finer_caller = RawGaussian(raw, finer, "broad", 2, 2, 1, 16)
    original_caller.compile()
    finer_caller.compile()
    need(original_caller.reference_hash != finer_caller.reference_hash
         and plan_hash(original_caller.plan) == plan_hash(finer_caller.plan),
         "full reference setup precision stays off online coefficient wires")
    results.append("reference-setup-precision-separate-from-online-gates")
    # Swap only the wrapper factors around the unchanged stored middle inverse.
    need(caller.kind == "narrow" and caller.n >= 4, "noncommuting wrapper control fixture")
    middle_inverse = caller.child.builder.inverse(caller.child.plan)
    wrong_inverse = ([[((i,), Mat([[1 / a]])) for i, a in enumerate(caller.b_values)]]
                     + list(middle_inverse)
                     + [[((i,), Mat([[1 / a]])) for i, a in enumerate(caller.a_values)]])
    need(frobenius_error(operator(wrong_inverse, caller.n), eliminate(caller.reference_matrix))
         > caller.n * caller.inverse_error ** 2, "wrong anchored inverse wrapper")
    results.append("wrong-inverse-diagonal-order")
    original = caller.a_factors[0]
    caller.a_factors[0] += 1
    results.append(rejected(caller.check_identity, "wrong-raw-exponential-constant"))
    caller.a_factors[0] = original
    need(canonical({"excess": 1}) != canonical({"excess": True}), "typed raw receipt")
    return results + ["typed-raw-receipt"]


def run():
    raw, sources = authenticate(include_generator=True, include_full=True,
                                include_gaussian=True, include_raw=True)
    small = Reference(raw, 32, 1, 3, 3, 14, 96)
    reference = reference_check(small)
    print("CHECK_COMMON_GAUSSIAN_REFERENCE", flush=True)
    large = Reference.for_cap(raw, 128, 1, 3, 4, 64, 16)
    sparse = Reference(raw, 10 ** 20 + 1, 10 ** 18, 3, 3, 30, 96)
    coordinates, _, _ = sparse.interior(10 ** 10, 4)
    sparse_window = sparse.window("narrow", coordinates)
    need(all(sparse.source_at.get(coordinates[i]) == 10 ** 10 + i for i in range(4))
         and sparse._holes is None and not sparse.record()["geometry_materialized"],
         "large-axis queries avoid global geometry enumeration")
    fixtures = [
        ("broad-small", small, "broad", 2, 2, False),
        ("narrow-small", small, "narrow", 2, 2, False),
        ("broad-positive-cell", large, "broad", 60, 4, False),
        ("broad-negative-cell", large, "broad", 65, 4, False),
        ("narrow-positive-cell", large, "narrow", 60, 4, False),
        ("narrow-fine-negative-cell", large, "narrow", 65, 4, True),
    ]
    records, callers = [], []
    for label, ref, kind, start, n, fine in fixtures:
        record, caller = one_case(label, raw, ref, kind, start, n, fine)
        records.append(record)
        callers.append(caller)
    need(all(row["budget"]["data_bits"] >= row["incoming_bits"] for row in records),
         "preserved raw incoming grids")
    return dict(schema_version=1, scope="common periodic Gaussian reference and raw capped interior circuits",
                sources=sources, global_reference=reference, large_reference=large.record(),
                large_address_query=dict(reference=sparse.record(), coordinates=list(coordinates),
                                         window_sha256=vector_hash([z for row in sparse_window for z in row])),
                cases=records, controls=controls(raw, small, callers[-1]),
                raw_interior_gate_execution=True, complete_gaussian_execution=False,
                physical_tape_execution=False, boundary_schur_execution=False,
                independent_transcendental_backend=False, universal_proof_kernel=False)


def verify_result(write=False):
    result = run()
    path = HERE / "RAW-GAUSSIAN-RESULT.json"
    if write:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed raw Gaussian receipt")
    print(json.dumps(dict(status="PASS_RAW_GAUSSIAN_REFERENCE_CIRCUIT", cases=len(result["cases"]),
                          gates=sum(row["gates"] for row in result["cases"]),
                          rounded_states=sum(len(row["states"]) for row in result["cases"]),
                          controls=len(result["controls"]),
                          result_sha256=sha256(canonical(result)).hexdigest()), sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    verify_result(parser.parse_args().write_result)


if __name__ == "__main__":
    main()
