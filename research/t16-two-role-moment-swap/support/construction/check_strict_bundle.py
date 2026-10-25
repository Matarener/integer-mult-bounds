#!/usr/bin/env python3
"""Bind an unchanged T16 strict replay to frozen sources, data and raw logs.

This checks a completed replay. It does not replace or execute its verifier.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

PINS_SHA = "47c7f51236309db402155e625171fdd865fe3bbc4bf0a6941df710f2c52a286f"
BASE = "463113d675af7410ac91d53a4fed51ec6494eb9a"
STAGES = ("restore-parent", "bind8", "lift16", "bind", "emit", "audit", "invoice",
          "assembly", "admission-controls", "bit-supplier-controls", "independent-t16")
DATA = {"data/OWNERS.json.gz", "data/PLAN.json", "data/SPEC.json"}
PROVIDER = "candidate/strict/global/base/providers/gauge44/"
LIMIT = 64 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    require(path.is_file() and not path.is_symlink(), "regular file: " + str(path))
    require(path.stat().st_size <= LIMIT, "file size limit")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    require(path.stat().st_size <= LIMIT, "JSON size limit")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "JSON payload limit")
    return json.loads(raw)


def verify_inputs(repo, pins_path):
    require(sha(pins_path) == PINS_SHA, "exact PR3308 source inventory")
    pins = read(pins_path)
    require(pins["base_commit"] == BASE and len(pins["files"]) == 45, "canonical source base")
    hashes = {}
    for row in pins["files"]:
        if row["usage"] == "input":
            name = row["path"]
            path = repo / name
            require(path.resolve().is_relative_to(repo), "source path escape")
            digest = sha(path)
            require(digest == row["sha256"], "changed canonical input: " + name)
            hashes[name] = digest
    require(len(hashes) == 43, "complete canonical input inventory")
    return hashes


def verify_source(repo, source, data):
    archive = repo / "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
    expected = {}
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        require(len(members) <= 256 and sum(m.size for m in members) <= LIMIT,
                "frozen source archive limit")
        for member in members:
            require(member.isfile(), "nonregular frozen source")
            require((source / member.name).resolve().is_relative_to(source), "source path escape")
            expected[member.name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    require(len(expected) == 180, "frozen 179-file inventory plus its manifest")
    for name in DATA:
        expected[name] = sha(data / Path(name).name)
    actual = {}
    for index, path in enumerate(source.rglob("*")):
        require(index < 320, "expanded source path limit")
        if path.is_file():
            actual[path.relative_to(source).as_posix()] = sha(path)
    require(actual == expected, "strict source differs beyond frozen three-file overlay")
    return {"archive_sha256": sha(archive), "files": actual}


def verify_provider(repo, local):
    pins = read(repo / "research/complex-t16-two-stage-cycles/LOCAL-PINS.json")
    require(len(pins) <= 16, "provider artifact inventory")
    archive = repo / "research/community-frontier1094-audit/selected-replay.tar.gz"
    hashes = {}
    with tarfile.open(archive) as tar:
        for name, expected in pins.items():
            member = tar.getmember(PROVIDER + name)
            require(member.isfile() and member.size <= LIMIT, "provider member")
            digest = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
            require(digest == expected == sha(local / name), "unchanged selected provider: " + name)
            hashes[name] = digest
    return hashes


def verify_data(data):
    spec, plan = read(data / "SPEC.json"), read(data / "PLAN.json")
    owners = sha(data / "OWNERS.json.gz")
    require(spec["data"]["owners_sha256"] == plan["assignment_sha256"] == owners,
            "candidate owner byte bindings")
    require(plan["replica_lift"]["owners_file_sha256"] == owners, "lift owner byte binding")
    require(spec["data"]["plan_sha256"] == sha(data / "PLAN.json"), "candidate plan byte binding")
    return {name: sha(data / name) for name in ("OWNERS.json.gz", "PLAN.json", "SPEC.json")}


def verify_logs(strict):
    stages = read(strict / "STAGES.json")
    require(tuple(s["name"] for s in stages) == STAGES, "eleven strict stages")
    result = read(strict / "REPLAY.json")
    require(result["stages"] == stages, "final stage binding")
    for stage in stages:
        require(stage["exit_code"] == 0, "failed stage: " + stage["name"])
        require(sha(strict / (stage["name"] + ".log")) == stage["log_sha256"],
                "changed raw stage log: " + stage["name"])
    return [{k: s[k] for k in ("name", "exit_code", "log_sha256")} for s in stages]


def verify_bindings(strict, data):
    paths = {"result": "REPLAY.json", "owner": "global/audit/OWNERS-AND-PROFILE.json",
             "controller": "global/audit/ASYNC-AUDIT.json", "invoice": "global/audit/PREFIX-AND-INVOICE.json",
             "assembly": "ASSEMBLY.json", "independent": "INDEPENDENT-T16.json",
             "lift": "lift/PARENT-LIFT-RECEIPT.json", "admission": "ADMISSION-CONTROLS.json",
             "bit": "BIT-SUPPLIER-CONTROLS.json"}
    docs = {key: read(strict / path) for key, path in paths.items()}
    statuses = {"result": "PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY",
                "owner": "PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE",
                "controller": "PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS",
                "invoice": "PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE",
                "assembly": "PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY",
                "independent": "PASS_INDEPENDENT_T16_LITERAL_WINDOWS_CHARTS_PREFIX_ROW",
                "lift": "PASS_T16_DIRECT_SUM_PARENT_AND_LITERAL_SOURCE_WINDOWS",
                "admission": "PASS_EXACT_MIXED_048_ALLCOLD_NATIVE_ASSEMBLY_ADMISSION_NEGATIVE_CONTROLS",
                "bit": "PASS_PR589_BIT_SUPPLIER_DERIVED_DEFICIT_NEGATIVE_CONTROLS"}
    for key, expected in statuses.items():
        require(docs[key]["status"] == expected, "wrong status: " + key)
    owner, invoice = docs["owner"], docs["invoice"]
    controller, independent, lift = docs["controller"], docs["independent"], docs["lift"]
    spec = read(data / "SPEC.json")["expected"]
    require(owner["controller_audit_sha256"] == sha(strict / paths["controller"]), "controller hash")
    require(invoice["owner_audit_sha256"] == sha(strict / paths["owner"]), "owner hash")
    require(invoice["controller_audit_sha256"] == owner["controller_audit_sha256"], "invoice controller")
    require(docs["assembly"]["input_sha256"]["owner_audit"] == sha(strict / paths["owner"]), "assembly owner")
    require(docs["assembly"]["input_sha256"]["fresh_invoice"] == sha(strict / paths["invoice"]), "assembly invoice")
    require(owner["template_sha256"] == invoice["template_sha256"] == controller["template_sha256"]
            == docs["assembly"]["template_sha256"], "template bindings")
    require(owner["paid_profile"] == docs["assembly"]["complex_profile"] == spec["global_profile"]
            == independent["profile"] == docs["result"]["complex_profile"], "complete paid profile")
    require(independent["idle"] == spec["idle_remainder_profile"], "complete idle profile")
    require(owner["rank_mass"] == independent["rank_mass"] == 1041408, "full rank mass")
    require(owner["deficit"] == independent["deficit"] == 5120, "deficit")
    require(lift["actual_window_membership_checked"] == independent["roles"] == 69120, "all role windows")
    require(controller["complete_invocations"] == independent["calls"] == 144, "whole invocations")
    require(lift["T8_identity_control"] and lift["T8_source_window_identity"], "lift controls")
    require(controller["mutation_controls_run"] and len(controller["mutations_rejected"]) == 15, "controller controls")
    require(len(docs["admission"]["rejected_controls"]) == 69
            and not docs["admission"]["discovery_accepted_controls"], "admission controls")
    require(len(docs["bit"]["rejected_controls"]) == 12
            and docs["bit"]["derived_deficit"] == 10272, "bit controls")
    require(len(independent["controls_rejected"]) == 6, "independent construction controls")
    charts = owner["actual_73column_sigmas"]
    require(charts == independent["actual_73_axis_charts"] == controller["actual_orthogonal_73column_maps"]
            == spec["actual_73column_sigmas"], "actual charts")
    require(invoice["physical_stock_identity"] == {"data_and_owner_families": 14336,
            "local_helpers": 480, "private_centres": 8, "coefficient_work": 2}, "complete physical stock")
    require(owner["physical"] == invoice["physical"] == 14826 <= independent["physical"] == 14850,
            "actual versus conservative physical stock")
    require(invoice["global_prefix_bits"] == independent["prefix_bits"] == 397
            and invoice["charged_prefix_bits"] == 512, "precision charge")
    require(invoice["finite"]["physical_row_coefficient"] == independent["physical_row_coefficient"]
            == 16469 < 20161, "row charge")
    require(set(invoice["strict_checks"]) == {"local_primitive_bound", "logical", "router", "literal", "mass",
            "precision", "tape", "row", "halving"} and all(invoice["strict_checks"].values()), "finite invoice")
    return {"artifacts": {name: sha(strict / path) for name, path in paths.items()},
            "kappa_nomination": docs["result"]["kappa"], "roles": 69120, "calls": 144,
            "charts": charts, "actual_physical_stock": 14826, "conservative_physical_stock": 14850,
            "controls": docs["result"]["controls"], "profile": owner["paid_profile"], "idle": independent["idle"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "pins", "source", "data", "local", "strict", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, "optimized Python unsupported")
    result = {"status": "PASS_SOURCE_BOUND_T16_CONSTRUCTION_ADMISSION", "errors": 0,
              "canonical_base": BASE, "python": sys.version, "verifier_sha256": sha(Path(__file__)),
              "canonical_inputs": verify_inputs(args.repo.resolve(), args.pins),
              "source": verify_source(args.repo.resolve(), args.source.resolve(), args.data),
              "provider": verify_provider(args.repo.resolve(), args.local),
              "candidate_data": verify_data(args.data),
              "stages": verify_logs(args.strict), **verify_bindings(args.strict, args.data),
              "scope": "Finite unchanged-supplier placement, windows, charts, controller and charged invoice. "
                       "Native ancestry reused from the selected archive; exact scoring, full invoice review "
                       "and inherited multiplication-theorem premises are separate obligations."}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], "errors=0", "roles=69120", "calls=144")


if __name__ == "__main__":
    main()
