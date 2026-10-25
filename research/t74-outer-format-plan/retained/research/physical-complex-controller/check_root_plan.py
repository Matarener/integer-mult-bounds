# SPDX-License-Identifier: Apache-2.0
"""Encoded reservation arithmetic against independent integer formulas."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_root import integer
from cardinal_counts import Count
from cover import OrthogonalCover
from root_plan import RootPlan, ceil_divide, ceil_log2, coarse_depth, floor_power
from words import BLANK


def run(full=False):
    digest = sha256()
    cases = 0
    values = tuple(range(1, 34)) if full else (1, 2, 3, 4, 7, 8, 9, 16, 17, 32, 33)
    for value in values:
        source = Count.literal(value)
        answer = ceil_log2(source)
        expected = (value - 1).bit_length()
        if integer(answer) != expected:
            raise ValueError("exact encoded ceiling logarithm")
        answer.close()
        for numerator, denominator in ((1, 2), (2, 3), (1, 500), (997, 1000)):
            if not full and numerator == 997 and value not in (1, 2, 3):
                continue
            answer = floor_power(source, numerator, denominator)
            result = integer(answer)
            if not result ** denominator <= value ** numerator < (result + 1) ** denominator:
                raise ValueError("encoded floor fractional power")
            digest.update(str((value, numerator, denominator, result)).encode())
            answer.close()
            cases += 1
        source.close()
    for value in range(1, 65):
        source, divisor = Count.literal(value), Count.literal(7)
        answer = ceil_divide(source, divisor)
        if integer(answer) != (value + 6) // 7:
            raise ValueError("encoded ceiling division")
        answer.close()
        answer = coarse_depth(source, 3, 2)
        n, expected = value, 0
        while n >= 3:
            n = 2 * (n // 3)
            expected += 1
        if integer(answer) != expected:
            raise ValueError("encoded coarse recursion depth")
        answer.close()
        source.close()
        divisor.close()
    divisor = 14336 * OrthogonalCover(73).size
    plan = RootPlan(73, 48, divisor, guard_exponent=2)
    counts = tuple(Count.literal(v) for v in (9, 8, 1, 2, 3, 2, 0))
    plan.compute(*counts)
    actual = {name: integer(plan.count(name)) for name in plan.roles}
    expected = dict(d=8, K=1, G=22, H=176, depth=0, q0=0, qF=352, qB=176, Q0=528,
                    delta=32, input_bits=11, work_bits=76, gaussians=12288)
    if plan.fast or any(actual[name] != value for name, value in expected.items()):
        raise ValueError("root planner complete formulas")
    plan.clear()
    if any(t.read() != BLANK for t in plan.roles.values()) or plan.pool.live:
        raise ValueError("planner owned cleanup")
    for value in counts:
        value.close()
    production = RootPlan(73, 48, divisor)
    counts = tuple(Count.literal(v) for v in (2, 1, 0, 0, 1, 1, 0))
    production.compute(*counts)
    if integer(production.count("delta")) != 1 << 210000 or integer(production.count("work_bits")) != (1 << 210001) + 5:
        raise ValueError("production encoded root guard")
    production.clear()
    for value in counts:
        value.close()
    return dict(fractional_power_cases=cases, logarithms=len(values), divisions_and_depths=64,
                planner_peak=max(plan.pool.peak, production.pool.peak), sha256=digest.hexdigest(),
                production_guard_metadata=True,
                scope="Encoded formulas and production guard metadata; no production payload.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    print(json.dumps(run(parser.parse_args().full), sort_keys=True, indent=2))
