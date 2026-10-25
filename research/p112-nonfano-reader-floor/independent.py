"""Separate GF16/determinant and literal-array replay. Nick Petalas. Apache-2.0."""

import itertools
import json
import re
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parent
OLD = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, limit=1_048_576):
    with (BASE / name).open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "independent capacity")
    return json.loads(data)


def product(x, y):
    raw = 0
    for bit in range(4):
        if y >> bit & 1:
            raw ^= x << bit
    for bit in range(6, 3, -1):
        if raw >> bit & 1:
            raw ^= 19 << (bit - 4)
    return raw


def determinant(points, characteristic=0):
    a, b, c = points
    if characteristic == 2:
        return (
            product(a[0], product(b[1], c[2]) ^ product(b[2], c[1]))
            ^ product(a[1], product(b[0], c[2]) ^ product(b[2], c[0]))
            ^ product(a[2], product(b[0], c[1]) ^ product(b[1], c[0]))
        )
    value = (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )
    return value % characteristic if characteristic else value


def dimension(points, characteristic=0):
    nonzero = [p for p in points if any(p)]
    if not nonzero:
        return 0
    for pair in itertools.combinations(nonzero, 2):
        for i, j in itertools.combinations(range(3), 2):
            if characteristic == 2:
                minor = product(pair[0][i], pair[1][j]) ^ product(
                    pair[0][j], pair[1][i]
                )
            else:
                minor = pair[0][i] * pair[1][j] - pair[0][j] * pair[1][i]
                if characteristic:
                    minor %= characteristic
            if minor:
                return (
                    3
                    if any(
                        determinant(t, characteristic)
                        for t in itertools.combinations(nonzero, 3)
                    )
                    else 2
                )
    return 1


def validated_templates():
    templates = load("TEMPLATES.json")
    require(
        templates["polynomial"] == 7
        and templates["representative_pairs"] == [[0, 1], [0, 3], [3, 4]],
        "independent templates",
    )
    require(
        len(templates["points"]) == 3
        and all(
            len(row) == 7
            and all(
                len(p) == 3 and all(type(x) is int and 0 <= x < 4 for x in p)
                for p in row
            )
            for row in templates["points"]
        ),
        "independent template capacity",
    )
    return templates


def marked_lemma():
    lines = {
        t
        for t in itertools.combinations(range(7), 3)
        if determinant([OLD[i] for i in t]) == 0
    }
    perms = [
        p
        for p in itertools.permutations(range(7))
        if {tuple(sorted(p[i] for i in line)) for line in lines} == lines
    ]
    require(len(perms) == 24, "independent automorphisms")
    templates = validated_templates()
    require(
        all(any(product(x, y) == 1 for y in range(1, 16)) for x in range(1, 16)),
        "GF16 field inverses",
    )
    omega = next(x for x in range(2, 16) if product(x, x) ^ x ^ 1 == 0)
    embed = [0, 1, omega, omega ^ 1]
    cases = 0
    for a, b in itertools.combinations(range(7), 2):
        choices = [
            (pair, row, p)
            for pair, row in zip(
                templates["representative_pairs"], templates["points"], strict=True
            )
            for p in perms
            if {p[i] for i in pair} == {a, b}
        ]
        require(bool(choices), "independent pair coverage")
        _, row, perm = choices[-1]
        new = [None] * 7
        for i in range(7):
            new[perm[i]] = [embed[x] for x in row[i]]
        ids = [i for i in range(7) if i not in (a, b)]
        for prime in (0, 3, 5, 7):
            for target, other in ((a, b), (b, a)):
                for mask in range(32):
                    old = [OLD[i] for j, i in enumerate(ids) if mask >> j & 1]
                    dest = [new[i] for j, i in enumerate(ids) if mask >> j & 1]
                    if dimension(old + [OLD[target]], prime) == dimension(old, prime):
                        require(
                            dimension(dest + [new[target]], 2) == dimension(dest, 2),
                            "independent reader span",
                        )
                    old += [OLD[other]]
                    if dimension(old + [OLD[target]], prime) > dimension(old, prime):
                        dest += [new[other]]
                        require(
                            dimension(dest + [new[target]], 2) > dimension(dest, 2),
                            "independent source zeros",
                        )
                    cases += 2
    return embed, cases


def decode(rows, binary=False):
    require(len(rows) == 5, "five independent factors")
    result = []
    for row in rows:
        require(
            len(row) <= 112
            and all(str(int(p)) == p and 0 <= int(p) < 112 for p in row),
            "literal port",
        )
        values = [0] * 112
        for port, value in row.items():
            require(
                isinstance(value, str)
                and re.fullmatch(r"-?[0-9]{1,6}(?:/[1-9][0-9]{0,5})?", value)
                is not None,
                "bounded rational literal",
            )
            values[int(port)] = int(value) if binary else Fraction(value)
            if binary:
                require(0 <= values[int(port)] < 4, "literal GF4 value")
        result.append(values)
    return result


def span(vectors):
    values = {0}
    require(
        len(vectors) <= 112 and all(0 <= v < 512 for v in vectors),
        "binary label capacity",
    )
    for vector in vectors:
        values |= {x ^ vector for x in values}
        require(len(values) <= 512, "binary span capacity")
    return values


def tariff(labels, closure, q, u):
    sources = {labels[j] for p, v in enumerate(q) if v for j in closure[p]}
    readers = sorted({labels[j] for p, v in enumerate(u) if v for j in closure[p]})
    images = {
        sum(((x & y).bit_count() % 2) << i for i, y in enumerate(readers))
        for x in span(sources)
    }
    require(len(images) & (len(images) - 1) == 0, "image power of two")
    return len(images).bit_length() - 1


def literal_geometry():
    recipes = load("../adaptive-kernel-demotion/inputs/DATA-PHASES.json")["recipes"]
    require(
        len(recipes) == 112 and sorted(r["port"] for r in recipes) == list(range(112)),
        "independent recipe capacity",
    )
    labels = [row["q"] for row in sorted(recipes, key=lambda row: row["port"])]
    require(
        len(set(labels)) == 112 and all(type(x) is int and 0 < x < 512 for x in labels),
        "independent labels",
    )
    groups = load("RETAINED-RANK32.json")["orthonormal_groups"]
    require(
        len(groups) <= 56
        and all(0 < len(g) <= 112 and len(g) % 2 == 0 for g in groups),
        "independent group capacity",
    )
    require(
        sorted(p for g in groups for p in g) == list(range(112)),
        "independent partition",
    )
    require(
        all(
            (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
            for group in groups
            for p, q in itertools.product(group, repeat=2)
        ),
        "independent Gram",
    )
    closure = {
        p: g[i : i + 2]
        for g in groups
        for i in range(0, len(g), 2)
        for p in g[i : i + 2]
    }
    aa, bb = set(groups[0][::2]), set(groups[1][::2])
    return labels, closure, aa, bb


def literal(embedding):
    labels, closure, aa, bb = literal_geometry()
    fixtures = load("FIXTURES.json")
    receipt = load("RESULT.json")
    require(len(fixtures) == 21, "21 literal fixtures")
    entries = 0
    for fixture, bill in zip(fixtures, receipt["fixture_bills"], strict=True):
        require(fixture["pair"] == bill[:2], "literal order")
        q, u = decode(fixture["q"]), decode(fixture["u"])
        nq, nu = decode(fixture["new_q"], True), decode(fixture["new_u"], True)
        require(
            all(not nq[i][p] or q[i][p] for i in range(5) for p in range(112)),
            "independent query support",
        )
        require(
            all(not nu[i][p] or u[i][p] for i in range(5) for p in range(112)),
            "independent reader support",
        )
        for p, r in itertools.product(range(112), repeat=2):
            expected = int(p in aa and r in aa) + int(p in bb and r in bb)
            require(
                sum(u[i][p] * q[i][r] for i in range(5)) == expected,
                "independent rational operator",
            )
            value = 0
            for i in range(5):
                value ^= product(embedding[nu[i][p]], embedding[nq[i][r]])
            require(value == expected, "independent GF16 operator")
            entries += 2
        before = [tariff(labels, closure, x, y) for x, y in zip(q, u, strict=True)]
        after = [tariff(labels, closure, x, y) for x, y in zip(nq, nu, strict=True)]
        require(before == bill[2] and after == bill[3], "independent actual tariffs")
        require(
            all(x <= y for x, y in zip(after, before, strict=True))
            and sum(after) >= 16,
            "independent bill floor",
        )
    require(entries == receipt["literal_operator_entries"], "independent entry count")
    return entries


def main():
    embedding, requests = marked_lemma()
    entries = literal(embedding)
    print(
        "PASS_INDEPENDENT_NONFANO",
        json.dumps(
            {
                "GF16_embedding": embedding,
                "request_candidates": requests,
                "literal_entries": entries,
            }
        ),
    )


if __name__ == "__main__":
    main()
