#!/usr/bin/env python3
"""FASTSITES: ibase.proxy_sites (ratio form) == proxy_sites_ref EXACTLY (list equality, same order) on real words, whole word and restricted `regs`; ibase.merge (indexed) == merge_ref-equivalent
(old merge, kept as merge_old) on every P3 window of the word.  usage: tests/ibase_fast_test.py WORD[,WORD..] [--quick]"""
import sys,os,time
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK); os.environ['TK_FREE_BOUNDS']='1'
import tkcommon,movekit as M,ibase,random
words=sys.argv[1].split(','); fails=0
for wn in words:
    _,w=tkcommon.load(wn); w=M.pin(w); v=M.View(w)
    t=time.time(); a=ibase.proxy_sites(v); t1=time.time()-t; t=time.time(); b=ibase.proxy_sites_ref(v) if not os.environ.get('QUICK') else a; t2=time.time()-t
    ok=(a==b); fails+=not ok; print(wn,'proxy_sites full',len(a),'sites',('EQUAL' if ok else 'DIFFERENT'),'fast %.1fs ref %.1fs'%(t1,t2),flush=True)
    rg=set(random.Random(1).sample(range(v.n),12))
    ok=(ibase.proxy_sites(v,rg)==ibase.proxy_sites_ref(v,rg)); fails+=not ok; print(wn,'proxy_sites regs',('EQUAL' if ok else 'DIFFERENT'),flush=True)
    import prims
    rng=random.Random(2); P=prims.PLUGIN; n=bad=0; ps=ibase.proxy_sites(v)
    for sm,a_,b_,q_,s0,s1,L in ps[:300]+rng.sample(ps,min(300,len(ps))):
        bl=v.blocks; i0=bl[s0][0]; i1=bl[s1][-1]
        try: win=prims.conj_window(v.S[i0:i1+1],a_,b_,q_,v.n)
        except prims.Block: continue
        n+=1
        if ibase.merge([list(e) for e in win])!=ibase.merge_old([list(e) for e in win]): bad+=1
    fails+=bad; print(wn,'merge vs merge_old on',n,'real conj windows:',bad,'differences',flush=True)
    # incremental proxy_sites along a chain of committed edits (P3 and P1 edits, canonical rebuilt words)
    import prims
    P=prims.PLUGIN; vv=M.View(M.View(w).rebuild_ref(M.View(w).S)); ibase.proxy_sites(vv); ninc=0; bad=0
    for step in range(int(os.environ.get('CHAIN','6'))):
        ctx=P.prepare(vv); eds=[]
        for pn in ('P3','P1'):
            g=P.sites(vv,ctx,prims=(pn,),window=(12000,13500)) if pn=='P1' else P.sites(vv,ctx,prims=(pn,))
            for k,ed in enumerate(g):
                if k>=40: break
                eds.append(ed)
        rng.shuffle(eds)
        for ed in eds:
            try: pr=P.parts(vv,ed)
            except Exception: continue
            if pr is None or pr[1] or pr[2]: continue
            try: w2=vv.rebuild_ref(pr[0])
            except Exception: continue
            v2=M.View(w2); old=ibase._LAST[0]; a=ibase.proxy_sites(v2); b=ibase.proxy_sites_full(v2)
            ninc+=(old is not None and old[0] is not v2.S); ok=(a==b); bad+=not ok
            print(wn,'chain step',step,ed['prim'],'incremental==full:',ok,len(a),flush=True)
            vv=v2; break
    fails+=bad; print(wn,'incremental proxy_sites: %d differences'%bad,dict(ibase.STATS))
print('FAILS',fails); sys.exit(1 if fails else 0)
