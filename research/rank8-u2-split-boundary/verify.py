#!/usr/bin/env python3
"""The rank-8/u2 16-child slack is not invariant under legal family splits.

The pinned ceiling engine supplies the child-cost enclosures. This file does
not edit it and does not claim a producer, a consumer or a new kappa.
"""
from fractions import Fraction
import hashlib
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "research" / "complex-local-word-ceiling" / "ceiling.py"
PIN = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
M = 73
FAMILIES = 896
CALLS = 9
CENTRE = 64
UNPAID = 2
R = 51
A = Fraction(1, 98)
LOCAL = {8: 698, 2: 1}
LOCAL_MASS = 8 * 698 + 2


def require(ok, why):
    if not ok:
        raise SystemExit("FAIL: " + why)


def load_engine():
    digest = hashlib.sha256(ENGINE.read_bytes()).hexdigest()
    require(digest == PIN, "ceiling.py sha256 differs from the package pin")
    spec = importlib.util.spec_from_file_location("pinned_ceiling", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(module.max_idle_rank(M) == R, "halving cap is not 51")
    return module


def call_mass(families):
    return (M - UNPAID) * families + CENTRE


def idle_mass(families):
    return call_mass(families) - LOCAL_MASS


def pack_idle(mass):
    require(mass >= 0, "negative idle")
    quotient, remainder = divmod(mass, R)
    histogram = {R: quotient}
    if remainder:
        histogram[remainder] = 1
    require(R * quotient + remainder == mass, "idle packing dropped mass")
    return histogram


def add(left, right, times=1):
    out = dict(left)
    for rank, count in right.items():
        out[rank] = out.get(rank, 0) + times * count
    return out


def hosted(counts):
    require(len(counts) == CALLS, "a schedule needs nine calls")
    require(sum(counts) == FAMILIES, "families must sum to 896")
    histogram = {}
    for families in counts:
        require(families >= 78, "a call below 78 families cannot hold the paid profile")
        histogram = add(histogram, LOCAL)
        histogram = add(histogram, pack_idle(idle_mass(families)))
    return histogram


def moment(engine, histogram):
    low = high = Fraction(0)
    for rank, count in histogram.items():
        if count == 0:
            continue
        left, right = engine.child_cost(int(rank), M, A)
        require(left <= right, "cost enclosure is inverted")
        low += count * left
        high += count * right
    return engine.down(low / FAMILIES), engine.up(high / FAMILIES)


def sign(bounds):
    low, high = bounds
    if high < 1:
        return "LT"
    if low > 1:
        return "GT"
    return "UNK"


def with_surcharge(histogram, extra):
    out = dict(histogram)
    out[1] = out.get(1, 0) + extra
    return out


def main():
    engine = load_engine()
    require(LOCAL_MASS == 5586, "paid mass is not the selected local mass")
    require(sum(rank * count for rank, count in {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}.items()) == 5586,
            "selected word mass changed")
    total = (M - UNPAID) * FAMILIES + CENTRE * CALLS
    require(total == 64192, "nine-call coverage mass changed")
    require(CALLS * LOCAL_MASS == 50274, "nine-call paid mass changed")
    require(total - CALLS * LOCAL_MASS == 13918, "nine-call idle mass changed")
    require(idle_mass(77) < 0, "77 families should be unable to hold the paid profile")
    require(idle_mass(78) == 16, "minimum call idle is not 16")

    pooled_idle = pack_idle(13918)
    require(pooled_idle == {51: 272, 46: 1}, "pooled idle histogram changed")
    pooled = add({8: 6282, 2: 9}, pooled_idle)
    require(sum(rank * count for rank, count in pooled.items()) == 64192, "pooled mass")

    balanced_counts = (100, 100, 100, 100, 100, 99, 99, 99, 99)
    shifted_counts = (101, 100, 100, 100, 99, 99, 99, 99, 99)
    require(sum(balanced_counts) == 896 and sum(shifted_counts) == 896, "split totals")
    # Moving one family from one 100-call onto another 100-call.
    require(sorted(shifted_counts) == sorted((101, 100, 100, 100, 99, 99, 99, 99, 99)), "shifted split")

    balanced = hosted(balanced_counts)
    require(balanced == {8: 6282, 2: 9, 51: 266, 48: 5, 28: 4}, "balanced histogram")
    shifted = hosted(shifted_counts)
    require(shifted == {8: 6282, 2: 9, 51: 267, 48: 3, 28: 5, 17: 1}, "shifted histogram")
    for histogram in (pooled, balanced, shifted):
        require(sum(rank * count for rank, count in histogram.items()) == 64192, "hosting lost mass")

    pooled_16 = sign(moment(engine, with_surcharge(pooled, 16)))
    pooled_17 = sign(moment(engine, with_surcharge(pooled, 17)))
    balanced_16 = sign(moment(engine, with_surcharge(balanced, 16)))
    balanced_17 = sign(moment(engine, with_surcharge(balanced, 17)))
    shifted_15 = sign(moment(engine, with_surcharge(shifted, 15)))
    shifted_16 = sign(moment(engine, with_surcharge(shifted, 16)))
    require(pooled_16 == "LT" and pooled_17 == "GT", "pooled 16/17 boundary moved")
    require(balanced_16 == "LT" and balanced_17 == "GT", "balanced 16/17 boundary moved")
    require(shifted_15 == "LT" and shifted_16 == "GT", "one-family move did not drop the budget to 15")

    # Failure controls. These stay explicit so -O cannot delete them.
    bare = moment(engine, with_surcharge(pooled, 16))
    dropped = dict(with_surcharge(pooled, 16))
    dropped[51] -= 1
    dropped[1] = dropped.get(1, 0) + 51
    require(moment(engine, dropped)[0] > bare[1], "replacing a cap child by rank 1 should raise the moment")
    try:
        hosted((77,) + (100,) * 7 + (119,))
    except SystemExit as exc:
        require(str(exc).startswith("FAIL: a call below 78"), "illegal call was accepted")
    else:
        require(False, "illegal call did not fail")

    print(
        "PASS_RANK8_U2_SPLIT_BOUNDARY"
        f" pooled={pooled_16}/{pooled_17}"
        f" balanced={balanced_16}/{balanced_17}"
        f" shifted={shifted_15}/{shifted_16}"
        " no_new_kappa"
    )


if __name__ == "__main__":
    main()
