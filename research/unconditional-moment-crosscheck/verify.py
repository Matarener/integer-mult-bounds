"""Independent recomputation of PR4100's exact-root and paid-power ledger.

This module re-implements the moment certificate from scratch: its own
rational logarithm and exponential enclosures, its own bill evaluator and
its own bisection. It imports no code from research/unconditional-batched-crt
or research/staged544-mixed-fourth-entry/vendor. Constants are transcribed
from the prose of the audited package (PROOF.md, "Paid powers" and
"Time" sections, at retained head 337d049) and the profile and comparison
denominator are read from the pinned PR4088 RESULT.json.

This is a finite numerical audit of stated arithmetic claims. It is not an
all-size theorem checker, a validation of the CRT total repair, the
free-algebra lift, the precision or tape arguments, or a supplier admission.
"""
from fractions import Fraction as Q
from decimal import Decimal as D, localcontext
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
MIXED = ROOT / "research/staged544-mixed-fourth-entry"


def need(condition, message):
    if not condition:
        raise ValueError(message)


# ---------------------------------------------------------------------------
# Own interval enclosures (fresh code; classic series with rigorous tails).
# ---------------------------------------------------------------------------

PREC = 60  # outward rounding target in significant decimal digits


def _outward(lo, hi, digits=PREC):
    scale = 10**digits
    lower = (lo.numerator * scale) // lo.denominator
    upper = -((-hi.numerator * scale) // hi.denominator)
    return Q(lower, scale), Q(upper, scale)


def _atanh_series(z, digits):
    """Interval for 2*atanh(z) = 2*sum z^(2j+1)/(2j+1), 0 <= z <= 1/3."""
    need(Q(0) <= z <= Q(1, 3), "atanh range")
    total = Q(0)
    power = z
    j = 0
    # stop once the remaining geometric-dominant tail is below the rounding
    while True:
        term = power / (2 * j + 1)
        total += 2 * term
        if term * (1 / (1 - z * z)) < Q(1, 10 ** (digits + 8)):
            break
        power *= z * z
        j += 1
    tail = 2 * power * z * z / ((2 * j + 3) * (1 - z * z))
    return total, total + tail


_LN_CACHE = {}


def ln_interval(n):
    """Interval for ln(n), positive integer n <= 256."""
    need(type(n) is int and 1 <= n <= 256, "ln rank range")
    if n in _LN_CACHE:
        return _LN_CACHE[n]
    e = n.bit_length() - 1
    m = Q(n, 1 << e)  # m in [1, 2)
    if m == 1:
        lm = Q(0)
        lo_m, hi_m = Q(0), Q(0)
    else:
        lo_m, hi_m = _ln_range12(m)
    if e == 0:
        lo2 = hi2 = Q(0)
    else:
        # ln 2 = 2*atanh(1/3) exactly
        lo2, hi2 = _atanh_series(Q(1, 3), PREC + 8)
        lo2, hi2 = lo2 * e, hi2 * e
    res = _outward(lo_m + lo2, hi_m + hi2, PREC + 4)
    _LN_CACHE[n] = res
    return res


def _ln_range12(m):
    """Interval for ln(m), rational m in [1, 2), via 2*atanh((m-1)/(m+1))."""
    need(Q(1) <= m < Q(2), "range 1..2")
    z = (m - 1) / (m + 1)
    return _atanh_series(z, PREC + 8)


def _exp_neg_interval(t):
    """Interval for exp(-t), rational t in [0, 11/2].

    Alternating series with decreasing terms: partial sums of odd order are
    lower bounds, of even order upper bounds.
    """
    need(Q(0) <= t <= Q(11, 2), "exp range")
    if t == 0:
        return Q(1), Q(1)
    term = Q(1)
    s = Q(1)
    lower, upper = Q(1) - t, Q(1)
    j = 1
    while True:
        term = -term * t / j
        s += term
        if j % 2 == 0:
            upper = s
        else:
            lower = s
        if j >= 2 and abs(term) < Q(1, 10 ** (PREC + 8)):
            break
        j += 1
    return lower, upper


def power_upper_lower(rank, a):
    """Enclose rank^(1-a) = rank * exp(-a*ln(rank)) as (lower, upper)."""
    lo_l, hi_l = ln_interval(rank)
    t_lo, t_hi = a * lo_l, a * hi_l
    e_lo, e_hi = _exp_neg_interval(t_hi)
    if t_lo != t_hi:
        e_lo_alt, _ = _exp_neg_interval(t_lo)
        e_lo = min(e_lo, e_lo_alt)
    return _outward(rank * e_lo, rank * e_hi, PREC)


def bill_interval(a, profile, w):
    """Enclose (sum_r n_r (r/73)^(1-a)) / w as (lower, upper)."""
    lo = Q(0)
    hi = Q(0)
    wq = Q(w)
    for rank, n in profile.items():
        l, u = power_upper_lower(rank, a)
        p_lo = l / power_upper_lower(73, a)[1]
        p_hi = u / power_upper_lower(73, a)[0]
        lo += n * p_lo
        hi += n * p_hi
    return _outward(lo / wq, hi / wq, PREC - 10)


# ---------------------------------------------------------------------------
# Transcribed constants (PROOF.md of the audited package, retained head).
# ---------------------------------------------------------------------------

PROFILE = {1: 8060060, 2: 2310120, 3: 751813, 4: 327210,
           5: 66425, 8: 25920, 48: 138492}
W_COMPARISON = 896 * 360  # rank-73 comparison count stated by the engine
B = Q(".001730979115670792472760579929302792893760378764")
KAPPA = Q(".00173097911567079247276057")
QW = B - Q(1, 10**28)
A_EFF = (B + QW) / 2
EPS = 1 - Q(1, 10**30)
BETA = 1 - Q(3, 10**30)
XI = EPS * (1 + QW) - Q(3, 32) + Q(1, 10**30)
STOP = Q(1, 10**32)
C = Q(8667, 5000000)
A1, A2 = C * (1 - C), C * (1 - C * C)

POWERS = {
    "main": 1 - EPS * QW,
    "global_router": 1 - A_EFF,
    "gaussian": EPS - QW * BETA,
    "group_router": EPS - A_EFF * BETA,
    "group_scans": EPS - BETA,
    "boundary": EPS - XI + Q(29, 32),
    "union": EPS + Q(1, 2) - XI,
    "products": 1 - EPS,
    "crt": 1 - A2 + 2 * (1 - EPS),
    "halo_arithmetic": EPS + BETA + 144 - 400,
    "halo_metadata": EPS + 50 - 400,
    "cached_phases_and_recovery": Q(0),
}
SIDE = {
    "dimension_below_one": 1 - EPS,
    "group_below_dimension": EPS - BETA,
    "group_positive": BETA,
    "group_headers": 1 - BETA,
    "membership": 1 - BETA - 2 * (1 - EPS),
    "shifted_guard": 1 - BETA - 2 * XI + 2,
    "cap_above_band": XI - Q(1, 2),
    "cap_below_phase": 2 - XI,
    "bounded_individual_chirp": 1 - XI,
    "core_above_faces": 400 - 48 - BETA,
    "leaf_saving": (1 - STOP) * B - QW,
    "bit_above_internal": A2 - A_EFF,
    "internal_above_q": A_EFF - QW,
    "root_above_q": B - QW,
    "crt_table_guard": Q(64) - 4,
}
REJECTED = {
    "old_Vd_crt": 1 - KAPPA - EPS,
    "old_g_union_scans": 1 - KAPPA - (EPS + BETA + Q(1, 2) - XI),
    "old_per_record_d_chirp": 1 - KAPPA - EPS,
    "old_theta_chirp_guard": 1 - BETA - 2 * XI + EPS,
    "no_group_gap_membership": 1 - EPS - 2 * (1 - EPS),
}


def decimal_bill(a, profile, w, prec=90):
    with localcontext() as ctx:
        ctx.prec = prec
        total = D(0)
        for rank, n in profile.items():
            r = D(rank) / D(73)
            total += n * (r ** (D(1) - D(a.numerator) / D(a.denominator)))
        return total / D(w) - D(1)


def main():
    result = json.loads((MIXED / "RESULT.json").read_text(encoding="utf8"))
    pinned_profile = {int(k): v for k, v in result["profile"].items()}
    need(pinned_profile == PROFILE, "profile agrees with pinned PR4088 RESULT.json")
    cond = Q(result["conditional_kappa"])

    # Exact rational ledger (12 paid powers as exponents; 15 side conditions
    # stated directly as slack quantities; 5 obsolete-route rejects).
    power_slacks = {n: 1 - KAPPA - p for n, p in POWERS.items()}
    need(len(POWERS) == 12 and len(SIDE) == 15, "ledger row counts")
    need(all(x > 0 for x in power_slacks.values()), "all 12 paid-power slacks strict")
    need(all(x > 0 for x in SIDE.values()), "all 15 side-condition slacks strict")
    need(all(x < 0 for x in REJECTED.values()), "all 5 obsolete routes still rejected")
    need(A1 == Q(".00173039532444"), "a1 decimal")
    need(A2 == Q(".001733394791695384296"), "a2 decimal")
    need(7**16 < 2**45, "Strassen exponent bound")

    # Headline comparison claims.
    gap = KAPPA - cond
    need(gap > Q(57, 10**26), "gap over PR4088 conditional kappa exceeds 5.7e-25")
    trunc = Q((B * 10**26).__floor__(), 10**26)
    need(trunc == KAPPA, "kappa is the 26-decimal-place truncation of b")
    need(KAPPA < B, "kappa strictly below b")

    # Independent moment certificate at the bracket endpoints.
    lo_b, hi_b = bill_interval(B, PROFILE, W_COMPARISON)
    need(hi_b < 1, "bill(b) < 1 (independent enclosure upper bound)")
    b_up = B + Q(1, 10**48)
    lo_u, hi_u = bill_interval(b_up, PROFILE, W_COMPARISON)
    need(lo_u > 1, "bill(b + 1e-48) > 1 (independent enclosure lower bound)")
    lo_k, hi_k = bill_interval(KAPPA, PROFILE, W_COMPARISON)
    need(hi_k < 1, "bill(kappa) < 1")
    lo_e, hi_e = bill_interval(A_EFF, PROFILE, W_COMPARISON)
    need(hi_e < 1, "bill(a_eff) < 1")
    lo_q, hi_q = bill_interval(QW, PROFILE, W_COMPARISON)
    need(hi_q < 1, "bill(q) < 1")

    # Informational root placement with 90-digit decimal arithmetic.
    f_lo = decimal_bill(B, PROFILE, W_COMPARISON)
    f_up = decimal_bill(b_up, PROFILE, W_COMPARISON)
    need(f_lo < 0 < f_up, "decimal sign agreement with rational certificate")
    a1_, a2_ = B, b_up
    for _ in range(140):
        mid = (a1_ + a2_) / 2
        if decimal_bill(mid, PROFILE, W_COMPARISON) < 0:
            a1_ = mid
        else:
            a2_ = mid
    with localcontext() as ctx:
        ctx.prec = 60
        root_lo = format(D(a1_.numerator) / D(a1_.denominator), ".52f")
        root_hi = format(D(a2_.numerator) / D(a2_.denominator), ".52f")
        marg = format(1 - D(hi_k.numerator) / D(hi_k.denominator), ".3e")
        m_b = format(D(hi_b.numerator) / D(hi_b.denominator) - 1, ".3e")
        m_u = format(D(lo_u.numerator) / D(lo_u.denominator) - 1, ".3e")
    need(a1_ > B and a2_ < b_up, "localized root inside (b, b + 1e-48)")

    # Controls: tampered claims must fail.
    rejected_controls = []

    def reject(label, fn):
        try:
            fn()
        except ValueError:
            rejected_controls.append(label)
            return
        raise ValueError("control was accepted: " + label)

    wrong = dict(PROFILE)
    wrong[1] += 1
    reject("rank-1 count inflated by one",
           lambda: need(bill_interval(B, wrong, W_COMPARISON)[1] < 1, "tampered profile"))
    shift = Q(1, 10**12)
    reject("bracket shifted up by 1e-12 (excludes the true root)",
           lambda: need(bill_interval(B + shift, PROFILE, W_COMPARISON)[1] < 1,
                       "bill at shifted lower endpoint claimed below one"))
    reject("root claimed at or above b + 1e-48",
           lambda: need(bill_interval(b_up, PROFILE, W_COMPARISON)[1] < 1,
                       "bill at upper endpoint must not be below one"))
    reject("unrounded kappa equals b", lambda: need(B < KAPPA, "kappa below b"))

    print(json.dumps({
        "status": "PASS_UNCONDITIONAL_MOMENT_CROSSCHECK",
        "audited": {"package": "research/unconditional-batched-crt",
                   "head": "337d04939571a637aeab54a0f58f54fde811663a",
                   "profile": PROFILE, "m": 73, "w": W_COMPARISON},
        "kappa_claim": str(KAPPA),
        "root_bracket_independent": [root_lo, root_hi],
        "bill_margins": {
            "b_upper": m_b,
            "kappa_margin_below_one": marg,
            "b_plus_48_lower": m_u,
        },
        "paid_power_slacks": {k: str(v) for k, v in power_slacks.items()},
        "side_slacks": {k: str(v) for k, v in SIDE.items()},
        "rejected_old_routes": {k: str(v) for k, v in REJECTED.items()},
        "gap_over_pr4088_conditional": str(gap),
        "conditional_kappa_pr4088": str(cond),
        "controls_rejected": rejected_controls,
        "scope": "Finite numerical cross-check of the stated exact-root and "
                 "paid-power ledger of PR4100 against its pinned PR4088 inputs. "
                 "Not an all-size proof check, not supplier admission, no new kappa.",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
