#!/usr/bin/env python3
"""Exercise source/log/data/chart/control rejection on disposable fixture copies."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile

import check_strict_bundle as gate

RECEIPTS = ("REPLAY.json", "global/audit/OWNERS-AND-PROFILE.json",
            "global/audit/ASYNC-AUDIT.json", "global/audit/PREFIX-AND-INVOICE.json",
            "ASSEMBLY.json", "INDEPENDENT-T16.json", "lift/PARENT-LIFT-RECEIPT.json",
            "ADMISSION-CONTROLS.json", "BIT-SUPPLIER-CONTROLS.json")


def reject(controls, name, expected, function):
    try:
        function()
    except ValueError as error:
        gate.require(expected in str(error), "unexpected rejection: " + str(error))
        controls.append({"name": name, "rejected_by": str(error)})
    else:
        raise ValueError("accepted negative control: " + name)


def source_controls(args, scratch, controls):
    pins = scratch / "SOURCES.json"
    pins.write_bytes(args.pins.read_bytes() + b" ")
    reject(controls, "changed_source_inventory", "exact PR3308 source inventory",
           lambda: gate.verify_inputs(args.repo, pins))
    source = scratch / "source"
    shutil.copytree(args.source, source)
    target = source / "code/audit_allcold.py"
    target.write_bytes(target.read_bytes() + b"\n")
    reject(controls, "changed_frozen_verifier", "strict source differs",
           lambda: gate.verify_source(args.repo, source, args.data))


def data_log_controls(args, scratch, controls):
    logs = scratch / "logs"
    logs.mkdir()
    for name in ("STAGES.json", "REPLAY.json", *(s + ".log" for s in gate.STAGES)):
        shutil.copyfile(args.strict / name, logs / name)
    target = logs / "audit.log"
    target.write_bytes(target.read_bytes() + b"changed\n")
    reject(controls, "changed_stage_log", "changed raw stage log",
           lambda: gate.verify_logs(logs))
    data = scratch / "data"
    shutil.copytree(args.data, data)
    target = data / "SPEC.json"
    record = gate.read(target)
    record["data"]["owners_sha256"] = "0" * 64
    target.write_text(json.dumps(record))
    reject(controls, "changed_candidate_binding", "candidate owner byte bindings",
           lambda: gate.verify_data(data))


def binding_controls(args, scratch, controls):
    receipts = scratch / "receipts"
    receipts.mkdir()
    for name in RECEIPTS:
        target = receipts / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.strict / name, target)
    target = receipts / "INDEPENDENT-T16.json"
    original = target.read_bytes()
    record = gate.read(target)
    record["actual_73_axis_charts"] -= 1
    target.write_text(json.dumps(record))
    reject(controls, "stale_actual_chart_count", "actual charts",
           lambda: gate.verify_bindings(receipts, args.data))
    target.write_bytes(original)
    record = gate.read(target)
    record["controls_rejected"].pop()
    target.write_text(json.dumps(record))
    reject(controls, "missing_construction_control", "independent construction controls",
           lambda: gate.verify_bindings(receipts, args.data))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "pins", "source", "data", "strict", "scratch", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    controls = []
    with tempfile.TemporaryDirectory(prefix="gate-controls-", dir=args.scratch) as temp:
        scratch = Path(temp)
        source_controls(args, scratch, controls)
        data_log_controls(args, scratch, controls)
        binding_controls(args, scratch, controls)
    result = {"status": "PASS_STRICT_BUNDLE_REJECTION_CONTROLS", "rejected": controls,
              "verifier_sha256": gate.sha(Path(gate.__file__)),
              "test_sha256": gate.sha(Path(__file__)), "candidate_data": gate.verify_data(args.data),
              "assembly_sha256": gate.sha(args.strict / "ASSEMBLY.json"),
              "invoice_sha256": gate.sha(args.strict / "global/audit/PREFIX-AND-INVOICE.json")}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], "rejected=" + str(len(controls)))


if __name__ == "__main__":
    main()
