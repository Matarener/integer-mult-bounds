#!/usr/bin/env python3
"""Exact corroboration of the partial-target codimension bound. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def extend(space, vector):
    """Encode a binary subspace by a bit for each of its elements."""
    result = space
    for value in range(32):
        if space >> value & 1:
            result |= 1 << (value ^ vector)
    return result


def subset_spaces(vectors):
    require(1 <= len(vectors) <= 10, "pool size outside finite check budget")
    require(all(0 <= v < 32 for v in vectors), "vector outside five-bit budget")
    spaces = [1] * (1 << len(vectors))
    for mask in range(1, len(spaces)):
        bit = mask & -mask
        spaces[mask] = extend(spaces[mask ^ bit], vectors[bit.bit_length() - 1])
    return spaces


def dimension(space):
    size = space.bit_count()
    require(size > 0 and size & (size - 1) == 0, "not a subspace cardinality")
    return size.bit_length() - 1


def all_subspaces(width):
    require(1 <= width <= 4, "width outside exhaustive budget")
    spaces = {1}
    for _ in range(width):
        spaces |= {extend(space, v) for space in spaces for v in range(1 << width)}
    return sorted(spaces)


def subset_costs(costs):
    require(1 <= len(costs) <= 10, "cost count outside finite check budget")
    require(all(type(c) is int and c >= 0 for c in costs), "negative or noninteger cost")
    result = [0] * (1 << len(costs))
    for mask in range(1, len(result)):
        bit = mask & -mask
        result[mask] = result[mask ^ bit] + costs[bit.bit_length() - 1]
    return result


def basis_support(vectors, basis, target):
    entries = [i for i in range(len(vectors)) if basis >> i & 1]
    require(len(entries) <= 5, "basis exceeds five-bit budget")
    expressions = {0: 0}
    for index in entries:
        additions = {v ^ vectors[index]: mask | (1 << index)
                     for v, mask in expressions.items()}
        require(not expressions.keys() & additions.keys(), "dependent basis")
        expressions.update(additions)
    support = 0
    for value in range(32):
        if target >> value & 1:
            require(value in expressions, "target outside basis span")
            support |= expressions[value]
    return support


def check_instance(vectors, costs, targets):
    spaces = subset_spaces(vectors)
    prices = subset_costs(costs)
    rank = dimension(spaces[-1])
    bases = [mask for mask, space in enumerate(spaces)
             if space == spaces[-1] and mask.bit_count() == rank]
    minimum = min(prices[mask] for mask in bases)
    bases = [mask for mask in bases if prices[mask] == minimum]
    comparisons = thresholds = 0
    for target in targets:
        require(target & spaces[-1] == target, "target outside pool span")
        demand = dimension(target)
        feasible = [mask for mask, space in enumerate(spaces) if target & space == target]
        optimum = min(prices[mask] for mask in feasible)
        witness = min(mask for mask in feasible if prices[mask] == optimum)
        for basis in bases:
            support = basis_support(vectors, basis, target)
            factor = rank - demand + 1 if demand else 0
            require(prices[support] <= factor * optimum, "codimension bound failed")
            comparisons += 1
            for threshold in sorted({0, *costs}):
                expensive = sum(1 << i for i, cost in enumerate(costs) if cost > threshold)
                bought = (witness & expensive).bit_count()
                used = (support & expensive).bit_count()
                require(used <= factor * bought, "price-threshold bound failed")
                thresholds += 1
    return comparisons, thresholds


def exhaustive_domain():
    # Check partial targets and every tied minimum basis, without importing
    # or exercising the predecessor's greedy producer.
    vectors = (1, 2, 4, 8, 3, 5, 10, 15)
    targets = all_subspaces(4)
    require(len(targets) == 67, "four-dimensional subspace census changed")
    comparisons = thresholds = 0
    for costs in itertools.product((0, 3), repeat=len(vectors)):
        checked, cuts = check_instance(vectors, costs, targets)
        comparisons += checked
        thresholds += cuts
    return {"weighted_pools": 256, "target_spaces_per_pool": len(targets),
            "basis_target_comparisons": comparisons, "threshold_checks": thresholds}


def sharp_examples():
    count = 0
    for rank in range(2, 6):
        for demand in range(1, rank):
            tail = sum(1 << i for i in range(demand - 1, rank))
            vectors = tuple(1 << i for i in range(rank)) + (tail,)
            target = 1
            for v in tuple(1 << i for i in range(demand - 1)) + (tail,):
                target = extend(target, v)
            spaces = subset_spaces(vectors)
            for scale in (3, 11, 101):
                costs = (1,) * (demand - 1) + (scale - 1,) * (rank - demand + 1) + (scale,)
                prices = subset_costs(costs)
                bases = [m for m, s in enumerate(spaces)
                         if s == spaces[-1] and m.bit_count() == rank]
                best = min(prices[m] for m in bases)
                require([m for m in bases if prices[m] == best] == [(1 << rank) - 1],
                        "sharp fixture lost its unique minimum basis")
                support = basis_support(vectors, (1 << rank) - 1, target)
                optimum = min(prices[m] for m, s in enumerate(spaces) if target & s == target)
                require(optimum == scale + demand - 1, "sharp optimum formula failed")
                require(prices[support] == (rank - demand + 1) * (scale - 1) + demand - 1,
                        "sharp pruned-cost formula failed")
                check_instance(vectors, costs, (target,))
                count += 1
    return count


def failure_controls():
    # Missing hypotheses must be capable of breaking the claimed conclusion.
    prices = subset_costs((3, 3, 1))
    spaces = subset_spaces((1, 2, 3))
    optimum = min(prices[m] for m, s in enumerate(spaces) if s == spaces[-1])
    require(prices[3] > optimum == 4, "nonminimum basis was not distinguished")
    require(subset_costs((1, 10))[3] > 2 * subset_costs((1, 10))[1],
            "unpruned support control failed")
    vectors = (1, 2, 3)
    prices = subset_costs((100, 100, 101))
    support = basis_support(vectors, 3, 9)
    require(prices[support] > prices[4], "codimension-only factor was not rejected")
    rejected = 0
    for costs in ((-1, 2), (True, 2)):
        try:
            subset_costs(costs)
        except ValueError:
            rejected += 1
    for basis, target in ((3, 1), (1, 5)):
        try:
            basis_support((1, 1), basis, target)
        except ValueError:
            rejected += 1
    require(rejected == 4, "malformed-input controls failed")
    return {"hypothesis_controls": 3, "input_rejections": rejected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a generated source-bound receipt")
    args = parser.parse_args()
    result = {"schema": "partial-query-basis-gap/v1", "finite_domain": exhaustive_domain(),
              "positive_integer_sharp_fixtures": sharp_examples(), "controls": failure_controls()}
    root = Path(__file__).resolve().parent
    result["sha256"] = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                        for name in ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")}
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        require(not args.receipt.resolve().is_relative_to(root.parents[1]),
                "receipt must stay outside the checkout")
        require(args.receipt.write_text(output) == len(output), "short receipt write")
    print(output, end="")
    print("PASS_PARTIAL_QUERY_BASIS_GAP")


if __name__ == "__main__":
    main()
