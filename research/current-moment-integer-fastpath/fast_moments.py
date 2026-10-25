#!/usr/bin/env python3
"""Opt-in, output-identical integer Taylor kernel for the frozen current engine.

Preserves Chris R/Clear1nsight's logarithms, 40-term exponential, rational
remainder and every outward rounding. Integer recurrence is classical; see
the prior retained ceiling fast path PR2552. Joseph Anglada with substantial
OpenAI Codex assistance. Apache-2.0. No mathematical acceptance gate changed.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import types

SOURCE = Path(__file__).resolve().parent / 'inputs' / 'exact_moments.py'
SOURCE_SHA256 = 'cf7439c9eb4095224126dd5eefc9f1c5dfe1968d6e8eca5b87d4a3897841182d'


def taylor_parts(p, q):
    """Unreduced S_40 and S_40 + R_40 for 0 <= p/q <= 1/64."""
    power = numerator = denominator = 1
    for j in range(1, 41):
        power *= p
        numerator = j * q * numerator + power
        denominator *= j * q
    factor = 41 * (42 * q - p)
    return (numerator, denominator,
            numerator * factor + power * p * 42, denominator * factor)


def load_engine(fast=True):
    raw = SOURCE.read_bytes()
    if sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('frozen moment source changed')
    module = types.ModuleType('authenticated_moments')
    module.__file__ = str(SOURCE)
    exec(compile(raw, str(SOURCE), 'exec', dont_inherit=True, optimize=0), module.__dict__)
    if fast:
        install(module)
    return module


def install(module):
    original = module.expbound
    precision = module.PRECISION
    if precision != 10**65:
        raise ValueError('unsupported rounding grid')

    def expbound(value):
        # Keep the predecessor's behavior for values outside its internal
        # exact-Fraction interface; discovery/acceptance uses Fraction only.
        if type(value) is not Fraction:
            return original(value)
        if value < 0:
            lo, hi = module.expbound(-value)
            return module.floorq(1 / hi), module.ceilq(1 / lo)
        squarings = 0
        while value > Fraction(1, 64):
            value /= 2
            squarings += 1
        p, q = value.numerator, value.denominator
        # T_40 = power/denominator, S_40 = numerator/denominator.
        # Original remainder T_40*x/41/(1-x/42) has denominator
        # denominator*41*(42*q-p), after cancelling its one factor q.
        numerator, denominator, upper_num, upper_den = taylor_parts(p, q)
        lo = numerator * precision // denominator
        hi = (upper_num * precision + upper_den - 1) // upper_den
        for _ in range(squarings):
            lo = lo * lo // precision
            hi = (hi * hi + precision - 1) // precision
        return Fraction(lo, precision), Fraction(hi, precision)

    module.expbound = expbound
    # A fresh loaded module has empty caches. Explicit installation on an
    # existing engine also invalidates caches before any comparisons.
    module.power.cache_clear()
    module.logarithm.cache_clear()
    return module
