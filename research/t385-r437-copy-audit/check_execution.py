#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate the recorded T385 run and forbid promotion of incomplete evidence.
This does not execute the scientific wrapper or convert author reuse into a new proof.
"""
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
STAGES = [
    "owners",
    "parent-lift",
    "rebind",
    "discovery",
    "outer-check_ledger.py",
    "outer-independent_check.py",
    "release",
]
HEAD = "de2cd5c58009205210e3bf328b0ef5cadf3903af"
ENDPOINT = (
    Fraction("0.001730578437266246818740") - Fraction(1, 10**46) - Fraction(1, 10**70)
)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    return json.loads(path.read_bytes())


def classify(evidence, admission, wrapper):
    need(
        evidence["source_head"] == HEAD and evidence["jobs"] == 1,
        "source/config binding",
    )
    need(evidence["native_and_ancestry_reused"] is True, "reuse boundary")
    stages = evidence["stages"]
    names = [stage["name"] for stage in stages]
    need(
        names == STAGES[: len(names)] and all(s["exit_code"] == 0 for s in stages),
        "completed stage prefix",
    )
    complete = (
        evidence["run_exit_code"] == 0
        and names == STAGES
        and admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE"
        and wrapper is not None
        and wrapper["status"] == "PASS_T385_COMPLETE_CONDITIONAL_RELEASE"
    )
    if evidence["classification"] == "COMPLETE_CONDITIONAL_REPLAY":
        need(complete, "incomplete execution cannot be promoted to complete replay")
        need(
            Fraction(admission["kappa"]) == Fraction(wrapper["kappa"]) == ENDPOINT,
            "exact released endpoint",
        )
        need(
            wrapper["changed_allocation_and_release_fresh"] is True
            and wrapper["native_and_ancestry_reused"] is True,
            "fresh/reused classification",
        )
        need(
            wrapper["admission_result_sha256"]
            == evidence["original_files"]["admission"]["original_sha256"],
            "wrapper binds the original admission-result bytes",
        )
        need(
            admission["source_manifest_sha256"] == evidence["source_manifest_sha256"],
            "admission source manifest",
        )
        need(
            admission["native_receipt_sha256"] == evidence["native_receipt_sha256"],
            "admission native receipt",
        )
        need(
            admission["replicas"] == 385
            and admission["actual_expected_helpers"] == 408,
            "literal construction size",
        )
        need(admission["stages"] == stages, "final stage records")
        return "COMPLETE_CONDITIONAL_REPLAY"
    need(
        evidence["classification"] == "INCOMPLETE_EXECUTION" and not complete,
        "execution classification",
    )
    need(evidence["run_exit_code"] != 0, "incomplete run has no successful exit")
    need(wrapper is None, "partial run has a contradictory full-wrapper result")
    return "INCOMPLETE_EXECUTION"


def main():
    manifest = read(P / "EVIDENCE.json")
    for name, digest in manifest["files"].items():
        path = P / name
        need(
            not Path(name).is_absolute() and ".." not in Path(name).parts,
            "evidence path",
        )
        need(
            path.is_file() and not path.is_symlink(), "missing/linked evidence: " + name
        )
        need(
            hashlib.sha256(path.read_bytes()).hexdigest() == digest,
            "evidence SHA: " + name,
        )
    evidence = read(P / "T385-EXECUTION.json")
    admission = read(P / "evidence/t385/admission-result.json")
    wrapper_path = P / "evidence/t385/wrapper-result.json"
    wrapper = read(wrapper_path) if wrapper_path.exists() else None
    result = classify(evidence, admission, wrapper)
    for stage in evidence["stages"]:
        path = P / "evidence/t385" / ("stage-" + stage["name"] + ".log")
        need(
            hashlib.sha256(path.read_bytes()).hexdigest() == stage["log_sha256"],
            "stage log binding",
        )
    mutants = []
    if result == "COMPLETE_CONDITIONAL_REPLAY":
        bad = copy.deepcopy(evidence)
        bad["stages"] = bad["stages"][:-1]
        mutants.append((bad, admission, wrapper))
        bad_admission = copy.deepcopy(admission)
        bad_admission["status"] = "PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED"
        mutants.append((evidence, bad_admission, wrapper))
        bad_wrapper = copy.deepcopy(wrapper)
        bad_wrapper["kappa"] = str(ENDPOINT + Fraction(1, 10**70))
        mutants.append((evidence, admission, bad_wrapper))
    else:
        bad = copy.deepcopy(evidence)
        bad["classification"] = "COMPLETE_CONDITIONAL_REPLAY"
        mutants.append((bad, admission, wrapper))
        bad = copy.deepcopy(evidence)
        bad["run_exit_code"] = 0
        mutants.append((bad, admission, wrapper))
        bad = copy.deepcopy(evidence)
        bad["native_and_ancestry_reused"] = False
        mutants.append((bad, admission, wrapper))
    for mutant in mutants:
        try:
            classify(*mutant)
        except ValueError:
            pass
        else:
            raise ValueError("accepted execution-coverage mutation")
    print(
        "PASS_T385_RECORDED_EVIDENCE classification="
        + result
        + " controls="
        + str(len(mutants))
    )


if __name__ == "__main__":
    main()
