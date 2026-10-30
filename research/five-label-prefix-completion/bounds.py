"""Sound outward tail envelopes, fixed-domain comparison traversal.

Prepared for SHIN09-git with substantial OpenAI Codex assistance. Apache-2.0.
The new geometric rule does not depend on the cap-11 comparison rule.
"""
from collections import Counter
from itertools import combinations

MASKS = (15, 23, 27, 29, 30, 31)
MODES = ("none", "cheap", "cap11", "one_vertex", "two_vertex", "one_without_cap", "two_without_cap")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def pair_support(points):
    bits = 0
    for a, b in combinations(points, 2):
        bits |= 1 << (a ^ b)
    return bits


def choose2(n):
    return n * (n - 1) // 2


def prefix_from_word(word, n=5, length=12):
    require(type(n) is int and 2 <= n <= 5, "dimension")
    require(type(length) is int and length % 2 == 0 and 2 * n <= length <= 12, "length")
    require(len(word) < length, "partial prefix required")
    points = [0]
    for label in word:
        require(type(label) is int and 0 <= label < n, "label")
        value = points[-1] ^ (1 << label)
        require(value not in points, "simple prefix required")
        points.append(value)
    return tuple(points)


def tail_envelope(points, n=5, length=12, joint=True):
    """Internal kernel: points must be a validated simple prefix starting at 0."""
    remaining = length - len(points) + 1
    last = points[-1]
    visited = set(points)
    future = tuple(x for x in range(1 << n) if x not in visited
                   and (last ^ x).bit_count() + x.bit_count() <= remaining)
    possible = pair_support(points)
    for old in points:
        for new in future:
            possible |= 1 << (old ^ new)
    if not joint:
        return future, possible | pair_support(future)
    # Every jointly reachable future-pair difference z already occurs as
    # last XOR (last XOR z): the second endpoint is old or belongs to U.
    # PROOF.md derives this equality; verify.py checks the literal pair formula.
    return future, possible


def completion_bound(word, n=5, length=12, joint=True):
    points = prefix_from_word(word, n, length)
    future, support = tail_envelope(points, n, length, joint)
    needed = length - len(points)
    full = (1 << (1 << n)) - 2
    return {"reject": len(future) < needed or support != full,
            "future": future,
            "missing": tuple(x for x in range(1, 1 << n) if not support >> x & 1)}


def remaining_reject(points, highest, length=12):
    return points[-1].bit_count() + 2 * (5 - highest - 1) > length - len(points) + 1


def union_reject(points):
    """Credited PR3005 same/cross pair-count bound at final parity split (6,6)."""
    classes = [tuple(x for x in points if x.bit_count() % 2 == bit) for bit in (0, 1)]
    a, b = map(len, classes)
    same = (pair_support(classes[0]) | pair_support(classes[1])).bit_count()
    cross = len({x ^ y for x in classes[0] for y in classes[1]})
    return a > 6 or b > 6 or same + 30 - choose2(a) - choose2(b) < 15 or cross + 36 - a * b < 16


def excess(points, mask):
    total = 0
    for bit in (0, 1):
        values = tuple(x for x in points if (x & mask).bit_count() % 2 == bit)
        total += choose2(len(values)) - pair_support(values).bit_count()
    return total


def cap_reject(points):
    """Only for five-label length-12 simple universal completions (PR4992)."""
    return any(excess(points, mask) > 11 for mask in MASKS)


def class_completion_lower(points, future, mask):
    """Exploratory cap-11 completion bound; not used by the geometric kernel."""
    classes = [tuple(x for x in points if (x & mask).bit_count() % 2 == bit) for bit in (0, 1)]
    pools = [tuple(x for x in future if (x & mask).bit_count() % 2 == bit) for bit in (0, 1)]
    sizes = list(map(len, classes))
    supports = [pair_support(c).bit_count() for c in classes]
    limits = [pair_support(classes[b] + pools[b]).bit_count() for b in (0, 1)]
    candidates = []
    for size in ((6,) if mask == 31 else (5, 6, 7)):
        final = (size, 12 - size)
        if any(not sizes[b] <= final[b] <= sizes[b] + len(pools[b]) for b in (0, 1)):
            continue
        upper = [min(limits[b], supports[b] + choose2(final[b]) - choose2(sizes[b])) for b in (0, 1)]
        candidates.append(sum(map(choose2, final)) - sum(upper))
    return min(candidates) if candidates else None


def reject(points, highest, mode):
    require(mode in MODES, "mode")
    if mode == "none":
        return False
    if remaining_reject(points, highest) or union_reject(points):
        return True
    if mode == "cheap":
        return False
    if mode not in ("one_without_cap", "two_without_cap") and cap_reject(points):
        return True
    if mode == "cap11":
        return False
    future, possible = tail_envelope(points, joint=mode in ("two_vertex", "two_without_cap"))
    return len(future) < 12 - len(points) or possible != (1 << 32) - 2


def search(mode="none"):
    """Canonical DFS; no rotation, reversal or closed-word equivalence pruning."""
    counts = Counter()
    closed = []
    hits = []

    def visit(word, points, highest, seen):
        counts["entered"] += 1
        if reject(points, highest, mode):
            counts["pruned"] += 1
            return
        if len(word) == 11:
            last = points[-1]
            if last and last & (last - 1) == 0:
                completed = word + (last.bit_length() - 1,)
                closed.append(completed)
                if pair_support(points) == (1 << 32) - 2:
                    hits.append(completed)
            return
        for label in range(min(highest + 1, 4) + 1):
            value = points[-1] ^ (1 << label)
            if not seen >> value & 1:
                visit(word + (label,), points + (value,), max(highest, label), seen | (1 << value))

    visit((), (0,), -1, 1)
    return {"entered": counts["entered"], "pruned": counts["pruned"],
            "closed": len(closed), "universal": len(hits)}, tuple(sorted(closed)), tuple(sorted(hits))

