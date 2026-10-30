"""Deterministic regular bipartite edge coloring from PR3403/PR3413.

Original source retained/authenticated by PR3413 at commit
391d02ced8e620d8f06aeda1ebe02f099d37af92. This six-width adaptation
changes only range(5) to range(len(counts)); no optimization is performed.
Apache-2.0, inherited attribution retained in CREDITS.md.
"""

from collections import deque


def need(condition, message):
    if not condition:
        raise ValueError(message)


def regular_graph(demands, counts, multiplicity):
    """Make the time-to-slot multigraph regular using dummy slots and times."""
    times = sorted(demands)
    slots = [k for k, n in enumerate(counts) for _ in range(n)]
    size = max(len(times), len(slots))
    need(size <= 144, "graph vertex bound")
    matrix = [[0] * size for _ in range(size)]
    for k in range(len(counts)):
        columns = [j for j, width in enumerate(slots) if width == k]
        remaining = {j: multiplicity for j in columns}
        for i, t in enumerate(times):
            count = demands[t][k]
            for j in columns:
                amount = min(count, remaining[j])
                matrix[i][j] += amount
                remaining[j] -= amount
                count -= amount
            need(count == 0, "slot supply exhausted")
        need(not any(remaining.values()), "unfilled real slot")
    row_defect = [multiplicity - sum(row) for row in matrix]
    col_defect = [multiplicity - sum(row[j] for row in matrix) for j in range(size)]
    for i in range(size):
        for j in range(len(slots), size):
            amount = min(row_defect[i], col_defect[j])
            matrix[i][j] += amount
            row_defect[i] -= amount
            col_defect[j] -= amount
    need(not any(row_defect) and not any(col_defect), "regularization")
    return matrix, times, slots


def perfect_matching(matrix):
    """Bounded alternating-path matching on positive support, without recursion."""
    size = len(matrix)
    left, right = [-1] * size, [-1] * size
    for start in range(size):
        queue, previous, endpoint = deque([start]), {}, None
        for _ in range(size):
            if not queue or endpoint is not None:
                break
            i = queue.popleft()
            for j in range(size):
                if matrix[i][j] <= 0 or j in previous:
                    continue
                previous[j] = i
                if right[j] == -1:
                    endpoint = j
                    break
                queue.append(right[j])
        need(endpoint is not None, "regular graph has no perfect matching")
        for _ in range(size):
            i = previous[endpoint]
            old = left[i]
            left[i], right[endpoint] = endpoint, i
            if old == -1:
                break
            endpoint = old
        else:
            raise ValueError("alternating path exceeded vertex bound")
    return left


def colour_pattern(demands, counts, multiplicity):
    if not any(counts):
        return [[] for _ in range(multiplicity)]
    matrix, times, slots = regular_graph(demands, counts, multiplicity)
    bins = []
    for _ in range(multiplicity):
        if len(bins) == multiplicity:
            break
        match = perfect_matching(matrix)
        amount = min(matrix[i][j] for i, j in enumerate(match))
        values = sorted(
            (times[i], slots[j]) for i, j in enumerate(match) if j < len(slots)
        )
        need(len({t for t, _ in values}) == len(values), "repeated time in colour")
        bins.extend([values] * amount)
        for i, j in enumerate(match):
            matrix[i][j] -= amount
    need(
        len(bins) == multiplicity and not any(any(row) for row in matrix),
        "colour exhaustion",
    )
    return bins
