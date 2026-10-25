#!/usr/bin/env python3
"""Portable exact finite identities; written proofs carry the quantified bounds."""
import ast, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def need(ok,message):
    if not ok: raise ValueError(message)

def load(name):
    path=ROOT/name; raw=path.read_bytes()
    expected=json.loads((ROOT/'CONTENT-SHA256.json').read_text())[name]
    need(hashlib.sha256(raw).hexdigest()==expected,'source hash: '+name)
    need(not any(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(raw))),'optimization-sensitive assert: '+name)
    ns={'__file__':str(path),'__name__':'authenticated_'+name.replace('.','_')}
    # dataclasses resolve their own module; use a fresh registered module.
    import types,sys
    module=types.ModuleType(ns['__name__']);module.__dict__.update(ns);sys.modules[module.__name__]=module
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module.__dict__

def main():
    manifest=json.loads((ROOT/'CONTENT-SHA256.json').read_text())
    for name,h in manifest.items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,'content hash: '+name)
    load('witness.py')['main']()
    q=load('quartic_opposite_gate.py'); need(json.loads(json.dumps(q['receipt']()))==json.loads((ROOT/'QUARTIC-OPPOSITE-GATE.json').read_text()),'quartic fixture')
    z=load('zero_helper_scan.py');need(z['receipt']()==json.loads((ROOT/'ZERO-HELPER-SCAN-COUNTEREXAMPLE.json').read_text()),'scan fixture')
    a=load('independent.py');a['main']()
    for label,ns in [('quartic',q),('independent',a)]:
        try:ns['need'](False,'forced explicit failure')
        except (RuntimeError,ValueError):pass
        else:raise ValueError('false check accepted: '+label)
    print('PASS_FIXED_SUPPORT_UNARY_QUERY_BOUNDS all_m_written_proofs finite_exact_witnesses no_new_kappa')

if __name__=='__main__':main()
