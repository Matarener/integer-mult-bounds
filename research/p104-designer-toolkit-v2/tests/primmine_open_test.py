#!/usr/bin/env python3
"""SCREENSMOKE: PRIMMINE's two 'search-exhausted at depth 5' rules are settled: x0-=x1; x2-=x0; x2+=x1 ==> x0+=x2; x2+=x1; x0-=x2; x2-=x0 (and every sign twin) = P0 reorder + ONE P3
(cls.search only linearised the trace in lex-min order, so T could not be placed before x2+=x1 with x2-=x0 behind it; B->A is one P1c step).  Needs ext/PRIMMINE/cls.py."""
import sys,os,itertools
HERE=os.path.dirname(os.path.abspath(__file__)); PM=os.path.join(HERE,'..','ext','PRIMMINE')
if not os.path.exists(PM+'/cls.py'): print('SKIP (no PRIMMINE/cls.py)'); print('FAILS 0'); sys.exit(0)
sys.path.insert(0,PM); import cls; from mlib import pev
A0=cls.nf(pev('ADD 0<-1 -1; ADD 2<-0 -1; ADD 2<-1 1;')); B0=cls.nf(pev('ADD 0<-2 1; ADD 2<-1 1; ADD 0<-2 -1; ADD 2<-0 -1;'))
flip=lambda P,r: tuple((e[0],e[1],e[2],-e[3] if ((e[2]==r)!=(e[1]==r)) else e[3]) for e in P)
fails=0
for name,r in (('rule A',None),('twin x0',0),('twin x1',1),('twin x2',2)):
    A,B=(A0,B0) if r is None else (cls.nf(flip(A0,r)),cls.nf(flip(B0,r))); S0=cls.sem(list(A)); ok=S0==cls.sem(list(B))
    hit=[tag for L in {p for p in itertools.permutations(A) if cls.sem(list(p))==S0} for tag,Q in cls.moves(L,S0,6) if Q==B]
    ok=ok and set(hit)=={'P3'} and cls.search(B,A,cap=3000,maxdepth=4)==['P1c']
    print(('PASS ' if ok else 'FAIL ')+name+': reorder + one P3 (forward), one P1c (reverse)'); fails+=not ok
print('FAILS',fails); sys.exit(1 if fails else 0)
