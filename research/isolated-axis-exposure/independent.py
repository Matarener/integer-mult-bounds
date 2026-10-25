#!/usr/bin/env python3
"""Bounded factorization census, without importing the primary checker or receipt."""
import itertools
import json


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def operations(length: int) -> tuple[tuple[int, int, int], ...]:
    return tuple((left, right, width)
                 for left in range(length)
                 for right in range(left + 1, length)
                 for width in range(1, min(right - left, length - right) + 1))


def apply(order: tuple[int, ...], op: tuple[int, int, int]) -> tuple[int, ...]:
    left, right, width = op
    return tuple(order[index + right - left] if left <= index < left + width
                 else order[index - right + left] if right <= index < right + width
                 else order[index] for index in range(len(order)))


def admits(order: tuple[int, ...], count: int) -> bool:
    active = {4 * index + offset for index in range(count) for offset in (0, 2)}
    return (all(order[4 * index] == 4 * index + 2 for index in range(count))
            and all(value == index for index, value in enumerate(order)
                    if index not in active))


def short_words(count: int) -> dict[str, int]:
    length = 4 * count - 1
    start = tuple(range(length))
    generators = operations(length)
    reached = {start}
    frontier = {start}
    tested = 0
    for depth in range(count):
        require(not any(admits(order, count) for order in frontier),
                "no short supported exposure")
        tested += len(frontier)
        if depth + 1 < count:
            next_layer = {apply(order, op) for order in frontier for op in generators}
            frontier = next_layer - reached
            reached.update(frontier)
    upper = start
    for index in range(count):
        upper = apply(upper, (4 * index, 4 * index + 2, 1))
    require(admits(upper, count), "g transpositions expose the sources")
    return {"g": count, "axis_count": length, "generators": len(generators),
            "distinct_states_shorter_than_g": tested, "minimum_calls": count}


def independent_bonds() -> dict[str, int]:
    tested = 0
    for length in range(1, 8):
        for order in itertools.permutations(range(length)):
            positions = {value: index for index, value in enumerate(order)}
            retained = int(order[0] == 0) + int(order[-1] == length - 1)
            retained += sum(positions[value + 1] == positions[value] + 1
                            for value in range(length - 1))
            linear = sum(b != a + 1 for a, b in
                         zip((-1,) + order, order + (length,)))
            require(length + 1 - retained == linear, "inverse-position bond count")
            tested += 1
    return {"permutations": tested}


def main() -> None:
    print(json.dumps({"status": "PASS_INDEPENDENT_B1_FACTORIZATION",
                      "short_word_census": [short_words(g) for g in range(1, 4)],
                      "inverse_position_bonds": independent_bonds()}, sort_keys=True))


if __name__ == "__main__":
    main()
