#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent integer-rounded binomial checks for the COPY planning receipt.

No import of check_budget.py or the logarithm/exponential interval engine.
For 0<b<1 and 0<=z<1,
  (1-z)^(-b) = sum_n (b)_n z^n/n!.
The next-term ratio is at most z, so the entire omitted tail is bounded
by next_term/(1-z). Every recurrence multiplication rounds outwards.
Substantial OpenAI Codex assistance. Not a formal-kernel proof.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCALE = 1 << 192
TERMS = 8192
WIDTH, STOCK, CALLS = 64, 28416, 288
SURCHARGE = Q(32*64**2, 10**16)
TARGET = Q(9199631083923049, 4990800368916076951)
LOCAL = {1: 1322, 2: 1342, 3: 79, 4: 39, 5: 102, 6: 11, 7: 18}
CODED = {1: 1298, 2: 1342, 3: 79, 4: 44, 5: 93, 6: 11, 7: 9}


def require(test, message):
    if not test:
        raise ValueError(message)


def ceil_div(n, d):
    return -((-n)//d)


@lru_cache(None)
def power_64_over_rank(rank, b):
    require(1 <= rank <= WIDTH and 0 < b < 1, "binomial domain")
    z = Q(WIDTH-rank, WIDTH)
    lower = upper = total_lower = total_upper = SCALE
    for n in range(TERMS):
        ratio = (b+n)*z/(n+1)
        lower = lower*ratio.numerator//ratio.denominator
        upper = ceil_div(upper*ratio.numerator, ratio.denominator)
        total_lower += lower
        total_upper += upper
    # The loop includes terms 0 through TERMS. Bound all later terms.
    next_ratio = (b+TERMS)*z/(TERMS+1)
    first_upper = ceil_div(upper*next_ratio.numerator, next_ratio.denominator)
    tail_upper = ceil_div(first_upper*WIDTH, rank)
    return Q(total_lower, SCALE), Q(total_upper+tail_upper, SCALE)


def arithmetic_add(x, y):
    return x[0]+y[0], x[1]+y[1]


def arithmetic_scale(x, c):
    return (x[0]*c, x[1]*c) if c >= 0 else (x[1]*c, x[0]*c)


def charged_excess(hist, b):
    total = (Q(0), Q(0))
    for rank, count in hist.items():
        total = arithmetic_add(total, arithmetic_scale(
            power_64_over_rank(rank, b), rank*count))
    total = arithmetic_add(total, arithmetic_scale(
        power_64_over_rank(1, b), SURCHARGE*sum(hist.values())))
    return total[0]-WIDTH*STOCK, total[1]-WIDTH*STOCK


def free_bad_excess(hist, b):
    total = (Q(0), Q(0))
    for rank, count in hist.items():
        total = arithmetic_add(total, arithmetic_scale(
            power_64_over_rank(rank, b), rank*count))
    total = arithmetic_scale(total, 1-Q(1, 10**16))
    return total[0]-WIDTH*STOCK, total[1]-WIDTH*STOCK


def expected_profile(local, full_per_call, partial_per_call):
    """Reconstruct all resource totals independently of the receipt."""
    F, D = full_per_call*CALLS, partial_per_call*CALLS
    t = Q(F-56832, 5)
    require(0 <= D <= 14208 and 0 <= t <= 14208, "resource regime")
    out = {r: Q(n*CALLS) for r, n in local.items()}
    for rank, count in ((7, 21312), (6, 14208), (4, 14208-D),
                        (2, t), (42, 14208-t)):
        out[rank] = out.get(rank, 0)+count
    return {r: n for r, n in out.items() if n}


def subtract_copies(hist, number):
    result = hist.copy()
    result[7] -= number
    require(result[7] >= 0, "COPY inventory")
    return result


def parse_hist(row):
    return {int(r): Q(n) for r, n in row["H"].items()}


def intervals_meet(x, serialized):
    y = Q(serialized["lower"]), Q(serialized["upper"])
    require(x[0] <= y[1] and y[0] <= x[1], "independent interval intersects primary")


def fraction_pair(x):
    return {"lower": str(x[0]), "upper": str(x[1])}


def verify_row(label, row, expected):
    require(parse_hist(row) == expected, label+": full histogram")
    require(Q(row["children"]) == sum(expected.values()), label+": child count")
    require(Q(row["rank_mass"]) == sum(r*n for r, n in expected.items()),
            label+": rank mass")
    interval = charged_excess(expected, TARGET)
    intervals_meet(interval, row["charged_excess"])
    favorable = interval[1] < 0
    require(favorable or interval[0] > 0, label+": strict target sign")
    roots = row.get("charged_root_bracket")
    result = {"label": label, "charged_excess": fraction_pair(interval),
              "target_favorable": favorable}
    if roots:
        low, high = Q(roots["lower"]), Q(roots["upper"])
        require(high-low == Q(1, 10**15), label+": adjacent root grid")
        lower_sign, upper_sign = charged_excess(expected, low), charged_excess(expected, high)
        require(lower_sign[1] < 0 < upper_sign[0], label+": independent root signs")
        intervals_meet(lower_sign, roots["lower_excess"])
        intervals_meet(upper_sign, roots["upper_excess"])
        result["root"] = {"lower": str(low), "upper": str(high),
                          "lower_excess": fraction_pair(lower_sign),
                          "upper_excess": fraction_pair(upper_sign)}
    if favorable:
        extra = row["additional_equal_rank_children_per_call"]
        for rank_str, cap in extra.items():
            rank, n = int(rank_str), cap["maximum"]
            for count, accept in ((n, True), (n+1, False)):
                augmented = expected.copy()
                augmented[rank] = augmented.get(rank, 0)+CALLS*count
                e = charged_excess(augmented, TARGET)
                require(e[1] < 0 if accept else e[0] > 0,
                        label+": independent adjacent decoder count")
    return result


def verify(receipt):
    require(Q(receipt["target_primitive"]) == TARGET, "same exact target")
    require(receipt["minimum_uniform_deletions_per_call"] == 1 and
            receipt["minimum_arbitrary_global_COPY7_deletions"] == 85,
            "declared minimum counts")
    base = expected_profile(LOCAL, 433, 5)
    out = []
    for k in range(10):
        row = receipt["ideal_uniform_COPY7_deletions"][str(k)]
        result = verify_row("ideal"+str(k), row, subtract_copies(base, CALLS*k))
        require(result["target_favorable"] == (k > 0), "uniform deletion boundary")
        out.append(result)
    for t, accept in ((84, False), (85, True)):
        interval = charged_excess(subtract_copies(base, t), TARGET)
        require(interval[1] < 0 if accept else interval[0] > 0,
                "global deletion boundary")
        intervals_meet(interval, receipt["adjacent_global_deletion_excess"][str(t)])
        free_bad = free_bad_excess(subtract_copies(base, t), TARGET)
        intervals_meet(free_bad, receipt["adjacent_global_deletion_free_bad_excess"][str(t)])
        if t == 84:
            require(free_bad[0] > 0, "84 deletions fail the favorable LP lower bound")
        out.append({"label": "global_deleted"+str(t), "charged_excess": fraction_pair(interval)})
    coded = expected_profile(CODED, 429, 0)
    out.append(verify_row("coded429", receipt["coded_profiles"]["coded429_full"], coded))
    mixed_local = CODED.copy()
    mixed_local[4] -= 5
    mixed = expected_profile(mixed_local, 424, 5)
    out.append(verify_row("coded424plus5", receipt["coded_profiles"][
        "coded424_full5_partial_if_terminal_adaptation_proved"], mixed))
    require(sum(r*n for r, n in coded.items()) ==
            sum(r*n for r, n in mixed.items()) == 1791072,
            "returned owner obligations included")
    direct = base.copy()
    for r, n in ((6, 4), (7, -8), (8, 4)):
        direct[r] = direct.get(r, 0)+CALLS*n
    direct_row = receipt["direct_query_mass63_lower_bound"]
    out.append(verify_row("direct_mass63_best_shape", direct_row, direct))
    free_bad = free_bad_excess(direct, TARGET)
    require(free_bad[0] > 0, "direct COPY class fails even with free bad packets")
    intervals_meet(free_bad, direct_row["free_bad_excess"])
    roots = direct_row.get("free_bad_root_bracket")
    if roots:
        lo, hi = Q(roots["lower"]), Q(roots["upper"])
        ls, hs = free_bad_excess(direct, lo), free_bad_excess(direct, hi)
        require(hi-lo == Q(1, 10**15) and ls[1] < 0 < hs[0],
                "direct free-bad ceiling interval")
        intervals_meet(ls, roots["lower_excess"])
        intervals_meet(hs, roots["upper_excess"])
    # Fixed constructed owner invoice is independently read from its pinned source.
    invoice_path = HERE/"../inputs/full-invoices.json"
    require(hashlib.sha256(invoice_path.read_bytes()).hexdigest() ==
            "d0877305ca03e88622586fd76622fc9e2e2da0484de3b112577467c82f386a92",
            "existing full invoice source")
    invoices = json.loads(invoice_path.read_bytes())
    literal = {int(r): Q(n) for r, n in
               invoices["profiles"]["reuse/reference"]["H"].items()}
    out.append(verify_row("literal_owner_one_deletion",
                         receipt["fixed_constructed_owner_invoice_one_deletion"],
                         subtract_copies(literal, CALLS)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=HERE/"BUDGET.json")
    ap.add_argument("--output", type=Path, default=HERE/"INDEPENDENT.json")
    args = ap.parse_args()
    receipt = json.loads(args.input.read_bytes())
    checks = verify(receipt)
    controls = []
    # Real receipt corruptions: lost owner mass, a falsely free next decoder,
    # and pretending the 84-deletion rejection already passes.
    mutants = []
    x = json.loads(args.input.read_bytes())
    x["coded_profiles"]["coded429_full"]["H"]["42"] = "1728/5"
    mutants.append(("lost_returned_owner_mass", x))
    x = json.loads(args.input.read_bytes())
    x["coded_profiles"]["coded429_full"]["additional_equal_rank_children_per_call"]["1"]["maximum"] = 58
    mutants.append(("unaffordable_rank1_decoder", x))
    x = json.loads(args.input.read_bytes())
    x["minimum_arbitrary_global_COPY7_deletions"] = 84
    mutants.append(("one_fewer_COPY_deletion", x))
    for label, mutant in mutants:
        try:
            verify(mutant)
        except ValueError as error:
            controls.append({"mutation": label, "rejected": True, "reason": str(error)})
        else:
            raise ValueError("mutation escaped: "+label)
    output = {"status": "PASS_INDEPENDENT_COPY_BUDGET_BINOMIAL",
              "no_new_kappa": True,
              "primary_receipt_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
              "algorithm": "positive binomial recurrence; integer outward rounding; "
                  "next_term/(1-z) entire-tail bound",
              "dyadic_bits": 192, "included_terms_after_constant": TERMS,
              "checks": checks, "negative_controls": controls,
              "scope": "Independent moment arithmetic and full inventory specialization; "
                  "not operator, owner chronology, native compiler, or joint assembly admission"}
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True)+"\n")
    print("PASS_INDEPENDENT_COPY_BUDGET_BINOMIAL no_new_kappa")


if __name__ == "__main__":
    main()
