"""Exact source-bound admission for the first P104 collector's producer cone.

Prepared by Clear1nsight with substantial OpenAI assistance. Apache-2.0.
The native word and Gaussian lattice retain their separately pinned authorship.
This module mutates no source file and performs no native/compiler build.
"""

import argparse
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from types import ModuleType


SOURCE_HASHES = {
    "word": "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50",
    "native": "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d",
    "model": "74c83367887dd885137b222155c86389fe0be9f1293a6f0e5fdb51d71f435fdd",
}
CUT = 2025
SIZE = 512
TARGETS = ("D31", "D30", "D29", "D28", "D27", "Q7")
Y_INPUTS = tuple("Y" + str(j) for j in list(range(22, 33)) + list(range(63, 104)))
SOURCE_FRAME = [256, 136, 64, 40, 16, 4, 2, 1]


class ProducerError(ValueError):
    """A source, numerical, or claimed admission obligation failed."""


def require(condition, message):
    if not condition:
        raise ProducerError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def read_pinned(path, label):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "regular source file required")
    with path.open("rb") as handle:
        data = handle.read(32 * 1024 * 1024 + 1)
    require(len(data) <= 32 * 1024 * 1024, "source size bound")
    return authenticated_bytes(data, label)


def authenticated_bytes(data, label):
    require(sha(data) == SOURCE_HASHES[label], "source digest mismatch: " + label)
    return data


def load_inputs(word_path, native_path, model_path):
    word_bytes = read_pinned(word_path, "word")
    native_bytes = read_pinned(native_path, "native")
    model_bytes = read_pinned(model_path, "model")
    word = json.loads(word_bytes)
    native = json.loads(gzip.decompress(native_bytes))
    model = ModuleType("p104_frozen_gaussian_model")
    exec(compile(model_bytes, str(model_path), "exec"), model.__dict__)
    return word, native, model


def extract_cone(word):
    """Backward slice using the authenticated destination-first ADD convention."""
    program = word["program"]
    needed = set(TARGETS)
    selected = []
    for event in reversed(range(CUT)):
        record = program[event]
        if record[1] not in needed:
            continue
        require(record[0] in ("transport", "add", "sign"), "producer instruction")
        selected.append(event)
        if record[0] == "add":
            needed.add(record[2])
    selected.reverse()
    require(needed == set(TARGETS) | set(Y_INPUTS), "exact 58 initial dependencies")
    require(len(selected) == 257, "exact producer cone size")
    counts = Counter(program[event][0] for event in selected)
    require(counts == {"transport": 200, "add": 57}, "exact producer instruction counts")
    require(all(word["initial_frames"][name] == [] for name in needed), "initial frames")
    return selected, sorted(needed)


def native_records(word, native, selected, model):
    occurrences = {}
    for item in native["transports"]:
        for event in item["events"]:
            require(event not in occurrences, "native event occurrence unique")
            occurrences[event] = item
    plans = {}
    for event in selected:
        record = word["program"][event]
        if record[0] != "transport":
            continue
        require(event in occurrences, "native event recipe exists")
        item = occurrences[event]
        require((item["old"], item["new"], item["recipe"]["rank"]) ==
                (record[2], record[3], record[4]), "native frame/rank binding")
        recipe = item["recipe"]
        require(type(recipe["rank"]) is int and 1 <= recipe["rank"] <= 9, "native rank")
        plans[event] = {"rank": recipe["rank"],
                        "right": model.wrapper_plan(recipe["right"]),
                        "left": model.wrapper_plan(recipe["left"])}
    return plans


def apply_wrapper(values, plan, model):
    require(len(values) == len(plan) == SIZE, "wrapper size")
    out = [(0, 0)] * SIZE
    for source, (target, phase) in enumerate(plan):
        out[target] = model.rot(values[source], phase)
    return out


def pi_valuation(value):
    if value == (0, 0):
        return None
    a, b = value
    valuation = 0
    while (a + b) % 2 == 0:
        a, b = (a + b) // 2, (b - a) // 2
        valuation += 1
    return valuation


def lattice_failure(values, model):
    for mask, coefficient in enumerate(model.newton(values)):
        valuation = pi_valuation(coefficient)
        if valuation is not None and valuation < mask.bit_count():
            return {"mask": mask, "degree": mask.bit_count(),
                    "coefficient": list(coefficient), "pi_valuation": valuation,
                    "required_pi_valuation": mask.bit_count()}
    return None


def exact_scale(values, coefficient):
    coefficient = Fraction(str(coefficient))
    p, q = coefficient.numerator, coefficient.denominator
    require(all(p * x % q == 0 for value in values for x in value),
            "fractional ADD is not exact on the retained grid")
    return [(p * a // q, p * b // q) for a, b in values]


def four_member(values, model):
    if any(x % 4 for value in values for x in value):
        return False
    return model.member(exact_scale(values, "1/4"))


def fingerprint(values, model):
    return {"sha256": sha(canonical(values)),
            "nonzero_complex_entries": sum(value != (0, 0) for value in values),
            "max_absolute_component": max(abs(x) for value in values for x in value),
            "in_B9": model.member(values), "newton_failure": lattice_failure(values, model)}


def native_execute(values, plan, model, counts, require_membership):
    values = apply_wrapper(values, plan["right"], model)
    if require_membership:
        require(model.member(values), "right wrapper preserves admitted domain")
    for bit in range(plan["rank"]):
        ideal = model.ideal_stage(values, bit)
        literal = model.lift_stage(values, bit)
        require(ideal == literal, "literal pair differs from exact ideal pair")
        if require_membership:
            require(model.member(literal), "coordinate prefix preserves admitted domain")
        counts["pair_obligations"] += SIZE // 2
        counts["coordinate_stages"] += 1
        values = literal
    values = apply_wrapper(values, plan["left"], model)
    if require_membership:
        require(model.member(values), "left wrapper preserves admitted domain")
    counts["native_calls"] += 1
    return values


def initial_admission(state, dependencies, model):
    require(set(state) == set(dependencies), "exact initial bank set")
    for values in state.values():
        require(model.validate(values) == 9, "nine-bit input bank")
    return {"all_initial_fields_in_B9": all(model.member(x) for x in state.values()),
            "Y_fields_outside_4B9": [name for name in Y_INPUTS if not four_member(state[name], model)]}


def replay_cone(word, plans, selected, dependencies, model, initial, require_admission):
    state = {name: values[:] for name, values in initial.items()}
    admission = initial_admission(state, dependencies, model)
    if require_admission:
        require(admission["all_initial_fields_in_B9"] and
                not admission["Y_fields_outside_4B9"], "producer entrance contract")
    frames = {name: word["initial_frames"][name][:] for name in dependencies}
    counts = {"native_calls": 0, "coordinate_stages": 0, "pair_obligations": 0,
              "quarter_adds": 0, "unit_adds": 0}
    failures = []
    for event in selected:
        record = word["program"][event]
        target = record[1]
        if record[0] == "transport":
            require(frames[target] == record[2], "native old frame at producer event")
            state[target] = native_execute(state[target], plans[event], model, counts, require_admission)
            frames[target] = record[3][:]
        else:
            apply_add(record, state, frames, model, counts)
        failure = lattice_failure(state[target], model)
        if failure is not None:
            failures.append({"event": event, "target": target, "witness": failure})
        if require_admission:
            require(failure is None, "producer output leaves lattice")
    require(all(frames[d] == SOURCE_FRAME for d in TARGETS[:5]), "final source frames")
    require(frames["Q7"] == [364], "final query frame")
    receipt = {"initial_admission": admission, "counts": counts,
               "all_fractional_adds_exact": True, "all_literal_native_pairs_exact": True,
               "first_lattice_failure": failures[0] if failures else None,
               "failing_event_outputs": failures,
               "entrance": {name: fingerprint(state[name], model) for name in TARGETS}}
    return state, receipt


def apply_add(record, state, frames, model, counts):
    _, target, source, coefficient, frame = record
    coefficient = add_contract(record, frames)
    if source in Y_INPUTS:
        counts["quarter_adds"] += 1
    else:
        counts["unit_adds"] += 1
    scaled = exact_scale(state[source], coefficient)
    state[target] = [model.add(a, b) for a, b in zip(state[target], scaled)]
    model.validate(state[target], 9)


def add_contract(record, frames):
    _, target, source, coefficient, frame = record
    require(frames[target] == frames[source] == frame, "ADD common frame")
    coefficient = Fraction(str(coefficient))
    if source in Y_INPUTS:
        require(target in TARGETS[:5] and coefficient == Fraction(1, 4), "actual quarter source")
    else:
        require(target == "Q7" and source in TARGETS[:5] and coefficient == -1,
                "actual Q7 subtraction")
    return coefficient


def validate_structure(word, selected, dependencies):
    frames = {name: word["initial_frames"][name][:] for name in dependencies}
    for event in selected:
        record = word["program"][event]
        if record[0] == "transport":
            require(frames[record[1]] == record[2], "native old frame at producer event")
            frames[record[1]] = record[3][:]
        else:
            add_contract(record, frames)
    require(all(frames[d] == SOURCE_FRAME for d in TARGETS[:5]), "final source frames")
    require(frames["Q7"] == [364], "final query frame")
    return frames


def dense_initial(dependencies, model):
    result = {}
    for ordinal, name in enumerate(dependencies):
        coefficients = [((17 * x + 13 * ordinal + (x >> 2)) % 19 - 9,
                         (11 * x + 7 * ordinal + (x >> 4)) % 23 - 11)
                        for x in range(SIZE)]
        values = model.encode(coefficients)
        result[name] = exact_scale(values, 4 if name in Y_INPUTS else 1)
    return result


def impulse_initial(dependencies, amplitude):
    result = {name: [(0, 0)] * SIZE for name in dependencies}
    result["Y27"][0] = (amplitude, 0)
    return result


def source_summary(word, selected, dependencies):
    program = word["program"]
    reads = {name: [] for name in Y_INPUTS}
    target_rows = {}
    for target in TARGETS:
        writes = [event for event in selected if program[event][1] == target]
        quarters = []
        for event in writes:
            record = program[event]
            if record[0] == "add" and record[2] in reads:
                reads[record[2]].append(event)
                quarters.append({"event": event, "source": record[2], "frame": record[4]})
        target_rows[target] = {"write_events": writes, "quarter_sources": quarters}
    require(all(len(events) == 1 for events in reads.values()), "each Y source used once in cone")
    return {"cut_before_event": CUT, "initial_dependencies": dependencies,
            "event_count": len(selected), "events": selected,
            "ordered_records_sha256": sha(canonical([[e, program[e]] for e in selected])),
            "native_rank_sum": sum(program[e][4] for e in selected if program[e][0] == "transport"),
            "target_paths": target_rows, "Y_read_events": reads,
            "scope": "numerical backward dependency cone; physical ownership remains external",
            "actual_cut_outputs": list(TARGETS),
            "auxiliary_Y_states": "historical last-required-read states, not actual cut outputs"}


def coefficient_valuation(coefficient):
    value = Fraction(str(coefficient))
    require(value != 0, "nonzero source coefficient")
    numerator, denominator = abs(value.numerator), value.denominator
    valuation = 0
    while numerator % 2 == 0:
        numerator //= 2
        valuation += 2
    while denominator % 2 == 0:
        denominator //= 2
        valuation -= 2
    require(denominator == 1, "dyadic scalar coefficient")
    return valuation


def impulse_prefix_valuation(word):
    """One-input reachability bound; no universal full-prefix admission claim."""
    lower = {"Y27": 12}
    active = []
    reads = []
    for event, record in enumerate(word["program"][:CUT]):
        kind, target = record[:2]
        if kind == "add":
            coefficient_valuation(record[3])
        elif kind == "sign":
            require(Fraction(str(record[2])) in (-1, 1), "source sign is a Gaussian unit")
        if kind == "transport" and target in lower:
            lower[target] -= record[4]
            require(lower[target] >= 0, "witness native prefix lacks pi factors")
            active.append({"event": event, "field": target, "lower_pi_valuation": lower[target]})
        elif kind == "add" and record[2] in lower:
            source = record[2]
            proposed = lower[source] + coefficient_valuation(record[3])
            require(proposed >= 0, "witness fractional source lacks pi factors")
            lower[target] = min(lower.get(target, proposed), proposed)
            reads.append({"event": event, "target": target, "source": source,
                          "coefficient": str(record[3]),
                          "source_after_coefficient_lower_pi_valuation": proposed})
        else:
            require(kind in ("transport", "add", "sign"), "prefix instruction grammar")
    return {"initial_point": {"Y27[0]": [64, 0], "all_other_initial_components": 0},
            "method": "component pi-valuations; native stage loses at most one; quarter loses four",
            "scope": "only this explicit initial point through events0..2024",
            "initial_bank_count": len(word["initial_frames"]),
            "all_literal_pairs_and_fractional_sources_exact": True,
            "active_native_events": active, "active_fractional_source_events": reads,
            "final_component_valuation_lower_bounds": lower}


def rejects(call, expected_message):
    try:
        call()
    except ProducerError as error:
        require(str(error) == expected_message, "control rejected for the wrong reason")
        return {"rejected": True, "reason": str(error)}
    raise ProducerError("negative control unexpectedly accepted")


def rejection_controls(word, selected, dependencies):
    wrong_quarter = json.loads(json.dumps(word))
    wrong_quarter["program"][1090][3] = "1/2"
    omitted_source = json.loads(json.dumps(word))
    omitted_source["program"][1090][2] = "Y26"
    wrong_order = json.loads(json.dumps(word))
    p = wrong_order["program"]
    p[1090], p[1129] = p[1129], p[1090]
    require(exact_scale([(-4, 4), (-8, -12)], "1/4") == [(-1, 1), (-2, -3)],
            "signed exact quarters")
    return {
        "source_byte_corruption": rejects(lambda: authenticated_bytes(b"corrupted", "word"),
                                           "source digest mismatch: word"),
        "wrong_quarter_at1090": rejects(lambda: validate_structure(wrong_quarter, selected, dependencies),
                                        "actual quarter source"),
        "omitted_Y27_source": rejects(lambda: extract_cone(omitted_source), "exact 58 initial dependencies"),
        "source_reads1090_1129_swapped": rejects(lambda: validate_structure(wrong_order, selected, dependencies),
                                                "ADD common frame"),
        "negative_nonintegral_quarter": rejects(lambda: exact_scale([(-3, 4)], "1/4"),
                                                "fractional ADD is not exact on the retained grid"),
        "signed_exact_quarters": {"inputs": [[-4, 4], [-8, -12]], "outputs": [[-1, 1], [-2, -3]]},
    }


def bind_witness_valuation(word, native, model):
    result = impulse_prefix_valuation(word)
    active = [row["event"] for row in result["active_native_events"]]
    require(len(active) == 20, "exact active native count for witness")
    native_records(word, native, active, model)
    result["all_active_native_frames_ranks_and_wrappers_bound"] = True
    result["ordered_active_native_records_sha256"] = sha(canonical([[e, word["program"][e]] for e in active]))
    result["ordered_prefix_records_sha256"] = sha(canonical(word["program"][:CUT]))
    return result


def verify_producer(word_path, native_path, model_path):
    word, native, model = load_inputs(word_path, native_path, model_path)
    selected, dependencies = extract_cone(word)
    validate_structure(word, selected, dependencies)
    plans = native_records(word, native, selected, model)
    _, positive = replay_cone(word, plans, selected, dependencies, model,
                              dense_initial(dependencies, model), True)
    negative_state, negative = replay_cone(word, plans, selected, dependencies, model,
                                          impulse_initial(dependencies, 64), False)
    require(negative["initial_admission"]["all_initial_fields_in_B9"], "witness starts in B9")
    require(negative["initial_admission"]["Y_fields_outside_4B9"] == ["Y27"], "one stronger-source failure")
    require(negative["first_lattice_failure"]["event"] == 1090, "first bad producer event")
    require(not negative["entrance"]["D31"]["in_B9"], "actual final producer failure")
    require(all(negative["entrance"][d]["in_B9"] for d in TARGETS if d != "D31"),
            "other five collector entrances remain admitted")
    negative["two_point_final_witness"] = {
        "addresses": [0, 8], "values": [list(negative_state["D31"][j]) for j in (0, 8)],
        "difference": list(model.sub(negative_state["D31"][8], negative_state["D31"][0]))}
    require(negative["two_point_final_witness"]["difference"] == [-1, 0], "degree-one final witness")
    repaired_state, repaired = replay_cone(word, plans, selected, dependencies, model,
                                          impulse_initial(dependencies, 256), True)
    require(repaired_state["D31"] == exact_scale(negative_state["D31"], 4), "amplitude256 positive control")
    rejected = False
    try:
        initial = impulse_initial(dependencies, 64)
        replay_cone(word, plans, selected, dependencies, model, initial, True)
    except ProducerError as error:
        rejected = str(error) == "producer entrance contract"
    require(rejected, "stronger-source contract rejects the witness")
    return {"status": "PASS", "source_sha256": SOURCE_HASHES,
            "source_cone": source_summary(word, selected, dependencies),
            "dense_dirty_admitted_fixture": positive,
            "one_coordinate_counterexample": negative,
            "amplitude256_admitted_control": repaired,
            "counterexample_full_prefix_valuation": bind_witness_valuation(word, native, model),
            "controls": rejection_controls(word, selected, dependencies),
            "stronger_contract_rejects_counterexample": rejected,
            "claim": "B9 prefix admission under exactly the stated strengthened initial contract",
            "not_claimed": ["maximal final-cut domain", "arbitrary-input source admission",
                            "full-word correctness", "physical owners or favorable recursive cost"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--model", type=Path,
                        default=Path(__file__).resolve().parent / "inputs/pr3382_model.py")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    source = args.repo / "research/p104-rounded-collector/inputs"
    result = verify_producer(source / "WORD.json", source / "NATIVE.json.gz", args.model)
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        with args.receipt.open("x") as handle:
            handle.write(data)
    print(json.dumps({"status": result["status"], "receipt_sha256": sha(data.encode()),
                      "cone_events": result["source_cone"]["event_count"],
                      "first_failure": result["one_coordinate_counterexample"]["first_lattice_failure"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
