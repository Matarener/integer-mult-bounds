#!/usr/bin/env python3
"""Direct exact-enclosure audit of the two final batched-interchange moment bounds.

The batched-assembly notes of the retained manuscript choose two recursive
savings, a_b = 246/10^9 and a_c = 7/10^7, because the child-list moments
Psi_b(1 - a_b) and Xi_c(1 - a_c) are strictly below one. The pinned
certificates prove that with sufficient bounds:

    Psi(1 - a) = sum_i w_i * exp(a * ln(1 / r_i))
               <= sum_i w_i / (1 - a * ell_i)                 (ell_i >= ln(1 / r_i))
               <  1.

This checker does not reuse that route. It certifies the same two
inequalities directly, with its own rational enclosures of ln and exp and
outward rounding, and reports

  * the exact rational weight and count identities of both child lists,
  * a direct interval for each moment at the published saving,
  * the published sufficient bound and its gap, recomputed exactly,
  * a certified bracket for the sharp moment threshold of each child list.

Scope: arithmetic on the two displayed child lists only. The sharp threshold
is a property of the moment inequality alone, not a claim that the assembly
may raise either saving, because the other parameter constraints (absorption
gaps, compact-control exponents, depth and row reservations) are unchanged
and are not examined here. No kappa, supplier or selected-frontier change.

Author: Nick Petalas, with AI assistance. Apache-2.0.
"""

import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

# The certified moment intervals are exact rationals with a few thousand
# digits; printing them is part of the receipt.
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(200000)

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent

# Repository-relative inputs, authenticated by SHA-256 from SOURCES.json.
INPUTS = (
    "notes/batched-assembly.tex",
    "notes/batched-algorithms.tex",
    "notes/batched-bit-rank-accounting.tex",
    "certificates/batched-network.json",
    "certificates/controlled-bit-rank-moment.json",
)
BIT_CERTIFICATE = "certificates/controlled-bit-rank-moment.json"
COMPLEX_CERTIFICATE = "certificates/batched-network.json"

BIT_SAVING = Q(246, 10**9)
COMPLEX_SAVING = Q(7, 10**7)
THRESHOLD_DENOMINATOR = 1 << 80
THRESHOLD_SEARCH_TOP = 2 * THRESHOLD_DENOMINATOR // 10**6  # 2e-6

MARKER = "PASS_BATCHED_MOMENT_THRESHOLD"


def fail(message):
    raise SystemExit("FAIL_BATCHED_MOMENT_THRESHOLD " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# Rigorous rational enclosures for ln and exp.
#
# ln N for an integer N is reduced to ln 2 plus one atanh series on an
# argument z in [0, 1/3). The truncation remainder is bounded by
# z^(2m+1) / ((2m+1) (1 - z^2)) with exact rational arithmetic.
# exp y for 0 <= y < 1 is bounded below by a positive Taylor partial sum and
# above by that sum plus 2 y^m / m!, since exp y < 2 on this range.
# --------------------------------------------------------------------------


def _atanh_bounds(z, terms):
    """(lower, remainder) for 2*sum_{j>=0} z^(2j+1)/(2j+1), 0 <= z < 1."""
    require(0 <= z < 1, "atanh argument outside [0,1)")
    total = Q(0)
    power = 2 * z
    for j in range(terms):
        if j:
            power *= z * z
        total += power / (2 * j + 1)
    remainder = power * z * z / ((2 * terms + 1) * (1 - z * z))
    return total, remainder


def _log2_bounds(terms):
    return _atanh_bounds(Q(1, 3), terms)


def log_int_bounds(n, terms=64):
    """Rigorous (lower, upper) rational bounds for ln n, n >= 1."""
    require(n >= 1, "ln domain")
    if n == 1:
        return Q(0), Q(0)
    shift = 0
    odd = n
    while odd % 2 == 0:
        odd //= 2
        shift += 1
    log2_lo, log2_rem = _log2_bounds(terms)
    log2_hi = log2_lo + log2_rem
    if odd == 1:
        return shift * log2_lo, shift * log2_hi
    reduce_shift = odd.bit_length() - 1
    w = Q(odd, 1 << reduce_shift)  # 1 <= w < 2
    z = (w - 1) / (w + 1)
    series_lo, series_rem = _atanh_bounds(z, terms)
    low = (shift + reduce_shift) * log2_lo + series_lo
    high = (shift + reduce_shift) * log2_hi + series_lo + series_rem
    return low, high


def log_rational_bounds(q, terms=64):
    """Rigorous (lower, upper) rational bounds for ln q, q > 0 rational."""
    require(q > 0, "ln domain")
    lo_n, hi_n = log_int_bounds(q.numerator, terms)
    lo_d, hi_d = log_int_bounds(q.denominator, terms)
    return lo_n - hi_d, hi_n - lo_d


def exp_bounds(low, high, terms=24):
    """(lower, upper) for exp(.) on an interval with 0 <= low <= high <= 1."""
    require(0 <= low <= high <= 1, "exp enclosure range")

    def partial(x):
        total = Q(0)
        term = Q(1)
        for k in range(terms):
            if k:
                term = term * x / k
            total += term
        return total, term * x / terms  # last term times x/terms = next term

    low_partial, _ = partial(low)
    high_partial, next_term = partial(high)
    return low_partial, high_partial + 2 * next_term


class Moment:
    """Moment sum_i w_i (1/r_i)^a with cached rigorous log enclosures."""

    def __init__(self, weights, ratios, log_terms=64):
        require(len(weights) == len(ratios) and weights, "moment shape")
        require(all(w >= 0 for w in weights), "negative weight")
        require(all(0 < r < 1 for r in ratios), "ratio outside (0,1)")
        self.weights = list(weights)
        self.ratios = list(ratios)
        self.inverses = [1 / r for r in ratios]
        self.logs = [log_rational_bounds(u, log_terms) for u in self.inverses]

    def bounds(self, a, exp_terms=20):
        """Certified (lower, upper) for the moment at rational a >= 0."""
        require(a >= 0, "negative saving")
        low = Q(0)
        high = Q(0)
        for w, (log_lo, log_hi) in zip(self.weights, self.logs):
            e_lo, e_hi = exp_bounds(a * log_lo, a * log_hi, exp_terms)
            low += w * e_lo
            high += w * e_hi
        return low, high

    def threshold_bracket(self, denominator=THRESHOLD_DENOMINATOR,
                          top=THRESHOLD_SEARCH_TOP):
        """Certified [a_low, a_high] with moment(a_low) < 1 < moment(a_high)."""
        require(self.bounds(Q(0))[1] < 1, "moment does not start below one")
        require(self.bounds(Q(top, denominator))[0] > 1, "search top too low")
        hold = 0
        fail_at = top
        while fail_at - hold > 1:
            middle = (hold + fail_at) // 2
            low, _ = self.bounds(Q(middle, denominator), exp_terms=8)
            if low > 1:
                fail_at = middle
                continue
            _, high = self.bounds(Q(middle, denominator), exp_terms=8)
            if high < 1:
                hold = middle
                continue
            # An unresolved middle is already a bracket at this resolution.
            return (Q(middle, denominator), Q(middle + 1, denominator))
        return (Q(hold, denominator), Q(fail_at, denominator))


# --------------------------------------------------------------------------
# Source binding and count identities.
# --------------------------------------------------------------------------


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == set(INPUTS), "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    assembly = (ROOT / INPUTS[0]).read_text(encoding="utf-8")
    for needle in ("a_{\\rm b}=246/10^9", "a_{\\rm c}=7/10^7",
                   "1007397164592", "2085111546336", "45772350635112192",
                   "2389799139122304"):
        require(needle in assembly, "assembly constant moved: " + needle)
    algorithms = (ROOT / INPUTS[1]).read_text(encoding="utf-8")
    for needle in ("n_1=s-B(21840+20384+784)-2N\\cdot20330",
                   "=105555640096680883200",
                   "\\Psi\\!\\left(1-\\frac{246}{10^9}\\right)<1"):
        require(needle in algorithms, "controlled-basis constant moved: " + needle)
    rank_accounting = (ROOT / INPUTS[2]).read_text(encoding="utf-8")
    for needle in ("a_{\\rm b}=\\frac{177}{10^9}", "\\eta=39/520019360"):
        require(needle in rank_accounting, "rank-accounting constant moved: " + needle)


def bit_moment():
    """Child list of the controlled-basis bit interchange, from its counts."""
    cert = json.loads((ROOT / BIT_CERTIFICATE).read_text(encoding="utf-8"))
    n = cert["counts"]
    m, W = n["m"], Q(n["W"])
    require(m == 21952 and n["h"] == 28, "bit modulus moved")
    require(Q(cert["bit_saving"]) == BIT_SAVING, "bit saving moved")
    require(cert["tau"] == str(1 - BIT_SAVING), "bit tau moved")
    classes = [(Q(row["copies"]), row["chunk_digits"]) for row in n["recursive_blocks"]]
    weights = [Q(n["singleton_calls"]) / (W * m)]
    ratios = [Q(1, m)]
    for copies, digits in classes:
        require(0 < digits < m, "bit chunk outside modulus")
        weights.append(copies * digits / (W * m))
        ratios.append(Q(digits, m))
    require(weights == [Q(x) for x in cert["rank_mass_weights"]], "bit weights moved")
    require(ratios == [Q(x) for x in cert["normalized_widths"]], "bit ratios moved")
    require(sum(weights) == 1 - Q(n["eta"]), "bit weight sum broken")
    # Structural identities of the note: B = v^2 R, N = v^3 and the class list.
    v = n["v"]
    require(v**3 == n["N"], "bit N is not v cubed")
    require(Q(v * v * n["roles_per_invocation"]) == Q(classes[0][0]), "bit B is not v^2 R")
    require(sorted(c for c, _ in classes) == sorted(
        [Q(n["v"]) ** 2 * n["roles_per_invocation"]] * 3 + [2 * n["N"]]),
        "bit bulk multiplicities moved")
    require(sorted(d for _, d in classes) == [784, 20330, 20384, 21840],
            "bit chunk multipliers moved")
    require(Q(n["singleton_calls"]) + sum(c * d for c, d in classes) == n["original_rank_sum"],
            "bit rank sum broken")
    require(Q(n["original_rank_sum"]) == (1 - Q(n["eta"])) * W * m, "bit Psi(1) moved")
    return Moment(weights, ratios), cert, n


def complex_moment():
    """Child list of the complex whole-residual recursion, from its counts."""
    cert = json.loads((ROOT / COMPLEX_CERTIFICATE).read_text(encoding="utf-8"))["complex"]
    n = cert["counts"]
    m, W = n["m"], Q(n["W"])
    require(m == 21952 and n["h"] == 28, "complex modulus moved")
    require(Q(cert["complex_saving"]) == COMPLEX_SAVING, "complex saving moved")
    require(cert["sigma"] == str(1 - COMPLEX_SAVING), "complex sigma moved")
    # Count identities displayed in the assembly note.
    v, side, h = n["v"], n["side_roles"], n["h"]
    require(Q(v * v * (side + h + 1)) == Q(n["bulk_classes"][0]["copies"]), "complex B_c moved")
    require(Q(2 * v * v * (v + side + h + 1)) == W, "complex W_c moved")
    require(Q(3 * v * v * h * (h + 1)) == n["L"], "complex L_c moved")
    require(W * m - 2 * v**3 + 2 * n["L"] == n["s"], "complex s_c moved")
    a1, a2 = (row["rank"] for row in n["bulk_classes"])
    require((a1, a2) == (21896, 21168), "complex ranks moved")
    copies = Q(n["bulk_classes"][0]["copies"])
    require(copies == Q(n["bulk_classes"][1]["copies"]), "complex copies differ")
    require(Q(n["singleton_calls"]) == Q(n["s"]) - copies * (a1 + a2), "complex S_c moved")
    weights = [Q(n["singleton_calls"]) / (W * m)] + [copies * a / (W * m) for a in (a1, a2)]
    ratios = [Q(1, m), Q(a1, m), Q(a2, m)]
    require(weights == [Q(x) for x in cert["rank_mass_weights"]], "complex weights moved")
    require(ratios == [Q(x) for x in cert["normalized_widths"]], "complex ratios moved")
    require(sum(weights) == 1 - Q(n["eta"]), "complex weight sum broken")
    require(Q(n["s"]) == (1 - Q(n["eta"])) * W * m, "complex Xi(1) moved")
    return Moment(weights, ratios), cert


def check_sufficient_route(cert, moment, saving):
    """Validate the pinned log enclosures and recompute the sufficient bound."""
    tight = [Q(x) for x in cert["logarithm_enclosures"]]
    simple = [Q(x) for x in cert["logarithm_upper_bounds"]]
    require(len(tight) == len(moment.weights) == len(simple), "log bound count")
    for index, u in enumerate(moment.inverses):
        # 200 series terms put the independent upper bound ~1e-193 above ln u,
        # far inside the pinned enclosures' own truncation error.
        log_high = log_rational_bounds(u, 200)[1]
        require(log_high < tight[index], "published enclosure is not an upper bound")
        require(tight[index] < simple[index], "tight enclosure is not below the simple bound")
    bound = sum(w / (1 - saving * ell) for w, ell in zip(moment.weights, simple))
    require(bound == Q(cert["moment_upper"]), "published moment upper bound does not recompute")
    require(1 - bound == Q(cert["strict_gap"]), "published strict gap does not recompute")
    require(bound < 1, "published sufficient bound fails")
    return bound, tight, simple


def decimal(value, digits=12, up=False):
    """Decimal string of a non-negative rational, rounded down unless up=True.

    Rounding down keeps a floor a lower bound and rounding up keeps a ceiling
    an upper bound, so both directions stay certified in the receipt.
    """
    require(value >= 0, "negative decimal")
    scaled = value * 10**digits
    scaled = -((-scaled).__floor__()) if up else scaled.__floor__()
    whole, rest = divmod(scaled, 10**digits)
    return str(whole) + "." + str(rest).zfill(digits)


def audit_side(name, moment, cert, saving):
    direct_low, direct_high = moment.bounds(saving)
    require(direct_high < 1, name + " direct moment fails at the published saving")
    sufficient, tight, simple = check_sufficient_route(cert, moment, saving)
    bracket_low, bracket_high = moment.threshold_bracket()
    hold_low, hold_high = moment.bounds(bracket_low)
    fail_low, fail_high = moment.bounds(bracket_high)
    require(hold_high < 1, name + " bracket lower endpoint does not hold")
    require(fail_low > 1, name + " bracket upper endpoint does not fail")
    require(saving < bracket_low,
            name + " published saving is not below the sharp bracket")
    return {
        "saving": str(saving),
        "direct_moment_upper_decimal": decimal(direct_high, 30, up=True),
        "direct_margin_lower_bound_decimal": decimal(1 - direct_high, 30),
        "sufficient_moment_upper": str(sufficient),
        "sufficient_gap": str(1 - sufficient),
        "sufficient_gap_decimal": decimal(1 - sufficient, 30),
        "sufficient_gap_is_smaller": (1 - sufficient) < (1 - direct_high),
        "sharp_threshold_low": str(bracket_low),
        "sharp_threshold_high": str(bracket_high),
        "sharp_threshold_low_decimal": decimal(bracket_low, 15),
        "sharp_threshold_high_decimal": decimal(bracket_high, 15, up=True),
        "sharp_threshold_relative_slack_decimal": decimal(
            bracket_low / saving - 1, 12),
        "log_enclosure_count": len(tight),
        "simple_log_bounds": [str(x) for x in simple],
    }


def evaluate():
    authenticate()
    bit, bit_cert, bit_counts = bit_moment()
    complex_moment_value, complex_cert = complex_moment()
    result = {
        "scope": "arithmetic on the two displayed batched child lists",
        "bit": audit_side("bit", bit, bit_cert, BIT_SAVING),
        "complex": audit_side("complex", complex_moment_value, complex_cert, COMPLEX_SAVING),
        "threshold_denominator": str(THRESHOLD_DENOMINATOR),
        "no_new_kappa": True,
    }
    # Negative control: far above either threshold both moments exceed one.
    control = Q(10**-5)
    for name, moment in (("bit", bit), ("complex", complex_moment_value)):
        low, _ = moment.bounds(control)
        require(low > 1, name + " control at a = 1e-5 did not exceed one")
        result.setdefault("control_fails_above_threshold_at", str(control))
    require(bit_counts["m"] == complex_cert["counts"]["m"], "mixed moduli")
    return result


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored,
            "RESULT.json does not match the execution: "
            + json.dumps(observed, sort_keys=True)[:400])
    print(MARKER
          + " bit_margin>=" + observed["bit"]["direct_margin_lower_bound_decimal"]
          + " complex_margin>=" + observed["complex"]["direct_margin_lower_bound_decimal"]
          + " no_new_kappa")


if __name__ == "__main__":
    main()
