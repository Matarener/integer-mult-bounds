#!/usr/bin/env python3
"""Independent exact geometric premises for the no-axial three-mark floor.

Uses explicit annihilator sets in F2^9, not Gaussian elimination or producer
imports. The quantified invoice deduction is a written argument, not this replay.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {
    "research/p112-rational-decoder-gate/CANDIDATE.json":
        "dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b",
    "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json":
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check(repo):
    objects = []
    for path, digest in PINS.items():
        raw = (repo / path).read_bytes()
        need(sha256(raw).hexdigest() == digest, "scientific input pin: " + path)
        objects.append(json.loads(raw))
    candidate, data = objects
    groups = candidate["groups"]
    marks = candidate["factor_supports"]
    labels = {r["port"]: r["q"] for r in data["recipes"]}
    owner = {p: g for g, ports in enumerate(groups) for p in ports}
    need(sorted(p for g in groups for p in g) == list(range(112)), "group partition")
    need(sorted(p for m in marks for p in m) == list(range(112)), "mark partition")
    need(set(labels) == set(range(112)) and len(data["recipes"]) == 112,
         "unique physical labels")
    need(all(0 < v < 512 for v in labels.values()), "nine-bit nonzero labels")
    triads = [g for g in range(len(groups)) if len(groups[g]) == 3]

    def dot(a, b):
        return (a & b).bit_count() % 2

    need(len(triads) == 37, "triad count")
    need(all(dot(labels[p], labels[q]) == int(p == q)
             for g in triads for p in groups[g] for q in groups[g]),
         "triad orthonormality")
    # Bit v represents the ambient vector v, including zero. Intersections of
    # annihilators correspond to spans of unions. Their size is 2^(9-rank).
    annihilators = {
        g: sum(1 << v for v in range(512)
               if all(dot(v, labels[p]) == 0 for p in groups[g]))
        for g in range(len(groups))
    }

    def union_rank(group_indices):
        intersection = (1 << 512) - 1
        for g in group_indices:
            intersection &= annihilators[g]
        cardinality = intersection.bit_count()
        need(cardinality > 0 and cardinality & (cardinality - 1) == 0,
             "annihilator must be a subspace")
        return 9 - (cardinality.bit_length() - 1)

    pair_counts = Counter(union_rank(gs) for gs in combinations(triads, 2))
    triple_counts = Counter(union_rank(gs) for gs in combinations(triads, 3))
    ordinary = [m for m in marks if len(m) == 2
                and all(len(groups[owner[p]]) == 3 for p in m)]
    roles = sorted({tuple(sorted(owner[p] for p in m)) for m in ordinary})
    need(len(ordinary) == 53 and len(roles) == 18, "ordinary mark/role counts")
    need(all(len(set(r)) == 2 for r in roles)
         and len({g for r in roles for g in r}) == 36, "disjoint paired roles")
    need(all(union_rank(r) == 6 for r in roles), "paired-role dimension")
    need(all(dot(labels[p], labels[q]) == 0
             for a, b in roles for p in groups[a] for q in groups[b]),
         "paired triads are mutually orthogonal")
    # Each ordinary self-rectangle is thus two orthonormal triads: tariff six.
    role_pair_counts = Counter(union_rank(a + b) for a, b in combinations(roles, 2))
    need(pair_counts == {4: 2, 5: 59, 6: 605}, "all physical pair ranks")
    need(triple_counts == {6: 31, 7: 900, 8: 4431, 9: 2408},
         "all physical triple ranks")
    need(role_pair_counts == {8: 11, 9: 142}, "all paired-role union ranks")
    return {
        "status": "PASS_INDEPENDENT_NO_AXIAL_GEOMETRY",
        "method": "Exact annihilator sets; no elimination or producer imports",
        "scientific_inputs": PINS,
        "physical_triads": len(triads),
        "triad_pair_checks": sum(pair_counts.values()),
        "triad_pair_ranks": dict(sorted(pair_counts.items())),
        "triad_triple_checks": sum(triple_counts.values()),
        "triad_triple_ranks": dict(sorted(triple_counts.items())),
        "ordinary_marks": len(ordinary),
        "paired_roles": roles,
        "paired_role_union_checks": sum(role_pair_counts.values()),
        "paired_role_union_ranks": dict(sorted(role_pair_counts.items())),
        "canonical_ordinary_tariff": 6,
        "scope": "Finite geometry only; arbitrary-coefficient cost >= 12+n is a written proof",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = check(args.repo_root)
    payload = json.dumps(result, indent=2) + "\n"
    receipt = HERE / "INDEPENDENT-RESULT.json"
    if args.write_receipt:
        receipt.write_text(payload, encoding="utf-8", newline="\n")
    else:
        need(receipt.read_text(encoding="utf-8") == payload, "receipt mismatch")
    print(json.dumps({k: result[k] for k in
                     ("status", "triad_pair_checks", "triad_triple_checks",
                      "paired_role_union_checks", "canonical_ordinary_tariff")}))


if __name__ == "__main__":
    main()
