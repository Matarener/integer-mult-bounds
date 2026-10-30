"""Exact single-ADD coefficient repairs for a scalar P104 endpoint.

The endpoint is a linear map on every public input, including dirty helpers.
Frames and the physical meaning of owned erasure are separate obligations.
"""

import argparse
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path

MAX_ROLES = 1024
MAX_EVENTS = 26000
MAX_BYTES = 16 * 1024 * 1024


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add_scaled(destination, source, coefficient):
    """Return a fresh sparse row, without retaining zero entries."""
    result = dict(destination)
    for index, value in source.items():
        updated = result.get(index, Q(0)) + coefficient * value
        need(max(abs(updated.numerator).bit_length(),
                 updated.denominator.bit_length()) <= 4096,
             "intermediate rational bit bound")
        if updated:
            result[index] = updated
        else:
            result.pop(index, None)
    return result


def parse_program(events, roles):
    need(type(roles) is int and 0 < roles <= MAX_ROLES, "role bound")
    need(isinstance(events, list) and len(events) <= MAX_EVENTS, "event bound")
    parsed = []
    lengths = {"ADD": 5, "COPY": 5, "SCALE": 4, "MOVE": 5,
               "INIT": 3, "CLEAR": 3}
    for event in events:
        need(isinstance(event, list) and event, "event shape")
        op = event[0]
        need(isinstance(op, str) and op in lengths, "unknown opcode")
        need(len(event) == lengths[op], "event length")
        destination = event[1]
        need(type(destination) is int and 0 <= destination < roles, "destination")
        source, coefficient = destination, Q(0)
        if op in ("ADD", "COPY"):
            source = event[2]
            need(type(source) is int and 0 <= source < roles, "source")
            need(source != destination, "aliased scalar ports")
        if op in ("ADD", "COPY", "SCALE"):
            value = event[-2]
            need(type(value) in (str, int), "coefficient type")
            need(len(str(value)) <= 160, "coefficient text bound")
            coefficient = Q(value)
            need(max(abs(coefficient.numerator).bit_length(),
                     coefficient.denominator.bit_length()) <= 256,
                 "coefficient bit bound")
        parsed.append((op, destination, source, coefficient))
    return tuple(parsed)


def initial_rows(inputs, roles):
    need(type(inputs) is int and 0 < inputs <= roles <= MAX_ROLES, "input bound")
    return [{i: Q(1)} if i < inputs else {} for i in range(roles)]


def forward_step(rows, event):
    op, destination, source, coefficient = event
    if op == "ADD":
        rows[destination] = add_scaled(rows[destination], rows[source], coefficient)
    elif op == "COPY":
        rows[destination] = add_scaled({}, rows[source], coefficient)
    elif op == "SCALE":
        rows[destination] = add_scaled({}, rows[destination], coefficient)
    elif op in ("INIT", "CLEAR"):
        rows[destination] = {}


def backward_step(columns, event):
    op, destination, source, coefficient = event
    if op in ("ADD", "COPY"):
        columns[source] = add_scaled(columns[source], columns[destination], coefficient)
        if op == "COPY":
            columns[destination] = {}
    elif op == "SCALE":
        columns[destination] = add_scaled({}, columns[destination], coefficient)
    elif op in ("INIT", "CLEAR"):
        columns[destination] = {}


def endpoint(program, inputs, roles):
    rows = initial_rows(inputs, roles)
    for event in program:
        forward_step(rows, event)
    return rows


def residual_factor(actual, target, inputs):
    need(isinstance(target, list) and len(target) == len(actual), "target rows")
    for row in target:
        need(isinstance(row, dict) and len(row) <= inputs, "target row shape")
        need(all(type(i) is int and 0 <= i < inputs and isinstance(v, Q)
                 for i, v in row.items()), "target entries")
        need(all(max(abs(v.numerator).bit_length(), v.denominator.bit_length())
                 <= 4096 for v in row.values()), "target fraction bit bound")
    residual = [add_scaled({i: v for i, v in t.items() if v}, a, Q(-1))
                for a, t in zip(actual, target)]
    nonzero = [i for i, row in enumerate(residual) if row]
    if not nonzero:
        return "already_matches", None
    row_index = nonzero[0]
    row = residual[row_index]
    column_index = min(row)
    entry = row[column_index]
    column = {i: residual[i][column_index] for i in nonzero
              if column_index in residual[i]}
    for i, candidate in enumerate(residual):
        if candidate != add_scaled({}, row, column.get(i, Q(0)) / entry):
            return "rank_exceeds_one", None
    return "rank_one", (row_index, column_index, row, column, entry)


def prefix_candidates(program, inputs, roles, factor):
    _, column_index, residual_row, _, entry = factor
    rows = initial_rows(inputs, roles)
    candidates = {}
    for index, event in enumerate(program):
        op, _, source, _ = event
        if op == "ADD":
            prefix = rows[source]
            value = prefix.get(column_index, Q(0))
            if value and prefix == add_scaled({}, residual_row, value / entry):
                candidates[index] = value
        forward_step(rows, event)
    return candidates


def localize(events, inputs, roles, target):
    """Return all nonzero coefficient changes restoring the complete target."""
    program = parse_program(events, roles)
    actual = endpoint(program, inputs, roles)
    status, factor = residual_factor(actual, target, inputs)
    if factor is None:
        return {"status": status, "repairs": []}
    row_index, _, _, residual_column, entry = factor
    candidates = prefix_candidates(program, inputs, roles, factor)
    columns = initial_rows(roles, roles)
    repairs = []
    for index in range(len(program) - 1, -1, -1):
        event = program[index]
        if index in candidates:
            suffix = columns[event[1]]
            value = suffix.get(row_index, Q(0))
            if value and suffix == add_scaled({}, residual_column, value / entry):
                delta = entry / (value * candidates[index])
                replacement = event[3] + delta
                denominator = replacement.denominator
                admissible = bool(replacement) and denominator & (denominator - 1) == 0
                admissible = admissible and abs(replacement) + 1 < 2**16
                repairs.append({"event": index, "old": str(event[3]),
                                "delta": str(delta), "replacement": str(replacement),
                                "p104_coefficient_rule": admissible})
        backward_step(columns, event)
    return {"status": "localized" if repairs else "no_single_add_repair",
            "repairs": list(reversed(repairs))}


def load_word(path):
    path = Path(path)
    need(path.stat().st_size <= MAX_BYTES, "input file bound")
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as stream:
        payload = stream.read(MAX_BYTES + 1)
    need(len(payload) <= MAX_BYTES, "decompressed input bound")
    word = json.loads(payload)
    need(isinstance(word, dict), "word object")
    return word


def p104_problem(word):
    """The toolkit's complete scalar endpoint; eight owned roles start at zero."""
    need(isinstance(word.get("initial"), list), "public roles")
    inputs = len(word["initial"])
    roles = inputs + 8
    need(roles <= MAX_ROLES, "P104 role bound")
    live = word.get("live")
    need(isinstance(live, list) and all(type(i) is int for i in live), "live ports")
    need(len(live) == len(set(live)), "duplicate live ports")
    target = initial_rows(inputs, roles)
    for source in live:
        need(type(source) is int and 0 <= source < inputs, "live source")
        destination = source + 112
        need(destination < inputs, "live target")
        target[destination] = add_scaled(target[destination], {source: Q(1)}, Q(1))
    return inputs, roles, target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("word", type=Path)
    args = parser.parse_args()
    word = load_word(args.word)
    inputs, roles, target = p104_problem(word)
    result = localize(word["program"], inputs, roles, target)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
