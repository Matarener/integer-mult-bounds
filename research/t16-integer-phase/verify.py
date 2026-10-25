#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Sharp pooled T16 integer profile through a=1/2. Exact standard-library proof.

Nick Petalas. Extends PR3352/3364; retained dual lineage Ali Romman/Hanson Sun.
Concavity and logarithm arithmetic adapted from the credited PR3364 checker.
"""

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from math import comb, factorial
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTHS = (4, 5, 7, 8, 9)
CAPS = (8, 16, 32, 48)
RHS = (10752, 7168, 7168, 7168, 8064, 4608, 4320, 17568, 34560)
UPPER = Q(1, 2)
DEGREE = 31
SCALE = 1 << 160


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    need(path.stat().st_size <= 2**24, "JSON size bound")
    return json.loads(path.read_text())


def source_inventory(inputs):
    prefix = "research/complex-t16-rare-pattern-exchanges/data/"
    plan, spec = (inputs[prefix + n] for n in ("PLAN.json", "SPEC.json"))
    manifest = inputs["research/community-frontier1094-audit/SELECTED-SOURCE.json"][
        "files"
    ]
    for name in ("PLAN.json", "SPEC.json"):
        raw = (ROOT / (prefix + name)).read_bytes()
        need(
            hashlib.sha256(raw).hexdigest() == manifest[prefix + name],
            "selected binding",
        )
    need(
        (plan["M"], plan["live"], plan["T"], plan["L"]) == (73, 14336, 16, 9),
        "selected template",
    )
    ports = len(plan["provider_registry"]["gauge44"]["ports"])
    need(ports == 112 and len(plan["windows"]) == 288, "bin source shape")
    bins, widths, calls = Counter(), Counter(), set()
    for capacity, _times in plan["windows"].values():
        need(capacity in CAPS, "source capacity")
        bins[capacity] += ports
    provider = spec["providers"]["gauge44"]
    expected = Counter({int(w): n for w, n in provider["inventory"].items()})
    need(len(plan["per_call_widths"]) == 144, "source call bound")
    for row in plan["per_call_widths"]:
        call = row["stage"], row["replica"]
        need(call not in calls and Counter(row["widths"]) == expected, "source call")
        calls.add(call)
        widths.update(row["widths"])
    need(calls == set(product(range(9), range(16))), "all calls")
    actual = tuple(bins[c] for c in CAPS) + tuple(widths[w] for w in WIDTHS)
    need(actual == RHS, "source inventories")
    return actual


def patterns(cert):
    aa, bb = cert["fractional_dual_constant"], cert["fractional_dual_power48"]
    need(len(aa) == len(bb) == 9 and all(type(n) is int for n in aa + bb), "dual shape")
    rows = []
    for i, capacity in enumerate(CAPS):
        for counts in product(*(range(capacity // w + 1) for w in WIDTHS)):
            r = capacity - sum(n * w for n, w in zip(counts, WIDTHS, strict=True))
            if r < 0:
                continue
            a = aa[i] + sum(n * v for n, v in zip(counts, aa[4:], strict=True))
            b = bb[i] + sum(n * v for n, v in zip(counts, bb[4:], strict=True))
            need(a + 48 * b == 37 * r, "dual rank identity")
            rows.append((capacity, counts, r, a, b))
    need(len(rows) == 1163, "all patterns")
    return rows


def combine(expressions):
    total = Counter()
    for terms, sign in expressions:
        for r, c in terms.items():
            total[r] += sign * c
    return {r: c for r, c in total.items() if c}


def edge(row):
    _capacity, _counts, r, a, b = row
    return combine([({r: 37} if r else {}, 1), ({1: a, 48: b}, -1)])


def hinges(terms):
    need(len(terms) <= 49 and all(1 <= r <= 48 for r, _c in terms), "hinge domain")
    return [sum(c * min(r, t) for r, c in terms) for t in range(1, 49)]


def short_log(q):
    """atanh series, 1 <= q <= 2; geometric bound on omitted terms."""
    need(1 <= q <= 2, "reduced logarithm domain")
    z = (q - 1) / (q + 1)
    lower = sum((2 * z ** (2 * k + 1) / (2 * k + 1) for k in range(64)), Q(0))
    error = 2 * z**129 / (129 * (1 - z * z))
    return lower, lower + error


def log_bounds(q):
    need(1 <= q <= 48, "logarithm domain")
    shifts = 0
    for _ in range(6):
        if q < 2:
            break
        q /= 2
        shifts += 1
    need(1 <= q < 2, "bounded logarithm reduction")
    lo, hi = short_log(q)
    l2, u2 = short_log(Q(2))
    lo, hi = lo + shifts * l2, hi + shifts * u2
    return Q(lo.numerator * SCALE // lo.denominator, SCALE), Q(
        -(-hi.numerator * SCALE // hi.denominator), SCALE
    )


def rational_power(r, p):
    """Outward 128-bit dyadic bracket using exact integer powering."""
    need(type(r) is int and 1 <= r <= 48 and 0 < p <= 1, "power domain")
    need(p.denominator <= 20, "power denominator bound")
    scale = 1 << 128
    target = r**p.numerator * scale**p.denominator
    lo, hi = 0, 48 * scale + 1
    for _ in range(135):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        if mid**p.denominator <= target:
            lo = mid
        else:
            hi = mid
    need(
        hi == lo + 1 and lo**p.denominator <= target < hi**p.denominator,
        "exact root bracket",
    )
    return Q(lo, scale), Q(hi, scale)


def sources():
    pins = load_json(HERE / "SOURCES.json")
    expected = {
        "research/community-frontier1094-audit/SELECTED-SOURCE.json",
        "research/complex-t16-rare-pattern-exchanges/data/PLAN.json",
        "research/complex-t16-rare-pattern-exchanges/data/SPEC.json",
    }
    need(len(pins["files"]) == 5, "bounded source manifest")
    inputs = {}
    for row in pins["files"]:
        if row["usage"] == "input":
            need(row["path"] in expected, "declared source path")
            raw = (ROOT / row["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source drift")
            inputs[row["path"]] = json.loads(raw)
    need(set(inputs) == expected, "complete input set")
    raw = (HERE / "PREDECESSOR.json").read_bytes()
    need(
        hashlib.sha256(raw).hexdigest() == pins["retained_certificate"]["sha256"],
        "retained predecessor drift",
    )
    return inputs


def potentials(cert, rows):
    paths = cert["potential_options"]
    need(len(paths) == 37 and paths[0] == [[]], "potential origin")
    values = []
    for target, options in enumerate(paths):
        need(1 <= len(options) <= 2, "bounded potential choices")
        current = []
        for path in options:
            need(isinstance(path, list) and len(path) <= 3, "bounded path")
            terms, residue = {}, 0
            for i in path:
                need(type(i) is int and 0 <= i < len(rows), "path pattern")
                terms = combine([(terms, 1), (edge(rows[i]), 1)])
                residue = (residue + rows[i][4]) % 37
            need(residue == target and terms not in current, "path destination")
            current.append(terms)
        values.append(current)
    need(sum(map(len, values)) == 49, "49 path candidates")
    need(
        values[13]
        == [
            {17: 37, 1: -5, 48: -13},
            {5: 37, 1: -79, 48: -13, 14: 37},
        ],
        "two target profiles",
    )
    return values


def bernstein_lower(terms, logs):
    coefficients = []
    for k in range(1, DEGREE + 2):
        lower = sum(
            (c * r * logs[r][0 if c >= 0 else 1] ** k / factorial(k) for r, c in terms),
            Q(0),
        )
        coefficients.append(lower)
    # log(48/r)<4; a<=1/2; exp(a*log(48/r))<exp(2)<9.
    tail = sum(abs(c * r) for r, c in terms) * UPPER ** (DEGREE + 1)
    tail *= Q(9 * 4 ** (DEGREE + 2), factorial(DEGREE + 2))
    result = []
    for j in range(DEGREE + 1):
        bound = sum(
            (
                coefficients[k] * UPPER**k * Q(comb(j, k), comb(DEGREE, k))
                for k in range(j + 1)
            ),
            Q(0),
        )
        result.append(bound - tail)
    return min(result)


def certify(terms, logs):
    need(sum(r * c for r, c in terms) == 0, "zero linear endpoint")
    if not terms:
        return "symbolic", None
    hh = hinges(terms)
    if min(hh) >= 0:
        need(max(hh) > 0, "strict concavity support")
        return "concavity", None
    lower = bernstein_lower(terms, logs)
    return ("Bernstein" if lower > 0 else None), lower


def all_edges(rows, values):
    logs = {r: log_bounds(Q(48, r)) for r in range(1, 49)}
    need(all(0 <= lo <= hi < 4 for lo, hi in logs.values()), "log interval bound")
    cache, used, obligations = {}, set(), 0
    for s in range(37):
        for left in values[s]:
            for row in rows:
                t = (s + row[4]) % 37
                found = False
                for right in values[t]:
                    slack = combine([(left, 1), (edge(row), 1), (right, -1)])
                    terms = tuple(sorted(slack.items()))
                    if terms not in cache:
                        cache[terms] = certify(terms, logs)
                    if cache[terms][0] is not None:
                        used.add(terms)
                        found = True
                        break
                need(found, "uniform minimum-potential edge")
                obligations += 1
    need(obligations == 56987, "all path-pattern obligations")
    methods = Counter(cache[t][0] for t in used)
    lower = min(cache[t][1] for t in used if cache[t][0] == "Bernstein")
    return {
        "path_pattern_obligations": obligations,
        "distinct_successful_comparisons": len(used),
        "proof_methods": dict(methods),
        "Bernstein_lower_bound": str(
            Q(lower.numerator * 10**6 // lower.denominator, 10**6)
        ),
    }


def inventory(profile, rhs):
    need(isinstance(profile, list) and 1 <= len(profile) <= 11, "witness bound")
    used, idle = [0] * 9, Counter()
    for row in profile:
        capacity, ns, n = row["capacity"], row["counts"], row["multiplicity"]
        need(capacity in CAPS and type(n) is int and n > 0, "integer multiplicity")
        need(len(ns) == 5 and all(type(v) is int and v >= 0 for v in ns), "counts")
        r = capacity - sum(w * v for w, v in zip(WIDTHS, ns, strict=True))
        need(r >= 0, "witness capacity")
        col = [int(capacity == c) for c in CAPS] + ns
        used = [a + n * b for a, b in zip(used, col, strict=True)]
        if r:
            idle[r] += n
    need(tuple(used) == tuple(rhs), "integer inventories")
    need(sum(r * n for r, n in idle.items()) == 237024, "fixed idle rank mass")
    return dict(idle)


def power_sum(terms, p):
    need(1 <= len(terms) <= 49, "bounded power sum")
    lo, hi = Q(0), Q(0)
    for r, c in terms.items():
        ll, uu = rational_power(r, p)
        lo += c * (ll if c >= 0 else uu)
        hi += c * (uu if c >= 0 else ll)
    return lo, hi


def phase_checks():
    # h(p) is new idle cost minus old idle cost.
    h = {5: 1, 14: 1, 17: -1, 1: -2}
    need(power_sum(h, Q(3, 5))[0] > 0, "old profile wins at a=2/5")
    need(power_sum(h, Q(7, 12))[1] < 0, "new profile wins at a=5/12")
    need(power_sum(h, Q(17, 20))[0] > 0, "old profile wins at a=3/20")
    half = power_sum(h, Q(1, 2))
    need(half[1] < Q(-7, 50), "strict new optimum at a=1/2")
    failed = power_sum({1: -74, 5: 74, 8: -37}, Q(17, 20))
    need(failed[1] < Q(-11, 250), "predecessor fixed-potential failure")
    return {
        "first_transition_saving_bracket": ["2/5", "5/12"],
        "transition_equation": "5^(1-a)+14^(1-a)-17^(1-a)-2=0",
        "old_profile_optimal_at": "3/20",
        "old_fixed_potential_slack_upper_at_3/20": "-11/250",
        "old_minus_new_idle_lower_at_1/2": "7/50",
    }


def verify(cert, rhs):
    rows = patterns(cert)
    values = potentials(cert, rows)
    report = all_edges(rows, values)
    need(len(cert["integer_profiles"]) == 2, "two attaining inventories")
    profiles = [inventory(p, rhs) for p in cert["integer_profiles"]]
    need(
        profiles == [{1: 2431, 17: 1, 48: 4887}, {1: 2429, 5: 1, 14: 1, 48: 4887}],
        "two exact profiles",
    )
    a = sum(n * v for n, v in zip(rhs, cert["fractional_dual_constant"], strict=True))
    b = sum(n * v for n, v in zip(rhs, cert["fractional_dual_power48"], strict=True))
    need((a, b, b % 37) == (89952, 180832, 13), "aggregate residue")
    report.update(
        saving_interval=["0", "1/2"],
        patterns=len(rows),
        states=37,
        path_candidates=49,
        idle_profiles=profiles,
        phase=phase_checks(),
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = verify(load_json(HERE / "CERTIFICATE.json"), source_inventory(sources()))
    raw = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write:
        (HERE / "RESULT.json").write_text(raw)
    else:
        need(
            json.loads(raw) == load_json(HERE / "RESULT.json"), "whole receipt equality"
        )
    print(
        "PASS_T16_INTEGER_PHASE",
        report["path_pattern_obligations"],
        report["proof_methods"],
    )


if __name__ == "__main__":
    main()
