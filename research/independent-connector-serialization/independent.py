#!/usr/bin/env python3
"""Separate full-matrix enumeration and literal dense-map endpoint checks.

No implementation is imported from serialize.py or verify.py. Apache-2.0.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def encode(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path: Path) -> dict:
    ensure(path.is_file() and not path.is_symlink(), "regular input required")
    with path.open("rb") as stream:
        raw = stream.read(1_048_577)
    ensure(len(raw) <= 1_048_576, "independent input byte bound")
    return json.loads(raw)


def authenticate_sources() -> None:
    metadata = read(HERE / "SOURCES.json")
    ensure(len(metadata["files"]) <= 8, "source row bound")
    for item in metadata["files"]:
        if item["usage"] == "input":
            path = ROOT / item["path"]
            ensure(path.resolve().is_relative_to(ROOT), "input escaped root")
            ensure(path.is_file() and not path.is_symlink(), "regular source required")
            with path.open("rb") as stream:
                raw = stream.read(1_048_577)
            ensure(len(raw) <= 1_048_576, "source byte bound")
            ensure(
                hashlib.sha256(raw).hexdigest() == item["sha256"],
                "independent source SHA256",
            )


def matrix_endpoint(codes: list[int], grouped: bool) -> list[int]:
    # Four scalar rows: x,z0,z1,y. Every row stores a full matrix row.
    matrix = [1, 2, 4, 8]
    schedule = [c for p in range(2) for c in codes if c // 2 == p] if grouped else codes
    for code in schedule:
        root = 1 if grouped else 1 + code // 2
        if code % 2:
            matrix[3] ^= matrix[root]
        else:
            matrix[root] ^= matrix[0]
    return matrix


def exhaustive_matrix() -> dict:
    histogram: Counter[str] = Counter()
    digest = hashlib.sha256()
    tested = accepted = 0
    for length in range(9):
        for ordinal in range(4**length):
            codes = [(ordinal >> (2 * p)) & 3 for p in range(length - 1, -1, -1)]
            matrix = matrix_endpoint(codes, False)
            tested += 1
            if matrix[:3] != [1, 2, 4] or matrix[3] not in (8, 9):
                continue
            target = matrix[3] - 8
            ensure(matrix_endpoint(codes, True) == matrix, "full-matrix serialization")
            after = [
                ["A" if c % 2 else "B", 0, 0]
                for p in range(2)
                for c in codes
                if c // 2 == p
            ]
            digest.update(encode([codes, target, after]) + b"\n")
            histogram[f"{length}:{target}"] += 1
            accepted += 1
    return {
        "tested": tested,
        "accepted": accepted,
        "histogram_length_and_target": dict(sorted(histogram.items())),
        "accepted_serializations_sha256": digest.hexdigest(),
    }


def group(word: dict) -> dict:
    events = []
    for port in range(word["roots"]):
        events.extend(
            [kind, index, 0] for kind, index, root in word["events"] if root == port
        )
    return {**word, "roots": 1, "events": events}


def fixtures() -> tuple[list[dict], list[dict]]:
    five = []
    credited = read(ROOT / "research/connector-all-tariff-optimum/RESULT.json")
    for item in credited["witnesses"]:
        events = [[k, i if k == "B" else i - 1, 0] for k, i in item["events"]]
        base = {
            "sources": 5,
            "roots": 1,
            "targets": list(range(1, 32)),
            "events": events,
        }
        five.append(base)
        echo = [["B", 0], ["B", 1], ["A", 6], ["B", 1], ["B", 0], ["A", 6]]
        streams = [events] + [[[k, i, p] for k, i in echo] for p in (1, 2)]
        joined = []
        for t in range(max(map(len, streams))):
            joined.extend(stream[t] for stream in streams if t < len(stream))
        five.append({**base, "roots": 3, "events": joined})
    generic = []
    for n, k in ((1, 1), (2, 2), (3, 3), (4, 4), (8, 16)):
        events = [
            [kind, p % n if kind == "B" else p, p]
            for kind in ("B", "A", "B", "A")
            for p in range(k)
        ]
        generic.append(
            {
                "sources": n,
                "roots": k,
                "targets": [1 << (p % n) for p in range(k)],
                "events": events,
            }
        )
    return five, generic


def summarize(words: list[dict]) -> list[dict]:
    return [
        {
            "roots": word["roots"],
            "events": len(word["events"]),
            "input_sha256": hashlib.sha256(encode(word)).hexdigest(),
            "serialized_sha256": hashlib.sha256(encode(group(word))).hexdigest(),
        }
        for word in words
    ]


def apply(rows: list[int], value: int) -> int:
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(rows))


def maps(n: int, outputs: int, width: int) -> tuple[list, list]:
    mask = (1 << width) - 1
    left = [[((j + 3) * (r + 5) + j) & mask for r in range(width)] for j in range(n)]
    left[0] = [1 << ((r + 1) % width) for r in range(width)]
    if n >= 2:
        left[1] = [1] + [0] * (width - 1)
    right = [
        [((i + 7) * (r + 3) + r) & mask for r in range(width)] for i in range(outputs)
    ]
    return left, right


def execute(
    word: dict, state: list[int], left: list, right: list, reverse: bool
) -> list[int]:
    result = state.copy()
    n, k = word["sources"], word["roots"]
    events = list(reversed(word["events"])) if reverse else word["events"]
    for event in events:
        kind, index = event[:2]
        if kind == "T":
            result[n + index] ^= result[n + 1 - index]
        elif kind == "B":
            result[n + event[2]] ^= apply(left[index], result[index])
        else:
            result[n + k + index] ^= apply(right[index], result[n + event[2]])
    return result


def dense_check(word: dict, coupled: bool = False) -> int:
    n, k, targets = word["sources"], word["roots"], word["targets"]
    ensure(1 <= n <= 8 and 1 <= k <= 16 and len(targets) <= 255, "dense domain")
    ensure(len(word["events"]) <= 4096, "dense event bound")
    cases = 0
    for width in (1, 2, 3):
        left, right = maps(n, len(targets), width)
        rows = n + k + len(targets)
        for column in range(rows * width + 1):
            initial = [0] * rows
            if column < rows * width:
                initial[column // width] = 1 << (column % width)
            else:
                initial = [((i + 1) * 7) & ((1 << width) - 1) for i in range(rows)]
            expected = initial.copy()
            for i, target in enumerate(targets):
                value = 0
                for j in range(n):
                    if target & (1 << j):
                        value ^= apply(left[j], initial[j])
                expected[n + k + i] ^= apply(right[i], value)
            actual = execute(word, initial, left, right, False)
            ensure(actual == expected, "dense forward endpoint")
            ensure(execute(word, actual, left, right, True) == initial, "dense inverse")
            cases += 1
    # Coupled evidence is intentionally never sent to the uncoupled grouper.
    ensure(not coupled or any(e[0] == "T" for e in word["events"]), "coupled fixture")
    return cases


def port_fixture() -> dict:
    word = {
        "sources": 2,
        "roots": 2,
        "targets": [1, 2],
        "events": [[kind, p, p] for kind in ("B", "A", "B", "A") for p in range(2)],
    }
    prices = {("B", 0, 0): 1, ("B", 1, 0): 100, ("B", 0, 1): 100, ("B", 1, 1): 1}
    before = sum(prices.get(tuple(e), 1) for e in word["events"])
    after = sum(prices.get(tuple(e), 1) for e in group(word)["events"])
    ensure((before, after) == (8, 206), "port-dependent tariff counterexample")
    pairs = dense_check(word) + dense_check(group(word))
    return {"before": before, "after": after, "dense_pairs": pairs}


def observer_fixture() -> int:
    word = {
        "sources": 1,
        "roots": 2,
        "targets": [1, 1],
        "events": [
            [kind, p, p] if kind == "A" else [kind, 0, p]
            for p in (1, 0)
            for kind in ("B", "A", "B", "A")
        ],
    }
    partial = {**word, "events": word["events"][:4]}
    after = group(word)
    grouped_partial = {**after, "events": after["events"][:4]}
    original_cut = execute(partial, [1, 1, 1, 0, 0], [[1]], [[1], [1]], False)
    serialized_cut = execute(grouped_partial, [1, 1, 0, 0], [[1]], [[1], [1]], False)
    ensure(
        original_cut[-2:] == [0, 1] and serialized_cut[-2:] == [1, 0],
        "intermediate-observation counterexample",
    )
    return dense_check(word) + dense_check(after)


def main() -> None:
    authenticate_sources()
    result = read(HERE / "RESULT.json")
    ensure(
        encode(exhaustive_matrix()) == encode(result["exhaustive"]),
        "independent census",
    )
    five, generic = fixtures()
    ensure(
        encode(summarize(five)) == encode(result["five_source"]), "five-source digests"
    )
    ensure(encode(summarize(generic)) == encode(result["generic"]), "generic digests")
    cases = sum(dense_check(w) + dense_check(group(w)) for w in five + generic)
    source = read(ROOT / "research/bidirectional-five-source-connector/EVIDENCE.json")
    events = source["witness"]["complete_word"]
    coupled = {
        "sources": 5,
        "roots": 2,
        "targets": list(range(1, 32)),
        "events": [[k, i - 1 if k == "A" else i, *rest] for k, i, *rest in events],
    }
    cases += dense_check(coupled, True)
    counts = Counter(event[0] for event in events)
    ensure(counts == {"B": 10, "A": 62, "T": 6}, "credited coupled counts")
    ensure(
        hashlib.sha256(encode(events)).hexdigest()
        == result["boundary"]["credited_coupled_word_sha256"],
        "coupled bytes",
    )
    port = port_fixture()
    cases += port["dense_pairs"] + observer_fixture()
    left, _ = maps(2, 1, 2)
    ensure(
        any(
            apply(left[0], apply(left[1], 1 << i))
            != apply(left[1], apply(left[0], 1 << i))
            for i in range(2)
        ),
        "dense maps really are noncommuting",
    )
    print(
        f"PASS_INDEPENDENT_SERIALIZATION matrix_words=87381 dense_forward_inverse_pairs={cases} port_prices=8,206"
    )


if __name__ == "__main__":
    main()
