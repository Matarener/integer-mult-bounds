"""Native bookkeeping with original Fraction miss/score arithmetic."""
from contextlib import contextmanager
from hashlib import sha256
import inspect
import builtins
from types import FunctionType
from pathlib import Path
import slot_parent as parent
import native_backend
from slot_binding import bind,fresh

F=parent.F;CAPACITY=parent.CAPACITY
Contributions=parent.Contributions;NORMAL_CONTRIBUTIONS=Contributions
certified_domain=parent.certified_domain
transformed=parent.transformed
weight_tokens=parent.weight_tokens
_known={}
_ABS=builtins.abs
exec('def compute(old,q,v,a,c):\n    value=old+q*v\n    change=abs(value)-abs(old)\n    return value,change*a,change*c,change\n',_known)

def checked_compute():
    if type(Contributions) is not type:return None
    descriptor=None
    for cls in type.__getattribute__(Contributions,'__mro__'):
        namespace=type.__getattribute__(cls,'__dict__')
        if 'compute' in namespace:
            descriptor=namespace['compute'];break
    if type(descriptor) is not staticmethod:return None
    fn=descriptor.__func__
    if type(fn) is not FunctionType:return None
    if fn.__defaults__ is not None or fn.__kwdefaults__ is not None or fn.__closure__ is not None:return None
    source=parent.parent.entry.parent
    if source.code_shape(fn.__code__)!=source.code_shape(_known['compute'].__code__):return None
    if type(fn.__builtins__) is not dict:return None
    effective=fn.__globals__.get('abs',fn.__builtins__.get('abs'))
    return fn if effective is _ABS else None

class CompactContributions:
    def __init__(self,capacity,weights,tokens):
        callback=checked_compute()
        if callback is None:raise ValueError('qualified original Fraction miss callback')
        self.native=native_backend.load().Cache(capacity,weights,tokens,callback,F.__dict__['_numerator'],F.__dict__['_denominator'],F)
    def event(self,q):return self.native.event(q)
    def statistics(self):return self.native.statistics()

def native_domain(word,weights):
    n=word['public']+word['owned_fields']
    if n<0 or word['public']<0 or word['owned_fields']<0 or len(weights)<len(word['program']):return False
    for event in word['program']:
        if type(event[1]) is not int or not 0<=event[1]<n:return False
        for value in event:
            if type(value) is F:
                try:a,b=value._numerator,value._denominator
                except AttributeError:return False
                if type(a) is not int or type(b) is not int or b<=0:return False
        if event[0] in ('ADD','COPY'):
            if len(event)<5 or type(event[2]) is not int or not 0<=event[2]<n or event[1]==event[2]:return False
    return True

def native_text(raw,mode):
    text=parent.parent.compact_text(raw)
    if mode=='cache':return text
    marker='            step_contribution = contributions.event(q)\n'
    start=text.index(marker)
    end=text.index('\n        if op in rounded:',start)
    # Bind the complete literal coefficient loop through the next operation arm.
    if end<0:raise ValueError('exact native coefficient loop endpoint')
    before=text[start:end]
    expected='''            step_contribution = contributions.event(q)
            for i, v in rows[event[2]].items():
                old = rows[r].get(i, F(0))
                value, increment_a, increment_c, change = step_contribution(old,v,i)
                scores[r][0] += increment_a
                scores[r][1] += increment_c
                scores[r][2] += change
                if value:
                    rows[r][i] = value
                else:
                    rows[r].pop(i, None)'''
    parent.parent.entry.parent.need(before==expected,'complete native coefficient-loop source')
    return text[:start]+'            contributions.event(q).apply(rows[r],rows[event[2]],scores[r])'+text[end:]

def derive(reference,capacity=CAPACITY,mode='apply'):
    entry=parent.parent.entry;source=entry.parent
    source.need(type(capacity) is int and 0<=capacity<=CAPACITY,'bounded integer table capacity')
    source.need(mode in ('cache','apply'),'known native mechanism')
    source.need(reference.F is F,'exact standard Fraction type')
    source.need(sha256(Path(reference.__file__).read_bytes()).hexdigest()==source.MODULE_SHA256,'exact Fraction module bytes')
    original=reference.error_trace;raw=inspect.getsource(original)
    safe=transformed(raw);compact=native_text(raw,mode)
    namespace=dict(reference.__dict__);exec(compile(raw,'<source-binding>','exec'),namespace)
    source.need(source.code_shape(original.__code__)==source.code_shape(namespace['error_trace'].__code__),'live Fraction code agrees with source')
    source.need(original.__defaults__ is None and original.__kwdefaults__ is None and original.__closure__ is None,'ordinary Fraction function')
    token=bind();last=[None,None,None];factory=Contributions
    def report(value):last[0]=None if value is None else dict(value)
    namespace.update(_contribution_factory=lambda:factory(capacity),_contribution_report=report,
                     _compact_factory=lambda weights,tokens:CompactContributions(capacity,weights,tokens))
    exec(compile(safe,'<checked-parent-table>','exec'),namespace);generic=namespace['error_trace']
    exec(compile(compact,'<native-canonical-keys>','exec'),namespace);specialized=namespace['error_trace']
    def call(word,weights,rounded):
        last[:]=[None,False,None]
        if token is None or not fresh(token):return original(word,weights,rounded)
        eligible=bool(capacity and factory is NORMAL_CONTRIBUTIONS and checked_compute() is not None and certified_domain(word,weights,rounded))
        if eligible and not native_domain(word,weights):return original(word,weights,rounded)
        tokens=weight_tokens(weights) if eligible else None
        if eligible and tokens is None:return original(word,weights,rounded)
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
