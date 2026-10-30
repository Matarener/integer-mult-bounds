"""Check the exact projector exclusions and the stated boundary controls."""
import argparse
from fractions import Fraction as F
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exact_replay as e
import free_replay
import period_check


def need(value, message):
    if not value:
        raise ValueError(message)


def short_certificate(mutate=False):
    names, ps, qs, ts = e.chart(4)
    variables = {name: {(i,): F(1)} for i, name in enumerate(names)}
    a, u, b, c = [variables[name] for name in ('a3_0', 'b2_1', 'b3_0', 'c3')]
    one, two = e.const(1), e.const(2)
    neg = lambda p: e.scale(p, -1)
    solution = [e.add(a, two), b, e.add(b, one), e.add(two, neg(c)),
                e.add(neg(a), neg(two)), e.add(a, u, neg(c), two),
                e.add(neg(b), neg(c)), e.add(a, b, two), u,
                e.add(neg(a), c, neg(two)), a, e.add(b, one), b, neg(c), c]
    substitution = dict(enumerate(solution))
    linear = e.coefficient_equations(ps, ts, 1)
    pivots = []
    reduced = e.row_reduce(linear, pivots)
    power_two = lambda x: x > 0 and x & (x-1) == 0
    need(len(reduced) == 11 and all(power_two(abs(v.numerator)) and
         power_two(v.denominator) for v in pivots), 'First coefficient needs an odd denominator')
    need(not any(e.substitute(p, substitution) for p in linear), 'Displayed first-coefficient chart fails')
    ps = [e.ms(p, substitution) for p in ps]
    qs = [e.substitute(p, substitution) for p in qs]
    second = e.coefficient_equations(ps, ts, 2)
    g0, g2, g3, g5, g11 = qs[0], qs[2], second[0], second[2], second[8]
    if mutate:
        g5 = e.add(g5, one)
    B = e.scale(e.add(g0, neg(g2)), F(1, 4))
    C2 = e.add(e.scale(g11, F(1, 2)), neg(e.mul(B, e.add(e.scale(a, -2), neg(u), e.scale(c, 3), neg(one)))))
    square = e.add(e.scale(g3, F(1, 2)), neg(C2),
                   neg(e.mul(B, e.add(neg(a), e.scale(u, -2), e.scale(c, 3), neg(two)))))
    A = e.add(e.scale(g5, F(1, 2)), e.scale(square, -2),
              neg(e.mul(B, e.add(a, e.scale(u, -2), c, e.const(4)))))
    certificate = e.add(e.scale(square, 4), neg(e.mul(e.add(e.scale(a, 2), one), A)))
    need(certificate == one, 'The polynomial identity for one fails')
    point = {names.index('a3_0'): e.const(-1), names.index('b2_1'): {},
             names.index('b3_0'): {}, names.index('c3'): {}}
    candidate = [e.ms(p, point) for p in ps]
    need(not any(e.substitute(q, point) for q in qs), 'The first-order control is not a projector')
    need(not any(e.coefficient_equations(candidate, ts, 1)), 'The first-order control fails too early')
    need(any(e.coefficient_equations(candidate, ts, 2)), 'The first-order control was wrongly accepted')
    return {'linear_rank': 11, 'free_parameters': 4, 'identity': '1',
            'denominators': 'powers of two only', 'first_order_false_positive_rejected': True}


def alternating(n):
    names, ps, qs, ts = e.chart(n, tuple(range(2, n, 2)))
    for step in range(n):
        equations = e.coefficient_equations(ps, ts, 1) if step == 0 else qs + e.coefficient_equations(ps, ts, 2)
        affine = [p for p in e.row_reduce(equations) if all(len(m) <= 1 for m in p)]
        values = e.linear_solution(affine)
        need(values is not None, 'The alternating construction has no affine solution')
        ps = [e.ms(p, values) for p in ps]
        qs = [e.substitute(q, values) for q in qs]
        if not values:
            break
    need(not any(qs), 'The alternating construction fails idempotence')
    need(all(set(p) <= {()} for matrix in ps for row in matrix for p in row), 'The construction has unresolved variables')
    for degree in range(1, n):
        need(not any(e.coefficient_equations(ps, ts, degree)), 'The full query polynomial fails')
    ident = e.eye(n)
    stages = [ps[0]] + ps + [ps[-1]]
    plus = [ident]
    for p in stages:
        old = plus
        plus = [old[0]] + [e.ma(old[j], e.mm(p, old[j-1])) for j in range(1,len(old))] + [e.mm(p, old[-1])]
    # The polynomials use w=z-1, so z=2 is the sum of their coefficients.
    value = e.zero(n)
    for coefficient in plus:
        value = e.ma(value,coefficient)
    shifted = lambda scalar: e.ma(value, [[e.scale(x,scalar) for x in row] for row in ident], -1)
    nilpotent = e.mm(shifted(2),shifted(4))
    need(nilpotent != e.zero(n), 'The coupled endpoint control has no Jordan defect')
    power = ident
    for _ in range(n):
        power = e.mm(nilpotent,power)
    need(power == e.zero(n), 'The Jordan-defect polynomial is not nilpotent')
    return {'n': n, 'thin_sites': list(range(2,n,2)),
            'full_query_polynomial': 'PASS', 'stage_at_two': 'NONSEMISIMPLE'}


def signed_control():
    """Two independent triangles attain the six-call signed bound."""
    _, _, raw = e.canonical(2)
    words = [{0:e.eye(4)}, {0:e.eye(4)}]
    for plane, sign in [(0,1),(2,-1)]:
        p = e.zero(4)
        for i in range(plane,plane+2):
            p[i][i] = e.const(1)
        for small in raw:
            t = e.eye(4)
            for i in range(2):
                for j in range(2):
                    t[plane+i][plane+j] = e.const(small[i][j])
            for channel, query in enumerate([e.eye(4),t]):
                out = {}
                for degree, coefficient in words[channel].items():
                    value = e.mm(query, coefficient)
                    for power, term in [(degree, e.mm(e.ma(e.eye(4),p,-1), value)),
                                        (degree+sign,e.mm(p,value))]:
                        out[power] = e.ma(out.get(power,e.zero(4)),term)
                words[channel] = {k:v for k,v in out.items() if v != e.zero(4)}
    expected = {}
    for power, start in [(3,0),(-3,2)]:
        matrix = e.zero(4)
        for j in range(start,start+2):
            matrix[j][j] = e.const(1)
        expected[power] = matrix
    need(words[0] == expected, 'The six-call signed positive endpoint fails')
    need(set(words[1]) == set(expected), 'The signed query endpoint has an extra power')
    need(all(e.ma(words[0][k],words[1][k]) == e.zero(4) for k in expected), 'The signed query endpoint fails')
    return {'calls':6,'fields':4,'stage_powers':[3,3,-3,-3],'complete_laurent_endpoint':'PASS'}


def verify():
    result = {'short_certificate':short_certificate(), 'signed_control':signed_control(),
              'finite_period_controls':period_check.verify(),
              'free_algebra_matrix_controls':free_replay.matrix_controls(),
              'block_corner_controls':free_replay.corner_controls()}
    try:
        short_certificate(mutate=True)
    except ValueError as error:
        need(str(error) == 'The polynomial identity for one fails', 'Wrong mutation rejection')
    else:
        raise ValueError('The changed coefficient was accepted')
    result['changed_coefficient_rejected'] = True
    rows, coupled = [], []
    for n in (4,6,8):
        for count in range(n//2):
            for thin in itertools.combinations(range(1,n),count):
                row = e.replay(n,thin,False)
                expected = ('SECOND_COEFFICIENT_CONSISTENT' if thin == tuple(range(2,n,2))
                            else 'EXACT_SECOND_COEFFICIENT_CONTRADICTION')
                need(row['status'] == expected, f'Unexpected exact outcome: n={n}, thin={thin}')
                rows.append({k:v for k,v in row.items() if k != 'seconds'})
                block = free_replay.replay(n, thin)
                block_expected = ('SECOND_COEFFICIENT_CONSISTENT' if thin == tuple(range(2,n,2))
                                  else 'EXACT_FREE_ALGEBRA_CONTRADICTION')
                need(block['status'] == block_expected,
                     f'Unexpected free-algebra outcome: n={n}, thin={thin}')
                coupled.append(block)
        print(f'PASS_EXACT_FIELD_COUNT_{n}',flush=True)
    result['domains'] = rows
    result['coupled_domains'] = coupled
    result['alternating_controls'] = [alternating(n) for n in (4,6,8)]
    result['new_kappa'] = False
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    path = Path(__file__).with_name('RESULT.json')
    result = verify()
    if args.write:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(result == json.loads(path.read_text()), 'The saved exact receipt differs')
    print('PASS_SHORTEST_QUERY_PROJECTOR_RIGIDITY')
