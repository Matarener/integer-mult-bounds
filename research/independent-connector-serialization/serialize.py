#!/usr/bin/env python3
"""Serialize restored uncoupled dirty connectors, preserving every call count.

Apache-2.0. Source credit and proof are in README.md and PROOF.md.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

MAX_BYTES = 1_048_576
MAX_EVENTS = 4096


@dataclass(frozen=True)
class Program:
    sources: int
    roots: int
    targets: tuple[int, ...]
    events: tuple[tuple[str, int, int], ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError("nonfinite JSON constant: " + value)


def read_json(path: Path) -> object:
    require(path.is_file() and not path.is_symlink(), "regular JSON file required")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "JSON exceeds byte limit")
    return json.loads(
        raw, object_pairs_hook=unique_object, parse_constant=reject_constant
    )


def integer(value: object, lower: int, upper: int, name: str) -> int:
    require(type(value) is int and lower <= value <= upper, "invalid " + name)
    return value


def parse_program(value: object) -> Program:
    require(type(value) is dict, "program must be an object")
    require(set(value) == {"sources", "roots", "targets", "events"}, "program keys")
    sources = integer(value["sources"], 1, 8, "source count")
    roots = integer(value["roots"], 1, 16, "root count")
    targets = value["targets"]
    require(type(targets) is list and 1 <= len(targets) <= 255, "target count")
    masks = tuple(integer(x, 0, (1 << sources) - 1, "target mask") for x in targets)
    events = value["events"]
    require(type(events) is list and len(events) <= MAX_EVENTS, "event limit")
    parsed = []
    for event in events:
        require(type(event) is list and len(event) == 3, "event shape")
        kind, index, port = event
        require(type(kind) is str and kind in ("A", "B"), "uncoupled A/B calls only")
        limit = sources if kind == "B" else len(masks)
        index = integer(index, 0, limit - 1, "operator index")
        port = integer(port, 0, roots - 1, "root port")
        parsed.append((kind, index, port))
    return Program(sources, roots, masks, tuple(parsed))


def as_json(program: Program) -> dict:
    return {
        "sources": program.sources,
        "roots": program.roots,
        "targets": list(program.targets),
        "events": [list(event) for event in program.events],
    }


def endpoint(program: Program) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Bits represent independent B_j x_j and incoming root dirt.

    Output entries omit their unchanged initial y_i. Its fixed A_i applies
    to each represented symbol, so these bits encode the full formal identity.
    """
    roots = [1 << (program.sources + p) for p in range(program.roots)]
    outputs = [0] * len(program.targets)
    for kind, index, port in program.events:
        if kind == "B":
            roots[port] ^= 1 << index
        else:
            outputs[index] ^= roots[port]
    return tuple(roots), tuple(outputs)


def check_endpoint(program: Program) -> None:
    roots, outputs = endpoint(program)
    expected = tuple(1 << (program.sources + p) for p in range(program.roots))
    require(roots == expected, "a dirty root was not restored")
    require(outputs == program.targets, "output endpoint or dirty cancellation failed")


def profile(program: Program) -> tuple[int, ...]:
    counts = [0] * (program.sources + len(program.targets))
    for kind, index, _ in program.events:
        counts[index if kind == "B" else program.sources + index] += 1
    return tuple(counts)


def serialize(program: Program) -> Program:
    """Stable grouping by root, then reuse a single restored dirty root."""
    check_endpoint(program)
    buckets: list[list[tuple[str, int, int]]] = [[] for _ in range(program.roots)]
    for kind, index, port in program.events:
        buckets[port].append((kind, index, 0))
    events = tuple(event for bucket in buckets for event in bucket)
    result = Program(program.sources, 1, program.targets, events)
    check_endpoint(result)
    require(profile(result) == profile(program), "serialization changed call counts")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "program", type=Path, help="bounded JSON program; emit one-root JSON"
    )
    args = parser.parse_args()
    try:
        result = serialize(parse_program(read_json(args.program)))
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(as_json(result), indent=2))


if __name__ == "__main__":
    main()
