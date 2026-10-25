#!/usr/bin/env python3
"""Check the unsigned F3 five-source connector. Produced by Nick Petalas."""

from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
PACKAGE_FILES = (
    "README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
    "CERTIFICATE.json", "verify.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def small_bytes(path):
    with path.open("rb") as handle:
        raw = handle.read(131073)
    require(len(raw) <= 131072, "JSON exceeds the package's 128 KiB bound")
    return raw


def read_json(path):
    return json.loads(small_bytes(path))


def source_bindings():
    manifest = read_json(HERE / "SOURCES.json")
    files = manifest["files"]
    require(len(files) == 3, "Unexpected source inventory")
    root = HERE.parents[1]
    live = {}
    for entry in files:
        if entry["usage"] == "input":
            require(entry["path"] == "research/universal-connector-boundary/README.md",
                    "Unexpected live input")
            digest = sha256(small_bytes(root / entry["path"])).hexdigest()
            require(digest == entry["sha256"], "Predecessor source bytes changed")
            live[entry["path"]] = digest
    require(len(live) == 1, "Missing live source binding")
    return live


def prefixes(source_word):
    value = [0] * 5
    result = [tuple(value)]
    for label in source_word:
        value[label] = (value[label] + 1) % 3
        result.append(tuple(value))
    return result


def first_readouts(source_word):
    points = prefixes(source_word)
    found = {}
    visited = 0
    for triple in combinations_with_replacement(range(16), 3):
        visited += 1
        row = tuple(sum(points[t][j] for t in triple) % 3 for j in range(5))
        if all(x in (0, 1) for x in row) and any(row):
            mask = sum(x << j for j, x in enumerate(row))
            found.setdefault(str(mask), list(triple))
    require(visited == 816, "Incomplete three-prefix enumeration")
    require(len(found) == 31, "Source path does not cover every requested mask")
    return found, visited


def make_word(source_word, readouts):
    word = []
    for boundary in range(16):
        for mask in range(1, 32):
            for _ in range(readouts[str(mask)].count(boundary)):
                word.append(["A", mask])
        if boundary < 15:
            word.append(["B", source_word[boundary]])
    return word


def certificate():
    data = read_json(HERE / "CERTIFICATE.json")
    require(data["schema_version"] == 1 and data["field"] == 3, "Wrong domain")
    source_word = data["source_word"]
    require(isinstance(source_word, list) and len(source_word) == 15,
            "Source path must have fifteen events")
    require(all(type(j) is int and 0 <= j < 5 for j in source_word),
            "Invalid source label")
    require(Counter(source_word) == Counter({j: 3 for j in range(5)}),
            "Each source must be called exactly three times")
    readouts, triples = first_readouts(source_word)
    require(data["readouts"] == readouts, "Readout certificate differs from regeneration")
    word = make_word(source_word, readouts)
    require(data["word"] == word, "Literal word differs from its boundary certificate")
    require(len(word) == 108, "Wrong complete-call count")
    counts = Counter((op, j) for op, j in word)
    require(len(counts) == 36 and set(counts.values()) == {3}, "Wrong call inventory")
    return word, triples


def symbolic_action(word, sign=1):
    """Coefficients of z0 and the five independent B_j x_j terms."""
    connector = [1, 0, 0, 0, 0, 0]
    outputs = [[0] * 6 for _ in range(31)]
    for op, label in word:
        if op == "B":
            connector[label + 1] = (connector[label + 1] + 1) % 3
        else:
            outputs[label - 1] = [
                (a + b) % 3 for a, b in zip(outputs[label - 1], connector)
            ]
    expected = [
        [0] + [sign * ((mask >> j) & 1) % 3 for j in range(5)]
        for mask in range(1, 32)
    ]
    return connector == [1, 0, 0, 0, 0, 0] and outputs == expected


def mutation_controls(word):
    missing_source = word[:-1]
    missing_readout = word[1:]
    wrong_source = [[op, (j + 1) % 5 if op == "B" else j] for op, j in word]
    wrong_output = [[op, 3 - j if op == "A" and j in (1, 2) else j]
                    for op, j in word]
    moved_readout = [event[:] for event in word]
    location = max(i for i, event in enumerate(word) if event == ["A", 31])
    event = moved_readout.pop(location)
    moved_readout.append(event)
    mutants = [missing_source, missing_readout, wrong_source,
               wrong_output, moved_readout]
    for mutant in mutants:
        require(not symbolic_action(mutant), "Semantic mutation escaped detection")
    require(not symbolic_action(word, sign=-1), "Wrong inverse direction escaped")
    return len(mutants) + 1


def tariff_checks(word):
    totals = []
    for source_prices in ((1, 1, 1, 1, 1), (1, 4, 10, 16, 28)):
        prices = {("B", j): price for j, price in enumerate(source_prices)}
        prices.update({("A", mask): 1 for mask in range(1, 32)})
        total = sum(prices[(op, label)] for op, label in word)
        require(total == 3 * sum(prices.values()), "Literal tariff differs from count floor")
        totals.append(total)
    require(totals == [108, 270], "Tariff fixtures changed")
    return totals


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) % 3 for row in matrix]


def matrix_bank(width):
    rng = Random(width)
    readers = [[[rng.randrange(3) for _ in range(width)]
                for _ in range(width)] for _ in range(31)]
    sources = [[[rng.randrange(3) for _ in range(width)]
                for _ in range(width)] for _ in range(5)]
    readers[0] = [[int(r == c == 0) for c in range(width)] for r in range(width)]
    readers[1] = [[0] * width for _ in range(width)]
    sources[0] = [[int(c == (r + 1) % width) for c in range(width)]
                  for r in range(width)]
    return readers, sources


def execute(word, state, bank):
    rows = [row[:] for row in state]
    readers, sources = bank
    for op, label in word:
        target = 36 if op == "B" else 4 + label
        value = matvec(sources[label], rows[label]) if op == "B" else (
            matvec(readers[label - 1], rows[36]))
        rows[target] = [(a + b) % 3 for a, b in zip(rows[target], value)]
    return rows


def direct_target(state, bank, sign=1, wrong_order=False):
    rows = [row[:] for row in state]
    readers, sources = bank
    for mask in range(1, 32):
        for j in range(5):
            if (mask >> j) & 1:
                value = (matvec(sources[j], matvec(readers[mask - 1], state[j]))
                         if wrong_order else
                         matvec(readers[mask - 1], matvec(sources[j], state[j])))
                rows[4 + mask] = [(a + sign * b) % 3
                                  for a, b in zip(rows[4 + mask], value)]
    return rows


def dirty_states(width):
    states = []
    for coordinate in range(37 * width):
        state = [[0] * width for _ in range(37)]
        state[coordinate // width][coordinate % width] = 1
        states.append(state)
    for offset in range(3):
        states.append([[(r * width + c + offset) % 3 for c in range(width)]
                       for r in range(37)])
    return states


def dense_checks(word):
    reverse = list(reversed(word))
    cases = 0
    order_controls = 0
    for width in (1, 2, 3):
        bank = matrix_bank(width)
        for state in dirty_states(width):
            forward = execute(word, state, bank)
            backward = execute(reverse, state, bank)
            require(forward == direct_target(state, bank), "Dense forward action failed")
            require(backward == direct_target(state, bank, -1), "Dense reverse action failed")
            require(execute(reverse, forward, bank) == state, "Forward/reverse failed")
            require(execute(word, backward, bank) == state, "Reverse/forward failed")
            cases += 1
        if width > 1:
            state = [[0] * width for _ in range(37)]
            state[0][0] = 1
            require(direct_target(state, bank) != direct_target(state, bank, wrong_order=True),
                    "Factor-order control did not distinguish noncommuting maps")
            order_controls += 1
    return cases, order_controls


def main():
    live = source_bindings()
    word, triples = certificate()
    require(symbolic_action(word), "Generic forward coefficients failed")
    require(symbolic_action(list(reversed(word)), -1), "Unsigned reverse failed")
    controls = mutation_controls(word)
    cases, order_controls = dense_checks(word)
    tariffs = tariff_checks(word)
    hashes = {name: sha256(small_bytes(HERE / name)).hexdigest() for name in PACKAGE_FILES}
    receipt = {
        "schema": "f3-five-source-connector/v1",
        "claim_type": "scoped proof with finite certificate",
        "complete_calls": len(word), "operators": 36,
        "prefix_triples": triples, "covered_binary_masks": 31,
        "dirty_bank_inputs": cases, "dense_direction_comparisons": 2 * cases,
        "dense_roundtrips": 2 * cases,
        "semantic_controls": controls + order_controls,
        "unit_and_weighted_tariffs": tariffs,
        "package_sha256": hashes, "input_sha256": live,
    }
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    print(encoded)
    print("RECEIPT_SHA256 " + sha256(encoded.encode()).hexdigest())
    print("PASS_F3_FIVE_SOURCE_CONNECTOR calls=108 masks=31")


if __name__ == "__main__":
    main()
