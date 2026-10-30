#!/usr/bin/env python3
"""Independent raw-mask proof of the three-line box obstruction.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
Definitions and prior classifications: Aaron Wang and Arham Tahir;
see README.md and SOURCES.json. No predecessor code is executed.
"""
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
import argparse
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW_TYPES = tuple((a, b) for a in range(8) for b in range(8) if a & b)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    frozen = manifest["frozen_sources"]
    need(bool(frozen), "no frozen sources")
    paths = set()
    for base, records in ((ROOT, manifest["files"]), (HERE, frozen)):
        for entry in records:
            if entry.get("usage", "input") != "input":
                continue
            path = base / entry["path"]
            need(path not in paths, "duplicate source path")
            paths.add(path)
            need(hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"],
                 "source digest mismatch: " + str(path))


def dot(a, b):
    return (a & b).bit_count() % 2


OPTIONS = tuple(tuple((a, b) for a in range(1, 8) for b in range(1, 8)
                      if a & ~cap_a == 0 and b & ~cap_b == 0 and dot(a, b))
                for cap_a, cap_b in RAW_TYPES)


@lru_cache(maxsize=None)
def compatible(source_type, source_a, target_type):
    """All diagonal-valid target options satisfying this forward zero arc."""
    constrained = not dot(RAW_TYPES[source_type][0], RAW_TYPES[target_type][1])
    return sum(1 << i for i, (_, b) in enumerate(OPTIONS[target_type])
               if not constrained or not dot(source_a, b))


def triple_witness(types):
    """Exact join of all diagonal-valid label pairs in every line order."""
    need(len(types) == 3 and all(0 <= t < len(RAW_TYPES) for t in types),
         "expected three raw-type indices")
    for order in permutations(range(3)):
        t0, t1, t2 = (types[i] for i in order)
        for a0, b0 in OPTIONS[t0]:
            allowed1 = compatible(t0, a0, t1)
            allowed2 = compatible(t0, a0, t2)
            for j, (a1, b1) in enumerate(OPTIONS[t1]):
                if not (allowed1 >> j) & 1:
                    continue
                final = allowed2 & compatible(t1, a1, t2)
                if final:
                    a2, b2 = OPTIONS[t2][(final & -final).bit_length() - 1]
                    a, b = [0] * 3, [0] * 3
                    for line, aa, bb in zip(order, (a0, a1, a2), (b0, b1, b2)):
                        a[line], b[line] = aa, bb
                    return {"kept": list(order), "order": list(order), "a": a, "b": b}
    return None


def check_witness(a0, b0, zeros, witness):
    """Definition-level replay, including direction and unkept-line scope."""
    n = len(a0)
    need(len(b0) == n and len(witness["a"]) == n and len(witness["b"]) == n,
         "label extent mismatch")
    order = witness["order"]
    need(len(order) == len(set(order)) and set(order) == set(witness["kept"]),
         "invalid kept order")
    need(all(0 <= t < n for t in order), "invalid line")
    for i, t in enumerate(order):
        a, b = witness["a"][t], witness["b"][t]
        need(0 <= a < 8 and 0 <= b < 8, "invalid mask")
        need(a & ~a0[t] == 0 and b & ~b0[t] == 0, "outside anchor box")
        need(dot(a, b) == 1, "diagonal is not one")
        for s in order[i + 1:]:
            need((t, s) not in zeros or dot(a, witness["b"][s]) == 0,
                 "forward zero arc violated")


def missing_arc_witness(a0, b0, x, y, z):
    need(len(a0) == len(b0) and len({x, y, z}) == 3,
         "need three distinct lines")
    need(all(0 <= t < len(a0) for t in (x, y, z)), "invalid line")
    common = 7
    for t in (x, y, z):
        common &= a0[t] & b0[t]
    need(common.bit_count() >= 2, "missing two common tied bits")
    first = common & -common
    second = (common ^ first) & -(common ^ first)
    labels = [0] * len(a0)
    labels[x] = labels[y] = first
    labels[z] = second
    return {"kept": [x, y, z], "order": [x, y, z],
            "a": labels, "b": list(labels)}


def coherent_families(size):
    result = set()
    for pair in (3, 5, 6):
        basic = RAW_TYPES.index((pair, pair))
        for special in ((pair, 7), (7, pair)):
            other = RAW_TYPES.index(special)
            for count in range(size + 1):
                result.add(tuple(sorted((basic,) * (size - count) + (other,) * count)))
    return result


def classify():
    forbidden = set()
    checked = 0
    for triple in combinations_with_replacement(range(len(RAW_TYPES)), 3):
        checked += 1
        witness = triple_witness(triple)
        if witness is None:
            forbidden.add(triple)
        else:
            a0, b0 = zip(*(RAW_TYPES[t] for t in triple))
            zeros = {(i, j) for i in range(3) for j in range(3)
                     if i != j and not dot(a0[i], b0[j])}
            check_witness(a0, b0, zeros, witness)
    need(checked == math.comb(39, 3), "incomplete triple universe")
    need(forbidden == coherent_families(3), "triple classification mismatch")
    # Deliberately unpruned: independent.py instead extends forbidden prefixes.
    families = []
    five_checked = 0
    for family in combinations_with_replacement(range(len(RAW_TYPES)), 5):
        five_checked += 1
        if all(triple in forbidden for triple in combinations(family, 3)):
            families.append(family)
    need(five_checked == math.comb(41, 5), "incomplete five-line universe")
    need(set(families) == coherent_families(5), "five-line classification mismatch")
    return {
        "raw_type_count": len(RAW_TYPES), "triple_count": checked,
        "forbidden_triples": [list(t) for t in sorted(forbidden)],
        "family_count": len(families), "families": [list(t) for t in sorted(families)],
        "exact_formula_match": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print recomputed receipt")
    args = parser.parse_args()
    authenticate()
    result = classify()
    previous = json.loads((HERE / "inputs/pr3031-floor.json").read_text())["v5"]["obstructions"]
    archived = sorted(tuple(sorted(RAW_TYPES.index(pair) for pair in zip(row["a0"], row["b0"])))
                      for row in previous)
    need(archived == [tuple(row) for row in result["families"]],
         "independent families disagree with pinned PR3031 receipt")
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == json.loads((HERE / "RESULT.json").read_text()), "receipt mismatch")
        print("PASS independent pair-option joins: 9139 triples, 749398 five-multisets, 33 families")


if __name__ == "__main__":
    main()
