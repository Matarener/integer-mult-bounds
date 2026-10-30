#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact algebraic calibration and actual CLI failures; OpenAI Codex assistance."""
import hashlib,json,pathlib,shutil,subprocess,sys,tempfile,types
from fractions import Fraction as Q
P=pathlib.Path(__file__).resolve().parent;ROOT=P.parents[1]
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
def load(text):
    m=types.ModuleType('binomial_test');exec(compile(text,'<binomial>','exec'),m.__dict__);return m
source=(P/'binomial.py').read_bytes();E=load(source)
# Known exact square-root ordering is an algebraically independent oracle.
for n in [1,8,64,256]:
    E.N=n
    for r in range(1,73):
        q=Q(73,r);lo,hi=E.power(q,Q(1,2))
        need(Q(lo,E.S)**2<=q<=Q(hi,E.S)**2,'square-root enclosure')
        need(E.power(q,Q(0))==(E.S,E.S),'exact zero power')
bad=load(source.replace(b'total_hi+tail',b'total_hi'))
bad.N=1;lo,hi=bad.unit(Q(2),Q(1,2))
need(Q(hi,bad.S)**2<2,'omitted-tail fault must break the algebraic oracle')
for args in [({0:1},Q(1,2),1),({1:-1},Q(1,2),1),({1:1},Q(-1),1)]:
    try:E.moment(*args)
    except ValueError:pass
    else:raise RuntimeError('invalid domain accepted')
def hashes(path):return {f.relative_to(path).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in path.rglob('*') if f.is_file()}
with tempfile.TemporaryDirectory(prefix='binomial40-controls-') as tmp:
    tmp=pathlib.Path(tmp);copy=tmp/'package';shutil.copytree(P,copy)
    before=hashes(copy)
    cmd=[sys.executable,'-B','-X','pycache_prefix='+str(tmp/'bytecode'),str(copy/'verify.py'),'--root',str(ROOT)]
    p=subprocess.run(cmd,capture_output=True,text=True)
    need(p.returncode==0,'Git-free copied package replay: '+p.stderr)
    need(hashes(copy)==before,'verifier changed package bytes')
    p=subprocess.run([sys.executable,'-O',*cmd[1:]],capture_output=True,text=True)
    need(p.returncode!=0 and 'enabled assertions' in p.stderr,'optimized interpreter refused')
    for file,field in [('CLAIM.json','kappa'),('RESULT.json','kappa')]:
        path=copy/file;raw=path.read_bytes();obj=json.loads(raw);obj[field]='1';path.write_text(json.dumps(obj))
        p=subprocess.run(cmd,capture_output=True,text=True)
        need(p.returncode!=0,'real CLI '+file+' mutation rejected');path.write_bytes(raw)
    path=copy/'SOURCES.json';raw=path.read_bytes();obj=json.loads(raw);obj['files']=[];path.write_text(json.dumps(obj))
    p=subprocess.run(cmd,capture_output=True,text=True)
    need(p.returncode!=0 and 'complete source manifest' in p.stderr,'source pin removal refused')
    path.write_bytes(raw)
    need(hashes(copy)==before,'controls restored copy')
print('PASS_BINOMIAL40_CONTROLS sqrt_cases=288 zero_cases=288 tail_fault=1 domain_faults=3 cli_faults=4 readonly_export=1')
