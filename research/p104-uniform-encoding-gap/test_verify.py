#!/usr/bin/env python3
"""Failure controls for the uniform-encoding gap. Loads verify.py by path."""
import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent / "verify.py"
_SPEC = importlib.util.spec_from_file_location("p104_uniform_encoding_gap_verify", _PATH)
gap = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(gap)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def nnz_commutator(encoding, operator):
    return gap.nnz(gap.commutator(gap.lift_uniform(operator), encoding))


def main():
    facts = gap.report()
    require(facts["physical_defect_nnz"] == 4, "witness support changed")
    require(facts["address_commutator_01"] == (2, -2), "recorded address entry changed")
    identity = gap.eye(gap.ADDR)
    zeta = gap.character_e1()
    scalar = gap.encoding([identity, identity], gap.SCALAR_D)
    physical = gap.encoding([identity, gap.chart(1)], gap.SCALAR_D)
    even = gap.encoding([identity, gap.chart(2)], gap.SCALAR_D)
    require(nnz_commutator(scalar, zeta) == 0, "scalar control")
    require(nnz_commutator(physical, zeta) != 0, "physical witness")
    require(nnz_commutator(even, zeta) == 0, "even-direction control")
    require(nnz_commutator(physical, identity) == 0, "identity completion must commute")

    def assert_obstruction(port_chart):
        candidate = gap.encoding([identity, port_chart], gap.SCALAR_D)
        if nnz_commutator(candidate, zeta) == 0:
            raise ValueError("expected an obstruction")

    raised = False
    try:
        assert_obstruction(gap.chart(2))
    except ValueError as exc:
        raised = "expected an obstruction" in str(exc)
    require(raised, "the even-direction chart must fail an obstruction claim")
    assert_obstruction(gap.chart(1))
    print("PASS_P104_UNIFORM_ENCODING_GAP_TESTS groups=3")


if __name__ == "__main__":
    main()
