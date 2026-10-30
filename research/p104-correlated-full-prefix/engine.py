"""Gaussian arithmetic adapted from Nick Petalas PR3449. Apache-2.0."""

import gzip
import io
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIDTH = 512
ZERO = (0, 0)
INPUTS = {
    'WORD.json': 'cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50',
    'NATIVE.json.gz': 'ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def load():
    root = HERE.parents[1] / 'research/p104-rounded-collector/inputs'
    values = []
    for name, expected in INPUTS.items():
        path = root / name
        need(path.is_file() and not path.is_symlink(), 'regular source ' + name)
        with path.open('rb') as handle:
            raw = handle.read(4 * 1024 * 1024 + 1)
        need(len(raw) <= 4 * 1024 * 1024, 'source capacity')
        need(hashlib.sha256(raw).hexdigest() == expected, 'source digest ' + name)
        if name.endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as compressed:
                raw = compressed.read(16 * 1024 * 1024 + 1)
            need(len(raw) <= 16 * 1024 * 1024, 'native expansion capacity')
        values.append(json.loads(raw))
    word, native = values
    need(len(word['program']) == 5398 and len(word['initial_frames']) == 358,
         'literal dimensions')
    bound = {}
    for row in native['transports']:
        for event in row['events']:
            need(event not in bound and 0 <= event < 5398, 'unique native event')
            need(word['program'][event] == [
                'transport', word['program'][event][1], row['old'], row['new'],
                row['recipe']['rank']], 'native binding')
            bound[event] = row['recipe']
    need(len(bound) == 2070, 'native occurrence coverage')
    return word, bound


def rotate(z, phase):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def plan(raw):
    rows, linear, quadratic = (raw[k] for k in
                               ('matrix_rows', 'linear_Z4', 'quadratic_rows'))
    need(len(rows) == len(linear) == len(quadratic) == 9, 'wrapper dimension')
    need(all(type(x) is int and 0 <= x < WIDTH for x in rows + quadratic),
         'binary wrapper rows')
    need(all(type(x) is int and 0 <= x < 4 for x in linear), 'linear phases')
    need(type(raw['offset']) is int and 0 <= raw['offset'] < WIDTH, 'offset')
    need(type(raw['phase']) is int and 0 <= raw['phase'] < 4, 'global phase')
    result = []
    for x in range(WIDTH):
        y = raw['offset'] ^ sum(((x & row).bit_count() % 2) << j
                                for j, row in enumerate(rows))
        phase = raw['phase']
        for j in range(9):
            if x & (1 << j):
                phase += linear[j]
                phase += 2 * (quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
        result.append((y, phase % 4))
    need(sorted(y for y, _ in result) == list(range(WIDTH)), 'wrapper bijection')
    return result


def wrapper(vector, mapping, inverse=False):
    need(len(vector) == len(mapping) == WIDTH, 'wrapper shape')
    out = [ZERO] * WIDTH
    for x, (y, phase) in enumerate(mapping):
        if inverse:
            out[x] = rotate(vector[y], -phase)
        else:
            out[y] = rotate(vector[x], phase)
    return out


def pair(a, b, sign=1):
    need(sign in (-1, 1), 'pair direction')
    dr, di = a[0] - b[0], a[1] - b[1]
    numerator = ((a[0] + b[0] - sign * di, a[1] + b[1] + sign * dr),
                 (a[0] + b[0] + sign * di, a[1] + b[1] - sign * dr))
    need(all(v % 2 == 0 for z in numerator for v in z), 'nonintegral ideal pair')
    ideal = tuple((x // 2, y // 2) for x, y in numerator)
    sr, si = b[0] + dr // 2, b[1] + di // 2
    rr, ri = -sign * di, sign * dr
    low = sr - rr // 2, si - ri // 2
    literal = ((low[0] + rr, low[1] + ri), low)
    need(literal == ideal, 'literal and ideal pair disagree')
    return ideal


def native(vector, recipe, inverse=False):
    rank = recipe['rank']
    need(type(rank) is int and 1 <= rank <= 9, 'native rank')
    first, last = ('left', 'right') if inverse else ('right', 'left')
    out = wrapper(vector, recipe[first + "_plan"], inverse)
    bits = range(rank - 1, -1, -1) if inverse else range(rank)
    for j in bits:
        for x in range(WIDTH):
            if not x & (1 << j):
                out[x], out[x | (1 << j)] = pair(
                    out[x], out[x | (1 << j)], -1 if inverse else 1)
    return wrapper(out, recipe[last + "_plan"], inverse)


def pi_power(exponent):
    need(type(exponent) is int and 0 <= exponent <= 16, 'pi exponent')
    a, b = 1, 0
    for _ in range(exponent):
        a, b = a - b, a + b
    return a, b


def monomial(mask, exponent):
    need(type(mask) is int and 0 <= mask < WIDTH, 'Newton mask')
    z = pi_power(exponent)
    return [z if x & mask == mask else ZERO for x in range(WIDTH)]


def coefficients(vector):
    need(len(vector) == WIDTH, 'Newton vector width')
    out = vector[:]
    for j in range(9):
        for x in range(WIDTH):
            if x & (1 << j):
                a, b = out[x], out[x ^ (1 << j)]
                out[x] = a[0] - b[0], a[1] - b[1]
    return out


def divisible_pi(z, exponent):
    a, b = z
    for _ in range(exponent):
        if (a + b) % 2:
            return False
        a, b = (a + b) // 2, (b - a) // 2
    return True


def in_newton(vector):
    return all(divisible_pi(z, mask.bit_count())
               for mask, z in enumerate(coefficients(vector)))
