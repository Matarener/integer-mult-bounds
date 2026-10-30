#!/usr/bin/env python3
"""PRIMMINE test: the fused moves PM1/PM3 apply value-preservingly (legal + endpoint rows by random evaluation) on #5811, the pscreen hook exists, and the miner binary + classifier agree on the P8-ret rule."""
import sys,os,itertools
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.join(HERE,'..'); sys.path.insert(0,TK)
os.environ.setdefault('TK_FREE_BOUNDS','1')
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
import movekit as M, prims, prims_mined as PM, pscreen
from tkcommon import load
p,w=load('5811'); w=M.pin(w); v=M.View(w); ctx=prims.PLUGIN.prepare(v)
k0=M.evaluate(w)['kappa']
n1=0; ok1=0
for ed in itertools.islice(PM.sites_pm1(v,ctx,window=(12000,12040)),400):
    n1+=1
    try: k=PM.fast(v,ed)
    except Exception: k=None
    if k is None or ok1>=3: continue
    w2=PM.apply_edit(w,ed,v); o=M.evaluate(w2)
    if o.get('legal'): ok1+=1
need(n1>0 and ok1>=1,'PM1: %d fused sites in the window, %d applied legally (rows preserved)'%(n1,ok1))
n3=0; ok3=0
for ed in itertools.islice(PM.sites_pm3(v,ctx,window=(12850,12900)),200):
    n3+=1
    try: k=PM.fast(v,ed)
    except Exception: k=None
    if k is None or ok3>=2: continue
    w2=PM.apply_edit(w,ed,v); o=M.evaluate(w2)
    if o.get('legal'): ok3+=1
need(n3>0 and ok3>=1,'PM3: %d fused sites, %d applied legally'%(n3,ok3))
need('prims_mined' in open(os.path.join(TK,'pscreen.py')).read(),'pscreen.py carries the prims_mined screen')
PM_DIR=os.path.join(TK,'ext','PRIMMINE')
if os.path.exists(os.path.join(PM_DIR,'cls.py')):
    sys.path.insert(0,PM_DIR)
    import cls
    from mlib import pev
    r=cls.search(pev('ADD 0<-1 -1; ADD 2<-0 1;'),pev('ADD 0<-1 -1; INIT 3; COPY 3<-0 1; ADD 2<-3 1; CLEAR 3;'),cap=300,maxdepth=3)
    need(isinstance(r,list) and r==['P8'],'classifier: ret courier = one P8 move (%s)'%(r,))
# PM4: read redirect through a transvection pair
sites4=list(PM.sites_pm4(v,ctx)); ok4=0
for ed in sites4[:20]:
    S2=PM.pm4_apply(v.S,ed)
    if PM.pm4_value_ok(v.S,S2,v.n): ok4+=1
need(len(sites4)>0 and ok4==min(20,len(sites4)),'PM4: %d sites, value-exact (sim_rows) on %d/%d sampled'%(len(sites4),ok4,min(20,len(sites4))))
if os.path.exists(os.path.join(PM_DIR,'cls.py')):
    need(cls.sem(list(cls.nf(pev('ADD 0<-1 -1; ADD 1<-2 -1; ADD 2<-1 1;'))))==cls.sem(list(cls.nf(pev('ADD 1<-2 -1; ADD 2<-1 1; ADD 0<-2 -1;')))),'PM4 toy identity: x0-=x1;x1-=x2;x2+=x1 == x1-=x2;x2+=x1;x0-=x2')
print('FAILED' if fails else 'ALL PASS'); sys.exit(1 if fails else 0)
