#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite corroboration of the concave-invoice antichain proof.

Produced by Nick Petalas. Standard library only; no predecessor replay.
The all-m theorem is proved in README.md. This executable bounds m by 11.
"""

from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys


MAX_M = 11
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def invoice(m, mask):
    """Construct a complete synthetic invoice, including its common target."""
    require(type(m) is int and 1 <= m <= MAX_M, "m must be in 1..11")
    require(type(mask) is int and 0 <= mask < 1 << m, "invalid subset mask")
    paid = {}
    for i in range(1, m + 1):
        ranks = (2 * i - 1, 2 * i + 1) if mask >> (i - 1) & 1 else (2 * i, 2 * i)
        for rank in ranks:
            key = str(rank)
            paid[key] = paid.get(key, 0) + 1
    mass = 2 * m * (m + 1)
    return {
        "schema": "integer-mult-recursive-invoice/v1",
        "contract": {
            "model": "mixed-target-unnormalized-power-v1",
            "rank_semantics": "synthetic H_r cost; all paid jobs and target debits included",
            "ambient_rank": mass,
            "boundary": "common synthetic target, no physical realization claimed",
        },
        "paid": paid,
        "targets": {str(mass): 1},
    }


def check_invariants(value, m):
    """Check conserved quantities without reconstructing the pair choices."""
    mass = 2 * m * (m + 1)
    require(value["schema"] == "integer-mult-recursive-invoice/v1", "wrong schema")
    require(value["contract"]["ambient_rank"] == mass, "wrong ambient rank")
    paid = value["paid"]
    require(0 < len(paid) <= 2 * m, "invalid support size")
    require(all(type(c) is int and c > 0 for c in paid.values()), "invalid count")
    require(all(1 <= int(r) <= 2 * m + 1 for r in paid), "invalid rank")
    require(sum(paid.values()) == 2 * m, "call count changed")
    require(sum(int(r) * c for r, c in paid.items()) == mass, "paid mass changed")
    require(value["targets"] == {str(mass): 1}, "target debit changed")


def hinge_twice(value, doubled_cap):
    """Evaluate twice the signed bill at the half-integral hinge cap."""
    require(type(doubled_cap) is int and doubled_cap >= 0, "invalid hinge cap")
    paid = sum(c * min(2 * int(r), doubled_cap) for r, c in value["paid"].items())
    target = sum(c * min(2 * int(r), doubled_cap) for r, c in value["targets"].items())
    return paid - target


def check_counter_tariff(left, right, cap, gap):
    """Certify a tariff under which the left signed invoice is more expensive."""
    require(left["contract"] == right["contract"], "different boundary contracts")
    require(type(cap) is int and cap > 0, "counter-tariff cap must be positive")
    require(type(gap) is int and gap > 0, "counter-tariff gap must be positive")
    observed = hinge_twice(left, 2 * cap) - hinge_twice(right, 2 * cap)
    require(observed == 2 * gap, "false counter-tariff gap")


def check_cube(m):
    """Enumerate every ordered pair and all half-integral support intervals."""
    members = [invoice(m, mask) for mask in range(1 << m)]
    baseline = members[0]
    coords = []
    for mask, value in enumerate(members):
        check_invariants(value, m)
        row = []
        for cap2 in range(4 * m + 3):
            observed = hinge_twice(value, cap2)
            delta = observed - hinge_twice(baseline, cap2)
            expected = -sum(max(0, 2 - abs(cap2 - 4 * i))
                            for i in range(1, m + 1) if mask >> (i - 1) & 1)
            require(delta == expected, "disjoint tent identity failed")
            row.append(observed)
        coords.append(row)
    pairs = 0
    for left, row in enumerate(coords):
        for right, other in enumerate(coords):
            observed = all(a <= b for a, b in zip(row, other, strict=True))
            require(observed == (right & ~left == 0), "subset-order theorem failed")
            pairs += 1
    return {"m": m, "members": len(members), "ordered_pairs": pairs,
            "half_grid_values": len(members) * (4 * m + 3)}


def layer_masks(m):
    return [mask for mask in range(1 << m) if mask.bit_count() == m // 2]


def check_layer_inventory(m, masks):
    require(len(masks) == comb(m, m // 2), "incomplete layer")
    require(len(set(masks)) == len(masks), "duplicate layer member")
    require(all(type(mask) is int and 0 <= mask < 1 << m
                and mask.bit_count() == m // 2 for mask in masks), "wrong layer")


def check_layer(m):
    """Stream two literal signed-bill counter-tariffs for every unordered pair."""
    masks = layer_masks(m)
    check_layer_inventory(m, masks)
    members = [invoice(m, mask) for mask in masks]
    for value in members:
        check_invariants(value, m)
    digest = sha256()
    pairs = 0
    for a, b in combinations(range(len(masks)), 2):
        left_only, right_only = masks[a] & ~masks[b], masks[b] & ~masks[a]
        require(left_only > 0 and right_only > 0, "equal-size distinct sets are comparable")
        left_cap = 2 * (right_only & -right_only).bit_length()
        right_cap = 2 * (left_only & -left_only).bit_length()
        check_counter_tariff(members[a], members[b], left_cap, 1)
        check_counter_tariff(members[b], members[a], right_cap, 1)
        certificate = [masks[a], masks[b], left_cap, right_cap, 1, 1]
        digest.update((json.dumps(certificate, separators=(",", ":")) + "\n").encode())
        pairs += 1
    require(pairs == len(masks) * (len(masks) - 1) // 2, "pair enumeration incomplete")
    return {"m": m, "members": len(masks), "paid_calls": 2 * m,
            "paid_rank_mass": 2 * m * (m + 1), "paid_rank_bound": 2 * m + 1,
            "unordered_pairs": pairs, "counter_tariffs": 2 * pairs,
            "counter_tariff_sha256": digest.hexdigest()}


def rejected(operation, *args):
    try:
        operation(*args)
    except ValueError:
        return 1
    raise RuntimeError("negative control was accepted")


def check_controls():
    count = 0
    for m, mask in ((0, 0), (12, 0), (True, 0), (2, -1), (2, 4), (2, True)):
        count += rejected(invoice, m, mask)
    a, b = invoice(2, 1), invoice(2, 2)
    check_counter_tariff(a, b, 4, 1)
    check_counter_tariff(b, a, 2, 1)
    for cap, gap in ((2, 1), (4, 2), (0, 1), (4, 0), (4, -1)):
        count += rejected(check_counter_tariff, a, b, cap, gap)
    wrong_target = invoice(2, 1)
    wrong_target["targets"] = {}
    count += rejected(check_invariants, wrong_target, 2)
    wrong_mass = invoice(2, 1)
    amount = wrong_mass["paid"].pop("1")
    wrong_mass["paid"]["2"] = amount
    count += rejected(check_invariants, wrong_mass, 2)
    changed_boundary = invoice(2, 2)
    changed_boundary["contract"]["boundary"] = "different consumer"
    count += rejected(check_counter_tariff, a, changed_boundary, 4, 1)
    masks = layer_masks(4)
    count += rejected(check_layer_inventory, 4, masks[:-1])
    count += rejected(check_layer_inventory, 4, masks[:-1] + [masks[0]])
    count += rejected(check_layer_inventory, 4, masks[:-1] + [0])
    return count


def main():
    require(len(sys.argv) == 1, "this read-only verifier takes no arguments")
    cubes = [check_cube(m) for m in range(1, 8)]
    layers = [check_layer(m) for m in (10, 11)]
    controls = check_controls()
    root = Path(__file__).resolve().parent
    hashes = {name: sha256((root / name).read_bytes()).hexdigest() for name in PACKAGE_FILES}
    receipt = {"status": "PASS_CONCAVE_INVOICE_ANTICHAINS", "claim_type": "scoped proof",
               "finite_corroboration_only": True, "source_sha256": hashes,
               "cubes": cubes, "layers": layers, "rejection_controls": controls}
    receipt["totals"] = {"cube_members": sum(row["members"] for row in cubes),
                         "cube_ordered_pairs": sum(row["ordered_pairs"] for row in cubes),
                         "layer_members": sum(row["members"] for row in layers),
                         "layer_pairs": sum(row["unordered_pairs"] for row in layers),
                         "counter_tariffs": sum(row["counter_tariffs"] for row in layers)}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
