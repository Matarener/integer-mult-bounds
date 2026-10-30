#!/usr/bin/env python3
"""Exact four-role C3 tariff certificate. Standard library; writes nothing."""
import hashlib
import json
from pathlib import Path

ROLES = 4
EVEN = 0x55
IDENTITY = tuple(1 << (2 * i) for i in range(ROLES))
TARGET = tuple(3 << (2 * i) for i in range(ROLES))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def omega(row):
    a, b = row & EVEN, (row >> 1) & EVEN
    return b | ((a ^ b) << 1)


def binary_rank(rows, width=4):
    pivots = [0] * width
    rank = 0
    for original in rows:
        row = original
        for bit in range(width - 1, -1, -1):
            if not (row >> bit) & 1:
                continue
            if pivots[bit]:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                rank += 1
                break
    return rank


def projectors():
    return tuple((u, v) for u in range(1, 16) for v in range(1, 16)
                 if (u & v).bit_count() % 2 == 1)


def left_gate(matrix, coupling, inverse=False):
    u, v = coupling
    need(0 < u < 16 and 0 < v < 16 and (u & v).bit_count() % 2 == 1,
         "coupling must be a binary rank-one idempotent")
    total = 0
    for j in range(ROLES):
        if (v >> j) & 1:
            total ^= matrix[j]
    delta = omega(total) if inverse else total ^ omega(total)
    return tuple(row ^ (delta if (u >> i) & 1 else 0)
                 for i, row in enumerate(matrix))


def multiply(left, right):
    result = []
    for row in left:
        total = 0
        for j in range(ROLES):
            coefficient = (row >> (2 * j)) & 3
            if coefficient & 1:
                total ^= right[j]
            if coefficient & 2:
                total ^= omega(right[j])
        result.append(total)
    return tuple(result)


def field_table(gates):
    table = {IDENTITY: ()}
    for i, gate in enumerate(gates):
        table[left_gate(IDENTITY, gate)] = (i,)
    for i, first in enumerate(gates):
        prefix = left_gate(IDENTITY, first)
        for j, second in enumerate(gates):
            table.setdefault(left_gate(prefix, second), (i, j))
    return table


def field_join(target, gates, table):
    # Chronological first factor is E00. The endpoint is scalar, so binary
    # simultaneous conjugation makes this normalization complete.
    first = gates.index((1, 1))
    wanted = multiply(target, left_gate(IDENTITY, gates[first], inverse=True))
    hits = []
    for word in table.values():
        complement = wanted
        # P=G_last...G_first, so right multiplication by P^-1 takes the
        # inverse factors in chronological order, not reversed order.
        for index in word:
            inverse = left_gate(IDENTITY, gates[index], inverse=True)
            complement = multiply(complement, inverse)
        if complement in table:
            witness = (first,) + word + table[complement]
            actual = IDENTITY
            for index in witness:
                actual = left_gate(actual, gates[index])
            need(actual == target, "join produced a false endpoint")
            hits.append(witness)
    return hits


def ring_times(a, b):
    result = 0
    for i in range(3):
        for j in range(3):
            if ((a >> i) & 1) and ((b >> j) & 1):
                result ^= 1 << ((i + j) % 3)
    return result


def ring_identity():
    return tuple(int(i == j) for i in range(4) for j in range(4))


def ring_gate(matrix, coupling, right=False, inverse=False):
    # Separate full group-ring implementation; no F4 arithmetic is imported.
    u, v = coupling
    delta = 5 if inverse else 3  # 1+g^2 or 1+g.
    out = list(matrix)
    if right:
        for i in range(4):
            total = 0
            for k in range(4):
                if (u >> k) & 1:
                    total ^= matrix[4 * i + k]
            for j in range(4):
                if (v >> j) & 1:
                    out[4 * i + j] ^= ring_times(total, delta)
    else:
        for j in range(4):
            total = 0
            for k in range(4):
                if (v >> k) & 1:
                    total ^= matrix[4 * k + j]
            for i in range(4):
                if (u >> i) & 1:
                    out[4 * i + j] ^= ring_times(total, delta)
    return tuple(out)


def ring_join(gates):
    identity = ring_identity()
    table = {identity: ()}
    for i, gate in enumerate(gates):
        table[ring_gate(identity, gate)] = (i,)
    for i, first in enumerate(gates):
        prefix = ring_gate(identity, first)
        for j, second in enumerate(gates):
            table.setdefault(ring_gate(prefix, second), (i, j))
    target = tuple(4 * x for x in identity)
    wanted = ring_gate(target, (1, 1), right=True, inverse=True)
    hits = 0
    for word in table.values():
        complement = wanted
        for index in word:
            complement = ring_gate(complement, gates[index], right=True,
                                   inverse=True)
        hits += int(complement in table)
    return len(table), hits


def check_projectors(gates):
    enumerated = set()
    for code in range(1 << 16):
        rows = tuple((code >> (4 * i)) & 15 for i in range(4))
        if binary_rank(rows) != 1:
            continue
        square = []
        for row in rows:
            total = 0
            for j in range(4):
                if (row >> j) & 1:
                    total ^= rows[j]
            square.append(total)
        if tuple(square) == rows:
            enumerated.add(rows)
    constructed = {tuple(v if (u >> i) & 1 else 0 for i in range(4))
                   for u, v in gates}
    need(enumerated == constructed and len(gates) == 120,
         "rank-one idempotent inventory mismatch")
    for u, v in gates:
        kernel = [x for x in range(1, 16) if not (v & x).bit_count() % 2]
        basis = [u]
        for x in kernel:
            if binary_rank(basis + [x]) > len(basis):
                basis.append(x)
        need(len(basis) == 4 and all(not (v & x).bit_count() % 2
                                    for x in basis[1:]),
             "binary normalization basis failed")
    return len(enumerated)


def check_triangular_identity():
    delta = 3
    count = 0
    positions = [(i, j) for i in range(4) for j in range(4) if i != j]
    for code in range(1 << len(positions)):
        vectors = [1 << i for i in range(4)]
        for bit, (i, j) in enumerate(positions):
            if (code >> bit) & 1:
                vectors[i] |= 1 << j
        matrix = IDENTITY
        for i in range(4):
            matrix = left_gate(matrix, (1 << i, vectors[i]))
        lower = list(IDENTITY)
        rhs = []
        for i in range(4):
            row = 1 << (2 * i)
            upper = 0
            for j in range(4):
                if (vectors[i] >> j) & 1:
                    if j < i:
                        lower[i] ^= delta << (2 * j)
                    else:
                        upper ^= delta << (2 * j)
            rhs.append(row ^ upper)
        need(multiply(tuple(lower), matrix) == tuple(rhs),
             "row-once triangular factorization failed")
        count += 1
    return count


def check_ring_and_witness():
    def image(a):
        return ((a & 1) ^ (2 if a & 2 else 0) ^ (3 if a & 4 else 0))
    def field_times(a, b):
        return (a if b & 1 else 0) ^ (omega(a) if b & 2 else 0)
    need(len({(a.bit_count() % 2, image(a)) for a in range(8)}) == 8,
         "augmentation/F4 representation is not faithful")
    for a in range(8):
        for b in range(8):
            need(image(ring_times(a, b)) == field_times(image(a), image(b)),
                 "field/group-ring product mismatch")
    word = tuple((1 << i, 1 << i) for i in range(4) for _ in range(2))
    actual = ring_identity()
    for gate in word:
        actual = ring_gate(actual, gate)
    target = tuple(4 * x for x in ring_identity())
    need(actual == target, "eight-call witness failed")
    for omitted in range(8):
        mutant = ring_identity()
        for i, gate in enumerate(word):
            if i != omitted:
                mutant = ring_gate(mutant, gate)
        need(mutant != target, "omitted call was not detected")
    # Full left-regular action on each of the twelve arbitrary dirty columns.
    for role in range(4):
        for address in range(3):
            output = [ring_times(actual[4 * i + role], 1 << address)
                      for i in range(4)]
            need(output == [((1 << ((address + 2) % 3)) if i == role else 0)
                            for i in range(4)], "dirty regular column failed")
    return 12


def controls(gates, table):
    need(field_join(IDENTITY, gates, table), "three-call identity control lost")
    one = left_gate(IDENTITY, (1, 1))
    need(field_join(one, gates, table), "one-call positive control lost")
    probe = IDENTITY
    for i in (0, 23, 71, 11, 94):
        probe = left_gate(probe, gates[i])
    need(field_join(probe, gates, table), "five-call positive control lost")
    try:
        left_gate(IDENTITY, (1, 2))
    except ValueError:
        pass
    else:
        raise ValueError("nilpotent was accepted as an idempotent")
    need(left_gate(one, (1, 1)) != IDENTITY,
         "order-three gate was treated as an involution")
    need(left_gate(left_gate(one, (1, 1)), (1, 1)) == IDENTITY,
         "three equal calls did not close")
    return 6


def main():
    gates = projectors()
    inventory = check_projectors(gates)
    table = field_table(gates)
    need(len(table) == 8361, "two-factor field inventory changed")
    need(not field_join(TARGET, gates, table), "five-call saving exists")
    ring_size, ring_hits = ring_join(gates)
    need((ring_size, ring_hits) == (8361, 0), "full-ring exclusion disagrees")
    result = {
        "claim_type": "scoped proof with exact finite corroboration",
        "minimum": 8,
        "roles": 4,
        "rank_one_idempotents": inventory,
        "two_factor_products": len(table),
        "normalized_join_candidates_per_engine": len(table),
        "five_call_hits_per_engine": ring_hits,
        "row_once_factorizations": check_triangular_identity(),
        "dirty_regular_columns": check_ring_and_witness(),
        "omitted_call_controls": 8,
        "semantic_controls": controls(gates, table),
    }
    root = Path(__file__).resolve().parent
    files = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
             "VERIFY.json", "verify.py")
    result["package_sha256"] = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in files
    }
    print(json.dumps(result, sort_keys=True))
    print("PASS_C3_FOUR_INVERSE_TARIFF minimum=8 five_call_hits=0")


if __name__ == "__main__":
    main()
