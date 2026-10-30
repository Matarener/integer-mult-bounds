"""Canonical expansion page metadata and complete numerical frame checks."""
from expansion_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from gaussian_rationals import read_count, write_count
from ring_words import Signed, power_two
from router_metadata import ceiling_log, owned
from words import need


class Fields:
    def __init__(self):
        self.fields = {}

    def keep(self, name, value):
        need(name not in self.fields, "one expansion metadata role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def close(self):
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()


def write_integer(value, target):
    target.append(int(value.negative))
    write_count(value.magnitude, target)


def read_integer(source):
    sign = source.read()
    need(sign in (0, 1), "expansion integer sign")
    source.step(1)
    magnitude = read_count(source)
    try:
        need(not sign or not magnitude.zero(), "canonical expansion integer zero")
        return Signed(magnitude, bool(sign))
    except BaseException:
        magnitude.close()
        raise


def same_integer(first, second):
    return first.negative == second.negative and compare(first.magnitude, second.magnitude) == 0


def work_width(precision, length):
    result = Count(precision)
    try:
        with owned(Count(length), Count.literal(3)) as (more, three):
            more.increment()
            with owned(ceiling_log(more)) as (guard,):
                result.add(guard)
            result.add(three)
        return result
    except BaseException:
        result.close()
        raise


def compile_frame(owner):
    for name in BlockHeader.names:
        if name != "sigma":
            positive(getattr(owner, name))
    with owned(Count.literal(1), Count.literal(2)) as (one, two):
        need(compare(owner.version, one) == 0, "expansion page version")
        need(compare(owner.alpha, two) >= 0, "expansion integer alpha at least two")
    with owned(Count(owner.s)) as (twice_s,):
        twice_s.multiply_small(2)
        need(compare(owner.s, owner.t) < 0 and compare(owner.t, twice_s) < 0,
             "near-one expansion ratio")
    need(compare(owner.m, owner.radius) <= 0 and compare(owner.m, owner.n) <= 0,
         "complete short expansion block shape")
    with owned(Count(owner.radius), Count.literal(3)) as (minimum, three):
        minimum.multiply_small(2)
        minimum.add(three)
        with owned(Count(minimum)) as (maximum,):
            maximum.add(owner.m)
            need(compare(minimum, owner.n) <= 0 and compare(owner.n, maximum) <= 0,
                 "complete bounded expansion stencil span")
    with owned(Count(owner.n), Count.literal(1)) as (total, one):
        total.add(owner.m)
        with owned(subtract(total, one)) as (expected,):
            need(compare(expected, owner.nc) == 0, "complete prefix convolution extent")
    with owned(Count(owner.p), Count(owner.p)) as (max_n, max_nc):
        max_n.multiply_small(4)
        max_nc.multiply_small(5)
        need(compare(owner.n, max_n) <= 0 and compare(owner.nc, max_nc) <= 0,
             "expansion block lengths within precision allowance")
    with owned(work_width(owner.P, owner.n)) as (expected,):
        need(compare(owner.width, expected) == 0, "expansion work width")
    with owned(Count(owner.n), Count(owner.sigma), Count(owner.p),
               Count.literal(12)) as (scaled_length, twice_sigma, minimum, guard):
        scaled_length.increment()
        scaled_length.multiply_small(32)
        twice_sigma.multiply_small(2)
        minimum.add(twice_sigma)
        minimum.add(guard)
        with owned(ceiling_log(scaled_length)) as (logarithm,):
            minimum.add(logarithm)
        need(compare(owner.P, minimum) >= 0, "expansion pre-extraction precision guard")
        with owned(subtract(owner.P, owner.p)) as (shift,):
            owner.keep("promote", Count(shift))
            owner.keep("extract", subtract(shift, twice_sigma))
    owner.keep("input_width", Count(owner.p))
    owner.input_width.increment()
    owner.input_width.increment()
    owner.keep("unit", power_two(owner.P))
    with owned(Count(owner.p)) as (twice_p,):
        twice_p.multiply_small(2)
        owner.keep("norm_bound", power_two(twice_p))
    for name, length in (("input_bits", owner.n), ("kernel_bits", owner.nc),
                         ("output_bits", owner.m)):
        owner.keep(name, Count.product(length, owner.width))


class BlockHeader(Fields):
    names = ("version", "p", "P", "width", "sigma", "s", "t", "alpha", "radius", "n", "m", "nc")
    origins = ("source_start", "target_start")

    def __init__(self, page):
        super().__init__()
        try:
            for name in self.names:
                self.keep(name, read_count(page))
            for name in self.origins:
                self.keep(name, read_integer(page))
            compile_frame(self)
        except BaseException:
            self.close()
            raise

    @classmethod
    def dump(cls, plan, page):
        for name in cls.names:
            write_count(getattr(plan, name), page)
        for name in cls.origins:
            write_integer(getattr(plan, name), page)

    def repeat(self, page):
        page.rewind()
        for name in self.names:
            with owned(read_count(page)) as (value,):
                need(compare(value, getattr(self, name)) == 0, "unchanged expansion block header")
        for name in self.origins:
            with owned(read_integer(page)) as (value,):
                need(same_integer(value, getattr(self, name)), "unchanged expansion block origin")
