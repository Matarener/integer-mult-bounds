#!/usr/bin/env python3
"""Exact two-stage Walsh/shear check; Jerry Chen, OpenAI Codex; Apache-2.0.

No predecessor implementation is imported. The integer butterfly interpreter
and Fraction/dense-matrix oracle below are separately represented. The universal
claim rests on PROOF.md plus the fixed-source witness certificate, not sampling.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
PAIRS = tuple((t, s) for t in range(4) for s in range(4) if t != s)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def half_even(n):
    """Nearest-even n/2, with floor quotient valid for both signs."""
    q, r = divmod(n, 2)
    return q + (r & (q & 1))


def butterfly_numerators(x, axis):
    out = list(x)
    for i in range(4):
        if not i & (1 << axis):
            j = i ^ (1 << axis)
            out[i], out[j] = x[i] + x[j], x[i] - x[j]
    return out


def literal(x, t, s, m, *, axis=0, fault=None):
    """Return rounded output, four-times exact output, first stored values."""
    require(len(x) == 4 and all(type(v) is int for v in x), 'integer-grid input')
    require(type(m) is int, 'integer shear coefficient')
    require((t, s) in PAIRS and axis in (0, 1), 'distinct valid ports/axes')
    first = butterfly_numerators(x, axis)
    quantize = (lambda n: n // 2) if fault == 'floor-ties' else half_even
    stored = [quantize(n) for n in first]
    changed = stored.copy()
    if fault != 'omit-shear':
        if fault == 'reverse-shear':
            changed[s] += m * stored[t]
        else:
            changed[t] += m * stored[s]
    second_axis = axis if fault == 'repeat-axis' else 1 - axis
    numerators = butterfly_numerators(changed, second_axis)
    if fault == 'wrong-difference':
        numerators[1 << second_axis] *= -1
    out = [quantize(n) for n in numerators]
    exact_first = first.copy()
    exact_first[t] += m * first[s]
    exact4 = butterfly_numerators(exact_first, 1 - axis)
    if fault == 'omit-exact-shear':
        exact4 = butterfly_numerators(first, 1 - axis)
    if fault == 'single-final-round':
        out = [round(Q(v, 4)) for v in exact4]
    return tuple(out), tuple(exact4), tuple(stored)


# Independent representation: literal dense matrices, exact rational rounding.
M0 = ((1, 1, 0, 0), (1, -1, 0, 0), (0, 0, 1, 1), (0, 0, 1, -1))
M1 = ((1, 0, 1, 0), (0, 1, 0, 1), (1, 0, -1, 0), (0, 1, 0, -1))


def mv(matrix, vector):
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in matrix)


def mm(a, b):
    columns = tuple(zip(*b))
    return tuple(tuple(sum(x * y for x, y in zip(row, col)) for col in columns)
                 for row in a)


def dense_data(t, s, m, axis=0):
    shear = [[int(i == j) for j in range(4)] for i in range(4)]
    shear[t][s] = m
    first, second = (M0, M1) if axis == 0 else (M1, M0)
    return first, shear, second, mm(second, mm(shear, first))


def oracle(x, data):
    first, shear, second, exact4 = data
    a = tuple(round(Q(v, 2)) for v in mv(first, x))
    b = mv(shear, a)
    out = tuple(round(Q(v, 2)) for v in mv(second, b))
    return out, mv(exact4, x), a


def authenticate_context():
    source = json.loads((HERE / 'SOURCES.json').read_text())
    for row in source['context_documents']:
        data = (HERE / row['local_path']).read_bytes()
        require(sha256(data).hexdigest() == row['sha256'], 'context source hash')
        header = b'blob ' + str(len(data)).encode() + b'\0'
        from hashlib import sha1
        require(sha1(header + data).hexdigest() == row['git_blob'], 'context Git blob')
    return len(source['context_documents'])


def check_witnesses(rows):
    require(type(rows) is list and len(rows) == 24, 'witness count')
    seen = set()
    for row in rows:
        require(type(row) is list and len(row) == 8
                and all(type(v) is int for v in row), 'witness row type')
        t, s, c, j, *x = row
        require((t, s) in PAIRS and c in (-1, 1) and 0 <= j < 4, 'witness key')
        require(all(v in (-1, 0, 1) for v in x), 'small witness input')
        require((t, s, c) not in seen, 'duplicate witness')
        seen.add((t, s, c))
        zero = oracle(x, dense_data(t, s, 0))
        one = oracle(x, dense_data(t, s, 1))
        require(zero[2][s] == 0, 'rounded shear source must vanish')
        require(4 * zero[0][j] - zero[1][j] == 3, 'witness intercept')
        require(zero[1][j] - one[1][j] == c, 'witness slope')
        # With rounded source zero, the rounded trajectory is independent of m;
        # the exact matrix is affine in m. These two identities suffice for all m.
        for m in (0, c, c * 83, c * (2**200 + 1)):
            got = literal(x, t, s, m)
            other = oracle(x, dense_data(t, s, m))
            require(got == other, 'witness engines disagree')
            require(4 * got[0][j] - got[1][j] == 3 + c * m, 'witness line')
    require(seen == {(t, s, c) for t, s in PAIRS for c in (-1, 1)}, 'witness coverage')


def census():
    """Complete input residues and coefficient residues; compare EVERY output."""
    counts = 0
    transcript = sha256()
    for t, s in PAIRS:
        for r in range(4):
            data = dense_data(t, s, r)
            # For m=r+4q, four-times error is slope*m+intercept.
            maxima = {-1: -10**9, 0: -10**9, 1: -10**9}
            minima = {-1: 10**9, 0: 10**9, 1: 10**9}
            for x in product(range(8), repeat=4):
                got = literal(x, t, s, r)
                other = oracle(x, data)
                require(got == other, 'residue engines disagree')
                out, exact4, stored = got
                first = butterfly_numerators(x, 0)
                d = [0] * 4
                d[t] = 2 * stored[s] - first[s]
                slopes = butterfly_numerators(d, 1)
                for j, c in enumerate(slopes):
                    require(c in (-1, 0, 1), 'coefficient slope')
                    a = 4 * out[j] - exact4[j] - c * r
                    maxima[c] = max(maxima[c], a)
                    minima[c] = min(minima[c], a)
                transcript.update(json.dumps(got, separators=(',', ':')).encode() + b'\n')
                counts += 1
            require(maxima == {-1: 3, 0: 3, 1: 3}, 'upper affine envelope')
            require(minima == {-1: -3, 0: -3, 1: -3}, 'lower affine envelope')
    return counts, transcript.hexdigest()


def shifted_controls():
    rng = random.Random(83)
    count = 0
    for _ in range(768):
        t, s = rng.choice(PAIRS)
        m = rng.choice((-83, -9, -4, -1, 0, 1, 4, 9, 83, 2**90 + 1))
        x = tuple(rng.randrange(-20, 21) for _ in range(4))
        z = tuple(rng.randrange(-2**40, 2**40) for _ in range(4))
        shifted = tuple(a + 8 * b for a, b in zip(x, z))
        base = literal(x, t, s, m)
        moved = literal(shifted, t, s, m)
        require(moved == oracle(shifted, dense_data(t, s, m)), 'large signed oracle')
        e = tuple(4 * a - b for a, b in zip(*base[:2]))
        e_shift = tuple(4 * a - b for a, b in zip(*moved[:2]))
        require(e == e_shift, 'period-eight error')
        next4 = literal(x, t, s, m + 4)
        d = [0] * 4
        d[t] = 2 * base[2][s] - butterfly_numerators(x, 0)[s]
        slopes = butterfly_numerators(d, 1)
        require(tuple(4 * a - b - old for a, b, old in zip(next4[0], next4[1], e))
                == tuple(4 * c for c in slopes), 'coefficient-period slope')
        require(max(map(abs, e)) <= abs(m) + 3, 'sharp upper bound')
        count += 1
    # Reversing the two distinct axes is a coordinate permutation (1 <-> 2).
    swapped = 0
    perm = (0, 2, 1, 3)
    for t, s in PAIRS:
        for m in (-1, 0, 1):
            data = dense_data(t, s, m, axis=1)
            for x in product((-1, 0, 1), repeat=4):
                got = literal(x, t, s, m, axis=1)
                require(got == oracle(x, data), 'reverse-axis oracle')
                standard = literal(tuple(x[i] for i in perm), perm[t], perm[s], m)
                require(got == tuple(tuple(v[i] for i in perm) for v in standard),
                        'axis conjugacy')
                swapped += 1
    return count, swapped


def rejection_controls(rows):
    rejected = []
    faults = ('floor-ties', 'omit-shear', 'reverse-shear', 'repeat-axis',
              'wrong-difference', 'omit-exact-shear', 'single-final-round')
    for fault in faults:
        detected = False
        for t, s in PAIRS:
            for m in (-1, 1):
                data = dense_data(t, s, m)
                for x in product((-1, 0, 1), repeat=4):
                    if literal(x, t, s, m, fault=fault) != oracle(x, data):
                        detected = True
                        break
                if detected:
                    break
            if detected:
                break
        require(detected, 'undetected semantic fault: ' + fault)
        rejected.append(fault)
    for name, altered in (
        ('missing-witness', rows[:-1]),
        ('duplicate-witness', rows[:-1] + rows[:1]),
        ('zeroed-witness', [rows[0][:4] + [0] * 4] + rows[1:]),
        ('wrong-slope', [rows[0][:2] + [-rows[0][2]] + rows[0][3:]] + rows[1:]),
        ('boolean-certificate', [[True] + rows[0][1:]] + rows[1:]),
    ):
        try:
            check_witnesses(altered)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('accepted malformed certificate: ' + name)
    for name, args in (
        ('off-grid', ((Q(1, 2), 0, 0, 0), 0, 1, 1)),
        ('fractional-shear', ((0, 0, 0, 0), 0, 1, Q(1, 2))),
        ('aliased-shear', ((0, 0, 0, 0), 0, 0, 1)),
    ):
        try:
            literal(*args)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('accepted outside-domain input: ' + name)
    # A unit shear defeats the unsheared 3/4 bound, while removing it restores 3/4.
    x, t, s, m = (0, -1, -1, -1), 0, 1, -1
    out, exact4, _ = literal(x, t, s, m)
    require(out == (0, 0, 0, 0) and exact4 == (-4, 1, 0, 1), 'unit-shear witness')
    plain = literal(x, t, s, 0)
    require(max(abs(4*a-b) for a,b in zip(*plain[:2])) == 3, 'unsheared control')
    rejected.append('unchanged-three-quarter-bound')
    return rejected


def generate_witnesses():
    rows = []
    for t, s in PAIRS:
        for c in (-1, 1):
            found = None
            for x in product((-1, 0, 1), repeat=4):
                zero = oracle(x, dense_data(t, s, 0))
                one = oracle(x, dense_data(t, s, 1))
                if zero[2][s]:
                    continue
                for j in range(4):
                    if (4 * zero[0][j] - zero[1][j] == 3
                            and zero[1][j] - one[1][j] == c):
                        found = [t, s, c, j, *x]
                        break
                if found is not None:
                    break
            require(found is not None, 'witness search exhausted')
            rows.append(found)
    return rows


def main():
    require(sys.argv[1:] in ([], ['--emit-result'], ['--emit-witnesses']), 'unknown option')
    if sys.argv[1:] == ['--emit-witnesses']:
        rows = generate_witnesses()
        print('{\n  "schema": "walsh-integer-shear-witnesses/v1",\n'
              '  "columns": ["target", "source", "slope", "output", "x0", "x1", "x2", "x3"],\n'
              '  "rows": [\n' + ',\n'.join('    ' + json.dumps(r) for r in rows) + '\n  ]\n}')
        return
    sources = authenticate_context()
    certificate = json.loads((HERE / 'WITNESSES.json').read_text())
    require(set(certificate) == {'schema', 'columns', 'rows'}, 'certificate fields')
    require(certificate['schema'] == 'walsh-integer-shear-witnesses/v1', 'certificate schema')
    require(certificate['columns'] == ['target', 'source', 'slope', 'output',
                                      'x0', 'x1', 'x2', 'x3'], 'certificate columns')
    rows = certificate['rows']
    for n in range(-1025, 1026):
        require(half_even(n) == round(Q(n, 2)), 'signed half rounding')
    check_witnesses(rows)
    cases, digest = census()
    periods, axes = shifted_controls()
    rejected = rejection_controls(rows)
    result = {
        'status': 'PASS_WALSH_INTERLEAVED_SHEAR',
        'exact_error_in_grid_units': '(|m|+3)/4',
        'scope': 'two distinct normalized real Walsh axes, one integer shear',
        'context_documents': sources, 'rounding_cases': 2051, 'witnesses': len(rows),
        'complete_residue_inputs': cases, 'complete_output_comparisons': 4 * cases,
        'full_output_transcript_sha256': digest,
        'large_signed_period_and_coefficient_cases': periods,
        'reverse_axis_cases': axes, 'rejected_controls': rejected,
        'no_new_kappa': True,
    }
    if sys.argv[1:] != ['--emit-result']:
        expected = json.loads((HERE / 'RESULT.json').read_text())
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                'committed result differs from computed result')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
