#!/usr/bin/env python3
"""Bounded finite checks of the general-dimensional selector proof."""

import argparse
from collections import deque
from fractions import Fraction as F
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import authenticate


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairing(x, y):
    return (x & y).bit_count() % 2


def coefficient(d):
    need(type(d) is int and d >= 2, "dimension must be at least two")
    if d % 2 == 0:
        return F(d, 2**d)
    if d == 3:
        return F(1, 3)
    t = 2**(d - 2)
    n = 2*t - 1
    return F((d - 2)*t - (d - 1), 2*n*(t - 2))


def expected_orbits(d):
    if d % 2 == 0:
        n, t = 2**(d - 1), 2**(d - 2)
        rows = [(n, d//2), (n*(t - 1), (d//2)*(t - 1))]
    else:
        t = 2**(d - 2)
        n = 2*t - 1
        rows = [(1, 1), (2*n, t), (n, (d - 1)//2),
                (n*(t - 2), ((d - 2)*t - (d - 1))//2)]
    return sorted((size, selected) for size, selected in rows if size)


def check_dimension(d):
    need(2 <= d <= 8, "finite geometry replay is bounded at dimension eight")
    all_vectors = range(2**d)
    odd = [x for x in all_vectors if x.bit_count() % 2]
    universe = {(q, w) for q in odd for w in odd if pairing(q, w)}
    sinks = [w for w in odd if not w & 1]
    chosen = []
    prefix_sizes = []
    for stop, w in enumerate(sinks):
        block = [(q, w) for q in odd if all(pairing(q, x) for x in sinks[:stop + 1])]
        chosen.extend(block)
        prefix_sizes.append(len(block))
    need(len(chosen) == (1 if d == 2 else d*2**(d - 3)), "general prefix size")
    need(sum(q == w for q, w in chosen) == d//2, "general diagonal count")
    if d % 2:
        chosen.append((2**d - 1, 2**d - 1))
    chosen_set = set(chosen)
    need(len(chosen) == len(chosen_set), "general selector uniqueness")
    need(chosen_set <= universe, "general selector domain")
    need(all(pairing(w, q) for i, (_, w) in enumerate(chosen) for q, _ in chosen[i:]),
         "general triangular condition")
    # All even transvections are isometries and involutions. Adjacent swaps
    # and source/sink exchange provide a second explicit orbit certificate.
    even = [a for a in all_vectors if a and a.bit_count() % 2 == 0]
    basis = [1 << k for k in range(d)]
    maps = []
    for a in even:
        table = tuple(x ^ a if pairing(x, a) else x for x in all_vectors)
        need(all(table[table[x]] == x for x in all_vectors), "general involution")
        need(all(pairing(table[x], table[y]) == pairing(x, y) for x in basis for y in basis),
             "general isometry")
        maps.append(table)
    for k in range(d - 1):
        maps.append(tuple(x ^ ((1 << k) | (1 << (k + 1)))
                          if ((x >> k) ^ (x >> (k + 1))) & 1 else x for x in all_vectors))
    unseen, orbits = set(universe), []
    while unseen:
        start = min(unseen)
        found, pending = {start}, deque([start])
        while pending:
            q, w = pending.popleft()
            for value in [(m[q], m[w]) for m in maps] + [(w, q)]:
                need(value in universe, "general orbit domain")
                if value not in found:
                    found.add(value)
                    pending.append(value)
        unseen -= found
        orbits.append(found)
    rows = sorted((len(o), len(o & chosen_set)) for o in orbits)
    need(rows == expected_orbits(d), "general orbit formula")
    need(min(F(selected, size) for size, selected in rows) == coefficient(d),
         "general minimum orbit fraction")
    return {"dimension": d, "types": len(universe), "selector": len(chosen),
            "orbit_incidences": rows, "coefficient": str(coefficient(d))}


def run(maximum):
    authenticate()
    results = [check_dimension(d) for d in range(2, maximum + 1)]
    # These exact comparisons corroborate the written minimum-fraction
    # argument; the all-dimension theorem uses the proof, not this finite list.
    for d in range(5, 50, 2):
        t, n = 2**(d - 2), 2**(d - 1) - 1
        need(t > d - 1, "odd minimum comparison premise")
        need(coefficient(d) <= F(d - 1, 2*n) <= F(t, 2*n) <= 1,
             "odd orbit ordering")
    need(coefficient(5) == F(1, 9) and coefficient(6) == F(3, 32), "source instances")
    need(coefficient(7) < F(3, 63), "wrong orbit chosen as the minimum")
    need(5*coefficient(5) == F(5, 9) and 15*coefficient(5) > 1,
         "dimension-five charge/rank consequences")
    need(2*coefficient(2) == 1, "equal-rank obstruction must be strict")
    return {"status": "PASS_GENERAL_ODD_TYPE_SELECTOR", "dimensions": results,
            "scope": "Finite geometry through dimension eight; PROOF.md supplies all-dimension quantifiers."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-dimension", type=int, choices=range(2, 9), default=8)
    args = parser.parse_args()
    print(json.dumps(run(args.max_dimension), sort_keys=True))
