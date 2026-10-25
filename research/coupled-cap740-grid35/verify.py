#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound arithmetic refinement of PR3148; unchanged supplier reused.

No cold native replay or new physical construction is claimed. Retained
engines and the original full-port/native/invoice evidence keep their credit.
Prepared with substantial OpenAI Codex assistance.
"""
import argparse
import ast
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap
from fractions import Fraction as Q
import types
import uuid

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
BASE=ROOT/'research/coupled-carrier-cap740'
SUPPLIER=ROOT/'research/gmx-t74-borrow43-handoff'
SOURCE_MANIFEST_SHA256='5bb835aa40d21cdf9027a331f4c7a433e950864b798b160f2566419f9097c9e6'


def need(ok,why):
    if not ok:raise ValueError(why)


def read(path):return json.loads(path.read_bytes())


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,value):
    path.write_bytes((json.dumps(value,indent=2,sort_keys=True)+'\n').encode())


def load(path,name):
    # Compile authenticated source directly, avoiding stale bytecode imports.
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def authenticate():
    need(sha(P/'SOURCES.json')==SOURCE_MANIFEST_SHA256,'complete source manifest and usage classes')
    for item in read(P/'SOURCES.json')['files']:
        if item['usage']=='input':
            need(sha(ROOT/item['path'])==item['sha256'],'source drift: '+item['path'])
    manifest=read(BASE/'MANIFEST.json')
    actual={p.relative_to(BASE).as_posix():sha(p) for p in BASE.rglob('*')
            if p.is_file() and p!=BASE/'MANIFEST.json'}
    need(actual==manifest,'unchanged complete predecessor package')


def calculate():
    authenticate()
    baseline=read(BASE/'evidence/COMPOSITION-RESULT.json')
    profile={int(r):n for r,n in baseline['profile'].items()}
    need(profile=={1:16376940,2:4821840,3:1567431,4:679320,5:147075,8:53280,48:282569},'complete fixed bill')
    need(sum(r*n for r,n in profile.items())==65088*740,'rank mass')
    old=Q(baseline['kappa'])
    engine=load(ROOT/'research/rank7-joint-endframes/tools/root.py','credited_root')
    lo,hi=engine.kappa_from_profile(profile,740,digits=40)
    C=Q((lo*10**35).__floor__(),10**35)
    K=C-Q(1,10**57)-Q(1,10**81)
    need(old<K<C<=lo<hi<C+Q(1,10**35),'strict gain and root bracket')
    second=load(ROOT/'research/two-sided-helper-extraction/tools/audit_moment.py','credited_independent_moment')
    moments=[]
    for E in (engine,second):
        below=E.moment(profile,C,896*740);above=E.moment(profile,C+Q(1,10**35),896*740)
        need(below[1]<1<above[0],'accept endpoint and reject next grid')
        for r in (1,48):
            bad=dict(profile);bad[r]+=1
            need(E.moment(bad,C,896*740)[0]>1,'extra unpaid child must reject')
        moments.append(dict(source_sha256=sha(Path(E.__file__)),upper_minus_one=str(below[1]-1),
                            successor_lower_minus_one=str(above[0]-1)))
    return dict(profile=profile,complex_lower=str(C),kappa=str(K),previous=str(old),gain=str(K-old),
                root_lower=str(lo),root_upper=str(hi),moments=moments)


def bootstrap(C):
    source=(SUPPLIER/'code/assemble.py').read_text()
    node=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef) and n.name=='_outer_witness_raw')
    body=textwrap.dedent('\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])+'\n')
    E=ROOT/'research/adaptive-kernel-demotion/vendor/engines/outer.py'
    need(sha(E)=='c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c','47-row engine')
    env=dict(Q=Q,mpz=int,hashlib=hashlib,PAYLOAD=2048,c=Q('0.001733427039589844234749'),
             SPEC=dict(outer_refinement=dict(endpoint_digits=35,grid_digits=29,margin_digits=39,bootstrap_steps=12)),
             A=load(E,'retained_assembly'))
    exec(compile(body,'<retained _outer_witness_raw>','exec'),env)
    k,cuts,outer,controls=env['_outer_witness_raw'](C)
    need(len(outer['strict_constraints'])==47 and all(v>0 for v in outer['strict_constraints'].values()),'all47 bootstrap constraints')
    need(len(cuts)==13 and len(controls)==4,'12 steps and four original controls')
    return dict(legacy_balanced_kappa=str(k),cutoffs=cuts,controls=controls,
                strict_constraints={n:str(v) for n,v in outer['strict_constraints'].items()})


def outer(arithmetic,work):
    admission=read(BASE/'evidence/ADMISSION-RESULT.json')
    patch=next(p for p in admission['patches'] if p['path']=='outer/check_ledger.py')
    raw=(SUPPLIER/'outer/check_ledger.py').read_bytes()
    need(hashlib.sha256(raw).hexdigest()==patch['before_sha256'],'outer preimage')
    text=raw.decode().replace('\r\n','\n')
    for before,after in patch['replacements']:
        need(text.count(before)==1,'one exact predecessor outer patch')
        text=text.replace(before,after)
    need(hashlib.sha256(text.encode()).hexdigest()==patch['after_sha256'],'exact admitted outer checker')
    (work/'outer').mkdir();(work/'new').mkdir()
    (work/'outer/check_ledger.py').write_bytes(text.encode())
    other=SUPPLIER/'outer/independent_check.py'
    stage=next(s for s in admission['stages'] if s['name']=='outer-independent_check.py')
    need(sha(other)==stage['script_sha256'],'exact independent checker')
    (work/'outer/independent_check.py').write_bytes(other.read_bytes())
    C=Q(arithmetic['complex_lower']);K=Q(arithmetic['kappa'])
    save(work/'new/SPEC.json',dict(geometry=dict(dimension=73,replicas=740),
         expected=dict(complex_lower=str(C),kappa=arithmetic['previous'],global_profile=arithmetic['profile'],live=896*740),
         outer_refinement=dict(endpoint_digits=35)))
    save(work/'CLAIM.json',dict(kappa=str(K),scope='Conditional fixed-supplier arithmetic refinement'))
    save(work/'outer/B.json',dict(b=str(C-Q(1,10**115)),b_above_endpoint=str(C+Q(1,10**35)),
                                 profile=arithmetic['profile'],live=896*740))
    for name in ('check_ledger.py','independent_check.py'):
        # Separate interpreter with a fresh bytecode namespace; assertions stay on.
        with (work/(name+'.log')).open('w') as log:
            subprocess.run([sys.executable,'-B','-X','pycache_prefix='+str(work/'pycache'),str(work/'outer'/name)],
                           check=True,stdout=log,stderr=subprocess.STDOUT)
    ledger=read(work/'outer/LEDGER.json');row=ledger['rows']['struct_boundary_radix_union']
    need(Q(row['kappa']['rational'])==K,'actual derived endpoint')
    need(len(row['strict_checks'])==63 and all(Q(v['rational'])>0 for v in row['strict_checks'].values()),'all63 outer rows')
    controls=ledger['rejecting_controls']['struct_boundary_radix_union']
    need(len(controls)==17 and all(v and all(Q(w['rational'])<=0 for w in v.values()) for v in controls.values()),'all17 original controls')
    balance=read(work/'outer/INDEPENDENT.json')
    need(balance['status']=='PASS_INDEPENDENT_BALANCE_DERIVATION' and
         Q(balance['rows']['struct_boundary_radix_union']['kappa'])==K,'independent endpoint derivation')
    return dict(ledger=ledger,independent=balance)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path)
    a=ap.parse_args()
    need(not sys.flags.optimize,'retained outer checkers require assertions')
    need(not a.output or not a.output.exists(),'output must be fresh')
    arithmetic=calculate()
    claim=read(P/'CLAIM.json')
    for key in ('kappa','complex_lower','previous','gain'):
        need(claim[key]==arithmetic[key],'exact public claim '+key)
    need(claim['endpoint_digits']==35 and claim['fresh_native_replay'] is False and
         claim['selected_frontier_changed'] is False,'public scope flags')
    need(type(claim['physical']) is int and claim['physical']==663549 and
         type(claim['private_zero_buffers']) is int and claim['private_zero_buffers']==91,'public physical bill')
    need(all(type(n) is int for n in claim['profile'].values()) and
         {int(r):n for r,n in claim['profile'].items()}==arithmetic['profile'],'public paid profile')
    baseline=load(BASE/'verify_release.py','retained_release').check()
    invoice=json.loads(gzip.decompress((BASE/'evidence/PREFIX-AND-INVOICE.json.gz').read_bytes()))
    need(len(invoice['strict_checks'])==9 and all(v is True for v in invoice['strict_checks'].values()),'nine fixed finite guards')
    need((invoice['physical'],invoice['private_zero_buffers'],invoice['global_prefix_bits'],invoice['charged_prefix_bits'])==
         (663549,91,1479,2048),'unchanged full physical and prefix bill')
    work=Path(os.environ.get('TMP',os.environ.get('TEMP','.'))).resolve()/('cap740-grid35-'+uuid.uuid4().hex)
    work.mkdir()
    try:
        fresh_outer=outer(arithmetic,work)
        boot=bootstrap(Q(arithmetic['complex_lower']))
        result=dict(status='PASS_COUPLED_CAP740_GRID35_CONDITIONAL_REFINEMENT',arithmetic=arithmetic,
                    profile_unchanged=True,finite_guards=invoice['strict_checks'],physical=663549,private_zero_buffers=91,
                    native_replay='Inherited unchanged PR3148 source-bound native evidence; no fresh native replay',
                    invoice_payload_sha256=hashlib.sha256(gzip.decompress((BASE/'evidence/PREFIX-AND-INVOICE.json.gz').read_bytes())).hexdigest(),
                    baseline_release=baseline,bootstrap=boot,outer=fresh_outer,
                    scope='Conditional fixed-supplier precision refinement; inherited physical/compiler/all-size assumptions remain')
        expected=read(P/'RESULT.json')
        encode=lambda value:json.dumps(json.loads(json.dumps(value)),sort_keys=True,separators=(',',':'))
        need(encode(result)==encode(expected),'fresh complete scoped result differs from published receipt')
        if a.output:save(a.output,result)
        print(result['status'],'gain',arithmetic['gain'])
    finally:
        need(work.parent==Path(os.environ.get('TMP',os.environ.get('TEMP','.'))).resolve() and
             work.name.startswith('cap740-grid35-'),'safe private work cleanup')
        shutil.rmtree(work)


if __name__=='__main__':main()
