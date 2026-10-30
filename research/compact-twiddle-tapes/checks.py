"""Independent exact invoices and deterministic cases. Nick Petalas. Apache-2.0."""

import hashlib
import itertools
import json
from types import ModuleType

from machine import Tape, encode, execute, fetch, require


def sources(package):
    root = package.parent.parent
    manifest = json.loads((package / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            path = root / row['path']
            require(path.is_file() and not path.is_symlink(), 'source absent or linked')
            require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'],
                    'source hash mismatch: ' + row['path'])
    path = root / 'research/synthetic-twiddle-circuit/circuit.py'
    module = ModuleType('authenticated_twiddle_circuit')
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def access_cost(wire):
    h = max(1, wire.bit_length())
    return 8 * h + 27 + 17 * wire - 5 * wire.bit_count()


def access_cases():
    """Check every address through ten bits, including every borrow boundary."""
    digest = hashlib.sha256()
    wire_text = '^' + '01' * 512 + '_'
    for wire in range(1024):
        field = bin(wire)[2:][::-1] + '#$'
        program, wires, counter = Tape(field, True), Tape(wire_text), Tape('_' * 13)
        bit = fetch(program, wires, counter)
        cost = sum(sum(t.counts) for t in (program, wires, counter))
        require(bit == wire % 2, 'wrong access value')
        require(cost == access_cost(wire), 'primitive invoice mismatch')
        require(program.head == len(field) - 1 and ''.join(program.cells) == field
                and wires.head == counter.head == 0 and ''.join(wires.cells) == wire_text
                and all(x == '_' for x in counter.cells), 'return invariant failed')
        digest.update(json.dumps([wire, cost]).encode())
    return {'indices': 1024, 'sha256': digest.hexdigest()}


def invoice(inputs, gates, outputs):
    """No program parsing, tape code, or machine operation is used here."""
    total_wires = inputs + 2 + len(gates)
    width = (total_wires - 1).bit_length()
    length = 2 + sum(3 + max(1, a.bit_length()) + max(1, b.bit_length())
                     for _, a, b in gates)
    length += sum(2 + max(1, w.bit_length()) for w in outputs)
    primitives = 8 * inputs + 2 * len(outputs) + 5 * total_wires + 2 * length + 31
    for j, (_, a, b) in enumerate(gates):
        primitives += 4 * (inputs + 2 + j) + 9 + access_cost(a) + access_cost(b)
    primitives += sum(4 + access_cost(w) for w in outputs)
    return {'primitives': primitives, 'program_cells': length,
            'cells': length + inputs + total_wires + len(outputs) + width + 10,
            'wire_cells': total_wires + 2, 'counter_cells': width + 3}


def boolean_oracle(inputs, gates, outputs, bits):
    values = [0, 1, *bits]
    require(len(bits) == inputs, 'oracle input width')
    for op, a, b in gates:
        values.append(values[a] * values[b] if op == 'and' else (values[a] + values[b]) % 2)
    return tuple(values[w] for w in outputs)


def check_case(inputs, gates, outputs, bits, expected=None):
    program = encode(inputs, gates, outputs)
    result = execute(program, bits)
    bill = invoice(inputs, gates, outputs)
    oracle = boolean_oracle(inputs, gates, outputs, bits) if expected is None else expected
    require(result.bits == oracle, 'wrong circuit value')
    require(sum(sum(c) for c in result.counts) == bill['primitives'], 'primitive invoice mismatch')
    require(sum(result.cells) == bill['cells'] and len(program) == bill['program_cells'],
            'cell invoice mismatch')
    require(result.cells[2:4] == (bill['wire_cells'], bill['counter_cells']), 'private extent mismatch')
    require(result.borrowed_restored and result.private_blank and result.heads == (0,) * 5,
            'return contract mismatch')
    return bill


def generic_cases():
    digest, cases, programs = hashlib.sha256(), 0, 0
    for inputs in range(1, 5):
        for seed in range(12):
            rows = []
            for j in range(seed % 7):
                limit = inputs + 2 + j
                rows.append(('and' if (seed + j) % 2 else 'xor',
                             (seed * 3 + j) % limit, (seed + 2 * j) % limit))
            gates = tuple(rows)
            outputs = (0, 1, inputs + 1, inputs + 1 + len(gates))
            programs += 1
            for bits in itertools.product((0, 1), repeat=inputs):
                bill = check_case(inputs, gates, outputs, bits)
                digest.update(json.dumps([inputs, seed, bits, bill], sort_keys=True).encode())
                cases += 1
    wide = []
    for inputs in (31, 63, 127, 255, 511):
        outputs = (0, 1, inputs, inputs + 1)
        wide.append(check_case(inputs, (), outputs, (1,) * inputs))
    return {'programs': programs + len(wide), 'cases': cases + len(wide),
            'sha256': digest.hexdigest(), 'wide_counter_cases': wide}


def exponent_oracle(circuit, bits):
    values = dict(zip(circuit.slots, bits))
    total = 0
    for i in range(max(i for i, _ in circuit.slots) + 1):
        if (i, circuit.h) in values:
            lower = sum((1 << v) * values[i, v] for v in range(circuit.h))
            total += values[i, circuit.h] * lower
    residue = ((1 if circuit.opposite else -1) * total << (circuit.ell - circuit.h))
    residue %= 1 << (circuit.ell + 1)
    return tuple((residue >> k) & 1 for k in range(circuit.ell, -1, -1))


def twiddle_cases(circuit_module):
    digest, cases, programs, maximum = hashlib.sha256(), 0, 0, {}
    shapes = [(2, 1, (True,)), (3, 1, (True, False)), (3, 2, (False, False))]
    shapes += [(4, 2, (True, False)), (5, 3, (True, True, False)),
               (12, 5, (True, False)), (32, 7, (False, True)), (48, 11, (True, False))]
    for ell, width, axes in shapes:
        rounds = range(ell) if ell <= 5 else (0, ell // 2, ell - 1)
        for h, opposite in itertools.product(rounds, (False, True)):
            c = circuit_module.compile_round(ell, width, axes, h, opposite)
            n = len(c.slots)
            words = range(1 << n) if n <= 7 else (0, 1, (1 << n) - 1)
            programs += 1
            for word in words:
                bits = tuple((word >> k) & 1 for k in range(n - 1, -1, -1))
                bill = check_case(n, c.gates, c.outputs, bits, exponent_oracle(c, bits))
                digest.update(json.dumps([ell, width, axes, h, opposite, str(word), bill],
                                         sort_keys=True).encode())
                if bill['primitives'] > maximum.get('primitives', 0):
                    maximum = dict(bill, ell=ell, inputs=n, gates=len(c.gates), outputs=len(c.outputs))
                cases += 1
    return {'programs': programs, 'headers': cases, 'sha256': digest.hexdigest(), 'maximum': maximum}


def rejections():
    bad = [('^$', (0,)), ('O0#$', (0,)), ('^O#$', (0,)), ('^O00#$', (0,)),
           ('^O10#$', (0,)), ('^O11#$', (0,)), ('^O2#$', (0,)),
           ('^O0#X0#0#$', (0,)), ('^X11#0#O0#$', (0,)),
           ('^O0#$', (True,)), ('^O0#$', ()), ('^O0#$', (0,) * 4095),
           ('^O' + '1' * 20 + '#$', (0,)), ('^' + 'O0#' * 70000 + '$', (0,))]
    for text, bits in bad:
        try:
            execute(text, bits)
        except ValueError:
            continue
        raise ValueError('invalid program accepted')
    return len(bad)


def comparison(package, circuit_module):
    """Reproduce the explicitly separate unary comparison, not a proof premise."""
    data = json.loads((package / 'COMPARISONS.json').read_text())
    row = data['sources'][0]
    retained = package / row['retained_path']
    require(hashlib.sha256(retained.read_bytes()).hexdigest() == row['sha256'],
            'comparison source hash mismatch')
    fixture = data['fixture']
    shape = fixture['shape']
    c = circuit_module.compile_round(shape['ell'], shape['width'],
                                     tuple(shape['long_axes']), shape['round'], shape['opposite'])
    a, g, q = len(c.slots), len(c.gates), len(c.outputs)
    length = 2 + sum(x + y + 5 for _, x, y in c.gates) + sum(w + 3 for w in c.outputs)
    require(fixture['unary_program_cells'] == length, 'unary comparison length mismatch')
    require(fixture['unary_all_tape_cells'] == length + a + (a + g + 2) + q + 7,
            'unary comparison cells mismatch')
    require(fixture['compact'] == invoice(a, c.gates, c.outputs), 'compact comparison differs')
    return fixture


def collect(package):
    circuit = sources(package)
    return {'schema_version': 1, 'access': access_cases(), 'generic': generic_cases(),
            'twiddle': twiddle_cases(circuit),
            'rejections': rejections(), 'comparison': comparison(package, circuit)}
