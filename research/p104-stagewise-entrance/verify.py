#!/usr/bin/env python3
"""Bounded, Git-free replay of the exact correlated producer entrance.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
The independent evaluator imports neither this implementation nor a predecessor.
"""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def json_bytes(data):
    def object_pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def forbidden(value):
        raise ValueError("noninteger JSON number: " + value)
    return json.loads(data, object_pairs_hook=object_pairs,
                      parse_float=forbidden, parse_constant=forbidden)


def read_file(path, limit=4 * 1024 * 1024):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "regular file required: " + path.name)
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    require(len(data) <= limit, "file capacity: " + path.name)
    return data


def module(name):
    path = PACKAGE / (name + ".py")
    captured = read_file(path)
    result = ModuleType("p104_stagewise_" + name)
    result.__file__ = str(path)
    exec(compile(captured, str(path), "exec"), result.__dict__)
    return result, hashlib.sha256(captured).hexdigest()


def authenticate_sources(root):
    sources = json_bytes(read_file(PACKAGE / "SOURCES.json"))
    checks = [(root / row["path"], row) for row in sources["files"] if row["usage"] == "input"]
    checks += [(PACKAGE / row["path"], row) for row in sources["retained_sources"]]
    result = {}
    for path, row in checks:
        data = read_file(path)
        actual = hashlib.sha256(data).hexdigest()
        require(actual == row["sha256"] and len(data) == row["bytes"],
                "runtime/provenance source mismatch: " + row["path"])
        result[row["path"]] = actual
    return result


def typed_equal(actual, expected, path="receipt"):
    require(type(actual) is type(expected), "typed receipt mismatch at " + path)
    if type(expected) is dict:
        require(set(actual) == set(expected), "receipt key mismatch at " + path)
        for key in expected:
            typed_equal(actual[key], expected[key], path + "." + key)
    elif type(expected) is list:
        require(len(actual) == len(expected), "receipt length mismatch at " + path)
        for index, (left, right) in enumerate(zip(actual, expected)):
            typed_equal(left, right, path + "[" + str(index) + "]")
    else:
        require(actual == expected, "receipt value mismatch at " + path)


def profile_comparison(classifier, independent_result):
    profiles = {kind: classifier.profile(kind) for kind in ("zero", "rank_one", "terminal")}
    aggregate = {str(k): 0 for k in range(5)}
    for kind, count in (("zero", 32), ("rank_one", 15), ("terminal", 5)):
        primary, other = profiles[kind], independent_result["profiles"][kind]
        require(primary["pi_index_exponent"] == other["index_log2"], "independent local index")
        if kind != "terminal":
            require(primary["exponents"] == other["exponents"], "independent local profile")
        for exponent, multiplicity in primary["exponent_histogram"].items():
            aggregate[exponent] += count * multiplicity
    require(aggregate == {str(k): v for k, v in independent_result["profiles"]["whole"]["counts"].items()},
            "independent full Gaussian quotient")
    total = sum(int(k) * v for k, v in aggregate.items())
    require(total == 20424, "exact total index")
    return {"local": profiles, "whole_exponent_histogram": aggregate,
            "whole_index_log2": total, "ideal_final_only_index_log2": 10240,
            "additional_stagewise_index_log2": total - 10240,
            "strong_independent_4B_index_log2": 52 * 512 * 4}


def structure_comparison(structure, other):
    require(structure["selected"] == other["cone"]["events"], "independent exact event slice")
    require(structure["dependencies"] == other["cone"]["initial_roles"], "independent initial roles")
    keys = ("bank", "source", "event", "next_event", "kind", "transport_event", "frame")
    require(len(structure["gaps"]) == len(other["slots"]) == 52, "exact partial-sum slots")
    for left, right in zip(structure["gaps"], other["slots"]):
        require(all(left[k] == right[k] for k in keys), "independent gap boundary")
        require(left["source_path_to_read"] == right["source_path"], "independent source path")


def dense_check(word, structure, plans, model, source, classifier, admission, other):
    initial = admission.dense_fixture(structure, plans, model, source, classifier)
    trace = source.trace_cone(word, structure, plans, model, initial)
    require(trace["ok"] and all(trace["cut_in_b"].values()), "dense exact literal admitted cut")
    expected = admission.expected_cut(initial, structure, plans, model, source)
    require(trace["cut"] == expected, "all six full-array cut equations")
    independent = other["generated_fixture"]
    require(digest(initial) == independent["initial_sha256"], "independent Y-path/D-path construction")
    require(trace["cut_sha256"] == independent["cut_sha256"], "independent full dense cut")
    require(trace["pairs_checked"] == independent["counts"]["literal_pair_comparisons"] == 90624,
            "all native pairs active in dense fixture")
    require(trace["first_non_b"] == independent["first_non_B"], "independent non-B stage")
    return {"initial_sha256": digest(initial), "initial_bank_sha256": {k: digest(v) for k, v in initial.items()},
            **{k: v for k, v in trace.items() if k != "cut"},
            "full_array_cut_equations_checked": 6, "actual_path_codec_roundtrips": 52}


def control_check(word, structure, plans, model, source, classifier, admission, other):
    result = {}
    for name, initial in admission.control_initials(structure, plans, model, source).items():
        for rows in structure["groups"].values():
            total = [(0, 0)] * 512
            for row in rows:
                total = [model.add(a, b) for a, b in zip(total, initial[row["source"]])]
            require(all(v == (0, 0) for v in total), "control ideal group sum zero")
        admitted = True
        try:
            admission.decode_sources(structure, plans, model, source, classifier,
                                     {y: initial[y] for y in source.YS})
        except classifier.OutsideProfile:
            admitted = False
        trace = source.trace_cone(word, structure, plans, model, initial)
        require(admitted == trace["ok"] == (name == "paired64"), "control exact admission decision")
        key = {"quarter": "first_quarter", "native": "post_native", "paired64": "known_paired64"}[name]
        independent = other["controls"][key]
        require(digest(initial) == independent["initial_sha256"], "independent control source construction")
        if name == "paired64":
            require(trace["cut_sha256"] == independent["cut_sha256"], "paired literal endpoint")
            require(all(z == (0, 0) for v in trace["cut"].values() for z in v), "paired zero cut")
        else:
            require(trace["failure"]["event"] == independent["first_failure"]["event"],
                    "independent first failure")
            expected = {"quarter": ("nonintegral_fractional_add", "nonintegral_quarter"),
                        "native": ("nonintegral_ideal_pair", "nonintegral_native_pair")}[name]
            require((trace["failure"]["kind"], independent["first_failure"]["kind"]) == expected,
                    "independent failure kind")
        result[name] = {"initial_sha256": digest(initial), "ideal_group_sums_zero": True,
                        "profile_admitted": admitted, **{k: v for k, v in trace.items() if k != "cut"}}
    return result


def rejection_checks(source, classifier, result):
    checks = []
    for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1.0}'):
        try:
            json_bytes(raw)
        except ValueError:
            checks.append("strict_json")
        else:
            raise ValueError("malformed JSON accepted")
    wrong = json_bytes(canonical(result))
    wrong["profiles"]["local"]["zero"]["exponent_histogram"]["4"] = True
    try:
        typed_equal(wrong, result)
    except ValueError:
        checks.append("boolean_is_not_integer_one")
    else:
        raise ValueError("Boolean receipt accepted")
    for kind in ("zero", "rank_one", "terminal"):
        try:
            classifier.decode_profile([(1, 0)] * 512, kind)
        except classifier.OutsideProfile:
            checks.append("outside_" + kind)
        else:
            raise ValueError("nondivisible profile accepted")
    with tempfile.TemporaryDirectory(prefix="p104-stagewise-source-reject-") as temporary:
        path = Path(temporary) / "WORD.json"
        path.write_bytes(b'{"not":"the frozen word"}\n')
        try:
            source.read_pinned(path, "word")
        except source.SourceError:
            checks.append("corrupt_scientific_source")
        else:
            raise ValueError("corrupt source accepted")
    return checks


def cost_comparison(primary, other):
    require(other["status"] == "PASS", "independent cost status")
    inventory = primary["path_inventory"]
    for ours, theirs in (("native_occurrence_count", "inverse_donor_native_occurrences"),
                         ("native_rank_mass", "rank_mass"), ("wrapper_count", "wrapper_occurrences"),
                         ("wrapper_cycle_sum", "wrapper_cycles"), ("gaussian_payload_swaps", "wrapper_swaps")):
        require(inventory[ours] == other[theirs], "independent cost inventory: " + ours)
    require(inventory["inverse_wrapper_phase_histogram"] == other["encoder_inverse_wrapper_phase_histogram"],
            "independent actual phase histogram")
    require(primary["forward"]["real_add_subtracts_before_swap_phase_lowering"]
            == other["encode"]["real_add_sub_if_doubling_is_add"], "independent forward arithmetic")
    require(primary["reverse"]["real_add_subtracts_before_swap_phase_lowering"]
            == other["decode"]["real_add_sub"], "independent inverse arithmetic")
    require(primary["reverse"]["real_halves"] == other["decode"]["native_real_floor_halvings"]
            + other["decode"]["codec_exact_real_halvings"], "independent exact/floor halves")
    lowered = other["optional_fully_lowered_real_arithmetic"]
    require(primary["forward"]["real_add_subtracts_with_swaps_and_negations"] ==
            lowered["encode_real_add_sub_including_doublings"] + lowered["explicit_real_negations"],
            "independent optional component-arithmetic lowering")
    require(primary["width_bounds"]["encoder_work_component_gain"] == other["height"]["pair_work_factor"],
            "independent conservative encoder width")


def build(root=ROOT):
    root = Path(root)
    before = authenticate_sources(root)
    names = ("source", "classifier", "admission", "costs", "independent", "independent_cost")
    loaded = [module(name) for name in names]
    source, classifier, admission, costs, independent, independent_cost = [item[0] for item in loaded]
    code_hashes = {name + ".py": item[1] for name, item in zip(names, loaded)}
    code_hashes["verify.py"] = hashlib.sha256(read_file(PACKAGE / "verify.py")).hexdigest()
    word, native, model = source.load_inputs(root)
    structure = source.structure(word, native)
    plans = source.native_plans(word, native, structure["selected"], model)
    scientific = root / "research/p104-rounded-collector/inputs"
    other = independent.verify_independent(scientific / "WORD.json", scientific / "NATIVE.json.gz")
    require(other["status"] == "PASS_INDEPENDENT_STAGEWISE_ENTRANCE", "independent success status")
    structure_comparison(structure, other)
    profiles = profile_comparison(classifier, other)
    invoice = costs.invoice(structure, plans, classifier)
    cost_audit = independent_cost.audit(root)
    cost_comparison(invoice, cost_audit)
    result = {"schema_version": 1, "result": "PASS_EXACT_STAGEWISE_ENTRANCE",
              "scope": "Exact literal-equals-ideal257-event producer cone and six admitted outputs, not arbitrary rounded paths or the whole prefix",
              "source_sha256": before, "implementation_sha256": code_hashes,
              "structure": structure, "profiles": profiles,
              "dense_fixture": dense_check(word, structure, plans, model, source, classifier, admission, other),
              "controls": control_check(word, structure, plans, model, source, classifier, admission, other),
              "logical_codec_invoice": invoice, "independent_cost": cost_audit,
              "independent": other}
    result = json_bytes(canonical(result))
    result["rejection_checks"] = rejection_checks(source, classifier, result)
    require(authenticate_sources(root) == before, "source inputs changed during replay")
    require({name: hashlib.sha256(read_file(PACKAGE / name)).hexdigest() for name in code_hashes}
            == code_hashes, "executed source files changed during replay")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--receipt", type=Path, default=PACKAGE / "RECEIPT.json")
    mode.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    try:
        result = build(args.root)
        if args.write_receipt:
            with args.write_receipt.open("xb") as handle:
                handle.write(json.dumps(result, sort_keys=True, indent=2).encode() + b"\n")
        else:
            typed_equal(json_bytes(read_file(args.receipt)), result)
        print(json.dumps({"result": result["result"], "gaussian_index_log2": 20424,
                          "literal_pairs": 90624, "dense_cut_sha256": result["dense_fixture"]["cut_sha256"],
                          "receipt_scientific_sha256": digest(result)}, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, "FAIL_STAGEWISE_ENTRANCE: " + str(error) + "\n")


if __name__ == "__main__":
    main()
