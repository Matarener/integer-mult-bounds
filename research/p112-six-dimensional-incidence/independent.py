#!/usr/bin/env python3
"""Independent Gram-matrix upper bound, with no primary or geometry imports.
Chris R / Clear1nsight with OpenAI Codex assistance. Apache-2.0.
The 23-pattern certificate was supplied by a separate conceptual-review agent.
"""
from collections import Counter
from hashlib import sha256
from itertools import product, permutations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def check(ok,message):
    if not ok:raise ValueError(message)

def gram_bound():
    cases=[]
    for a,b,c in product((-1,0,1),repeat=3):
        det=8+2*a*b*c-2*(a*a+b*b+c*c)
        if det<=0:continue
        adj=((4-c*c,b*c-2*a,a*c-2*b),
             (b*c-2*a,4-b*b,a*b-2*c),
             (a*c-2*b,a*b-2*c,4-a*a))
        targets=[]
        for k in product(range(-2,3),repeat=3):
            quadratic=sum(k[i]*adj[i][j]*k[j] for i in range(3) for j in range(3))
            if quadratic==2*det:targets.append(k)
        check(all(tuple(-x for x in k) in targets for k in targets),'opposite root absent')
        cases.append({'off_diagonal':[a,b,c],'determinant':det,'signed_targets':len(targets)})
    check(len(cases)==23,'positive definite Gram pattern count')
    check(Counter(x['signed_targets'] for x in cases)=={6:1,8:6,12:16},'Gram target histogram')
    return cases

def determinant(matrix):
    n=len(matrix);answer=0
    for order in permutations(range(n)):
        value=(-1)**sum(order[i]>order[j] for i in range(n) for j in range(i+1,n))
        for i in range(n):value*=matrix[i][order[i]]
        answer+=value
    return answer

def gram4_bound():
    cases=[]
    for a,b,c,d,e,f in product((-1,0,1),repeat=6):
        g=((2,a,b,c),(a,2,d,e),(b,d,2,f),(c,e,f,2))
        if any(determinant([r[:k] for r in g[:k]])<=0 for k in range(1,5)):continue
        det=determinant(g)
        adj=[[(-1)**(i+j)*determinant([[g[a][b] for b in range(4) if b!=i] for a in range(4) if a!=j]) for j in range(4)] for i in range(4)]
        count=0
        for k in product(range(-2,3),repeat=4):
            if sum(k[i]*adj[i][j]*k[j] for i in range(4) for j in range(4))==2*det:count+=1
        cases.append([[a,b,c,d,e,f],det,count])
    hist=Counter(c[2] for c in cases)
    check(hist=={10:12,12:12,14:64,20:200,24:105},'rank4 Gram histogram')
    return {'patterns':len(cases),'candidate_vectors':len(cases)*625,'signed_target_histogram':{str(k):hist[k] for k in sorted(hist)},'maximum_lines':12,'case_digest':sha256(json.dumps(cases,separators=(',',':')).encode()).hexdigest()}

def original_functions():
    path=ROOT/'research/p112-b6-t4-reconciliation/vendor/bk2b.py'
    namespace={};exec(compile(path.read_text().split('import sys')[0],str(path),'exec'),namespace)
    return namespace

def main():
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage']=='input':check(sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'source changed')
    receipt=json.loads((HERE/'RESULT.json').read_text())
    cases=gram_bound()
    check(max(x['signed_targets'] for x in cases)//2==receipt['rational_flats'][1]['maximum']==6,'rank-three bound')
    check(gram4_bound()==receipt['rank4_gram'],'independent rank4 Gram certificate')
    old=original_functions()
    for c in receipt['callers']:
        w=c['weights'];check(old['feasible'](w,6) and not old['killed'](w,6),'original filter rejects caller')
        check(sum(x-2 for x in w)<36 and len(w)==11,'historical cell')
        cap=sum({2:2,3:4,4:8,5:12,6:20,7:36}[x] for x in w)
        bounds=[(19*(112-z)-55*(12-z)+8)//9 for z in range(4)]
        check(bounds==[164,168,172,176] and cap<min(bounds),'pair incidence optimization')
        check(c['contradiction_margin']==min(bounds)-cap,'caller margin')
    print('PASS_P112_INCIDENCE_INDEPENDENT 23_Gram3_and393_Gram4_patterns root_caps6,12 caller_margins8,16')
if __name__=='__main__':main()
