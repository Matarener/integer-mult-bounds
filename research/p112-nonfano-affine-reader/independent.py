#!/usr/bin/env python3
"""Separate raw-Gram, two-half enumeration; no primary imports. Apache-2.0."""

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).absolute().parent
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
DATA_HASH = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
GROUP_HASH = "2e990b02186660c68d9d38cabc864d662b01458b3eafeab774a8b8406bbfb57b"


def check(condition, reason):
    if not condition:
        raise ValueError(reason)


def load(path, digest=None):
    check(path.absolute() == path.resolve() and path.is_file(), "regular source")
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    check(len(raw) <= 1048576, "source capacity")
    if digest is not None:
        check(hashlib.sha256(raw).hexdigest() == digest, "source drift")
    return json.loads(raw)


def inputs():
    data = load(HERE.parents[1] / INPUT, DATA_HASH)
    check(len(data["recipes"]) == 112, "recipe count")
    labels = [r["q"] for r in data["recipes"]]
    groups = load(HERE / "RETAINED-RANK32.json", GROUP_HASH)["orthonormal_groups"]
    check(len(groups) == 16, "group count")
    check(sorted(sum(groups, [])) == list(range(112)), "partition")
    mates, targets, sizes = {}, [], []
    for group in groups:
        check(len(group) in (4, 6, 8), "group size")
        for p, q in itertools.product(group, repeat=2):
            check((labels[p] & labels[q]).bit_count() % 2 == int(p == q), "orthonormal")
        for j in range(0, len(group), 2):
            for p in group[j : j + 2]:
                mates[p] = tuple(group[j : j + 2])
        targets.extend((group[::2], group[1::2]))
        sizes.extend((len(group), len(group)))
    return labels, mates, targets, sizes


def extend(old, values):
    rows = list(old)
    for value in values:
        for pivot in rows:
            value = min(value, value ^ pivot)
        if value:
            rows.append(value)
            rows.sort(reverse=True)
    return tuple(rows)


def raw_prices(triple, labels, mates, targets):
    ports = sum((targets[t] for t in triple), [])
    check(6 <= len(ports) <= 12, "reader dimension")
    costs = []
    for parts in ((0, 1), (0, 2), (1, 2), (0, 1, 2)):
        source = sorted(
            {p for part in parts for t in targets[triple[part]] for p in mates[t]}
        )
        columns = [
            tuple(
                sum(
                    ((labels[p] & labels[q]).bit_count() % 2) << i
                    for i, p in enumerate(source)
                )
                for q in mates[t]
            )
            for t in ports
        ]
        states, ranks = [()], [0]
        for mask in range(1, 1 << len(ports)):
            high = 1 << (mask.bit_length() - 1)
            current = extend(states[mask ^ high], columns[high.bit_length() - 1])
            states.append(current)
            ranks.append(len(current))
        costs.append(ranks)
    return costs


def half_assignments(parts, start):
    check(len(parts) <= 6, "half dimension")
    result = []
    for values in itertools.product((0, 1, -1), repeat=len(parts)):
        masks = [0, 0, 0, 0]
        for j, (part, value) in enumerate(zip(parts, values, strict=True)):
            signs = (
                (1, 1, -1) if part == 0 else ((1, -1, 1) if part == 1 else (-1, 1, 1))
            )
            for term in range(3):
                if signs[term] - value:
                    masks[term] |= 1 << (start + j)
            if value:
                masks[3] |= 1 << (start + j)
        result.append((tuple(masks), values))
    return result


def minimum(triple, labels, mates, targets):
    costs = raw_prices(triple, labels, mates, targets)
    parts = [part for part, t in enumerate(triple) for _ in targets[t]]
    split = len(parts) // 2
    left = half_assignments(parts[:split], 0)
    right = half_assignments(parts[split:], split)
    c0, c1, c2, c3 = costs
    best, witness = 100, ()
    for a, av in left:
        for b, bv in right:
            cost = c0[a[0] | b[0]] + c1[a[1] | b[1]] + c2[a[2] | b[2]] + c3[a[3] | b[3]]
            if cost < best:
                best, witness = cost, av + bv
    check(len(witness) == len(parts), "empty minimum")
    return best, witness, len(left) * len(right)


def operator_check(triple, values, targets):
    axes = [[int(p in targets[t]) for t in triple] for p in range(112)]
    ports = sum((targets[t] for t in triple), [])
    check(len(ports) == len(values), "w dimension")
    w = dict(zip(ports, values, strict=True))
    readers, queries = [], []
    for p, (a, b, c) in enumerate(axes):
        z = w.get(p, 0)
        readers.append((a + b - c - z, a - b + c - z, -a + b + c - z, 2 * z))
        queries.append((a + b, a + c, b + c, a + b + c))
    count = 0
    for p, q in itertools.product(range(112), repeat=2):
        lhs = sum(readers[p][j] * queries[q][j] for j in range(4))
        rhs = 2 * sum(axes[p][j] * axes[q][j] for j in range(3))
        check(lhs == rhs, "literal operator mismatch")
        count += 1
    return count


def main():
    labels, mates, targets, sizes = inputs()
    expected = load(HERE / "RESULT.json")
    cache = {tuple(r["targets"]): r for r in expected["classes"]}
    digest, histogram, states, count = hashlib.sha256(), Counter(), 0, 0
    for triple in itertools.combinations(range(32), 3):
        # Deliberately solve all 4,960 triples without the primary's orbit shortcut.
        best, witness, work = minimum(triple, labels, mates, targets)
        original = sum(sizes[t] for t in triple)
        group_ids = [t // 2 for t in triple]
        representative = tuple(
            2 * g + int(i != 0 and group_ids[i - 1] == g)
            for i, g in enumerate(group_ids)
        )
        row = cache[representative]
        check(
            (best, list(witness), work) == (row["minimum"], row["w"], row["states"]),
            "class mismatch",
        )
        digest.update(
            (
                json.dumps([*triple, original, best, *witness], separators=(",", ":"))
                + "\n"
            ).encode()
        )
        histogram[best - original] += 1
        states += work
        count += 1
    check(count == expected["triples"] == 4960, "triple coverage")
    check(states == expected["expanded_states"], "state coverage")
    check(
        {str(k): v for k, v in histogram.items()}
        == expected["minimum_excess_histogram"],
        "histogram",
    )
    check(digest.hexdigest() == expected["stream_sha256"], "stream mismatch")
    best = expected["best"]
    entries = operator_check(best["targets"], best["w"], targets)
    print(
        "PASS_INDEPENDENT_NONFANO_AFFINE",
        json.dumps(
            {
                "triples": count,
                "states": states,
                "stream_sha256": digest.hexdigest(),
                "literal_entries": entries,
            },
            sort_keys=True,
        ),
    )


if __name__ == "__main__":
    main()
