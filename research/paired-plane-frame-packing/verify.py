#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check an explicit P112 frame packing and its strict plane-mask scalar fit."""

import copy
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
SOURCE_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
PORTS = 112


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path, size_limit):
    require(path.stat().st_size <= size_limit, "input size limit")
    return json.loads(path.read_bytes())


def labels_from_source(data):
    require(hashlib.sha256(data).hexdigest() == SOURCE_SHA, "source hash")
    rows = json.loads(data)["recipes"]
    require(len(rows) == PORTS, "source recipe count")
    require(sorted(row["port"] for row in rows) == list(range(PORTS)), "source ports")
    labels = [row["q"] for row in sorted(rows, key=lambda row: row["port"])]
    require(all(type(q) is int and 0 < q < 512 for q in labels), "nine-bit labels")
    require(len(set(labels)) == PORTS, "distinct labels")
    return labels


def dot(left, right):
    return (left & right).bit_count() % 2


def validate_groups(groups, labels):
    require(type(groups) is list and 1 <= len(groups) <= 56, "group count")
    require(all(type(g) is list and len(g) in (2, 4, 6, 8) for g in groups), "group sizes")
    require(all(type(p) is int for g in groups for p in g), "integer ports")
    require(sorted(p for g in groups for p in g) == list(range(PORTS)), "port partition")
    for group in groups:
        for left in group:
            for right in group:
                require(dot(labels[left], labels[right]) == int(left == right), "Gram I")


def check_certificate(cert, labels):
    require(cert["schema_version"] == 1, "certificate version")
    groups = cert["orthonormal_groups"]
    validate_groups(groups, labels)
    frames = sum(len(group) == 8 for group in groups)
    require(frames == cert["eight_frame_count"] == 13, "frame count")
    remainder = [p for group in groups if len(group) != 8 for p in group]
    require(len(remainder) == 8, "eight-port remainder")
    require(not any(all(dot(labels[a], labels[b]) == 0 for a, b in itertools.combinations(s, 2))
                    for s in itertools.combinations(remainder, 4)), "no remainder four-frame")
    pairs = [group[i:i + 2] for group in groups for i in range(0, len(group), 2)]
    owners = {port: k for k, pair in enumerate(pairs) for port in pair}
    supports = [group[side::2] for group in groups for side in (0, 1)]
    support_owner = {port: k for k, support in enumerate(supports) for port in support}
    orth = [[i != j and all(dot(labels[a], labels[b]) == 0 for a in left for b in right)
             for j, right in enumerate(pairs)] for i, left in enumerate(pairs)]
    forced = 0
    for left in range(PORTS):
        for right in range(PORTS):
            entry = int(support_owner[left] == support_owner[right])
            if left == right or not orth[owners[left]][owners[right]]:
                require(entry == int(left == right), "strict scalar mask")
                forced += 1
    clique = cert["clique_planes"]
    require(type(clique) is list and 1 <= len(clique) <= 56, "clique size")
    require(all(type(v) is int and 0 <= v < 56 for v in clique), "clique vertices")
    require(len(set(clique)) == len(clique), "distinct clique vertices")
    require(all(not orth[u][v] for u, v in itertools.combinations(clique, 2)), "clique edges")
    # The clique forces I_(2*|clique|) in EVERY fit; disjoint supports give
    # this particular fit exactly len(supports) independent rank-one blocks.
    return {
        "ports": PORTS,
        "disjoint_eight_frames": frames,
        "uncovered_after_eight_frames": PORTS - 8 * frames,
        "remainder_orthogonality_edges": sum(dot(labels[a], labels[b]) == 0
                                             for a, b in itertools.combinations(remainder, 2)),
        "remainder_has_orthonormal_four_set": False,
        "group_sizes": sorted(map(len, groups), reverse=True),
        "pairs": len(pairs),
        "forced_scalar_entries": forced,
        "fitting_rank_lower_bound": 2 * len(clique),
        "fitting_rank_upper_bound": len(supports),
        "particular_fit_rank_every_field": len(supports),
        "source_sha256": SOURCE_SHA,
    }


def rejection_controls(cert, labels, source_data):
    mutants = []
    duplicate = copy.deepcopy(cert)
    duplicate["orthonormal_groups"][0][0] = duplicate["orthonormal_groups"][0][1]
    mutants.append(("duplicate_port", duplicate))
    omitted = copy.deepcopy(cert)
    omitted["orthonormal_groups"].pop()
    mutants.append(("omitted_group", omitted))
    wrong_count = copy.deepcopy(cert)
    wrong_count["eight_frame_count"] += 1
    mutants.append(("wrong_frame_count", wrong_count))
    bad_clique = copy.deepcopy(cert)
    bad_clique["clique_planes"].append(bad_clique["clique_planes"][0])
    mutants.append(("duplicate_clique_plane", bad_clique))
    # Preserve the port partition but destroy a Gram-I condition.
    wrong_pair = copy.deepcopy(cert)
    groups = wrong_pair["orthonormal_groups"]
    target = next((k, j) for k in range(1, len(groups)) for j in range(len(groups[k]))
                  if dot(labels[groups[0][0]], labels[groups[k][j]]) == 1)
    k, j = target
    groups[0][1], groups[k][j] = groups[k][j], groups[0][1]
    mutants.append(("nonorthogonal_swap", wrong_pair))
    for name, mutant in mutants:
        try:
            check_certificate(mutant, labels)
        except ValueError:
            continue
        raise ValueError("accepted negative control: " + name)
    try:
        labels_from_source(source_data + b"\n")
    except ValueError:
        return [name for name, _ in mutants] + ["changed_source_bytes"]
    raise ValueError("accepted changed source bytes")


def main():
    source_path = ROOT / SOURCE
    require(source_path.stat().st_size <= 4_000_000, "source size limit")
    source_data = source_path.read_bytes()
    labels = labels_from_source(source_data)
    cert = read_json(HERE / "CERTIFICATE.json", 100_000)
    result = check_certificate(cert, labels)
    result["rejected_controls"] = rejection_controls(cert, labels, source_data)
    expected = read_json(HERE / "RESULT.json", 100_000)
    require(result == expected, "result receipt mismatch")
    print(json.dumps(result, sort_keys=True))
    print("PASS_PAIRED_PLANE_FRAME_PACKING no_new_kappa")


if __name__ == "__main__":
    main()
