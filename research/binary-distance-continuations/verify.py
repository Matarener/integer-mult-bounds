"""Exact finite corroboration. Produced by Nick Petalas. Apache-2.0."""

import argparse
import ast
import hashlib
import itertools
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_construction():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            actual = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            require(actual == row['sha256'], 'changed source: ' + row['path'])
    # Both import locations are explicit; the external code is authenticated.
    sys.path.insert(0, str(ROOT / 'research/segment-continuation-stack'))
    sys.path.insert(0, str(PACKAGE))
    import binary_stack
    import stack
    return binary_stack, stack


def exact_push(d, distances):
    h = sum(distances)
    bits = sum(x.bit_length() for x in distances)
    ones = sum(x.bit_count() for x in distances)
    return 8*d + 12*h - 5*ones + 8*bits + 13*16 + 14


def exact_pop(d, distances, child_lengths, child_heads):
    h = sum(distances)
    bits = sum(x.bit_length() for x in distances)
    ones = sum(x.bit_count() for x in distances)
    cleanup = sum(2*g + 5*t + 7 for t, g in zip(child_lengths, child_heads))
    return 14*d + 12*h - 5*ones + 14*bits + 16*16 + 16 + cleanup


def frame(descriptor, mask, distances):
    rows = []
    for role, distance in enumerate(distances):
        digits = format(distance, 'b') if distance else ''
        encoded = ''.join('u' if bit == '0' else ':' for bit in digits)
        rows.append(str((mask >> role) & 1) + encoded + ';')
    return '[' + descriptor + ':' + ''.join(rows) + ']'


def fixture(stack, words, heads, descriptor, mask, prefix='101[:;]'):
    meter = stack.Meter()
    payload = [stack.Tape(meter, prefix, word, head)
               for word, head in zip(words, heads)]
    control = stack.Tape(meter, prefix)
    desc = stack.Tape(meter, prefix, descriptor)
    scratch = stack.Tape(meter, prefix)
    return meter, payload, control, desc, scratch, mask


def snapshots(machine):
    _, payload, control, desc, scratch, mask = machine
    return tuple(t.snapshot() for t in [*payload, control, desc, scratch]), mask


def write_child(tape, word, head, stack):
    for symbol in word:
        stack.emit(tape, symbol)
    for _ in range(len(word) - head):
        tape.move(-1)


def boundary(module, stack, words, heads, descriptor, mask, children, child_heads):
    machine = fixture(stack, words, heads, descriptor, mask)
    meter, payload, control, desc, scratch, _ = machine
    before = snapshots(machine)
    distances = [len(w)-h for w, h in zip(words, heads)]
    controller = module.Controller(payload, control, desc, scratch, mask)
    start = meter.total
    controller.push()
    push = meter.total - start
    require(push == exact_push(len(descriptor), distances), 'exact push invoice')
    actual = ''.join(control._cells.get(i, '_')
                     for i in range(before[0][-3][0], control._head))
    expected = frame(descriptor, mask, distances)
    require(actual == expected, 'binary frame grammar')
    require(scratch.snapshot() == before[0][-1], 'scratch after push')
    for tape, word, head in zip([*payload, desc], children, child_heads):
        write_child(tape, word, head, stack)
    # Discard the push controller so the return cannot use hidden saved state.
    controller = module.Controller(payload, control, desc, scratch, 0)
    start = meter.total
    controller.pop()
    pop = meter.total - start
    lengths = [len(w) for w in children]
    require(pop == exact_pop(len(descriptor), distances, lengths, child_heads),
            'exact pop invoice')
    restored = (*machine[:-1], controller.occupied)
    require(snapshots(restored) == before, 'complete parent restoration')
    require(push + pop <= module.action_bound(
        len(descriptor), sum(distances), sum(lengths)), 'complete action bound')
    return len(expected), push+pop


def exhaustive_small(module, stack):
    count = 0
    descriptors = [''.join(x) for n in range(4)
                   for x in itertools.product('01', repeat=n)]
    for length in range(6):
        for word_tuple in itertools.product('01', repeat=length):
            word = ''.join(word_tuple)
            for head in range(length+1):
                for descriptor in descriptors:
                    role = count % 16
                    words, heads = ['']*16, [0]*16
                    words[role], heads[role] = word, head
                    children = ['']*17
                    children[(role+3) % 17] = '01011'
                    child_heads = [0]*17
                    child_heads[(role+3) % 17] = count % 6
                    boundary(module, stack, words, heads, descriptor, 1 << role,
                             children, child_heads)
                    count += 1
    boundary(module, stack, ['']*16, [0]*16, '', 0, ['']*17, [0]*17)
    return count+1


def nested(module, stack, depth, prefix_length):
    machine = fixture(stack, ['01011']*16, [3]*16, '10100', 65535,
                      '1'*prefix_length)
    _, payload, control, desc, scratch, mask = machine
    saved = []
    for level in range(depth):
        before = snapshots((*machine[:-1], mask))
        controller = module.Controller(payload, control, desc, scratch, mask)
        controller.push()
        saved.append(before)
        for role, tape in enumerate(payload):
            word = '10100' * (1 + (role+level) % 4)
            write_child(tape, word, (role+level) % (len(word)+1), stack)
        write_child(desc, '101' * (1 + level % 3), 0, stack)
        mask = 65535
    for before in reversed(saved):
        controller = module.Controller(payload, control, desc, scratch, mask)
        controller.pop()
        mask = controller.occupied
        require(snapshots((*machine[:-1], mask)) == before, 'nested restoration')
    return depth


def counter_boundaries(module, stack):
    count = 0
    for exponent in range(1, 13):
        for distance in ((1 << exponent)-1, 1 << exponent, (1 << exponent)+1):
            boundary(module, stack, ['1'*distance]+['']*15, [0]*16,
                     '00101', 1, ['']*17, [0]*17)
            count += 1
    return count


def negative_controls(module, stack):
    rejected = []
    machine = fixture(stack, ['101']+['']*15, [0]*16, '01', 1)
    _, payload, control, desc, scratch, mask = machine
    controller = module.Controller(payload, control, desc, scratch, mask)
    controller.push()
    control._cells[control._head-1] = '['
    try:
        controller.pop()
    except ValueError:
        rejected.append('wrong top delimiter')
    for name, replacement in (('increment', lambda counter: None),
                              ('decrement', lambda counter: False)):
        original = getattr(module, name)
        try:
            setattr(module, name, replacement)
            try:
                boundary(module, stack, ['101']+['']*15, [0]*16, '01', 1,
                         ['']*17, [0]*17)
            except ValueError:
                rejected.append('omitted ' + name)
        finally:
            setattr(module, name, original)
    try:
        boundary(module, stack, ['1']+['']*15, [0]*16, '', 0,
                 ['']*17, [0]*17)
    except ValueError:
        rejected.append('absent nonempty role')
    require(len(rejected) == 4, 'all semantic controls reject')
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-receipt', type=Path)
    args = parser.parse_args()
    module, stack = load_construction()
    tree = ast.parse((PACKAGE / 'binary_stack.py').read_text())
    require(not any(isinstance(n, ast.Attribute) and n.attr.startswith('_')
                    for n in ast.walk(tree)), 'no simulator metadata access')
    result = {'status': 'PASS_BINARY_DISTANCE_CONTINUATIONS'}
    result['small_boundaries'] = exhaustive_small(module, stack)
    result['power_boundaries'] = counter_boundaries(module, stack)
    result['nested_returns'] = sum(nested(module, stack, depth, prefix)
                                   for depth in (1, 7, 31)
                                   for prefix in (16, 257, 4096))
    length, actions = boundary(module, stack, ['1'*4096]*16, [0]*16, '', 65535,
                               ['']*17, [0]*17)
    result['distance_4096_each_role'] = {
        'binary_frame_symbols': length, 'unary_frame_symbols': 16*4096+35,
        'saved_frame_symbols': 16*4096+35-length, 'matched_actions': actions,
    }
    result['negative_controls'] = negative_controls(module, stack)
    result['source_sha256'] = {
        name: hashlib.sha256((PACKAGE/name).read_bytes()).hexdigest()
        for name in ('binary_stack.py', 'verify.py', 'PROOF.md')}
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        require(result == json.loads((PACKAGE/'RESULT.json').read_text()),
                'generated source-bound receipt')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
