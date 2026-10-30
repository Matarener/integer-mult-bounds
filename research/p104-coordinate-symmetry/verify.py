#!/usr/bin/env python3
"""Exact coordinate stabilizer and invariant-frame census. Apache-2.0."""
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SOURCE = "research/p104-carrier-code-uniqueness/e8/ports.json"
FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
SOURCE_HASH = "ba6a0b9cf76b7cccc1ce8b3d1aa78a4aa329b34d45aded694648f0cf43fc9fce"
SIGMA = (3, 1, 8, 0, 7, 6, 5, 4, 2)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_ports(data):
    require(hashlib.sha256(data).hexdigest() == SOURCE_HASH, "source hash")
    ports = json.loads(data)
    require(isinstance(ports, list) and len(ports) == 104, "port list length")
    require(all(type(x) is int and 0 < x < 512 for x in ports), "port domain")
    require(len(set(ports)) == 104, "distinct ports")
    require({x.bit_count() for x in ports} == {3, 7}, "weight classes")
    return frozenset(ports)


def act(value, permutation):
    return sum(((value >> i) & 1) << permutation[i] for i in range(len(permutation)))


def coordinate_stabilizer(ports):
    missing = {w: frozenset(x for x in range(512)
                           if x.bit_count() == w and x not in ports) for w in (3, 7)}
    require(len(missing[3]) == 14 and len(missing[7]) == 2, "complement sizes")
    group = []
    candidates = 0
    visited = 0
    for permutation in itertools.permutations(range(9)):
        visited += 1
        if frozenset(act(x, permutation) for x in missing[7]) != missing[7]:
            continue
        candidates += 1
        if frozenset(act(x, permutation) for x in missing[3]) == missing[3]:
            require(frozenset(act(x, permutation) for x in ports) == ports,
                    "full port preservation")
            group.append(permutation)
    require(visited == math.factorial(9), "permutation coverage")
    require(candidates == 960, "weight-seven filter count")
    require(group == [tuple(range(9)), SIGMA], "exact stabilizer")
    return group, visited, candidates


def subspaces(n, k):
    """Unique reduced bases with least-set-bit pivots, including the zero space."""
    require(type(n) is int and 0 <= n <= 9, "ambient dimension")
    require(type(k) is int and 0 <= k <= n, "frame dimension")
    for pivots in itertools.combinations(range(n), k):
        free = tuple((i, j) for i, p in enumerate(pivots)
                     for j in range(p + 1, n) if j not in pivots)
        require(len(free) <= 20, "RREF parameter bound")
        for bits in range(1 << len(free)):
            rows = [1 << p for p in pivots]
            for index, (i, j) in enumerate(free):
                rows[i] |= ((bits >> index) & 1) << j
            yield tuple(rows)


def contains(basis, value):
    for row in basis:
        if value & (row & -row):
            value ^= row
    return value == 0


def invariant(basis, action):
    return all(contains(basis, action[row]) for row in basis)


def gaussian(n, k):
    require(type(n) is int and 0 <= n <= 9, "Gaussian ambient dimension")
    if k < 0 or k > n:
        return 0
    numerator = math.prod((1 << (n - j)) - 1 for j in range(k))
    denominator = math.prod((1 << (k - j)) - 1 for j in range(k))
    require(numerator % denominator == 0, "Gaussian integrality")
    return numerator // denominator


def fixed_formula(n, rank, k):
    require(0 <= rank <= n // 2 and 0 <= k <= n <= 9, "nilpotent domain")
    h = n - rank
    total = 0
    for image_dim in range(min(rank, k // 2) + 1):
        kernel_dim = k - image_dim
        if kernel_dim <= h:
            total += (gaussian(rank, image_dim)
                      * gaussian(h - image_dim, k - 2 * image_dim)
                      * (1 << (image_dim * (h - kernel_dim))))
    return total


def census(n, action):
    require(len(action) == 1 << n and action[0] == 0, "linear-action domain")
    totals = []
    fixed = []
    for k in range(n + 1):
        count = stationary = 0
        for basis in subspaces(n, k):
            count += 1
            stationary += invariant(basis, action)
        require(count == gaussian(n, k), "RREF census completeness")
        totals.append(count)
        fixed.append(stationary)
    return totals, fixed


def small_controls():
    domains = checked = 0
    for n in range(7):
        for rank in range(n // 2 + 1):
            permutation = list(range(n))
            for i in range(rank):
                permutation[2 * i], permutation[2 * i + 1] = 2 * i + 1, 2 * i
            action = tuple(act(x, permutation) for x in range(1 << n))
            totals, fixed = census(n, action)
            require(fixed == [fixed_formula(n, rank, k) for k in range(n + 1)],
                    "small Jordan-type formula control")
            domains += 1
            checked += sum(totals)
    return domains, checked


def port_orbits(ports, action):
    orbits = {tuple(sorted({x, action[x]})) for x in ports}
    require(set().union(*(set(o) for o in orbits)) == ports, "port orbit coverage")
    require(sum(map(len, orbits)) == len(ports), "disjoint port orbits")
    sizes = {str(k): sum(len(o) == k for o in orbits) for k in (1, 2)}
    require(sizes == {"1": 8, "2": 48}, "port orbit profile")
    return {"count": len(orbits), "sizes": sizes,
            "fixed_labels": sorted(x for x in ports if action[x] == x)}


def rejection_controls(data, ports, action):
    rejected = 0
    for bad in (data + b" ", data.replace(b"11", b"12", 1)):
        try:
            read_ports(bad)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("corrupt source accepted")
    for n, k in ((10, 1), (9, 10), (-1, 0), (3, -1), (True, 0)):
        try:
            next(subspaces(n, k))
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid Grassmannian accepted")
    wrong = (1, 0, 2, 3, 4, 5, 6, 7, 8)
    require({act(x, wrong) for x in ports} != ports, "false port symmetry rejected")
    require(not invariant((1,), action), "moving line is not invariant")
    require(invariant((1, 8), action), "moving-line orbit plane is invariant")
    require(invariant((11,), action), "fixed-port line is invariant")
    require(sum(action[x] == x for x in range(512)) == 32, "fixed vector count")
    require(len({action[x] ^ x for x in range(512)}) == 16, "nilpotent rank")
    require(all(action[action[x]] == x for x in range(512)), "involution")
    return {"rejections": rejected, "semantic_controls": 7}


def main():
    data = (PACKAGE.parents[1] / SOURCE).read_bytes()
    ports = read_ports(data)
    group, visited, candidates = coordinate_stabilizer(ports)
    action = tuple(act(x, SIGMA) for x in range(512))
    controls = rejection_controls(data, ports, action)
    totals, fixed = census(9, action)
    predicted = [fixed_formula(9, 4, k) for k in range(10)]
    require(fixed == predicted, "all-dimension fixed-frame formula")
    require(fixed == [1, 31, 395, 1955, 4371, 4371, 1955, 395, 31, 1],
            "source fixed-frame profile")
    orbit_counts = [(a + b) // 2 for a, b in zip(totals, fixed)]
    require(all((a + b) % 2 == 0 for a, b in zip(totals, fixed)), "Burnside integrality")
    require(orbit_counts[2] == 21915 and totals[2] == 43435, "plane quotient")
    small_domains, small_frames = small_controls()
    result = {
        "status": "PASS_P104_COORDINATE_SYMMETRY", "errors": 0,
        "claim_type": "finite certificate and scoped counting proof", "new_kappa": False,
        "permutations_checked": visited, "weight_seven_candidates": candidates,
        "group": group, "port_orbits": port_orbits(ports, action),
        "frame_counts_by_dimension": totals, "fixed_frames_by_dimension": fixed,
        "frame_orbits_by_dimension": orbit_counts, "frames_enumerated": sum(totals),
        "small_jordan_domains": small_domains, "small_frames_enumerated": small_frames,
        "controls": controls, "python": platform.python_version(),
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "package_sha256": {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                           for name in FILES},
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
