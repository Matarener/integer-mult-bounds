"""Finite gate before construction, using the actual frozen Fraction source."""
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
import inspect
import json
from pathlib import Path
import random
import sys
import tempfile
import types
from frozen import baseline, require
from fraction_table import derive, installed, transformed, Contributions, CAPACITY


def types_of(value):
    if isinstance(value, dict):
        return ('dict', {k:types_of(v) for k,v in value.items()})
    if isinstance(value, (list, tuple)):
        return (type(value).__name__, [types_of(v) for v in value])
    return type(value).__name__


def fixtures():
    rng = random.Random(5848)
    special = [['ADD',0,1,1,0],['ADD',1,0,1,0],['ADD',1,0,-2,0],
               ['ADD',1,0,1,0],['COPY',2,1,-1,0],['SCALE',1,'1/2',0],
               ['MOVE',2,0,0,False],['INIT',2,0],['CLEAR',2,0]]
    yield dict(public=2,owned_fields=1,program=special), [(F(1),F(1))]*len(special), {'ADD','COPY','SCALE','INIT','CLEAR','MOVE'}
    scalars = ['1','-1','1/2','-3/8','2','-4','5/16']
    for case in range(240):
        n = 3+case%6
        program = []
        for i in range(case%95):
            op = rng.choice(['INIT','CLEAR','MOVE','ADD','COPY','SCALE'])
            r = rng.randrange(n)
            if op in ('INIT','CLEAR'):event=[op,r,0]
            elif op=='MOVE':event=[op,r,0,0,False]
            elif op=='SCALE':event=[op,r,rng.choice(scalars),0]
            else:event=[op,r,rng.choice([s for s in range(n) if s!=r]),rng.choice(scalars),0]
            program.append(event)
        weights=[(F(rng.randrange(6),2**rng.randrange(7)),F(rng.randrange(5),2**rng.randrange(6))) for e in program]
        rounded={op for op in ('INIT','CLEAR','MOVE','ADD','COPY','SCALE') if rng.randrange(2)}
        yield dict(public=n-1,owned_fields=1,program=program),weights,rounded


def main():
    results=[]
    def rejects(label, action, exception=ValueError):
        try:action()
        except exception:results.append(label)
        else:raise ValueError('accepted '+label)
    with baseline() as package:
        sys.path.insert(0,str(package))
        import source
        with source.baseline() as p:
            spec=importlib.util.spec_from_file_location('finite_precision_entry',p/'verify.py')
            v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
            with v.source() as (_,original,ref):
                old=ref.error_trace
                fast=derive(ref)
                cases=list(fixtures());events=0
                engines={capacity:derive(ref,capacity) for capacity in (0,1,2,CAPACITY)}
                for word,weights,rounded in cases:
                    before=deepcopy((word,weights,rounded))
                    a=old(word,weights,rounded)
                    for capacity in (0,1,2,CAPACITY):
                        f=engines[capacity];b=f(word,weights,rounded)
                        require(a==b and types_of(a)==types_of(b),'complete finite output and numeric types')
                        require(f.statistics()['resident']<=capacity,'bounded per-trace table')
                    require((word,weights,rounded)==before,'inputs remain unchanged')
                    events+=len(word['program'])
                word,weights,rounded=cases[0]
                value=fast(word,weights,rounded);value[0]['final_scores'][0][0]=F(999)
                require(fast(word,weights,rounded)==old(word,weights,rounded),'fresh mutable output')
                results.append('returned-mutation-isolated')
                raw=inspect.getsource(old)
                rejects('source-drift',lambda:transformed(raw+'\n# drift\n'))
                saved_F=ref.F;ref.F=int
                try:rejects('Fraction-type-drift',lambda:derive(ref))
                finally:ref.F=saved_F
                with tempfile.TemporaryDirectory() as td:
                    file=Path(td)/'precision.py';file.write_bytes(Path(ref.__file__).read_bytes()+b'\n# drift\n')
                    saved_file=ref.__file__;ref.__file__=str(file)
                    try:rejects('module-byte-drift',lambda:derive(ref))
                    finally:ref.__file__=saved_file
                code=old.__code__.replace(co_consts=('live-code-drift',)+old.__code__.co_consts[1:])
                ref.error_trace=types.FunctionType(code,old.__globals__)
                try:rejects('live-code-drift',lambda:derive(ref))
                finally:ref.error_trace=old
                constants=list(old.__code__.co_consts)
                index=next(i for i,c in enumerate(constants) if isinstance(c,types.CodeType))
                constants[index]=constants[index].replace(co_consts=constants[index].co_consts+('nested-code-drift',))
                ref.error_trace=types.FunctionType(old.__code__.replace(co_consts=tuple(constants)),old.__globals__)
                try:rejects('nested-live-code-drift',lambda:derive(ref))
                finally:ref.error_trace=old
                for label,change in [
                    ('omitted-witness',('witness[k] = dict(rows[r])','witness[k] = {}')),
                    ('omitted-rounded-sites',('if op in rounded:','if False:'))]:
                    text=transformed(raw);require(change[0] in text,'mutant site');text=text.replace(*change)
                    ns=dict(ref.__dict__);ns.update(_contribution_factory=Contributions,_contribution_report=lambda value:None)
                    exec(compile(text,'<negative-control>','exec'),ns)
                    require(any(ns['error_trace'](*c)!=old(*c) for c in cases),'mutant rejected '+label)
                    results.append(label)
                correct_compute=Contributions.compute
                for label,index in [('wrong-coefficient',0),('wrong-weighted-increment',1)]:
                    def corrupted(*args,**kwargs):
                        out=list(correct_compute(*args,**kwargs));out[index]+=F(1);return tuple(out)
                    Contributions.compute=staticmethod(corrupted)
                    try:require(any(fast(*c)!=old(*c) for c in cases),'arithmetic mutant rejected '+label)
                    finally:Contributions.compute=staticmethod(correct_compute)
                    results.append(label)
                for label,bad_word,bad_weights in [('bad-role',dict(public=2,owned_fields=0,program=[['ADD',99,0,1,0]]),[(F(1),F(1))]),('bad-scalar',dict(public=2,owned_fields=0,program=[['ADD',0,1,'bad',0]]),[(F(1),F(1))]),('missing-weight',word,[])]:
                    errors=[]
                    for fn in (old,fast):
                        try:fn(bad_word,bad_weights,rounded)
                        except (IndexError,ValueError) as e:errors.append((type(e).__name__,str(e)))
                        else:raise ValueError('missing original exception '+label)
                    require(errors[0]==errors[1],'same original exception '+label);results.append(label)
                with installed(ref) as f:
                    require(ref.error_trace is f and f(*cases[0])==old(*cases[0]),'scoped install')
                require(ref.error_trace is old,'restore on success');results.append('restore-success')
                try:
                    with installed(ref):raise RuntimeError('caller-failure')
                except RuntimeError:pass
                require(ref.error_trace is old,'restore on exception');results.append('restore-exception')
                require(derive(ref)(*cases[0])==old(*cases[0]),'fresh derivation');results.append('fresh-derivation')
                # Complete exact keys, collision safety, FIFO, exceptions and fresh lifetimes.
                base=(F(0),F(1),F(1),F(2),F(3))
                for field in range(5):
                    c=Contributions(4);c.step(*base);c.step(*base)
                    changed=list(base);changed[field]+=F(1,2)
                    require(c.step(*changed)==correct_compute(*changed),'complete key value')
                    require(c.hits==1 and c.misses==2,'every key field bound')
                    results.append('key-field-'+str(field))
                c=Contributions(2);a=base;b=(F(1),*base[1:]);d=(F(2),*base[1:])
                c.step(*a);c.step(*b);c.step(*a);c.step(*d)
                require(c.evictions==1 and len(c.table)==2,'capacity eviction')
                prior=c.misses;c.step(*a);require(c.misses==prior+1,'FIFO eviction recomputes');results.append('FIFO-eviction')
                c=Contributions(2);c.step(*base)
                same=(F(0,2),F(2,2),F(3,3),F(4,2),F(9,3));c.step(*same)
                require(c.hits==1,'canonical equal-value key');results.append('canonical-key')
                modulus=sys.hash_info.modulus
                one=base;two=(F(modulus),*base[1:]);keys=lambda values:tuple(t for x in values for t in (x.numerator,x.denominator))
                require(hash(keys(one))==hash(keys(two)) and keys(one)!=keys(two),'actual hash-collision fixture')
                c=Contributions(2);require(c.step(*one)!=c.step(*two) and c.misses==2,'full equality after hash collision');results.append('hash-collision')
                c=Contributions(0);c.step(*base);c.step(*base);require(not c.table and c.bypasses==2,'disabled table');results.append('disabled')
                for cap in (-1,CAPACITY+1,True,1.5):rejects('invalid-capacity-'+str(cap),lambda cap=cap:Contributions(cap))
                class Explodes:
                    def __mul__(self,value):raise ArithmeticError('uncached failure')
                c=Contributions(2)
                for attempt in range(2):rejects('uncached-exception-'+str(attempt),lambda:c.step(F(0),Explodes(),F(1),F(1),F(1)),ArithmeticError)
                require(not c.table,'exceptions not cached')
                fast(*cases[0]);first=fast.statistics();fast(*cases[0]);require(first==fast.statistics(),'fresh per-call table counters');results.append('fresh-call-table')
                first['hits']=-1;require(fast.statistics()['hits']>=0,'stats mutation isolated');results.append('stats-mutation')
                try:fast(dict(public=1,owned_fields=0,program=[['ADD',99,0,1,0]]),[(F(1),F(1))],{'ADD'})
                except IndexError:pass
                else:raise ValueError('missing original failed-call exception')
                require(fast.statistics() is None,'failed call has no old accepted stats');results.append('failed-call-clears-stats')
                require(len(results)==34,'finite control census')
    result={'status':'PASS_FINITE_FRACTION_TABLE_FEASIBILITY','cases':len(cases),'events':events,'controls':results,'all_complete_values_and_types_equal':True}
    print(json.dumps(result,sort_keys=True))
    return result
if __name__=='__main__':main()
