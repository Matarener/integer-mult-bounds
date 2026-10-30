"""Four-term actual-reader floor checks. Nick Petalas. Apache-2.0."""

import argparse
import itertools as it
import json
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
TRIPLES = tuple(it.combinations(range(6), 3))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, limit=1_048_576):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "input capacity")
    return raw


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256")
    header = b"blob " + str(len(raw)).encode() + b"\0"
    need(
        sha1(header + raw, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "source blob",
    )


def mul(a, b):
    result = 0
    for _ in range(4):
        if b & 1:
            result ^= a
        a <<= 1
        if a & 16:
            a ^= 19
        b >>= 1
    return result


def solve(rows, rhs, width, binary=False):
    """One solution with free variables zero, or None. Dimensions <= 6."""
    need(width <= 6 and len(rows) <= 6, "linear capacity")
    a = [list(row) + [value] for row, value in zip(rows, rhs, strict=True)]
    pivot = []
    for col in range(width):
        found = next((j for j in range(len(pivot), len(a)) if a[j][col]), None)
        if found is None:
            continue
        k = len(pivot)
        a[k], a[found] = a[found], a[k]
        inv = (
            next(i for i in range(1, 16) if mul(a[k][col], i) == 1)
            if binary
            else 1 / F(a[k][col])
        )
        a[k] = [mul(x, inv) if binary else x * inv for x in a[k]]
        for j in range(len(a)):
            if j == k:
                continue
            scale = a[j][col]
            a[j] = [
                x ^ mul(scale, y) if binary else x - scale * y
                for x, y in zip(a[j], a[k], strict=True)
            ]
        pivot.append(col)
    if any(not any(row[:width]) and row[-1] for row in a):
        return None
    result = [0] * width
    for j, col in enumerate(pivot):
        result[col] = a[j][-1]
    return result


def det(points, binary=False):
    a, b, c = points
    if binary:
        return (
            mul(a[0], mul(b[1], c[2]) ^ mul(b[2], c[1]))
            ^ mul(a[1], mul(b[0], c[2]) ^ mul(b[2], c[0]))
            ^ mul(a[2], mul(b[0], c[1]) ^ mul(b[1], c[0]))
        )
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def signature(points, binary=False):
    return sum(
        (det([points[i] for i in triple], binary) == 0) << j
        for j, triple in enumerate(TRIPLES)
    )


def templates():
    e, f, g = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    return [
        [(1, t, mul(t, t)) for t in range(6)],
        [e, f, (1, 1, 0), g, (1, 2, 1), (1, 3, 2)],
        [e, f, (1, 1, 0), g, (1, 2, 1), (2, 4, 3)],
        [e, f, (1, 1, 0), g, (1, 0, 1), (1, 2, 4)],
        [e, f, g, (1, 1, 0), (1, 0, 1), (0, 1, 2)],
        [e, f, g, (1, 1, 0), (1, 0, 1), (0, 1, 1)],
        [e, f, (1, 1, 0), (1, 2, 0), g, (1, 0, 1)],
        [e, f, (1, 1, 0), (1, 2, 0), g, (1, 4, 1)],
        [e, f, (1, 1, 0), (1, 2, 0), (1, 4, 0), g],
    ]


def catalogue():
    declared = json.loads(read(HERE / "TEMPLATES.json", 8192))
    need(declared["field_polynomial"] == 19, "template polynomial")
    need(
        declared["points"] == [[list(p) for p in row] for row in templates()],
        "template table matches proof",
    )
    images = {}
    line_counts = []
    for points in templates():
        need(all(any(p) for p in points), "nonzero template points")
        need(
            all(
                any(
                    mul(a[j], b[k]) ^ mul(a[k], b[j])
                    for j, k in it.combinations(range(3), 2)
                )
                for a, b in it.combinations(points, 2)
            ),
            "simple template points",
        )
        line_counts.append(signature(points, True).bit_count())
        for order in it.permutations(range(6)):
            permuted = [points[i] for i in order]
            images.setdefault(signature(permuted, True), permuted)
    need(line_counts == [0, 1, 2, 2, 3, 4, 5, 4, 10], "nine template incidences")
    need(len(images) == 352, "labeled incidence types")
    return images, line_counts


def classify(images):
    counts = []
    for count in range(5):
        total = 0
        for lines in it.combinations(range(20), count):
            triples = [set(TRIPLES[i]) for i in lines]
            if any(len(a & b) > 1 for a, b in it.combinations(triples, 2)):
                continue
            if any(sum(p in t for t in triples) > 2 for p in range(6)):
                continue
            need(sum(1 << i for i in lines) in images, "short-line coverage")
            total += 1
        counts.append(total)
    return counts


def requests(old, new):
    count = 0
    for mask, target in it.product(range(16), (4, 5)):
        indices = [i for i in range(4) if mask >> i & 1]
        old_rows = [[old[i][j] for i in indices] for j in range(3)]
        new_rows = [[new[i][j] for i in indices] for j in range(3)]
        x = solve(old_rows, old[target], len(indices))
        y = solve(new_rows, new[target], len(indices), True)
        need((x is None) == (y is None), "reader span request")
        rows = [old[4], old[5]] + [old[i] for i in indices]
        rhs = [int(target == 4), int(target == 5)] + [0] * len(indices)
        x = solve(rows, rhs, 3)
        rows = [new[4], new[5]] + [new[i] for i in indices]
        y = solve(rows, rhs, 3, True)
        need((x is None) == (y is None), "source zero request")
        count += 2
    return count


def rational_configurations(images):
    points = [(1, y, z) for y, z in it.product((-1, 0, 1), repeat=2)]
    points += [(0, 1, z) for z in (-1, 0, 1)] + [(0, 0, 1)]
    axes = [(1, 0, 0), (0, 1, 0)]
    queries = [p for p in points if p not in axes]
    configs = total = 0
    for subset in it.combinations(queries, 4):
        old = list(subset) + axes
        total += requests(old, images[signature(old)])
        configs += 1
    return configs, total


def degenerate_checks():
    a, b, c, zero = (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)
    examples = [
        ([a, b, zero, (1, 1, 0), a, b], [a, b, zero, (1, 1, 0), a, b]),
        ([a, b, (1, 2, 0), (2, 3, 0), a, b], [a, b, (1, 1, 0), (1, 2, 0), a, b]),
        ([c, (0, 0, 2), a, b, a, b], [c, c, a, b, a, b]),
        ([c, zero, a, b, a, b], [c, zero, a, b, a, b]),
    ]
    return sum(requests(old, new) for old, new in examples)


def rank(rows, width):
    pivots = [0] * width
    for row in rows:
        for bit in range(width - 1, -1, -1):
            if row >> bit & 1:
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return sum(bool(p) for p in pivots)


def geometry():
    meta = json.loads(read(HERE / "SOURCES.json", 32768))
    pin = next(p for p in meta["files"] if p["usage"] == "input")
    need(pin["path"] == INPUT, "input path")
    raw = read(HERE.parents[1] / INPUT)
    authenticate(raw, pin)
    recipes = json.loads(raw)["recipes"]
    need(len(recipes) == 112, "112 recipes")
    labels = [r["q"] for r in sorted(recipes, key=lambda r: r["port"])]
    need(len(set(labels)) == 112 and all(0 < q < 512 for q in labels), "labels")
    raw = read(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_rank32"])
    groups = json.loads(raw)["orthonormal_groups"]
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for group in groups:
        need(len(group) % 2 == 0, "even group")
        need(
            all(
                (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                for p, q in it.product(group, repeat=2)
            ),
            "orthonormality",
        )
    owners = {
        p: g[i : i + 2]
        for g in groups
        for i in range(0, len(g), 2)
        for p in g[i : i + 2]
    }
    indicators = [g[side::2] for g in groups for side in range(2)]
    return labels, owners, indicators


def cost(labels, owners, source, reader):
    s = sorted({q for p, value in enumerate(source) if value for q in owners[p]})
    t = sorted({q for p, value in enumerate(reader) if value for q in owners[p]})
    rows = [
        sum(((labels[p] & labels[q]).bit_count() % 2) << j for j, q in enumerate(t))
        for p in s
    ]
    return rank(rows, len(t))


def expanded(labels, owners, indicators):
    group = {p: i for i, indicator in enumerate(indicators) for p in indicator}
    checked = 0
    for p, q, j, k in it.product(range(112), range(112), range(2), range(2)):
        value = int(group[p] == group[q]) * (
            (labels[owners[p][j]] & labels[owners[q][k]]).bit_count() % 2
        )
        need(value == int(p == q and j == k), "expanded I224")
        checked += 1
    return checked


def literal_fixture(pair, indicators):
    a, b = [set(indicators[i]) for i in pair]
    av = [int(p in a) for p in range(112)]
    bv = [int(p in b) for p in range(112)]
    c = [F((-1, 0, 1, 2)[p % 4]) for p in range(112)]
    d = [F((0, 1, -1, 2)[p % 4]) for p in range(112)]
    need(any(c[p] for p in range(112) if p not in a | b), "external source direction")
    need(any(d[p] for p in range(112) if p not in a | b), "external reader direction")
    outside = [p for p in range(112) if p not in a | b]
    need(
        any(c[p] and not d[p] for p in outside)
        and any(d[p] and not c[p] for p in outside),
        "two independent external directions",
    )
    queries = [
        [av[p] + c[p] for p in range(112)],
        [bv[p] + c[p] for p in range(112)],
        c,
        [av[p] + bv[p] + 2 * c[p] for p in range(112)],
    ]
    readers = [
        [av[p] - d[p] for p in range(112)],
        [bv[p] - d[p] for p in range(112)],
        [-av[p] - bv[p] for p in range(112)],
        d,
    ]
    return av, bv, queries, readers


def transfer(new, av, bv, queries, readers):
    q = [[0] * 112 for _ in range(4)]
    u = [[0] * 112 for _ in range(4)]
    for p in range(112):
        zeros = [i for i in range(4) if not queries[i][p]]
        rows = [new[4], new[5]] + [new[i] for i in zeros]
        x = solve(rows, [av[p], bv[p]] + [0] * len(zeros), 3, True)
        need(x is not None, "source functional exists")
        for i in range(4):
            q[i][p] = mul(new[i][0], x[0]) ^ mul(new[i][1], x[1]) ^ mul(new[i][2], x[2])
            need(not q[i][p] or queries[i][p], "source support inclusion")
        active = [i for i in range(4) if readers[i][p]]
        rows = [[new[i][j] for i in active] for j in range(3)]
        target = [mul(av[p], new[4][j]) ^ mul(bv[p], new[5][j]) for j in range(3)]
        y = solve(rows, target, len(active), True)
        need(y is not None, "reader coefficients exist")
        for i, value in zip(active, y, strict=True):
            u[i][p] = value
    return q, u


def operators(av, bv, q, u, binary=False):
    for p, r in it.product(range(112), repeat=2):
        expected = av[p] * av[r] + bv[p] * bv[r]
        if binary:
            actual = 0
            for i in range(4):
                actual ^= mul(u[i][p], q[i][r])
        else:
            actual = sum(u[i][p] * q[i][r] for i in range(4))
        need(actual == expected, "exact pair operator")


def literal_checks(images):
    labels, owners, indicators = geometry()
    entries = expanded(labels, owners, indicators)
    old = [(1, 0, 1), (0, 1, 1), (0, 0, 1), (1, 1, 2), (1, 0, 0), (0, 1, 0)]
    new = images[signature(old)]
    receipt = []
    for pair in [(0, 1), (0, 2), (0, 30), (16, 17), (20, 30), (28, 29)]:
        av, bv, q, u = literal_fixture(pair, indicators)
        operators(av, bv, q, u)
        nq, nu = transfer(new, av, bv, q, u)
        operators(av, bv, nq, nu, True)
        before = [cost(labels, owners, q[i], u[i]) for i in range(4)]
        after = [cost(labels, owners, nq[i], nu[i]) for i in range(4)]
        floor = 2 * sum(len(indicators[i]) for i in pair)
        need(
            cost(labels, owners, av, av) + cost(labels, owners, bv, bv) == floor,
            "original terms attain floor",
        )
        need(all(y <= x for x, y in zip(before, after, strict=True)), "termwise tariff")
        need(sum(after) >= floor, "literal pair floor")
        receipt.append({"pair": pair, "before": before, "after": after, "floor": floor})
    return entries, receipt


def run():
    images, counts = catalogue()
    classification = classify(images)
    configs, requests_count = rational_configurations(images)
    degenerate_requests = degenerate_checks()
    entries, fixtures = literal_checks(images)
    return {
        "template_dependent_triples": counts,
        "short_line_counts": classification,
        "labeled_types": len(images),
        "rational_configurations": configs,
        "span_and_zero_requests": requests_count,
        "expanded_entries": entries,
        "degenerate_requests": degenerate_requests,
        "literal_fixtures": fixtures,
        "operator_entries": 2 * 6 * 112 * 112,
        "claim": "Sharp four-term pair-reader floor over every field and even orthonormal partition; no new kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run()
    raw = (json.dumps(result, indent=2) + "\n").encode()
    if args.write:
        (HERE / "RESULT.json").write_bytes(raw)
    else:
        need(read(HERE / "RESULT.json", 32768) == raw, "result receipt")
    print("PASS_FOUR_TERM_PAIR", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
