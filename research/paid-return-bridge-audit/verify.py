#!/usr/bin/env python3
"""Independent exact checks of PR5526's conditional paid-return bridge.

Prepared for josecarlosgonzalezroque-design with OpenAI Codex assistance.
Apache-2.0. No predecessor executable is imported or executed.
The universal argument and inherited premises are in AUDIT.md.
"""
import argparse
import ast
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = "research/clifford-pointwise-faithfulness/"
PASSIVE = "research/passive-saved-query-ceiling/evidence/"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    inputs = [item for item in sources["files"] if item["usage"] == "input"]
    need(len(inputs) == 8, "eight declared immutable review inputs")
    for item in inputs:
        raw = (ROOT / item["path"]).read_bytes()
        need(sha256(raw).hexdigest() == item["sha256"], "source bytes changed: " + item["path"])
    return len(inputs)


def dot(a, b):
    return sum((x*y for x, y in zip(a, b, strict=True)), Q(0))


def plus(a, b, factor=Q(1)):
    return tuple(x + factor*y for x, y in zip(a, b, strict=True))


def perpendicular(row, orthogonal):
    row = tuple(map(Q, row))
    for vector in orthogonal:
        row = plus(row, vector, -dot(row, vector)/dot(vector, vector))
    return row


def basis(rows):
    result = []
    for row in rows:
        residual = perpendicular(row, result)
        if any(residual):
            result.append(residual)
    return result


def mm(a, b, d):
    return tuple(sum(a[d*i+k]*b[d*k+j] for k in range(d))
                 for i in range(d) for j in range(d))


def transpose(a, d):
    return tuple(a[d*j+i] for i in range(d) for j in range(d))


def identity(d):
    return tuple(Q(i == j) for i in range(d) for j in range(d))


def block(matrix, column, count):
    z = (Q(0),)*len(matrix)
    return tuple(x for j in range(count) for x in (matrix if j == column else z))


def left(matrix, row, d):
    size = d*d
    return tuple(x for start in range(0, len(row), size)
                 for x in mm(matrix, row[start:start+size], d))


def orbit(rows, group, d):
    return [left(g, row, d) for row in rows for g in group]


def squared_error(targets, rows, d):
    orthogonal = basis(rows)
    errors = [perpendicular(t, orthogonal) for t in targets]
    return sum((dot(e, e)/d for e in errors), Q(0))


def c3_fixture(count):
    d = 3
    one = identity(d)
    shift = tuple(Q(i == (j+1) % d) for i in range(d) for j in range(d))
    group = [one, shift, mm(shift, shift, d)]
    target = tuple(Q((1, 1, -1)[i] if i == j else 0)
                   for i in range(d) for j in range(d))
    need(mm(group[-1], shift, d) == one, "cyclic unitary group closes")
    need(all(mm(transpose(g, d), g, d) == one for g in group), "unitary orbit actions")
    need(mm(transpose(target, d), target, d) == one, "unitary target")
    history = orbit([block(one, j, count) for j in range(count)], group, d)
    targets = [block(target, j, count) for j in range(count)]
    frame = orbit(targets, group, d)
    need(len(basis(history)) == 3*count, "initial module dimension")
    need(len(basis(history+frame)) == 6*count, "disjoint full target modules")
    # The two coefficient supports are independent, but are NOT orthogonal.
    for j, a in enumerate(history):
        for k, b in enumerate(frame):
            need(dot(a, b)/d == (Q(1, 3) if j == k else 0), "nonorthogonal cross Gram")
    initial = basis(history)
    residual = [perpendicular(t, initial) for t in frame]
    for j, a in enumerate(residual):
        for k, b in enumerate(residual):
            need(dot(a, b)/d == (Q(8, 9) if j == k else 0), "relative Gram is 8/9 I")
    return d, group, history, targets, frame


def module_checks():
    cases = outside = 0
    minima = {}
    for count in (2, 3):
        d, group, history, targets, frame = c3_fixture(count)
        full_support = basis(history+frame)
        shear = tuple(map(Q, (1, 1, 0, 0, 1, 0, 0, 0, 1)))
        need(shear not in group, "feedback need not be an ordinary action")
        seed = 0x5526 + count
        for trial in range(24):
            available = list(history)
            previous = (Q(0),)*(d*d*count)
            for q in range(count+1):
                if q:
                    fresh = []
                    for _ in previous:
                        seed = (1664525*seed + 1013904223) % (1 << 32)
                        fresh.append(Q(seed % 11 - 5, 1 + (seed >> 8) % 3))
                    returned = plus(tuple(fresh), left(shear, previous, d))
                    outside += bool(any(perpendicular(returned, full_support)))
                    previous = returned
                    available += orbit([returned], group, d)
                dim = len(basis(available)) - len(basis(history))
                need(dim <= q*len(group), "one return adds at most h quotient dimensions")
                error = squared_error(targets, available, d)
                need(error >= Q(8, 9)*max(count-q, 0), "relative error lower bound")
                orbit_error = squared_error(frame, available, d)
                need(orbit_error == len(group)*error, "unitary orbit factor cancels once")
                key = str(count) + ":" + str(q)
                minima[key] = min(minima.get(key, error), error)
                cases += 1
        # The enlarged arbitrary-oracle model attains the HS lower bound.
        for q in range(count+1):
            available = history + orbit(targets[:q], group, d)
            error = squared_error(targets, available, d)
            need(error == Q(8, 9)*(count-q), "exact target returns attain fixture bound")
            cases += 1
    need(outside > 0, "new paid rows outside the reviewed coefficient support")
    return {"prefix_cases": cases, "returns_outside_initial_and_target_span": outside,
            "relative_gram_lower": "8/9", "whole_gram_lower": "2/3",
            "minimum_errors_by_b_and_q": {k: str(v) for k, v in sorted(minima.items())}}


def exhaustive_two_field():
    d = 2
    one = identity(d)
    z = tuple(map(Q, (1, 0, 0, -1)))
    x = tuple(map(Q, (0, 1, 1, 0)))
    group = [one, z]
    history = orbit([block(one, j, 2) for j in range(2)], group, d)
    targets = [block(x, j, 2) for j in range(2)]
    histogram = {}
    # All four missing coefficients in {-1,0,1}; diagonal terms are in history.
    for entries in product((-1, 0, 1), repeat=4):
        row = tuple(map(Q, (0, entries[0], entries[1], 0,
                            0, entries[2], entries[3], 0)))
        error = squared_error(targets, history+orbit([row], group, d), d)
        need(error >= 1, "exhaustive one-return error floor")
        histogram[str(error)] = histogram.get(str(error), 0) + 1
    need(sum(histogram.values()) == 81 and histogram.get("1", 0) > 0,
         "complete ternary domain and attaining cases")
    return histogram


def semantic_controls():
    d, group, history, targets, frame = c3_fixture(2)
    one_return = history + orbit([targets[0]], group, d)
    error = squared_error(targets, one_return, d)
    need(error == Q(8, 9), "normalization control fixture")
    controls = {
        "omit_orbit_division": error < Q(8, 9)*len(group),
        "pretend_disjoint_supports_orthogonal": error < 1,
        "normalize_by_payload_dimension_twice": error/d < Q(8, 9),
        "cache_a_target_without_reducing_missing_count":
            squared_error(targets, history+frame, d) < Q(8, 9)*2,
    }
    # One ordinary-stable return supplies two singular targets on distinct inputs.
    p0, p1 = tuple(map(Q, (1, 0, 0, 0))), tuple(map(Q, (0, 0, 0, 1)))
    z = tuple(map(Q, (1, 0, 0, -1)))
    singular_targets = [block(p0, 0, 2), block(p1, 1, 2)]
    packed = plus(*singular_targets)
    controls["drop_unitary_target_premise"] = squared_error(
        singular_targets, orbit([packed], [identity(2), z], 2), 2) == 0
    zero = (Q(0),)*len(packed)
    controls["forget_retained_history_after_clear"] = (
        len(basis([packed, zero])) == 1 and len(basis([zero])) == 0)
    controls["use_noninvariant_initial_history"] = (
        len(basis([packed])) < len(basis(orbit([packed], [identity(2), z], 2))))
    need(all(controls.values()), "semantic counterexamples expose weakened premises")
    return sorted(controls)


def extract_invoice():
    path = PASSIVE + "frozen/pr4948-mixed-thin-gate/check.py"
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    selected = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = node.targets[0]
            if isinstance(name, ast.Name) and name.id in ("P", "Tar"):
                need(name.id not in selected, "unique literal invoice assignment")
                selected[name.id] = ast.literal_eval(node.value)
    need(set(selected) == {"P", "Tar"}, "both source invoice dictionaries found")
    for profile in selected.values():
        need(all(type(r) is int and type(n) is int and r > 0 and n > 0
                 for r, n in profile.items()), "positive integer rank histogram")
    return selected["P"], selected["Tar"]


def log_interval(r, terms=96):
    z = Q(r-1, r+1)
    total, power = Q(0), z
    for k in range(terms):
        total += 2*power/(2*k+1)
        power *= z*z
    tail = 2*power/((2*terms+1)*(1-z*z))
    return total, total+tail


def exp_minus(x, terms):
    need(0 <= x < 1, "alternating exponential terms decrease")
    total = term = Q(1)
    for k in range(1, terms+1):
        term *= -x/k
        total += term
    return total


def power_interval(r, saving):
    if r == 1:
        return Q(1), Q(1)
    lo, hi = log_interval(r)
    lower = r*exp_minus(saving*hi, 9)
    upper = r*exp_minus(saving*lo, 8)
    scale = 10**12
    return Q((lower*scale).__floor__(), scale), Q((upper*scale).__ceil__(), scale)


def pricing_checks():
    paid, targets = extract_invoice()
    gate = read_json(PASSIVE + "frozen/pr4948-saved-query-macro-gate/GRADE-GATE.json")
    ports = gate["actual_source_zero_diagonal_ports"]
    need(len(ports) == len(set(ports)) == 104 and ports == sorted(ports),
         "104 distinct declared source ports")
    inherited = read_json(PASSIVE + "INDEPENDENT.json")
    need(inherited["earlier_grades"] == [0, 1] and inherited["target_grade"] == 9
         and inherited["post_FULL_unselected_grade_census"] == {"7": 5408},
         "inherited grade declarations match the audited implication")
    declared = read_json(SOURCE + "REPAIR-INVOICE.json")
    repaired = dict(paid)
    repaired[1] += len(ports)
    need(repaired == {int(k): v for k, v in declared["paid"].items()},
         "repair adds exactly the claimed 104 rank-one jobs")
    need(targets == {int(k): v for k, v in declared["targets"].items()},
         "original target credits retained exactly once")
    def hinges(q):
        return [sum(n*min(r, k) for r, n in paid.items()) + q
                - sum(n*min(r, k) for r, n in targets.items()) for k in range(1, 18)]
    h104, h96, h95 = hinges(104), hinges(96), hinges(95)
    need(min(h104) > 0 and h104[-1] == 8, "exact repair loses every power tariff")
    need(min(h96) == 0 and h96[-1] == 0 and min(h96[:-1]) > 0,
         "96 returns exhaust rank mass and every concave margin")
    need(h95[-1] == -1, "95 threshold is necessary, not excluded by rank mass")
    source = read_json(SOURCE + "REPAIR-RESULT.json")
    need(source["new_returns_required"] == len(ports)
         and source["first_width"] == 72 and source["later_width"] == 84,
         "declared return and width thresholds")
    for row in source["optimistic_invoice_comparison"]["hinges"]:
        need(row["value"] == (h104[row["rank"]-1] if row["rank"] else 0),
             "all saved support hinges agree with independent sums")
    saving = Q(source["reference_tariff_budget"]["reference_saving"])
    intervals = {r: power_interval(r, saving) for r in sorted(set(paid) | set(targets))}
    lower = sum(targets.get(r, 0)*lo - paid.get(r, 0)*hi
                for r, (lo, hi) in intervals.items())
    upper = sum(targets.get(r, 0)*hi - paid.get(r, 0)*lo
                for r, (lo, hi) in intervals.items())
    need(36 < lower <= upper < 37, "independent reference budget is strictly between 36 and 37")
    source_lo, source_hi = map(Q, source["reference_tariff_budget"]["margin_interval"])
    need(lower <= source_lo <= source_hi <= upper, "predecessor interval fits independent enclosure")
    for width, value in ((72, Q(1, 9)*(1-Q(36, 104))),
                         (84, Q(125, 126)*(1-Q(36, 104)))):
        need(Q(source["reference_tariff_budget"]["operator_error_squared_from_width_" + str(width)])
             == value, "reference-budget approximation consequence")
    expected_floors = {
        "any_profitable_repair_operator_error_squared_from_width_72": Q(1, 9)*(1-Q(95, 104)),
        "any_profitable_repair_operator_error_squared_from_width_84": Q(125, 126)*(1-Q(95, 104)),
        "operator_error_squared_at_103_returns_and_width_84": Q(125, 126)*(1-Q(103, 104)),
    }
    for key, value in expected_floors.items():
        need(Q(source[key]) == value, "source approximation consequence: " + key)
    return {"source_ports": ports, "inherited_grades": [0, 1, 7], "target_grade": 9,
            "paid": paid, "targets": targets, "all_integer_hinges_q104": h104,
            "all_integer_hinges_q96": h96, "rank_mass_at_q95": h95[-1],
            "reference_saving": str(saving),
            "independent_margin_interval": [str(lower), str(upper)],
            "reference_max_returns_for_positive_margin": 36,
            "reference_width84_operator_error_squared": str(Q(125, 126)*(1-Q(36, 104))),
            "source_error_floors": {k: str(v) for k, v in expected_floors.items()},
            "interval_method": "96-term positive log series; 9/8-term alternating exp; outward 10^-12 grid"}


def run():
    return {"status": "PASS_PAID_RETURN_BRIDGE_AUDIT", "source_inputs": authenticate(),
            "module": module_checks(), "ternary_one_return_errors": exhaustive_two_field(),
            "semantic_controls": semantic_controls(), "invoice": pricing_checks(),
            "scope": "Conditional proof bridge and declared invoice; no native replay or new kappa"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the complete recomputed receipt")
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        print(encoded, end="")
    else:
        need(json.loads((HERE / "RESULT.json").read_text(encoding="utf-8")) == json.loads(encoded),
             "saved audit receipt differs")
        print(result["status"])
