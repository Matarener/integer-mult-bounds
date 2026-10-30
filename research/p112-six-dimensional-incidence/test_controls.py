#!/usr/bin/env python3
"""Failure controls for rank, common zeros, field scope and receipt integrity.
Chris R / Clear1nsight with OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
from pathlib import Path
import json
from itertools import combinations
import subprocess
import sys
import tempfile
import shutil

HERE=Path(__file__).resolve().parent

def check(ok,message):
    if not ok:raise ValueError(message)

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def main():
    v=load('verify');ind=load('independent');roots=v.load_roots();r=json.loads((HERE/'RESULT.json').read_text())
    maximizing=[roots[i] for i in r['rational_flats'][1]['maximizer']]
    check(len(maximizing)==6 and len(v.basis(maximizing))==3,'rank-three extremizer')
    check(v.basis(maximizing)==v.basis(tuple(-7*x for x in row) for row in reversed(maximizing)),'rational rescaling invariance')
    d4=[row for row in roots if all(x==0 for x in row[4:])]
    check(len(d4)==12 and len(v.basis(d4))==4,'rank-four boundary blocks extrapolation')
    cases=ind.gram_bound();check(len(cases)==23,'all nonsingular Gram patterns')
    # At zero radical count the old weight-only relaxation is too weak.
    check(2*109-11*6==152 and 152<=156<224-11*6,'improvement is essential')
    check([224-66+9*z for z in range(4)]==[158,167,176,185],'shared-zero charges')
    check(ind.gram4_bound()['maximum_lines']==12,'rank4 Gram maximum')
    check([(19*(112-z)-55*(12-z)+8)//9 for z in range(4)]==[164,168,172,176],'pair incidence integer ceiling')
    # Honest actual-code positive fixture, with two common zero coordinates.
    frame=set()
    for i in range(0,8,2):
        for sign in (-2,2):
            row=[0]*8;row[i]=2;row[i+1]=sign;frame.add(tuple(row))
    live=[r for r in roots if r not in frame]
    chosen=(0,1,2,3,4,6)
    pieces=[[r[j] for r in live] for j in chosen]
    zero=[t for t in range(112) if all(p[t]==0 for p in pieces)]
    singleton=[sum(p[t]!=0 and sum(q[t]!=0 for q in pieces)==1 for t in range(112)) for p in pieces]
    total=sum(sum(x!=0 for x in p) for p in pieces)
    check(len(zero)==2 and all(s+len(zero)<=6 for s in singleton),'actual code fiber bound')
    check(2*(112-len(zero))<=total+sum(singleton),'actual incidence count')
    check(total>=224-6*len(pieces)+(len(pieces)-2)*len(zero),'actual support floor')
    multiplicities=[sum(p[t]!=0 for p in pieces) for t in range(112) if t not in zero]
    n=len(pieces);u=multiplicities.count(1);vv=multiplicities.count(2);ww=sum(m>=3 for m in multiplicities)
    check((n-1)*u+vv<=n*(n-1)//2*(12-len(zero)),'actual pair count')
    check(total>=2*(112-len(zero))-u+ww,'actual multiplicity lower bound')
    # Characteristic two destroys doubled-root norm and injective evaluation.
    check(all(sum(x*x for x in row)%2==0 for row in roots),'characteristic two excluded')
    # Corrupt an on-disk result and run the separate optimized checker; it must fail.
    with tempfile.TemporaryDirectory(prefix='p112-incidence-control-') as temp:
        root=Path(temp);dest=root/'research'/HERE.name
        shutil.copytree(HERE,dest)
        for entry in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if entry['usage']=='input':
                out=root/entry['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HERE.parents[1]/entry['path'],out)
        target=dest/'RESULT.json';target.chmod(target.stat().st_mode|0o200)
        mutant=json.loads(target.read_text());mutant['callers'][0]['contradiction_margin']=9;target.write_text(json.dumps(mutant))
        proc=subprocess.run([sys.executable,'-I','-O','-B',str(dest/'independent.py')],capture_output=True,text=True)
        check(proc.returncode!=0 and 'caller margin' in proc.stderr,'optimized mutated receipt accepted')
    print('PASS_P112_INCIDENCE_CONTROLS rank3_attainment rank4_boundary common_zero actual_code char2 optimized_receipt_mutant')
if __name__=='__main__':main()
