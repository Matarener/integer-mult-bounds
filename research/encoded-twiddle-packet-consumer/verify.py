#!/usr/bin/env python3
"""Source-bound signed-packet tests; integer arithmetic is oracle-only.

Copyright 2026 Sagar Thakrar. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. The retained producer is
Nick Petalas's PR3593; its bytes and notices remain unchanged.
"""
from collections import Counter
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRODUCER = "inputs/pr3593/controller.py"


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    entries = [(ROOT, row) for row in manifest["files"] if row["usage"] == "input"]
    entries += [(HERE, row) for row in manifest["frozen_sources"]]
    receipt = {}
    for base, row in entries:
        require(digest((base / row["path"]).read_bytes()) == row["sha256"],
                "input changed: " + row["path"])
        receipt[row["path"]] = row["sha256"]
    return receipt


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, HERE / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def encode(values, width):
    return [bit for pair in values for number in pair
            for bit in ((number >> j) & 1 for j in range(width - 1, -1, -1))]


def polynomial(values, exponent):
    """Direct coefficient destination/sign rule, independent of segment copying."""
    extent = len(values)
    output = [None] * extent
    for position, pair in enumerate(values):
        power = position + exponent
        sign = -1 if (power // extent) % 2 else 1
        output[power % extent] = tuple(sign * component for component in pair)
    return output


def framed(tape):
    cells = tape.cells
    require(cells[0] == "^" and "$" in cells, "framed output")
    stop = cells.index("$")
    require(all(bit in (0, 1) for bit in cells[1:stop]), "binary output body")
    return list(cells[1:stop])


def counts(tapes):
    total = Counter()
    for tape in tapes:
        total.update(tape.counts)
    return total


def counters_delta(after, before):
    require(all(after[key] >= before[key] for key in before), "monotone operation counters")
    return {key: after[key] - before[key] for key in sorted(set(after) | set(before))}


def run_case(module, ell, width, values, exponent, header=None, descriptor=None):
    if header is None:
        header = module.Tape([(exponent >> j) & 1 for j in range(ell, -1, -1)])
    if descriptor is None:
        descriptor = module.Tape("^" + "1" * ell + "#1##L#-#$")
    width_descriptor = module.Tape("^" + "1" * width + "$")
    source = module.Tape(["^", *encode(values, width), "$"])
    borrowed = (header, descriptor, width_descriptor, source)
    snapshots = [list(tape.cells) for tape in borrowed]
    consumer = module.Consumer(ell, width)
    owned_names = tuple(consumer.tapes)
    all_tapes = (*borrowed, *consumer.tapes.values())
    before = counts(all_tapes)
    borrowed_before = counts(borrowed)
    output = consumer.run(header, descriptor, width_descriptor, source)
    require(consumer.tapes["header"] is header and consumer.tapes["descriptor"] is descriptor,
            "direct borrowed producer tape identity")
    require(framed(output) == encode(polynomial(values, exponent), width), "signed polynomial endpoint")
    require(all(list(tape.cells) == original and tape.head == 0
                for tape, original in zip(borrowed, snapshots)), "borrowed source/header/descriptor preservation")
    require(output.head == 0, "output head return")
    require(all(consumer.tapes[name].head == 0 and not any(consumer.tapes[name].cells)
                for name in owned_names if name != "output"), "private scratch erasure")
    operations = counters_delta(counts(all_tapes), before)
    invoiced = Counter()
    for key, value in consumer.invoice.items():
        if "." in key:
            invoiced[key.rsplit(".", 1)[1]] += value
    actual = Counter(counts(all_tapes))
    actual.subtract(borrowed_before)
    require(dict(invoiced) == dict(actual), "complete physical operation invoice")
    require(consumer.invoice["gate"] == sum(consumer.gates.values()), "complete gate invoice")
    return dict(output_sha256=digest(bytes(framed(output))), operations=operations,
                invoice=dict(consumer.invoice), gates=dict(consumer.gates),
                cells=sum(len(tape.cells) for tape in all_tapes)), output


def slots(ell, chunk, axes):
    """Source physical order: long top bits, interleaved remainder, axis chunks."""
    remainder = (ell - 1) % chunk
    result = [(axis, ell - 1) for axis, long in enumerate(axes) if long]
    result += [(axis, bit) for bit in range(remainder - 1, -1, -1)
               for axis in range(len(axes))]
    for high in range(ell - 2, remainder - 1, -chunk):
        for axis in range(len(axes)):
            result.extend((axis, bit) for bit in range(high, high - chunk, -1))
    return result


def producer_closed(machine, bits):
    require(machine.data["address"].cells == list(bits), "producer borrowed address")
    require(all(tape.head == 0 for tape in machine.data.values()), "producer data heads")
    require(all(not any(machine.data[role].cells) for role in ("bank", "total")), "producer private data erasure")
    require(all(counter.tape.head == 0 and not any(counter.tape.cells)
                for counter in machine.c.values()), "producer counter erasure and heads")
    require(machine.descriptor.head == 0, "producer descriptor head")


def producer_case(module, producer, opposite, canonical_address=False):
    ell, chunk, height, axes = 8, 4, 5, (True, False) * 6
    names = slots(ell, chunk, axes)
    bits = tuple(int(bit == height or (axis + 2 * bit) % 5 in (0, 2))
                 if canonical_address else int(axis == 0 and bit <= height)
                 for axis, bit in names)
    named = dict(zip(names, bits))
    total = sum(named[axis, height] * sum((1 << bit) * named[axis, bit]
                for bit in range(height)) for axis in range(len(axes)))
    exponent = ((1 if opposite else -1) * (1 << (ell - height)) * total) % (1 << (ell + 1))
    machine = producer.Controller(producer.encode(ell, chunk, height, axes, opposite), bits, trace=False)
    machine.execute()
    producer_closed(machine, bits)
    producer_invoice = machine.invoice()
    header = machine.data["output"]
    require(header.cells == [(exponent >> j) & 1 for j in range(ell, -1, -1)], "independent produced residue")
    if not canonical_address:
        require(exponent == (248 if opposite else 264), "specified nontrivial producer witness")
    values = [(i - 128, 127 - i) for i in range(256)]
    receipt, output = run_case(module, ell, 10, values, exponent, header, machine.descriptor)
    producer_closed(machine, bits)
    # A separately executed opposite consumer checks inversion on the actual
    # returned packet. Integer decoding below is a test oracle only.
    opposite_machine = producer.Controller(producer.encode(ell, chunk, height, axes, not opposite), bits, trace=False)
    opposite_machine.execute()
    producer_closed(opposite_machine, bits)
    width_descriptor = module.Tape("^" + "1" * 10 + "$")
    second = module.Consumer(ell, 10)
    returned = second.run(opposite_machine.data["output"], opposite_machine.descriptor,
                          width_descriptor, output)
    require(framed(returned) == encode(values, 10), "producer/opposite exact packet round trip")
    require(output.head == 0, "roundtrip borrowed packet head")
    producer_closed(opposite_machine, bits)
    require(all(second.tapes[name].head == 0 and not any(second.tapes[name].cells)
                for name in ("prefix", "suffix", "word", "a", "b")), "roundtrip scratch erasure")
    producer_actions = (sum(sum(row.values()) for row in producer_invoice["data"].values())
                        + producer_invoice["control_tape_actions"]
                        + producer_invoice["descriptor_actions"]
                        + sum(producer_invoice["gates"].values()))
    producer_cells = sum(producer_invoice[name] for name in
                         ("data_cells", "control_cells", "descriptor_cells"))
    joined_cells = producer_cells + receipt["cells"] - len(header.cells) - len(machine.descriptor.cells)
    return dict(opposite=opposite, canonical_address=canonical_address, exponent=exponent,
                address_sha256=digest(bytes(bits)), producer_invoice=producer_invoice,
                consumer=receipt, shared_header_cells=len(header.cells),
                shared_descriptor_cells=len(machine.descriptor.cells),
                joined_cells=joined_cells, joined_tapes=34,
                joined_operations=producer_actions + sum(receipt["invoice"].values()),
                roundtrip_sha256=digest(bytes(framed(returned))))


def rejects(operation, expected):
    try:
        operation()
    except ValueError as error:
        require(expected in str(error), "unexpected rejection: " + str(error))
        return str(error)
    raise ValueError("control survived: " + expected)


def controls(module):
    values = [(1, -2), (3, -1), (-2, 2), (0, 3)]
    source = (HERE / "consumer.py").read_text()
    cases = (
        ("wrong_wrap_sign", 'self.emit("suffix", not epsilon)',
         'self.emit("suffix", bool(epsilon))', 1, "signed polynomial endpoint"),
        ("wrong_unwrapped_sign", 'self.emit("prefix", bool(epsilon))',
         'self.emit("prefix", not epsilon)', 4, "signed polynomial endpoint"),
        ("uncharged_physical_move", 'self.invoice[role + ".move"] += 1',
         'self.invoice[role + ".move"] += 0', 3, "complete physical operation invoice"),
        ("reversed_segments", 'self.emit("suffix", not epsilon)\n            self.emit("prefix", bool(epsilon))',
         'self.emit("prefix", bool(epsilon))\n            self.emit("suffix", not epsilon)',
         1, "signed polynomial endpoint"),
    )
    result = []
    for name, old, new, exponent, reason in cases:
        require(source.count(old) == 1, "unique semantic mutation site")
        altered = source.replace(old, new)
        from types import ModuleType
        mutant = ModuleType("consumer_mutant")
        exec(compile(altered, str(HERE / "consumer.py"), "exec"), mutant.__dict__)
        failure = rejects(lambda: run_case(mutant, 2, 4, values, exponent), reason)
        result.append(dict(name=name, detected=failure, sha256=digest(altered.encode())))
    path = HERE / PRODUCER
    original = Path.read_bytes
    with patch.object(Path, "read_bytes", lambda p: b"counterfeit" if p == path else original(p)):
        result.append(dict(name="changed_producer_rejected", detected=rejects(authenticate, "input changed: " + PRODUCER)))
    # These finite invalid-header controls assert detection only. Malformed
    # external extents and arbitrary failure restoration are outside admission.
    for name, header, expected in (
        ("nonbinary_header_sign", [7, 0, 1], "header sign bit"),
        ("nonbinary_header_shift", [0, 0, 7], "header exponent bit"),
    ):
        consumer = module.Consumer(2, 4)
        operation = lambda: consumer.run(module.Tape(header), module.Tape("^11#1##L#-#$"),
                                        module.Tape("^1111$"), module.Tape(["^", *encode(values, 4), "$"]))
        result.append(dict(name=name, detected=rejects(operation, expected)))
    consumer = module.Consumer(2, 4)
    owned = tuple(consumer.tapes.values())
    snapshots = [list(tape.cells) for tape in owned]
    detected = rejects(lambda: consumer.run(module.Tape([0, 0, 1]), module.Tape("^11#1##L#-#$"),
                        module.Tape("^1111$"), consumer.tapes["prefix"]),
                       "borrowed tape aliases private role")
    require(all(list(tape.cells) == snapshot and tape.head == 0
                for tape, snapshot in zip(owned, snapshots)), "alias rejection precedes mutation")
    result.append(dict(name="owned_role_alias", detected=detected))
    return result


def minimum_control(module):
    consumer = module.Consumer(2, 3)
    owned = tuple(consumer.tapes.values())
    borrowed = (module.Tape([1, 0, 0]), module.Tape("^11#1##L#-#$"),
                module.Tape("^111$"), module.Tape(["^", *encode([(-4, 0)] * 4, 3), "$"]))
    snapshots = [list(tape.cells) for tape in borrowed]
    detected = rejects(lambda: consumer.run(*borrowed), "signed minimum cannot be negated")
    require(all(list(tape.cells) == snapshot and tape.head == 0
                for tape, snapshot in zip(borrowed, snapshots)), "minimum rejection preserves borrowed tapes")
    require(all(not any(tape.cells) and tape.head == 0 for tape in owned), "minimum rejection erases owned tapes")
    return detected


def counter_checks(module):
    """Execute the real marked countdown on independent test-only encodings."""
    receipt = hashlib.sha256()
    cases = [(value, 12) for value in range(65)]
    cases += [(value, width) for value in (127, 128, 129, 255, 256, 257, 511, 512, 1024)
              for width in (12, 40)]
    for value, width in cases:
        consumer = object.__new__(module.Consumer)
        consumer.invoice, consumer.gates = Counter(), Counter()
        tape = module.Tape(["^", *((value >> bit) & 1 for bit in range(width)), "$", "!"])
        tape.head = width + 1  # Test-only entry convention of mark_top.
        consumer.tapes = {"a": tape}
        zero = consumer.mark_top("a")
        iterations = 0
        while not zero:
            zero = consumer.decrement("a")
            iterations += 1
            require(iterations <= value, "countdown underflow or nontermination")
        require(iterations == value and tape.head == 0, "exact marked countdown")
        require(not any(tape.cells[1:width + 1]), "countdown endpoint zero")
        operations = sum(consumer.invoice.values())
        require(operations <= 100 * (value + width + 1), "amortized countdown envelope")
        receipt.update(canonical((value, width, operations)))
    tree = ast.parse((HERE / "consumer.py").read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Consumer")
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name != "__init__"]
    require(not any(isinstance(node, ast.Attribute) and node.attr in ("cells", "head", "capacities")
                    for method in methods for node in ast.walk(method)), "runtime bypasses physical tape API")
    constructor = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
    require(not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("read", "write", "move", "gate", "test")
                    for node in ast.walk(constructor)), "host allocation drives physical actions")
    return dict(cases=len(cases), sha256=receipt.hexdigest(),
                control="Actual countdown, including wide zero padding; static runtime Tape-API boundary guard")


def build():
    sources = authenticate()
    module = load("packet_consumer_under_test", "consumer.py")
    producer = load("retained_twiddle_producer", PRODUCER)
    evidence = hashlib.sha256()
    case_count = 0
    totals = Counter()
    for ell in (2, 3, 4):
        values = [(i - (1 << (ell - 1)), (1 << (ell - 1)) - 1 - i)
                  for i in range(1 << ell)]
        for exponent in range(1 << (ell + 1)):
            receipt, _ = run_case(module, ell, 6, values, exponent)
            evidence.update(canonical((ell, exponent, receipt)))
            totals.update(receipt["operations"])
            case_count += 1
    for value in range(-3, 4):
        receipt, _ = run_case(module, 2, 3, [(value, -value)] * 4, 4)
        evidence.update(canonical((value, receipt)))
        case_count += 1
    # The stronger consumer contract admits a minimum word if it is not negated.
    receipt, _ = run_case(module, 2, 3, [(-4, -4)] * 4, 0)
    evidence.update(canonical(receipt))
    minimum_rejection = minimum_control(module)
    rejected = controls(module)
    countdown = counter_checks(module)
    examples = [producer_case(module, producer, opposite, canonical_address)
                for canonical_address in (False, True) for opposite in (False, True)]
    return dict(status="PASS_ENCODED_TWIDDLE_PACKET_CONSUMER", source_sha256=sources,
                complete_residue_cases=56, signed_word_cases=8, total_success_cases=case_count + 1,
                small_sha256=evidence.hexdigest(), small_operations=dict(totals),
                controls=rejected, minimum_negation_rejected=minimum_rejection, producer_examples=examples,
                countdown=countdown,
                scope="Actual one-header signed packet consumption; four unchanged encoded producer joins and opposite round trips. No address enumeration, normalized root or full layer invoice.")


def main():
    result = json.loads(json.dumps(build()))
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(not sys.argv[1:], "usage: verify.py [--emit]")
        require(result == json.loads((HERE / "RESULT.json").read_text()), "retained result mismatch")
        print(result["status"])


if __name__ == "__main__":
    main()
