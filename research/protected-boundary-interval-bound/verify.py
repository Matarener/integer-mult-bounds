#!/usr/bin/env python3
"""Exact checks of the protected-boundary interval inequality. Apache-2.0."""

import hashlib
import json
from pathlib import Path


MAX_FACTORS = 16
MAX_HEIGHT = 4
MAX_TERMS = 64
MAX_WORD = 32
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def envelope(height):
    require(type(height) is int and 0 <= height <= 10000, "invalid height")
    return 2 if height == 0 else height * height + 2 * height + 3


def identity(size):
    require(type(size) is int and 1 <= size <= 12, "invalid matrix size")
    return [[{(): 1} if i == j else {} for j in range(size)] for i in range(size)]


def add(left, right, sign=1):
    result = dict(left)
    for word, coefficient in right.items():
        value = result.get(word, 0) + sign * coefficient
        if value:
            result[word] = value
        else:
            result.pop(word, None)
    require(len(result) <= MAX_TERMS, "polynomial capacity")
    require(all(len(word) <= MAX_WORD for word in result), "word capacity")
    return result


def multiply(left, right):
    result = {}
    for first, a in left.items():
        for second, b in right.items():
            word = first + second
            result[word] = result.get(word, 0) + a * b
    require(len(result) <= MAX_TERMS, "product capacity")
    require(all(len(word) <= MAX_WORD for word in result), "word capacity")
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def product(left, right):
    size = len(left)
    require(len(right) == size, "matrix size mismatch")
    result = [[{} for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] = add(result[i][j], multiply(left[i][k], right[k][j]))
    return result


def row_mass(row):
    return sum(abs(value) for entry in row for value in entry.values())


def matrix_mass(matrix):
    return max(row_mass(row) for row in matrix)


def generic_template(height, label):
    """Independent formal entries, with source first and target last."""
    size = height + 2
    result = identity(size)
    for i in range(1, size):
        for j in range(size - 1):
            result[i][j] = {((label, i, j),): 1}
    return result


def check_block_counts():
    cases = 0
    for height in range(1, 9):
        left = generic_template(height, "p")
        right = generic_template(height, "q")
        combined = product(left, right)
        require(row_mass(combined[0]) == 1, "protected source count")
        require(row_mass(combined[-1]) == envelope(height), "target block count")
        for row in combined[1:-1]:
            require(row_mass(row) == height * height + height + 1, "scratch block count")
        cases += 1
    for height in range(1, 10001):
        require((height + 2) ** 2 - envelope(height) == 2 * height + 1, "strict gain")
    return cases


def leaf_word(factors, sign):
    require(type(factors) is int and 1 <= factors <= MAX_FACTORS, "invalid factor count")
    require(type(sign) is int and sign in (-1, 1), "invalid sign")
    height = (factors - 1).bit_length()
    require(height <= MAX_HEIGHT, "height capacity")
    stack = [(0, factors, 0, 1, 0, sign)]
    result = []
    for _ in range((4 ** (height + 1) - 1) // 3):
        if not stack:
            break
        start, count, source, target, depth, direction = stack.pop()
        if count == 1:
            result.append((start, source, target, direction))
            continue
        left = count // 2
        connector = depth + 2
        u = (start, left, source, connector, depth + 1)
        v = (start + left, count - left, connector, target, depth + 1)
        children = (u + (1,), v + (1,), u + (-1,), v + (-1,))
        if direction == -1:
            children = (v + (1,), u + (1,), v + (-1,), u + (-1,))
        stack.extend(reversed(children))
    require(not stack, "node budget exhausted")
    q = 1 << (factors.bit_length() - 1)
    require(len(result) == 3 * q * factors - 2 * q * q, "word extent")
    return result, height + 2


def apply_leaf(matrix, event):
    factor, source, target, sign = event
    require(source != target, "aliased leaf")
    row = []
    for entry in matrix[source]:
        row.append({(factor,) + word: value for word, value in entry.items()})
    matrix[target] = [add(old, new, sign) for old, new in zip(matrix[target], row, strict=True)]


def check_word(factors, sign):
    events, size = leaf_word(factors, sign)
    height = size - 2
    intervals = 0
    for start in range(len(events)):
        matrix = identity(size)
        for end in range(start, len(events)):
            apply_leaf(matrix, events[end])
            require(matrix_mass(matrix) <= envelope(height), "new interval envelope")
            require(matrix[0] == identity(size)[0], "source changed")
            require(all(matrix[i][1] == ({(): 1} if i == 1 else {})
                        for i in range(size)), "target was read")
            intervals += 1
    complete = identity(size)
    for event in events:
        apply_leaf(complete, event)
    expected = identity(size)
    expected[1][0] = {tuple(range(factors - 1, -1, -1)): sign}
    require(complete == expected, "full arbitrary-dirty endpoint")
    return intervals


def must_reject(function, argument):
    try:
        function(argument)
    except ValueError:
        return
    raise ValueError("invalid argument accepted")


def check_controls():
    controls = 0
    for value in (True, -1, 10001, 1.0):
        must_reject(envelope, value)
        controls += 1
    for value in (True, 0, 17):
        must_reject(lambda count: leaf_word(count, 1), value)
        controls += 1
    for value in (True, 0, 2):
        must_reject(lambda sign: leaf_word(2, sign), value)
        controls += 1
    # These abstract controls deliberately remove one premise at a time.
    size = 3
    dense = [[{(("d", i, j),): 1} for j in range(size)] for i in range(size)]
    source_only = [[dict(entry) for entry in row] for row in dense]
    source_only[0] = identity(size)[0]
    target_only = [[dict(entry) for entry in row] for row in dense]
    for i in range(size):
        target_only[i][-1] = {(): 1} if i == size - 1 else {}
    require(matrix_mass(product(source_only, source_only)) > envelope(1), "unread-target control")
    require(matrix_mass(product(target_only, target_only)) > envelope(1), "protected-source control")
    scaled = generic_template(1, "s")
    scaled[-1][0] = {(("s", 2, 0),): 10}
    require(matrix_mass(product(scaled, scaled)) > envelope(1), "entry-size control")
    controls += 3
    require(envelope(1) > 3, "must not label the upper envelope sharp")
    controls += 1
    return controls


def main():
    block_cases = check_block_counts()
    controls = check_controls()
    intervals = 0
    fixtures = (1, 2, 3, 5, 8, 11)
    for factors in fixtures:
        positive, _ = leaf_word(factors, 1)
        negative, _ = leaf_word(factors, -1)
        require(negative == [(a, b, c, -d) for a, b, c, d in reversed(positive)], "literal inverse")
        for sign in (-1, 1):
            intervals += check_word(factors, sign)
    package = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in FILES}
    receipt = {"status": "PASS_PROTECTED_BOUNDARY_INTERVAL_BOUND", "claim_type": "scoped proof",
               "generic_block_cases": block_cases, "strict_gain_heights": 10000,
               "word_factor_counts": list(fixtures), "word_orientations": 12,
               "nonempty_intervals": intervals, "controls": controls, "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
