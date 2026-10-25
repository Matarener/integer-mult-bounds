"""Independent arithmetic, exact operation invoice and finite fixtures."""

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys
from types import SimpleNamespace

import machine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def source():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            path = ROOT / row['path']
            machine.require(not path.is_symlink() and path.is_file(), 'missing source')
            machine.require(path.stat().st_size <= 8_000_000, 'source too large')
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            machine.require(digest == row['sha256'], 'source hash mismatch')
    path = ROOT / 'research/synthetic-twiddle-circuit/circuit.py'
    spec = importlib.util.spec_from_file_location('pinned_twiddle', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def invoice(circuit, length):
    a, g, q = len(circuit.slots), len(circuit.gates), len(circuit.outputs)
    b = a + g + 2
    steps = 8 * a + 2 * q + 5 * b + 2 * length + 32
    steps += sum(5 * (u + v) + 4 * (a + 2 + j) + 27
                 for j, (_, u, v) in enumerate(circuit.gates))
    steps += sum(5 * w + 13 for w in circuit.outputs)
    return steps, length + a + b + q + 7


def run(circuit, address, expected):
    text = machine.encode(circuit)
    result = machine.execute(text, address)
    machine.require(result.bits == expected, 'sequential result mismatch')
    steps, cells = invoice(circuit, len(text))
    measured = sum(row[key] for row in result.counts for key in ('read', 'write', 'move'))
    machine.require(measured == steps, 'operation invoice mismatch')
    measured_cells = len(text) + len(address) + 2 + result.wire_cells + len(expected) + 3
    machine.require(measured_cells == cells, 'cell invoice mismatch')
    machine.require(result.restored and result.blank_private and result.heads == (0, 0, 0, 0),
                    'restoration mismatch')
    return {'operations': steps, 'cells': cells, 'program_cells': len(text),
            'gates': len(circuit.gates)}


def oracle(circuit, address):
    # Integer arithmetic is confined to this independent verifier.
    coordinates = [0] * (max(i for i, _ in circuit.slots) + 1)
    for bit, (axis, exponent) in zip(address, circuit.slots):
        coordinates[axis] += bit * (1 << exponent)
    total = 0
    for axis, value in enumerate(coordinates):
        if (axis, circuit.h) in circuit.slots:
            branch = (value // (1 << circuit.h)) % 2
            total += branch * (value % (1 << circuit.h))
    sign = 1 if circuit.opposite else -1
    value = (sign * total * (1 << (circuit.ell - circuit.h))) % (1 << (circuit.ell + 1))
    return tuple((value >> k) & 1 for k in range(circuit.ell, -1, -1))


def headers(module):
    count, complete, programs = 0, 0, 0
    largest = {'operations': 0}
    for ell in range(2, 5):
        for axes in range(1, 3):
            for flags in itertools.product((False, True), repeat=axes):
                for width in range(1, ell):
                    for h, opposite in itertools.product(range(ell), (False, True)):
                        circuit = module.compile_round(ell, width, flags, h, opposite)
                        bits = len(circuit.slots)
                        values = range(1 << bits) if bits <= 6 else (0, 1, 37, (1 << bits) - 1)
                        complete += bits <= 6
                        programs += 1
                        for value in values:
                            word = tuple((value >> k) & 1 for k in range(bits - 1, -1, -1))
                            measured = run(circuit, word, oracle(circuit, word))
                            machine.require(module.evaluate(circuit, word) == oracle(circuit, word),
                                            'predecessor arithmetic disagrees')
                            if measured['operations'] > largest['operations']:
                                largest = measured
                            count += 1
    return {'cases': count, 'programs': programs, 'complete_address_programs': complete,
            'largest': largest}


def wide(module):
    randomizer = random.Random(3522)
    rows = []
    for ell, axes, h in ((8, 3, 6), (16, 2, 14), (32, 1, 30), (48, 1, 46)):
        for opposite in (False, True):
            circuit = module.compile_round(ell, 3, (True,) * axes, h, opposite)
            for _ in range(2):
                word = tuple(randomizer.randrange(2) for _ in circuit.slots)
                rows.append(run(circuit, word, oracle(circuit, word)))
    return {'cases': len(rows), 'largest': max(rows, key=lambda x: x['operations'])}


def generic():
    cases, programs = 0, 0
    for first, second in itertools.product(('and', 'xor'), repeat=2):
        for a, b in itertools.product(range(4), repeat=2):
            for c in (0, 3, 4):
                gates = ((first, a, b), (second, c, 4))
                circuit = SimpleNamespace(slots=(0, 1), gates=gates, outputs=tuple(range(6)))
                programs += 1
                for address in itertools.product((0, 1), repeat=2):
                    values = [0, 1, *address]
                    for op, left, right in gates:
                        values.append(values[left] & values[right] if op == 'and'
                                      else values[left] ^ values[right])
                    run(circuit, address, tuple(values))
                    cases += 1
    return {'programs': programs, 'cases': cases}


def invalid():
    bad = [('^$', (0,)), ('O10$', (0,)), ('^O0$', (0,)), ('^O11110$', (0,)),
           ('^Y10$', (0,)), ('^O10X1010$', (0,)), ('^O1$', (0,)),
           ('^O10$', (True,)), ('^O10$', (2,)), ('^O10$', ()),
           ('^' + 'O' * machine.MAX_PROGRAM + '$', (0,)),
           ('^O10$', (0,) * (machine.MAX_WIRES - 1)),
           ('^A1010O10$', (0,) * (machine.MAX_WIRES - 2))]
    for program, address in bad:
        try:
            machine.execute(program, address)
        except ValueError:
            continue
        raise ValueError('malformed boundary accepted')
    valid = machine.execute('^O10$', (0,))
    machine.require(valid.bits == (0,), 'valid retry failed')
    return len(bad)


def receipt():
    module = source()
    return {'status': 'PASS_SYNTHETIC_TWIDDLE_TAPES', 'generic': generic(),
            'headers': headers(module), 'wide': wide(module), 'invalid_rejections': invalid(),
            'tape_roles': 4, 'invoice': 'exact reads+writes+unit_moves',
            'scope': 'finite execution plus separate unbounded written interpreter proof'}
