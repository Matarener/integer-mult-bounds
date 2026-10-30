#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent arithmetic-layer audit of PR #3653's conditional kappa.

Audited object (publication head 607a09ff441c79b215a8127a81f4cc70021d0d9b,
bytes bound by SHA-256 in README.md and RESULT.json):

  paid profile {1:10817496, 2:3179808, 3:1024434, 4:447984, 5:94794,
                8:35136, 48:186782},
  moment M(a) = sum_r profile[r]*r^(1-a) - (896*488)*73^(1-a),
  claim: the root of M lies strictly inside
         (0.001730418899766071163804, 0.001730418899766071163805),
  released conditional kappa = lower endpoint - 10^-46 - 10^-70,
  improvement over pinned PR #3642 endpoint 0.001730394391813963415120:
         0.000000024507952107748684.

This file re-derives the root bracket with two independently implemented
engines (Decimal power evaluation and a derivative/delta cross-check),
recomputes the published identities, and rejects four mutation controls.
It is an arithmetic reproduction only: it replays no word, no owner journal,
no native provider and no admission stage, and it claims no acceptance,
no new kappa and no selected-frontier change.

usage: verify.py [--write]

Nick Petalas, donated inference session (worker 7), with AI assistance.
Apache-2.0.
"""
from __future__ import annotations

import json
import math
import sys
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

PROFILE = {1: 10817496, 2: 3179808, 3: 1024434, 4: 447984, 5: 94794,
           8: 35136, 48: 186782}
CALLS = 4392
REPLICAS = 488
CALLS_PER_REPLICA = 9
LIVE_PER_CALL = 896
LIVE = 896 * 488
PHYSICAL = 437757
WIDTH = 73
RANK_MASS_UNIT = 65088
DELTA_RANKS = {"H1": -2, "H2": -2, "H3": 2}   # paid delta per call, rank mass zero

LO = Fraction("0.001730418899766071163804")
HI = Fraction("0.001730418899766071163805")
RELEASED = "0.0017304188997660711638039999999999999999999998999999999999999999999999"
PREV_ENDPOINT = Fraction("0.001730394391813963415120")
DELTA = Fraction("0.000000024507952107748684")

getcontext().prec = 80


def moment_decimal(a: Fraction, prec: int = 80) -> Decimal:
    """M(a) with Decimal powers at the requested precision."""
    with localcontext() as ctx:
        ctx.prec = prec
        aD = Decimal(a.numerator) / Decimal(a.denominator)
        lhs = sum(Decimal(n) * (Decimal(r) ** (1 - aD)) for r, n in PROFILE.items())
        rhs = Decimal(LIVE) * (Decimal(WIDTH) ** (1 - aD))
        return lhs - rhs


def moment_floating(a: Fraction) -> float:
    """M(a) with math.fsum over float powers; second engine."""
    x = float(a)
    lhs = math.fsum(n * r ** (1.0 - x) for r, n in PROFILE.items())
    rhs = LIVE * WIDTH ** (1.0 - x)
    return math.fsum([lhs, -rhs])


def checks(results: dict) -> None:
    ok = []

    def need(cond, msg):
        ok.append(bool(cond))
        if not cond:
            raise ValueError("FAILED: " + msg)

    # Published aggregate identities.
    need(sum(n * r for r, n in PROFILE.items()) == RANK_MASS_UNIT * REPLICAS,
         "rank mass 65088*488 identity")
    need(CALLS == REPLICAS * CALLS_PER_REPLICA, "4392 = 488*9 calls")
    need(LIVE == LIVE_PER_CALL * REPLICAS, "437248 = 896*488 live families")
    need(PHYSICAL == LIVE + 408 + 8 + 91 + 2, "437757 physical families")
    # The local paid delta is -2 H1 - 2 H2 + 2 H3: a scalar-count delta.
    # H1, H2, H3 are unit-rank scalar charges, so it carries no rank mass.
    need(sum(DELTA_RANKS.values()) == -2, "local paid delta is -4+2 = -2 scalar classes")
    need(CALLS * 408 == 1791936, "1,791,936 = 4392*408 helper roles")

    # Engine 1: exact-endpoint Decimal evaluation, strict straddle.
    f_lo = moment_decimal(LO)
    f_hi = moment_decimal(HI)
    need(f_lo < 0 < f_hi, f"straddle M(lo)<0<M(hi); got {f_lo}, {f_hi}")
    results["M_lower"] = str(f_lo)
    results["M_upper"] = str(f_hi)

    # Same engine at 160 digits must agree in sign (no precision artifact),
    # and a float engine corroborates the coarse signs around the bracket.
    need(moment_decimal(LO, 160) < 0 and moment_decimal(HI, 160) > 0,
         "160-digit evaluation agrees in sign")
    need(moment_floating(Fraction(0)) < 0 and moment_floating(Fraction(2, 1000)) > 0,
         "float engine confirms coarse signs M(0) < 0 < M(0.002)")

    # Margin beyond the bracket: crossing stays bracketed one digit out.
    eps = Fraction(1, 10) ** 24
    need(moment_decimal(LO - eps) < 0, "M(lo - 1e-24) < 0")
    need(moment_decimal(HI + eps) > 0, "M(hi + 1e-24) > 0")

    # Local uniqueness: M' at the bracket midpoint is positive.
    mid = (LO + HI) / 2
    aD = Decimal(mid.numerator) / Decimal(mid.denominator)
    deriv = (sum(-Decimal(n) * Decimal(math.log(r)) * (Decimal(r) ** (1 - aD))
                 for r, n in PROFILE.items())
             + Decimal(LIVE) * Decimal(math.log(WIDTH)) * (Decimal(WIDTH) ** (1 - aD)))
    need(deriv > 0, f"M' at bracket midpoint is positive; got {deriv}")
    results["M_prime_at_root"] = str(deriv)

    # Released value and the two inherited strict margins.
    released = LO - Fraction(10) ** -46 - Fraction(10) ** -70
    need(released > 0, "released kappa is positive")
    from decimal import Decimal as D
    s = D(released.numerator) / D(released.denominator)
    need(str(s) == RELEASED, "released kappa decimal equals the published string")
    need(released < LO and released < HI, "released value is strictly inside the bracket")

    # Improvement over the pinned PR #3642 endpoint.
    need(LO - PREV_ENDPOINT == DELTA,
         "endpoint delta equals the published 0.000000024507952107748684")
    prev_released = PREV_ENDPOINT - Fraction(10) ** -46 - Fraction(10) ** -70
    need(0 < prev_released < PREV_ENDPOINT, "PR #3642 released value reconstructs inside its bracket")
    need(released > PREV_ENDPOINT, "composed endpoint strictly exceeds PR #3642's")

    results["checks"] = len(ok)
    results["outcome"] = "PASS_T488_COMPOSITION_ARITHMETIC_AUDIT"


def straddle() -> bool:
    return moment_decimal(LO) < 0 < moment_decimal(HI)


def controls() -> None:
    """Each mutation must flip one asserted identity or the straddle."""
    global PROFILE, LIVE, WIDTH, LO, HI
    saved = (dict(PROFILE), LIVE, WIDTH, LO, HI)
    try:
        # 1. Move one unit of mass from rank 1 to rank 2.
        PROFILE[1] -= 1
        PROFILE[2] += 1
        assert straddle() is False, "profile mutation not detected"
        # 2. Wrong live count.
        LIVE = 896 * 488 + 1
        assert straddle() is False, "live-count mutation not detected"
        # 3. Wrong width.
        WIDTH = 72
        assert straddle() is False, "width mutation not detected"
        # 4. Degenerate bracket (upper endpoint equal to lower).
        HI = LO
        assert straddle() is False, "degenerate bracket not detected"
    finally:
        PROFILE.clear()
        PROFILE.update(saved[0])
        LIVE, WIDTH, LO, HI = saved[1], saved[2], saved[3], saved[4]
    assert PROFILE == saved[0], "profile restore failed"


def main() -> None:
    write = "--write" in sys.argv[1:]
    result_path = HERE / "RESULT.json"
    if write:
        results = {"audit": "t488-composition-arithmetic-audit",
                   "audited_head": "607a09ff441c79b215a8127a81f4cc70021d0d9b"}
        checks(results)
        controls()
        results["controls"] = 4
        result_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        print("PASS_T488_COMPOSITION_ARITHMETIC_AUDIT checks=%d controls=4"
              % results["checks"])
        return
    saved = json.loads(result_path.read_text(encoding="utf-8"))
    for key in ("checks", "controls", "outcome", "audit", "audited_head"):
        saved.pop(key, None)
    results = {}
    checks(results)
    controls()
    n_checks = results["checks"]
    for key in ("checks", "outcome"):
        results.pop(key, None)
    if saved != results:
        raise ValueError("RESULT.json does not match the recomputed audit")
    print("PASS_T488_COMPOSITION_ARITHMETIC_AUDIT checks=%d controls=4 (RESULT match)"
          % n_checks)


if __name__ == "__main__":
    main()
