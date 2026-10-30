#!/usr/bin/env python3
"""Exact finite corroboration of the rectangular augmentation-rank proof."""

import hashlib
import itertools
import json
from pathlib import Path


MAX_ROLES = 4


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows, columns):
    need(0 <= columns <= 12, "represented column bound")
    need(len(rows) <= 12, "represented row bound")
    need(all(0 <= row < 1 << columns for row in rows), "binary row")
    work = list(rows)
    pivot = 0
    for column in range(columns):
        found = next((i for i in range(pivot, len(work)) if work[i] >> column & 1), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        for i in range(pivot + 1, len(work)):
            if work[i] >> column & 1:
                work[i] ^= work[pivot]
        pivot += 1
    return pivot


def apply_linear(rows, value):
    return sum(((row & value).bit_count() & 1) << i for i, row in enumerate(rows))


def xor_rows(rows, mask):
    result = 0
    for i, row in enumerate(rows):
        if mask >> i & 1:
            result ^= row
    return result


def make_group(dimension):
    need(dimension in (1, 2), "finite address dimension")
    size = 1 << dimension
    identity = tuple(1 << i for i in range(dimension))
    elements = [(identity, 0)]
    for rows in itertools.product(range(size), repeat=dimension):
        if rank(rows, dimension) == dimension:
            elements.extend((rows, b) for b in range(size) if (rows, b) != (identity, 0))
    need(len(elements) <= 24, "finite group bound")
    index = {g: i for i, g in enumerate(elements)}
    table = []
    actions = [tuple(apply_linear(a, x) ^ b for x in range(size)) for a, b in elements]
    action_index = {p: i for i, p in enumerate(actions)}
    for i, (a, b) in enumerate(elements):
        row = []
        for j, (c, e) in enumerate(elements):
            linear = tuple(xor_rows(c, a[k]) for k in range(dimension))
            product = index[(linear, apply_linear(a, e) ^ b)]
            literal = action_index[tuple(actions[i][actions[j][x]] for x in range(size))]
            need(product == literal, "independent point-composition law")
            row.append(product)
        table.append(tuple(row))
    homogeneous = [tuple(a[i] | ((b >> i & 1) << dimension) for i in range(dimension))
                   + (1 << dimension,) for a, b in elements]
    return tuple(table), tuple(homogeneous)


def ring_product(a, b, table):
    result = 0
    for i in range(len(table)):
        if a >> i & 1:
            for j in range(len(table)):
                if b >> j & 1:
                    result ^= 1 << table[i][j]
    return result


def shape(matrix):
    need(isinstance(matrix, tuple) and 1 <= len(matrix) <= MAX_ROLES, "matrix rows")
    width = len(matrix[0])
    need(1 <= width <= MAX_ROLES and all(len(row) == width for row in matrix), "matrix columns")
    return len(matrix), width


def multiply(left, right, table):
    height, inner = shape(left)
    other_inner, width = shape(right)
    need(inner == other_inner, "composition dimensions")
    result = []
    for i in range(height):
        row = []
        for j in range(width):
            value = 0
            for k in range(inner):
                value ^= ring_product(left[i][k], right[k][j], table)
            row.append(value)
        result.append(tuple(row))
    return tuple(result)


def scalar(rows, width):
    need(1 <= width <= MAX_ROLES, "scalar width")
    need(all(0 <= row < 1 << width for row in rows), "scalar entries")
    result = tuple(tuple(row >> j & 1 for j in range(width)) for row in rows)
    shape(result)
    return result


def image(matrix, homogeneous, augmentation=False):
    height, width = shape(matrix)
    block = len(homogeneous[0])
    result = [0] * (height * block)
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            need(0 <= value < 1 << len(homogeneous), "formal coefficient bound")
            for g in range(len(homogeneous)):
                if value >> g & 1:
                    for a in range(block):
                        bits = 1 << a if augmentation else homogeneous[g][a]
                        result[i * block + a] ^= bits << (j * block)
    return tuple(result)


def defect(matrix, homogeneous):
    actual = image(matrix, homogeneous)
    baseline = image(matrix, homogeneous, augmentation=True)
    rows = tuple(a ^ b for a, b in zip(actual, baseline, strict=True))
    return rank(rows, len(matrix[0]) * len(homogeneous[0]))


def identity(roles):
    return scalar(tuple(1 << i for i in range(roles)), roles)


def paid(roles, label, u, v):
    need(1 <= roles <= MAX_ROLES, "paid roles")
    need(0 < u < 1 << roles and 0 < v < 1 << roles, "paid vectors")
    need((u & v).bit_count() & 1, "paid idempotence")
    need(0 < label < 24, "paid label index")
    return tuple(tuple((int(i == j) ^ ((1 ^ (1 << label))
                       if (u >> i & 1) and (v >> j & 1) else 0))
                       for j in range(roles)) for i in range(roles))


def exhaustive_rectangles(table, homogeneous):
    inventories = {}
    for height, width in itertools.product((1, 2), repeat=2):
        inventories[height, width] = tuple(
            tuple(tuple(values[i * width:(i + 1) * width]) for i in range(height))
            for values in itertools.product(range(4), repeat=height * width))
    count = 0
    transcript = hashlib.sha256()
    cached = {m: defect(m, homogeneous) for matrices in inventories.values() for m in matrices}
    for matrix, value in cached.items():
        rows = tuple(a ^ b for a, b in zip(image(matrix, homogeneous),
                     image(matrix, homogeneous, augmentation=True), strict=True))
        span = {0}
        for row in rows:
            span |= {x ^ row for x in tuple(span)}
        need(len(span) == 1 << value, "independent row-span rank oracle")
    for height, inner, width in itertools.product((1, 2), repeat=3):
        for a in inventories[height, inner]:
            for b in inventories[inner, width]:
                product = multiply(a, b, table)
                value = cached[product]
                need(value <= cached[a] + cached[b], "rectangular defect inequality")
                transcript.update(bytes((height, inner, width, value)))
                count += 1
    return count, transcript.hexdigest()


def free_and_paid(homogeneous):
    free_count = 0
    paid_count = 0
    labels = [g for g in range(1, len(homogeneous))
              if defect(((1 << g,),), homogeneous) == 1]
    for height, width in itertools.product(range(1, 4), repeat=2):
        for bits in range(1 << (height * width)):
            matrix = scalar(tuple(bits >> (i * width) & ((1 << width) - 1)
                                  for i in range(height)), width)
            need(defect(matrix, homogeneous) == 0, "free rectangular map")
            free_count += 1
    for roles in range(1, 4):
        for u, v in itertools.product(range(1, 1 << roles), repeat=2):
            if (u & v).bit_count() & 1:
                for g in labels:
                    need(defect(paid(roles, g, u, v), homogeneous) == 1, "paid rank")
                    paid_count += 1
    return free_count, paid_count, labels


def regular_apply(matrix, vector, table):
    """Separate faithful action using sets, rather than packed convolution."""
    height, width = shape(matrix)
    need(len(vector) == width, "regular input width")
    output = []
    for i in range(height):
        entries = set()
        for j in range(width):
            support = [g for g in range(len(table)) if matrix[i][j] >> g & 1]
            for g in support:
                for h in vector[j]:
                    value = table[g][h]
                    entries.symmetric_difference_update((value,))
        output.append(frozenset(entries))
    return tuple(output)


def replay(events, table):
    operator = identity(len(events[0][0]))
    for event in events:
        operator = multiply(event, operator, table)
    return operator


def clean_events(first, second):
    enter = scalar((1, 2, 0, 0), 2)
    copy = scalar((1, 2, 5, 10), 4)
    erase = scalar((0, 0, 4, 8), 4)
    select = scalar((4, 8), 4)
    calls = [paid(4, first[0], 4, 4), paid(4, first[1], 4, 4),
             paid(4, second[0], 8, 8), paid(4, second[1], 8, 8)]
    return [enter, copy, *calls, erase, select]


def clean_fixtures(table, homogeneous, labels):
    pairs = [(a, b) for a, b in itertools.product(labels, repeat=2)
             if table[a][b] != table[b][a]
             and defect(((1 << table[b][a],),), homogeneous) == 2]
    need(len(pairs) > 0, "noncommuting fixture domain")
    columns = 0
    omissions = 0
    for i, first in enumerate(pairs):
        second = pairs[(i + 1) % len(pairs)]
        events = clean_events(first, second)
        target = ((1 << table[first[1]][first[0]], 0),
                  (0, 1 << table[second[1]][second[0]]))
        need(replay(events, table) == target, "full formal clean endpoint")
        need(defect(target, homogeneous) == 4, "sharp four-call boundary")
        for call in range(2, 6):
            need(replay(events[:call] + events[call + 1:], table) != target, "omitted call")
            omissions += 1
        for role, g in itertools.product(range(2), range(len(table))):
            vector = tuple(frozenset((g,)) if j == role else frozenset() for j in range(2))
            expected = regular_apply(target, vector, table)
            actual = vector
            for event in events:
                actual = regular_apply(event, actual, table)
            need(actual == expected, "faithful arbitrary-input clean circuit")
            columns += 1
    return len(pairs), columns, omissions, pairs[0]


def controls(table, homogeneous, pair):
    count = 0
    events = clean_events(pair, pair)
    dirty = [identity(4), *events[1:]]
    need(replay(dirty, table)[0][2] != 0, "dirty-helper leak control")
    count += 1
    norm = (1 << len(table)) - 1
    need(norm != 0 and image(((norm,),), homogeneous) == (0, 0, 0), "nonfaithful kernel")
    target = replay(events, table)
    altered = ((target[0][0] ^ norm, target[0][1]), target[1])
    need(image(altered, homogeneous) == image(target, homogeneous) and altered != target,
         "represented equality cannot certify formal equality")
    count += 1
    need(defect(((1 << pair[0],),), homogeneous) == 1, "free address countercontrol")
    count += 1
    double = ((1 << pair[0], 0), (0, 1 << pair[0]))
    need(defect(double, homogeneous) == 2, "rank-two undercharge control")
    count += 1
    for case in range(4):
        try:
            if case == 0:
                make_group(3)
            elif case == 1:
                scalar((2,), 1)
            elif case == 2:
                paid(2, pair[0], 1, 2)
            else:
                multiply(identity(1), identity(2), table)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid domain accepted")
    return count


def main():
    small_table, small_homogeneous = make_group(1)
    table, homogeneous = make_group(2)
    rectangles, digest = exhaustive_rectangles(small_table, small_homogeneous)
    free_count, paid_count, labels = free_and_paid(homogeneous)
    fixtures, columns, omissions, pair = clean_fixtures(table, homogeneous, labels)
    result = {
        "status": "PASS_CLEAN_AFFINE_ERASURE_FLOOR", "claim_type": "scoped proof with finite corroboration",
        "rectangular_products": rectangles, "rectangular_digest": digest,
        "free_scalar_maps": free_count, "paid_factors": paid_count,
        "clean_erasing_fixtures": fixtures, "faithful_basis_columns": columns,
        "omission_controls": omissions, "boundary_controls": controls(table, homogeneous, pair),
        "new_fixture_minimum": 4, "no_new_kappa": True,
    }
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["source_sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                               for name in names}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
