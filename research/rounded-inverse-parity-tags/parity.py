"""Coordinate-parity recovery for one fixed rounded native inverse.

Produced by Nick Petalas. Apache-2.0.
The native matrix and rounded-map interface are credited in README.md.
"""

import hashlib
import itertools
import json
from pathlib import Path

OWNERS = 112
MODES = 8
INPUT_BITS = 4096
SELECTED = (0, 9, 27, 76, 79)
MATRIX_HASH = "2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def matrix():
    path = Path(__file__).with_name("MATRIX.json")
    need(path.stat().st_size <= 1 << 20, "matrix file size bound")
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MATRIX_HASH, "matrix source hash")
    columns = json.loads(raw)["mode_columns"]
    need(len(columns) == MODES, "matrix mode count")
    need(all(len(c) == OWNERS for c in columns), "matrix owner count")
    need(all(type(a) is int and a in (-1, 0, 1) for c in columns for a in c),
         "matrix entry domain")
    return tuple(zip(*columns))


def vector(values, length, bits, label):
    need(type(values) in (list, tuple) and len(values) == length, label + " length")
    need(all(type(a) is int and a.bit_length() <= bits for a in values),
         label + " integer domain")


def times(rows, values):
    return tuple(sum(a * b for a, b in zip(row, values)) for row in rows)


def transpose_times(rows, values):
    return tuple(sum(rows[i][j] * values[i] for i in range(OWNERS))
                 for j in range(MODES))


def round52(value):
    magnitude = (abs(value) + 26) // 52
    return magnitude if value >= 0 else -magnitude


def forward(rows, values):
    vector(values, OWNERS, INPUT_BITS, "input")
    modes = transpose_times(rows, values)
    quotient = tuple(round52(16 * a) for a in modes)
    correction = times(rows, quotient)
    return tuple(16 * a - b for a, b in zip(values, correction))


def encode(rows, values):
    output = forward(rows, values)
    return output, tuple(values[i] % 2 for i in SELECTED)


def right_inverse(rows):
    """Return sparse columns B_j with M^T B_j = 2 e_j."""
    witnesses = []
    for j in range(MODES):
        target = tuple(2 * (k == j) for k in range(MODES))
        found = None
        for a, b, sign in itertools.product(range(OWNERS), range(OWNERS), (-1, 1)):
            if tuple(rows[a][k] + sign * rows[b][k] for k in range(MODES)) == target:
                found = (a, b, sign)
                break
        need(found is not None, "missing two-unit row witness")
        witnesses.append(found)
    return tuple(witnesses)


def quotient_lists(rows, basis, output):
    moments = transpose_times(rows, output)
    choices = []
    for j, (a, b, sign) in enumerate(basis):
        paired = output[a] + sign * output[b]
        need(paired % 2 == 0, "output fails two-unit congruence")
        residue = (-paired // 2) % 8
        low = -((26 + moments[j]) // 4)
        high = (26 - moments[j]) // 4
        candidates = tuple(q for q in range(low, high + 1) if q % 8 == residue)
        need(0 < len(candidates) <= 2, "quotient candidate bound")
        choices.append(candidates)
    return choices


def decode(rows, basis, output, tags):
    vector(output, OWNERS, INPUT_BITS + 12, "output")
    vector(tags, len(SELECTED), 1, "tags")
    need(all(a in (0, 1) for a in tags), "tag bit domain")
    choices = quotient_lists(rows, basis, output)
    answer = None
    for quotient in itertools.product(*choices):
        numerator = tuple(a + b for a, b in zip(output, times(rows, quotient)))
        if any(a % 16 for a in numerator):
            continue
        candidate = tuple(a // 16 for a in numerator)
        if tuple(candidate[i] % 2 for i in SELECTED) != tuple(tags):
            continue
        if any(a.bit_length() > INPUT_BITS for a in candidate):
            continue
        if forward(rows, candidate) != tuple(output):
            continue
        need(answer is None, "coordinate tags are ambiguous")
        answer = candidate
    need(answer is not None, "no matching preimage")
    return answer


def directions(rows):
    result = []
    for v in itertools.product((-1, 0, 1), repeat=MODES):
        if not any(v):
            continue
        image = times(rows, v)
        if all(a % 2 == 0 for a in image):
            result.append((v, tuple(a // 2 for a in image)))
    return tuple(result)


def collision_pair(rows, basis, direction):
    left = [0] * OWNERS
    for v, (a, b, sign) in zip(direction, basis):
        left[a] -= 7 * v
        left[b] -= 7 * sign * v
    difference = times(rows, direction)
    need(all(a % 2 == 0 for a in difference), "nonintegral collision")
    right = tuple(a + b // 2 for a, b in zip(left, difference))
    return tuple(left), right
