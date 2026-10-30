#!/usr/bin/env python3
"""Complete independent six-bank endpoint replay by 64-state action tables.

No historical algebra constructor is imported.  Gaussian scalar coefficients
are exact rational pairs at each f modulo four.  Every bank has an independent
input column; the inactive six character bits are checked to be spectators.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction as F
import json
import hashlib
import types
from pathlib import Path

_engine = Path(__file__).resolve().with_name('independent.py')
_engine_bytes = _engine.read_bytes()
if hashlib.sha256(_engine_bytes).hexdigest() != 'f382b43e44fade941e961da870276035a9cb17dfe94c5a4b5867c7a33f8e2a72':
    raise ValueError('independent action-table source hash')
q = types.ModuleType('cut58_independent_action_table')
q.__file__ = str(_engine)
exec(compile(_engine_bytes, str(_engine), 'exec'), q.__dict__)

ACTIVE = (0, 1, 2, 3, 10, 11)
MASK = sum(1 << i for i in ACTIVE)
ZERO = ((F(0), F(0)),) * 4
ONE = ((F(1), F(0)),) * 4
IDENTITY = q.identity(6)
IKEY = IDENTITY[:2]


def normal(g, coefficients=ONE):
    c = g[1][0]
    key = g[0], tuple((a - c) % 4 for a in g[1])
    values = tuple(q.gaussian_multiply(v, q.UNITS[(c * r + g[2]) % 4]) for r, v in enumerate(coefficients))
    return {key: values} if any(v != (0, 0) for v in values) else {}


def decode(data):
    for j, row in enumerate(data['rows']):
        q.need((row & ~MASK) == 0 if j in ACTIVE else row == 1 << j, 'inactive bits are literal spectators')
        if j not in ACTIVE:
            q.need(data['alpha'][j] == data['quad'][j] == 0, 'no inactive phase')
        else:
            q.need(not (data['quad'][j] & ~MASK), 'no active-inactive phase coupling')
    q.need(not (data['offset'] & ~MASK), 'no inactive translation')
    return q.table(data, ACTIVE)


def unary(data):
    return normal(decode(data))


def add(a, b):
    out = dict(a)
    for key, values in b.items():
        new = tuple(q.gaussian_add(x, y) for x, y in zip(out.get(key, ZERO), values))
        if any(v != (0, 0) for v in new):
            out[key] = new
        else:
            out.pop(key, None)
    return out


def scale(a, coefficient):
    return {key: tuple((coefficient * x, coefficient * y) for x, y in values) for key, values in a.items()} if coefficient else {}


def multiply(a, b):
    out = {}
    for x, v in a.items():
        for y, w in b.items():
            g = q.compose((*x, 0), (*y, 0))
            out = add(out, normal(g, tuple(q.gaussian_multiply(z, t) for z, t in zip(v, w))))
    return out


def summ(items):
    out = {}
    for item in items:
        out = add(out, item)
    return out


def product(*items):
    out = {IKEY: ONE}
    for item in items:
        out = multiply(out, item)
    return out


def eye():
    return [[{IKEY: ONE} if i == j else {} for j in range(6)] for i in range(6)]


def mm(a, b):
    return [[summ(multiply(a[i][k], b[k][j]) for k in range(6)) for j in range(6)] for i in range(6)]


def deserialize(matrix):
    out = []
    for row in matrix:
        target = []
        for entry in row:
            value = {}
            for term in entry:
                coefficients = tuple(tuple(F(v) for v in pair) for pair in term['coefficients_by_f_mod4'])
                value = add(value, normal(decode(term['x_monomial']), coefficients))
            target.append(value)
        out.append(target)
    return out


def replay(events):
    matrix = eye()
    for e in events:
        if e['kind'] == 'ADD':
            d, s, c = e['dst'], e['src'], F(e['coefficient'])
            matrix[d] = [add(x, scale(y, c)) for x, y in zip(matrix[d], matrix[s])]
        elif e['kind'] == 'SCALE':
            b, c = e['bank'], F(e['coefficient'])
            q.need(c != 0, 'invertible scalar')
            matrix[b] = [scale(x, c) for x in matrix[b]]
        elif e['kind'] == 'BANK_SWAP':
            i, j = e['banks']
            matrix[i], matrix[j] = matrix[j], matrix[i]
        else:
            b = e['bank']
            g = unary(e['x_monomial'])
            matrix[b] = [multiply(g, x) for x in matrix[b]]
    return matrix


def target(ops):
    K, W, T = (unary(ops[name]) for name in ('K', 'W', 'T'))
    I, z = {IKEY: ONE}, {}
    minusW = add(I, scale(W, -1))
    return [[product(K,T), z, z, z, z, z],
            [scale(product(W,K,T),-1), z, product(minusW,T), scale(T,-1), scale(product(W,T,K),-1), z],
            [scale(product(K,T),-1), z, T, scale(T,-1), scale(product(T,K),-1), z],
            [scale(product(K,W,K,T),-1), product(K,T), product(K,minusW,T), z, scale(product(K,W,T,K),-1), z],
            [z, z, z, z, product(T,K), z],
            [z, z, z, z, z, T]]


def main():
    raw = q.read_source()
    q.need(q.hashlib.sha256(raw).hexdigest() == q.SOURCE_SHA256, 'immutable CUT58 source bytes')
    src = json.loads(raw)
    expected = target(src['operators'])
    q.need(deserialize(src['complete_local_matrix']) == expected, 'complete declared six-bank target')
    q.need(replay(src['events']) == expected, 'literal forward suffix, every bank column')
    q.need(replay(src['simplified_rank_neutral_events']) == expected, 'simplified forward suffix, every bank column')
    reverse = deserialize(src['complete_local_inverse'])
    q.need(replay(src['inverse_events']) == reverse, 'literal inverse suffix')
    q.need(mm(expected, reverse) == eye(), 'forward after inverse, all six columns')
    q.need(mm(reverse, expected) == eye(), 'inverse after forward, all six columns')
    # Controls are checked outside any caught exception path.
    omitted = [dict(e) for e in src['simplified_rank_neutral_events'] if e['label'] != 'b accumulator']
    q.need(replay(omitted) != expected, 'reject omitted independent b-accumulator')
    shifted = json.loads(json.dumps(src['operators']))
    shifted['T']['global_phase'] = (shifted['T']['global_phase'] + 2) % 4
    q.need(target(shifted) != expected, 'reject omitted literal common Gaussian sign')
    print('PASS_INDEPENDENT_64_STATE_ALL_F_SIX_BANK_REPLAY', '36blocks', 'both_inverse_orders', '2rejecting_controls')


if __name__ == '__main__':
    main()
