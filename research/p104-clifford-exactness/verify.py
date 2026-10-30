#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound primary replay and independent receipt comparison.

Clear1nsight, with substantial OpenAI assistance. Finite scalar reference;
not the repository's native compiler or a physical supplier.
"""

import argparse
from copy import deepcopy
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path, PurePosixPath
import types

PACKAGE = Path(__file__).resolve().parent
WORD = "research/p104-rounded-collector/inputs/WORD.json"
NATIVE = "research/p104-rounded-collector/inputs/NATIVE.json.gz"
LIFTING = "research/p104-reversible-lifting/lifting.py"
SCIENTIFIC_SHA256 = {
    WORD: "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50",
    NATIVE: "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d",
    LIFTING: "9424ee08f22b717f6d58f7cc46f189c5549fa86778afcd0c0762ab2daf591160",
}
SOURCES = ["D31", "D30", "D29", "D28", "D27"]
OLD_FRAME = [256, 136, 64, 40, 16, 4, 2, 1]
NEW_FRAME = [364]
ZERO = (0, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_module(path, data=None):
    """Compile source bytes explicitly, ignoring adjacent bytecode caches."""
    module = types.ModuleType(path.stem)
    module.__file__ = str(path)
    exec(compile(path.read_bytes() if data is None else data, str(path), "exec"), module.__dict__)
    return module


def checked_bytes(data, expected, name):
    require(hashlib.sha256(data).hexdigest() == expected, "source SHA256 mismatch: " + name)
    return data


def authenticate(repo):
    inventory = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    manifest = json.loads((PACKAGE / "VERIFY.json").read_bytes())
    rows = [row for row in inventory if row["usage"] == "input"]
    require(len({row["path"] for row in rows}) == len(rows), "duplicate source input")
    require({row["path"] for row in rows} == set(manifest["inputs"]), "complete declared input closure")
    loaded, hashes = {}, {}
    for row in rows:
        name = row["path"]
        parts = PurePosixPath(name).parts
        require(parts and not name.startswith("/") and ".." not in parts, "canonical input path")
        path = repo.joinpath(*parts)
        require(path.is_file() and not path.is_symlink(), "missing regular source input: " + name)
        require(path.stat().st_size <= 32 * 1024 * 1024, "bounded source input")
        data = checked_bytes(path.read_bytes(), row["sha256"], name)
        if name in SCIENTIFIC_SHA256:
            checked_bytes(data, SCIENTIFIC_SHA256[name], name)
        loaded[name], hashes[name] = data, row["sha256"]
    require(set(SCIENTIFIC_SHA256) <= loaded.keys(), "missing scientific source")
    return loaded, hashes


def expected_events():
    return ([["zero", "C", OLD_FRAME]]
            + [["add", "C", name, 1, OLD_FRAME] for name in SOURCES]
            + [["transport", "C", OLD_FRAME, NEW_FRAME, 7],
               ["add", "Q7", "C", "1", NEW_FRAME],
               ["transport", "C", NEW_FRAME, OLD_FRAME, 7]]
            + [["add", "C", name, "-1", OLD_FRAME] for name in reversed(SOURCES)]
            + [["erase", "C", OLD_FRAME]])


def frame_prefix(word):
    """Syntactic frame/lifetime availability only; no earlier arithmetic claim."""
    frames = deepcopy(word["initial_frames"])
    entrance = None
    for index, event in enumerate(word["program"][:2040]):
        if index == 2025:
            entrance = deepcopy(frames)
        kind, name = event[:2]
        if kind == "transport":
            require(frames[name] == event[2], "transport entrance frame at " + str(index))
            frames[name] = event[3]
        elif kind == "add":
            require(frames[name] == frames[event[2]] == event[4], "ADD frames at " + str(index))
        elif kind == "sign":
            require(frames[name] == event[3], "sign frame at " + str(index))
        elif kind == "zero":
            require(name not in frames, "private ZERO needs new owned field")
            frames[name] = event[2]
        else:
            require(kind == "erase" and frames[name] == event[2], "private ERASE frame")
            del frames[name]
    require(entrance is not None and "C" not in entrance and "C" not in frames, "owned private lifetime")
    require(all(entrance[name] == OLD_FRAME for name in SOURCES), "source cut frames")
    require(entrance["Q7"] == NEW_FRAME, "query cut frame")
    require(entrance == frames, "collector restores all frame labels")
    return {"checked_structural_prefix_events": 2040,
            "entrance_source_frames": {name: entrance[name] for name in SOURCES},
            "entrance_query_frame": entrance["Q7"], "private_C_absent_at_both_boundaries": True,
            "earlier_arithmetic_or_domain_admission_checked": False}


def bind_sources(word, native):
    require(word["schema_version"] == native["schema_version"] == 1, "source schema")
    require(word["chart"] == native["chart"] == "Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)", "source chart")
    require(len(word["program"]) == 5398 and len(native["transports"]) == 1245, "source inventory lengths")
    events = word["program"][2025:2040]
    require(events == expected_events(), "literal fifteen-event collector")
    recipes = []
    for event_index in (2031, 2033):
        matches = [row for row in native["transports"] if event_index in row["events"]]
        require(len(matches) == 1, "unique native occurrence")
        row, event = matches[0], word["program"][event_index]
        require(row["events"] == [event_index], "exact native occurrence list")
        require(row["old"] == event[2] and row["new"] == event[3], "native occurrence frames")
        require(set(row["recipe"]) == {"rank", "left", "right"} and row["recipe"]["rank"] == event[4] == 7,
                "native rank and recipe schema")
        recipes.append(row["recipe"])
    return events, recipes, frame_prefix(word)


def must_reject(callback, text):
    try:
        callback()
    except ValueError as error:
        require(text in str(error), "wrong rejection: " + str(error))
        return str(error)
    raise ValueError("control accepted: " + text)


def algebra_checks(m, predecessor):
    pair_count = 0
    for ar, ai, br, bi, inverse in product(range(-3, 4), range(-3, 4), range(-2, 3), range(-2, 3), (False, True)):
        a, b = (ar, ai), (br, bi)
        literal = m.lift_pair(a, b, inverse)
        require(literal == predecessor.pair(a, b, inverse), "literal predecessor differential")
        parity = ((ar - br) - (ai - bi)) % 2 == 0
        numerators = m.ideal_pair_numerators(a, b, inverse)
        require(all(tuple(2 * c for c in z) == n for z, n in zip(literal, numerators)) == parity,
                "exact signed-floor iff pi divides difference")
        require(m.lift_pair(*literal, not inverse) == (a, b), "literal pair exact reversal")
        pair_count += 1
    intertwiner_count = 0
    for rank in range(1, 5):
        n = 1 << rank
        gates = [(kind, (bit,)) for kind in ("C", "CINV", "S", "SINV", "X") for bit in range(rank)]
        gates += [(kind, (a, b)) for kind in ("CNOT", "CZ", "SWAP") for a in range(rank) for b in range(rank) if a != b]
        for column in range(n):
            coefficients = [ZERO] * n
            coefficients[column] = (1 if column % 2 else -1, (column % 3) - 1)
            values = m.encode(coefficients)
            require(m.decode(values) == coefficients, "codec exact inverse")
            for kind, bits in gates:
                require(m.value_gate(values, kind, bits) == m.encode(m.coefficient_gate(coefficients, kind, bits)),
                        "integral generator intertwiner")
                intertwiner_count += 1
    witness = [ZERO, ZERO, ZERO, (1, 1)]
    require(not m.member(witness), "single-gate witness outside B2")
    m.ideal_stage(witness, 0)
    m.ideal_stage(witness, 1)
    simultaneous = must_reject(lambda: m.ideal_stage(m.ideal_stage(witness, 0), 1), "nonintegral")
    phase = [(1, 0), (0, 1)]
    require(m.member(phase) and m.lift_stage(phase, 0) == [(1, 1), ZERO], "old phase witness is exactly admitted")
    quarter_source, quarter = [(4, 0), ZERO], [(1, 0), ZERO]
    require(m.member(quarter_source) and not m.member(quarter), "integral quarter leaves lattice")
    require(not m.member([quarter[x & 1] for x in range(512)]), "actual ambient quarter boundary")
    coefficients = [ZERO, (2, 0)]
    require(m.value_gate(m.encode(coefficients), "C", (0,)) != m.encode(m.value_gate(coefficients, "C", (0,))),
            "CE is not EC on an exact common entrance")
    large = 1 << (m.MAX_COMPONENT_BITS - 1)
    output_limit = must_reject(lambda: m.coefficient_gate([(large, 0), (large, 0)], "C", (0,)),
                              "finite reference limit")
    return {"signed_pair_cases_including_inverse": pair_count,
            "generator_intertwiner_cases_ranks_1_through_4": intertwiner_count,
            "single_gate_not_all_partial_products": simultaneous,
            "phase_witness_admitted_exactly": True, "integral_quarter_rejected_at_ranks_1_and_9": True,
            "unjustified_codec_commutation_rejected": True,
            "single_bit_coefficient_output_limit": output_limit}


def full_add(m, left, right, sign=1):
    require(len(left) == len(right), "equal array ADD dimensions")
    return [(a + sign * c, b + sign * d) for (a, b), (c, d) in zip(left, right)]


def native_map(m, values, recipe, trace=None):
    out = m.wrapper(values, recipe["right"])
    if trace is not None:
        require(m.member(out), "right wrapper lattice closure")
        trace.append(digest(out))
    for bit in range(recipe["rank"]):
        exact = m.ideal_stage(out, bit)
        out = m.lift_stage(out, bit)
        require(out == exact, "literal native pair-prefix exactness")
        if trace is not None:
            require(m.member(out), "native prefix lattice closure")
            trace.append(digest(out))
    out = m.wrapper(out, recipe["left"])
    if trace is not None:
        require(m.member(out), "left wrapper lattice closure")
        trace.append(digest(out))
    return out


def collector(m, events, recipes, sources, query, private=None, omit_last_ungather=False):
    require(len(sources) == 5, "five source arrays")
    for value in sources + [query]:
        m.validate(value, 9)
    require(all(m.member(value) for value in sources + [query]), "collector lattice entrance")
    require(private is None or private == [ZERO] * 512, "private C requires owned zero entrance")
    values = {name: data[:] for name, data in zip(SOURCES, sources)}
    values["Q7"] = query[:]
    snapshots, at_query = [], None
    for index, event in enumerate(events, 2025):
        kind, destination = event[:2]
        if kind == "zero":
            require(destination not in values, "new owned private C")
            values[destination] = [ZERO] * 512
        elif kind == "add":
            if omit_last_ungather and index == 2038:
                continue
            values[destination] = full_add(m, values[destination], values[event[2]], int(event[3]))
            if destination == "Q7":
                at_query = values[destination][:]
        elif kind == "transport":
            values[destination] = native_map(m, values[destination], recipes[0 if index == 2031 else 1], snapshots)
        else:
            require(kind == "erase" and values[destination] == [ZERO] * 512, "literal private zero at ERASE")
            del values[destination]
            snapshots.append(digest([ZERO] * 512))
            continue
        require(m.member(values[destination]), "whole-event lattice closure")
        snapshots.append(digest(values[destination]))
    require(all(values[name] == value for name, value in zip(SOURCES, sources)), "borrowed sources unchanged")
    total = [ZERO] * 512
    for value in sources:
        total = full_add(m, total, value)
    expected = full_add(m, query, native_map(m, total, recipes[0]))
    require(values["Q7"] == at_query == expected and "C" not in values, "complete collector endpoint")
    return values["Q7"], {"query_sha256": digest(values["Q7"]), "prefix_snapshots": len(snapshots),
                          "prefixes_sha256": digest(snapshots), "all_five_sources_unchanged": True,
                          "owned_private_C_erases_exactly": True}


def collector_checks(m, predecessor, events, recipes):
    wrappers, cycles, plans = {}, [], []
    for label, recipe in zip(("U", "V"), recipes):
        for side in ("right", "left"):
            record = recipe[side]
            plan = m.wrapper_plan(record)
            require(plan == predecessor.plan(record), "all-address wrapper source differential")
            lengths = [len(cycle) for cycle in predecessor.cycles(plan)]
            cycles.append(len(lengths))
            plans.append(plan)
            wrappers[label + ":" + side] = {"plan_sha256": digest(plan), "cycles": len(lengths),
                                           "all_512_addresses_and_phases_match_source": True}
    require(cycles == [64, 128, 160, 64], "four literal wrapper cycle counts")
    inverse_plans = [predecessor.inverse_plan(plans[1]), predecessor.inverse_plan(plans[0])]
    return_differences = [sum(a != b for a, b in zip(actual, inverse))
                          for actual, inverse in zip(plans[2:], inverse_plans)]
    require(return_differences == [512, 512], "actual V not paired-inverse wrapper records")
    cases, retained = [], None
    for seed in range(4):
        coefficients = [[(((x + 3) * (k + 5) + seed * 7) % 23 - 11,
                          ((x * x + 9) * (k + 1) + seed * 13) % 29 - 14)
                         for x in range(512)] for k in range(6)]
        arrays = [m.encode(value) for value in coefficients]
        result, evidence = collector(m, events, recipes, arrays[:5], arrays[5])
        for recipe in recipes:
            left, right = predecessor.plan(recipe["left"]), predecessor.plan(recipe["right"])
            current = arrays[seed]
            numerator = predecessor.exact(current, 7, left, right)
            require(all(a % 128 == b % 128 == 0 for a, b in numerator), "ideal full recipe integral")
            exact = [(a // 128, b // 128) for a, b in numerator]
            require(native_map(m, current, recipe) == exact, "full source ideal oracle differential")
            literal = current[:]
            meter = {"pairs": 0, "wrapper_values": 0, "wrapper_cycles": 0, "wrapper_swaps": 0}
            predecessor.kernel(literal, 7, left, right, meter=meter)
            require(literal == exact, "authenticated predecessor literal kernel differential")
        cases.append(evidence)
        if seed == 0:
            retained = (coefficients, arrays, result)
    coefficients, arrays, result = retained
    # Optional coefficient-space call: five owned copies, six encodes, the
    # direct collector, query decode, and five source decodes/uncopies.
    copied = [value[:] for value in coefficients[:5]]
    encoded_sources = [m.encode(value) for value in copied]
    coded_result, _ = collector(m, events, recipes, encoded_sources, m.encode(coefficients[5]))
    decoded_query = m.decode(coded_result)
    total = [ZERO] * 512
    for value in coefficients[:5]:
        total = full_add(m, total, value)
    expected_query = full_add(m, coefficients[5], m.decode(native_map(m, m.encode(total), recipes[0])))
    require(decoded_query == expected_query, "cold coefficient contract E^-1 U E")
    for encoded, original in zip(encoded_sources, coefficients[:5]):
        require(full_add(m, m.decode(encoded), original, -1) == [ZERO] * 512, "five owned copy banks uncompute")
    controls = {
        "owned_zero_required": must_reject(lambda: collector(m, events, recipes, arrays[:5], arrays[5], [(1, 0)] * 512), "owned zero"),
        "cleanup_omission": must_reject(lambda: collector(m, events, recipes, arrays[:5], arrays[5], omit_last_ungather=True), "zero at ERASE"),
        "return_wrapper_record_differences": return_differences,
        "paired_inverse_swap_undercharge": [4 * 512 + 2 * sum(cycles[:2]), 4 * 512 + sum(cycles)],
    }
    bad_sources = deepcopy(arrays[:5])
    bad_sources[0][0] = m.add(bad_sources[0][0], (1, 0))
    controls["out_of_domain_entrance"] = must_reject(lambda: collector(m, events, recipes, bad_sources, arrays[5]), "lattice entrance")
    wrong_phase = [(target, plans[0][target][1]) for target, phase in plans[0]]
    require(wrong_phase != plans[0], "input-address phase convention discriminates output address")
    controls["output_address_phase_substitution_differs"] = sum(a != b for a, b in zip(wrong_phase, plans[0]))
    return {"dense_signed_collectors": cases, "actual_wrappers": wrappers, "controls": controls,
            "cold_coefficient_contract": {"logical_map": "Q + E^-1 U E sum(D)",
                                           "query_sha256": digest(decoded_query), "five_copy_banks_return_zero": True},
            "direct_collector_ledger": m.collector_ledger(9, 7, cycles),
            "codec_per_bank_per_direction": m.codec_ledger(9),
            "cold_codec_extra_ledger": m.cold_codec_ledger(9),
            "codec_bounds_for_unit_component_entrance": m.codec_bounds(9, 1),
            "collector_bounds_for_unit_component_entrance": m.collector_bounds(9, 5, 1),
            "cold_codec_bounds_for_unit_component_entrance": m.cold_codec_bounds(9, 1)}


def source_controls(loaded, word, native):
    controls = {}
    for name, expected in SCIENTIFIC_SHA256.items():
        changed = loaded[name] + b"\n"
        controls[Path(name).name + "_corruption"] = must_reject(lambda: checked_bytes(changed, expected, name), "SHA256 mismatch")
    changed = deepcopy(word)
    changed["program"][2032][4] = OLD_FRAME
    controls["query_frame_drift"] = must_reject(lambda: bind_sources(changed, native), "fifteen-event")
    changed_native = deepcopy(native)
    selected = next(row for row in changed_native["transports"] if 2033 in row["events"])
    selected["events"].append(2031)
    controls["ambiguous_native_occurrence"] = must_reject(lambda: bind_sources(word, changed_native), "unique native occurrence")
    return controls


def compare_invoice(invoice, independent_collector):
    require(invoice["wrapper_cycles"] == independent_collector["actual_wrapper_cycles"]
            and invoice["wrapper_swaps"] == independent_collector["actual_one_scratch_wrapper_swaps"],
            "literal wrapper invoice differs from independent source counts")
    require(invoice["paired_butterflies"] == independent_collector["literal_pair_invocations_per_collector"]
            and invoice["field_adds"] == independent_collector["unit_array_ADDs"],
            "literal pair and ADD invoice differs from independent source counts")


def replay(repo):
    implementation = {name: (PACKAGE / name).read_bytes() for name in ("verify.py", "model.py", "independent.py")}
    loaded, hashes = authenticate(repo)
    word, native = json.loads(loaded[WORD]), json.loads(gzip.decompress(loaded[NATIVE]))
    events, recipes, frames = bind_sources(word, native)
    m = source_module(PACKAGE / "model.py", implementation["model.py"])
    predecessor = source_module(repo / LIFTING, loaded[LIFTING])
    primary_algebra = algebra_checks(m, predecessor)
    primary_collector = collector_checks(m, predecessor, events, recipes)
    independent_module = source_module(PACKAGE / "independent.py", implementation["independent.py"])
    independent = independent_module.verify_independent(repo / WORD, repo / NATIVE, repo / LIFTING)
    require(independent["status"] == "PASS_INDEPENDENT_P104_PHASE_COMPLETE_DOMAIN"
            and independent["complete_columns"]["ideal_complex_columns"] == 512
            and independent["complete_columns"]["signed_Z_basis_columns"] == 1024
            and independent["complete_columns"]["literal_basis_pair_obligations"] == 3670016,
            "complete independent coverage and success required")
    require(independent["collector_events_sha256"] == digest(events), "independent complete event binding")
    require(independent["collector"]["actual_wrapper_cycles"] == 416
            and independent["collector"]["actual_one_scratch_wrapper_swaps"] == 2464, "independent actual wrapper invoice")
    invoice = primary_collector["direct_collector_ledger"]
    compare_invoice(invoice, independent["collector"])
    changed_invoice = dict(invoice, wrapper_cycles=384, wrapper_swaps=2432)
    primary_collector["controls"]["paired_inverse_invoice_rejected"] = must_reject(
        lambda: compare_invoice(changed_invoice, independent["collector"]), "literal wrapper invoice")
    for event, label in ((2031, "U"), (2033, "V")):
        for side in ("right", "left"):
            require(independent["literal_wrappers"][str(event) + ":" + side]["plan_sha256"]
                    == primary_collector["actual_wrappers"][label + ":" + side]["plan_sha256"], "independent complete wrapper plans")
    require(all((PACKAGE / name).read_bytes() == data for name, data in implementation.items()), "implementation drift during replay")
    return {"schema_version": 1, "status": "PASS_P104_CLIFFORD_EXACTNESS",
            "implementation_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in implementation.items()},
            "source_sha256": hashes, "collector_event_range_inclusive": [2025, 2039],
            "literal_events_sha256": digest(events), "structural_cut_binding": frames,
            "primary_algebra": primary_algebra, "primary_collector": primary_collector,
            "source_and_binding_controls": source_controls(loaded, word, native),
            "independent": independent,
            "scope": "Phase-compatible Gaussian domain and one complete restricted-input scalar collector; no prior caller admission, physical supplier, recursive saving or changed frontier."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=PACKAGE.parents[1])
    parser.add_argument("--write-receipt", type=Path, help="write an explicitly requested fresh receipt instead of comparing the retained one")
    args = parser.parse_args()
    receipt = replay(args.repo.resolve())
    encoded = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()
    if args.write_receipt:
        with args.write_receipt.open("xb") as output:
            output.write(encoded)
    else:
        require(encoded == (PACKAGE / "RECEIPT.json").read_bytes(), "complete deterministic receipt differs")
    print("PASS_P104_CLIFFORD_EXACTNESS " + json.dumps({"receipt_sha256": hashlib.sha256(encoded).hexdigest(),
          "independent_complex_columns": 512, "independent_signed_module_columns": 1024,
          "literal_collector_events": 15, "actual_wrapper_swaps": 2464}, sort_keys=True))


if __name__ == "__main__":
    main()
