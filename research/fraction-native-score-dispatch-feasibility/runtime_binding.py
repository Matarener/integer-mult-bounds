"""Authenticate the exact same Fraction addition branch, or retain generic +=.

No standard-library mutation or alternative rational arithmetic. Source/runtime
inspection and controls by Chris R / Clear1nsight with substantial Codex/Astra
assistance; original arithmetic remains its credited Python/Fraction authors.
"""
import builtins
from fractions import Fraction as F
from hashlib import sha256
import json
import math
import operator
from pathlib import Path
from types import FunctionType
from table_parent import code_shape

EXPECTED=json.loads(Path(__file__).with_name('RUNTIME-SHAPES.json').read_text())['functions']


def raw_function(name):
    value=F.__dict__.get(name)
    if type(value) is FunctionType:
        return value
    if name=='__new__' and type(value) is staticmethod:
        function=value.__func__
        if type(function) is FunctionType:return function
    if name=='_from_coprime_ints' and type(value) is classmethod:
        function=value.__func__
        if type(function) is FunctionType:return function
    raise ValueError('ordinary authenticated descriptor '+name)


def state_token():
    """Identity-only trace-entry freshness; never invoke foreign descriptors."""
    try:
        values=[]
        for name in EXPECTED:
            fn=raw_function(name);g=fn.__globals__;b=fn.__builtins__
            if type(b) is not dict:return None
            values.extend((F.__dict__[name],fn,fn.__code__,fn.__defaults__,fn.__kwdefaults__,g,b,g.get('Fraction'),g.get('math')))
            for key in ('isinstance','super','int','abs'):
                values.append(g.get(key,b.get(key)))
            for cell in fn.__closure__ or ():
                values.append(cell.cell_contents)
        for cls in F.__mro__:
            values.extend((cls,'__iadd__' in cls.__dict__,cls.__dict__.get('__iadd__'),'__new__' in cls.__dict__,cls.__dict__.get('__new__')))
        values.append(math.gcd)
        return tuple(values)
    except (ValueError,AttributeError,TypeError,KeyError):return None


def still_current(token):
    current=state_token()
    return token is not None and current is not None and len(token)==len(current) and all(a is b for a,b in zip(token,current))


def bind_kernel(strict=False):
    try:
        if any('__iadd__' in cls.__dict__ for cls in F.__mro__):
            raise ValueError('no distinct Fraction augmented assignment')
        functions={}
        for name,expected in EXPECTED.items():
            value=raw_function(name)
            if type(value) is not FunctionType or sha256(repr(code_shape(value.__code__)).encode()).hexdigest()!=expected:
                raise ValueError('known live Fraction executable '+name)
            functions[name]=value
        forward=functions['__add__'];kernel=functions['_add']
        cells=dict(zip(forward.__code__.co_freevars,forward.__closure__ or ()))
        if set(cells)!={'fallback_operator','monomorphic_operator'}:
            raise ValueError('exact addition closure fields')
        if cells['monomorphic_operator'].cell_contents is not kernel or cells['fallback_operator'].cell_contents is not operator.add:
            raise ValueError('addition closure uses this exact kernel')
        for fn in functions.values():
            g=fn.__globals__
            if g.get('Fraction') is not F or g.get('math') is not math:
                raise ValueError('standard Fraction and math globals')
            b=fn.__builtins__
            b=vars(b) if b is builtins else b
            if type(b) is not dict:
                raise ValueError('ordinary builtin mapping')
            for name in ('isinstance','super','int','abs'):
                if g.get(name,b.get(name)) is not getattr(builtins,name):
                    raise ValueError('standard builtin '+name)
        if type(math.gcd) is not type(operator.add) or math.gcd.__module__!='math' or math.gcd.__name__!='gcd':
            raise ValueError('standard builtin gcd')
        constructor=F.__dict__['_from_coprime_ints']
        if type(constructor) is not classmethod or constructor.__func__ is not functions['_from_coprime_ints']:
            raise ValueError('Fraction classmethod allocator')
        allocator=next((cls.__dict__['__new__'] for cls in F.__mro__[1:] if '__new__' in cls.__dict__),None)
        if allocator is not object.__dict__['__new__']:
            raise ValueError('standard inherited allocator')
        for wrapper,operation,builtin in [('__mul__','_mul',operator.mul),('__sub__','_sub',operator.sub)]:
            method=functions[wrapper]
            mc=dict(zip(method.__code__.co_freevars,method.__closure__ or ()))
            if set(mc)!={'fallback_operator','monomorphic_operator'} or mc['monomorphic_operator'].cell_contents is not functions[operation] or mc['fallback_operator'].cell_contents is not builtin:
                raise ValueError('type-preserving branch '+wrapper)
        return kernel
    except (ValueError,AttributeError,TypeError,KeyError) as error:
        if strict:raise ValueError('unsupported Fraction direct-add binding: '+str(error)) from error
        return None
