#!/usr/bin/env python3
"""Finite evidence for the signed-connector ring-characteristic theorem."""

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
TARGET = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
OPERATORS = ("B0", "B1", "B2", "A0", "A1", "A2")
CHARACTERISTICS = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16)
BINARY_WORD = (("A", 0, -1), ("A", 1, -1), ("A", 2, -1),
               ("B", 0, 1), ("B", 1, 1), ("A", 2, 1),
               ("B", 2, 1), ("A", 0, 1), ("A", 1, 1),
               ("B", 0, -1), ("B", 1, -1), ("B", 2, -1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = {}
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            path = ROOT / entry["path"]
            data = path.read_bytes()
            require(digest(data) == entry["sha256"], f"source hash: {path}")
            inputs[entry["path"]] = data
    return inputs


def source_json(inputs, name):
    return json.loads(inputs[f"research/{name}/CERTIFICATE.json"])


def normalize(value, characteristic):
    return value % characteristic if characteristic else value


def coefficient_action(word):
    require(0 < len(word) <= 14, "word length outside finite evidence domain")
    source = [0, 0, 0]
    dirt = [0, 0, 0]
    rows = [[0, 0, 0] for _ in range(3)]
    for kind, index, sign in word:
        require(kind in ("A", "B") and index in range(3), "invalid port")
        require(sign in (-1, 1), "invalid query sign")
        if kind == "B":
            source[index] += sign
        else:
            dirt[index] += sign
            for column in range(3):
                rows[index][column] += sign * source[column]
    return source, dirt, rows


def correct(word, characteristic):
    source, dirt, rows = coefficient_action(word)
    residual = source + dirt
    residual += [rows[i][j] - TARGET[i][j]
                 for i in range(3) for j in range(3)]
    return all(normalize(value, characteristic) == 0 for value in residual)


def occurrences(word):
    return tuple(sum(kind + str(index) == name for kind, index, _ in word)
                 for name in OPERATORS)


def coefficient_checks():
    sign_cases = 0
    for characteristic in (0, *range(2, 18)):
        for length in range(1, 4):
            for signs in itertools.product((-1, 1), repeat=length):
                zero = normalize(sum(signs), characteristic) == 0
                expected = length == 2 and (
                    characteristic == 2 or sum(signs) == 0)
                expected |= characteristic == 3 and abs(sum(signs)) == 3
                require(zero == expected, "short signed-count law")
                sign_cases += 1
    vectors = tuple(itertools.product((-1, 0, 1), repeat=3))
    alias_cases = 0
    for characteristic in range(3, 18):
        for difference in vectors:
            for target in vectors:
                modular_equal = all((a - b) % characteristic == 0
                                    for a, b in zip(difference, target))
                require(modular_equal == (difference == target), "modular alias")
                alias_cases += 1
    require(normalize(1 - (-1), 2) == 0, "characteristic-two control")
    return sign_cases, alias_cases


def collect_words(inputs):
    integer = source_json(inputs, "weighted-signed-connector-seed58")["witnesses"]
    ternary = source_json(inputs, "ternary-connector-independent-seed84")["canonical_words"]
    require(set(integer) == set(ternary) == set(OPERATORS), "six witness keys")
    words = [(2, "paired", BINARY_WORD)]
    for name in OPERATORS:
        for characteristic, witnesses, extra in ((0, integer, 2), (3, ternary, 1)):
            word = tuple(tuple(query) for query in witnesses[name])
            require(len(word) == 12 + extra, "credited witness length")
            expected = tuple(2 + (extra if op == name else 0) for op in OPERATORS)
            require(occurrences(word) == expected, "credited witness counts")
            require(correct(word, characteristic), "witness coefficient action")
            words.append((characteristic, name, word))
    require(correct(BINARY_WORD, 2) and occurrences(BINARY_WORD) == (2,) * 6,
            "characteristic-two word")
    return words


def price_checks(words):
    prices = [tuple(Fraction(1 if i == j else 5) for i in range(6))
              for j in range(6)]
    prices += [tuple(Fraction(i + 1, i + 2) for i in range(6)), (Fraction(1),) * 6]
    cases = 0
    for characteristic, surcharge in ((0, 2), (2, 0), (3, 1)):
        candidates = [word for char, _, word in words if char == characteristic]
        for tariff in prices:
            bills = [sum(price * count for price, count in
                         zip(tariff, occurrences(word))) for word in candidates]
            require(min(bills) == 2 * sum(tariff) + surcharge * min(tariff),
                    "fixed-price envelope")
            cases += 1
    return cases


def add(left, right, sign, characteristic):
    return tuple(normalize(a + sign * b, characteristic) for a, b in zip(left, right))


def multiply(matrix, vector, characteristic):
    return tuple(normalize(sum(a * b for a, b in zip(row, vector)), characteristic)
                 for row in matrix)


def dual_matrix(seed):
    # Multiplication by a+b*epsilon is [[a,0],[b,a]], epsilon**2=0.
    matrix = [[0] * 4 for _ in range(4)]
    for i in range(2):
        for j in range(2):
            a = (seed + 2 * i + j) % 3 - 1
            b = (2 * seed + i + 3 * j) % 5 - 2
            matrix[2 * i][2 * j] = a
            matrix[2 * i + 1][2 * j] = b
            matrix[2 * i + 1][2 * j + 1] = a
    return tuple(tuple(row) for row in matrix)


def execute(word, bank, operators, characteristic):
    state = list(bank)
    for kind, index, sign in word:
        source, target = (index, 6) if kind == "B" else (6, 3 + index)
        matrix = operators[(kind, index)]
        state[target] = add(state[target], multiply(matrix, state[source], characteristic),
                            sign, characteristic)
    return tuple(state)


def target_bank(bank, operators, characteristic, sign=1):
    state = list(bank)
    for i in range(3):
        for j in range(3):
            bx = multiply(operators[("B", j)], bank[j], characteristic)
            abx = multiply(operators[("A", i)], bx, characteristic)
            state[3 + i] = add(state[3 + i], abx, sign * TARGET[i][j], characteristic)
    return tuple(state)


def dense_checks(words):
    operators = {(kind, j): dual_matrix(1 + j + 4 * (kind == "A"))
                 for kind in ("A", "B") for j in range(3)}
    a, b = operators[("A", 0)], operators[("B", 0)]
    require(multiply(a, multiply(b, (1, 0, 0, 0), 0), 0) !=
            multiply(b, multiply(a, (1, 0, 0, 0), 0), 0), "noncommuting maps")
    banks = [tuple(tuple(int(4 * role + k == column) for k in range(4))
                   for role in range(7)) for column in range(28)]
    banks += [tuple(tuple((seed + 3 * role + 2 * k) % 7 - 3 for k in range(4))
                    for role in range(7)) for seed in (1, 3)]
    cases = 0
    for characteristic in CHARACTERISTICS:
        selected = 2 if characteristic == 2 else 3 if characteristic == 3 else 0
        for char, _, word in words:
            if char != selected:
                continue
            inverse = tuple((kind, index, -sign) for kind, index, sign in reversed(word))
            for raw in banks:
                bank = tuple(tuple(normalize(x, characteristic) for x in row) for row in raw)
                output = execute(word, bank, operators, characteristic)
                require(output == target_bank(bank, operators, characteristic), "dense action")
                require(execute(inverse, bank, operators, characteristic) ==
                        target_bank(bank, operators, characteristic, -1), "dense inverse")
                require(execute(inverse, output, operators, characteristic) == bank,
                        "dirty round trip")
                cases += 1
    return cases


def negative_checks(words):
    cases = 0
    for char, _, word in words:
        if char == 0:
            for index in range(len(word)):
                require(not correct(word[:index] + word[index + 1:], 4), "deleted query")
                changed = list(word)
                kind, port, sign = changed[index]
                changed[index] = (kind, port, -sign)
                require(not correct(changed, 4), "flipped query")
                cases += 2
        if char == 3:
            for wrong in (0, 4, 5, 6, 9):
                require(not correct(word, wrong), "ternary-only restoration")
                cases += 1
    require(not correct(BINARY_WORD, 3), "binary sign alias control")
    cases += 1
    return cases


def receipt():
    inputs = read_inputs()
    words = collect_words(inputs)
    sign_cases, alias_cases = coefficient_checks()
    counts = {"signed_count_cases": sign_cases, "no_alias_cases": alias_cases,
              "price_cases": price_checks(words), "dense_cases": dense_checks(words),
              "negative_controls": negative_checks(words), "witnesses": len(words)}
    payload = {path.name: digest(path.read_bytes()) for path in sorted(PACKAGE.iterdir())
               if path.is_file() and path.name != "RESULT.json"}
    return {"schema": "signed-characteristic-spectrum/v1", "counts": counts,
            "payload_sha256": payload,
            "input_sha256": {path: digest(data) for path, data in sorted(inputs.items())},
            "status": "PASS_SIGNED_CHARACTERISTIC_SPECTRUM"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    result = receipt()
    if args.write_receipt:
        destination = args.write_receipt.resolve()
        require(not destination.is_relative_to(ROOT), "receipt output must be outside checkout")
        with destination.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(result == expected, "generated receipt differs")
    print(result["status"], json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
