"""Finite corroboration and a selected-prime strict-padding witness."""

import json
from hashlib import sha256

from minimum import depth, digit_table, require, select, selected_tables


def census():
    digest = sha256()
    cases = admitted = improved = newly_fitted = 0
    for q in (2, 3):
        for m in (2, 3):
            for w in (1, 2):
                for b in (1, 6):
                    for compatibility in (1, 2):
                        for e in range(1, 257):
                            d = depth(e // w, m, m - 1)
                            strict = digit_table(q, b, compatibility, d)
                            covering = digit_table(
                                q, b, compatibility, d, covering=True
                            )
                            plan = select(e, w, m, m - 1, strict)
                            old = select(e, w, m, m - 1, covering)
                            if plan is not None:
                                admitted += 1
                                newly_fitted += int(old is None)
                                improved += int(old is not None and plan[0] < old[0])
                                require(
                                    old is None or old[0] <= plan[0] + 1,
                                    "one digit bound",
                                )
                            require(
                                old is None or plan is not None,
                                "covering fit preserved",
                            )
                            row = [q, m, w, b, compatibility, e, plan, old]
                            digest.update(
                                json.dumps(row, separators=(",", ":")).encode() + b"\n"
                            )
                            cases += 1
    return {
        "cases": cases,
        "admitted": admitted,
        "improved": improved,
        "newly_fitted": newly_fitted,
        "sha256": digest.hexdigest(),
    }


def selected_witness():
    q = (1 << 127) - 1
    residue = 4
    for _ in range(125):
        residue = (residue * residue - 2) % q
    require(
        residue == 0 and all(127 % p for p in (2, 3, 5, 7, 11)), "Lucas-Lehmer prime"
    )
    threshold = 64
    for _ in range(84):
        threshold = 64 * ((threshold + 41) // 42)
    strict, covering = selected_tables(2, 85)
    k = strict[85]
    e = 2 * threshold + k
    require(1 < e**17 <= 2**10000, "exact existing atom width is two")
    require(depth(e // 2, 64, 42) == 85, "complete selected depth table")
    new = select(e, 2, 64, 42, strict)
    old = select(e, 2, 64, 42, covering)
    require(new == (k, threshold, 0, 85), "selected strict optimum")
    require(old is not None and old[0] == k + 1, "selected one digit improvement")
    require(covering[85] == k + 1, "selected strict versus covering threshold")
    coefficient = 9475 * 28416**85
    require(q**10 < coefficient < 2 * q**10, "small exact coefficient interval")
    return {
        "q": str(q),
        "e": e,
        "width": 2,
        "threshold_a85": threshold,
        "strict_plan": list(new),
        "covering_plan": list(old),
        "coefficient": str(coefficient),
        "overhead_strict": 10,
        "overhead_covering": 11,
        "prime_test": "Lucas-Lehmer p=127, 125 steps, residue zero",
    }


def check_padding_equivalence():
    cases = 0
    for rows in range(1, 129):
        for stock in range(1, 257):
            padded = ((rows + stock - 1) // stock) * stock
            require((padded < 2 * rows) == (stock < 2 * rows), "exact volume condition")
            cases += 1
    return cases
