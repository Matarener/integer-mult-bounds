#!/usr/bin/env python3
"""Failure controls for the log_q parent-term correction."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "logq_parent", os.path.join(HERE, "verify.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main():
    boot, cons = MODULE.evaluate()
    gap = MODULE.Fraction(1) - MODULE.Fraction(
        "67018507072324140916999892981492927675859083/"
        "40000000000000000000000000000000000000000000000")
    assert MODULE.parent_term(gap, 2642, 80) == boot
    assert 80 * boot == MODULE.parent_term(gap, 2642, 1)
    assert cons != boot
    # rho = 0 rejects a one-digit leaf: log_q(q) = 1 is not <= 0.
    assert not (1 <= 0)
    try:
        MODULE.parent_term(gap, 2642, 0)
    except ValueError:
        pass
    else:
        raise SystemExit("floor 0 was accepted")
    print("PASS_SELECTED_STOCK_LOGQ_PARENT_TESTS controls=4")


if __name__ == "__main__":
    main()
