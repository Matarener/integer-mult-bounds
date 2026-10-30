"""synth.sample -- `tk synth`: spec I/O, round trip, random sampler.
KNOBS (name -> (probability that a draw uses it, sampler)) is the DOCUMENTED DISTRIBUTION around the anchor spec (default 5718: the fuzz-tested profile; 5756-family words need --relax-style
verdicts.  A draw takes each class independently with the listed probability (at least one class is forced), and composes the knobs:
  owned_perm 0.35   uniform random permutation of the 8 root owned ids          root_order 0.35  uniform random permutation of the 8 root lifetimes in time
  sign_flip  0.30   each root negated with p=0.4                                 root_scale 0.20  1-3 roots multiplied by 2^k, k in {-1,1,2}
  order      0.30   N~logU[200,6000] neighbour moves, window~U[50,500]           helper_init 0.30 frac~logU[1e-3,0.1] of helpers start from a random sub-frame (credit up, one more MOVE)
  helper_final 0.30 frac~logU[1e-3,0.1] of helpers end in a random super-frame   hop_split   0.30 frac~logU[1e-3,0.05] of >=2-dim MOVEs get a random intermediate stop
  hop_lazy   0.05   drop the recorded hop chains (lazy direct MOVEs)
Results: one JSON line per draw in SYNTH/cpu_results.jsonl (or --out) with the knobs, value_ok, legal before/after repair, fixes, kappa, delta vs the anchor and canon hash; legal words that are new
(canon hash not seen before) and best-so-far go to the SEARCHCORE store when --store is given.  A draw above --frontier is validated (tk accept --native-ref via wsearch.drive.validate_file) and written
to SYNTH/CANDIDATE-<hash>.json.gz.
"""
import sys,os,json,gzip,time,math,random
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.dirname(HERE); sys.path.insert(0,TKD)
from tkcommon import *
import dag as D, incr
from synth import spec as S, gen as G, repair as R
SYN=W + '/ext/SYNTH'
KNOBS=dict(owned_perm=.35,root_order=.35,sign_flip=.30,root_scale=.20,order=.30,helper_init=.30,helper_final=.30,hop_split=.30,hop_lazy=.05)
def logu(rng,a,b): return math.exp(rng.uniform(math.log(a),math.log(b)))
def draw_wild(rng,spec):
    """WILD distribution (--classes wild): every class on with wide ranges, order swaps that ignore read/write dependences half of the time -> exercises value rejection and the legaliser"""
    kn,pick=draw_knobs(rng,spec,None)
    kn.update(helper_init='rand',helper_final='rand',helper_frac=rng.choice([.1,.3,.7,1.0]),helper_seed=rng.randrange(10**6),hop_policy='split',hop_frac=rng.choice([.05,.2,.5]),hop_seed=rng.randrange(10**6))
    if rng.random()<.5: kn.update(event_order='swap',order_swaps=int(logu(rng,500,20000)),order_window=rng.randint(50,2000),order_seed=rng.randrange(10**6),order_unsafe=rng.random()<.5)
    return kn,pick+['wild']
def draw_knobs(rng,spec,classes=None):
    roots=[r['reg'] for r in spec['roots']]; names=[k for k in KNOBS if classes is None or k in classes]
    pick=[k for k in names if rng.random()<KNOBS[k]] or [rng.choice(names)]
    kn={}
    for k in pick:
        if k=='owned_perm': p=roots[:]; rng.shuffle(p); kn['owned_perm']={r:q for r,q in zip(roots,p)}
        elif k=='root_order': p=list(range(len(roots))); rng.shuffle(p); kn['root_order']=p
        elif k=='sign_flip': kn['sign_flip']=[r for r in roots if rng.random()<.4] or [rng.choice(roots)]
        elif k=='root_scale': kn['root_scale']={r:str(rng.choice([.5,2,4])).replace('.5','1/2').replace('.0','') for r in rng.sample(roots,rng.randint(1,3))}
        elif k=='order': kn.update(event_order='swap',order_swaps=int(logu(rng,200,6000)),order_window=rng.randint(50,500),order_seed=rng.randrange(10**6))
        elif k=='helper_init': kn.update(helper_init='rand',helper_frac=logu(rng,1e-3,.1),helper_seed=rng.randrange(10**6))
        elif k=='helper_final': kn.update(helper_final='rand',helper_frac=logu(rng,1e-3,.1),helper_seed=kn.get('helper_seed',rng.randrange(10**6)))
        elif k=='hop_split': kn.update(hop_policy='split',hop_frac=logu(rng,1e-3,.05),hop_seed=rng.randrange(10**6))
        elif k=='hop_lazy' and 'hop_policy' not in kn: kn.update(hop_policy='lazy')
    return kn,pick
def anchor_spec(anchor,profile):
    path=SYN+'/spec_%s.json.gz'%anchor
    if os.path.exists(path): return D.load(path)
    s=S.spec_from_word(anchor,profile=profile,alias=anchor); os.makedirs(SYN,exist_ok=True); D.save(s,path); return s
def evaluate_spec(spec,knobs,profile,repair=True,want_word=False):
    t=time.time(); row=dict(knobs={k:v for k,v in knobs.items()})
    w,info=G.build_word(spec,knobs); row['value_ok']=info['value_ok']; row['log']=info['log']
    if w is None: row.update(legal0=False,legal=False,kappa=None,reason='value',bad_regs=info['bad_regs']); return row,None
    ev=R.evaluate(w,profile); row['legal0']=ev['legal']; row['kappa0']=ev['kappa']
    if not ev['legal']:
        row['viol0']=ev['viol'][:3]; row['bad_pairs0']=ev['bad_pairs']
        if repair:
            w2,fx,ok=R.repair(w,profile); row['fixes']=fx[:12]; row['n_fixes']=len(fx)
            if ok: w=w2; ev=R.evaluate(w,profile)
            else: ev=R.evaluate(w2,profile); row['viol']=ev['viol'][:3]; row['bad_pairs']=ev['bad_pairs']
    row['legal']=ev['legal']; row['kappa']=ev['kappa'] if ev['legal'] else None; row['kappa_illegal']=None if ev['legal'] else ev['kappa']; row['secs']=round(time.time()-t,2)
    return row,(w if ev['legal'] else None)
def roundtrip(a):
    anchor=a.roundtrip; profile=a.profile_name or (anchor if anchor in DATA_PROFILES else None)
    p,w0=load(anchor); profile=profile or profile_of(w0)[0]
    t=time.time(); spec=anchor_spec(anchor,profile); t1=time.time()
    dag,info=G.generate(spec,verify=True); w,_=G.build_word(spec,verify=True); t2=time.time()
    i0=incr.IncrWord(w0,profile=profile); i1=incr.IncrWord(w,profile=profile)
    print('roundtrip %s (profile %s): spec %.1fs, gen+realise %.1fs'%(anchor,profile,t1-t,t2-t1))
    print('  value_ok (generated DAG delivers the contract: Y_j += X_j, X_j, helpers, owned 0): %s'%info['value_ok'])
    print('  legal anchor %s  regenerated %s (native bad pairs %d)'%(i0.legal_all,i1.legal_all,len(i1.bad_pairs)))
    print('  kappa anchor      %.18f\n  kappa regenerated %.18f   SAME=%s'%(i0.kappa,i1.kappa,i0.kappa==i1.kappa))
    print('  invoice: paid equal %s, helper credits equal %s; events %d vs %d, MOVEs %d vs %d'%(dict(i0.paid)==dict(i1.paid),dict(i0.hel)==dict(i1.hel),len(w0['program']),len(w['program']),sum(e[0]=='MOVE' for e in w0['program']),sum(e[0]=='MOVE' for e in w['program'])))
    try:
        from wsearch import canon; c0,c1=canon.canon_hash(w0),canon.canon_hash(w); print('  canon hash anchor %s regenerated %s EQUAL=%s'%(c0[:12],c1[:12],c0==c1))
    except Exception as ex: print('  canon unavailable',ex)
    return 0 if (info['value_ok'] and i1.legal_all and i0.kappa==i1.kappa) else 1
def append(path,row):
    with open(path,'a') as f: f.write(json.dumps(row,default=str)+'\n')
def sample(a):
    if not getattr(a,'strict_bounds',False): os.environ['TK_FREE_BOUNDS']='1'     # wild/mass-split draws hit the 26000 event-cap convention; kappa is unaffected
    anchor=a.anchor; profile=a.profile_name or (anchor if anchor in DATA_PROFILES else None)
    p,w0=load(anchor); profile=profile or profile_of(w0)[0]
    spec=anchor_spec(anchor,profile); k0=incr.IncrWord(w0,profile=profile).kappa
    out=a.out or SYN+'/cpu_results.jsonl'; os.makedirs(os.path.dirname(out),exist_ok=True)
    done=set()
    if os.path.exists(out):
        for l in open(out):
            try: j=json.loads(l); done.add((j['seed'],j['i']))
            except Exception: pass
    classes=None if a.classes=='all' else a.classes.split(',')
    store=None; canon=None
    try:
        from wsearch import canon as canon_mod; canon=canon_mod
        if a.store:
            from wsearch.store import Store; store=Store(None if a.store=='default' else a.store)
    except Exception as ex: print('store/canon unavailable:',ex)
    seen={}; fr=float(a.frontier); cpu0=time.process_time(); n=bad=0; best=(k0,'anchor'); stats=dict(draws=0,value_illegal=0,legal0=0,legal=0,repaired=0,neutral=0,above=0,worse=0)
    for i in range(a.random):
        if (a.seed,i) in done: continue
        if (time.process_time()-cpu0)/3600>a.budget: print('budget reached at draw',i); break
        rng=random.Random(a.seed*1000003+i); kn,pick=draw_wild(rng,spec) if classes==['wild'] else draw_knobs(rng,spec,classes)
        row,w=evaluate_spec(spec,kn,profile,repair=not a.no_repair)
        row.update(seed=a.seed,i=i,classes=pick,anchor=anchor,profile=profile,delta=None if row['kappa'] is None else row['kappa']-k0)
        stats['draws']+=1; stats['value_illegal']+=(not row['value_ok']); stats['legal0']+=bool(row.get('legal0')); stats['legal']+=bool(row['legal']); stats['repaired']+=bool(row['legal'] and not row.get('legal0'))
        if w is not None:
            h=canon.canon_hash(w) if canon else None; row['chash']=h
            row['new']=h not in seen if h else None
            if h: seen.setdefault(h,i)
            d=row['delta']
            if abs(d)<1e-15: stats['neutral']+=1
            elif d<0: stats['worse']+=1
            if row['kappa']>best[0]+1e-15: best=(row['kappa'],'draw %d'%i)
            if store and h and row['new'] and row['kappa']>k0+1e-15:       # only words ABOVE the anchor go to the shared store (neutral relabellings stay in the jsonl)
                store.put_word(h,w)
                store.add_eval(h,profile,True,row['kappa'],validator='fast'); store.add_lineage(h,'',{'synth_knobs':kn},'synth',a.seed,'synth%d'%a.seed,i)
            if row['kappa']>fr:
                stats['above']+=1; os.makedirs(SYN,exist_ok=True); cf=SYN+'/CANDIDATE-%s.json.gz'%(h or str(i))[:12]; D.save(w,cf)
                from wsearch.drive import validate_file
                res=validate_file(cf,profile); row['validation']=res; row['flag']='CANDIDATE' if (res['accept_ok'] and res['prstack_ok']) else 'UNCONFIRMED'
                print('ABOVE FRONTIER',row['kappa'],row['flag'],cf,flush=True)
        append(out,row)
        if stats['draws']%25==0: print(json.dumps(stats),'best %.15f (%s)'%best,flush=True)
    print('DONE',json.dumps(stats),'best %.15f (%s) anchor %.15f  cpu %.0fs'%(best+(k0,time.process_time()-cpu0)),flush=True)
    return 0
def front_gen(a):
    """tk synth --front-gen: unhinted front end + junk generator (synth/frontgen.py); legal? values? kappa vs the anchor, gap by cost line"""
    if not getattr(a,'strict_bounds',False): os.environ['TK_FREE_BOUNDS']='1'
    from synth import frontgen as FG
    anchor=a.anchor if a.anchor!='5718' else '5756'; profile=a.profile_name or (anchor if anchor in DATA_PROFILES else None)
    p,w0=load(anchor); profile=profile or profile_of(w0)[0]
    spec=anchor_spec(anchor,profile); spec=dict(spec,front='generated',back='generated:'+getattr(a,'back','star'),helpers=(getattr(a,'helpers',None) or 'star')); spec.pop('body',None)
    t=time.time(); w,info=G.build_word(spec); print('front generated: value_ok',info['value_ok'],{k:v for k,v in info.items() if k not in('log',)},'%.1fs'%(time.time()-t))
    if w is None: return 1
    iw=incr.IncrWord(w,profile=profile)
    print('legal (IncrWord = legal.check + native pairs, TK_FREE_BOUNDS=%s): %s  violations %d  bad native pairs %d  kappa %.15f'%(os.environ.get('TK_FREE_BOUNDS'),iw.legal_all,len(iw.viol),len(iw.bad_pairs),iw.kappa))
    if a.out: D.save(w,a.out); print('wrote',a.out)
    if not getattr(a,'no_gap',False): FG.gap_report(w0,w,profile,ig=iw)
    return 0 if (iw.legal_all and info['value_ok']) else 1
def main(a):
    if getattr(a,'learned',0): from synth import learned as LN; return LN.run(a)
    if getattr(a,'front_gen',False): return front_gen(a)
    if a.spec_from:
        pr=a.profile_name or (a.spec_from if a.spec_from in DATA_PROFILES else None); s=S.spec_from_word(a.spec_from,profile=pr,alias=a.spec_from); out=a.out or SYN+'/spec_%s.json.gz'%a.spec_from
        os.makedirs(os.path.dirname(out),exist_ok=True); D.save(s,out); print('wrote',out,'roots',len(s['roots']),'helpers',s['helpers']['count'],'ops',len(s['body']['ops'])); return 0
    if a.roundtrip: return roundtrip(a)
    if a.gen:
        s=D.load(a.gen); pr=a.profile_name or s['family']['profile']; w,info=G.build_word(s); print(info)
        if w is None: return 1
        w2,fx,ok=R.repair(w,pr) if not R.evaluate(w,pr)['legal'] else (w,[],True); ev=R.evaluate(w2,pr); print(ev,'fixes',len(fx)); out=a.out or SYN+'/gen_word.json.gz'; D.save(w2,out); print('wrote',out); return 0 if ev['legal'] else 1
    if a.cpuq:
        job=W+'/jobs/pending/%s.sh'%a.cpuq; os.makedirs(os.path.dirname(job),exist_ok=True)
        cmd='TK_FREE_BOUNDS=1 %s -B %s/tk.py synth --random %d --seed %d --anchor %s --classes %s --budget %s --frontier %s%s'%(PY,TKD,a.random,a.seed,a.anchor,a.classes,a.budget,a.frontier,(' --store '+a.store) if a.store else '')
        open(job,'w').write('#!/bin/bash\n# timeout: %d\n# threads: 1\ncd %s\n%s >> %s/ext/SYNTH/%s.log 2>&1\necho "%s: synth sampler seed %d (%d draws) around %s -> $(grep DONE %s/ext/SYNTH/%s.log | tail -1 | cut -c1-230) (ext/SYNTH/cpu_results.jsonl)" >> %s/the results log\n'%(int(a.budget*3600*1.2)+600,W,cmd,W,a.cpuq,a.cpuq,a.seed,a.random,a.anchor,W,a.cpuq,W))
        os.chmod(job,0o755); print('wrote',job); return 0
    if a.random: return sample(a)
    print('tk synth: give --spec-from | --gen | --roundtrip | --random N'); return 2
