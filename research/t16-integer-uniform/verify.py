#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Uniform pooled T16 integer optimum. Standard-library exact arithmetic.

Nick Petalas. Certificate from PR3352; dual lineage Ali Romman/Hanson Sun.
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
UPPER = Q(1, 7)
DEGREE = 19
SCALE = 1 << 160


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    need(path.stat().st_size <= 2**24, "JSON size bound")
    return json.loads(path.read_text())


def sources():
    pins = load_json(HERE / "SOURCES.json")
    inputs = {}
    for row in pins["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source drift")
            inputs[row["path"]] = json.loads(raw)
    origin = pins["retained_certificate"]
    raw = (HERE / "CERTIFICATE.json").read_bytes()
    need(
        hashlib.sha256(raw).hexdigest() == origin["sha256"],
        "retained certificate drift",
    )
    return inputs


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


def potential(cert, rows):
    paths = cert["residue_paths"]
    need(len(paths) == 37 and paths[0] == [], "potential origin")
    values = []
    for target, path in enumerate(paths):
        need(isinstance(path, list) and len(path) <= 36, "bounded path")
        terms, residue = {}, 0
        for i in path:
            need(type(i) is int and 0 <= i < len(rows), "path pattern")
            terms = combine([(terms, 1), (edge(rows[i]), 1)])
            residue = (residue + rows[i][4]) % 37
        need(residue == target, "path destination")
        values.append(terms)
    need(values[13] == {17: 37, 1: -5, 48: -13}, "target potential")
    return values


def slacks(rows, values):
    counts = Counter()
    failure_edge = None
    for s in range(37):
        for i, row in enumerate(rows):
            t = (s + row[4]) % 37
            terms = combine([(values[s], 1), (edge(row), 1), (values[t], -1)])
            need(sum(r * c for r, c in terms.items()) == 0, "zero linear endpoint")
            counts[tuple(sorted(terms.items()))] += 1
            if terms == {1: -74, 5: 74, 8: -37}:
                failure_edge = [s, i, t]
    need(sum(counts.values()) == 43031, "all directed edges")
    need(failure_edge is not None, "larger-domain control edge")
    return counts, failure_edge


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


def bernstein_lower(terms, logs, upper=UPPER):
    need(0 < upper <= Q(1, 7), "certified saving domain")
    coefficients = []
    for k in range(1, DEGREE + 2):
        lower = sum(
            (c * r * logs[r][0 if c >= 0 else 1] ** k / factorial(k) for r, c in terms),
            Q(0),
        )
        coefficients.append(lower)
    # exp(a*log(48/r)) <= 1/(1-4/7) < 3; Lagrange tail / a.
    tail = sum(abs(c * r) for r, c in terms) * upper ** (DEGREE + 1)
    tail *= Q(3 * 4 ** (DEGREE + 2), factorial(DEGREE + 2))
    result = []
    for j in range(DEGREE + 1):
        bound = sum(
            (
                coefficients[k] * upper**k * Q(comb(j, k), comb(DEGREE, k))
                for k in range(j + 1)
            ),
            Q(0),
        )
        result.append(bound - tail)
    need(min(result) > 0, "uniform Bernstein positivity")
    return min(result)


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


def witness(cert, rhs):
    need(len(cert["integer_patterns"]) == 10, "witness bound")
    used, idle = [0] * 9, Counter()
    for row in cert["integer_patterns"]:
        capacity, ns, n = row["capacity"], row["counts"], row["multiplicity"]
        need(capacity in CAPS and type(n) is int and n > 0, "integer multiplicity")
        need(
            len(ns) == 5 and all(type(v) is int and v >= 0 for v in ns), "helper counts"
        )
        r = capacity - sum(w * v for w, v in zip(WIDTHS, ns, strict=True))
        need(r >= 0, "witness capacity")
        col = [int(capacity == c) for c in CAPS] + ns
        used = [a + n * b for a, b in zip(used, col, strict=True)]
        if r:
            idle[r] += n
    need(tuple(used) == tuple(rhs), "integer inventories")
    need(dict(idle) == {1: 2431, 17: 1, 48: 4887}, "attaining idle profile")
    a = sum(n * v for n, v in zip(rhs, cert["fractional_dual_constant"], strict=True))
    b = sum(n * v for n, v in zip(rhs, cert["fractional_dual_power48"], strict=True))
    need(a == 89952 and b == 180832 and b % 37 == 13, "aggregate residue")
    return dict(idle)


def verify(cert, rhs):
    rows = patterns(cert)
    values = potential(cert, rows)
    spectra, failure_edge = slacks(rows, values)
    logs = {r: log_bounds(Q(48, r)) for r in range(1, 49)}
    need(all(0 <= lo <= hi < 4 for lo, hi in logs.values()), "log bounds below four")
    methods = Counter()
    least = None
    for terms in spectra:
        if not terms:
            method = "symbolic"
        elif min(hinges(terms)) >= 0:
            need(max(hinges(terms)) > 0, "strict concavity support")
            method = "concavity"
        else:
            bound = bernstein_lower(terms, logs)
            least = bound if least is None else min(least, bound)
            method = "Bernstein"
        methods[method] += 1
    need(methods == {"symbolic": 1, "concavity": 5228, "Bernstein": 75}, "proof census")
    powers = {r: rational_power(r, Q(17, 20)) for r in (1, 5, 8)}
    bad_upper = -74 * powers[1][0] + 74 * powers[5][1] - 37 * powers[8][0]
    need(bad_upper < Q(-44, 1000), "larger-domain fixed-potential failure")
    return {
        "saving_interval": ["0", "1/7"],
        "patterns": len(rows),
        "edges": 43031,
        "unique_slacks": len(spectra),
        "unique_proof_methods": dict(methods),
        "symbolic_edges": spectra[()],
        "strict_edges": 43031 - spectra[()],
        "Bernstein_lower_bound": str(
            Q(least.numerator * 10**6 // least.denominator, 10**6)
        ),
        "idle_profile": witness(cert, rhs),
        "linear_endpoint_mass": 237024,
        "fixed_potential_failure": {
            "saving": "3/20",
            "edge": failure_edge,
            "slack_terms": {"1": -74, "5": 74, "8": -37},
            "upper_bound": "-11/250",
        },
    }


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
        "PASS_T16_INTEGER_UNIFORM",
        report["patterns"],
        report["edges"],
        report["unique_proof_methods"],
    )


if __name__ == "__main__":
    main()
