#!/usr/bin/env python3
"""Independent conditional audit of PR3620's P104 all-pair deletion threshold.

Audits PROOF.md section 3 of PR #3620 (head 5a4354c6) given PR #3609's changed
full dual (head 13f974da) and the named paired-chain coverage law. Written from
the stated model, without opening PR3620's budget.py. Two exact methods:

A. Fraction interval arithmetic on the model numerator (clamped residual,
   explicit capacity), with atanh/Taylor series and rigorous tails, plus the
   written convexity argument for all integer p >= 1.
B. Decimal arithmetic (correctly rounded ln/exp, padded outward) on the
   closed-form excess, a finite range p = 1..P0-1 and a linearised tail bound
   for p >= P0 that does not use convexity.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
"""
import hashlib
import json
import sys
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, localcontext
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
F_PATH = ROOT / "research/p104-consumer-budget-audit/RESULT.json"
F_SHA256 = "08705a91912d937a782696cd3e0905a9a5b63e60ce7daf9ff9618968f32eaae5"
D_PATH = HERE / "inputs/PR3609_RECEIPT.json"
D_SHA256 = "6d06db043316af94377653a8e3fbfa1dcd686e20760af943b08e7060896ccf8b"
D_BLOB = "6faa5157f2274a5bb85da4d5e44b1b1ff39eb32c"

KAPPA = Fr(836330098538459, 500000000000000000)
A596 = Fr(1, 596)
ROUND = 10 ** 50          # outward rounding grid for method A
TAIL_P0 = 24              # method B tail starts here
PREC = 70                 # method B working precision
PAD = Decimal(10) ** -55  # method B outward padding (relative per child, absolute per sum)
PASSING = {"kappa": (6, 11), "kappa_over_1_minus_kappa": (6, 11), "a596": (6, 10)}  # d = 426


# ---------------------------------------------------------------- sources
def need(condition, message):
    """Explicit check (not an assert statement), so python -O cannot skip it."""
    if not condition:
        raise AssertionError(message)


def blob_id(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_sources():
    fb, db = F_PATH.read_bytes(), D_PATH.read_bytes()
    need(hashlib.sha256(fb).hexdigest() == F_SHA256, "PR2744 RESULT.json drift")
    need(hashlib.sha256(db).hexdigest() == D_SHA256, "PR3609 RECEIPT.json drift")
    need(blob_id(db) == D_BLOB, "PR3609 RECEIPT.json blob drift")
    fj, dj = json.loads(fb), json.loads(db)
    contract, fwd = fj["contract"], fj["censuses"]["forward2458"]
    F = {int(r): n for r, n in fwd["profile"].items()}
    inv = dj["invoice"]
    full, proj, comp = inv["changed_full"], inv["projection"], inv["entrance_completion"]
    D = {int(r): n for r, n in full["native_profile"].items()}
    stop = inv["conditional_consumer_stop"]
    facts = {
        # forward profile and the PR2744 contract (its p = 4 instance)
        "F_mass_3070": sum(r * n for r, n in F.items()) == fwd["rank_mass"] == 3070,
        "F_calls_1646": sum(F.values()) == fwd["operations"]["transport"] == 1646,
        "F_progress_3014": fwd["persistent_endpoint_progress"] == 3014,
        "roles_104_104_150": fwd["role_types"] == {"X": 104, "Y": 104, "dirty": 150},
        "P_is_role_maximum": contract["maximum_original_progress_per_call"]
        == 104 * 8 + 104 * 8 + 150 * 9 == 3014,
        "contract_is_p4_instance": (contract["width"], contract["original_families"],
                                    contract["forward_calls"], contract["dual_calls"],
                                    contract["unpaid_per_original_family"])
        == (16 * 4 + 9, 208 * 4, 4 + 1, 4, 1),
        # changed dual: receipt totals and the projection + completion split
        "D_mass_3542": sum(r * n for r, n in D.items()) == full["native_rank_mass"] == 3542,
        "D_calls_1742": sum(D.values()) == full["native_calls"] == 1742,
        "D_is_projection_plus_completion":
            all(int(proj["native_profile"].get(str(r), 0))
                + int(comp["native_profile"].get(str(r), 0)) == D[r] for r in D)
            and proj["native_rank_mass"] + comp["native_rank_mass"] == 3542
            and comp["native_profile"] == {"1": 52, "9": 93},
        "completion_adds_no_bank": comp["new_private_Gaussian_banks"] == 0,
        "pr3609_uses_same_law_at_p4": (stop["W"], stop["m"], stop["persistent_credit_per_call"],
                                       stop["forward_calls"], stop["dual_calls"])
        == (832, 73, 3014, 5, 4)
        and "coverage law and endpoint credit unchanged" in stop["remaining_hypotheses"],
    }
    need(all(facts.values()), str({k: v for k, v in facts.items() if not v}))
    return F, D, facts


def default_params(F, D):
    return {"F": dict(F), "D": dict(D), "P": 3014, "w": 208, "m_slope": 16, "m_const": 9,
            "d_fail": 425, "d_pass": 426, "p4_fail": 427, "p4_pass": 428}


# ------------------------------------------------- method A: Fraction intervals
def down(x):
    return Fr((x.numerator * ROUND) // x.denominator, ROUND)


def up(x):
    return Fr(-((-x.numerator * ROUND) // x.denominator), ROUND)


def atanh_bounds(t, terms=60):
    """0 <= t <= 1/3: positive series, tail <= t^(2N+1)/((2N+1)(1-t^2))."""
    s, power = Fr(0), t
    for j in range(terms):
        s += power / (2 * j + 1)
        power *= t * t
    return s, s + power / ((2 * terms + 1) * (1 - t * t))


LN2 = tuple(2 * b for b in atanh_bounds(Fr(1, 3)))


def ln_bounds(x):
    """Rigorous [lo, hi] for ln x, rational x >= 1."""
    x = Fr(x)
    need(x >= 1, "ln domain")
    k = max(0, x.numerator.bit_length() - x.denominator.bit_length())
    while Fr(2) ** k > x:
        k -= 1
    while Fr(2) ** (k + 1) <= x:
        k += 1
    lo, hi = atanh_bounds((x / 2 ** k - 1) / (x / 2 ** k + 1))   # 1 <= x/2^k < 2
    return down(k * LN2[0] + 2 * lo), up(k * LN2[1] + 2 * hi)


def exp_bounds(lo, hi, terms=24):
    """Rigorous [exp(lo), exp(hi)] for 0 <= lo <= hi < 1."""
    need(0 <= lo <= hi < 1, "exp domain")

    def partial(x):
        s, term = Fr(0), Fr(1)
        for k in range(terms):
            s += term
            term = term * x / (k + 1)
        return s, term                       # term = x^N / N!

    s_lo, _ = partial(lo)
    s_hi, last = partial(hi)
    return down(s_lo), up(s_hi + last / (1 - hi / (terms + 1)))


def child_bounds(m, r, a):
    """Interval for m^a r^(1-a) = r (m/r)^a, 1 <= r <= m, 0 <= a < 1."""
    lo, hi = ln_bounds(Fr(m, r))
    elo, ehi = exp_bounds(a * lo, a * hi)
    return r * elo, r * ehi


def model_excess_A(par, p, d, a, B=0, clamp=True):
    """Interval for N - m(W+B), N = sum_r n_r m^a r^(1-a) + I_B. Pass iff negative."""
    m = par["m_slope"] * p + par["m_const"]
    W = par["w"] * p
    Dd = dict(par["D"])
    Dd[1] = Dd.get(1, 0) - d
    need(Dd[1] >= 0 and max(par["F"]) <= m and max(par["D"]) <= m, "rank/deletion domain")
    lo = hi = Fr(0)
    for r in sorted(set(par["F"]) | set(Dd)):
        n = (p + 1) * par["F"].get(r, 0) + p * Dd.get(r, 0)
        if n:
            c_lo, c_hi = child_bounds(m, r, a)
            lo, hi = lo + n * c_lo, hi + n * c_hi
    J = (m - 1) * W + m * B - (2 * p + 1) * par["P"]
    I = max(0, J) if clamp else J
    cap = m * (W + B)
    return lo + I - cap, hi + I - cap


# --------------------------------------------- method B: Decimal, closed form
def dec(a):
    return Decimal(a.numerator) / Decimal(a.denominator)


def dec_child(m, r, a):
    """r (m/r)^a from correctly rounded Decimal ln/exp, padded outward."""
    v = Decimal(r) * (dec(a) * (Decimal(m) / Decimal(r)).ln()).exp()
    return v * (1 - PAD), v * (1 + PAD)


def weights(par, p, d):
    """Rank weights of p U_d + V: p (F_r + D_{d,r}) + F_r."""
    out = {}
    for r in sorted(set(par["F"]) | set(par["D"])):
        f, g = par["F"].get(r, 0), par["D"].get(r, 0) - (d if r == 1 else 0)
        out[r] = (p * (f + g) + f, f + g, f)
    return out


def closed_form_B(par, p, d, a):
    """E_d(p,a) = m^a (p U_d + V) - (w + 2P) p - P, unclamped, B cancelled."""
    m = par["m_slope"] * p + par["m_const"]
    with localcontext() as c:
        c.prec = PREC
        lo = hi = Decimal(0)
        for r, (wt, _, _) in weights(par, p, d).items():
            if wt:
                v_lo, v_hi = dec_child(m, r, a)
                lo += wt * v_lo
                hi += wt * v_hi
        const = Decimal((par["w"] + 2 * par["P"]) * p + par["P"])
        return lo - const - PAD, hi - const + PAD


def tail_bound_B(par, d, a, p0):
    """For integer p >= p0: E_d(p,a) >= p*c1 + c0, from exp(x) >= 1 + x and
    ln(m/r) >= ln(m0/r) (all weights nonnegative, all ranks below m0)."""
    m0 = par["m_slope"] * p0 + par["m_const"]
    with localcontext() as c:
        c.prec = PREC
        s1 = s0 = Decimal(0)
        mass1 = mass0 = 0
        for r, (_, w1, w0) in weights(par, p0, d).items():
            need(w1 >= 0 and w0 >= 0 and r < m0, "tail monotonicity premises")
            lnv = (Decimal(m0) / Decimal(r)).ln() - PAD
            s1 += w1 * r * lnv
            s0 += w0 * r * lnv
            mass1 += w1 * r
            mass0 += w0 * r
        c1 = (mass1 - par["w"] - 2 * par["P"]) + dec(a) * s1 - PAD
        c0 = (mass0 - par["P"]) + dec(a) * s0 - PAD
    return c1, c0


# -------------------------------------------------------------- the audit
def dstr(x, places, rounding):
    with localcontext() as c:
        c.prec = PREC
        return str(dec(Fr(x)).quantize(Decimal(10) ** -places, rounding=rounding))


def inside(iv, a, b):
    return Fr(a) < iv[0] and iv[1] < Fr(b)


def audit(par):
    """Return (claims, values). Every claim must be True for PASS."""
    claims, val = {}, {}
    points = {"E425_p6_kappa": (6, par["d_fail"], KAPPA), "E425_p7_kappa": (7, par["d_fail"], KAPPA),
              "E425_p8_kappa": (8, par["d_fail"], KAPPA), "E426_p7_a596": (7, par["d_pass"], A596),
              "E426_p7_kappa": (7, par["d_pass"], KAPPA), "E427_p4_kappa": (4, par["p4_fail"], KAPPA),
              "E428_p4_a596": (4, par["p4_pass"], A596)}
    EA = {k: model_excess_A(par, *v) for k, v in points.items()}
    for k, iv in EA.items():
        val[k] = [dstr(iv[0], 15, ROUND_FLOOR), dstr(iv[1], 15, ROUND_CEILING)]
    # PR3620 PROOF.md section 3: stated strict decimal enclosures and consequences
    claims["stated_E425_p6"] = inside(EA["E425_p6_kappa"], "2.62322106", "2.62322107")
    claims["stated_E425_p7"] = inside(EA["E425_p7_kappa"], "1.60068641", "1.60068642")
    claims["stated_E425_p8"] = inside(EA["E425_p8_kappa"], "1.97354361", "1.97354362")
    claims["stated_E426_p7_a596"] = inside(EA["E426_p7_a596"], "-4.55707137", "-4.55707136")
    claims["stated_allowance_4_557071360876949"] = inside(EA["E426_p7_a596"], "-4.557071360876950",
                                                          "-4.557071360876949")
    claims["four_units_pass_five_fail"] = EA["E426_p7_a596"][1] + 4 < 0 < EA["E426_p7_a596"][0] + 5
    claims["E426_p7_kappa_negative"] = EA["E426_p7_kappa"][1] < 0
    claims["p4_427_fails_at_kappa"] = EA["E427_p4_kappa"][0] > 0
    claims["p4_428_passes_at_a596"] = EA["E428_p4_a596"][1] < 0
    claims["a596_exceeds_kappa"] = KAPPA < A596 and KAPPA < A596 / (1 + A596) == Fr(1, 597)
    # Clamp and banks: J_B = (m-1)W + mB - (2p+1)P
    def J(p, B=0):
        m = par["m_slope"] * p + par["m_const"]
        return (m - 1) * par["w"] * p + m * B - (2 * p + 1) * par["P"]
    claims["clamp_inactive_at_pass_points"] = J(7) > 0 and J(4) > 0
    claims["p1_zero_bank_clamp_adds_4050"] = J(1) == -4050
    claims["banks_cancel_at_p7"] = all(model_excess_A(par, 7, par["d_fail"], KAPPA, B)
                                       == EA["E425_p7_kappa"] for B in (1, 17, 10 ** 6))
    claims["clamp_only_raises_p1"] = all(
        model_excess_A(par, 1, par["d_fail"], KAPPA, B)[0]
        >= model_excess_A(par, 1, par["d_fail"], KAPPA, B, clamp=False)[0] for B in (0, 100, 200))
    # Method B (closed form, Decimal) agrees with method A (model, Fractions)
    agree = True
    for k in ("E425_p6_kappa", "E425_p7_kappa", "E425_p8_kappa", "E426_p7_a596", "E428_p4_a596"):
        b_lo, b_hi = closed_form_B(par, *points[k])
        agree &= Fr(b_lo) <= EA[k][1] and EA[k][0] <= Fr(b_hi) and b_hi - b_lo < Decimal("1e-40")
        agree &= EA[k][1] - EA[k][0] < Fr(1, 10 ** 40)
    claims["methods_A_B_agree"] = agree
    # Method A, all integer p >= 1: strict convexity premises + discrete minimum at 7
    Dd = dict(par["D"])
    Dd[1] -= par["d_fail"]
    claims["convexity_premises"] = (0 < KAPPA < 1 and min(Dd.values()) >= 0 and Dd[1] > 0
                                    and min(par["F"].values()) >= 0 and sum(par["F"].values()) > 0
                                    and max(set(Dd) | set(par["F"])) <= par["m_slope"] + par["m_const"]
                                    and 0 < par["m_slope"] <= 2 * par["m_const"])
    e6, e7, e8 = EA["E425_p6_kappa"], EA["E425_p7_kappa"], EA["E425_p8_kappa"]
    claims["A_discrete_min_p7_positive"] = e7[1] < e6[0] and e7[1] < e8[0] and e7[0] > 0
    # Method B, all integer p >= 1 without convexity: finite range + linear tail
    finite = {p: closed_form_B(par, p, par["d_fail"], KAPPA) for p in range(1, TAIL_P0)}
    c1, c0 = tail_bound_B(par, par["d_fail"], KAPPA, TAIL_P0)
    claims["B_finite_p1_to_p23_positive"] = all(v[0] > 0 for v in finite.values())
    claims["B_finite_argmin_p7"] = min(finite, key=lambda p: finite[p][0]) == 7
    claims["B_tail_p24_onward_positive"] = c1 > 0 and TAIL_P0 * c1 + c0 > 0
    val["B_tail"] = {"p0": TAIL_P0, "slope_lower": str(c1.quantize(Decimal("1e-9"), ROUND_FLOOR)),
                     "value_at_p0_lower": str((TAIL_P0 * c1 + c0).quantize(Decimal("1e-9"), ROUND_FLOOR))}
    val["B_finite_lower"] = {str(p): str(v[0].quantize(Decimal("1e-9"), ROUND_FLOOR))
                             for p, v in finite.items()}
    # Deletion lemma, finite certificate on ranks <= 9:
    # r^(1-a) - (r-delta)^(1-a) <= delta for 1 <= delta <= r, strict when r >= 2
    ok = strict = True
    for a in (KAPPA, A596):
        def pw_hi(s):      # upper bound of s^(1-a) = s / exp(a ln s)
            return Fr(s) if s <= 1 else s / exp_bounds(*(a * x for x in ln_bounds(s)))[0]

        def pw_lo(s):
            return Fr(s) if s <= 1 else s / exp_bounds(*(a * x for x in ln_bounds(s)))[1]
        for r in range(1, 10):
            for delta in range(1, r + 1):
                saving_hi = pw_hi(r) - pw_lo(r - delta)
                ok &= saving_hi <= delta
                strict &= r == 1 or saving_hi < delta
    claims["deletion_lemma_ranks_le_9"] = ok and max(par["D"]) <= 9
    claims["deletion_strict_above_rank1"] = strict
    claims["rank1_children_available"] = par["D"][1] >= max(par["d_pass"], par["p4_pass"])
    # Audit finding: the stated allowance is a point value at (p=7, a=1/596).
    # For d_pass, E is strictly convex in p (same premises, D_{d,1} > 0), so the
    # negative set is an integer interval bounded by two positive neighbours.
    total_p8 = per_call_p7 = per_any_call_p7 = True
    val["d426_slack"] = {}
    for name, a in (("kappa", KAPPA), ("kappa_over_1_minus_kappa", KAPPA / (1 - KAPPA)), ("a596", A596)):
        E = {p: model_excess_A(par, p, par["d_pass"], a) for p in range(1, 16)}
        neg = [p for p in E if E[p][1] < 0]
        lo_p, hi_p = (min(neg), max(neg)) if neg else (0, 0)
        bounded = (bool(neg) and neg == list(range(lo_p, hi_p + 1)) and lo_p > 1 and hi_p < 15
                   and E[lo_p - 1][0] > 0 and E[hi_p + 1][0] > 0)
        total_p8 &= bounded and all(E[8][1] < E[p][0] for p in neg if p != 8)
        per_call_p7 &= bounded and all(E[7][1] / 7 < E[p][0] / p for p in neg if p != 7)
        # extra cost charged per call of either kind: 2p+1 calls
        per_any_call_p7 &= bounded and all(E[7][1] / 15 < E[p][0] / (2 * p + 1) for p in neg if p != 7)
        claims["d426_passing_p_%s_%d_to_%d" % ((name,) + PASSING[name])] = bounded and (lo_p, hi_p) == PASSING[name]
        val["d426_slack"][name] = {
            "passing_p": [lo_p, hi_p],
            "total_slack_p7": dstr(-E[7][1], 12, ROUND_FLOOR),
            "total_slack_p8": dstr(-E[8][1], 12, ROUND_FLOOR),
            "per_dual_call_slack_p7": dstr(-E[7][1] / 7, 12, ROUND_FLOOR),
            "per_any_call_slack_p7": dstr(-E[7][1] / 15, 12, ROUND_FLOOR)}
    claims["finding_d426_total_slack_max_at_p8"] = total_p8
    claims["finding_d426_per_dual_call_slack_max_at_p7"] = per_call_p7
    claims["finding_d426_per_any_call_slack_max_at_p7"] = per_any_call_p7
    e8 = model_excess_A(par, 8, par["d_pass"], A596)
    claims["finding_five_units_pass_at_p8_a596"] = e8[1] + 5 < 0
    claims["finding_five_units_pass_at_p7_kappa"] = EA["E426_p7_kappa"][1] + 5 < 0
    return claims, val


def main(argv):
    F, D, facts = load_sources()
    claims, val = audit(default_params(F, D))
    receipt = {"schema_version": 1, "sources": facts, "claims": claims, "values": val,
               "F": {str(r): F[r] for r in sorted(F)}, "D": {str(r): D[r] for r in sorted(D)}}
    text = json.dumps(receipt, indent=1, sort_keys=True) + "\n"
    out = HERE / "RESULT.json"
    if "--write" in argv:
        out.write_text(text, encoding="utf-8")
    failed = [k for k, v in claims.items() if not v]
    need(not failed, "FAILED claims: " + ", ".join(failed))
    need(out.read_text(encoding="utf-8") == text, "RESULT.json differs from recomputation")
    s = val["d426_slack"]
    rng = {k: "p%d..%d" % tuple(s[k]["passing_p"]) for k in s}
    req = "kappa_over_1_minus_kappa"  # a_req under the retained conversion kappa = a/(1+a)
    print("PASS_P104_CONSUMER_THRESHOLD_AUDIT d425_rejects_every_p>=1 "
          "d426_passes(a596:%s,a_req:%s) total_slack_p7(a596=%s,a_req=%s)(best_p_for_per_call_costs) "
          "fixed_cost_slack_best_p8(a596=%s,a_req=%s) a_req=kappa/(1-kappa) "
          "conditional_on_PR3609_D_and_named_law"
          % (rng["a596"], rng[req], s["a596"]["total_slack_p7"][:8], s[req]["total_slack_p7"][:8],
             s["a596"]["total_slack_p8"][:8], s[req]["total_slack_p8"][:8]))


if __name__ == "__main__":
    main(sys.argv[1:])
