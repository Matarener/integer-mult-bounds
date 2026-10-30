"""One rounded periodic Gaussian reference, with original cells and hole rules.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Geometry/reference: Vlado, Jeremy Kothe and Cinna Davis.
Outward interval arithmetic: Mason Hale.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import isqrt

from exact import Mat, ceil_log2, need
from gaussian import INTERVALS, load_intervals, rational


def ceiling(x):
    x = rational(x)
    return -(-x.numerator // x.denominator)


def nearest_up(x):
    x = rational(x) + Q(1, 2)
    return x.numerator // x.denominator


def ceiling_sqrt(x):
    x = rational(x)
    need(x >= 0, "nonnegative exact square root bound")
    root = isqrt(x.numerator // x.denominator)
    return root + int(root * root < x)


class Exponentials:
    def __init__(self, raw):
        self.oracle = load_intervals(raw[INTERVALS])

    def decay_box(self, factor, bits):
        factor = rational(factor)
        need(factor >= 0 and type(bits) is int and bits >= 16, "decay domain")
        if factor == 0:
            return self.oracle.Interval.rational(1, bits)
        box = self.oracle.exp_negative(self.oracle.pi_interval(bits) * factor)
        need(Q(box.hi - box.lo, box.scale) <= 512 * bits ** 2 * Q(1, 1 << bits),
             "retained decay width")
        return box

    def absolute(self, factor, error_bits):
        need(type(error_bits) is int and error_bits >= 1, "absolute exponential precision")
        p = error_bits + 1
        box = self.decay_box(factor, 2 * p + 32)
        result, error = self.oracle.inward_quantize(
            (box, self.oracle.Interval.rational(0, box.bits)), p)
        value = Q(result[0], 1 << p)
        need(result[1] == 0 and 0 <= value <= 1 and error <= Q(1, 1 << error_bits),
             "absolute decay receipt")
        return value, error

    def relative(self, factor, exponent_bound, relative_bits, precision=None):
        factor, exponent_bound = rational(factor), rational(exponent_bound)
        need(0 <= factor <= exponent_bound and type(relative_bits) is int and relative_bits >= 1,
             "relative positive exponential domain")
        length = ceiling(8 * exponent_bound)
        required = length + relative_bits + 3
        p = required if precision is None else precision
        need(type(p) is int and p >= required, "positive weight setup precision")
        box = self.decay_box(factor, 2 * p + 32)
        step = 1 << (box.bits - p)
        value = Q(box.lo // step, 1 << p)
        absolute_error = max(abs(value - Q(box.lo, box.scale)), abs(value - Q(box.hi, box.scale)))
        relative_error = absolute_error * (1 << length)
        need(value > 0 and relative_error <= Q(1, 1 << (relative_bits + 2)),
             "positive relative weight receipt")
        return dict(value=value, absolute_error=absolute_error, relative_error=relative_error,
                    precision=p, working_bits=box.bits, exponent=factor,
                    lower=Q(box.lo, box.scale), upper=Q(box.hi, box.scale))

    def geometric_tail(self, first, step, scale, bits):
        numerator, ratio = self.decay_box(first, bits), self.decay_box(step, bits)
        denominator = 1 - Q(ratio.hi, ratio.scale)
        need(denominator > 0, "positive Gaussian tail denominator")
        return rational(scale) * Q(numerator.hi, numerator.scale) / denominator


@dataclass(frozen=True)
class ReferenceSpec:
    source_size: int
    excess: int
    alpha: int
    source_halfwidth: int
    target_halfwidth: int
    entry_bits: int


@dataclass(frozen=True)
class Entry:
    value: Q
    kind: str
    lift: int
    retained_error: Q


class Coordinates:
    def __init__(self, size, function):
        self.size, self.function = size, function

    def __getitem__(self, key):
        if isinstance(key, slice):
            return tuple(self.function(j) for j in range(*key.indices(self.size)))
        need(type(key) is int, "integer coordinate index")
        key = key + self.size if key < 0 else key
        if not 0 <= key < self.size:
            raise IndexError(key)
        return self.function(key)

    def __iter__(self):
        return (self.function(j) for j in range(self.size))

    def __len__(self):
        return self.size


class SelectedAddresses:
    def __init__(self, selected, source_size, target_size):
        self.selected, self.source_size, self.target_size = selected, source_size, target_size

    def get(self, coordinate):
        candidate = nearest_up(Q(self.source_size * coordinate, self.target_size))
        if 0 <= candidate < self.source_size and self.selected[candidate] == coordinate:
            return candidate
        return None


class Reference:
    def __init__(self, raw, source_size, excess, alpha, source_halfwidth,
                 target_halfwidth, entry_bits):
        need(all(type(x) is int for x in (source_size, excess, alpha, source_halfwidth,
                                         target_halfwidth, entry_bits)), "integer reference parameters")
        need(0 < excess < source_size and alpha >= 1 and entry_bits >= 8,
             "Gaussian reference geometry")
        target_size = source_size + excess
        need(0 <= 2 * source_halfwidth < source_size and 0 <= 2 * target_halfwidth < target_size,
             "unique retained periodic lifts")
        self.spec = ReferenceSpec(source_size, excess, alpha, source_halfwidth,
                                  target_halfwidth, entry_bits)
        self.allocation = None
        self.theta, self.rho, self.lam = Q(excess, source_size), Q(target_size, source_size), Q(source_size, target_size)
        self.target_size = target_size
        self.phases = Coordinates(source_size, lambda j: nearest_up(self.theta * j))
        self.selected = Coordinates(source_size, lambda j: j + self.phases[j])
        need(self.selected[0] == 0 and self.selected[-1] < target_size, "selected endpoint range")
        self.source_at = SelectedAddresses(self.selected, source_size, target_size)
        self._holes = None
        self.betas = Coordinates(source_size, lambda j: self.theta * j - self.phases[j])
        self.exp = Exponentials(raw)
        self.weight_exponent_bound = Q(alpha ** 2, 4) / self.theta
        self.weight_relative_bits = entry_bits + 4
        self.weight_precision = ceiling(8 * self.weight_exponent_bound) + self.weight_relative_bits + 3
        self.ratio_log_bound = ceiling(8 * alpha ** 2 * source_halfwidth)
        self.kernel_error_bits = entry_bits + self.ratio_log_bound + 4
        self.weights, self.kernel, self.entries = {}, {}, {}
        work = 2 * (entry_bits + ceiling(8 * alpha ** 2 * self.rho ** 2) + 16) + 32
        w, width = source_halfwidth, target_halfwidth
        self.narrow_tail = self.exp.geometric_tail(alpha ** 2 * w * (w + 1),
                                                   2 * alpha ** 2 * (w + 1), 2, work)
        broad_c = 1 / (alpha ** 2 * self.rho ** 2)
        self.broad_tail = self.exp.geometric_tail(broad_c * (width + Q(1, 2)) ** 2,
                                                  2 * broad_c * (width + 1), Q(2, alpha), work)
        self.entry_error = Q(1, 1 << entry_bits)
        self.errors = {
            "narrow": self.narrow_tail + (2 * w + 1) * self.entry_error,
            "broad": self.broad_tail + (2 * width + 1) * self.entry_error,
        }
        adjacent = self.exp.decay_box(2 * alpha ** 2 * self.theta, work)
        distant = self.exp.decay_box(2 * alpha ** 2, work)
        self.narrow_gap = (1 - Q(adjacent.hi, adjacent.scale)
                           - 5 * Q(distant.hi, distant.scale) - self.errors["narrow"])
        self.narrow_inverse_bounds = None
        if self.narrow_gap > 0:
            width = 2 * source_halfwidth + 2
            self.narrow_inverse_bounds = (
                1 / self.narrow_gap,
                1 / self.narrow_gap + 2 * width * (1 - self.narrow_gap) / self.narrow_gap ** 2)
        description = {key: getattr(self.spec, key) for key in self.spec.__dataclass_fields__}
        self.description_hash = sha256(json.dumps(description, sort_keys=True).encode()).hexdigest()

    @property
    def holes(self):
        if self._holes is None:
            self._holes = tuple(k for k in range(self.target_size) if self.source_at.get(k) is None)
        return self._holes

    @classmethod
    def for_cap(cls, raw, source_size, excess, alpha, cap, radius, target):
        need(all(type(x) is int for x in (source_size, excess, alpha, cap, target))
             and 0 < excess < source_size and alpha >= 1 and cap > 0
             and cap & (cap - 1) == 0 and 2 * cap <= source_size and target >= 1,
             "uniform reference cap and geometry")
        radius = rational(radius)
        need(radius >= 1, "uniform reference radius")
        theta, rho = Q(excess, source_size), Q(source_size + excess, source_size)
        from gaussian import Gaussian
        exponent = 1 + alpha ** 2 * theta * (cap ** 2 + cap + 1)
        gauge = alpha * (1 << ceiling(8 * exponent))
        middle = 2 * Gaussian(raw, cap, 1 / (alpha ** 2 * rho), 0, 1, 1).qbar
        inverse = gauge ** 2 * middle
        error_bits = target + ceil_log2(8 * (radius + 1) * inverse ** 2)
        source_width = ceiling_sqrt(Q(error_bits + 5, 3 * alpha ** 2))
        a = alpha ** 2 * rho ** 2
        target_width = max(ceiling(a), ceiling_sqrt(a * (error_bits + 5) / 3),
                           2 * source_width + 2)
        entry_bits = error_bits + 3 + ceil_log2(2 * max(source_width, target_width) + 1)
        result = cls(raw, source_size, excess, alpha, source_width, target_width, entry_bits)
        need(max(result.errors.values()) <= Q(1, 1 << error_bits), "uniform cap reference error")
        result.allocation = dict(cap=cap, radius=str(radius), target_bits=target,
                                 gauge_exponent_bound=str(exponent), gauge_bound=str(gauge),
                                 normalized_bound=str(middle), inverse_bound=str(inverse),
                                 error_bits=error_bits)
        return result

    def weight(self, j):
        need(type(j) is int and 0 <= j < self.spec.source_size, "global weight index")
        if j not in self.weights:
            factor = self.spec.alpha ** 2 * (Q(1, 4) - self.betas[j] ** 2) / self.theta
            self.weights[j] = self.exp.relative(factor, self.weight_exponent_bound,
                                               self.weight_relative_bits, self.weight_precision)
        return self.weights[j]["value"]

    def kernel_value(self, h):
        h = abs(h)
        need(h <= self.spec.source_halfwidth, "retained unshifted source offset")
        if h not in self.kernel:
            self.kernel[h] = self.exp.absolute(self.spec.alpha ** 2 * self.rho * h ** 2,
                                               self.kernel_error_bits)
        return self.kernel[h][0]

    def _narrow(self, row, column):
        i, j = self.source_at.get(row), self.source_at.get(column)
        if i is None or j is None:
            return Entry(Q(int(row == column)), "hole-identity", 0, Q(0))
        if i == j:
            return Entry(Q(1), "unit-diagonal", 0, Q(0))
        source_size = self.spec.source_size
        lift = -nearest_up(Q(j - i, source_size))
        h = j + lift * source_size - i
        if abs(h) > self.spec.source_halfwidth:
            return Entry(Q(0), "omitted", lift, Q(0))
        if lift == 0 and self.phases[i] == self.phases[j]:
            value = self.weight(i) * self.kernel_value(h) / self.weight(j)
            return Entry(value, "shared-weight-ratio", lift, self.entry_error)
        factor = self.spec.alpha ** 2 * ((self.rho * h + self.betas[i]) ** 2 - self.betas[j] ** 2)
        value, error = self.exp.absolute(factor, self.spec.entry_bits + 2)
        return Entry(value, "cross-period" if lift else "cross-cell", lift, error)

    def _broad(self, row, column):
        j = self.source_at.get(column)
        if j is None:
            return Entry(Q(int(row == column)), "hole-column", 0, Q(0))
        lift = -nearest_up(Q(column - row, self.target_size))
        distance = column + lift * self.target_size - row
        if abs(distance) > self.spec.target_halfwidth:
            return Entry(Q(0), "omitted", lift, Q(0))
        factor = (j + lift * self.spec.source_size - self.lam * row) ** 2 / self.spec.alpha ** 2
        value, error = self.exp.absolute(factor, self.spec.entry_bits + 2)
        return Entry(value / self.spec.alpha, "broad-gaussian", lift, error / self.spec.alpha)

    def entry(self, kind, row, column):
        need(kind in ("narrow", "broad") and type(row) is int and type(column) is int
             and 0 <= row < self.target_size and 0 <= column < self.target_size, "reference entry domain")
        key = kind, row, column
        if key not in self.entries:
            self.entries[key] = (self._narrow if kind == "narrow" else self._broad)(row, column)
        return self.entries[key]

    def window(self, kind, indices):
        need(len(set(indices)) == len(indices), "distinct reference window coordinates")
        return Mat([[self.entry(kind, i, j).value for j in indices] for i in indices])

    def interior(self, start, n):
        size = self.spec.source_size
        need(type(start) is int and type(n) is int and n > 0 and n & (n - 1) == 0
             and 0 <= start and start + n <= size and 2 * n <= size,
             "dyadic interior inside original period cut")
        phase = self.phases[start]
        need(all(self.phases[j] == phase for j in range(start, start + n)),
             "interior stays inside one original phase cell")
        center = Q(2 * start + n - 1, 2)
        beta = self.theta * center - phase
        coordinates = self.selected[start:start + n]
        need(coordinates == tuple(range(coordinates[0], coordinates[0] + n)),
             "unit target gaps in the interior")
        return coordinates, center, beta

    def require_narrow_gap(self):
        need(self.narrow_gap > 0, "positive common narrow reference row gap")
        return self.narrow_inverse_bounds

    def record(self):
        materialize = self.spec.source_size <= 1024
        return dict(description_sha256=self.description_hash,
                    allocation=self.allocation,
                    parameters={key: getattr(self.spec, key) for key in self.spec.__dataclass_fields__},
                    target_size=self.target_size, geometry_materialized=materialize,
                    selected=list(self.selected) if materialize else None,
                    holes=list(self.holes) if materialize else None,
                    phases=list(self.phases) if materialize else None,
                    weight_precision=self.weight_precision,
                    weight_relative_bits=self.weight_relative_bits, kernel_error_bits=self.kernel_error_bits,
                    narrow_tail=str(self.narrow_tail), broad_tail=str(self.broad_tail),
                    narrow_error=str(self.errors["narrow"]), broad_error=str(self.errors["broad"]),
                    narrow_gap_lower=str(self.narrow_gap),
                    narrow_inverse_bounds=None if self.narrow_inverse_bounds is None
                    else list(map(str, self.narrow_inverse_bounds)),
                    narrow_physical_bandwidth=2 * self.spec.source_halfwidth + 2,
                    broad_physical_bandwidth=self.spec.target_halfwidth,
                    weight_receipts=[dict(index=j, **{key: str(value) if isinstance(value, Q) else value
                                                     for key, value in self.weights[j].items()})
                                     for j in sorted(self.weights)],
                    kernel_receipts=[dict(offset=h, value=str(self.kernel[h][0]),
                                          error=str(self.kernel[h][1]))
                                     for h in sorted(self.kernel)])
