#!/usr/bin/env python3
"""SEARCHPERF tests: Delta/hunks position map, IncrEvaluator vs the full evaluator, ibase/blockmove update_sites vs fresh enumeration, native-ref verdict logic, driver smoke
(incr + incremental pools + resync).  usage: tests/searchperf_test.py [--quick]   (--quick skips the driver smoke; ~25 s, smoke ~90 s)"""
import sys,os,random,copy,time,tempfile,json,subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
os.environ['TK_FREE_BOUNDS']='1'; os.environ['TK_PROFILE']='5756'
import tkcommon,movekit as M,incr
from wsearch import pools,drive
from wsearch.evalincr import IncrEvaluator,fast_diff_edit
fails=[];n=0
def need(c,what):
    global n; n+=1; print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
def main():
    quick='--quick' in sys.argv; rng=random.Random(5)
    _,w=tkcommon.load('5756'); w=M.pin(w); v=M.View(w)
    # 1. position map
    S=v.S; ok=True
    for trial in range(30):
        S2=[list(e) for e in S]
        for _ in range(rng.randint(1,4)):
            k=rng.randrange(40,len(S2)-40); t=rng.choice('idr')
            if t=='i': S2.insert(k,['ADD',3,5,'1',7])
            elif t=='d': del S2[k]
            else: S2[k]=['ADD',9,11,'1/2',5]
        class V: pass
        a=V(); a.S=S; a.w=w; b=V(); b.S=S2; b.w=w
        d=pools.Delta(a,b); inside=0
        for p in rng.sample(range(len(S)),400):
            q=d.map(p)
            if q is None: inside+=1; continue
            if not(0<=q<len(S2) and S2[q]==S[p]): ok=False
    need(ok,'Delta.map: every mapped old position carries the same event in the new program (30 random local edits)')
    # 2. IncrEvaluator vs full on plugin edits
    ev=IncrEvaluator(resync=0); cur=w; good=0; tot=0; agree=True; legal_n=0
    for c in('ibase','a2x'):
        pl=M.plugin(c); ctx=pl.prepare(v); L=[]
        for ed in pl.sites(v,ctx):
            L.append(ed)
            if len(L)>=1500: break
        rng.shuffle(L)
        for ed in L[:25]:
            try: w2=pl.apply(v,ed)
            except Exception: continue
            o=ev.evaluate(w2,ed,base=w); f=M.evaluate(w2); tot+=1
            e1=incr.apply_edit_to_word(w,fast_diff_edit(w,w2)); e2=incr.apply_edit_to_word(w,incr.diff_edit(w,w2))
            if not(e1['program']==w2['program'] and e1['frames']==w2['frames'] and e1['initial']==w2['initial'] and e1['final']==w2['final'] and e1['program']==e2['program']): agree=False; print('  diff mismatch',c,ed)
            if bool(o.get('legal'))!=bool(f.get('legal')): agree=False; print('  legal mismatch',c,ed,o.get('why'),f.get('why'))
            elif f.get('legal'):
                legal_n+=1
                if abs(o['kappa']-f['kappa'])>1e-15 or bool(o['side_ok'])!=bool(f['side_ok']) or (o['ev_slack']>=0)!=(f['ev_slack']>=0): agree=False; print('  value mismatch',c,ed,o,f)
    need(agree and tot>=30,'IncrEvaluator == movekit.evaluate on %d plugin edits (%d legal): legal, kappa<=1e-15, side, event slack'%(tot,legal_n))
    # adopt + resync
    for c in('ibase','a2x'):
        pl=M.plugin(c); ctx=pl.prepare(v); done=False
        for ed in pl.sites(v,ctx):
            try: w2=pl.apply(v,ed)
            except Exception: continue
            o=ev.evaluate(w2,ed,base=w)
            if o.get('legal'): ev.adopt(w2); w=w2; v=M.View(w); break
    try: ev.check_sync(); need(ev.nbind==1 and ev.commits==2,'adopt = commit (1 bind, 2 commits) and check_sync agrees with the full check')
    except RuntimeError as ex: need(False,'check_sync: %s'%ex)
    # 2b. rebuild (inlined hot loop) and ibase.merge (linear) vs their reference implementations
    import ibase
    from fractions import Fraction as Q
    def rebuild_ref(v,S2):
        w=v.w; own=v.own; cur=list(w['initial'])+[None]*(v.NR-len(w['initial'])); prog=[]
        def move(r,f):
            if cur[r]!=f:
                if cur[r] is None: raise ValueError('dead')
                prog.append(['MOVE',r,cur[r],f,r in own]); cur[r]=f
        for e in S2:
            op,r=e[:2]
            if op=='INIT': cur[r]=e[2]
            elif op=='CLEAR': move(r,e[2]); cur[r]=None
            else:
                move(r,e[-1])
                if op in('ADD','COPY'): move(e[2],e[-1])
            prog.append(e if type(e) is list else list(e))
        for r in range(len(w['initial'])):
            if r not in own: move(r,w['final'][r])
        return prog
    vv=M.View(w0 if 'w0' in dir() else w)
    S2=[list(e) for e in vv.S]; k=rng.randrange(100,len(S2)-100); S2.insert(k,['ADD',3,5,'1',S2[k][-1]]); del S2[k+50]
    try: a_=vv.rebuild(S2)['program']
    except ValueError: a_=None
    try: b_=rebuild_ref(vv,S2)
    except ValueError: b_=None
    need(a_==b_ and a_ is not None or (a_ is None and b_ is None),'View.rebuild (inlined loop) == reference loop')
    bad=0
    for _ in range(1500):
        evs=[['ADD',rng.randrange(4),rng.randrange(4),rng.choice(['1','-1','1/2','-1/2']),rng.choice([5,5,5,6])] if rng.random()<0.9 else ['SCALE',rng.randrange(4),'1',5] for _ in range(rng.randint(1,14))]
        evs=[e for e in evs if e[0]!='ADD' or e[1]!=e[2]]
        if ibase.merge_ref([x[:] for x in evs])!=ibase.merge([x[:] for x in evs]): bad+=1
    need(bad==0,'ibase.merge (linear) == merge_ref on 1500 random event strings incl. cancellations')
    # 3. update_sites vs fresh
    _,w0=tkcommon.load('5756'); w0=M.pin(w0); v0=M.View(w0)
    for c,cap in(('ibase',20000),('blockmove',20000)):
        pl=M.plugin(c)
        if c=='blockmove' and quick: continue
        t=time.time(); P0=list(pl.sites(v0,pl.prepare(v0))); t0=time.time()-t
        ev2=IncrEvaluator(resync=0); cw=w0; cv=v0; P=P0
        for step in range(3):
            pl2=M.plugin('ibase'); L=list(pl2.sites(cv,pl2.prepare(cv)))[:400]; rng.shuffle(L)
            for ed in L:
                try: w2=pl2.apply(cv,ed)
                except Exception: continue
                o=ev2.evaluate(w2,ed,base=cw)
                if o.get('legal'):
                    ev2.adopt(w2); v2=M.View(w2); d=pools.Delta(cv,v2); t=time.time(); P=pl.update_sites(cv,v2,d,P); tu=time.time()-t; cw=w2; cv=v2; break
        F=list(pl.sites(cv,pl.prepare(cv)))
        key=lambda e:json.dumps(e,sort_keys=True,default=str)
        FU=set(map(key,F)); PU=set(map(key,P)); miss=len(FU-PU)
        extra=len(PU-FU)
        need(len(F)==0 and len(P)>=0 or miss<=0.05*len(F),'%s.update_sites after 3 adopted ibase edits: %d of %d fresh sites missing (%d stale extra); full enumeration %.1fs, last update %.2fs'%(c,miss,len(F),extra,t0,tu))
        okapply=0;tried=0
        for e in rng.sample(P,min(40,len(P))):
            tried+=1
            try: pl.apply(cv,e); okapply+=1
            except Exception: pass
        need(tried==0 or okapply>=0.5*tried,'%s: pooled edits remain applicable (%d/%d)'%(c,okapply,tried))
    # 4. native-ref verdict
    V=drive.native_ref_verdict
    need(V(dict(ok=True,native_check=dict(ref=True,pairs=2927,computed=2927,bad=0)))['ok'],'verdict: stack accept, reference ran, 2927 pairs all computed -> ok')
    need(not V(dict(ok=True,native_check=dict(ref=False,pairs=2927,computed=2927,bad=0)))['ok'],'verdict: native_ref flag false -> not ok')
    need(not V(dict(ok=True,native_check=dict(ref=True,pairs=0,computed=0,bad=0)))['ok'],'verdict: zero pairs -> not ok')
    need(not V(dict(ok=True,native_check=dict(ref=True,pairs=100,computed=40,bad=0)))['ok'],'verdict: pair cache used (computed<pairs) -> not ok')
    need(not V(dict(stage='native',error='x',native_pairs=5,native_computed=5,native_ref=True))['ok'],'verdict: no verdict in the json -> not ok')
    need(not V(dict(ok=True))['ok'],'verdict: old-style json without native_ref evidence -> not ok (never CANDIDATE)')
    need(V(dict(ok=True,native_ref=True,native_pairs=7,native_computed=7))['ok'],'verdict: non-stack accept json (native_ref/native_pairs/native_computed) -> ok')
    # 5. driver smoke
    if not quick:
        d_=tempfile.mkdtemp(); env=dict(os.environ)
        r=subprocess.run([sys.executable,'-B',TK+'/tk.py','search','--from','5756','--relax','--strategy','anneal','--classes','a2x,ibase','--max-steps','120','--budget','0.05','--seed','3','--store',d_+'/s.sqlite','--run-id','smoke','--frontier','1','--resync','3','--temp','3e-9,3e-10'],capture_output=True,text=True,env=env,timeout=280)
        out=r.stdout+r.stderr; print(out[-600:])
        need(r.returncode==0 and 'DONE smoke' in out and 'resyncs ok' in out and 'evaluator incr' in out,'tk search anneal (incr, incremental pools, --resync 3) completes; no INCR/FULL MISMATCH')
    print('%d checks, %d failed'%(n,len(fails))); sys.exit(1 if fails else 0)
main()
