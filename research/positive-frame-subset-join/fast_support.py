"""Exact integer subset joins. Produced by Nick Petalas, Apache-2.0."""

from fractions import Fraction
from itertools import product
from math import gcd, lcm


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer_vectors(vectors):
    """One injective denominator clearing for all labels and targets."""
    require(len(vectors) == 10, "six labels and four targets required")
    denominator = 1
    for vector in vectors:
        require(len(vector) == 3, "three coordinates required")
        for value in vector:
            require(type(value) in (int, Fraction), "exact rational required")
            value = Fraction(value)
            require(max(value.numerator.bit_length(), value.denominator.bit_length())
                    <= 256, "rational exceeds 256-bit input bound")
            denominator = lcm(denominator, value.denominator)
    return tuple(tuple(Fraction(value).numerator
                       * (denominator // Fraction(value).denominator)
                       for value in vector) for vector in vectors)


def subset_sums(vectors, counts):
    """At most 81 old-label or 25 added-label integer triples."""
    return {tuple(sum(u[j] * vectors[j][axis] for j in range(len(counts)))
                  for axis in range(3))
            for u in product(*(range(count + 1) for count in counts))}


def support_mask(counts, labels, targets):
    require(len(counts) == 6, "six multiplicities required")
    require(all(type(count) is int and 0 <= count <= 8 for count in counts)
            and sum(counts) <= 8, "total multiplicity must be at most eight")
    require(len(labels) == 6 and len(targets) == 4, "wrong label or target count")
    vectors = integer_vectors(tuple(labels) + tuple(targets))
    old = subset_sums(vectors[:4], counts[:4])
    added = subset_sums(vectors[4:6], counts[4:])
    return tuple(any(tuple(target[i] - value[i] for i in range(3)) in old
                     for value in added) for target in vectors[6:])


def concrete_splits(source, profiles, grid=8):
    """PR6111's concrete split inventory, in its original order."""
    require(len(profiles) <= 442 and type(grid) is int and 1 <= grid <= 8,
            "concrete inventory exceeds the frozen replay bounds")
    for counts, residual in profiles:
        r, s = counts[4:]
        if source.det(residual) > 0:
            splits = [source.split_from_direction(residual, x, y)
                      for x in range(-grid, grid + 1) for y in range(grid + 1)
                      if gcd(x, y) == 1 and not (y == 0 and x != 1)]
        else:
            splits = sorted({source.sc(Fraction(k, m), residual)
                             for m in range(2, 41) for k in range(1, m)})
        for split in splits:
            left = source.sc(Fraction(1, r), split)
            right = source.sc(Fraction(1, s),
                              source.add(residual, source.sc(-1, split)))
            if not (source.psd_rank1(left) and source.psd_rank1(right)):
                raise SystemExit("FAIL: concrete split")
            yield counts, left, right


def direct_support_regression(source, profiles, grid=8):
    """Adapt PR6111's loop, changing only the subset-support predicate."""
    tested = passed = 0
    for counts, left, right in concrete_splits(source, profiles, grid):
        tested += 1
        if all(support_mask(counts, source.OLD + (left, right), source.TARGETS)):
            passed += 1
            if not source.lattice_killers(counts, left, right):
                raise SystemExit("FAIL: concrete survivor %r" % ((counts, left, right),))
    return tested, passed
