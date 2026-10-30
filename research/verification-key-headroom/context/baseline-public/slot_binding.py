"""Bind only pure Fraction key getters and exact owned slots; never arithmetic."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
from types import FunctionType,MemberDescriptorType
from table_parent import code_shape

EXPECTED=json.loads(Path(__file__).with_name('GETTER-SHAPES.json').read_text())


def snapshot():
    try:
        result=[]
        for name in ('numerator','denominator'):
            prop=F.__dict__.get(name);slot=F.__dict__.get('_'+name)
            if type(prop) is not property or type(prop.fget) is not FunctionType or type(slot) is not MemberDescriptorType:
                return None
            fn=prop.fget
            result.extend((prop,fn,fn.__code__,fn.__defaults__,fn.__kwdefaults__,fn.__closure__,slot))
        for cls in F.__mro__:
            result.extend((cls,'__getattribute__' in cls.__dict__,cls.__dict__.get('__getattribute__'),'__getattr__' in cls.__dict__,cls.__dict__.get('__getattr__')))
        return tuple(result)
    except (AttributeError,TypeError,ValueError):return None


def fresh(token):
    now=snapshot()
    return token is not None and now is not None and len(token)==len(now) and all(a is b for a,b in zip(token,now))


def bind(strict=False):
    try:
        if any('__getattr__' in cls.__dict__ for cls in F.__mro__):
            raise ValueError('no foreign missing-attribute fallback')
        for name,expected in EXPECTED.items():
            prop=F.__dict__.get(name);slot=F.__dict__.get('_'+name)
            if type(prop) is not property or type(prop.fget) is not FunctionType or type(slot) is not MemberDescriptorType:
                raise ValueError('standard getter and owned slot '+name)
            fn=prop.fget
            if fn.__defaults__ is not None or fn.__kwdefaults__ is not None or fn.__closure__ is not None:
                raise ValueError('pure getter has no defaults or closure')
            if fn.__code__.co_names!=('_'+name,) or sha256(repr(code_shape(fn.__code__)).encode()).hexdigest()!=expected:
                raise ValueError('exact getter executable '+name)
            if slot.__objclass__ is not F or slot.__name__!='_'+name:
                raise ValueError('slot belongs to this exact Fraction class')
        accessor=next((c.__dict__['__getattribute__'] for c in F.__mro__ if '__getattribute__' in c.__dict__),None)
        if accessor is not object.__dict__['__getattribute__']:
            raise ValueError('ordinary object attribute lookup')
        return snapshot()
    except (ValueError,AttributeError,TypeError,KeyError) as error:
        if strict:raise ValueError('unsupported Fraction key getters: '+str(error)) from error
        return None
