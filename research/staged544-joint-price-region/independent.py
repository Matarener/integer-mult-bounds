# SPDX-License-Identifier: Apache-2.0
"""Independent fixed-exponent tight-face and adjacent-inventory-flow audit.

The mathematical model and original dual are due to Erwan Secousses/PR3815,
dataisfire/PR3734 and zxv/PR3682. Sagar Thakrar/PR3862 supplies the individual
basis-range interpretation. This checker imports no predecessor or companion
checker. It uses closed-form dual coordinates, ascending multiset enumeration,
positive exponential series with reciprocals, and a constructive closed-form
description of every feasible point on the twelve-column tight face.
"""
from fractions import Fraction as Q
from functools import lru_cache
import json
from pathlib import Path

WIDTHS = (4, 5, 6, 7, 8, 9)
CAPACITIES = (8, 16, 32, 48)
EXPONENT = Q(1730578437266246818741, 10**24)
SCALE = 10**100
EXPECTED_TIGHT = {
    (8, (0, 0, 0, 0, 1, 0)),
    (16, (0, 0, 0, 0, 2, 0)),
    (16, (0, 0, 0, 1, 0, 1)),
    (32, (0, 0, 0, 0, 0, 3)),
    (32, (0, 0, 0, 0, 4, 0)),
    (32, (0, 0, 0, 1, 2, 1)),
    (32, (0, 0, 0, 2, 0, 2)),
    (32, (0, 0, 1, 0, 1, 2)),
    (32, (0, 1, 0, 0, 0, 3)),
    (32, (1, 0, 0, 0, 0, 3)),
    (48, (0, 0, 0, 0, 0, 0)),
    (48, (0, 0, 0, 0, 0, 5)),
}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def check_model(model):
    expected = {'a', 'widths', 'capacities', 'demands', 'bins', 'basis',
                'extras', 'flows', 'expected_axis_ranges'}
    require(type(model) is dict and set(model) == expected, 'model fields')
    require(Q(model['a']) == EXPONENT, 'fixed exponent source')
    require(model['widths'] == list(WIDTHS), 'model widths')
    require(model['capacities'] == list(CAPACITIES), 'model capacities')
    require(model['demands'] == [234, 18, 162, 477, 864, 1917], 'model inventory')
    require(model['bins'] == [672, 448, 448, 448], 'model bins')
    require(model['flows'] == [5, 6, 7, 8, 9], 'model adjacent flows')
    require(model['expected_axis_ranges'] == ['18', '48', '88/3', '30', '48'],
            'model claimed ranges')
    extras = {(16, (0, 0, 0, 0, 2, 0)), (32, (0, 0, 0, 0, 4, 0))}
    for key, wanted in [('extras', extras), ('basis', EXPECTED_TIGHT-extras)]:
        require(type(model[key]) is list and len(model[key]) == len(wanted),
                'model column count')
        converted = set()
        for cap, counts in model[key]:
            require(type(cap) is int and type(counts) is list
                    and len(counts) == 6 and all(type(v) is int and v >= 0 for v in counts),
                    'model column domain')
            converted.add((cap, tuple(counts)))
        require(converted == wanted, 'model tight columns')


def rounded_interval(lo, hi):
    require(lo <= hi, 'interval order')
    return Q(lo.numerator * SCALE // lo.denominator, SCALE), Q(
        -((-hi.numerator * SCALE) // hi.denominator), SCALE)


def logarithm(x):
    """Atanh expansion: 120 positive terms and a geometric tail bound."""
    require(Q(1) <= x <= Q(2), 'log reduction domain')
    z = (x - 1) / (x + 1)
    term, total = z, Q(0)
    for j in range(120):
        total += 2 * term / (2*j + 1)
        term *= z*z
    return total, total + 2 * term / (241 * (1-z*z))


def exponential(x):
    """Positive Taylor terms; bound the remaining ratios by x/42."""
    require(Q(0) <= x < Q(1, 100), 'positive exp domain')
    term = total = Q(1)
    for j in range(1, 41):
        term *= x / j
        total += term
    next_term = term * x / 41
    return total, total + next_term / (1 - x / 42)


@lru_cache(None)
def power_interval(rank):
    require(type(rank) is int and 0 <= rank <= 48, 'power rank')
    if rank in (0, 1):
        return Q(rank), Q(rank)
    shift = rank.bit_length() - 1
    a, b = logarithm(Q(rank, 1 << shift))
    c, d = logarithm(Q(2))
    low, high = rounded_interval(a + shift*c, b + shift*d)
    el, _ = exponential(EXPONENT * low)
    _, eh = exponential(EXPONENT * high)
    return rounded_interval(Q(rank) / eh, Q(rank) / el)


def add(*terms):
    result = {}
    for factor, vector in terms:
        for rank, coefficient in vector.items():
            result[rank] = result.get(rank, Q(0)) + factor * coefficient
    return {rank: value for rank, value in result.items() if value}


def atom(rank):
    return {rank: Q(1)} if rank else {}


def dual():
    p9 = add((Q(1, 5), atom(3)), (-Q(1, 5), atom(48)))
    p8 = add((Q(3, 4), p9), (-Q(1, 4), atom(5)))
    pi = {
        9: p9, 8: p8, 7: add((2, p8), (-1, p9)),
        6: add((3, p8), (-2, p9)),
        5: add((-1, atom(5))), 4: add((1, atom(1)), (-1, atom(5))),
    }
    mu = {8: add((-1, p8)), 16: add((-2, p8)),
          32: add((-4, p8)), 48: atom(48)}
    return pi, mu


def multiset_patterns(capacity):
    """Emit each ascending width multiset once, without count-bound recursion."""
    counts = [0] * len(WIDTHS)

    def visit(start, used):
        yield tuple(counts)
        for index in range(start, len(WIDTHS)):
            width = WIDTHS[index]
            if used + width <= capacity:
                counts[index] += 1
                yield from visit(index, used + width)
                counts[index] -= 1
    yield from visit(0, 0)


def residual(capacity, counts, pi, mu):
    remaining = capacity - sum(w*n for w, n in zip(WIDTHS, counts))
    return add((1, atom(remaining)), (-1, mu[capacity]),
               *((-n, pi[w]) for w, n in zip(WIDTHS, counts)))


def evaluate(vector):
    lo = hi = Q(0)
    for rank, coefficient in vector.items():
        a, b = power_interval(rank)
        lo += coefficient * (a if coefficient >= 0 else b)
        hi += coefficient * (b if coefficient >= 0 else a)
    return lo, hi


def demand(flow):
    x5, x6, x7, x8, x9 = map(Q, flow)
    return (234+x5, 18-x5+x6, 162-x6+x7,
            477-x7+x8, 864-x8+x9, 1917-x9)


def region(flow):
    x5, x6, x7, x8, x9 = map(Q, flow)
    return (min(flow) >= 0 and x5 <= 18+x6
            and x6+x7+x8+x9 <= 48
            and x7+x8 <= 30+x6+x9
            and 3*x7 <= 88+x6+x8+x9)


def face_parameters(d):
    a, b, c, d7, d8, d9 = map(Q, d)
    k = d7 - 448
    ell = (d8 - 672 - c) / 2
    g = 448 - a - b - c - (k + ell)/2
    z = (d9 - d7 - 3*a - 3*b - 2*c - 3*g) / 5
    feasible = (min(a, b, c, g) >= 0 and 0 <= z <= 448
                and max(Q(0), -k) <= min(Q(448), ell))
    return feasible, (a, b, c, k, ell, g, z)


def check_witness(rows, d):
    require(set(rows) == EXPECTED_TIGHT, 'witness support')
    require(min(rows.values()) >= 0, 'nonnegative witness')
    require(tuple(sum(value*pattern[i] for (_, pattern), value in rows.items())
                  for i in range(6)) == tuple(d), 'helper demand witness')
    require({cap: sum(value for (c0, _), value in rows.items() if c0 == cap)
             for cap in CAPACITIES} == {8: 672, 16: 448, 32: 448, 48: 448},
            'bin demand witness')


def witness(d):
    feasible, (a, b, c, k, ell, g, z) = face_parameters(d)
    require(feasible, 'demand outside twelve-column face')
    u = max(Q(0), -k)
    e = max(Q(0), u + (k-ell)/2)
    rows = {
        (8, (0, 0, 0, 0, 1, 0)): Q(672),
        (16, (0, 0, 0, 0, 2, 0)): u,
        (16, (0, 0, 0, 1, 0, 1)): 448-u,
        (32, (0, 0, 0, 0, 0, 3)): g,
        (32, (0, 0, 0, 0, 4, 0)): (ell-k)/2-u+e,
        (32, (0, 0, 0, 1, 2, 1)): k+u-2*e,
        (32, (0, 0, 0, 2, 0, 2)): e,
        (32, (0, 0, 1, 0, 1, 2)): c,
        (32, (0, 1, 0, 0, 0, 3)): b,
        (32, (1, 0, 0, 0, 0, 3)): a,
        (48, (0, 0, 0, 0, 0, 0)): 448-z,
        (48, (0, 0, 0, 0, 0, 5)): z,
    }
    check_witness(rows, d)
    return rows


def rejected(call, message):
    try:
        call()
    except ValueError:
        return message
    raise ValueError('control accepted: ' + message)


def main():
    package = Path(__file__).resolve().parent
    model = json.loads((package / 'MODEL.json').read_text())
    check_model(model)
    pi, mu = dual()
    tight, strict, total = set(), [], 0
    for cap in CAPACITIES:
        seen = set()
        for p in multiset_patterns(cap):
            require(p not in seen, 'duplicate multiset')
            seen.add(p)
            total += 1
            rc = residual(cap, p, pi, mu)
            if not rc:
                tight.add((cap, p))
            else:
                lo, hi = evaluate(rc)
                require(lo > 0, 'strict reduced cost enclosure')
                strict.append((lo, hi, cap, p))
    require(total == 2551 and tight == EXPECTED_TIGHT, 'complete tight face')
    maxima = (Q(18), Q(48), Q(88, 3), Q(30), Q(48))
    tested = whole_bin_boundaries = 0
    for i, maximum in enumerate(maxima):
        for value in (Q(0), maximum/2, maximum):
            flow = [Q(0)]*5
            flow[i] = value
            require(region(flow), 'axis boundary region')
            require(face_parameters(demand(flow))[0], 'axis closed-form feasibility')
            rows = witness(demand(flow))
            tested += 1
            if value == maximum:
                require(all((360*count).denominator == 1 for count in rows.values()),
                        'T360 whole-bin axis boundary')
                require(all((360*count).denominator == 1 for count in demand(flow)),
                        'T360 whole-helper axis boundary')
                whole_bin_boundaries += 1
        flow[i] = maximum + Q(1, 1000)
        require(not region(flow) and not face_parameters(demand(flow))[0],
                'axis beyond maximum rejected')
    simultaneous = (Q(0), Q(28), Q(28), Q(0), Q(0))
    require(not region(simultaneous), 'simultaneous individual ranges control')
    require(face_parameters(demand(simultaneous))[1][5] == -2,
            'simultaneous obstruction is minus two rank32 triple9 columns')
    controls = [rejected(lambda: witness(demand(simultaneous)),
                         'joint_28_28_outside_tight_face')]
    altered = dict(pi)
    altered[9] = add((1, pi[9]), (Q(1, 10**30), atom(1)))
    lo, hi = evaluate(residual(16, (0, 0, 0, 1, 0, 1), altered, mu))
    require(hi < 0, 'dual perturbation semantic rejection')
    controls.append('width9_dual_increased_1e-30')
    for key, value, label in [
        ('a', '1/2', 'changed_exponent'),
        ('demands', [234, 18, 162, 478, 864, 1917], 'changed_inventory'),
        ('expected_axis_ranges', ['18', '49', '88/3', '30', '48'], 'inflated_range'),
        ('extras', model['extras'][:1], 'missing_extra_tight_column'),
    ]:
        changed = dict(model)
        changed[key] = value
        controls.append(rejected(lambda changed=changed: check_model(changed), label))
    zero = (Q(0),)*5
    changed_rows = witness(demand(zero))
    changed_rows[(8, (0, 0, 0, 0, 1, 0))] += Q(1, 2)
    controls.append(rejected(lambda: check_witness(changed_rows, demand(zero)),
                             'changed_witness_half_bin'))
    # Exhaust finite rational test points of the equivalence and constructive map.
    from itertools import product
    grid = (Q(0), Q(1), Q(18), Q(28), Q(30), Q(48))
    inside = outside = 0
    for flow in product(grid, repeat=5):
        accepted = region(flow)
        require(accepted == face_parameters(demand(flow))[0], 'region equivalence grid')
        if accepted:
            witness(demand(flow))
            inside += 1
        else:
            outside += 1
    minimum = min(strict)
    result = {
        'status': 'PASS_INDEPENDENT_STAGED544_JOINT_PRICE_REGION',
        'exponent': str(EXPONENT), 'patterns': total,
        'symbolically_tight_patterns': len(tight),
        'strict_patterns': len(strict),
        'minimum_strict_reduced_cost_lower': str(minimum[0]),
        'axis_maxima_x5_to_x9': [str(x) for x in maxima],
        'axis_witnesses': tested,
        'T360_integral_axis_boundaries': whole_bin_boundaries,
        'region_grid_inside': inside, 'region_grid_outside': outside,
        'negative_controls': controls,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
