#!/usr/bin/env python3
"""Exact finite corroboration of the isolated-axis B1 factorization theorem."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
MAX_BREAKS = 4


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def authenticate() -> dict[str, str]:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    expected = {
        "research/physical-ordinary-interchange/binary.py",
        "research/physical-ordinary-interchange/PROOF.md",
    }
    need({row["path"] for row in rows} == expected and len(rows) == 2,
         "exact source closure")
    result = {}
    for row in rows:
        path = PACKAGE.parents[1] / row["path"]
        need(not path.is_symlink() and path.is_file(), "regular source input")
        raw = path.read_bytes()
        need(len(raw) <= 100000, "source size bound")
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source SHA256: " + row["path"])
        result[row["path"]] = digest
    return result


def breaks(order: tuple[int, ...]) -> int:
    """Include the fixed sentinels so endpoint coordinates have two bonds."""
    augmented = (-1,) + order + (len(order),)
    return sum(right != left + 1 for left, right in zip(augmented, augmented[1:]))


def moves(size: int) -> tuple[tuple[int, int, int], ...]:
    need(1 <= size <= 64, "bounded finite fixture size")
    return tuple((left, width, right)
                 for width in range(1, size // 2 + 1)
                 for left in range(size - 2 * width + 1)
                 for right in range(left + width, size - width + 1))


def exchange(order: tuple[int, ...], move: tuple[int, int, int]) -> tuple[int, ...]:
    left, width, right = move
    return (order[:left] + order[right:right + width]
            + order[left + width:right] + order[left:left + width]
            + order[right + width:])


def invariant() -> dict[str, int]:
    comparisons = 0
    maximum = 0
    for size in range(1, 8):
        generators = moves(size)
        for order in itertools.permutations(range(size)):
            before = breaks(order)
            for move in generators:
                after = exchange(order, move)
                increase = breaks(after) - before
                need(increase <= MAX_BREAKS, "four-cut exchange invariant")
                need(exchange(after, move) == order, "exchange is an involution")
                maximum = max(maximum, increase)
                comparisons += 1
    need(maximum == 4, "sharp four-break increase")
    return {"permutation_sizes": 7, "comparisons": comparisons,
            "maximum_increase": maximum}


def supported_endpoint(order: tuple[int, ...], sources: tuple[int, ...],
                       targets: tuple[int, ...]) -> bool:
    support = set(sources + targets)
    return (all(order[target] == source for source, target in zip(sources, targets))
            and all(order[index] == index for index in range(len(order))
                    if index not in support))


def endpoints() -> dict[str, int]:
    cases = completions = constructed = 0
    for count in range(1, 7):
        for spacing in range(4, 9):
            size = count * spacing + 1
            targets = tuple(index * spacing for index in range(count))
            sources = tuple(target + 2 for target in targets)
            for remaining in itertools.permutations(targets):
                order = list(range(size))
                for source, target, value in zip(sources, targets, remaining):
                    order[target] = source
                    order[source] = value
                endpoint = tuple(order)
                need(supported_endpoint(endpoint, sources, targets), "supported exposure")
                need(breaks(endpoint) == 4 * count, "all completions have four g breaks")
                completions += 1
            order = tuple(range(size))
            for source, target in zip(sources, targets):
                order = exchange(order, (target, 1, source))
            need(supported_endpoint(order, sources, targets), "g-call upper construction")
            need(breaks(order) == 4 * count, "upper construction attains bound")
            constructed += count
            cases += 1
    return {"families": cases, "all_supported_completions": completions,
            "constructive_single_bit_calls": constructed}


def scope_controls() -> dict[str, object]:
    adjacent = exchange(tuple(range(4)), (0, 2, 2))
    need(supported_endpoint(adjacent, (2, 3), (0, 1)), "adjacent support control")
    need(breaks(adjacent) == 3 < 8, "isolation cannot be dropped")
    count, size = 3, 24
    sources, targets = (12, 16, 20), (0, 4, 8)
    broad = exchange(tuple(range(size)), (0, 12, 12))
    need(all(broad[t] == s for s, t in zip(sources, targets)), "broad exposure")
    need(not supported_endpoint(broad, sources, targets), "larger support excluded")
    need(breaks(broad) == 3 < 4 * count, "fixed spectators are essential")
    direct = list(range(12))
    for left, right in ((0, 2), (4, 6), (8, 10)):
        direct[left], direct[right] = direct[right], direct[left]
    need(breaks(tuple(direct)) == 12 > MAX_BREAKS, "new primitive is outside B1")
    return {"adjacent_support_one_call_breaks": breaks(adjacent),
            "larger_support_one_call_breaks": breaks(broad),
            "simultaneous_non_B1_breaks": breaks(tuple(direct)),
            "sentinel_control": breaks((2, 1, 0, 3)) == 4}


def result() -> dict[str, object]:
    return {"status": "PASS_ISOLATED_AXIS_EXPOSURE",
            "source_sha256": authenticate(), "invariant": invariant(),
            "endpoints": endpoints(), "scope_controls": scope_controls(),
            "claim": "Minimum over union-supported extensions is exactly g B1 calls",
            "scope": "Literal complete-packet equal-contiguous-block exchanges only"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-to", type=Path)
    args = parser.parse_args()
    actual = result()
    if args.emit_to is not None:
        with args.emit_to.open("x") as output:
            encoded = json.dumps(actual, indent=2, sort_keys=True) + "\n"
            need(output.write(encoded) == len(encoded), "complete receipt write")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
             "stored result differs")
    print(json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
