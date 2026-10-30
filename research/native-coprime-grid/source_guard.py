"""Execute only the pinned production_axis AST, with host Count semantics.
This is not a replay of the encoded physical-tape implementation.
Following ToikY's PR4029 source-binding method; new adapter by Dugongue.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import ast
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from hashlib import sha256

PIN='474730f42fcd2bd24720af4e08c71fb51cc374c3e16b8b6d7e565900f1a9e7c3'

def need(ok,msg):
    if not ok:raise ValueError(msg)

class Count:
    def __init__(self,x):self.value=x.value if isinstance(x,Count) else int(x)
    @classmethod
    def literal(cls,x):return cls(x)
    @classmethod
    def product(cls,a,b):return cls(a.value*b.value)
    def multiply_small(self,n):self.value*=n
    def add(self,x):self.value+=x.value

@contextmanager
def owned(*items):yield items

def subtract(a,b):
    need(a.value>=b.value,'natural subtraction')
    return Count(a.value-b.value)

def compare(a,b):return (a.value>b.value)-(a.value<b.value)

def load():
    data=(Path(__file__).parent/'source/tensor_plan.py').read_bytes()
    need(sha256(data).hexdigest()==PIN,'pinned production source changed')
    tree=ast.parse(data)
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='TensorPlan')
    method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='production_axis')
    env=dict(owned=owned,Count=Count,subtract=subtract,compare=compare,need=need)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),
                 'pinned_production_axis','exec'),env)
    return env['production_axis']

def check(moduli,targets,halo=1,width=1):
    need(len(moduli)==len(targets) and len(moduli)>0,'shape')
    f=load();d=len(moduli)+1
    obj=SimpleNamespace(d=Count(d),target_halo=Count(halo),w=Count(width))
    for s,t in zip(moduli,targets):f(obj,Count(s),Count(t))
