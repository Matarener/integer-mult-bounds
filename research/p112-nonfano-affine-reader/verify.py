#!/usr/bin/env python3
"""Optimize the complete fixed non-Fano affine reader family. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).absolute().parent
DATA = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
DATA_HASH = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
GROUP_HASH = "2e990b02186660c68d9d38cabc864d662b01458b3eafeab774a8b8406bbfb57b"
PROOF_HASH = "fea68cfc1bc1d8a4151dfbe9e05b9679eda7fc63f7022649b6a79d349e149516"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_file(path, digest=None):
    require(path.absolute() == path.resolve(), "source symlink")
    require(path.is_file(), "source is not regular")
    with path.open("rb") as stream:
        raw = stream.read((1 << 20) + 1)
    require(len(raw) <= 1 << 20, "input capacity")
    if digest is not None:
        require(hashlib.sha256(raw).hexdigest() == digest, "source drift")
    return raw


def read_json(path, digest=None):
    return json.loads(read_file(path, digest), object_pairs_hook=unique_object)


def basis(values):
    pivots = [0] * 9
    for value in values:
        require(type(value) is int and 0 <= value < 512, "binary vector domain")
        for pivot in range(8, -1, -1):
            if value >> pivot & 1:
                if pivots[pivot]:
                    value ^= pivots[pivot]
                else:
                    pivots[pivot] = value
                    break
    return tuple(value for value in pivots if value)


def geometry():
    data = read_json(HERE.parents[1] / DATA, DATA_HASH)
    retained = read_json(HERE / "RETAINED-RANK32.json", GROUP_HASH)
    read_file(HERE / "RETAINED-PREDECESSOR-PROOF.md", PROOF_HASH)
    require([r["port"] for r in data["recipes"]] == list(range(112)), "port order")
    labels = tuple(r["q"] for r in data["recipes"])
    groups = retained["orthonormal_groups"]
    require(len(groups) == 16, "group count")
    require(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    planes, targets, sizes = [()] * 112, [], []
    for group in groups:
        require(0 < len(group) <= 8 and len(group) % 2 == 0, "even group")
        require(
            all(
                (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                for p in group
                for q in group
            ),
            "Gram-I group",
        )
        for offset in range(0, len(group), 2):
            pair = tuple(group[offset : offset + 2])
            for port in pair:
                planes[port] = pair
        for side in range(2):
            targets.append(tuple(group[side::2]))
            sizes.append(len(group))
    return labels, planes, targets, sizes


def price_tables(triple, labels, planes, targets):
    ports = sum((targets[t] for t in triple), ())
    require(len(ports) <= 12 and len(set(ports)) == len(ports), "port capacity")
    tables = []
    for parts in ((0, 1), (0, 2), (1, 2), (0, 1, 2)):
        source = basis(
            [
                labels[p]
                for part in parts
                for t in targets[triple[part]]
                for p in planes[t]
            ]
        )
        projected = [
            tuple(
                sum(
                    ((v & labels[p]).bit_count() % 2) << j for j, v in enumerate(source)
                )
                for p in planes[t]
            )
            for t in ports
        ]
        states, costs = [()], [0] * (1 << len(ports))
        for mask in range(1, 1 << len(ports)):
            bit = mask & -mask
            merged = basis((*states[mask ^ bit], *projected[bit.bit_length() - 1]))
            states.append(merged)
            costs[mask] = len(merged)
        tables.append(costs)
    return tables


def choices(length, start, part):
    require(1 <= length <= 4 and 0 <= start <= 10 and 0 <= part < 3, "choice domain")
    result = []
    opposite = 2 - part
    for values in itertools.product((0, 1, -1), repeat=length):
        masks = [0, 0, 0, 0]
        for offset, value in enumerate(values):
            if value == 0:
                included = (0, 1, 2)
            elif value == 1:
                included = (opposite, 3)
            else:
                included = tuple(t for t in range(3) if t != opposite) + (3,)
            for term in included:
                masks[term] |= 1 << (start + offset)
        result.append((tuple(masks), values))
    return result


def solve(triple, labels, planes, targets, sizes):
    require(len(triple) == 3 and sorted(set(triple)) == list(triple), "triple order")
    require(all(type(t) is int and 0 <= t < 32 for t in triple), "triple domain")
    c0, c1, c2, c3 = price_tables(triple, labels, planes, targets)
    lengths = [len(targets[t]) for t in triple]
    ca, cb, cc = [choices(n, sum(lengths[:i]), i) for i, n in enumerate(lengths)]
    best, witness = 100, ()
    for (a, av), (b, bv) in itertools.product(ca, cb):
        t0, t1, t2, t3 = (a[j] | b[j] for j in range(4))
        for c, cv in cc:
            cost = c0[t0 | c[0]] + c1[t1 | c[1]] + c2[t2 | c[2]] + c3[t3 | c[3]]
            if cost < best:
                best, witness = cost, av + bv + cv
    require(len(witness) == sum(lengths), "minimizer missing")
    return {
        "targets": list(triple),
        "original": sum(sizes[t] for t in triple),
        "minimum": best,
        "states": 3 ** sum(lengths),
        "w": list(witness),
    }


def canonical(triple):
    groups = [t // 2 for t in triple]
    return tuple(
        2 * g + int(i > 0 and groups[i - 1] == g) for i, g in enumerate(groups)
    )


def row_bytes(triple, record):
    row = [*triple, record["original"], record["minimum"], *record["w"]]
    return (json.dumps(row, separators=(",", ":")) + "\n").encode()


def summarize(records):
    cache = {tuple(r["targets"]): r for r in records}
    digest, histogram, states = hashlib.sha256(), Counter(), 0
    best = None
    for triple in itertools.combinations(range(32), 3):
        record = cache[canonical(triple)]
        excess = record["minimum"] - record["original"]
        histogram[excess] += 1
        states += record["states"]
        digest.update(row_bytes(triple, record))
        if best is None or excess < best["minimum"] - best["original"]:
            best = dict(record, targets=list(triple))
    require(len(cache) == 800 and sum(histogram.values()) == 4960, "orbit coverage")
    return {
        "triples": 4960,
        "plane_equivalence_classes": 800,
        "evaluated_states": sum(r["states"] for r in records),
        "expanded_states": states,
        "minimum_excess_histogram": {str(k): v for k, v in sorted(histogram.items())},
        "stream_sha256": digest.hexdigest(),
        "best": best,
        "classes": records,
    }


def identity_control():
    axes = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0))
    queries = [(a + b, a + c, b + c, a + b + c) for a, b, c in axes]
    checked = 0
    for i, (a, b, c) in enumerate(axes):
        for w in (0, 1, -1, 2, 7):
            readers2 = (a + b - c - w, a - b + c - w, -a + b + c - w, 2 * w)
            for j, query in enumerate(queries):
                target = 2 * sum(x * y for x, y in zip(axes[i], axes[j], strict=True))
                require(
                    sum(x * y for x, y in zip(readers2, query, strict=True)) == target,
                    "identity",
                )
                checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--case", nargs=3, type=int)
    args = parser.parse_args()
    require(not (args.write and args.case), "write/case conflict")
    labels, planes, targets, sizes = geometry()
    require(identity_control() == 125, "identity coverage")
    if args.case is not None:
        triple = tuple(args.case)
        actual = solve(triple, labels, planes, targets, sizes)
        expected = read_json(HERE / "RESULT.json")
        matches = [
            r for r in expected["classes"] if tuple(r["targets"]) == canonical(triple)
        ]
        require(len(matches) == 1, "expected class missing")
        require(actual == dict(matches[0], targets=list(triple)), "case mismatch")
        print(json.dumps(actual, sort_keys=True))
        return
    triples = sorted({canonical(t) for t in itertools.combinations(range(32), 3)})
    result = summarize([solve(t, labels, planes, targets, sizes) for t in triples])
    if args.write:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(result == read_json(HERE / "RESULT.json"), "result mismatch")
    print(
        "PASS_P112_NONFANO_AFFINE_READER",
        json.dumps({k: v for k, v in result.items() if k != "classes"}, sort_keys=True),
    )


if __name__ == "__main__":
    main()
