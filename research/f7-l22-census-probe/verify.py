#!/usr/bin/env python3
"""Bounded length-22 probe of the corrected Hamming-weight-parity census.

Three stages, all from pinned sources:

1. Integrity: the extended engine differs from the pinned predecessor
   engine only in the documented compile-time gate lines.
2. Validation: (a) the pinned package's own math check passes;
   (b) the extended engine passes the predecessor's small-domain
   brute-force cross-check (all budget modes) via its check_corrected_c.py;
   (c) the extended engine, compiled at L=20 and L=18, reproduces all six
   recorded receipts of the predecessor package node-exactly.
3. Probe: census runs at length 22 for the nine open splits of the L22
   split domain. A split whose run finishes with exit 0, complete=true and
   zero hits is a finite exclusion of that split. A run that hits its cap
   aborts (exit 2, complete=false) and records only a LOWER BOUND on that
   split's tree size. Timing fields are not compared.

Replay scope:

* The registered checks cover stages 1-2 and a fresh node-exact replay of
  the three completed exclusions (11,7), (10,8) and (11,8), one command
  per split (`--probe-split S,T`). These three exclusions are the
  package's finite claims and are CI-certified.
* `--probe-all-splits` is the opt-in full measurement: it additionally
  replays the six capped lower-bound probes against the committed
  RESULT.json receipt. That is about 1.4e10 nodes and is not run by CI;
  the six capped probes stay locally measured and reproducible.
* The committed RESULT.json session receipt is never rewritten; every run
  writes LAST-RUN.json instead.

Stage 3 measures the resource budget named as the blocker of the L22
census in research/f7-l22-split-domain (PR #3708) and #2973. No complete
exclusion is claimed for any split that aborted, and no claim at all is
made about f(7) beyond what complete zero-hit splits imply.
"""
import argparse
import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PREDECESSOR = REPO / "research" / "f7-weight-parity-census-correction"

# The nine open length-22 splits from research/f7-l22-split-domain (PR #3708),
# after the two 17-point splits are excluded by the imported set-level
# results of #2773 and #2870.
OPEN_SPLITS = [(11, 11), (11, 10), (11, 9), (10, 10), (11, 8),
               (10, 9), (11, 7), (10, 8), (9, 9)]

# The three splits whose census finished with complete=true and zero hits.
# Registered CI commands replay exactly these, one split per command.
EXCLUSION_SPLITS = [(11, 7), (10, 8), (11, 8)]

RECORDED_CASES = [
    ("7", "20", "n7_l20_10_10"),
    ("7", "20", "n7_l20_10_9"),
    ("7", "20", "n7_l20_10_8"),
    ("7", "20", "n7_l20_9_9"),
    ("7", "20", "n7_l20_10_7"),
    ("7", "18", "n7_l18_9_9"),
]


def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_engine(source, n, l, out):
    cmd = ["cc", "-O3", "-Wall", "-Wextra", "-Werror", "-std=c11",
           f"-DN={n}", f"-DL={l}", str(source), "-o", str(out)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def run_case(binary, split, directory, cap=0):
    directory.mkdir(parents=True, exist_ok=True)
    hitfile = directory / "hits.txt"
    datafile = directory / "result.json"
    cmd = [str(binary), f"{split[0]},{split[1]}", "--hits", str(hitfile),
           "--json", str(datafile)]
    if cap:
        cmd += ["--cap", str(cap)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(datafile.read_text())
    words = hitfile.read_text().splitlines() if hitfile.exists() else []
    return proc, data, words


def stage_integrity():
    pred_source = PREDECESSOR / "engine" / "corrected_census.c"
    ext_source = HERE / "engine" / "extended_census.c"
    require(sha256(pred_source) ==
            "265ead915d1b490c1923bce9b894ecac60f6195fc3d2ceadd6b25077238f415a",
            "pinned predecessor engine hash changed")
    pred_lines = pred_source.read_text().splitlines()
    ext_lines = ext_source.read_text().splitlines()
    require(len(pred_lines) == len(ext_lines),
            "extended engine must have the same line count")
    changed = [(i + 1, a, b) for i, (a, b) in
               enumerate(zip(pred_lines, ext_lines)) if a != b]
    allowed = {15, 35, 36}
    require({c[0] for c in changed} == allowed,
            f"unexpected engine delta at lines {[c[0] for c in changed]}")
    require(changed[0][2].strip().startswith("* N in [1,7], positive even L<=22"),
            "line 15 must be the header comment only")
    require("L > 22" in changed[1][2] and "L <= 22" in changed[2][2],
            "lines 35-36 must change only the L<=20 gate to L<=22")
    return {"predecessor_engine_sha256": sha256(pred_source),
            "extended_engine_sha256": sha256(ext_source),
            "changed_lines": sorted(allowed)}


def stage_math_check():
    proc = subprocess.run(
        [sys.executable, "-B", str(PREDECESSOR / "math" / "check_math.py")],
        capture_output=True, text=True)
    require(proc.returncode == 0, f"predecessor math check failed:\n{proc.stdout[-2000:]}")
    return {"check_math_exit": 0}


def stage_brute_crosscheck(work):
    proc = subprocess.run(
        [sys.executable, "-B",
         str(PREDECESSOR / "validation" / "check_corrected_c.py"),
         "--engine-source", str(HERE / "engine" / "extended_census.c"),
         "--output-dir", str(work / "brute")],
        capture_output=True, text=True)
    require(proc.returncode == 0,
            f"extended-engine brute cross-check failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    return {"check_corrected_c_exit": 0}


def stage_replay_receipts(work):
    source = HERE / "engine" / "extended_census.c"
    per_case = []
    for n, l, case in RECORDED_CASES:
        recorded = json.loads(
            (PREDECESSOR / "engine" / "results" / f"{case}.json").read_text())
        rec = recorded["shards"][0]
        binary = work / f"census_n{n}_l{l}_ext"
        compile_engine(source, n, l, binary)
        proc, data, words = run_case(binary, (recorded["split"][0], recorded["split"][1]),
                                     work / f"replay_{case}")
        require(proc.returncode == 0 and data["complete"] is True,
                f"{case}: replay did not complete (exit {proc.returncode})")
        total = data["total"][0]
        fields = {}
        for key in ("nodes", "candidate_restored_leaves", "hits",
                    "even_budget", "odd_budget"):
            if key in ("even_budget", "odd_budget"):
                fields[key] = (data[key], recorded[key])
            else:
                fields[key] = (total[key], rec[key])
        for key, (got, want) in fields.items():
            require(got == want,
                    f"{case}: {key} replayed {got} != recorded {want}")
        require(total["hits"] == len(words), f"{case}: hit-file mismatch")
        per_case.append({"case": case, "nodes": total["nodes"],
                         "candidate_restored_leaves":
                             total["candidate_restored_leaves"],
                         "hits": total["hits"], "node_exact_match": True})
    return {"replayed_cases": per_case}


def probe_one(split, cap, work):
    s, t = split
    binary = work / f"census_n7_l22"
    directory = work / f"probe_{s}_{t}"
    directory.mkdir(parents=True, exist_ok=True)
    proc, data, words = run_case(binary, split, directory, cap=cap)
    total = data["total"][0]
    return {
        "split": [s, t],
        "even_budget": data["even_budget"],
        "odd_budget": data["odd_budget"],
        "complete": data["complete"],
        "aborted": data["aborted"],
        "process_exit": proc.returncode,
        "nodes": total["nodes"],
        "candidate_restored_leaves": total["candidate_restored_leaves"],
        "hits": total["hits"],
        "hit_words": words,
        "seconds": total["seconds"],
        "finite_split_exclusion": bool(proc.returncode == 0
                                       and data["complete"] is True
                                       and total["hits"] == 0),
    }


def stage_probe(splits, cap, workers):
    """Fresh capped probes, compared against the committed RESULT.json.

    The committed receipt is session evidence and is never rewritten. A
    fresh run must agree with it: a split recorded complete must complete
    again with the identical node count and zero hits (node counts are
    cap-independent for completed runs); a split recorded aborted at the
    recorded cap must abort again at the fresh cap with zero hits. The
    fresh cap must not exceed the recorded cap. Determinism of the
    traversal order is what makes exact node equality possible; timing
    fields are excluded everywhere.

    The registered CI commands pass one exclusion split each. The six
    capped lower-bound splits are replayed only by the explicit opt-in
    `--probe-all-splits`, never by a registered command.
    """
    committed_path = HERE / "RESULT.json"
    require(committed_path.exists(),
            "RESULT.json (committed session receipt) is missing; it is the "
            "comparison target and must not be deleted")
    committed = json.loads(committed_path.read_text())
    recorded_cap = committed["probe"]["cap_per_split"]
    require(cap <= recorded_cap,
            f"fresh cap {cap} exceeds recorded cap {recorded_cap}")
    recorded = {tuple(r["split"]): r for r in committed["probe"]["probes"]}
    require(set(recorded) == set(OPEN_SPLITS), "committed splits changed")
    for split in splits:
        require(tuple(split) in recorded,
                f"split {split} is not in the committed RESULT.json receipt")

    work = Path(tempfile.mkdtemp(prefix="l22probe-"))
    try:
        binary = work / "census_n7_l22"
        compile_engine(HERE / "engine" / "extended_census.c", 7, 22, binary)
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {split: pool.submit(probe_one, split, cap, work)
                       for split in splits}
            rows = [futures[split].result() for split in splits]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    for row in rows:
        rec = recorded[tuple(row["split"])]
        require(row["hits"] == 0 and rec["hits"] == 0,
                f"split {row['split']}: unexpected hit")
        if rec["finite_split_exclusion"]:
            require(row["finite_split_exclusion"],
                    f"split {row['split']}: recorded complete but fresh run "
                    f"did not complete (nodes {row['nodes']})")
            require(row["nodes"] == rec["nodes"],
                    f"split {row['split']}: node drift {row['nodes']} vs "
                    f"recorded {rec['nodes']}")
        else:
            require(row["nodes"] == cap,
                    f"split {row['split']}: aborted run stopped at "
                    f"{row['nodes']} != cap {cap}")
            require(row["nodes"] <= rec["nodes"],
                    f"split {row['split']}: fresh nodes exceed recorded")
    complete = [r for r in rows if r["finite_split_exclusion"]]
    aborted = [r for r in rows if not r["finite_split_exclusion"]]
    return {"cap_per_split": cap, "recorded_cap": recorded_cap,
            "compared_against": "committed RESULT.json",
            "splits": rows,
            "complete_zero_hit_splits": [r["split"] for r in complete],
            "aborted_splits": [r["split"] for r in aborted],
            "any_hits": any(r["hits"] for r in rows)}


def parse_probe_split(parser, item):
    parts = item.split(",")
    if len(parts) != 2 or not all(p.strip().isdigit() for p in parts):
        parser.error(f"--probe-split expects S,T as integers; got {item!r}")
    split = (int(parts[0]), int(parts[1]))
    if split not in OPEN_SPLITS:
        parser.error(f"--probe-split {item}: not one of the nine open "
                     "length-22 splits")
    return split


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--probe-cap", type=int, default=2_000_000_000,
                        help="node cap per length-22 probe (0 = unlimited); "
                             "must not exceed the recorded cap in RESULT.json")
    parser.add_argument("--workers", type=int, default=9)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--skip-probe", action="store_true",
                      help="run only integrity, math and validation stages")
    mode.add_argument("--probe-all-splits", action="store_true",
                      help="opt-in full nine-split replay of the committed "
                           "RESULT.json receipt, including the six capped "
                           "lower-bound probes (about 1.4e10 nodes; not run "
                           "by CI)")
    mode.add_argument("--probe-split", action="append", metavar="S,T",
                      help="replay only the named split(s); repeatable; the "
                           "registered CI commands replay one completed "
                           "exclusion per invocation")
    args = parser.parse_args()

    splits = None
    if args.probe_split:
        splits = []
        for item in args.probe_split:
            split = parse_probe_split(parser, item)
            if split not in splits:
                splits.append(split)
    probe_only = bool(splits) or args.probe_all_splits

    result = {"schema": 1, "package": "f7-l22-census-probe"}
    with tempfile.TemporaryDirectory(prefix="l22probestage-") as tmp:
        work = Path(tmp)
        result["integrity"] = stage_integrity()
        if not probe_only:
            result["math_check"] = stage_math_check()
            result["brute_crosscheck"] = stage_brute_crosscheck(work)
            result["receipt_replay"] = stage_replay_receipts(work)
        if not args.skip_probe:
            probe_splits = (OPEN_SPLITS if args.probe_all_splits
                            else (splits or EXCLUSION_SPLITS))
            result["probe"] = stage_probe(probe_splits, args.probe_cap,
                                          args.workers)

    report = HERE / "LAST-RUN.json"
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if "probe" in result:
        for row in result["probe"]["splits"]:
            print(f"  probe {row['split']}: complete={row['complete']} "
                  f"nodes={row['nodes']:,} hits={row['hits']} "
                  f"finite_split_exclusion={row['finite_split_exclusion']}")
        p = result["probe"]
        print("complete zero-hit splits:", p["complete_zero_hit_splits"])
        print("aborted splits:", p["aborted_splits"])
        print("any hits:", p["any_hits"])
    if "receipt_replay" in result:
        for row in result["receipt_replay"]["replayed_cases"]:
            print(f"  replay {row['case']}: nodes={row['nodes']:,} "
                  f"node_exact_match={row['node_exact_match']}")
    print("PASS_F7_L22_CENSUS_PROBE")
    if "probe" in result and result["probe"]["any_hits"]:
        print("NOTE: a probe reported hits; inspect hit_words in the fresh "
              "run before relying on any exclusion claim.")


if __name__ == "__main__":
    main()
