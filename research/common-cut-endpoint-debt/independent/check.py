#!/usr/bin/env python3
"""Exact heterogeneous support certificate in a formal Gaussian path alphabet.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
This checks an operator expansion, not a restored dirty-workspace caller.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path


ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
I = (Fraction(0), Fraction(1))
A = (Fraction(1, 2), Fraction(1, 2))
B = (Fraction(1, 2), Fraction(-1, 2))
HALF = (Fraction(1, 2), Fraction(0))
MINUS_I_HALF = (Fraction(0), Fraction(-1, 2))


class AuditError(ValueError):
    pass


def require(condition, guard, disabled=()):
    if guard not in disabled and not condition:
        raise AuditError(guard)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    return (x[0] * y[0] - x[1] * y[1],
            x[0] * y[1] + x[1] * y[0])


def conjugate(x):
    return (x[0], -x[1])


def power(x, n):
    answer = ONE
    for _ in range(n):
        answer = mul(answer, x)
    return answer


def encoded_fraction(x):
    return [x.numerator, x.denominator]


def encoded_gaussian(x):
    return [encoded_fraction(x[0]), encoded_fraction(x[1])]


def encoded_kernel(kernel):
    return [[offset, encoded_gaussian(coefficient)]
            for offset, coefficient in sorted(kernel.items())]


def tensor_kernel(left, local, shift):
    result = {}
    for x, a in left.items():
        for y, b in local.items():
            result[x | (y << shift)] = mul(a, b)
    return result


def path(word):
    kernel = {0: ONE}
    coefficient = ONE
    for index, letter in enumerate(word):
        if letter == "A":
            local, scalar = {0: A, 1: B}, A
        elif letter == "B":
            local, scalar = {2: ONE}, HALF
        elif letter == "C":
            local, scalar = {3: ONE}, MINUS_I_HALF
        else:
            raise AuditError("unknown formal path letter")
        kernel = tensor_kernel(kernel, local, 2 * index)
        coefficient = mul(coefficient, scalar)
    return {"word": "".join(word), "kernel": kernel,
            "coefficient": coefficient}


def paths(f):
    return [path(word) for word in itertools.product("ABC", repeat=f)]


def target_kernel(f):
    # Independent direct expansion of all 2f positive C gates, with no use of
    # the three-letter path decomposition or its scalar coefficients.
    n = 2 * f
    return {offset: mul(power(A, n - offset.bit_count()),
                        power(B, offset.bit_count()))
            for offset in range(1 << n)}


def aggregate(items):
    result = {}
    for item in items:
        for offset, value in item["kernel"].items():
            result[offset] = add(result.get(offset, ZERO),
                                 mul(item["coefficient"], value))
    return {offset: value for offset, value in result.items() if value != ZERO}


def support_rank(item):
    size = len(item["kernel"])
    require(size > 0 and size & (size - 1) == 0, "path support is a power of two")
    return size.bit_length() - 1


def support_mass(items, n):
    return sum((Fraction(len(item["kernel"]), 1 << n) for item in items),
               Fraction(0))


def accept_support(items, n, disabled=()):
    require(all(item["coefficient"] != ZERO for item in items),
            "nonzero path coefficients", disabled)
    require(support_mass(items, n) >= 1, "heterogeneous support mass", disabled)


def accept_partition(items, n, disabled=()):
    counts = Counter(offset for item in items for offset in item["kernel"])
    require(counts == Counter({offset: 1 for offset in range(1 << n)}),
            "row support partition", disabled)


def accept_operator(items, f, disabled=()):
    actual, wanted = aggregate(items), target_kernel(f)
    size = 1 << (2 * f)
    # Every ordinary input column and output row is compared. There are no
    # omitted helper columns: the formal alphabet has no helper registers.
    same = all(actual.get(row ^ column, ZERO) == wanted[row ^ column]
               for column in range(size) for row in range(size))
    require(same, "complete Gaussian operator", disabled)


def expected_histogram(f):
    return {k: math.comb(f, k) * 2 ** (f - k) for k in range(f + 1)}


def invoice(items):
    histogram = Counter(support_rank(item) for item in items)
    return {"path_count": len(items), "histogram": dict(sorted(histogram.items())),
            "native_rank_mass": sum(k * count for k, count in histogram.items())}


def accept_invoice(items, f, disabled=()):
    expected = {"path_count": 3 ** f, "histogram": expected_histogram(f),
                "native_rank_mass": f * 3 ** (f - 1)}
    require(invoice(items) == expected, "complete unshared path invoice", disabled)


def accept(items, f):
    accept_support(items, 2 * f)
    accept_partition(items, 2 * f)
    accept_operator(items, f)
    accept_invoice(items, f)


def reject(name, predicate, guard):
    try:
        predicate(())
    except AuditError as error:
        require(str(error) == guard, "wrong semantic rejection: " + name)
    else:
        raise AuditError("expected rejection missing: " + name)
    # This invokes the same production predicate with precisely its named
    # guard removed. It does not claim that all other predicates would accept.
    predicate((guard,))
    return {"name": name, "guard": guard, "intended_rejection": True,
            "same_guard_deletion_accepts": True,
            "deletion_scope": "the named production predicate"}


def copy_items(items):
    return [{"word": item["word"], "kernel": dict(item["kernel"]),
             "coefficient": item["coefficient"]} for item in items]


def controls():
    result = []
    short = paths(1)[:2]
    require(len(short) >= 2, "coarse uniform bound passes")
    require(support_mass(short, 2) == Fraction(3, 4), "strict refinement witness")
    result.append(reject("coarse bound passes but heterogeneous mass fails",
                         lambda disabled: accept_support(short, 2, disabled),
                         "heterogeneous support mass"))
    duplicate = copy_items(paths(1))
    duplicate[2] = dict(duplicate[1])
    require(support_mass(duplicate, 2) == 1, "equal mass overlap witness")
    result.append(reject("equal support mass with a repeated support",
                         lambda disabled: accept_partition(duplicate, 2, disabled),
                         "row support partition"))
    wrong_phase = copy_items(paths(1))
    wrong_phase[2]["coefficient"] = conjugate(wrong_phase[2]["coefficient"])
    accept_partition(wrong_phase, 2)
    result.append(reject("wrong Gaussian scalar phase at full support",
                         lambda disabled: accept_operator(wrong_phase, 1, disabled),
                         "complete Gaussian operator"))
    adjoint = copy_items(paths(1))
    adjoint[0]["kernel"] = {key: conjugate(value)
                              for key, value in adjoint[0]["kernel"].items()}
    accept_partition(adjoint, 2)
    result.append(reject("positive native gate replaced by its adjoint",
                         lambda disabled: accept_operator(adjoint, 1, disabled),
                         "complete Gaussian operator"))
    fixed_three = [path((letter, letter)) for letter in "ABC"]
    require(support_mass(fixed_three, 4) == Fraction(3, 8),
            "fixed three path tensor witness")
    result.append(reject("fixed three paths do not tensor to chunk two",
                         lambda disabled: accept_support(fixed_three, 4, disabled),
                         "heterogeneous support mass"))
    cancelling = copy_items(paths(1))
    extra = path("A")
    cancelling.append(extra)
    inverse_scalar = dict(extra)
    inverse_scalar["coefficient"] = mul((-Fraction(1), Fraction(0)),
                                        extra["coefficient"])
    cancelling.append(inverse_scalar)
    accept_operator(cancelling, 1)
    require(invoice(cancelling)["native_rank_mass"] == 3,
            "paid cancelling pair remains charged")
    result.append(reject("paid cancelling native pair preserves the endpoint",
                         lambda disabled: accept_invoice(cancelling, 1, disabled),
                         "complete unshared path invoice"))
    return result


def record(f):
    items = paths(f)
    accept(items, f)
    reverse = list(reversed(items))
    accept(reverse, f)
    gauged = copy_items(items)
    gauged[0]["coefficient"] = mul(gauged[0]["coefficient"], conjugate(I))
    gauged[0]["kernel"] = {offset: mul(value, I)
                            for offset, value in gauged[0]["kernel"].items()}
    accept(gauged, f)
    computed = invoice(items)
    actual = aggregate(items)
    size = 1 << (2 * f)
    return {"chunk": f, "address_bits": 2 * f,
            "paths": [{"word": item["word"],
                       "coefficient": encoded_gaussian(item["coefficient"]),
                       "kernel": encoded_kernel(item["kernel"]),
                       "rank": support_rank(item),
                       "raw_support_deficit": 2 * f - support_rank(item)}
                      for item in items],
            "invoice": computed, "monomial_paths": 2 ** f,
            "positive_rank_paths": 3 ** f - 2 ** f,
            "support_mass": encoded_fraction(support_mass(items, 2 * f)),
            "target_kernel": encoded_kernel(target_kernel(f)),
            "complete_operator": [[encoded_gaussian(actual[row ^ column])
                                   for column in range(size)] for row in range(size)],
            "all_ordinary_entries_compared": size * size,
            "all_rows_have_disjoint_complete_support": True,
            "positive_controls": ["term permutation", "opposite scalar/operator phase gauge"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require(args.output.is_absolute(), "output must be absolute")
    require(not args.output.exists(), "output already exists")
    require(not args.output.resolve().is_relative_to(Path(__file__).resolve().parent),
            "output must be external")
    cases = [record(f) for f in (1, 2, 3)]
    negatives = controls()
    result = {
        "status": "PASS_HETEROGENEOUS_SUPPORT",
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "coefficient_encoding": "[[real numerator, denominator], [imaginary numerator, denominator]]",
        "alphabet": "positive C_x=(1+i)/2 I+(1-i)/2 X_x, translations, nonzero Gaussian dyadic path scalars",
        "theorem": "sum_j 2^(-D_j)>=1 where D_j=N-r_j; if D_j=d_j*f then sum_j2^(-d_j*f)>=1",
        "scope": "formal unshared path expansion, no helper registers, no OPEN caller or physical implementation admission",
        "cases": cases, "controls": negatives,
        "coverage": {"chunks": [1, 2, 3], "ordinary_entries": 4368,
                     "rejecting_controls": len(negatives),
                     "same_predicate_deletions": len(negatives),
                     "positive_controls": 6},
        "invoice_scope": "native ranks of the displayed unshared path products only; coefficient scans, access, accumulator, dirty workspace and restoration are not priced",
        "no_new_kappa": True,
    }
    require(sum(case["all_ordinary_entries_compared"] for case in cases) == 4368,
            "complete entry coverage")
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    with args.output.open("x") as destination:
        destination.write(encoded)
    print("PASS_HETEROGENEOUS_SUPPORT: 4368 entries; 6 rejections and 6 named deletions")


if __name__ == "__main__":
    main()
