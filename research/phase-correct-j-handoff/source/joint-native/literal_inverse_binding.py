#!/usr/bin/env python3
"""Independent literal-circuit audit of the original-t inverse coefficient.

No caller X-character algebra is imported. Physical event circuits are
recompiled with the frozen Gaussian Clifford implementation, then their
X-character actions are derived directly gate by gate. Apache-2.0;
substantial OpenAI Codex assistance. No new kappa claim.
"""
from pathlib import Path
from fractions import Fraction
from functools import lru_cache
import argparse
import hashlib
import json
import sys
sys.dont_write_bytecode = True
from joint_coefficient_gate import NATIVE, PIN, operators
from native_model import ce, mul, need, phase, b
from lifted_algebra import G, ONE, ZERO, UNITS

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'caller-joint'
SOURCE_PINS = {
    'joint_algebra.py': '6fe4de627845a36e2e08723e705daa86959846fe4ea577e94fca233829d7d5c9',
    'joint_prefix.py': 'a4dcaa1ad05ef8dbba60ddd47b3ad44a3095ebb5fd31f6adfb935a7b1c46a2c7',
    'JOINT-PREFIX.json': 'e6e574525a51299bae4fc876c02f0a767d7d927150b7a5fe0a814afd7ec93ebd',
}


def par(x):
    return x.bit_count() & 1


def mv(rows, x):
    return sum(par(row & x) << j for j, row in enumerate(rows))


def circuit_op(events, n):
    out = ce.ident(n)
    for event in events:
        kind = event[0]
        if kind == 'P':
            gate = ce.perm(n, tuple(event[1]))
        elif kind == 'D':
            gate = ce.diag(n, tuple(event[1]), tuple(event[2]))
        elif kind == 'C':
            gate = ce.cgate(n, event[1], event[2])
        elif kind == 'X':
            gate = ce.xgate(n, event[1])
        elif kind == 'phase':
            gate = phase(n, event[1])
        else:
            raise ValueError('uncovered physical primitive ' + kind)
        out = out.then(gate)
    return out


@lru_cache(None)
def pinv_transpose(rows):
    return ce.transpose(ce.inv(rows, len(rows)), len(rows))


def x_action(events, n, x):
    """Literal action on physical X eigencharacters, including global units."""
    power = 0
    for event in events:
        kind = event[0]
        if kind == 'P':
            x = mv(pinv_transpose(tuple(event[1])), x)
        elif kind == 'C':
            power += event[2] * par(event[1] & x)
        elif kind == 'X':
            power += 2 * par(event[1] & x)
        elif kind == 'D':
            need(not any(event[1]) and all(a % 2 == 0 for a in event[2]),
                 'current source literal D is a Pauli; no Fourier-monomial assumption hidden')
            x ^= sum(((a // 2) & 1) << j for j, a in enumerate(event[2]))
        elif kind == 'phase':
            power += event[1]
        else:
            raise ValueError(kind)
    return x, power % 4


def make_key(n, act, qfun):
    offset, c = act(0), qfun(0) % 4
    columns = [act(1 << j) ^ offset for j in range(n)]
    rows = tuple(sum(((columns[j] >> i) & 1) << j for j in range(n)) for i in range(n))
    alpha = tuple((qfun(1 << j) - c) % 4 for j in range(n))
    quad = []
    for i in range(n):
        row = 0
        for j in range(i + 1, n):
            v = (qfun((1 << i) | (1 << j)) - c - alpha[i] - alpha[j]) % 4
            need(v % 2 == 0, 'literal phase is a Gaussian quadratic')
            row |= (v // 2) << j
        quad.append(row)
    return (rows, offset, alpha, tuple(quad)), c


def act(key, x):
    return mv(key[0], x) ^ key[1]


def qval(key, x):
    return (sum(a for i, a in enumerate(key[2]) if x >> i & 1)
            + 2 * sum(par(row & x) for i, row in enumerate(key[3]) if x >> i & 1)) % 4


def units(fn):
    return tuple(UNITS[fn(r) % 4] for r in range(4))


def sumexpr(a, c):
    out = dict(a)
    for k, v in c.items():
        w = tuple(x + y for x, y in zip(out.get(k, (ZERO,) * 4), v))
        if any(w):
            out[k] = w
        else:
            out.pop(k, None)
    return out


def scale(a, c):
    return {k: tuple(x * G(Fraction(c)) for x in v) for k, v in a.items()} if c else {}


@lru_cache(None)
def key_product(a, c):
    n = len(a[0])
    return make_key(n, lambda x: act(a, act(c, x)), lambda x: qval(c, x) + qval(a, act(c, x)))


def product(a, c):
    out = {}
    for ka, va in a.items():
        for kc, vc in c.items():
            k, constant = key_product(ka, kc)
            value = tuple(x * y * u for x, y, u in zip(va, vc, units(lambda r: r * constant)))
            out = sumexpr(out, {k: value})
    return out


def from_circuit(op, exponent):
    key, c = make_key(op.n, lambda x: x_action(op.circuit, op.n, x)[0],
                      lambda x: x_action(op.circuit, op.n, x)[1])
    return {key: units(lambda r: exponent + (c - exponent) * r)}


def serial(a):
    return [{'X_character_rows': list(k[0]), 'offset': k[1], 'alpha': list(k[2]),
             'quadratic_upper_rows': list(k[3]),
             'coefficients_by_f_mod4': [x.encode() for x in v]}
            for k, v in sorted(a.items())]


def inverse_row(fixture, mutate=False):
    q, n, m = fixture['q'], fixture['banks'], fixture['ambient_arity']
    identity = from_circuit(ce.ident(m), 0)
    row = [{} for _ in range(n)]
    row[1] = identity
    hist = {}
    for event in fixture['events']:
        kind = event['kind']
        if kind == 'ADD':
            d, s = event['dst'], event['src']
            row[s] = sumexpr(row[s], scale(row[d], -Fraction(event['coefficient'])))
        elif kind == 'BANK_SWAP':
            i, j = event['banks']
            row[i], row[j] = row[j], row[i]
        else:
            op = circuit_op(event['one_coordinate_literal_circuit'], m)
            need(op.tab == tuple(tuple(x) for x in event['one_coordinate_tableau']),
                 'independently recompiled physical event signed tableau')
            rank = b.native_rank(op)
            if kind == 'NATIVE':
                need(rank == event['rank_per_f'], 'actual native event arity, not label')
                hist[rank] = hist.get(rank, 0) + 1
            else:
                need(rank == 0, 'free physical event is actually monomial')
            exponent = -event['phase_exponent']
            value = from_circuit(op.adjoint(), exponent)
            row[event['bank']] = product(row[event['bank']], value)
    z, J, A, B1, B2, Q1, Dv, F, C, collapsed = operators(q, 1)
    target = from_circuit(mul(F, J), 2 * q + 2 - int(mutate))
    actual = product(target, row[3])
    expected = from_circuit(C, 6 - 3 * q)
    if mutate:
        need(actual != expected, 'missing target-J f-dependent Gaussian unit rejected beyond f1')
    else:
        need(actual == expected and len(actual) == 1,
             'literal all-f inverse-row coefficient equals independent Clifford formula')
        need(hist == {2: n * (2 * q + 1) + q + 2}, 'source/query/idle/continuation profile bound')
    return {'q': q, 'independent_original_input_row': 1, 'current_carrier_column': 3,
            'physical_events': len(fixture['events']), 'native_histogram': hist,
            'original_column_binding_all_f': 'PASS' if not mutate else 'MUTANT_REJECTED',
            'actual_coefficient': serial(actual) if not mutate else None}


def run():
    for name, digest in SOURCE_PINS.items():
        need(hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() == digest, 'caller source pin ' + name)
    source = json.loads((SOURCE / 'JOINT-PREFIX.json').read_text())
    records = [inverse_row(x) for x in source['fixtures']]
    inverse_row(source['fixtures'][0], True)
    return {'status': 'PASS_INDEPENDENT_LITERAL_ORIGINAL_T_INVERSE_COEFFICIENT',
            'scientific_pin': PIN, 'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins': [{'path': str(SOURCE / n), 'sha256': h} for n, h in SOURCE_PINS.items()],
            'fixtures': records,
            'method': 'Derive X-character affine/quadratic action directly from each literal physical circuit; independently recompile every signed tableau; right-multiply the original-t inverse row by each forward primitive inverse. No caller joint_algebra/quadratic_charts module is imported.',
            'all_f_phase': 'Each physical one-coordinate circuit O with exponent e represents i^(e*(1-f))*O^tensor(f). Exact Gaussian coefficient vectors retain every f mod4 residue; native J units are not inferred from f1.',
            'negative_control': 'Omit only the target-J f-dependent tensor unit. This changes the actual desired output gauge and is rejected by the complete inverse coefficient although f1 alone cannot see it. Individual source-query2/query5 unit deletions were insensitive for this selected inverse entry and are not counted as rejected controls.',
            'scope': 'Independent source binding for the required inverse coefficient at q2/q3. Caller owns full physical all-column/inverse prefix; the separate written coefficient/support theorem covers every q satisfying its stated original-column interface.',
            'no_new_kappa': True}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'LITERAL-INVERSE-BINDING.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved independent physical coefficient binding differs')
    print(out['status'])
