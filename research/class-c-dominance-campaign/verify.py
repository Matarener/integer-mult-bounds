#!/usr/bin/env python3
"""Exact conditional campaign audit; no geometric span computation.

Krzysztof Wojt, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import csv
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
G = (0, 1, 2, 4, 8, 12, 20, 36)
PINS = {
    "rows70.csv": "c0eb6bb88498bf39a8b2020b1d0d600181f6e13eb9dd6a6e5f90794f0895754a",
    "rows17.csv": "9ebe7fc1ecd74148e7bdefa1f6bb2ed00551884b1a4a6558d7f129f7eef4efd5",
    "help-README.md": "aba39c91e262edfb495cf1ccaf7c7555199ee9c0b87e99ecd22e4f1bb14c292f",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dims(config):
    require(isinstance(config, str) and len(config) == 4, "need four dimensions")
    require(all(c in "1234567" for c in config), "dimension outside 1..7")
    values = tuple(map(int, config))
    require(values == tuple(sorted(values, reverse=True)), "noncanonical dimensions")
    return values


def dominates(target, source):
    return all(a >= b for a, b in zip(dims(target), dims(source)))


def admissible(config):
    return sum(G[d] for d in dims(config)) <= 52


def load_rows():
    for name, expected in PINS.items():
        actual = hashlib.sha256((HERE / "inputs" / name).read_bytes()).hexdigest()
        require(actual == expected, "source drift: " + name)
    with (HERE / "inputs/rows70.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    with (HERE / "inputs/rows17.csv").open(newline="") as handle:
        hard = list(csv.DictReader(handle))
    require([int(r["row_idx"]) for r in rows] == list(range(70)), "row identity/order")
    hard_projection = [{k: v for k, v in r.items() if k != "rrc_status"}
                       for r in rows if r["rrc_status"] == "HARD"]
    require(len(hard) == 17 and hard == hard_projection,
            "HARD table differs from source subset")
    for row in rows:
        weights = json.loads(row["weights"])
        require(int(row["d"]) + int(row["e"]) == len(weights), "dimension ledger")
        require(all(type(w) is int and 1 <= w <= 7 for w in weights), "piece weight")
        configs = row["covering_4flat_configs"].split()
        require(len(configs) == len(set(configs)), "duplicate configuration")
        require(all(admissible(c) for c in configs), "inadmissible listed configuration")
    return rows, hard


def covers(row, target, relation=dominates):
    return any(relation(target, source) for source in row["covering_4flat_configs"].split())


def minimum_covers(rows, configs, relation):
    needed = {int(r["row_idx"]) for r in rows if r["covering_4flat_configs"]}
    sets = {c: {int(r["row_idx"]) for r in rows if covers(r, c, relation)} for c in configs}
    for size in range(1, len(configs) + 1):
        solutions = [list(choice) for choice in itertools.combinations(configs, size)
                     if set().union(*(sets[c] for c in choice)) == needed]
        if solutions:
            return {"size": size, "solutions": solutions}
    raise ValueError("no campaign covers the listed incidences")


def plan(rows, targets):
    witnesses, uncovered = [], []
    for row in rows:
        match = next(((target, threshold, source) for target, threshold in targets
                      if threshold <= int(row["d"])
                      for source in row["covering_4flat_configs"].split()
                      if dominates(target, source)), None)
        if match is None:
            uncovered.append(int(row["row_idx"]))
        else:
            target, threshold, source = match
            witnesses.append({"row": int(row["row_idx"]), "d": int(row["d"]),
                              "source": source, "target": target, "threshold": threshold})
    return {"targets": [[c, t] for c, t in targets], "witnesses": witnesses,
            "uncovered": uncovered}


def validate_plan(rows, receipt):
    by_id = {int(r["row_idx"]): r for r in rows}
    seen = set()
    declared = {tuple(t) for t in receipt["targets"]}
    for target, threshold in declared:
        require(admissible(target), "target exceeds the 52-label budget")
        require(type(threshold) is int and threshold >= 1, "invalid threshold")
    for w in receipt["witnesses"]:
        require(w["row"] in by_id and w["row"] not in seen, "missing/duplicate row")
        seen.add(w["row"])
        row = by_id[w["row"]]
        require(w["d"] == int(row["d"]), "changed row dimension")
        require(w["source"] in row["covering_4flat_configs"].split(), "invented cover")
        require((w["target"], w["threshold"]) in declared, "undeclared target")
        require(dominates(w["target"], w["source"]), "invalid extension")
        require(w["threshold"] <= int(row["d"]), "span threshold too weak")
    require(seen.isdisjoint(receipt["uncovered"]), "covered row also uncovered")
    require(seen | set(receipt["uncovered"]) == set(by_id), "incomplete row partition")


def result(rows, hard):
    configs = sorted({c for r in rows for c in r["covering_4flat_configs"].split()})
    coverage = {
        "dominance": {c: [s for s in configs if dominates(c, s)] for c in configs},
        "cover_all": {c: [int(r["row_idx"]) for r in rows if covers(r, c)] for c in configs},
        "cover_hard": {c: [int(r["row_idx"]) for r in hard if covers(r, c)] for c in configs},
    }
    hard_plan = plan(hard, [("6554", 7), ("5555", 8)])
    all_plan = plan(rows, [("6554", 6), ("5555", 8)])
    validate_plan(hard, hard_plan)
    validate_plan(rows, all_plan)
    return {
        "schema_version": 1,
        "scope": "conditional scheduling implication; no geometric span pass or new exclusion",
        "coverage": coverage,
        "literal_minimum_hard": minimum_covers(hard, configs, lambda a, b: a == b),
        "literal_minimum_all": minimum_covers(rows, configs, lambda a, b: a == b),
        "claimed_three_literal_misses": [int(r["row_idx"]) for r in rows
                                         if r["covering_4flat_configs"] and not any(
                                             c in r["covering_4flat_configs"].split()
                                             for c in ("5544", "5555", "6554"))],
        "dominance_minimum_hard": minimum_covers(hard, configs, dominates),
        "dominance_minimum_all": minimum_covers(rows, configs, dominates),
        "hard_campaign": hard_plan, "all_campaign": all_plan, "source_sha256": PINS,
    }


def controls(hard, receipt):
    require(dominates("6554", "5544") and not dominates("6554", "5555"), "extension control")
    require(admissible("6554") and admissible("5555") and not admissible("6555"),
            "budget control")
    weak = plan(hard, [("6554", 8), ("5555", 8)])
    require(weak["uncovered"] == [7, 8, 13, 37], "T8-only must miss lower-d rows")
    require(receipt["hard_campaign"]["uncovered"] == [37], "hard remainder changed")
    require(receipt["all_campaign"]["uncovered"] == [3, 12, 24, 37, 54, 61],
            "no-config rows must stay unresolved")
    require(receipt["literal_minimum_hard"]["size"] == 3, "literal control changed")
    require(receipt["literal_minimum_all"]["size"] == 4, "all-row literal minimum changed")
    require(receipt["claimed_three_literal_misses"] == [4, 5, 6, 17, 20, 28, 33, 66, 69],
            "literal three-config claim control changed")
    require(receipt["dominance_minimum_hard"]["solutions"] == [["5555", "6554"]],
            "two-target minimum changed")
    mutations = []
    bad = copy.deepcopy(receipt["hard_campaign"])
    bad["witnesses"][0]["threshold"] = 8
    bad["targets"].append(["6554", 8])
    mutations.append(("weak threshold", bad))
    bad = copy.deepcopy(receipt["hard_campaign"])
    w = next(w for w in bad["witnesses"] if w["row"] == 35)
    w["target"], w["threshold"] = "6554", 7
    mutations.append(("false dominance", bad))
    bad = copy.deepcopy(receipt["hard_campaign"])
    bad["witnesses"][0]["source"] = "1111"
    mutations.append(("invented inherited cover", bad))
    bad = copy.deepcopy(receipt["hard_campaign"])
    bad["witnesses"][0]["target"] = "6555"
    bad["targets"].append(["6555", 7])
    mutations.append(("over-budget target", bad))
    for name, bad in mutations:
        try:
            validate_plan(hard, bad)
        except ValueError:
            continue
        raise ValueError("accepted mutant: " + name)
    return len(mutations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate deterministic receipt")
    args = parser.parse_args()
    rows, hard = load_rows()
    receipt = result(rows, hard)
    rejected = controls(hard, receipt)
    target = HERE / "RESULT.json"
    if args.write:
        target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        require(receipt == json.loads(target.read_text()), "committed receipt differs")
    print(f"PASS_CLASS_C_DOMINANCE hard=16 all=64 targets=2 rejected={rejected} no_span_pass")


if __name__ == "__main__":
    main()
