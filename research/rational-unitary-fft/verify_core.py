"""Execute complete finite-core Gaussian words against their shared references.

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
from exact import C, Mat, apply, ceil_log2, need, upper
from core import Core, allocated_reference, matrix_hash, max_complex, row_gap
from gaussian_reference import Entry, Reference
from verify import authenticate, canonical, rejected


def exact_action(matrix, state):
    columns = len(state[0]) if state else 0
    return Mat([[C(sum((a * state[k][j].re for k, a in enumerate(row) if a), Q(0)),
                   sum((a * state[k][j].im for k, a in enumerate(row) if a), Q(0)))
                 for j in range(columns)] for row in matrix])


def difference(left, right):
    need(len(left) == len(right), "reference comparison rows")
    return Mat([[a - b for a, b in zip(x, y)] for x, y in zip(left, right)])


def report(value, allowance):
    need(0 <= value <= allowance, "reported error allowance")
    bits = max(160, ceil_log2(1 / allowance) + 16)
    return str(min(allowance, upper(value, bits)))


def stage_certificate(core, stage, before, after):
    columns = len(before[0])
    if stage == "boundary_inverse":
        residual = difference(exact_action(core.schur, Mat([after[i] for i in core.boundary])),
                              Mat([before[i] for i in core.boundary]))
        error = max_complex(residual) / core.gap
        need(all(before[i] == after[i] for i in core.interior), "boundary stage preserves interiors")
    else:
        wanted = Mat([list(row) for row in before])
        if stage.startswith("interior_"):
            for cell in core.cells:
                matrix = cell["inverse"] if stage.endswith("inverse") else cell["matrix"]
                output = exact_action(matrix, Mat([before[i] for i in cell["indices"]]))
                for i, row in zip(cell["indices"], output):
                    wanted[i] = row
        elif stage == "boundary_forward":
            output = exact_action(core.schur, Mat([before[i] for i in core.boundary]))
            for i, row in zip(core.boundary, output):
                wanted[i] = row
        else:
            lower = stage.startswith("lower_")
            matrix = core.lower_coupling if lower else core.upper_coupling
            targets, sources = ((core.boundary, core.interior) if lower
                                else (core.interior, core.boundary))
            if sources:
                output = exact_action(matrix, Mat([before[i] for i in sources]))
                sign = -1 if stage.endswith("negative") else 1
                for i, row in zip(targets, output):
                    wanted[i] = [before[i][j] + sign * row[j] for j in range(columns)]
        error = max_complex(difference(after, wanted))
    need(error <= core.stage_error, "actual factor error against the current reference input")
    return dict(stage=stage, input_sha256=matrix_hash(before), output_sha256=matrix_hash(after),
                error_upper=report(error, core.stage_error), nonzero_error=error > 0)


def endpoint_certificate(core, rhs, answer):
    if core.kind == "narrow":
        residual = max_complex(difference(exact_action(core.matrix, answer), rhs))
        error = residual / core.gap
        method = "exact reference residual divided by certified row gap"
    else:
        error = max_complex(difference(answer, exact_action(core.matrix, rhs)))
        residual = None
        method = "exact reference forward product"
    need(error <= core.total_error, "complete finite-core reference error")
    return dict(method=method, error_upper=report(error, core.total_error),
                residual_upper=str(upper(residual)) if residual is not None else None,
                nonzero_error=error > 0)


def one_case(label, raw, reference, kind, first, last, cap, columns, target, incoming):
    print("PREPARE_GAUSSIAN_CORE", label, last - first, flush=True)
    core = Core(raw, reference, kind, first, last, cap, 1, target, incoming,
                physical_band=max(2 * reference.spec.source_halfwidth + 2,
                                  reference.spec.target_halfwidth))
    print("EXECUTE_GAUSSIAN_CORE", label, len(core.cells), len(core.boundary), flush=True)
    rhs = Mat([[C(Q((3 * i + 2 * j) % 7 - 3, 8), Q((5 * i + j) % 5 - 2, 8))
                for j in range(columns)] for i in range(core.n)])
    if incoming > 3:
        rhs[0][0] = C(Q(1, 1 << incoming))
    answer, execution, traces = core.execute(rhs, capture=True)
    need(matrix_hash(rhs) == matrix_hash(traces[0][1]), "borrowed initial core data")
    need(all(matrix_hash(a[2]) == matrix_hash(b[1]) for a, b in zip(traces, traces[1:])),
         "current-value chronological stage inputs")
    factors = [stage_certificate(core, *trace) for trace in traces]
    endpoint = endpoint_certificate(core, rhs, answer)
    record = core.record()
    record.update(label=label, columns=columns, input_sha256=matrix_hash(rhs),
                  output_sha256=matrix_hash(answer), execution=execution,
                  factor_certificates=factors, endpoint=endpoint)
    print("CHECK_GAUSSIAN_CORE", label, flush=True)
    return record, core, rhs, answer, traces


def controls(raw, reference, cases):
    results = []
    narrow = next(row for row in cases if row[1].kind == "narrow" and row[1].cells)
    edge = next(row for row in cases if row[1].kind == "narrow" and not row[1].cells)
    _, core, rhs, _, traces = narrow
    _, small, small_rhs, _, small_traces = edge
    results.append(rejected(lambda: Core(raw, reference, "narrow", 0, reference.target_size,
                                        16, 1, 20), "unhandled-periodic-corner"))
    results.append(rejected(lambda: Core(raw, reference, "narrow", 0, 20, 3, 1, 20),
                            "nondyadic-core-cap"))
    results.append(rejected(lambda: Core(raw, reference, "narrow", 0, 20, 16, 1, 20,
                                        physical_band=1), "understated-core-physical-band"))
    poor = Reference(raw, 384, 1, 2, 4, 18, 8)
    results.append(rejected(lambda: Core(raw, poor, "narrow", core.first, core.last, 16, 1, 20),
                            "reference-not-funded-for-amplified-dense-inputs"))
    saved = list(small.stages)
    small.stages[1], small.stages[4] = small.stages[4], small.stages[1]
    results.append(rejected(lambda: small.execute(small_rhs), "wrong-retained-factor-order"))
    small.stages = saved
    upper_trace = next(trace for trace in traces if trace[0] == "upper_negative")
    results.append(rejected(lambda: stage_certificate(core, upper_trace[0], upper_trace[1],
                                                       upper_trace[1]), "omitted-original-sparse-coupling"))
    boundary_trace = next(trace for trace in small_traces if trace[0] == "boundary_inverse")
    boundary_rhs = Mat([boundary_trace[1][i] for i in small.boundary])
    prepared, _ = small.solver.run(boundary_rhs)
    baseline = small.solver.baseline(boundary_rhs)
    need(prepared == baseline, "prepared dyadic pages match the unchanged boundary adapter")
    results.append("prepared-page-source-value-equivalence")
    value = small.solver.inverse_pages["lower"][0][0][0]
    small.solver.inverse_pages["lower"][0][0][0] += 1
    bad, _ = small.solver.run(boundary_rhs)
    bad_state = Mat([list(row) for row in boundary_trace[1]])
    for i, row in zip(small.boundary, bad):
        bad_state[i] = row
    results.append(rejected(lambda: stage_certificate(small, "boundary_inverse", boundary_trace[1], bad_state),
                            "corrupted-prepared-inverse-page"))
    small.solver.inverse_pages["lower"][0][0][0] = value
    key = "narrow", small.coordinates[0], small.coordinates[0]
    old_entry = reference.entries[key]
    reference.entries[key] = Entry(Q(2), "unit-diagonal", 0, Q(0))
    results.append(rejected(lambda: small.execute(small_rhs), "changed-core-reference-after-setup"))
    reference.entries[key] = old_entry
    off_grid = Mat([list(row) for row in small_rhs])
    off_grid[0][0] = C(Q(1, 1 << (small.incoming + 1)))
    results.append(rejected(lambda: small.execute(off_grid), "discarded-core-incoming-grid"))
    oversized = Mat([list(row) for row in small_rhs])
    oversized[0][0] = C(2)
    results.append(rejected(lambda: small.execute(oversized), "underdeclared-core-input-radius"))
    need(all(row[1].solver is None for row in cases if row[1].kind == "broad"),
         "broad boundary requires no inverse solver")
    results.append("broad-schur-is-applied")
    need(canonical({"columns": 1}) != canonical({"columns": True}), "typed core receipt")
    return results + ["typed-core-receipt"]


def run(quick=False):
    raw, sources = authenticate(include_generator=True, include_full=True, include_gaussian=True,
                                include_raw=True, include_core=True)
    reference = Reference(raw, 384, 1, 2, 4, 18, 320)
    length = 7 * reference.spec.target_halfwidth + 16 + 1
    specifications = [
        ("narrow-core", "narrow", 8, 8 + length, 1, 20, 3),
        ("broad-core", "broad", 8, 8 + length, 1, 20, 3),
        ("narrow-hole-fine", "narrow", 187, 198, 5, 24, 768),
        ("broad-hole", "broad", 187, 198, 3, 20, 3),
    ]
    if quick:
        specifications = specifications[2:]
    cases = [one_case(label, raw, reference, kind, first, last, 16, columns, target, incoming)
             for label, kind, first, last, columns, target, incoming in specifications]
    if quick:
        return dict(scope="diagnostic boundary-only core replay", cases=[row[0] for row in cases])
    need(all(len(row[1].cells) >= 2 for row in cases[:2]), "multiple actual interior blocks")
    need(any(row[0]["endpoint"]["nonzero_error"] for row in cases), "nonzero complete rounded error")
    auto, allocation = allocated_reference(raw, 512, 1, 2, 2, 1, 8)
    need(auto.narrow_gap > 0 and auto.allocation is not None, "noncircular common-reference allocation")
    return dict(schema_version=1, scope="complete ordinary finite-core Gaussian factor words",
                sources=sources, reference=reference.record(), cases=[row[0] for row in cases],
                allocation_only=dict(reference=auto.record(), budget=allocation),
                controls=controls(raw, reference, cases),
                finite_core_numerical_execution=True, physical_tape_execution=False,
                complete_gaussian_execution=False, core_halo_comparison=False,
                tensor_execution=False, stored_global_inverse_pair=False,
                independent_transcendental_backend=False, universal_proof_kernel=False)


def verify_result(write=False):
    result = run()
    path = HERE / "CORE-RESULT.json"
    if write:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed core receipt")
    print(json.dumps(dict(status="PASS_FINITE_GAUSSIAN_CORE", cases=len(result["cases"]),
                          interiors=sum(len(row["interior_blocks"]) for row in result["cases"]),
                          dense_gate_applications=sum(row["execution"]["statistics"]["dense_gate_applications"]
                                                      for row in result["cases"]),
                          boundary_scalar_products=sum(row["execution"]["statistics"]["boundary_scalar_products"]
                                                       for row in result["cases"]),
                          controls=len(result["controls"]),
                          result_sha256=sha256(canonical(result)).hexdigest()), sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    if args.quick:
        result = run(quick=True)
        print(json.dumps(dict(status="PASS_CORE_DIAGNOSTIC", cases=len(result["cases"]))))
    else:
        verify_result(args.write_result)


if __name__ == "__main__":
    main()
