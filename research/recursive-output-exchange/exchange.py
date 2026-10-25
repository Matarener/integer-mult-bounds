"""Completed output handoffs by a finite permutation of fixed tape roles.

No numerical data, tape cells or host head offsets determine a role exchange.
The finite-role interpretation and recursive cost are stated in PROOF.md.
Tekalign, substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager

import bindings
bindings.activate()
from cardinal_counts import Count
from cardinality import radix_power
import ordinary
from role_parking import BODY
from scratch_pool import Lease
from session import borrowed_count, borrowed_tape
from stage import Adapter
from words import BLANK, LEFT, need


def exchange(owner, lease):
    """Swap the physical role bindings of owner.output and one live lease.

The caller specifies which body is empty. Both roles must be at their origin;
all checks precede mutation. Lease identity and its pool slot stay unchanged.
"""
    need(isinstance(lease,Lease),'output exchange requires a physical scratch lease')
    empty_or_full=lease.owned()
    output=owner.output
    need(all(output is not tape for tape in lease.pool.tapes),'disjoint output and scratch inventory')
    need(lease.pool.tapes[lease.slot] is empty_or_full,'lease role binding')
    for tape in (output,empty_or_full):
        tape.step(-1)
        try:
            need(tape.read()==LEFT,'completed origin before role exchange')
        finally:
            tape.step(1)
    lease.pool.tapes=tuple(output if slot==lease.slot else tape
                           for slot,tape in enumerate(lease.pool.tapes))
    lease.physical=output
    owner.output=empty_or_full


def publish(owner, result, destination):
    """Completed owned result -> empty ordinary output, without payload transfer."""
    need(destination is owner.output,'named ordinary output role')
    need(destination.read()==BLANK,'empty ordinary publication port')
    # Retain transfer()'s dense-body rejection with one read-only scan.
    # Avoiding data movement must not silently drop this source check.
    result.rewind()
    try:
        symbol=result.read()
        while symbol!=BLANK:
            need(symbol in BODY,'dense transferred body')
            result.step(1)
            symbol=result.read()
    finally:
        result.rewind()
    exchange(owner,result)
    # The original execute_plan ends this now-empty lease with result.clear().


def adopt(owner, pool):
    """Completed ordinary output -> empty parent lease; caller later clears it."""
    need(owner.closed,'completed ordinary before parent adoption')
    result=pool.acquire()
    try:
        need(result.read()==BLANK,'empty parent adoption role')
        exchange(owner,result)
        return result
    except BaseException:
        result.clear()
        raise


@contextmanager
def publication(owner):
    """Opt in only this compiled Ordinary instance; restore the source binding."""
    original=ordinary.transfer
    def transfer(result,destination):
        if destination is owner.output:
            publish(owner,result,destination)
        else:
            original(result,destination)
    ordinary.transfer=transfer
    try:yield
    finally:ordinary.transfer=original


class ExchangeAdapter(Adapter):
    """PR2915 swap lifecycle with both completed output copies eliminated."""
    def swap(self,source,ring,q,before,middle,suffix):
        need(not self.in_base and self.scope is not None and q==self.q,
             'successor primitive cannot re-enter from its preceding stage')
        width=Count.literal(0)
        extents=[Count(value) for value in (before,middle,suffix)]
        try:
            for _ in radix_power(ring,q):width.increment()
            with publication(self.native), self.scope.suspended():
                returned=self.native.run(borrowed_tape(source),borrowed_count(width),
                                         *(borrowed_count(value) for value in extents))
            need(returned is self.native.output,'completed named ordinary output')
            result=adopt(self.native,self.scope)
            self.calls['swaps']+=1
            return result
        finally:
            width.close()
            for value in extents:value.close()
