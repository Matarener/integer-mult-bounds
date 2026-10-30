#!/usr/bin/env python3
"""CLSFIX: cls.search ranges over all linearisations (P1s free reorder).  Known cases: SCREENSMOKE rule A (forward = reorder+P3), a rule that the lex-min search left at the cap (resolved in the reverse direction), linearisation enumeration is trace-complete.  Needs ext/PRIMMINE/cls.py."""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); PM=os.path.join(HERE,'..','ext','PRIMMINE')
if not os.path.exists(PM+'/cls.py'): print('SKIP (no PRIMMINE/cls.py)'); print('FAILS 0'); sys.exit(0)
sys.path.insert(0,PM); import cls; from mlib import pev
fails=0
def chk(ok,msg):
    global fails; print(('PASS ' if ok else 'FAIL ')+msg); fails+=not ok
# 1. linearisations
P=cls.nf(pev('ADD 0<-1 -1; ADD 2<-0 -1; ADD 2<-1 1;')); L,t=cls.linearisations(P)
chk(len(L)==3 and not t and all(cls.sem(list(q))==cls.sem(list(P)) for q in L),'linearisations of rule-A LHS = 3 value-equal orders (x2-=x0 / x2+=x1 commute; x2+=x1 / x0-=x1 commute)')
# 2. forward search finds rule A in ONE P3 with default (all-linearisation) search; the lex-min-only search does not within depth 1
B=cls.nf(pev('ADD 0<-2 1; ADD 2<-1 1; ADD 0<-2 -1; ADD 2<-0 -1;'))
chk(cls.search(P,B,cap=3000,maxdepth=1)==['P3'],'rule A forward = [P3] at depth 1 (all linearisations)')
chk(cls.search(P,B,cap=3000,maxdepth=1,lin=False)!=['P3'],'lex-min-only search misses it at depth 1 (the old artefact)')
# 3. classify(): a rule left 'unresolved at cap' by the old classifier is now decomposed (via B->A)
A=cls.nf(pev('ADD 0<-1 -1; ADD 2<-0 -1; ADD 1<-0 1')); B2=cls.nf(pev('INIT 3; COPY 3<-1 -1; ADD 3<-0 1; ADD 0<-1 -1; ADD 2<-3 -1; ADD 1<-0 1; CLEAR 3'))
st,p=cls.classify(A,B2,cap=100,maxdepth=2)
chk(st in('fwd','rev') and p is not None and len(p)==2 and set(p)<=cls.BASIS,'former cap rule (P8 + P1c) classifies: %s %s'%(st,p))
print('FAILS',fails); sys.exit(1 if fails else 0)
