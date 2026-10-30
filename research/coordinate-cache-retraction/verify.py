#!/usr/bin/env python3
"""Finite corroboration of the coordinate-chart retraction. Standard library only."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def echelon(rows, prime, width):
    require(type(prime) is int and prime in (2, 3, 5), "unsupported finite-check field")
    require(1 <= width <= 6 and len(rows) <= 6, "matrix capacity exceeded")
    require(all(len(row) == width for row in rows), "ragged matrix")
    require(all(type(x) is int for row in rows for x in row), "noninteger entry")
    matrix = [[x % prime for x in row] for row in rows]
    pivots = []
    for column in range(width):
        candidates = [i for i in range(len(pivots), len(matrix)) if matrix[i][column]]
        if not candidates:
            continue
        index = len(pivots)
        matrix[index], matrix[candidates[0]] = matrix[candidates[0]], matrix[index]
        scale = pow(matrix[index][column], -1, prime)
        matrix[index] = [(x * scale) % prime for x in matrix[index]]
        for i in range(len(matrix)):
            if i != index:
                factor = matrix[i][column]
                matrix[i] = [(x - factor * y) % prime
                             for x, y in zip(matrix[i], matrix[index])]
        pivots.append(column)
    return tuple(tuple(row) for row in matrix[:len(pivots)]), tuple(pivots)


def pairing(left, right):
    n = len(left) // 2
    return sum(left[i] * right[-1-i] - left[-1-i] * right[i] for i in range(n))


def coordinate_rows(mask, width):
    return tuple(tuple(int(i == j) for j in range(width))
                 for i in range(width) if mask & (1 << i))


def retract(rows, prime, n):
    require(type(n) is int and 1 <= n <= 3, "chart dimension exceeded")
    basis, pivots = echelon(rows, prime, 2*n)
    require(len(basis) == n, "not a full chart")
    require(all(pairing(a, b) % prime == 0 for a in basis for b in basis),
            "not isotropic")
    mask = sum(1 << i for i in pivots)
    require(all(not (mask & (1 << i) and mask & (1 << (2*n-1-i)))
                for i in range(n)), "paired pivot invariant failed")
    return mask


def all_rref_planes(prime, n):
    require(prime in (2, 3, 5) and 1 <= n <= 3, "unsupported census")
    patterns = []
    for pivots in itertools.combinations(range(2*n), n):
        free = tuple((i, j) for i in range(n) for j in range(2*n)
                     if j not in pivots and j > pivots[i])
        patterns.append((pivots, free))
    require(sum(prime ** len(free) for _, free in patterns) <= 4096,
            "census capacity exceeded")
    for pivots, free in patterns:
        for entries in itertools.product(range(prime), repeat=len(free)):
            rows = [[0] * (2*n) for _ in range(n)]
            for i, column in enumerate(pivots):
                rows[i][column] = 1
            for (i, j), value in zip(free, entries):
                rows[i][j] = value
            yield tuple(tuple(row) for row in rows)


def literal_span(rows, prime, width):
    require(prime ** len(rows) <= 125, "span capacity exceeded")
    return frozenset(tuple(sum(c * row[j] for c, row in zip(coefficients, rows))
                           % prime for j in range(width))
                     for coefficients in itertools.product(range(prime), repeat=len(rows)))


def chart_domain(prime, n, expected):
    planes = tuple(all_rref_planes(prime, n))
    charts = tuple(rows for rows in planes
                   if all(pairing(a, b) % prime == 0 for a in rows for b in rows))
    require(len(charts) == expected and len(charts) <= 256, "chart census mismatch")
    spans = tuple(literal_span(rows, prime, 2*n) for rows in charts)
    masks = tuple(retract(rows, prime, n) for rows in charts)
    for rows, span, mask in zip(charts, spans, masks):
        require(len(span) == prime**n, "dependent census basis")
        leading = {next(i for i, x in enumerate(v) if x) for v in span if any(v)}
        require(mask == sum(1 << i for i in leading), "literal leading positions disagree")
        require(retract(coordinate_rows(mask, 2*n), prime, n) == mask,
                "retraction is not idempotent")
    require(len(set(masks)) == 2**n, "coordinate image incomplete")
    return planes, charts, spans, masks


def check_domain(prime, n, expected):
    planes, charts, spans, masks = chart_domain(prime, n, expected)
    dimensions = {prime**i: i for i in range(n+1)}
    attained = set()
    strict = 0
    for i in range(len(charts)):
        for j in range(len(charts)):
            common = spans[i] & spans[j]
            distance = n - dimensions[len(common)]
            projected = n - (masks[i] & masks[j]).bit_count()
            require(projected <= distance, "distance increased")
            common_leads = {next(k for k, x in enumerate(v) if x)
                            for v in common if any(v)}
            require(all((masks[i] & masks[j]) & (1 << k) for k in common_leads),
                    "intersection-leading inclusion failed")
            attained.add((distance, projected))
            strict += projected < distance
    tariffs = tuple((0,) + values for values in
                    itertools.combinations_with_replacement(range(4), n))
    for tariff in tariffs:
        for distance, projected in attained:
            require(tariff[projected] <= tariff[distance], "monotone price increased")
    return {"field": prime, "n": n, "all_planes": len(planes), "charts": len(charts),
            "coordinate_charts": len(set(masks)), "ordered_pairs": len(charts)**2,
            "strict_contractions": strict, "tariff_distance_checks": len(tariffs)*len(attained)}


def fixed_tree_check():
    _, charts, spans, masks = chart_domain(2, 2, 15)
    lookup = {rows: i for i, rows in enumerate(charts)}
    terminals = tuple(lookup[coordinate_rows(mask, 4)] for mask in sorted(set(masks)))
    dims = {1: 0, 2: 1, 4: 2}
    price = (0, 2, 3)
    costs = tuple(tuple(price[2-dims[len(a & b)]] for b in spans) for a in spans)
    projected = tuple(lookup[coordinate_rows(mask, 4)] for mask in masks)
    count = 0
    minima = []
    # All three four-leaf binary topologies, retaining zero-length edges.
    for split in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
        a, b, c, d = (terminals[i] for i in split)
        full, restricted = [], []
        for u, v in itertools.product(range(len(charts)), repeat=2):
            value = costs[a][u]+costs[b][u]+costs[u][v]+costs[v][c]+costs[v][d]
            pu, pv = projected[u], projected[v]
            after = costs[a][pu]+costs[b][pu]+costs[pu][pv]+costs[pv][c]+costs[pv][d]
            require(after <= value, "whole tree price increased")
            full.append(value)
            if u in terminals and v in terminals:
                restricted.append(value)
            count += 1
        require(min(full) == min(restricted), "restricted tree minimum changed")
        minima.append(min(full))
    return {"labeled_trees": count, "minimum_prices_in_half_units": minima}


def expect_rejection(rows, prime, n):
    try:
        retract(rows, prime, n)
    except ValueError:
        return
    raise ValueError("malformed chart accepted")


def controls():
    for rows, prime, n in (((), 2, 1), (((1, 0),), 4, 1),
                           (((1, 0, 0),), 2, 1), (((1.0, 0),), 2, 1),
                           (((1, 0, 0, 0), (1, 0, 0, 0)), 2, 2),
                           (((1, 0, 0, 0), (0, 0, 0, 1)), 2, 2),
                           (((1, 0),), 2, 4)):
        expect_rejection(rows, prime, n)
    left, right = ((1, 0),), ((1, 1),)
    require(retract(left, 2, 1) == retract(right, 2, 1), "strict witness lost")
    require(literal_span(left, 2, 2) & literal_span(right, 2, 2) == {(0, 0)},
            "strict witness not distinct")
    before, after = 1, 0
    require(-after > -before, "negative-edge control failed")
    decreasing = (1, 0)
    require(decreasing[after] > decreasing[before], "decreasing tariff control failed")
    # An interleaved order e1,f1,e2,f2 makes naive pivots nonisotropic.
    interleaved = ((1, 0, 1, 0), (0, 1, 0, 2))
    _, bad_pivots = echelon(interleaved, 3, 4)
    require(bad_pivots == (0, 1), "bad-order control lost")
    a, b = interleaved
    require((a[0]*b[1]-a[1]*b[0]+a[2]*b[3]-a[3]*b[2]) % 3 == 0,
            "original interleaved plane not isotropic")
    require(retract(((1, 1, 0, 0), (0, 0, 2, 1)), 3, 2) == 5,
            "self-dual order correction failed")
    projected_rows = coordinate_rows(retract(right, 2, 1), 2)
    require(projected_rows != right, "noncoordinate terminal was fixed")
    return {"invalid_charts_rejected": 7, "scope_controls": 4}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", action="store_true", help="print a generated hash-bound record")
    args = parser.parse_args()
    domains = [check_domain(p, n, expected) for p, n, expected in
               ((2, 1, 3), (3, 1, 4), (5, 1, 6), (2, 2, 15),
                (3, 2, 40), (5, 2, 156), (2, 3, 135))]
    result = {"status": "PASS_COORDINATE_CACHE_RETRACTION", "domains": domains,
              "tree": fixed_tree_check(), "controls": controls()}
    if args.emit_result:
        package = Path(__file__).resolve().parent
        result["sha256"] = {name: hashlib.sha256((package/name).read_bytes()).hexdigest()
                            for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                                         "VERIFY.json", "verify.py")}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
