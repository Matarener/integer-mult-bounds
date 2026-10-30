#!/usr/bin/env python3
"""Failure controls: each mutation must be rejected by the checks in verify.py."""
import verify

PASS = "PASS_HUB_EXCESS_ALL_H_CONTROLS"


def rejects(action):
    try:
        action()
    except AssertionError:
        return True
    return False


def main():
    # 1. Moving t off E+F+G changes the reduced circuits through E.
    original = verify.CORE["t"]
    verify.CORE["t"] = (1, 1, 2)
    try:
        if not rejects(verify.check_core):
            raise SystemExit("control 1: mutated t accepted")
    finally:
        verify.CORE["t"] = original

    # 2. Dropping one circuit from the expected list breaks the h=2 census match.
    saved = verify.EXPECTED_CIRCUITS
    verify.EXPECTED_CIRCUITS = saved - {frozenset("tac")}
    try:
        if not rejects(lambda: verify.census_charge(2)):
            raise SystemExit("control 2: truncated table accepted")
    finally:
        verify.EXPECTED_CIRCUITS = saved

    # 3. Treating a family-C reader as non-family: no cost-one evaluator exists.
    saved_family = verify.FAMILY_CIRCUITS
    verify.FAMILY_CIRCUITS = saved_family - {frozenset("dab")}
    try:
        if not rejects(lambda: verify.check_costs_closed_form(2)):
            raise SystemExit("control 3: family C given cost one")
    finally:
        verify.FAMILY_CIRCUITS = saved_family

    # 4. Census cost of every family reader is exactly 2 at h=2 (12 rows).
    names, vecs, E, F, readers, _ = verify.census(2)
    by_name = dict(zip(names, vecs))
    twos = [r for r in readers[0] if verify.min_paid(by_name, (), r, E, F) == 2]
    if sorted(map(verify.circuit_of, twos), key=sorted) != sorted(
            [frozenset("dc")] * 2 + [frozenset("gtc")] * 2 + [frozenset("dab")] * 2, key=sorted):
        raise SystemExit("control 4: cost-two readers are not exactly families A-C")

    print(PASS, "mutations_rejected=3", "h2_cost_two_E_readers=6")


if __name__ == "__main__":
    main()
