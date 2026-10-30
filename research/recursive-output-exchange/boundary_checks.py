"""Exact handoff tariff, reuse and rejection controls on literal fixed tapes."""
from types import SimpleNamespace
from unittest.mock import patch

import bindings
bindings.activate()
import exchange
from directory import append_tape
from ordinary import transfer
from records import Tape
from role_parking import BODY
from scratch_pool import ScratchPool
from words import BLANK, LEFT, need


def body(t):
    t=getattr(t,'physical',t)
    return bytes(t.cells[1:]).rstrip(bytes([BLANK]))


def one(data,optimized):
    inner,outer=ScratchPool(3),ScratchPool(3)
    owner=SimpleNamespace(output=Tape(),closed=False)
    result=inner.acquire()
    for symbol in data:result.append(symbol)
    result.rewind()
    inventory=[owner.output]+list(inner.tapes)+list(outer.tapes)
    counts=dict(reads=0,writes=0,moves=0)
    methods=dict(reads=Tape.read,writes=Tape.write,moves=Tape.step)
    def wrap(name):
        def call(*a,**kw):counts[name]+=1;return methods[name](*a,**kw)
        return call
    with patch.object(Tape,'read',wrap('reads')),patch.object(Tape,'write',wrap('writes')),patch.object(Tape,'step',wrap('moves')):
        if optimized:exchange.publish(owner,result,owner.output)
        else:transfer(result,owner.output)
        result.clear();owner.closed=True
        if optimized:output=exchange.adopt(owner,outer)
        else:
            output=outer.acquire()
            append_tape(owner.output,output);output.rewind();owner.output.clear()
    need(body(output)==bytes(data) and output.head==1,'literal completed handoff body')
    need(owner.output.read()==BLANK,'native port reusable')
    after=[owner.output]+list(inner.tapes)+list(outer.tapes)
    need(sorted(map(id,after))==sorted(map(id,inventory)) and len(set(map(id,after)))==7,
         'literal fixed role permutation')
    # Reacquire the ended inner slot; stale cleanup must not erase its new owner.
    dirty=inner.acquire();dirty.append(1);dirty.append(0);dirty.rewind()
    before=body(dirty);result.clear()
    need(body(dirty)==before and dirty.active,'stale cleanup preserves reused slot')
    try:result.read()
    except ValueError:pass
    else:raise ValueError('ended lease read accepted')
    dirty.clear();output.clear();inner.empty();outer.empty()
    return counts


def rejects(function,message):
    try:function()
    except ValueError as error:
        need(message in str(error),'unexpected control failure: '+str(error));return
    raise ValueError('negative control accepted: '+message)


def controls():
    pool=ScratchPool(3);lease=pool.acquire();lease.append(1);lease.rewind()
    owner=SimpleNamespace(output=Tape(),closed=False)
    rejects(lambda:exchange.adopt(owner,pool),'completed ordinary')
    rejects(lambda:exchange.exchange(owner,owner.output),'physical scratch lease')
    old=owner.output;owner.output=lease.physical
    rejects(lambda:exchange.exchange(owner,lease),'disjoint output')
    owner.output=old;owner.output.append(1);owner.output.rewind()
    rejects(lambda:exchange.publish(owner,lease,owner.output),'empty ordinary publication')
    owner.output.clear();lease.physical.step(1)
    snapshot=(tuple(pool.tapes),lease.physical,owner.output,lease.head)
    rejects(lambda:exchange.exchange(owner,lease),'completed origin')
    need(snapshot==(tuple(pool.tapes),lease.physical,owner.output,lease.head),'failed origin check leaves bindings/head unchanged')
    lease.rewind();lease.clear()
    rejects(lambda:exchange.exchange(owner,lease),'live scratch lease')
    # Retain the original transfer rejection for a LEFT marker inside the body.
    malformed=pool.acquire();malformed.append(1);malformed.append(LEFT)
    malformed.physical.head=1  # Deliberate malformed fixture, not a runtime selector.
    rejects(lambda:exchange.publish(owner,malformed,owner.output),'dense transferred body')
    # Invalid input has no successful-cleanup contract; restore the fixture explicitly.
    malformed.physical.cells[2]=0;malformed.physical.head=1;malformed.clear();pool.empty()
    return 7


def run():
    rows=[]
    for n in (0,1,2,3,7,31,64,257):
        data=[BODY[i%len(BODY)] for i in range(n)]
        a=one(data,False);b=one(data,True)
        delta={k:a[k]-b[k] for k in a}
        need(delta==dict(reads=10*n+5,writes=4*n,moves=8*n+8),'exact retained-check handoff saving')
        rows.append(dict(length=n,before=a,after=b,saved=sum(delta.values())))
    return dict(cases=rows,controls=controls(),tariff='22*V+13',additional_tapes=0,
                additional_numerical_words=0)
