#!/usr/bin/env python3
"""Exact favorable ceiling screens for the measured plane invoice and two extensions."""
from __future__ import annotations

from fractions import Fraction as Q
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CEILING_DIR = ROOT / "research/complex-local-word-ceiling"
sys.path.insert(0, str(CEILING_DIR))
import ceiling  # noqa: E402

M, FAMILIES, STAGES = 73, 896, 9
BASE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}
TARGET_A = Q(1, 99)
GRID = Q(1, 10**12)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def screen(local, centre, unpaid):
    lower, upper = ceiling.ceiling(
        local, M, FAMILIES, STAGES, centre, grid=GRID, unpaid=unpaid)
    target_interval = ceiling.relax(
        local, M, FAMILIES, STAGES, centre, TARGET_A, unpaid=unpaid)
    model = ceiling.model(
        local, M, FAMILIES, STAGES, centre, unpaid=unpaid)
    return {
        "a_interval": [str(lower), str(upper)],
        "kappa_upper": str(upper / (1 + upper)),
        "kappa_upper_decimal": float(upper / (1 + upper)),
        "target_relaxation_interval_at_a_1_over_99": [
            str(target_interval[0]), str(target_interval[1])],
        "target_relaxation_upper_decimal": float(target_interval[1]),
        "local_mass": str(model["local_mass"]),
        "idle_mass": str(model["idle_mass"]),
        "unpaid_coordinates": unpaid,
        "centre_charge": centre,
    }


def run():
    # The candidate's raw port-support ranks sum to 74, but closing both source
    # and reader supports under the complete matched planes gives nine rank-9
    # readers, hence the measured complete-plane tariff is 81.
    new_reader = {**BASE, 9: 9}
    predecessor_reader = {**BASE, 9: 16}
    rank16 = {16: Q(5603, 16)}
    results = {
        "candidate81_two_unpaid": screen(new_reader, 81, 2),
        "candidate81_three_unpaid": screen(new_reader, 81, 3),
        "predecessor144_three_unpaid": screen(predecessor_reader, 144, 3),
        "rank16_centre81_two_unpaid": screen(rank16, 81, 2),
    }
    require(results["candidate81_two_unpaid"]["kappa_upper_decimal"] < 0.01,
            "two-unpaid measured reader profile unexpectedly clears target")
    require(results["candidate81_three_unpaid"]["kappa_upper_decimal"] > 0.01 and
            results["candidate81_three_unpaid"]["target_relaxation_upper_decimal"] < 1,
            "three-unpaid measured plane profile does not clear target screen")
    require(results["predecessor144_three_unpaid"]["kappa_upper_decimal"] < 0.01,
            "predecessor complete-plane reader profile unexpectedly clears target")
    require(results["rank16_centre81_two_unpaid"]["kappa_upper_decimal"] > 0.01,
            "rank-16 planning relaxation unexpectedly fails target screen")
    return {
        "status": "PASS_GAUGE44_EXACT_PLANNING_SCREENS",
        "scope": "Favorable complex-side ceilings only; third unpaid coordinate and rank-16 delivery are assumptions, not constructions.",
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
