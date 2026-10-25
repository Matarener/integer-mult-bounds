"""Original native checks on the named R439 kernel entrance boundary.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
Reuses the frozen PR3326 native harness; no predecessor assertion is replaced.
The local role map and nonempty selection are an explicit staging adaptation.
Physical source ownership, donor ownership and bank admission remain separate.
"""

import hashlib
import json
from pathlib import Path
import types

HELPER = Path("research/xor-scatter-native-audit/native_check.py")
HELPER_SHA256 = "b6615abf7f68af9bca13b20360936944e7e8de8f3684da6c29400e8e98cf4a6c"
SELECTION = [{"a": 444, "partners": [470], "new_frame_id": 79, "E_dimension": 1}]
FIXTURES = {"kernel": 9, "active_alias": 10}
STAGED_FILES = (
    "cin/249-states.json", "cin/frames.json", "cin/249-DONOR-OWNERSHIP.json",
    "cout/COHORT249-FRAMES.json", "cout/COHORT249-INITIAL.json",
    "cout/COHORT249-SELECTION.json", "cout/COHORT249-RECORDS.bin",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_helper(snapshot_root):
    path = snapshot_root / HELPER
    source = path.read_bytes()
    require(hashlib.sha256(source).hexdigest() == HELPER_SHA256, "frozen native helper hash")
    module = types.ModuleType("pinned_xor_native_harness")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
                    encoding="utf-8")


def staged_hashes(directory):
    return {name: digest(directory / name) for name in STAGED_FILES}


def changed_paths(before, after):
    require(before.keys() == after.keys(), "staged inventory changed")
    return sorted(name for name in before if before[name] != after[name])


def stage_selection(helper, snapshot_root, output, directory):
    """Run original empty staging, then record exactly two metadata changes."""
    cin, cout = helper.stage(snapshot_root, output, directory)
    before = staged_hashes(directory)
    states_path = cin / "249-states.json"
    states = json.loads(states_path.read_bytes())
    require([states[key] for key in ("h", "v", "R", "n", "ZERO")] == [8, 111, 439, 661, 0],
            "fixed native dimension and zero-frame contract")
    require(states["regs"] == states["source_owned_roles"] == [], "original empty owner scope")
    require(states["initial"]["444"] == 79 and states["initial"]["470"] == 0,
            "named changed entrance")
    require(states["final"]["444"] == states["final"]["470"] == 1, "restored full endpoints")
    frames = json.loads((cin / "frames.json").read_bytes())["frames"]
    require(frames["79"]["dim"] == 1, "inherited line frame")
    require(json.loads((cout / "COHORT249-FRAMES.json").read_bytes()) == {},
            "no new frame added")
    states["regs"] = list(range(222, 661))
    write_json(states_path, states)
    write_json(cout / "COHORT249-SELECTION.json", SELECTION)
    after = staged_hashes(directory)
    changed = ["cin/249-states.json", "cout/COHORT249-SELECTION.json"]
    require(changed_paths(before, after) == changed, "only role-map and selection adapted")
    require(digest(output / "249-records.bin") == after["cout/COHORT249-RECORDS.bin"],
            "unmodified exporter stream")
    receipt = {
        "original_staging_sha256": before, "adapted_staging_sha256": after,
        "changed_files": changed, "selection": SELECTION,
        "role_map": {"definition": "regs[i] = 222 + i", "count": 439},
        "source_owned_roles": [], "donor_keys": [],
        "inherited_frame_id": 79, "new_frames_added": 0,
        "export_sha256": {name: digest(output / name) for name in
                          ("249-records.bin", "249-states.json", "frames.json")},
        "scope": "Local identity role labels; no physical owner or donor manifest is asserted.",
    }
    return cin, cout, receipt


def expected_fixture(helper, name, records):
    literal, prefix = helper.invoice(records), helper.prefix_invoice(records)
    copies = FIXTURES[name]
    expected = {"records": 27180 + 2 * (copies - 9), "moves": 2910, "adds": 24252,
                "copies": copies, "erasures": copies, "scatter_adds": 527,
                "rank_mass": 5128 + 7 * (copies - 9)}
    require(all(literal[key] == value for key, value in expected.items()), "fixed finite invoice")
    require(literal["paid_histogram"] == [[1, 1322], [2, 1342], [3, 79], [4, 44],
                                         [5, 102], [6, 11], [7, 19 + copies - 9]],
            "complete paid histogram")
    require([prefix["forward"], prefix["reverse"]] == ["49347", "1113070"],
            "fixed signed prefix bounds")
    require(prefix["bits"] == 93 and int(prefix["payload"]) < 1 << 104, "payload guard")
    require(not helper.scalar_differences(records), "independent positive scalar endpoint")
    return literal, prefix


def retained_alias_windows(name, records):
    """Bind the active alias claim to actual COPY windows in the exported stream."""
    copies = [i for i, row in enumerate(records) if row[0] == 2]
    windows = []
    for slot, start in enumerate(copies):
        if records[start][1] != 472:
            continue
        finish = next(i for i in range(start + 1, len(records)) if records[i][0] == 3)
        require(records[finish][1] == 472, "alias source remains bound through ERASE")
        additions = [row for row in records[start + 1:finish] if row[0] == 1]
        require(additions and all(row[2] == 661 and row[5] == 3 for row in additions),
                "retained alias window must have genuine scatter consumers")
        windows.append({"slot": slot, "source": 472, "copy_record_index": start,
                        "erase_record_index": finish, "scatter_adds": len(additions),
                        "target_registers": [row[1] for row in additions]})
    require([window["slot"] for window in windows] == ([0, 9] if name == "active_alias" else [0]),
            "exact retained-source alias slots")
    return windows


def reconcile_legality(helper, result, literal):
    value = result["receipt"]
    require(result["accepted"] and value["status"] == helper.LEGAL_PASS, "legality acceptance")
    fields = (("records", "records"), ("nested_MOVEs", "moves"), ("common_frame_ADDs", "adds"),
              ("copies", "copies"), ("erasures", "erasures"), ("rank_mass", "rank_mass"),
              ("paid_histogram", "paid_histogram"))
    require(all(value[native] == literal[local] for native, local in fields),
            "native legality invoice agrees with literal records")
    require(value["selected_pairs"] == 1 and value["selected_helpers"] == 2,
            "nonempty selected kernel support")
    require(value["source_owner_intersections"] == value["donor_intersections"] == 0,
            "local exclusion guards")
    require(value["all_final_frames_pass"] is True and value["new_frame_ids_collision"] is False,
            "native final frames and inherited catalogue")


def reconcile_columns(helper, result, literal, prefix, copies):
    value = result["receipt"]
    require(result["accepted"] and value["status"] == helper.COLUMN_PASS, "column acceptance")
    require(value["formal_columns_checked"] == 883 and value["local_registers"] == 661 and
            value["independent_dirty_registers"] == 439, "complete five-stage formal domain")
    require(value["local_raw_H"] == literal["paid_histogram"], "native column paid histogram")
    require(value["local_scalar_additions"] == literal["adds"] and
            value["five_stage_additions"] == 5 * literal["adds"], "native scalar invoice")
    require(value["fresh_center_copies"] == 5 * copies and
            value["reverse_fresh_center_copies"] == 2 * copies, "forward/reverse fresh-copy bill")
    require([row["cancellation_free_signed_row_l1_upper"] for row in value["signed_lift_prefix"]]
            == [prefix["forward"], prefix["reverse"]], "native signed prefix recurrence")
    require(value["payload_prefix_upper"] == prefix["payload"] and
            value["payload_prefix_bits"] == prefix["bits"], "native exact payload invoice")
    require(value["copied_center_original_source_immutable"] is True, "native immutable source")
    require(value["negative_controls"] == [{"omit_bridge": i, "rejected": True} for i in range(6)],
            "native six omitted-bridge controls")


def fixture_checks(helper, binaries, snapshot_root, name, output, workdir):
    records = helper.read_records((output / "249-records.bin").read_bytes())
    literal, prefix = expected_fixture(helper, name, records)
    windows = retained_alias_windows(name, records)
    directory = workdir / name
    cin, cout, adaptation = stage_selection(helper, snapshot_root, output, directory)
    contracts = {}
    for copies in (9, 10):
        correct = copies == FIXTURES[name]
        legal = helper.checked_native(binaries[copies]["legality_h"], [cin, cout],
                                      directory / f"legality{copies}.json", helper.LEGAL_PASS,
                                      None if correct else "unclosed COPY")
        columns = helper.checked_native(binaries[copies]["columns_h"],
                                        [cout / "COHORT249-RECORDS.bin"],
                                        directory / f"columns{copies}.json", helper.COLUMN_PASS,
                                        None if correct else "center boundaries")
        if correct:
            reconcile_legality(helper, legal, literal)
            reconcile_columns(helper, columns, literal, prefix, copies)
        contracts[str(copies)] = {"legality": legal, "columns": columns}
    return {"invoice": literal, "prefix": prefix, "adaptation": adaptation,
            "retained_source_472_windows": windows,
            "contracts": contracts}, records


def metadata_mutation(directory, name):
    choices = {
        "wrong_dimension": ("cout/COHORT249-SELECTION.json", "0/E_dimension", 1, 2,
                            "wrong new rank"),
        "source_owner_collision": ("cin/249-states.json", "source_owned_roles", [], [444],
                                   "source owner or donor selected"),
        "donor_collision": ("cin/249-DONOR-OWNERSHIP.json", "donor_keys", [], [470],
                            "source owner or donor selected"),
        "wrong_partner": ("cout/COHORT249-SELECTION.json", "0/partners", [470], [223], None),
    }
    relative, pointer, before, after, error = choices[name]
    path = directory / relative
    value = json.loads(path.read_bytes())
    container = value[0] if pointer.startswith("0/") else value
    key = pointer.split("/")[-1]
    require(container[key] == before, "metadata mutation precondition")
    container[key] = after
    write_json(path, value)
    return {"file": relative, "json_pointer": "/" + pointer,
            "before": before, "after": after}, error


def metadata_controls(helper, binaries, snapshot_root, output, workdir, positive):
    results = {}
    for name in ("wrong_dimension", "source_owner_collision", "donor_collision", "wrong_partner"):
        directory = workdir / name
        cin, cout, adaptation = stage_selection(helper, snapshot_root, output, directory)
        mutation, error = metadata_mutation(directory, name)
        after = staged_hashes(directory)
        require(changed_paths(adaptation["adapted_staging_sha256"], after) == [mutation["file"]],
                "one metadata file changed")
        legal = helper.checked_native(binaries["legality_h"], [cin, cout],
                                      directory / "legality.json", helper.LEGAL_PASS, error)
        if name == "wrong_partner":
            reconcile_legality(helper, legal, positive["invoice"])
            require(legal == positive["contracts"]["9"]["legality"],
                    "native checker does not bind the declared partner to the stream")
        results[name] = {
            "adaptation": adaptation, "mutation": mutation, "control_staging_sha256": after,
            "legality": legal, "scalar_stream_unchanged": True,
            "unchanged_columns_receipt": "fixtures/kernel/contracts/9/columns",
            "columns_rerun": False,
        }
    return results


def exit_shear_control(helper, binaries, snapshot_root, output, workdir, records):
    directory = workdir / "missing_exit_shear"
    cin, cout, adaptation = stage_selection(helper, snapshot_root, output, directory)
    matches = [i for i, row in enumerate(records) if tuple(row) == (1, 470, 444, 1, 1, 5)]
    require(len(matches) == 1, "unique exact named exit shear")
    index = matches[0]
    require(index == max(i for i, row in enumerate(records) if row[0] == 1 and row[5] == 5),
            "exit shear is the last restoration ADD")
    changed = records[:index] + records[index + 1:]
    stream = cout / "COHORT249-RECORDS.bin"
    stream.write_bytes(b"".join(helper.RECORD.pack(*row) for row in changed))
    after = staged_hashes(directory)
    require(changed_paths(adaptation["adapted_staging_sha256"], after)
            == ["cout/COHORT249-RECORDS.bin"], "only one stream changed")
    legal = helper.checked_native(binaries["legality_h"], [cin, cout],
                                  directory / "legality.json", helper.LEGAL_PASS)
    columns = helper.checked_native(binaries["columns_h"], [stream],
                                    directory / "columns.json", helper.COLUMN_PASS,
                                    helper.ENDPOINT_FAILURE)
    literal = helper.invoice(changed)
    reconcile_legality(helper, legal, literal)
    original = helper.invoice(records)
    require(literal["records"] == original["records"] - 1 and
            literal["adds"] == original["adds"] - 1 and literal["rank_mass"] == original["rank_mass"],
            "one unpriced scalar ADD omitted with unchanged frame bill")
    differences = helper.scalar_differences(changed)
    require(differences == [{"output": 470, "input_columns": [444]}], "exact missing-restoration defect")
    return {
        "adaptation": adaptation, "control_staging_sha256": after,
        "mutation": {"file": "cout/COHORT249-RECORDS.bin", "zero_based_record_index": index,
                     "before": list(records[index]), "after": None},
        "legality": legal, "columns": columns, "invoice": literal,
        "scalar_differences": differences,
    }


def run_native(snapshot_root, outputs_by_fixture, workdir, boost_include, compiler="c++"):
    snapshot_root, workdir, boost_include = map(Path, (snapshot_root, workdir, boost_include))
    require(set(outputs_by_fixture) == set(FIXTURES), "fixed native fixture inventory")
    helper = load_helper(snapshot_root)
    workdir.mkdir(parents=True, exist_ok=False)
    binaries, backend = helper.compile_native(snapshot_root, workdir, boost_include, compiler)
    results, streams = {}, {}
    for name in FIXTURES:
        results[name], streams[name] = fixture_checks(
            helper, binaries, snapshot_root, name, Path(outputs_by_fixture[name]), workdir)
    require(results["kernel"]["prefix"] == results["active_alias"]["prefix"],
            "active aliases preserve the complete signed prefix invoice")
    controls_directory = workdir / "controls"
    controls_directory.mkdir()
    kernel_output = Path(outputs_by_fixture["kernel"])
    controls = metadata_controls(helper, binaries[9], snapshot_root, kernel_output,
                                 controls_directory, results["kernel"])
    controls["missing_exit_shear"] = exit_shear_control(
        helper, binaries[9], snapshot_root, kernel_output, controls_directory, streams["kernel"])
    return {
        "status": "PASS_KERNEL_ENTRANCE_NATIVE_BOUNDARY", "backend": backend,
        "reused_helper": {"path": HELPER.as_posix(), "sha256": HELPER_SHA256},
        "compile_contract": {"HDIM": 8, "VPORTS": 111, "RHELP": 439, "NCOPY": [9, 10]},
        "fixtures": results, "controls": controls,
        "scope": "Five-stage finite native replay with a nonempty declared kernel selection and local role labels; "
                 "kernel-to-word binding is a separate model obligation. No physical ownership, bank, "
                 "nine-/eleven-stage, or supplier admission is asserted.",
        "inherited_nondegeneracy_receipt_flag_is_not_a_fresh_bank_audit": True,
        "no_new_kappa": True,
    }
