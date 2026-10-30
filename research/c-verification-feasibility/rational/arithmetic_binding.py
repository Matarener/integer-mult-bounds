"""Source-only prototype: authenticate operations bypassed by score batching.

A compiled source tree is inspected as data; the independent Fraction oracle
is never patched. The first supported runtime is the pinned host CPython3.12.
"""
import builtins
from fractions import Fraction as F
import fractions
from hashlib import sha256
import math
import numbers
import operator
from pathlib import Path
import sys
from types import CodeType, FunctionType, BuiltinFunctionType
import slot_binding

SOURCE_SHA256='cf33568f7b767f66896995a7a81cc662e8be226f2e58efb61d2028f64eb5d231'
# Explicitly reviewed CPython source revisions; all live operation guards remain.
SUPPORTED_RUNTIME_SOURCES={(3,12,3):frozenset((SOURCE_SHA256,)),
    (3,12,15):frozenset(('d52d1ab9d5be26924e4914a5e40069c992bbfa68f773694c2e5ee8452d0766a0',))}
DIRECT=('_add','_sub','_mul','__abs__','__bool__','__new__')
WRAPPED=(('__add__','_add','add','forward'),('__radd__','_add','add','reverse'),
         ('__sub__','_sub','sub','forward'),('__rsub__','_sub','sub','reverse'),
         ('__mul__','_mul','mul','forward'),('__rmul__','_mul','mul','reverse'))
BUILTINS=('isinstance','type','int','float','complex','super','abs')
_expected=None

def _shape(code):
    return (code.co_code,tuple(_shape(x) if type(x) is CodeType else x for x in code.co_consts),
            code.co_names,code.co_varnames,code.co_freevars,code.co_cellvars,
            code.co_argcount,code.co_posonlyargcount,code.co_kwonlyargcount,
            code.co_flags,code.co_exceptiontable)

def _codes():
    global _expected
    path=Path(fractions.__file__)
    raw=path.read_bytes()
    if path.is_symlink() or sha256(raw).hexdigest() not in SUPPORTED_RUNTIME_SOURCES.get(sys.version_info[:3],()):raise ValueError('pinned Fraction source')
    if _expected is not None:return _expected
    compiled=compile(raw,str(path),'exec',optimize=sys.flags.optimize)
    result={}
    def visit(code):
        result[code.co_qualname]=code
        for value in code.co_consts:
            if type(value) is CodeType:visit(value)
    visit(compiled)
    _expected=result
    return result

def _function(fn,qualname):
    if type(fn) is not FunctionType or fn.__kwdefaults__ is not None:
        raise ValueError('ordinary arithmetic function')
    defaults=fn.__defaults__
    if qualname=='Fraction.__new__':
        if type(defaults) is not tuple or len(defaults)!=2 or type(defaults[0]) is not int or defaults[0]!=0 or defaults[1] is not None:raise ValueError('arithmetic defaults')
    elif defaults is not None:raise ValueError('arithmetic defaults')
    if _shape(fn.__code__)!=_shape(_codes()[qualname]):raise ValueError('arithmetic executable shape')
    if fn.__globals__ is not fractions.__dict__:raise ValueError('arithmetic globals owner')
    if type(fn.__builtins__) is not dict:raise ValueError('arithmetic builtins mapping')
    for name in BUILTINS:
        if fn.__builtins__.get(name) is not getattr(builtins,name):raise ValueError('arithmetic builtins identity')
    return fn

def _snapshot():
    ns=type.__getattribute__(F,'__dict__')
    out=[F,fractions.Fraction,math.gcd,operator.add,operator.sub,operator.mul]
    for name in DIRECT+('_from_coprime_ints',)+tuple(x[0] for x in WRAPPED):
        raw=ns.get(name);fn=raw.__func__ if type(raw) in (classmethod,staticmethod) else raw
        out.append(raw)
        if type(fn) is FunctionType:
            out.extend((fn,fn.__code__,fn.__defaults__,fn.__kwdefaults__,fn.__closure__))
            if fn.__closure__:
                for cell in fn.__closure__:out.extend((cell,cell.cell_contents))
            out.extend(fn.__globals__.get(x) for x in ('Fraction','math','numbers','operator'))
            out.extend(fn.__builtins__.get(x) for x in BUILTINS)
    for cls in F.__mro__:
        ns=type.__getattribute__(cls,'__dict__')
        out.extend((cls,ns.get('__iadd__'),ns.get('__setattr__'),ns.get('__delattr__'),ns.get('__del__')))
    return tuple(out)

def bind():
    try:
        if sys.implementation.name!='cpython' or sys.version_info[:2]!=(3,12):return None
        slots=slot_binding.bind(strict=True)
        expected_mro=(F,numbers.Rational,numbers.Real,numbers.Complex,numbers.Number,object)
        if len(F.__mro__)!=len(expected_mro) or any(x is not y for x,y in zip(F.__mro__,expected_mro)):return None
        ns=type.__getattribute__(F,'__dict__')
        owned_slots=ns.get('__slots__')
        if fractions.Fraction is not F or type(owned_slots) is not tuple or len(owned_slots)!=2 or any(type(x) is not str for x in owned_slots) or owned_slots!=('_numerator','_denominator'):return None
        if fractions.__dict__.get('math') is not math or fractions.__dict__.get('operator') is not operator:return None
        if type(math.gcd) is not BuiltinFunctionType or math.gcd.__name__!='gcd' or math.gcd.__self__ is not math:return None
        for name in ('add','sub','mul'):
            fn=getattr(operator,name)
            if type(fn) is not BuiltinFunctionType or fn.__name__!=name or fn.__module__!='_operator':return None
        for name in DIRECT:
            raw=ns.get(name)
            fn=_function(raw.__func__ if type(raw) is staticmethod else raw,'Fraction.'+name)
            if fn.__closure__ is not None and not (fn.__code__.co_freevars==('__class__',) and len(fn.__closure__)==1 and fn.__closure__[0].cell_contents is F):return None
        factory=ns.get('_from_coprime_ints')
        if type(factory) is not classmethod:return None
        fn=_function(factory.__func__,'Fraction._from_coprime_ints')
        if fn.__closure__ is not None and not (fn.__code__.co_freevars==('__class__',) and len(fn.__closure__)==1 and fn.__closure__[0].cell_contents is F):return None
        for name,mono,op,direction in WRAPPED:
            fn=_function(ns.get(name),'Fraction._operator_fallbacks.<locals>.'+direction)
            closure=dict(zip(fn.__code__.co_freevars,(c.cell_contents for c in fn.__closure__ or ())))
            if len(closure)!=2 or closure.get('fallback_operator') is not getattr(operator,op) or closure.get('monomorphic_operator') is not ns[mono]:return None
        for cls in F.__mro__:
            raw=type.__getattribute__(cls,'__dict__')
            if '__iadd__' in raw or '__del__' in raw:return None
            if '__setattr__' in raw and raw['__setattr__'] is not object.__dict__['__setattr__']:return None
            if '__delattr__' in raw and raw['__delattr__'] is not object.__dict__['__delattr__']:return None
        return slots,_snapshot(),math.gcd
    except (AttributeError,KeyError,TypeError,ValueError,OSError):return None

def fresh(token):
    if token is None or not slot_binding.fresh(token[0]):return False
    try:now=_snapshot()
    except (AttributeError,ValueError,TypeError):return False
    return len(now)==len(token[1]) and all(x is y for x,y in zip(now,token[1]))
