#!/usr/bin/env python3
"""Bounded source/operator/arithmetic regression; full admission is separate.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. Preserved full-run receipts are evidence, not a substitute replay.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from common import HERE, REPO, authenticate, check_no_python_caches, need
from replay import ACTIVE, COUNTS, make_adapter
from receipt_transport import (check as check_transport, controls as transport_controls,
                               historical_source_sha, read, sha)

EXECUTION_SOURCES = {"common.py", "replay.py", "operator_admission.py",
                     "joint_bound.py", "INPUT-PINS.json"}
RECEIPTS = {"RESULT.json", "INHERITED-RESULT.json", "ADMISSION-RESULT.json",
            "RELEASE-RECEIPT.json", "STRICT-RESULT.json", "OPERATOR.json",
            "JOINT-BOUND.json", "ASSEMBLY.json", "PREFIX-AND-INVOICE.json",
            "OUTER-LEDGER.json", "SPEC.json", "MIXED-CONTRACT.json",
            "CHALLENGES-normal.json", "CHALLENGES-optimized.json"}
BOUND_RECEIPTS = {"result": "ADMISSION-RESULT.json", "release": "RELEASE-RECEIPT.json",
                  "strict_result": "STRICT-RESULT.json", "assembly": "ASSEMBLY.json",
                  "invoice": "PREFIX-AND-INVOICE.json", "outer": "OUTER-LEDGER.json",
                  "spec": "SPEC.json", "contract": "MIXED-CONTRACT.json"}


def evidence_coverage(evidence):
    need(set(evidence["execution_source_sha256"]) == EXECUTION_SOURCES,
         "complete execution source coverage")
    need(set(evidence["receipt_sha256"]) == {"evidence/" + p for p in RECEIPTS},
         "complete recorded receipt coverage")


def rejecting(action, message):
    try:
        action()
    except ValueError as exc:
        need(message in str(exc), "specific cache rejection")
        return
    raise ValueError("accepted invalid cache fixture")


def cache_controls(root):
    cache = root / "cache-fixture"
    cache.mkdir()
    bad = cache / "module.pyc"
    bad.write_bytes(b"compiled cache witness")
    rejecting(lambda: check_no_python_caches([cache]), "compiled scientific source cache")
    bad.unlink()
    link = cache / "linked-source"
    link.symlink_to(root, target_is_directory=True)
    rejecting(lambda: check_no_python_caches([cache]), "scientific source symlink")
    link.unlink()
    check_no_python_caches([cache])


def main():
    count = authenticate()
    transport = check_transport()
    transport['negative_controls'] = transport_controls()
    evidence = read(HERE / "EVIDENCE.json")
    need(evidence["status"] == "RECORDED_COMPLETE_FINITE_REPLAY", "complete run evidence")
    evidence_coverage(evidence)
    for field, message in (("execution_source_sha256", "execution source coverage"),
                           ("receipt_sha256", "recorded receipt coverage")):
        mutant = json.loads(json.dumps(evidence))
        mutant[field].pop(next(iter(mutant[field])))
        rejecting(lambda: evidence_coverage(mutant), message)
    for name, digest in evidence["execution_source_sha256"].items():
        need(historical_source_sha(name) == digest, "full-run source changed: " + name)
    for name, digest in evidence["receipt_sha256"].items():
        need(sha(HERE / name) == digest, "preserved receipt changed: " + name)
    outer = read(HERE / "evidence/RESULT.json")
    inherited = read(HERE / "evidence/INHERITED-RESULT.json")
    admitted = read(HERE / "evidence/ADMISSION-RESULT.json")
    need(outer["status"] == "PASS_POOLED_COMPLETE_FINITE_ADMISSION", "recorded wrapper result")
    need(inherited["status"] == admitted["status"] ==
         "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE", "recorded complete engine result")
    need(outer["inherited_result_sha256"] == sha(HERE / "evidence/INHERITED-RESULT.json")
         and inherited["admission_result_sha256"] == sha(HERE / "evidence/ADMISSION-RESULT.json")
         and admitted["release_receipt_sha256"] == sha(HERE / "evidence/RELEASE-RECEIPT.json")
         and outer["operator_receipt_sha256"] == sha(HERE / "evidence/OPERATOR.json"),
         "recorded release chain")
    env = dict(PATH=os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               PYTHONINTMAXSTRDIGITS="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    options = ["-O"] if not __debug__ else []
    with tempfile.TemporaryDirectory(prefix="pooled-complex-check-") as temp:
        root = Path(temp)
        cache_controls(root)
        adapter = root / "adapter"
        patches = make_adapter(adapter)
        need(len(patches) == 21, "complete recorded adapter")

        def run(script, args=()):
            command = [sys.executable, *options, "-B", str(script), *map(str, args)]
            result = subprocess.run(command, cwd=REPO, env=env, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    timeout=180)
            need(result.returncode == 0, "failed " + script.name + ":\n" + result.stdout)

        run(adapter / "test_binding.py")
        run(HERE / "operator_admission.py", ["--controls", "--output", root / "operator.json"])
        run(HERE / "joint_bound_inputs.py", ["--output", root / "joint.json"])
        operator = read(root / "operator.json")
        joint = read(root / "joint.json")
        need(operator == read(HERE / "evidence/OPERATOR.json"), "exact operator reproduction")
        recorded = read(HERE / "evidence/JOINT-BOUND.json")
        for key in set(joint) | set(recorded):
            if key not in ("status", "release_binding"):
                need(joint[key] == recorded[key], "independent joint arithmetic: " + key)
        need(recorded["release_binding"]["status"] == "COMPLETED_FINITE_RELEASE_RECEIPTS_BOUND",
             "recorded full release binding")
        need(set(recorded["release_binding"]["files"]) == set(BOUND_RECEIPTS),
             "complete joint receipt coverage")
        for key, name in BOUND_RECEIPTS.items():
            need(recorded["release_binding"]["files"][key]["sha256"] == sha(HERE / "evidence" / name),
                 "joint receipt binding: " + key)
        need(joint["all_size_admission"] is False and joint["selected_frontier_changed"] is False,
             "finite scope remains explicit")
        check_no_python_caches([root])
    authenticate()
    print(json.dumps(dict(status="PASS_POOLED_BOUNDED_REGRESSION", pinned_inputs=count,
                          active_providers=ACTIVE, call_counts=COUNTS, adapter_changes=len(patches),
                          operator_controls=len(operator["controls"]), arithmetic_controls=len(joint["controls"]),
                          lossless_transport=transport,
                          scope="Fresh operator/arithmetic/binding regression plus preserved full-run source/receipt integrity; not a fresh complete release or all-size theorem."),
                     sort_keys=True))


if __name__ == "__main__":
    main()
