"""Authenticate eight canonical inputs before isolated source execution."""
import ast
from hashlib import sha1,sha256
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SEAL='826d4dcdc29c66b7395bad8de9201dafee12aa5aa0eaf2772b14e621439daf44'
PREFIX='research/selected-bit-physical-caller/inputs/pr2753/'


def need(ok,message):
    if not ok:raise ValueError(message)


def authenticate():
    raw=(HERE/'SOURCES.json').read_bytes()
    need(sha256(raw).hexdigest()==SEAL,'sealed source inventory')
    result={}
    for row in json.loads(raw)['files']:
        if row['usage']!='input':continue
        data=(ROOT/row['path']).read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'source SHA256: '+row['path'])
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'source Git blob')
        result[row['path']]=data
    need(len(result)==8,'complete eight-source closure')
    return result


def source_module(name,path,raw):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    exec(compile(raw,str(path),'exec',optimize=0),module.__dict__)
    return module


def load():
    data=authenticate();modules={}
    for name in ('words','records','stream','cardinality','counts'):
        path=PREFIX+'predecessor/vendor/'+name+'.py'
        modules[name]=source_module(name,ROOT/path,data[path])
    path=PREFIX+'predecessor/cardinal_counts.py'
    modules['cardinal_counts']=source_module('cardinal_counts',ROOT/path,data[path])
    path=PREFIX+'layout.py'
    modules['layout']=source_module('layout',ROOT/path,data[path])
    # Only Geometry is needed. Native forms/Callback/field admission are not
    # executed, imported, or certified by this child-geometry interval.
    path=PREFIX+'predecessor/vendor/numeric.py'
    tree=ast.parse(data[path]);node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Geometry')
    ns={'Unsigned':modules['words'].Unsigned,'need':need}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(ROOT/path),'exec',optimize=0),ns)
    modules['Geometry']=ns['Geometry']
    # A private exact Counter class borrows one permanent blank record role.
    tree=ast.parse(data[PREFIX+'predecessor/vendor/stream.py'])
    node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Counter')
    def counter_type(workspace):
        ns=dict(modules['stream'].__dict__);ns['Tape']=lambda:workspace
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<pinned-counter>','exec',optimize=0),ns)
        return ns['Counter']
    modules['counter_type']=counter_type
    return SimpleNamespace(**modules)


def adapt(env,powers):
    """Preserve the entire frozen method except its three power invocations."""
    raw=authenticate()[PREFIX+'layout.py'];tree=ast.parse(raw)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Layout')
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='child_extents')
    found=[]
    class Rewrite(ast.NodeTransformer):
        def visit_Expr(self,node):
            value=node.value
            if isinstance(value,ast.Call) and isinstance(value.func,ast.Name) and value.func.id=='multiply_atom_power':
                found.append(tuple(ast.unparse(a) for a in value.args))
                if len(found)<3:return ast.copy_location(ast.Pass(),node)
                return ast.copy_location(ast.parse('_shared([(pre,a),(middle,between),(tail,after)], self.ring, self.q)').body[0],node)
            return self.generic_visit(node)
    fn=Rewrite().visit(fn);ast.fix_missing_locations(fn)
    need(found==[('pre','a','self.ring','self.q'),('middle','between','self.ring','self.q'),
                 ('tail','after','self.ring','self.q')],'exact three-power source method shape')
    ns=dict(env.layout.__dict__);ns['_shared']=powers.multiply
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'<adapted-child-extents>','exec',optimize=0),ns)
    return ns['child_extents']
