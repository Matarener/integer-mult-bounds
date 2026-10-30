"""Verify the wrapper, its interface, and complete composition fixtures.

Produced by Nick Petalas. Apache-2.0. No predecessor verifier is invoked.
"""

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/runtime-quarter-carry"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    """Compile authenticated source bytes directly, without bytecode caches."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    need(name not in sys.modules, "fresh module name")
    sys.modules[name] = module
    try:
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    finally:
        sys.modules.pop(name, None)
    return module


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    need(len(inputs) == 6, "complete input closure")
    for row in inputs:
        need(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
             "source bytes: " + row["path"])
    return {row["path"]: row["sha256"] for row in inputs}


def native_program(machine, table):
    rows = []
    for row in table["instructions"]:
        if row[0] == "branch":
            row = (row[0], row[1], tuple(tuple(p) for p in row[2]), row[3])
        rows.append(tuple(row))
    return machine.Program(tuple(rows), table["tapes"], table["entry"])


def bank_for(dense, shape, payload, code):
    origins = [11 * tape - 61 for tape in range(19)]
    bank = [({o - 5: dense.ONE, o: dense.MARK, o + 7: dense.ZERO}, o)
            for o in origins]
    bank[0] = dense.marked([dense.ONE if b else dense.ZERO for b in payload], origins[0])
    for tape, extent in zip((4, 5, 7), shape):
        bank[tape] = dense.binary(extent, origins[tape])
    for tape in (2, 3, 8, 10, 11, 12, 13, 14, 15):
        bank[tape] = ({}, origins[tape])
    packet = [dense.ONE if (code + 16) >> bit & 1 else dense.ZERO for bit in range(5)]
    bank[16] = dense.marked(packet, origins[16])
    return bank


def native_run(machine, program, bank, cap):
    result = machine.Machine(program, [machine.Tape(cells, head) for cells, head in bank])
    result.run(cap)
    state = [(dict(tape.cells), tape.head) for tape in result.tapes]
    spans = [max(visited or {tape.head}) - min(visited or {tape.head}) + 1
             for tape, visited in zip(result.tapes, result.visits)]
    return state, result.steps, sum(spans)


def dense_run(dense, table, bank, cap):
    tapes, steps = dense.execute(table, bank, cap)
    return ([(t.snapshot(), t.head) for t in tapes], steps,
            sum(t.high - t.low + 1 for t in tapes))


def structural_check(original, wrapped):
    """Undo relocation independently and compare every retained row."""
    need(len(wrapped["instructions"]) == len(original["instructions"]) + 7,
         "exact seven-row prefix")
    need(wrapped["instructions"][5] == ["goto", original["entry"] + 7],
         "fallback enters original entry")
    for before, after in zip(original["instructions"], wrapped["instructions"][7:]):
        decoded = deepcopy(after)
        if decoded[0] == "branch":
            for pair in decoded[2]:
                pair[1] -= 7
            decoded[3] -= 7
        elif decoded[0] == "goto":
            decoded[1] -= 7
        need(decoded == before, "unaltered fallback instruction")


def unit_cases(machine, dense, tables, programs):
    count = dense_count = 0
    for inverse in (False, True):
        for code in range(-16, 13):
            for p, s in ((1, 1), (1, 4), (2, 2)):
                for bits in product((0, 1), repeat=p * s):
                    bank = bank_for(dense, (p, 1, s), bits, code)
                    result = native_run(machine, programs[inverse], bank, 5)
                    need(result == (bank, 4, 20), "unit branch preserves every cell and head")
                    if p == s == 1 and bits == (1,):
                        need(dense_run(dense, tables[inverse], bank, 5) == result,
                             "separate unit interpreter")
                        dense_count += 1
                    count += 1
    return count, dense_count


def prefix_cases(machine, dense, wrapper):
    stub = {"tapes": 19, "entry": 0, "instructions": [["halt"]]}
    table = wrapper.wrap(stub, vars(machine))
    program = native_program(machine, table)
    count = 0
    # Descriptor-only prefix tests allocate no Q-sized payload.
    moduli = [1, 3, 5] + [(1 << bits) + 1 for bits in (3, 8, 31, 128, 512)]
    for q in moduli:
        bank = [({-7: dense.ONE, 0: dense.MARK, 9: dense.ZERO}, 0) for _ in range(19)]
        bank[5] = dense.binary(q, -23)
        result = native_run(machine, program, bank, 6)
        need(result == (bank, 4 if q == 1 else 5, 20), "exact prefix toll and restoration")
        need(dense_run(dense, table, bank, 6) == result, "separate prefix interpreter")
        count += 1
    return count


def composition_cases(machine, dense, tables, programs):
    rows = []
    for shape, code in (((1, 3, 1), 12), ((2, 5, 3), -16), ((1, 125, 1), -3)):
        p, q, s = shape
        payload = [int(index == 7 % (p * q * s)) for index in range(p * q * s)]
        offset = code * pow(4, -1, q) % q
        for inverse in (False, True):
            bank = bank_for(dense, shape, payload, code)
            sign = -1 if inverse else 1
            expected = [payload[(a * q + (x - sign * offset) % q) * s + z]
                        for a, x, z in product(range(p), range(q), range(s))]
            target = deepcopy(bank)
            target[0] = dense.marked([dense.ONE if bit else dense.ZERO for bit in expected],
                                     bank[0][1] - 1)
            result = native_run(machine, programs[inverse], bank, 200_000)
            need(result[0] == target, "composed original-owner rotation and restoration")
            need(dense_run(dense, tables[inverse], bank, 200_000) == result,
                 "separate complete composition interpreter")
            need(3 * result[1] <= 1115 * len(payload), "new transition envelope")
            need(result[2] <= 24 * len(payload), "new visited-cell envelope")
            rows.append(dict(shape=list(shape), code=code, inverse=inverse,
                             steps=result[1], visited=result[2]))
    return rows


def reject(action):
    try:
        action()
    except (ValueError, RuntimeError):
        return
    raise ValueError("negative control was accepted")


def controls(machine, dense, tables, programs, wrapper, originals):
    bank = bank_for(dense, (1, 1, 1), [1], -3)
    for index in (2, 4):
        bad = deepcopy(tables[False])
        bad["instructions"][index] = ["goto", index + 1]
        q = 1 if index == 2 else 5
        fixture = bank if q == 1 else bank_for(dense, (1, q, 1), [1] + [0] * (q - 1), -3)
        reject(lambda: need(native_run(machine, native_program(machine, bad), fixture, 100_000)[0][5][1]
                            == fixture[5][1], "omitted descriptor return"))
    wrong = deepcopy(tables[False])
    wrong["instructions"][7] = ["halt"]
    reject(lambda: structural_check(originals[False], wrong))
    reject(lambda: need(native_run(machine, programs[False], bank, 5)[1] <= 3,
                        "understated four-transition bill"))
    reject(lambda: wrapper.wrap({"tapes": 18, "entry": 0, "instructions": [["halt"]]},
                                 vars(machine)))
    reject(lambda: wrapper.wrap({"tapes": 19, "entry": 1, "instructions": [["halt"]]},
                                 vars(machine)))
    return 6


def run():
    input_hashes = authenticate()
    machine = load("carry_bypass_retained_machine", SOURCE / "inputs/machine.py")
    dense = load("carry_bypass_retained_dense", SOURCE / "inputs/independent.py")
    wrapper = load("carry_bypass_wrapper", PACKAGE / "wrapper.py")
    raw = (SOURCE / "TABLE.json.gz").read_bytes()
    need(len(raw) < 1_000_000, "bounded compressed source table")
    unpacked = gzip.decompress(raw)
    need(len(unpacked) < 10_000_000, "bounded authenticated table payload")
    source = json.loads(unpacked)
    tables, programs, originals = {}, {}, {}
    for inverse in (False, True):
        original = source["quarter:" + str(inverse)]
        originals[inverse] = original
        tables[inverse] = wrapper.wrap(original, vars(machine))
        structural_check(original, tables[inverse])
        dense.validate(tables[inverse])
        programs[inverse] = native_program(machine, tables[inverse])
    units = unit_cases(machine, dense, tables, programs)
    prefixes = prefix_cases(machine, dense, wrapper)
    compositions = composition_cases(machine, dense, tables, programs)
    negative = controls(machine, dense, tables, programs, wrapper, originals)
    need(Fraction(1111, 3) + Fraction(4, 3) == Fraction(1115, 3) < 468,
         "strict transition-bound improvement")
    files = sorted(path for path in PACKAGE.iterdir() if path.is_file())
    return dict(status="PASS_UNIT_MODULUS_CARRY_BYPASS", unit_cases=units[0],
                separate_unit_cases=units[1], prefix_cases=prefixes,
                composition_cases=compositions, negative_controls=negative,
                transitions_per_volume="1115/3", visited_per_volume=24,
                input_sha256=input_hashes,
                package_sha256={path.name: sha256(path.read_bytes()).hexdigest() for path in files})


if __name__ == "__main__":
    need(sys.argv[1:] == [], "no output or mutation options")
    print(json.dumps(run(), indent=2, sort_keys=True))
