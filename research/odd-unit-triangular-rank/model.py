"""Finite certificates for the odd-type fitting-rank theorem; Apache-2.0."""

from collections import deque
from fractions import Fraction
from functools import reduce
from operator import xor


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return (x & y).bit_count() & 1


def types(dimension):
    need(dimension in (5, 6), "supported ambient dimension")
    odd = tuple(x for x in range(1 << dimension) if x.bit_count() & 1)
    return tuple((q, w) for q in odd for w in odd if dot(q, w))


def selector(dimension):
    need(dimension in (5, 6), "supported ambient dimension")
    odd = tuple(x for x in range(1 << dimension) if x.bit_count() & 1)
    directions = tuple(2 ^ (1 << k) for k in range(2, dimension))
    sinks = tuple(
        2 ^ reduce(xor, (d for k, d in enumerate(directions) if mask >> k & 1), 0)
        for mask in range(1 << len(directions))
    )
    chosen, sizes = [], []
    for j, w in enumerate(sinks):
        block = [(q, w) for q in odd if all(dot(q, old) for old in sinks[: j + 1])]
        chosen.extend(block)
        sizes.append(len(block))
    if dimension == 5:
        chosen.append((31, 31))
    return tuple(chosen), sinks, tuple(sizes)


def check_selector(dimension, chosen):
    allowed = set(types(dimension))
    need(len(set(chosen)) == len(chosen), "selector repeats a type")
    need(set(chosen) <= allowed, "selector contains an inadmissible type")
    for i, (_, w) in enumerate(chosen):
        need(all(dot(w, q) for q, _ in chosen[i:]), "selector is not triangular")


def generators(dimension):
    basis = [1 << k for k in range(dimension)]
    images = [[basis[1], basis[0], *basis[2:]], [*basis[1:], basis[0]]]
    for a in (3, 15, (1 << dimension) - 1):
        if a < 1 << dimension and not a.bit_count() & 1:
            images.append([e ^ (a if dot(a, e) else 0) for e in basis])
    maps = []
    for columns in images:
        need(
            all(dot(columns[i], columns[j]) == (i == j)
                for i in range(dimension) for j in range(dimension)),
            "generator does not preserve the binary form",
        )
        table = tuple(
            reduce(xor, (columns[k] for k in range(dimension) if x >> k & 1), 0)
            for x in range(1 << dimension)
        )
        need(len(set(table)) == 1 << dimension, "generator is not bijective")
        maps.append(table)
    return tuple(maps)


def orbit_partition(dimension):
    allowed = set(types(dimension))
    maps = generators(dimension)
    remaining, result = set(allowed), []
    while remaining:
        first = min(remaining)
        orbit, queue = {first}, deque([first])
        while queue:
            q, w = queue.popleft()
            neighbors = [(table[q], table[w]) for table in maps] + [(w, q)]
            for neighbor in neighbors:
                need(neighbor in allowed, "symmetry left the type universe")
                if neighbor not in orbit:
                    orbit.add(neighbor)
                    queue.append(neighbor)
        remaining.difference_update(orbit)
        result.append(tuple(sorted(orbit)))
    return tuple(result)


def orbit_name(dimension, orbit):
    q, w = orbit[0]
    special = (1 << dimension) - 1
    if dimension == 5 and q == w == special:
        return "special"
    if dimension == 5 and (q == special or w == special):
        return "one-special"
    return "diagonal" if q == w else "cross"


def certificate(dimension):
    chosen, sinks, sizes = selector(dimension)
    check_selector(dimension, chosen)
    check_selector(dimension, tuple((w, q) for q, w in reversed(chosen)))
    chosen_set = set(chosen)
    orbits = orbit_partition(dimension)
    rows = []
    for orbit in orbits:
        selected = len(chosen_set.intersection(orbit))
        rows.append({"name": orbit_name(dimension, orbit), "size": len(orbit),
                     "selected": selected, "fraction": str(Fraction(selected, len(orbit)))})
    return {"dimension": dimension, "types": sum(map(len, orbits)),
            "selector": chosen, "sinks": sinks, "blocks": sizes,
            "orbits": sorted(rows, key=lambda row: row["name"])}


def weighted_bound(dimension, multiplicities):
    allowed = set(types(dimension))
    need(set(multiplicities) <= allowed, "multiplicity has an inadmissible type")
    need(all(type(n) is int and n >= 0 for n in multiplicities.values()),
         "multiplicities must be nonnegative integers")
    chosen = set(selector(dimension)[0])
    bound = Fraction(0)
    for orbit in orbit_partition(dimension):
        count = sum(multiplicities.get(t, 0) for t in orbit)
        bound += Fraction(len(chosen.intersection(orbit)), len(orbit)) * count
    return bound


def check_fitting(dimension, ports, matrix):
    need(set(ports) <= set(types(dimension)), "fitting ports are inadmissible")
    n = len(ports)
    need(len(matrix) == n and all(len(row) == n for row in matrix), "matrix extent")
    for i, (_, w) in enumerate(ports):
        need(matrix[i][i] != 0, "fitting diagonal must be nonzero")
        for j, (q, _) in enumerate(ports):
            need(i == j or not dot(w, q) or matrix[i][j] == 0,
                 "forbidden scalar coefficient")


def beta_five_floor(port_count):
    need(type(port_count) is int and port_count >= 1, "positive port count")
    return 5 * ((3 * port_count + 31) // 32)
