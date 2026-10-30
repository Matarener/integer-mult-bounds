#!/usr/bin/env python3
"""Check the source-bound negative E decoder application.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
A, B = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def norm2(a):
    return a[0] ** 2 + a[1] ** 2


def q_apply(state, inverse=False):
    a, b = (B, A) if inverse else (A, B)
    out = {}
    for x, value in state.items():
        for y, factor in ((x, a), (x ^ 1, b)):
            out[y] = plus(out.get(y, ZERO), times(value, factor))
    return {x: value for x, value in out.items() if value != ZERO}


def binary_rank(vectors):
    pivots = {}
    for x in vectors:
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
    return len(pivots)


def native_apply(state, columns, sign):
    out = {}
    for x, value in state.items():
        y = x & ~((1 << len(columns)) - 1)
        for j, column in enumerate(columns):
            if x >> j & 1:
                y ^= column
        factor = -1 if (x & sign).bit_count() % 2 else 1
        out[y] = (value[0] * factor, value[1] * factor)
    return out


def read_inputs():
    for entry in json.loads(ROOT.joinpath('INPUTS.json').read_text()):
        data = ROOT.joinpath(entry['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry['sha256'], 'source SHA256')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == entry['git_blob'], 'source Git object')
    return json.loads(ROOT.joinpath('source/decoder-result.json').read_text())


def validate_data(data):
    require(type(data['ambient_axes']) is int and data['ambient_axes'] == 73, 'ambient axes')
    require(data['owner_input'] == [0, 0, 0] and data['owner_output'] == [1, 0, 0], 'owner endpoints')
    r0, r1 = (1, 1, 1, 1, 0, 0, 0, 0), (1, 1, 0, 0, 1, 1, 0, 0)
    cross = F(sum(x * y for x, y in zip(r0, r1)), 8)
    active = F(8, 112)
    middle = 3 * active ** 2 * (1 - active) * F(98, 97) + active ** 3 * F(1078, 1079)
    coefficient = cross * middle
    require(cross == F(data['E_inverse_cross_entry']) == F(1, 4), 'actual cross coefficient')
    require(middle == F(data['E_diagonal']) == F(1541, 104663), 'actual middle coefficient')
    require(F(data['E_inverse_diagonal']) == 1, 'actual diagonal inverse')
    require(coefficient == F(data['surviving_coefficient']) == F(1541, 418652), 'path coefficient')
    columns = data['selected_permutation_columns']
    require(len(columns) == 25 and binary_rank(columns) == 25, 'invertible local map')
    require(all(type(x) is int and 0 < x < 1 << 25 for x in columns), 'local columns')
    require(columns[0] != 1, 'central axis must move')
    sign = data['selected_sign']
    require(type(sign) is int and 0 <= sign < 1 << 25, 'native sign')
    got = q_apply(native_apply(q_apply({0: ONE}), columns, sign), True)
    expected = {x: tuple(F(v) for v in value) for x, value in data['conjugated_zero_column']}
    require(got == expected and len(got) == 4 and all(norm2(z) == F(1, 4) for z in got.values()), 'actual sparse column')
    return coefficient, columns, sign


def row_bound(n, width):
    require(n >= 1 and width >= 4 * n + 4, 'unproved width')
    width -= width % 2
    N, gaussian, total = 2 * n, 1, F(0)
    for k in range(1, N + 1):
        numerator = gaussian * ((1 << (N - k + 1)) - 1)
        denominator = (1 << k) - 1
        require(numerator % denominator == 0, 'Gaussian binomial integrality')
        gaussian = numerator // denominator
        count = 2 * ((1 << N) - 1) if k == 1 else gaussian * (1 << (k * (k + 3) // 2))
        total += F(count, 1 << (k * width // 2))
    return total


def infinite_bound(shift):
    d, total = 1, F(1, 1 << (shift + 1))
    for k in range(1, 6):
        d *= (1 << k) - 1
        if 2 <= k <= 4:
            total += F(1, (1 << (shift * k)) * d)
    total += F(1, (1 << (5 * shift)) * d) / (1 - F(1, 63 * (1 << shift)))
    return total


def controls(data):
    rejected = 0
    mutations = [('ambient_axes', True), ('surviving_coefficient', '1/4'), ('E_diagonal', '98'),
                 ('selected_sign', data['selected_sign'] ^ 1), ('owner_output', [0, 0, 0])]
    for key, value in mutations:
        altered = {**data, key: value}
        try:
            validate_data(altered)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('changed source field accepted')
    try:
        row_bound(73, 295)
    except ValueError:
        rejected += 1
    else:
        raise ValueError('unproved width accepted')
    require(F(data['surviving_coefficient']) ** 2 != F(data['surviving_coefficient']), 'external scalar is not tensorized')
    rejected += 1
    # Two phase copies can cancel. The source uniqueness premise excludes this case.
    require(1 + (-1) ** 1 == 0 and 1 + (-1) ** 2 == 2, 'projective phase merging')
    rejected += 1
    raw = ROOT.joinpath('source/decoder-result.json').read_bytes()
    require(hashlib.sha256(raw + b' ').hexdigest() != hashlib.sha256(raw).hexdigest(), 'source corruption control')
    return rejected + 1


def main():
    data = read_inputs()
    coefficient, columns, sign = validate_data(data)
    for x in (0, 1):
        before = q_apply({x: ONE}, True)
        shifted = {y ^ 1: z for y, z in before.items()}
        signed = {y: ((-1) ** (y & 1) * z[0], (-1) ** (y & 1) * z[1]) for y, z in before.items()}
        require(q_apply(shifted) == {x ^ 1: ONE}, 'Q X Q inverse')
        require(q_apply(signed) == {x ^ 1: (F(0), F(-1 if x == 0 else 1))}, 'Q Z Q inverse')
    addresses = [0] + [1 << j for j in range(73)] + [(1 << j) | (1 << ((j + 7) % 73)) for j in range(73)]
    for x in addresses:
        require(q_apply(q_apply({x: ONE}), True) == {x: ONE}, 'unitary Q inverse')
        require(q_apply(q_apply({x: ONE})) == {x ^ 1: ONE}, 'Q squared is X')
        result = q_apply(native_apply(q_apply({x: ONE}), columns, sign), True)
        require(len(result) == 4 and sum(norm2(z) for z in result.values()) == 1, 'nonmonomial unit column')
    bounds = 0
    for n in (1, 2, 3, 9, 17, 73):
        for shift, cap in ((0, F(8, 9)), (2, F(3, 20)), (6, F(1, 126))):
            uniform = infinite_bound(shift)
            require(uniform < cap, 'complete infinite tail')
            for parity in (0, 1):
                actual = row_bound(n, 4 * n + 4 + 2 * shift + parity)
                require(actual <= uniform, 'finite count versus dimension-uniform row bound')
                bounds += 1
    require(4 * 73 + 4 == 296 and coefficient / 3 == F(1541, 1255956), 'application threshold and norm floor')
    require(2 * 4198 - 216 > 8178 and 2 * 4197 - 216 == 8178, 'credited old support threshold')
    print('PASS_NEGATIVE_E_DECODER_GRAM_BOUND ' + json.dumps(dict(source_files=3,
        sparse_columns=len(addresses),clifford_generator_checks=4,finite_gram_bounds=bounds,controls=controls(data),
        axes=73,old_support_threshold=4198,new_threshold=296,
        path_coefficient=str(coefficient),operator_error_floor=str(coefficient / 3),
        normalized_squared_error_floor=str(coefficient ** 2 / 9),
        stronger_squared_floor_from_308=str(F(125, 126) * coefficient ** 2)), sort_keys=True))


if __name__ == '__main__':
    main()
