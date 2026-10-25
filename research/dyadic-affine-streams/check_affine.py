"""Independent modular column oracle and complete physical tape observer."""
import random
from time import perf_counter
from unittest.mock import patch
import fused_sources
fused_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
import kernels
from physical_words import PhysicalArena, PhysicalWord
from provenance import Provenance
from records import Tape
from scratch_pool import ScratchPool
from session import sealed_constructors
from words import BLANK, Ring, Word, need
import affine
from rotation import translated


def body(tape):
    tape = getattr(tape, 'physical', tape)
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def incumbent(source, ring, before, suffix, multiplier, amount, factory, inverse):
    current = source
    try:
        if inverse and amount:
            current = translated(current, ring, before, suffix, -amount, factory) if -amount != 1 else \
                kernels.translated(current, ring, 3, before, suffix, 1)
        for _ in range({2: 1, 4: 2}[multiplier]):
            following = kernels.doubled(current, ring, before, suffix, factory, inverse)
            if current is not source:
                current.clear()
            current = following
        if not inverse and amount:
            following = translated(current, ring, before, suffix, amount, factory) if amount != 1 else \
                kernels.translated(current, ring, 3, before, suffix, 1)
            current.clear()
            current = following
        result, current = current, None
        return result
    finally:
        if current is not None and current is not source:
            current.clear()


def one_case(q, b, s, multiplier, amount, inverse, optimized, capacity=48,
             extra_bit=False, wrong_offset=False, zero_payload=False, wrong_direction=False):
    bank, pool = PhysicalArena(64), ScratchPool(capacity)
    maximum = Count.literal(q)
    bank.prepare(maximum)
    modulus = bank.load(maximum)
    ring = Ring(modulus)
    before, suffix = Count.literal(b), Count.literal(s)
    source = Tape()
    length = b*q*s
    rng = random.Random(1+1000*q+100*b+10*s+amount+multiplier)
    for _ in range(length+int(extra_bit)):
        source.append(0 if zero_payload else rng.randrange(2))
    source.rewind()
    initial = body(source)
    observer = Provenance(length)
    observer.mark(source)
    occupied = []
    for index in range(3):
        lease = pool.acquire()
        for bit in (1, index & 1, 0, 1):
            lease.append(bit)
        lease.rewind()
        lease.step(1)
        occupied.append((lease, bytes(lease.physical.cells), lease.physical.head))
    source_bytes = bytes(source.cells)
    count_bytes = tuple(bytes(c.tape.cells) for c in (before, suffix))
    numerical = tuple(bytes(w.tape.cells) for w in (*bank.words, bank.template))
    counts = dict(reads=0, writes=0, moves=0)

    def wrap(key):
        def call(*args, **kwargs):
            counts[key] += 1
            return methods[key](*args, **kwargs)
        return call

    def forbidden(*args, **kwargs):
        raise ValueError('fixture-only operation in affine stream')

    with no_decode(), sealed_constructors(), pool.install(), observer.installed(), \
         patch.object(Word, '__init__', forbidden), patch.object(PhysicalWord, 'inspect', forbidden):
        methods = dict(reads=Tape.read, writes=Tape.write, moves=Tape.step)
        with patch.object(Tape, 'read', wrap('reads')), patch.object(Tape, 'write', wrap('writes')), \
             patch.object(Tape, 'step', wrap('moves')):
            start = perf_counter()
            output = (affine.transformed if optimized else incumbent)(
                source, ring, before, suffix, multiplier, amount+int(wrong_offset), pool.acquire,
                not inverse if wrong_direction else inverse)
            seconds = perf_counter()-start
        expected, masks = bytearray(length), [0]*length
        for origin, bit in enumerate(initial[:length]):
            block, tail = divmod(origin, s)
            prefix, x = divmod(block, q)
            y = (pow(multiplier, -1, q)*(x-amount)) % q if inverse else (multiplier*x+amount) % q
            target = (prefix*q+y)*s+tail
            expected[target], masks[target] = bit, 1 << origin
        need(body(output) == expected and observer.masks(output.physical, length) == tuple(masks),
             'complete affine map and independent input columns')
        need(output is not source and pool.live.get(output.slot) is output, 'distinct owned affine output')
        need(bytes(source.cells) == source_bytes and source.head == output.head == 1, 'borrowed source restored')
        need(tuple(bytes(c.tape.cells) for c in (before, suffix)) == count_bytes
             and before.tape.head == suffix.tape.head == 1, 'borrowed cardinalities restored')
        if optimized:
            need(tuple(bytes(w.tape.cells) for w in (*bank.words, bank.template)) == numerical,
                 'no numerical bank mutation')
        peak = pool.peak-len(occupied)
        need(len(pool.live) == len(occupied)+1, 'only affine output remains')
        output.clear()
        for lease, data, head in occupied:
            need(bytes(lease.physical.cells) == data and lease.physical.head == head,
                 'occupied dirty bytes and heads preserved')
            need(pool.live.get(lease.slot) is lease, 'occupied dirty ownership preserved')
            lease.clear()
        pool.empty()
    ring.close()
    bank.free(modulus)
    bank.erase_owned()
    source.clear()
    for count in (maximum, before, suffix):
        count.close()
    return dict(q=q, b=b, s=s, multiplier=multiplier, amount=amount, inverse=inverse,
                columns=length, physical=counts, total=sum(counts.values()), scratch=peak, dirty=3), seconds


def cases():
    return [(q, b, s, a, c, inverse) for q in (3, 5, 7, 9, 17, 25, 81)
            for b, s in ((1, 1), (2, 3)) for a in (2, 4)
            for c in range(-4, 5) for inverse in (False, True)]


def run():
    result = []
    for case in cases():
        before, _ = one_case(*case, False)
        after, _ = one_case(*case, True)
        result.append(dict(before=before, after=after))
    return result
