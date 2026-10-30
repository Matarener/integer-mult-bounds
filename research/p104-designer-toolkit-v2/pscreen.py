"""pscreen -- the primitive basis and the macro library as `tk eval` screens (P8GAP, FRONTAUTO/NOTES.md).

Why: every new frontier PR must be screened with EVERY primitive automatically.  Before this module `tk eval --screens` knew only handoff/evretime/retime/reorder/split (+ the movekit classes ibase a2x blockmove split2 relay);
P1/P2 (prims), P7 (prims_role), P8-P11 (prims_extra) and the macros were only reachable by hand, which is how #5811 (a six-event P8 accumulation) stayed invisible.

Screens (names are the `tk eval --screens` / FRONTAUTO names):
  prims        P1 (ADD move with Steinberg corrections) + P2 (re-frame) + P3 (conjugation) + P4 (split) + P5 (block move) + P6 (compensated injection): prims.greedy, exact IncrWord confirmation
  prims_role   P7 retire(r): public helper -> owned scratch (moves the pins: own exact level, M.evaluate with the stamped pins)
  prims_extra  P8 (acc/ret owned bridges, maximal-run groups) in its own pin-aware level, then P9 (SCALE hop / fuse) + P10 (owned/main reframe) + P11 (ADD split) via prims.greedy, and P12 (Weyl exchange) when implemented
  alias        P14 (ALIAS): helper alias with reader/frame re-plan (prims_alias.py; output is in minimal-frame form, retime afterwards)
  handover     P13 (LATECUT): late-cut split hand-over of a helper to a NEW public register, compensation solved as an exact LP (handover.py, module docstring)
  macros       the macro library (cofrm, carry, rehome ; conj, inject, split, block) with dip tolerance
CLI:  tk pscreen WORD --set prims|prims_role|prims_extra|macros [--tl S] [--steps N] [--out F]   (writes F only when the exact kappa improves)
Every screen output is re-checked by `tk eval` (legal + native + accept) before it is adopted."""
import os,sys,json,gzip,time
HERE=os.path.dirname(os.path.abspath(__file__))
SETS=('prims','prims_role','prims_extra','macros','handover','alias','alias2','prims_mined','automacro','ctxmine','ctxmine2','k2sa')
PRIMS_COVERED={'PM1':'prims_mined','PM2':'prims_mined','PM3':'prims_mined','PM4':'prims_mined','P1':'prims','P2':'prims','P3':'prims','P4':'prims','P5':'prims','P6':'prims','P7':'prims_role','P8':'prims_extra','P9':'prims_extra','P10':'prims_extra','P11':'prims_extra','P12':'prims_extra','P13':'handover','P14':'alias','P15':'alias2','RS':'automacro','CTX':'ctxmine','CTX2':'ctxmine2',
               'merge3':'(sibling merge: tool, not a search screen)'}
def _log(*x): print(*x,flush=True)
def _greedy(w,prm,tl,steps,window=None,topq=None):
    import prims
    k,w2,chain,st=prims.greedy(w,tuple(prm),steps=steps,tl=tl,log=_log,window=window,**(dict(topq=topq) if topq else {})); return w2,chain
def _pin_greedy(levelfn,w,tl,steps):      # levelfn(w,left)
    """greedy over a pin-aware level (returns [(kappa,word,edit,...)] best first); exact M.evaluate with stamped pins is the judge"""
    import movekit as M
    k=M.evaluate(M.pin(w))['kappa']; w=M.pin(w); chain=[]; t0=time.time()
    for s in range(steps):
        left=tl-(time.time()-t0)
        if left<=0: break
        ch=levelfn(w,left)
        if not ch or ch[0][0]<=k+1e-15: break
        k,w=ch[0][0],ch[0][1]; chain.append(ch[0][2]); _log('  step %d: %.15f %s'%(s+1,k,json.dumps(ch[0][2])[:200]))
    return w,chain
def run_set(name,w,tl=300,steps=10,window=None,topq=None):
    """window=(lo,hi) in the View's scalar-program (S) indices and topq: SCREENSMOKE bounds for tests/screen_smoke.py; honoured by prims, macros, prims_extra, prims_mined, automacro (default None = whole word, unchanged behaviour)"""
    import movekit as M
    if name=='prims_mined':      # PRIMMINE: fused mined moves PM1 (P1c o P8), PM3 (P3 o P8) (prims_mined.py, module docstring); not in SETS (FRONTAUTO list is another lane's file)
        import prims_mined as PM
        return PM.run(w,tl=tl,steps=min(steps,3),log=_log,kinds_pm=('PM4','PM1','PM3','PM2'),window=window,**(dict(topq=topq) if topq else {}))
    if name=='k2sa':      # K2UNIFY: s2s compaction + bounded multi-seed unified k2net SA + exact validation + `tk accept --native-ref` on a gain (k2/screen.py, module docstring)
        from k2 import screen as K2S
        return K2S.run(w,tl=tl,steps=steps,window=window,topq=topq,log=_log,seeds=tuple(int(x) for x in os.environ.get('K2SA_SEEDS','1,2').split(',')),native_ref=os.environ.get('K2SA_NATIVE_REF','1')!='0',capfree=os.environ.get('TK_EVENT_CAP')=='0')
    if name=='ctxmine2':      # CTXMINE2: + P3 conjugation, equal-value read redirect, coefficient split/merge (ctxmine2_lift.py)
        import ctxmine2_lift as CL2
        return CL2.run(w,tl=tl,steps=min(steps,3),log=_log,window=window)
    if name=='ctxmine':      # CTXMINE: lifted-guard real-context window search (ctxmine_lift.py)
        import ctxmine_lift as CL
        return CL.run(w,tl=tl,steps=min(steps,3),log=_log,window=window)
    if name=='automacro':      # AUTOMACRO: RSPLIT (remote Steinberg split, #5827) + plugins automacro_*.py (module docstring)
        import automacro_rsplit as RS
        return RS.run(w,tl=tl,steps=min(steps,3),log=_log,window=window,**(dict(topq=topq) if topq else {}))
    if name=='prims': return _greedy(w,('P1','P2','P3','P4','P5','P6'),tl,steps,window,topq)
    if name=='macros':
        import macros
        stages=[[macros.LIB[x] for x in s.split(',')] for s in 'cofrm,carry,rehome;conj,inject,split,block'.split(';')]
        k,w2,chain,st=macros.search(w,stages,steps=steps,tl=tl,log=_log,window=window,**(dict(topq=topq) if topq else {})); return w2,chain
    if name=='prims_role':
        import prims_role as PR
        def lvl(w,left):
            out=[]
            regs=None
            if window:      # smoke / sampled screening: only the registers touched inside the S-window
                S_=M.View(w).S; regs={r for e in S_[window[0]:window[1]] for r in ((e[1],) if e[0] in('INIT','CLEAR','SCALE') else (e[1],e[2])) if r<len(w['initial'])}
            for s in PR.find_sites(w,regs=regs)[:12]:
                try: w2=PR.apply_retire(w,s['r'],s['plan'])
                except Exception: continue
                o=M.evaluate(w2)
                if o.get('legal'): out.append((o['kappa'],w2,dict(prim='P7',r=s['r'])))
            out.sort(key=lambda x:-x[0]); return out
        return _pin_greedy(lvl,w,tl,steps)
    if name=='prims_extra':
        import prims_extra as PE
        w1,c1=_pin_greedy(lambda w,left:PE.level(w,('acc','ret'),topq=topq or 20,tl=left,WR=400,log=_log,window=window),w,tl*0.5,steps)
        w2,c2=_greedy(w1,('P9','P10','P11','P12'),tl*0.5,steps,window,topq)
        return w2,c1+c2
    if name=='handover':      # LATECUT: P13 late-cut split hand-over with solved compensation (handover.py)
        import handover as H
        return _pin_greedy(lambda w,left:H.level(w,tl=left,log=_log),w,tl,steps)
    if name=='alias':      # ALIAS: P14 helper alias + frame re-plan (prims_alias.py, module docstring); judged against its own minimal-frame base word
        import prims_alias as PA
        return _pin_greedy(lambda w,left:PA.level(w,tl=left,log=_log),PA.base(w),tl,steps)
    if name=='alias2':      # SRCREORDER: P15 helper alias with source-read re-ordering (prims_alias2.py, module docstring); same hybrid-frame base as P14
        import prims_alias2 as PA2
        return _pin_greedy(lambda w,left:PA2.level(w,tl=left,log=_log),PA2.base(w),tl,steps)
    raise ValueError(name)
def add_parsers(sp):
    p=sp.add_parser('pscreen',help='run one primitive/macro screen (prims|prims_role|prims_extra|macros) on a word; the same code `tk eval --screens` runs'); p.add_argument('word'); p.add_argument('--set',required=True,choices=SETS)
    p.add_argument('--tl',type=float,default=300); p.add_argument('--steps',type=int,default=10); p.add_argument('--out'); p.add_argument('--window',nargs=2,type=int,help='S-index window (smoke tests / sampled screening)'); p.add_argument('--topq',type=int)
def main(a):
    os.environ.setdefault('TK_FREE_BOUNDS','1')
    import movekit as M
    from tkcommon import load
    p,w=load(a.word); w=M.pin(w); k0=M.evaluate(w)
    if not k0.get('legal'): _log('ILLEGAL',k0.get('why')); return 1
    w2,chain=run_set(a.set,w,a.tl,a.steps,window=tuple(a.window) if getattr(a,'window',None) else None,topq=getattr(a,'topq',None)); k1=M.evaluate(w2)
    _log('RESULT %s kappa %.15f -> %.15f (%+.3e) steps %d'%(a.set,k0['kappa'],k1['kappa'],k1['kappa']-k0['kappa'],len(chain)))
    if a.out and chain and k1.get('legal') and k1['kappa']>k0['kappa']+1e-15: json.dump(w2,gzip.open(a.out,'wt')); _log('wrote',a.out)
    return 0
def screen_fn(name):
    def fn(ctx,cur,base):
        import eval as E
        o=base+'.json.gz'; rc=E._run(['pscreen',cur,'--set',name,'--tl',str(ctx['tl']),'--out',o],base+'.log',ctx['tl'],ctx)
        return (o if os.path.exists(o) else None),dict(rc=rc)
    return fn
def register_screens():
    import eval as E
    for n in SETS:
        if n not in E.SCREENS: E.register(n,screen_fn(n))
