#!/usr/bin/env python3
"""Weighted five-node clean-chain threshold. Apache-2.0.

Produced by Nick Petalas. Independent human and formal proof-kernel review
are unclaimed. No predecessor implementation is imported.
"""

import argparse
from collections import deque
import hashlib
from heapq import heappop, heappush
from itertools import product
import json
from pathlib import Path
import platform

NODES = 5
STATES = 32
GOAL = 16
MAX_WIDTH = 10**12
VIA_THREE = (1, 2, 3, -2, -1, 4, 5, -4, 1, 2, -3, -2, -1)
VIA_TWO = (1, 2, -1, 3, 4, 5, -4, -3, 1, -2, -1)


def require(condition, message):
    """Keep proof-relevant checks enabled under optimized Python."""
    if not condition:
        raise AssertionError(message)


def validate_widths(widths):
    if not isinstance(widths, tuple) or len(widths) != NODES:
        raise ValueError("supply exactly five widths as a tuple")
    if any(type(w) is not int or not 1 <= w <= MAX_WIDTH for w in widths):
        raise ValueError("widths must be integers in 1..10^12")


def capacity(widths):
    validate_widths(widths)
    a, b, c, d, output = widths
    return output + max(a + b, c + d, b + c + min(a, d))


def attaining_schedule(widths):
    validate_widths(widths)
    return VIA_THREE if widths[0] < widths[3] else VIA_TWO


def replay(widths, moves):
    validate_widths(widths)
    if not isinstance(moves, tuple) or len(moves) > 31:
        raise ValueError("the supplied schedule must have at most 31 moves")
    occupied = set()
    peak = 0
    for move in moves:
        if type(move) is not int or not 1 <= abs(move) <= NODES:
            raise ValueError("invalid node operation")
        node = abs(move)
        if (node in occupied) != (move < 0):
            raise ValueError("compute/erase presence mismatch")
        if node > 1 and node - 1 not in occupied:
            raise ValueError("the parent is absent")
        if move > 0:
            occupied.add(node)
        else:
            occupied.remove(node)
        peak = max(peak, sum(widths[i - 1] for i in occupied))
    if occupied != {NODES}:
        raise ValueError("the endpoint must contain only node five")
    return peak


def graph():
    """Build every legal toggle independently of the supplied schedules."""
    edges = []
    for state in range(STATES):
        row = []
        for node in range(NODES):
            if node == 0 or state & (1 << (node - 1)):
                row.append(state ^ (1 << node))
        edges.append(tuple(row))
    require(sum(map(len, edges)) == 96, "wrong edge count")
    return tuple(edges)


def state_costs(widths):
    return tuple(
        sum(widths[i] for i in range(NODES) if state & (1 << i))
        for state in range(STATES)
    )


def minimax_oracle(widths, edges, clean=True):
    """Bottleneck shortest paths over all 32 states, with no formula use."""
    costs = state_costs(widths)
    distances = [sum(widths) + 1] * STATES
    distances[0] = 0
    todo = [(0, 0)]
    # Each directed edge can relax once after its source is settled.
    for _ in range(97):
        if not todo:
            break
        peak, state = heappop(todo)
        if peak != distances[state]:
            continue
        if state == GOAL or (not clean and state & GOAL):
            return peak
        for target in edges[state]:
            candidate = max(peak, costs[target])
            if candidate < distances[target]:
                distances[target] = candidate
                heappush(todo, (candidate, target))
    raise AssertionError("the finite minimax oracle did not reach its goal")


def reachable(edges, allowed):
    seen = {0}
    todo = deque([0])
    for _ in range(STATES):
        if not todo:
            return tuple(sorted(seen))
        state = todo.popleft()
        for target in edges[state]:
            if allowed[target] and target not in seen:
                seen.add(target)
                todo.append(target)
    require(not todo, "reachability exceeded 32 distinct states")
    return tuple(sorted(seen))


def check_cuts(edges):
    cuts = []
    # {1,2,5}, {3,4,5}, and the alternative four-node gates.
    for masks in ((19,), (28,), (23, 30)):
        allowed = tuple(
            not any(state & mask == mask for mask in masks)
            for state in range(STATES)
        )
        component = reachable(edges, allowed)
        require(GOAL not in component, "a separating gate is avoidable")
        cuts.append({"forbidden_supersets": masks, "reachable": component})
    return cuts


def check_widths(edges):
    count = 0
    branches = [0, 0]
    for widths in product(range(1, 8), repeat=NODES):
        predicted = capacity(widths)
        require(minimax_oracle(widths, edges) == predicted, (widths, "minimum"))
        require(replay(widths, attaining_schedule(widths)) == predicted,
                (widths, "attainment"))
        allowed = tuple(cost < predicted for cost in state_costs(widths))
        require(GOAL not in reachable(edges, allowed), (widths, "lower bound"))
        branches[widths[0] >= widths[3]] += 1
        count += 1
    require(count == 7**5 and all(branches), "incomplete width domain")
    return count, branches


def expect_rejected(operation, *args):
    try:
        operation(*args)
    except ValueError:
        return
    raise AssertionError("an invalid contract was accepted")


def check_controls(edges):
    invalid = (
        (), (1, 2, 3, 4), (1, 2, 3, 4, 5, 6), [1, 1, 1, 1, 1],
        (0, 1, 1, 1, 1), (-1, 1, 1, 1, 1), (True, 1, 1, 1, 1),
        (1.0, 1, 1, 1, 1), (MAX_WIDTH + 1, 1, 1, 1, 1),
    )
    for widths in invalid:
        expect_rejected(capacity, widths)
    unit = (1,) * NODES
    bad_words = ((), (2,), (1, -2), (0,), (True,), (1, 2, -1, -2), (1,) * 32)
    for word in bad_words:
        expect_rejected(replay, unit, word)
    require(minimax_oracle(unit, edges, clean=False) == 3, "visit control")
    require(minimax_oracle(unit, edges) == 4, "clean control")
    for widths, chosen, other in (
        ((1, 1, 1, 10, 1), VIA_THREE, VIA_TWO),
        ((10, 1, 1, 1, 1), VIA_TWO, VIA_THREE),
    ):
        require(replay(widths, chosen) == 12, "weighted attaining control")
        require(replay(widths, other) == 13, "weighted branch control")
    require(capacity((MAX_WIDTH,) * NODES) == 4 * MAX_WIDTH, "integer limit")
    require(capacity((1, 1, 1, 10, 1)) == 12, "min/max mutation control")
    return {"invalid_widths": len(invalid), "invalid_words": len(bad_words)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="save generated evidence outside the package")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    if args.receipt and args.receipt.resolve().is_relative_to(package):
        parser.error("receipt must be outside the package")
    edges = graph()
    cuts = check_cuts(edges)
    width_count, branches = check_widths(edges)
    controls = check_controls(edges)
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    result = {
        "status": "PASS_WEIGHTED_FIVE_NODE_CHAIN",
        "claim_type": "scoped written proof with finite corroboration",
        "width_tuples": width_count,
        "width_range": [1, 7],
        "attaining_branch_counts": branches,
        "cuts": cuts,
        "controls": controls,
        "python": platform.python_version(),
        "source_sha256": {
            name: hashlib.sha256((package / name).read_bytes()).hexdigest()
            for name in names
        },
        "limitations": "pure clean pebble model; no native or selected-supplier admission",
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
