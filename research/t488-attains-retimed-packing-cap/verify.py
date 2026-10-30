#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Does the composed T488 x retiming profile attain the T530 packing ceiling?

Audited objects (public, exact pins and SHA-256 in README.md and SOURCES.json):

  * PR #3642, research/staged-release-retiming-t530/packing-cap at head
    6568db75adbb61437190545f6fef1534c70e91e5. Its RETIMED-PACKING-CAP.json
    publishes the feasible primal idle bill per replica
        {1: 234, 3: 261/4, 5: 57/4, 48: 1531/4},
    the retimed local bill per call {1:2437,2:724,3:226,4:102,5:20,8:8},
    capacities per replica {8:672,16:448,32:448,48:448}, the ideal profile at
    T=740, and the fixed-inventory relaxation root bracket
        (0.001730418899766071163804, 0.001730418899766071163805).

  * PR #3653, research/retimed-t488-composition at head
    607a09ff441c79b215a8127a81f4cc70021d0d9b. Its published paid profile is
        {1:10817496,2:3179808,3:1024434,4:447984,5:94794,8:35136,48:186782}
    at 4,392 calls and 488 replicas (9 calls per replica).

The check is one exact integer identity plus its consequences:

    PROFILE_488 == 4392 * local_bill + 488 * ideal_idle_per_replica.

So the composed profile is exactly the certificate's own optimal profile at
T=488 (its published T=740 ideal profile is reproduced by the same rule as a
convention cross-check). Because the local bill enters the moment additively
and is fixed, the moment-minimising packing does not depend on the bill; a
construction already at the optimal vertex stays optimal when the bill changes.
Hence the composed profile attains the fixed-capacity relaxation ceiling, the
T530-to-T488 packing headroom is closed exactly, and no repacking inside the
certificate's model can improve the composed kappa.

Scope: this is an exact arithmetic and model-consistency audit. The optimality
of the published primal vertex is PR #3642's certificate (its 2,551-pattern
dual), cited and re-executed as recorded evidence, not re-proved here. No word,
owner journal, native provider, admission stage or selected-frontier value is
replayed. No new kappa is claimed.

usage: verify.py [--write]

Produced by Nick Petalas with AI assistance.
Apache-2.0.
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- PR #3642 packing-cap constants (quoted from the pinned public receipt) ---
BILL = {1: 2437, 2: 724, 3: 226, 4: 102, 5: 20, 8: 8}
PRE_RETIMING_BILL = {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}
IDEAL_IDLE = {1: Fraction(234), 3: Fraction(261, 4),
              5: Fraction(57, 4), 48: Fraction(1531, 4)}
CAPACITY_COUNTS = {8: 672, 16: 448, 32: 448, 48: 448}
WIDTH_INVENTORY = {4: 26, 5: 2, 6: 18, 7: 52, 8: 97, 9: 213}
CAP_ROOT = (Fraction(432604724941517790951, 250000000000000000000000),
            Fraction(346083779953214232761, 200000000000000000000000))
CAP_ROOT_DECIMAL = ("0.001730418899766071163804",
                    "0.001730418899766071163805")
LITERAL_ROOT = (Fraction(21629929897674542689, 12500000000000000000000),
                Fraction(1730394391813963415121, 1000000000000000000000000))
LITERAL_ROOT_DECIMAL = ("0.001730394391813963415120",
                        "0.001730394391813963415121")
HEADROOM = Fraction(24507952107748683, 10 ** 24)
LITERAL_TO_CAP_FLOAT = "0.999985836983108"
PATTERNS, STRICT, SYMBOLIC_ZERO = 2551, 2539, 12
IDEAL_740 = {1: 16403580, 2: 4821840, 3: 1553445, 4: 679320,
             5: 143745, 8: 53280, 48: 283235}

# --- PR #3653 composed profile (quoted from the pinned public proof) ---
PROFILE_488 = {1: 10817496, 2: 3179808, 3: 1024434, 4: 447984,
               5: 94794, 8: 35136, 48: 186782}
CALLS_488, REPLICAS_488, CALLS_PER_REPLICA = 4392, 488, 9
PROFILE_530 = {1: 11747920, 2: 3453480, 3: 1112042, 4: 486540,
               5: 103690, 8: 38160, 48: 202828}
CALLS_530, REPLICAS_530 = 4770, 530
LIVE_PER_CALL, WIDTH = 896, 73
RANK_MASS_PER_REPLICA = 65088
PHYSICAL_488 = 437757
RELEASED_488 = ("0.0017304188997660711638039999999999999999999998999999"
                "999999999999999999")
MARGINS = (Fraction(1, 10 ** 46), Fraction(1, 10 ** 70))

getcontext().prec = 80


def ideal_profile(replicas: int, calls: int) -> dict[int, Fraction]:
    """Certificate's own construction: local bill per call + optimal idle bill."""
    profile = {r: Fraction(calls * q) for r, q in BILL.items()}
    for r, q in IDEAL_IDLE.items():
        profile[r] = profile.get(r, Fraction(0)) + replicas * q
    return profile


def as_decimal(value: Fraction, digits: int) -> str:
    """Exact decimal string for a fraction whose denominator divides 10**digits."""
    assert (value * 10 ** digits).denominator == 1
    n = value.numerator * (10 ** digits // value.denominator)
    sign = "-" if n < 0 else ""
    n = abs(n)
    return f"{sign}{n // 10 ** digits}.{n % 10 ** digits:0{digits}d}"


def moment(profile: dict[int, Fraction], a: Fraction, live: int) -> Decimal:
    """M(a) = sum_r n_r*r^(1-a) - live*73^(1-a); root of M is the saving b."""
    assert 0 < a < 1 and live % LIVE_PER_CALL == 0
    e = Decimal(1) - Decimal(a.numerator) / Decimal(a.denominator)
    total = Decimal(0)
    for r, n in profile.items():
        nf = Fraction(n)
        total += (Decimal(nf.numerator) / Decimal(nf.denominator)) * (Decimal(r) ** e)
    total -= Decimal(live) * (Decimal(WIDTH) ** e)
    return total


def rank_mass(profile: dict[int, Fraction]) -> Fraction:
    return sum(Fraction(r) * n for r, n in profile.items())


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.controls = 0
        self.rows: dict[str, object] = {}

    def check(self, ok: bool, label: str) -> None:
        if not ok:
            raise SystemExit(f"FAIL {label}")
        self.checks += 1

    def control(self, rejected: bool, label: str) -> None:
        if not rejected:
            raise SystemExit(f"CONTROL NOT REJECTED {label}")
        self.controls += 1

    def record(self, key: str, value: object) -> None:
        self.rows[key] = value


def main() -> None:
    write = "--write" in sys.argv[1:]
    audit = Audit()

    # 1. Convention cross-check on the certificate's own published ideal.
    audit.check(CALLS_PER_REPLICA * 740 == 6660, "T740 has 6,660 calls")
    audit.check(ideal_profile(740, 6660) == {r: Fraction(n) for r, n in IDEAL_740.items()},
                "T740 ideal profile follows the bill + idle rule")
    audit.check(all(Fraction(n).denominator == 1 for n in ideal_profile(740, 6660).values()),
                "T740 ideal profile is integral")
    audit.record("ideal_profile_rule", "calls*bill + replicas*ideal_idle_per_replica")

    # 2. The composed profile is exactly the certificate's ideal at T=488.
    audit.check(CALLS_488 == CALLS_PER_REPLICA * REPLICAS_488, "4,392 = 488*9 calls")
    built = ideal_profile(REPLICAS_488, CALLS_488)
    audit.check(built == {r: Fraction(n) for r, n in PROFILE_488.items()},
                "composed T488 profile equals the certificate's ideal at T=488")
    audit.check(all(v.denominator == 1 for v in built.values()),
                "T488 ideal is integer-attained (488 = 0 mod 4)")
    audit.record("identity", "PROFILE_488 == 4392*bill + 488*ideal_idle_per_replica")

    # 3. Aggregate identities.
    audit.check(rank_mass(built) == RANK_MASS_PER_REPLICA * REPLICAS_488,
                "composed rank mass is 65088*488")
    live = LIVE_PER_CALL * REPLICAS_488
    audit.check(live == 437248, "live stock is 896*488")
    audit.check(PHYSICAL_488 == live + 408 + 8 + 91 + 2,
                "physical 437757 = live + 408 helpers + 8 centers + 91 buffers + 2 fields")
    audit.record("rank_mass", 65088 * 488)
    audit.record("live", live)
    audit.record("physical", PHYSICAL_488)

    # 4. Idle-bill decomposition is exact and matches the certificate.
    idle = {r: PROFILE_488.get(r, 0) - CALLS_488 * BILL.get(r, 0)
            for r in set(PROFILE_488) | set(BILL)}
    idle = {r: Fraction(v, REPLICAS_488) for r, v in idle.items() if v}
    audit.check(idle == IDEAL_IDLE, "residual equals ideal_idle_per_replica exactly")
    audit.check(sum(Fraction(r) * q for r, q in idle.items()) == 18873,
                "idle rank mass is 18873 per replica")
    audit.check(sum(Fraction(r) * q for r, q in BILL.items()) == 5135,
                "local bill rank mass is 5135 per call")
    audit.check(CALLS_PER_REPLICA * 5135 + 18873 == RANK_MASS_PER_REPLICA,
                "9*5135 + 18873 = 65088 per replica")

    # 5. Capacity feasibility of the ideal vertex at T=488.
    for rank, cap in CAPACITY_COUNTS.items():
        count = Fraction(REPLICAS_488) * idle.get(rank, Fraction(0))
        audit.check(count <= cap * REPLICAS_488,
                    f"rank-{rank} child count within per-replica capacity")
    audit.record("capacity_counts_per_replica", CAPACITY_COUNTS)
    audit.record("width_inventory_per_call", WIDTH_INVENTORY)

    # 6. Moment bracket at the certificate's adjacent 10^-24 grid points.
    lo, hi = CAP_ROOT
    m_lo = moment(built, lo, live)
    m_hi = moment(built, hi, live)
    audit.check(m_lo < 0 < m_hi,
                "composed moment straddles the certificate's cap bracket")
    mid = (lo + hi) / 2
    e = Decimal(1) - Decimal(mid.numerator) / Decimal(mid.denominator)
    deriv = -(sum((Decimal(Fraction(n).numerator) / Decimal(Fraction(n).denominator))
                  * (Decimal(r) ** e) * Decimal(r).ln()
                  for r, n in built.items()))
    deriv += Decimal(live) * (Decimal(WIDTH) ** e) * Decimal(WIDTH).ln()
    audit.check(deriv > 0, "moment is strictly increasing at the bracket midpoint")
    audit.check(moment(built, lo - Fraction(1, 10 ** 24), live) < 0 <
                moment(built, hi + Fraction(1, 10 ** 24), live),
                "straddle holds one grid step outside the bracket")
    audit.record("M_at_cap_lower", str(m_lo))
    audit.record("M_at_cap_upper", str(m_hi))
    audit.record("M_prime_at_bracket_midpoint", str(deriv))

    # 7. Released string, delta and headroom.
    released = lo - MARGINS[0] - MARGINS[1]
    audit.check(as_decimal(released, 70) == RELEASED_488,
                "released decimal string reconstructs from the lower endpoint")
    audit.check(released < lo < hi, "released value stays strictly below the bracket")
    delta = lo - LITERAL_ROOT[0]
    audit.check(delta == hi - LITERAL_ROOT[1],
                "bracket shift is the same at both endpoints")
    audit.check(abs(delta - HEADROOM) <= Fraction(1, 10 ** 24),
                "bracket shift agrees with the published root headroom to one grid step")
    audit.check(LITERAL_ROOT[0] < lo < hi and LITERAL_ROOT[1] < hi,
                "the whole T530 literal bracket lies below the T488 cap bracket")
    audit.record("released_kappa", RELEASED_488)
    audit.record("delta_over_T530_floor", str(delta))
    audit.record("published_root_headroom", str(HEADROOM))
    audit.record("literal_to_cap_ratio_T530_quoted", LITERAL_TO_CAP_FLOAT)
    audit.record("literal_to_cap_ratio_T488", "1 (the two profiles are identical)")

    # 8. Controls: the identity is not automatic.
    #    (a) The T530 literal is not at the ideal vertex.
    t530_built = ideal_profile(REPLICAS_530, CALLS_530)
    t530_diff = {r: t530_built.get(r, 0) - PROFILE_530.get(r, 0)
                 for r in set(t530_built) | set(PROFILE_530)}
    audit.control(any(v != 0 for v in t530_diff.values()),
                  "T530 literal differs from the ideal profile")
    t530_idle = {r: Fraction(PROFILE_530.get(r, 0) - CALLS_530 * BILL.get(r, 0), REPLICAS_530)
                 for r in set(PROFILE_530) | set(BILL)}
    audit.control({r: v for r, v in t530_idle.items() if v} != IDEAL_IDLE,
                  "T530 literal residual is not the certificate's idle bill")

    #    (b) Pre-retiming bill does not reconstruct the composed profile.
    pre = {r: Fraction(CALLS_488 * q) for r, q in PRE_RETIMING_BILL.items()}
    for r, q in IDEAL_IDLE.items():
        pre[r] = pre.get(r, Fraction(0)) + REPLICAS_488 * q
    audit.control(pre != {r: Fraction(n) for r, n in PROFILE_488.items()},
                  "pre-retiming local bill fails the identity")

    #    (c) Wrong replica scaling fails.
    wrong = {r: Fraction(CALLS_488 * q) for r, q in BILL.items()}
    for r, q in IDEAL_IDLE.items():
        wrong[r] = wrong.get(r, Fraction(0)) + REPLICAS_530 * q
    audit.control(wrong != {r: Fraction(n) for r, n in PROFILE_488.items()},
                  "wrong replica count fails the identity")

    #    (d) One rank-1 unit in the profile breaks the bracket.
    mutated = dict(PROFILE_488)
    mutated[1] += 1
    audit.control(not (moment(mutated, lo, live) < 0 < moment(mutated, hi, live)),
                  "one rank-1 unit shift breaks the certificate bracket")

    #    (e) Swapped bracket endpoints are rejected by the sign straddle.
    audit.control(not (moment(built, hi, live) < 0 < moment(built, lo, live)),
                  "swapped bracket endpoints fail the straddle")

    #    (f) Integrality is load-bearing: T=490 (not a multiple of 4) is fractional.
    frac = ideal_profile(490, 4410)
    audit.control(any(v.denominator != 1 for v in frac.values()),
                  "T not divisible by 4 gives a fractional ideal profile")
    audit.record("integrality_condition", "T = 0 mod 4; T=488 satisfies it")

    result = {
        "audit": "t488-attains-retimed-packing-cap",
        "outcome": "PASS_T488_ATTAINS_RETIMED_PACKING_CAP",
        "base_commit": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "audited_pr3642_head": "6568db75adbb61437190545f6fef1534c70e91e5",
        "audited_pr3653_head": "607a09ff441c79b215a8127a81f4cc70021d0d9b",
        "identity": "PROFILE_488 = 4392*bill + 488*ideal_idle_per_replica",
        "cap_root_bracket": list(CAP_ROOT_DECIMAL),
        "checks": audit.checks,
        "controls": audit.controls,
        "no_new_kappa": True,
    }
    result.update(audit.rows)
    if write:
        (HERE / "RESULT.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("wrote RESULT.json")
        return
    expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    if expected != json.loads(json.dumps(result)):
        diff = sorted(set(expected) ^ set(result)) or [
            k for k in set(expected) & set(result) if expected[k] != result[k]]
        raise SystemExit(f"FAIL RESULT.json mismatch: {diff[:6]}")
    audit.check(True, "RESULT.json matches the recomputed receipt")
    print("PASS_T488_ATTAINS_RETIMED_PACKING_CAP "
          f"checks={audit.checks} controls={audit.controls} "
          "identity_exact=true cap_attained=true no_new_kappa")


if __name__ == "__main__":
    main()
