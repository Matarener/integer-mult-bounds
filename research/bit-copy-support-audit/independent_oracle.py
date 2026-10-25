#!/usr/bin/env python3
"""Independent finite support oracle; no predecessor implementation imports.

Rational geometry and F2 coefficient arithmetic are deliberately separate.
Rows are exact decoded linear forms in independent q, dirty_a, dirty_b.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def reduced(rows, n=3):
    rows = [[Q(value) for value in row] for row in rows if any(row)]
    at = 0
    for column in range(n):
        pivot = next((r for r in range(at, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[at], rows[pivot] = rows[pivot], rows[at]
        scale = rows[at][column]
        rows[at] = [value / scale for value in rows[at]]
        for r in range(len(rows)):
            if r != at and rows[r][column]:
                scale = rows[r][column]
                rows[r] = [a - scale * b for a, b in zip(rows[r], rows[at])]
        at += 1
        if at == len(rows):
            break
    return tuple(tuple(row) for row in rows[:at])


def perpendicular(frame, n=3):
    pivots = [next(i for i, x in enumerate(row) if x) for row in frame]
    answer = []
    for free in range(n):
        if free in pivots:
            continue
        row = [Q(0)] * n
        row[free] = Q(1)
        for equation, pivot in zip(frame, pivots):
            row[pivot] = -equation[free]
        answer.append(row)
    return reduced(answer, n)


def intersection(left, right):
    return perpendicular(reduced(perpendicular(left) + perpendicular(right)))


def subset(left, right):
    return reduced(left + right) == right


def frame_family(basis):
    return tuple(reduced([basis[i] for i in range(3) if mask & (1 << i)])
                 for mask in range(8))


def check_geometry(frames):
    require(len(set(frames)) == 8, "basis does not generate eight distinct frames")
    contains = [[subset(left, right) for right in frames] for left in frames]
    intersections = [[frames.index(intersection(a, b)) for b in frames] for a in frames]
    for a in range(8):
        for b in range(8):
            meet = intersections[a][b]
            require(contains[meet][a] and contains[meet][b], "intersection not a lower bound")
            for c in range(8):
                require(not (contains[c][a] and contains[c][b]) or contains[c][meet],
                        "intersection not the greatest lower bound")
    return contains, intersections


def closed_walks(frames, contains, meets):
    """Every strict nested closed private walk of zero through four edges."""
    neighbors = [[b for b in range(8) if b != a and (contains[a][b] or contains[b][a])]
                 for a in range(8)]
    census = Counter()
    meets_seen = Counter()
    total = 0
    for start in range(8):
        stack = [(start, (start,), start, 0, 0, 0)]
        while stack:
            current, path, meet, cost, upward, downward = stack.pop()
            edges = len(path) - 1
            if current == start:
                require(upward == downward and cost == upward + downward,
                        "closed walk has unequal upward/downward dimension charges")
                require(2 * len(frames[meet]) >= 2 * len(frames[start]) - cost,
                        "closed-walk intersection dimension bound failed")
                require(all(contains[meet][vertex] for vertex in path),
                        "walk intersection escapes a visited frame")
                total += 1
                census[edges] += 1
                meets_seen[meet] += 1
            if edges < 4:
                for target in neighbors[current]:
                    delta = len(frames[target]) - len(frames[current])
                    stack.append((target, path + (target,), meets[meet][target],
                                  cost + abs(delta), upward + max(delta, 0),
                                  downward + max(-delta, 0)))
    return {"closed_walks": total, "by_edge_count": dict(sorted(census.items())),
            "intersection_frames_seen": len(meets_seen)}


def support_holds(frame_ids, rows, meet, contains):
    return all(not (row & 1) or contains[meet][frame]
               for frame, row in zip(frame_ids, rows))


def exhaustive_inductive_transitions(frames, contains):
    """All two-register linear states satisfying the invariant, not just samples.

    Each row has three independent F2 columns: q, dirty_a, dirty_b.
    Every 0/1 scalar READ/ADD and all upward MOVE targets are tested.
    This single-step closure covers arbitrary finite operation counts, but only
    for these two finite frame families; the accompanying written induction is
    needed for arbitrary rational geometries/register counts.
    """
    counts = Counter()
    for meet, first, second in product(range(8), repeat=3):
        ids = (first, second)
        for row_a, row_b in product(range(8), repeat=2):
            rows = (row_a, row_b)
            if not support_holds(ids, rows, meet, contains):
                continue
            counts["admissible_symbolic_states"] += 1
            for receiver in range(2):
                for scalar in (0, 1):
                    # READ is available only at a private visited frame. Every
                    # such frame contains meet; grant every equal-frame read
                    # satisfying that necessary condition for this stronger test.
                    if contains[meet][ids[receiver]]:
                        new_rows = list(rows)
                        new_rows[receiver] ^= scalar
                        require(support_holds(ids, new_rows, meet, contains),
                                "equal-frame private read broke support")
                        counts["equal_frame_read_transitions"] += 1
                    source = 1 - receiver
                    if ids[source] == ids[receiver]:
                        new_rows = list(rows)
                        new_rows[receiver] ^= scalar * rows[source]
                        require(support_holds(ids, new_rows, meet, contains),
                                "equal-frame public add broke support")
                        counts["equal_frame_add_transitions"] += 1
                for target in range(8):
                    if contains[ids[receiver]][target]:
                        new_ids = list(ids)
                        new_ids[receiver] = target
                        require(support_holds(new_ids, rows, meet, contains),
                                "upward public move broke support")
                        counts["upward_move_transitions"] += 1
    counts["all_transitions"] = sum(value for key, value in counts.items()
                                   if key.endswith("_transitions"))
    return dict(counts)


def evaluate(row, bits):
    return (row & bits).bit_count() & 1


def cancellation_control(frames, contains):
    # q, a, b are independent. q is copied/read without changing its own value.
    meet = 1
    ids = [meet, meet]
    rows = [2, 4]
    trace = [("initial", list(rows))]
    rows[0] ^= 1
    trace.append(("read q into a", list(rows)))
    rows[1] ^= rows[0]
    trace.append(("add a into b", list(rows)))
    rows[0] ^= 1
    trace.append(("read q into a again", list(rows)))
    rows[1] ^= 1
    trace.append(("read q into b", list(rows)))
    rows[1] ^= rows[0]
    trace.append(("add restored a into b", list(rows)))
    require(rows == [2, 4], "cancellation loop did not restore arbitrary dirty data")
    require(all(support_holds(ids, pair, meet, contains) for _, pair in trace),
            "cancellation loop broke support")
    concrete = 0
    for bits in range(8):
        a, b, q = (bits >> 1) & 1, (bits >> 2) & 1, bits & 1
        a ^= q
        b ^= a
        a ^= q
        b ^= q
        b ^= a
        require([a, b] == [evaluate(row, bits) for row in rows],
                "symbolic and concrete dirty loop disagree")
        concrete += 1
    return {"symbolic_trace_columns_q_a_b": trace,
            "all_concrete_dirty_and_q_assignments": concrete,
            "restores_both_arbitrary_dirty_inputs": True}


def forbidden_controls(frames, contains):
    zero, line = 0, 1
    require(not contains[line][zero], "counterexample line unexpectedly trivial")
    # q + dirty_a, after an allowed equal-frame private read at line.
    before_ids, before_rows = [line, zero], [3, 4]
    require(support_holds(before_ids, before_rows, line, contains),
            "counterexample premise already violates support")
    # Forbidden move line -> zero transports the same decoded linear row.
    downward_ids = [zero, zero]
    require(not support_holds(downward_ids, before_rows, line, contains),
            "downward-move mutant escaped detection")
    # Forbidden ADD from line into a zero-frame receiver creates q there.
    mismatched_rows = [3, 4 ^ 3]
    require(not support_holds(before_ids, mismatched_rows, line, contains),
            "mismatched-add mutant escaped detection")
    # Both violations remain visible with all independent dirty assignments;
    # compare q=0 and q=1 while fixing the dirty columns.
    comparisons = 0
    for dirty_bits in range(4):
        q_zero = dirty_bits << 1
        q_one = q_zero | 1
        require(evaluate(before_rows[0], q_zero) != evaluate(before_rows[0], q_one),
                "downward mutant lost q influence")
        require(evaluate(mismatched_rows[1], q_zero) != evaluate(mismatched_rows[1], q_one),
                "mismatched-add mutant lost q influence")
        comparisons += 2
    return {"downward_move_rejected": True, "mismatched_add_rejected": True,
            "dirty_assignment_influence_comparisons": comparisons,
            "downward_example": {"frames_before": before_ids,
                                 "frames_after": downward_ids, "rows": before_rows},
            "mismatched_add_example": {"frames": before_ids, "rows_after": mismatched_rows}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    bases = {
        "coordinate": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        "noncoordinate_rational": ((1, Q(1, 2), 0), (0, 1, Q(1, 3)), (Q(1, 5), 0, 1)),
    }
    result = {"status": "PASS", "ambient_dimension": 3,
              "coefficient_field": "F2", "geometry_field": "Q",
              "independent_columns": ["q", "dirty_a", "dirty_b"],
              "scope": "finite symbolic induction and controls, not a full R438 source replay",
              "families": {}}
    for name, basis in bases.items():
        frames = frame_family(basis)
        contains, meets = check_geometry(frames)
        result["families"][name] = {
            "frames": [[[str(value) for value in row] for row in frame] for frame in frames],
            "walks": closed_walks(frames, contains, meets),
            "influence": exhaustive_inductive_transitions(frames, contains),
            "cancellation": cancellation_control(frames, contains),
            "assumption_counterexamples": forbidden_controls(frames, contains),
        }
    result["total_closed_private_walks"] = sum(x["walks"]["closed_walks"] for x in result["families"].values())
    result["total_symbolic_states"] = sum(x["influence"]["admissible_symbolic_states"] for x in result["families"].values())
    result["total_transition_checks"] = sum(x["influence"]["all_transitions"] for x in result["families"].values())
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "families"}, sort_keys=True))


if __name__ == "__main__":
    main()
