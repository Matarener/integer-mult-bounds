"""Replay exact streams, separate invoices, and valid-state transitions.

Nick Petalas. Apache-2.0. No multiplication exponent is certified.
"""

import hashlib
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        require(path.is_file() and not path.is_symlink(), 'missing regular input')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'],
                'input hash differs: ' + row['path'])
    return load('sweep_circuit', ROOT / 'research/synthetic-twiddle-circuit/circuit.py')


def check_stream(shape, count, machine, oracle, circuit):
    program = circuit.compile_round(shape.ell, shape.width, shape.long_axes,
                                    shape.h, shape.opposite)
    require(shape.slots() == program.slots, 'physical order differs')
    runner = machine.Sweep(shape)
    observed = 0

    def observe(bits):
        nonlocal observed
        want = oracle.exponent(shape, observed)
        require(circuit.decode_word(bits) == want, 'named exponent differs')
        address = circuit.encode_address(observed, len(program.slots))
        require(bits == circuit.evaluate(program, address), 'circuit output differs')
        observed += 1

    actual = runner.run(count, observe)
    require(observed == count, 'record count differs')
    require(actual == oracle.expected(shape, count), 'exact data invoice differs')
    a = len(program.slots)
    require(actual['flips'] == sum(count // (1 << j) for j in range(a)),
            'flip formula differs')
    require(actual['flips'] < 2 * count, 'amortized flip bound fails')
    require(actual['work'] <= 100 * count * (a + shape.ell + 1)
            + 10 * (a + shape.ell + 1), 'linear amortized bound fails')
    require(actual['cells'] == a + max(1, len(shape.participants()) * (shape.h + 1))
            + shape.h + shape.ell + 2, 'capacity differs')
    if count == 1 << a:
        require(actual['flips'] == 2 * count - 2, 'full-cube count differs')
    return actual


def small(machine, oracle, circuit):
    fixtures = addresses = 0
    examples = []
    for ell in range(2, 6):
        for width in range(1, ell):
            for axes in ((False,), (True,), (False, True), (True, False),
                         (False, False), (True, True)):
                a = sum(ell if x else ell - 1 for x in axes)
                for h in range(ell):
                    for opposite in (False, True):
                        shape = machine.Shape(ell, width, axes, h, opposite)
                        count = 1 << a
                        bill = check_stream(shape, count, machine, oracle, circuit)
                        fixtures += 1
                        addresses += count
                        if ell == 4 and width == 2 and axes == (False, True) and h == 2:
                            examples.append(dict(ell=ell, width=width, axes=list(axes), h=h,
                                                 opposite=opposite, records=count, bill=bill))
    return dict(complete_fixtures=fixtures, complete_headers=addresses, examples=examples)


def transition(shape, address, machine, oracle):
    """Diagnostic installation of a valid state, not a charged initializer."""
    runner = machine.Sweep(shape)
    a, n = len(runner.slots), shape.h + 1
    runner.address.cells[:] = [(address >> j) & 1 for j in range(a)]
    named = dict(zip(runner.slots, runner.address.cells))
    for axis, base in runner.offsets.items():
        for v in range(n):
            runner.bank.cells[base + v] = named[axis, v]
    total = sum(named[i, shape.h] * sum(named[i, v] << v for v in range(shape.h))
                for i in runner.offsets) % (1 << n)
    runner.total.cells[:] = [(total >> v) & 1 for v in range(n)]
    runner.advance()
    after = (address + 1) % (1 << a)
    require(sum(x << j for j, x in enumerate(runner.address.cells)) == after,
            'wide odometer differs')
    named = {s: (after >> j) & 1 for j, s in enumerate(runner.slots)}
    require(all(runner.bank.cells[base + v] == named[axis, v]
                for axis, base in runner.offsets.items() for v in range(n)),
            'wide cache differs')
    value = sum(x << j for j, x in enumerate(runner.total.cells))
    exponent = value * (1 << (shape.ell - shape.h)) % (1 << (shape.ell + 1))
    positive = machine.Shape(shape.ell, shape.width, shape.long_axes, shape.h, True)
    require(exponent == oracle.exponent(positive, after), 'wide transition differs')
    for tape in (runner.address, runner.bank, runner.total, runner.output):
        tape.clear()
        require(tape.head == 0 and not any(tape.cells), 'transition cleanup failed')


def wide(machine, oracle, circuit):
    transitions = 0
    for ell, width, axes, h in ((8, 4, (True,) * 3 + (False,) * 9, 5),
                                 (48, 17, (True, False, True), 31),
                                 (256, 128, (False, True), 200)):
        shape = machine.Shape(ell, width, axes, h)
        a = len(shape.slots())
        seeds = [0, (1 << a) - 1, ((1 << a) - 1) // 3]
        seeds += [(1 << j) - 1 for j in (1, a // 3, a // 2, a - 1)]
        for address in seeds:
            transition(shape, address, machine, oracle)
            transitions += 1
    shape = machine.Shape(6, 2, (False, True), 4)
    bills = [check_stream(shape, count, machine, oracle, circuit)
             for count in (1, 3, 17, 256)]
    return dict(wide_valid_state_transitions=transitions, prefix_headers=277,
                prefix_bills=bills)


def result():
    circuit = sources()
    machine = load('sweep_machine', PACKAGE / 'sweep.py')
    oracle = load('sweep_independent', PACKAGE / 'independent.py')
    return dict(status='PASS_TWIDDLE_ADDRESS_SWEEP', small=small(machine, oracle, circuit),
                wide=wide(machine, oracle, circuit))


def run():
    actual = result()
    require(json.loads((PACKAGE / 'RESULT.json').read_text()) == actual,
            'committed result differs')
    print(json.dumps(actual, sort_keys=True))


if __name__ == '__main__':
    run()
