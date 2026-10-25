#!/usr/bin/env python3
"""Exact tighter sufficient ranks for PR4359's conditional finite compiler.

Standard library only; no generated file is modified unless --out is given.
Apache-2.0. Substantial OpenAI/Codex assistance. The compiler and its inherited
native premises are those of PR4359, based on Jacob Alan Sussman's Theorem 1G.
"""
import argparse
from functools import lru_cache
from fractions import Fraction as Q
import json
from math import factorial
from pathlib import Path


CASES = (
    {"family": "complex", "targets": {6:192, 7:56, 8:93, 9:1229, 25:448, 57:224},
     "paid": {1:17623, 2:5065, 3:1738, 4:714, 5:254},
     "tested_saving": "0.002305", "uniform_saving": "0.002304",
     "theta_upper": "9/10", "old_H0": 60000040, "old_H1": 276540184361},
    {"family": "BIT", "targets": {8:3073, 22:444, 50:222},
     "paid": {1:9261, 2:9394, 3:553, 4:308, 5:714, 6:77, 7:1465},
     "tested_saving": "0.002769", "uniform_saving": "0.002760",
     "theta_upper": "15/16", "old_H0": 10666731, "old_H1": 6552928412},
)


def need(ok, message):
    if not ok:
        raise AssertionError(message)


@lru_cache(maxsize=None)
def log_interval(value):
    """Rational lower/upper bounds from the positive atanh series."""
    value = Q(value)
    need(value > 0, "logarithm needs positive argument")
    if value < 1:
        lo, hi = log_interval(1/value)
        return -hi, -lo
    power = 0
    while value > 2:
        value /= 2
        power += 1
    u = (value-1)/(value+1)
    count = 96
    lo = 2*sum((u**(2*j+1)/(2*j+1) for j in range(count)), Q(0))
    tail = 2*u**(2*count+1)/((2*count+1)*(1-u*u))
    hi = lo+tail
    if power:
        a, b = log_interval(Q(2))
        lo, hi = lo+power*a, hi+power*b
    return lo, hi


def exp_interval(value):
    need(0 <= value < Q(1,10), "small positive exponential argument")
    count = 32
    lo = sum((value**j/factorial(j) for j in range(count+1)), Q(0))
    tail = value**(count+1)/factorial(count+1)/(1-value/(count+2))
    return lo, lo+tail


def moment_margin(targets, paid, saving):
    """Enclose sum targets*k^(1-saving) - sum paid*r^(1-saving)."""
    lo = hi = Q(0)
    for rank in sorted(set(targets) | set(paid)):
        count = targets.get(rank, 0)-paid.get(rank, 0)
        a, b = log_interval(Q(rank))
        lower = Q(rank)/exp_interval(saving*b)[1]
        upper = Q(rank)/exp_interval(saving*a)[0]
        lo += count*(lower if count >= 0 else upper)
        hi += count*(upper if count >= 0 else lower)
    return lo, hi


def rank_bound(test_saving, uniform_saving, m, theta_bar):
    """Conditional bound: caller supplies the source/exit recurrence hypotheses.

    In particular m*E(n)/n < 16*n^(-(1-theta_bar)) and the strict tested
    superpotential must hold. This function does not assert either premise.
    """
    test_saving, uniform_saving, theta_bar = map(Q, (test_saving, uniform_saving, theta_bar))
    t, z = 1-test_saving, 1-uniform_saving
    z0, h = (t+z)/2, 1-theta_bar
    delta = z0-t
    need(0 < t < z0 < z < 1 and 0 < h < 1 and m >= 2,
         "strict rational savings and exit contraction")
    log2_lo, log2_hi = log_interval(Q(2))
    logm_lo, logm_hi = log_interval(Q(m))
    invz_lo, invz_hi = log_interval(1/z0)
    # eta=z0*m^(z0-1); these enclose -log(eta).
    debt_lo = invz_lo+(1-z0)*logm_lo
    debt_hi = invz_hi+(1-z0)*logm_hi
    H0 = ((4+debt_hi/(delta*log2_lo))/h).__ceil__()
    need(H0 >= m.bit_length(), "threshold covers the finite base range")
    exit_gap = delta*(h*H0-4)*log2_lo-debt_hi
    need(exit_gap >= 0, "exit coefficient is at most eta")
    final_ratio = H0*(1-z0)/(z-z0)
    H1 = final_ratio.__floor__()+1
    final_gap = H1*(z-z0)-H0*(1-z0)
    need(H1 > H0 and final_gap > 0, "strict winning-rank inequality")
    # The interval width is small enough to determine these two integers.
    need(debt_lo > delta*(h*(H0-1)-4)*log2_hi,
         "one smaller H0 violates the same sufficient exit inequality")
    need((H1-1)*(z-z0) <= H0*(1-z0),
         "one smaller H1 fails the strict final inequality")
    return {"H0": H0, "H1": H1, "t": str(t), "z0": str(z0), "z": str(z),
            "delta": str(delta), "h": str(h), "m": m,
            "eta_definition": "z0*m^(z0-1)",
            "exit_condition": "delta*(h*H0-4)*log(2) >= -log(eta)",
            "certified_exit_gap_positive": exit_gap > 0,
            "strict_final_power_gap": str(final_gap),
            "controls": {"H0_minus_one_rejected": True, "H1_minus_one_rejected": True}}


def verify():
    rows = []
    for case in CASES:
        m, kmin, rmax = max(case["targets"]), min(case["targets"]), max(case["paid"])
        theta = Q(case["theta_upper"])
        h = 1-theta
        need(1 <= rmax < kmin <= m, "native mixed rank separation")
        need(rmax**theta.denominator < kmin**theta.numerator, "exit exponent bound")
        need(m**h.numerator < 2**h.denominator and 2*rmax <= 16,
             "inherited exit coefficient constant 16")
        surplus = sum(k*v for k,v in case["targets"].items())-sum(k*v for k,v in case["paid"].items())
        need(surplus > 0, "rank-one potential proves L(n)<=n")
        margin = moment_margin(case["targets"], case["paid"], Q(case["tested_saving"]))
        need(margin[0] > 0, "strict source profile superpotential")
        need(moment_margin(case["targets"], case["paid"], Q("0.004"))[1] < 0,
             "unsupported .004 superpotential is rejected")
        result = rank_bound(case["tested_saving"], case["uniform_saving"], m, theta)
        need(result["H1"] < case["old_H1"], "strictly smaller sufficient fixed rank")
        rows.append({**case, **result, "rank_one_surplus": surplus,
                     "strict_superpotential_verified": True,
                     "old_to_new_log_rank_ratio": str(Q(case["old_H1"], result["H1"])),
                     "materialized_winning_word": False})
    return {"status": "PASS_EXACT_TIGHTER_TEMPLATE_RANKS", "cases": rows,
            "scope": "Conditional quantitative refinement of PR4359's finite compiler; unchanged uniform savings and inherited native, precision, and outer premises.",
            "new_kappa_from_template_refinement": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = verify()
    serialized = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.out:
        args.out.write_text(serialized)
    print(serialized, end="")
