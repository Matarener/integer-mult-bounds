"""gensearch.run -- evaluator cache + search strategies + deterministic/resumable driver.
Every evaluation is a row {level, sid, spec, ...} appended to GENSEARCH/cpu_results.jsonl (the lineage = the spec); a rerun with the same strategy+seed regenerates the same spec sequence
(rng seeded per draw / per generation, selection only reads cached rows) and so resumes by cache hits.  Levels: L0 dag-only R0 tax, L1 fast invoice + admit slack, L2 exact IncrWord (+ admit.best).
"""
import sys,os,json,math,random,time,gzip
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
from gensearch import space as S, build as B
from tkcommon import W
GS=B.GS; FRONTIER=0.0031219213
class Ev:
    def __init__(s,run,path=None,store=None,seed=0,frontier=FRONTIER):
        s.run=run; s.path=path or GS+'/cpu_results.jsonl'; s.rows={}; s.seed=seed; s.frontier=frontier; s.n_new=dict(L0=0,L1=0,L2=0); s.best=None; s.stored=0; s.t0=time.time()
        os.makedirs(os.path.dirname(s.path),exist_ok=True)
        if os.path.exists(s.path):
            for l in open(s.path):
                try: r=json.loads(l); s.rows[(r['level'],r['sid'])]=r
                except Exception: pass
        s.store=None
        if store:
            from wsearch.store import Store; s.store=Store(None if store=='default' else store)
    def _put(s,r):
        s.rows[(r['level'],r['sid'])]=r; open(s.path,'a').write(json.dumps(r,default=str)+'\n')
    def L0(s,sp):
        sp=S.normalize(sp); i=S.sid(sp)
        if ('L0',i) in s.rows: return s.rows[('L0',i)]
        t=time.time(); r=dict(level='L0',sid=i,spec=sp,run=s.run,seed=s.seed)
        try:
            dag,info=B.build_dag(sp); r.update(B.r0(dag)); r['value_ok']=bool(info['value_ok'])
        except Exception as ex: r.update(error=repr(ex)[:200],value_ok=False)
        r['secs']=round(time.time()-t,2); s.n_new['L0']+=1; s._put(r); return r
    def L1(s,sp):
        sp=S.normalize(sp); i=S.sid(sp)
        if ('L1',i) in s.rows: return s.rows[('L1',i)]
        t=time.time(); r=dict(level='L1',sid=i,spec=sp,run=s.run,seed=s.seed)
        try:
            w,info,dag=B.build_word(sp); r['value_ok']=bool(info['value_ok'])
            if w is not None: r.update(B.r0(dag)); r.update(B.fast(w))
        except Exception as ex: r.update(error=repr(ex)[:200],value_ok=False)
        r['secs']=round(time.time()-t,2); s.n_new['L1']+=1; s._put(r); return r
    def L2(s,sp):
        sp=S.normalize(sp); i=S.sid(sp)
        if ('L2',i) in s.rows: return s.rows[('L2',i)]
        t=time.time(); r=dict(level='L2',sid=i,spec=sp,run=s.run,seed=s.seed)
        try:
            w,info,dag=B.build_word(sp); r['value_ok']=bool(info['value_ok'])
            if w is not None:
                ex,iw=B.exact(w); r.update(ex)
                if ex['legal']: s._after_legal(r,w,iw)
        except Exception as ex: r.update(error=repr(ex)[:200],legal=False)
        r['secs']=round(time.time()-t,2); s.n_new['L2']+=1; s._put(r); return r
    def _after_legal(s,r,w,iw):
        k=r['kappa']
        if s.best is None or k>s.best: s.best=k
        if k>s.frontier and (r.get('admit_any') or r.get('admit_strict')):
            cf=GS+'/CANDIDATE-%s.json.gz'%r['sid']; json.dump(w,gzip.open(cf,'wt')); r['candidate_file']=cf
            from wsearch.drive import validate_file
            res=validate_file(cf,B.ANCHOR); r['validation']=res; r['flag']='CANDIDATE' if (res['accept_ok'] and res['prstack_ok']) else 'UNCONFIRMED'; print('ABOVE FRONTIER',k,r['flag'],cf,flush=True)
        if s.store is not None and s.stored<3 and (not s.top_stored or k>=s.top_stored):
            try:
                from wsearch import canon
                h=canon.canon_hash(w); s.store.put_word(h,w); s.store.add_eval(h,B.ANCHOR,True,k,validator='gensearch-exact',ok=bool(r.get('admit_strict')))
                s.store.add_lineage(h,'',{'gensearch_spec':r['spec']},'gensearch',s.seed,s.run,0); r['chash']=h; s.stored+=1; s.top_stored=max(s.top_stored or 0,k)
            except Exception as ex: r['store_err']=repr(ex)[:100]
    top_stored=None
def kh(r): return r.get('kappa_hat') or -1.0
# ------------------------------------------------------------------ strategies (deterministic functions of seed + cached rows)
def strat_random(ev,seed,deadline,batch=40,exact_top=3,log=print):
    i=0; pool=[]
    while time.time()<deadline:
        for _ in range(batch):
            if time.time()>=deadline: break
            sp=S.sample(random.Random('r%d/%d'%(seed,i))); i+=1; r=ev.L1(sp)
            if r.get('kappa_hat'): pool.append(r)
        done=0
        for r in sorted(pool,key=kh,reverse=True):
            if done>=exact_top or time.time()>=deadline: break
            if ('L2',r['sid']) not in ev.rows: done+=1
            ev.L2(r['spec'])
        log('random draws %d  L1 best %.9f  L2 best %s  new %s'%(i,max([kh(p) for p in pool] or [0]),ev.best,ev.n_new),flush=True)
def strat_evo(ev,seed,deadline,lam=12,mu=4,exact_every=3,log=print):
    pop=[ev.L1(S.sample(random.Random('e%d/init%d'%(seed,i)))) for i in range(lam)]; pop=[p for p in pop if p.get('kappa_hat')]; sigma=1.0; gen=0
    while time.time()<deadline:
        pop.sort(key=kh,reverse=True); par=pop[:mu]; rng=random.Random('e%d/g%d'%(seed,gen)); kids=[]; succ=0
        for _ in range(lam):
            if time.time()>=deadline: break
            p=rng.choice(par); c=ev.L1(S.mutate(rng,p['spec'],sigma))
            if c.get('kappa_hat'):
                kids.append(c); succ+=kh(c)>kh(par[-1])
        seen={r['sid'] for r in pop}; pop=pop+[k for k in kids if k['sid'] not in seen]; pop.sort(key=kh,reverse=True); pop=pop[:max(mu*3,lam)]
        sigma=min(2.5,sigma*1.2) if kids and succ/len(kids)>.2 else max(.3,sigma*.85); gen+=1
        if gen%exact_every==0:
            for r in pop[:2]: ev.L2(r['spec'])
        log('evo gen %d sigma %.2f  L1 best %.9f  L2 best %s  new %s'%(gen,sigma,kh(pop[0]),ev.best,ev.n_new),flush=True)
    for r in pop[:3]: ev.L2(r['spec'])
def strat_halving(ev,seed,deadline,n0=90,eta=3,exact_top=4,log=print):
    rd=0
    while time.time()<deadline:
        specs=[S.sample(random.Random('h%d/%d/%d'%(seed,rd,i))) for i in range(n0)]
        r0=[ev.L0(sp) for sp in specs if time.time()<deadline]; r0=[r for r in r0 if r.get('r0') is not None and r.get('value_ok')]; r0.sort(key=lambda r:r['r0'])
        l1=[ev.L1(r['spec']) for r in r0[:max(1,len(r0)//eta)] if time.time()<deadline]; l1=[r for r in l1 if r.get('kappa_hat')]; l1.sort(key=kh,reverse=True)
        for r in l1[:exact_top]:
            if time.time()<deadline: ev.L2(r['spec'])
        rd+=1; log('halving round %d: %d -> %d -> %d  L1 best %.9f  L2 best %s  new %s'%(rd,len(specs),len(r0)//eta,min(exact_top,len(l1)),kh(l1[0]) if l1 else 0,ev.best,ev.n_new),flush=True)
STRATS=dict(random=strat_random,evo=strat_evo,halving=strat_halving)
# ------------------------------------------------------------------ analysis
def _rank(x):
    o=sorted(range(len(x)),key=lambda i:x[i]); r=[0]*len(x)
    for p,i in enumerate(o): r[i]=p
    return r
def corr(a,b):
    n=len(a)
    if n<3: return None
    ma,mb=sum(a)/n,sum(b)/n; va=sum((x-ma)**2 for x in a); vb=sum((y-mb)**2 for y in b)
    return None if va==0 or vb==0 else sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb)
def report(path=None):
    rows={}; 
    for l in open(path or GS+'/cpu_results.jsonl'):
        try: r=json.loads(l); rows[(r['level'],r['sid'])]=r
        except Exception: pass
    L={lv:[r for (l,_),r in rows.items() if l==lv] for lv in('L0','L1','L2')}
    out={lv:len(v) for lv,v in L.items()}
    l1=[r for r in L['L1'] if r.get('kappa_hat')]; out['L1_value_ok']=sum(1 for r in L['L1'] if r.get('value_ok')); out['L1_errors']=sum(1 for r in L['L1'] if r.get('error'))
    out['L1_strict_admissible']=sum(1 for r in l1 if r.get('admit_strict')); out['L1_strict_events_ok']=sum(1 for r in l1 if r.get('strict_events_ok')); out['L1_strict_scalar_ok']=sum(1 for r in l1 if r.get('strict_scalar_ok'))
    l2=L['L2']; leg=[r for r in l2 if r.get('legal')]; out['L2_legal']=len(leg); out['L2_admit_any']=sum(1 for r in l2 if r.get('admit_any')); out['L2_admit_strict']=sum(1 for r in l2 if r.get('admit_strict'))
    out['L2_legal_and_admit_any']=sum(1 for r in leg if r.get('admit_any'))
    out['best_exact']=max([r['kappa'] for r in leg] or [None]); 
    if leg: b=max(leg,key=lambda r:r['kappa']); out['best_spec']=b['spec']; out['best_sid']=b['sid']
    pairs=[(rows.get(('L1',r['sid'])),r) for r in leg]; pairs=[(a,b) for a,b in pairs if a and a.get('kappa_hat')]
    if len(pairs)>=3:
        x=[a['kappa_hat'] for a,b in pairs]; y=[b['kappa'] for a,b in pairs]; out['n_pairs']=len(pairs)
        out['pearson_khat_exact']=corr(x,y); out['spearman_khat_exact']=corr(_rank(x),_rank(y)); out['max_abs_khat_minus_exact']=max(abs(a-b) for a,b in zip(x,y))
        r0=[-a['r0'] for a,b in pairs]; out['pearson_r0_exact']=corr(r0,y); out['spearman_r0_exact']=corr(_rank(r0),_rank(y))
    both=[r for r in L['L1'] if r.get('kappa_hat') and r.get('r0')]
    if len(both)>=3: out['n_L1']=len(both); out['pearson_r0_khat_L1']=corr([-r['r0'] for r in both],[r['kappa_hat'] for r in both]); out['spearman_r0_khat_L1']=corr(_rank([-r['r0'] for r in both]),_rank([r['kappa_hat'] for r in both]))
    # all L0 vs L1 (dag-only R0 vs fast kappa)
    return out
def main(a):
    os.environ['TK_FREE_BOUNDS']='1'
    if a.report: print(json.dumps(report(),indent=1,default=str)); return 0
    if a.cpuq: return write_cpuq(a)
    run=a.run or '%s-s%d'%(a.strategy,a.seed); ev=Ev(run,store=a.store,seed=a.seed,frontier=float(a.frontier)); dl=time.time()+60*a.minutes
    print('gensearch',run,'strategy',a.strategy,'minutes',a.minutes,'cache rows',len(ev.rows),flush=True)
    STRATS[a.strategy](ev,a.seed,dl)
    rep=report(); print('DONE',json.dumps({k:rep.get(k) for k in('L0','L1','L2','L2_legal','best_exact','pearson_khat_exact','spearman_r0_exact')},default=str),flush=True)
    return 0
def write_cpuq(a):
    base=W + '/ext/GENSEARCH'; os.makedirs(W+'/jobs/pending',exist_ok=True); n=0
    for k,(strat,seed,mins) in enumerate(eval(a.plan)):
        name='%s%d_%s_s%d'%(a.cpuq,k,strat,seed); job=W+'/jobs/pending/%s.sh'%name
        cmd='TK_FREE_BOUNDS=1 %s -B %s/tk.py gensearch --strategy %s --seed %d --minutes %d --run %s --store default --frontier %s >> %s/%s.log 2>&1'%(sys.executable,os.path.dirname(HERE),strat,seed,mins,name,a.frontier,base,name)
        open(job,'w').write('#!/bin/bash\n# timeout: %d\n# threads: 1\ncd %s\n%s\necho "%s: gensearch %s seed %d %d min -> $(grep DONE %s/%s.log | tail -1 | cut -c1-260) (ext/GENSEARCH/cpu_results.jsonl)" >> %s/the results log\n'%(mins*60+1800,W,cmd,name.upper(),strat,seed,mins,base,name,W))
        os.chmod(job,0o755); print('wrote',job); n+=1
    return 0
