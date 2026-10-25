"""Independent semantic and access checks. Nick Petalas, Apache-2.0."""

from collections import Counter
from itertools import product
from pathlib import Path
import hashlib
import importlib.util
import json

import controller as c

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def load_oracle():
    spec = importlib.util.spec_from_file_location(
        'canonical', ROOT / 'research/synthetic-twiddle-circuit/circuit.py')
    module = importlib.util.module_from_spec(spec)
    # The canonical dataclass needs its module registered during import.
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def authenticate():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            path = ROOT / row['path']
            c.require(path.is_file() and not path.is_symlink(), 'missing source input')
            c.require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'],
                      'source input changed: ' + row['path'])
    vendored = json.loads((PACKAGE / 'PREDECESSOR.json').read_text())
    for row in vendored['files']:
        raw = (PACKAGE / row['retained_path']).read_bytes()
        c.require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'predecessor changed')


def expected(oracle, shape):
    ell, k, h, axes, opposite = shape
    slots = oracle.named_slots(ell, k, axes)
    active = [i for i, long in enumerate(axes) if h < ell - (not long)]
    b = (ell - 1) % k
    a = b if b <= h < ell - 1 else 0
    stride = max(1, a)
    P, n = max(1, len(active) * stride), h + 1
    access = {role: [] for role in c.ROLES}
    reads, writes = Counter(), Counter()
    def touch(role, target, mode):
        access[role].append(target)
        (reads if mode == 'read' else writes)[role] += 1
    for index, (axis, v) in enumerate(slots):
        touch('address', index, 'read')
        if axis not in active:
            continue
        base = active.index(axis) * stride
        lows = []
        if v < a:
            touch('bank', base + v, 'write')
        elif v == h:
            for low in range(a):
                touch('bank', base + low, 'read')
                touch('bank', base + low, 'write')
                lows.append(low)
            touch('bank', base, 'write')
        elif a <= v < h:
            touch('bank', base, 'read')
            lows.append(v)
        for low in lows:
            for target in range(low, n):
                touch('total', target, 'read')
                touch('total', target, 'write')
    f = int(h > 0 and not opposite)
    if f:
        for target in range(n):
            touch('total', target, 'read')
            touch('total', target, 'write')
    for j in range(ell + 1):
        if j <= h:
            touch('total', h - j, 'read')
        touch('output', j, 'write')
    for role, size in (('bank', P), ('total', n)):
        for target in range(size):
            touch(role, target, 'write')
    data = {}
    for role, targets in access.items():
        walk = [0, *targets, 0]
        row = {'read': reads[role], 'write': writes[role],
               'move': sum(abs(y - x) for x, y in zip(walk, walk[1:], strict=False))}
        data[role] = {key: value for key, value in row.items() if value}
    L = len(active) * h * (h + 3) // 2
    gates = {'and': len(active) * h + L + f * n, 'xor': L + 2 * f * n}
    return data, {key: value for key, value in gates.items() if value}


def replay(opcodes, bits, sizes):
    """Independent finite-opcode evaluator, used only by the verifier."""
    data = {role: [0] * size for role, size in sizes.items()}
    data['address'] = list(bits)
    heads = dict.fromkeys(c.ROLES, 0)
    state = dict.fromkeys(c.REGISTERS, 0)
    state['one'] = 1
    read_order = []
    for code in opcodes:
        kind, role, reg = c.OPS[code]
        if kind == 'move':
            heads[role] += reg
            c.require(0 <= heads[role] < sizes[role], 'replay move out of bounds')
        elif kind == 'read':
            state[reg] = data[role][heads[role]]
            if role == 'address':
                read_order.append(heads[role])
        elif kind == 'write':
            data[role][heads[role]] = state[reg]
        elif role == 'mask':
            state['carry'] = state['branch'] * state['pending']
        elif role == 'ripple':
            old, carry = state['old'], state['carry']
            state['inverse'], state['carry'] = (old + carry) % 2, (old + carry) // 2
        elif role == 'invert':
            state['inverse'] = 1 - state['old']
        elif role == 'negate':
            old, carry = state['inverse'], state['carry']
            state['old'], state['carry'] = (old + carry) % 2, (old + carry) // 2
        elif role == 'save-branch':
            state['branch'] = state['input']
        elif role == 'save-pending':
            state['pending'] = state['input']
        elif role == 'carry-one':
            state['carry'] = 1
        else:
            c.require(role == 'reset', 'unknown replay action')
            state = {name: int(name == 'one') for name in c.REGISTERS}
    c.require(read_order == list(range(len(bits))), 'borrowed read order differs')
    c.require(not any(heads.values()), 'head not restored')
    c.require(data['address'] == list(bits), 'borrowed input changed')
    c.require(not any(data['bank']) and not any(data['total']), 'private data not erased')
    c.require(state == {name: int(name == 'one') for name in c.REGISTERS}, 'scratch not restored')
    return tuple(data['output'])


def direct(oracle, shape, bits):
    ell, k, h, axes, opposite = shape
    values = dict(zip(oracle.named_slots(ell, k, axes), bits, strict=True))
    S = sum(values[i, h] * sum((1 << v) * values[i, v] for v in range(h))
            for i, long in enumerate(axes) if h < ell - (not long))
    residue = ((1 if opposite else -1) * (1 << (ell - h)) * S) % (1 << (ell + 1))
    return tuple((residue >> j) & 1 for j in range(ell, -1, -1))


def run_controller(oracle, shape, bits, trace=True):
    descriptor = c.encode(*shape)
    machine = c.Controller(descriptor, bits, trace=trace)
    machine.execute()
    invoice = machine.invoice()
    data, gates = expected(oracle, shape)
    c.require(invoice['data'] == data and invoice['gates'] == gates, 'exact data invoice differs')
    c.require(tuple(machine.data['output'].cells) == direct(oracle, shape, bits), 'wrong exponent')
    c.require(machine.data['address'].cells == list(bits), 'borrowed input changed')
    c.require(all(t.head == 0 for t in machine.data.values()), 'data head not restored')
    c.require(all(not any(machine.data[x].cells) for x in ('bank', 'total')), 'data erasure failed')
    c.require(all(t.tape.head == 0 and not any(t.tape.cells) for t in machine.c.values()),
              'counter erasure or head return failed')
    c.require(machine.descriptor.cells == list('^' + descriptor + '$') and
              machine.descriptor.head == 0, 'borrowed descriptor changed')
    M, N = len(bits) + shape[0] + 1, len(descriptor)
    actions = invoice['control_tape_actions'] + invoice['descriptor_actions'] + sum(
        sum(row.values()) for row in data.values()) + sum(gates.values())
    c.require(actions <= 5000 * M * M * (N + 4), 'polynomial work bound failed')
    cells = sum(invoice[x] for x in ('data_cells', 'control_cells', 'descriptor_cells'))
    c.require(cells <= 90 * M, 'linear cell bound failed')
    c.require(invoice['control_cells'] == 21 * (N + 4), 'counter capacity differs')
    return machine, invoice


def science():
    authenticate()
    oracle = load_oracle()
    shapes, addresses, control_runs = 0, 0, 0
    trace_digest = hashlib.sha256()
    for ell in (2, 3, 4):
        for k, h, axes, opposite in product(range(1, ell), range(ell),
                                          ((False,), (True,), (False, False), (False, True),
                                           (True, False), (True, True)), (False, True)):
            shape = ell, k, h, axes, opposite
            program = oracle.compile_round(ell, k, axes, h, opposite)
            A = len(program.slots)
            machine, invoice = run_controller(oracle, shape, (0,) * A)
            control_runs += 1
            sizes = {role: len(t.cells) for role, t in machine.data.items()}
            trace_digest.update(bytes(machine.trace))
            for bits in product((0, 1), repeat=A):
                output = replay(machine.trace, bits, sizes)
                c.require(output == direct(oracle, shape, bits), 'replay arithmetic mismatch')
                c.require(output == oracle.evaluate(program, bits), 'canonical circuit mismatch')
                addresses += 1
            other, other_invoice = run_controller(oracle, shape, (1,) * A)
            control_runs += 1
            c.require(other.trace == machine.trace and other_invoice == invoice,
                      'control schedule depends on address data')
            shapes += 1
    examples = []
    for shape in ((8, 4, 5, (True, False) * 6, False),
                  (8, 4, 5, (True, False) * 6, True),
                  (16, 7, 12, (True, False), False),
                  (32, 15, 25, (False, True), True)):
        A = sum(shape[0] if x else shape[0] - 1 for x in shape[3])
        slots = oracle.named_slots(shape[0], shape[1], shape[3])
        bits = tuple(int(v == shape[2] or (i + 2 * v) % 5 in (0, 2)) for i, v in slots)
        machine, invoice = run_controller(oracle, shape, bits)
        c.require(tuple(machine.data['output'].cells) == oracle.evaluate(
            oracle.compile_round(shape[0], shape[1], shape[3], shape[2], shape[4]), bits),
                  'wide canonical mismatch')
        examples.append({'ell': shape[0], 'K': shape[1], 'h': shape[2],
                         'axes': len(shape[3]), 'opposite': shape[4], 'invoice': invoice,
                         'output_bits': ''.join(map(str, machine.data['output'].cells))})
        control_runs += 1
    return {'status': 'PASS_ENCODED_TWIDDLE_CONTROLLER', 'complete_shapes': shapes,
            'complete_addresses': addresses, 'actual_control_runs': control_runs,
            'small_trace_sha256': trace_digest.hexdigest(), 'examples': examples}
