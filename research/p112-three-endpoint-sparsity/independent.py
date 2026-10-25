"""Separate explicit-coordinate shell and projected-section reconstruction.

Shares only authentication, receipt encoding, and rejection helpers with the primary.
"""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from math import gcd, lcm

from common import PACKAGE, authenticate, digest_rows, read_json, require


def direction(row):
    denominator = lcm(*(Fraction(v).denominator for v in row))
    integers = tuple(int(v * denominator) for v in row)
    divisor = gcd(*integers)
    require(divisor != 0, "zero direction")
    integers = tuple(v // divisor for v in integers)
    return (
        integers if next(v for v in integers if v) > 0 else tuple(-v for v in integers)
    )


def explicit_shell():
    roots, long = set(), set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=8):
        if sum(signs) % 4 == 0:
            roots.add(tuple(signs) if signs[0] == 1 else tuple(-v for v in signs))
    for i in range(8):
        row = [0] * 8
        row[i] = 4
        long.add(tuple(row))
    for indices in combinations(range(8), 4):
        for signs in product((-2, 2), repeat=4):
            row = [0] * 8
            for i, sign in zip(indices, signs, strict=True):
                row[i] = sign
            row = tuple(row)
            long.add(row if next(v for v in row if v) > 0 else tuple(-v for v in row))
    for i in range(8):
        for signs in product((-1, 1), repeat=8):
            row = tuple(3 * v if j == i else v for j, v in enumerate(signs))
            if sum(row) % 4 == 0:
                long.add(row if row[0] > 0 else tuple(-v for v in row))
    require(len(roots) == 120 and len(long) == 1080, "explicit shell counts")
    require(all(sum(v * v for v in row) == 8 for row in roots), "root norm")
    require(all(sum(v * v for v in row) == 16 for row in long), "D7 norm")
    return tuple(sorted(roots)), tuple(sorted(long))


def support_receipt(roots, long):
    frame = set()
    for i in range(0, 8, 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[i + 1] = 2, sign
            frame.add(tuple(row))
    live = set(roots) - frame
    require(len(live) == 112, "literal frame")
    counts = Counter(
        str(sum(sum(x * y for x, y in zip(h, r, strict=True)) != 0 for r in live))
        for h in long
    )
    require(counts == {"70": 128, "73": 896, "76": 56}, "D7 live supports")
    require(
        all(
            sum(sum(x * y for x, y in zip(h, r, strict=True)) == 0 for r in roots) == 42
            for h in long
        ),
        "D7 zero count",
    )
    return dict(sorted(counts.items()))


def sections(lines):
    # The canonical orthogonal roots are a=(0^6,2,-2), b=(0^6,2,2).
    # Normalize at the first nonzero coordinate outside their plane. Within
    # one section all first six coordinates agree exactly, leaving two scalars.
    groups = defaultdict(list)
    for row in lines:
        pivot = next((i for i in range(6) if row[i]), None)
        if pivot is not None:
            normalized = tuple(Fraction(v, row[pivot]) for v in row)
            groups[normalized[:6]].append(normalized)
    return groups


def projected_candidates(groups, lines):
    candidates = set()
    for rows in groups.values():
        require(len(rows) <= 64, "projection section bound")
        for v in rows:
            for w in rows:
                dp, dq = v[6] - w[6], v[7] - w[7]
                if not dp or dp != -dq:
                    continue
                scale = 2 / dp
                u = tuple(scale * x for x in v)
                u_minus_b = u[:6] + (u[6] - 2, u[7] - 2)
                if direction(u_minus_b) in lines:
                    candidates.add(u)
    require(len(candidates) == 360, "separate affine count")
    return candidates


def endpoint_candidates(groups, candidates, lines):
    first, second = set(), set()
    for u in candidates:
        pivot = next(i for i in range(6) if u[i])
        key = tuple(v / u[pivot] for v in u[:6])
        for v in groups[key]:
            scale = u[pivot]
            delta = tuple(x - scale * y for x, y in zip(u, v, strict=True))
            if delta[6] != -delta[7]:
                continue
            t = delta[6] / 2
            if t in (0, 1, -1):
                continue
            first.add(u + (t,))
            u_plus_tb = u[:6] + (u[6] + 2 * t, u[7] + 2 * t)
            if direction(u_plus_tb) in lines:
                second.add(u + (t,))
    require(len(first) == 32 and not second, "separate fifth endpoint exclusion")
    return {
        "first_pencil": len(first),
        "first_parameters": sorted({str(v[-1]) for v in first}),
        "second_pencil": len(second),
        "complete": 0,
        "first_sha256": digest_rows(first),
    }


def direct_incidence():
    triples = tuple(combinations(range(8), 3))
    capacities = []
    for k in range(9):
        active = set(range(k))
        capacities.append(sum(bool(active.intersection(t)) for t in triples))
    require(capacities == [0, 21, 36, 46, 52, 55, 56, 56, 56], "direct triple counts")
    # Independent finite integer DP for the maximal incidence charge outside S.
    maxima = []
    for small in range(15):
        dp = [-100000] * 161
        dp[0] = 0
        for _ in range(112 - small):
            next_dp = [-100000] * 161
            for used in range(161):
                for k in range(min(8, 160 - used) + 1):
                    next_dp[used + k] = max(next_dp[used + k], dp[used] + capacities[k])
            dp = next_dp
        maxima.append(56 * small + max(dp))
    require(max(maxima) == 3772, "separate incidence cap")
    return maxima


def main():
    authenticate()
    roots, long = explicit_shell()
    lines = {direction(r) for r in roots + long}
    groups = sections(lines)
    candidates = projected_candidates(groups, lines)
    fifth = endpoint_candidates(groups, candidates, lines)
    expected = read_json(PACKAGE / "RESULT.json")
    require(
        digest_rows(lines) == expected["shell"]["line_sha256"],
        "shell digest disagreement",
    )
    require(
        support_receipt(roots, long) == expected["shell"]["d7_supports"],
        "support disagreement",
    )
    require(
        digest_rows(candidates) == expected["geometry"]["candidate_sha256"],
        "affine digest disagreement",
    )
    require(fifth == expected["geometry"]["fifth_endpoint"], "pencil disagreement")
    require(
        max(direct_incidence()) == expected["incidence"]["triple_incidence_cap"],
        "charge disagreement",
    )
    print(
        "PASS_SEPARATE_P112_THREE_ENDPOINTS explicit_lines=1200 candidates=360 first=32 second=0 incidence=3772"
    )


if __name__ == "__main__":
    main()
