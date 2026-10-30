"""Exact design screens, not a new finite supplier or multiplication bound.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse
import importlib.util
import json
import math

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('shared_block_tools',
    HERE.parent/'shared-core-blocks/audit.py')
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
require, encode = B.require, B.encode


def ceil(x):
    return -(-x.numerator//x.denominator)


def rank_floor(v):
    """Triangle-free symmetrized support, diagonal-one scalar matrix."""
    k = (math.isqrt(1+4*v)-1)//2
    while k*(k+1) < v:
        k += 1
    return k


def span_loss_floor(v, r):
    """Copied channels of dimension r cannot mix distinct source images.

    If K channels are used, b of them with dimension >r, then
    v<=K(b+1)-b(b-1)/2 and L>=r*K+b. Minimize this integer relaxation.
    """
    require(v >= 1 and r >= 1, 'positive ports and block rank')
    K = (math.isqrt(9+8*v)-3)//2
    while K*(K+3)//2 < v:
        K += 1
    best = (r*v, v, 0)
    while r*K < best[0]:
        lo, hi = -1, K
        while hi-lo > 1:
            b = (lo+hi)//2
            if K*(b+1)-b*(b-1)//2 >= v:
                hi = b
            else:
                lo = b
        best = min(best, (r*K+hi, K, hi))
        K += 1
    return dict(channels=best[1], larger_channels=best[2], loss=best[0])


def first_span_scale(r, loss_per_port):
    # A bounded *exact* scalar enumeration, not a geometry search.
    for v in range(1, 100001):
        bound = span_loss_floor(v, r)
        if bound['loss'] <= loss_per_port*v:
            return dict(minimum_ports=v, **bound)
    raise ValueError('scale screen bound exceeded')


def minimum_scale(alpha, strict=False):
    """Necessary v<=k(k+1), k/v <= alpha (or < alpha).

    This is only an integer feasibility screen, not an existence bound.
    """
    require(0 < alpha < 1, 'rank fraction')
    k = max(1, (1/alpha).numerator//(1/alpha).denominator
            if strict else ceil(1/alpha)-1)
    v = k//alpha+1 if strict else ceil(k/alpha)
    v = int(v)
    require(v <= k*(k+1), 'first feasible integer scale')
    require((Q(k, v) < alpha) if strict else (Q(k, v) <= alpha),
            'rank fraction at first scale')
    return dict(central_rank_at_first_scale=k, minimum_ports=v)


def loss_allowance(d, r, rho, saving):
    p = B.ideal_budget(d, r, saving, rho)
    lo, hi = p['moment_interval']
    a, b = p['auxiliary_cost_interval']
    W = 2+rho
    return W*(1-hi)/b, W*(1-lo)/a


def graph_screen(rows):
    n = len(rows)
    require(all((row >> i)&1 for i, row in enumerate(rows)), 'unit diagonal')
    adj = [set() for _ in rows]
    for i in range(n):
        for j in range(i):
            if (rows[i] >> j)&1 or (rows[j] >> i)&1:
                adj[i].add(j)
                adj[j].add(i)
    triangle_free = all(not (adj[i] & adj[j])
                        for i in range(n) for j in adj[i])
    k = B.H.binary_rank(rows)
    if triangle_free:
        # Each neighborhood gives a literal identity principal submatrix.
        for neighbors in adj:
            for i in neighbors:
                require(all(((rows[i] >> j)&1) == (i == j)
                            for j in neighbors), 'neighborhood identity')
        require(max(map(len, adj), default=0) <= k, 'degree <= scalar rank')
        require(n <= k*(k+1), 'triangle-free rank/port inequality')
        require(n <= k*(k+3)//2, 'elementary triangle-free Ramsey inequality')
    return dict(v=n, rank=k, triangle_free=triangle_free,
                maximum_degree=max(map(len, adj), default=0))


def odd_cycle_control(k):
    n = 2*k+1
    blocks = [set((i+2*j) % n for j in range(k)) for i in range(n)]
    require(all(not (blocks[i] & blocks[(i+1) % n]) for i in range(n)),
            'coordinate cycle annihilations')
    require(all(len(blocks[i] & blocks[(i+2) % n]) == k-1 for i in range(n)),
            'two-step dimension bound attained')
    require(k == k*(n-2*k), 'odd-cycle inequality attained')
    return dict(odd_cycle_length=n, d=n, r=k,
                coordinate_blocks=[sorted(x) for x in blocks],
                status='Geometry control only; commuting labels, no supplier.')


def folded_cube(q):
    """Folded odd q-cube: vertices F2^(q-1); unit generators plus all-ones."""
    require(q >= 5 and q % 2 == 1, 'odd folded cube')
    D = q-1
    n = 1 << D
    generators = [1 << i for i in range(D)]+[n-1]
    rows = [(1 << x) ^ sum(1 << (x ^ g) for g in generators)
            for x in range(n)]
    control = graph_screen(rows)
    # Exact C^2=0 in F2: independent translation matrices commute, and
    # (q+1) is even. Also replay every row in these finite controls.
    for row in rows:
        product = 0
        left = row
        while left:
            bit = left & -left
            product ^= rows[bit.bit_length()-1]
            left ^= bit
        require(product == 0, 'binary nilpotence')
    # Rational Walsh characters diagonalize the same integer matrix.
    eigenvalues = Counter()
    for w in range(D+1):
        eigenvalues[1+D-2*w+(-1)**w] += math.comb(D, w)
    rational_rank = sum(count for eig, count in eigenvalues.items() if eig)
    # General-family rank proof uses cube splitting; finite values are
    # checked rather than assuming that formula in elimination.
    expected = (1 << (D-1))-(1 << (D//2-1))
    require(control['rank'] == expected, 'folded cube rank formula control')
    require(control['rank'] >= Q(3, 8)*n, 'central rank fraction screen')
    return dict(q=q, odd_girth=q, **control,
                binary_rank=control['rank'], rational_rank=rational_rank,
                rank_fraction=Q(control['rank'], n),
                rational_eigenvalue_multiplicities=dict(sorted(eigenvalues.items())),
                binary_square_zero=True)


def audit():
    bit, complex_s = Q(2, 25), Q(3, 40)
    third = B.ideal_budget(3, 1, bit, Q(0), Q(0))['moment_interval']
    third_power = B.power(Q(1, 3), bit)
    zero = tuple(3*x for x in third_power)
    require(zero[0] > 1 and third[0] > 1, 'bare triangle exclusion')
    t = Q(9, 19)
    allowances = loss_allowance(19, 9, Q(1), bit)
    alpha = tuple(x/t for x in allowances)
    scales = [minimum_scale(x, strict=True) for x in alpha]
    require(scales[0] == scales[1], 'stable minimum scale enclosure')
    colors = [int(1/x)+1 for x in alpha]
    require(colors[0] == colors[1], 'stable coloring screen')
    v = 250
    k = rank_floor(v)
    loss = 9*k
    target = B.ideal_budget(19, 9, bit, Q(1), Q(loss, 19*v))
    stronger = span_loss_floor(v, 9)
    stronger_moment = B.ideal_budget(19, 9, bit, Q(1),
                                    Q(stronger['loss'], 19*v))
    require(target['moment_interval'][0] > 1, 'copied-center budget rejected')
    require(loss > 19, 'hypothetical loss is insufficient')

    cube_endpoints = []
    for s in (bit, complex_s):
        # At t=0, all nonzero relaxed children have relative width 1/3.
        a, b = B.power(Q(1, 3), s)
        rho = Q(3, 8)
        zero = ((6+3*rho)*a/(2+rho), (6+3*rho)*b/(2+rho))
        half = B.ideal_budget(2, 1, s, rho, rho/2)['moment_interval']
        require(zero[0] > 1 and half[0] > 1, 'concave endpoint exclusion')
        cube_endpoints.append(dict(saving=s, at_zero=zero, at_half=half))

    # An initially attractive low-stock target, rejected by the span screen.
    alternate = B.shared_profile(5, 2, 1000, 200, 100,
                                 {5: 220}, {3: 1000}, {3: 1000})
    alternate['moments'] = {str(s): B.moment(alternate['child_histogram'],
                                           alternate['m'], alternate['W'], s)
                            for s in (bit, complex_s)}
    require(all(x[1] < 1 for x in alternate['moments'].values()),
            'alternative arithmetic control')
    alt_floor = span_loss_floor(1000, 2)
    require(alt_floor['loss'] > 100, 'low-stock target fails source-span floor')
    alt_paid = B.ideal_budget(5, 2, bit, Q(1, 5), Q(alt_floor['loss'], 5000))
    require(alt_paid['moment_interval'][0] > 1, 'even packed corrected cost fails')

    return dict(status='Design screens only; no new supplier or kappa.',
                scope='Uniform idempotent source blocks; diagonal-one scalar '
                      'central map, side support requiring mutual annihilation; '
                      'copied-center floor requires literal conservative '
                      'source-span readouts. Moment screens use zero gauges '
                      'and minimum-rank data paths.',
                odd_cycle_controls=[odd_cycle_control(k) for k in (2, 7, 9)],
                bare_triangle_exclusion=dict(saving=bit, at_zero=zero,
                                             at_one_third=third),
                rank_nine_target=dict(loss_ratio_allowance=allowances,
                    central_rank_fraction_ceiling=alpha,
                    necessary_chromatic_number=colors[0],
                    minimum_odd_girth=19,
                    strict_allowance_minimum_scale=scales[0],
                    fixed_loss_ratio=Q(1, 250),
                    fixed_loss_minimum_scale=minimum_scale(Q(19, 2250)),
                    fixed_loss_span_scale=first_span_scale(9, Q(19, 250))),
                rejected_250_port_budget=dict(v=v, central_rank_floor=k,
                    copied_loss_floor=loss, proposed_loss=19,
                    optimistic_moment_interval=target['moment_interval'],
                    source_span_loss_floor=stronger,
                    source_span_moment_interval=stronger_moment['moment_interval']),
                folded_cube_controls=[folded_cube(q) for q in (5, 7, 9, 11)],
                folded_cube_family_endpoint_screen=cube_endpoints,
                low_stock_alternative=dict(profile=alternate,
                    central_rank_floor=rank_floor(1000),
                    source_span_floor=alt_floor,
                    corrected_moment_interval=alt_paid['moment_interval'],
                    status='Rejected in the copied-center model despite '
                           'passing its originally proposed histogram.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    value = encode(audit())
    if args.write:
        args.write.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    if args.check:
        require(value == json.loads(args.check.read_text()), 'saved design certificate')
    print('Interaction-family design screens passed; no new supplier or kappa.')
