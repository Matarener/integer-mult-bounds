#!/usr/bin/env python3
"""Replay the 6600-call seven-source full ternary certificate.

Produced by Nick Petalas. Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement, product
import json
from math import comb
from pathlib import Path
import random


SOURCES = 7
ROWS = 3 ** SOURCES - 1
SOURCE_WORD = tuple(map(int, "260536506545241601014125215430234634321306"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digits(value):
    require(0 <= value <= ROWS, "coefficient row out of range")
    result = []
    for _ in range(SOURCES):
        value, digit = divmod(value, 3)
        result.append(digit)
    return tuple(result)


def packed_sum(left, right):
    value, place = 0, 1
    for _ in range(SOURCES):
        value += ((left % 3 + right % 3) % 3) * place
        left //= 3
        right //= 3
        place *= 3
    return value


def packed_prefixes(word):
    require(0 < len(word) <= 64, "source path length out of bounds")
    state, prefixes = 0, []
    for source in word:
        require(0 <= source < SOURCES, "invalid source")
        prefixes.append(state)
        state = packed_sum(state, 3 ** source)
    require(state == 0, "source path is not restored")
    return prefixes


def construct():
    require(len(SOURCE_WORD) == 42, "wrong source count")
    require(Counter(SOURCE_WORD) == Counter({j: 6 for j in range(SOURCES)}),
            "wrong source multiplicities")
    prefixes = packed_prefixes(SOURCE_WORD)
    witnesses = {}
    for a, b, c in combinations_with_replacement(range(42), 3):
        row = packed_sum(packed_sum(prefixes[a], prefixes[b]), prefixes[c])
        if row not in witnesses:
            witnesses[row] = (a, b, c)
    require(len(witnesses) == ROWS + 1, "a ternary row is missing")
    events = [[] for _ in range(42)]
    for row in range(1, ROWS + 1):
        for boundary in witnesses[row]:
            events[boundary].append(("A", row))
    calls = []
    for boundary, source in enumerate(SOURCE_WORD):
        calls.extend(events[boundary])
        calls.append(("B", source))
    require(len(calls) == 6600, "wrong complete-call count")
    return calls, witnesses


def independent_coverage():
    # Tuple arithmetic, independently of packed_sum and the constructed schedule.
    state, prefixes = [0] * SOURCES, []
    for source in SOURCE_WORD:
        prefixes.append(tuple(state))
        state[source] = (state[source] + 1) % 3
    require(state == [0] * SOURCES, "tuple path is not restored")
    covered = set()
    for a, b, c in combinations_with_replacement(prefixes, 3):
        covered.add(tuple((x + y + z) % 3 for x, y, z in zip(a, b, c)))
    require(covered == set(product(range(3), repeat=SOURCES)),
            "tuple coverage is incomplete")
    return len(covered)


def formal_replay(calls, modulus=3):
    require(len(calls) <= 6601 and modulus in (3, 6), "replay bound exceeded")
    # Entries stand for incoming connector dirt, then B_j x_j.
    connector = [1] + [0] * SOURCES
    outputs = [[0] * (SOURCES + 1) for _ in range(ROWS)]
    for kind, label in calls:
        if kind == "B":
            require(0 <= label < SOURCES, "invalid source call")
            connector[label + 1] = (connector[label + 1] + 1) % modulus
        else:
            require(kind == "A" and 1 <= label <= ROWS, "invalid readout")
            target = outputs[label - 1]
            for j, coefficient in enumerate(connector):
                target[j] = (target[j] + coefficient) % modulus
    require(connector == [1] + [0] * SOURCES, "connector dirt changed")
    for row, target in enumerate(outputs, 1):
        # A_row left-multiplies every symbol. No A/B commutation is used.
        require(target == [0] + list(digits(row)), f"wrong row {row}")
    return len(outputs)


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) % 3 for row in matrix]


def matmul(left, right):
    size = len(left)
    return [[sum(left[i][k] * right[k][j] for k in range(size)) % 3
             for j in range(size)] for i in range(size)]


def dense_replay(calls, size, seed):
    require(1 <= size <= 4, "dense dimension out of bounds")
    rng = random.Random(seed)
    sources = [[rng.randrange(3) for _ in range(size)] for _ in range(SOURCES)]
    b_maps = [[[rng.randrange(3) for _ in range(size)] for _ in range(size)]
              for _ in range(SOURCES)]
    if size >= 2:
        # Singular noncommuting maps are included, not assumed generic.
        b_maps[0] = [[int(i == 0 and j == 1) for j in range(size)]
                     for i in range(size)]
        b_maps[1] = [[int(i == 1 and j == 0) for j in range(size)]
                     for i in range(size)]
        require(matmul(b_maps[0], b_maps[1]) != matmul(b_maps[1], b_maps[0]),
                "dense fixture lost noncommutation")
    a_maps = [[[rng.randrange(3) for _ in range(size)] for _ in range(size)]
              for _ in range(ROWS)]
    connector = [rng.randrange(3) for _ in range(size)]
    initial_connector = connector[:]
    outputs = [[rng.randrange(3) for _ in range(size)] for _ in range(ROWS)]
    expected = [row[:] for row in outputs]
    images = [matvec(matrix, source) for matrix, source in zip(b_maps, sources)]
    for row in range(1, ROWS + 1):
        vector = [sum(d * image[k] for d, image in zip(digits(row), images)) % 3
                  for k in range(size)]
        increment = matvec(a_maps[row - 1], vector)
        expected[row - 1] = [(x + y) % 3 for x, y in zip(expected[row - 1], increment)]
    for kind, label in calls:
        if kind == "B":
            increment, target = matvec(b_maps[label], sources[label]), connector
        else:
            increment = matvec(a_maps[label - 1], connector)
            target = outputs[label - 1]
        target[:] = [(x + y) % 3 for x, y in zip(target, increment)]
    require(connector == initial_connector, "dense connector not restored")
    require(outputs == expected, "dense output is wrong")
    return ROWS


def controls(calls):
    first_b = next(i for i, call in enumerate(calls) if call[0] == "B")
    first_a = next(i for i, call in enumerate(calls) if call[0] == "A")
    dropped_b = calls[:first_b] + calls[first_b + 1:]
    dropped_a = calls[:first_a] + calls[first_a + 1:]
    misrouted = calls[:]
    misrouted[first_a] = ("A", misrouted[first_a][1] % ROWS + 1)
    relabelled = [(kind, (label + 1) % SOURCES if kind == "B" else label)
                  for kind, label in calls]
    appended = calls + [("B", 0)]
    cases = [(dropped_b, 3), (dropped_a, 3), (misrouted, 3),
             (relabelled, 3), (appended, 3), (calls, 6)]
    rejected = 0
    for mutant, modulus in cases:
        try:
            formal_replay(mutant, modulus)
        except ValueError:
            rejected += 1
    require(rejected == len(cases), "a semantic control was accepted")
    return rejected


def main():
    calls, witnesses = construct()
    require(formal_replay(calls) == ROWS, "formal row count changed")
    covered = independent_coverage()
    dense_cases = 0
    for size in range(1, 5):
        for seed in (621, 1020):
            require(dense_replay(calls, size, seed) == ROWS, "dense row count changed")
            dense_cases += 1
    rejected = controls(calls)
    folder = Path(__file__).resolve().parent
    hashes = {name: sha256((folder / name).read_bytes()).hexdigest()
              for name in ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")}
    receipt = {"marker": "PASS_F3_TERNARY_SEVEN_SOURCE", "source_calls": 42,
               "readouts": 3 * ROWS, "calls": len(calls), "rows": ROWS,
               "covered_including_zero": covered, "boundary_triples": comb(44, 3),
               "dense_cases": dense_cases, "rejected_controls": rejected,
               "witness_rows": len(witnesses) - 1, "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
