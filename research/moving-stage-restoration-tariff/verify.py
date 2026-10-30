#!/usr/bin/env python3
"""Exact positive moving-stage tariff. Produced by Nick Petalas; Apache-2.0."""

import argparse
from collections import deque
import hashlib
import json
from math import factorial
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PRIME = 65537
MAX_BLOCKS = 6


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(blocks, support, anchor):
    require(type(blocks) is int and 1 <= blocks <= MAX_BLOCKS, "block bound")
    require(type(anchor) is int and anchor in (0, 1), "anchor parity")
    require(type(support) is frozenset, "support representation")
    require(all(type(s) is int and 1 <= s < blocks for s in support), "support")


def construct(blocks, support, anchor):
    validate(blocks, support, anchor)
    correction = (len(support) + anchor) % 2
    word = tuple(s for s in sorted(support) for _ in range(2))
    return word + (0,) * correction


def normal_form(word, blocks):
    """P_perm times product D_j^exponent, with exact integer exponents."""
    require(1 <= blocks <= MAX_BLOCKS and len(word) <= 2 * blocks, "word bound")
    require(all(type(s) is int and 0 <= s < blocks for s in word), "stage")
    permutation = list(range(blocks))
    exponents = [0] * blocks
    for s in word:
        exponents[permutation.index(0)] += 1
        permutation = [s if x == 0 else 0 if x == s else x for x in permutation]
    require(sum(exponents) == len(word), "one Gaussian per stage")
    return tuple(permutation), tuple(exponents)


def quotient_oracle(blocks):
    """BFS in the independent output-frame form D_mask P_perm."""
    identity = tuple(range(blocks))
    start = (identity, 0)
    distances = {start: 0}
    queue = deque([start])
    capacity = factorial(blocks) * (1 << blocks)
    for _ in range(capacity):
        if not queue:
            break
        permutation, mask = queue.popleft()
        for s in range(blocks):
            moved = mask ^ 1
            if s and (moved & 1) != ((moved >> s) & 1):
                moved ^= 1 | (1 << s)
            p = tuple(s if x == 0 else 0 if x == s else x for x in permutation)
            state = (p, moved)
            if state not in distances:
                require(len(distances) < capacity, "finite quotient capacity")
                distances[state] = distances[(permutation, mask)] + 1
                queue.append(state)
    require(not queue and len(distances) == capacity, "complete quotient")
    for mask in range(1 << blocks):
        support = frozenset(s for s in range(1, blocks) if mask >> s & 1)
        word = construct(blocks, support, mask & 1)
        require(distances[(identity, mask)] == len(word), "shortest tariff")
        p, exponents = normal_form(word, blocks)
        require(p == identity, "constructor restores permutation")
        actual_mask = sum((e % 2) << s for s, e in enumerate(exponents))
        require(actual_mask == mask, "constructor Gaussian support")
    return capacity, 1 << blocks


def gaussian(values, axis):
    imaginary = 256
    a = (1 + imaginary) * pow(2, -1, PRIME) % PRIME
    b = (1 - imaginary) * pow(2, -1, PRIME) % PRIME
    out = list(values)
    bit = 1 << axis
    for x in range(len(values)):
        if not x & bit:
            y = x | bit
            out[x] = (a * values[x] + b * values[y]) % PRIME
            out[y] = (b * values[x] + a * values[y]) % PRIME
    return out


def swap_blocks(values, stage, width):
    out = [0] * len(values)
    block_mask = (1 << width) - 1
    for x, value in enumerate(values):
        difference = ((x >> (stage * width)) ^ x) & block_mask
        y = x ^ difference ^ (difference << (stage * width))
        out[y] = value
    return out


def execute(word, initial, width):
    values = list(initial)
    for s in word:
        for axis in range(width):
            values = gaussian(values, axis)
        values = swap_blocks(values, s, width)
    return values


def target(initial, support_mask, blocks, width, anchor_flip):
    values = list(initial)
    for s in range(blocks):
        if support_mask >> s & 1:
            for axis in range(s * width, (s + 1) * width):
                values = gaussian(values, axis)
    if anchor_flip:
        values = [values[x ^ ((1 << width) - 1)] for x in range(len(values))]
    return values


def literal_checks():
    require(pow(256, 2, PRIME) == PRIME - 1, "imaginary unit")
    columns = 0
    for blocks, width in ((1, 1), (2, 1), (3, 1), (4, 1), (2, 2), (3, 2)):
        dimension = 1 << (blocks * width)
        for mask in range(1 << blocks):
            support = frozenset(s for s in range(1, blocks) if mask >> s & 1)
            anchor = mask & 1
            word = construct(blocks, support, anchor)
            delta = (len(support) + anchor) % 2
            even_exponent = len(support) + delta - anchor
            require(even_exponent >= 0 and even_exponent % 2 == 0, "local monomial")
            for column in range(dimension):
                initial = [int(x == column) for x in range(dimension)]
                actual = execute(word, initial, width)
                expected = target(initial, mask, blocks, width, (even_exponent // 2) % 2)
                require(actual == expected, "literal full operator column")
                columns += 1
    return columns


def rejection_controls():
    invalid = ((0, frozenset(), 0), (7, frozenset(), 0),
               (2, frozenset({2}), 0), (2, frozenset({0}), 0),
               (2, frozenset({1}), 2), (True, frozenset(), 0),
               (2, {1}, 0), (2, frozenset({True}), 0))
    for args in invalid:
        rejected = False
        try:
            construct(*args)
        except ValueError:
            rejected = True
        require(rejected, "invalid constructor accepted")
    p, exponents = normal_form((1, 2, 0), 3)
    require(all(e % 2 == 1 for e in exponents), "externally normalized positive control")
    require(p != (0, 1, 2), "external permutation is still unpaid")
    p, exponents = normal_form((1, 1), 2)
    require(p == (0, 1) and exponents == (1, 1), "anchor correction omission")
    p, _ = normal_form((1,), 2)
    require(p != (0, 1), "return omission")
    initial = [1] + [0] * 15
    word = construct(4, frozenset({1, 2, 3}), 1)
    require(execute(word, initial, 1) != target(initial, 15, 4, 1, 0),
            "residual local monomial must not be omitted")
    return len(invalid) + 4


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(inputs) == 2, "two predecessor text inputs")
    for row in inputs:
        data = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "source hash")


def run():
    authenticate()
    states = targets = 0
    for blocks in range(1, MAX_BLOCKS + 1):
        count, endpoints = quotient_oracle(blocks)
        states += count
        targets += endpoints
    return {"status": "PASS_MOVING_STAGE_RESTORATION_TARIFF",
            "quotient_states": states, "restored_endpoints": targets,
            "literal_columns": literal_checks(), "controls": rejection_controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="create a new hash-bound receipt")
    args = parser.parse_args()
    result = run()
    if args.receipt is not None:
        names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
        result["package_sha256"] = {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names}
        with args.receipt.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
