#!/usr/bin/env python3
"""Emit the finite clean-helper exchange certificate to stdout."""

import hashlib
import itertools
import json


GATES = tuple((d, s) for d in range(5) for s in range(5) if d != s)


def add(rows, gate):
    destination, source = gate
    result = list(rows)
    result[destination] ^= result[source]
    return tuple(result)


def ball(start, radius):
    seen = {start}
    frontier = {start}
    layers = [1]
    for _ in range(radius):
        following = {add(rows, gate) for rows in frontier for gate in GATES} - seen
        seen.update(following)
        frontier = following
        layers.append(len(frontier))
    return seen, layers


def truth_state(rows):
    result = 0
    for wire, row in enumerate(rows):
        for data in range(16):
            result |= ((row & data).bit_count() % 2) << (16 * wire + data)
    return result


def digest(states):
    values = sorted(truth_state(rows) for rows in states)
    payload = json.dumps(values, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def certificate():
    initial = (1, 2, 4, 8, 0)
    left, layers = ball(initial, 2)
    bases = tuple((a, b) for a in range(1, 4) for b in range(1, 4) if a != b)
    endpoints = []
    for upper, lower in itertools.product(bases, repeat=2):
        target = (upper[0] << 2, upper[1] << 2, *lower, 0)
        right, right_layers = ball(target, 3)
        if left.intersection(right):
            raise ValueError("a word of length at most five exists")
        endpoints.append({"rows": target, "layers": right_layers,
                          "states": len(right), "sha256": digest(right)})
    words = []
    for pairs in (((0, 2), (1, 3)), ((0, 3), (1, 2))):
        word = tuple(gate for a, b in pairs for gate in ((a, b), (b, a), (a, b)))
        rows = initial
        for gate in word:
            rows = add(rows, gate)
        words.append({"gates": word, "rows": rows})
    return {"schema_version": 1, "data_wires": 4, "clean_helpers": 1,
            "gate_count": 20, "excluded_maximum_length": 5,
            "prefix": {"layers": layers, "states": len(left), "sha256": digest(left)},
            "endpoints": endpoints, "six_add_attainments": words}


if __name__ == "__main__":
    print(json.dumps(certificate(), indent=2) + "\n", end="")
