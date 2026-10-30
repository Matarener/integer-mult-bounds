"""Pair-span reader floor by extension-field transfer. Nick Petalas. Apache-2.0."""

import argparse
import itertools
import json
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"


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


def load():
    meta = json.loads(read(HERE / "SOURCES.json", 32768))
    pins = [r for r in meta["files"] if r["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == INPUT, "input inventory")
    raw = read(ROOT / INPUT)
    authenticate(raw, pins[0])
    rows = json.loads(raw)["recipes"]
    need(type(rows) is list and len(rows) == 112, "112 recipes")
    need(all(type(r["port"]) is int for r in rows), "integer ports")
    need(sorted(r["port"] for r in rows) == list(range(112)), "port IDs")
    labels = [r["q"] for r in sorted(rows, key=lambda r: r["port"])]
    need(all(type(q) is int and 0 < q < 512 for q in labels), "nine-bit labels")
    need(len(set(labels)) == 112, "distinct labels")
    raw = read(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_rank32"])
    groups = json.loads(raw)["orthonormal_groups"]
    need(type(groups) is list and len(groups) == 16, "sixteen groups")
    need(all(type(g) is list and len(g) in (4, 6, 8) for g in groups), "group sizes")
    need(all(type(p) is int for g in groups for p in g), "integer group ports")
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for g in groups:
        need(
            all(dot(labels[p], labels[q]) == int(p == q) for p in g for q in g),
            "orthonormal group",
        )
    return labels, groups


def dot(a, b):
    return (a & b).bit_count() % 2


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


def mul(a, b):
    value = 0
    for _ in range(6):
        if b & 1:
            value ^= a
        a <<= 1
        if a & 64:
            a ^= 67
        b >>= 1
    return value


def inverse(a):
    need(0 < a < 64, "nonzero field divisor")
    result = 1
    for _ in range(62):
        result = mul(result, a)
    need(mul(a, result) == 1, "field inverse")
    return result


def solve(d, e, target):
    a, b = d
    c, h = e
    x, y = target
    reciprocal = inverse(mul(a, h) ^ mul(b, c))
    return mul(mul(x, h) ^ mul(y, c), reciprocal), mul(
        mul(a, y) ^ mul(b, x), reciprocal
    )


def geometry(groups):
    owners = {}
    indicators = []
    for g in groups:
        indicators.extend((g[::2], g[1::2]))
        for j in range(0, len(g), 2):
            for p in g[j : j + 2]:
                owners[p] = g[j : j + 2]
    return owners, indicators


def closure(support, owners):
    return sorted({q for p in support for q in owners[p]})


def cost(labels, source, reader):
    rows = [
        sum(dot(labels[p], labels[q]) << j for j, q in enumerate(reader))
        for p in source
    ]
    return rank(rows, len(reader))


def literal_identity(labels, groups, owners, indicators):
    owner = {p: k for k, row in enumerate(indicators) for p in row}
    for p in range(112):
        for q in range(112):
            for j, k in itertools.product(range(2), repeat=2):
                value = int(owner[p] == owner[q]) * dot(
                    labels[owners[p][j]], labels[owners[q][k]]
                )
                need(value == int(p == q and j == k), "expanded I224")
    bill = sum(cost(labels, g, g) * 2 for g in groups)
    need(bill == 224, "literal tariff 224")
    return bill


def fixture(a, b, count, offset):
    directions = [(F(1), F(0)), (F(0), F(1))]
    directions.extend((F(1), F(j)) for j in range(1, count - 1))
    readers = [[F(0)] * 112 for _ in directions]
    for p in a + b:
        i, j = (p + offset) % count, (p + offset + 3) % count
        x, y = F(p in a), F(p in b)
        c, d = directions[i]
        e, h = directions[j]
        determinant = c * h - d * e
        readers[i][p], readers[j][p] = (
            (x * h - y * e) / determinant,
            (c * y - d * x) / determinant,
        )
    outside = next(p for p in range(112) if p not in a + b)
    for j, value in enumerate((-1, -1, 1)):
        readers[j][outside] += F(value)
    old = readers[2]
    readers[2] = [value / 2 for value in old]
    readers.append([value / 4 for value in old])
    directions.append(tuple(2 * value for value in directions[2]))
    directions.append((F(0), F(0)))
    readers.append([F(7)] * 112)
    return directions, readers


def classify(directions, readers):
    need(
        2 <= len(directions) <= 32 and len(directions) == len(readers), "query capacity"
    )
    need(all(len(r) == 112 for r in readers), "reader capacity")
    classes = {}
    for i, (x, y) in enumerate(directions):
        if x or y:
            key = (F(1), y / x) if x else (F(0), F(1))
            classes.setdefault(key, []).append(i)
    need(2 <= len(classes) <= 32, "class capacity")
    images = []
    for key in classes:
        images.append(
            (1, 0)
            if key == (1, 0)
            else (0, 1)
            if key == (0, 1)
            else (1, len(images) + 1)
        )
    need(len(set(images)) == len(images), "injective images")
    return list(classes.items()), images


def transfer(a, b, classes, images, readers):
    result = [[0] * 112 for _ in images]
    for p in range(112):
        target = (int(p in a), int(p in b))
        if target == (0, 0):
            continue
        active = [
            j
            for j, (_, indices) in enumerate(classes)
            if any(readers[i][p] for i in indices)
        ]
        need(bool(active), "target needs active class")
        matching = [j for j in active if classes[j][0] == target]
        if matching:
            need(images[matching[0]] == target, "axis fixed")
            result[matching[0]][p] = 1
        else:
            need(len(active) >= 2, "target needs two directions")
            i, j = active[:2]
            result[i][p], result[j][p] = solve(images[i], images[j], target)
    return result


def check_operator(a, b, directions, readers, extension=False):
    for p in range(112):
        actual = [0, 0]
        for d, row in zip(directions, readers, strict=True):
            for k in range(2):
                if extension:
                    actual[k] ^= mul(row[p], d[k])
                else:
                    actual[k] += row[p] * d[k]
        need(actual == [int(p in a), int(p in b)], "pair operator")


def check_tariffs(labels, owners, a, b, readers, classes, images, converted):
    old_total = 0
    new_total = 0
    for j, (key, indices) in enumerate(classes):
        source = closure((a if key[0] else []) + (b if key[1] else []), owners)
        old_union = set()
        subtotal = 0
        for i in indices:
            support = [p for p, value in enumerate(readers[i]) if value]
            old_union.update(support)
            subtotal += cost(labels, source, closure(support, owners))
        support = [p for p, value in enumerate(converted[j]) if value]
        need(set(support) <= old_union, "reader support containment")
        image = images[j]
        new_source = closure((a if image[0] else []) + (b if image[1] else []), owners)
        need(set(new_source) <= set(source), "query support containment")
        union_bill = cost(labels, source, closure(old_union, owners))
        new_bill = cost(labels, new_source, closure(support, owners))
        need(new_bill <= union_bill <= subtotal, "grouped tariff comparison")
        old_total += subtotal
        new_total += new_bill
    floor = 2 * (len(a) + len(b))
    need(old_total >= new_total >= floor, "pair reader floor")
    return old_total, new_total


def run():
    for a in range(1, 64):
        inverse(a)
    labels, groups = load()
    owners, indicators = geometry(groups)
    literal_identity(labels, groups, owners, indicators)
    histogram = {}
    fixtures = 0
    classes_checked = 0
    for index, (a, b) in enumerate(itertools.combinations(indicators, 2)):
        for count in (6, 11):
            directions, readers = fixture(a, b, count, index)
            check_operator(a, b, directions, readers)
            classes, images = classify(directions, readers)
            converted = transfer(a, b, classes, images, readers)
            check_operator(a, b, images, converted, extension=True)
            old, new = check_tariffs(
                labels, owners, a, b, readers, classes, images, converted
            )
            key = f"{old},{new},{2 * (len(a) + len(b))}"
            histogram[key] = histogram.get(key, 0) + 1
            fixtures += 1
            classes_checked += len(classes)
    return {
        "claim": (
            "all-field finite pair-span lists have sharp actual-reader floor m_A+m_B"
        ),
        "field": "GF(64), polynomial x^6+x+1; finite check, written proof uses F2(t)",
        "pairs": 496,
        "rational_to_extension_fixtures": fixtures,
        "grouped_tariff_comparisons": classes_checked,
        "operator_coordinate_checks": fixtures * 112 * 2 * 2,
        "expanded_identity_entries": 224**2,
        "literal_tariff": 224,
        "old_new_floor_histogram": dict(sorted(histogram.items())),
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.write:
        (HERE / "RESULT.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n"
        )
    else:
        need(json.loads(read(HERE / "RESULT.json")) == result, "receipt")
    print(
        "PASS_EXTENSION_FIELD_PAIR_READER_FLOOR",
        result["rational_to_extension_fixtures"],
        "fixtures",
    )


if __name__ == "__main__":
    main()
