#!/usr/bin/env python3
"""Exact finite corroboration of the consecutive-query detour theorem.

Produced by Nick Petalas. Apache-2.0. No predecessor code is imported.
"""

import hashlib
import itertools
import json
import math
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_tariff(table):
    require(2 <= len(table) <= 32, "tariff size outside finite check domain")
    require(table[0] == 0, "nonzero zero-rank tariff")
    increments = [table[i + 1] - table[i] for i in range(len(table) - 1)]
    require(all(x >= 0 for x in increments), "decreasing tariff")
    require(all(a >= b for a, b in zip(increments, increments[1:])),
            "nonconcave tariff")


def check_chain(distance, chain):
    require(3 <= len(chain) <= 10, "need two to nine positive queries")
    require(len(set(chain)) == len(chain), "repeated original chart")
    require(all(0 <= c < len(distance) for c in chain), "chart outside domain")
    positions = [0]
    for a, b in zip(chain, chain[1:]):
        q = distance[a][b]
        require(q > 0, "nonpositive query length")
        positions.append(positions[-1] + q)
    for i, a in enumerate(chain):
        for j, b in enumerate(chain):
            require(distance[a][b] == abs(positions[i] - positions[j]),
                    "original queries do not form a geodesic")
    return positions


def chain_cost(distance, path, tariff):
    return sum(tariff[distance[a][b]] for a, b in zip(path, path[1:]))


def literal_gain(distance, chain, path, tariff):
    require(1 <= len(path) <= 3, "finite checker supports one to three cuts")
    old_target = tariff[distance[chain[0]][chain[-1]]]
    old_paid = chain_cost(distance, chain, tariff)
    new_target = chain_cost(distance, (chain[0], *path, chain[-1]), tariff)
    new_paid = sum(chain_cost(distance, (a, *path, b), tariff)
                   for a, b in zip(chain, chain[1:]))
    return new_target - old_target - new_paid + old_paid


def cancelled_gain(distance, chain, path, tariff):
    baseline = chain_cost(distance, chain, tariff)
    baseline -= tariff[distance[chain[0]][chain[-1]]]
    first = sum(tariff[distance[c][path[0]]] for c in chain[1:-1])
    last = sum(tariff[distance[c][path[-1]]] for c in chain[1:-1])
    interior = chain_cost(distance, path, tariff)
    return baseline - first - last - (len(chain) - 2) * interior


def optimum(distance, chain, tariff):
    costs = [sum(tariff[distance[a][b]] for a in chain[1:-1])
             for b in chain[1:-1]]
    index = costs.index(min(costs)) + 1
    value = chain_cost(distance, chain, tariff)
    value -= tariff[distance[chain[0]][chain[-1]]] + 2 * min(costs)
    return value, chain[index]


def internal_subsets(t):
    require(2 <= t <= 9, "finite partition bound")
    return [tuple(i for i in range(1, t) if mask >> (i - 1) & 1)
            for mask in range(1, 1 << (t - 1))]


def one_point_extensions():
    """Every bounded integer metric extension of unit paths of lengths 2..5."""
    candidates = extensions = median_checks = 0
    for t in range(2, 6):
        subsets = internal_subsets(t)
        pairs = list(itertools.combinations(range(t + 1), 2))
        for radii in itertools.product(range(t + 2), repeat=t + 1):
            candidates += 1
            if any(not (abs(radii[i] - radii[j]) <= j - i <= radii[i] + radii[j])
                   for i, j in pairs):
                continue
            extensions += 1
            for sites in subsets:
                low = max(sites[0], max(i - radii[i] for i in sites))
                high = min(sites[-1], min(i + radii[i] for i in sites))
                require(low <= high, "interval projection failed")
                require(all(abs(low - i) <= radii[i] for i in sites),
                        "projection did not dominate every coordinate")
                for h in range(1, t + 2):
                    ambient = sum(min(radii[i], h) for i in sites)
                    endpoint = min(sum(min(abs(i - j), h) for i in sites)
                                   for j in sites)
                    require(ambient >= endpoint, "ambient median beats endpoint")
                    median_checks += 1
    return {"candidate_vectors": candidates, "metric_extensions": extensions,
            "hinge_median_checks": median_checks}


def symplectic(a, b, n):
    mask = (1 << n) - 1
    return (((a & mask) & (b >> n)).bit_count()
            + ((b & mask) & (a >> n)).bit_count()) & 1


def span(basis):
    values = {0}
    for v in basis:
        values |= {x ^ v for x in values}
    return frozenset(values)


def lagrangians(n):
    require(n in (2, 3), "finite symplectic domain")
    spaces = set()
    for basis in itertools.combinations(range(1, 1 << (2 * n)), n):
        if any(symplectic(a, b, n) for a, b in itertools.combinations(basis, 2)):
            continue
        space = span(basis)
        if len(space) == 1 << n:
            spaces.add(space)
    return sorted(spaces, key=lambda s: tuple(sorted(s)))


def chart_fixture(n):
    spaces = lagrangians(n)
    require(len(spaces) == (15 if n == 2 else 135), "wrong chart enumeration")
    distance = [[n - (len(a & b).bit_length() - 1) for b in spaces]
                for a in spaces]
    chain = []
    for j in range(n + 1):
        basis = [1 << (i if i < j else n + i) for i in range(n)]
        chain.append(spaces.index(span(basis)))
    require(check_chain(distance, chain) == list(range(n + 1)),
            "canonical chain distances")
    for i, row in enumerate(distance):
        require(row[i] == 0, "nonzero chart self-distance")
        for j, dij in enumerate(row):
            require(dij == distance[j][i], "asymmetric chart distance")
            require(all(dij <= row[k] + distance[k][j] for k in range(len(spaces))),
                    "chart distance violates triangle inequality")
    return distance, tuple(chain)


def verify_paths(distance, chain, max_cuts):
    check_chain(distance, chain)
    maximum_distance = max(max(row) for row in distance)
    paths = invoice_checks = attainments = 0
    for h in range(1, maximum_distance + 1):
        tariff = tuple(min(r, h) for r in range(maximum_distance + 1))
        check_tariff(tariff)
        best, endpoint = optimum(distance, chain, tariff)
        for m in range(1, max_cuts + 1):
            observed = None
            for path in itertools.product(range(len(distance)), repeat=m):
                literal = literal_gain(distance, chain, path, tariff)
                reduced = cancelled_gain(distance, chain, path, tariff)
                require(literal == reduced, "literal invoice multiplicity differs")
                require(literal <= best, "path beats predicted maximum")
                observed = literal if observed is None else max(observed, literal)
                paths += 1
                invoice_checks += 1
            require(observed == best, "enumerated maximum differs")
            require(literal_gain(distance, chain, (endpoint,) * m, tariff) == best,
                    "constant endpoint path fails to attain")
            attainments += 1
    return {"path_tariff_checks": paths, "literal_cancellations": invoice_checks,
            "maxima_and_attainments": attainments}


def rank_nine_corollary():
    require(44 ** 100 < 9 ** 99 * 5 ** 100, "exact power threshold fails")
    partitions = 0
    for t in range(3, 10):
        for sites in internal_subsets(t):
            if len(sites) < 2:
                continue
            require(all(any(abs(i - j) >= 1 for i in sites) for j in sites),
                    "missing unit median penalty")
            positions = (0, *sites, t)
            lengths = [b - a for a, b in zip(positions, positions[1:])]
            require(min(lengths) >= 1 and sum(lengths) == t, "partition defect")
            partitions += 1
    scale = 10 ** 12
    root = math.isqrt(19 * scale * scale)
    require(root * root < 19 * scale * scale < (root + 1) ** 2,
            "positive example radical enclosure")
    lower = 5 * scale - root - 1
    upper = 5 * scale - root
    require(lower > 0, "larger-rank positive example lost")
    return {"positive_integer_partitions_k_at_least_three": partitions,
            "rank_nine_gain_strict_upper": "-9/5",
            "sqrt_positive_gain_interval": [f"{lower}/{scale}", f"{upper}/{scale}"]}


def boundary_controls():
    controls = 0
    for tariff in ((1, 2), (0, -1), (0, 1, 3), (0,)):
        try:
            check_tariff(tariff)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid tariff was accepted")
    line = [[abs(i - j) for j in range(4)] for i in range(4)]
    tariff = tuple(range(4))
    chain, path = (0, 1, 2, 3), (1, 2)
    exact = literal_gain(line, chain, path, tariff)
    wrong_interior = chain_cost(line, chain, tariff) - tariff[3]
    wrong_interior -= sum(tariff[line[c][f]] for c in chain[1:-1] for f in path)
    require(exact != wrong_interior, "omitted interior multiplicity escaped")
    wrong_debit = chain_cost(line, (chain[0], *path, chain[-1]), tariff)
    wrong_debit -= sum(chain_cost(line, (a, *path, b), tariff)
                       for a, b in zip(chain, chain[1:]))
    wrong_debit += chain_cost(line, chain, tariff)
    require(exact != wrong_debit, "omitted original target debit escaped")
    controls += 2
    # Nongeodesic internal sites: three leaves, then their star center.
    star = [[0 if i == j else 1 if 3 in (i, j) else 2 for j in range(4)]
            for i in range(4)]
    leaf_min = min(sum(star[i][j] for i in range(3)) for j in range(3))
    require(sum(star[i][3] for i in range(3)) == 3 < leaf_min == 4,
            "nongeodesic counterexample")
    require(1 ** 2 + 1 ** 2 < 0 ** 2 + 2 ** 2,
            "convex-tariff interior counterexample")
    controls += 2
    try:
        check_chain(star, (0, 1, 2))
    except ValueError:
        controls += 1
    else:
        raise ValueError("nongeodesic query chain accepted")
    return controls


def main():
    require(len(sys.argv) == 1, "this bounded verifier accepts no arguments")
    result = {"status": "PASS_CONSECUTIVE_QUERY_DETOUR",
              "claim_type": "scoped proof with finite corroboration"}
    result["one_point_extensions"] = one_point_extensions()
    distance, chain = chart_fixture(3)
    result["three_qubit_lagrangians"] = len(distance)
    profiles = ((chain[0], chain[1], chain[3]),
                (chain[0], chain[2], chain[3]), chain)
    result["three_qubit_profiles"] = [verify_paths(distance, c, 2) for c in profiles]
    small_distance, small_chain = chart_fixture(2)
    result["two_qubit_three_cut_paths"] = verify_paths(small_distance, small_chain, 3)
    result["power_corollary"] = rank_nine_corollary()
    result["boundary_controls"] = boundary_controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                        for name in names}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
