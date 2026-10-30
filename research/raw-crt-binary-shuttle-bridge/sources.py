# SPDX-License-Identifier: Apache-2.0
"""Authenticated source bytes and exact Raw descriptor constants."""
import ast
import builtins
import hashlib
import json
from pathlib import Path
import types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,why):
    if not ok:raise ValueError(why)

def authenticate():
    values={}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            raw=(ROOT/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source changed: '+row['path'])
            values[row['path']]=raw
    return values

def load():
    raw=authenticate();prefix='research/literal-elementary-interchange/'
    program=types.ModuleType('retained_program')
    exec(compile(raw[prefix+'program.py'],'<retained program>','exec'),program.__dict__)
    machine=types.ModuleType('retained_machine')
    def imports(name,*a,**k):
        need(name=='program','declared machine import');return program
    machine.__dict__['__builtins__']=dict(vars(builtins),__import__=imports)
    exec(compile(raw[prefix+'machine.py'],'<retained machine>','exec'),machine.__dict__)
    binary=types.ModuleType('retained_binary')
    exec(compile(raw['research/binary-elementary-interchange/binary_machine.py'],'<retained binary>','exec'),binary.__dict__)
    tree=ast.parse(raw['research/standalone-elementary-crt-raw/raw.py'])
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Raw')
    init=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    geometry={}
    for node in init.body:
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Attribute) and node.targets[0].attr in ('u','t'):
            geometry[node.targets[0].attr]=ast.literal_eval(node.value.args[0].generators[0].iter)
    need(geometry=={'u':(2,1,1024,12),'t':(2,4,256,12)},'actual source shuttle geometries')
    return program,machine,binary,geometry
PROGRAM,MACHINE,BINARY,ACTUAL=load()
