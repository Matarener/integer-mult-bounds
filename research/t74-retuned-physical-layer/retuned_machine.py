"""Keep the frozen node transition, with a new fixed stopping exponent."""

from active_sources import active, require
active()
from retuned_native import profile
from t74_machine import T74Machine
from machine import BLANK, Count, compare, divide, fixed_power, need, positive, skip, subtract


class RetunedMachine(T74Machine):
    STOP_POWER = 1000000

    def __init__(self, binding, native, catalogue, observe=None):
        require(native.profile == profile(), "retuned ordinary profile before machine construction")
        super().__init__(binding, native, catalogue, observe)

    def node(self):
        dimension = Count.literal(self.binding.dimension)
        test = extent = columns = removed = rest = suffix = shift = divisor = unused = remainder = None
        try:
            for name in ("prefixes", "rows", "spacing", "guard", "component_bits", "coefficients", "root_width"):
                positive(self.c(name))
            need(compare(self.c("width"), self.c("root_width")) <= 0, "node within global width")
            self.shape()
            extent = self.complete_extent()
            self.roles["current"].rewind()
            skip(self.roles["current"], extent)
            need(self.roles["current"].read() == BLANK, "complete node input")
            self.roles["current"].rewind()
            if self.c("width").zero() or compare(self.c("width"), dimension) < 0:
                self.apply_leaf(self.c("width"), self.c("before"), self.c("after"))
                self.mode = "return"
                return
            test = fixed_power(self.c("width"), self.STOP_POWER, self.c("root_width"))
            if compare(test, self.c("root_width")) < 0:
                self.apply_leaf(self.c("width"), self.c("before"), self.c("after"))
                self.mode = "return"
                return
            columns = Count(self.c("width"))
            delta = columns.divide_small(self.binding.dimension)
            if delta:
                removed = Count.literal(delta)
                rest = subtract(self.c("width"), removed)
                suffix = Count.product(rest, self.c("spacing"))
                suffix.add(self.c("after"))
                self.apply_leaf(removed, self.c("before"), suffix)
                shift = Count.product(removed, self.c("spacing"))
                shift.add(self.c("before"))
                self.save(shift, "before")
                shift = None
                self.save(rest, "width")
                rest = None
            self.save(columns, "columns")
            columns = None
            divisor = Count.literal(self.binding.families * self.binding.cover.size)
            unused, remainder = divide(self.c("rows"), divisor)
            need(remainder.zero() and not unused.zero(), "complete fresh row divisor at node")
            self.save(unused, "unused")
            unused = None
            local_bits = Count.product(self.c("prefixes"), self.c("unused"))
            local_extent = Count.product(local_bits, self.c("row_bits"))
            local_bits.close()
            divisor2 = Count(self.c("component_bits"))
            divisor2.multiply_small(2)
            gaussian_count, rem2 = divide(local_extent, divisor2)
            try:
                need(rem2.zero(), "complete Gaussian local packet")
                self.save(gaussian_count, "gaussians")
                gaussian_count = None
            finally:
                if gaussian_count is not None:
                    gaussian_count.close()
                local_extent.close()
                divisor2.close()
                rem2.close()
            self.event = self.subgroup = self.cover_index = self.pc = 0
            self.group = None
            self.mode = "group"
        finally:
            for value in (dimension, test, extent, columns, removed, rest, suffix, shift, divisor, unused, remainder):
                if value is not None:
                    value.close()
