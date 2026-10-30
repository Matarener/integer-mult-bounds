#!/usr/bin/env python3
"""Exact, source-bound local circuit check; not a full theorem verification.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The whole-word row/column checks are credited, authenticated predecessor code.
The dense integer prefix check below is separate from the sparse synthesizer.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/p104-helper470-twin-rung-removal/"
LOCAL = "research/p104-unread-path-resynthesis/local.py"
START, STOP, FRAME = 1, 9896, 3


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    # Round-trip first so that all mapping keys have their JSON string form.
    return json.dumps(json.loads(json.dumps(value)), sort_keys=True,
                      separators=(",", ":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def load_code(raw, path, name):
    """Execute the bytes just read, never a preexisting bytecode cache."""
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def authenticated_inputs(root):
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    data = {}
    for item in manifest["files"]:
        if item["usage"] == "input":
            raw = (root / item["path"]).read_bytes()
            need(sha256(raw).hexdigest() == item["sha256"],
                 "Source SHA256: " + item["path"])
            data[item["path"]] = raw
    need(set(data) == {SOURCE + "WORD.json.gz", SOURCE + "RESULT.json", LOCAL},
         "Complete live source inventory")
    return data


def check_alphabet(program, available):
    for event in program:
        need(event[0] in ("ADD", "SCALE"), "Scalar-only prefix")
        need(len(event) == (5 if event[0] == "ADD" else 4), "Event arity")
        need(event[-1] == FRAME and event[1] in available, "Available scalar chart")
        q = Q(event[-2])
        n, d = abs(q.numerator), q.denominator
        need(q and d & (d - 1) == 0, "Nonzero dyadic coefficient")
        need(abs(q) + 1 < 2**16, "Inherited fixed coefficient bound")
        if event[0] == "SCALE":
            need(n & (n - 1) == 0, "Invertible dyadic SCALE")
        else:
            need(event[2] in available and event[1] != event[2], "Available distinct source")


def integer_matrix(program, roles):
    """All entries, with one integer numerator row and binary denominator.

    This does not call the synthesizer's Fraction/sparse row routines. It
    checks arbitrary independent entry values, including the owned role.
    """
    index = {role: i for i, role in enumerate(roles)}
    size = len(roles)
    rows = [[int(i == j) for j in range(size)] for i in range(size)]
    exponents = [0] * size
    max_l1 = Q(1)
    for event in program:
        destination = index[event[1]]
        q = Q(event[-2])
        numerator, denominator = q.numerator, q.denominator
        need(denominator & (denominator - 1) == 0, "Integer engine dyadic input")
        shift = denominator.bit_length() - 1
        if event[0] == "SCALE":
            rows[destination] = [numerator * x for x in rows[destination]]
            exponents[destination] += shift
        else:
            need(event[0] == "ADD", "Integer engine opcode")
            source = index[event[2]]
            level = max(exponents[destination], exponents[source] + shift)
            a = 1 << (level - exponents[destination])
            b = numerator << (level - exponents[source] - shift)
            rows[destination] = [a * x + b * y for x, y in
                                 zip(rows[destination], rows[source])]
            exponents[destination] = level
        while exponents[destination] and all(x % 2 == 0 for x in rows[destination]):
            rows[destination] = [x // 2 for x in rows[destination]]
            exponents[destination] -= 1
        max_l1 = max(max_l1, Q(sum(map(abs, rows[destination])),
                               1 << exponents[destination]))
    return {"rows": rows, "exponents": exponents}, str(max_l1)


def inverse(program):
    answer = []
    for original in reversed(program):
        event = original.copy()
        q = Q(event[-2])
        event[-2] = str(-q if event[0] == "ADD" else 1 / q)
        answer.append(event)
    return answer


def scalar_allowance(program):
    total = 0
    for event in program:
        op = event[0]
        if op in ("INIT", "CLEAR"):
            total += 2
        elif op == "MOVE":
            continue
        else:
            q = Q(event[-2])
            n, d = abs(q.numerator), q.denominator
            if op == "SCALE":
                total += 2 * (abs(n.bit_length() - d.bit_length()) + int(q < 0))
            else:
                need(op in ("ADD", "COPY"), "Tariff opcode")
                total += 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)
    return total


def rejected(check, label):
    try:
        check()
    except ValueError as error:
        return str(error)
    raise ValueError("Negative control unexpectedly accepted: " + label)


def controls(prefix, roles, matrix, available, candidate, local, inputs):
    results = {}
    def mismatch(program):
        need(integer_matrix(program, roles)[0] == matrix, "Arbitrary-entry prefix matrix")

    wrong_sign = deepcopy(prefix)
    add_index = next(i for i, event in enumerate(prefix) if event[0] == "ADD")
    wrong_sign[add_index][-2] = str(-Q(wrong_sign[add_index][-2]))
    results["wrong_ADD_sign"] = rejected(lambda: mismatch(wrong_sign), "ADD sign")
    missing_scale = deepcopy(prefix)
    del missing_scale[next(i for i, event in enumerate(prefix) if event[0] == "SCALE")]
    results["missing_SCALE"] = rejected(lambda: mismatch(missing_scale), "SCALE omission")
    # The actual owned role is initialized to zero immediately before the cut.
    # Multiplying it there by two is invisible to that specialization, but must
    # fail the stronger arbitrary-entry local certificate.
    results["owned_zero_specialization"] = rejected(
        lambda: mismatch([["SCALE", 778, "2", FRAME]] + prefix), "Owned zero assumption")
    specialized = deepcopy(candidate)
    specialized["program"].insert(START, ["SCALE", 778, "2", FRAME])
    local.replay(specialized)
    results["owned_zero_specialization_whole_word"] = "PASS as expected; only the stronger local obligation rejects it"
    for name, changed in (("wrong_chart", deepcopy(prefix)),
                          ("odd_denominator", deepcopy(prefix)),
                          ("unavailable_source", deepcopy(prefix))):
        if name == "wrong_chart":
            changed[add_index][-1] = 7
        elif name == "odd_denominator":
            changed[add_index][-2] = "1/3"
        else:
            need(0 not in available, "Unavailable-source control fixture")
            changed[add_index][2] = 0
        results[name] = rejected(lambda: check_alphabet(changed, available), name)
    damaged = deepcopy(candidate)
    damaged["program"][START + add_index][-2] = wrong_sign[add_index][-2]
    results["whole_word_wrong_sign"] = rejected(lambda: local.replay(damaged), "Whole-word sign")
    with tempfile.TemporaryDirectory(prefix="p104-prefix-control-") as temporary:
        root = Path(temporary)
        for path, raw in inputs.items():
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        for path, raw in inputs.items():
            (root / path).write_bytes(raw + b" ")
            results["damaged_" + Path(path).name] = rejected(
                lambda: authenticated_inputs(root), path)
            (root / path).write_bytes(raw)
    fixture = [["ADD", 4, 9, "1/2", FRAME], ["SCALE", 9, "-2", FRAME],
               ["ADD", 9, 4, "3/4", FRAME]]
    need(integer_matrix(fixture, [4, 9])[0]
         == {"rows": [[2, 1], [6, -13]], "exponents": [1, 3]},
         "Integer engine explicit positive fixture")
    need(integer_matrix(fixture + inverse(fixture), [4, 9])[0]
         == integer_matrix([], [4, 9])[0], "Integer engine inverse positive fixture")
    results["dyadic_inverse_positive_fixture"] = "PASS"
    return results


def run():
    inputs = authenticated_inputs(ROOT)
    source = json.loads(gzip.decompress(inputs[SOURCE + "WORD.json.gz"]))
    source_result = json.loads(inputs[SOURCE + "RESULT.json"])
    local = load_code(inputs[LOCAL], ROOT / LOCAL, "p104_credited_local")
    synthesis = load_code((HERE / "synthesize.py").read_bytes(), HERE / "synthesize.py", "prefix_synthesis")
    program = source["program"]
    need(len(program) == 22803 and program[0] == ["INIT", 778, FRAME], "Frozen prefix entry")
    need(program[STOP][0] == "MOVE" and source["frames"][FRAME] == [], "Frozen prefix exit/chart")
    old_prefix = program[START:STOP]
    roles = sorted({event[1] for event in old_prefix}
                   | {event[2] for event in old_prefix if event[0] == "ADD"})
    available = {i for i, frame in enumerate(source["initial"]) if frame == FRAME} | {778}
    need(set(roles) <= available, "All touched roles available at entry")
    check_alphabet(old_prefix, available)
    replacement, discovery = synthesis.synthesize(old_prefix)
    check_alphabet(replacement, set(roles))
    old_matrix, old_norm = integer_matrix(old_prefix, roles)
    new_matrix, new_norm = integer_matrix(replacement, roles)
    need(new_matrix == old_matrix, "Exact arbitrary-entry prefix equality")
    need(integer_matrix(replacement + inverse(replacement), roles)[0]
         == integer_matrix([], roles)[0], "Complete inverse-prefix identity")
    _, inverse_norm = integer_matrix(inverse(replacement), roles)
    candidate = deepcopy(source)
    candidate["program"] = program[:START] + replacement + program[STOP:]
    need({k: v for k, v in candidate.items() if k != "program"}
         == {k: v for k, v in source.items() if k != "program"}, "All boundary and frame metadata unchanged")
    need([e for e in candidate["program"] if e[0] not in ("ADD", "SCALE")]
         == [e for e in program if e[0] not in ("ADD", "SCALE")], "All non-scalar events unchanged")
    old_local, new_local = local.replay(source), local.replay(candidate)
    need(canonical(old_local) == canonical(source_result["local"]), "Pinned source receipt replay")
    for key in old_local:
        if key != "real_scalar_allowance":
            need(old_local[key] == new_local[key], "Unchanged local invoice: " + key)
    old_cost, new_cost = scalar_allowance(program), scalar_allowance(candidate["program"])
    need(old_cost == old_local["real_scalar_allowance"]
         and new_cost == new_local["real_scalar_allowance"], "Separate complete scalar tariff")
    need(len(replacement) < len(old_prefix) and new_cost < old_cost, "Strict event and allowance savings")
    columns = local.reverse_columns(candidate)
    negative_controls = controls(replacement, roles, old_matrix, available, candidate, local, inputs)
    calls = source_result["physical_caller"]["full_calls"]
    # Retain, rather than tighten, PR6030 pricing.py's complete envelopes.
    # Its native/caller implementation assumptions are inherited, not replayed.
    ports = len(candidate["live"])
    local_routes = (sum(new_local["paid"].values()) + 2 * sum(new_local["helpers"].values())
                    + 2 * ports + 4 * ports + 4 * new_local["owned_lifetimes"]) * 1000
    need(local_routes == source_result["complete_cost"]["nonrecursive"]["local_routes"],
         "Unchanged route, normalizer, adapter and lifetime envelope")
    need(new_cost + local_routes < 10**7, "Complete local ordinary budget")
    raw = source_result["complete_cost"]["nonrecursive"]["raw_scalar_upper"]
    need(raw < 10**9, "Pinned inherited caller ordinary envelope")
    receipt = {
        "status": "PASS_P104_PREFIX_ROW_SYNTHESIS",
        "base_commit": json.loads((HERE / "SOURCES.json").read_bytes())["base_commit"],
        "cut": {"start_inclusive": START, "stop_exclusive": STOP, "frame": FRAME,
                "roles": len(roles), "explicit_matrix_entries": len(roles)**2,
                "untouched_roles": source["public"] + source["owned_fields"] - len(roles)},
        "discovery": discovery,
        "before": {"prefix_events": len(old_prefix), "word_events": len(program),
                   "prefix_opcodes": dict(Counter(e[0] for e in old_prefix)),
                   "prefix_scalar_allowance": scalar_allowance(old_prefix), "local": old_local},
        "after": {"prefix_events": len(replacement), "word_events": len(candidate["program"]),
                  "prefix_opcodes": dict(Counter(e[0] for e in replacement)),
                  "max_absolute_prefix_coefficient": str(max(abs(Q(e[-2])) for e in replacement)),
                  "prefix_scalar_allowance": scalar_allowance(replacement), "local": new_local},
        "saved": {"events_per_local_call": len(old_prefix) - len(replacement),
                  "scalar_allowance_per_local_call": old_cost - new_cost,
                  "inherited_full_forward_calls": calls,
                  "scalar_allowance_across_inherited_forward_calls": calls * (old_cost - new_cost)},
        "canonical_sha256": {"replacement_prefix": digest(replacement),
                             "complete_candidate_word": digest(candidate),
                             "integer_prefix_matrix": digest(new_matrix)},
        "prefix_max_row_l1": {"source": old_norm, "candidate": new_norm,
                              "candidate_inverse": inverse_norm,
                              "scope": "Exact intermediate scalar prefix matrices only; not a rounded error analysis."},
        "complete_columns": columns,
        "inherited_budgets": {"local_routes_normalizers_adapters_and_lifetimes": local_routes,
                              "local_ordinary_before": old_cost + local_routes,
                              "local_ordinary_after": new_cost + local_routes,
                              "local_allowance": 10**7,
                              "complete_caller_ordinary_envelope": raw,
                              "complete_caller_allowance": 10**9,
                              "complete_caller_envelope_recomputed": False,
                              "paid_calls": source_result["complete_cost"]["paid_calls"],
                              "productive_fields": source_result["complete_cost"]["productive_fields"],
                              "native_and_physical_caller_replayed": False},
        "controls": negative_controls,
        "kappa": {"changed": False, "selected": source_result["complete_cost"]["kappa"],
                  "claim": "No new kappa; isolated scalar-circuit result."},
    }
    return receipt, candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create an absent RESULT.json after all checks")
    parser.add_argument("--emit-word", type=Path, help="Create an absent JSON word outside the checkout")
    args = parser.parse_args()
    receipt, candidate = run()
    result_path = HERE / "RESULT.json"
    if args.write:
        with result_path.open("x") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        need(canonical(receipt) == canonical(json.loads(result_path.read_bytes())), "Committed result receipt")
    if args.emit_word:
        path = args.emit_word.resolve()
        need(not path.is_relative_to(ROOT), "Emit only outside the source checkout")
        with path.open("xb") as stream:
            stream.write(canonical(candidate) + b"\n")
    print(json.dumps(receipt, sort_keys=True))
    print(receipt["status"])


if __name__ == "__main__":
    main()
