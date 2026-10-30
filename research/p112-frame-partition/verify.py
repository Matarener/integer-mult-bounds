#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact source-bound exclusion of a fourteen-frame P112 partition."""

import argparse
import copy
import hashlib
import json
import os
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
SOURCE_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
FLAGS = [
    "-std=c++20",
    "-O3",
    "-Wall",
    "-Wextra",
    "-Wpedantic",
    "-Wshadow",
    "-Wconversion",
    "-Werror",
]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_labels(data):
    need(hashlib.sha256(data).hexdigest() == SOURCE_SHA, "source hash")
    rows = json.loads(data)["recipes"]
    need(len(rows) == 112, "source count")
    need(sorted(r["port"] for r in rows) == list(range(112)), "source ports")
    labels = [r["q"] for r in sorted(rows, key=lambda r: r["port"])]
    need(
        all(type(q) is int and 0 < q < 512 and q.bit_count() % 2 for q in labels),
        "odd nine-bit labels",
    )
    need(len(set(labels)) == 112, "distinct labels")
    return labels


def frames_from_labels(labels):
    adjacent = [
        sum(
            1 << j
            for j in range(112)
            if i != j and (labels[i] & labels[j]).bit_count() % 2 == 0
        )
        for i in range(112)
    ]
    frames, pending = [], [((), (1 << 112) - 1)]
    for _ in range(200_000):
        if not pending:
            need(len(frames) == 4032, "complete frame count")
            return sorted(frames)
        chosen, candidates = pending.pop()
        if len(chosen) == 8:
            frames.append(chosen)
            need(len(frames) <= 4032, "frame capacity")
            continue
        for _ in range(candidates.bit_count()):
            bit = candidates & -candidates
            candidates -= bit
            p = bit.bit_length() - 1
            if candidates.bit_count() + len(chosen) + 1 >= 8:
                pending.append(((*chosen, p), candidates & adjacent[p]))
    raise ValueError("frame enumeration exhausted its node budget")


def permutation(labels, pair):
    need(type(pair) is list and len(pair) == 2, "generator shape")
    need(
        all(type(v) is int and 0 < v < 512 and v.bit_count() % 2 == 0 for v in pair),
        "even nonzero transvection vectors",
    )
    index = {q: i for i, q in enumerate(labels)}
    transformed = []
    for value in labels:
        for v in pair:
            value ^= v if (value & v).bit_count() % 2 else 0
        need(value in index, "generator must preserve source labels")
        transformed.append(index[value])
    need(sorted(transformed) == list(range(112)), "generator bijection")
    return transformed


def components(labels, frames, pairs):
    need(len(frames) == 4032 and len(set(frames)) == 4032, "complete distinct census")
    need(type(pairs) is list and len(pairs) == 7, "seven generators")
    lookup = {f: i for i, f in enumerate(frames)}
    parent = list(range(4032))

    def leader(i):
        for _ in range(4032):
            if parent[i] == i:
                return i
            parent[i] = parent[parent[i]]
            i = parent[i]
        raise ValueError("component depth budget")

    for pair in pairs:
        perm = permutation(labels, pair)
        for i, frame in enumerate(frames):
            image = tuple(sorted(perm[p] for p in frame))
            need(image in lookup, "generator frame image")
            a, b = leader(i), leader(lookup[image])
            if a != b:
                parent[b] = a
    groups = {}
    for i, frame in enumerate(frames):
        groups.setdefault(leader(i), []).append(frame)
    result = sorted(groups.values(), key=len)
    need([len(g) for g in result] == [448, 3584], "two orbit sizes")
    return result


def packing(cert, labels):
    groups = cert["packing_13"]
    need(type(groups) is list and len(groups) == 13, "thirteen packing groups")
    need(all(type(g) is list and len(g) == 8 for g in groups), "eight ports per group")
    flat = [p for group in groups for p in group]
    need(all(type(p) is int and 0 <= p < 112 for p in flat), "packing port range")
    need(len(set(flat)) == 104, "disjoint packing ports")
    for group in groups:
        for a in group:
            for b in group:
                need(
                    (labels[a] & labels[b]).bit_count() % 2 == int(a == b),
                    "packing Gram",
                )


def check_representatives(cert, orbits):
    special, ordinary = orbits
    need(tuple(cert["special_representative"]) in special, "special representative")
    need(tuple(cert["ordinary_representative"]) in ordinary, "ordinary representative")


def rejection_controls(cert, labels, source, frames, orbits):
    bad = copy.deepcopy(cert)
    bad["packing_13"][0][0] = bad["packing_13"][0][1]
    swapped = copy.deepcopy(cert)
    swapped["ordinary_representative"] = cert["special_representative"]
    cases = [
        ("duplicate_packing_port", lambda: packing(bad, labels)),
        ("changed_source", lambda: source_labels(source + b"\n")),
        ("odd_transvection", lambda: permutation(labels, [1, 48])),
        ("nonpreserving_transvection", lambda: permutation(labels, [3, 6])),
        (
            "omitted_frame",
            lambda: components(labels, frames[:-1], cert["transvection_pairs"]),
        ),
        ("wrong_orbit_representative", lambda: check_representatives(swapped, orbits)),
    ]
    for name, action in cases:
        try:
            action()
        except ValueError:
            continue
        raise ValueError("accepted control " + name)
    return [name for name, _ in cases]


def cover_input(columns, frames, fixed=(), budget=60_000_000):
    return (
        f"{columns} {len(frames)} {len(fixed)} {budget}\n"
        + " ".join(map(str, fixed))
        + "\n"
        + "\n".join(" ".join(map(str, f)) for f in frames)
        + "\n"
    )


def run_native(binary, data, timeout=540):
    process = subprocess.run(
        [str(binary)],
        input=data,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=True,
    )
    result = json.loads(process.stdout)
    need(set(result) == {"status", "nodes", "rows"}, "native result shape")
    need(result["status"] in ("SAT", "UNSAT", "UNKNOWN"), "native verdict")
    need(
        type(result["nodes"]) is int and 0 <= result["nodes"] <= 60_000_001,
        "native node bound",
    )
    return result


def tiny_controls(binary):
    rng = random.Random(20261017)
    for case in range(32):
        width = 16 if case % 2 == 0 else 24
        rows = []
        for _ in range(3):
            ports = list(range(width))
            rng.shuffle(ports)
            for start in range(0, width, 8):
                if rng.randrange(4):
                    rows.append(tuple(sorted(ports[start : start + 8])))
        if not rows:
            rows = [tuple(range(8))]
        masks = [sum(1 << p for p in row) for row in rows]
        possible = False
        for subset in range(1 << len(rows)):
            union, disjoint = 0, True
            for i, mask in enumerate(masks):
                if subset >> i & 1:
                    disjoint = disjoint and not (union & mask)
                    union |= mask
            possible |= disjoint and union == (1 << width) - 1
        got = run_native(binary, cover_input(width, rows, budget=10_000))
        need(
            got["status"] == ("SAT" if possible else "UNSAT"),
            "complete tiny subset oracle disagreement",
        )


def native_controls(binary, cert):
    flat = sorted(p for f in cert["packing_13"] for p in f)
    remap = {p: i for i, p in enumerate(flat)}
    positive = [tuple(remap[p] for p in f) for f in cert["packing_13"]]
    result = run_native(binary, cover_input(104, positive))
    need(
        result["status"] == "SAT" and sorted(result["rows"]) == list(range(13)),
        "known thirteen-frame cover control",
    )
    partial = run_native(binary, cover_input(16, [tuple(range(8))]))
    need(partial["status"] == "UNSAT", "uncovered-column control")
    unknown = run_native(binary, cover_input(104, positive, budget=0))
    need(unknown["status"] == "UNKNOWN", "zero budget is not UNSAT")
    for malformed in (cover_input(8, [(0,) * 8]), "113 1 0 1\n"):
        process = subprocess.run(
            [str(binary)],
            input=malformed,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        need(
            process.returncode == 2 and not process.stdout,
            "reject malformed native input",
        )
    tiny_controls(binary)
    return [
        "packing13_SAT",
        "uncovered_column_UNSAT",
        "budget_UNKNOWN",
        "duplicate_column_rejected",
        "oversized_input_rejected",
        "complete_subset_oracle32",
    ]


def exclusion(binary, frames, fixed):
    answer = run_native(binary, cover_input(112, frames, (frames.index(tuple(fixed)),)))
    need(
        answer["status"] == "UNSAT" and answer["rows"] == [], "complete UNSAT required"
    )
    return answer["nodes"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    path = ROOT / SOURCE
    need(path.stat().st_size <= 4_000_000, "source size")
    source = path.read_bytes()
    labels = source_labels(source)
    need((HERE / "CERTIFICATE.json").stat().st_size < 100_000, "certificate size")
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes())
    need(cert["schema_version"] == 1, "certificate version")
    packing(cert, labels)
    frames = frames_from_labels(labels)
    orbits = components(labels, frames, cert["transvection_pairs"])
    check_representatives(cert, orbits)
    controls = rejection_controls(cert, labels, source, frames, orbits)
    compiler = shutil.which(os.environ.get("CXX", "c++"))
    need(compiler is not None, "C++20 compiler required")
    with tempfile.TemporaryDirectory(prefix="p112-frames-", dir=args.work_root) as work:
        binary = Path(work) / "dlx"
        subprocess.run(
            [compiler, *FLAGS, str(HERE / "dlx.cpp"), "-o", str(binary)],
            check=True,
            timeout=60,
        )
        controls += native_controls(binary, cert)
        special_nodes = exclusion(binary, orbits[0], cert["special_representative"])
        ordinary_nodes = exclusion(binary, frames, cert["ordinary_representative"])
    result = {
        "source_sha256": SOURCE_SHA,
        "complete_eight_frames": len(frames),
        "frame_census_sha256": hashlib.sha256(
            "\n".join(",".join(map(str, f)) for f in frames).encode()
        ).hexdigest(),
        "orbit_sizes": [len(g) for g in orbits],
        "packing_number": 13,
        "fourteen_partition": "UNSAT",
        "special_case_nodes": special_nodes,
        "ordinary_case_nodes": ordinary_nodes,
        "colouring_channel_floor": 30,
        "controls": controls,
    }
    if args.output:
        need(
            not args.output.exists() and not args.output.resolve().is_relative_to(HERE),
            "new external output required",
        )
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(
            result == json.loads((HERE / "RESULT.json").read_bytes()),
            "receipt mismatch",
        )
    print(json.dumps(result, sort_keys=True))
    print("PASS_P112_FRAME_PARTITION maximum13 no_new_kappa")


if __name__ == "__main__":
    main()
