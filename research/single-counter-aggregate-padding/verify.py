"""Literal tape execution and independent mixed-radix oracle; Apache-2.0."""

import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def module():
    spec = importlib.util.spec_from_file_location("single_counter_machine", PACKAGE / "machine.py")
    require(spec is not None and spec.loader is not None, "missing machine")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class Meter:
    def __init__(self, cap):
        self.cap = cap
        self.count = 0

    def tick(self, _action):
        self.count += 1
        require(self.count <= self.cap, "action budget exhausted")


class Tape:
    """Finite tape with protected cells outside its two markers."""

    def __init__(self, contents, meter, origin=0, writable=True):
        self.cells = ["!"] + list(contents) + ["!"]
        self.origin = origin
        self.head = origin + 2
        self.initial_head = self.head
        self.meter = meter
        self.writable = writable
        self.capacity = len(self.cells)

    def index(self):
        index = self.head - self.origin
        require(1 <= index < self.capacity - 1, "crossed protected boundary")
        return index

    def read(self):
        self.meter.tick("read")
        return self.cells[self.index()]

    def write(self, value):
        self.meter.tick("write")
        require(self.writable, "write to immutable tape")
        require(value in ("0", "1", "$"), "invalid write")
        self.cells[self.index()] = value

    def move(self, step):
        self.meter.tick("move")
        require(type(step) is int and step in (-1, 1), "nonunit move")
        self.head += step
        self.index()


def descriptor(q):
    return "" if q == 1 else bin(q - 1)[2:][::-1]


def oracle(shape, payload, restrict):
    widths = [(q - 1).bit_length() for q in shape]
    padded = [1 << width for width in widths]
    coordinates = itertools.product(*(range(r) for r in padded))
    live = [all(x < q for x, q in zip(row, shape)) for row in coordinates]
    if restrict:
        return "".join(bit for bit, take in zip(payload, live) if take)
    iterator = iter(payload)
    return "".join(next(iterator) if take else "0" for take in live)


def fixture(machine, shape, payload, restrict=False, origin=0, prepare=None):
    widths = [(q - 1).bit_length() for q in shape]
    volume = math.prod(1 << width for width in widths)
    output_size = math.prod(shape) if restrict else volume
    bound = 192 * volume + 16 * sum(widths) + 80
    meter = Meter(bound)
    descriptors = [Tape("^" + descriptor(q) + "$", meter, origin + i * 7, False)
                   for i, q in enumerate(shape)]
    counters = [Tape("^" + "0" * width + "$", meter, origin - i * 11)
                for i, width in enumerate(widths)]
    source = Tape("^" + payload + "$", meter, origin + 100, False)
    target = Tape("^" + "_" * (output_size + 1), meter, origin - 100)
    immutable = [(tape, tuple(tape.cells)) for tape in descriptors + [source]]
    coordinates = [machine.Coordinate(d, c) for d, c in zip(descriptors, counters)]
    if prepare is not None:
        prepare(coordinates)
    machine.scan(coordinates, source, target, meter.tick, restrict)
    require("".join(target.cells[2:2 + output_size]) == oracle(shape, payload, restrict),
            "wrong payload")
    require(target.cells[2 + output_size] == "$", "missing output delimiter")
    for tape, before in immutable:
        require(tuple(tape.cells) == before, "immutable source changed")
    for tape in counters:
        require(set(tape.cells[2:-2]) <= {"0"}, "counter not zero")
    for tape in descriptors + counters + [source, target]:
        require(tape.head == tape.initial_head, "head not restored")
        require(tape.cells[0] == tape.cells[-1] == "!", "outside cell changed")
    require(len(descriptors + counters + [source, target]) == 12, "wrong tape count")
    require(sum(len(t.cells) - 4 for t in counters) == sum(widths), "wrong work extent")
    return meter.count, bound


def payload(size, seed):
    return "".join(str(((i * 13 + seed) ^ (i >> 1)) & 1) for i in range(size))


def scan_cases(machine):
    records = []
    shapes = list(itertools.product((1, 2, 3), repeat=5))
    shapes += [(q, 1, 1, 1, 1) for q in (4, 5, 7, 8, 9, 15, 16, 17, 31, 32, 33, 65, 129)]
    shapes += [(3, 5, 2, 7, 1), (2, 3, 4, 5, 2)]
    for index, shape in enumerate(shapes):
        n = math.prod(1 << (q - 1).bit_length() for q in shape)
        for restrict in (False, True):
            size = n if restrict else math.prod(shape)
            steps, bound = fixture(machine, shape, payload(size, index), restrict, index - 130)
            records.append((shape, restrict, steps, bound))
    return records


def all_payloads(machine):
    count = 0
    for shape in ((1, 1, 1, 1, 1), (3, 1, 1, 1, 1), (3, 3, 1, 1, 1)):
        size = math.prod(shape)
        for bits in itertools.product("01", repeat=size):
            word = "".join(bits)
            fixture(machine, shape, word)
            fixture(machine, shape, oracle(shape, word, False), True)
            count += 2
    for bits in itertools.product("01", repeat=8):
        fixture(machine, (3, 2, 1, 1, 1), "".join(bits), True)
        count += 1
    return count


def coordinate_cases(machine):
    count = 0
    for q in range(1, 258):
        width = (q - 1).bit_length()
        r = 1 << width
        meter = Meter(96 * r + 32 * width + 128)
        d = Tape("^" + descriptor(q) + "$", meter, -17, False)
        c = Tape("^" + "0" * width + "$", meter, 39)
        coordinate = machine.Coordinate(d, c)
        for index in range(r):
            require(coordinate.genuine == (index < q), "wrong coordinate phase")
            require(coordinate.advance() == (index == r - 1), "wrong coordinate carry")
        require(coordinate.genuine, "phase did not reset")
        coordinate.finish()
        require(set(c.cells[2:-2]) <= {"0"}, "coordinate cleanup")
        require(c.head == c.initial_head and d.head == d.initial_head, "coordinate head")
        count += 1
    return count


def rejection(action):
    try:
        action()
    except (ValueError, RuntimeError):
        return 1
    raise ValueError("control accepted")


def controls(machine):
    count = 0
    for word in ("", "00", "x"):
        count += rejection(lambda word=word: fixture(machine, (1,) * 5, word))
    count += rejection(lambda: fixture(machine, (1,) * 5, "0", prepare=lambda c: c.pop()))
    count += rejection(lambda: fixture(machine, (3, 1, 1, 1, 1), "101",
                                       prepare=lambda c: setattr(c[0], "genuine", False)))
    meter = Meter(100)
    count += rejection(lambda: machine.borrow(Tape("^x$", meter)))
    count += rejection(lambda: machine.load(Tape("^x$", meter), Tape("^0$", meter)))
    count += rejection(lambda: machine.load(Tape("^1$", meter), Tape("^00$", meter)))
    count += rejection(lambda: Tape("^0$", meter, writable=False).write("1"))
    count += rejection(lambda: Tape("^0$", meter).move(2))
    count += rejection(lambda: Meter(0).tick("exhaustion"))
    return count


def mutation_controls(machine):
    count = 0
    original_load = machine.load
    original_clear = machine.clear

    def wrong_complement(descriptor, counter, complement=False):
        return original_load(descriptor, counter, False)

    try:
        machine.load = wrong_complement
        count += rejection(lambda: fixture(machine, (3, 1, 1, 1, 1), "101"))
    finally:
        machine.load = original_load
    try:
        machine.clear = lambda counter: None
        count += rejection(lambda: fixture(machine, (3, 1, 1, 1, 1), "101"))
    finally:
        machine.clear = original_clear
    require(machine.load is original_load and machine.clear is original_clear,
            "mutation binding was not restored")
    return count


def main():
    machine = module()
    records = scan_cases(machine)
    result = {"status": "PASS_SINGLE_COUNTER_AGGREGATE_PADDING", "claim_type": "scoped construction",
              "scan_cases": len(records), "all_payload_scans": all_payloads(machine),
              "coordinate_cycles": coordinate_cases(machine),
              "controls": controls(machine) + mutation_controls(machine),
              "tapes": 12, "counter_cells": "D", "action_bound": "192N+16D+80",
              "scan_digest": hashlib.sha256(json.dumps(records).encode()).hexdigest()}
    result["sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
