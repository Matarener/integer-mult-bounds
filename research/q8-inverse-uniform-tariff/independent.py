"""Code-disjoint faithful regular Q8 action and independent attaining words."""

import hashlib
import json
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUATERNIONS = (
    (1, 0, 0, 0),
    (-1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, -1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, -1, 0),
    (0, 0, 0, 1),
    (0, 0, 0, -1),
)
INVERSES = (0, 1, 3, 2, 5, 4, 7, 6)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def multiply(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    a0, a1, a2, a3 = a
    b0, b1, b2, b3 = b
    return (
        a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3,
        a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
        a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1,
        a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0,
    )


def permutation(label: int) -> tuple[int, ...]:
    return tuple(
        QUATERNIONS.index(multiply(QUATERNIONS[label], x)) for x in QUATERNIONS
    )


def act(state: tuple[int, ...], call: tuple[int, int, int]) -> tuple[int, ...]:
    label, u, v = call
    summed = 0
    for role, value in enumerate(state):
        if (v >> role) & 1:
            summed ^= value
    changed = summed
    for source, destination in enumerate(permutation(label)):
        if (summed >> source) & 1:
            changed ^= 1 << destination
    return tuple(
        value ^ (changed if (u >> role) & 1 else 0) for role, value in enumerate(state)
    )


def columns(roles: int, word: tuple[tuple[int, int, int], ...]) -> tuple[int, ...]:
    result = []
    for source in range(roles * 8):
        state = tuple(
            (1 << (source % 8)) if role == source // 8 else 0 for role in range(roles)
        )
        for call in reversed(word):
            state = act(state, call)
        result.append(sum(value << (8 * role) for role, value in enumerate(state)))
    return tuple(result)


def diagonal(elements: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        1 << (8 * role + destination)
        for role, label in enumerate(elements)
        for destination in permutation(label)
    )


def construct(
    elements: tuple[int, ...], prefer_i: bool
) -> tuple[tuple[int, int, int], ...]:
    words = ((), (2, 2) if prefer_i else (4, 4), (2,), (3,), (4,), (5,), (2, 4), (4, 2))
    return tuple(
        (label, 2**role, 2**role)
        for role, target in enumerate(elements)
        for label in words[target]
    )


def reverse(word: tuple[tuple[int, int, int], ...]) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (INVERSES[g] if (u & v).bit_count() % 2 else g, u, v)
        for g, u, v in reversed(word)
    )


def build() -> dict:
    digest = hashlib.sha256()
    total_columns = omissions = 0
    cases = tuple(product(range(8), repeat=2)) + tuple(product(range(8), repeat=3))
    for elements in cases:
        for prefer_i in (True, False):
            word = construct(elements, prefer_i)
            actual = columns(len(elements), word)
            check(actual == diagonal(elements), "faithful dirty endpoint")
            digest.update(json.dumps(actual).encode())
            total_columns += len(actual)
    # Noncommuting, nilpotent and idempotent gates touch active and spectator dirt.
    for roles in range(2, 9):
        elements = (*range(roles - 1), 0)
        base = construct(elements, True)
        prefix = tuple(
            (
                2 + n % 4,
                1 + (7 * n + 1) % (2**roles - 1),
                1 + (11 * n + 2) % (2**roles - 1),
            )
            for n in range(6)
        )
        word = prefix + reverse(prefix) + base
        actual = columns(roles, word)
        check(actual == diagonal(elements), "mixed/spectator restoration")
        total_columns += len(actual)
        for position in range(len(word)):
            mutated = word[:position] + word[position + 1 :]
            check(columns(roles, mutated) != actual, "mixed omission not rejected")
            omissions += 1
    return {
        "status": "PASS_Q8_INVERSE_REGULAR_ACTION",
        "pair_and_triple_lists": len(cases),
        "regular_columns": total_columns,
        "endpoint_digest": digest.hexdigest(),
        "mixed_words": 7,
        "mixed_omissions": omissions,
    }


def main() -> None:
    result = build()
    if len(sys.argv) == 2 and sys.argv[1] == "--write":
        with (HERE / "INDEPENDENT.json").open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        check(len(sys.argv) == 1, "invalid arguments")
        check((HERE / "INDEPENDENT.json").stat().st_size < 100_000, "oversized receipt")
        check(
            json.dumps(result, sort_keys=True)
            == json.dumps(
                json.loads((HERE / "INDEPENDENT.json").read_bytes()), sort_keys=True
            ),
            "independent receipt differs",
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
