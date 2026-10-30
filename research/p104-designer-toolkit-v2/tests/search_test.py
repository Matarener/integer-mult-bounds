#!/usr/bin/env python3
"""SEARCHCORE tests: canon hash invariances/distinctions, store round trip, driver smoke.  usage: tests/search_test.py [--quick]"""
import sys,os,random,copy,time,gzip,json,tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
from tkcommon import load,legal
from wsearch import canon
fails=[];n=0
def need(c,what):
    global n; n+=1; print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
def wp(x): return TK+'/words/%s.json.gz'%x
def relabel(w,rng):
    n=len(w['initial']); live=set(w['live']); H=[r for r in range(n) if r not in live and r-112 not in live and r<n]
    own=set(legal.owned_set(w)); H=[r for r in H if r not in own]
    P=H[:]; rng.shuffle(P); m={a:b for a,b in zip(H,P)}; f=lambda r:m.get(r,r)
    w2=copy.deepcopy(w); 
    w2['initial']=[w['initial'][{v:k for k,v in m.items()}.get(r,r)] for r in range(n)]; w2['final']=[w['final'][{v:k for k,v in m.items()}.get(r,r)] for r in range(n)]
    for e in w2['program']:
        e[1]=f(e[1])
        if e[0] in('ADD','COPY'): e[2]=f(e[2])
    return w2
def shuffle_commuting(w,rng,tries=20000):
    """random adjacent swaps of items that touch disjoint registers (always commute) or are MOVEs of different regs"""
    P=[list(e) for e in w['program']]
    def regs(e): return {e[1]}|({e[2]} if e[0] in('ADD','COPY') else set())
    for _ in range(tries):
        i=rng.randrange(len(P)-1); a,b=P[i],P[i+1]
        if a[0] in('INIT','CLEAR') and b[0] in('INIT','CLEAR'): continue
        if regs(a)&regs(b): continue
        P[i],P[i+1]=b,a
    w2=dict(w); w2['program']=P; return w2
def swap_commuting_add(w,rng):
    """swap an adjacent pair ADD(t,s,..),ADD(t,s2,..) (additive writes into one register commute) with no MOVE between, public regs"""
    n=len(w['initial']); P=[list(e) for e in w['program']]; c=[i for i in range(len(P)-1) if P[i][0]=='ADD' and P[i+1][0]=='ADD' and P[i][1]==P[i+1][1] and P[i][1]<n and P[i][2]<n and P[i+1][2]<n and P[i][2]!=P[i+1][1] and P[i+1][2]!=P[i][1] and P[i][4]==P[i+1][4] and P[i][2]!=P[i+1][2]]
    if not c: return None
    i=rng.choice(c); P[i],P[i+1]=P[i+1],P[i]; w2=dict(w); w2['program']=P; return w2
def main():
    rng=random.Random(1)
    _,w=load('5660'); h=canon.canon_hash(w); t=time.time(); canon.canon_hash(w); dt=time.time()-t
    need(dt<5,'canon_hash 5660 in %.2fs'%dt)
    need(canon.canon_hash(relabel(w,rng))==h,'relabelled copy hashes equal (5660)')
    need(canon.canon_hash(shuffle_commuting(w,rng))==h,'independent adjacent items shuffled (MOVE/event order) hash equal')
    w2=swap_commuting_add(w,rng); need(w2 is not None and canon.canon_hash(w2)==h,'commuting additive-write swap hashes equal')
    # a non-commuting change must differ: swap first adjacent ADD pair that conflicts (same register read/write)
    P=[list(e) for e in w['program']]
    for i in range(len(P)-1):
        a,b=P[i],P[i+1]
        if a[0]=='ADD' and b[0]=='ADD' and a[2]==b[1] and a[4]==b[4]: P[i],P[i+1]=b,a; break
    w3=dict(w); w3['program']=P; need(canon.canon_hash(w3)!=h,'non-commuting swap changes the hash')
    w4=copy.deepcopy(w); 
    for e in w4['program']:
        if e[0]=='ADD': e[3]='7/3'; break
    need(canon.canon_hash(w4)!=h,'changed quotient changes the hash')
    # decompile -> realise round trip
    import dag as D
    d=D.decompile(w,forms=False); wr,rep=D.realise(d,None,(),verify=False)
    need(canon.canon_hash(wr)==h,'decompile->realise round trip hash equal (5660)')
    # OWNEDN reorder variant differs
    _,wv=load(TK+'/ext/OWNEDN/5660__reorder.json.gz'); need(canon.canon_hash(wv)!=h,'#5660 and its OWNEDN reorder variant hash differently')
    need(canon.canon_hash(wv)==canon.canon_hash(relabel(wv,rng)),'reorder variant: relabelled copy equal')
    _,w18=load('5718'); h18=canon.canon_hash(w18); need(h18!=h and canon.canon_hash(relabel(w18,rng))==h18,'5718 distinct from 5660, relabel-invariant')
    # store
    from wsearch import store
    d_=tempfile.mkdtemp(); S=store.Store(d_+'/s.sqlite'); S.put_word(h18,w18); S.add_eval(h18,'p',True,3.11e-3,dict(kappa='0.0031102457201285',lo='x',hi='y'),True,'fast')
    need(S.get_word(h18)['initial']==w18['initial'] and S.best(1)[0]['chash']==h18,'store round trip')
    print('%d checks, %d failed'%(n,len(fails))); sys.exit(1 if fails else 0)
main()
