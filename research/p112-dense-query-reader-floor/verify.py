"""Dense pair-query actual-reader floor. Nick Petalas. Apache-2.0."""

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


def read(path, maximum=1_048_576):
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    need(len(raw) <= maximum, "input capacity")
    return raw


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256")
    header = b"blob " + str(len(raw)).encode() + b"\0"
    need(
        sha1(header + raw, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "source Git blob",
    )


def load():
    meta = json.loads(read(HERE / "SOURCES.json", 32768))
    pins = [row for row in meta["files"] if row["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == INPUT, "source inventory")
    raw = read(ROOT / INPUT)
    authenticate(raw, pins[0])
    recipes = json.loads(raw)["recipes"]
    need(type(recipes) is list and len(recipes) == 112, "112 recipes")
    need(all(type(row["port"]) is int for row in recipes), "integer ports")
    need(sorted(row["port"] for row in recipes) == list(range(112)), "port IDs")
    labels = [row["q"] for row in sorted(recipes, key=lambda row: row["port"])]
    need(all(type(q) is int and 0 < q < 512 for q in labels), "nine-bit labels")
    need(len(set(labels)) == 112, "distinct labels")
    raw = read(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_rank32"])
    groups = json.loads(raw)["orthonormal_groups"]
    need(type(groups) is list and len(groups) == 16, "sixteen groups")
    need(all(type(g) is list and len(g) in (4, 6, 8) for g in groups), "groups")
    need(all(type(p) is int for g in groups for p in g), "integer group ports")
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for group in groups:
        need(
            all(
                (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                for p in group
                for q in group
            ),
            "orthonormal group",
        )
    return labels, groups


def rank(rows, width):
    need(len(rows) <= 112 and 0 <= width <= 112, "rank capacity")
    pivots = [0] * width
    for row in rows:
        need(type(row) is int and 0 <= row < 1 << width, "binary row")
        for bit in range(width - 1, -1, -1):
            if row >> bit & 1:
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return sum(bool(p) for p in pivots)


def closure(support, owners):
    return sorted({q for p in support for q in owners[p]})


def cost(labels, source, reader):
    rows = [
        sum(
            ((labels[p] & labels[q]).bit_count() % 2) << j for j, q in enumerate(reader)
        )
        for p in source
    ]
    return rank(rows, len(reader))


def geometry(groups):
    owners = {}
    indicators = []
    for group in groups:
        for j in range(0, len(group), 2):
            for port in group[j : j + 2]:
                owners[port] = group[j : j + 2]
        indicators.extend((group[::2], group[1::2]))
    need(len(owners) == 112 and len(indicators) == 32, "geometry capacity")
    return owners, indicators


def census(labels, owners, indicators):
    histogram = {}
    subsets = 0
    for a, b in itertools.combinations(indicators, 2):
        ports = a + b
        source = closure(ports, owners)
        need(len(ports) <= 8 and not set(a) & set(b), "pair capacity")
        for mask in range(1 << len(ports)):
            support = [p for j, p in enumerate(ports) if mask >> j & 1]
            bill = cost(labels, source, closure(support, owners))
            d_a = 2 * sum(p in support for p in a)
            d_b = 2 * sum(p in support for p in b)
            need(bill >= max(d_a, d_b), "two independent column sets")
            need(2 * bill >= d_a + d_b, "rank two-cover inequality")
            gap = 2 * bill - d_a - d_b
            histogram[gap] = histogram.get(gap, 0) + 1
            subsets += 1
    return subsets, dict(sorted(histogram.items()))


def fixture(a, b, count):
    need(count in (2, 4, 7), "fixture query capacity")
    directions = [(F(1), F(j + 1)) for j in range(count)]
    readers = [[F(0)] * 112 for _ in directions]
    for p in a + b:
        i, j = p % count, (p + 1) % count
        x, y = F(p in a), F(p in b)
        s, t = directions[i][1], directions[j][1]
        readers[i][p], readers[j][p] = (t * x - y) / (t - s), (y - s * x) / (t - s)
    if count > 2:
        outside = next(p for p in range(112) if p not in a + b)
        for j, value in enumerate((-1, 2, -1)):
            readers[j][outside] = F(value)
    return directions, readers


def check_fixture(labels, owners, a, b, directions, readers):
    need(2 <= len(directions) <= 16, "query list capacity")
    need(len(readers) == len(directions), "reader count")
    need(all(len(row) == 112 for row in readers), "reader capacity")
    need(all(x and y for x, y in directions), "dense queries required")
    source = closure(a + b, owners)
    total = 0
    covers = [0, 0]
    for row in readers:
        support = [p for p, v in enumerate(row) if v]
        bill = cost(labels, source, closure(support, owners))
        d_a = 2 * sum(bool(row[p]) for p in a)
        d_b = 2 * sum(bool(row[p]) for p in b)
        need(2 * bill >= d_a + d_b, "fixture rank two-cover")
        total += bill
        covers[0] += d_a
        covers[1] += d_b
    for p in range(112):
        actual = tuple(
            sum(row[p] * v[j] for v, row in zip(directions, readers, strict=True))
            for j in range(2)
        )
        need(actual == (int(p in a), int(p in b)), "exact pair operator")
        if p in a + b:
            need(sum(bool(row[p]) for row in readers) >= 2, "target two-cover")
    floor = 2 * (len(a) + len(b))
    need(covers[0] >= 4 * len(a) and covers[1] >= 4 * len(b), "coverage floor")
    need(total >= 4 * max(len(a), len(b)), "dense pair reader floor")
    need(total >= floor, "pair reader floor")
    return total, floor


def run():
    labels, groups = load()
    owners, indicators = geometry(groups)
    subsets, histogram = census(labels, owners, indicators)
    bills = []
    for index in range(32):
        a, b = indicators[index], indicators[index ^ 1]
        if index % 2:
            b = indicators[(index + 5) % 32]
        for count in (2, 4, 7):
            directions, readers = fixture(a, b, count)
            bill, floor = check_fixture(labels, owners, a, b, directions, readers)
            bills.append(
                {
                    "a": index,
                    "b_ports": b,
                    "queries": count,
                    "bill": bill,
                    "floor": floor,
                    "dense_floor": 4 * max(len(a), len(b)),
                }
            )
    same = [r for r in bills if r["a"] % 2 == 0 and r["queries"] == 2]
    need(len(same) == 16 and all(r["bill"] == r["floor"] for r in same), "attainment")
    return {
        "pairs": 496,
        "reader_support_subsets": subsets,
        "two_cost_minus_coverage_histogram": histogram,
        "rational_fixtures": len(bills),
        "compressed_operator_entries": 112 * 2 * len(bills),
        "same_group_two_query_attainments": len(same),
        "fixtures": bills,
        "claim": (
            "all-field dense rank-two query lists have actual-reader cost "
            ">= 2 max(m_A,m_B)"
        ),
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run()
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        (HERE / "RESULT.json").write_text(serialized)
    else:
        need(
            json.loads(read(HERE / "RESULT.json", 65536)) == json.loads(serialized),
            "receipt",
        )
    print(
        "PASS_DENSE_PAIR_READER_FLOOR",
        result["reader_support_subsets"],
        "subsets",
        len(result["fixtures"]),
        "fixtures",
    )


if __name__ == "__main__":
    main()
