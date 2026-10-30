#!/usr/bin/env python3
"""Rebalancing #4359's own outer ledger: smaller compiler savings, much smaller explicit ranks, same kappa 0.0023.

In #4359's controller/outer_parameters.py the complex uniform saving enters the ledger only through
`new_complex_uniform_saving_above_b` (= 0.002304 - b) and the BIT saving only through
`actual_bit_above_effective` (= bit_saving - a) after the atom conversion a_BIT = (1 - 3/1000) C1 + (3/1000) a_old
and the cover fallback C1 < C0. This verifier
  1. transcribes the ledger (54 predicates) and reproduces #4359's nine published outer margins exactly;
  2. sets b = 0.00230255, complex uniform 0.0023026, BIT C0 = 0.002311, C1 = 0.00231, admitted BIT 0.002303,
     and checks every ledger predicate and every BIT conversion/fallback condition strictly;
  3. certifies the two superpotentials at #4359's unchanged tested savings, and recomputes the explicit ranks
     with #4405's refined induction (exit coefficient <= eta), against #4359's and #4405's ranks.
Transcribed formulas are credited to zxv's #4359; nothing is imported from it.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json
import sys

GRID = Q(1, 10**45)
COMPLEX = ({6: 192, 7: 56, 8: 93, 9: 1229, 25: 448, 57: 224}, {1: 17623, 2: 5065, 3: 1738, 4: 714, 5: 254})
BIT = ({8: 3073, 22: 444, 50: 222}, {1: 9261, 2: 9394, 3: 553, 4: 308, 5: 714, 6: 77, 7: 1465})
BASELINE = Q("0.001730980256")       # #4181 headline, the ledger's improvement comparison (rounded down)
PUBLISHED = {"main_transform": "0.00230197698", "global_coordinate_router": "0.0023025",
             "fused_gaussian": "0.00231193094", "group_bit_router": "0.002312430925",
             "boundary_algebraic_matrix": "0.00230297698", "sparse_union_movement": "0.40855297698",
             "group_scans": "0.99998", "polynomial_products": "0.99999", "microbox_face_corrections": "77.00004"}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def ledger(b, kappa=Q(23, 10000), bit_saving=Q(27, 10000), uniform=Q("0.002304"),
           epsilon=Q(99999, 100000), beta=Q(99997, 100000), layout=Q(1, 10**6)):
    """transcription of #4359 outer_parameters.ledger with b and the two savings as parameters"""
    q, a = Q("0.002302"), Q("0.0023025")
    r0, stop = Q(1, 10**6), Q(1, 10**8)
    tau, sigma = 1 - a, 1 - b
    internal = tau + (1 - stop) * max(sigma - tau, Q(0))
    leaf = sigma + stop * (1 - sigma)
    lam = 1 - (q + a) / 2
    c = (3 - Q(45, 16)) / 2
    xi = epsilon * (1 + q) - c + layout
    key = beta + 1 - epsilon
    margins = {
        "main_transform": epsilon * q, "global_coordinate_router": a,
        "fused_gaussian": 1 - epsilon + q * beta, "group_bit_router": 1 - epsilon + a * beta,
        "group_scans": 1 - epsilon + beta, "boundary_algebraic_matrix": c + xi - epsilon,
        "sparse_union_movement": xi + Q(1, 2) - epsilon, "polynomial_products": epsilon,
        "microbox_face_corrections": 1 - (epsilon + beta + 48 - 128 + 2),
    }
    checks = {
        "actual_bit_above_effective": bit_saving - a, "complex_above_effective": b - a,
        "q_positive": q, "complex_endpoint": b - q, "q_below_effective": a - q,
        "stop_positive": stop, "stop_below_one": 1 - stop,
        "leaf_saving_above_effective": (1 - stop) * b - a,
        "q_below_internal": 1 - internal - q, "q_below_leaf": 1 - leaf - q,
        "lambda_above_tau": lam - tau, "lambda_above_sigma": lam - sigma,
        "lambda_above_internal": lam - internal, "lambda_prime_above_lambda": 1 - q - lam,
        "lambda_prime_above_leaf": 1 - q - leaf,
        "epsilon_positive": epsilon, "epsilon_below_one": 1 - epsilon,
        "cap_above_band": xi - Q(1, 2), "cap_below_cell": epsilon - xi,
        "group_positive": beta, "group_below_dimension": epsilon - beta, "support_router_span": 1 - beta,
        "group_gauge_power_slack": 1 - (2 * xi - 2) - r0 - beta,
        "actual_logarithmic_group_guard": 1 - (2 * xi - 2) - beta,
        "global_gamma_power_slack": 1 - epsilon - r0, "actual_logarithmic_gamma_guard": 1 - epsilon,
        "alpha_logarithm_absorption": r0, "group_key_fits_record": 1 - key,
        "membership_arithmetic_fits_record": 1 - beta - 2 * (1 - epsilon),
        "microbox_halo_volume": 128 - 48 - beta, "positive_layout_slack": layout,
        "short_record_fallback": epsilon - a, "complex_below_one_over_32": Q(1, 32) - b,
        "strassen_integer_power_gap": Q(2 ** 45 - 7 ** 16), "theta_positive_polynomial_power": Q(2),
        "cap_below_phase_cell_power": 2 - xi, "halo_covers_generic_inverse_radius": Q(48 - 43),
        "union_tag_work_per_visit_fits_record": 1 - beta, "union_header_fits_record": 1 - beta,
        "source_axis_superpolynomial": 1 - epsilon,
        "gaussian_above_main": margins["fused_gaussian"] - margins["main_transform"],
    }
    checks.update({name + "_above_kappa": value - kappa for name, value in margins.items()})
    checks["new_complex_uniform_saving_above_b"] = uniform - b
    checks["improvement_over_user_baseline"] = kappa - BASELINE
    checks["new_semantic_guard_with_C1_one"] = 1 - epsilon
    checks["fine_prime_halo_umbrella"] = 10 - (2 * 2 + 2 + Q(1, 2))
    return margins, checks


def transfer_audit_checks(b, bit_saving, uniform, epsilon=Q(99999, 100000), beta=Q(99997, 100000)):
    """transcription of the 19 functional checks in #4359 transfer-audit/outer_transfer_audit.py"""
    q, a, r0, stop = Q("0.002302"), Q("0.0023025"), Q(1, 10**6), Q(1, 10**8)
    xi = epsilon * (1 + q) - (3 - Q(45, 16)) / 2 + Q(1, 10**6)
    lam, lam_p = 1 - (q + a) / 2, 1 - q
    sigma, tau = 1 - b, 1 - a
    internal = tau + (1 - stop) * max(sigma - tau, Q(0))
    leaf = sigma + stop * (1 - sigma)
    return {
        "new_uniform_complex_above_selected_b": uniform - b,
        "actual_ordinary_BIT_above_effective": bit_saving - a,
        "selected_complex_above_effective": b - a,
        "lambda_above_actual_internal": lam - internal, "lambda_above_sigma": lam - sigma,
        "lambda_prime_above_lambda": lam_p - lam, "lambda_prime_above_stopped_leaf": lam_p - leaf,
        "new_semantic_main_guard": 1 - epsilon, "new_semantic_group_guard": 1 - beta,
        "complete_per_axis_neighborhood": 1 - epsilon, "global_support_reservoir_and_suffix": 1 - beta,
        "new_BIT_row_stock_sublinear_in_active_group": beta * (1 - Q(3, 1000)),
        "group_strictly_smaller_than_global_dimension": epsilon - beta,
        "global_gamma_spare_power": 1 - epsilon - r0, "fine_prime_group_guard": 1 - (2 * xi - 2) - r0 - beta,
        "polynomial_descriptor_complete_fiber": 1 - epsilon,
        "fixed_halo_explicit_metadata_branch": 128 - 48 - epsilon - beta - 1,
        "member_and_tag_record_budget": 1 - beta - 2 * (1 - epsilon),
        "old_full_span_short_record_fallback": epsilon - a,
    }


def bit_conversion(c0, c1, admitted, atom=Q(3, 1000), old=Q(384599, 10**10)):
    exact = (1 - atom) * c1 + atom * old
    gap = c0 - c1
    need(gap > 0 and atom > exact > admitted and atom < 1 - exact, "BIT atom conversion terms fit")
    need((1 + gap / 4) / (1 + gap / 2) < 1, "fallback moment strict")
    return exact, gap


def down(x):
    return (x / GRID).__floor__() * GRID


def up(x):
    return (x / GRID).__ceil__() * GRID


def ln_bounds(k):
    if k == 1:
        return Q(0), Q(0)
    y = Q(k - 1, k + 1)
    s, term, n = Q(0), y, 0
    while True:
        s += term / (2 * n + 1)
        n += 1
        term *= y * y
        tail = term / (2 * n + 1) / (1 - y * y)
        if tail < GRID:
            return down(2 * s), up(2 * (s + tail))


def exp_small(lo, hi):
    def series(x):
        s, term = Q(0), Q(1)
        for i in range(60):
            s += term
            term = term * x / (i + 1)
        return s, abs(term) * 2
    a, ea = series(lo)
    b, eb = series(hi)
    return down(a - ea), up(b + eb)


def superpotential(case, saving, logs):
    targets, paid = case
    lo = Q(0)
    for k, w in targets.items():
        lo += w * k * exp_small(-saving * logs[k][1], -saving * logs[k][0])[0]
    for r, pr in paid.items():
        lo -= pr * r * exp_small(-saving * logs[r][1], -saving * logs[r][0])[1]
    return lo


def ranks(t, z, h, m, logs, refined=True):
    z0 = (t + z) / 2
    delta = z0 - t
    ln2 = logs[2]
    x = 1 - z0
    s, term = Q(0), x
    for j in range(1, 40):
        s += term / j
        term *= x
    l2_lo = -(s + term / (1 - x)) / ln2[0] + (z0 - 1) * logs[m][1] / ln2[0]
    if refined:
        H0 = -((-(4 * delta - l2_lo)) // (h * delta))
    else:
        H0 = -((-(3 + 4 * delta)) // (h * delta))
    ratio = H0 * (1 - z0) / (z - z0)
    return H0, ratio.numerator // ratio.denominator + 1


def main():
    # 1. transcription control
    margins, checks = ledger(Q("0.002303"))
    for name, value in PUBLISHED.items():
        need(margins[name] == Q(value), f"published margin {name}")
    need(len(checks) == 54 and all(v > 0 for v in checks.values()), "54 predicates positive at #4359's values")
    exact_old, _ = bit_conversion(Q("0.00276"), Q("0.00275"), Q(27, 10000))
    need(exact_old == Q(27418653797, 10**13), "#4359 BIT conversion reproduced")

    # 2. rebalanced savings
    b_new, uniform_new = Q("0.00230255"), Q("0.0023026")
    c0, c1, admitted = Q("0.002311"), Q("0.00231"), Q("0.002303")
    exact_new, gap = bit_conversion(c0, c1, admitted)
    margins2, checks2 = ledger(b_new, bit_saving=admitted, uniform=uniform_new)
    bad = [k for k, v in checks2.items() if not v > 0]
    need(not bad, f"rebalanced ledger predicates positive: {bad}")
    need(margins2 == margins, "outer margins unchanged (they do not depend on b or the savings)")
    old_ta = transfer_audit_checks(Q("0.002303"), Q(27, 10000), Q("0.002304"))
    new_ta = transfer_audit_checks(b_new, admitted, uniform_new)
    need(len(new_ta) == 19 and all(v > 0 for v in old_ta.values()) and all(v > 0 for v in new_ta.values()),
         "all 19 outer_transfer_audit functional checks positive before and after")
    min_slack = min(checks2.values())

    # 3. superpotentials and ranks
    logs = {k: ln_bounds(k) for k in (1, 2, 3, 4, 5, 6, 7, 8, 9, 22, 25, 50, 57)}
    t_c, t_b = 1 - Q(461, 200000), 1 - Q(2769, 1000000)
    need(superpotential(COMPLEX, 1 - t_c, logs) > 0 and superpotential(BIT, 1 - t_b, logs) > 0,
         "superpotentials at #4359's tested savings")
    rows = {}
    for name, t, z_old, z_new, h, m, r4359, r4405 in (
            ("complex", t_c, 1 - Q(36, 15625), 1 - uniform_new, Q(1, 10), 57, 276540184361, 1546084442),
            ("BIT", t_b, 1 - Q(69, 25000), 1 - c0, Q(1, 16), 50, 6552928412, 42843607)):
        need(ranks(t, z_old, h, m, logs, refined=False)[1] == r4359, f"{name}: #4359 rank reproduced")
        need(ranks(t, z_old, h, m, logs)[1] == r4405, f"{name}: #4405 rank reproduced")
        H0, H1 = ranks(t, z_new, h, m, logs)
        rows[name] = {"uniform_saving": str(1 - z_new), "H0": H0, "H1": H1,
                      "H1_4359": r4359, "H1_4405": r4405, "factor_vs_4405": f"{r4405 / H1:.1f}"}
    print(json.dumps({
        "status": "PASS_PR4359_LEDGER_REBALANCE",
        "transcription_control": "nine published margins and 54 predicates reproduced",
        "outer_transfer_audit_functional_checks": "19 positive at the rebalanced values",
        "rebalanced": {"b": str(b_new), "complex_uniform": str(uniform_new), "BIT_C0": str(c0), "BIT_C1": str(c1),
                       "BIT_exact_ordinary": str(exact_new), "BIT_admitted": str(admitted),
                       "cover_prime_rule": f"q > {256 / gap} N^5", "min_predicate_slack": str(min_slack)},
        "ranks": rows,
        "kappa": "23/10000 (unchanged)",
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
