#!/usr/bin/env python3
"""Replay exact arithmetic and finite controls for characteristic-four floor obstructions."""

from itertools import combinations, product
from math import comb
from random import Random
import json
import hashlib
from pathlib import Path
import sys
from depth_two import census, calibrate, canonical, served_by_pairs
from axis_obstruction import evaluate as axis_evaluate, calibrate as axis_calibrate
from n4_controls import run_controls as structural_controls

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def limit(k, r):
    small = min(k, (r + 1) // 2)
    return k + small + (k - small) // 4


def packed_prefixes(word, k):
    require(len(word) == 4 * k, "length")
    require(all(word.count(j) == 4 for j in range(k)), "multiplicities")
    values = [0]
    counts = [0] * k
    for symbol in word[:-1]:
        counts[symbol] = (counts[symbol] + 1) % 4
        values.append(sum(count << (4 * j) for j, count in enumerate(counts)))
    parity_mask = sum(1 << (4 * j) for j in range(k))
    r = 4 * k - len({value & parity_mask for value in values})
    return values, r


def inspect_word(word, k, offsets):
    values, r = packed_prefixes(word, k)
    bad_mask = sum(2 << (4 * j) for j in range(k))
    upper = limit(k, r)
    maximum = 0
    for offset in offsets:
        actual = sum(not ((value + offset) & bad_mask) for value in values)
        require(actual <= upper, f"intersection bound: {word}, {offset}, {r}, {actual}, {upper}")
        maximum = max(maximum, actual)
    return maximum


def exhaustive_small():
    words = 0
    translations = 0
    for k in (2, 3):
        offsets = tuple(sum(x << (4 * j) for j, x in enumerate(v))
                        for v in product(range(4), repeat=k))
        positions = tuple(range(4 * k))
        for zero in combinations(positions, 4):
            rest = tuple(t for t in positions if t not in zero)
            choices = (rest,) if k == 2 else combinations(rest, 4)
            for one in choices:
                word = [2] * (4 * k)
                for t in zero:
                    word[t] = 0
                for t in one:
                    word[t] = 1
                inspect_word(word, k, offsets)
                words += 1
                translations += len(offsets)
    return words, translations


def random_large():
    rng = Random(102019)
    checked = 0
    for k in (4, 9, 18, 19):
        for _ in range(1000):
            word = [j for j in range(k) for _ in range(4)]
            rng.shuffle(word)
            offsets = tuple(sum(rng.randrange(4) << (4 * j) for j in range(k))
                            for _ in range(100))
            inspect_word(word, k, offsets)
            checked += 1
    return checked


def arithmetic():
    rows = []
    for r in range(76):
        n = 76 - r
        cube = comb(76, 3) * limit(19, r) // 4 + comb(76, 2) + 1
        parity = 1 + comb(n, 2) + comb(n, 4)
        upper = min(cube, parity)
        require(upper < 1 << 19, "nineteen-source strict exclusion")
        rows.append({"r": r, "cube_intersection": limit(19, r), "mask_upper": upper})
    return rows


def inventory_normal_form():
    compositions = [v for v in product(range(5), repeat=4) if sum(v) == 4]
    types = sorted(v for v in compositions if (3*v[0] + 2*v[1] + v[2]) % 4 == 1)
    rotations = set()
    for template in ((3, 0, 0, 1), (0, 2, 1, 1)):
        for shift in range(4):
            rotations.add(template[shift:] + template[:shift])
    require(len(compositions) == 35, "inventory composition count")
    require(set(types) == rotations and len(types) == 8, "inventory types")
    require(all(0 in row for row in types), "every inventory must miss a gap")
    return {"weak_compositions": len(compositions), "types": [list(v) for v in types],
            "type_count_vectors_k10": comb(17, 7)}


def check_maximizers():
    rows = json.loads((HERE / "MAXIMIZERS.json").read_text())["canonical_maximizers"]
    require(len(rows) == 4, "maximizer catalog size")
    seen = set()
    for row in rows:
        word = row["walk"]
        require(canonical(word), "maximizer is not first-occurrence canonical")
        require(tuple(word) not in seen, "duplicate maximizer")
        seen.add(tuple(word))
        reached = served_by_pairs(word, 5)
        missing = [m for m in range(1, 32) if not (reached >> m) & 1]
        require(reached.bit_count() == 29 and row["covered_nonzero"] == 28,
                "maximizer coverage")
        require(row["missing"] == missing, "maximizer missing masks")
        rounds = all(sorted(word[t:t+5]) == list(range(5)) for t in range(0, 20, 5))
        require(rounds and row["permutation_rounds"], "maximizer round structure")
    return len(rows)


def check_cube_sharpness():
    data = json.loads((HERE / "CUBE-SHARPNESS.json").read_text())
    require(data["k"] == 18 and data["cube_translate"] == [0]*18, "sharpness scope")
    values, repeated = packed_prefixes(data["word"], 18)
    high = sum(2 << (4*j) for j in range(18))
    inside = [t for t, value in enumerate(values) if not value & high]
    require(repeated == data["parity_repetitions"] == 0, "sharpness parity repeats")
    require(len(inside) == data["cube_intersection"] == limit(18, 0) == 22,
            "sharpness intersection")
    require(inside == data["valid_boundaries"], "sharpness boundary list")
    groups = data["bad_arc_groups"]
    require([len(g) for g in groups] == [4, 4, 5, 5], "sharpness groups")
    require(sorted(j for g in groups for j in g) == list(range(18)), "group partition")
    word = data["word"]
    require(word[:18] == list(range(18)), "sharpness initial calls")
    offset = 18
    for group in groups:
        length = 3*len(group)
        require(sorted(word[offset:offset+length]) == sorted(group*3), "bad arc inventory")
        offset += length
    return {"k": 18, "parity_repetitions": repeated, "cube_intersection": len(inside),
            "valid_boundaries": inside}


def depth_two_results():
    data = {"k4": census(4), "k5_full": census(5),
            "k5_at_least_30": census(5, 30), "k5_at_least_29": census(5, 29),
            "calibration": calibrate(), "maximizer_count": check_maximizers()}
    require(data["k5_at_least_30"]["solutions"] == 0, "depth-two maximum exceeds 29")
    require(data["k5_at_least_29"]["solutions"] == data["maximizer_count"],
            "maximizer catalog is incomplete")
    return data


def receipt():
    digest = hashlib.sha256()
    names = ('PROOF17.md', 'axis_obstruction.py', 'n4_controls.py', 'CERTIFICATE.json', 'CUBE-SHARPNESS.json', 'README.md', 'SOURCES.json', 'TASK.json', 'VERIFY.json', 'DEPTH2.md', 'MAXIMIZERS.json', 'depth_two.py', 'independent_depth2.c', 'independent_check.py', 'verify.py')
    for name in names:
        digest.update(name.encode() + b"\0" + hashlib.sha256((HERE / name).read_bytes()).digest())
    return digest.hexdigest()


def main():
    require(sys.argv[1:] in ([], ["--write-certificate"]), "unexpected arguments")
    rows = arithmetic()
    words, translations = exhaustive_small()
    large_words = random_large()
    result = {"claim": "9<=N(4)<=17", "cube_control_rows": rows,
              "small_words": words, "small_translations": translations,
              "random_words": large_words,
              "cube_control_source_count": 19,
              "cube_control_max_mask_upper": max(row["mask_upper"] for row in rows),
              "eighteen_exclusion": {"arithmetic": axis_evaluate(), "controls": axis_calibrate()},
              "structural_controls": structural_controls(),
              "inventory_normal_form": inventory_normal_form(),
              "cube_sharpness": check_cube_sharpness(),
              "depth_two": depth_two_results()}
    if sys.argv[1:]:
        (HERE / "CERTIFICATE.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads((HERE / "CERTIFICATE.json").read_text()),
                "certificate differs from recomputation")
    print(json.dumps({"claim": result["claim"], "k18_residual_branches": 6,
                      "depth2_max_nonzero": 28, "canonical_maximizers": 4}, sort_keys=True))
    print("receipt_sha256", receipt())
    print("PASS_CONNECTOR_CHAR4_FLOOR_OBSTRUCTIONS N4<=17 depth2_max=4 depth2_k5_coverage=28")


if __name__ == "__main__":
    main()
