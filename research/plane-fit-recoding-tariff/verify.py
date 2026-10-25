#!/usr/bin/env python3
"""Exact full-plane tariffs for a fixed P112 group-fit row space.

Nick Petalas. Apache-2.0. See TASK.json for assistance disclosure.
"""

import json
from collections import Counter
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
PORTS = 112
GROUPS = 16
CHANNELS = 32


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, row):
    need(sha256(raw).hexdigest() == row["sha256"], "source SHA256 differs")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    need(
        sha1(blob, usedforsecurity=False).hexdigest() == row["git_blob"],
        "source Git blob differs",
    )


def read_bounded(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "input byte capacity exceeded")
    return raw


def load():
    meta = json.loads(read_bounded(HERE / "SOURCES.json", 32768))
    pins = [row for row in meta["files"] if row["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == SOURCE, "live source inventory")
    raw = read_bounded(ROOT / SOURCE, 2097152)
    authenticate(raw, pins[0])
    recipes = json.loads(raw)["recipes"]
    need(len(recipes) == PORTS, "selected port count")
    need(sorted(row["port"] for row in recipes) == list(range(PORTS)), "port IDs")
    labels = [row["q"] for row in sorted(recipes, key=lambda row: row["port"])]
    need(len(set(labels)) == PORTS, "distinct labels")
    need(all(type(q) is int and 0 < q < 512 for q in labels), "nine-bit labels")
    raw = read_bounded(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_rank32"])
    cert = json.loads(raw)
    return labels, cert["orthonormal_groups"]


def validate_partition(labels, groups):
    need(len(groups) == GROUPS, "sixteen groups")
    need(all(type(g) is list and len(g) in (4, 6, 8) for g in groups), "even groups")
    ports = [p for g in groups for p in g]
    need(all(type(p) is int for p in ports), "integer port IDs")
    need(sorted(ports) == list(range(PORTS)), "exact port partition")
    for group in groups:
        for i in group:
            for j in group:
                need(
                    (labels[i] & labels[j]).bit_count() % 2 == int(i == j),
                    "group Gram identity",
                )
    need(Counter(map(len, groups)) == {8: 11, 6: 2, 4: 3}, "source group sizes")


def basis_bits(rows, width=9):
    """At most 112 rows, each with at most nine bits, in the scientific path."""
    need(0 <= width <= 9 and len(rows) <= PORTS, "binary elimination bounds")
    basis = [0] * width
    for original in rows:
        value = original
        need(type(value) is int and 0 <= value < 1 << width, "binary row bounds")
        for bit in range(width - 1, -1, -1):
            if value & (1 << bit):
                if basis[bit]:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return tuple(row for row in basis if row)


def gram_rank(basis):
    rows = [
        sum(((x & y).bit_count() % 2) << j for j, y in enumerate(basis)) for x in basis
    ]
    return len(basis_bits(rows, len(basis)))


def closure_table(labels, groups):
    """Enumerate every possible full-plane closure of a row-space query."""
    count = 1 << GROUPS
    spaces = [()] * count
    costs = [0] * count
    lower = [0] * count
    cache = {}
    for mask in range(1, count):
        bit = mask & -mask
        group_id = bit.bit_length() - 1
        previous = mask ^ bit
        spaces[mask] = basis_bits(
            list(spaces[previous]) + [labels[p] for p in groups[group_id]]
        )
        basis = spaces[mask]
        if basis not in cache:
            cache[basis] = gram_rank(basis)
        costs[mask] = cache[basis]
        lower[mask] = max(lower[previous], len(groups[group_id]))
        need(costs[mask] >= lower[mask], "full-plane rank below contained identity")
    return costs


def rank_mod(matrix, prime):
    need(1 <= len(matrix) <= 64, "query count in 1..64")
    need(all(len(row) == CHANNELS for row in matrix), "32 support coefficients")
    need(prime in (2, 3, 5, 1000003), "declared exact field")
    need(all(type(x) is int for row in matrix for x in row), "integer coefficients")
    rows = [[x % prime for x in row] for row in matrix]
    rank = 0
    for column in range(CHANNELS):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [x * inverse % prime for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            factor = rows[i][column]
            rows[i] = [
                (x - factor * y) % prime
                for x, y in zip(rows[i], rows[rank], strict=True)
            ]
        rank += 1
    return rank


def query_bill(coefficients, prime, costs):
    need(
        rank_mod(coefficients, prime) == CHANNELS, "queries do not span fixed row space"
    )
    masks = [
        sum(
            1 << g
            for g in range(GROUPS)
            if row[2 * g] % prime or row[2 * g + 1] % prime
        )
        for row in coefficients
    ]
    bill = sum(costs[mask] for mask in masks)
    need(bill >= 224, "weighted basis tariff bound violated")
    return bill


def coordinates(query, groups, prime):
    """Reject queries outside the fixed row space, rather than extending the claim."""
    need(
        len(query) == PORTS and all(type(x) is int for x in query), "112 scalar entries"
    )
    need(prime in (2, 3, 5, 1000003), "declared exact field")
    result = []
    for group in groups:
        for side in (0, 1):
            values = {query[p] % prime for p in group[side::2]}
            need(len(values) == 1, "query outside fixed group-fit row space")
            result.append(values.pop())
    return result


def literal_mask(labels, groups):
    pairs = [g[j : j + 2] for g in groups for j in range(0, len(g), 2)]
    owner = {p: i for i, pair in enumerate(pairs) for p in pair}
    supports = [g[side::2] for g in groups for side in (0, 1)]
    channel = {p: i for i, support in enumerate(supports) for p in support}
    forced = 0
    for i in range(PORTS):
        for j in range(PORTS):
            orthogonal = all(
                (labels[x] & labels[y]).bit_count() % 2 == 0
                for x in pairs[owner[i]]
                for y in pairs[owner[j]]
            )
            if i == j or not orthogonal:
                forced += 1
                need(int(channel[i] == channel[j]) == int(i == j), "strict scalar mask")
    return channel, forced


def dense_factorization(channel, prime):
    """Check UQ=K on every entry for C=I+J and C^-1=I-J/33."""
    need(prime in (2, 5, 1000003), "33 must be invertible")
    inverse = pow(33, -1, prime)
    coefficient = [
        [(int(i == j) + 1) % prime for j in range(CHANNELS)] for i in range(CHANNELS)
    ]
    decoder = [
        [(int(i == j) - inverse) % prime for j in range(CHANNELS)]
        for i in range(CHANNELS)
    ]
    for i in range(PORTS):
        for j in range(PORTS):
            value = (
                sum(
                    decoder[channel[i]][k] * coefficient[k][channel[j]]
                    for k in range(CHANNELS)
                )
                % prime
            )
            need(
                value == int(channel[i] == channel[j]),
                "dense UQ differs from literal K",
            )
    return coefficient


def run():
    labels, groups = load()
    validate_partition(labels, groups)
    costs = closure_table(labels, groups)
    channel, forced = literal_mask(labels, groups)
    identity = [[int(i == j) for j in range(CHANNELS)] for i in range(CHANNELS)]
    need(query_bill(identity, 2, costs) == 224, "literal attaining basis")
    dense = {}
    for prime in (2, 5, 1000003):
        coefficient = dense_factorization(channel, prime)
        for row in coefficient:
            query = [row[channel[p]] for p in range(PORTS)]
            need(
                coordinates(query, groups, prime) == row, "query coordinate round trip"
            )
        dense[str(prime)] = query_bill(coefficient, prime, costs)
    redundant = identity + [[1] * CHANNELS]
    need(query_bill(redundant, 2, costs) == 233, "redundant row-space query")
    return {
        "status": "PASS_PLANE_FIT_RECODING_TARIFF",
        "errors": 0,
        "ports": PORTS,
        "fixed_matrix_rank": CHANNELS,
        "all_field_rowspace_tariff_minimum": 224,
        "closed_group_subsets": len(costs) - 1,
        "closure_rank_histogram": {
            str(k): v for k, v in sorted(Counter(costs[1:]).items())
        },
        "forced_scalar_entries": forced,
        "dense_factor_entries": 3 * PORTS**2,
        "dense_recode_tariffs": dense,
        "redundant_query_tariff": 233,
        "representative_only_undercharge": sum(len(g) for g in groups),
        "scope": (
            "Fixed literal K and queries in its row space; full-plane one-total tariff."
        ),
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    actual = run()
    expected = json.loads(read_bounded(HERE / "RESULT.json", 16384))
    need(actual == expected, "result receipt differs")
    print(json.dumps(actual, sort_keys=True))
