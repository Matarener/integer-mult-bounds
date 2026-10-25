"""Exact source pins; isolated coefficient/tariff extraction without imports."""
import ast
from fractions import Fraction
from hashlib import sha1,sha256
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MANIFEST_SHA256='70a871edd82b326c9d625e9309387c8a6c9a9fdb5a6a59140db488b337db1d6d'


def need(ok,message):
    if not ok:raise ValueError(message)


def authenticate():
    manifest=(HERE/'SOURCES.json').read_bytes()
    need(sha256(manifest).hexdigest()==MANIFEST_SHA256,'sealed source inventory SHA256')
    pins={}
    for r in json.loads(manifest)['files']:
        if r['usage']!='input':continue
        raw=(ROOT/r['path']).read_bytes()
        need(sha256(raw).hexdigest()==r['sha256'],'source SHA256: '+r['path'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'],'source Git blob')
        pins[r['path']]=r['sha256']
    return pins


def oracles():
    authenticate()
    path=ROOT/'research/h6-compensation-network/construction/network.py'
    tree=ast.parse(path.read_text())
    edge=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='edge_records')
    assign=next(n for n in ast.walk(edge) if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='coefficient' for t in n.targets))
    code=compile(ast.Expression(assign.value),str(path),'eval')
    def coefficient(pairing,same=False):
        return eval(code,{'Q':Fraction,'source':0,'target':0 if same else 1,'pairing':pairing})
    tariff_path=ROOT/'research/e8-complex-gauge-kernel/code/emit_gk.py'
    tree=ast.parse(tariff_path.read_text())
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='primitive_bound')
    namespace={'Q':Fraction}
    exec(compile(ast.Module(body=[function],type_ignores=[]),str(tariff_path),'exec',optimize=0),namespace)
    def tariff(q):
        q=Fraction(q)
        return namespace['primitive_bound'](['add',0,1,q.numerator,q.denominator])
    return coefficient,tariff


def helper_terms_oracle():
    authenticate()
    path=ROOT/'research/h6-compensation-network/pricing/verify.py'
    tree=ast.parse(path.read_text())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='helper_terms')
    namespace={'F':Fraction,'H':17,'require':need}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),str(path),'exec',optimize=0),namespace)
    return namespace['helper_terms']
