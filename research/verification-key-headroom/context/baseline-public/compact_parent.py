"""Compact exact table keys; original Fraction arithmetic on every miss."""
from contextlib import contextmanager
from hashlib import sha256
import inspect
from pathlib import Path
import entry_parent as entry

F=entry.F
CAPACITY=entry.CAPACITY
CONTEXT_CAPACITY=16384
Contributions=entry.Contributions
NORMAL_CONTRIBUTIONS=Contributions
certified_domain=entry.certified_domain
transformed=entry.transformed


def weight_tokens(weights,limit=CONTEXT_CAPACITY):
    entry.parent.need(type(limit) is int and 0<=limit<=CONTEXT_CAPACITY,'bounded context token capacity')
    mapping={};tokens=[]
    for row in weights:
        a,c=row[0],row[1]
        key=(a.numerator,a.denominator,c.numerator,c.denominator)
        token=mapping.get(key)
        if token is None:
            if len(mapping)>=limit:return None
            token=len(mapping);mapping[key]=token
        tokens.append(token)
    return tokens


class CompactContributions(NORMAL_CONTRIBUTIONS):
    def __init__(self,capacity,weights,tokens):
        super().__init__(capacity)
        self.weights=weights;self.tokens=tokens

    def event(self,q):
        qn,qd=q.numerator,q.denominator
        table=self.table;weights=self.weights;tokens=self.tokens;capacity=self.capacity
        compute=self.compute
        def step(old,v,i):
            self.calls+=1
            key=(old.numerator,old.denominator,qn,qd,v.numerator,v.denominator,tokens[i])
            result=table.get(key)
            if result is not None:
                self.hits+=1
                return result
            self.misses+=1
            result=compute(old,q,v,weights[i][0],weights[i][1])
            if len(table)>=capacity:
                table.popitem(last=False);self.evictions+=1
            table[key]=result
            return result
        return step


def compact_text(raw):
    text=transformed(raw)
    before='def error_trace(word, weights, rounded):\n'
    entry.parent.need(text.count(before)==1,'one compact function signature')
    text=text.replace(before,'def error_trace(word, weights, rounded, tokens):\n')
    before='    contributions = _contribution_factory()\n    contributions.certify(word,weights,rounded)\n'
    entry.parent.need(text.count(before)==1,'one compact factory seam')
    text=text.replace(before,'    contributions = _compact_factory(weights,tokens)\n')
    before="        elif op in ('ADD', 'COPY'):\n            q = F(event[-2])\n            for i, v in rows[event[2]].items():\n"
    entry.parent.need(text.count(before)==1,'one source ADD/COPY event seam')
    text=text.replace(before,"        elif op in ('ADD', 'COPY'):\n            q = F(event[-2])\n            step_contribution = contributions.event(q)\n            for i, v in rows[event[2]].items():\n")
    before='''                value, increment_a, increment_c, change = contributions.step(
                    old, q, v, weights[i][0], weights[i][1])
'''
    entry.parent.need(text.count(before)==1,'one compact call seam')
    return text.replace(before,'                value, increment_a, increment_c, change = step_contribution(old,v,i)\n')


def derive(reference,capacity=CAPACITY):
    parent=entry.parent
    parent.need(type(capacity) is int and 0<=capacity<=CAPACITY,'bounded integer table capacity')
    parent.need(reference.F is F,'exact standard Fraction type')
    parent.need(sha256(Path(reference.__file__).read_bytes()).hexdigest()==parent.MODULE_SHA256,'exact Fraction module bytes')
    original=reference.error_trace;raw=inspect.getsource(original)
    safe=transformed(raw);compact=compact_text(raw)
    namespace=dict(reference.__dict__)
    exec(compile(raw,'<source-binding>','exec'),namespace)
    parent.need(parent.code_shape(original.__code__)==parent.code_shape(namespace['error_trace'].__code__),'live Fraction code agrees with source')
    parent.need(original.__defaults__ is None and original.__kwdefaults__ is None and original.__closure__ is None,'ordinary Fraction function')
    last=[None,None,None]
    factory=Contributions
    def report(value):last[0]=None if value is None else dict(value)
    namespace.update(_contribution_factory=lambda:factory(capacity),_contribution_report=report,
                     _compact_factory=lambda weights,tokens:CompactContributions(capacity,weights,tokens))
    exec(compile(safe,'<checked-parent-table>','exec'),namespace);generic=namespace['error_trace']
    exec(compile(compact,'<compact-canonical-keys>','exec'),namespace);specialized=namespace['error_trace']
    def call(word,weights,rounded):
        tokens=weight_tokens(weights) if capacity and factory is NORMAL_CONTRIBUTIONS and certified_domain(word,weights,rounded) else None
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
