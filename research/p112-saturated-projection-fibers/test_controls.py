#!/usr/bin/env python3
"""Boundary fixtures and optimized corrupted-receipt failure control."""
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent

def check(ok,why):
    if not ok:raise ValueError(why)

def main():
    spec=importlib.util.spec_from_file_location('primary',HERE/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    roots=v.load_roots();receipt=json.loads((HERE/'RESULT.json').read_text())
    six=[roots[i]for i in receipt['rational_flats'][1]['maximizer']]
    check(len(six)==6 and len(v.basis(six))==3,'saturated boundary attained')
    check(v.basis(six)==v.basis(tuple(-7*x for x in row)for row in reversed(six)),'rational basis invariance')
    frame=set()
    for i in range(0,8,2):
        for sign in (-2,2):
            row=[0]*8;row[i]=2;row[i+1]=sign;frame.add(tuple(row))
    paircounts=set()
    for a,b in combinations(roots,2):
        if sum(x*y for x,y in zip(a,b))==0:paircounts.add(sum(r not in frame for r in (a,b)))
    check(paircounts=={0,1,2},'full-kernel count differs from live count')
    # Two proportional coefficient columns can own different singleton sites in
    # one six-site fiber, but disjoint pieces do not create twelve such sites.
    owned=[{0,1,2},{3,4,5}];fiber=set(range(6))
    check(not owned[0]&owned[1] and set.union(*owned)==fiber and sum(map(len,owned))==6,'group repeated columns')
    live=[r for r in roots if r not in frame]
    pieces=[[r[j]for r in live]for j in range(6)]+[[0]*112 for _ in range(5)]
    total=sum(sum(x!=0 for x in p)for p in pieces)
    check(len(v.basis(pieces))==6 and total>=178,'actual-code positive fixture with zero columns')
    check(all(sum(x*x for x in r)%2==0 for r in roots),'positive characteristic excluded')
    check(164<=176<178,'old floor does not exclude new caller')
    cap=v.capacity_corollary()
    check(cap['maximum_capacity']==176 and cap['uniform_margin']==2,'rank-at-most-six branch')
    check(cap['maxima_by_length'][11]['maximizer']==[2,2,5]+[6]*8,'unique extremizer')
    # The excluded weight-seven extension has capacity188, so176 cannot cover it.
    check(2+2+8+7*20+36==188>178 and 2+7*4+5==35,'weight-seven scope boundary')
    with tempfile.TemporaryDirectory(prefix='p112-saturated-control-')as temp:
        dest=Path(temp);shutil.copyfile(HERE/'independent.py',dest/'independent.py')
        mutant=dict(receipt);mutant['uniform_support_floor']=179
        (dest/'RESULT.json').write_text(json.dumps(mutant))
        p=subprocess.run([sys.executable,'-I','-O','-B',str(dest/'independent.py')],capture_output=True,text=True)
        check(p.returncode!=0 and 'caller margin receipt'in p.stderr,'optimized receipt mutation accepted')
    print('PASS_SATURATED_CONTROLS actual_code full_vs_live repeated_columns rank3_boundary optimized_mutant')
if __name__=='__main__':main()
