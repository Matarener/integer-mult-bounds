"""Deterministic dyadic row synthesis of one frozen P104 scalar prefix.

Prepared for @CubeJerry with substantial OpenAI Codex assistance.
Sparse elimination and row sharing are classical; the source application is new.
Apache-2.0. No claim of circuit optimality.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q

START, STOP, FRAME = 1, 9896, 3
MAX_PAIR_STEPS = 2000


def need(condition, message):
    if not condition:
        raise ValueError(message)


def is_unit(value):
    numerator = abs(value.numerator)
    return bool(numerator) and numerator & (numerator - 1) == 0


def add_row(destination, source, coefficient):
    for column, value in source.items():
        result = destination.get(column, 0) + coefficient * value
        if result:
            destination[column] = result
        else:
            destination.pop(column, None)


def prefix_matrix(program):
    roles = sorted({e[1] for e in program}
                   | {e[2] for e in program if e[0] == "ADD"})
    rows = {role: {role: Q(1)} for role in roles}
    for event in program:
        need(event[0] in ("ADD", "SCALE") and event[-1] == FRAME,
             "Only the fixed scalar chart may be synthesized")
        destination, coefficient = event[1], Q(event[-2])
        if event[0] == "ADD":
            need(destination != event[2], "Distinct ADD operands")
            add_row(rows[destination], rows[event[2]], coefficient)
        else:
            rows[destination] = {k: coefficient * v
                                 for k, v in rows[destination].items()}
    return rows


def best_reduction(rows, destination, source):
    left, right = rows[destination], rows[source]
    common = left.keys() & right.keys()
    if 2 * len(common) - len(right) < 2:
        return None
    ratios = Counter(left[k] / right[k] for k in sorted(common))
    choices = [(len(common) + count - len(right),
                -abs(q.numerator).bit_length() - q.denominator.bit_length(), q)
               for q, count in ratios.items()
               if q.denominator & (q.denominator - 1) == 0 and abs(q) < 2**12]
    if not choices:
        return None
    gain, _, ratio = max(choices)
    return (gain, destination, source, -ratio) if gain >= 2 else None


def synthesize(program):
    """Return a literal replacement and discovery counts, without writing files."""
    rows = prefix_matrix(program)
    operations = []

    def add(destination, source, coefficient):
        add_row(rows[destination], rows[source], coefficient)
        operations.append(["ADD", destination, source, str(coefficient), FRAME])

    def scale(destination, coefficient):
        rows[destination] = {k: v * coefficient
                             for k, v in rows[destination].items()}
        operations.append(["SCALE", destination, str(coefficient), FRAME])

    # Whole-row sharing can cross the original dependency graph: both endpoints
    # of the entire prefix, rather than its internal observations, are retained.
    candidates = {}
    evaluations = 0
    for destination in rows:
        for source in rows:
            if destination != source:
                evaluations += 1
                choice = best_reduction(rows, destination, source)
                if choice:
                    candidates[destination, source] = choice
    pair_steps = 0
    while candidates:
        need(pair_steps < MAX_PAIR_STEPS, "Row-sharing step limit")
        _, destination, source, coefficient = max(candidates.values())
        add(destination, source, coefficient)
        pair_steps += 1
        for key in [key for key in candidates if destination in key]:
            del candidates[key]
        for other in rows:
            if other == destination:
                continue
            for left, right in ((destination, other), (other, destination)):
                evaluations += 1
                choice = best_reduction(rows, left, right)
                if choice:
                    candidates[left, right] = choice
    sparse_entries = sum(map(len, rows.values()))

    # Markowitz-style sparse pivots, restricted to units in Z[1/2]. Every
    # pivot normalization and every final permutation is an emitted operation.
    remaining_rows, remaining_columns = set(rows), set(rows)
    while remaining_columns:
        column_rows = defaultdict(list)
        for row in sorted(remaining_rows):
            for column in rows[row]:
                if column in remaining_columns:
                    column_rows[column].append(row)
        choices = []
        for row in sorted(remaining_rows):
            for column, value in rows[row].items():
                if column in remaining_columns and is_unit(value):
                    count = len(column_rows[column])
                    choices.append(((len(rows[row]) - 1) * (count - 1),
                                    len(rows[row]), count,
                                    abs(value.numerator).bit_length()
                                    + value.denominator.bit_length(),
                                    row != column, row, column))
        need(bool(choices), "No dyadic-unit pivot; no circuit emitted")
        *_, pivot, column = min(choices)
        if rows[pivot][column] != 1:
            scale(pivot, 1 / rows[pivot][column])
        for destination in rows:
            if destination != pivot and column in rows[destination]:
                add(destination, pivot, -rows[destination][column])
        remaining_rows.remove(pivot)
        remaining_columns.remove(column)

    exchanges = 0
    for row in rows:
        if rows[row] == {row: Q(1)}:
            continue
        other = next(k for k, value in rows.items() if value == {row: Q(1)})
        add(row, other, Q(1))
        add(other, row, Q(-1))
        add(row, other, Q(1))
        scale(other, Q(-1))
        exchanges += 1
    need(all(value == {row: Q(1)} for row, value in rows.items()),
         "Elimination must end at the literal identity")

    # If E_k ... E_1 M = I, then M = E_1^-1 ... E_k^-1. Chronological
    # execution therefore uses the inverses in reverse list order.
    replacement = []
    for original in reversed(operations):
        event = original.copy()
        event[-2] = str(-Q(event[-2]) if event[0] == "ADD" else 1 / Q(event[-2]))
        replacement.append(event)
    return replacement, {"roles": len(rows), "pair_steps": pair_steps,
                         "pair_evaluations": evaluations,
                         "entries_after_pair_steps": sparse_entries,
                         "unit_pivots": len(rows), "charged_exchanges": exchanges}
