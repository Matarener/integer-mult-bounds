#!/usr/bin/env python3
"""Verify the union-support length-22 word census.

Stages, all from pinned sources:

1. Integrity: the pinned corrected engine of #2973 is byte-unchanged, and the
   union engine differs from it by exactly the committed DELTA.diff.
2. The predecessor package's own math check passes.
3. The predecessor's raw-product brute-force cross-check passes with the union
   engine as the engine under test. That check runs every small-domain split in
   all four budget modes; with the union budget enabled by default, positive
   universal counts exercise the new prune.
4. Union-only small-domain check: with both older budgets disabled, the union
   budget alone must still find exactly the brute-force universal count.
5. The six recorded L20/L18 zero-hit receipts replay to complete=true and zero
   hits under the union engine. Node counts are deliberately not compared:
   the union budget removes nodes by design, and the pinned predecessor
   receipts stay unchanged.
6. Length-22 probes, one split per invocation, sharded over the fifteen
   restricted-growth length-four prefixes but node-comparable to an
   unsharded run (duplicate roots subtracted). A completed zero-hit split is a
   finite split exclusion; an aborted run is a tree-size lower bound only.

The committed RESULT.json is the session receipt and is never rewritten.
Each run writes LAST-RUN.json.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PREDECESSOR = REPO / "research" / "f7-weight-parity-census-correction"
ENGINE = HERE / "engine" / "union_census.c"
DELTA = HERE / "engine" / "DELTA.diff"
PREDECESSOR_SHA = "265ead915d1b490c1923bce9b894ecac60f6195fc3d2ceadd6b25077238f415a"

RECORDED_CASES = [
    ("7", "20", "n7_l20_10_10", (10, 10)),
    ("7", "20", "n7_l20_10_9", (10, 9)),
    ("7", "20", "n7_l20_10_8", (10, 8)),
    ("7", "20", "n7_l20_9_9", (9, 9)),
    ("7", "20", "n7_l20_10_7", (10, 7)),
    ("7", "18", "n7_l18_9_9", (9, 9)),
]

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PREDECESSOR / "validation"))


def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def sha256(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_engine(source, n, length, out):
    cmd = ["cc", "-O3", "-Wall", "-Wextra", "-Werror", "-std=c11",
           f"-DN={n}", f"-DL={length}", str(source), "-o", str(out)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return str(out)


def run_case(binary, split, directory, extra=(), cap=0):
    directory.mkdir(parents=True, exist_ok=True)
    hitfile = directory / "hits.txt"
    datafile = directory / "result.json"
    cmd = [binary, f"{split[0]},{split[1]}", "--hits", str(hitfile),
           "--json", str(datafile), *extra]
    if cap:
        cmd += ["--cap", str(cap)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(datafile.read_text()) if datafile.exists() else None
    words = hitfile.read_text().splitlines() if hitfile.exists() else []
    return proc, data, words


def stage_integrity():
    pred_source = PREDECESSOR / "engine" / "corrected_census.c"
    require(sha256(pred_source) == PREDECESSOR_SHA,
            "pinned predecessor engine hash changed")
    import difflib
    before = pred_source.read_text().splitlines(keepends=True)
    after = ENGINE.read_text().splitlines(keepends=True)
    delta = "".join(difflib.unified_diff(
        before, after, fromfile="engine/corrected_census.c",
        tofile="engine/union_census.c", n=0))
    require(delta == DELTA.read_text(),
            "union engine differs from the committed DELTA.diff")
    return {"predecessor_engine_sha256": sha256(pred_source),
            "union_engine_sha256": sha256(ENGINE),
            "delta_matches_commit": True}


def stage_math_check():
    proc = subprocess.run(
        [sys.executable, "-B", str(PREDECESSOR / "math" / "check_math.py")],
        capture_output=True, text=True)
    require(proc.returncode == 0,
            f"predecessor math check failed:\n{proc.stdout[-2000:]}")
    return {"check_math_exit": 0}


def stage_brute(work):
    proc = subprocess.run(
        [sys.executable, "-B",
         str(PREDECESSOR / "validation" / "check_corrected_c.py"),
         "--engine-source", str(ENGINE),
         "--output-dir", str(work / "brute")],
        capture_output=True, text=True)
    require(proc.returncode == 0,
            f"union-engine brute cross-check failed:\n"
            f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    return {"check_corrected_c_exit": 0}


def stage_union_only(work):
    from brute_validation import brute
    ground = brute(4, 8)
    binary = compile_engine(ENGINE, 4, 8, work / "union_only_n4_l8")
    rows = []
    for split, expected in ground["splits"].items():
        proc, data, words = run_case(
            binary, tuple(map(int, split.split(","))), work / f"uo_{split}",
            extra=("--no-even-budget", "--no-odd-budget"))
        require(proc.returncode == 0 and data["complete"] is True,
                f"union-only ({split}): did not complete")
        require(data["total"][0]["hits"] == expected["universal"],
                f"union-only ({split}): {data['total'][0]['hits']} != "
                f"{expected['universal']}")
        require(len(words) == len(set(words)) == data["total"][0]["hits"],
                f"union-only ({split}): hit-file mismatch")
        rows.append({"split": split, "universal": expected["universal"],
                     "nodes": data["total"][0]["nodes"]})
    return {"n": 4, "length": 8, "splits": rows}


def stage_receipts(work):
    rows = []
    for n, length, case, split in RECORDED_CASES:
        binary = compile_engine(ENGINE, n, length, work / f"receipt_n{n}_l{length}")
        proc, data, words = run_case(binary, split, work / f"receipt_{case}")
        require(proc.returncode == 0 and data["complete"] is True,
                f"{case}: replay did not complete (exit {proc.returncode})")
        total = data["total"][0]
        require(total["hits"] == 0 and total["candidate_restored_leaves"] == 0,
                f"{case}: unexpected candidate leaf or hit")
        rows.append({"case": case, "split": list(split),
                     "nodes": total["nodes"],
                     "union_budget_prunes": total["union_budget_prunes"],
                     "complete": True, "hits": 0,
                     "node_exact_with_predecessor": False})
    return {"replayed_cases": rows,
            "note": "result check only; the union budget changes node counts "
                    "by design and the pinned receipts are unchanged"}


def stage_probe(splits, workers, work):
    import sharded
    committed = json.loads((HERE / "RESULT.json").read_text())
    recorded = {tuple(r["split"]): r for r in committed["probes"]}
    binary = compile_engine(ENGINE, 7, 22, work / "union_n7_l22")
    rows = []
    for split in splits:
        require(split in recorded, f"split {split} is not in RESULT.json")
        rec = recorded[split]
        if rec["finite_split_exclusion"]:
            fresh = sharded.run_split(Path(binary), split, workers,
                                      work / f"probe_{split[0]}_{split[1]}")
            total = fresh["totals"]
            require(fresh["complete"] and fresh["hits"] == 0,
                    f"split {split}: recorded complete but fresh run was not a "
                    f"complete zero-hit run")
            require(total["nodes"] == rec["sharded_nodes"],
                    f"split {split}: node drift {total['nodes']} != "
                    f"{rec['sharded_nodes']}")
            rows.append({"split": list(split), "complete": True, "hits": 0,
                         "sharded_nodes": total["nodes"],
                         "finite_split_exclusion": True,
                         "shards": fresh["shards"]})
        else:
            require(rec["complete"] is False and rec["capped_shards"],
                    f"split {split}: bad lower-bound receipt")
            rows.append({"split": list(split), "complete": False,
                         "sharded_nodes": rec["sharded_nodes"],
                         "capped_shards": rec["capped_shards"],
                         "finite_split_exclusion": False,
                         "note": "lower-bound receipt only; not re-run"})
    return {"probes": rows}


def parse_split(parser, item):
    parts = item.split(",")
    if len(parts) != 2 or not all(p.strip().isdigit() for p in parts):
        parser.error(f"--probe-split expects S,T; got {item!r}")
    return (int(parts[0]), int(parts[1]))


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-probe", action="store_true",
                        help="integrity, math, brute and receipt stages only")
    parser.add_argument("--probe-split", action="append", metavar="S,T",
                        help="replay one recorded split; repeatable")
    parser.add_argument("--probe-all", action="store_true",
                        help="replay every completed split in RESULT.json")
    parser.add_argument("--workers", type=int, default=15)
    args = parser.parse_args()

    result = {"schema": 1, "package": "f7-l22-union-census"}
    probe_only = bool(args.probe_split or args.probe_all)
    with tempfile.TemporaryDirectory(prefix="unioncensus-") as tmp:
        work = Path(tmp)
        result["integrity"] = stage_integrity()
        if not probe_only:
            result["math_check"] = stage_math_check()
            result["brute_crosscheck"] = stage_brute(work)
            result["union_only"] = stage_union_only(work)
            result["receipts"] = stage_receipts(work)
        if args.probe_split:
            splits = []
            for item in args.probe_split:
                split = parse_split(parser, item)
                if split not in splits:
                    splits.append(split)
            result["probe"] = stage_probe(splits, args.workers, work)
        elif args.probe_all:
            committed = json.loads((HERE / "RESULT.json").read_text())
            splits = [tuple(r["split"]) for r in committed["probes"]
                      if r["finite_split_exclusion"]]
            result["probe"] = stage_probe(splits, args.workers, work)
    report = HERE / "LAST-RUN.json"
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if "probe" in result:
        for row in result["probe"]["probes"]:
            print(f"  probe {row['split']}: complete={row['complete']} "
                  f"sharded_nodes={row['sharded_nodes']:,} "
                  f"exclusion={row['finite_split_exclusion']}")
    if "receipts" in result:
        for row in result["receipts"]["replayed_cases"]:
            print(f"  receipt {row['case']}: nodes={row['nodes']:,} hits=0")
    print("PASS_F7_L22_UNION_CENSUS")


if __name__ == "__main__":
    main()
