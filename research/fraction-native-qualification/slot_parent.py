"""Same compact keys with verified pure property-to-slot equivalence."""
from contextlib import contextmanager
from hashlib import sha256
import inspect
from pathlib import Path
import compact_parent as parent
from slot_binding import bind,fresh

F=parent.F;CAPACITY=parent.CAPACITY
Contributions=parent.Contributions
NORMAL_CONTRIBUTIONS=Contributions
certified_domain=parent.certified_domain
transformed=parent.transformed
def weight_tokens(weights,limit=parent.CONTEXT_CAPACITY):
    parent.entry.parent.need(type(limit) is int and 0<=limit<=parent.CONTEXT_CAPACITY,'bounded context token capacity')
    mapping={};tokens=[]
    for row in weights:
        a,c=row[0],row[1]
        if type(a) is not F or type(c) is not F:return None
        try:key=(a._numerator,a._denominator,c._numerator,c._denominator)
        except AttributeError:return None
        if any(type(x) is not int for x in key) or key[1]<=0 or key[3]<=0:return None
        token=mapping.get(key)
        if token is None:
            if len(mapping)>=limit:return None
            token=len(mapping);mapping[key]=token
        tokens.append(token)
    return tokens


class CompactContributions(parent.CompactContributions):
    def event(self,q):
        qn,qd=q.numerator,q.denominator
        table=self.table;weights=self.weights;tokens=self.tokens;capacity=self.capacity;compute=self.compute
        def step(old,v,i):
            self.calls+=1
            key=(old._numerator,old._denominator,qn,qd,v._numerator,v._denominator,tokens[i])
            result=table.get(key)
            if result is not None:self.hits+=1;return result
            self.misses+=1
            result=compute(old,q,v,weights[i][0],weights[i][1])
            if len(table)>=capacity:table.popitem(last=False);self.evictions+=1
            table[key]=result
            return result
        return step


def derive(reference,capacity=CAPACITY):
    entry=parent.entry;source=entry.parent
    source.need(type(capacity) is int and 0<=capacity<=CAPACITY,'bounded integer table capacity')
    source.need(reference.F is F,'exact standard Fraction type')
    source.need(sha256(Path(reference.__file__).read_bytes()).hexdigest()==source.MODULE_SHA256,'exact Fraction module bytes')
    original=reference.error_trace;raw=inspect.getsource(original)
    safe=transformed(raw);compact=parent.compact_text(raw)
    namespace=dict(reference.__dict__);exec(compile(raw,'<source-binding>','exec'),namespace)
    source.need(source.code_shape(original.__code__)==source.code_shape(namespace['error_trace'].__code__),'live Fraction code agrees with source')
    source.need(original.__defaults__ is None and original.__kwdefaults__ is None and original.__closure__ is None,'ordinary Fraction function')
    token=bind();last=[None,None,None];factory=Contributions
    def report(value):last[0]=None if value is None else dict(value)
    namespace.update(_contribution_factory=lambda:factory(capacity),_contribution_report=report,
                     _compact_factory=lambda weights,tokens:CompactContributions(capacity,weights,tokens))
    exec(compile(safe,'<checked-parent-table>','exec'),namespace);generic=namespace['error_trace']
    exec(compile(compact,'<slot-canonical-keys>','exec'),namespace);specialized=namespace['error_trace']
    def call(word,weights,rounded):
        if token is None or not fresh(token):
            last[:]=[None,False,None]
            return original(word,weights,rounded)
        eligible=bool(capacity and factory is NORMAL_CONTRIBUTIONS and certified_domain(word,weights,rounded))
        tokens=weight_tokens(weights) if eligible else None
        if eligible and tokens is None:
            last[:]=[None,False,None]
            return original(word,weights,rounded)
        last[1]=tokens is not None;last[2]=None if tokens is None else (max(tokens)+1 if tokens else 0)
        return specialized(word,weights,rounded,tokens) if tokens is not None else generic(word,weights,rounded)
    call.statistics=lambda:None if last[0] is None else dict(last[0])
    call.compacted_selected=lambda:last[1]
    call.token_count=lambda:last[2]
    return call


@contextmanager
def installed(reference,capacity=CAPACITY):
    original=reference.error_trace;derived=derive(reference,capacity);reference.error_trace=derived
    try:yield derived
    finally:reference.error_trace=original
