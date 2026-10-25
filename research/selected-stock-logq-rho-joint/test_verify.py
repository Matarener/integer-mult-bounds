#!/usr/bin/env python3
"""Failure controls for the joint log_q leaf coefficient."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "logq_rho_joint", os.path.join(HERE, "verify.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main():
    boot, cons = MODULE.evaluate()
    gap = MODULE.Fraction(1) - MODULE.Fraction(
        "67018507072324140916999892981492927675859083/"
        "40000000000000000000000000000000000000000000000")
    assert MODULE.parent_term(gap, MODULE.PARENT_DIGITS) == boot
    assert MODULE.parent_term(gap, MODULE.LOOSE_BITS) == 80 * boot
    assert cons != boot
    assert MODULE.one_digit_leaf_log() == 1
    # A positive leaf coefficient is a different envelope from rho = 0.
    assert MODULE.parent_term(gap, MODULE.PARENT_DIGITS) + 8194 != boot
    try:
        MODULE.shape_slack_coefficients(0)
    except ValueError:
        pass
    else:
        raise SystemExit("width 0 was accepted")
    try:
        MODULE.parent_term(0, MODULE.PARENT_DIGITS)
    except ValueError:
        pass
    else:
        raise SystemExit("a zero stock gap was accepted")
    constant, slope = MODULE.shape_slack_coefficients(1)
    assert (constant, slope) == (1, 0)
    print("PASS_SELECTED_STOCK_LOGQ_RHO_JOINT_TESTS controls=5")


if __name__ == "__main__":
    main()
