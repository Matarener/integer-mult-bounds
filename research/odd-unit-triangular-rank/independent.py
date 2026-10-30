#!/usr/bin/env python3
"""Separate vector-coordinate certificate; imports no primary geometry code."""

from collections import deque
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import authenticate


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inner(x, y):
    return sum(a * b for a, b in zip(x, y)) % 2


def add(x, y):
    return tuple((a + b) % 2 for a, b in zip(x, y))


def integer(x):
    return sum(b * 2**k for k, b in enumerate(x))


def build(n):
    vectors = list(itertools.product((0, 1), repeat=n))
    odd = sorted((x for x in vectors if inner(x, x)), key=integer)
    universe = {(q, w) for q in odd for w in odd if inner(q, w)}
    # Enumerate the hyperplane directly rather than the primary affine formula.
    sinks = [w for w in odd if w[0] == 0]
    chosen = []
    for stop, w in enumerate(sinks):
        chosen.extend((q, w) for q in odd if all(inner(q, x) for x in sinks[:stop + 1]))
    if n == 5:
        chosen.append(((1,) * n, (1,) * n))
    require(len(chosen) == len(set(chosen)), "duplicate selector type")
    for row in range(len(chosen)):
        for col in range(row, len(chosen)):
            require(inner(chosen[row][1], chosen[col][0]) == 1,
                    "independent triangular constraint")
    # Use all even transvections and adjacent coordinate swaps, a different
    # generator family from model.py. Each transformation is an involution.
    maps = []
    for a in vectors:
        if any(a) and inner(a, a) == 0:
            maps.append({x: add(x, a) if inner(a, x) else x for x in vectors})
    for k in range(n - 1):
        maps.append({x: x[:k] + (x[k + 1], x[k]) + x[k + 2:] for x in vectors})
    basis = [tuple(int(k == j) for k in range(n)) for j in range(n)]
    for mapping in maps:
        require(all(mapping[mapping[x]] == x for x in vectors), "involution check")
        require(all(inner(mapping[x], mapping[y]) == inner(x, y)
                    for x in basis for y in basis), "independent isometry check")
    unseen, orbits = set(universe), []
    while unseen:
        start = min(unseen)
        reached, queue = {start}, deque([start])
        while queue:
            q, w = queue.popleft()
            images = [(m[q], m[w]) for m in maps] + [(w, q)]
            for value in images:
                require(value in universe, "independent orbit domain")
                if value not in reached:
                    reached.add(value)
                    queue.append(value)
        unseen -= reached
        orbits.append(reached)
    incidences = sorted((len(o), len(o.intersection(chosen))) for o in orbits)
    expected = [(1, 1), (15, 2), (30, 8), (90, 10)] if n == 5 else [(32, 3), (480, 45)]
    require(incidences == expected, "independent orbit incidences")
    encoded = [(integer(q), integer(w)) for q, w in chosen]
    digest = hashlib.sha256(json.dumps(encoded, separators=(",", ":")).encode()).hexdigest()
    require(digest == {
        5: "96726988127c29a14030b175bada688bfc3eb574dcb5fed32ad973abe01f423f",
        6: "7422ceb1f7f0332c25ebaea83c18cf98bda5056536a73373b27ecde3c32d60be",
    }[n], "independent selector identity")
    # Nonuniform multiplicities include missing types and repeated types.
    counts = {t: (integer(t[0]) + 3 * integer(t[1])) % 7 for t in universe}
    expected_weight = sum(Fraction(len(o.intersection(chosen)), len(o)) *
                          sum(counts[t] for t in o) for o in orbits)
    total = sum(counts.values())
    universal = Fraction(1, 9) if n == 5 else Fraction(3, 32)
    require(expected_weight >= universal * total, "independent weighted average")
    return {"dimension": n, "types": len(universe), "selector": len(chosen),
            "orbit_incidences": incidences, "selector_sha256": digest,
            "weighted_ports": total, "weighted_bound": str(expected_weight)}


if __name__ == "__main__":
    require(len(sys.argv) == 1, "unknown independent arguments")
    authenticate()
    print(json.dumps({"status": "PASS_INDEPENDENT_ODD_UNIT_RANK",
                      "certificates": [build(5), build(6)]}, sort_keys=True))
