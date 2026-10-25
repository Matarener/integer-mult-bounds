#!/usr/bin/env python3
"""Rational arithmetic reused from Clear1nsight PR3946, head 8dec5c663ace6285aeee49ec3f8eeae9a8bc9a58.

Chris R / Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
No predecessor executable is imported. See PROOF.md for the interval argument.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache

M, W, R = 73, Q(896, 9), 51
GRID = 1 << 80


def need(ok, why):
    if not ok:
        raise ValueError(why)


def outward(lo, hi):
    return Q((lo.numerator * GRID) // lo.denominator, GRID), Q(-((-hi.numerator * GRID) // hi.denominator), GRID)


@lru_cache(None)
def integral_log(y, panels=1024):
    """Midpoint lower / trapezoid upper for integral_1^y 1/t dt."""
    y = Q(y)
    need(1 <= y <= 2 and type(panels) is int and panels > 0, 'quadrature domain')
    if y == 1:
        return Q(0), Q(0)
    h = (y - 1) / panels
    lo = h * sum(1 / (1 + (Q(j) + Q(1, 2)) * h) for j in range(panels))
    hi = h * ((1 + 1 / y) / 2 + sum(1 / (1 + j * h) for j in range(1, panels)))
    return outward(lo, hi)


@lru_cache(None)
def logarithm(x):
    x = Q(x)
    need(x >= 1, 'logarithm domain')
    powers = 0
    while x > 2:
        x /= 2
        powers += 1
    lo, hi = integral_log(x)
    two_lo, two_hi = integral_log(Q(2))
    return outward(lo + powers * two_lo, hi + powers * two_hi)


def exponential(lo, hi, degree=6):
    need(0 <= lo <= hi <= Q(1, 2), 'exponential domain')
    need(type(degree) is int and degree >= 1, 'exponential degree')
    lsum = usum = lterm = uterm = Q(1)
    for j in range(1, degree + 1):
        lterm *= lo / j
        uterm *= hi / j
        lsum += lterm
        usum += uterm
    first = uterm * hi / (degree + 1)
    tail = first / (1 - hi / (degree + 2))
    return outward(lsum, usum + tail)


@lru_cache(None)
def cost(rank, a):
    need(type(rank) is int and 0 < rank < M and a >= 0, 'child domain')
    lo, hi = logarithm(Q(M, rank))
    lo, hi = exponential(a * lo, a * hi)
    return outward(Q(rank, M) * lo, Q(rank, M) * hi)

def expand(packet, name):
    events = []

    def visit(sequence):
        for event in sequence:
            tag = event[0]
            if tag == 'retained_core':
                need(event[1] in ('forward', 'backward'), 'core orientation')
                visit(packet['core_words'][event[1]])
            elif tag in ('private_sweep', 'cover_sweep'):
                visit(event[2])
            else:
                need(tag in ('scalar', 'climb', 'adapter', 'residual_adapter',
                             'phase', 'native_line', 'cover_map'), 'unknown event')
                events.append(event)

    visit(packet['programs'][name])
    return events


def profile(packet, events):
    out = Counter()
    for event in events:
        if event[0] == 'climb':
            rank = event[5]
        elif event[0] == 'native_line':
            record = packet['native_line_recipes'][event[2]]
            rank = record['rank']
            need(record['recipe']['rank'] == rank, 'wrapper recipe rank')
        else:
            continue
        need(type(rank) is int and 0 < rank < M, 'literal child rank')
        out[rank] += 1
    return dict(sorted(out.items()))


def moment(base, decoder_pair, centre, rank8, a, idle_rank=R):
    need(all(type(r) is int and 0 < r < M and Q(n) >= 0 for r,n in base.items()), 'local profile domain')
    need(2 * idle_rank**2 < M**2 and idle_rank >= max(base), 'halving / relaxation rank')
    need(Q(decoder_pair) >= 0 and Q(centre) >= 0, 'negative budget charge')
    local = {r: Q(n) for r, n in base.items()}
    local[1] += Q(decoder_pair, 2)
    if rank8:
        local[8] = Q(8)
    total = (M - 1) * W + centre
    paid = sum(r * n for r, n in local.items())
    idle = total - paid
    need(idle >= 0, 'negative idle mass')
    lo = hi = Q(0)
    for rank, number in local.items():
        clo, chi = cost(rank, a)
        lo += number * clo
        hi += number * chi
    clo, chi = cost(idle_rank, a)
    return outward((lo + idle / idle_rank * clo) / W,
                   (hi + idle / idle_rank * chi) / W)


def decimal_interval(pair, digits=12):
    scale = 10**digits
    lo, hi = pair
    l = lo.numerator * scale // lo.denominator
    u = -((-hi.numerator * scale) // hi.denominator)
    return {'lower': str(Q(l, scale)), 'upper': str(Q(u, scale)),
            'decimal_lower': f'{l // scale}.{l % scale:0{digits}d}',
            'decimal_upper': f'{u // scale}.{u % scale:0{digits}d}'}
