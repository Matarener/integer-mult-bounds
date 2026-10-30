#!/usr/bin/env python3
"""Reverse cancellation-free row coefficient of the two-window R437 carrier.

The words are the PR #4067 composed word and its candidate phases. This file
does not import that package. The norm rule is the cancellation-free recurrence
norm[d] += norm[s] on each scalar ADD, with the copy buffer carrying the opened
register's norm.
"""
import gzip
import hashlib
import json
import math
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
OLD_SHA256 = "e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e"
PHASE_SHA256 = "47c092cf409ac09c4386e5e59ea539d7406f65f746ddcf62a595353507c16607"
REGISTERS = 659
COPY = 659

OLD_FORWARD = 49347
OLD_REVERSE = 1113998
NEW_FORWARD = 49347
NEW_REVERSE = 1123650
OLD_ADDS = 24208
NEW_ADDS = 24211
FORWARD_CHILDREN = 2915
PEAK_REGISTER = 158
PEAK_SOURCE = 223
PEAK_SOURCE_NORM = 8689
BIT_WIDTH = 21


class Reject(Exception):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_words():
    old_path = PACKAGE / "inputs" / "R437-COMPOSED-WORD.json.gz"
    phase_path = PACKAGE / "inputs" / "CANDIDATE-PHASES.json.gz"
    need(sha256(old_path) == OLD_SHA256, "composed-word bytes")
    need(sha256(phase_path) == PHASE_SHA256, "candidate-phase bytes")
    old = json.loads(gzip.decompress(old_path.read_bytes()))
    phases = json.loads(gzip.decompress(phase_path.read_bytes()))
    new = dict(old)
    for key in ("A", "B", "C", "D"):
        new[key] = phases[key]
    return old, new


def frame_dimensions(word):
    def normalize(vector):
        factor = math.gcd(*vector)
        if not factor:
            return tuple(vector)
        sign = 1 if next(entry for entry in vector if entry) > 0 else -1
        return tuple(sign * entry // factor for entry in vector)

    def reduce_row(vector, basis):
        reduced = tuple(vector)
        for pivot, row in basis:
            if reduced[pivot]:
                reduced = normalize(
                    [row[pivot] * left - reduced[pivot] * right
                     for left, right in zip(reduced, row)])
        return reduced

    dimensions = []
    lines = word["lines"]
    for frame in word["frames"]:
        basis = []
        for index in frame:
            row = reduce_row(lines[index], basis)
            if any(row):
                pivot = next(column for column, entry in enumerate(row) if entry)
                basis.append((pivot, normalize(row)))
                basis.sort()
        closed = [index for index, _row in enumerate(lines)
                  if not any(reduce_row(lines[index], basis))]
        need(closed == list(frame), "frame is not its rational closure")
        dimensions.append(len(basis))
    return dimensions


def operation_records(word, dimensions):
    frames = [set(frame) for frame in word["frames"]]
    current = list(word["start"])
    records = []

    def move(register, destination):
        origin = current[register]
        if origin == destination:
            return
        need(frames[origin] <= frames[destination], "frame descent")
        records.append(("move", register, origin, destination,
                        dimensions[destination] - dimensions[origin]))
        current[register] = destination

    for section in ("D", "A", "B", "C"):
        if section == "B":
            for index, register in enumerate(word["ret"]):
                records.append(("open", register, current[register],
                                dimensions[current[register]]))
                for target, members in enumerate(word["scatter"]):
                    if index in members:
                        records.append(("add", 111 + target, COPY, 0))
                records.append(("close", register))
        for frame, destination, sources in word[section]:
            for register in (destination, *sources):
                move(register, frame)
            for source in sources:
                records.append(("add", destination, source, frame))
    for register, frame in enumerate(word["final"]):
        move(register, frame)
    return records


def walk(records, reverse):
    sequence = list(reversed(records)) if reverse else records
    norm = [1] * REGISTERS + [0]
    high = 1
    peak = None
    adds = 0
    children = 0
    for record in sequence:
        kind = record[0]
        if kind == "move":
            children += 1
            continue
        if kind == "add":
            destination, source = record[1], record[2]
            norm[destination] += norm[source]
            adds += 1
            if norm[destination] > high:
                high = norm[destination]
                peak = (destination, source, norm[source], high)
            continue
        if kind == ("close" if reverse else "open"):
            register = record[1]
            norm[COPY] = norm[register]
            if not reverse:
                children += 1
            continue
        norm[COPY] = 0
        if reverse:
            children += 1
    return {"l1": high, "adds": adds, "children": children, "peak": peak}


def coefficient(word):
    records = operation_records(word, frame_dimensions(word))
    return {"forward": walk(records, False), "reverse": walk(records, True)}


def report(old, new):
    before = coefficient(old)
    after = coefficient(new)
    need(before["forward"]["l1"] == OLD_FORWARD, "old forward coefficient")
    need(before["reverse"]["l1"] == OLD_REVERSE, "old reverse coefficient")
    need(after["forward"]["l1"] == NEW_FORWARD, "new forward coefficient")
    need(after["reverse"]["l1"] == NEW_REVERSE, "new reverse coefficient")
    need(before["forward"]["adds"] == OLD_ADDS, "old add count")
    need(after["forward"]["adds"] == NEW_ADDS, "new add count")
    need(before["reverse"]["adds"] == OLD_ADDS and after["reverse"]["adds"] == NEW_ADDS,
         "reverse add count")
    need(before["forward"]["children"] == FORWARD_CHILDREN, "old child count")
    need(after["forward"]["children"] == FORWARD_CHILDREN, "new child count")
    for side in ("forward", "reverse"):
        need(before[side]["peak"][:3] == after[side]["peak"][:3], "peak address moved")
    need(after["reverse"]["peak"][:3] == (PEAK_REGISTER, PEAK_SOURCE, PEAK_SOURCE_NORM),
         "reverse peak address")
    delta = NEW_REVERSE - OLD_REVERSE
    need(delta == 9652, "reverse delta")
    need(after["reverse"]["peak"][3] - PEAK_SOURCE_NORM
         == before["reverse"]["peak"][3] - PEAK_SOURCE_NORM + delta,
         "delta already in the destination")
    need(OLD_REVERSE.bit_length() == BIT_WIDTH and NEW_REVERSE.bit_length() == BIT_WIDTH,
         "bit width")
    need(OLD_REVERSE < NEW_REVERSE, "old integer coefficient covers the new word")
    return {
        "old_reverse": OLD_REVERSE,
        "new_reverse": NEW_REVERSE,
        "delta": delta,
        "forward": NEW_FORWARD,
        "bit_width": BIT_WIDTH,
        "children": FORWARD_CHILDREN,
        "add_delta": NEW_ADDS - OLD_ADDS,
        "old_integer_coefficient_covers": False,
        "bit_width_cap_covers": True,
    }


def main():
    payload = report(*load_words())
    print("PASS_R437_REVERSE_ROW_COEFFICIENT " + json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (Reject, OSError, ValueError, KeyError) as exc:
        raise SystemExit("FAIL: " + str(exc)) from exc
