"""Independent modular column oracle and complete physical-I/O measurement."""
from time import perf_counter
from unittest.mock import patch
import random

import bindings
bindings.activate()
from cardinal_counts import Count
from check_support import no_decode
import kernels
from physical_words import PhysicalArena, PhysicalWord
from provenance import Provenance
from records import Tape
from scratch_pool import ScratchPool
from session import sealed_constructors
from words import BLANK, Ring, Word, need
import rotation


def body(tape):
    physical = getattr(tape, "physical", tape)
    return bytes(physical.cells[1:]).rstrip(bytes([BLANK]))


def one_case(q, b, s, amount, optimized, capacity=40, extra_bit=False, wrong_sign=False):
    bank, pool = PhysicalArena(64), ScratchPool(capacity)
    maximum = Count.literal(q)
    bank.prepare(maximum)
    modulus = bank.load(maximum)
    ring = Ring(modulus)
    before, suffix = Count.literal(b), Count.literal(s)
    source = Tape()
    rng = random.Random(6 + 1000*q + 100*b + 10*s + amount)
    length = b*q*s
    for _ in range(length + int(extra_bit)):
        source.append(rng.randrange(2))
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
    count_bytes = tuple(bytes(c.tape.cells) for c in (before,suffix))
    source_bytes = bytes(source.cells)
    numerical = tuple(bytes(word.tape.cells) for word in (*bank.words, bank.template))
    counts = dict(reads=0, writes=0, moves=0)
    def wrap(key):
        def observed(*args, **kw):
            counts[key] += 1
            return methods[key](*args, **kw)
        return observed
    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture-only operation in physical carry")
    with no_decode(), sealed_constructors(), pool.install(), observer.installed(), \
            patch.object(Word, "__init__", forbidden), patch.object(PhysicalWord, "inspect", forbidden):
        methods = {"reads":Tape.read, "writes":Tape.write, "moves":Tape.step}
        with patch.object(Tape,"read",wrap("reads")), patch.object(Tape,"write",wrap("writes")), \
                patch.object(Tape,"step",wrap("moves")):
            start = perf_counter()
            if optimized and amount != 1:
                output = rotation.translated(source, ring, before, suffix,
                                             -amount if wrong_sign else amount, pool.acquire)
            else:
                output = kernels.translated(source, ring, 3, before, suffix, amount)
            seconds = perf_counter()-start
        expected, masks = bytearray(length), [0]*length
        for origin, bit in enumerate(initial[:length]):
            block, tail = divmod(origin, s)
            prefix, x = divmod(block, q)
            target = (prefix*q + (x+amount)%q)*s + tail
            expected[target], masks[target] = bit, 1 << origin
        need(body(output) == expected and observer.masks(output.physical,length) == tuple(masks),
             "complete modular carry and independent input columns")
        need(output is not source and pool.live.get(output.slot) is output,
             "distinct owned carry output")
        need(bytes(source.cells) == source_bytes and source.head == output.head == 1,
             "borrowed source bytes and heads restored")
        need(tuple(bytes(c.tape.cells) for c in (before,suffix)) == count_bytes
             and before.tape.head == suffix.tape.head == 1, "borrowed cardinalities preserved")
        if optimized and amount != 1:
            need(tuple(bytes(word.tape.cells) for word in (*bank.words,bank.template)) == numerical,
                 "no numerical bank mutation")
        peak = pool.peak - len(occupied)
        need(len(pool.live) == len(occupied)+1, "only output lease remains")
        output.clear()
        for lease, data, head in occupied:
            need(bytes(lease.physical.cells) == data and lease.physical.head == head,
                 "occupied dirty bytes and heads restored")
            need(pool.live.get(lease.slot) is lease, "occupied ownership preserved")
            lease.clear()
        pool.empty()
    ring.close()
    bank.free(modulus)
    bank.erase_owned()
    source.clear()
    for count in (maximum,before,suffix):count.close()
    return dict(q=q,b=b,s=s,amount=amount,columns=length,physical=counts,
                total=sum(counts.values()),scratch=peak,dirty=3), seconds


def cases():
    amounts = (-4,-3,-2,-1,1,2,3,4)
    return [(q,b,s,a) for q in (3,5) for b,s in ((1,1),(2,1),(1,3),(2,3)) for a in amounts] + \
           [(q,2,3,a) for q in (7,9,25,81) for a in amounts]


def run():
    rows=[]
    for case in cases():
        before,_=one_case(*case,False)
        after,_=one_case(*case,True)
        need(before['columns']==after['columns'],'same complete domain')
        rows.append(dict(before=before,after=after))
    return rows
