"""Global lifted geometry and rational real-chirp exponents for one block."""
from expansion_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from expansion_records import Fields, compile_frame, work_width
from gaussian_rationals import Rational
from ring_words import Signed, add, fits
from router_metadata import owned
from words import need


def integer(value):
    return Rational(Signed(Count(value)), Count.literal(1), False)


def absolute(value):
    return Rational(Signed(Count(value.numerator.magnitude)), Count(value.denominator), False)


class BlockGeometry(Fields):
    def __init__(self, s, t, alpha, radius, target_start, target_length, p, precision, sigma):
        super().__init__()
        try:
            for name, value in (("s", s), ("t", t), ("alpha", alpha), ("radius", radius),
                                ("m", target_length), ("p", p), ("P", precision), ("sigma", sigma)):
                self.keep(name, Count(value))
                if name != "sigma":
                    positive(value)
            self.keep("version", Count.literal(1))
            self.keep("target_start", target_start.copy())
            with owned(Count(s)) as (twice_s,):
                twice_s.multiply_small(2)
                need(compare(s, t) < 0 and compare(t, twice_s) < 0, "expansion source ratio")
            need(compare(target_length, radius) <= 0, "expansion target block within radius")
            fits(s, p)
            fits(t, p)
            fits(alpha, p)
            with owned(Count(p)) as (origin_width,):
                origin_width.increment()
                origin_width.increment()
                fits(target_start.magnitude, origin_width)
            self.keep("u", Count.product(alpha, alpha))
            self.keep("kappa", Rational(Signed(Count(s)), Count(t)))
            self.keep("u_value", integer(self.u))
            with owned(Rational.integer(target_start)) as (target,):
                with owned(self.kappa.times(target)) as (center,):
                    self.keep("j0", center.integer_part())
                    with owned(Rational.integer(self.j0)) as (origin,):
                        self.keep("gamma", origin.minus(center))
            with owned(Rational.literal(-1), Rational.literal(0)) as (minus_one, zero):
                need(self.gamma.compare(minus_one) > 0 and self.gamma.compare(zero) <= 0,
                     "global expansion fractional origin")
            low_magnitude = Count(radius)
            low_magnitude.increment()
            self.keep("h_low", Signed(low_magnitude, True))
            with owned(Count.literal(1)) as (one,):
                with owned(subtract(target_length, one)) as (last,):
                    with owned(integer(last)) as (position,):
                        with owned(self.kappa.times(position)) as (scaled,):
                            with owned(scaled.minus(self.gamma)) as (relative,):
                                high = relative.integer_part(True)
            try:
                need(not high.negative, "nonnegative expansion upper origin")
                high.magnitude.add(radius)
                high.magnitude.increment()
                self.keep("h_high", high)
                high = None
            finally:
                if high is not None:
                    high.close()
            self.keep("n", Count(self.h_high.magnitude))
            self.n.add(radius)
            self.n.increment()
            self.n.increment()
            with owned(Count(self.n), Count.literal(1)) as (total, one):
                total.add(target_length)
                self.keep("nc", subtract(total, one))
            self.keep("source_start", add(self.j0, self.h_low))
            self.keep("kernel_start", self.h_high.negated())
            self.keep("width", work_width(precision, self.n))
            compile_frame(self)
            self.prepare_quadratics()
        except BaseException:
            self.close()
            raise

    def prepare_quadratics(self):
        with owned(Rational.literal(1), Rational.literal(2)) as (one, two):
            with owned(one.minus(self.kappa)) as (difference,):
                self.keep("a_square", difference.over(self.u_value))
            with owned(two.times(self.gamma)) as (twice_gamma,):
                self.keep("a_linear", twice_gamma.over(self.u_value))
                with owned(twice_gamma.times(self.kappa)) as (product,):
                    with owned(product.negated()) as (negative,):
                        self.keep("b_linear", negative.over(self.u_value))
            with owned(self.gamma.times(self.gamma)) as (square,):
                self.keep("a_constant", square.over(self.u_value))
            with owned(self.kappa.times(self.kappa)) as (square,):
                with owned(square.minus(self.kappa)) as (difference,):
                    self.keep("b_square", difference.over(self.u_value))
            self.keep("kernel_square", self.kappa.over(self.u_value))

    def exponent(self, kind, index):
        need(kind in ("A", "K", "B"), "fixed expansion factor family")
        length = self.n if kind == "A" else self.nc if kind == "K" else self.m
        need(compare(index, length) < 0, "expansion factor index")
        with owned(Signed(Count(index))) as (ordinal,):
            if kind == "A":
                position = add(self.h_low, ordinal)
            elif kind == "K":
                position = add(self.kernel_start, ordinal)
            else:
                position = ordinal.copy()
        with owned(position):
            with owned(Rational.integer(position)) as (x,):
                with owned(x.times(x)) as (square,):
                    if kind == "K":
                        return self.kernel_square.times(square)
                    square_factor = self.a_square if kind == "A" else self.b_square
                    linear_factor = self.a_linear if kind == "A" else self.b_linear
                    with owned(square_factor.times(square), linear_factor.times(x)) as (quadratic, linear):
                        total = quadratic.plus(linear)
                    if kind == "B":
                        return total
                    with owned(total):
                        return total.plus(self.a_constant)


class ProductionBlock(Fields):
    """Derive the retained all-size radius, work grid and normalization scale."""
    def __init__(self, p, alpha):
        super().__init__()
        try:
            positive(p)
            positive(alpha)
            with owned(Count.literal(101), Count.literal(2)) as (minimum, two):
                need(compare(p, minimum) >= 0 and compare(alpha, two) >= 0,
                     "production expansion precision and integer alpha")
            self.keep("u", Count.product(alpha, alpha))
            need(compare(self.u, p) < 0, "production alpha squared below precision")
            self.keep("root", Count.literal(1))
            while True:
                with owned(Count.product(self.root, self.root)) as (square,):
                    if compare(square, p) >= 0:
                        break
                self.root.increment()
            self.keep("radius", Count.product(alpha, self.root))
            self.keep("P", Count(p))
            self.P.multiply_small(32768)
            self.keep("sigma", Count(p))
            self.sigma.multiply_small(4096)
        except BaseException:
            self.close()
            raise
