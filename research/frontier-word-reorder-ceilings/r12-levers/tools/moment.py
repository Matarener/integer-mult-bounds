"""Reproduce PR4610 p16 moment invoice; float root finder for screening."""
import sys, json, importlib.util
from pathlib import Path
from collections import Counter
ROOT=Path.home()/'imb-r12'
A=ROOT/'research/kappa-round6-compiler-tightening-20261022'
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m
sys.path.insert(0,str(A))
ar=load(A/'arithmetic.py','ar')
LOCAL={'helpers':{4:28,7:7,8:47,9:326},'paid':{1:2201,2:412,3:510,4:127,5:40,8:8}}
def invoice(local=LOCAL):
    H,N,T,P,word=ar.assemble(local); return H,N,T,P,word
def margin(T,P,C):
    return sum(n*k**(1-C) for k,n in T.items())-sum(n*r**(1-C) for r,n in P.items())
def root(T,P,lo=0.0,hi=0.5):
    for _ in range(200):
        m=(lo+hi)/2
        if margin(T,P,m)>0: lo=m
        else: hi=m
    return lo
if __name__=='__main__':
    H,N,T,P,word=invoice()
    print('T',dict(sorted(T.items())));print('P',dict(sorted(P.items())))
    print('events',Counter(e[0] for e in word['physical_events']))
    print('root',root(T,P))
