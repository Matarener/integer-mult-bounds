#!/usr/bin/env python3
"""Check encoded prefix arithmetic and its complete reduced root caller."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def need(ok,message):
    if not ok:raise ValueError(message)


def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage']!='input':continue
        path=HERE/Path(row['path']).name
        raw=path.read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source hash: '+path.name)
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source blob: '+path.name)
    return sum(row['usage']=='input' for row in manifest['files'])


def integer(count):
    # The verifier alone decodes tapes. This read does not change a tape meter.
    from words import RIGHT
    physical=getattr(count.tape,'physical',count.tape)
    digits=list(physical.cells[1:])
    need(RIGHT in digits,'terminated Count')
    digits=digits[:digits.index(RIGHT)]
    need(digits and all(x in (0,1) for x in digits),'binary Count')
    return sum(bit<<i for i,bit in enumerate(digits))


def tape_snapshot(counts):
    return tuple((bytes(getattr(c.tape,'physical',c.tape).cells),c.tape.head) for c in counts)


def meter(tapes):
    unique={id(getattr(t,'physical',t)):getattr(t,'physical',t) for t in tapes}
    return tuple(sum(getattr(t.meter,name) for t in unique.values()) for name in ('reads','writes','moves'))


def oracle(M,K,T,m,r,F):
    def profile(width):
        depth=0
        while width>=T:
            width=r*(width//m);depth+=1
        return depth,F**depth
    for q in range(M):
        depth,stock=profile(M-q);rows=1<<(K*q)
        padded=((rows+stock-1)//stock)*stock
        if padded<2*rows:return q,depth,stock
    raise ValueError('no oracle prefix')


def syntax_checks(planner,root):
    tree=ast.parse((HERE/'planner.py').read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.Attribute):
            need(node.attr not in ('cells','head','meter','bit_count','__dict__'),'no decoded runtime tape access')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
            need(node.func.id not in ('int','float','eval','exec','getattr','setattr','__import__'),'no host decoder or runtime patch')
    source=(root/'research/physical-complex-controller/root_layer.py').read_text()
    need('plan=None' in source and 'self.plan = plan if plan is not None else RootPlan(' in source,'existing root plan interface')
    from root_plan import RootPlan,FIELDS
    need(planner.MinimumRootPlan.count is RootPlan.count and planner.MinimumRootPlan.clear is RootPlan.clear,'source field access and cleanup retained')
    need(set(FIELDS)==set(planner.MinimumRootPlan(2,1,2,guard_exponent=2).roles),'all source plan fields retained')
    return len(FIELDS)


def arithmetic(planner,root):
    from cardinal_counts import Count
    from scratch_pool import ScratchPool
    from session import OuterScope,sealed_constructors
    spec=importlib.util.spec_from_file_location('minimum_prefix_reference',HERE/'reference.py')
    reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
    pool=ScratchPool(32);scope=OuterScope(pool)
    totals=[0,0,0];cases=nonpower=between=0
    domain=[]
    for m,r,thresholds,divisors in ((2,1,(2,3,6),(2,3,6)),(3,2,(3,5),(2,5))):
        for T in thresholds:
            for F in divisors:
                for M in range(1,33):
                    for K in (1,2,4):domain.append((M,K,T,m,r,F))
    production_divisor=14336*(1<<1296)
    for j in range(1,37):production_divisor*=((1<<(2*j))-1)
    domain.extend((M,K,73,73,48,production_divisor) for M,K in ((72,1),(74,4096),(147,4096)))
    for M,K,T,m,r,F in domain:
        counts=tuple(Count.literal(x) for x in (M,K,T))
        before=tape_snapshot(counts);tapes=(*pool.tapes,*(c.tape for c in counts));start=meter(tapes)
        with sealed_constructors(),scope.installed():
            result=planner.minimum_prefix(*counts,m,r,F)
            got=tuple(integer(c) for c in result)
            need(got==oracle(M,K,T,m,r,F),'least strict-padding prefix')
            prior=reference.PrefixCompiler(F,T,m,r).compile(M,K)
            need(got[0]==prior['q0'] and got[1]==prior['depth'],'retained reference contract')
            q,d,S=got;R=1<<(K*q)
            need(((R+S-1)//S)*S<2*R,'strict padding at returned prefix')
            need(tape_snapshot(counts)==before,'borrowed Count bytes and heads')
            for c in result:c.close()
        pool.empty()
        stop=meter(tapes)
        for i in range(3):totals[i]+=stop[i]-start[i]
        for c in counts:c.close()
        cases+=1;nonpower+=int(F&(F-1)!=0);between+=int(R<S<2*R)
    controls=0
    for M,K,T,m,r,F in ((0,1,2,2,1,6),(3,0,2,2,1,6),(3,1,1,2,1,6),
                        (3,1,2,2,2,6),(3,1,2,2,1,1),(3,1,2,True,1,6)):
        counts=tuple(Count.literal(x) for x in (M,K,T));before=tape_snapshot(counts)
        with sealed_constructors(),scope.installed():
            try:planner.minimum_prefix(*counts,m,r,F)
            except ValueError:controls+=1
            else:raise ValueError('invalid planner input accepted')
        need(tape_snapshot(counts)==before,'failed search preserves borrowed Counts');pool.empty()
        for c in counts:c.close()
    need(controls==6 and all(x>0 for x in totals),'controls and positive physical planner work')
    return dict(cases=cases,non_power_divisor_cases=nonpower,rows_below_stock_cases=between,
                failure_controls=controls,fixed_pool_capacity=32,peak_live_leases=pool.peak,
                tape_reads=totals[0],tape_writes=totals[1],tape_moves=totals[2],
                production_divisor_bits=production_divisor.bit_length(),plan_fields=syntax_checks(planner,root))


def encode(values,width):
    return bytes((v>>bit)&1 for pair in values for v in pair for bit in range(width))


def body(tape):
    from words import BLANK
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def walsh(values,D,left,right,fields,rows):
    # In-place butterflies give an oracle independent of the physical caller.
    addresses=1<<(left+D+right);result=[list(pair) for pair in values]
    for row in range(rows):
        for axis in range(D):
            mask=1<<(right+axis)
            for address in range(addresses):
                if address&mask:continue
                for field in range(fields):
                    a=(row*addresses+address)*fields+field;b=a+mask*fields
                    x,y=result[a][:],result[b][:]
                    result[a]=[x[c]+y[c] for c in (0,1)]
                    result[b]=[x[c]-y[c] for c in (0,1)]
    divisor=1<<D
    return [tuple((abs(v)//divisor)*(1 if v>=0 else -1) for v in pair) for pair in result]


def roots(planner,root,phase):
    from cardinal_counts import Count
    from fixture_binding import FixtureBinding
    from macro_code import Code
    from ordinary import Ordinary
    from records import Tape
    from root_layer import RootLayer
    from root_streams import RowPadding
    from selected_binding import Group
    from session import erase_marker
    from words import BLANK
    class OneCover:
        size=1
        @staticmethod
        def unrank(index):
            need(index==0,'single fixture cover');return (1,2)
    class Observed(planner.MinimumRootPlan):
        def compute(self,*args):
            super().compute(*args)
            names=('q0','depth','stock','original_rows','padded_rows','core_width')
            self.observed={k:integer(self.count(k)) for k in names}
            return self
    class Reduced(Observed):
        def parameters(self,precision):return tuple(Count.literal(v) for v in (8,1,1,1,32))
    class Repeated(FixtureBinding):
        def __init__(self,copies):
            super().__init__();self.copies=copies;self.families=2*copies;self.cover=OneCover()
        def group_count(self,event):
            need(event==0,'fixture event');return self.copies
        def group(self,event,subgroup,cover):
            need(0<=subgroup<self.copies,'fixture subgroup')
            g=super().group(event,0,cover)
            return Group(tuple((2*subgroup+f,c) for f,c in g.keys),g.code,g.recipes)
    packets=0;events={};digest=hashlib.sha256();plans=[];peaks=[];controls=0
    for copies,reduced,cases in ((1,False,((5,0,1,1,2,2,0),(5,1,1,1,2,2,0),(5,2,1,0,2,1,0),(6,3,0,1,1,1,0))),
                                  (1,True,((9,8,0,0,1,1,0),)),(3,True,((9,8,0,0,1,1,0),(9,8,0,0,1,1,0)))):
        if phase=='roots-direct' and reduced:continue
        if phase=='roots-two' and (not reduced or copies!=1):continue
        if phase=='roots-six' and (not reduced or copies!=3):continue
        binding=Repeated(copies)
        native=Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),SimpleNamespace(families=0),
                        (Code((('unreachable',),),0),),capacity=64)
        plan=(Reduced if reduced else Observed)(2,1,2*copies,guard_exponent=2)
        def observe(machine,event):
            events[event]=events.get(event,0)+1
            need(not machine.pool.live and not layer.pool.live,'closed pools at child cut')
        layer=RootLayer(binding,native,binding.catalogue,plan,observe)
        for parameters in cases:
            p,D,left,right,fields,rows,rho=parameters
            count=rows*(1<<(left+D+right))*fields
            values=[((2+packets)+(1 if i&1==0 else -1),
                     (1+packets%2)*(1 if (i&3).bit_count()%2==0 else -1)) for i in range(count)]
            raw=encode(values,p+2);expected=encode(walsh(values,D,left,right,fields,rows),p+2)
            source=Tape()
            for bit in raw:source.append(bit)
            source.rewind();counts=tuple(Count.literal(v) for v in parameters);before=tape_snapshot(counts)
            result=layer.run(source,*counts)
            desc=plan.observed;desc['families']=2*copies;desc['reduced_law']=reduced
            if reduced and copies==3:
                need(desc['q0']==2 and desc['stock']==6 and desc['original_rows']==4 and desc['padded_rows']==6,'actual non-power padding case')
            plans.append(desc)
            need(body(result)==expected and any(body(result)),'complete dirty root endpoint')
            need(body(source)==raw and tape_snapshot(counts)==before,'complete root borrowed state')
            need(layer.closed and not layer.pool.live and layer.current.read()==BLANK and
                 all(t.read()==BLANK for t in plan.roles.values()),'root-owned state cleared')
            plan.pool.empty();digest.update(body(result))
            result.clear();erase_marker(result);source.clear()
            for c in counts:c.close()
            packets+=1
        peaks.append(plan.pool.peak)
    if phase in ('roots','roots-six'):
        padding=RowPadding();counts=tuple(Count.literal(v) for v in (1,1,2,2));source=Tape()
        for bit in (1,0,1,0):source.append(bit)
        source.rewind();controls=0
        try:padding.run(source,*counts,remove=True)
        except ValueError as error:
            need('nonzero padded row' in str(error),'dirty padding failure reason');controls+=1
        else:raise ValueError('nonzero padded row accepted')
        need(padding.closed and not padding.pool.live and body(source)==bytes((1,0,1,0)),'dirty padding cleanup')
        source.clear()
        for bit in (1,0,0,0):source.append(bit)
        source.rewind();answer=padding.run(source,*counts,remove=True)
        need(body(answer)==bytes((1,0)),'padding reuse after failure')
        answer.clear();erase_marker(answer);source.clear()
        for c in counts:c.close()
    return dict(packets=packets,plans=plans,recursive_events=events,padding_failure_controls=controls,
                plan_pool_peaks=peaks,sha256=digest.hexdigest(),
                scope='Production root formulas with reduced guard; fast roots use an explicit reduced parameter law and complete C2 fixture.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=('arithmetic','roots','roots-direct','roots-two','roots-six'),required=True)
    args=parser.parse_args();inputs=authenticate()
    import planner,retained
    root,_=retained.activate()
    result=arithmetic(planner,root) if args.phase=='arithmetic' else roots(planner,root,args.phase)
    print(json.dumps(dict(status='PASS_ENCODED_MINIMUM_ROOT_PREFIX_'+args.phase.upper(),source_inputs=inputs,**result),sort_keys=True,indent=2))


if __name__=='__main__':main()
