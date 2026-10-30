"""Exact gate certificates and fixed-grid replay of the retained FFT/shear child.

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
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from exact import (C, Mat, Vec, adjoint, apply, component_l1, eye, inverse_gate,
                   need, norm2, qheight, round_q, unitary, upper, vector_hash)
from engine import Builder, Phases, budget, certificate, inverse_sqrt_box

ORACLE = "research/cubic-cyclic-inverse/vendor/interval_kernel.py"
CIRCUIT = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def rejected(operation, label):
    try:
        operation()
    except (ValueError, AssertionError):
        return label
    raise ValueError("control unexpectedly passed: " + label)


def authenticate(include_generator=False, include_full=False, include_gaussian=False, include_raw=False,
                 include_core=False):
    rows = [r for r in json.loads((HERE / "SOURCES.json").read_text())["files"] if r["usage"] == "input"]
    raw = {}
    for row in rows:
        content = (ROOT / row["path"]).read_bytes()
        need(sha256(content).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        rejected(lambda: need(sha256(content + b"\0").hexdigest() == row["sha256"], "changed source"),
                 "source corruption")
        raw[row["path"]] = content
    # Preserve the completed child receipts' mathematical input inventory.
    # All declared inputs above still receive the same byte-integrity check.
    added = {
        "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_exact_algebra.py",
        "research/rational-unitary-fft/vendor/stein_rational.py",
        "research/rational-unitary-fft/vendor/STEIN-PROVENANCE.json",
    }
    full = {"research/unconditional-batched-crt/vendor/GAUGEFREE-INTERIORS.md"}
    gaussian = {
        "research/certified-gaussian-recovery/intervals.py",
        "research/certified-gaussian-recovery/NOTICE.md",
        "research/certified-gaussian-recovery/PROOF.md",
        "research/capped-fusion-t74-k554/outer/check_gaugefree.py",
        "research/capped-phase-fusion/evidence/radical_reduction_ultra/HOLES-AND-Q-LDU.md",
    }
    raw_gaussian = {
        "research/unconditional-batched-crt/PROOF.md",
        "research/unconditional-batched-crt/vendor/FINE-PRIME.md",
        "research/capped-phase-fusion/BILATERAL-LDU.md",
        "research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md",
        "research/capped-phase-fusion/PHASE-LAYOUT-AUDIT.md",
        "research/capped-phase-fusion/FORWARD-SMALL-A-AUDIT.md",
    }
    core = {
        "research/rational-unitary-fft/vendor/boundary_adapter.py",
        "research/rational-unitary-fft/vendor/BOUNDARY-PROVENANCE.json",
        "research/capped-phase-fusion/evidence/radical_reduction_ultra/check_constructions.py",
        "research/capped-phase-fusion/evidence/gaussian_fast_ultra/check_capped_gauges.py",
        "research/capped-phase-fusion/evidence/phase_layout_audit_ultra/check_union.py",
    }
    return raw, [{"path": r["path"], "sha256": r["sha256"]} for r in rows
                 if (include_generator or r["path"] not in added)
                 and (include_full or r["path"] not in full)
                 and (include_gaussian or r["path"] not in gaussian)
                 and (include_raw or r["path"] not in raw_gaussian)
                 and (include_core or r["path"] not in core)]


def operator(plan, n):
    columns = [apply(plan, Vec(int(i == j) for i in range(n)))[0] for j in range(n)]
    return Mat([[columns[j][i] for j in range(n)] for i in range(n)])


def mv(matrix, vector):
    return Vec(sum((a * x for a, x in zip(row, vector)), C()) for row in matrix)


def plan_hash(plan):
    return sha256(canonical([[[list(ids), [[x.record() for x in row] for row in gate]]
                             for ids, gate in layer] for layer in plan])).hexdigest()


def fft_check(builder, n, phases):
    plan = builder.namespace["fft"](list(range(n)))
    before = len(phases.certificates)
    inverse = builder.namespace["inverse"](plan)
    need(len(phases.certificates) == before, "inverse reuses stored coefficients")
    for layer in plan:
        used = set()
        for ids, gate in layer:
            need(not used.intersection(ids) and unitary(gate), "disjoint exactly unitary FFT gate")
            used.update(ids)
    actual = operator(plan, n)
    for j in range(n):
        basis = Vec(int(i == j) for i in range(n))
        image = Vec(actual[i][j] for i in range(n))
        need(apply(inverse, image)[0] == basis, "exact FFT adjoint round trip")
    scale_box = inverse_sqrt_box(n, phases.working_bits)
    need(scale_box[0] ** 2 * n <= 1 <= scale_box[1] ** 2 * n, "Fourier normalization enclosure")
    squared_error = Q(0)
    for i in range(n):
        for j in range(n):
            box = phases.box(n, -i * j)
            for interval, coordinate in zip(box, (actual[i][j].re, actual[i][j].im)):
                candidates = [x * y for x in interval for y in scale_box]
                squared_error += max(abs(coordinate - min(candidates)),
                                     abs(coordinate - max(candidates))) ** 2
    epsilon = 2 * (n.bit_length() - 1) * phases.nu
    need(squared_error <= n * epsilon ** 2, "independent dense Fourier enclosure")
    return {"n": n, "layers": len(plan), "gates": sum(len(layer) for layer in plan),
            "operator_sha256": vector_hash([x for row in actual for x in row]),
            "fourier_frobenius_squared_upper": str(upper(squared_error)),
            "operator_error_bound": str(epsilon)}


def structure(plan, n, certificate_row):
    height = 0
    shear_layers = 0
    unitary_gates = 0
    for layer in plan:
        used = set()
        layer_shears = []
        for ids, gate in layer:
            need(not used.intersection(ids) and len(set(ids)) == len(ids), "disjoint source layer")
            need(all(0 <= i < 2 * n for i in ids), "owned source wires")
            used.update(ids)
            for row in gate:
                for entry in row:
                    height = max(height, qheight(entry.re), qheight(entry.im))
            crossing = len(ids) == 2 and ids[0] < n <= ids[1]
            if crossing:
                need(gate[0][0] == gate[1][1] == 1 and gate[0][1] == 0, "source-oriented pointwise shear")
                layer_shears.append(gate[1][0])
            else:
                need(all(i < n for i in ids) or all(i >= n for i in ids), "unitary bank ownership")
                need(unitary(gate), "exactly unitary bank gate")
                unitary_gates += 1
        if layer_shears:
            need(len(layer_shears) == n and len(used) == 2 * n, "complete spectral layer")
            bound = (certificate_row["mg"] if shear_layers == 0 else certificate_row["mh"])
            bound += Q(1, 1 << certificate_row["multiplier_bits"])
            need(all(value.norm2() <= bound ** 2 for value in layer_shears), "charged spectral norm")
            shear_layers += 1
    need(shear_layers == 2 and len(plan) <= certificate_row["layer_bound"], "complete child schedule")
    need(height <= certificate_row["coefficient_height_bound"], "bounded online coefficient encoding")
    return {"unitary_gates": unitary_gates, "spectral_layers": shear_layers,
            "max_coefficient_height": height}


def ideal_endpoint(matrix, vector):
    n = len(matrix)
    source, target = vector[:n], vector[n:]
    image = mv(matrix, source)
    return Vec(source + [a + b for a, b in zip(target, image)])


def one_case(matrix, target, raw, phase_pool, fine_grid=False):
    n = len(matrix)
    base = Vec(C(Q((7 * i + 3) % 17 - 8, 8), Q((5 * i + 1) % 13 - 6, 8))
               for i in range(2 * n))
    source = Vec(base[:n])
    cancelled = Vec(source + [-x for x in mv(matrix, source)])
    large = Vec(C((1 if i % 2 == 0 else -1) * (1 << 20),
                  (1 if i % 3 else -1) * (1 << 19)) for i in range(2 * n))
    vectors = [base, Vec(-x for x in base), cancelled, large]
    if fine_grid:
        vectors.append(Vec([C(Q(1, 1 << 80))] + [C() for _ in range(2 * n - 1)]))
    radius = max(Q(1), *(component_l1(x) for x in vectors))
    components = [part for vector in vectors for value in vector for part in (value.re, value.im)]
    need(all(value.denominator & (value.denominator - 1) == 0 for value in components),
         "dyadic incoming fixtures")
    incoming_bits = max(value.denominator.bit_length() - 1 for value in components)
    bound = budget(matrix, radius, target, incoming_bits)
    p = bound["phase_bits"]
    if p not in phase_pool:
        phase_pool[p] = Phases(p, raw[ORACLE])
    phases = phase_pool[p]
    builder = Builder(phases, bound["multiplier_bits"], raw[CIRCUIT])
    fft = fft_check(builder, n, phases)
    plan = builder.plan(matrix)
    structural = structure(plan, n, bound)
    actual = operator(plan, 2 * n)
    for i in range(2 * n):
        for j in range(2 * n):
            if i < n or j >= n:
                need(actual[i][j] == int(i == j), "exact unrounded dirty-source and target-identity blocks")
    coefficient_squared = sum(((actual[n + i][j] - matrix[i][j]).norm2()
                               for i in range(n) for j in range(n)), Q(0))
    need(coefficient_squared <= n * bound["coefficient_error"] ** 2,
         "independent exact Toeplitz reference")
    micro = Vec([C(Q(2, 1 << bound["data_bits"]))] + [C() for _ in range(2 * n - 1)])
    vectors.append(micro)
    declared_bits = max(part.denominator.bit_length() - 1 for vector in vectors
                        for value in vector for part in (value.re, value.im))
    final_bound = budget(matrix, radius, target, declared_bits)
    need(all(final_bound[key] == value for key, value in bound.items()
             if key != "input_fractional_bits"), "micro fixture preserves execution precision")
    bound = final_bound
    states = []
    for vector in vectors:
        need(norm2(vector) <= radius ** 2, "input radius")
        rounded_out, stats = apply(plan, vector, bound["data_bits"])
        rational_out = mv(actual, vector)
        wanted = ideal_endpoint(matrix, vector)
        coefficient_error = norm2(Vec(a - b for a, b in zip(rational_out, wanted)))
        rounding_error = norm2(Vec(a - b for a, b in zip(rounded_out, rational_out)))
        total_error = norm2(Vec(a - b for a, b in zip(rounded_out, wanted)))
        source_error = norm2(Vec(a - b for a, b in zip(rounded_out[:n], vector[:n])))
        need(coefficient_error <= (bound["coefficient_error"] * radius) ** 2, "coefficient forward error")
        need(rounding_error <= bound["rounding_error"] ** 2, "actual rounded gate error")
        need(total_error <= bound["total_error"] ** 2, "complete rounded child error")
        need(source_error <= bound["rounding_error"] ** 2, "rounded source restoration allowance")
        need(stats["max_observed_height"] <= bound["temporary_bits"], "observed temporary envelope")
        need(stats["max_reduced_fractional_bits"] <= bound["data_bits"]
             and stats["max_grid_numerator_bits"] + 1 <= bound["data_bits"] + bound["integer_bits"],
             "fixed data record width")
        states.append({"input_sha256": vector_hash(vector), "output_sha256": vector_hash(rounded_out),
                       "coefficient_error_squared_upper": str(upper(coefficient_error)),
                       "rounding_error_squared_upper": str(upper(rounding_error)),
                       "total_error_squared_upper": str(upper(total_error)),
                       "source_error_squared_upper": str(upper(source_error)),
                       "source_restoration_exact": source_error == 0, "statistics": stats})
    record_bound = {k: (str(v) if isinstance(v, Q) else v) for k, v in bound.items()}
    return {"input_sha256": vector_hash([x for row in matrix for x in row]), "n": n,
            "budget": record_bound, "fft": fft, "structure": structural,
            "source_ast_sha256": builder.original_ast, "adapted_ast_sha256": builder.adapted_ast,
            "plan_sha256": plan_hash(plan), "layers": len(plan),
            "gates": sum(len(layer) for layer in plan),
            "toeplitz_frobenius_squared_upper": str(upper(coefficient_squared)),
            "states": states}, builder, bound


def controls(raw):
    n = 4
    matrix = Mat([[C(Q(2 + i - j, 16), Q(1 if i >= j else -1, 32))
                   for j in range(n)] for i in range(n)])
    bound = budget(matrix, Q(8), 20)
    def build():
        return Builder(Phases(bound["phase_bits"], raw[ORACLE]), bound["multiplier_bits"], raw[CIRCUIT])
    def fails_target(plan):
        actual = operator(plan, 2 * n)
        wanted = Mat([[int(i == j) if i < n or j >= n else matrix[i - n][j]
                       for j in range(2 * n)] for i in range(2 * n)])
        error = sum(((a - b).norm2() for ar, br in zip(actual, wanted) for a, b in zip(ar, br)), Q(0))
        need(error > n * bound["coefficient_error"] ** 2, "mutant violates exact-operator certificate")
    controls = []
    builder = build()
    builder.namespace["inverse"] = lambda p: [[(ids, inverse_gate(gate)) for ids, gate in layer]
                                             for layer in p]
    fails_target(builder.plan(matrix))
    controls.append("wrong-inverse-layer-order")
    builder = build()
    plan = builder.plan(matrix)
    swap = Mat([[0, 1], [1, 0]])
    fails_target([[(ids, gate) for ids, gate in layer if gate != swap] for layer in plan])
    controls.append("missing-bit-reversal")
    wrong_scale = []
    for layer in plan:
        changed = []
        for ids, gate in layer:
            if len(ids) == 2 and ids[0] < n <= ids[1]:
                gate = Mat([[1, 0], [gate[1][0] / 2, 1]])
            changed.append((ids, gate))
        wrong_scale.append(changed)
    fails_target(wrong_scale)
    controls.append("normalized-instead-of-unnormalized-multipliers")
    builder = build()
    builder.np.linalg.inv = lambda gate: gate if len(gate) == 1 else inverse_gate(gate)
    fails_target(builder.plan(matrix))
    controls.append("missing-inverse-twist")
    q = round_q(Q(707, 1000), 8)
    bad_gate = Mat([[q, q], [q, -q]])
    controls.append(rejected(lambda: need(unitary(bad_gate), "unitarity"), "independent-butterfly-rounding"))
    controls.append(rejected(lambda: certificate(n, bound["mg"], bound["mh"], Q(8), 20,
                                                 bound["phase_bits"], bound["multiplier_bits"], 4),
                             "underfunded-data-precision"))
    controls.append(rejected(lambda: certificate(n, bound["mg"], bound["mh"], Q(8), 20,
                                                 4, bound["multiplier_bits"], bound["data_bits"]),
                             "underfunded-phase-precision"))
    controls.append(rejected(lambda: certificate(n, bound["mg"], bound["mh"], Q(8), 20,
                                                 bound["phase_bits"], bound["multiplier_bits"],
                                                 bound["data_bits"], bound["data_bits"] + 1),
                             "discarded-incoming-grid"))
    low, high = Phases(8, raw[ORACLE]), Phases(24, raw[ORACLE])
    stale = low.phase(7, 1)
    high.phase(7, 1)
    box = high.box(7, 1)
    distance = sum(max(abs(x - y) for x in interval)
                   for interval, y in zip(box, (stale.re, stale.im)))
    need(distance > high.nu and low.oracle["pi_interval"] is not high.oracle["pi_interval"],
         "stale lower-precision phase rejects")
    controls.append("stale-phase-at-higher-precision")
    controls.append(rejected(lambda: C(0.5), "floating coefficient"))
    need(canonical({"n": 1}) != canonical({"n": True}), "typed receipt")
    return controls + ["source-corruption", "typed-receipt"]


def run():
    raw, sources = authenticate()
    phase_pool, records = {}, []
    for n in (1, 2, 4, 8, 16):
        for complex_case in (False, True):
            column = Vec([C(Q(1, 2))] + [C(Q((-1) ** i, 16 * n),
                Q(i, 32 * n) if complex_case else 0) for i in range(1, n)])
            row = Vec([C(Q(1, 2))] + [C(Q(1, 8 * n),
                Q((-1) ** j, 16 * n) if complex_case else 0) for j in range(1, n)])
            matrix = Mat([[column[i - j] if i >= j else row[j - i] for j in range(n)] for i in range(n)])
            record, _, _ = one_case(matrix, 12 if not complex_case else 20, raw, phase_pool)
            records.append(record)
    for value in (C(), C(Q(1, 8))):
        matrix = Mat([[value for _ in range(4)] for _ in range(4)])
        record, _, _ = one_case(matrix, 20, raw, phase_pool, fine_grid=(value == 0))
        records.append(record)
    need(any(not state["source_restoration_exact"] for row in records for state in row["states"]),
         "nonzero rounded source error witness")
    return {"schema_version": 1, "scope": "actual rational FFT/Toeplitz gate schedule and fixed-grid data",
            "sources": sources, "cases": records,
            "phases": [phase_pool[key].record() for key in sorted(phase_pool)],
            "controls": controls(raw), "physical_tape_execution": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed receipt")
    print(json.dumps({"status": "PASS_RATIONAL_UNITARY_FFT", "cases": len(result["cases"]),
                      "rounded_states": sum(len(row["states"]) for row in result["cases"]),
                      "gates": sum(row["gates"] for row in result["cases"]),
                      "result_sha256": sha256(canonical(result)).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
