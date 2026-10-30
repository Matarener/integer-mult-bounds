#!/usr/bin/env python3
"""Optimize two logical defect guards on the cited PR4510 suffix ledger.

Produced by Nick Petalas. Apache-2.0.
The ledger and its logical perturbation theorem are David Ganz's PR4510.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import platform

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUT = "research/native-suffix-errors/RESULT.json"
PIN = "38fa4bc3b526b12dbb89a3841e71b4778a26746632198995794544ad2b91b6e6"
EXPECTED = {
    "forward": (16263, 1168, 11, 9, 189405, Fraction(7257, 8192)),
    "backward": (16271, 1168, 13, 11, 224371, Fraction(827, 1024)),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_pin(raw):
    require(len(raw) <= 2 * 1024 * 1024, "input exceeds two MiB")
    require(sha256(raw).hexdigest() == PIN, "source hash mismatch")


def load_cases(raw):
    check_pin(raw)
    payload = json.loads(raw)
    require(payload["status"] == "PASS_NATIVE_SUFFIX_ERROR_CERTIFICATES",
            "unexpected input schema")
    cases = {}
    for direction in EXPECTED:
        data = payload["results"]["rewritten"][direction]
        source_rows = data["persistent_output_rows"]
        require(len(source_rows) == 632, "expected 632 published output rows")
        rows = tuple((Fraction(r["weights"]["add"]),
                      Fraction(r["weights"]["scale"])) for r in source_rows)
        require(all(a >= 0 and s >= 0 for a, s in rows), "negative weight")
        counts = data["events_per_class"]
        costs = counts["add"], counts["scale"]
        require(all(type(c) is int and 0 < c <= 20000 for c in costs),
                "invalid event count")
        cases[direction] = rows, costs, tuple(r["role"] for r in source_rows)
    return cases


def bound(rows, guards):
    ga, gs = guards
    require(type(ga) is int and type(gs) is int, "guards must be integers")
    require(0 <= ga <= 256 and 0 <= gs <= 256, "guard out of range")
    return max(a / (1 << ga) + s / (1 << gs) for a, s in rows)


def certificate(rows, costs, guards):
    """A monotonicity certificate excludes every cheaper integer pair."""
    ca, cs = costs
    ga, gs = guards
    require(ga > 0 and gs > 0, "this certificate needs positive guards")
    maximum = bound(rows, guards)
    require(maximum <= 1, "candidate violates an output constraint")
    add_floor = max(a for a, _ in rows) / (1 << (ga - 1))
    require(add_floor > 1, "one fewer ADD guard is not excluded")
    cost = ca * ga + cs * gs
    require(ca * (ga + 1) > cost, "larger ADD guard could be cheaper")
    scale_floor = bound(rows, (ga, gs - 1))
    require(scale_floor > 1, "one fewer SCALE guard is not excluded")
    return {"guards": list(guards), "charge": cost,
            "maximum_output_bound": str(maximum),
            "add_only_lower_witness": str(add_floor),
            "next_add_cost_floor": ca * (ga + 1),
            "one_less_scale_witness": str(scale_floor)}


def enumerate_optimum(rows, costs, upper):
    """Independent bounded search, using integer inequalities on every row."""
    ca, cs = costs
    max_a, max_s = upper // ca, upper // cs
    require(max_a <= 32 and max_s <= 256, "enumeration capacity exceeded")
    # Clear rational row denominators before evaluating any candidate.
    integer_rows = []
    for a, s in rows:
        denominator = a.denominator * s.denominator
        integer_rows.append((int(a * denominator), int(s * denominator),
                             denominator))
    winners, tested = [], 0
    best = upper
    for ga in range(max_a + 1):
        for gs in range((upper - ca * ga) // cs + 1):
            tested += 1
            feasible = all(a * (1 << gs) + s * (1 << ga)
                           <= d * (1 << (ga + gs))
                           for a, s, d in integer_rows)
            cost = ca * ga + cs * gs
            if feasible and cost <= best:
                if cost < best:
                    winners = []
                best = cost
                winners.append((ga, gs))
    require(winners, "no feasible allocation")
    return best, winners, tested


def expect_rejection(function, *args):
    try:
        function(*args)
    except (ValueError, TypeError):
        return
    raise ValueError("negative control was accepted")


def controls(cases, raw):
    count = 0
    for direction, (rows, costs, _) in cases.items():
        _, _, ga, gs, _, _ = EXPECTED[direction]
        for bad in [(ga - 1, gs), (ga, gs - 1), (ga + 1, gs)]:
            expect_rejection(certificate, rows, costs, bad)
            count += 1
        for bad in [(-1, gs), (ga, 257), (True, gs), (ga, "9")]:
            expect_rejection(bound, rows, bad)
            count += 1
    expect_rejection(check_pin, raw + b" ")
    return count + 1


def run_case(direction, case):
    rows, costs, roles = case
    ca, cs, ga, gs, expected_cost, expected_bound = EXPECTED[direction]
    require(costs == (ca, cs), "source event counts differ")
    result = certificate(rows, costs, (ga, gs))
    require(result["charge"] == expected_cost, "unexpected optimum charge")
    require(Fraction(result["maximum_output_bound"]) == expected_bound,
            "unexpected output bound")
    uniform = ga
    uniform_cost = (ca + cs) * uniform
    require(bound(rows, (uniform, uniform)) <= 1, "uniform is infeasible")
    require(bound(rows, (uniform - 1, uniform - 1)) > 1,
            "uniform benchmark is not minimal")
    best, winners, tested = enumerate_optimum(rows, costs, uniform_cost)
    require(best == expected_cost and winners == [(ga, gs)],
            "independent enumeration disagrees")
    values = tuple(a / (1 << ga) + s / (1 << gs) for a, s in rows)
    result.update({"output_rows": len(rows), "event_counts": list(costs),
                   "uniform_guards": [uniform, uniform],
                   "uniform_charge": uniform_cost,
                   "charge_saved": uniform_cost - expected_cost,
                   "unique_optimum": True, "pairs_enumerated": tested,
                   "maximizing_roles": [r for r, v in zip(roles, values)
                                        if v == expected_bound]})
    return result


def main():
    raw = (ROOT / INPUT).read_bytes()
    cases = load_cases(raw)
    result = {direction: run_case(direction, cases[direction])
              for direction in EXPECTED}
    control_count = controls(cases, raw)
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((PACKAGE / name).read_bytes()).hexdigest()
              for name in names}
    print(json.dumps({"status": "PASS_SUFFIX_GUARD_ALLOCATION",
                      "claim_type": "finite certificate and scoped optimum",
                      "python": platform.python_version(), "input_sha256": PIN,
                      "package_sha256": hashes, "results": result,
                      "rejection_controls": control_count}, sort_keys=True))


if __name__ == "__main__":
    main()
