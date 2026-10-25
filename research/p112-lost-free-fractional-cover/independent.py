#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.

Independent stdlib dense-vector check of the source-bound fractional cover.

Imports no discovery, package or predecessor code. Does not enumerate frames,
execute a physical decoder, certify a solver bound, or reprove source admission.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
import tarfile
from fractions import Fraction

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[1] / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
CANDIDATE = HERE / "COVER.json"
RAW_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"

class Rejected(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise Rejected(message)

def integer(value, low, high):
    require(type(value) is int and low <= value <= high, "strict integer range")
    return value

def vector(value):
    integer(value, 0, 511)
    return [(value // (2 ** k)) % 2 for k in range(9)]

def dot(left, right):
    require(len(left) == len(right) == 9, "nine coordinates")
    require(all(type(x) is int and x in (0, 1) for x in left + right), "binary coordinates")
    return sum(x * y for x, y in zip(left, right)) % 2

def rank(rows):
    matrix = [list(row) for row in rows]
    require(all(len(row) == 9 for row in matrix), "nine-column rank")
    pivot = 0
    for column in range(9):
        selected = next((j for j in range(pivot, len(matrix)) if matrix[j][column]), None)
        if selected is None:
            continue
        matrix[pivot], matrix[selected] = matrix[selected], matrix[pivot]
        for j in range(len(matrix)):
            if j != pivot and matrix[j][column]:
                matrix[j] = [(x + y) % 2 for x, y in zip(matrix[j], matrix[pivot])]
        pivot += 1
    return pivot

def labels_from_raw(data):
    require(type(data) is dict and integer(data.get("ports"), 112, 112) == 112, "source port count")
    recipes = data.get("recipes")
    require(type(recipes) is list and len(recipes) == 112, "source recipes")
    labels = [None] * 112
    for record in recipes:
        require(type(record) is dict, "source record")
        i = integer(record.get("port"), 0, 111)
        require(labels[i] is None, "duplicate source port")
        labels[i] = vector(record.get("q"))
    require(all(x is not None for x in labels), "complete source ports")
    require(len({tuple(x) for x in labels}) == 112, "distinct labels")
    require(all(dot(x, x) == 1 for x in labels), "source norm one")
    require(rank(labels) == 9, "ambient rank nine")
    return labels

def check_cover(data, labels):
    require(type(data) is dict, "certificate object")
    integer(data.get("schema_version"), 1, 1)
    integer(data.get("dimension"), 9, 9)
    integer(data.get("port_count"), 112, 112)
    integer(data.get("lost_free_bound"), 56, 56)
    require(type(data.get("total_weight")) is str and Fraction(data["total_weight"]) == 14, "declared total")
    frames = data.get("frames")
    require(type(frames) is list and 1 <= len(frames) <= 112, "compact nonempty frame list")
    coverage = [Fraction(0) for _ in range(112)]
    total = Fraction(0)
    seen = set()
    for record in frames:
        require(type(record) is dict, "frame object")
        ports = record.get("ports")
        require(type(ports) is list and len(ports) == 8, "eight frame ports")
        for i in ports:
            integer(i, 0, 111)
        require(len(set(ports)) == 8, "distinct frame ports")
        key = tuple(sorted(ports))
        require(key not in seen, "distinct frame records")
        seen.add(key)
        rows = [labels[i] for i in ports]
        for i, left in enumerate(rows):
            for j, right in enumerate(rows):
                require(dot(left, right) == int(i == j), "Gram I8")
        require(rank(rows) == 8, "frame dense rank eight")
        value = record.get("weight")
        require(type(value) is str, "rational text")
        try:
            weight = Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise Rejected("rational weight") from exc
        require(weight > 0, "positive rational weight")
        total += weight
        for i in ports:
            coverage[i] += weight
    require(all(x == 1 for x in coverage), "exact per-port coverage one")
    require(total == 14, "exact total fourteen")
    require(4 * total == 56, "lost-free cover bound")
    return {"frame_count": len(frames), "port_count": 112, "ambient_dimension": 9,
            "label_rank": rank(labels), "frame_ranks": [8], "gram_entries": len(frames) * 64,
            "exact_coverage": "1", "exact_total_weight": str(total), "lost_free_bound": 56,
            "fixed_tariff_cost_lower_bound": 72 + 2 * (112 - 56)}

def check_plane_pairs(pairs):
    require(type(pairs) is list and len(pairs) > 0, "plane list")
    rows = []
    for pair in pairs:
        require(type(pair) is list and len(pair) == 2, "plane pair")
        q, r = (vector(x) for x in pair)
        require(dot(q, q) == dot(r, r) == 1 and dot(q, r) == 0, "nondegenerate orthonormal plane")
        rows.extend((q, r))
    for i, left in enumerate(rows):
        for j, right in enumerate(rows):
            require(dot(left, right) == int(i == j), "pairwise orthogonal planes")
    require(rank(rows) == len(rows), "independent plane basis")
    require(2 * len(pairs) <= 9, "ambient plane capacity")
    return len(pairs)

def expect_rejection(label, callback):
    try:
        callback()
    except Rejected as exc:
        return {"name": label, "status": "REJECTED", "reason": str(exc)}
    raise Rejected("negative control accepted: " + label)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def source_bytes():
    archive_bytes = ARCHIVE.read_bytes()
    require(sha(archive_bytes) == ARCHIVE_SHA, "selected archive hash")
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        matches = [entry for entry in archive if entry.name == MEMBER]
        require(len(matches) == 1 and matches[0].isreg(), "one regular selected member")
        require(matches[0].size < 2**21, "bounded selected member")
        return archive.extractfile(matches[0]).read()

def main():
    started = time.monotonic()
    raw_bytes = source_bytes()
    candidate_bytes = CANDIDATE.read_bytes()
    require(sha(raw_bytes) == RAW_SHA, "pinned raw source hash")
    labels = labels_from_raw(json.loads(raw_bytes))
    candidate = json.loads(candidate_bytes)
    result = check_cover(candidate, labels)
    controls = []
    def mutate(name, change):
        altered = copy.deepcopy(candidate)
        change(altered)
        controls.append(expect_rejection(name, lambda: check_cover(altered, labels)))
    mutate("changed rational weight", lambda x: x["frames"][0].update(weight=str(Fraction(x["frames"][0]["weight"]) + Fraction(1, 1000003))))
    mutate("dropped frame", lambda x: x["frames"].pop())
    mutate("duplicate frame port", lambda x: x["frames"][0]["ports"].__setitem__(1, x["frames"][0]["ports"][0]))
    # Force a distinct but nonorthogonal raw label into the first frame.
    first = candidate["frames"][0]["ports"]
    bad = next(i for i in range(112) if i not in first and dot(labels[i], labels[first[0]]) == 1)
    mutate("bad Gram frame", lambda x: x["frames"][0]["ports"].__setitem__(1, bad))
    mutate("out-of-range port", lambda x: x["frames"][0]["ports"].__setitem__(0, 112))
    mutate("boolean port", lambda x: x["frames"][0]["ports"].__setitem__(0, False))
    mutate("boolean dimension", lambda x: x.update(dimension=True))
    mutate("boolean weight", lambda x: x["frames"][0].update(weight=True))
    mutate("negative weight", lambda x: x["frames"][0].update(weight="-1"))
    mutate("zero weight", lambda x: x["frames"][0].update(weight="0"))
    mutate("zero denominator", lambda x: x["frames"][0].update(weight="1/0"))
    # Four explicit independent orthonormal planes exist in F2^9.
    positive_planes = [[1, 2], [4, 8], [16, 32], [64, 128]]
    require(check_plane_pairs(positive_planes) == 4, "four-plane positive fixture")
    controls.append(expect_rejection("degenerate plane q equals r", lambda: check_plane_pairs([[1, 1]])))
    controls.append(expect_rejection("isotropic plane direction", lambda: check_plane_pairs([[1, 6]])))
    controls.append(expect_rejection("shared plane direction", lambda: check_plane_pairs([[1, 2], [4, 2]])))
    controls.append(expect_rejection("boolean plane direction", lambda: check_plane_pairs([[True, 2]])))
    controls.append(expect_rejection("out-of-range plane direction", lambda: check_plane_pairs([[1, 512]])))
    controls.append(expect_rejection("five claimed orthogonal planes", lambda: check_plane_pairs(positive_planes + [[256, 1]])))
    # Raw schema controls ensure source q/port booleans are not silently integers.
    changed_raw = json.loads(raw_bytes)
    changed_raw["recipes"][0]["q"] = True
    controls.append(expect_rejection("boolean source label", lambda: labels_from_raw(changed_raw)))
    changed_raw2 = json.loads(raw_bytes)
    changed_raw2["recipes"][0]["port"] = False
    controls.append(expect_rejection("boolean source port", lambda: labels_from_raw(changed_raw2)))
    require(source_bytes() == raw_bytes and CANDIDATE.read_bytes() == candidate_bytes, "inputs unchanged")
    result.update({
        "status": "PASS_INDEPENDENT_COMPACT_FRACTIONAL_COVER",
        "pid": os.getpid(),
        "runtime_seconds": time.monotonic() - started,
        "maxrss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "command": [sys.executable, "-I", "-O", "-Werror", "-B", str(Path(__file__).resolve())],
        "hashes": {"raw_sha256": sha(raw_bytes), "candidate_sha256": sha(candidate_bytes),
                   "checker_sha256": sha(Path(__file__).read_bytes())},
        "negative_controls": controls,
        "negative_control_count": len(controls),
        "inputs_unchanged": True,
        "proof_scope": "Exact nonnegative cover plus the orthonormal-plane dimension argument in F2^9; fixed tariff 72+2*(112-|S|). No census, source isometry, maximum-S theorem, physical dirty execution, supplier or kappa claim."
    })
    print("PASS_INDEPENDENT_COMPACT_FRACTIONAL_COVER frames=112 controls=" + str(len(controls)) + " no_new_kappa")

if __name__ == "__main__":
    main()
