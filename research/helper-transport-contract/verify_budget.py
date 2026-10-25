#!/usr/bin/env python3
"""Small, source-pinned transport budget calculation; no supplier admission claim.

Prepared for apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Directed-rational power arithmetic is reused from Clear1nsight's pinned selected
supplier, with its attribution and source untouched.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
BASE = "32890bc5de034ab8fc93ac88ead7279a6a416d04"
FUNDING = "research/coupled-helper-neutral-completion/reports/expected/funding.json"
ENGINE = ("research/coupled-helper-neutral-completion/capsule/workspace/"
          "swarm-coupled-caller-sol-high-20261024/agents/invoice/exact_moments.py")
CANONICAL = "research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz"
PROVIDER = ("research/coupled-helper-neutral-completion/capsule/workspace/"
            "swarm-provider-audit-sol-high-20261024/repository/research/"
            "native-rank8-helper-provider/WORD.json.gz")
EXPECTED = {
    FUNDING: "70ab7d13548962097ad83ad393b8482f52e827b8996869011ce6d071146bd3eb",
    ENGINE: "cf7439c9eb4095224126dd5eefc9f1c5dfe1968d6e8eca5b87d4a3897841182d",
    CANONICAL: "7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05",
    PROVIDER: "7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(funding):
    kappa, s, gap = Q(funding["kappa"]), Q(funding["tested"]), Q(funding["gap"])
    need(s == Q(605457649, 200000000000), "unexpected tested saving")
    need(s - kappa == 7 * gap, "supplier exponent ladder differs")
    return kappa, s, gap


def source_invoices(repo):
    payload = gzip.decompress((repo / CANONICAL).read_bytes())
    canonical = json.loads(payload)["canonical"]
    provider = json.loads(gzip.decompress((repo / PROVIDER).read_bytes()))
    need(provider["source_sha256"] == hashlib.sha256(payload).hexdigest(),
         "provider source binding")
    need(provider["direction"] == "backward", "selected backward provider")
    word = provider["word"]
    closure = {19, 300, 301}
    changed = True
    while changed:
        changed = False
        for event in word[9044:9137]:
            if event[0] == "scalar" and event[1][0] == "add":
                refs = event[1][1:3]
                need(all(ref[0] == "L" for ref in refs), "persistent closure roles")
                fields = {ref[1] for ref in refs}
                if fields & closure and not fields <= closure:
                    closure.update(fields)
                    changed = True
    frames = list(canonical["start"])
    bases = canonical["frames"]
    entry = None
    touched, paid = set(), Counter()
    included = 0
    for index, event in enumerate(word[:9137]):
        if index == 9044:
            entry = list(frames)
        kind = event[0]
        if kind in ["phase", "adapter", "residual_adapter"]:
            # These are inert markers in native_extensions.literal_replay.
            need(index < 9044, "no inert marker in selected block")
            continue
        if kind == "climb":
            _, _, field, old, new, rank = event
            need(frames[field] == old, "source climb frame")
            need(len(bases[new]) - len(bases[old]) == rank > 0,
                 "source climb dimension and charge")
            frames[field] = new
            involved = [field]
            if index >= 9044 and field in closure:
                paid[rank] += 1
        elif kind == "warp":
            need(index < 9044, "no warp in selected block")
            _, ref, _, old, new = event
            need(ref[0] == "L" and frames[ref[1]] == old, "source warp frame")
            frames[ref[1]] = new
            involved = [ref[1]]
        elif kind == "scalar":
            operation, frame = event[1:]
            need(operation[0] in ["add", "scale"], "source scalar opcode")
            refs = operation[1:3] if operation[0] == "add" else operation[1:2]
            need(all(ref[0] == "L" and frames[ref[1]] == frame for ref in refs),
                 "source scalar coframe")
            involved = [ref[1] for ref in refs]
        else:
            raise ValueError(f"unexpected prefix opcode: {kind}")
        if index >= 9044 and set(involved) & closure:
            need(set(involved) <= closure, "dependency-closed interval")
            touched.update(involved)
            included += 1
    need(len(touched) == 20, "twenty-field boundary")
    endpoints = [{"field": f, "entry_frame": entry[f], "exit_frame": frames[f],
                  "rank_increase": len(bases[frames[f]]) - len(bases[entry[f]])}
                 for f in sorted(touched)]
    ideal = Counter(e["rank_increase"] for e in endpoints)
    need(min(ideal) > 0 and paid == {1: 38} and ideal == {1: 3, 2: 16, 3: 1},
         "source-derived invoices differ from the scoped claim")
    need(included == 85, "selected event count")
    return dict(paid), dict(ideal), endpoints, included


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def subtract(a, b):
    return a[0] - b[1], a[1] - b[0]


def times(n, a):
    need(n >= 0, "nonnegative interval multiplier")
    return n * a[0], n * a[1]


def outward_18(interval):
    """Readable exact endpoints with denominator 10**18, rounded outward."""
    d = 10 ** 18
    low, high = interval
    return [str(Q(low.numerator * d // low.denominator, d)),
            str(Q(-((-high.numerator * d) // high.denominator), d))]


def independent_budget_checks(s):
    """Coarse rational proof, independent of the imported logarithm/power code.

    Taylor's exponential series has positive terms. After term30, the first
    omitted term divided by 1-q/32 bounds the tail for 0<=q<3.
    """
    def exp_interval(q):
        need(0 <= q < 3, "independent exponential range")
        total = term = Q(1)
        for j in range(1, 31):
            term *= q / j
            total += term
        return total, total + (term * q / 31) / (1 - q / 32)

    # These checks prove the logarithm brackets without importing log or exp.
    brackets = [(2, Q(69, 100), Q(7, 10)),
                (3, Q(109, 100), Q(11, 10)),
                (5, Q(8, 5), Q(17, 10))]
    for n, lo, hi in brackets:
        need(exp_interval(lo)[1] < n < exp_interval(hi)[0],
             f"independent logarithm bracket: {n}")
    # 1-x <= exp(-x) <= 1-x+x*x/2 for x>=0.
    b_upper = Q(257, 10) * s
    b_lower = Q(507, 20) * s - Q(1931, 200) * s * s
    g_upper = Q(157, 25) * s + Q(2229, 200) * s * s
    h2_lower = 2 * (1 - Q(7, 10) * s)
    independent = {
        "per_local_B20_plus_one_split_below_H1": b_upper + g_upper < 1,
        "once_global_H2_exceeds_18_combined_allowances":
            18 * (b_upper + g_upper) < h2_lower,
        "once_global_H1_not_excluded_by_18_B20": 18 * b_lower > 1,
    }
    need(all(independent.values()), "independent elementary budget guard")
    return {"checks": independent,
            "B20_lower": str(b_lower), "B20_upper": str(b_upper),
            "split_upper": str(g_upper), "H2_lower": str(h2_lower)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    for relative, expected in EXPECTED.items():
        actual = hashlib.sha256((args.repo / relative).read_bytes()).hexdigest()
        need(actual == expected, f"source hash differs: {relative}")
    funding = json.loads((args.repo / FUNDING).read_text())
    kappa, s, gap = parameters(funding)
    paid_profile, ideal_profile, endpoints, included = source_invoices(args.repo)
    t = 1 - s
    spec = importlib.util.spec_from_file_location("pinned_exact_moments", args.repo / ENGINE)
    arithmetic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arithmetic)
    p = {rank: arithmetic.power(rank, t) for rank in [1, 2, 3, 4, 5, 7, 8, 9, 145]}
    original = arithmetic.moment(paid_profile, t)
    ideal = arithmetic.moment(ideal_profile, t)
    b = subtract(original, ideal)
    g = subtract(add(p[4], p[5]), p[9])
    first_line_split = subtract(add(p[1], p[8]), p[9])
    both = add(b, g)
    target_debit = subtract(p[9], p[4])
    results = {
        "twenty_field_ideal_saving": b,
        "eighteen_times_ideal_saving": times(18, b),
        "one_9_to_4_plus_5_target_split": g,
        "conditional_9_to_1_plus_8_target_split_not_admitted": first_line_split,
        "eighteen_conditional_9_to_1_plus_8_splits_not_admitted": times(18, first_line_split),
        "eighteen_target_splits": times(18, g),
        "combined_per_local": both,
        "combined_eighteen_locals": times(18, both),
        "one_H2_repair": p[2],
        "one_H3": p[3],
        "one_H7_isolated_exit_coefficient": p[7],
        "debit_if_rank9_target_retires_at_rank4_without_productive_successor": target_debit,
        "one_rank_target_downgrade_lower_bound_up_to_145":
            times(t, arithmetic.power(145, -s)),
    }
    checks = {
        "B20_less_than_one_H1": b[1] < 1,
        "B20_plus_split_less_than_one_H1": both[1] < 1,
        "eighteen_splits_less_than_one_H1": 18 * g[1] < 1,
        "eighteen_B20_can_cover_one_H1_only_as_optimistic_budget": 18 * b[0] > 1,
        "eighteen_B20_plus_splits_less_than_one_H2": 18 * both[1] < p[2][0],
        "surrendered_positive_integer_rank_target_exceeds_B20": b[1] < 1,
        "rank9_to4_target_debit_exceeds_B20": target_debit[0] > b[1],
        "elementary_upper_bound": b[1] < Q(257, 10) * s < Q(78, 1000),
        "balanced_split_bounds_conditional_first_line_split": first_line_split[1] < g[0],
        "one_H7_exceeds_B20_plus_conditional_first_line_split":
            p[7][0] > b[1] + first_line_split[1],
    }
    need(all(checks.values()), "budget inequality failed")
    independent = independent_budget_checks(s)
    controls = []

    def require_rejected(name, operation):
        try:
            operation()
        except ValueError:
            controls.append(name)
            return
        raise ValueError(f"mutation was not rejected: {name}")

    require_rejected("substitute_selected_kappa_for_tested_saving",
                     lambda: parameters({**funding, "tested": funding["kappa"]}))

    def signed_moment(profile):
        out = (Q(0), Q(0))
        for rank, count in profile.items():
            need(type(rank) is int and rank > 0 and type(count) is int,
                 "signed invoice integers")
            term = times(abs(count), arithmetic.power(rank, t))
            out = add(out, term) if count >= 0 else subtract(out, term)
        return out

    def require_positive_change(paid_change, target_change):
        gain = subtract(signed_moment(target_change), signed_moment(paid_change))
        need(gain[0] > 0, "signed complete invoice does not improve")
        return gain

    # Aggregate ideal regrouping minus one once-global H1 can pass the budget.
    require_positive_change({1: -35 * 18 + 1, 2: 16 * 18, 3: 18}, {})
    # Misreading the same repair as one H1 per LOCAL must fail that pipeline.
    require_rejected("once_global_H1_miscounted_as_one_per_LOCAL",
                     lambda: require_positive_change({1: -35 * 18 + 18,
                                                      2: 16 * 18, 3: 18}, {}))
    require_positive_change({}, {4: 1, 5: 1, 9: -1})
    require_rejected("paid_9_to_4_plus_5_split_misread_as_target_gain",
                     lambda: require_positive_change({4: 1, 5: 1, 9: -1}, {}))
    require_rejected("successor_owned_zero_but_productive_credit_assumed",
                     lambda: require_positive_change({}, {4: 1, 9: -1}))
    report = {
        "status": "PASS_TRANSPORT_BUDGET",
        "source_base": BASE,
        "source_hashes": EXPECTED,
        "selected_kappa": str(kappa),
        "tested_saving": str(s),
        "moment_exponent": str(t),
        "uniform_complex_saving": str(kappa + 6 * gap),
        "source_block": {"range": [9044, 9137], "paid": paid_profile,
                         "closure_seed": [19, 300, 301], "included_events": included,
                         "optimistic_endpoint_paid": ideal_profile, "endpoints": endpoints},
        "outward_rational_enclosures": {name: outward_18(v) for name, v in results.items()},
        "checks": checks,
        "independent_elementary_guard": independent,
        "semantic_mutation_controls_rejected": controls,
        "scope": "Conditional recursive invoice screen, not a legal construction or funded kappa.",
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        for name, v in results.items():
            print(f"{name}: {outward_18(v)}")


if __name__ == "__main__":
    main()
