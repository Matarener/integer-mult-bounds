#!/usr/bin/env python3
"""Exact integer search for native-free pre-Y/post-X involution controls."""
from itertools import product
import json
from pathlib import Path
import numpy as np

PAIRS = [0,0,0,1,1,2,2,3,3]
REVERSE = [False,True,False,True,False,True,False,True,False]
BRIDGES = [[], [(0,1,1)], [(0,1,-1)], [(1,2,1)], [(1,2,-1)], [(2,3,1)], [(2,3,-1)], [], [(3,2,1),(2,1,1),(1,0,1)]]
I=np.eye(8,dtype=np.int64)

def bridge(t,s,c):
    x=I.copy(); x[2*t,2*s]=c; x[2*s+1,2*t+1]=-c
    return x

def local(j,d,pre,post):
    p=PAIRS[j]; m=I.copy()
    b=np.array([[1,-1],[0,d]], dtype=np.int64) if REVERSE[j] else np.array([[d,0],[d,1]], dtype=np.int64)
    b[:,1]*=d**pre; b[0,:]*=d**post
    m[2*p:2*p+2,2*p:2*p+2]=b
    a,bv,c,e = map(int,b.ravel()); det=a*e-bv*c
    inv=I.copy(); inv[2*p:2*p+2,2*p:2*p+2]=np.array([[e,-bv],[-c,a]],dtype=np.int64)//det
    assert np.array_equal(m@inv,I)
    return m,inv

def block(j,d,c):
    m,inv=local(j,d,*c)
    for t,s,k in BRIDGES[j]:
        m=bridge(t,s,k)@m
        inv=inv@bridge(t,s,-k)
    assert np.array_equal(m@inv,I)
    return m,inv

def word(d,controls):
    m=I.copy()
    for j,c in enumerate(controls):m=block(j,d,c)[0]@m
    return m

def run():
    choices=list(product(range(2),repeat=2))
    target=word(1,[(0,0)]*9)
    stages=[[block(j,-1,c) for c in choices] for j in range(9)]
    prefix={}
    for cs in product(range(4),repeat=5):
        m=I.copy()
        for j,c in enumerate(cs):m=stages[j][c][0]@m
        prefix.setdefault(m.tobytes(),[]).append(cs)
    solutions=[]
    for cs in product(range(4),repeat=4):
        inv=I.copy()
        for j,c in zip(range(5,9),cs):inv=inv@stages[j][c][1]
        wanted=inv@target
        for pre in prefix.get(wanted.tobytes(),[]):
            cc=[choices[c] for c in pre+cs]
            assert np.array_equal(word(-1,cc),target)
            assert np.array_equal(word(1,cc),target)
            solutions.append(cc)
    result={'status':'EXACT_INTEGER_EXHAUSTIVE_SEARCH','num_patterns':4**9,'distinct_prefixes':len(prefix),'target':target.tolist(),'solutions':solutions,'solution_count':len(solutions)}
    print(json.dumps(result,indent=2))
    Path(__file__).with_name('CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run()
