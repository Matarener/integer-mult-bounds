#!/usr/bin/env python3
"""Check eight source slices and their complete concave-cost certificates."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz"
PAYLOAD_HASH = "cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd"
ROLES = [("L", i) for i in range(632)] + [("C", 0)]
F = Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def histogram(value):
    return {str(k): v for k, v in sorted(value.items()) if v}


def authenticate(data, wanted):
    require(digest(data) == wanted, "Input hash mismatch")


def read_source():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    pins = [r for r in manifest["files"] if r["usage"] == "input"]
    require({r["path"] for r in pins} == {SOURCE, "scripts/compare_recursive_invoices.py"},
            "The live input set changed")
    for pin in pins:
        authenticate((ROOT / pin["path"]).read_bytes(), pin["sha256"])
    raw = gzip.decompress((ROOT / SOURCE).read_bytes())
    authenticate(raw, PAYLOAD_HASH)
    word = json.loads(raw)
    require(word["canonical"]["v"] == 112 and word["canonical"]["h"] == 9,
            "The source geometry changed")
    return word


def load_comparator():
    path = ROOT / "scripts/compare_recursive_invoices.py"
    spec = importlib.util.spec_from_file_location("slice_invoice_preflight", path)
    require(spec is not None and spec.loader is not None, "Cannot load the price checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_rows(direction, active):
    rows = {}
    for i in range(632):
        row = {(("L", i), ()): F(1)} if i >= 224 or i in active else {}
        donor = i - 112 if direction == "forward" else i + 112
        receiver = i >= 112 if direction == "forward" else i < 112
        if i < 224 and receiver and donor in active:
            row[(("L", donor), ())] = F(1 if direction == "forward" else -1)
        rows["L", i] = row
    rows["C", 0] = {}
    return rows


def initial_rows(active):
    return {r: ({(r, ()): F(1)} if r[0] == "L" and (r[1] >= 224 or r[1] in active)
                else {}) for r in ROLES}


def apply_scalar(rows, op):
    name, target = op[0], tuple(op[1])
    if name == "clear":
        rows[target] = {}
    elif name == "copy":
        rows[target] = dict(rows[tuple(op[2])])
    elif name == "scale":
        factor = F(op[2], op[3])
        rows[target] = {key: value * factor for key, value in rows[target].items()
                        if value * factor}
    elif name == "add":
        factor = F(op[3], op[4])
        for key, value in list(rows[tuple(op[2])].items()):
            result = rows[target].get(key, F(0)) + factor * value
            if result:
                rows[target][key] = result
            else:
                rows[target].pop(key, None)
    else:
        raise ValueError("Unknown scalar operation")


def replay(program, active, direction, skip_prefix=0):
    rows = initial_rows(active)
    versions = {r: None for r in ROLES}
    nodes, zero_paid = [], set()
    paid = Counter()
    for index, event in enumerate(program):
        if index < skip_prefix:
            continue
        kind = event[0]
        if kind in {"adapter", "phase"}:
            continue  # These records do not change the formal logical row.
        if kind == "scalar":
            op = event[1]
            target = tuple(op[1])
            deps = [versions[target]]
            if op[0] == "clear":
                deps = []
            elif op[0] == "copy":
                deps = [versions[tuple(op[2])]]
            elif op[0] == "add":
                deps.append(versions[tuple(op[2])])
            apply_scalar(rows, op)
        elif kind == "warp":
            target = tuple(event[1])
            deps = [versions[target]]
            symbol = event[2]
            if direction == "backward":
                symbol += 1000000 if symbol > 0 else -1000000
            rows[target] = {(owner, tail[1:] if tail and tail[0] == -symbol
                              else (symbol,) + tail): value
                            for (owner, tail), value in rows[target].items()}
        elif kind in {"climb", "center"}:
            target = ("L", event[2]) if kind == "climb" else ("C", event[1])
            deps = [versions[target]]
            paid[event[-1]] += 1
            if not rows[target]:
                zero_paid.add(index)
        else:
            raise ValueError("Unknown source event")
        versions[target] = len(nodes)
        nodes.append((index, tuple(v for v in deps if v is not None)))
    return rows, versions, nodes, zero_paid, paid


def dependency_slice(versions, nodes, demanded):
    pending = [versions[r] for r in demanded]
    live = set()
    while pending:
        node = pending.pop()
        if node is None or node in live:
            continue
        live.add(node)
        pending.extend(nodes[node][1])
    return {nodes[node][0] for node in live}


def check_endpoints(rows, expected, demanded):
    require(all(rows[r] == expected[r] for r in demanded), "A retained endpoint changed")
    require(rows["C", 0] == {}, "The owned center did not return zero")


def targets(canonical, input_bank, output_bank):
    frames, starts, ends = canonical["frames"], canonical["start"], canonical["final"]
    result = Counter(len(frames[ends[i]]) - len(frames[starts[i]]) for i in range(224, 632))
    require(result == Counter({4: 28, 7: 7, 8: 47, 9: 326}), "The helper target census changed")
    if output_bank is not None:
        result[8 if input_bank == output_bank else 9] += 112
    return result


def invoice(paid, target):
    return {"schema": "integer-mult-recursive-invoice/v1",
            "contract": {"model": "mixed-target-unnormalized-power-v1",
                         "rank_semantics": "H_r costs r^t for 0<t<1; all retained helper targets credited",
                         "ambient_rank": 9,
                         "boundary": "one declared formal dependency slice; physical repairs granted free"},
            "paid": histogram(paid), "targets": histogram(target)}


def price_certificate(paid, target, comparator):
    hinges = {str(a): sum(n * min(r, a) for r, n in paid.items()) -
              sum(n * min(r, a) for r, n in target.items()) for a in range(1, 10)}
    require(all(v >= 0 for v in hinges.values()) and hinges["1"] > 0,
            "The strict concave-power rejection failed")
    comparison = comparator.compare_invoices(invoice(Counter(), Counter()), invoice(paid, target))
    require(comparison["classification"] == "uniformly_worse", "The shared preflight disagrees")
    return hinges


def one_case(word, direction, input_bank, output_bank, comparator, skip_prefix=0):
    active = set(range(112 * input_bank, 112 * (input_bank + 1))) if input_bank is not None else set()
    kept = list(range(112 * output_bank, 112 * (output_bank + 1))) if output_bank is not None else []
    demanded = [("L", i) for i in range(224, 632)] + [("L", i) for i in kept]
    program = word["programs"][direction]
    rows, versions, nodes, zero_paid, paid = replay(program, active, direction, skip_prefix)
    expected = expected_rows(direction, active)
    check_endpoints(rows, expected, demanded if skip_prefix else ROLES[:-1])
    if not skip_prefix:
        require(histogram(paid) == word["canonical"]["local_profile"], "The source paid census changed")
    live = dependency_slice(versions, nodes, demanded + [("C", 0)])
    retained = Counter(program[i][-1] for i in live - zero_paid if program[i][0] in {"climb", "center"})
    selected = [e for i, e in enumerate(program) if i in live and i not in zero_paid]
    sliced_rows = replay(selected, active, direction)[0]
    check_endpoints(sliced_rows, expected, demanded)
    target = targets(word["canonical"], input_bank, output_bank)
    hinges = price_certificate(retained, target, comparator)
    return {"direction": direction, "input_bank": input_bank, "output_bank": output_bank,
            "skipped_prefix": skip_prefix, "formal_endpoint_rows": len(demanded) if skip_prefix else 632,
            "slice_endpoint_rows": len(demanded), "paid": histogram(retained), "targets": histogram(target),
            "zero_paid_events": len(zero_paid), "live_events": len(live),
            "paid_event_ids_sha256": digest(packed(sorted(i for i in live - zero_paid
                                                    if program[i][0] in {"climb", "center"}))),
            "retained_event_ids_sha256": digest(packed(sorted(live - zero_paid))),
            "rank_surplus": sum(r*n for r,n in target.items()) - sum(r*n for r,n in retained.items()),
            "paid_minus_target_hinges": hinges, "all_strict_concave_power_tariffs_fail": True}


def must_reject(action, label):
    try:
        action()
    except (ValueError, KeyError):
        return label
    raise ValueError("A negative control was accepted: " + label)


def compute(word, comparator):
    rows = []
    for direction in ("forward", "backward"):
        choices = [(0, 0), (0, 1), (1, 1), (None, None)] if direction == "forward" else [
            (0, 0), (1, 0), (1, 1), (None, None)]
        rows.extend(one_case(word, direction, a, b, comparator) for a, b in choices)
    require(word["programs"]["forward"][6037] == ["phase", "entry_adapters"],
            "The prefix boundary changed")
    prefix = [one_case(word, "forward", a, b, comparator, 6037)
              for a, b in [(0, 0), (None, None)]]
    require(prefix[0]["paid"] == rows[0]["paid"] and prefix[1]["paid"] == rows[3]["paid"],
            "The prefix-removal invoice changed")
    mutation = dict(expected_rows("forward", set()))
    mutation["L", 224] = {}
    changed_program = json.loads(json.dumps(word["programs"]["forward"]))
    require(changed_program[21447] == ["scalar", ["add", ["L", 382], ["L", 383], -1, 1], 1],
            "The semantic control source event changed")
    changed_program[21447][1][3] = 1
    changed_rows = replay(changed_program, set(), "forward")[0]
    controls = [
        must_reject(lambda: check_endpoints(changed_rows, expected_rows("forward", set()), ROLES[:-1]),
                    "wrong sign at the last helper ADD"),
        must_reject(lambda: authenticate(b"changed", PAYLOAD_HASH), "changed source bytes"),
        must_reject(lambda: check_endpoints(mutation, expected_rows("forward", set()), [("L", 224)]),
                    "missing independent helper output"),
        must_reject(lambda: price_certificate(Counter({1: 1}), Counter({9: 1}), comparator),
                    "unearned target credit"),
    ]
    positive = comparator.compare_invoices(invoice(Counter({1: 1, 8: 1}), Counter({9: 1})),
                                           invoice(Counter(), Counter()))
    require(positive["classification"] == "uniformly_better", "The positive concavity control failed")
    return {"status": "PASS_NATIVE_MAIN_BANK_SLICE_GATE_NO_NEW_KAPPA", "source_payload_sha256": PAYLOAD_HASH,
            "complete_kappa_improvement": False, "cases": rows, "prefix_variants": prefix,
            "negative_controls": controls, "positive_control": "H1+H8 minus H9 has strict positive cost"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true", help="Write the author receipt; this is not a frozen-receipt replay")
    args = parser.parse_args()
    result = compute(read_source(), load_comparator())
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print("WROTE_AUTHOR_RECEIPT")
    else:
        require(result == json.loads((PACKAGE / "RESULT.json").read_text()), "The scientific receipt changed")
        print(result["status"])
        print("Eight slices and two prefix variants; all independent helper targets are retained.")


if __name__ == "__main__":
    main()
