#!/usr/bin/env python3
"""Recompute the exact finite certificate. Requires a C++20 compiler."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oracle import (
    ball,
    diagonal,
    direct_word,
    factors,
    identity,
    matmul,
    pack,
    representative,
    require,
    tables,
    target_lists,
    unpack,
)

PACKAGE = Path(__file__).resolve().parent
FLAGS = [
    "-std=c++20",
    "-O3",
    "-Wall",
    "-Wextra",
    "-Wconversion",
    "-Wsign-conversion",
    "-Wshadow",
    "-Wpedantic",
    "-Werror",
]
CASES = {
    "r3-two": (3, 2, 3, ["332", "334", "352"]),
    "r3-three": (3, 3, 4, ["333", "335"]),
    "r4-two": (4, 2, 3, ["3320", "3340", "3520"]),
    "r4-pair": (4, 2, 2, ["3300", "3500"]),
    "positive-control": (3, 1, 2, ["222", "224", "242"]),
}


def run(argv, timeout=600):
    return subprocess.run(
        argv, check=True, text=True, capture_output=True, timeout=timeout
    ).stdout


def source_pins():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    root = PACKAGE.parent.parent
    for row in sources["files"]:
        if row["usage"] == "input":
            path = root / row["path"]
            require(path.is_file(), f"missing input {path}")
            require(
                hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "input drift",
            )


def independent_probes(directory, multiply):
    group, _ = tables()
    expected = bytearray(x for row in group for x in row)
    for r in range(1, 5):
        alphabet = factors(r)
        for f in alphabet:
            expected.extend(pack(f, r))
        seed = 117
        for _ in range(1024):
            a = identity(r)
            for _ in range(5):
                seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
                a = matmul(a, alphabet[seed % len(alphabet)], r, multiply)
            expected.extend(pack(a, r))
            expected.extend(pack(matmul(a, diagonal((3,) * r), r, multiply), r))
    actual = (directory / "probes.bin").read_bytes()
    require(actual == expected, "independent full-convolution probe mismatch")
    return {
        "states": (len(expected) - 64) // 16,
        "group_products": 64,
        "sha256": hashlib.sha256(actual).hexdigest(),
    }


def independent_balls(directory, multiply):
    receipts = {}
    cache = {}
    for tag, (r, left, right, _) in CASES.items():
        for suffix, depth, inverse in [
            ("inverse", left, True),
            ("prefix", right - 1, False),
        ]:
            key = r, depth, inverse
            if key not in cache:
                cache[key] = ball(r, depth, inverse, multiply)
            data = (directory / f"{tag}-{suffix}.bin").read_bytes()
            require(len(data) % 16 == 0, "truncated ball")
            encoded = [data[k : k + 16] for k in range(0, len(data), 16)]
            order = [struct.unpack("<4I", x) for x in encoded]
            require(order == sorted(set(order)), "ball is not sorted and unique")
            actual = {unpack(x, r) for x in encoded}
            require(actual == cache[key], f"independent ball mismatch {tag}/{suffix}")
            receipts[f"{tag}-{suffix}"] = {
                "states": len(actual),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
    return receipts, cache


def attaining(multiply):
    omission = 0
    canonical = set()
    targets = target_lists()
    for target, cost in targets.items():
        canonical.add(representative(target))
        r = len(target)
        word = direct_word(target)
        require(len(word) == cost, "direct bill")
        a = identity(r)
        for f in word:
            a = matmul(a, f, r, multiply)
        require(a == diagonal(target), "direct endpoint")
        for k in range(len(word)):
            a = identity(r)
            for position, f in enumerate(word):
                if position != k:
                    a = matmul(a, f, r, multiply)
            require(a != diagonal(target), "deleted call accepted")
            omission += 1
    expected = {
        representative(tuple(map(int, s)))
        for tag, (_, _, _, ss) in CASES.items()
        if tag != "positive-control"
        for s in ss
    }
    require(canonical == expected, "symmetry representatives incomplete")
    return {
        "targets": len(targets),
        "orbits": len(canonical),
        "omissions": omission,
        "by_roles": {str(r): sum(len(t) == r for t in targets) for r in (3, 4)},
    }


def independent_meets(cache, multiply):
    # A separate exact membership check for every search with right depth <=3.
    result = {}
    for tag, (r, left, right, targets) in CASES.items():
        if right == 4:
            continue
        inverse = cache[r, left, True]
        positive = (
            cache.get((r, right, False)) if r == 4 else ball(r, right, False, multiply)
        )
        if positive is None:
            # The r4 depth-three ball is deliberately not stored. Native search
            # streams it, and its complete prefix ball is independently checked.
            continue
        hits = []
        for target in targets:
            wanted = {
                matmul(a, diagonal(tuple(map(int, target))), r, multiply)
                for a in inverse
            }
            hits.append(len(positive & wanted))
        require(
            all(x == 0 for x in hits) if tag != "positive-control" else all(hits),
            "independent meet",
        )
        result[tag] = hits
    return result


def compute(directory, compiler):
    source_pins()
    executable = directory / "search"
    run([compiler, *FLAGS, str(PACKAGE / "search.cpp"), "-o", str(executable)], 120)
    run([str(executable), "probes", str(directory)])
    lines = run([str(executable), "search", str(directory)])
    rows = [json.loads(line) for line in lines.splitlines()]
    require([x["tag"] for x in rows] == list(CASES), "search cases changed")
    for row in rows:
        r, left, right, targets = CASES[row["tag"]]
        require(
            (row["r"], row["left"], row["right"]) == (r, left, right), "search scope"
        )
        require(row["factors"] == len(factors(r)), "alphabet incomplete")
        require(
            row["candidates"] == row["prefix_ball"] * (row["factors"] + 1),
            "stream incomplete",
        )
        require(len(row["hits"]) == len(targets), "missing target")
        require(
            all(x == 0 for x in row["hits"])
            if row["tag"] != "positive-control"
            else all(x > 0 for x in row["hits"]),
            "wrong search endpoint result",
        )
    _, multiply = tables()
    probes = independent_probes(directory, multiply)
    balls, cache = independent_balls(directory, multiply)
    meets = independent_meets(cache, multiply)
    predecessor = json.loads(
        (
            PACKAGE.parent / "q8-inverse-label-pair-census" / "CERTIFICATE.json"
        ).read_text()
    )
    calibration = {}
    for name in ("diag_mi_mi", "diag_mi_mj", "diag_mj_mj"):
        value = predecessor["endpoints"][name]["positive"]["minimum"]
        require(type(value) is int and value == 6, "predecessor pair calibration")
        calibration[name] = value
    return {
        "scope": "finite positive-Q8 multiple-negative call minima",
        "search": rows,
        "balls": balls,
        "probes": probes,
        "attainment": attaining(multiply),
        "independent_meets": meets,
        "predecessor_pair_minima": calibration,
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    compiler = shutil.which("clang++") or shutil.which("g++")
    require(compiler is not None, "C++20 compiler required")
    if args.write_receipt:
        require(not args.write_receipt.exists(), "refusing to overwrite receipt")
    with tempfile.TemporaryDirectory(prefix="q8-sign-") as temporary:
        receipt = compute(Path(temporary), compiler)
    if args.write_receipt:
        with args.write_receipt.open("x") as output:
            output.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(
            json.dumps(receipt, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "receipt mismatch",
        )
    print("PASS_Q8_MULTIPLE_NEGATIVE targets=152 orbits=10 no_new_kappa")


if __name__ == "__main__":
    main()
