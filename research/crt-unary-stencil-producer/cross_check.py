"""Bind paid unary output to the unchanged scanner and pre-code source oracle.

All indexing, integers and hashes here are observer verification, not producer
instructions. The consumer and source adapter are authenticated before exec.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True, optimize=0), module.__dict__)
    return module


def bind_inputs():
    rows = json.loads((P / 'SOURCES.json').read_text())['files']
    count = 0
    for row in rows:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'declared input SHA256: ' + row['path'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
             'declared Git blob: ' + row['path'])
        count += 1
    pins = json.loads((P / 'SOURCE-PINS.json').read_text())
    for row in pins:
        need(row['origin_commit'] == '4f49743a9df0cf7501cdc62bd5707a122fa071e9', 'exact predecessor head')
        raw = (ROOT / row['path']).read_bytes()
        need(len(raw) == row['size'] and hashlib.sha256(raw).hexdigest() == row['sha256'],
             'unchanged minimal predecessor export')
    need(hashlib.sha256((P / 'independent_oracle.py').read_bytes()).hexdigest()
         == '78ba91c921ddcb37cefe674e10f34e9f896c6243af859bdb63f50b6e7086cd34',
         'pre-code oracle freeze')
    return count


def build(producer, machine, shape, **mutant):
    inputs = tuple(machine.Tape([machine.LEFT] + ['1'] * n + [machine.END, machine.BLANK]) for n in shape)
    before = [list(t.cells) for t in inputs]
    work, stencil = producer.produce(*inputs, machine.Tape, **mutant)
    need(all(t.cells == old for t, old in zip(inputs, before)), 'protected unary input cells')
    if not mutant.get('omit_cleanup'):
        need(all(t.cells[0] == machine.LEFT and all(c == machine.BLANK for c in t.cells[1:]) for t in work),
             'eight private records erased with END markers')
    if not mutant.get('omit_output_return'):
        need(all(t.head == 0 for t in inputs + work + (stencil,)), 'producer heads at permanent LEFT')
    invoice = sum(t.actions for t in inputs + work + (stencil,))
    if not mutant:
        g, h, k, y, j, b = shape
        need(invoice == 33*h + 25*k + 38*y - 6*g - j + 12*b + 335, 'independent exact producer invoice')
        need(sum(len(t.cells) for t in inputs + work + (stencil,)) == 4*h + 2*k - g + 4*y + 2*b + 38,
             'independent exact visited-space census')
    return stencil, invoice


def consume(machine, stencil):
    original = list(stencil.cells)
    previous = stencil.actions
    counter, mask = machine.transduce(stencil)
    need(stencil.cells == original and counter.head == mask.head == stencil.head == 0, 'consumer protected/returned boundary')
    need(all(c == machine.BLANK for c in counter.cells[1:]), 'consumer counter erased including END')
    bits = ''.join(mask.cells[1:-1])
    length = len(stencil.cells) - 2
    need(len(bits) == 1 << length and mask.cells[0] == machine.LEFT and mask.cells[-1] == machine.END,
         'owned complete mask')
    actions = sum(t.actions for t in (stencil, counter, mask)) - previous
    need(actions == 8 * len(bits) * length + 15 * len(bits) + 13 * length + 18, 'unchanged scanner exact invoice')
    return bits, actions


def run():
    bindings = bind_inputs()
    producer = load('cross_producer', P / 'producer.py')
    machine = load('cross_retained_machine', P / 'source/predecessor_machine.py')
    oracle = load('cross_frozen_oracle', P / 'independent_oracle.py')
    source = load('cross_crt_source', ROOT / 'research/unconditional-batched-crt/check_batched_crt.py')
    frozen = json.loads((P / 'ORACLE-RESULT.json').read_text())
    rows, addresses, setups, scans = [], 0, 0, 0
    for entry in frozen['rows']:
        shape = tuple(entry[key] for key in ('G', 'H', 'K', 'Y', 'J', 'B'))
        g, h, k, y, j, b = shape
        stencil, invoice = build(producer, machine, shape)
        cells = oracle.expected_stencil(*shape)
        need(stencil.cells == [machine.LEFT] + cells + [machine.END], 'paid output versus pre-code direct stencil')
        need(hashlib.sha256(json.dumps(cells, separators=(',', ':')).encode()).hexdigest()
             == entry['stencil_json_sha256'], 'frozen oracle stencil receipt')
        bits, scan = consume(machine, stencil)
        need(hashlib.sha256(bits.encode()).hexdigest() == entry['bad_mask_sha256'], 'actual consumer versus pre-code mask')
        for address, bit in enumerate(bits):
            yy = (address >> b) & ((1 << y) - 1)
            tt = (address >> (b + y)) & ((1 << h) - 1)
            uu = address >> (b + y + h)
            expected = oracle.source_good(address, *shape)
            need(source.good(uu, tt, yy, bits=g, positions=(j,), guard=k) == expected == (bit == '0'),
                 'actual source good predicate')
            need(source.linear_guard(uu, tt, yy, bits=g, positions=(j,), guard=k, control_bits=h, ybits=y)
                 == expected, 'actual source linear-guard predicate')
        rows.append(dict(geometry=list(shape), addresses=len(bits), setup_actions=invoice, scanner_actions=scan))
        addresses += len(bits)
        setups += invoice
        scans += scan
    # These execute changed producer instructions and the unchanged consumer.
    # They leave the admitted model deliberately; they are not predecessor bugs.
    shape = (1, 2, 5, 7, 1, 1)
    stencil, _ = build(producer, machine, shape)
    right, _ = consume(machine, stencil)
    controls = []
    for name in ('include_parity', 'wrong_lower_pivot', 'wrong_upper_pivot'):
        wrong_stencil, _ = build(producer, machine, shape, **{name: True})
        wrong, _ = consume(machine, wrong_stencil)
        address = next((i for i, pair in enumerate(zip(right, wrong)) if pair[0] != pair[1]), None)
        need(address is not None, 'changed producer has actual predicate impact: ' + name)
        controls.append(dict(mutant=name, first_different_address=address, correct_bad=right[address], mutant_bad=wrong[address]))
    return dict(status='PASS_UNARY_STENCIL_CALLER_CROSSCHECK', declared_source_bindings=bindings,
                geometries=len(rows), addresses=addresses, setup_actions=setups, scanner_actions=scans,
                rows=rows, semantic_producer_consumer_controls=controls,
                scope='One-target unary geometry producer composed with unchanged scanner. Finite execution corroborates the separate all-admitted-input proof; no binary/global descriptor, many-target, payload or full CRT theorem.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    result = run()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k:result[k] for k in ('status','geometries','addresses','setup_actions','scanner_actions')}))


if __name__ == '__main__':
    main()
