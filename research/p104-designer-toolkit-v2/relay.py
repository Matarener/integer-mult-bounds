"""tk relay -- temporal / relay move class (TKRELAY): replace ONE scalar contact by a span of values that already exist elsewhere in time.

    ADD(r <- s, c) @F at op i   ==>   delete it, and add  sum_k a_k * u_k  to r at insertion gaps g_k inside the window where r is neither read, scaled, copied nor cleared
    (additions into r commute), with every term placed where BOTH r and u_k already reside in the frame F_k (no new MOVE: just-in-time MOVE semantics of View.rebuild),
    and  sum_k a_k * form(u_k at g_k) == c * form(s at i)   EXACTLY as linear forms over the input rows.   The word then still computes the same linear map; what changes
    is only the MOVE multiset: r's (or s's) sole visit to the frame F vanishes and two paid MOVEs merge into one.
This is the common core of three swarm moves, found by exact span solving (spansolve.py), not by hand:
    #5713 distributed scalar updates  (ADD 715 <- 747 @598  ==>  715 += 525/4 - 712 @frame 3 early, 715 += -525/4 + 340/4 @396 late; H1+H2 -> H3)         [back-test: exact]
    #5605 compensated shared relay / #5612 delayed shared preparation: the same contact replacement but the difference of the two forms is allowed to be non-zero on
    columns that the free pre/post ADDs of frames 3/127 repair (RELAYGEN); `--opt free=` hands such a column set to spansolve (residual returned) --
    for what the exact-equality plugin does and does not reproduce of those two.
Interface (movekit.Plugin): prepare(view)->ValueTimeline; sites(view,ctx)-> edits  {'i','r','s','c','F','terms':[[u,coef,gap,F,stage],..],'sig'};
scalars(view,edit)-> new scalar program (MOVEs re-derived by View.rebuild).  CLI: `tk relay WORD [--apply --steps N --max-sites N --shard i/n --edit JSON --out F --list N --opt k=v]`
options (--opt): terms=4 (max terms), sole=1 (only contacts whose removal can merge MOVEs: sole stay of r or s), nbest=2, engine=dfs|cpsat, tl=60 (cpsat seconds), ids=i,j (only these ops)."""
import sys,os,json,gzip,time,collections
from fractions import Fraction as Q
import movekit as M
from tkcommon import load
from movekit import qs
import spansolve as SS
OPT=dict(terms='4',sole='1',nbest='2',engine='dfs',tl='60',ids='',native='1',shard='0/1',exact='1',comp='0',paid='0',owned='1',maxsub='3',hoist='1',jmax='60')
def opt(k): return OPT[k]
def sole_flags(tl,i):
    """(r_sole, s_sole): op i is the only event of that register's stay in its frame (previous and next event of the register are in other frames)"""
    import bisect
    e=tl.S[i]; f=e[-1]; out=[]
    for x in (e[1],e[2]):
        L=tl.ev[x]; keys=[a for a,_,_ in L]; k=bisect.bisect_left(keys,i)
        fp=L[k-1][1] if k>0 else (tl.init[x] if x<tl.n else None)
        fn=L[k+1][1] if k+1<len(L) else (tl.fin[x] if x<tl.n else None)
        out.append(fp!=f and fn!=f)
    return out
class Relay(M.Plugin):
    name='relay'; doc=__doc__; quick=True; site_fields=('sig',)
    def prepare(self,view): return SS.ValueTimeline(view)
    def _sig(self,view,i):
        S=view.S; e=S[i]; n=sum(1 for j in range(i) if S[j][:3]==e[:3] and S[j][-2:]==e[-2:])
        return '%s %d %d %s %d #%d'%(e[0],e[1],e[2],e[3],e[4],n)
    def candidates(self,view,tl):
        ids=[int(x) for x in opt('ids').split(',') if x]; sh,nsh=[int(x) for x in opt('shard').split('/')]; k=0
        for i,e in enumerate(view.S):
            if ids and i not in ids: continue
            if e[0]!='ADD': continue
            if opt('sole')=='1':
                a,b=sole_flags(tl,i)
                if not(a or b): continue
            k+=1
            if k%nsh!=sh: continue
            yield i
    def solve_site(self,view,tl,i,free=()):
        e=view.S[i]; r=e[1]
        P=tl.pool(r,i); tg=tl.target(i)
        if opt('paid')=='1': P=P+tl.pool_paid(r,i)
        if opt('engine')=='cpsat':
            sols=SS.solve_cpsat(tg,P,max_terms=int(opt('terms')),free_cols=free,threads=2,time_limit=float(opt('tl')))
        else:
            sols=SS.solve(tg,P,max_terms=int(opt('terms')),free_cols=free,nbest=int(opt('nbest')))
        return sols,len(P)
    def sites(self,view,ctx):
        tl=ctx
        for i in self.candidates(view,tl):
            e=view.S[i]
            sols,_=self.solve_site(view,tl,i)
            for s in sols:
                yield dict(i=i,r=e[1],s=e[2],c=e[3],F=e[4],terms=[[c.meta['u'],qs(a),c.meta['gap'],c.meta['F'],c.meta['stage']] for c,a in s.terms],sig=self._sig(view,i))
    def scalars(self,view,edit):
        if edit.get('kind')=='joint': return self.joint_scalars_comp(view,edit)
        if edit.get('comp') and not edit.get('_raw'):
            import relaycomp as RC
            S3,info=RC.absorb(view,self.scalars(view,dict(edit,_raw=1)))
            if S3 is None: raise ValueError('absorb: %s'%info)
            edit['info']=info; return S3
        S=view.S; i=edit['i']; r=edit['r']; ins={}
        for u,a,g,F,st in edit['terms']: ins.setdefault(g,[]).append((st,['ADD',r,u,a,F]))
        out=[]
        for k,e in enumerate(S):
            for _,x in sorted(ins.pop(k,[]),key=lambda t:t[0]): out.append(x)
            if k!=i: out.append(e if type(e) is list else list(e))
        for g in sorted(ins):
            for _,x in sorted(ins[g],key=lambda t:t[0]): out.append(x)
        return out
    def comp_single_edits(self,view,tl,log=print):
        """compensated single-target spans: spansolve modulo the Zpre columns; E = S_t (x) residual must be pre/post absorbable (cheap algebraic test), uncompensated price must gain"""
        import relaycomp as RC
        J=RC.Joint(view,tl); w=view.w; live=set(w['live']); n=view.n
        zc={c for c in J.Zpre if c not in live and c-112 not in live}
        cands=list(self.candidates(view,tl)); sp=RC.SensPass(view,set(),want_ops=set(cands)); k0=M.evaluate(view.w)['kappa']; out=[]
        for i in cands:
            e=view.S[i]; r=e[1]; P=tl.pool(r,i)
            if opt('paid')=='1': P=P+tl.pool_paid(r,i)
            sols=SS.solve(tl.target(i),P,max_terms=int(opt('terms')),free_cols=zc,nbest=int(opt('nbest')))
            St=sp.contact[i]; rows=set(St)
            for sol in sols:
                d=sol.residual
                if not d: continue          # exact: handled by the exact class
                pre=[y for y in rows if w['initial'][y]==J.Fpre and y not in live and all(c<n and w['initial'][c]==J.Fpre for c in d)]
                if any(c in rows for c in d) : continue
                rest=[y for y in rows if y not in set(pre)]
                if not all(y in J.Zpost for y in rest) or len(rest)>24: continue
                ed=dict(i=i,r=r,s=e[2],c=e[3],F=e[4],comp=True,terms=[[c.meta['u'],qs(a_),c.meta['gap'],c.meta['F'],c.meta['stage']] for c,a_ in sol.terms],sig=self._sig(view,i)+' comp')
                try: k,_=M.quick(view,self.scalars(view,dict(ed,comp=False)))
                except Exception: k=None
                if k is not None and k>k0+1e-15: out.append(dict(ed,qgain=k-k0))
        out.sort(key=lambda p:-p['qgain']); log('  comp-single: %d candidate edits with positive uncompensated price'%len(out)); return out
    def joint_scalars_comp(self,view,edit):
        import relaycomp as RC
        S2=RC.joint_scalars(view,edit); S3,info=RC.absorb(view,S2)
        if S3 is None: raise ValueError('absorb: %s'%info)
        edit['info']=info; return S3
    def joint_edits(self,view,tl,log=print):
        """compensated joint relays: proposals (S-span x value-span matching) -> exact algebraic filter -> quick uncompensated price; best first"""
        import relaycomp as RC
        J=RC.Joint(view,tl); props=J.propose(maxsub=int(opt('maxsub')),hoist=opt('hoist')=='1',groups=J.reader_groups(owned_only=opt('owned')=='1'),log=log,sole_ops=({i for i in self.candidates(view,tl)} if opt('owned')!='1' else None))
        kp=RC.algebraic_filter(view,tl,J,props,log=log); k0=M.evaluate(view.w)['kappa']; pos=[]
        for p in kp:
            try: k,_=M.quick(view,RC.joint_scalars(view,p))
            except Exception: k=None
            if k is not None and k>k0+1e-15: p=dict(p,qgain=k-k0); pos.append(p)
        pos.sort(key=lambda p:-p['qgain']); log('  joint: %d with positive uncompensated price'%len(pos)); return pos
PLUGIN=Relay()
# ---------------------------------------------------------------------------------------------------------------- INCR confirmation
def incr_confirm(iw,w,v,edits,pl=PLUGIN):
    """exact legality (incl. native pairs) + price of each edit by IncrWord on top of the base word w; -> list of (edit, dk, word)"""
    import incr
    out=[]
    for ed in edits:
        try:
            w2=v.rebuild(pl.scalars(v,ed)); res=iw.try_edit(incr.diff_edit(w,w2))
        except (ValueError,KeyError,IndexError,AssertionError) as ex:
            continue
        if res.legal: out.append((ed,res.dk,w2))
    return out
def screen_incr(w,log=print,results=None,keys=None,max_sites=None,min_gain=1e-15):
    """solve every candidate contact, price each resulting edit with IncrWord (exact legality incl. native pairs + exact kappa) -> (list of dict(edit,dk,word) best first, IncrWord)"""
    import incr
    v=M.View(w); tl=PLUGIN.prepare(v); iw=incr.IncrWord(w); out=[]; n=0; nsol=0; t0=time.time()
    for i in (PLUGIN.candidates(v,tl) if opt('exact')=='1' else ()):
        sig=PLUGIN._sig(v,i)
        if keys is not None and sig not in keys: continue
        if max_sites and n>=max_sites: break
        n+=1; e=v.S[i]
        try: sols,_=PLUGIN.solve_site(v,tl,i)
        except Exception as ex: log('  site %d: %s'%(i,repr(ex)[:80])); continue
        for s_ in sols:
            nsol+=1
            ed=dict(i=i,r=e[1],s=e[2],c=e[3],F=e[4],terms=[[c.meta['u'],qs(a_),c.meta['gap'],c.meta['F'],c.meta['stage']] for c,a_ in s_.terms],sig=sig)
            try:
                w2=v.rebuild(PLUGIN.scalars(v,ed)); res=iw.try_edit(incr.diff_edit(w,w2))
            except (ValueError,KeyError,IndexError,AssertionError) as ex:
                rec=dict(edit=ed,legal=False,why=repr(ex)[:60]); res=None
            else:
                rec=dict(edit=ed,legal=bool(res.legal),dk=res.dk,why=res.reason)
            if results: results.write(json.dumps(rec,default=str)+'\n'); results.flush()
            if res is not None and res.legal and res.dk>min_gain: rec['word']=w2; out.append(rec)
    if opt('comp')!='0':
        jl=(PLUGIN.joint_edits(v,tl,log)[:int(opt('jmax'))] if opt('comp') in('1','3') else [])
        if opt('comp') in('2','3'): jl=jl+PLUGIN.comp_single_edits(v,tl,log)[:int(opt('jmax'))]
        nj=0
        for ed in jl:
            if keys is not None and ed.get('sig') not in keys and False: continue
            try:
                w2=v.rebuild(PLUGIN.scalars(v,ed)); res=iw.try_edit(incr.diff_edit(w,w2))
            except (ValueError,KeyError,IndexError,AssertionError) as ex:
                rec=dict(edit=ed,legal=False,why=repr(ex)[:80]); res=None
            else: rec=dict(edit=ed,legal=bool(res.legal),dk=res.dk,why=res.reason)
            nj+=1
            log('  joint %s x=%s u=%s q=%+.3e -> %s'%(ed.get('remove',ed.get('i')),ed.get('x',ed.get('r')),ed.get('u',[t[0] for t in ed.get('terms',[])]),ed['qgain'],('dk %+.3e'%res.dk if res is not None and res.legal else rec['why'])))
            if results: results.write(json.dumps(rec,default=str)+'\n'); results.flush()
            if res is not None and res.legal and res.dk>min_gain: rec['word']=w2; ed.setdefault('sig','J %s %s %s %s'%(ed.get('remove'),ed.get('x'),ed.get('u'),ed.get('gap'))); out.append(rec)
    out.sort(key=lambda r:-r['dk']); log('  relay: %d contacts solved (%d solutions) in %.0fs, %d legal improving'%(n,nsol,time.time()-t0,len(out)))
    return out,iw
def main(a):
    for kv in (getattr(a,'opt',None) or []):
        k,_,val=kv.partition('='); OPT[k]=val
    OPT['shard']=a.shard; a.shard='0/1'
    if OPT.get('free')=='1': os.environ['TK_FREE_BOUNDS']='1'
    if a.edit: return M.cli(PLUGIN,a)
    path,w=load(a.word); w=M.pin(w); log=lambda *x:print(*x,flush=True)
    k0=M.evaluate(w)
    if not k0.get('legal'): log('ILLEGAL',k0.get('why')); return 1
    log('relay on %s: kappa %.15f (%d events)'%(os.path.basename(path),k0['kappa'],len(w['program'])))
    res=open(a.results,'a') if a.results else None; cur=w; keys=None; applied=[]
    for step in range(a.steps if a.apply else 1):
        out,iw=screen_incr(cur,log,res,keys,a.max_sites or None)
        for r in out[:a.list]: log('  dk %+.3e %s'%(r['dk'],json.dumps(r['edit'])[:200]))
        if not a.apply: break
        if not out:
            if keys is None: break
            keys=None; continue
        keys={r['edit']['sig'] for r in out}
        b=out[0]; cur=b['word']; applied.append(dict(edit=b['edit'],dk=b['dk']))
        log('  APPLY relay %s: +%.3e'%(json.dumps(b['edit'])[:100],b['dk']))
    if applied and a.out:
        o=M.evaluate(cur); json.dump(cur,gzip.open(a.out,'wt')); log('wrote %s: %d edits, kappa %.15f (+%.3e) legal %s'%(a.out,len(applied),o.get('kappa',0),o.get('kappa',0)-k0['kappa'],o.get('legal')))
    elif not applied and a.out and out: json.dump(out[0]['word'],gzip.open(a.out,'wt')); log('wrote best single edit',a.out)
    return 0
