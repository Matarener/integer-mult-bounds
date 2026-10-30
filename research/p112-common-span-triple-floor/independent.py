"""Separate raw-Gram and finite-field common-span replay. Apache-2.0."""

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).absolute().parent
Q = {
    "MMM": ((1, 1, -1), (1, -1, 1), (-1, 1, 1), (1, 1, 1)),
    "VVV": ((1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)),
}


def check(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    path = HERE / name
    check(not path.is_symlink() and path.is_file(), "regular independent input")
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    check(len(raw) <= 1048576, "independent capacity")
    return json.loads(raw)


def eliminate(columns):
    check(
        len(columns) <= 24
        and all(type(c) is int and 0 <= c < (1 << 24) for c in columns),
        "raw Gram capacity",
    )
    rows = list(columns)
    pivots = 0
    for bit in range(24):
        found = next((j for j in range(pivots, len(rows)) if rows[j] >> bit & 1), None)
        if found is None:
            continue
        rows[pivots], rows[found] = rows[found], rows[pivots]
        for j in range(pivots + 1, len(rows)):
            if rows[j] >> bit & 1:
                rows[j] ^= rows[pivots]
        pivots += 1
    return pivots


def fixture(row):
    labels = [label for group in row["groups"] for label in group]
    check(len(labels) <= 18 and all(0 < x < 256 for x in labels), "fixture capacity")
    planes, targets = [], []
    offset = 0
    for group in row["groups"]:
        check(len(group) in (2, 4, 6), "even independent group")
        check(
            all(
                ((group[i] & group[j]).bit_count() & 1) == (i == j)
                for i, j in itertools.product(range(len(group)), repeat=2)
            ),
            "independent Gram-I",
        )
        planes += [(offset + j, offset + j + 1) for j in range(0, len(group), 2)]
        offset += len(group)
    for g, half in row["targets"]:
        start = sum(map(len, row["groups"][:g]))
        targets.append(tuple(range(start + half, start + len(row["groups"][g]), 2)))
    common = row["groups"][row["targets"][0][0]]
    second = row["groups"][row["targets"][1][0]]
    check(
        eliminate(common + second) == len(common) == len(second),
        "independent common span",
    )
    return labels, planes, targets


def support_pattern(family, part, choice):
    a, b, c = [int(j == part) for j in range(3)]
    if family == "MMM":
        entries = (a + b - choice, a + c - choice, b + c - choice, choice)
    else:
        w = (0, 1, -1)[choice]
        entries = (a + b - c - w, a - b + c - w, -a + b + c - w, 2 * w)
    return tuple(j for j, x in enumerate(entries) if x)


def tables_for(labels, planes, targets, family):
    ports = sum(targets, ())
    closure = [next(pair for pair in planes if port in pair) for port in ports]
    tables = []
    for query in Q[family]:
        sources = sorted(
            {
                p
                for j, target in enumerate(targets)
                if query[j]
                for t in target
                for pair in planes
                if t in pair
                for p in pair
            }
        )
        table = []
        for mask in range(1 << len(ports)):
            readers = sorted(
                {p for j, pair in enumerate(closure) if mask >> j & 1 for p in pair}
            )
            columns = [
                sum(
                    ((labels[s] & labels[r]).bit_count() & 1) << j
                    for j, s in enumerate(sources)
                )
                for r in readers
            ]
            table.append(eliminate(columns))
        tables.append(table)
    return tables


def scientific(row, expected):
    labels, planes, targets = fixture(row)
    parts = [j for j, target in enumerate(targets) for _ in target]
    counts = 0
    for family, alphabet in (("MMM", range(2)), ("VVV", range(3))):
        tables = tables_for(labels, planes, targets, family)
        digest, histogram, minimum, winner = hashlib.sha256(), Counter(), 100, None
        for choices in itertools.product(alphabet, repeat=len(parts)):
            masks = [0] * 4
            for j, (part, choice) in enumerate(zip(parts, choices, strict=True)):
                for term in support_pattern(family, part, choice):
                    masks[term] |= 1 << j
            charges = [tables[j][masks[j]] for j in range(4)]
            bill = sum(charges)
            check(bill >= expected["residual_bound"], "independent residual floor")
            histogram[bill] += 1
            digest.update(bytes(charges))
            if bill < minimum:
                minimum, winner = bill, list(choices)
        actual = {
            "states": sum(histogram.values()),
            "minimum": minimum,
            "w": winner,
            "bill_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "charge_stream_sha256": digest.hexdigest(),
        }
        check(
            actual == expected["families"][family], "independent complete bill stream"
        )
        counts += sum(histogram.values())
    return counts


def atoms(row, expected):
    labels, planes, targets = fixture(row)
    common = row["groups"][row["targets"][0][0]]
    space = {0}
    for vector in common:
        space |= {x ^ vector for x in space}
    ports = targets[0] + targets[1]
    part = [0] * len(targets[0]) + [1] * len(targets[1])
    checks = 0
    for family, alphabet in (("MMM", range(2)), ("VVV", range(3))):
        histogram, digest = Counter(), hashlib.sha256()
        for choices in itertools.product(alphabet, repeat=len(ports)):
            sums, dimensions = {0}, []
            for term in range(4):
                reader = [
                    labels[p]
                    for j, port in enumerate(ports)
                    if term in support_pattern(family, part[j], choices[j])
                    for pair in planes
                    if port in pair
                    for p in pair
                ]
                atom = {
                    v
                    for v in space
                    if all((v & x).bit_count() % 2 == 0 for x in reader)
                }
                dimension = len(atom).bit_length() - 1
                check(len(atom) == 1 << dimension, "independent atom cardinality")
                old = len(sums)
                sums = {a ^ b for a in sums for b in atom}
                check(len(sums) == old * len(atom), "independent direct sum injection")
                dimensions.append(dimension)
            check(len(sums) <= len(space), "joint atom bound")
            histogram[sum(dimensions)] += 1
            digest.update(bytes(dimensions))
            checks += 1
        actual = {
            "states": sum(histogram.values()),
            "dimension_sum_histogram": {
                str(k): v for k, v in sorted(histogram.items())
            },
            "atom_stream_sha256": digest.hexdigest(),
        }
        check(actual == expected[family], "independent atom stream")
    return checks


def field_controls(row):
    labels, _, targets = fixture(row)
    n, checks = len(labels), 0
    axes = [[int(p in target) for p in range(n)] for target in targets]
    for field, family in itertools.product((3, 5, 7), ("MMM", "VVV")):
        inv2, gauge = pow(2, -1, field), (1, 2, 1)
        w = [(p + 1) % field for p in range(n)]
        readers, queries = [], []
        for p in range(n):
            a, b, c = [axis[p] for axis in axes]
            ds = next((gauge[j] for j, axis in enumerate(axes) if axis[p]), 1)
            if family == "MMM":
                u = (
                    (a + b) * inv2 - w[p],
                    (a + c) * inv2 - w[p],
                    (b + c) * inv2 - w[p],
                    w[p],
                )
            else:
                u = (
                    (a + b - c - w[p]) * inv2,
                    (a - b + c - w[p]) * inv2,
                    (-a + b + c - w[p]) * inv2,
                    w[p],
                )
            readers.append(
                [
                    u[i] * ds * pow(i % (field - 1) + 1, -1, field) % field
                    for i in range(4)
                ]
            )
            queries.append(
                [
                    sum(Q[family][i][j] * axes[j][p] for j in range(3))
                    * pow(ds, -1, field)
                    * (i % (field - 1) + 1)
                    % field
                    for i in range(4)
                ]
            )
        for p, r in itertools.product(range(n), repeat=2):
            check(
                (
                    sum(readers[p][i] * queries[r][i] for i in range(4))
                    - sum(axes[j][p] * axes[j][r] for j in range(3))
                )
                % field
                == 0,
                "gauged finite-field affine identity",
            )
            checks += 1
    return checks


def main():
    rows, result = read("FIXTURES.json"), read("RESULT.json")
    check(
        1 <= len(rows) <= 12 and len(rows) == len(result["fixtures"]),
        "independent fixture inventory",
    )
    states, joint, fields = 0, 0, 0
    for row, expected, atom in zip(
        rows, result["fixtures"], result["joint_atoms"], strict=True
    ):
        check(
            row["name"] == expected["name"] == atom["name"], "independent fixture name"
        )
        states += scientific(row, expected)
        joint += atoms(row, atom)
        fields += field_controls(row)
    print(
        "PASS_INDEPENDENT_COMMON_SPAN "
        + json.dumps(
            {
                "bill_assignments": states,
                "joint_atom_assignments": joint,
                "field_operator_entries": fields,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
