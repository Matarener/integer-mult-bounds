#!/usr/bin/env python3
"""Probe independent positive/negative idle windows in the physical controller.

Binary candidates are screened exactly and then replayed over the integral
Laurent ring.  This changes no native local word; it changes which physical
data fields receive idle recursive calls.  No new exponent is claimed.
Apache-2.0. Substantial OpenAI assistance.
"""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import argparse
import json
import time

import complex_controller_factor as C
import mixed_productive_bit as B

HERE = Path(__file__).resolve().parent


def controller(p, keep, binary=False):
    n, stages = 2*p, 2*p+1
    zero = 0 if binary else (0,)*(stages+1)
    matrix = [[({0} if i == j else set()) if binary else
               ({zero:1} if i == j else {}) for j in range(n)] for i in range(n)]
    events, idle = [], []

    def term(q, selected):
        return (q & 1) | sum(1 << (s+1) for s in selected) if binary else (q,)+tuple(int(s in selected) for s in range(stages))

    def multiply(polynomial, exponents, coefficient=1):
        return {x ^ exponents for x in polynomial} if binary else C.monomial_times(polynomial, exponents, coefficient)

    def plus(a, b, coefficient=1):
        return a ^ b if binary else C.plus(a, b, coefficient)

    def idle_call(pair, selected, kind):
        for side in (0, 1):
            index = len(idle)
            retained = bool(keep >> index & 1)
            role = 2*pair+side
            idle.append(dict(index=index, pair=pair, side=side, field=role,
                             stages=list(selected), rank=8*len(selected),
                             kind=kind, retained=retained))
            if retained:
                matrix[role] = [multiply(x, term(0, selected)) for x in matrix[role]]
                events.append(["IDLE_FIELD", role, list(selected)])

    def local(stage, pair, reverse):
        x, y = 2*pair, 2*pair+1
        if reverse:
            x, y = y, x
        sign, q = (-1, 1) if reverse else (1, -1)
        matrix[y] = [plus(a, multiply(b, term(q, []), sign)) for a, b in zip(matrix[y], matrix[x])]
        for role in (x, y):
            matrix[role] = [multiply(a, term(0, [stage])) for a in matrix[role]]
        events.append(["LOCAL", stage, pair, reverse])
        if stage % 2 and stage <= 2*p-3:
            idle_call((stage+1)//2, list(range(stage+1)), "initial")
        elif stage % 2 == 0 and 2 <= stage <= 2*p-2:
            idle_call(stage//2, [stage], "middle")
        elif stage == 2*p:
            for j in range(p-1):
                idle_call(j, list(range(2*j+3, 2*p+1)), "terminal")

    def bridge(dst, src, coefficient):
        for d, s, c in ((2*dst, 2*src, coefficient), (2*src+1, 2*dst+1, -coefficient)):
            matrix[d] = [plus(a, b, c) for a, b in zip(matrix[d], matrix[s])]
            events.append(["ADD", d, s, c])

    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1:
            bridge(j, j+1, 1)
        local(2*j+2, j, False)
        if j < p-1:
            bridge(j, j+1, -1)
    for j in reversed(range(p-1)):
        bridge(j+1, j, 1)
    for j in range(p):
        matrix[2*j], matrix[2*j+1] = matrix[2*j+1], [multiply(x, zero, -1) for x in matrix[2*j]]
        events.append(["SIGNED_SWAP", 2*j, 2*j+1])
    if binary:
        coefficients = B.polynomial_coefficients(matrix)
    else:
        coefficients = {}
        for i, row in enumerate(matrix):
            for j, polynomial in enumerate(row):
                for key, value in polynomial.items():
                    coefficients.setdefault(key, [[Q(0)]*n for _ in range(n)])[i][j] += value
        coefficients = {k:a for k,a in coefficients.items() if any(any(row) for row in a)}
    return coefficients, events, idle


def run(p):
    start = time.monotonic()
    trials, candidates, cases = 1 << (6*(p-1)), [], []
    for mask in range(trials):
        coefficients, _, _ = controller(p, mask, True)
        if B.simultaneous_monomial_factor(coefficients) is not None:
            candidates.append(mask)
    for mask in candidates:
        coefficients, events, idle = controller(p, mask)
        result = C.factor(coefficients)
        if result is not None:
            case = C.serialize_case(p, mask, coefficients, events, idle, result)
            case["idle_mask_semantics"] = "Two consecutive bits per former paired window; positive then negative field"
            case["all_windows_paired"] = all(bool(mask >> (2*j)&1) == bool(mask >> (2*j+1)&1) for j in range(3*(p-1)))
            cases.append(case)
    return dict(schema="single-field-idle-controller/1", pairs=p, trials=trials,
                binary_candidates=len(candidates), exact_Laurent_cases=len(cases),
                asymmetric_cases=sum(not c["all_windows_paired"] for c in cases),
                source_sha256={Path(__file__).name:sha256(Path(__file__).read_bytes()).hexdigest()},
                cases=cases, runtime_seconds=time.monotonic()-start, new_kappa=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    B.need(1 <= args.pairs <= 4, "Bounded probe")
    result = run(args.pairs)
    path = args.output or HERE/f"SINGLE-FIELD-CONTROLLER-P{args.pairs}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k != "cases"}, sort_keys=True))


if __name__ == "__main__":
    main()
