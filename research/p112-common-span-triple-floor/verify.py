"""Common-span triple reader theorem. Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import itertools as it
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[1]
PATTERNS = {
    "MMM": ((3, 12), (5, 10), (6, 9)),
    "VVV": ((7, 12, 11), (7, 10, 13), (7, 9, 14)),
}
QUERIES = {
    "MMM": ((1, 1, -1), (1, -1, 1), (-1, 1, 1), (1, 1, 1)),
    "VVV": ((1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    answer = {}
    for key, value in pairs:
        need(key not in answer, "duplicate JSON key")
        answer[key] = value
    return answer


def read_file(path):
    need(path.absolute() == path.resolve() and path.is_file(), "regular input path")
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    need(len(raw) <= 1048576, "input capacity")
    return raw


def load(path):
    return json.loads(read_file(path), object_pairs_hook=unique)


def authenticate():
    manifest = load(HERE / "SOURCES.json")
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    need(1 <= len(rows) <= 16, "source inventory capacity")
    for row in rows:
        path = ROOT / row["path"]
        need(
            path.is_relative_to(ROOT) and path.absolute() == path.resolve(),
            "input alias",
        )
        need(
            hashlib.sha256(read_file(path)).hexdigest() == row["sha256"],
            "source drift",
        )
    retained = manifest["retained_sources"]
    need(len(retained) == 1, "retained source inventory")
    path = HERE / retained[0]["local_path"]
    need(path.parent == HERE and not path.is_symlink(), "retained source path")
    need(
        hashlib.sha256(read_file(path)).hexdigest() == retained[0]["sha256"],
        "retained source drift",
    )


def rank(values, width):
    need(0 <= width <= 32 and len(values) <= 256, "rank capacity")
    need(
        all(type(v) is int and 0 <= v < (1 << width) for v in values),
        "packed rank domain",
    )
    pivots = [0] * width
    for original in values:
        value = original
        for bit in range(width - 1, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(bool(x) for x in pivots)


def geometry(row):
    groups, targets, d = row["groups"], row["targets"], row["common_dimension"]
    need(2 <= d <= 6 and d % 2 == 0 and 1 <= len(groups) <= 3, "geometry capacity")
    need(
        len(targets) == 3 and len({tuple(t) for t in targets}) == 3, "distinct targets"
    )
    labels, pairs, indicators = [], [], []
    for group in groups:
        need(0 < len(group) <= 6 and len(group) % 2 == 0, "even group")
        need(all(type(x) is int and 0 < x < 256 for x in group), "label domain")
        need(
            all(
                (x & y).bit_count() % 2 == int(i == j)
                for i, x in enumerate(group)
                for j, y in enumerate(group)
            ),
            "Gram-I group",
        )
        offset = len(labels)
        labels.extend(group)
        pairs.extend(
            (offset + j - j % 2, offset + j - j % 2 + 1) for j in range(len(group))
        )
    starts = [sum(map(len, groups[:j])) for j in range(len(groups))]
    for g, half in targets:
        need(type(g) is int and 0 <= g < len(groups) and half in (0, 1), "target index")
        indicators.append(tuple(range(starts[g] + half, starts[g] + len(groups[g]), 2)))
    ga, gb, gc = [groups[g] for g, _ in targets]
    need(len(ga) == len(gb) == d and len(gc) <= d, "two largest group sizes")
    need(rank(ga + gb, 8) == d, "common span")
    return labels, pairs, indicators, [len(groups[g]) for g, _ in targets]


def price_tables(family, labels, pairs, targets):
    ports = sum(targets, ())
    need(len(ports) <= 9 and len(set(ports)) == len(ports), "target port capacity")
    tables = []
    for query in QUERIES[family]:
        source = sorted(
            {
                p
                for j, target in enumerate(targets)
                if query[j]
                for t in target
                for p in pairs[t]
            }
        )
        projected = [
            tuple(
                sum(
                    ((labels[p] & labels[r]).bit_count() % 2) << j
                    for j, p in enumerate(source)
                )
                for r in pairs[t]
            )
            for t in ports
        ]
        table = [0] * (1 << len(ports))
        for mask in range(1, len(table)):
            columns = [
                x for j, pair in enumerate(projected) if mask >> j & 1 for x in pair
            ]
            table[mask] = rank(columns, len(source))
        tables.append(table)
    return tables


def masks_for(family, values, parts):
    masks = [0] * 4
    for j, (value, part) in enumerate(zip(values, parts, strict=True)):
        pattern = PATTERNS[family][part][value]
        for term in range(4):
            if pattern >> term & 1:
                masks[term] |= 1 << j
    return masks


def solve_fixture(row):
    labels, pairs, targets, sizes = geometry(row)
    parts = tuple(j for j, target in enumerate(targets) for _ in target)
    output = {}
    for family, alphabet in (("MMM", range(2)), ("VVV", range(3))):
        tables = price_tables(family, labels, pairs, targets)
        digest, histogram, minimum, winner = hashlib.sha256(), Counter(), 100, None
        for values in it.product(alphabet, repeat=len(parts)):
            masks = masks_for(family, values, parts)
            charges = [tables[j][masks[j]] for j in range(4)]
            bill = sum(charges)
            need(bill >= 3 * sizes[0], "common-span residual bound")
            histogram[bill] += 1
            digest.update(bytes(charges))
            if bill < minimum:
                minimum, winner = bill, list(values)
        need(minimum >= sum(sizes), "triple floor")
        output[family] = {
            "states": sum(histogram.values()),
            "minimum": minimum,
            "w": winner,
            "bill_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "charge_stream_sha256": digest.hexdigest(),
        }
    return {
        "name": row["name"],
        "original": sum(sizes),
        "residual_bound": 3 * sizes[0],
        "families": output,
    }


def atom_census(row, family):
    labels, pairs, targets, sizes = geometry(row)
    common = [labels[p] for t in targets[0] for p in pairs[t]]
    space = [0]
    for vector in common:
        space += [x ^ vector for x in space]
    need(len(space) == 1 << sizes[0] and len(set(space)) == len(space), "common basis")
    ports = targets[0] + targets[1]
    parts = (0,) * len(targets[0]) + (1,) * len(targets[1])
    digest, counts = hashlib.sha256(), Counter()
    alphabet = range(2 if family == "MMM" else 3)
    for values in it.product(alphabet, repeat=len(ports)):
        masks = masks_for(family, values, parts)
        atoms, dimensions = [], []
        for mask in masks:
            selected = [
                labels[p]
                for j, port in enumerate(ports)
                if mask >> j & 1
                for p in pairs[port]
            ]
            vectors = [
                v for v in space if all((v & x).bit_count() % 2 == 0 for x in selected)
            ]
            dimension = rank(vectors, 8)
            need(len(vectors) == 1 << dimension, "annihilator size")
            atoms.extend(vectors[1:])
            dimensions.append(dimension)
        # At most d independent pivots are needed, even when an atom is V.
        combined = []
        for vector in atoms:
            if rank([*combined, vector], 8) > len(combined):
                combined.append(vector)
        need(
            len(combined) == sum(dimensions) <= sizes[0], "joint atoms are a direct sum"
        )
        counts[sum(dimensions)] += 1
        digest.update(bytes(dimensions))
    return {
        "states": sum(counts.values()),
        "dimension_sum_histogram": {str(k): v for k, v in sorted(counts.items())},
        "atom_stream_sha256": digest.hexdigest(),
    }


def operator_controls(row):
    labels, _, targets, _ = geometry(row)
    n, checked = len(labels), 0
    a = [[int(p in target) for p in range(n)] for target in targets]
    for family in ("MMM", "VVV"):
        for trial in range(4):
            w = [(p + trial) % 3 - 1 for p in range(n)]
            if family == "MMM":
                readers = [
                    [
                        a[0][p] + a[1][p] - w[p],
                        a[0][p] + a[2][p] - w[p],
                        a[1][p] + a[2][p] - w[p],
                        w[p],
                    ]
                    for p in range(n)
                ]
            else:
                readers = [
                    [
                        a[0][p] + a[1][p] - a[2][p] - w[p],
                        a[0][p] - a[1][p] + a[2][p] - w[p],
                        -a[0][p] + a[1][p] + a[2][p] - w[p],
                        2 * w[p],
                    ]
                    for p in range(n)
                ]
            queries = [
                [
                    sum(QUERIES[family][i][j] * a[j][p] for j in range(3))
                    for p in range(n)
                ]
                for i in range(4)
            ]
            for p, r in it.product(range(n), repeat=2):
                need(
                    sum(readers[p][i] * queries[i][r] for i in range(4))
                    == 2 * sum(a[j][p] * a[j][r] for j in range(3)),
                    "ambient affine operator",
                )
                checked += 1
    return checked


def rational_rank(columns):
    need(
        len(columns) <= 7 and all(len(c) == 3 for c in columns),
        "rational rank capacity",
    )
    rows, count = [list(map(Fraction, c)) for c in columns], 0
    for col in range(3):
        pivot = next((j for j in range(count, len(rows)) if rows[j][col]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        scale = rows[count][col]
        rows[count] = [x / scale for x in rows[count]]
        for j in range(len(rows)):
            if j != count:
                scale = rows[j][col]
                rows[j] = [
                    a - scale * b for a, b in zip(rows[j], rows[count], strict=True)
                ]
        count += 1
    return count


def selective_maps():
    examples = (
        (
            ((-1, 0, 1), (1, 1, 0), (-1, 1, 1), (0, 1, 1)),
            ((1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
        ),
        (
            ((-1, 1, 0), (-1, 0, 1), (-2, 1, 1), (-1, 1, 1)),
            ((1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)),
        ),
    )
    counts = []
    for old, new in examples:
        need(
            all(
                all(not a or b for a, b in zip(n, o, strict=True))
                for n, o in zip(new, old, strict=True)
            ),
            "selective query support",
        )
        true = 0
        for mask, j in it.product(range(16), range(3)):
            target = tuple(int(i == j) for i in range(3))
            selected = [old[i] for i in range(4) if mask >> i & 1]
            if rational_rank([*selected, target]) != rational_rank(selected):
                continue
            binary = [
                sum(x << k for k, x in enumerate(new[i]))
                for i in range(4)
                if mask >> i & 1
            ]
            need(rank([*binary, 1 << j], 3) == rank(binary, 3), "selective target span")
            true += 1
        counts.append(true)
    need(counts == [14, 15], "selective request inventory")
    return {"candidate_requests": 96, "true_requests": counts}


def compute():
    authenticate()
    fixtures = load(HERE / "FIXTURES.json")
    need(type(fixtures) is list and 1 <= len(fixtures) <= 12, "fixture inventory")
    records, atoms, entries = [], [], 0
    for row in fixtures:
        records.append(solve_fixture(row))
        atoms.append(
            {"name": row["name"], **{f: atom_census(row, f) for f in ("MMM", "VVV")}}
        )
        entries += operator_controls(row)
    return {
        "fixtures": records,
        "joint_atoms": atoms,
        "integer_operator_entries": entries,
        "selective_maps": selective_maps(),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == load(HERE / "RESULT.json"), "result receipt")
        print(
            "PASS_COMMON_SPAN_TRIPLE fixtures="
            + str(len(result["fixtures"]))
            + " entries="
            + str(result["integer_operator_entries"])
        )


if __name__ == "__main__":
    main()
