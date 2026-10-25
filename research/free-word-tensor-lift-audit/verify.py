"""Source-bound formal-operator premise and noncommuting tensor checks.

New audit: OpenAI Codex assistance. Retained source interpreter is credited in
source/NOTICE.md; executing it is a source replay, not an independent engine.
Only standard library; no native/owner/analytic supplier integration is claimed.
Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import gzip
import hashlib
import json
import types

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'source'
MODULUS = 101


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_bytes())
    need(len(pins) == 10, 'complete source inventory')
    for row in pins:
        path = SOURCE / row['path']
        need(not path.is_symlink(), 'source symlink')
        raw = path.read_bytes()
        need(len(raw) == row['bytes'], 'source length: ' + row['path'])
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['path'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
             'source Git blob: ' + row['path'])
    return pins


def retained_module(name, rel):
    module = types.ModuleType(name)
    path = SOURCE / rel
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def load_word(name):
    return json.loads(gzip.decompress((SOURCE / 'inputs' / (name + '.json.gz')).read_bytes()))


def scalar(value):
    q = Fraction(value)
    need(q.denominator % MODULUS, 'scalar denominator divisible by field characteristic')
    return q.numerator * pow(q.denominator, -1, MODULUS) % MODULUS


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def multiply(a, b):
    need(len(a[0]) == len(b), 'matrix shape')
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) % MODULUS
                       for j in range(len(b[0]))) for i in range(len(a)))


def tensor(a, b):
    return tuple(tuple(a[i][j] * b[k][l] % MODULUS for j in range(len(a[0]))
                       for l in range(len(b[0]))) for i in range(len(a)) for k in range(len(b)))


def tensor_power(a, f):
    need(type(f) is int and 1 <= f <= 3, 'finite tensor fixture range')
    result = ((1,),)
    for _ in range(f):
        result = tensor(result, a)
    return result


def inverse2(a):
    determinant = (a[0][0] * a[1][1] - a[0][1] * a[1][0]) % MODULUS
    need(determinant, 'invertible generator')
    c = pow(determinant, -1, MODULUS)
    return ((c * a[1][1] % MODULUS, -c * a[0][1] % MODULUS),
            (-c * a[1][0] % MODULUS, c * a[0][0] % MODULUS))


def transpose(a):
    return tuple(zip(*a))


def generator(k):
    # det=1. Distinct first-row entries give 72 distinct source generators.
    a, b = k % MODULUS, (k * k + 3) % MODULUS
    return ((1, a), (b, (1 + a * b) % MODULUS))


def action(a, vector):
    return tuple(sum(x * y for x, y in zip(row, vector)) % MODULUS for row in a)


def axpy(a, b, c):
    return tuple((x + c * y) % MODULUS for x, y in zip(a, b))


def events(word):
    # This event reconstruction is written independently of the retained program
    # helper. Operator numbers are chronological indices in the literal word.
    for correction in word['initial_corrections']:
        yield ('correction', correction)
    for section in ('precondition', 'compensation', 'A', 'cut'):
        yield from word[section]
    at = {}
    for number, record in enumerate(word['warps'], 1):
        at.setdefault(record[0], []).append(('warp', record[1], number))
    for position in range(len(word['B']) + 1):
        yield from at.get(position, ())
        if position < len(word['B']):
            yield word['B'][position]
    yield from word['restore']
    yield from word['cleanup']


def direct_replay(word, f, dual=False, *, scale_mode='scalar', correction_mode='word'):
    dimension = 2 ** f
    live = [r for r in range(704) if r not in set(word['removed'])]
    registers = live + [704 + int(r) for r in word['helper_final']]
    need(len(set(registers)) == 723, 'complete direct fixture register inventory')
    initial = {r: tuple((17 * r * r + (3 * r + 11) * j + 7 * j * j + 1) % MODULUS
                        for j in range(dimension)) for r in registers}
    values = dict(initial)
    maps = {}
    for k in range(1, 1 + len(word['warps'])):
        base = transpose(inverse2(generator(k))) if dual else generator(k)
        maps[k] = tensor_power(base, f)
        maps[-k] = tensor_power(inverse2(base), f)
    for gate in events(word):
        kind = gate[0]
        if kind == 'add':
            target, source = gate[1:3]
            c = scalar(Fraction(gate[3], gate[4]))
            if dual:
                target, source, c = source, target, -c
            values[target] = axpy(values[target], values[source], c)
        elif kind == 'scale':
            c = scalar(Fraction(gate[2], gate[3]))
            if dual:
                c = pow(c, -1, MODULUS)
            if scale_mode == 'tensorized':
                c = pow(c, f, MODULUS)
            values[gate[1]] = tuple(c * value % MODULUS for value in values[gate[1]])
        elif kind == 'warp':
            values[gate[1]] = action(maps[gate[2]], values[gate[1]])
        elif kind == 'correction':
            correction = gate[1]
            target, source = correction['target'], correction['source']
            c = scalar(correction['coefficient'])
            ops = list(reversed(correction['operator_word']))
            if dual:
                target, source, c = source, target, -c
                ops = [-k for k in correction['operator_word']]
            result = values[source]
            for k in ops:
                result = action(maps[k], result)
            if correction_mode == 'erase_generator':
                result = values[source]
            values[target] = axpy(values[target], result, c)
        else:
            raise ValueError('unrecognized literal gate: ' + str(kind))
    expected = dict(initial)
    for r in range(112):
        if dual:
            expected[r] = axpy(initial[r], initial[r + 112], -1)
        else:
            expected[r + 112] = axpy(initial[r + 112], initial[r], 1)
    mismatches = [r for r in registers if values[r] != expected[r]]
    return {'registers': len(registers), 'tensor_multiplicity': f, 'component_dimension': dimension,
            'orientation': 'dual' if dual else 'forward', 'mismatching_registers': mismatches}


def matrix_subtract(a, b):
    return tuple(tuple((x - y) % MODULUS for x, y in zip(ar, br)) for ar, br in zip(a, b))


def controls():
    a, b = generator(1), generator(2)
    need(multiply(a, b) != multiply(b, a), 'noncommuting fixture')
    need(len({generator(k) for k in range(1, 73)}) == 72, 'distinct 72-generator fixture')
    I = identity(2)
    # The lift is the linear extension of a map on GROUP elements, never the
    # tensor power of a sum/difference or of a scalar times an operator.
    termwise = matrix_subtract(tensor(a, a), identity(4))
    whole_difference = tensor(matrix_subtract(a, I), matrix_subtract(a, I))
    need(termwise != whole_difference, 'whole-difference tensorization must be rejected')
    c = 2
    scalar_operator = tuple(tuple(c * x % MODULUS for x in row) for row in tensor(a, a))
    wrong_scalar = tensor(tuple(tuple(c * x % MODULUS for x in row) for row in a),
                          tuple(tuple(c * x % MODULUS for x in row) for row in a))
    need(scalar_operator != wrong_scalar, 'scalar tensorization must be rejected')
    need(multiply(tensor(a, a), tensor(inverse2(a), inverse2(a))) == identity(4), 'lifted inverse')
    need(tensor(multiply(a, b), multiply(a, b)) == multiply(tensor(a, a), tensor(b, b)), 'lifted multiplication')
    word = load_word('FOUR-base')
    missing = direct_replay(word, 2, correction_mode='erase_generator')
    need(missing['mismatching_registers'], 'erased correction generator was accepted')
    scaled = direct_replay(word, 2, scale_mode='tensorized')
    need(scaled['mismatching_registers'], 'tensorized role scalar was accepted')
    return {'noncommuting_generators': True, 'distinct_generators': 72,
            'whole_difference_tensorization_rejected': True, 'whole_scalar_tensorization_rejected': True,
            'inverse_compatibility': True, 'product_compatibility': True,
            'erased_correction_generator_mismatches': missing['mismatching_registers'],
            'tensorized_role_scalar_mismatches': scaled['mismatching_registers']}


def compute():
    authenticate()
    C = retained_module('credited_source_core', 'vendor/audit_core.py')
    A = retained_module('credited_source_semantics', 'vendor/audit_verify.py')
    rows = {}
    for provider in ('THREE-base', 'THREE-extra', 'FOUR-base', 'FOUR-extra'):
        word = load_word(provider)
        source_check = A.semantics(C, word)
        direct = [direct_replay(word, f, dual) for f in (1, 2, 3) for dual in (False, True)]
        need(all(not row['mismatching_registers'] for row in direct), 'direct tensor endpoint')
        rows[provider] = {'source_free_group_replay': source_check,
                          'direct_noncommuting_field_fixtures': direct,
                          'warp_generators': len(word['warps']),
                          'initial_correction_terms': len(word['initial_corrections']),
                          'literal_event_count': sum(1 for _ in events(word))}
    return {'schema_version': 1, 'status': 'PASS_SOURCE_BOUND_FREE_OPERATOR_LIFT_AUDIT',
            'new_kappa': False, 'full_multiplication_theorem': False, 'encoded_execution': False,
            'providers': rows, 'controls': controls()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = compute()
    raw = json.dumps(result, sort_keys=True, indent=2) + '\n'
    output = HERE / 'RESULT.json'
    if args.write:
        need(not output.exists(), 'refuse to overwrite frozen result')
        output.write_text(raw)
    else:
        need(output.read_text() == raw, 'frozen result differs')
    print(result['status'])


if __name__ == '__main__':
    main()
