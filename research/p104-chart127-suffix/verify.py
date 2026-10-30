"""Source-bound exact checks for one new scalar circuit. Apache-2.0.

Produced by Nick Petalas. Integer matrix replay is separate from synthesis.
Ali Romman's authenticated complete-word interpreter is reused for the new word.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from synthesize import (FRAME, MAX_EVENTS, MAX_ROLES, START, STOP, inverse,
                        matrix, require, roles_of, synthesize, unit)

ROOT = HERE.parents[1]
WORD = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'
CHECKER = 'research/p104-unread-path-resynthesis/local.py'


def digest(value):
    return sha256(json.dumps(value, sort_keys=True,
                             separators=(',', ':')).encode()).hexdigest()


def authenticate(raw, expected):
    require(sha256(raw).hexdigest() == expected, 'Exact source bytes')
    return raw


def inputs():
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    data = {}
    for item in sources['files']:
        if item['usage'] == 'input':
            data[item['path']] = authenticate((ROOT / item['path']).read_bytes(),
                                               item['sha256'])
    require(set(data) == {WORD, CHECKER}, 'Complete scientific input inventory')
    return data


def alphabet(program, roles):
    require(0 < len(program) <= MAX_EVENTS and len(roles) <= MAX_ROLES,
            'Bounded circuit and roles')
    for e in program:
        require(e[0] in ('ADD', 'SCALE'), 'Scalar alphabet')
        require(len(e) == (5 if e[0] == 'ADD' else 4), 'Scalar arity')
        require(e[-1] == FRAME and e[1] in roles, 'Available fixed chart')
        q = Fraction(e[-2])
        require(q and q.denominator & (q.denominator - 1) == 0,
                'Nonzero dyadic coefficient')
        require(abs(q.numerator).bit_length() <= 16
                and q.denominator.bit_length() <= 16, 'Coefficient capacity')
        if e[0] == 'SCALE':
            require(unit(q), 'Dyadic-unit SCALE')
        else:
            require(e[2] in roles and e[2] != e[1], 'Available distinct source')


def dense(program, roles):
    """Compute every coefficient using integer rows and binary exponents."""
    n = len(roles)
    positions = {r: i for i, r in enumerate(roles)}
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    levels = [0] * n
    peak = Fraction(1)
    for e in program:
        r = positions[e[1]]
        q = Fraction(e[-2])
        shift = q.denominator.bit_length() - 1
        if e[0] == 'SCALE':
            rows[r] = [q.numerator * x for x in rows[r]]
            levels[r] += shift
        else:
            s = positions[e[2]]
            exponent = max(levels[r], levels[s] + shift)
            a = 1 << (exponent - levels[r])
            b = q.numerator << (exponent - levels[s] - shift)
            rows[r] = [a * x + b * y for x, y in zip(rows[r], rows[s])]
            levels[r] = exponent
        # The full row cannot be zero, since each accepted gate is invertible.
        common = min((abs(x) & -abs(x)).bit_length() - 1
                     for x in rows[r] if x)
        reduction = min(common, levels[r])
        if reduction:
            rows[r] = [x >> reduction for x in rows[r]]
            levels[r] -= reduction
        peak = max(peak, Fraction(sum(map(abs, rows[r])), 1 << levels[r]))
    return {'rows': rows, 'levels': levels}, str(peak)


def allowance(program):
    total = 0
    for e in program:
        q = Fraction(e[-2])
        n, d = abs(q.numerator), q.denominator
        if e[0] == 'SCALE':
            total += 2 * (abs(n.bit_length() - d.bit_length()) + int(q < 0))
        else:
            total += 2 * (3 + n.bit_length() - 1 + n.bit_count()
                          + d.bit_length() - 1)
    return total


def reject(function, *args):
    try:
        function(*args)
    except (ValueError, KeyError):
        return
    raise ValueError('A negative control was accepted')


def fixtures():
    fixture = [['ADD', 0, 1, '1/2', FRAME], ['SCALE', 1, '-2', FRAME],
               ['ADD', 1, 0, '3/4', FRAME], ['SCALE', 0, '1/4', FRAME]]
    replacement, _ = synthesize(fixture)
    require(dense(fixture, [0, 1])[0] == dense(replacement, [0, 1])[0],
            'Hand-sized dyadic positive control')
    require(matrix(fixture) == {0: {0: Fraction(1, 4), 1: Fraction(1, 8)},
                                1: {0: Fraction(3, 4), 1: Fraction(-13, 8)}},
            'Hand-computed matrix')
    for bad in ([['ADD', 0, 0, '1', FRAME]],
                [['ADD', 0, 2, '1', FRAME]],
                [['ADD', 0, 1, '1/3', FRAME]],
                [['SCALE', 0, '3', FRAME]],
                [['SCALE', 0, '0', FRAME]],
                [['SCALE', 0, '2', FRAME + 1]]):
        reject(alphabet, bad, [0, 1])
    return 6


def controls(original, replacement, roles, expected, source_bytes):
    mutated = [e.copy() for e in replacement]
    mutated[0][-2] = str(-Fraction(mutated[0][-2]))
    require(dense(mutated, roles)[0] != expected, 'A sign fault must change the map')
    index = next(i for i, e in enumerate(replacement) if e[0] == 'SCALE'
                 and Fraction(e[-2]) != 1)
    require(dense(replacement[:index] + replacement[index + 1:], roles)[0]
            != expected, 'A missing scale must change the map')
    bad = [replacement[0].copy()]
    bad[0][-1] += 1
    reject(alphabet, bad, roles)
    require(dense(inverse(original), roles)[0] ==
            dense(inverse(replacement), roles)[0], 'Reverse circuit equality')
    for raw in source_bytes.values():
        reject(authenticate, bytes([raw[0] ^ 1]) + raw[1:], sha256(raw).hexdigest())
    return 5


def whole_word(word, replacement, raw_checker):
    module = ModuleType('chart127_retained_interpreter')
    module.__file__ = str(ROOT / CHECKER)
    exec(compile(raw_checker, module.__file__, 'exec'), module.__dict__)
    candidate = dict(word)
    candidate['program'] = word['program'][:START] + replacement + word['program'][STOP:]
    old_other = [e for e in word['program'] if e[0] not in ('ADD', 'SCALE')]
    new_other = [e for e in candidate['program'] if e[0] not in ('ADD', 'SCALE')]
    require(old_other == new_other, 'Ordered non-scalar events are unchanged')
    result = module.replay(candidate)
    require(result['real_scalar_allowance'] == 186918, 'Complete scalar allowance')
    require(result['endpoint_coefficients'] == 799 * 799, 'All endpoint coefficients')
    require((result['public_inputs'], result['owned_fields'], result['owned_lifetimes'],
             result['peak_owned_fields']) == (770, 29, 31, 13), 'Complete storage inventory')
    return candidate, result


def run():
    source_bytes = inputs()
    word = json.loads(gzip.decompress(source_bytes[WORD]))
    require(len(word['program']) == 22803, 'Fixed selected word size')
    require(word['program'][STOP] == ['ADD', 533, 453, '2', 245],
            'The foreign-chart observation boundary is retained')
    original = word['program'][START:STOP]
    roles = roles_of(original)
    replacement, discovery = synthesize(original)
    alphabet(original, roles)
    alphabet(replacement, roles)
    before, old_peak = dense(original, roles)
    after, new_peak = dense(replacement, roles)
    require(before == after, 'Every arbitrary-entry matrix coefficient agrees')
    require(digest(after) == '746cc644611fbc4be59878f9726669b58391378255ffdd2ba52bfb1da595385a',
            'Frozen complete matrix')
    require(digest(replacement) == 'ed9afcb5d55fe74f4306d8bc8928f59f0ee8201882597672013c90f4cb11c896',
            'Frozen first improving circuit')
    require((len(original), len(replacement), len(roles)) == (2970, 2851, 545),
            'Fixed circuit dimensions')
    costs = allowance(original), allowance(replacement)
    require(costs == (25988, 23478), 'Complete local scalar allowances')
    candidate, complete = whole_word(word, replacement, source_bytes[CHECKER])
    control_count = fixtures() + controls(original, replacement, roles, before, source_bytes)
    report = {'status': 'PASS_P104_CHART127_SUFFIX', 'interval': [START, STOP],
              'frame': FRAME, 'discovery': discovery,
              'events': [len(original), len(replacement)], 'allowance': list(costs),
              'ops_before': dict(Counter(e[0] for e in original)),
              'ops_after': dict(Counter(e[0] for e in replacement)),
              'matrix_coefficients': len(roles) ** 2, 'matrix_sha256': digest(before),
              'maximum_local_row_l1': [old_peak, new_peak],
              'replacement_sha256': digest(replacement), 'word_sha256': digest(candidate),
              'complete_events': len(candidate['program']), 'complete_replay': complete,
              'rejection_controls': control_count,
              'source_sha256': {p: sha256(raw).hexdigest() for p, raw in source_bytes.items()},
              'package_sha256': {p.name: sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(HERE.iterdir()) if p.is_file()}}
    return report, candidate


def write_external(path, payload):
    require(path.is_absolute() and not path.resolve().is_relative_to(ROOT),
            'An absolute output outside the checkout is required')
    with path.open('xb') as stream:
        stream.write(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--emit-word', type=Path)
    args = parser.parse_args()
    report, candidate = run()
    if args.receipt:
        write_external(args.receipt, (json.dumps(report, sort_keys=True, indent=2) + '\n').encode())
    if args.emit_word:
        write_external(args.emit_word, (json.dumps(candidate, sort_keys=True,
                                                  separators=(',', ':')) + '\n').encode())
    print(report['status'], 'events=2970->2851 allowance=25988->23478',
          'matrix=545x545 full_word=22684 controls=' + str(report['rejection_controls']))


if __name__ == '__main__':
    main()
