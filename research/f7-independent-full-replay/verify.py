#!/usr/bin/env python3
"""Run an independent finite replay of the corrected seven-label census."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
OLD_ENGINE = "research/universal-f7-singleton-seedb859517b/engine.py"
UPPER_WITNESS = "research/f7-weight-parity-census-correction/UPPER-WITNESS.json"
CASES = ((10, 10), (10, 9), (10, 8), (9, 9), (10, 7))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_input_pins() -> dict[str, str]:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    pins = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], f"input hash mismatch: {row['path']}")
        pins[row["path"]] = digest
    require(OLD_ENGINE in pins, "old census input is not declared")
    require(UPPER_WITNESS in pins, "upper witness input is not declared")
    return pins


def canonical_rgs(word: tuple[int, ...]) -> bool:
    names: dict[int, int] = {}
    for symbol in word:
        if symbol not in names:
            names[symbol] = len(names)
        if names[symbol] != symbol:
            return False
    return True


def direct_word_data(word: tuple[int, ...], n: int) -> dict[str, object]:
    state = 0
    prefix = [0]
    counts = [0] * n
    for symbol in word:
        counts[symbol] += 1
        state ^= 1 << symbol
        prefix.append(state)
    points = prefix[:-1]
    even = [x for x in points if x.bit_count() % 2 == 0]
    odd = [x for x in points if x.bit_count() % 2 == 1]
    bit0_even = [x for x in points if (x & 1) == 0]
    bit0_odd = [x for x in points if (x & 1) != 0]

    def excess(groups: list[list[int]]) -> int:
        return sum(
            len(g) * (len(g) - 1) // 2
            - len({a ^ b for a, b in itertools.combinations(g, 2)})
            for g in groups
        )

    cover = {a ^ b for a in points for b in points}
    return {
        "closed": state == 0,
        "counts": counts,
        "points": points,
        "distinct": len(set(points)) == len(points),
        "cover_size": len(cover),
        "weight_split": (len(even), len(odd)),
        "bit0_split": (len(bit0_even), len(bit0_odd)),
        "bit0_excess": excess([bit0_even, bit0_odd]),
        "balanced_budget": sum(len(g) * (len(g) - 1) // 2 for g in (even, odd)) - 7,
        "actual_bit0_budget": sum(len(g) * (len(g) - 1) // 2 for g in (bit0_even, bit0_odd)) - 7,
    }


def brute_small_domain() -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]]:
    """Directly enumerate raw words; use no census traversal implementation."""
    universal: list[tuple[int, ...]] = []
    bad_budget: list[tuple[int, ...]] = []
    for word in itertools.product(range(4), repeat=8):
        if not canonical_rgs(word):
            continue
        counts = [word.count(i) for i in range(4)]
        if counts != [2, 2, 2, 2]:
            continue
        data = direct_word_data(word, 4)
        if not data["closed"] or not data["distinct"] or data["weight_split"] != (4, 4):
            continue
        if data["cover_size"] != 16:
            continue
        universal.append(word)
        if data["bit0_excess"] > data["balanced_budget"]:
            bad_budget.append(word)
    return universal, bad_budget


def load_old_engine():
    path = ROOT / OLD_ENGINE
    spec = importlib.util.spec_from_file_location("f7_pinned_old_engine", path)
    require(spec is not None and spec.loader is not None, "cannot load pinned predecessor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def compile_replay(build_dir: Path) -> Path:
    compiler = shutil.which(os.environ.get("CC", "cc"))
    require(compiler is not None, "C compiler not found (set CC to clang or gcc)")
    executable = build_dir / "f7_replay"
    command = [
        compiler, "-O3", "-std=c11", "-Wall", "-Wextra", "-Werror",
        str(PACKAGE / "replay.c"), "-o", str(executable),
    ]
    subprocess.run(command, check=True, timeout=60)
    return executable


def run_census(executable: Path, n: int, length: int, split: tuple[int, int], cap: int | None = None):
    argv = [str(executable), str(n), str(length), str(split[0]), str(split[1])]
    if cap is not None:
        argv.append(str(cap))
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=600)
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid census output: {proc.stdout!r} {proc.stderr!r}") from exc
    return proc.returncode, result


def verify_upper_witness() -> str:
    data = json.loads((ROOT / UPPER_WITNESS).read_text())
    word = tuple(int(x) for x in data["word"])
    n = int(data["n"])
    require(n == 7 and len(word) == 24, "pinned upper witness dimensions changed")
    require(set(word) == set(range(n)), "upper witness omits a label")
    require(all(word.count(i) >= 2 and word.count(i) % 2 == 0 for i in range(n)),
            "upper witness is not restored with positive even multiplicities")
    report = direct_word_data(word, n)
    require(report["closed"] and report["cover_size"] == 1 << n,
            "upper witness failed direct XOR check")
    return data["word"]


def verify_small(executable: Path) -> dict[str, object]:
    word = (0, 1, 0, 2, 1, 3, 2, 3)
    data = direct_word_data(word, 4)
    require(data["closed"] and data["counts"] == [2, 2, 2, 2], "witness is not restored")
    require(data["distinct"] and data["cover_size"] == 16, "witness is not simple universal")
    require(data["weight_split"] == (4, 4), "unexpected time/weight parity split")
    require(data["bit0_split"] == (6, 2), "unexpected bit-0 class sizes")
    require(data["bit0_excess"] == 8 and data["balanced_budget"] == 5 and
            data["actual_bit0_budget"] == 9, "collision-budget arithmetic mismatch")

    all_hits, false_pruned = brute_small_domain()
    require(len(all_hits) == 22 and len(false_pruned) == 6,
            f"direct raw-word census mismatch: {len(all_hits)} hits, {len(false_pruned)} false prunes")
    require(word in false_pruned, "named word is absent from direct false-prune set")

    old = load_old_engine()
    old_unbudgeted = old.cyclic_census(4, 8, budget=None, simple=True, collect_all=True)
    old_budgeted = old.cyclic_census(4, 8, budget=5, simple=True, collect_all=True)
    def balanced_words(receipt):
        return {tuple(w) for w in receipt["words"]
                if direct_word_data(tuple(w), 4)["weight_split"] == (4, 4)}
    require(balanced_words(old_unbudgeted) == set(all_hits),
            "pinned predecessor unbudgeted hits disagree with direct oracle")
    require(balanced_words(old_budgeted) == set(all_hits) - set(false_pruned),
            "pinned predecessor's fixed budget does not reproduce the direct omissions")
    witness_unbudgeted = old.cyclic_census(
        4, 8, budget=None, simple=True, stop_on_first=True, prefix=word)
    witness_budgeted = old.cyclic_census(
        4, 8, budget=5, simple=True, stop_on_first=True, prefix=word)
    require(witness_unbudgeted["hits"] == 1 and witness_budgeted["hits"] == 0,
            "pinned predecessor did not accept/reject the named word as expected")

    status, replay = run_census(executable, 4, 8, (4, 4))
    require(status == 0 and replay["complete"] and not replay["aborted"] and
            replay["hits"] == "22", "independent small C census disagrees with raw oracle")
    cap_status, capped = run_census(executable, 7, 20, (10, 10), cap=1000)
    require(cap_status == 2 and capped["aborted"] and not capped["complete"] and
            capped["nodes"] == "1000", "node-cap control did not fail closed")

    return {
        "n4_l8_4_4_raw_canonical_universals": len(all_hits),
        "n4_l8_false_rejected_by_fixed_bit0_budget": len(false_pruned),
        "named_witness": "01021323",
        "named_witness_prefixes": data["points"],
        "weight_split": data["weight_split"],
        "bit0_split": data["bit0_split"],
        "bit0_excess": data["bit0_excess"],
        "old_fixed_budget": data["balanced_budget"],
        "actual_bit0_budget": data["actual_bit0_budget"],
        "new_census_small_hits": replay["hits"],
        "cap_fail_closed": True,
    }


def verify_full(executable: Path) -> list[dict[str, object]]:
    results = []
    for split in CASES:
        status, result = run_census(executable, 7, 20, split)
        require(status == 0 and result["complete"] and not result["aborted"],
                f"incomplete n=7 split {split}: rc={status} {result}")
        require(result["n"] == 7 and result["length"] == 20 and
                result["split"] == list(split), f"wrong run identity at split {split}")
        require(result["hits"] == "0", f"universal word found at split {split}")
        results.append(result)
    require(verify_upper_witness() == "010201030102010345464546",
            "pinned reflected-Gray control changed")

    expected_dir = ROOT / "research/f7-weight-parity-census-correction/engine/results"
    for split, result in zip(CASES, results):
        suffix = f"n7_l20_{split[0]}_{split[1]}.json"
        expected = json.loads((expected_dir / suffix).read_text())
        total = expected["total"]
        require(expected["complete"] is True and len(total) == 1 and
                expected["split"] == list(split) and
                expected["groups"] == "hamming_weight_parity" and
                total[0]["complete"] is True and total[0]["hits"] == 0,
                f"retained full-replay receipt is not a complete zero-hit result: {suffix}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="run all five complete n=7 censuses")
    parser.add_argument("--quick", action="store_true", help="run only independent small and cap controls")
    args = parser.parse_args()
    require(args.full != args.quick, "choose exactly one of --quick or --full")
    verify_input_pins()
    with tempfile.TemporaryDirectory(prefix="f7-independent-replay-") as tmp:
        executable = compile_replay(Path(tmp))
        small = verify_small(executable)
        print("SMALL", json.dumps(small, sort_keys=True))
        if args.quick:
            print("PASS_F7_INDEPENDENT_QUICK old_prune_false_on_6_of_22 no_full_n7_replay")
            return
        results = verify_full(executable)
        nodes = sum(int(result["nodes"]) for result in results)
        print("FULL_SPLITS", json.dumps([
            {"split": result["split"], "nodes": result["nodes"],
             "closed_leaves": result["closed_leaves"], "hits": result["hits"]}
            for result in results
        ], sort_keys=True))
        print(f"PASS_F7_INDEPENDENT_FULL cases=5 total_nodes={nodes} universal_words=0 upper_witness_length=24")


if __name__ == "__main__":
    main()
