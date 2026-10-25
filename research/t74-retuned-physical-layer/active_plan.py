"""Keep the retained encoded reservations, using the actual selected width."""

from active_sources import active
active()
from root_plan import (Count, Counter, RootPlan, ceil_divide, ceil_log2, coarse_depth,
                       compare, copy_symbols, floor_power, need, positive,
                       power_two, sealed_constructors, subtract)


class ActiveWidthPlan(RootPlan):
    def compute(self, precision, selected, left, right, coefficients, outer_rows, residue):
        need(self.closed and not self.pool.live, "closed root planning entry")
        self.clear()
        self.closed = False
        inputs = dict(precision=precision, selected=selected, left=left, right=right,
                      coefficients=coefficients, outer_rows=outer_rows, residue=residue)
        need(all(isinstance(v, Count) for v in inputs.values()), "encoded root inputs")
        for name, value in inputs.items():
            copy_symbols(value.tape, self.roles[name])
        owned = []

        def keep(value):
            owned.append(value)
            return value

        def literal(value):
            return keep(Count.literal(value))

        def plus(*values, constant=0):
            result = literal(constant)
            for value in values:
                result.add(value)
            return result

        def times(a, b):
            return keep(Count.product(a, b))

        def scaled(value, constant):
            if constant == 0:
                return literal(0)
            result = keep(Count(value))
            if constant > 1:
                result.multiply_small(constant)
            return result

        def save(name, value):
            copy_symbols(value.tape, self.roles[name])
            return value

        try:
            with sealed_constructors(), self.scope.installed():
                save("zero", literal(0))
                two = literal(2)
                need(compare(precision, two) >= 0, "root precision at least two")
                positive(coefficients)
                positive(outer_rows)
                limit = keep(floor_power(precision, 997, 1000))
                need(compare(selected, limit) <= 0, "selected width within root domain")
                d = save("d", literal(1) if selected.zero() else keep(Count(selected)))
                K = save("K", keep(floor_power(d, 1, 500)))
                need(compare(residue, K) < 0, "selected root residue")
                logarithm = keep(ceil_log2(precision))
                G = save("G", plus(scaled(logarithm, 4), constant=6))
                H = save("H", times(d, G))
                depth = save("depth", keep(coarse_depth(d, self.dimension, self.maximum_rank)))
                q0 = save("q0", scaled(depth, (self.level_divisor - 1).bit_length()))
                qF = save("qF", keep(ceil_divide(scaled(H, 2), K)))
                qB = save("qB", keep(ceil_divide(H, K)))
                Q0 = save("Q0", plus(q0, qF, qB))
                delta = save("delta", scaled(d, 1 << self.guard_exponent))
                save("input_bits", plus(precision, constant=2))
                work_bits = save("work_bits", plus(precision, scaled(delta, 2), constant=3))
                active_bits = times(selected, K)
                addresses = keep(power_two(plus(left, active_bits, right)))
                save("gaussians", times(times(addresses, coefficients), outer_rows))
                self.fast = compare(selected, Q0) > 0
                if self.fast:
                    save("core_width", keep(subtract(selected, Q0)))
                    save("core_front", keep(subtract(times(qF, K), scaled(H, 2))))
                    save("core_back", plus(keep(subtract(times(qB, K), H)), right))
                    row_axes = times(q0, K)
                    original_rows = save("original_rows", keep(power_two(row_axes)))
                    prefix_count = save("prefixes", times(outer_rows, keep(power_two(left))))
                    stock = literal(1)
                    repetitions = keep(Counter(depth))
                    while not repetitions.finished:
                        stock.multiply_small(self.level_divisor)
                        repetitions.decrement()
                    save("stock", stock)
                    multiples = keep(ceil_divide(original_rows, stock))
                    save("padded_rows", times(multiples, stock))
                    rectangle = plus(keep(subtract(active_bits, row_axes)), right)
                    row_gaussians = times(keep(power_two(rectangle)), coefficients)
                    save("row_bits", scaled(times(row_gaussians, work_bits), 2))
                else:
                    for name in ("core_width", "core_front", "core_back", "row_bits"):
                        save(name, literal(0))
                    for name in ("prefixes", "original_rows", "padded_rows", "stock"):
                        save(name, literal(1))
        except BaseException:
            for tape in self.roles.values():
                tape.clear()
            raise
        finally:
            for value in reversed(owned):
                value.close()
            self.pool.empty()
            self.closed = True
        return self
