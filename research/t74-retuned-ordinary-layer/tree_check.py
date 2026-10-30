# SPDX-License-Identifier: Apache-2.0
"""Exact small control for the weighted-tree proof when tau < sigma.

This deliberately uses a toy five-child recurrence, not a T74 supplier.
All visited widths are fourth powers; no logarithm or fractional-power
engine is imported. Hiroki Kumazaki with substantial OpenAI Codex assistance.
"""

from collections import defaultdict
from fractions import Fraction
from math import isqrt
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def powers(width):
    """Return exact width^(1/2), width^(1/4) on this fixture's domain."""
    square = isqrt(width)
    fourth = isqrt(square)
    require(square * square == width and fourth * fourth == square,
            "fixture width must be a positive fourth power")
    return square, fourth


def enumerate_tree(non_strict_stop=False, omit_leaf_cost=False):
    """Expand all five children explicitly with their physical-volume weights."""
    root = 16 ** 4
    pending = [(root, Fraction(1), 0)]
    levels = defaultdict(lambda: dict(nodes=0, sigma_mass=Fraction(0)))
    internal = []
    leaves = []
    while pending:
        width, weight, level = pending.pop()
        square, fourth = powers(width)
        levels[level]["nodes"] += 1
        levels[level]["sigma_mass"] += weight * square
        stopped = width < 16 or (width * width <= root if non_strict_stop
                                else width * width < root)
        record = dict(width=width, weight=weight, level=level,
                      sigma_mass=weight * square)
        if stopped:
            record["cost"] = Fraction(0) if omit_leaf_cost else weight * width
            leaves.append(record)
        else:
            record["cost"] = weight * fourth
            internal.append(record)
            require(width % 16 == 0, "exact fixture child width")
            for _ in range(5):
                pending.append((width // 16, weight / 2, level + 1))
    return dict(root=root, levels=dict(levels), internal=internal, leaves=leaves)


def costs(tree):
    return (sum((row["cost"] for row in tree["internal"]), Fraction(0)),
            sum((row["cost"] for row in tree["leaves"]), Fraction(0)))


def run():
    tree = enumerate_tree()
    root = tree["root"]
    root_sigma, root_tau = powers(root)
    moment = Fraction(5, 8)  # (H/W) * (r/m)^sigma = (5/2) * (1/16)^(1/2).
    require(moment < 1, "strict toy moment")
    require(len(tree["internal"]) == 31 and len(tree["leaves"]) == 125,
            "complete explicit five-child tree")
    for level, row in tree["levels"].items():
        require(row["nodes"] == 5 ** level, "all positive children retained")
        require(row["sigma_mass"] == root_sigma * moment ** level,
                "exact weighted sigma mass at each level")
    require(sum(row["width"] == 256 for row in tree["internal"]) == 25,
            "width squared equal to root is internal at the strict threshold")
    require(all(row["width"] == 16 for row in tree["leaves"]),
            "strict stop reaches width sixteen")

    internal_cost, leaf_cost = costs(tree)
    require(internal_cost == 61 and leaf_cost == 250, "exact complete toy invoice")
    internal_sigma_mass = sum((row["sigma_mass"] for row in tree["internal"]), Fraction(0))
    leaf_sigma_mass = sum((row["sigma_mass"] for row in tree["leaves"]), Fraction(0))
    require(internal_cost <= internal_sigma_mass <= root_sigma / (1 - moment),
            "tau below sigma internal domination and geometric bound")
    require(leaf_sigma_mass <= root_sigma, "stopped leaf antichain mass")
    # beta=1/2 and sigma=1/2: root^(beta*(1-sigma))=root^(1/4)=16.
    require(leaf_cost <= root_tau * leaf_sigma_mass <= root_tau * root_sigma,
            "leaf exponent sigma+beta*(1-sigma)=3/4")

    # The old tau>sigma estimate has the wrong direction in this domain.
    # At root/16, e^tau=8 whereas root^(tau-sigma)*e^sigma=4.
    width = root // 16
    square, fourth = powers(width)
    wrong_upper = Fraction(square, root_tau)
    require(fourth > wrong_upper, "reject old exponent-direction inequality")

    omitted = enumerate_tree(omit_leaf_cost=True)
    require(costs(omitted)[0] == internal_cost and costs(omitted)[1] == 0,
            "leaf-omission control changes only the leaf invoice")
    require(sum(costs(omitted)) != internal_cost + leaf_cost,
            "reject unpaid stopped leaves")

    non_strict = enumerate_tree(non_strict_stop=True)
    require(len(non_strict["internal"]) == 6 and len(non_strict["leaves"]) == 25,
            "nonstrict stopping mutation changes executed tree")
    require(all(row["width"] == 256 for row in non_strict["leaves"]),
            "nonstrict mutation stops at equality")
    require(costs(non_strict) == (Fraction(36), Fraction(1600)),
            "independent equality-stop control invoice")
    require(costs(non_strict) != (internal_cost, leaf_cost),
            "reject changed stopping semantics")

    return dict(
        scope="generic exact weighted-tree control; not a T74 or production-payload replay",
        root=root, dimension=16, child_rank=1, children=5, child_volume_weight="1/2",
        sigma="1/2", tau="1/4", beta="1/2", sigma_moment=str(moment),
        internal_nodes=len(tree["internal"]), leaf_nodes=len(tree["leaves"]),
        internal_cost=str(internal_cost), leaf_cost=str(leaf_cost),
        internal_sigma_mass=str(internal_sigma_mass), leaf_sigma_mass=str(leaf_sigma_mass),
        levels=[dict(level=level, nodes=row["nodes"], sigma_mass=str(row["sigma_mass"]))
                for level, row in sorted(tree["levels"].items())],
        controls=["old exponent-direction inequality", "unpaid stopped leaves",
                  "nonstrict stopping at equality"],
    )


if __name__ == "__main__":
    print("PASS_GENERIC_WEIGHTED_TREE", json.dumps(run(), sort_keys=True))
