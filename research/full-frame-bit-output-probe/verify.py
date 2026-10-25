#!/usr/bin/env python3
"""Replay the full-frame BIT probe and its finite bridged controls."""
from __future__ import annotations

import argparse
import gzip
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BIT = ROOT / "research/e8-bit-p111-tuned"
SKELETON = ROOT / "research/e8-bit-carrier-skeleton"

sys.path.insert(0, str(BIT / "code"))

import xcheck_p  # noqa: E402
import boundary_audit  # noqa: E402


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"load module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


levers = load_module("bit_profile_levers", ROOT / "research/bit-revision3-levers-seed03/levers.py")


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_json(path: Path):
    return json.loads(path.read_text())


def make_candidate():
    source = json.load(gzip.open(BIT / "data/bitE8mut-p111.json.gz", "rt"))
    word = json.loads(json.dumps(source))
    v = word["v"]
    full = next(i for i, frame in enumerate(word["frames"]) if len(frame) == v)
    zero = next(i for i, frame in enumerate(word["frames"]) if not frame)
    word["R"] = 0
    word["start"] = word["start"][:v] + [zero] * v
    word["final"] = [full] * (2 * v)
    word["D"] = []
    word["A"] = []
    word["B"] = [[full, v + t, [t]] for t in range(v)]
    word["C"] = []
    word["scatter"] = [[] for _ in range(v)]
    word["ret"] = []
    word.pop("stats", None)
    return word, full


def exact_local_replay(word, full):
    v = word["v"]
    W = xcheck_p.Word(word)
    labels = W.labels()
    values, current, stats = W.replay()
    need(len(values) == 2 * v, "arbitrary dirty-column census")
    need(all(values[s] == 1 << s for s in range(v)), "sources restore every input column")
    need(all(values[v + t] == (1 << (v + t)) | (1 << t) for t in range(v)),
         "every target is y_t+x_t")
    need(all(current[r] == full for r in range(2 * v)), "all outputs finish in FULL")
    need(stats["B"] == v and stats["scatter_terms"] == 0, "direct-copy gate census")
    hypotheses, conclusion, _ = W.interface()
    need(all(hypotheses.values()), "H1-H5 under the changed terminal contract")
    need(all(conclusion.values()), "interleaved-interface conclusion")

    # A source mutation must alter the exact endpoint.
    mutant = json.loads(json.dumps(word))
    mutant["B"][0][2] = [1]
    wrong, _, _ = xcheck_p.Word(mutant).replay()
    need(wrong[v] != (1 << v) | 1, "changed-source mutant was not detected")

    profile = Counter()
    for s in range(v):
        profile[W.fdim[full] - W.fdim[word["start"][s]]] += 1
        profile[W.fdim[full] - W.fdim[word["start"][v + s]]] += 1
    need(profile == Counter({7: v, 8: v}), "source/target frame-climb profile")
    return labels, hypotheses, conclusion, stats, profile


def run(argv, *, cwd=ROOT):
    return subprocess.run(
        [str(part) for part in argv], cwd=cwd, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )


def cxx_prefix():
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    need(compiler and shutil.which(compiler[0]), "C++17 compiler is unavailable")
    include = SKELETON / "portable-include"
    checkers = SKELETON / "code/bit/checkers"
    boost = Path(os.environ.get("BOOST_INCLUDE", "/usr/include"))
    return compiler, include, checkers, boost


def run_official_checkers(word):
    compiler, include, checkers, boost = cxx_prefix()
    with tempfile.TemporaryDirectory(prefix="full-frame-bit-output-") as td:
        temp = Path(td)
        candidate = temp / "direct-full.json.gz"
        candidate.write_bytes(gzip.compress(
            json.dumps(word, separators=(",", ":")).encode(), mtime=0
        ))
        records, initial, output = temp / "records", temp / "cin", temp / "cout"
        run([sys.executable, "-B", SKELETON / "code/bit/export_records.py", candidate, records])
        run([sys.executable, "-B", SKELETON / "code/bit/regression/stage_cohort.py",
             records, records, initial, output])

        common = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=0", "-DVPORTS=111", "-DRHELP=0",
                  f"-I{include}", f"-I{checkers}", f"-I{boost}"]
        legality = temp / "legality"
        run([*compiler, *common, "-o", legality, checkers / "legality_h.cpp"])
        run([legality, initial, output, output / "legality.json"])
        legality_result = load_json(output / "legality.json")
        need(legality_result["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
             "retained local legality checker")
        need(legality_result["copies"] == legality_result["erasures"] == 0,
             "candidate has no retained-center copies")
        need(legality_result["rank_mass"] == 1665 and legality_result["all_final_frames_pass"],
             "local physical profile and final frames")

        bridged = []
        for pairs in (2, 4, 5):
            binary = temp / f"columns-k{pairs}"
            result_path = output / f"columns-k{pairs}.json"
            run([*compiler, *common, f"-DKPAIRS={pairs}", "-o", binary,
                 checkers / "columns_k.cpp"])
            run([binary, output / "COHORT249-RECORDS.bin", result_path])
            result = load_json(result_path)
            stages = 2 * pairs + 1
            need(result["status"] == ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"
                                       if pairs == 2 else
                                       "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"),
                 f"retained {stages}-stage formal-column checker")
            need(result["formal_columns_checked"] == 2 * pairs * 111,
                 f"complete {stages}-stage physical-column count")
            need(result["fresh_center_copies"] == 0 and result["local_scalar_additions"] == 111,
                 f"zero-center {stages}-stage program")
            need(result["local_raw_H"] == [[7, 111], [8, 111]],
                 f"{stages}-stage local profile")
            need(result["bridge_additions"] == 6 * (pairs - 1) * 111,
                 f"{stages}-stage bridge count")
            controls = result["negative_controls"]
            need(len(controls) == 6 * (pairs - 1) and all(c["rejected"] for c in controls),
                 f"all omitted-bridge controls at {stages} stages")
            bridged.append({
                "stages": stages,
                "formal_columns": result["formal_columns_checked"],
                "local_scalar_additions": result["local_scalar_additions"],
                "bridge_additions": result["bridge_additions"],
                "omitted_bridge_controls_rejected": len(controls),
            })
        return {
            "local_legality": {
                "status": legality_result["status"],
                "registers": 222,
                "moves": legality_result["nested_MOVEs"],
                "adds": legality_result["common_frame_ADDs"],
                "copies": legality_result["copies"],
                "rank_mass": legality_result["rank_mass"],
                "all_final_frames_pass": legality_result["all_final_frames_pass"],
            },
            "bridged": bridged,
        }


def endpoint_and_budget_audits(word):
    global_source = (BIT / "vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py").read_text()
    geometry_source = (SKELETON / "code/nine/geometry.py").read_text()
    need("rho=P.row_join(A)" in geometry_source and "rho*S.diag(U,S.eye(7))*rho" in geometry_source,
         "pinned interstage reflection convention changed")
    checker_source = (SKELETON / "code/bit/checkers/columns_k.cpp").read_text()
    need("if(q.op==0){if(q.f)H[q.f]++;}else if(q.op==1)e.push_back" in checker_source,
         "scalar checker MOVE handling changed")
    full = boundary_audit.full_frame_audit(word, global_source, levers)
    W = xcheck_p.Word(word)
    W.labels()
    rotating = boundary_audit.rotating_normal_probe(W.lines + W.punct, levers)
    return full, rotating


def current_outer_contract():
    global_k = (BIT / "vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py").read_text()
    adapter = (BIT / "code/adapt9p.py").read_text()
    assembly = (BIT / "vendor/pr510/e8-r480-nine-stage/code/assemble9.py").read_text()
    need("lg['copies']==lg['erasures']==9" in global_k,
         "pinned global template center-count premise changed")
    need("9 <= CST <= 72" in adapter, "pinned assembly adaptation center-rank premise changed")
    need("9 * 8 * L" in assembly, "pinned selected assembly deficit formula changed")
    return {
        "global_template_requires_nine_copies": True,
        "adapted_assembly_requires_center_rank_between_9_and_72": True,
        "selected_assembly_deficit_uses_nine_rank8_centers": True,
    }


def build_result():
    selected = load_json(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == "0.001672660197076918", "selected frontier changed; refresh the probe")
    word, full = make_candidate()
    labels, hypotheses, conclusion, stats, profile = exact_local_replay(word, full)
    physical = run_official_checkers(word)
    full_audit, rotating = endpoint_and_budget_audits(word)
    return {
        "status": "PASS_FULL_FRAME_SCOPE_CORRECTION_AND_ROTATING_NORMAL_ENDPOINT_AUDIT",
        "selected_kappa_unchanged": selected["decimal"],
        "candidate": {
            "v": word["v"], "helpers": word["R"], "retained_totals": len(word["ret"]),
            "direct_B_gates": len(word["B"]), "full_frame_id": full,
            "labels": labels, "replay_gates": dict(stats),
            "profile": {str(r): n for r, n in sorted(profile.items())},
            "h1_h5": hypotheses, "interface_conclusion": conclusion,
            "exact_arbitrary_input_map": "all sources restored; each target y_t+x_t",
        },
        "official_finite_checks": physical,
        "scalar_column_checks_do_not_verify_address_frame_junctions": True,
        "address_boundary_and_complete_mass_audit": full_audit,
        "rotating_normal_experiment": rotating,
        "current_outer_contract": current_outer_contract(),
        "unproved": [
            "a changed template with matched address endpoints and positive complete rank deficit",
            "a joint consumer that avoids the rotating spectator's separate rank-two correction",
            "a valid improved complex supplier",
            "all-size precision, tape, wrapper and selected cold replay",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if args.audit_only:
        need(not args.write_result, "audit-only does not regenerate the full receipt")
        word, _ = make_candidate()
        full_audit, rotating = endpoint_and_budget_audits(word)
        expected = load_json(PACKAGE / "RESULT.json")
        need(full_audit == expected["address_boundary_and_complete_mass_audit"], "boundary audit receipt")
        need(rotating == expected["rotating_normal_experiment"], "rotating-normal audit receipt")
        print("PASS_EXACT_ADDRESS_ENDPOINT_AND_COMPLETE_RANK_AUDITS")
        return
    result = build_result()
    path = PACKAGE / "RESULT.json"
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_result:
        path.write_text(encoded)
    else:
        need(path.exists(), "RESULT.json is missing; run --write-result intentionally")
        need(path.read_text() == encoded, "RESULT.json differs; inspect changes before regeneration")
    print(result["status"])
    print(json.dumps({
        "profile": result["candidate"]["profile"],
        "stages": result["official_finite_checks"]["bridged"],
        "full_frame_nine_stage_bill_at_zero": result["address_boundary_and_complete_mass_audit"]["complete_rank_budgets"][1]["bill_at_zero"],
        "rotating_normal_literal_closure_bill_at_zero": result["rotating_normal_experiment"]["corrected_zero_saving_bill"],
        "selected_kappa_unchanged": result["selected_kappa_unchanged"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
