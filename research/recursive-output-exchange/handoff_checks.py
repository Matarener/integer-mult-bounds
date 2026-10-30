"""Actual fitted B1 under C1, complete columns and noncircular bindings.

Harness follows Jose Manuel's retained check_handoff; adds paired measurements
and immutable physical-inventory checks for the new role interface.
"""
from time import perf_counter
from unittest.mock import patch

import bindings
bindings.activate()
import exchange
from cardinal_counts import Count
from check_engine import fixture_engine, toy_plan
from check_support import no_decode
from compile_routes import Registry
from physical_words import PhysicalArena, PhysicalWord
from provenance import Provenance
from records import Tape
import routes
from scratch_pool import ScratchPool
from stage import Adapter, StagePool
import stream_runner
from words import BLANK, Ring, Word, need


def body(tape):
    tape=getattr(tape,'physical',tape)
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def one(optimized):
    native=fixture_engine();entered=[]
    pool=ScratchPool(260)
    adapter=(exchange.ExchangeAdapter if optimized else Adapter)(native,Registry(2),capacity=64)
    scope=StagePool(pool,adapter)
    def fitted(payload,original,prefixes,gap,suffix):
        need(adapter.in_base and stream_runner.atom_swap is scope.original_swap and
             routes.route_cube is scope.original_cube,'both preceding bindings at native entry')
        entered.append('base-entry')
        return native.execute_plan(payload,original,prefixes,gap,suffix,toy_plan)
    native.run=fitted
    def observe(stage,_payload,_returned):
        need(stream_runner.atom_swap is scope.original_swap and routes.route_cube is scope.original_cube,
             'C0 roots retain A0 bindings')
        entered.append(stage)
    native.observe=observe
    bank=PhysicalArena(64);maximum,one=Count.literal(32),Count.literal(1)
    bank.prepare(maximum);modulus=bank.load(maximum);ring=Ring(modulus)
    source=Tape()
    for i in range(1024):source.append((i*13 ^ i//7 ^ 5)&1)
    source.rewind();initial=body(source)
    observer=Provenance(1024);observer.mark(source)
    saved={slot:(word,bytes(word.cells),word.head) for slot,word in enumerate(bank.words) if slot in bank.live}
    physical=[native.output]+list(native.pool.tapes)+list(pool.tapes)
    counts=dict(reads=0,writes=0,moves=0)
    def wrap(name):
        def call(*a,**kw):counts[name]+=1;return methods[name](*a,**kw)
        return call
    def forbidden(*a,**kw):raise ValueError('fixture-only operation inside completed handoff')
    with no_decode(),observer.installed(),patch.object(Word,'__init__',forbidden),patch.object(PhysicalWord,'inspect',forbidden),scope.install():
        methods=dict(reads=Tape.read,writes=Tape.write,moves=Tape.step)
        operands=[one.marginal() for _ in range(3)]
        try:
            with patch.object(Tape,'read',wrap('reads')),patch.object(Tape,'write',wrap('writes')),patch.object(Tape,'step',wrap('moves')):
                start=perf_counter();output=stream_runner.atom_swap(source,ring,2,*operands);elapsed=perf_counter()-start
        finally:
            for value in operands:value.close()
        expected=bytearray(1024);masks=[0]*1024
        for i,bit in enumerate(initial):
            a,b=divmod(i,32);expected[b*32+a]=bit;masks[b*32+a]=1<<i
        need(body(output)==expected and observer.masks(output.physical,1024)==tuple(masks),
             'all complete fitted source columns')
        need(body(source)==initial and source.head==output.head==1,'preserved source and heads')
        need(saved=={slot:(word,bytes(word.cells),word.head) for slot,word in enumerate(bank.words) if slot in bank.live},
             'parent numerical values and heads preserved')
        after=[native.output]+list(native.pool.tapes)+list(pool.tapes)
        need(len(set(map(id,after)))==len(after) and sorted(map(id,after))==sorted(map(id,physical)),
             'fitted fixed-role inventory')
        output.clear();pool.empty()
    adapter.close()
    need(entered==['base-entry','before','after','before','after'],'two genuine fitted roots')
    need(native.closed and all(x==BLANK for x in native.output.cells),'native empty for next call')
    result=dict(columns=1024,trace=entered,preceding_roots=native.runtime.completed_roots,
                physical=counts,total=sum(counts.values()),calls=adapter.calls,parent_peak=pool.peak)
    ring.close();bank.free(modulus);bank.erase_owned();source.clear();maximum.close();one.close()
    return result,elapsed


def run():
    before,_=one(False);after,_=one(True)
    need(before['calls']==after['calls'] and before['trace']==after['trace'],'unchanged complete fitted children')
    need(after['total']<before['total'],'fitted boundary saves physical traffic')
    return dict(before=before,after=after)
