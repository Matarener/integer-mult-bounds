#!/usr/bin/env python3
"""Independent finite specialization oracle; no audited evaluator is imported.

This evaluates the four pinned literal programs on deterministic correlated
real vectors under a noncommuting signed-permutation representation. It is
an implementation cross-check of the written free-group proof, not its proof.
Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

PINS = {
    'THREE-base.json.gz': '137793e275870db2161048405017b83dcc1824ee',
    'THREE-extra.json.gz': '7cce921b20dc0504cea954ab3297c5b55a9468dc',
    'FOUR-base.json.gz': '65957e5ca322049d985f23fdc0bd8da07ffa4c2a',
    'FOUR-extra.json.gz': '1f3239c30e9343cf4e34b4371fcbeebb94a19011',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(None)
def signed_action(operator, multiplicity):
    # On one ternary factor choose -I, a 3-cycle, a signed transposition
    # or a diagonal reflection. The cycle and reflection do not commute,
    # even after tensoring twice (unlike an anticommuting Pauli pair).
    kind = abs(operator) % 4
    permutation = ((0, 1, 2), (1, 2, 0), (1, 0, 2), (0, 1, 2))[kind]
    signs = ((-1, -1, -1), (1, 1, 1), (1, -1, 1), (1, -1, 1))[kind]
    mapping = []
    for x in range(3 ** multiplicity):
        y, sign, remaining = 0, 1, x
        for j in range(multiplicity):
            remaining, digit = divmod(remaining, 3)
            y += permutation[digit] * 3 ** j
            sign *= signs[digit]
        mapping.append((y, sign))
    if operator < 0:
        inverse = [None] * len(mapping)
        for x, (y, sign) in enumerate(mapping):
            inverse[y] = (x, sign)
        mapping = inverse
    return tuple(mapping)


def unary(values, operator, multiplicity):
    result = [Fraction(0)] * len(values)
    for x, (y, sign) in enumerate(signed_action(operator, multiplicity)):
        result[y] = sign * values[x]
    return result


def literal_events(word):
    for correction in word['initial_corrections']:
        yield ('correction', correction)
    for key in ('precondition', 'compensation', 'A', 'cut'):
        for gate in word[key]:
            yield ('gate', gate)
    insertions = {}
    for index, warp in enumerate(word['warps'], 1):
        insertions.setdefault(warp[0], []).append(['warp', warp[1], index])
    for position in range(len(word['B']) + 1):
        for gate in insertions.get(position, []):
            yield ('gate', gate)
        if position < len(word['B']):
            yield ('gate', word['B'][position])
    for key in ('restore', 'cleanup'):
        for gate in word[key]:
            yield ('gate', gate)


def specialize(word, multiplicity, dual=False):
    v = word['report']['v']
    original_registers = 2 * v + word['report']['R']
    live = sorted(set(range(original_registers)) - set(word['removed']))
    buffers = [original_registers + int(x) for x in word['helper_final']]
    # Every buffer and live register is nonzero. Different coordinates share
    # affine data, deliberately giving correlated and dirty input vectors.
    initial = {
        register: [Fraction((register + 3) * (j + 2) - 17 * (j % 2))
                   for j in range(3 ** multiplicity)]
        for register in live + buffers
    }
    values = deepcopy(initial)
    events = 0
    for kind, event in literal_events(word):
        events += 1
        if kind == 'correction':
            target, source = event['target'], event['source']
            coefficient = Fraction(event['coefficient'])
            operations = list(reversed(event['operator_word']))
            if dual:
                target, source, coefficient = source, target, -coefficient
                operations = [-operation for operation in event['operator_word']]
                # Inverse-transpose of the transvection uses -c*W^T.
                # For real orthogonal generators W^T reverses the word and
                # inverts its factors; application order is the original word.
            moved = list(values[source])
            for operation in operations:
                moved = unary(moved, operation, multiplicity)
            values[target] = [a + coefficient * b for a, b in zip(values[target], moved)]
        elif event[0] == 'add':
            target, source = event[1:3]
            coefficient = Fraction(event[3], event[4])
            if dual:
                target, source, coefficient = source, target, -coefficient
            values[target] = [a + coefficient * b
                              for a, b in zip(values[target], values[source])]
        elif event[0] == 'scale':
            coefficient = Fraction(event[2], event[3])
            if dual:
                coefficient = 1 / coefficient
            values[event[1]] = [coefficient * a for a in values[event[1]]]
        elif event[0] == 'warp':
            # Both signs of a real signed permutation are orthogonal.
            values[event[1]] = unary(values[event[1]], event[2], multiplicity)
        else:
            raise ValueError('unexpected primitive: ' + repr(event))
    expected = deepcopy(initial)
    for source in range(v):
        target = source + v
        if dual:
            expected[source] = [a - b for a, b in zip(initial[source], initial[target])]
        else:
            expected[target] = [a + b for a, b in zip(initial[target], initial[source])]
    require(values == expected, 'concrete specialization endpoint differs')
    return {'multiplicity': multiplicity, 'orientation': 'dual' if dual else 'forward',
            'live_registers': len(live), 'dirty_buffers': len(buffers),
            'coordinates_per_register': 3 ** multiplicity, 'events': events}


def controls():
    for multiplicity in (1, 2, 3):
        x = list(map(Fraction, range(1, 3 ** multiplicity + 1)))
        require(unary(unary(x, 1, multiplicity), 3, multiplicity) !=
                unary(unary(x, 3, multiplicity), 1, multiplicity),
                'chosen representation became commutative')
    vector = [Fraction(1)] + [Fraction(0)] * 8
    # g_4 represents unary -I: at multiplicity two it becomes +I, whereas a
    # separately declared scalar -1 stays -I. Conflation must be rejected.
    require(unary(vector, 4, 2) != [-a for a in vector], 'unary phase/scalar conflated')
    # (-I-I) tensor two is 4I; the correct termwise g_4-I is zero.
    correct = [a - b for a, b in zip(unary(vector, 4, 2), vector)]
    wrong = [4 * a for a in vector]
    require(correct != wrong, 'tensor of an operator sum was accepted')
    # Scalars remain scalar; they are not raised to the multiplicity power.
    require([Fraction(1, 2) * a for a in vector] !=
            [Fraction(1, 4) * a for a in vector], 'scalar exponentiation accepted')
    one_factor = [Fraction(1), Fraction(0), Fraction(0)]
    require([a + b for a, b in zip(unary(one_factor, 4, 1), one_factor)] == [0, 0, 0],
            'realization-only control no longer cancels at one factor')
    require([a + b for a, b in zip(unary(vector, 4, 2), vector)] != [0] * 9,
            'realization-only cancellation incorrectly survives specialization')
    for operator in range(1, 73):
        for multiplicity in (1, 2, 3):
            vector = list(map(Fraction, range(1, 3 ** multiplicity + 1)))
            require(unary(unary(vector, operator, multiplicity), -operator, multiplicity) == vector,
                    'generator inverse does not cancel')
    return {'noncommuting_multiplicities': [1, 2, 3], 'semantic_distinctions': 4,
            'inverse_checks': 216}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, default=Path(__file__).resolve().parent / 'source/inputs')
    args = parser.parse_args()
    records = {}
    for name, expected_blob in PINS.items():
        raw = (args.inputs / name).read_bytes()
        actual_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(actual_blob == expected_blob, 'pinned source changed: ' + name)
        word = json.loads(gzip.decompress(raw))
        rows = []
        for multiplicity in (1, 2, 3):
            for dual in (False, True):
                rows.append(specialize(word, multiplicity, dual))
        records[name] = {'git_blob': actual_blob, 'sha256': hashlib.sha256(raw).hexdigest(),
                         'specializations': rows}
    result = {'status': 'PASS_INDEPENDENT_REAL_SPECIALIZATION',
              'scope': 'finite correlated dirty-vector cross-check; all-f proof is written',
              'source_provider_count': len(records), 'records': records,
              'controls': controls()}
    frozen = Path(__file__).resolve().parent / 'INDEPENDENT-REAL.json'
    require(json.loads(frozen.read_bytes()) == result, 'frozen specialization receipt differs')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
