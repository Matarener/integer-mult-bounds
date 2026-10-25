#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate dense-coordinate census, BFS symmetry check and active-row exhaustion."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from collections import deque
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
DIGEST = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"


def insist(value, reason):
    if not value:
        raise ValueError(reason)


def vectors():
    path = REPO / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
    insist(path.stat().st_size < 4_000_000, "input size")
    raw = path.read_bytes()
    insist(hashlib.sha256(raw).hexdigest() == DIGEST, "literal source bytes")
    rows = json.loads(raw)["recipes"]
    insist(sorted(r["port"] for r in rows) == list(range(112)), "port enumeration")
    return [
        tuple((r["q"] >> k) & 1 for k in range(9))
        for r in sorted(rows, key=lambda r: r["port"])
    ]


def gram(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True)) % 2


def enumerate_dense(vs):
    matrix = [[gram(v, w) for w in vs] for v in vs]
    insist(all(matrix[i][i] == 1 for i in range(112)), "odd self-pairings")
    found, todo = [], [((), list(range(112)))]
    for _ in range(200_000):
        if not todo:
            insist(len(found) == 4032, "complete independent frame count")
            return sorted(found), matrix
        prefix, options = todo.pop()
        if len(prefix) == 8:
            found.append(prefix)
            insist(len(found) <= 4032, "census capacity")
            continue
        for at, p in enumerate(options):
            if len(prefix) + len(options) - at >= 8:
                todo.append(
                    ((*prefix, p), [j for j in options[at + 1 :] if not matrix[p][j]])
                )
    raise ValueError("independent census incomplete")


def actions(vs, pairs, matrix):
    lookup = {v: i for i, v in enumerate(vs)}
    result = []
    insist(len(pairs) == 7, "generator count")
    for pair in pairs:
        insist(
            len(pair) == 2 and all(type(k) is int and 0 < k < 512 for k in pair),
            "generator input",
        )
        images = []
        for v in vs:
            w = v
            for integer in pair:
                t = tuple((integer >> k) & 1 for k in range(9))
                insist(gram(t, t) == 0, "transvection isotropy")
                coefficient = gram(w, t)
                w = tuple((a + coefficient * b) % 2 for a, b in zip(w, t, strict=True))
            insist(w in lookup, "source-preserving transformation")
            images.append(lookup[w])
        insist(sorted(images) == list(range(112)), "permutation")
        insist(
            all(
                matrix[i][j] == matrix[images[i]][images[j]]
                for i in range(112)
                for j in range(112)
            ),
            "full Gram preservation",
        )
        result.append(images)
    return result


def bfs(frames, permutations, initial):
    domain = set(frames)
    start = tuple(initial)
    insist(start in domain, "orbit seed")
    seen, queue = {start}, deque([start])
    for _ in range(4032):
        if not queue:
            return sorted(seen)
        frame = queue.popleft()
        for perm in permutations:
            image = tuple(sorted(perm[p] for p in frame))
            insist(image in domain, "orbit image is a frame")
            if image not in seen:
                seen.add(image)
                queue.append(image)
    raise ValueError("orbit traversal capacity")


def native(binary, width, rows, fixed=(), budget=60_000_000):
    text = f"{width} {len(rows)} {len(fixed)} {budget}\n"
    text += " ".join(str(i) for i in fixed) + "\n"
    text += "\n".join(" ".join(str(p) for p in f) for f in rows) + "\n"
    run = subprocess.run(
        [str(binary)],
        input=text,
        capture_output=True,
        text=True,
        timeout=540,
        check=True,
    )
    receipt = json.loads(run.stdout)
    insist(set(receipt) == {"status", "nodes", "rows"}, "native receipt")
    insist(receipt["status"] in ("SAT", "UNSAT", "UNKNOWN"), "native status")
    return receipt


def native_checks(binary, cert, special, frames):
    packing = cert["packing_13"]
    ports = sorted(p for f in packing for p in f)
    rename = {p: i for i, p in enumerate(ports)}
    small = [tuple(rename[p] for p in f) for f in packing]
    sat = native(binary, 104, small)
    insist(
        sat["status"] == "SAT" and sorted(sat["rows"]) == list(range(13)),
        "source13 positive cover",
    )
    insist(
        native(binary, 104, small, budget=0)["status"] == "UNKNOWN", "budget control"
    )
    # No fixed row in this separate all-special exclusion.
    first = native(binary, 112, special)
    second = native(
        binary, 112, frames, (frames.index(tuple(cert["ordinary_representative"])),)
    )
    insist(first["status"] == second["status"] == "UNSAT", "exhaustion required")
    insist(first["rows"] == second["rows"] == [], "no witness in exclusion")
    expected = json.loads((BASE / "RESULT.json").read_bytes())
    insist(second["nodes"] == expected["ordinary_case_nodes"], "independent tree count")
    return first["nodes"], second["nodes"]


def reduction(cert):
    vs = vectors()
    frames, matrix = enumerate_dense(vs)
    packing = cert["packing_13"]
    insist(
        len(packing) == 13 and len({p for f in packing for p in f}) == 104,
        "packing size and disjointness",
    )
    insist(all(tuple(f) in set(frames) for f in packing), "packing frames")
    permutations = actions(vs, cert["transvection_pairs"], matrix)
    special = bfs(frames, permutations, cert["special_representative"])
    ordinary = bfs(frames, permutations, cert["ordinary_representative"])
    insist(len(special) == 448 and len(ordinary) == 3584, "independent orbit sizes")
    insist(
        set(special).isdisjoint(ordinary)
        and set(special) | set(ordinary) == set(frames),
        "complete orbit partition",
    )
    census_bytes = "\n".join(",".join(map(str, f)) for f in frames).encode()
    expected = json.loads((BASE / "RESULT.json").read_bytes())
    insist(
        hashlib.sha256(census_bytes).hexdigest() == expected["frame_census_sha256"],
        "independently enumerated frame set",
    )
    return special, frames


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path)
    args = parser.parse_args()
    insist((BASE / "CERTIFICATE.json").stat().st_size < 100_000, "certificate size")
    cert = json.loads((BASE / "CERTIFICATE.json").read_bytes())
    special, frames = reduction(cert)
    compiler = shutil.which(os.environ.get("CXX", "c++"))
    insist(compiler is not None, "C++20 compiler")
    with tempfile.TemporaryDirectory(
        prefix="p112-independent-", dir=args.work_root
    ) as work:
        binary = Path(work) / "active"
        subprocess.run(
            [
                compiler,
                "-std=c++20",
                "-O3",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Wshadow",
                "-Wconversion",
                "-Werror",
                str(BASE / "independent.cpp"),
                "-o",
                str(binary),
            ],
            check=True,
            timeout=60,
        )
        small, full = native_checks(binary, cert, special, frames)
    print(
        json.dumps(
            {
                "all_special_unfixed_nodes": small,
                "ordinary_fixed_nodes": full,
                "packing_number": 13,
                "orbit_sizes": [448, 3584],
            },
            sort_keys=True,
        )
    )
    print("PASS_INDEPENDENT_P112_FRAME_PARTITION maximum13 no_new_kappa")


if __name__ == "__main__":
    main()
