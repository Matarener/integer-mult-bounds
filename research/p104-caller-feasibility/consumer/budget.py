#!/usr/bin/env python3
"""Independent rational Route 1 arithmetic; no predecessor code is imported.

This module checks named optimistic coverage models and a separately pinned
conditional T740 profile. It does not construct a native network or owners.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_MANIFEST = "52fcd3f2b03c4fe0818860122636f1a749455caa9330a06ad03ab9f678b97c84"
LOG_TERMS = 48
EXP_TERMS = 20
GRID = 10**60
RECEIPT_GRID = 10**35
MARKER = "PASS_ROUTE1_CONSUMER_BUDGET"


class Rejection(ValueError):
    """A source, arithmetic or typed-contract check failed."""


def require(condition, message):
    if not condition:
        raise Rejection(message)


def integer(value, name, minimum=0):
    require(type(value) is int and value >= minimum, name + " must be an integer")
    return value


def rational(value, name, minimum=Q(0)):
    require(type(value) is Q and value >= minimum, name + " must be a Fraction")
    return value


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def parse_json(raw):
    require(type(raw) is bytes and len(raw) <= 2_000_000, "bounded JSON bytes required")
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=lambda s: (_ for _ in ()).throw(Rejection(s)))


def strict_equal(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(strict_equal(v, right[k]) for k, v in left.items())
    if type(left) is list:
        return len(left) == len(right) and all(strict_equal(x, y) for x, y in zip(left, right))
    return left == right


def authenticate(root=ROOT):
    raw = (root / "SOURCES.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_MANIFEST, "source manifest drift")
    manifest = parse_json(raw)
    bodies = {}
    for row in manifest["files"]:
        path = row["local"]
        require(path.startswith("inputs/") and ".." not in path, "source path contract")
        body = (root / path).read_bytes()
        require(len(body) == row["bytes"], "source byte length drift: " + path)
        require(hashlib.sha256(body).hexdigest() == row["sha256"], "source SHA256 drift: " + path)
        blob = b"blob " + str(len(body)).encode() + b"\0" + body
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob drift: " + path)
        bodies[Path(path).name] = body
    require(len(bodies) == 11, "source inventory changed")
    return bodies


def round_down(x, grid=GRID):
    return Q((x.numerator * grid) // x.denominator, grid)


def round_up(x, grid=GRID):
    return -round_down(-x, grid)


def compact(interval):
    low, high = interval
    require(low <= high, "reversed interval")
    return [str(round_down(low, RECEIPT_GRID)), str(round_up(high, RECEIPT_GRID))]


def add_interval(left, right):
    return left[0] + right[0], left[1] + right[1]


def scale_interval(interval, scale):
    require(scale >= 0, "nonnegative interval multiplier required")
    return interval[0] * scale, interval[1] * scale


def atanh_log(u):
    """Outward bounds for log(u), 1 <= u <= 2, by a positive series."""
    require(Q(1) <= u <= Q(2), "log range reduction failed")
    z = (u - 1) / (u + 1)
    power, total = z, Q(0)
    square = z * z
    for j in range(LOG_TERMS):
        total += 2 * power / (2 * j + 1)
        power *= square
    tail = 2 * power / ((2 * LOG_TERMS + 1) * (1 - square))
    return round_down(total), round_up(total + tail)


@lru_cache(maxsize=256)
def log_interval(x):
    rational(x, "log argument", Q(1))
    require(x <= 1_000_000, "bounded log argument required")
    exponent, u = 0, x
    while u >= 2:
        exponent += 1
        u /= 2
    small = atanh_log(u)
    two = atanh_log(Q(2))
    return small[0] + exponent * two[0], small[1] + exponent * two[1]


def exp_point(y):
    rational(y, "exp argument")
    require(y <= Q(1, 10), "bounded exp argument required")
    term, total = Q(1), Q(1)
    for j in range(1, EXP_TERMS + 1):
        term *= y / j
        total += term
    next_term = term * y / (EXP_TERMS + 1)
    tail = next_term / (1 - y / (EXP_TERMS + 2))
    return round_down(total), round_up(total + tail)


@lru_cache(maxsize=512)
def power_interval(x, a):
    rational(a, "saving")
    require(a < Q(1), "saving must be below one")
    log_low, log_high = log_interval(x)
    return exp_point(a * log_low)[0], exp_point(a * log_high)[1]


def read_profile(value):
    require(type(value) is dict and 1 <= len(value) <= 100, "bounded profile required")
    result = {}
    for key, count in value.items():
        require(type(key) is str and key.isascii() and key.isdigit(), "canonical profile rank required")
        rank = int(key)
        require(str(rank) == key and rank > 0, "canonical positive rank required")
        result[rank] = integer(count, "profile count")
    return result


def profile_mass(profile):
    return sum(rank * count for rank, count in profile.items())


def paid_cost(profile, width, a):
    integer(width, "width", 1)
    result = (Q(0), Q(0))
    for rank, count in sorted(profile.items()):
        integer(rank, "rank", 1)
        integer(count, "count")
        require(rank <= width, "child rank exceeds width")
        term = power_interval(Q(width, rank), a)
        result = add_interval(result, scale_interval(term, rank * count))
    return result


def combined_profile(forward, dual, pairs):
    integer(pairs, "pair count", 1)
    return {r: (pairs + 1) * forward.get(r, 0) + pairs * dual.get(r, 0)
            for r in sorted(forward.keys() | dual.keys())}


def deleted_profile(dual, deletion):
    integer(deletion, "deletion allowance")
    require(deletion <= dual[1], "insufficient rank-one children for abstract witness")
    result = dict(dual)
    result[1] -= deletion
    return result


def excess(forward, replacement_dual, pairs, a, *, banks=0, relief=0,
           added_cost=Q(0), clamp=True):
    """Rank-normalized bill minus capacity under the named coverage law.

    `relief` is genuinely unpaid coverage relief; added_cost pays every new
    operation in the same rank-normalized units. It is never inferred free.
    """
    integer(pairs, "pair count", 1)
    integer(banks, "fully paid banks")
    integer(relief, "unpaid coverage relief")
    rational(added_cost, "added cost")
    width, families = 16 * pairs + 9, 208 * pairs
    residual = (width - 1) * families + width * banks - (2 * pairs + 1) * 3014 - relief
    if clamp:
        residual = max(0, residual)
    interval = paid_cost(combined_profile(forward, replacement_dual, pairs), width, a)
    delta = residual + added_cost - width * (families + banks)
    return interval[0] + delta, interval[1] + delta


def must_reject(operation, reason):
    try:
        operation()
    except (Rejection, json.JSONDecodeError) as exc:
        require(reason in str(exc), "control rejected for the wrong reason")
        return str(exc)
    raise Rejection("negative control accepted: " + reason)


def sources(bodies):
    previous = parse_json(bodies["PR2744_RESULT.json"])
    current = parse_json(bodies["PR3609_RECEIPT.json"])
    selected = parse_json(bodies["SELECTED.json"])
    forward = read_profile(previous["censuses"]["forward2458"]["profile"])
    dual = read_profile(current["invoice"]["changed_full"]["native_profile"])
    expected_f = {1: 1216, 2: 74, 3: 86, 4: 104, 5: 48, 6: 42, 7: 68, 8: 8}
    expected_d = {1: 1316, 2: 61, 3: 74, 4: 86, 5: 33, 6: 25, 7: 46, 8: 8, 9: 93}
    require(strict_equal(forward, expected_f), "forward source profile changed")
    require(strict_equal(dual, expected_d), "changed full dual source profile changed")
    require(profile_mass(forward) == 3070 and profile_mass(dual) == 3542, "source masses changed")
    require(sum(forward.values()) == 1646 and sum(dual.values()) == 1742, "source calls changed")
    require(previous["censuses"]["forward2458"]["persistent_endpoint_progress"] == 3014,
            "credited progress changed")
    kappa = Q(selected["kappa"])
    require(kappa == Q(836330098538459, 500000000000000000), "selected saving changed")
    primitive = Q(previous["bills"]["dual2712"]["lower_bounds"]["selected_primitive"]["a"])
    guide = bodies["ALL_PAIR_README.md"].decode()
    for phrase in ["`p+1` forward calls, `p` dual calls, `m=16p+9` and `W=208p`",
                   "`I_B=max(0,(m-1)W+m*B_aux-(2p+1)C)`", "One unpaid coordinate"]:
        require(phrase in guide, "coverage source phrase changed")
    return forward, dual, kappa, primitive


def all_pair_check(forward, dual, kappa, primitive):
    reject_dual = deleted_profile(dual, 425)
    values = {p: excess(forward, reject_dual, p, kappa, clamp=False) for p in [6, 7, 8]}
    require(values[7][0] > 0, "425 allowance no longer rejected")
    require(values[6][0] > values[7][1], "left convex slope not negative")
    require(values[8][0] > values[7][1], "right convex slope not positive")
    stronger = Q(1, 596)
    require(stronger > primitive > kappa / (1 - kappa) > kappa, "test saving order changed")
    require(stronger / (1 + stronger) == Q(1, 597) > kappa, "balanced implication check")
    pass_dual = deleted_profile(dual, 426)
    passed = excess(forward, pass_dual, 7, stronger)
    require(passed[1] < 0, "426 abstract allowance fails stronger test")
    # These are actual rank-normalized additional costs, not free source edits.
    priced_pass = excess(forward, pass_dual, 7, stronger, added_cost=Q(4))
    priced_fail = excess(forward, pass_dual, 7, stronger, added_cost=Q(5))
    require(priced_pass[1] < 0 < priced_fail[0], "added-cost separating control failed")
    fixed_427 = excess(forward, deleted_profile(dual, 427), 4, kappa)
    fixed_428 = excess(forward, deleted_profile(dual, 428), 4, stronger)
    require(fixed_427[0] > 0 and fixed_428[1] < 0, "four-pair allowance check failed")
    bank = excess(forward, reject_dual, 7, kappa, banks=19)
    require(bank == values[7], "fully paid banks changed the excess numerator")
    # Below p=2 the actual clamp only increases the analytic lower bound.
    unclamped = excess(forward, reject_dual, 1, kappa, clamp=False)
    clamped = excess(forward, reject_dual, 1, kappa)
    require(clamped[0] - unclamped[0] == 4050, "negative-residual clamp changed")
    require(unclamped[0] > values[7][1], "p=1 analytic lower bound mismatch")
    baseline = excess(forward, dual, 7, stronger)
    savings = scale_interval(power_interval(Q(121), stronger), 7 * 426)
    require(passed[0] <= baseline[0] - savings[0] <= passed[1], "replacement cost identity drift")
    return {
        "scope": "Fixed forward, per-child integer dual rank deletion, named all-pair coverage; all other costs free unless explicitly added.",
        "all_integer_pairs": "p>=1, every finite number of fully paid banks",
        "convexity_certificate": "E''=16*a*(16p+9)^(a-2)*((16*(1+a)*p+18)*U-16*(1-a)*V)>0 since U>V>0",
        "rejection_saving": str(kappa),
        "rejected_deletion_allowance": 425,
        "global_integer_minimizer_for_rejection": 7,
        "three_exact_excess_intervals": {str(p): compact(v) for p, v in values.items()},
        "positive_abstract_profile": {str(k): v for k, v in sorted(pass_dual.items())},
        "positive_pair_count": 7,
        "positive_deletion_allowance": 426,
        "positive_saving": str(stronger),
        "selected_primitive": str(primitive),
        "abstract_positive_excess": compact(passed),
        "exact_additional_rank_cost_headroom": compact((-passed[1], -passed[0])),
        "added_cost_4_pass_excess": compact(priced_pass),
        "added_cost_5_fail_excess": compact(priced_fail),
        "fixed_four_pairs_427_reject": compact(fixed_427),
        "fixed_four_pairs_428_abstract_pass": compact(fixed_428),
        "no_realised_deletion_or_complete_supplier": True,
    }


def conditional_t740_check(bodies, kappa):
    claim = parse_json(bodies["PR3605_CLAIM.json"])
    profile = read_profile(parse_json(bodies["PR3605_PROFILE.json"]))
    require(strict_equal(profile, read_profile(claim["profile"])), "T740 profile/claim disagreement")
    local = {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}
    idle = {1: 174156, 3: 48334, 4: 1, 5: 10792, 6: 3, 48: 283185}
    rebuilt = {r: 6660 * local.get(r, 0) + idle.get(r, 0) for r in local.keys() | idle.keys()}
    require(strict_equal(profile, rebuilt), "T740 local/idle assembly disagreement")
    require(claim["replicas"] == 740 and claim["calls"] == 6660 and claim["dimension"] == 73,
            "T740 finite dimensions changed")
    require(claim["live"] == 663040 and claim["physical"] == 663549, "T740 stocks changed")
    capacity = 73 * 663040
    require(sum(profile.values()) == 23953011 and profile_mass(profile) == 48165120,
            "T740 complete counts changed")
    require(capacity - profile_mass(profile) == 236800 == 320 * 740, "T740 mass deficit changed")
    low_a, high_a = (Q(s) for s in claim["root_interval"])
    require(high_a - low_a == Q(1, 10**24), "T740 adjacent endpoints changed")
    low_m = scale_interval(paid_cost(profile, 73, low_a), Q(1, capacity))
    high_m = scale_interval(paid_cost(profile, 73, high_a), Q(1, capacity))
    require(low_m[1] < 1 < high_m[0], "T740 strict root bracket failed")
    selected_m = scale_interval(paid_cost(profile, 73, kappa / (1 - kappa)), Q(1, capacity))
    require(selected_m[1] < 1, "T740 selected-saving screen failed")
    supplied_k = Q(claim["kappa"])
    require(supplied_k == low_a - Q(1, 10**46) - Q(1, 10**70), "stated outer endpoint arithmetic")
    require(supplied_k > Q(173, 100000) > kappa, "stated conditional endpoint comparison")
    require(Q(claim["unchanged_bit_endpoint"]) > high_a, "BIT endpoint ordering changed")
    # Positive additions near a root are a sharp control for the eight strata.
    corrupt = dict(profile)
    corrupt[1] += 1
    extra = scale_interval(paid_cost(corrupt, 73, low_a), Q(1, capacity))
    require(extra[0] > 1, "one extra unpaid rank-one child accepted at the claimed lower endpoint")
    return {
        "scope": "Independent profile arithmetic only; conditional finite release/owners/native/outer hypotheses are inherited and not rerun.",
        "head": "3efbb5de06a49ffeea6684482f2d3fe48cdca3fb",
        "profile": {str(r): count for r, count in sorted(profile.items())},
        "width": 73, "families": 663040, "capacity_rank_mass": capacity,
        "children": sum(profile.values()), "paid_rank_mass": profile_mass(profile),
        "root_interval": [str(low_a), str(high_a)],
        "moment_at_lower_endpoint": compact(low_m),
        "moment_at_upper_endpoint": compact(high_m),
        "moment_at_selected_balanced_requirement": compact(selected_m),
        "one_extra_rank_one_child_rejects": compact(extra),
        "stated_outer_endpoint_arithmetic_agrees": True,
        "new_outer_proof_or_complete_release_replay": False,
    }


def prior_hosting_check(bodies, kappa):
    text = bodies["PR3574_README.md"].decode()
    require("1,126 extra" in text and "At 1,127 units" in text, "prior hosting statement changed")
    channel = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}
    require(profile_mass(channel) == 2368, "prior channel mass")
    local = dict(channel)
    local[1] += 208 * 9
    capacity = Q(73 * 832, 9)
    saving = kappa / (1 - kappa)
    values = {}
    for hosted in [0, 1126, 1127]:
        paid = dict(local)
        paid[1] += hosted
        remaining = 2472 - hosted
        interval = paid_cost(paid, 73, saving)
        residual = scale_interval(power_interval(Q(73, 51), saving), remaining)
        values[hosted] = scale_interval(add_interval(interval, residual), 1 / capacity)
    require(values[0][1] < 1 and values[1126][1] < 1 < values[1127][0],
            "prior 1126/1127 hosting comparison disagrees")
    return {
        "source_pr": 3574, "head": "eb11cd484c23990c250bdc67ae61829ebae35536",
        "scope": "Different native-channel plus unit-step correction provider; every hosting rank unit displaces one ideal rank-51 idle mass unit.",
        "saving": str(saving),
        "moments": {str(h): compact(interval) for h, interval in values.items()},
        "provider_geometry_native_and_owners_not_replayed": True,
    }


def analyze(root=ROOT):
    bodies = authenticate(root)
    forward, dual, kappa, primitive = sources(bodies)
    pair_result = all_pair_check(forward, dual, kappa, primitive)
    t740 = conditional_t740_check(bodies, kappa)
    hosting = prior_hosting_check(bodies, kappa)
    controls = {
        "boolean_count": must_reject(lambda: read_profile({"1": True}), "must be an integer"),
        "duplicate_key": must_reject(lambda: parse_json(b'{"a":1,"a":2}'), "duplicate JSON key"),
        "boolean_pair_count": must_reject(lambda: combined_profile(forward, dual, True), "must be an integer"),
        "out_of_range_rank": must_reject(lambda: paid_cost({74: 1}, 73, kappa), "child rank exceeds width"),
        "negative_cost": must_reject(lambda: excess(forward, dual, 7, kappa, added_cost=Q(-1)), "added cost"),
        "typed_receipt_identity": not strict_equal({"schema_version": 1}, {"schema_version": True}),
    }
    require(controls["typed_receipt_identity"], "Boolean/integer receipt alias accepted")
    return {
        "schema_version": 1, "status": MARKER,
        "source_manifest_sha256": SOURCE_MANIFEST,
        "arithmetic": {"log_terms": LOG_TERMS, "exp_terms": EXP_TERMS,
                       "rounding_grid": str(GRID), "decision_method": "exact rational outward intervals; no floating-point decisions"},
        "all_pair_deletion": pair_result,
        "conditional_t740": t740,
        "distinct_prior_hosting_threshold": hosting,
        "negative_controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly create the local receipt")
    args = parser.parse_args()
    observed = analyze()
    receipt = ROOT / "RESULT.json"
    if args.write:
        receipt.write_text(json.dumps(observed, sort_keys=True, indent=2) + "\n")
    else:
        require(strict_equal(observed, parse_json(receipt.read_bytes())), "typed receipt mismatch")
    print(MARKER)


if __name__ == "__main__":
    try:
        main()
    except (Rejection, KeyError, OSError, json.JSONDecodeError) as error:
        print("FAIL_ROUTE1_CONSUMER_BUDGET " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
