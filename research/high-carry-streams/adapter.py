"""Opt-in adapter. Execute lifecycle retained from Jose Manuel, PR2915.

Apache-2.0. The only changed dispatch is the bounded carry kernel.
"""
import bindings
bindings.activate()
from cardinal_counts import Count
from high_route import apply, extents
from routes import copy_rows
from session import initialize_marker
from words import BLANK, Ring, need
from stage import Adapter
from rotation import translated


def apply_carry(source, operation, route, ring, modulus, fibre, adapter, factory):
    if operation[0] != "translate" or operation[2] == 1:
        return apply(source, operation, route, ring, modulus, fibre, adapter, factory)
    before, suffix = extents(modulus, fibre, route.dimension, operation[1])
    try:
        return translated(source, ring, before, suffix, operation[2], factory)
    finally:
        before.close()
        suffix.close()


def execute(source, route, context, fibre, adapter, factory):
    need((route.q, route.dimension) == (context.q, context.dimension), "route/context binding")
    operations = adapter.registry.compile(route)
    current = factory()
    source.rewind()
    ring = modulus_word = None
    modulus = Count(context.cap)
    bank = adapter.high_bank
    try:
        copy_rows(source, current, context.highs, fibre)
        need(source.read() == BLANK, "complete source high cube")
        source.rewind()
        current.rewind()
        if context.raw.compare(context.cap, context.ring.one) > 0:
            for word in (*bank.words, bank.template):
                initialize_marker(word.tape)
            bank.prepare(modulus)
            modulus_word = bank.load(modulus)
            ring = Ring(modulus_word)
            for operation in operations:
                following = apply_carry(current, operation, route, ring, modulus, fibre, adapter, factory)
                current.clear()
                current = following
        result, current = current, None
        return result
    finally:
        source.rewind()
        if current is not None:
            current.clear()
        if ring is not None:
            ring.close()
            bank.free(modulus_word)
            bank.erase_owned()
        modulus.close()


class CarryAdapter(Adapter):
    def route_cube(self, source, route, context, fibre, factory=None):
        need(not self.in_base and self.scope is not None, "successor route stage")
        result = execute(source, route, context, fibre, self,
                         self.scope.acquire if factory is None else factory)
        self.calls["cubes"] += 1
        return result
