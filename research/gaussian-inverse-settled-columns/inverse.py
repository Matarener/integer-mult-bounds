"""Skip proved identity columns in the physical Gaussian setup inverse.

Derived from Jose Manuel's PR3851 gaussian_matrix.inverse, Apache-2.0.
The suffix traversal and its resource proof were produced by Nick Petalas.
"""
from contextlib import closing
from cardinal_counts import Count
from encoded import compare, subtract
from gaussian_matrix import Matrix
from gaussian_rationals import Rational
from router_metadata import indices, owned
from words import need


def suffix_indices(start, stop):
    """Borrow endpoints and yield an owned encoded cursor on [start, stop)."""
    need(compare(start, stop) <= 0, "ordered inverse column interval")
    with owned(Count(start), subtract(stop, start)) as (cursor, length):
        for _ in indices(length):
            yield cursor
            cursor.increment()


def normalize(augmented, k, pivot):
    with closing(suffix_indices(k, augmented.columns)) as columns:
        for j in columns:
            with owned(augmented.get(k, j)) as (previous,):
                if previous.numerator.magnitude.zero():
                    continue
                with owned(previous.over(pivot)) as (value,):
                    augmented.set(k, j, value)


def eliminate(augmented, k, dimension):
    for i in indices(dimension):
        if compare(i, k) == 0:
            continue
        with owned(augmented.get(i, k)) as (factor,):
            if factor.numerator.magnitude.zero():
                continue
            with closing(suffix_indices(k, augmented.columns)) as columns:
                for j in columns:
                    with owned(augmented.get(k, j)) as (source,):
                        if source.numerator.magnitude.zero():
                            continue
                        with owned(augmented.get(i, j)) as (previous,):
                            with owned(factor.times(source)) as (product,):
                                with owned(previous.minus(product)) as (value,):
                                    augmented.set(i, j, value)


def inverse(matrix):
    """Same positive-pivot contract and exact result as PR3851's inverse."""
    need(compare(matrix.rows, matrix.columns) == 0, "square exact inverse")
    dimension = matrix.rows

    def entry(i, j):
        if compare(j, dimension) < 0:
            return matrix.get(i, j)
        with owned(subtract(j, dimension)) as (column,):
            return Rational.literal(1 if compare(i, column) == 0 else 0)

    with owned(Count(dimension)) as (twice,):
        twice.multiply_small(2)
        augmented = Matrix(dimension, twice, matrix.pool, entry)
    try:
        for k in indices(dimension):
            with owned(augmented.get(k, k)) as (pivot,):
                need(not pivot.numerator.negative and not pivot.numerator.magnitude.zero(),
                     "positive exact setup pivot")
                normalize(augmented, k, pivot)
            eliminate(augmented, k, dimension)

        def right(i, j):
            with owned(Count(j)) as (column,):
                column.add(dimension)
                return augmented.get(i, column)

        return Matrix(dimension, dimension, matrix.pool, right)
    finally:
        augmented.close()
