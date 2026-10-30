#!/usr/bin/env python3
"""Replay sector words on all inputs and dirty owned fields.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import importlib.util
import json
import random
import sys

HERE = Path(__file__).resolve().parent


def need(test, message):
    if not test:
        raise ValueError(message)


def load():
    for row in json.loads((HERE / 'INPUTS.json').read_text()):
        need(sha256((HERE / row['local']).read_bytes()).hexdigest() == row['sha256'],
             'Source bytes: ' + row['local'])
    spec = importlib.util.spec_from_file_location('query_packing', HERE / 'packing.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rank(matrix):
    data = [list(map(F, row)) for row in matrix]
    height, width = len(data), len(data[0]) if data else 0
    used = 0
    for j in range(width - 1, -1, -1):
        pivot = next((i for i in range(used, height) if data[i][j]), None)
        if pivot is None:
            continue
        data[used], data[pivot] = data[pivot], data[used]
        value = data[used][j]
        data[used] = [x / value for x in data[used]]
        for i in range(used + 1, height):
            value = data[i][j]
            data[i] = [x - value * y for x, y in zip(data[i], data[used])]
        used += 1
    return used


def add_row(dst, src, coefficient, mask):
    for (original, monomial, odd), value in src.items():
        key = original, monomial ^ mask, odd
        value = dst.get(key, F(0)) + coefficient * value
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def query(row):
    return {(original, mask ^ odd, 1 - odd): value
            for (original, mask, odd), value in row.items()}


def replay(word, even, odd):
    n, m = word['input_fields'], word['output_fields']
    count = 1 << word['generators']
    owned = word['output_registers'] + word['work_registers']
    rows = [{(i, 0, 0): F(1)} for i in range(n + len(owned))]
    calls = 0
    for event in word['program']:
        tag, dst = event[:2]
        need(dst in owned, 'Writes use only owned output/work fields')
        if tag == 'CLEAR':
            rows[dst] = {}
        elif tag == 'QUERY':
            rows[dst] = query(rows[dst])
            calls += 1
        else:
            need(tag == 'ADD', 'Opcode')
            _, _, src, coefficient, mask = event
            need(0 <= mask < count and src != dst, 'Ordinary source and sector mask')
            add_row(rows[dst], rows[src], F(coefficient), mask)
    need(calls == word['query_count'], 'Literal query count')
    for i, output in enumerate(word['output_registers']):
        expected = {}
        for parity, parts in enumerate((even, odd)):
            for mask, matrix in enumerate(parts):
                for j, value in enumerate(matrix[i]):
                    if F(value):
                        expected[j, mask, parity] = F(value)
        need(rows[output] == expected, 'All-input polynomial endpoint')
    need(all(not rows[i] for i in word['work_registers']), 'Dirty work returns zero')
    need(rows[:n] == [{(i, 0, 0): F(1)} for i in range(n)], 'Inputs unchanged')
    return calls


def zeros(count, m, n):
    return [[[F(0) for _ in range(n)] for _ in range(m)] for _ in range(count)]


def from_sectors(matrices):
    count, m, n = len(matrices), len(matrices[0]), len(matrices[0][0])
    return [[[sum((-1 if (mask & sector).bit_count() % 2 else 1)
                  * F(matrices[sector][i][j]) for sector in range(count)) / count
              for j in range(n)] for i in range(m)] for mask in range(count)]


def check_case(engine, even, odd):
    word = engine.compile_map(even, odd)
    replay(word, even, odd)
    count, m, n = len(odd), len(odd[0]), len(odd[0][0])
    ranks = [rank([[sum((-1 if (mask & sector).bit_count() % 2 else 1)
                        * F(odd[mask][i][j]) for mask in range(count))
                    for j in range(n)] for i in range(m)]) for sector in range(count)]
    need(word['sector_ranks'] == ranks and word['query_count'] == max(ranks),
         'Independent sector lower bound')
    return word


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def plus(a, b, sign=1):
    return [[x + sign * y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def gauge_cases(engine):
    rng = random.Random(9137)
    total = 0
    for n in range(1, 7):
        identity = engine.eye(n)
        for _ in range(12):
            changes = []
            for _ in range(3):
                u = engine.eye(n)
                for _ in range(3 * n):
                    if n == 1:
                        break
                    i, j = rng.sample(range(n), 2)
                    c = rng.choice([-2, -1, 1, 2])
                    u[i] = [x + c * y for x, y in zip(u[i], u[j])]
                changes.append(u)
            u, v, matrix = changes
            p0 = [[F(i == j and i < rng.randrange(n + 1)) if i == j else F(0)
                   for j in range(n)] for i in range(n)]
            r0 = [[F(i == j and i < rng.randrange(n + 1)) if i == j else F(0)
                   for j in range(n)] for i in range(n)]
            p = matmul(matmul(u, p0), engine.inverse(u))
            r = matmul(matmul(v, r0), engine.inverse(v))
            pc, rc = plus(identity, p, -1), plus(identity, r, -1)
            even = zeros(2, n, n)
            even[0] = plus(matmul(matmul(rc, matrix), pc), matmul(matmul(r, matrix), p))
            odd = [matmul(matmul(r, matrix), pc), matmul(matmul(rc, matrix), p)]
            word = check_case(engine, even, odd)
            defect = plus(matmul(r, matrix), matmul(matrix, p), -1)
            need(word['query_count'] == rank(defect), 'Sharp role-gauge tariff')
            total += 1
    return total


def feedback_cases(engine):
    rng = random.Random(2509)
    total, saved = 0, 0
    for _ in range(160):
        n, count = 3, 4
        rows = [{(i, 0, 0): F(1)} for i in range(n)]
        queries = 0
        for step in range(18):
            i = rng.randrange(n)
            if rng.randrange(3) == 0:
                rows[i] = query(rows[i]); queries += 1
            else:
                j = (i + rng.randrange(1, n)) % n
                add_row(rows[i], rows[j], F(rng.choice([-2, -1, 1, 2])), rng.randrange(count))
            for sector in range(count):
                matrix = [[sum(value * (-1 if (mask & sector).bit_count() % 2 else 1)
                               for (source, mask, parity), value in row.items()
                               if source == j and parity) for j in range(n)] for row in rows]
                need(rank(matrix) <= queries, 'Every query prefix obeys the lower-bound invariant')
        even, odd = zeros(count, n, n), zeros(count, n, n)
        for i, row in enumerate(rows):
            for (j, mask, parity), value in row.items():
                (odd if parity else even)[mask][i][j] = value
        word = check_case(engine, even, odd)
        need(word['query_count'] <= queries, 'Feedback compression')
        saved += queries - word['query_count']; total += 1
    return total, saved


def physical_example(word):
    """Use literal tensor Gaussian matrices, separate from the polynomial replay."""
    def add(a, b):
        return a[0] + b[0], a[1] + b[1]
    def scale(a, c):
        return c * a[0], c * a[1]
    def multiply(a, b):
        return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]
    checks = 0
    for width in range(1, 5):
        volume = 1 << width
        matrix = []
        for x in range(volume):
            row = []
            for y in range(volume):
                value = (1, 0)
                for bit in range(width):
                    value = multiply(value, (1, -1 if (x ^ y) >> bit & 1 else 1))
                row.append((F(value[0], volume), F(value[1], volume)))
            matrix.append(row)
        def apply(vector, conjugate=False):
            result = []
            for row in matrix:
                value = (F(0), F(0))
                for coefficient, entry in zip(row, vector):
                    if conjugate:
                        coefficient = coefficient[0], -coefficient[1]
                    value = add(value, multiply(coefficient, entry))
                result.append(value)
            return result
        for bank in range(2):
            for address in range(volume):
                rows = [[(F(0), F(0)) for _ in range(volume)] for _ in range(5)]
                rows[bank][address] = F(1), F(0)
                original = rows[bank][:]
                expected = [add(a, scale(add(b, scale(c, 1 if bank == 0 else -1)), F(1, 4)))
                            for a, b, c in zip(original, apply(original), apply(original, True))]
                for event in word['program']:
                    tag, dst = event[:2]
                    if tag == 'CLEAR':
                        rows[dst] = [(F(0), F(0))] * volume
                    elif tag == 'QUERY':
                        rows[dst] = apply(rows[dst])
                    else:
                        _, _, src, coefficient, mask = event
                        shift = volume - 1 if mask else 0
                        rows[dst] = [add(value, scale(rows[src][x ^ shift], F(coefficient)))
                                     for x, value in enumerate(rows[dst])]
                need(rows[word['output_registers'][bank]] == expected, 'Physical tensor Gaussian example')
                need(not any(a or b for a, b in rows[word['output_registers'][1 - bank]]), 'Other physical output')
                checks += 1
    return checks


def main():
    engine = load()
    small = [[[F(a), F(b)], [F(c), F(d)]]
             for a, b, c, d in product((-1, 0, 1), repeat=4)]
    total, strict = 0, 0
    for a in small:
        for b in small:
            odd = from_sectors([a, b]); even = zeros(2, 2, 2)
            even[0] = engine.eye(2)
            word = check_case(engine, even, odd)
            strict += word['query_count'] < sum(word['sector_ranks'])
            total += 1
    rng = random.Random(5025)
    rectangular = 0
    for m in range(1, 7):
        for n in range(1, 7):
            for count in (2, 4):
                even = [[[F(rng.randrange(-3, 4), 4) for _ in range(n)] for _ in range(m)] for _ in range(count)]
                odd = [[[F(rng.randrange(-3, 4), 2) for _ in range(n)] for _ in range(m)] for _ in range(count)]
                check_case(engine, even, odd); rectangular += 1
    examples = []
    for s in range(1, 6):
        count = 1 << s
        sectors = zeros(count, count, count)
        for sector in range(count):
            sectors[sector][sector][sector] = F(1, 2)
        odd = from_sectors(sectors); even = zeros(count, count, count)
        even[0] = engine.eye(count)
        word = check_case(engine, even, odd)
        need(word['query_count'] == 1, 'One query for every sector count')
        examples.append({k: word[k] for k in ('generators', 'query_count', 'ordinary_adds', 'ordinary_clears', 'owned_fields_including_outputs')})
        if s == 1:
            example = {'even': [[[str(x) for x in row] for row in matrix] for matrix in even],
                       'odd': [[[str(x) for x in row] for row in matrix] for matrix in odd]}
            expected_word = word
    controls = 0
    odd = zeros(2, 1, 1); odd[0][0][0] = F(1, 3)
    try:
        engine.compile_map(zeros(2, 1, 1), odd)
    except ValueError:
        controls += 1
    else:
        raise ValueError('Nondyadic input accepted')
    for mutant in ('query', 'mask', 'clear'):
        word = json.loads(json.dumps(expected_word))
        if mutant == 'query':
            word['program'] = [e for e in word['program'] if e[0] != 'QUERY']
        elif mutant == 'mask':
            event = next(e for e in word['program'] if e[0] == 'ADD' and e[4])
            event[4] = 0
        else:
            word['program'] = word['program'][1:]
        try:
            replay(word, example['even'], example['odd'])
        except ValueError:
            controls += 1
        else:
            raise ValueError('Corrupt word accepted: ' + mutant)
    physical = physical_example(expected_word)
    gauge = gauge_cases(engine)
    feedback, feedback_saved = feedback_cases(engine)
    result = {'complete_two_by_two_sector_pairs': total, 'strict_sharing_pairs': strict,
              'rectangular_cases': rectangular, 'role_gauge_cases': gauge,
              'feedback_words': feedback, 'feedback_queries_removed': feedback_saved,
              'rejection_controls': controls, 'physical_basis_cases': physical, 'examples': examples,
              'example_word_sha256': sha256(json.dumps(expected_word, sort_keys=True).encode()).hexdigest(),
              'lower_bound_scope': 'Faithful sectors; scalar combinations of the declared involutions; Q or inverse Q on one field',
              'no_new_kappa': True}
    if '--emit' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
        (HERE / 'EXAMPLE.json').write_text(json.dumps(example, indent=2) + '\n')
        (HERE / 'EXAMPLE-WORD.json').write_text(json.dumps(expected_word, indent=2) + '\n')
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_text()), 'Result receipt')
        need(example == json.loads((HERE / 'EXAMPLE.json').read_text()), 'Source example')
        need(expected_word == json.loads((HERE / 'EXAMPLE-WORD.json').read_text()), 'Emitted example')
    print(json.dumps(result, sort_keys=True))
    print('PASS_OPTIMAL_SECTOR_QUERY_COMPILER')


if __name__ == '__main__':
    main()
