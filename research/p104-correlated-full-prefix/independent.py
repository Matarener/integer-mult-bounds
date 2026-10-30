"""Separate forward-dependency, integer-butterfly and subgroup reconstruction.

Imports no package or predecessor executable. Apache-2.0.
"""

import gzip
import hashlib
import io
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checksum(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def sources():
    root = HERE.parents[1] / 'research/p104-rounded-collector/inputs'
    pins = [('WORD.json', 'cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50'),
            ('NATIVE.json.gz',
             'ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d')]
    data = []
    for name, pin in pins:
        path = root / name
        require(path.is_file() and not path.is_symlink(), 'regular independent input')
        with path.open('rb') as handle:
            raw = handle.read(4 * 1024 * 1024 + 1)
        require(len(raw) <= 4 * 1024 * 1024 and hashlib.sha256(raw).hexdigest() == pin,
                'independent source authentication')
        if name.endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as handle:
                raw = handle.read(16 * 1024 * 1024 + 1)
            require(len(raw) <= 16 * 1024 * 1024, 'independent expansion capacity')
        data.append(json.loads(raw))
    word, archive = data
    recipes = {}
    for row in archive['transports']:
        for event in row['events']:
            require(event not in recipes and word['program'][event] ==
                    ['transport', word['program'][event][1], row['old'], row['new'],
                     row['recipe']['rank']], 'independent occurrence binding')
            recipes[event] = row['recipe']
    require(len(recipes) == 2070 and len(word['program']) == 5398, 'independent dimensions')
    return word, recipes


def permutation(raw):
    result = []
    for x in range(512):
        bits = [(x >> j) & 1 for j in range(9)]
        out = raw['offset']
        phase = raw['phase']
        for j in range(9):
            out ^= ((x & raw['matrix_rows'][j]).bit_count() & 1) << j
            phase += bits[j] * raw['linear_Z4'][j]
            for k in range(j + 1, 9):
                phase += 2 * bits[j] * bits[k] * ((raw['quadratic_rows'][j] >> k) & 1)
        result.append((out, phase % 4))
    require(len({x for x, _ in result}) == 512, 'independent permutation')
    return result


def move(vector, mapping):
    out = [(0, 0)] * 512
    for x, (destination, power) in enumerate(mapping):
        a, b = vector[x]
        out[destination] = [(a, b), (-b, a), (-a, -b), (b, -a)][power]
    return out


def butterfly(vector, bit):
    out = vector[:]
    for x in range(512):
        if (x >> bit) & 1:
            continue
        a, b = vector[x]
        c, d = vector[x | (1 << bit)]
        values = (a + c - b + d, b + d + a - c,
                  a + c + b - d, b + d - a + c)
        require(all(v % 2 == 0 for v in values), 'independent integral scaled butterfly')
        out[x] = values[0] // 2, values[1] // 2
        out[x | (1 << bit)] = values[2] // 2, values[3] // 2
    return out


def forward_actions(word, recipes):
    reached, actions = {'Y27', 'Y26'}, []
    for event, row in enumerate(word['program'][:2025]):
        if row[0] == 'add' and row[2] in reached:
            reached.add(row[1])
            actions.append((event, row, None))
        elif row[0] == 'transport' and row[1] in reached:
            recipe = recipes[event]
            require(row[4] == recipe['rank'], 'independent native occurrence')
            actions.append((event, row, (permutation(recipe['right']),
                                         permutation(recipe['left']), recipe['rank'])))
        elif row[0] == 'sign':
            require(row[1] not in reached, 'independent inactive sign')
    require(len(actions) <= 200, 'independent dependency capacity')
    return actions


def run(y, actions):
    state = {'Y27': [(4 * a, 4 * b) for a, b in y],
             'Y26': [(-4 * a, -4 * b) for a, b in y]}
    cuts = {}
    for event, row, native in actions:
        dst = row[1]
        if native is None:
            p, q = Fraction(row[3]).as_integer_ratio()
            before = state.get(dst, [(0, 0)] * 512)
            source = state[row[2]]
            require(all(p * a % q == p * b % q == 0 for a, b in source),
                    'independent scaled ADD')
            term = [(p * a // q, p * b // q) for a, b in source]
            cuts[f'{event}:addend:{dst}'] = term
            state[dst] = [(a + c, b + d) for (a, b), (c, d)
                          in zip(before, term, strict=True)]
        else:
            right, left, rank = native
            out = move(state[dst], right)
            for bit in range(rank):
                out = butterfly(out, bit)
                cuts[f'{event}:C{bit}:{dst}'] = out[:]
            state[dst] = move(out, left)
    for name in ('D31', 'D30', 'D29', 'D28', 'D27', 'Q7'):
        require(all(z == (0, 0) for z in state.get(name, [])), 'independent endpoint')
    return cuts


def newton(mask, reserve=0):
    a, b = 1, 0
    for _ in range(mask.bit_count() + reserve):
        a, b = a - b, a + b
    return [(a, b) if x & mask == mask else (0, 0) for x in range(512)]


def reconstruct(actions):
    matrices = {}
    for column in range(512):
        cuts = run(newton(column), actions)
        if column == 0:
            matrices = {key: [[0, 0, 0, 0] for _ in range(512)] for key in cuts}
        require(list(cuts) == list(matrices), 'independent stable cuts')
        bit = 1 << column
        for key, vector in cuts.items():
            for address, (real, imag) in enumerate(vector):
                row = matrices[key][address]
                if real & 1:
                    row[0] |= bit
                if real & 2:
                    row[1] |= bit
                if imag & 1:
                    row[2] |= bit
                if imag & 2:
                    row[3] |= bit
    nonzero = {key: rows for key, rows in matrices.items() if any(any(r) for r in rows)}
    return list(nonzero), [row for rows in nonzero.values() for row in rows]


def f2_insert(row, pivots):
    for _ in range(1025):
        if row == 0:
            return
        pivot = row.bit_length() - 1
        if pivot not in pivots:
            pivots[pivot] = row
            return
        row ^= pivots[pivot]
    raise ValueError('independent binary capacity')


def group_index(rows):
    """|G| = |G mod 2| * |G intersect 2(Z/4)^n|, using addition only."""
    odd, torsion = {}, {}
    require(len(rows) <= 40000, 'independent row capacity')
    for source in rows:
        low, high = source
        require(0 <= low < (1 << 1024) and 0 <= high < (1 << 1024),
                'independent row width')
        for _ in range(1025):
            if low == 0:
                f2_insert(high, torsion)
                break
            pivot = low.bit_length() - 1
            if pivot not in odd:
                odd[pivot] = (low, high)
                break
            other_low, other_high = odd[pivot]
            high ^= other_high ^ (low & other_low)
            low ^= other_low
        else:
            raise ValueError('independent Z4 capacity')
    for low, _ in odd.values():
        f2_insert(low, torsion)
    return len(odd) + len(torsion)


def rows_at_power(matrix, power):
    rows = []
    for al, ah, bl, bh in matrix:
        r = (al | (bl << 512), ah | ((bh ^ bl) << 512))
        s = (bl | (al << 512), bh | (ah << 512))
        if power == 0:
            rows.extend((r, s))
        elif power == 1:
            low = r[0] ^ s[0]
            rows.extend(((low, r[1] ^ s[1] ^ s[0] ^ (r[0] & s[0])),
                         (low, r[1] ^ s[1] ^ (r[0] & s[0]))))
        elif power == 2:
            rows.extend(((0, r[0]), (0, s[0])))
        else:
            rows.append((0, r[0] ^ s[0]))
    return rows


def check_fixtures(receipt, actions):
    terms = receipt['separating_witness']['newton_coefficients']
    require(len(terms) == 9, 'nine-term witness')
    y = [(sum(z[0] for mask, z in terms if x & mask == mask),
          sum(z[1] for mask, z in terms if x & mask == mask)) for x in range(512)]
    require(checksum(y) == receipt['separating_witness']['source_sha256'], 'witness bytes')
    failures = [(key, x, z) for key, vector in run(y, actions).items()
                for x, z in enumerate(vector) if z[0] % 4 or z[1] % 4]
    require(failures[0] == ('1190:addend:D10', 0, (-2, 2)), 'independent first failure')
    y = [(0, 0)] * 512
    for mask in receipt['admitted_correlated_fixture']['pi3_newton_basis_masks']:
        term = newton(mask, 3)
        y = [(a + c, b + d) for (a, b), (c, d) in zip(y, term, strict=True)]
    require(checksum(y) == receipt['admitted_correlated_fixture']['source_sha256'],
            'admitted bytes')
    require(all(a % 4 == b % 4 == 0 for vector in run(y, actions).values()
                for a, b in vector), 'independent admitted source')


def main():
    require(len(sys.argv) == 1, 'usage: independent.py')
    word, recipes = sources()
    actions = forward_actions(word, recipes)
    keys, matrix = reconstruct(actions)
    with (HERE / 'RESULT.json').open('rb') as handle:
        raw = handle.read(1024 * 1024 + 1)
    require(len(raw) <= 1024 * 1024, 'independent receipt capacity')
    receipt = json.loads(raw)
    require(keys == receipt['checkpoints'] and checksum(matrix) == receipt['matrix_sha256'],
            'independent complete matrix')
    indices = [group_index(rows_at_power(matrix, k)) for k in range(4)]
    require(indices == [868, 424, 133, 19], 'independent Gaussian images')
    check_fixtures(receipt, actions)
    print('PASS_P104_FULL_PREFIX_INDEPENDENT images=868,424,133,19')


if __name__ == '__main__':
    main()
