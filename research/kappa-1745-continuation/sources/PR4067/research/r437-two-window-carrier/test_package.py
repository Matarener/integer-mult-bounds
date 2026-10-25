#!/usr/bin/env python3
"""Separate scalar-column replay and actual CLI mutation controls."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('exchange_verifier',P/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def need(ok,msg):
    if not ok: raise RuntimeError(msg)

def column_replay(w,k):
    # Deliberately one Boolean column, no bit-matrix, builder or certificate.
    z=[int(i==k) for i in range(659)]
    for sec in ['D','A','B','C']:
        if sec=='B':
            copies=[z[r] for r in w['ret']]
            for i,js in enumerate(w['scatter']):
                for j in js:z[111+i]^=copies[j]
        for _,d,ss in w[sec]:
            for s in ss:z[d]^=z[s]
    wanted=[int(i==k) ^ int(i==k+111 and k<111) for i in range(659)]
    need(z==wanted,'independent Boolean-column identity '+str(k))

def main():
    w=v.load();c=json.loads((P/'CANDIDATE.json').read_text());dims=v.geometry(w)
    for k in range(659): column_replay(c,k)
    controls=[]
    def reject(name,x):
        try:v.ledger(x,dims)
        except v.Reject:controls.append(name)
        else:raise RuntimeError('mutant accepted: '+name)
    x=deepcopy(c);x['D']=deepcopy(w['D']);reject('stale dirty compensation',x)
    x=deepcopy(c);x['C']=x['C'][:-1];reject('missing literal cleanup',x)
    x=deepcopy(c);x['A'].remove([509,467,[413]]);reject('missing delayed debt',x)
    x=deepcopy(c)
    for g in x['A']:
        if g[0]==509:g[2]=[77 if s==469 else s for s in g[2]]
    reject('unpaid direct source77 and actual B35 descent',x)
    x=deepcopy(c)
    at=x['A'].index([509,467,[413]]);x['A'].insert(at,[186,444,[77]])
    reject('early source92 then old source77 frame descent',x)
    x=deepcopy(c);x['A'].insert(0,deepcopy(w['B'][35]));reject('move target observation before scatter',x)
    for name,position in [('clear before last low observation',68),('clear after first source write',284)]:
        x=deepcopy(c);clear=x['B'].pop(69);x['B'].insert(position,clear)
        x['C']=[[1,d,ss] for f,d,ss in reversed(x['A']+x['B']) if not 111<=d<222]
        reject(name,x)
    x=deepcopy(c);x['B'].pop(69);x['C']=[[1,d,ss] for f,d,ss in reversed(x['A']+x['B']) if not 111<=d<222];reject('missing delayed cleanup',x)
    # Literal output contract at the original later read is the repair, while
    # the borrowed bank may retain a source row until C restores every column.
    old=v.ledger(w,dims);new=v.ledger(c,dims)
    need(old['capture_source_rows']==new['capture_source_rows'],'nine source capture rows')
    need(old['source_writes']==new['source_writes'],'source write histories')
    # Elementary majorization witness: each transfer balances unequal entries.
    vectors=[[6,2,2,0],[5,3,2,0],[4,3,3,0],[3,3,3,1]]
    for a,b in zip(vectors,vectors[1:]):
        diff=[b[i]-a[i] for i in range(4)]
        giver=diff.index(-1);taker=diff.index(1)
        need(sorted(diff)==[-1,0,0,1] and a[giver]>a[taker]+1,'strict concavity transfer')
    with tempfile.TemporaryDirectory() as t:
        q=Path(t)/'package';shutil.copytree(P,q,ignore=shutil.ignore_patterns('__pycache__'))
        cmd=[sys.executable,'-I','-B','-OO',str(q/'verify.py')]
        def run(ok):
            r=subprocess.run(cmd,cwd=t,capture_output=True,text=True,timeout=60)
            need((r.returncode==0)==ok,'optimized Git-free CLI outcome: '+r.stdout+r.stderr)
        run(True)
        hs=importlib.util.spec_from_file_location('chunk_loader',q/'host.py')
        hm=importlib.util.module_from_spec(hs);hs.loader.exec_module(hm)
        payload=hm.candidate_template_bytes()
        manifest=q/'CANDIDATE-TEMPLATE.json';mb=manifest.read_bytes();m=json.loads(mb)
        chunk=q/m['parts'][0]['path'];cb=chunk.read_bytes()
        def reject_chunk():
            try:hm.candidate_template_bytes()
            except (hm.v.Reject,OSError):pass
            else:raise RuntimeError('candidate chunk mutation accepted')
        chunk.write_bytes(bytes([cb[0]^1])+cb[1:]);reject_chunk();chunk.write_bytes(cb)
        chunk.unlink();reject_chunk();chunk.write_bytes(cb)
        changed=json.loads(mb);changed['parts'][0],changed['parts'][1]=changed['parts'][1],changed['parts'][0];manifest.write_text(json.dumps(changed));reject_chunk()
        changed=json.loads(mb);changed['sha256']='0'*64;manifest.write_text(json.dumps(changed));reject_chunk();manifest.write_bytes(mb)
        need(hm.candidate_template_bytes()==payload,'candidate chunks restored exactly')
        b=(q/'RESULT.json').read_bytes();(q/'RESULT.json').write_text('{}');run(False);(q/'RESULT.json').write_bytes(b)
        b=(q/'CANDIDATE.json').read_bytes();y=json.loads(b);y['A'][0][1]=1;(q/'CANDIDATE.json').write_text(json.dumps(y));run(False);(q/'CANDIDATE.json').write_bytes(b)
        f=q/'inputs/R437-COMPOSED-WORD.json.gz';b=f.read_bytes();f.write_bytes(b+b'corruption');run(False);f.write_bytes(b)
        (q/'inputs/UPSTREAM-NOTICE.md').unlink();run(False)
    print('PASS_TWO_WINDOW_INDEPENDENT_COLUMNS_659', 'semantic_controls='+str(len(controls)), 'Git_free_optimized=PASS cli_rejections=4 chunk_rejections=4 majorization_transfers=3')
if __name__=='__main__':main()
