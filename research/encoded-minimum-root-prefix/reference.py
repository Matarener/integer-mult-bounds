#!/usr/bin/env python3
"""Exact reference compiler for the root row prefix.

This uses host integers. It does not execute physical Count or payload code.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from functools import lru_cache


def need(ok, message):
    if not ok:
        raise ValueError(message)


def floor_root(n, degree):
    need(type(n) is int and n >= 0 and type(degree) is int and degree > 0, 'root domain')
    lo, hi = 0, 1 << ((n.bit_length()+degree-1)//degree)
    while lo+1 < hi:
        mid = (lo+hi)//2
        if mid**degree <= n:
            lo = mid
        else:
            hi = mid
    return hi if hi**degree <= n else lo


def depth(width, threshold, dimension=73, maximum_rank=48):
    need(type(width) is int and width >= 0, 'nonnegative width')
    need(type(threshold) is int and threshold >= dimension > maximum_rank > 0, 'depth domain')
    result = 0
    while width >= threshold:
        width = maximum_rank*(width//dimension)
        result += 1
    return result


class PrefixCompiler:
    def __init__(self, divisor, threshold, dimension=73, maximum_rank=48):
        need(type(divisor) is int and divisor > 1, 'positive nontrivial divisor')
        need(threshold >= dimension > maximum_rank > 0, 'compiler domain')
        self.divisor = divisor
        self.threshold = threshold
        self.dimension = dimension
        self.maximum_rank = maximum_rank

    def active_depth(self, width):
        return depth(width, self.threshold, self.dimension, self.maximum_rank)

    @lru_cache(maxsize=256)
    def stock_bits(self, levels):
        return (self.divisor**levels).bit_length()-1

    def feasible(self, remaining, spacing, prefix):
        need(0 <= prefix < remaining and spacing >= 1, 'positive core')
        levels = self.active_depth(remaining-prefix)
        return self.stock_bits(levels) <= spacing*prefix

    def compile(self, remaining, spacing):
        need(type(remaining) is int and remaining >= 1 and type(spacing) is int and spacing >= 1, 'prefix domain')
        # This known feasible upper bound avoids a search through the root width.
        conservative = self.active_depth(remaining)*(self.divisor-1).bit_length()
        upper = min(remaining-1, (conservative+spacing-1)//spacing)
        lower = -1
        while upper-lower > 1:
            middle = (lower+upper)//2
            if self.feasible(remaining,spacing,middle):
                upper = middle
            else:
                lower = middle
        levels = self.active_depth(remaining-upper)
        need(self.feasible(remaining,spacing,upper), 'feasible minimum')
        need(upper == 0 or not self.feasible(remaining,spacing,upper-1), 'strict minimality')
        return {'q0':upper, 'depth':levels, 'stock_floor_log2':self.stock_bits(levels),
                'row_address_bits':spacing*upper,
                'previous_stock_floor_log2':None if upper==0 else self.stock_bits(self.active_depth(remaining-upper+1))}
