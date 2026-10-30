"""Same complete source harness before/after, with dirty leases and tape I/O."""
from fractions import Fraction as F
import importlib.util
from time import perf_counter
from unittest.mock import patch

import bindings
bindings.activate()
import exchange
from words import need


def retained():
    path=bindings.ROOT/'research/selected-bit-fast-primitives/check_routes.py'
    spec=importlib.util.spec_from_file_location('exchange_retained_routes',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def one(case,optimized):
    old=retained()
    from records import Tape
    class DirtyPool(old.ScratchPool):
        def __init__(self,n):
            super().__init__(n);self.borrowed=[]
            for i in range(3):
                lease=self.acquire()
                for bit in (i%2,1,0,1):lease.append(bit)
                lease.rewind();lease.step(1)
                self.borrowed.append((lease,bytes(lease.physical.cells),lease.physical.head))
        def empty(self):
            for lease,data,head in self.borrowed:
                need(bytes(lease.physical.cells)==data and lease.physical.head==head,'dirty parent lease preserved')
                need(lease.owned() is self.tapes[lease.slot],'dirty lease binding preserved')
                lease.clear()
            self.borrowed=[];super().empty()
    audits=[]
    class AuditedAdapter(exchange.ExchangeAdapter if optimized else old.Adapter):
        def swap(self,*args):
            pools=(self.scope.base,self.native.pool)
            before=[self.native.output]+[t for p in pools for t in p.tapes]
            need(len(set(map(id,before)))==len(before),'initial physical roles disjoint')
            result=super().swap(*args)
            after=[self.native.output]+[t for p in pools for t in p.tapes]
            need(sorted(map(id,before))==sorted(map(id,after)),'constant physical role inventory')
            for pool in pools:
                for slot,lease in pool.live.items():
                    need(lease.owned() is pool.tapes[slot],'all live lease bindings')
            need(result.physical is not self.native.output,'distinct returned parent output')
            audits.append(1)
            return result
    counts=dict(reads=0,writes=0,moves=0);elapsed=[]
    original=old.route_packet
    def route(*args,**kwargs):
        methods=dict(reads=Tape.read,writes=Tape.write,moves=Tape.step)
        def wrapper(name):
            def call(*a,**kw):
                counts[name]+=1
                return methods[name](*a,**kw)
            return call
        with patch.object(Tape,'read',wrapper('reads')),patch.object(Tape,'write',wrapper('writes')),patch.object(Tape,'step',wrapper('moves')):
            start=perf_counter();result=original(*args,**kwargs);elapsed.append(perf_counter()-start)
            return result
    with patch.object(old,'ScratchPool',DirtyPool),patch.object(old,'Adapter',AuditedAdapter),patch.object(old,'route_packet',route):
        result=old.one_case(**case)
    need(len(audits)==result['calls']['swaps'],'all native boundaries audited')
    result.update(physical=counts,total=sum(counts.values()),dirty_roles=3,
                  inventory_audits=len(audits))
    return result,sum(elapsed)


def cases():
    mixed=(("add",0,1,F(1,2)),("scale",1,1,F(-2)),("swap",0,1,F(1)))
    return [dict(q=3,width=2,low=((1,2),(2,2)),word=(("swap",0,1,F(1)),),old_prefixes=2,fibre_value=3),
            dict(q=3,width=2,low=((2,1),(1,1)),word=mixed,old_prefixes=2,fibre_value=3),
            dict(q=5,width=2,low=((1,4),(2,1)),word=mixed,old_prefixes=1,fibre_value=1),
            dict(q=3,width=1,low=((1,2),(2,2)),word=mixed,old_prefixes=2,fibre_value=3)]


def run():
    rows=[]
    for case in cases():
        before,_=one(case,False);after,_=one(case,True)
        need(before['calls']==after['calls'],'identical recursive child counts')
        need(after['total']<=before['total'],'nonincreasing complete fixture traffic')
        rows.append(dict(before=before,after=after))
    need(rows[0]['after']['total']<rows[0]['before']['total'],'strict completed-handoff saving')
    return rows
