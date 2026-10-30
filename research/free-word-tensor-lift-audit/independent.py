"""Independent one-output-at-a-time pullback over Q[F_72].

No implementation or normalizer from the retained source is imported/executed.
The literal word format and endpoint contract were read from those sources;
this independence is of implementation, not independence of source provenance.
Only neighboring inverse letters reduce; no commutativity, torsion, matrix
minimal polynomial, finite-character identity, or scalar operator evaluation.
Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    rows = json.loads((HERE / 'SOURCE-PINS.json').read_bytes())
    for row in rows:
        path = HERE / 'source' / row['path']
        require(not path.is_symlink(), 'source symlink')
        raw = path.read_bytes()
        require(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'],
                'source content changed: ' + row['path'])
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
                'source Git blob changed: ' + row['path'])


def reduce_right(word, letters):
    stack = list(word)
    for letter in letters:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def accumulate(target, source, scalar, suffix=()):
    # Source and target may be the same dictionary only on malformed words;
    # taking a snapshot keeps this helper's algebra deterministic in that case.
    for word, value in list(source.items()):
        key = reduce_right(word, suffix)
        result = target.get(key, Q(0)) + scalar * value
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def literal(word, dual):
    sequence = []
    for correction in word['initial_corrections']:
        target, source = correction['target'], correction['source']
        coeff = Q(correction['coefficient'])
        operator = tuple(correction['operator_word'])
        if dual:
            target, source, coeff = source, target, -coeff
            operator = tuple(-o for o in reversed(operator))
        sequence.append(('add', target, source, coeff, operator))
    sections = list(word['precondition']) + list(word['compensation']) + list(word['A']) + list(word['cut'])
    positions = {}
    for index, warp in enumerate(word['warps'], 1):
        positions.setdefault(warp[0], []).append(('warp', warp[1], index))
    for i in range(len(word['B']) + 1):
        sections += positions.get(i, ())
        if i < len(word['B']):
            sections.append(word['B'][i])
    sections += word['restore'] + word['cleanup']
    for gate in sections:
        if gate[0] == 'add':
            dst, src, c = gate[1], gate[2], Q(gate[3], gate[4])
            if dual:
                dst, src, c = src, dst, -c
            sequence.append(('add', dst, src, c, ()))
        elif gate[0] == 'scale':
            c = Q(gate[2], gate[3])
            sequence.append(('scale', gate[1], 1 / c if dual else c))
        elif gate[0] == 'warp':
            # Distinct dual symbols are abstract generators D_k=G_k^(-T).
            # The same numbering is harmless because the two passes are separate.
            sequence.append(('warp', gate[1], gate[2]))
        else:
            raise ValueError('unrecognized literal primitive')
    return sequence


def pullback(sequence, output):
    values = {output: {(): Q(1)}}
    for event in reversed(sequence):
        kind, target = event[:2]
        current = values.get(target)
        if not current:
            continue
        if kind == 'add':
            _, _, source, coefficient, suffix = event
            accumulate(values.setdefault(source, {}), current, coefficient, suffix)
        elif kind == 'scale':
            values[target] = {word: event[2] * value for word, value in current.items()}
        else:
            moved = {}
            accumulate(moved, current, Q(1), (event[2],))
            values[target] = moved
    return {register: polynomial for register, polynomial in values.items() if polynomial}


def check_word(word, name, dual=False):
    regs = sorted((set(range(704)) - set(word['removed'])) | {704 + int(r) for r in word['helper_final']})
    require(len(regs) == 723, '723 independent inputs/outputs')
    sequence = literal(word, dual)
    total_terms = 0
    for register in regs:
        expected = {register: {(): Q(1)}}
        if not dual and 112 <= register < 224:
            expected[register - 112] = {(): Q(1)}
        if dual and register < 112:
            expected[register + 112] = {(): Q(-1)}
        got = pullback(sequence, register)
        require(got == expected, 'formal pullback mismatch: %s/%s/%s' % (name, dual, register))
        total_terms += sum(len(polynomial) for polynomial in got.values())
    require(total_terms == 835, 'complete endpoint term census')
    return {'outputs': len(regs), 'independent_inputs': len(regs), 'nonzero_terms': total_terms,
            'nonempty_surviving_words': 0, 'literal_events': len(sequence), 'dual': dual}


def controls():
    require(reduce_right((1, 2), (-2, -1)) == (), 'inverse stack positive')
    require(reduce_right((1, 2), (-1, -2)) != (), 'commutator must not cancel')
    require(reduce_right((1,), (1, 1, 1)) == (1, 1, 1, 1), 'fourth power must not vanish')
    polynomial = {}; accumulate(polynomial, {(): Q(1)}, Q(1), (1,)); accumulate(polynomial, {(): Q(1)}, Q(-1))
    require(polynomial == {(1,): Q(1), (): Q(-1)}, 'G-I stays two distinct terms')
    return {'adjacent_inverse': True, 'commutative_collapse_rejected': True,
            'finite_order_collapse_rejected': True, 'difference_terms_remain_separate': True}


def compute():
    authenticate()
    rows = {}
    for name in ('THREE-base', 'THREE-extra', 'FOUR-base', 'FOUR-extra'):
        word = json.loads(gzip.decompress((HERE / 'source' / 'inputs' / (name + '.json.gz')).read_bytes()))
        rows[name] = [check_word(word, name, dual) for dual in (False, True)]
    return {'schema_version': 1, 'status': 'PASS_INDEPENDENT_FORMAL_PULLBACK',
            'providers': rows, 'controls': controls()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = compute()
    raw = json.dumps(result, sort_keys=True, indent=2) + '\n'
    path = HERE / 'INDEPENDENT.json'
    if args.write:
        require(not path.exists(), 'refuse to overwrite frozen independent result')
        path.write_text(raw)
    else:
        require(path.read_text() == raw, 'independent frozen result differs')
    print(result['status'])


if __name__ == '__main__':
    main()
