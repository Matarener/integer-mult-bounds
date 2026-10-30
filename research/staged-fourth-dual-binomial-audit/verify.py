"""Independent finite PR4091 dual audit; no predecessor code imports.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
See PROOF.md for the positive binomial series and its uniform tail bound.
"""

import argparse
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/staged-fourth-mixture-ceiling"
WIDTHS = (5, 6, 7, 8, 9)
CAPACITIES = (8, 16, 32, 48)
LOW, HIGH = F(173, 100000), F(174, 100000)
SCALE = 10**40
TERMS = 2048
DIM = 74


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    # JSON object keys are strings, including when constructed from rank integers.
    normalized = json.loads(json.dumps(value))
    return json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()


def check_digest(data, expected):
    require(hashlib.sha256(data).hexdigest() == expected, "source digest mismatch")


def authenticate():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    inputs = [row for row in pins["files"] if row["usage"] == "input"]
    for row in inputs:
        check_digest((ROOT / row["path"]).read_bytes(), row["sha256"])
    return {row["path"]: row["sha256"] for row in inputs}


def read_source(relative):
    raw = (SOURCE / relative).read_bytes()
    return json.loads(gzip.decompress(raw) if relative.endswith(".gz") else raw)


def binary_span(vectors):
    """Explicit 512-element vector space, independent of echelon rank code."""
    span = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, "binary frame vector")
        span |= {x ^ vector for x in span}
    require(len(span) & (len(span) - 1) == 0, "span size")
    return span


def combine(*terms):
    result = {}
    for coefficient, expression in terms:
        for rank, value in expression.items():
            result[rank] = result.get(rank, F(0)) + coefficient * value
    return {rank: F(value) for rank, value in result.items() if value}


def symbol(rank):
    return {rank: F(1)} if rank else {}


def source_model():
    order = read_source("source4088/owner/ORDER.json")
    require(len(order) == 3240 and len(set(map(tuple, order))) == 3240,
            "complete unique call order")
    require(set(map(tuple, order)) == set(product(range(9), range(360))),
            "nine stages and current 360 replicas")
    template = read_source("source4088/owner/TEMPLATE.json.gz")
    children = template["idle_children"]
    require(template["m"] == 73, "ambient rank")
    require(len(children) == 2016, "template child count")
    require(len({(row["port"], row["child"]) for row in children}) == 2016,
            "distinct port/child records")
    ports = {row["port"] for row in children}
    require(len(ports) == 112, "port count")
    for port in ports:
        require(Counter(row["rank"] for row in children if row["port"] == port)
                == {8: 6, 16: 4, 32: 4, 48: 4}, "per-port capacities")
    # The historical `replicas:37` fields are deliberately not multipliers.
    bins = Counter(row["rank"] for row in children)
    bins = {cap: bins[cap] * 360 for cap in CAPACITIES}
    profiles, widths = {}, {}
    for orientation in ("base", "extra"):
        by_kind = {}
        for kind in ("THREE", "FOUR"):
            word = read_source(f"source4088/inputs/{kind}-{orientation}.json.gz")
            alive = set(range(224, 704)) - set(word["removed"])
            require(len(alive) == 408, "helper inventory")
            by_role = {}
            for helper in sorted(alive):
                entry = binary_span(word["start_extra"].get(str(helper), []))
                exit_frame = binary_span(word["helper_final"].get(
                    str(helper), [1 << i for i in range(9)]))
                require(entry <= exit_frame, "nested helper endpoints")
                by_role[helper] = (len(exit_frame).bit_length()
                                   - len(entry).bit_length())
            histogram = Counter(by_role.values())
            profile = {int(r): n for r, n in word["report"]["local_profile"].items()}
            require(all(type(n) is int and n >= 0 and 0 < r < 73
                        for r, n in profile.items()), "reported local profile")
            if kind in profiles:
                require(profiles[kind] == profile and widths[kind] == histogram,
                        "orientation agreement")
            profiles[kind], widths[kind] = profile, dict(histogram)
            by_kind[kind] = by_role
        require(by_kind["THREE"].keys() == by_kind["FOUR"].keys(),
                "same helper identities")
        difference = {h: (by_kind["THREE"][h], by_kind["FOUR"][h])
                      for h in by_kind["THREE"]
                      if by_kind["THREE"][h] != by_kind["FOUR"][h]}
        require(difference == {601: (8, 7)}, "changed helper601 width")
    require(widths["THREE"] == {5: 28, 6: 18, 7: 56, 8: 93, 9: 213},
            "THREE width model")
    delta = combine((1, profiles["FOUR"]), (-1, profiles["THREE"]))
    require(delta == {1: 2, 3: 3, 4: -3}, "reported local delta")
    return bins, profiles, widths, delta


def patterns():
    rows = []
    for capacity in CAPACITIES:
        for counts in product(*(range(capacity // w + 1) for w in WIDTHS)):
            residual = capacity - sum(w * n for w, n in zip(WIDTHS, counts))
            if residual >= 0:
                rows.append((capacity, *counts, residual))
    validate_patterns(rows)
    return rows


def validate_patterns(rows):
    """Check every residual coefficient by an independent coin-series DP."""
    ways = [1] + [0] * max(CAPACITIES)
    for width in WIDTHS:
        for used in range(width, len(ways)):
            ways[used] += ways[used - width]
    expected = {(c, residual): ways[c - residual]
                for c in CAPACITIES for residual in range(c + 1)}
    actual = Counter((row[0], row[-1]) for row in rows)
    require(len(rows) == len(set(rows)), "duplicate pattern")
    for row in rows:
        require(len(row) == 7 and row[0] in CAPACITIES, "pattern schema")
        require(all(type(n) is int and n >= 0 for n in row[1:]), "whole helpers")
        require(sum(w * n for w, n in zip(WIDTHS, row[1:6])) + row[-1] == row[0],
                "pattern capacity")
    require(all(actual[key] == count for key, count in expected.items())
            and set(actual) <= set(expected), "pattern residual spectrum")
    require(len(rows) == 841, "841 patterns")


def constraint_row(pattern):
    return [int(pattern[0] == cap) for cap in CAPACITIES] + list(pattern[1:6])


def solve(matrix, rhs):
    """Exact Gauss-Jordan solve, with several RHS columns and explicit pivots."""
    n = len(matrix)
    require(all(len(row) == n for row in matrix) and len(rhs) == n,
            "square exact system")
    columns = len(rhs[0])
    require(all(len(row) == columns for row in rhs), "RHS shape")
    augmented = [[F(v) for v in a + b] for a, b in zip(matrix, rhs)]
    determinant = F(1)
    for col in range(n):
        pivot = next((i for i in range(col, n) if augmented[i][col]), None)
        require(pivot is not None, "singular exact system")
        if pivot != col:
            augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
            determinant = -determinant
        factor = augmented[col][col]
        determinant *= factor
        augmented[col] = [v / factor for v in augmented[col]]
        for row in range(n):
            if row != col:
                factor = augmented[row][col]
                augmented[row] = [x - factor * y
                                  for x, y in zip(augmented[row], augmented[col])]
    solution = [row[n:] for row in augmented]
    require(all(sum(F(matrix[i][j]) * solution[j][k] for j in range(n))
                == rhs[i][k] for i in range(n) for k in range(columns)),
            "solution residual")
    return solution, determinant


def dense(expression):
    return [expression.get(r, F(0)) for r in range(DIM)]


def sparse(vector):
    return {r: coefficient for r, coefficient in enumerate(vector) if coefficient}


def support_from_certificate(certificate):
    support = []
    for row in certificate["primal"]:
        support.append((row["capacity"], *(row["helper_counts"][str(w)] for w in WIDTHS),
                        row["residual"]))
    require(len(support) == 8 and len(set(support)) == 8, "central support")
    require(set(support) <= set(patterns()), "central whole-helper patterns")
    return support


def reconstruct_dual(support, side, delta):
    equations = [constraint_row(row) for row in support]
    rhs = [dense(symbol(row[-1])) for row in support]
    if side == "middle":
        # d + v7 - v8 = 0 is free-mixture stationarity.
        equations.append([0, 0, 0, 0, 0, 0, -1, 1, 0])
        rhs.append(dense(delta))
    else:
        entering = ((32, 0, 0, 1, 2, 1, 0) if side == "left"
                    else (48, 0, 2, 0, 0, 4, 0))
        equations.append(constraint_row(entering))
        rhs.append(dense(symbol(entering[-1])))
    answer, determinant = solve(equations, rhs)
    return [sparse(row) for row in answer], determinant


def ceil_div(numerator, denominator):
    return -(-numerator // denominator)


@lru_cache(None)
def normalized_power(rank, exponent, terms=TERMS, scale=SCALE):
    """Enclose (rank**(1-a)-rank)/a by a positive binomial series.

    t1=z, t(k+1)=t(k)*(k-a)*z/(k+1), z=1-1/rank.
    The omitted tail is <= rank*t(N+1). All operations round outwards.
    """
    require(type(rank) is int and rank >= 1 and 0 < exponent < 1,
            "binomial domain")
    require(type(terms) is int and terms >= 1 and scale >= 1, "series precision")
    if rank == 1:
        return F(0), F(0)
    a_num, a_den = exponent.numerator, exponent.denominator
    low = scale * (rank - 1) // rank
    high = ceil_div(scale * (rank - 1), rank)
    sum_low = sum_high = 0
    for k in range(1, terms + 1):
        sum_low += low
        sum_high += high
        numerator = (k * a_den - a_num) * (rank - 1)
        denominator = (k + 1) * a_den * rank
        low = low * numerator // denominator
        high = ceil_div(high * numerator, denominator)
    # high now bounds the first OMITTED term, scaled by `scale`.
    return F(-rank * (sum_high + rank * high), scale), F(-rank * sum_low, scale)


def interval_expression(expression, lower=LOW, upper=HIGH, terms=TERMS):
    require(0 < lower <= upper < 1, "exponent interval")
    require(sum(r * c for r, c in expression.items()) == 0, "zero rank mass")
    low = high = F(0)
    for rank, coefficient in expression.items():
        # Each normalized power is increasing: positive-series coefficients decrease.
        a = normalized_power(rank, lower, terms)[0]
        b = normalized_power(rank, upper, terms)[1]
        low += coefficient * (a if coefficient > 0 else b)
        high += coefficient * (b if coefficient > 0 else a)
    return low, high


def slack(pattern, dual):
    return combine((1, symbol(pattern[-1])),
                   *((-n, expression) for n, expression in
                     zip(constraint_row(pattern), dual)))


def check_dual(rows, dual):
    tight, bounds = [], []
    for row in rows:
        expression = slack(row, dual)
        if not expression:
            tight.append(row)
        else:
            low, high = interval_expression(expression)
            require(low > 0, f"nonpositive dual slack: {row}")
            bounds.append((low, high, row))
    require(bounds, "nontrivial strict constraints")
    return tight, min(bounds)


def primal_system(support, bins, widths, free_mixture=False):
    columns = [constraint_row(row) for row in support]
    if free_mixture:
        # B*y = N*widths + x*(e7-e8), put x on the left.
        columns.append([0, 0, 0, 0, 0, 0, -1, 1, 0])
    matrix = list(map(list, zip(*columns)))
    base = [bins[c] for c in CAPACITIES] + [3240 * widths["THREE"][w] for w in WIDTHS]
    direction = [0, 0, 0, 0, 0, 0, 1, -1, 0]
    rhs = [[value] if free_mixture else [value, dx]
           for value, dx in zip(base, direction)]
    return solve(matrix, rhs)


def check_primal(rows, multiplicities, x, bins, widths):
    require(len(rows) == len(multiplicities), "primal length")
    require(0 <= x <= 3240 and all(value >= 0 for value in multiplicities),
            "nonnegative primal")
    totals = [sum(F(n) * value for n, value in zip(column, multiplicities))
              for column in zip(*(constraint_row(row) for row in rows))]
    expected = [bins[c] for c in CAPACITIES] + [
        3240 * widths["THREE"][w] + x * ((w == 7) - (w == 8)) for w in WIDTHS]
    require(totals == expected, "primal bin/helper balance")
    return combine(*((value, symbol(row[-1])) for row, value in zip(rows, multiplicities)))


def fixed_power_expression(expression, exponent):
    low = high = F(0)
    for rank, coefficient in expression.items():
        a, b = normalized_power(rank, exponent)
        a, b = rank + exponent * a, rank + exponent * b
        low += coefficient * (a if coefficient > 0 else b)
        high += coefficient * (b if coefficient > 0 else a)
    return low, high


def json_expression(expression):
    return {str(r): str(c) for r, c in sorted(expression.items())}


def interval_json(pair):
    return list(map(str, pair))


def compute():
    pins = authenticate()
    bins, profiles, widths, delta = source_model()
    published = read_source("RESULT.json")
    rows = patterns()
    support = support_from_certificate(published)
    require(bins == {int(k): v for k, v in published["bin_counts"].items()}, "source bins")
    central, determinant = primal_system(support, bins, widths, True)
    mixture = central[-1][0]
    values = [row[0] for row in central[:-1]]
    require(mixture == published["optimum_fourth_calls"] == 1080, "unique mixture")
    require(values == [F(row["multiplicity"]) for row in published["primal"]],
            "published central primal")
    idle = check_primal(support, values, mixture, bins, widths)
    profile = combine((3240, profiles["THREE"]), (mixture, delta), (1, idle))
    require(profile == {int(r): n for r, n in published["complete_profile"].items()},
            "complete paid profile")
    require(sum(r * n for r, n in profile.items()) == 23431680, "complete paid mass")
    dual_reports, affine_reports = {}, {}
    for side in ("left", "middle", "right"):
        dual, dual_det = reconstruct_dual(support, side, delta)
        recorded = published["dual"][side]
        expected = [{int(r): F(c) for r, c in recorded[kind][str(key)].items()}
                    for kind, keys in (("capacity_dual", CAPACITIES), ("item_dual", WIDTHS))
                    for key in keys]
        require(dual == expected, f"{side} independently solved potentials")
        tight, smallest = check_dual(rows, dual)
        recorded_tight = {(c, *counts, residual)
                          for c, counts, residual in recorded["identically_tight"]}
        require(set(tight) == recorded_tight, f"{side} exact tight face")
        slope = combine((1, delta), (1, dual[6]), (-1, dual[7]))
        require(slope == {int(r): F(c) for r, c in recorded["slope_expression"].items()},
                f"{side} mixture slope")
        slope_bounds = interval_expression(slope)
        if side == "middle":
            require(not slope and set(tight) == set(support), "central uniqueness support")
        else:
            require(slope_bounds[1] < 0 if side == "left" else slope_bounds[0] > 0,
                    f"{side} strict slope sign")
            entering = ((32, 0, 0, 1, 2, 1, 0) if side == "left"
                        else (48, 0, 2, 0, 0, 4, 0))
            segment_support = support + [entering]
            affine, primal_det = primal_system(segment_support, bins, widths)
            endpoints = (0, 1080) if side == "left" else (1080, 3240)
            for x in endpoints:
                check_primal(segment_support, [b + x * d for b, d in affine], x, bins, widths)
            require(all(not slack(row, dual) for row in segment_support),
                    f"{side} affine complementary slackness")
            affine_reports[side] = {
                "domain": list(endpoints), "determinant": str(primal_det),
                "patterns": [list(row) for row in segment_support],
                "multiplicity_constant_and_x": [list(map(str, pair)) for pair in affine],
            }
            if side == "right":
                at1090 = [b + 1090 * d for b, d in affine]
                idle1090 = check_primal(segment_support, at1090, 1090, bins, widths)
                require(idle1090 == {3: 22783, 5: 1625, 48: 138492}, "1090 idle consequence")
                require(at1090[-1] == 5, "five entering cap48 patterns")
        dual_reports[side] = {
            "basis_determinant": str(dual_det), "tight_patterns": [list(row) for row in tight],
            "strict_patterns": len(rows) - len(tight),
            "minimum_slack_over_a_lower_bound": str(smallest[0]),
            "minimizing_enclosure_pattern": list(smallest[2]),
            "slope_expression": json_expression(slope),
            "slope_over_a_interval": interval_json(slope_bounds),
        }
    # Coarse existence check only: do not refine or replay the published root digits.
    bill = combine((1, profile), (-896 * 360, symbol(73)))
    low_bill, high_bill = fixed_power_expression(bill, LOW), fixed_power_expression(bill, HIGH)
    require(low_bill[1] < 0 < high_bill[0], "root inside dual-certified interval")
    return {
        "status": "PASS_STAGED_FOURTH_DUAL_BINOMIAL_AUDIT",
        "source_sha256": pins,
        "scope": "Fixed PR4091 pooled LP; source local-profile reports inherited; no owner/native/admission replay or new kappa.",
        "enclosure": {"method": "positive binomial series; integer outward rounding; geometric tail",
                      "terms": TERMS, "scale": str(SCALE), "exponent_interval": [str(LOW), str(HIGH)]},
        "patterns": len(rows), "pattern_counts": dict(Counter(row[0] for row in rows)),
        "pattern_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
        "source_widths": widths, "source_bins": bins,
        "inherited_local_profiles": profiles,
        "central_primal_determinant": str(determinant), "unique_mixture": str(mixture),
        "central_multiplicities": list(map(str, values)), "idle": json_expression(idle),
        "complete_paid_profile": json_expression(profile),
        "dual": dual_reports, "affine_primal": affine_reports,
        "x1090": {"idle": json_expression(idle1090), "new_cap48_pattern_count": "5",
                  "status": "right-face pooled optimum; central eight-pattern support alone is infeasible"},
        "coarse_root_endpoint_moments": [interval_json(low_bill), interval_json(high_bill)],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Explicitly write a new evidence JSON")
    args = parser.parse_args()
    result = compute()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(canonical(result) == canonical(json.loads((HERE / "RESULT.json").read_text())),
                "saved evidence differs")
    print(result["status"], "patterns=841 duals=3 tight=11/8/9 unique_x=1080")


if __name__ == "__main__":
    main()
