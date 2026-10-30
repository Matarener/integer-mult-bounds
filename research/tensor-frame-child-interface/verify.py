#!/usr/bin/env python3
"""Separate the scalar #4088 child bill from a factorwise tensor repetition.

The free-word lift in research/unconditional-batched-crt/COMPLEX.md replaces
each rank-r native transition by one child of rank r*f inside width 73*f.
#4184 certifies the algebra and leaves that frame/child coordinate unpriced.
This checker does not import that audit or the predecessor moment engine.
"""
from fractions import Fraction as Q
import json
import sys
from pathlib import Path

sys.set_int_max_str_digits(0)

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/staged544-mixed-fourth-entry/RESULT.json"
RECIPES = (
    ROOT / "research/staged544-mixed-fourth-entry/recipe/RECORD-base.json",
    ROOT / "research/staged544-mixed-fourth-entry/recipe/RECORD-extra.json",
)
WIDTH = 73
ROLES = 896 * 360
SCALAR_RANKS = {1, 2, 3, 4, 5, 8}


def need(ok, why):
    if not ok:
        raise SystemExit("FAIL: " + why)


def artanh_bounds(z, terms):
    need(Q(0) < z < 1, "artanh argument")
    total = Q(0)
    power = z
    square = z * z
    for j in range(terms):
        total += power / (2 * j + 1)
        power *= square
    tail = power / ((2 * terms + 1) * (1 - square))
    return total, total + tail


def ln_bounds(n, terms=80):
    need(type(n) is int and n >= 1, "positive integer")
    e = n.bit_length() - 1
    mantissa = Q(n, 1 << e)
    lo2, hi2 = artanh_bounds(Q(1, 3), terms)
    lo2, hi2 = 2 * lo2, 2 * hi2
    if mantissa == 1:
        return e * lo2, e * hi2
    z = (mantissa - 1) / (mantissa + 1)
    lo, hi = artanh_bounds(z, terms)
    return 2 * lo + e * lo2, 2 * hi + e * hi2


def exp_minus_bounds(x, terms=30):
    need(Q(0) <= x < 1, "exponential argument")
    partial = Q(0)
    term = Q(1)
    for j in range(terms + 1):
        if j:
            term *= -x / j
        partial += term
    remainder = abs(term) * x / (terms + 1)
    if (terms + 1) % 2 == 0:
        return partial, partial + remainder
    return partial - remainder, partial


def power_bounds(rank, k):
    lo, hi = ln_bounds(rank)
    # rank^(1-k) = rank * exp(-k ln rank), decreasing in the logarithm.
    elo, ehi = exp_minus_bounds(k * hi), exp_minus_bounds(k * lo)
    return rank * elo[0], rank * ehi[1]


def show(value, digits=24):
    sign = "-" if value < 0 else ""
    value = abs(value)
    scale = 10 ** digits
    digits_only = (value.numerator * scale) // value.denominator
    whole, frac = divmod(digits_only, scale)
    return f"{sign}{whole}.{frac:0{digits}d}"


def moment_bounds(profile, k):
    lo = hi = Q(0)
    for rank, count in profile.items():
        left, right = power_bounds(rank, k)
        if count >= 0:
            lo += count * left
            hi += count * right
        else:
            lo += count * right
            hi += count * left
    return lo, hi


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    profile = {int(rank): count for rank, count in result["profile"].items()}
    need(set(profile) == SCALAR_RANKS | {48}, "profile ranks")
    need(all(count > 0 for count in profile.values()), "positive counts")
    need(sum(rank * count for rank, count in profile.items()) == 65088 * 360, "rank mass")
    k = Q(result["root_lower"])
    need(k == Q("0.001730979115670792472760"), "pinned lower endpoint")
    need(Q(0) < k < Q(1, 500), "endpoint range")

    for path in RECIPES:
        record = json.loads(path.read_text(encoding="utf-8"))
        local = {int(rank): count for rank, count in record["report"]["local_profile"].items()}
        need(set(local) <= SCALAR_RANKS, path.name + " local ranks stay scalar")
        need(len(record["warps"]) == 72, path.name + " warp count")
        need("tensor" not in json.dumps(record["report"]), path.name + " report names no tensor frame")

    scalar = {**profile, WIDTH: -ROLES}
    m_lo, m_hi = moment_bounds(scalar, k)
    need(m_hi < 0, "scalar bill is strictly negative at the pinned endpoint")
    need(m_lo > -Q(1, 10**12), "scalar slack is smaller than 10^-12")

    parent = power_bounds(WIDTH, k)
    q_lo, q_hi = ROLES * parent[0], ROLES * parent[1]
    need(q_lo > 10**7, "parent term")

    def child_power(f):
        return power_bounds(f, k)

    # Factorwise repetition: f copies of every scalar child, parent width 73f.
    # One-child lift: each rank r becomes one rank r*f inside width 73f.
    samples = {}
    two_gap = None
    copy_hi_at_two = None
    for f in (1, 2, 3, 4, 8, 73):
        copy = {rank: f * count for rank, count in profile.items()}
        copy[WIDTH * f] = -ROLES
        copy_lo, copy_hi = moment_bounds(copy, k)
        lifted = {rank * f: count for rank, count in profile.items()}
        lifted[WIDTH * f] = -ROLES
        lift_lo, lift_hi = moment_bounds(lifted, k)
        samples[str(f)] = {
            "factorwise_lower": show(copy_lo),
            "factorwise_upper": show(copy_hi),
            "rank_times_f_lower": show(lift_lo),
            "rank_times_f_upper": show(lift_hi),
        }
        if f == 1:
            need(copy_hi < 0 and lift_hi < 0, "f=1 reproduces the scalar sign")
        else:
            need(copy_lo > 0, "factorwise bill is positive at f=%d" % f)
            need(lift_hi < 0, "single rf-child bill stays negative at f=%d" % f)
        if f == 2:
            two_gap = copy_lo
            copy_hi_at_two = copy_hi

    # Every integer f>=2 is at least the f=2 factorwise bill when that bill's
    # derivative in f stays positive. h(f)=f*P-Q*f^(1-k).
    p_lo = m_lo + q_lo
    f_power = child_power(2)
    # f^{-k} = exp(-k ln f) = f^(1-k)/f
    f_minus_k_hi = f_power[1] / 2
    derivative_lo = p_lo - (1 - k) * q_hi * f_minus_k_hi
    need(derivative_lo > 0, "factorwise moment increases for every f>=2")
    need(two_gap > 1000, "f=2 factorwise margin")

    # Identity check on the closed form, using the same enclosures:
    # M_copy = f*M + Q*(f - f^(1-k)), so its lower bound cannot exceed the
    # direct child-sum enclosure's upper bound.
    f = 2
    scale = child_power(f)
    closed_lo = f * m_lo + q_lo * (f - scale[1])
    need(closed_lo > 0, "closed-form factorwise lower bound")
    need(copy_hi_at_two >= closed_lo, "enclosures overlap")
    recorded_upper = Q(result["lower_moment_interval"][1])
    need(recorded_upper < 0, "pinned RESULT.json enclosure is negative")
    swollen = dict(profile)
    swollen[1] += 10**9
    swollen_hi = moment_bounds({**swollen, WIDTH: -ROLES}, k)[1]
    need(swollen_hi > 0, "a billion extra rank-1 children must fail the scalar test")

    print(json.dumps({
        "status": "PASS_TENSOR_FRAME_CHILD_GAP",
        "endpoint": str(k),
        "scalar_moment_lower": show(m_lo),
        "scalar_moment_upper": show(m_hi),
        "parent_term_lower": show(q_lo),
        "samples": samples,
        "factorwise_derivative_lower_at_f2": show(derivative_lo),
        "scope": "f=1 passes; every integer f>=2 factorwise repetition fails; the single rank-(r*f) child keeps the scalar sign",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
