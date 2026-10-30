#!/usr/bin/env python3
"""Source-reusing scalar Gaussian adapter; no Full construction or gate run.

Original modules and interval backend are unchanged. A delegating exponential
wrapper records actual requests; coefficient/error ledger comparisons are made
outside the uncalled compile_root method. Prepared with OpenAI assistance.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import importlib
import json
from pathlib import Path
import sys

HEAD = "66b95cc916552f487203be14fd99a7aea0bdd78e"
ORACLE_RESULT_SHA = "d924d37a44491ece0636fbbc1515bb3f06b19918e3732cb26a98f18471c6a8f7"
PINS = {
    "gaussian.py": "08155357fd39b5fd7959f51f1d205b6511b8577b51520d793c89f92368b399ab",
    "exact.py": "c9b89d7357210af69865690ba12e695366961f8b501a8fab9d0fefe3fb30c479",
    "engine.py": "9e36aee0835e6b1b62997433581f88b5a434ccab8ae43e5c25d1deaaf1ebf653",
    "triangular.py": "46780d95ddebfed22e8f0c18565fe2e768250afa5beeb31f450292cc06f7ec11",
    "generator.py": "827ef9fe1bd664859995892b59843c390f7969c938fb7e1e6dc585c31a54b555",
    "full.py": "1f42d5f2858564ffb320e54ba6aa29651025491569823e25006bf5862457b803",
    "intervals.py": "159d2a7d32a8cc7c8f56632a8ef127308b984a0a6753c9d6bdccacc6e7d6d4df",
    "source_evaluator.py": "5274b2838f322dc56a88570e4f9262fcd3857cd387160ad138e083ccdfbe9761",
    "GAUSSIAN-RESULT.json": "72b206c813fae8e8c24c6784bb97dbbba5040741cb93c4affd09443bc44350f5",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def qstr(value):
    return str(Q(value))


def request_id(factor, bits):
    return str(bits) + ":" + qstr(factor)


def capture(source):
    for name, expected in PINS.items():
        need(sha((source / name).read_bytes()) == expected, "source hash: " + name)
    sys.path.insert(0, str(source))
    for name in ("gaussian", "full", "generator", "triangular", "engine", "exact"):
        sys.modules.pop(name, None)
    gaussian = importlib.import_module("gaussian")
    exact = importlib.import_module("exact")
    need(Path(gaussian.__file__).resolve() == (source / "gaussian.py").resolve(), "actual module path")
    saved = json.loads((source / "GAUSSIAN-RESULT.json").read_bytes())
    raw = {gaussian.INTERVALS: (source / "intervals.py").read_bytes(),
           gaussian.EVALUATOR: (source / "source_evaluator.py").read_bytes()}
    events = []

    class TracedGaussian(gaussian.Gaussian):
        def exponential(self, factor, bits):
            original_backend = self.oracle.exp_negative
            backend_arguments = []
            def traced_backend(argument):
                backend_arguments.append({"lower": str(Q(argument.lo, argument.scale)),
                                          "upper": str(Q(argument.hi, argument.scale)),
                                          "bits": argument.bits,
                                          "shortcut_condition": argument.lo >= argument.bits * argument.scale})
                return original_backend(argument)
            self.oracle.exp_negative = traced_backend
            try:
                result = super().exponential(factor, bits)
            finally:
                self.oracle.exp_negative = original_backend
            events.append({"case": getattr(self, "probe_label", "initial-zero"),
                           "stage": getattr(self, "probe_stage", "initial-zero"),
                           "caller": sys._getframe(1).f_code.co_name,
                           "id": request_id(factor, bits), "factor": qstr(factor), "bits": bits,
                           "backend_arguments": backend_arguments,
                           "lower": str(Q(result.lo, result.scale)),
                           "upper": str(Q(result.hi, result.scale))})
            return result

    zero = object.__new__(TracedGaussian)
    zero.oracle = gaussian.load_intervals(raw[gaussian.INTERVALS])
    one = zero.exponential(Q(0), 16)
    need(one.lo == one.hi == one.scale, "initial exact f=0 gives one")
    records = []
    for record in saved["cases"]:
        producer = object.__new__(TracedGaussian)
        producer.probe_label, producer.probe_stage = record["label"], "initialization"
        # Preserve original automatic vs explicit cutoff choices.
        window = record["window"] if record["label"] in (
            "low-requested-precision", "high-requested-precision") else None
        producer.__init__(raw, record["n"], Q(record["c"]), Q(record["shift"]),
                          Q(record["radius"]), record["target_bits"], record["incoming_bits"], window)
        producer.probe_stage = "actual-Tsec-table"
        matrix = producer.namespace["Tsec"](
            producer.spec.n, gaussian.PiMultiple(producer.spec.c), producer.spec.shift).astype(complex)
        need(producer.builder is None and producer.plan is None and producer.root is None,
             "no full compilation or root compilation was invoked")
        n = producer.spec.n
        need(set(producer.offsets) == set(range(-producer.window, producer.window + 1)), "shared offset table")
        need(all(matrix[i][j] == (producer.offsets[j-i]["value"] if abs(j-i) <= producer.window else 0)
                 for i in range(n) for j in range(n)), "actual Tsec root equals shared table")
        coefficient_error = sum((r["error"] for r in producer.offsets.values()), Q(0))
        kernel_error = producer.tail_bound + coefficient_error
        need(coefficient_error <= producer.epsilon / 2 and kernel_error <= producer.epsilon
             and producer.epsilon * producer.qbar <= Q(1, 2), "external scalar ledger reproduces source guard")
        fields = dict(n=n, c=str(producer.spec.c), shift=str(producer.spec.shift),
                      radius=str(producer.spec.radius), target_bits=producer.spec.target,
                      incoming_bits=producer.spec.incoming, window=producer.window,
                      conditioning_bits=producer.conditioning_bits,
                      conditioning_interval=[str(Q(producer.conditioning_box.lo, producer.conditioning_box.scale)),
                                             str(Q(producer.conditioning_box.hi, producer.conditioning_box.scale))],
                      ideal_inverse_bound=str(producer.qbar), error_bits=producer.error_bits,
                      coefficient_bits=producer.coefficient_bits, working_bits=producer.working_bits,
                      epsilon=str(producer.epsilon), tail_bound=str(producer.tail_bound),
                      coefficient_error=str(coefficient_error), kernel_error=str(kernel_error),
                      root_sha256=exact.vector_hash([z for row in matrix for z in row]),
                      source_ast_sha256=producer.source_ast, callsite_ast_sha256=producer.callsite_ast,
                      offsets=[dict(offset=u, **{k: str(v) for k, v in producer.offsets[u].items()})
                               for u in sorted(producer.offsets)])
        for key, value in fields.items():
            need(value == record[key], "saved scalar field " + record["label"] + ":" + key)
        producer.probe_stage = "finer-reference"
        precision = producer.error_bits + 16 + exact.ceil_log2(2 * n)
        fine_bits = 2 * precision + 32
        fine, fine_error, fine_offsets = {}, Q(0), []
        for u in range(1-n, n):
            factor = producer.spec.c * ((Q(u)-producer.spec.shift)**2-producer.spec.shift**2)
            box = producer.exponential(factor, fine_bits)
            fine[u] = Q(box.lo, box.scale)
            fine_error += Q(box.hi-box.lo, box.scale)
            fine_offsets.append(dict(offset=u, factor=str(factor), id=request_id(factor, fine_bits),
                                     lower=str(Q(box.lo, box.scale)), upper=str(Q(box.hi, box.scale))))
        need(fine_bits == record["fine_reference_bits"] and str(fine_error) == record["fine_reference_error"],
             "saved finer scalar reference fields")
        fine_matrix = exact.Mat([[fine[j-i] for j in range(n)] for i in range(n)])
        fine_sha = exact.vector_hash([z for row in fine_matrix for z in row])
        need(fine_sha == record["fine_reference_sha256"], "saved finer reference matrix hash")
        records.append(dict(label=record["label"], **fields, fine_reference_bits=fine_bits,
                            fine_reference_error=str(fine_error), fine_reference_sha256=fine_sha,
                            fine_offsets=fine_offsets))
    probe = producer
    probe.probe_label, probe.probe_stage = "stress", "saved-exponential-stress"
    stresses = []
    for row in saved["enclosures"]:
        box = probe.exponential(Q(row["factor"]), row["bits"])
        need(box.lo == row["lo"] and box.hi == row["hi"], "saved stress interval replay")
        stresses.append(dict(row))
    probe.probe_stage = "near-shortcut-stress"
    additional_stress = []
    for bits in (16, 38, 70):
        center = Q(bits * 113, 355)
        for factor in (Q(bits, 4), Q(bits, 3), center-Q(1, 10**8),
                       center+Q(1, 10**8), Q(1, 1 << (bits+8))):
            box = probe.exponential(factor, bits)
            need(0 <= box.lo <= box.hi <= box.scale, "additional stress range")
            additional_stress.append({"bits": bits, "factor": str(factor),
                                      "lower": str(Q(box.lo, box.scale)),
                                      "upper": str(Q(box.hi, box.scale)),
                                      "zero_one_grid_shape": box.lo == 0 and box.hi == 1})
    unique = {event["id"]: {k: event[k] for k in ("id", "factor", "bits")} for event in events}
    queries = {"schema_version": 1, "source_head": HEAD,
               "scope": "actual scalar inputs only; no source interval endpoints or expected answers",
               "queries": sorted(unique.values(), key=lambda x: (x["bits"], Q(x["factor"])))}
    report = {"source_head": HEAD, "source_sha256": PINS,
              "initial_zero_exact_one": True, "cases": records, "events": events,
              "stress_cases": stresses, "additional_stress": additional_stress,
              "request_count": len(events), "unique_requests": len(unique),
              "query_canonical_sha256": sha(canonical(queries)),
              "full_constructed": False, "compile_called": False, "gates_executed": False}
    return queries, report


def read_certificates(path, queries):
    data = path.read_bytes()
    need(ORACLE_RESULT_SHA is not None and sha(data) == ORACLE_RESULT_SHA, "frozen independent output hash")
    independent = json.loads(data)
    rows = independent["results"]
    expected = {r["id"]: r for r in queries["queries"]}
    need(len(rows) == len(expected), "independent query count")
    certificates = {}
    for row in rows:
        key = row["id"]
        need(key in expected and key not in certificates, "independent query identity")
        need(Q(row["factor"]) == Q(expected[key]["factor"]) and row["bits"] == expected[key]["bits"],
             "independent query parameters")
        interval = row["exp_negative_pi_factor"]
        lower, upper = Q(interval["lower"]), Q(interval["upper"])
        need(0 <= lower <= upper <= 1, "independent exponential range")
        certificates[key] = (lower, upper)
    return certificates


def source_fault_controls(source, certificates):
    """Calibrate semantic rejection with actual source calls and restored patches."""
    gaussian = sys.modules["gaussian"]
    raw = {gaussian.INTERVALS: (source / "intervals.py").read_bytes(),
           gaussian.EVALUATOR: (source / "source_evaluator.py").read_bytes()}
    backend = gaussian.load_intervals(raw[gaussian.INTERVALS])
    # Original Gaussian.exponential, with a faulty pi backend that returns one.
    original_pi = backend.pi_interval
    backend.pi_interval = lambda bits: backend.Interval.rational(1, bits)
    try:
        probe = object.__new__(gaussian.Gaussian)
        probe.oracle = backend
        wrong = probe.exponential(Q(1, 4), 16)
    finally:
        backend.pi_interval = original_pi
    wrong_interval = Q(wrong.lo, wrong.scale), Q(wrong.hi, wrong.scale)
    correct = certificates[request_id(Q(1, 4), 16)]
    need(wrong_interval[1] < correct[0] or wrong_interval[0] > correct[1],
         "omitted pi source fault is independently disjoint")
    # Original coefficient method; retain its real quantized value but forge its error.
    original_quantize = backend.inward_quantize
    def underbill(boxes, bits):
        numerators, _ = original_quantize(boxes, bits)
        return numerators, Q(0)
    backend.inward_quantize = underbill
    try:
        producer = gaussian.Gaussian(raw, 2, Q(1), Q(1, 3), Q(65), 8, 3, 1)
        value = producer.coefficient(1)
        row = producer.offsets[1]
    finally:
        backend.inward_quantize = original_quantize
    lo, hi = certificates[request_id(row["factor"], producer.working_bits)]
    need(row["error"] == 0 and (value < lo or value > hi),
         "underbilled quantization source fault has actual nonzero error")
    # Original automatic cutoff/Tsec, with an unpaid zero tail at every cutoff.
    original_tail = gaussian.Gaussian.tail
    gaussian.Gaussian.tail = lambda self, window: Q(0)
    try:
        producer = gaussian.Gaussian(raw, 8, Q(2), Q(1, 3), Q(260), 20, 3)
        matrix = producer.namespace["Tsec"](8, gaussian.PiMultiple(Q(2)), Q(1, 3)).astype(complex)
    finally:
        gaussian.Gaussian.tail = original_tail
    witness_lower = certificates[request_id(Q(2, 3), 150)][0]
    need(producer.window == 0 and producer.tail_bound == 0 and matrix[0][1] == 0
         and witness_lower > 0, "zero-tail source fault omits an independently positive coefficient")
    need(producer.builder is None and producer.plan is None, "fault controls do not compile Full")
    return {
        "omitted_pi": {"rejected": True, "factor": "1/4", "bits": 16,
                       "faulty_source_interval": list(map(str, wrong_interval)),
                       "independent_interval": list(map(str, correct)),
                       "reason": "actual source exponential yields disjoint interval"},
        "underbilled_quantization": {"rejected": True, "value": str(value), "forged_error": "0",
                                     "independent_interval": [str(lo), str(hi)],
                                     "reason": "actual quantized value lies outside its forged zero-error certificate"},
        "zero_tail": {"rejected": True, "n": 8, "window": producer.window,
                      "claimed_tail": "0", "dropped_offset": 1,
                      "independent_dropped_coefficient_lower": str(witness_lower),
                      "reason": "actual source auto-cutoff drops a certified positive finite offset"},
    }


def audit(source, oracle_path, queries, report):
    certificates = read_certificates(oracle_path, queries)
    event_checks = 0
    shortcuts, nonshortcuts, exact_zeros = 0, 0, 0
    for event in report["events"]:
        lower, upper = certificates[event["id"]]
        need(Q(event["lower"]) <= lower <= upper <= Q(event["upper"]),
             "independent interval contained in actual source interval: " + event["id"])
        if not event["backend_arguments"]:
            need(Q(event["factor"]) == 0 and lower == upper == 1, "exact-zero bypass")
            exact_zeros += 1
        else:
            need(len(event["backend_arguments"]) == 1, "one actual exp backend call")
            if event["backend_arguments"][0]["shortcut_condition"]:
                shortcuts += 1
            else:
                nonshortcuts += 1
        event_checks += 1
    need(shortcuts > 0 and nonshortcuts > 0 and exact_zeros > 0, "all scalar evaluation regimes witnessed")
    cases = []
    retained_checks, finite_checks = 0, 0
    for case in report["cases"]:
        n, c = case["n"], Q(case["c"])
        cond = certificates[request_id(1/(4*c), case["conditioning_bits"])]
        lower = Q(case["conditioning_interval"][0])
        qbar = Q(case["ideal_inverse_bound"])
        need(0 < lower <= cond[0] <= cond[1] and qbar == n/lower,
             "actual conditioning reciprocal bound independently enclosed")
        retained_upper = Q(0)
        for row in case["offsets"]:
            lo, hi = certificates[request_id(Q(row["factor"]), case["working_bits"])]
            value, error = Q(row["value"]), Q(row["error"])
            actual_error_upper = max(abs(value-lo), abs(value-hi))
            need(actual_error_upper <= error, "retained quantized error independently certified")
            retained_upper += actual_error_upper
            retained_checks += 1
        omitted_lower, omitted_upper = Q(0), Q(0)
        finite_total = Q(0)
        offsets = {r["offset"]: r for r in case["offsets"]}
        for row in case["fine_offsets"]:
            lo, hi = certificates[row["id"]]
            source_lo, source_hi = Q(row["lower"]), Q(row["upper"])
            need(source_lo <= lo <= hi <= source_hi, "finer reference scalar enclosure")
            if abs(row["offset"]) > case["window"]:
                omitted_lower += lo
                omitted_upper += hi
                finite_total += hi
            else:
                value = Q(offsets[row["offset"]]["value"])
                finite_total += max(abs(value-lo), abs(value-hi))
            finite_checks += 1
        need(omitted_upper <= Q(case["tail_bound"]), "independent finite omitted tail below actual geometric allowance")
        need(finite_total <= Q(case["kernel_error"]) <= Q(case["epsilon"]),
             "independent finite coefficient ledger within actual kernel budget")
        need(Q(case["epsilon"])*qbar <= Q(1, 2), "actual scalar perturbation margin")
        cases.append({"label": case["label"], "n": n, "shift": case["shift"],
                      "incoming_bits": case["incoming_bits"], "window": case["window"],
                      "target_bits": case["target_bits"], "coefficient_bits": case["coefficient_bits"],
                      "qbar": str(qbar), "finite_omitted_lower": str(omitted_lower),
                      "finite_omitted_upper": str(omitted_upper), "source_tail_allowance": case["tail_bound"],
                      "retained_error_upper": str(retained_upper),
                      "finite_kernel_error_upper": str(finite_total), "source_kernel_allowance": case["kernel_error"]})
    need(len(cases) == 9 and retained_checks == 43 and finite_checks == 61, "complete selected finite coverage")
    need(any(Q(c["finite_omitted_lower"]) > 0 for c in cases), "positive finite tail witnessed")
    controls = source_fault_controls(source, certificates)
    return {"status": "PASS_INDEPENDENT_SCALAR_BACKEND_AUDIT", "source_head": HEAD,
            "source_sha256": PINS, "query_canonical_sha256": sha(canonical(queries)),
            "oracle_result_sha256": ORACLE_RESULT_SHA,
            "source_capture_canonical_sha256": sha(canonical(report)),
            "source_events_checked": event_checks, "unique_scalar_queries": len(certificates),
            "certified_relation": "every independent certified interval is contained in the actual source interval",
            "actual_backend_regimes": {"shortcut": shortcuts, "nonshortcut": nonshortcuts,
                                       "exact_zero_bypass": exact_zeros},
            "retained_quantized_offsets_checked": retained_checks, "finite_offsets_checked": finite_checks,
            "cases": cases, "source_fault_controls": controls,
            "scope": "finite normalized scalar backend, source table/conditioning/quantization/tail ledger",
            "full_constructed": False, "compile_called": False, "gates_executed": False,
            "limits": ["finite source-bound checks, not universal analytic or width acceptance",
                       "no Full/admission/gate/circuit replay", "no raw gauges or physical delivery",
                       "no proof-assistant verification or new kappa"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument("--source", type=Path, default=here / "source")
    parser.add_argument("--query-output", type=Path)
    parser.add_argument("--capture-output", type=Path)
    parser.add_argument("--oracle", type=Path, default=here / "ORACLE-QUERY-RESULT.json")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected", type=Path, default=here / "INTEGRATION-RESULT.json")
    parser.add_argument("--capture-expected", type=Path, default=here / "SOURCE-CAPTURE.json")
    args = parser.parse_args()
    queries, report = capture(args.source)
    if args.query_output:
        args.query_output.write_text(json.dumps(queries, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    if args.capture_output:
        args.capture_output.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    if args.prepare_only:
        result = {"status": "PASS_SCALAR_SOURCE_CAPTURE", "cases": len(report["cases"]),
                  "actual_requests": report["request_count"], "unique_requests": report["unique_requests"],
                  "query_canonical_sha256": report["query_canonical_sha256"]}
    else:
        result = audit(args.source, args.oracle, queries, report)
        if not args.output:
            need(canonical(json.loads(args.expected.read_bytes())) == canonical(result),
                 "complete typed integration receipt matches actual replay")
            need(sha(canonical(json.loads(args.capture_expected.read_bytes())))
                 == result["source_capture_canonical_sha256"],
                 "retained complete scalar capture matches actual replay")
    payload = json.dumps(result, sort_keys=True, indent=2)+"\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
