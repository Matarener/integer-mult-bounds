# SPDX-License-Identifier: Apache-2.0
"""Minimum prefixes on the retained physical Count interface.

RootPlan.compute is adapted from Jose Manuel's physical-complex-controller.
New search and integration: Ali Romman with substantial OpenAI Codex assistance.
"""
import retained
retained.activate()
from cardinal_counts import Count, positive
from compact_counts import power_two
from encoded import atom_width, compare, subtract
from machine import copy_symbols
from root_plan import RootPlan, ceil_divide, ceil_log2, floor_power
from session import sealed_constructors
from words import RIGHT, need


def floor_log2(value):
    positive(value)
    digits=Count.literal(0)
    one=Count.literal(1)
    value.rewind()
    try:
        while value.read()!=RIGHT:
            need(value.read() in (0,1),'binary stock digit')
            digits.increment()
            value.step(1)
        return subtract(digits,one)
    finally:
        value.rewind();digits.close();one.close()


def reached_profile(width,threshold,dimension,maximum_rank,divisor):
    current=Count(width)
    depth=Count.literal(0)
    stock=Count.literal(1)
    try:
        while compare(current,threshold)>=0:
            current.divide_small(dimension)
            if maximum_rank>1:current.multiply_small(maximum_rank)
            depth.increment();stock.multiply_small(divisor)
        return depth,stock
    except BaseException:
        depth.close();stock.close();raise
    finally:
        current.close()


def minimum_prefix(remaining,spacing,threshold,dimension,maximum_rank,divisor):
    """Return owned q, reached depth and exact stock. Borrow all input Counts."""
    need(type(dimension) is int and type(maximum_rank) is int and type(divisor) is int
         and 1<=maximum_rank<dimension<=73 and divisor>1,'fixed prefix constants')
    positive(remaining);positive(spacing)
    one=Count.literal(1);bound=None;depth=None;stock=None;upper=None;lower=None;last=None;mid=None
    dimension_count=Count.literal(dimension)
    try:
        need(compare(threshold,dimension_count)>=0,'global cutoff at least dimension')
        depth,stock=reached_profile(remaining,threshold,dimension,maximum_rank,divisor)
        bound=Count(depth)
        factor=(divisor-1).bit_length()
        if factor>1:bound.multiply_small(factor)
        upper=ceil_divide(bound,spacing)
        depth.close();depth=None;stock.close();stock=None;bound.close();bound=None
        last=subtract(remaining,one)
        if compare(upper,last)>0:
            upper.close();upper=Count(last)
        lower=Count.literal(0)
        while compare(lower,upper)<0:
            mid=Count(lower);mid.add(upper);mid.divide_small(2)
            core=d=s=bits=paid=None
            try:
                core=subtract(remaining,mid)
                d,s=reached_profile(core,threshold,dimension,maximum_rank,divisor)
                bits=floor_log2(s);paid=Count.product(spacing,mid)
                accepted=compare(bits,paid)<=0
            finally:
                for value in (core,d,s,bits,paid):
                    if value is not None:value.close()
            if accepted:
                upper.close();upper=mid;mid=None
            else:
                mid.increment();lower.close();lower=mid;mid=None
        core=subtract(remaining,lower)
        try:
            depth,stock=reached_profile(core,threshold,dimension,maximum_rank,divisor)
        finally:core.close()
        answer=Count(lower)
        result=(answer,depth,stock);depth=stock=None
        return result
    finally:
        for value in (one,bound,depth,stock,upper,lower,last,mid,dimension_count):
            if value is not None:value.close()


class MinimumRootPlan(RootPlan):
    def parameters(self,precision):
        """Return owned d, K, G, H and delta for the source parameter law."""
        owned=[];logarithm=None
        try:
            d=floor_power(precision,997,1000);owned.append(d)
            K=floor_power(d,1,500);owned.append(K)
            logarithm=ceil_log2(precision)
            G=Count(logarithm);owned.append(G);G.multiply_small(4)
            for _ in range(6):G.increment()
            H=Count.product(d,G);owned.append(H)
            delta=Count(d);owned.append(delta)
            if self.guard_exponent:delta.multiply_small(1<<self.guard_exponent)
            return tuple(owned)
        except BaseException:
            for value in reversed(owned):value.close()
            raise
        finally:
            if logarithm is not None:logarithm.close()

    def compute(self, precision, selected, left, right, coefficients, outer_rows, residue):
        need(self.closed and not self.pool.live, "closed root planning entry")
        self.clear()
        self.closed = False
        inputs = dict(precision=precision, selected=selected, left=left, right=right,
                      coefficients=coefficients, outer_rows=outer_rows, residue=residue)
        need(all(isinstance(v, Count) for v in inputs.values()), "encoded root inputs")
        for name, value in inputs.items():
            copy_symbols(value.tape, self.roles[name])
        owned = []  # A fixed number of compiled expression results, independent of input widths.

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
                parameters = self.parameters(precision)
                for value in parameters:
                    keep(value)
                d, K, G, H, delta = parameters
                for name, value in zip(("d", "K", "G", "H", "delta"), parameters):
                    save(name, value)
                need(compare(selected, d) <= 0, "selected width within root domain")
                need(compare(residue, K) < 0, "selected root residue")
                qF = save("qF", keep(ceil_divide(scaled(H, 2), K)))
                qB = save("qB", keep(ceil_divide(H, K)))
                margins = plus(qF, qB)
                if compare(selected, margins) > 0:
                    remaining = keep(subtract(selected, margins))
                    threshold = keep(atom_width(d, 1, 1000))
                    dimension_count = literal(self.dimension)
                    if compare(threshold, dimension_count) < 0:
                        threshold = dimension_count
                    prefix, exact_depth, exact_stock = minimum_prefix(
                        remaining, K, threshold, self.dimension, self.maximum_rank, self.level_divisor)
                    q0 = save("q0", keep(prefix))
                    depth = save("depth", keep(exact_depth))
                    stock = keep(exact_stock)
                else:
                    q0 = save("q0", literal(0))
                    depth = save("depth", literal(0))
                    stock = literal(1)
                Q0 = save("Q0", plus(q0, qF, qB))
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
