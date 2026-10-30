"""Exact finite evidence. Produced by Nick Petalas. Apache-2.0."""

import hashlib
import itertools
import json
import math
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def cycle_rank(permutation):
    """Rank(P-I) over every field, computed from permutation cycles."""
    size = len(permutation)
    require(sorted(permutation) == list(range(size)), "not a permutation")
    seen = [False] * size
    cycles = 0
    for start in range(size):
        if seen[start]:
            continue
        cycles += 1
        node = start
        for _ in range(size):
            if seen[node]:
                break
            seen[node] = True
            node = permutation[node]
        require(node == start, "cycle did not close")
    return size - cycles


def fixture(period, copies, scratch, budget):
    require(2 <= period <= 100, "period outside finite checker domain")
    require(1 <= copies <= 4 and 0 <= scratch <= 3, "invalid fixture size")
    require(0 <= budget <= 2 * period * copies, "invalid rank budget")
    size = period * copies + scratch
    stage, frame = list(range(size)), list(range(size))
    per_copy = (period - math.gcd(period, 2)) // 2
    remaining = min(budget, copies * per_copy)
    for copy in range(copies):
        offset = copy * period
        for index in range(period):
            stage[offset + index] = offset + (index + 1) % period
        used = min(per_copy, remaining)
        for index in range(1, used + 1):
            left, right = offset + index, offset + period - index
            frame[left], frame[right] = frame[right], frame[left]
        remaining -= used
    require(remaining == 0, "unallocated rank")
    return stage, frame


def permutation_matrix(permutation, prime):
    size = len(permutation)
    return [[int(permutation[col] == row) % prime for col in range(size)]
            for row in range(size)]


def rank_mod(matrix, prime):
    """Forward elimination, independent of the cycle-count rank formula."""
    size = len(matrix)
    require(size <= 32 and all(len(row) == size for row in matrix), "matrix size")
    require(prime in (2, 3, 5, 7, 11), "unsupported finite-check field")
    rows = [[entry % prime for entry in row] for row in matrix]
    rank = 0
    for col in range(size):
        pivot = next((i for i in range(rank, size) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][col], -1, prime)
        rows[rank] = [(entry * inverse) % prime for entry in rows[rank]]
        for index in range(rank + 1, size):
            factor = rows[index][col]
            rows[index] = [(a - factor * b) % prime
                           for a, b in zip(rows[index], rows[rank])]
        rank += 1
    return rank


def defect(matrix, stage, prime):
    """Complete U J - J U^-1, including every workspace row and column."""
    size = len(stage)
    inverse = [0] * size
    for source, target in enumerate(stage):
        inverse[target] = source
    return [[(matrix[inverse[row]][col] - matrix[row][inverse[col]]) % prime
             for col in range(size)] for row in range(size)]


def frame_rank(matrix, prime):
    size = len(matrix)
    return rank_mod([[matrix[row][col] - int(row == col)
                      for col in range(size)] for row in range(size)], prime)


def check_constructions():
    cases = 0
    for period, copies, scratch in itertools.product(range(2, 33), range(1, 5), (0, 3)):
        demand = copies * (period - math.gcd(period, 2))
        for budget in range(demand // 2 + 3):
            stage, frame = fixture(period, copies, scratch, budget)
            joint = [frame[stage[index]] for index in range(len(stage))]
            square = [joint[joint[index]] for index in range(len(stage))]
            require(cycle_rank(frame) == min(budget, demand // 2), "frame rank")
            require(cycle_rank(square) == max(0, demand - 2 * budget), "defect rank")
            require(all(frame[frame[i]] == i for i in range(len(frame))), "not involutory")
            require(frame[period * copies:] == list(range(period * copies, len(frame))),
                    "workspace changed by construction")
            cases += 1
    return cases


def check_dense_fields():
    cases = 0
    for period, copies, scratch, prime in itertools.product(
            range(2, 13), (1, 2), (0, 2), (2, 3, 5, 7, 11)):
        demand = copies * (period - math.gcd(period, 2))
        for budget in range(demand // 2 + 3):
            stage, frame = fixture(period, copies, scratch, budget)
            matrix = permutation_matrix(frame, prime)
            require(rank_mod(matrix, prime) == len(stage), "singular frame")
            require(frame_rank(matrix, prime) == min(budget, demand // 2), "dense frame rank")
            require(rank_mod(defect(matrix, stage, prime), prime)
                    == max(0, demand - 2 * budget), "dense defect rank")
            cases += 1
    return cases


def bit_rank(rows, size):
    basis = [0] * size
    rank = 0
    for original in rows:
        row = original
        for pivot in range(size - 1, -1, -1):
            if not row & (1 << pivot):
                continue
            if basis[pivot]:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                rank += 1
                break
    return rank


def bit_defect(rows, stage):
    size = len(stage)
    inverse = [0] * size
    for source, target in enumerate(stage):
        inverse[target] = source
    result = []
    for index in range(size):
        right = sum(((rows[index] >> col) & 1) << stage[col] for col in range(size))
        result.append(rows[inverse[index]] ^ right)
    return result


def check_all_small_frames():
    records = []
    for period, scratch in ((2, 1), (3, 0), (3, 1), (4, 0)):
        stage, _ = fixture(period, 1, scratch, 0)
        size = len(stage)
        require(size <= 4, "exhaustive domain too large")
        best = [size + 1] * (size + 1)
        invertible = 0
        for encoded in range(1 << (size * size)):
            rows = [(encoded >> (row * size)) & ((1 << size) - 1) for row in range(size)]
            if bit_rank(rows, size) != size:
                continue
            invertible += 1
            changed = bit_rank([row ^ (1 << i) for i, row in enumerate(rows)], size)
            residual = bit_rank(bit_defect(rows, stage), size)
            require(residual >= max(0, period - math.gcd(period, 2) - 2 * changed),
                    "universal inequality violated")
            best[changed] = min(best[changed], residual)
        for budget in range(size + 1):
            actual = min(best[:budget + 1])
            expected = max(0, period - math.gcd(period, 2) - 2 * budget)
            require(actual == expected, "exhaustive optimum differs")
        records.append({"period": period, "scratch": scratch, "field": 2,
                        "matrices": 1 << (size * size), "invertible": invertible,
                        "minima_by_budget": [min(best[:r + 1]) for r in range(size + 1)]})
    return records


def check_controls():
    stage, _ = fixture(6, 1, 0, 1)
    wrong = list(range(6))
    wrong[1], wrong[2] = wrong[2], wrong[1]
    matrix = permutation_matrix(wrong, 3)
    require(frame_rank(matrix, 3) == 1, "wrong-frame control lost its rank")
    require(rank_mod(defect(matrix, stage, 3), 3) == 4, "wrong-frame control")
    # Rank-one mixing from dirty scratch into a stage-fixed vector is permitted.
    stage, frame = fixture(5, 1, 1, 2)
    mixed = permutation_matrix(frame, 3)
    for row in range(5):
        mixed[row][5] = 1
    require(rank_mod(mixed, 3) == 6, "mixed frame is singular")
    require(rank_mod(defect(mixed, stage, 3), 3) == 0, "dirty mixing not restored")
    require(frame_rank(mixed, 3) == 3, "dirty frame rank")
    # An order-two action is not the regular order-four representation.
    nonfaithful = [1, 0, 3, 2]
    identity = permutation_matrix(list(range(4)), 2)
    require(rank_mod(defect(identity, nonfaithful, 2), 2) == 0, "nonfaithful boundary")
    stage, _ = fixture(3, 1, 1, 0)
    for encoded in range(256):
        matrix_encoded = (encoded * 257 + 12345) % 65536
        rows = [(matrix_encoded >> (4 * row)) & 15 for row in range(4)]
        dense = [[(row >> col) & 1 for col in range(4)] for row in rows]
        literal = defect(dense, stage, 2)
        packed = [sum(value << col for col, value in enumerate(row)) for row in literal]
        require(packed == bit_defect(rows, stage), "bit defect disagreement")
        require(rank_mod(literal, 2) == bit_rank(packed, 4), "rank engines disagree")
    return {"wrong_low_rank_frame": 1, "dirty_workspace_mixing": 1,
            "nonfaithful_stage": 1, "dense_bit_crosschecks": 256}


def check_two_sided():
    cases = 0
    for period in range(2, 8):
        stage, _ = fixture(period, 1, 0, 0)
        inverse_stage = [(index - 1) % period for index in range(period)]
        for left in itertools.permutations(range(period)):
            inverse_left = [0] * period
            for source, target in enumerate(left):
                inverse_left[target] = source
            right = [inverse_stage[inverse_left[inverse_stage[i]]] for i in range(period)]
            endpoint = [left[stage[right[i]]] for i in range(period)]
            require(endpoint == inverse_stage, "two-sided endpoint")
            require(cycle_rank(left) + cycle_rank(right) >= period - math.gcd(period, 2),
                    "two-sided rank floor")
            cases += 1
    return cases


def main():
    construction_cases = check_constructions()
    dense_cases = check_dense_fields()
    exhaustive = check_all_small_frames()
    controls = check_controls()
    two_sided_cases = check_two_sided()
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"):
        hashes[name] = hashlib.sha256((package / name).read_bytes()).hexdigest()
    print(json.dumps({"status": "PASS_CYCLIC_REVERSAL_RANK_TRADEOFF",
                      "claim_type": "scoped proof with finite exact corroboration",
                      "construction_cases": construction_cases, "dense_field_cases": dense_cases,
                      "two_sided_cases": two_sided_cases,
                      "exhaustive_frames": exhaustive, "controls": controls,
                      "source_sha256": hashes}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
