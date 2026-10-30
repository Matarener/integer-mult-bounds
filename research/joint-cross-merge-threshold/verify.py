#!/usr/bin/env python3
"""Exact disjoint cross-side merge threshold. Apache-2.0, Nick Petalas."""

from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import hashlib
from itertools import combinations, combinations_with_replacement, permutations
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
SAVING = F(7, 2000)
SCALE = 1 << 120
SOURCE_HASH = "e712e5373ecbfea0c1b7c115b52eea4fb533c6c7c2ebae3aa98a2dd1f058721c"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(numerator, denominator):
    return -(-numerator // denominator)


def log_unit_bounds(numerator, denominator):
    """Bounds on log(numerator/denominator), with ratio in [1, 2]."""
    require(denominator <= numerator <= 2 * denominator, "log ratio")
    a, b = numerator - denominator, numerator + denominator
    lower = upper = 0
    for j in range(64):
        top = 2 * SCALE * a ** (2 * j + 1)
        bottom = (2 * j + 1) * b ** (2 * j + 1)
        lower += top // bottom
        upper += ceil_div(top, bottom)
    # The positive atanh tail is at most 2*z^129/(129*(1-z^2)).
    tail_top = 2 * SCALE * a**129 * b**2
    tail_bottom = 129 * b**129 * (b**2 - a**2)
    upper += ceil_div(tail_top, tail_bottom)
    return F(lower, SCALE), F(upper, SCALE)


def exp_bounds(x):
    """Positive Taylor series plus a geometric bound for its tail."""
    require(0 <= x <= 1, "exponential range")
    term = total = F(1)
    for j in range(1, 25):
        term *= x / j
        total += term
    # All subsequent term ratios are at most 1/26.
    tail = term * x / 25 * F(26, 25)
    return total, total + tail


@lru_cache(maxsize=512)
def power_bounds(rank, saving=SAVING):
    require(isinstance(rank, int) and 1 <= rank <= 1024, "rank range")
    require(0 < saving <= F(1, 8), "saving range")
    shift = rank.bit_length() - 1
    l2, u2 = log_unit_bounds(2, 1)
    low, high = log_unit_bounds(rank, 1 << shift)
    low += shift * l2
    high += shift * u2
    exp_low, _ = exp_bounds(saving * low)
    _, exp_high = exp_bounds(saving * high)
    return rank / exp_high, rank / exp_low


def moment_bounds(histogram, saving=SAVING):
    low = high = F(0)
    require(len(histogram) <= 1024, "histogram size")
    for rank, count in histogram.items():
        require(isinstance(count, int) and count >= 0, "job count")
        left, right = power_bounds(rank, saving)
        low += count * left
        high += count * right
    return low, high


def load_ledger(raw=None):
    if raw is None:
        raw = (PACKAGE / "inputs/PR5298-RESULT.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_HASH, "source hash")
    ledger = json.loads(raw)["ledger"]
    paid, targets = {}, Counter()
    for side in ("complex", "bit"):
        jobs = Counter()
        for role in ledger["paid_by_role"][side].values():
            jobs.update({int(r): n for r, n in role.items()})
        require(sum(jobs.values()) <= 100000, "side capacity")
        require(all(1 <= r <= 1024 and n > 0 for r, n in jobs.items()), "jobs")
        paid[side] = jobs
        for role in ledger["targets_by_role"][side].values():
            targets.update({int(r): n for r, n in role.items()})
    return paid, targets


def descending_jobs(histogram):
    return sorted(histogram.elements(), reverse=True)


def merge(paid, left, right, count):
    require(0 <= count <= min(len(left), len(right)), "merge count")
    result = paid.copy()
    for j in range(count):
        a, b = left[j], right[j]
        result[a] -= 1
        result[b] -= 1
        result[a + b] += 1
    require(all(n >= 0 for n in result.values()), "disjointness")
    return +result


def threshold_certificate(paid, targets):
    left, right = (descending_jobs(paid[s]) for s in ("complex", "bit"))
    original = paid["complex"] + paid["bit"]
    t_low, t_high = moment_bounds(targets)
    before = merge(original, left, right, 405)
    after = merge(original, left, right, 406)
    b_low, b_high = moment_bounds(before)
    a_low, a_high = moment_bounds(after)
    require(t_high < b_low, "405 must fail even under optimal pairing")
    require(t_low > a_high, "406 must pass")
    require(sum(r*n for r, n in before.items()) == sum(r*n for r, n in after.items()),
            "merge must preserve paid rank mass")
    require(sum(original.values()) - sum(after.values()) == 406, "job reduction")
    pairs = Counter(zip(left[:406], right[:406]))
    require(pairs == {(72, 63): 222, (72, 56): 2, (64, 56): 182}, "pair witness")
    scale = 10**12
    margins = [[(t_low-p_high)*scale//1, ceil_div((t_high-p_low).numerator*scale,
                 (t_high-p_low).denominator)] for p_low, p_high in
               ((b_low, b_high), (a_low, a_high))]
    return {"minimum_merges": 406, "saving": str(SAVING),
            "margin_scale": scale, "margin_integer_intervals": margins,
            "pairs": [[a, b, n] for (a, b), n in sorted(pairs.items(), reverse=True)]}


def integer_power_certificate(paid, targets):
    """Certify coarse power bounds independently, by integer exponentiation."""
    scale, bounds = 1 << 36, {}
    for rank in range(1, 146):
        low, high = power_bounds(rank)
        lower = low * scale // 1
        upper = ceil_div(high.numerator * scale, high.denominator)
        exact = rank**1993 * scale**2000
        require(lower**2000 <= exact <= upper**2000, "integer power certificate")
        bounds[rank] = (F(lower, scale), F(upper, scale))
    original = paid["complex"] + paid["bit"]
    left, right = (descending_jobs(paid[s]) for s in ("complex", "bit"))
    target_low = sum(n * bounds[r][0] for r, n in targets.items())
    target_high = sum(n * bounds[r][1] for r, n in targets.items())
    before = merge(original, left, right, 405)
    after = merge(original, left, right, 406)
    require(target_high < sum(n * bounds[r][0] for r, n in before.items()),
            "independent 405 exclusion")
    require(target_low > sum(n * bounds[r][1] for r, n in after.items()),
            "independent 406 witness")
    return len(bounds)


def finite_matching_oracle():
    """Enumerate every partial matching of two labeled three-job lists."""
    cases = matchings = 0
    lists = tuple(combinations_with_replacement(range(1, 5), 3))
    for left in lists:
        for right in lists:
            original = Counter(left + right)
            for count in range(1, 4):
                optimum = merge(original, sorted(left, reverse=True),
                                sorted(right, reverse=True), count)
                _, best_high = moment_bounds(optimum)
                for a_ids in combinations(range(3), count):
                    for b_ids in permutations(range(3), count):
                        candidate = original.copy()
                        for i, j in zip(a_ids, b_ids):
                            a, b = left[i], right[j]
                            candidate[a] -= 1
                            candidate[b] -= 1
                            candidate[a+b] += 1
                        candidate = +candidate
                        if candidate != optimum:
                            low, _ = moment_bounds(candidate)
                            require(best_high < low, "matching oracle")
                        matchings += 1
                cases += 1
    return cases, matchings


def controls():
    rejected = 0
    for function, arguments in ((power_bounds, (0,)), (power_bounds, (1025,)),
                                (power_bounds, (2, F(0))), (exp_bounds, (F(2),)),
                                (log_unit_bounds, (3, 1)),
                                (merge, (Counter({1: 2}), [1], [1], 2)),
                                (load_ledger, (b"{}",))):
        try:
            function(*arguments)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid argument was accepted")
    good = Counter({2: 1, 8: 1})
    crossed = Counter({5: 2})
    # Largest-with-largest gives merged ranks 8 and 2, versus 5 and 5.
    _, high = moment_bounds(good)
    low, _ = moment_bounds(crossed)
    require(high < low, "reverse-pairing control")
    return rejected + 1


def main():
    paid, targets = load_ledger()
    result = threshold_certificate(paid, targets)
    cases, matchings = finite_matching_oracle()
    result.update({"matching_cases": cases, "enumerated_matchings": matchings,
                   "integer_power_bounds": integer_power_certificate(paid, targets),
                   "controls": controls()})
    hashes = {str(p.relative_to(PACKAGE)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(PACKAGE.rglob("*")) if p.is_file()}
    print("PASS_JOINT_CROSS_MERGE_THRESHOLD " + json.dumps(result, sort_keys=True))
    print(json.dumps({"receipt_schema": 1, "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
