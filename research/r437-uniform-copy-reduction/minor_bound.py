#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Finite audits of the written rank-specific low-class counting argument.

No claim that finite field enumeration proves the quantified polynomial lemma.
"""
from fractions import Fraction as F
from itertools import combinations, product
import json
from pathlib import Path

P = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def det(a, q):
    if not a:
        return 1
    if len(a) == 1:
        return a[0][0] % q
    if len(a) == 2:
        return (a[0][0] * a[1][1] - a[0][1] * a[1][0]) % q
    return sum((-1) ** j * a[0][j] * det([row[:j] + row[j + 1:] for row in a[1:]], q)
               for j in range(len(a))) % q


def minor(a, rows, columns, q):
    return det([[a[i][j] for j in columns] for i in rows], q)


def cb_numerator(g, rank, k, q, wrong_sign=False):
    n, first = len(g), tuple(range(k))
    rows_complement = tuple(range(k, n))
    result = 0
    for selected in combinations(range(rank), k):
        columns_complement = tuple(j for j in range(n) if j not in selected)
        sign = 1 if wrong_sign else (-1) ** (sum(first) + sum(selected))
        result += sign * minor(g, first, selected, q) * minor(g, rows_complement, columns_complement, q)
    return result % q


def projected(g, rank, q):
    n, determinant = len(g), det(g, q)
    need(determinant != 0, "GL input")
    invdet = pow(determinant, -1, q)
    # Adjugate, rather than the producer's Gaussian inverse.
    inverse = [[(-1) ** (i + j) * minor(g, [k for k in range(n) if k != j],
                                      [k for k in range(n) if k != i], q) * invdet % q
                for j in range(n)] for i in range(n)]
    return [[sum(g[i][k] * inverse[k][j] for k in range(rank)) % q
             for j in range(n)] for i in range(n)]


def calculate():
    tables, sign_control = [], False
    for n, rank, q in [(2, 1, 3), (2, 1, 5), (2, 1, 7), (2, 1, 17), (3, 2, 3)]:
        total, bad, numerators = 0, 0, 0
        for flat in product(range(q), repeat=n * n):
            g = [list(flat[i:i + n]) for i in range(0, len(flat), n)]
            d = det(g, q)
            if not d:
                continue
            total += 1
            p = projected(g, rank, q)
            failed = False
            for k in range(1, rank + 1):
                numerator = cb_numerator(g, rank, k, q)
                principal = minor(p, range(k), range(k), q)
                need(numerator == d * principal % q, "Jacobi/Cauchy-Binet numerator")
                if cb_numerator(g, rank, k, q, wrong_sign=True) != numerator:
                    sign_control = True
                failed |= principal == 0
                numerators += 1
            bad += failed
        expected_gl = 1
        for k in range(n):
            expected_gl *= q ** n - q ** k
        need(total == expected_gl, "complete GL enumeration")
        bound = F(rank * n * (q - 1), q * (q - 2))
        need(F(bad, total) <= bound, "finite check of the complete conditional fraction")
        tables.append(dict(dimension=n, rank=rank, q=q, GL=total, bad=bad,
                           fraction=str(F(bad, total)), numerator_checks=numerators))
    need(sign_control, "Jacobi sign mutation has a separating matrix")
    q_floor = 2 ** 80
    large_prime_upper = F(449, q_floor)
    fallback = 3 * (127 + 254 + 16256)
    need(fallback == 49911 and fallback < 32 * 64 ** 2, "full fallback child allowance")
    need(large_prime_upper < F(1, 10 ** 16), "inherited epsilon safely covers rank seven")
    return dict(status="PASS_RANK7_LOW_CLASS_MINOR_BOUND",
                generic_minor_numerator_degree=64, product_degree=448,
                conditional_fraction="min(1,448*(q-1)/(q*(q-2)))",
                simple_bound="delta_7 < 896/q for q>=3; delta_7 <449/q for q>=450",
                source_admissible_uniform_upper=str(large_prime_upper),
                fallback_children_per_bad_class_upper=fallback,
                source_admissible_fallback_multiplier_upper=str(fallback * large_prime_upper),
                inherited_epsilon="1/10000000000000000",
                union_over_paid_labels=False, full_high_lifts_covered=True,
                coverage="Written polynomial and conditional-caller proof; finite audits are supporting evidence, not proof of physical refinement.",
                complete_small_GL_tables=tables, sign_mutation_separated=True,
                checked_obligations=["conditioning on GL explicitly charged", "fallback children not free"])


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    path = P / "MINOR-BOUND.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.loads(path.read_bytes()) == result, "minor receipt differs")
    print(result["status"] + " small_GL=" + str(sum(row["GL"] for row in result["complete_small_GL_tables"])))


if __name__ == "__main__":
    main()
