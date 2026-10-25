"""Two-marked-target non-Fano transfer. Nick Petalas. Apache-2.0."""

import argparse
import itertools as it
import json
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
P = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))
LINES = {(0, 1, 3), (0, 2, 4), (0, 5, 6), (1, 2, 5), (1, 4, 6), (2, 3, 6)}


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path, limit=1_048_576):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "input capacity")
    return raw


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    need(
        sha1(blob, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "source Git blob",
    )


def mul(a, b):
    result = 0
    for _ in range(2):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return result


def elimination(rows, width, binary=False):
    need(0 <= width <= 6 and len(rows) <= 112, "linear capacity")
    need(all(len(row) == width for row in rows), "linear shape")
    if binary:
        need(
            all(type(x) is int and 0 <= x < 4 for row in rows for x in row), "GF4 value"
        )
    a = [list(row) if binary else list(map(F, row)) for row in rows]
    pivots = []
    for col in range(width):
        found = next((j for j in range(len(pivots), len(a)) if a[j][col]), None)
        if found is None:
            continue
        k = len(pivots)
        a[k], a[found] = a[found], a[k]
        inv = (
            next(x for x in range(1, 4) if mul(x, a[k][col]) == 1)
            if binary
            else 1 / a[k][col]
        )
        a[k] = [mul(x, inv) if binary else x * inv for x in a[k]]
        for j in range(len(a)):
            if j != k:
                scale = a[j][col]
                a[j] = [
                    x ^ mul(scale, y) if binary else x - scale * y
                    for x, y in zip(a[j], a[k], strict=True)
                ]
        pivots.append(col)
    return a, pivots


def rank(rows, width=3, binary=False):
    return len(elimination(rows, width, binary)[1])


def solve(rows, rhs, width, binary=False):
    need(len(rows) == len(rhs), "right hand side shape")
    a, pivots = elimination(
        [list(row) + [v] for row, v in zip(rows, rhs, strict=True)], width + 1, binary
    )
    if width in pivots:
        return None
    answer = [0] * width
    for j, col in enumerate(pivots):
        answer[col] = a[j][-1]
    return answer


def det(rows):
    a, b, c = rows
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def matching(pairs):
    return tuple(sorted(tuple(sorted(pair)) for pair in pairs))


def automorphisms():
    outer = (0, 1, 2, 6)
    diagonals = {3: ((0, 1), (2, 6)), 4: ((0, 2), (1, 6)), 5: ((0, 6), (1, 2))}
    lookup = {matching(v): k for k, v in diagonals.items()}
    result = []
    for image in it.permutations(outer):
        mapping = dict(zip(outer, image, strict=True))
        for point, pairs in diagonals.items():
            mapping[point] = lookup[
                matching((mapping[x], mapping[y]) for x, y in pairs)
            ]
        perm = tuple(mapping[i] for i in range(7))
        need(
            {tuple(sorted(perm[i] for i in line)) for line in LINES} == LINES,
            "automorphism",
        )
        result.append(perm)
    need(len(set(result)) == 24, "24 automorphisms")
    return result


def requests(a, b, new):
    ids = [i for i in range(7) if i not in (a, b)]
    counts = [0, 0]
    for target, other in ((a, b), (b, a)):
        for mask in range(32):
            old = [P[j] for i, j in enumerate(ids) if mask >> i & 1]
            dest = [new[j] for i, j in enumerate(ids) if mask >> i & 1]
            if rank(old + [P[target]]) == rank(old):
                need(
                    rank(dest + [new[target]], binary=True) == rank(dest, binary=True),
                    "reader-span request",
                )
                counts[1] += 1
            old += [P[other]]
            if rank(old + [P[target]]) > rank(old):
                dest += [new[other]]
                need(
                    rank(dest + [new[target]], binary=True) > rank(dest, binary=True),
                    "source-zero request",
                )
                counts[0] += 1
    return counts


def lemma():
    dets = {t: det([P[i] for i in t]) for t in it.combinations(range(7), 3)}
    need({k for k, v in dets.items() if not v} == LINES, "six original lines")
    need(set(dets.values()) <= {-2, -1, 0, 1, 2}, "odd-characteristic minors")
    need(
        all(
            any(
                abs(x[i] * y[j] - x[j] * y[i]) == 1
                for i, j in it.combinations(range(3), 2)
            )
            for x, y in it.combinations(P, 2)
        ),
        "odd-characteristic pair minors",
    )
    data = json.loads(read(HERE / "TEMPLATES.json", 8192))
    need(data["polynomial"] == 7, "GF4 polynomial")
    pairs, rows = data["representative_pairs"], data["points"]
    need(pairs == [[0, 1], [0, 3], [3, 4]] and len(rows) == 3, "three pair orbits")
    need(
        all(len(row) == 7 and rank(row, binary=True) == 3 for row in rows),
        "template rank",
    )
    perms = automorphisms()
    images, counts = {}, [0, 0]
    for a, b in it.combinations(range(7), 2):
        choices = [
            (j, perm)
            for j, pair in enumerate(pairs)
            for perm in perms
            if {perm[i] for i in pair} == {a, b}
        ]
        need(bool(choices), "pair orbit coverage")
        j, perm = choices[0]
        new = [None] * 7
        for i in range(7):
            new[perm[i]] = rows[j][i]
        need(rank([new[a], new[b]], binary=True) == 2, "marked independence")
        counts = [x + y for x, y in zip(counts, requests(a, b, new), strict=True)]
        images[a, b] = new
    return images, counts


def geometry():
    meta = json.loads(read(HERE / "SOURCES.json"))
    comparison = json.loads(read(HERE / "COMPARISON.json"))
    authenticate(read(HERE / "PREDECESSOR-PROOF.md"), comparison["predecessor"])
    raw = read(HERE.parents[1] / INPUT)
    authenticate(raw, next(x for x in meta["files"] if x["path"] == INPUT))
    recipes = json.loads(raw)["recipes"]
    need(len(recipes) == 112, "112 recipes")
    labels = [r["q"] for r in sorted(recipes, key=lambda r: r["port"])]
    need(len(set(labels)) == 112 and all(0 < q < 512 for q in labels), "binary labels")
    raw = read(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_partition"])
    groups = json.loads(raw)["orthonormal_groups"]
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for g in groups:
        need(len(g) > 0 and len(g) % 2 == 0, "positive even group")
        need(
            all(
                (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                for p, q in it.product(g, repeat=2)
            ),
            "literal orthonormality",
        )
    owners = {
        p: g[i : i + 2]
        for g in groups
        for i in range(0, len(g), 2)
        for p in g[i : i + 2]
    }
    return labels, owners, [g[side::2] for g in groups for side in range(2)]


def binary_rank(rows):
    need(
        len(rows) <= 224 and all(type(x) is int and 0 <= x < 1 << 224 for x in rows),
        "binary capacity",
    )
    pivots = {}
    for row in rows:
        for bit in range(223, -1, -1):
            if row >> bit & 1:
                if bit in pivots:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return len(pivots)


def cost(labels, owners, q, u):
    source = sorted({j for p, x in enumerate(q) if x for j in owners[p]})
    reader = sorted({j for p, x in enumerate(u) if x for j in owners[p]})
    return binary_rank(
        [
            sum(
                ((labels[x] & labels[y]).bit_count() % 2) << j
                for j, y in enumerate(reader)
            )
            for x in source
        ]
    )


def representations(points, target):
    result = []
    for mask in range(1, 32):
        ids = [i for i in range(5) if mask >> i & 1]
        got = solve([[points[i][j] for i in ids] for j in range(3)], target, len(ids))
        if got is not None:
            row = [0] * 5
            for i, value in zip(ids, got, strict=True):
                row[i] = value
            if row not in result:
                result.append(row)
    need(bool(result), "target represented")
    return result


def fixture(a, b, indicators):
    av, bv = ([int(i in indicators[k]) for i in range(112)] for k in (0, 2))
    ids = [i for i in range(7) if i not in (a, b)]
    points = [P[i] for i in ids]
    third = next(p for p in P if det([P[a], P[b], p]))
    choices = [representations(points, P[t]) for t in (a, b)]
    q, u = [[0] * 112 for _ in range(5)], [[0] * 112 for _ in range(5)]
    for p in range(112):
        t = F((-2, 0, 1, 3)[p % 4], 2) if av[p] or bv[p] else int(p == 111)
        functional = solve([P[a], P[b], third], [av[p], bv[p], t], 3)
        need(functional is not None, "source basis")
        for i in range(5):
            q[i][p] = sum(x * y for x, y in zip(functional, points[i], strict=True))
        if av[p] or bv[p]:
            options = choices[int(bool(bv[p]))]
            for i, value in enumerate(options[p % len(options)]):
                u[i][p] = value
    for free in range(5):
        ids4 = [i for i in range(5) if i != free]
        got = solve([[points[i][j] for i in ids4] for j in range(3)], points[free], 4)
        if got is not None:
            u[free][110] = -1
            for i, value in zip(ids4, got, strict=True):
                u[i][110] = value
            break
    need(not any(av[p] or bv[p] for p in (110, 111)), "spectators")
    return av, bv, q, u


def transfer(a, b, new, av, bv, q, u):
    ids = [i for i in range(7) if i not in (a, b)]
    nq, nu = [[0] * 112 for _ in range(5)], [[0] * 112 for _ in range(5)]
    for p in range(112):
        if not av[p] and not bv[p]:
            continue
        zeros = [i for i in range(5) if not q[i][p]]
        f = solve(
            [new[a], new[b]] + [new[ids[i]] for i in zeros],
            [av[p], bv[p]] + [0] * len(zeros),
            3,
            True,
        )
        need(f is not None, "source request solution")
        selected = [i for i in range(5) if u[i][p]]
        coeff = solve(
            [[new[ids[i]][j] for i in selected] for j in range(3)],
            new[a] if av[p] else new[b],
            len(selected),
            True,
        )
        need(coeff is not None, "reader request solution")
        for i in range(5):
            nq[i][p] = (
                mul(f[0], new[ids[i]][0])
                ^ mul(f[1], new[ids[i]][1])
                ^ mul(f[2], new[ids[i]][2])
            )
        for i, value in zip(selected, coeff, strict=True):
            nu[i][p] = value
    need(
        all(not nq[i][p] or q[i][p] for i in range(5) for p in range(112)),
        "query zeros",
    )
    need(
        all(not nu[i][p] or u[i][p] for i in range(5) for p in range(112)),
        "reader zeros",
    )
    return nq, nu


def operator_check(av, bv, q, u, binary=False):
    for p, r in it.product(range(112), repeat=2):
        value = 0
        for i in range(5):
            value = (
                value ^ mul(u[i][p], q[i][r]) if binary else value + u[i][p] * q[i][r]
            )
        need(value == av[p] * av[r] + bv[p] * bv[r], "literal operator entry")
    return 112 * 112


def expanded(labels, owners, indicators):
    membership = {p: i for i, group in enumerate(indicators) for p in group}
    rows = []
    for p, j in it.product(range(112), range(2)):
        row = 0
        for r, k in it.product(range(112), range(2)):
            value = int(membership[p] == membership[r]) * (
                (labels[owners[p][j]] & labels[owners[r][k]]).bit_count() % 2
            )
            need(value == int(p == r and j == k), "expanded identity entry")
            row |= value << (2 * r + k)
        rows.append(row)
    need(binary_rank(rows) == 224, "expanded identity rank")
    return 224 * 224


def run():
    images, counts = lemma()
    labels, owners, indicators = geometry()
    entries, bills, ranks, fixtures = 0, [], {}, []
    floor = 2 * (len(indicators[0]) + len(indicators[2]))
    for (a, b), new in images.items():
        av, bv, q, u = fixture(a, b, indicators)
        entries += operator_check(av, bv, q, u)
        nq, nu = transfer(a, b, new, av, bv, q, u)
        entries += operator_check(av, bv, nq, nu, True)
        before = [cost(labels, owners, x, y) for x, y in zip(q, u, strict=True)]
        after = [cost(labels, owners, x, y) for x, y in zip(nq, nu, strict=True)]
        need(
            all(x <= y for x, y in zip(after, before, strict=True)),
            "termwise bill domination",
        )
        need(sum(after) >= floor and sum(before) >= floor, "literal pair bill")
        qr, ur = (
            rank(list(zip(*q, strict=True)), 5),
            rank(list(zip(*u, strict=True)), 5),
        )
        need(qr == 3 and ur >= 3, "external factor ranks")
        key = f"{qr},{ur}"
        ranks[key] = ranks.get(key, 0) + 1
        bills.append([a, b, before, after])
        fixtures.append(
            {
                "pair": [a, b],
                "q": pack(q),
                "u": pack(u),
                "new_q": pack(nq),
                "new_u": pack(nu),
            }
        )
    return fixtures, {
        "schema_version": 1,
        "pair_orbits": 3,
        "marked_pairs": 21,
        "request_candidates": 21 * 128,
        "source_zero_requests": counts[0],
        "reader_span_requests": counts[1],
        "factor_rank_counts": ranks,
        "literal_operator_entries": entries,
        "expanded_identity_entries": expanded(labels, owners, indicators),
        "literal_pair_floor": floor,
        "fixture_bills": bills,
        "claim": "Non-Fano five-ray marked-target transfer and actual-reader floor; no new kappa.",
    }


def pack(vectors):
    return [
        {str(p): str(value) for p, value in enumerate(row) if value} for row in vectors
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    fixtures, result = run()
    if args.write_result:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
        (HERE / "FIXTURES.json").write_text(json.dumps(fixtures, indent=2) + "\n")
    else:
        need(result == json.loads(read(HERE / "RESULT.json")), "result receipt")
        need(
            fixtures == json.loads(read(HERE / "FIXTURES.json")),
            "literal fixture receipt",
        )
    print(
        "PASS_NONFANO_MARKED_TRANSFER",
        json.dumps({k: v for k, v in result.items() if k != "fixture_bills"}),
    )


if __name__ == "__main__":
    main()
