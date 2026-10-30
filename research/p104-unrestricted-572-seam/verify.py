#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact certificate for the unrestricted linear helper-572 seam obstruction."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
WORD = "research/p104-helper470-twin-rung-removal/WORD.json.gz"
CUT, LEFT_END, RIGHT_END = 13637, 13651, 13655
FIRST = (127, 572, 581, 582, 731, 778)
EXTRA = (740, 709)
LEFT = (127, 581, 582, 731, 778)
RIGHT = (572, 740, 709)
OUTPUTS = (116, 120, 127, 134, 138, 176)
VISIBLE = (0, 1, 2, 3, 5, 7)
T0 = ((1, 0, 0, 0, 0, 0, 0, 0),
      (0, 0, 1, 0, 0, 0, 0, 0),
      (0, 0, 0, 1, 2, 0, 0, 0),
      (0, 0, 0, 0, 1, 0, 0, 0),
      (0, 0, 0, 0, 0, 1, 0, 0),
      (0, 0, 0, 0, 0, 1, 0, 0),
      (0, 0, 0, 0, 0, -1, 1, 0),
      (0, 0, 0, 0, 0, 0, 0, 1))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(row, other, scale):
    result = row.copy()
    for column, value in other.items():
        value = result.get(column, Q(0)) + scale * value
        if value:
            result[column] = value
        else:
            result.pop(column, None)
    return result


def apply(rows, event):
    operation, target = event[:2]
    if operation in ("ADD", "COPY"):
        old = rows[target] if operation == "ADD" else {}
        rows[target] = add(old, rows[event[2]], Q(event[3]))
    elif operation == "SCALE":
        rows[target] = {i: Q(event[2]) * v for i, v in rows[target].items()
                        if Q(event[2]) * v}
    elif operation in ("INIT", "CLEAR"):
        rows[target] = {}
    else:
        need(operation == "MOVE", "known scalar opcode")


def prefix(word):
    n, size = word["public"], word["public"] + word["owned_fields"]
    rows = [{i: Q(1)} if i < n else {} for i in range(size)]
    charts = word["initial"] + [None] * word["owned_fields"]
    snapshots, inventories = {}, {}
    for index in range(RIGHT_END + 1):
        event = word["program"][index]
        operation, target = event[:2]
        if operation == "INIT":
            need(charts[target] is None, "INIT ownership")
            charts[target] = event[2]
        elif operation == "MOVE":
            need(charts[target] == event[2], "MOVE entry chart")
            charts[target] = event[3]
        elif operation == "CLEAR":
            need(charts[target] == event[2], "CLEAR entry chart")
            charts[target] = None
        else:
            need(charts[target] == event[-1], "scalar target chart")
            if operation in ("ADD", "COPY"):
                need(charts[event[2]] == event[-1], "scalar source chart")
        apply(rows, event)
        if index in (CUT, RIGHT_END):
            snapshots[index] = [row.copy() for row in rows]
        if CUT <= index <= RIGHT_END:
            inventories[index] = tuple(tuple(r for r, c in enumerate(charts) if c == f)
                                       for f in (595, 603))
    return snapshots, inventories


def suffix(word):
    size = word["public"] + word["owned_fields"]
    roles = LEFT + RIGHT
    rows = [{roles.index(r): Q(1)} if r in roles else {} for r in range(size)]
    for index in range(RIGHT_END + 1, len(word["program"])):
        apply(rows, word["program"][index])
    return rows[:word["public"]]


def pivot_columns(rows):
    """At most eight rows; exact row elimination, with no input-column bound hidden."""
    basis = {}
    for original in rows:
        row = original.copy()
        for pivot in sorted(basis):
            if pivot in row:
                row = add(row, basis[pivot], -row[pivot])
        if row:
            pivot = min(row)
            scale = row[pivot]
            basis[pivot] = {i: value / scale for i, value in row.items()}
    return tuple(sorted(basis))


def determinant(matrix):
    """Independent Leibniz determinant; callers enforce size at most eight."""
    n = len(matrix)
    need(1 <= n <= 8 and all(len(row) == n for row in matrix), "small square minor")
    total = Q(0)
    for order in permutations(range(n)):
        value = Q(1)
        for i in range(n):
            value *= matrix[i][order[i]]
        inversions = sum(order[i] > order[j] for i in range(n) for j in range(i + 1, n))
        total += (-1 if inversions % 2 else 1) * value
    return total


def chronology(word, inventories):
    need(word["program"][CUT] == ["COPY", 778, 572, "1", 595], "cut COPY")
    need(word["program"][13652] == ["MOVE", 572, 595, 603, False], "single channel MOVE")
    need(word["program"][13654] == ["ADD", 740, 572, "-1", 603], "retained second-stage ADD")
    need(word["program"][RIGHT_END] == ["MOVE", 709, 597, 603, False], "external 709 entry")
    need(word["program"][13656] == ["CLEAR", 778, 595], "retained owned erasure")
    for index in range(CUT, LEFT_END + 1):
        need(inventories[index][0] == FIRST, "fixed first bank")
    for index in (13652, 13654):
        need(inventories[index][1] == (572, 740), "second bank before 709")
    need(inventories[RIGHT_END][1] == (572, 709, 740), "second bank after 709")
    for event in word["program"][CUT + 1:RIGHT_END + 1]:
        if event[0] in ("ADD", "COPY", "SCALE") and event[-1] == 595:
            need(event[1] in FIRST, "all first-stage scalar targets stay inside bank")
        need(not (event[0] in ("ADD", "COPY", "SCALE") and event[1] == 709),
             "external 709 value fixed before entry")


def certify(word):
    snapshots, inventories = prefix(word)
    chronology(word, inventories)
    n = word["public"]
    sources = [snapshots[CUT][r].copy() if r != 572 else {n: Q(1)}
               for r in FIRST + EXTRA]
    pivots = pivot_columns(sources)
    need(len(pivots) == 8, "eight independent source forms")
    need(pivots == (0, 2, 34, 572, 581, 582, 740, 770), "source witness columns")
    source_minor = [[row.get(i, Q(0)) for i in pivots] for row in sources]
    source_det = determinant(source_minor)
    need(source_det == Q(1, 32), "independent source minor")
    for role, coefficients in zip(LEFT + RIGHT, T0):
        reconstructed = {}
        for row, coefficient in zip(sources, coefficients):
            reconstructed = add(reconstructed, row, Q(coefficient))
        need(reconstructed == snapshots[RIGHT_END][role], "complete unsplit boundary identity")
    responses = suffix(word)
    need(all(not row.get(4, 0) for row in responses), "778 is erased at every public output")
    need(all(row.get(6, 0) == (1 if i == 740 else 0)
             for i, row in enumerate(responses)), "740 reaches only its own public output")
    outside = [i for i, chart in enumerate(word["final"]) if chart != word["final"][572]]
    need(740 not in outside and all(i in outside for i in OUTPUTS), "protected output witnesses")
    minor = [[responses[i].get(j, Q(0)) for j in VISIBLE] for i in OUTPUTS]
    need(determinant(minor) == 8, "six protected rows force all six visible boundary forms")
    return {"source_pivots": pivots, "source_minor_det": str(source_det),
            "protected_outputs": OUTPUTS, "protected_minor_det": "8",
            "protected_output_count": len(outside), "new_input_column": n,
            "first_bank": FIRST, "post_bank": LEFT + RIGHT,
            "protected_minor": [[str(x) for x in row] for row in minor]}


def controls(word):
    trials = 0
    for prime in (2, 3, 5):
        for a0, a1, d0, d1 in product(range(prime), repeat=4):
            q00, q01 = d0 * a0 % prime, d0 * a1 % prime
            q10, q11 = d1 * a0 % prime, d1 * a1 % prime
            need(q00 * q11 % prime == q01 * q10 % prime, "single channel has rank at most one")
            need(not (q00 == 1 and q01 == 0 and q11 != 0), "recovered old value forbids new signal")
            trials += 1
    need(determinant([[1, 0], [0, 1]]) == 1, "two-channel scope escape accepted")
    need(determinant([[1, 1], [1, 1]]) == 0, "dependent source forms rejected")
    mutations = ((CUT, 3, "2"), (13652, 3, 597),
                 (13655, 1, 740), (13656, 1, 740))
    for index, position, value in mutations:
        changed = dict(word)
        changed["program"] = [event.copy() for event in word["program"]]
        changed["program"][index][position] = value
        try:
            certify(changed)
        except ValueError:
            pass
        else:
            raise ValueError("changed seam or erasure accepted")
    return {"rank_one_products": trials, "changed_schedule_rejections": len(mutations),
            "two_channel_positive": True, "dependent_forms_control": True,
            "original_input_control": True}


def decode(raw, expected):
    need(sha256(raw).hexdigest() == expected, "source SHA256")
    word = json.loads(gzip.decompress(raw))
    need(word["public"] == 770 and word["owned_fields"] == 29, "bounded source dimensions")
    need(len(word["program"]) == 22803, "bounded source event count")
    return word


def main():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pin = next(row for row in manifest["files"] if row["path"] == WORD)
    raw = (HERE.parents[1] / WORD).read_bytes()
    word = decode(raw, pin["sha256"])
    result = certify(word)
    result["controls"] = controls(word)
    try:
        decode(raw + b"changed", pin["sha256"])
    except ValueError:
        result["controls"]["changed_source_rejected"] = True
    else:
        raise ValueError("changed source accepted")
    result["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(HERE.iterdir()) if p.is_file()}
    result["source_sha256"] = pin["sha256"]
    result["status"] = "PASS_P104_UNRESTRICTED_572_SEAM"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
