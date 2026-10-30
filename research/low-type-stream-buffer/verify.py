#!/usr/bin/env python3
"""Finite corroboration of the one-pass low-type buffer theorem.

Produced by Nick Petalas. Apache-2.0.
The written proof supplies the universal claim.
"""
import argparse
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path

MAX_SYMBOLS = 4096


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def batch_order(n: int, low_types: int, chunk: int) -> tuple[int, ...]:
    require(all(type(x) is int and 1 <= x <= MAX_SYMBOLS
                for x in (n, low_types, chunk)), "invalid dimensions")
    require(n * low_types * chunk <= MAX_SYMBOLS, "stream too large")
    return tuple((cycle * low_types + low) * chunk + offset
                 for low in range(low_types) for cycle in range(n)
                 for offset in range(chunk))


def validate_stream(payload: tuple[int, ...], order: tuple[int, ...],
                    capacity: int, cut: int) -> None:
    size = len(payload)
    require(type(payload) is tuple and 0 <= size <= MAX_SYMBOLS,
            "invalid payload length or container")
    require(all(type(x) is int and -(1 << 63) <= x < (1 << 63)
                for x in payload), "invalid payload symbol")
    require(type(order) is tuple and len(order) == size
            and all(type(x) is int for x in order)
            and set(order) == set(range(size)), "invalid permutation")
    require(type(capacity) is int and 0 <= capacity <= size, "invalid capacity")
    require(type(cut) is int and 0 <= cut <= size, "invalid cut")


def dispatch(payload: tuple[int, ...], order: tuple[int, ...], capacity: int,
             cut: int = 0) -> tuple[tuple[int, ...], int, tuple[tuple[int, int], ...]]:
    """Simulate one read stream, append-only output and bounded payload slots.

    Output is an observation log unavailable to the simulated controller.
    Ready arriving symbols bypass storage. The cut snapshot is instrumentation.
    """
    validate_stream(payload, order, capacity, cut)
    retained: dict[int, int] = {}
    output: list[int] = []
    snapshot: tuple[tuple[int, int], ...] = ()
    peak = 0
    for index, symbol in enumerate(payload):
        if order[len(output)] == index:
            output.append(symbol)
        else:
            require(len(retained) < capacity, "payload capacity exhausted")
            retained[index] = symbol
            peak = max(peak, len(retained))
        for _ in range(len(payload) - len(output)):
            wanted = order[len(output)]
            if wanted not in retained:
                break
            output.append(retained.pop(wanted))
        require(len(retained) == index + 1 - len(output), "lost payload")
        if index + 1 == cut:
            snapshot = tuple(sorted(retained.items()))
    require(not retained and len(output) == len(payload), "incomplete dispatch")
    return tuple(output), peak, snapshot


def prefix_oracle(order: tuple[int, ...]) -> int:
    """Count read indices outside the longest available output prefix."""
    size = len(order)
    peak = 0
    for read in range(size + 1):
        prefix = size
        for rank, index in enumerate(order):
            if index >= read:
                prefix = rank
                break
        peak = max(peak, read - prefix)
    return peak


def schedule_oracle(order: tuple[int, ...]) -> int:
    """Minimax over every legal read/emit interleaving, with direct bypass."""
    size = len(order)
    best = [[size + 1] * (size + 1) for _ in range(size + 1)]
    best[0][0] = 0
    for read in range(size + 1):
        for written in range(size + 1):
            old = best[read][written]
            if old > size:
                continue
            if written < size and order[written] < read:
                best[read][written + 1] = min(best[read][written + 1], old)
            if read == size:
                continue
            best[read + 1][written] = min(
                best[read + 1][written], max(old, read + 1 - written))
            if written < size and order[written] == read:
                best[read + 1][written + 1] = min(
                    best[read + 1][written + 1], max(old, read - written))
    return best[size][size]


def check_permutations() -> int:
    count = 0
    for size in range(8):
        payload = tuple(range(size))
        for order in permutations(payload):
            output, peak, _ = dispatch(payload, order, size)
            require(output == order, "wrong literal permutation")
            require(peak == prefix_oracle(order) == schedule_oracle(order),
                    "independent scheduling disagreement")
            count += 1
    return count


def check_batches() -> tuple[int, int]:
    count = rejected = 0
    for n, low_types, chunk in product(range(1, 9), repeat=3):
        order = batch_order(n, low_types, chunk)
        expected = (n - 1) * (low_types - 1) * chunk
        payload = tuple(range(len(order)))
        output, peak, _ = dispatch(payload, order, expected)
        require(output == order and peak == expected == prefix_oracle(order),
                "batch theorem disagreement")
        if expected:
            try:
                dispatch(payload, order, expected - 1)
            except ValueError as error:
                require(str(error) == "payload capacity exhausted", "wrong rejection")
                rejected += 1
            else:
                raise ValueError("subcritical buffer accepted")
        count += 1
    return count, rejected


def check_payloads() -> int:
    count = 0
    for n, low_types, chunk in product(range(1, 5), range(1, 5), range(1, 4)):
        size = n * low_types * chunk
        if size > 12:
            continue
        order = batch_order(n, low_types, chunk)
        capacity = (n - 1) * (low_types - 1) * chunk
        for payload in product((0, 1), repeat=size):
            output, peak, _ = dispatch(payload, order, capacity)
            require(output == tuple(payload[index] for index in order)
                    and peak == capacity, "payload corruption")
            count += 1
    return count


def check_information_cut() -> tuple[int, int]:
    families = states = 0
    for n, low_types, chunk in product(range(2, 5), range(2, 5), range(1, 4)):
        capacity = (n - 1) * (low_types - 1) * chunk
        if capacity > 10:
            continue
        order = batch_order(n, low_types, chunk)
        cut = (n - 1) * low_types * chunk
        hidden = tuple((cycle * low_types + low) * chunk + offset
                       for cycle in range(n - 1) for low in range(1, low_types)
                       for offset in range(chunk))
        require(len(hidden) == capacity, "wrong cut dimension")
        seen = set()
        for bits in product((0, 1), repeat=capacity):
            payload = [0] * len(order)
            for index, bit in zip(hidden, bits, strict=True):
                payload[index] = bit
            output, _, snapshot = dispatch(tuple(payload), order, capacity, cut)
            require(output == tuple(payload[index] for index in order), "bad cut output")
            require(tuple(index for index, _ in snapshot) == hidden,
                    "wrong retained cut indices")
            require(snapshot not in seen, "noninjective retained information")
            seen.add(snapshot)
            states += 1
        require(len(seen) == 2 ** capacity, "missing cut state")
        families += 1
    return families, states


def check_cover_substitution() -> int:
    count = 0
    for low_types, high, slabs, depth, body in product(
            range(1, 6), range(1, 5), range(1, 5), range(1, 9), range(1, 5)):
        for level in range(depth):
            n = slabs * (low_types * high) ** (depth - level - 1)
            chunk = high ** (level + 1) * body
            volume = slabs * (low_types * high) ** depth * body // low_types ** level
            buffer = (n - 1) * (low_types - 1) * chunk
            require(n * low_types * chunk == volume, "inconsistent source dimensions")
            require(low_types * buffer
                    == (low_types - 1) * (volume - low_types * chunk),
                    "incorrect normalized buffer")
            count += 1
    return count


def check_rejections() -> int:
    cases = (
        ((0, 1), (0, 0), 2, 0), ((0, 1), (0, 2), 2, 0),
        ((0, 1), (True, 0), 2, 0), ((0, 1), (0,), 2, 0),
        ((0, 1), (0, 1), -1, 0), ((0, 1), (0, 1), 3, 0),
        ((0, 1), (0, 1), 2, 3), ((0, 1), (0, 1), True, 0),
        ((0, 1 << 63), (0, 1), 2, 0), ((False, 1), (0, 1), 2, 0),
    )
    for payload, order, capacity, cut in cases:
        try:
            dispatch(payload, order, capacity, cut)
        except ValueError:
            pass
        else:
            raise ValueError("invalid stream accepted")
    for args in ((0, 2, 1), (True, 2, 1), (17, 17, 17), (1, -1, 1)):
        try:
            batch_order(*args)
        except ValueError:
            pass
        else:
            raise ValueError("invalid dimensions accepted")
    return len(cases) + 4


def verify() -> dict:
    batches, exhausted = check_batches()
    families, states = check_information_cut()
    return {
        "status": "PASS_LOW_TYPE_STREAM_BUFFER",
        "permutations": check_permutations(),
        "batch_shapes": batches,
        "subcritical_capacity_rejections": exhausted,
        "binary_payloads": check_payloads(),
        "information_cut_families": families,
        "distinct_information_cut_states": states,
        "cover_parameter_substitutions": check_cover_substitution(),
        "invalid_input_rejections": check_rejections(),
        "claim_type": "scoped written proof; finite corroboration",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    report = verify()
    root = Path(__file__).resolve().parent
    report["package_sha256"] = {
        name: sha256((root / name).read_bytes()).hexdigest()
        for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                     "VERIFY.json", "verify.py")
    }
    encoded = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.receipt:
        require(not args.receipt.resolve().is_relative_to(root),
                "receipt must stay outside package")
        require(args.receipt.write_text(encoded, encoding="utf-8") == len(encoded),
                "incomplete receipt write")
    print(encoded, end="")


if __name__ == "__main__":
    main()
