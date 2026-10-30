"""Source-only wrapper for the extended, staged PR5864 native package.

Root stages native_bulk.c as native_cache.c and updates its source receipt.
No build is performed merely by importing this wrapper.
"""
from contextlib import contextmanager
from hashlib import sha256
import inspect
from pathlib import Path
from fractions import Fraction as F
import math
import fraction_table as predecessor
import native_backend
import arithmetic_binding

CAPACITY=predecessor.CAPACITY
BASE_DERIVE=predecessor.derive

def canonical_fraction(value):
    if type(value) is not F:return False
    try:n,d=value._numerator,value._denominator
    except AttributeError:return False
    return type(n) is int and type(d) is int and d>0 and math.gcd(n,d)==1

def rational_domain(word,weights,rounded):
    if not predecessor.certified_domain(word,weights,rounded):return False
    if not predecessor.native_domain(word,weights):return False
    if any(not canonical_fraction(value) for pair in weights for value in pair[:2]):return False
    # Scalars are still converted at their original event, in original order.
    # Exact strings remain permitted: F(str) returns a canonical Fraction or
    # raises at the original point. No dyadic assumption or eager parsing.
    for event in word['program']:
        if any(type(x) is F and not canonical_fraction(x) for x in event):return False
    return True

class CompactContributions:
    def __init__(self,capacity,weights,tokens):
        callback=predecessor.checked_compute()
        if callback is None:raise ValueError('original Fraction contribution callback')
        self.native=native_backend.load().Cache(capacity,weights,tokens,callback,
                         F.__dict__['_numerator'],F.__dict__['_denominator'],F)
    def event(self,q):return self.native.event(q)
    def statistics(self):return self.native.statistics()

def derive(reference,capacity=CAPACITY,mode='apply'):
    fallback=BASE_DERIVE(reference,capacity,mode)
    token=arithmetic_binding.bind()
    source=predecessor.parent.parent.entry.parent
    raw=inspect.getsource(reference.error_trace)
    source.need(sha256(Path(reference.__file__).read_bytes()).hexdigest()==source.MODULE_SHA256,'exact rational reference source')
    text=predecessor.native_text(raw,'apply')
    before='contributions.event(q).apply(rows[r],rows[event[2]],scores[r])'
    source.need(text.count(before)==1,'one rational score batch seam')
    text=text.replace(before,'contributions.event(q).apply_rational(rows[r],rows[event[2]],scores[r],_rational_gcd)')
    state=[None,False,None]
    def report(value):state[0]=None if value is None else dict(value)
    namespace=dict(reference.__dict__)
    namespace.update(_compact_factory=lambda weights,tokens:CompactContributions(capacity,weights,tokens),
                     _contribution_report=report,_rational_gcd=None if token is None else token[2])
    exec(compile(text,'<rational-score-batch>','exec'),namespace)
    specialized=namespace['error_trace']
    def call(word,weights,rounded):
        state[:]=[None,False,None]
        if mode!='apply' or not capacity or predecessor.Contributions is not predecessor.NORMAL_CONTRIBUTIONS or not arithmetic_binding.fresh(token) or predecessor.checked_compute() is None:
            return fallback(word,weights,rounded)
        if not rational_domain(word,weights,rounded):return fallback(word,weights,rounded)
        tokens=predecessor.weight_tokens(weights)
        if tokens is None:return fallback(word,weights,rounded)
        state[1]=True;state[2]=max(tokens)+1 if tokens else 0
        return specialized(word,weights,rounded,tokens)
    call.rational_selected=lambda:state[1]
    call.statistics=lambda:dict(state[0]) if state[1] and state[0] is not None else fallback.statistics()
    call.compacted_selected=lambda:True if state[1] else fallback.compacted_selected()
    call.token_count=lambda:state[2] if state[1] else fallback.token_count()
    return call

@contextmanager
def installed(reference,capacity=CAPACITY):
    original=reference.error_trace
    value=derive(reference,capacity)
    reference.error_trace=value
    try:yield value
    finally:reference.error_trace=original
