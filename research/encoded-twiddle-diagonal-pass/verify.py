#!/usr/bin/env python3
"""Independent complete-cube oracle and physical-boundary checks.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar, with substantial OpenAI Codex assistance.
Named-slot and polynomial oracles retain Nick Petalas's transform lineage.
Instrumentation below is checker-only; it supplies no production decision.
"""
from collections import Counter
from contextlib import ExitStack
import ast
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    entries = [(ROOT, x) for x in manifest["files"] if x["usage"] == "input"]
    entries += [(HERE, x) for x in manifest["frozen_sources"]]
    for base, row in entries:
        raw = (base / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source authentication: " + row["path"])
        result[row["path"]] = row["sha256"]
    return result


def load(name, path):
    module = ModuleType(name)
    module.__file__ = str(HERE / path)
    exec(compile((HERE / path).read_bytes(), module.__file__, "exec"), module.__dict__)
    return module


def slots(ell, K, axes):
    """Independent source formula, not a call into the producer scheduler."""
    b = (ell - 1) % K
    ordered = [(i, ell - 1) for i, long in enumerate(axes) if long]
    ordered += [(i, bit) for bit in range(b - 1, -1, -1) for i in range(len(axes))]
    for top in range(ell - 2, b - 1, -K):
        ordered += [(i, bit) for i in range(len(axes)) for bit in range(top, top - K, -1)]
    expected = {(i, bit) for i, long in enumerate(axes) for bit in range(ell if long else ell - 1)}
    require(len(ordered) == len(expected) and set(ordered) == expected, "literal source-slot bijection")
    return ordered


def exponent(address, names, ell, h, axes, opposite):
    bits = [(address >> (len(names) - 1 - j)) & 1 for j in range(len(names))]
    named = dict(zip(names, bits))
    total = sum(named[i, h] * sum((1 << bit) * named[i, bit] for bit in range(h))
                for i, long in enumerate(axes) if h < (ell if long else ell - 1))
    return ((1 if opposite else -1) * (1 << (ell - h)) * total) % (1 << (ell + 1)), bits


def packet(address, r, width):
    """Diverse bounded data; address and coefficient affect both components."""
    cap = (1 << (width - 1)) - 1
    modulus = 2 * cap + 1
    return [((3 * address + 5 * j + address * j) % modulus - cap,
             (7 * address - 3 * j + 2 * address * j + 1) % modulus - cap)
            for j in range(r)]


def encode(values, width):
    return [((value >> bit) & 1) for pair in values for value in pair for bit in range(width - 1, -1, -1)]


def rotate(values, E):
    """Coefficient destination/sign identity, independent of two-buffer split."""
    r = len(values)
    result = [None] * r
    for j, pair in enumerate(values):
        quotient, target = divmod(j + E, r)
        sign = -1 if quotient % 2 else 1
        result[target] = tuple(sign * x for x in pair)
    return result


def inventory(machine):
    result = {}
    candidates = [*machine.producer.data.values(), machine.producer.descriptor,
                  *(c.tape for c in machine.producer.c.values()),
                  *machine.consumer.tapes.values(), *machine.tapes.values()]
    for tape in candidates:
        result[id(tape)] = tape
    return result


def no_new_tape(*_args, **_kwargs):
    raise ValueError("runtime allocated a replacement tape")


def run_case(adapter, producer, consumer, shape, source_override=None):
    ell, K, h, axes, opposite, width = shape
    names = slots(ell, K, axes)
    A, r = len(names), 1 << ell
    N = 1 << A
    descriptor = "1" * ell + "#" + "1" * K + "#" + "1" * h + "#" + "".join(
        "L" if x else "S" for x in axes) + "#" + ("+" if opposite else "-") + "#"
    original_values = [packet(i, r, width) for i in range(N)]
    source = ["@"]
    expected = ["@"]
    residues = []
    for i, values in enumerate(original_values):
        E, _bits = exponent(i, names, ell, h, axes, opposite)
        residues.append(E)
        source.extend(["^", *encode(values, width), "$"])
        expected.extend(["^", *encode(rotate(values, E), width), "$"])
    source.append("!")
    expected.append("!")
    if source_override is not None:
        # For inverse replay, decode each actual returned record in the checker.
        source = list(source_override)
        require(source[0] == "@" and source[-1] == "!", "inverse stream framing")
        original_values = []
        expected = ["@"]
        offset = 1
        for i in range(N):
            require(source[offset] == "^", "inverse packet start")
            offset += 1
            values = []
            for _j in range(r):
                pair = []
                for _component in range(2):
                    word = source[offset:offset + width]
                    require(len(word) == width and all(x in (0, 1) for x in word), "inverse signed word")
                    value = sum(bit << (width - 1 - j) for j, bit in enumerate(word))
                    if word[0]:
                        value -= 1 << width
                    pair.append(value)
                    offset += width
                values.append(tuple(pair))
            require(source[offset] == "$", "inverse packet end")
            offset += 1
            original_values.append(values)
            expected.extend(["^", *encode(rotate(values, residues[i]), width), "$"])
        require(offset == len(source) - 1, "inverse complete cube")
        expected.append("!")

    observed = Counter()
    adapter_calls = Counter()
    consumer_calls = Counter()
    with ExitStack() as instrumentation:
        for cls in (producer.Tape, consumer.Tape):
            for method in ("read", "write", "move"):
                original = getattr(cls, method)

                def counted(self, *args, _original=original, _method=method):
                    value = _original(self, *args)
                    observed[id(self), _method] += 1
                    return value

                instrumentation.enter_context(patch.object(cls, method, counted))
        for cls, counter in ((adapter.DiagonalPass, adapter_calls), (consumer.Consumer, consumer_calls)):
            for method in ("read", "write", "move"):
                original = getattr(cls, method)

                def counted_role(self, role, *args, _original=original, _method=method, _counter=counter):
                    value = _original(self, role, *args)
                    _counter[role + "." + _method] += 1
                    return value

                instrumentation.enter_context(patch.object(cls, method, counted_role))
        machine = adapter.DiagonalPass(producer, consumer, descriptor, width, source)
        initial = inventory(machine)
        require(len(initial) == 38, "fixed 38-role inventory")
        require(len({id(t.cells) for t in initial.values()}) == 38, "distinct tape backing")
        identities = set(initial)
        capacities = {key: len(tape.cells) for key, tape in initial.items()}
        borrowed = (machine.tapes["fullinput"], machine.tapes["width"], machine.tapes["descriptor"])
        snapshots = [list(tape.cells) for tape in borrowed]
        events = {"produced": 0, "consumed": 0}
        header_hash = hashlib.sha256()
        execute = machine.producer.execute
        consume = machine.consumer.run

        def checked_execute():
            index = events["produced"]
            require(index < N and index == events["consumed"], "one producer per physical packet")
            require(set(inventory(machine)) == identities, "stable physical tape identities")
            E, bits = exponent(index, names, ell, h, axes, opposite)
            require(machine.producer.data["address"] is machine.tapes["address"], "actual odometer address alias")
            require(machine.tapes["address"].cells == bits and machine.tapes["address"].head == 0,
                    "complete physical address sequence")
            require(all(c.tape.cells[0] == 2 and c.tape.cells[-1] == 3 and c.tape.head == 0
                        for c in machine.producer.c.values()), "encoded producer counter rearm")
            execute()
            header = machine.tapes["header"]
            require(header.cells == [(E >> bit) & 1 for bit in range(ell, -1, -1)] and header.head == 0,
                    "independent named-coordinate header")
            require(machine.producer.trace is None, "no retained producer instruction history")
            header_hash.update(bytes(header.cells))
            events["produced"] += 1

        def checked_consume(header, desc, width_desc, source_packet):
            index = events["consumed"]
            require(events["produced"] == index + 1 and index < N, "actual header/packet pairing")
            require(header is machine.producer.data["output"] and desc is machine.producer.descriptor,
                    "actual producer output borrowed")
            require(width_desc is machine.tapes["width"] and source_packet is machine.tapes["packet"],
                    "actual extracted packet borrowed")
            require(source_packet.cells == ["^", *encode(original_values[index], width), "$"],
                    "packet extraction keeps source order")
            result = consume(header, desc, width_desc, source_packet)
            bits = encode(rotate(original_values[index], residues[index]), width)
            require(result.cells == ["^", *bits, "$", "!"] and result.head == 0,
                    "literal signed packet endpoint")
            events["consumed"] += 1
            return result

        machine.producer.execute = checked_execute
        machine.consumer.run = checked_consume
        with patch.object(producer.Tape, "__init__", no_new_tape), patch.object(consumer.Tape, "__init__", no_new_tape):
            output = machine.run()
        require(events == {"produced": N, "consumed": N}, "complete full-wrap packet count")
        require(output is machine.tapes["fulloutput"] and output.cells == expected, "complete diagonal stream endpoint")
        require(all(tape.cells == original for tape, original in zip(borrowed, snapshots)), "borrowed stream/descriptors preserved")
        final = inventory(machine)
        require(set(final) == identities and all(len(t.cells) == capacities[key] for key, t in final.items()),
                "no tape replacement or growth")
        require(all(tape.head == 0 for tape in final.values()), "all 38 heads returned")
        retained = {id(output), *(id(tape) for tape in borrowed)}
        require(all(not any(tape.cells) for key, tape in final.items() if key not in retained), "all private roles blank")
        require(machine.gates["flip"] == 2 * N - 2 and machine.gates["consumer-rearm"] == N
                and machine.gates["reset-first"] == N - 1, "full-wrap/rearm gate census")
        require(dict(machine.actions) == dict(adapter_calls), "adapter action invoice reconciliation")
        require({k: v for k, v in machine.consumer.invoice.items() if "." in k} == dict(consumer_calls),
                "consumer action invoice reconciliation")
        require(machine.consumer.invoice["gate"] == sum(machine.consumer.gates.values()), "consumer gate reconciliation")
        actual = Counter()
        for key, tape in final.items():
            for operation in ("read", "write", "move"):
                require(tape.counts[operation] == observed[key, operation], "primitive operation observation reconciliation")
                actual[operation] += tape.counts[operation]
        gates = sum(machine.gates.values()) + sum(machine.producer.gates.values()) + sum(machine.consumer.gates.values())
        total = sum(actual.values()) + gates
        full_cells = len(machine.tapes["fullinput"].cells) + len(output.cells)
        all_cells = sum(capacities.values())
        Q = ell + K + h + len(axes) + 6
        b = (ell - 1) % K
        a = b if b <= h < ell - 1 else 0
        participating = sum(h < (ell if long else ell - 1) for long in axes)
        bank = max(1, participating * max(a, 1))
        producer_cells = A + bank + (h + 1) + ell + 1 + 22 * Q + 86
        B = 2 * r * width
        expected_cells = producer_cells + 2 * N * (B + 2) + 4 * B + 2 * width + A + 3 * ell + 32
        expected_auxiliary = producer_cells + 4 * B + 2 * width + A + 3 * ell + 28
        require(all_cells == expected_cells and all_cells - full_cells == expected_auxiliary,
                "exact physical capacity formula")
        require(len(machine.producer.c) == 21 and machine.producer.trace is None
                and len(machine.tapes) <= 11 and len(machine.consumer.tapes) == 10, "fixed control dictionaries/no histories")
        receipt = dict(shape=dict(ell=ell, K=K, h=h, axes=list(axes), opposite=opposite, width=width),
                       records=N, address_bits=A, roles=38, cells=all_cells, full_stream_cells=full_cells,
                       auxiliary_cells=all_cells - full_cells, physical_operations=dict(actual),
                       gate_operations=gates, total_tariff=total, adapter_gates=dict(machine.gates),
                       adapter_actions=dict(machine.actions), consumer_gates=dict(machine.consumer.gates),
                       producer_gates=dict(machine.producer.gates), headers_sha256=header_hash.hexdigest(),
                       source_sha256=digest(source), output_sha256=digest(output.cells))
        return receipt, list(output.cells)


def rejects(call, text):
    try:
        call()
    except ValueError as error:
        require(text in str(error), "unexpected control diagnostic: " + str(error))
        return str(error)
    raise ValueError("control was accepted: " + text)


def controls(adapter, producer, consumer):
    raw = (HERE / "pass.py").read_text()
    mutations = (
        ("no_odometer_flip", "self.write('address', 1-old)", "self.write('address', old)", "complete physical address sequence"),
        ("no_counter_rearm", "self.rearm_producer()", "pass", "encoded producer counter rearm"),
        ("consumer_left_used", "self.consumer.used = False", "self.consumer.used = True", "one-shot consumer"),
        ("header_not_cleared", "self.clear_header()", "pass", "all private roles blank"),
        ("early_fullwrap", "if self.test(self.increment()):", "if self.test(not self.increment()):", "full cube packet extent"),
        ("uncharged_adapter_move", "self.actions[role+'.move'] += 1", "self.actions[role+'.move'] += 0", "adapter action invoice reconciliation"),
    )
    results = []
    for name, old, new, diagnostic in mutations:
        require(raw.count(old) == 1, "unique actual mutation site: " + name)
        changed = raw.replace(old, new)
        module = ModuleType("diagonal_pass_mutant")
        module.__file__ = str(HERE / "pass.py")
        exec(compile(changed, module.__file__, "exec"), module.__dict__)
        failure = rejects(lambda: run_case(module, producer, consumer, (2, 1, 1, (True,), False, 4)), diagnostic)
        results.append(dict(name=name, diagnostic=failure, mutated_sha256=hashlib.sha256(changed.encode()).hexdigest()))
    return results


def static_boundary():
    tree = ast.parse((HERE / "pass.py").read_text())
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == "DiagonalPass")
    methods = [x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name != "__init__"]
    require(not any(isinstance(x, ast.Attribute) and x.attr in ("cells", "head", "capacities")
                    for method in methods for x in ast.walk(method)), "adapter bypasses physical tape API")
    require(not any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "range"
                    for method in methods for x in ast.walk(method)), "runtime host-counted range")
    return "Runtime accesses only tape primitives; no host-counted ranges, cell indexing or head inspection."


def build(include_large=True):
    sources = authenticate()
    producer = load("diagonal_retained_producer", "inputs/controller.py")
    consumer = load("diagonal_retained_consumer", "inputs/consumer.py")
    adapter = load("diagonal_adapter", "pass.py")
    evidence = []
    small = (3, 2, 1, (True, False), False, 4)
    first, stream = run_case(adapter, producer, consumer, small)
    evidence.append(first)
    inverse, returned = run_case(adapter, producer, consumer, (*small[:4], True, small[5]), stream)
    require(digest(returned) == first["source_sha256"], "actual full-pass opposite round trip")
    evidence.append(inverse)
    for shape in ((4, 2, 2, (True,), False, 4), (3, 2, 2, (False,), False, 3),
                  (2, 1, 0, (True, False), True, 3)):
        receipt, _ = run_case(adapter, producer, consumer, shape)
        evidence.append(receipt)
    negative = controls(adapter, producer, consumer)
    if include_large:
        receipt, _ = run_case(adapter, producer, consumer, (6, 2, 4, (True, False), False, 4))
        evidence.append(receipt)
    return dict(status="PASS_ENCODED_TWIDDLE_DIAGONAL", source_sha256=sources,
                physical_boundary=static_boundary(), complete_cube_cases=evidence, controls=negative,
                roundtrip="Actual complete32-record forward output consumed by opposite pass, with original input recovered.",
                instrumentation="Checker-only bounded counters wrap primitives and call boundaries; no production scheduling decisions or histories supplied.",
                limitations=["Valid already-positioned complete cubes and represented signed negations only.",
                             "No butterfly, relocation, normalization, rounding or complete supplier."])


def main():
    args = sys.argv[1:]
    require(args in ([], ["--emit"], ["--small"]), "usage: verify.py [--emit|--small]")
    result = build(args != ["--small"])
    if args:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "frozen receipt mismatch")
        print(result["status"])


if __name__ == "__main__":
    main()
