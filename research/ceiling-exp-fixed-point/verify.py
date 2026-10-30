#!/usr/bin/env python3
"""Compare one selected ceiling evaluation with an opt-in fixed-point exponential."""
import hashlib
import importlib.util
import statistics
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ENGINE = ROOT / "research/complex-local-word-ceiling/ceiling.py"
PIN = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
LEMMA = (
    "For the selected local word, the fixed-point exponential returns the same "
    "256-bit bounds as the pinned Taylor series, so the published ceiling bracket "
    "is unchanged."
)
LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
PUBLISHED = (
    Q(52814190909, 31250000000000),
    Q(1690054109089, 1000000000000000),
)


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def load_engine():
    spec = importlib.util.spec_from_file_location("pinned_ceiling", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_fast():
    spec = importlib.util.spec_from_file_location("ceiling_exp_fixed_point", PACKAGE / "fast_exp.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    require(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    raw = ENGINE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PIN, "pinned ceiling.py bytes changed")
    engine = load_engine()
    fast = load_fast()
    for value in range(1, 74):
        engine.ln(value)

    def fast_exp(low, high):
        return fast.bounds(low, high, engine.PREC, engine.require)

    original = engine.exp
    visited = []

    def record(low, high):
        visited.append((low, high))
        return original(low, high)

    engine.exp = record
    reference = engine.ceiling(dict(LOCAL), 73, 896, 9, 64)
    wider = dict(LOCAL)
    wider[1] += 1
    reference_wider = engine.ceiling(wider, 73, 896, 9, 64)
    mismatches = 0
    for low, high in visited:
        if fast_exp(low, high) != original(low, high):
            mismatches += 1
    require(mismatches == 0, "fixed-point bounds differ on a visited argument")
    require(reference == PUBLISHED, "reference ceiling moved off the published bracket")
    engine = load_engine()
    for value in range(1, 74):
        engine.ln(value)
    engine.exp = fast_exp
    accelerated = engine.ceiling(dict(LOCAL), 73, 896, 9, 64)
    accelerated_wider = engine.ceiling(dict(wider), 73, 896, 9, 64)
    require(accelerated == reference and accelerated_wider == reference_wider,
            "accelerated ceiling bracket differs")
    require(fast_exp(Q(0), Q(0)) == original(Q(0), Q(0)), "zero argument differs")
    for bad in ((Q(-1, 100), Q(0)), (Q(0), Q(3, 5))):
        try:
            fast_exp(*bad)
        except ValueError:
            pass
        else:
            raise SystemExit("out-of-range argument was accepted")
    truncated = (
        fast.series(Q(1, 10), False, engine.PREC, max_terms=1),
        fast.series(Q(1, 10), True, engine.PREC, max_terms=1),
    )
    require(truncated != original(Q(1, 10), Q(1, 10)), "truncated series was accepted")

    def timed(use_fast):
        module = load_engine()
        for value in range(1, 74):
            module.ln(value)
        if use_fast:
            module.exp = fast_exp
        start = time.perf_counter()
        bracket = module.ceiling(dict(LOCAL), 73, 896, 9, 64)
        return time.perf_counter() - start, bracket

    reference_times = []
    fast_times = []
    for sample in range(3):
        first_fast = sample % 2 == 1
        for use_fast in (first_fast, not first_fast):
            elapsed, bracket = timed(use_fast)
            require(bracket == PUBLISHED, "timed ceiling bracket differs")
            (fast_times if use_fast else reference_times).append(elapsed)
    reference_median = statistics.median(reference_times)
    fast_median = statistics.median(fast_times)
    require(fast_median * 5 < reference_median, "fixed-point evaluation was not at least 5x faster")
    ratio = reference_median / fast_median
    print(
        "PASS_CEILING_EXP_FIXED_POINT "
        f"ref_s={reference_median:.6f} fast_s={fast_median:.6f} ratio={ratio:.2f} "
        f"visited={len(visited)} mismatches=0 "
        f"bracket={PUBLISHED[1].numerator}/{PUBLISHED[1].denominator}"
    )


if __name__ == "__main__":
    main()
