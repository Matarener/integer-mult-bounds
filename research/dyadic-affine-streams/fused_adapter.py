"""Opt-in affine fusion; lifecycle retained from PR2915 and PR3343."""
import fused_sources
fused_sources.activate()
from adapter import CarryAdapter, apply_carry
from cardinal_counts import Count
from high_route import extents
from routes import copy_rows
from session import initialize_marker
from words import BLANK, Ring, need
from affine import transformed


def fuse(operations):
    """Fuse only contiguous, identical-field dyadic factors. No reordering."""
    result = []
    i = 0
    while i < len(operations):
        operation = operations[i]
        kind, target = operation[:2]
        if kind == 'double':
            end = i+1
            if end < len(operations) and operations[end] == ('double', target):
                end += 1
            multiplier = 1 << (end-i)
            amount = 0
            if end < len(operations) and operations[end][:2] == ('translate', target):
                amount = operations[end][2]
                end += 1
            if amount:
                result.append(('affine', target, multiplier, amount, False))
                i = end
                continue
        elif kind == 'translate':
            start = i+1
            end = start
            while end < min(start+2, len(operations)) and operations[end] == ('half', target):
                end += 1
            if end > start and end-i > 1:
                amount = -operation[2]
                result.append(('affine', target, 1 << (end-start), amount, True))
                i = end
                continue
        result.append(operation)
        i += 1
    return tuple(result)


def execute(source, route, context, fibre, adapter, factory):
    need((route.q, route.dimension) == (context.q, context.dimension), 'route/context binding')
    operations = fuse(adapter.registry.compile(route))
    current = factory()
    source.rewind()
    ring = modulus_word = None
    modulus = Count(context.cap)
    bank = adapter.high_bank
    try:
        copy_rows(source, current, context.highs, fibre)
        need(source.read() == BLANK, 'complete source high cube')
        source.rewind()
        current.rewind()
        if context.raw.compare(context.cap, context.ring.one) > 0:
            for word in (*bank.words, bank.template):
                initialize_marker(word.tape)
            bank.prepare(modulus)
            modulus_word = bank.load(modulus)
            ring = Ring(modulus_word)
            for operation in operations:
                if operation[0] == 'affine':
                    before, suffix = extents(modulus, fibre, route.dimension, operation[1])
                    try:
                        following = transformed(current, ring, before, suffix, *operation[2:4],
                                                factory, operation[4])
                    finally:
                        before.close()
                        suffix.close()
                else:
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


class AffineAdapter(CarryAdapter):
    def route_cube(self, source, route, context, fibre, factory=None):
        need(not self.in_base and self.scope is not None, 'successor route stage')
        result = execute(source, route, context, fibre, self,
                         self.scope.acquire if factory is None else factory)
        self.calls['cubes'] += 1
        return result
