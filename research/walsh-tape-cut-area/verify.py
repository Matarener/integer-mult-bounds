#!/usr/bin/env python3
"""Exact finite evidence for the written one-head Walsh layout theorem."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


MAX_CELLS = 64


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dimensions(n: int, columns: int) -> int:
    require(type(n) is int and 2 <= n <= 32 and n & (n - 1) == 0,
            'n must be a power of two in [2,32]')
    require(type(columns) is int and 1 <= columns <= 8,
            'columns must be in [1,8]')
    require(n * columns <= MAX_CELLS, 'finite checker cell cap exceeded')
    return n * columns


def index(address: int, column: int, n: int, columns: int, layout: str) -> int:
    require(layout in ('address', 'column'), 'unknown layout')
    return address * columns + column if layout == 'address' else column * n + address


def endpoint(n: int, columns: int, layout: str) -> list[list[int]]:
    size = dimensions(n, columns)
    matrix = [[0] * size for _ in range(size)]
    for a in range(n):
        for b in range(n):
            sign = -1 if (a & b).bit_count() % 2 else 1
            for c in range(columns):
                matrix[index(a, c, n, columns, layout)][index(b, c, n, columns, layout)] = sign
    return matrix


def rank(matrix: list[list[int]]) -> int:
    require(len(matrix) <= MAX_CELLS, 'rank row cap exceeded')
    width = len(matrix[0]) if matrix else 0
    require(width <= MAX_CELLS and all(len(row) == width for row in matrix),
            'invalid rank matrix')
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot = 0
    for column in range(width):
        selected = next((i for i in range(pivot, len(work)) if work[i][column]), None)
        if selected is None:
            continue
        work[pivot], work[selected] = work[selected], work[pivot]
        divisor = work[pivot][column]
        work[pivot] = [value / divisor for value in work[pivot]]
        for row in range(pivot + 1, len(work)):
            coefficient = work[row][column]
            if coefficient:
                work[row] = [a - coefficient * b for a, b in zip(work[row], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def cut_ranks(matrix: list[list[int]], cut: int) -> tuple[int, int]:
    size = len(matrix)
    require(1 <= cut < size <= MAX_CELLS, 'cut outside finite matrix')
    left_from_right = rank([row[cut:] for row in matrix[:cut]])
    right_from_left = rank([row[:cut] for row in matrix[cut:]])
    return left_from_right, right_from_left


def predicted_rank(n: int, columns: int, cut: int, layout: str) -> int:
    size = dimensions(n, columns)
    require(1 <= cut < size, 'cut outside finite matrix')
    require(layout in ('address', 'column'), 'unknown layout')
    if layout == 'address':
        return min(cut, size - cut)
    residual = cut % n
    return min(residual, n - residual)


def ceil_sum(length: int, registers: int) -> int:
    quotient, remainder = divmod(length, registers)
    return registers * quotient * (quotient + 1) // 2 + (quotient + 1) * remainder


def single_block_bound(size: int, registers: int) -> int:
    require(type(size) is int and size >= 2 and size % 2 == 0, 'even size required')
    require(type(registers) is int and registers >= 1, 'positive registers required')
    half = size // 2
    return 4 * ceil_sum(half - 1, registers) + 2 * ((half + registers - 1) // registers)


def travel_bound(n: int, columns: int, registers: int, layout: str) -> int:
    size = dimensions(n, columns)
    require(layout in ('address', 'column'), 'unknown layout')
    if layout == 'address':
        return single_block_bound(size, registers)
    return columns * single_block_bound(n, registers) + 2 * (columns - 1)


def rank_census() -> dict[str, int]:
    fixtures = cuts = bounds = 0
    for n in (2, 4, 8, 16):
        for columns in (1, 2, 3, 4):
            for layout in ('address', 'column'):
                matrix = endpoint(n, columns, layout)
                ranks = []
                for cut in range(1, len(matrix)):
                    expected = predicted_rank(n, columns, cut, layout)
                    require(cut_ranks(matrix, cut) == (expected, expected), 'cut rank formula')
                    ranks.append(expected)
                    cuts += 1
                for registers in (1, 2, 3, 5, 8, 16, 64):
                    enumerated = 2 * sum(max(1, (r + registers - 1) // registers) for r in ranks)
                    require(enumerated == travel_bound(n, columns, registers, layout), 'ceiling sum')
                    bounds += 1
                if layout == 'address':
                    require(2 * sum(ranks) == (n * columns) ** 2 // 2, 'address rank area')
                else:
                    require(2 * sum(ranks) == columns * n * n // 2, 'column rank area')
                fixtures += 1
    return dict(matrix_fixtures=fixtures, spatial_cuts=cuts, register_bounds=bounds)


def butterfly_word(n: int, columns: int, layout: str) -> list[tuple[int, str]]:
    dimensions(n, columns)
    word = []
    for stage in range(n.bit_length() - 1):
        stride = 1 << stage
        for base in range(0, n, 2 * stride):
            for offset in range(stride):
                for column in range(columns):
                    a = index(base + offset, column, n, columns, layout)
                    b = index(base + offset + stride, column, n, columns, layout)
                    word.extend(((a, 'swap'), (b, 'butterfly'), (a, 'swap')))
    require(len(word) == 3 * columns * (n // 2) * (n.bit_length() - 1), 'gate count')
    return word


def execute(size: int, word: list[tuple[int, str]], inverse: bool = False) -> tuple[list[list[Fraction]], list[int], list[int]]:
    require(2 <= size <= MAX_CELLS and len(word) <= 4096, 'execution cap exceeded')
    rows = [[Fraction(i == j) for j in range(size + 1)] for i in range(size + 1)]
    right = [0] * (size - 1)
    left = [0] * (size - 1)
    position = 0
    instructions = list(reversed(word)) if inverse else word
    for location, gate in instructions:
        require(0 <= location < size and gate in ('swap', 'butterfly'), 'invalid local gate')
        step = 1 if location > position else -1
        for previous in range(position, location, step):
            boundary = previous if step == 1 else previous - 1
            (right if step == 1 else left)[boundary] += 1
        position = location
        cell, carried = rows[location], rows[size]
        if gate == 'swap':
            rows[location], rows[size] = carried, cell
        else:
            scale = Fraction(1, 2) if inverse else Fraction(1)
            rows[size] = [scale * (a + b) for a, b in zip(carried, cell)]
            rows[location] = [scale * (a - b) for a, b in zip(carried, cell)]
    for previous in range(position, 0, -1):
        left[previous - 1] += 1
    require(left == right, 'head return')
    return rows, left, right


def literal_census() -> dict[str, int]:
    programs = moves = gates = checks = 0
    for n in (2, 4, 8):
        for columns in (1, 2, 3):
            for layout in ('address', 'column'):
                word = butterfly_word(n, columns, layout)
                size = n * columns
                result, left, right = execute(size, word)
                expected = endpoint(n, columns, layout)
                require(result[:size] == [row + [0] for row in expected], 'literal endpoint')
                require(result[size] == [0] * size + [1], 'dirty register restoration')
                backward, _, _ = execute(size, word, inverse=True)
                for i in range(size + 1):
                    for j in range(size + 1):
                        require(sum(backward[i][k] * result[k][j] for k in range(size + 1)) == (i == j), 'literal inverse')
                for cut in range(1, size):
                    demand = max(1, predicted_rank(n, columns, cut, layout))
                    require(left[cut - 1] >= demand and right[cut - 1] >= demand, 'directional communication')
                    checks += 1
                require(sum(left) + sum(right) >= travel_bound(n, columns, 1, layout), 'total travel')
                positions = [0] + [location for location, _ in word] + [0]
                distance = sum(abs(a - b) for a, b in zip(positions, positions[1:]))
                require(distance == sum(left) + sum(right), 'literal unit-move accounting')
                programs += 1
                moves += distance
                gates += len(word)
    return dict(literal_programs=programs, local_gates=gates, unit_moves=moves,
                directional_cut_checks=checks)


def controls() -> int:
    requests = ((1, 1), (3, 1), (2, 0), (32, 8))
    for n, columns in requests:
        rejected = False
        try:
            dimensions(n, columns)
        except ValueError:
            rejected = True
        require(rejected, 'invalid dimension accepted')
    matrix = endpoint(4, 3, 'column')
    require(cut_ranks(matrix, 4) == (0, 0), 'whole-column boundary must have zero rank')
    require(predicted_rank(4, 3, 4, 'address') != 0, 'layout mutation invisible')
    require(travel_bound(4, 3, 1, 'column') == 28, 'inter-column travel cannot be free')
    word = butterfly_word(2, 1, 'address')
    altered, _, _ = execute(2, word[:-1])
    require(altered[2] != [0, 0, 1], 'omitted dirty restore undetected')
    altered, _, _ = execute(2, [(p, 'swap') for p, _ in word])
    require(altered[:2] != [row + [0] for row in endpoint(2, 1, 'address')], 'wrong local gate')
    require(single_block_bound(16, 2) < single_block_bound(16, 1), 'register budget ignored')
    require(cut_ranks(endpoint(2, 1, 'address'), 1) == (1, 1), 'remote zero-travel shortcut')
    return len(requests) + 7


def main() -> None:
    evidence = rank_census()
    evidence.update(literal_census())
    evidence['controls'] = controls()
    evidence['example_n8_m4_s1'] = dict(address=travel_bound(8, 4, 1, 'address'),
                                      column=travel_bound(8, 4, 1, 'column'))
    package = Path(__file__).resolve().parent
    files = sorted(path for path in package.iterdir() if path.is_file())
    require(len(files) <= 16, 'package file cap exceeded')
    evidence['sha256'] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    print('PASS_WALSH_TAPE_CUT_AREA')
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
