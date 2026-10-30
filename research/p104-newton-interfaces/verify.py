#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-complete joint replay of the three assigned P104 interface questions.

Clear1nsight, with substantial OpenAI assistance. The proofs state the universal
claims. These exact, bounded computations authenticate the actual source paths,
exercise the arithmetic, and compare separately implemented evidence. No Git,
network, third-party dependency, or predecessor checkout is needed for replay.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import types


PACKAGE = Path(__file__).resolve().parent
WORD = "research/p104-rounded-collector/inputs/WORD.json"
NATIVE = "research/p104-rounded-collector/inputs/NATIVE.json.gz"
BUDGET = "research/p104-consumer-budget-audit/README.md"
SCIENTIFIC = {
    WORD: "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50",
    NATIVE: "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d",
    BUDGET: "13694215d0c1a245b392f7155e8395b9c4bad9c5db3558833c784d9449616417",
}
RETAINED = {
    "inputs/pr3382_model.py": "74c83367887dd885137b222155c86389fe0be9f1293a6f0e5fdb51d71f435fdd",
    "inputs/PR3382_PROOF.md": "1ca8c0e7e78f0f39de6cff7accc68ccd3901bfb50759bf7a2e2896bcf63bf081",
}
MODULES = ("producer.py", "consumer.py", "cost_audit.py", "independent.py")
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        require(name not in result, "duplicate JSON key: " + name)
        result[name] = value
    return result


def reject_number(value):
    raise ValueError("non-integer JSON number: " + value)


def strict_json(data):
    return json.loads(data, object_pairs_hook=unique_object,
                      parse_constant=reject_number, parse_float=reject_number)


def regular_bytes(root, name):
    pure = PurePosixPath(name)
    require(isinstance(name, str) and str(pure) == name and pure.parts
            and not pure.is_absolute() and ".." not in pure.parts,
            "canonical relative input path")
    path = root
    for part in pure.parts:
        path = path / part
        require(not path.is_symlink(), "symlink input: " + name)
    require(path.is_file() and path.stat().st_size <= 32 * 1024 * 1024,
            "bounded regular input required: " + name)
    return path.read_bytes()


def checked(data, expected, name):
    require(sha(data) == expected, "source SHA256 mismatch: " + name)
    return data


def authenticate(repo, package=PACKAGE):
    sources = strict_json(regular_bytes(package, "SOURCES.json"))
    manifest = strict_json(regular_bytes(package, "VERIFY.json"))
    rows = [row for row in sources["files"] if row["usage"] == "input"]
    names = [row["path"] for row in rows]
    require(len(set(names)) == len(names), "duplicate declared source input")
    require(len(set(manifest["inputs"])) == len(manifest["inputs"])
            and set(names) == set(manifest["inputs"]), "complete declared input closure")
    require(set(SCIENTIFIC) <= set(names), "missing scientific input")
    retained = sources["retained_sources"]
    require(len(retained) == len(RETAINED)
            and {row["path"] for row in retained} == set(RETAINED),
            "complete retained predecessor closure")
    loaded, hashes = {}, {}
    for row in rows:
        name = row["path"]
        data = checked(regular_bytes(repo, name), row["sha256"], name)
        if name in SCIENTIFIC:
            checked(data, SCIENTIFIC[name], name)
        loaded[name], hashes[name] = data, sha(data)
    for row in retained:
        name = row["path"]
        data = checked(regular_bytes(package, name), RETAINED[name], name)
        require(row["sha256"] == RETAINED[name] and len(data) == row["bytes"],
                "retained source metadata")
        loaded["package/" + name], hashes["package/" + name] = data, sha(data)
    return loaded, hashes


def source_module(name):
    """Compile the actual source bytes without consulting adjacent .pyc files."""
    data = regular_bytes(PACKAGE, name)
    module = types.ModuleType(name.removesuffix(".py"))
    module.__file__ = str(PACKAGE / name)
    exec(compile(data, module.__file__, "exec"), module.__dict__)
    return module, sha(data)


def same_receipt(expected, actual):
    # JSON spelling distinguishes bool from int and normalises tuples to arrays.
    require(canonical(expected) == canonical(actual), "typed scientific receipt mismatch")


def must_reject(callback, reason):
    try:
        callback()
    except ValueError as error:
        require(reason in str(error), "unexpected failure control: " + str(error))
        return "REJECTED: " + reason
    raise ValueError("failure control was accepted: " + reason)


def integrity_controls(loaded):
    controls = {
        "duplicate_json_key": must_reject(
            lambda: strict_json('{"rank":1,"rank":1}'), "duplicate JSON key"),
        "nonfinite_json": must_reject(
            lambda: strict_json('{"rank":NaN}'), "non-integer JSON number"),
        "float_json": must_reject(
            lambda: strict_json('{"rank":1.0}'), "non-integer JSON number"),
        "bool_as_integer_receipt": must_reject(
            lambda: same_receipt({"admitted": True}, {"admitted": 1}),
            "typed scientific receipt mismatch"),
        "partial_component_result": must_reject(
            lambda: crosscheck({"status": "PARTIAL"}, {}, {}, {}),
            "all component evidence must report complete PASS"),
    }
    with tempfile.TemporaryDirectory(prefix="p104-interface-integrity-") as folder:
        scratch = Path(folder)
        package = scratch / "research/p104-newton-interfaces"
        package.mkdir(parents=True)
        for name in ("SOURCES.json", "VERIFY.json"):
            (package / name).write_bytes(regular_bytes(PACKAGE, name))
        for name, data in loaded.items():
            path = package / name.removeprefix("package/") if name.startswith("package/") else scratch / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        # Exercise the complete authentication gate before any module is loaded.
        native_path = scratch / NATIVE
        native_data = loaded[NATIVE]
        native_path.write_bytes(bytes([native_data[0] ^ 1]) + native_data[1:])
        controls["corrupt_actual_native_input"] = must_reject(
            lambda: authenticate(scratch, package), "source SHA256 mismatch: " + NATIVE)
        native_path.write_bytes(native_data)
        model_path = package / "inputs/pr3382_model.py"
        model_path.write_bytes(model_path.read_bytes() + b"\n")
        controls["corrupt_retained_model_before_execution"] = must_reject(
            lambda: authenticate(scratch, package),
            "source SHA256 mismatch: inputs/pr3382_model.py")
        model_path.write_bytes(loaded["package/inputs/pr3382_model.py"])
        manifest = strict_json((package / "VERIFY.json").read_bytes())
        manifest["inputs"].remove(NATIVE)
        (package / "VERIFY.json").write_bytes(canonical(manifest))
        controls["undeclared_live_input"] = must_reject(
            lambda: authenticate(scratch, package), "complete declared input closure")
    return controls


def crosscheck(producer, consumer, cost, independent):
    require(producer["status"] == "PASS"
            and consumer["status"] == "PASS_P104_OPEN_CONSUMER_INTERFACE"
            and independent["status"] == "PASS"
            and independent["full_prefix_witness"]["status"] == "PASS"
            and independent["scalar_ports"]["status"] == "PASS"
            and consumer["symbolic_open_interface"]["status"] == "PASS_EXACT_OPEN_INTERFACE_ROWS"
            and consumer["dense_open_replay"]["status"] == "PASS_DENSE_CHRONOLOGICAL_OPEN_REPLAY",
            "all component evidence must report complete PASS")
    source = cost["source_audit"]
    direct = source["direct_reference_schedule"]
    pcone = producer["source_cone"]
    require(pcone["events"] == source["producer"]["events"], "independent producer event cone")
    require(pcone["initial_dependencies"] == source["producer"]["initial_roles"],
            "independent producer initial roles")
    require(consumer["closed_event_indices"] == source["internal_event_indices"],
            "independent complete internal chronology")
    require(consumer["closed_opcode_counts"] == source["internal_opcode_counts"],
            "independent complete internal opcodes")
    ports = consumer["symbolic_open_interface"]["external_port_records"]
    port_manifest = [{k: row[k] for k in ("event", "target", "source", "coefficient", "frame")}
                     for row in ports]
    require(port_manifest == source["outgoing_ports"], "independent complete outgoing port bindings")
    require(consumer["external_read_event_indices"] == [row["event"] for row in ports],
            "symbolic ports match actual extraction")
    require(sha(canonical(consumer["external_read_event_indices"])) ==
            independent["scalar_ports"]["external_port_indices_sha256"], "third implementation port chronology")
    require(consumer["path_certificate"]["status"] == "PASS_ALL_ACTUAL_FRAME_PATHS"
            and independent["scalar_ports"]["frame_map_certificate_required"] is True,
            "phase-sensitive frame certificate required by scalar oracle")
    interface = consumer["symbolic_open_interface"]
    require(interface["gauge_normalized_X_port_operator"]["target_signs"] ==
            independent["scalar_ports"]["X_target_signs"], "independent signed half-sum rows")
    require(interface["persistent_banks_restored_in_full_frame"] == source["initial_roles"]
            and all(frame == FULL for frame in source["final_frames"].values()),
            "all63 final physical frames and logical restorations")
    counts = consumer["dense_open_replay"]["counts"]
    require(counts["native_pair_comparisons"] == direct["signed_floor_pairs"]
            == 256 * consumer["closed_native_rank_sum"] == 148736,
            "independent native arithmetic bill")
    require(counts["complete_wrapper_domain_checks"] == direct["wrappers"] == 784,
            "independent wrapper count")
    require(counts["executed_internal_array_adds"] + len(ports)
            == direct["field_adds_including_all_ports"] == 857,
            "all internal and outgoing ADDs paid once")
    witness = independent["full_prefix_witness"]
    negative = producer["one_coordinate_counterexample"]
    for role, row in negative["entrance"].items():
        other = witness["entrance"][role]
        require(row["sha256"] == other["sha256"]
                and row["in_B9"] == (other["newton_failure"] is None),
                "full prefix versus minimal cone entrance: " + role)
    pfirst, ifirst = negative["first_lattice_failure"], witness["first_full_prefix_B9_failure"]
    require(pfirst["event"] == ifirst["event"] == 1090
            and pfirst["target"] == ifirst["field"] == "D31", "first actual admission failure")
    require(all(pfirst["witness"][key] == ifirst[key]
                for key in ("mask", "degree", "coefficient", "pi_valuation")),
            "independent exact Newton failure")
    valuation = producer["counterexample_full_prefix_valuation"]
    require(witness["active_native_events"] == [row["event"] for row in valuation["active_native_events"]]
            and witness["active_add_events"] == [row["event"] for row in valuation["active_fractional_source_events"]],
            "full numerical witness versus independent valuation proof")
    require(consumer["coefficient_maps"]["full_frame"]["nonzero_entries"] == 3**9
            and consumer["coefficient_maps"]["full_frame"]["maximum_absolute_component"] == 1,
            "coefficient matrix agrees with tensor formula sparsity")
    return {"status": "PASS_SEPARATE_IMPLEMENTATIONS_AGREE", "producer_events": len(pcone["events"]),
            "internal_events": len(consumer["closed_event_indices"]), "outgoing_ports": len(ports),
            "phase_certificate_required_and_checked": True, "restored_internal_roles": 63,
            "counterexample_entrance_arrays_compared": len(negative["entrance"]),
            "full_prefix_structural_native_occurrences": witness["prefix_native_occurrences_bound"],
            "full_prefix_active_pair_comparisons": witness["active_pair_comparisons"],
            "scope": "Exact bounded open interface; no omitted external history or whole supplier inferred."}


def compute(repo):
    loaded, hashes = authenticate(repo)
    controls = integrity_controls(loaded)
    modules, implementations = {}, {}
    for name in MODULES:
        modules[name], implementations[name] = source_module(name)
    implementations["verify.py"] = sha(regular_bytes(PACKAGE, "verify.py"))
    producer = modules["producer.py"].verify_producer(repo / WORD, repo / NATIVE,
                                                      PACKAGE / "inputs/pr3382_model.py")
    consumer = modules["consumer.py"].verify_consumer(repo / WORD, repo / NATIVE)
    audit = modules["cost_audit.py"]
    cost = {"fixed_consumer": audit.fixed_consumer(), "codec_reference": audit.codec_reference(),
            "source_audit": audit.source_audit(repo)}
    independent = modules["independent.py"].verify_independent(repo / WORD, repo / NATIVE)
    agreement = crosscheck(producer, consumer, cost, independent)
    return {"schema_version": 1, "status": "PASS_P104_NEWTON_INTERFACES",
            "implementation_sha256": implementations, "authenticated_inputs": hashes,
            "integrity_controls": controls, "producer": producer, "consumer": consumer,
            "cost": cost, "independent": independent, "cross_implementation": agreement}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=PACKAGE.parents[1])
    parser.add_argument("--write-receipt", type=Path,
                        help="create a new receipt exclusively; never replace an existing file")
    args = parser.parse_args()
    # Parse a retained receipt before computation, rejecting malformed evidence early.
    expected = None if args.write_receipt else strict_json(regular_bytes(PACKAGE, "RECEIPT.json"))
    actual = compute(args.repo)
    payload = json.dumps(actual, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.write_receipt:
        with args.write_receipt.open("x", encoding="utf-8") as stream:
            stream.write(payload)
    else:
        same_receipt(expected, actual)
    print(json.dumps({"status": actual["status"], "receipt_sha256": sha(payload.encode()),
                      "agreement": actual["cross_implementation"],
                      "retained_receipt_compared": expected is not None}, sort_keys=True))


if __name__ == "__main__":
    main()
