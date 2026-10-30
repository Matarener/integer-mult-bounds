"""Complete tile frames, contained short windows and retained bulk metadata."""
from expansion_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from expansion_geometry import ProductionBlock
from expansion_records import Fields, read_integer, write_integer
from gaussian_prepare import ProductionPlan
from gaussian_rationals import Rational, read_count, write_count
from ring_words import Signed, add, difference, fits, power_two
from router_metadata import ceiling_log, owned
from twiddle_setup import quotient
from words import need


def advance(origin, length):
    with owned(Signed(Count(length))) as (distance,):
        return add(origin, distance)


def source_index(s, t, target, ceiling=False):
    with owned(Rational(Signed(Count.product(s, target.magnitude), target.negative), Count(t))) as (ratio,):
        return ratio.integer_part(ceiling)


def stencil_bounds(s, t, radius, target_start, target_length):
    with owned(source_index(s, t, target_start), Count(radius)) as (first, distance):
        distance.increment()
        with owned(Signed(Count(distance))) as (margin,):
            start = difference(first, margin)
    try:
        with owned(advance(target_start, target_length), Signed(Count.literal(1))) as (end, one):
            with owned(difference(end, one)) as (last_target,):
                with owned(source_index(s, t, last_target, True), Count(radius)) as (last, distance):
                    distance.increment()
                    distance.increment()
                    finish = advance(last, distance)
        return start, finish
    except BaseException:
        start.close()
        raise


def compile_tile(owner):
    for name in TileHeader.names:
        if name != "sigma":
            positive(getattr(owner, name))
    with owned(Count.literal(2)) as (two,):
        need(compare(owner.version, two) == 0 and compare(owner.alpha, two) >= 0,
             "expansion tile version and integer alpha")
    with owned(Count(owner.s)) as (twice,):
        twice.multiply_small(2)
        need(compare(owner.s, owner.t) < 0 and compare(owner.t, twice) < 0,
             "expansion tile near-one ratio")
    for value in (owner.s, owner.t, owner.alpha):
        fits(value, owner.p)
    need(compare(owner.source_count, owner.input_capacity) <= 0, "expansion halo fits its padded capacity")
    with owned(quotient(owner.target_length, owner.radius, True)) as (blocks,):
        need(compare(blocks, owner.blocks) == 0, "complete expansion tile block count")
    with owned(Count(owner.radius), Count(owner.radius), Count.literal(3), Count.literal(2),
               Count(owner.p), Count(owner.p)) as (max_n, max_nc, three, two, p4, p5):
        max_n.multiply_small(3)
        max_n.add(three)
        max_nc.multiply_small(4)
        max_nc.add(two)
        p4.multiply_small(4)
        p5.multiply_small(5)
        need(compare(max_n, p4) <= 0 and compare(max_nc, p5) <= 0,
             "uniform short expansion tile blocks")
        max_n.increment()
        max_n.multiply_small(32)
        with owned(ceiling_log(max_n), Count(owner.p), Count(owner.sigma), Count.literal(12)) as (logarithm, minimum, scale, guard):
            scale.multiply_small(2)
            minimum.add(scale)
            minimum.add(logarithm)
            minimum.add(guard)
            need(compare(owner.P, minimum) >= 0, "complete expansion tile precision guard")
    owner.keep("input_width", Count(owner.p))
    owner.input_width.increment()
    owner.input_width.increment()
    owner.keep("record_width", Count(owner.input_width))
    owner.record_width.multiply_small(2)
    with owned(Count(owner.p)) as (twice_p,):
        twice_p.multiply_small(2)
        owner.keep("norm_bound", power_two(twice_p))


class TileHeader(Fields):
    names = ("version", "p", "P", "sigma", "s", "t", "alpha", "radius",
             "source_count", "input_capacity", "target_length", "blocks")
    origins = ("source_start", "target_start")

    def __init__(self, page):
        super().__init__()
        try:
            for name in self.names:
                self.keep(name, read_count(page))
            for name in self.origins:
                self.keep(name, read_integer(page))
            compile_tile(self)
        except BaseException:
            self.close()
            raise

    @classmethod
    def dump(cls, plan, target):
        for name in cls.names:
            write_count(getattr(plan, name), target)
        for name in cls.origins:
            write_integer(getattr(plan, name), target)


class TileGeometry(Fields):
    def __init__(self, s, t, alpha, radius, source_start, source_count, input_capacity,
                 target_start, target_length, p, precision, sigma):
        super().__init__()
        try:
            for name, value in (("s", s), ("t", t), ("alpha", alpha), ("radius", radius),
                                ("source_count", source_count), ("input_capacity", input_capacity),
                                ("target_length", target_length), ("p", p), ("P", precision), ("sigma", sigma)):
                self.keep(name, Count(value))
                if name != "sigma":
                    positive(value)
            self.keep("version", Count.literal(2))
            self.keep("source_start", source_start.copy())
            self.keep("target_start", target_start.copy())
            self.keep("blocks", quotient(target_length, radius, True))
            compile_tile(self)
            first, last = stencil_bounds(s, t, radius, target_start, target_length)
            with owned(first, last, advance(source_start, source_count)) as (first, last, source_end):
                with owned(difference(first, source_start), difference(source_end, last)) as (left, right):
                    need(not left.negative and not right.negative,
                         "complete expansion source halo contains every short stencil")
        except BaseException:
            self.close()
            raise


class ProductionTile(Fields):
    """Retain the microbox halo and the matching compression metadata."""
    def __init__(self, s, t, d, alpha, p, tile_index):
        super().__init__()
        try:
            self.keep("block_plan", ProductionBlock(p, alpha))
            for name, value in (("s", s), ("t", t), ("d", d), ("alpha", alpha), ("p", p),
                                ("radius", self.block_plan.radius), ("P", self.block_plan.P),
                                ("sigma", self.block_plan.sigma), ("u", self.block_plan.u)):
                self.keep(name, Count(value))
            with owned(Count.product(p, p)) as (square,):
                self.keep("halo", Count.product(square, p))
                self.halo.multiply_small(4096)
                with owned(Count.product(square, square)) as (fourth,):
                    with owned(Count.product(fourth, fourth)) as (eighth,):
                        with owned(ceiling_log(eighth)) as (logarithm,):
                            self.keep("L", power_two(logarithm))
            with owned(ceiling_log(t)) as (logarithm,):
                with owned(power_two(logarithm)) as (dyadic,):
                    need(compare(dyadic, t) == 0, "production expansion dyadic target")
            self.keep("target_start", Signed(Count.product(tile_index, self.L)))
            self.keep("target_length", Count(self.L))
            self.keep("input_capacity", Count(self.L))
            with owned(advance(self.target_start, self.L)) as (end,):
                need(not end.negative and compare(end.magnitude, t) <= 0,
                     "production complete target tile")
                core_start = source_index(s, t, self.target_start)
                try:
                    core_end = source_index(s, t, end)
                except BaseException:
                    core_start.close()
                    raise
            with owned(core_start, core_end) as (core_start, core_end):
                with owned(difference(core_end, core_start), Signed(Count(self.halo))) as (core_length, halo):
                    need(not core_length.negative and not core_length.magnitude.zero(), "positive source core")
                    with owned(difference(self.target_start, halo), Count(self.halo)) as (halo_start, halo_length):
                        halo_length.multiply_small(2)
                        halo_length.add(self.L)
                        self.keep("inverse_plan", ProductionPlan(s, t, d, self.u, p, halo_start,
                            halo_length, core_start, core_length.magnitude))
            self.keep("source_start", self.inverse_plan.start.copy())
            self.keep("source_count", Count(self.inverse_plan.m))
            with owned(Count(self.L), Count(self.halo), Count(self.inverse_plan.w)) as (covered, halos, bands):
                halos.multiply_small(2)
                bands.multiply_small(2)
                covered.add(halos)
                covered.add(bands)
                covered.multiply_small(2)
                need(compare(s, covered) > 0, "production global period exceeds twice the padded halo")
            with owned(Count.product(d, self.halo)) as (required,):
                required.multiply_small(64)
                need(compare(self.L, required) >= 0, "production source-padding headroom")
            need(compare(self.P, self.inverse_plan.P) == 0, "paired Gaussian work grid")
            self.keep("version", Count.literal(2))
            self.keep("blocks", quotient(self.L, self.radius, True))
            compile_tile(self)
        except BaseException:
            self.close()
            raise
