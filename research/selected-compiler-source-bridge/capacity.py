#!/usr/bin/env python3
"""Arithmetic-only CPython capacity obstruction; never enumerate GL64.

Adapted from the verified Claude Opus 5.5 cpython_representability.py review,
with substantial OpenAI Codex assistance. Apache-2.0. Source/compiler credit
remains with Jose Manuel (jmbarrancoml), David Arias and the retained source
contributors. The independent Astra census supplies a separate source-link
check, not a dependency of this arithmetic module.

This script does NOT import/read the compiler or authenticate its semantics.
The conditional source premises below must be established separately against
pinned bytes. It does not predict a first exception, first allocation failure,
or a feasible partial-run length. There is no GL64, numerical or Lean replay.

For q >= 3 and 0 <= k < 64,
    q**64 - q**k = q**k * (q**(64-k) - 1).
Both factors on the right are positive and nondecreasing in q; the second is
strictly increasing (64-k >= 1). Hence every product factor is strictly
increasing, and so N(q) >= N(3). This proves the comparison for ALL integer
q >= 3, thus for every accepted prime q >= 3, not just two sampled primes.
"""
import argparse
import json
import math
import platform
import struct
import sys

RHO, R, DIMENSION = 32, 28278, 64
Q_MIN = 3
MAX_Q_BITS = 32  # execution guard only; the monotonic proof has no q upper bound
CALLER = "research/selected-bit-physical-caller"
SOURCE_PREMISES = {
    "checked_by_this_script": False,
    "files": [CALLER + "/macro_code.py",
              CALLER + "/inputs/pr2753/predecessor/vendor/low_codes.py"],
    "premises": [
        "Accepted LOW field size is a prime q >= 3, with N(q) = product(q**64 - q**k, k=0..63).",
        "The independently source-linked abstract visitation count is T = 32 * 28278 * N(q).",
        "The unchanged eager compile_node retains one operations list; each residual return appends a begin and an end.",
        "A complete successful return builds Code(tuple(operations), staged); both sequence lengths are at least 2*T.",
        "On conventional 32/64-bit CPython, list/tuple lengths cannot exceed Py_ssize_t's maximum 2**31-1 / 2**63-1."
    ],
    "conditional_conclusion": "Those premises exclude a complete successful eager selected compile_node return on conventional 32/64-bit CPython.",
    "first_failure_determined": False,
    "earlier_failures": "Allocation, size, LOW-unranking or other checks may fail earlier; no failure order is established.",
    "unaffected": "Conditional census/lifetime formulas, idealized unbounded semantics and abstract Lean counting claims are not falsified; no claim about lazy/regional compilation."
}


class Rejected(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Rejected(message)


def gl_order(q, dimension=DIMENSION):
    """Exact arithmetic product, not a primality test or matrix enumerator.

    The finite-field interpretation needs q to be a prime power. The proof
    uses accepted prime q >= 3; this helper also permits small composite q
    solely for arithmetic tests. Guards bound executed integer arithmetic.
    """
    need(type(q) is int and 2 <= q and q.bit_length() <= MAX_Q_BITS, "bounded integer q >= 2")
    need(type(dimension) is int and 1 <= dimension <= DIMENSION, "dimension in 1..64")
    return math.prod(q**dimension - q**k for k in range(dimension))


def factor_monotonicity():
    """A quantified algebraic argument, not a finite sampling certificate."""
    return {
        "domain": "integers b >= a >= 3, 0 <= k < 64 (hence accepted primes)",
        "factorization": "q**64 - q**k = q**k * (q**(64-k) - 1)",
        "positive_factors": "q**k >= 1 and q**(64-k) - 1 >= 2",
        "comparison": "b**k >= a**k > 0 and b**(64-k)-1 >= a**(64-k)-1 > 0; multiply these inequalities, then multiply over k",
        "strictness": "For b > a, the second factor is strictly larger for every k because 64-k >= 1, including k=0",
        "conclusion": "N(q) >= N(3) for every integer q >= 3; no primality enumeration or sampled-q inference",
        "formal_verification": False
    }


def build_report():
    n3 = gl_order(Q_MIN)
    lower = (Q_MIN**64 - Q_MIN**63) ** 64  # = (2 * 3**63)**64
    t = RHO * R * n3
    minimum = 2 * t  # lower bound only; other retained operations add entries
    try:
        len(range(n3))
        len_range_ok = True
    except OverflowError:
        len_range_ok = False
    # Two ordinal integers only, not any GL64 matrices or LOW unranking.
    iterator = iter(range(n3))
    range_iterates = [next(iterator), next(iterator)] == [0, 1]
    conventional = {"32-bit 2**31-1": minimum > 2**31 - 1,
                    "64-bit 2**63-1": minimum > 2**63 - 1}
    arithmetic_ok = (n3 >= lower and minimum > 2**6500 and all(conventional.values()))
    return {
        "status": "PASS" if arithmetic_ok else "FAIL",
        "python": sys.version.split()[0], "implementation": platform.python_implementation(),
        "pointer_bytes": struct.calcsize("P"), "sys_maxsize": sys.maxsize,
        "sys_maxsize_bit_length": sys.maxsize.bit_length(),
        "q": Q_MIN, "dimension": DIMENSION, "replicas": RHO, "requests": R,
        "visits_coefficient_of_N": RHO * R, "min_len_coefficient_of_N": 2 * RHO * R,
        # Decimal strings preserve exact values even in JSON consumers using floats.
        "N_GL64_F3_exact_decimal": str(n3), "T_exact_decimal": str(t),
        "min_len_2T_exact_decimal": str(minimum),
        "N_GL64_F3_decimal_digits": len(str(n3)), "N_GL64_F3_bit_length": n3.bit_length(),
        "N3_ge_closed_form_lower": n3 >= lower,
        "closed_form_lower": "(2 * 3**63)**64",
        "monotonic_factor_argument": factor_monotonicity(),
        "T_bit_length": t.bit_length(), "min_len_2T_bit_length": minimum.bit_length(),
        "min_len_gt_2_pow_6500": minimum > 2**6500,
        "min_len_gt_sys_maxsize": minimum > sys.maxsize,
        "N_alone_gt_sys_maxsize": n3 > sys.maxsize,
        "min_len_gt_conventional": conventional,
        "illustration_len_range_N_representable": len_range_ok,
        "illustration_range_N_iterates": range_iterates,
        "range_illustration_scope": "Only two ordinal integers are advanced. len(range(N)) is not an operation asserted to occur in the selected loop, and is not a first-failure claim.",
        "source_semantics": SOURCE_PREMISES,
        "scope": "Arithmetic tests only. Conditional on the separately authenticated source semantics, a complete successful eager selected compilation cannot fit conventional 32/64-bit CPython lengths. No source execution, numerical verification, or first-failure determination.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)  # fixed q=3 witness; no user-controlled huge execution
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
