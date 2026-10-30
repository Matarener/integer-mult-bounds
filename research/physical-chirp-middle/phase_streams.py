"""Sequential exact phase products and value-preserving signed narrowing."""

from chirp_sources import active
active()
from chirp_plan import GridPlan
from ring_words import read_signed, write_signed
from router_metadata import indices, owned
from words import BLANK, need


def paired(first, second, plan, pool, arithmetic, conjugate=False):
    need(type(conjugate) is bool, "finite endpoint conjugation")
    result = pool.acquire()
    first.rewind()
    second.rewind()
    grid = GridPlan(plan.p, plan.small_word_width)
    try:
        for _ in indices(plan.gaussians):
            with owned(read_signed(first, plan.small), read_signed(first, plan.small),
                       read_signed(second, plan.small), read_signed(second, plan.small)) as values:
                a, b, c, d = values
                with owned(b.negated() if conjugate else b.copy()) as (imaginary,):
                    with owned(*arithmetic.pointwise(a, imaginary, c, d, grid)) as output:
                        for value in output:
                            write_signed(value, result, plan.small)
        need(first.read() == second.read() == BLANK, "complete paired phase packets")
        result.rewind()
        return result
    except BaseException:
        result.clear()
        raise
    finally:
        first.rewind()
        second.rewind()


def repeated(source, table, plan, pool, arithmetic, conjugate=False):
    need(type(conjugate) is bool, "finite twist conjugation")
    result = pool.acquire()
    source.rewind()
    grid = GridPlan(plan.p, plan.small_word_width)
    try:
        for _ in indices(plan.records):
            table.rewind()
            for _ in indices(plan.r):
                with owned(read_signed(source, plan.small), read_signed(source, plan.small),
                           read_signed(table, plan.small), read_signed(table, plan.small)) as values:
                    a, b, u, v = values
                    with owned(v.negated() if conjugate else v.copy()) as (imaginary,):
                        with owned(*arithmetic.pointwise(a, b, u, imaginary, grid)) as output:
                            for value in output:
                                write_signed(value, result, plan.small)
            need(table.read() == BLANK, "complete repeated twist table")
        need(source.read() == BLANK, "complete coefficient-twist packet")
        result.rewind()
        return result
    except BaseException:
        result.clear()
        raise
    finally:
        source.rewind()
        table.rewind()


def narrow(source, incoming_width, plan, pool):
    result = pool.acquire()
    source.rewind()
    try:
        for _ in indices(plan.gaussians):
            for _ in range(2):
                with owned(read_signed(source, incoming_width)) as (value,):
                    # The signed writer rejects a value needing discarded high bits.
                    write_signed(value, result, plan.small)
        need(source.read() == BLANK, "complete exact width-narrowing packet")
        result.rewind()
        return result
    except BaseException:
        result.clear()
        raise
    finally:
        source.rewind()
