"""synth.learned -- GENLEARN: rules mined from the swarm lineage (#5561 -> #5599 -> #5660 -> #5718 -> #5756) as samplers + a verified tightener.  See ../GENLEARN-RULEBOOK.md, ../module docstring.

  build_rules(aliases) -> dict          statistics of the raw programs (synth/learned_stats.py) condensed into sampling tables; saved to synth/data/learned_rules.json
  RULES                                 the saved tables (loaded lazily)
  tax(ranks)                            D ln D - sum r ln r : the helper-line law (cost = k * sum tax, ratio .996 to the exact invoice on all lineage words)
  helper_report(dag)                    per-helper first/last use frame dims, d0 flag, class, chain, loose-endpoint slack, tax
  postprocess(dag, spec, rng)           the `helpers: learned` / `schedule: learned` modes of gen.generate (spec['modes']={'helpers':'learned','schedule':'learned','seed':s}):
       helpers learned:  R1 tight endpoints (init := first-use frame for helpers without a dim-0 event; final := last-use frame), then R2 stop-count resampling of every recorded helper hop chain
                         (target #stops ~ class table; surplus intermediate stops dropped, deficits filled by splitting the longest hop at a random sub-frame)
       schedule learned: R3 the same for the X and Y main registers (target stops from the X / Y tables)
  Every transform is value-neutral (ops untouched); frame legality is left to repair.evaluate/IncrWord.
"""
import sys,os,json,math,random,collections
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE)); sys.path.insert(0,HERE)
DATA=HERE+'/data/learned_rules.json'
def tax(ranks):
    ranks=[r for r in ranks if r>0]; D=sum(ranks)
    return (D*math.log(D) if D else 0.0)-sum(r*math.log(r) for r in ranks)
def _span(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return s
def build_rules(aliases=('5561','5599','5660','5718','5756')):
    import learned_stats as L
    R=dict(words=list(aliases))
    per={}
    for a in aliases:
        w=L.loadw(a); fr=w['frames']; n=len(w['initial']); live=set(w['live']); dim=lambda f:len(fr[f])
        role=lambda r:'X' if r in live else ('Y' if r-112 in live and r<n else 'H')
        it={r:[dim(w['initial'][r])] for r in range(n)}
        first={};last={};d0=set()
        for e in w['program']:
            if e[0]=='MOVE' and e[1]<n: it[e[1]].append(dim(e[3]))
            elif e[0] in('ADD','COPY'):
                f=dim(e[4])
                for r in (e[1],e[2]):
                    if r<n:
                        first.setdefault(r,f); last[r]=f
                        if f==0: d0.add(r)
        P=dict(slack_init=0,slack_final=0,helpers=0)
        mv=collections.defaultdict(collections.Counter); trans=collections.Counter(); rs=collections.Counter(); start=collections.Counter(); fin=collections.Counter()
        xs=collections.Counter(); ys=collections.Counter(); xr=collections.Counter(); yr=collections.Counter()
        for r in range(n):
            s=it[r]; rk=tuple(s[i+1]-s[i] for i in range(len(s)-1))
            if role(r)=='H' and r in first:
                P['helpers']+=1; key='d0' if r in d0 else 'late'
                mv[key][len(rk)]+=1; start[(key,s[0])]+=1; fin[(last[r],s[-1])]+=1
                P['slack_init']+=int(s[0]<first[r]); P['slack_final']+=int(s[-1]>last[r])
                for i in range(len(s)-1): trans[(s[i],s[i+1])]+=1
                rs[(key,rk)]+=1
            elif role(r)=='X': xs[len(rk)]+=1; xr[rk]+=1
            elif role(r)=='Y': ys[len(rk)]+=1; yr[rk]+=1
        per[a]=dict(P=P,mv={k:dict(v) for k,v in mv.items()},start={str(k):v for k,v in start.items()},fin={str(k):v for k,v in fin.items()},
                    trans={'%d>%d'%k:v for k,v in trans.items()},rs={'%s:%s'%(k[0],''.join(map(str,k[1]))):v for k,v in rs.items()},xs=dict(xs),ys=dict(ys),
                    xr={''.join(map(str,k)):v for k,v in xr.items()},yr={''.join(map(str,k)):v for k,v in yr.items()})
    R['per_word']=per
    R['anchor']=per[aliases[-1]]
    return R
_R=[None]
def rules():
    if _R[0] is None:
        if not os.path.exists(DATA):
            os.makedirs(os.path.dirname(DATA),exist_ok=True); json.dump(build_rules(),open(DATA,'w'))
        _R[0]=json.load(open(DATA))
    return _R[0]
def _dim(fr,f):
    return len(fr[f]) if isinstance(f,int) else len(f)
def helper_report(dag):
    """for every helper (and, with roles=True semantics, every register): chain of op frames, hop frames, first/last use dim, d0 flag, slack, tax"""
    fr=dag['frames']; ops=dag['ops']; regs=dag['regs']; hops={}
    for i,r,fs in dag['schedule'].get('hops',[]): hops.setdefault((i,r),[]).extend(fs)
    out={}
    for r,v in regs.items():
        r=int(r); role,i0,f0=v if isinstance(v,(list,tuple)) else (None,None,None)
        out[r]=dict(role=role,init=i0,final=f0,uses=[],hopat={})
    for j,o in enumerate(ops):
        for r in ((o[1],o[2]) if o[0] in('ADD','COPY') else (o[1],)):
            if r is not None and r in out: out[r]['uses'].append((j,o[4]))
    for (i,r),fs in hops.items():
        if r in out: out[r]['hopat'][i]=fs
    return out
def _chain(info,fr):
    """list of frames the register passes: init, hop stops and op frames in time order (as realise would MOVE)"""
    ch=[info['init']] if info['init'] is not None else []
    for j,f in info['uses']:
        for x in info['hopat'].get(j,[]): ch.append(x)
        ch.append(f)
    for x in info['hopat'].get(10**9,[]): ch.append(x)
    return ch
def _nmoves(info,hops,r):
    """number of MOVEs of register r implied by its (init, hop stops, op frames, final) chain"""
    ch=[info['init']]
    for j,f in info['uses']:
        ch+=list(hops.get((j,r),[])); ch.append(f)
    ch+=list(hops.get((10**9,r),[])); 
    if info['final'] is not None: ch.append(info['final'])
    return sum(1 for a,b in zip(ch,ch[1:]) if a!=b)
def _sample_count(cnt,rng):
    items=sorted((int(k),v) for k,v in cnt.items()); t=sum(v for _,v in items); u=rng.random()*t
    for k,v in items:
        u-=v
        if u<=0: return k
    return items[-1][0]
def postprocess(dag,spec,rng):
    """apply the learned modes to a tk-dag/1 dict IN PLACE; returns a log dict.
    helpers learned : R1 tight endpoints (a helper without a dim-0 event whose first use is at dim 1..8 starts AT its first-use frame; every helper ends AT its last-use frame
                      when that frame is below the declared final) and R2 no idle stops (hop frames other than the op frame are dropped).  Both are value-neutral and never raise the tax;
                      on the swarm lineage they are no-ops (0 slack in 2,694 helper instances), on FRONTGEN STAR they are no-ops (every helper is dim-0 loaded and ends at its dim-9 restore).
    schedule learned: R2 for the X / Y main registers, and (rng) re-draw of each main's stop pattern is NOT done: stops of mains are all op frames (0 idle stops in 17k MOVEs)."""
    log=dict(init_raised=0,final_lowered=0,idle_stops_dropped=0,main_idle_dropped=0)
    M=spec.get('modes',{}); HM=M.get('helpers')=='learned'; SM=M.get('schedule')=='learned'
    if not(HM or SM): return log
    fr=dag['frames']; ops=dag['ops']; n=dag['meta']['npub']; info=helper_report(dag)
    key=lambda f:frozenset(_span(fr[f] if isinstance(f,int) else f))
    hops=collections.defaultdict(list)
    for i,r,fs in dag['schedule'].get('hops',[]): hops[(i,r)].extend(fs)
    d0=set()
    for j,o in enumerate(ops):
        if o[0] in('ADD','COPY') and _dim(fr,o[4])==0: d0.add(o[1]); d0.add(o[2])
    opf={}
    for r,v in info.items(): opf[r]=dict(v['uses'])
    for r,v in info.items():
        if r>=n or not v['uses']: continue
        role=v['role']
        if role=='helper' and HM:
            f1=v['uses'][0][1]; d1=_dim(fr,f1)
            if r not in d0 and 1<=d1<=8 and key(v['init'])<key(f1):
                dag['regs'][str(r)][1]=f1; hops.pop((v['uses'][0][0],r),None); log['init_raised']+=1
            fl=v['uses'][-1][1]
            if key(v['final'])>key(fl):
                dag['regs'][str(r)][2]=fl; hops.pop((len(ops),r),None); log['final_lowered']+=1
        if (role=='helper' and HM) or (role in('X','Y') and SM):
            for (i,rr),fs in list(hops.items()):
                if rr!=r or len(fs)<2: continue
                tgt=opf[r].get(i)
                if tgt is not None and key(fs[-1])==key(tgt):
                    kept=[fs[-1]]; log['idle_stops_dropped' if role=='helper' else 'main_idle_dropped']+=len(fs)-1; hops[(i,rr)]=kept
    dag['schedule']['hops']=[[i,r,fs] for (i,r),fs in hops.items() if fs]
    return log
def rule_audit(w):
    """audit a WORD (dict) against the rulebook rules; returns metrics (all counts; 0 is conforming for slack/idle/untight)"""
    import collections
    fr=w['frames']; n=len(w['initial']); live=set(w['live']); dim=lambda f:len(fr[f]) if isinstance(f,int) else len(f)
    role=lambda r:'O' if r>=n else ('X' if r in live else ('Y' if r-112 in live else 'H'))
    first={};last={};d0=set();it={r:[dim(w['initial'][r])] for r in range(n)}; pend={}; idle=collections.Counter(); mv=collections.Counter()
    for e in w['program']:
        if e[0]=='MOVE':
            r=e[1]; mv[role(r)]+=1
            if r in pend: idle[role(r)]+=1
            pend[r]=1
            if r<n: it[r].append(dim(e[3]))
        else:
            for r in ([e[1],e[2]] if e[0] in('ADD','COPY') and e[2] is not None else [e[1]]):
                pend.pop(r,None)
                if r<n and e[0] in('ADD','COPY'):
                    f=dim(e[4]); first.setdefault(r,f); last[r]=f
                    if f==0: d0.add(r)
    hel=[r for r in range(n) if role(r)=='H']
    si=[r for r in hel if r in first and r not in d0 and it[r][0]<first[r]]; sf=[r for r in hel if r in first and it[r][-1]>last[r]]
    tx=sum(tax([it[r][i+1]-it[r][i] for i in range(len(it[r])-1)]) for r in hel)
    jl=sum(1 for e in w['program'] if e[0]=='ADD' and e[4] is not None and dim(e[4])==0 and role(e[1])=='Y' and e[2]<n and role(e[2])=='H')
    return dict(helpers=len(hel),helper_tax=round(tx,1),tax_per_helper=round(tx/max(1,len(hel)),2),loose_init=len(si),loose_final=len(sf),loose_init_ranks=sum(first[r]-it[r][0] for r in si),loose_final_ranks=sum(it[r][-1]-last[r] for r in sf),
                idle_stops=dict(idle),moves=dict(mv),dim0_born=sum(1 for r in hel if it[r][0]==0),dim0_junk_loads_Y_from_H=jl,
                helpers_with_dim0_event=sum(1 for r in hel if r in d0),d0_but_not_born_at_0=sum(1 for r in hel if r in d0 and it[r][0]>0),untouched=sum(1 for r in hel if r not in first))

def run(a):
    """tk synth --learned N [--anchor A] [--seed S] [--helpers learned] [--schedule learned] [--front-gen]: N draws of the learned modes; every draw evaluated exactly
    (IncrWord, TK_FREE_BOUNDS=1) and compared with the unmodified template (anchor) or the FRONTGEN word.  Prints per-draw kappa, transforms applied, and the cost-line breakdown of the best/median draw."""
    import time,gzip
    os.environ['TK_FREE_BOUNDS']='1'
    from tkcommon import load,profile_of,DATA_PROFILES
    import incr, dag as D
    from synth import sample as SM, gen as G, repair as RP, frontgen as FG
    anchor=a.anchor; profile=a.profile_name or (anchor if anchor in DATA_PROFILES else None)
    p,w0=load(anchor); profile=profile or profile_of(w0)[0]
    spec=SM.anchor_spec(anchor,profile)
    base_front=bool(getattr(a,'front_gen',False))
    if base_front: spec=dict(spec,front='generated',back='generated:'+getattr(a,'back','star')); spec.pop('body',None)
    modes={}
    if (getattr(a,'helpers',None) or 'learned')=='learned': modes['helpers']='learned'
    if getattr(a,'schedule',None)=='learned': modes['schedule']='learned'
    i0=incr.IncrWord(w0,profile=profile); k_anchor=i0.kappa
    t=time.time(); w,info=G.build_word(spec,None); ib=incr.IncrWord(w,profile=profile); k_base=ib.kappa
    print('base (%s, no modes): legal %s kappa %.15f   anchor %s kappa %.15f   %.1fs'%('FRONTGEN' if base_front else 'template',ib.legal_all,k_base,anchor,k_anchor,time.time()-t))
    rows=[]; best=None
    for i in range(a.learned):
        sp=dict(spec,modes=dict(modes,seed=a.seed*100003+i))
        t=time.time(); w,info=G.build_word(sp,None)
        if w is None: rows.append(dict(i=i,value=False)); continue
        ev=RP.evaluate(w,profile); rep=0
        if not ev['legal'] and not base_front:
            w2,fx,ok=RP.repair(w,profile); rep=len(fx)
            if ok: w=w2; ev=RP.evaluate(w,profile)
        rows.append(dict(i=i,legal=ev['legal'],kappa=ev['kappa'],fixes=rep,log=info.get('learned'),secs=round(time.time()-t,1)))
        if ev['legal'] and (best is None or ev['kappa']>best[0]): best=(ev['kappa'],i,w)
        print('draw %d legal %s kappa %.15f (d vs base %+.3e, vs anchor %+.3e) fixes %d %s'%(i,ev['legal'],ev['kappa'],ev['kappa']-k_base,ev['kappa']-k_anchor,rep,info.get('learned')),flush=True)
    leg=[r for r in rows if r.get('legal')]
    print('SUMMARY draws %d legal %d  kappa>=base %d  best %s'%(len(rows),len(leg),sum(1 for r in leg if r['kappa']>=k_base-1e-15),'%.15f'%best[0] if best else None))
    if best and best[0]>k_anchor+1e-13 and not base_front:
        out=a.out or (os.path.dirname(HERE)+'/out/learned_best.json.gz'); D.save(best[2],out); print('ABOVE ANCHOR: wrote',out,'-> validate with: tk accept --native-ref')
    if base_front and best:
        FG.gap_report(w0,best[2],profile)
    return 0

def counterfactual(anchor='5756',profile=None):
    """price of VIOLATING the tightness rules on the anchor template (evidence beyond counts): loosen all late starters to start at the zero frame (R1a), loosen all lowered finals to dim 9 (R1b), both."""
    os.environ['TK_FREE_BOUNDS']='1'
    from tkcommon import load,profile_of
    import incr, dag as D, copy
    from synth import sample as SM, gen as G, repair as RP
    p,w0=load(anchor); profile=profile or profile_of(w0)[0]
    spec=SM.anchor_spec(anchor,profile); dag,info=G.generate(spec)
    fr=dag['frames']; z=next(i for i,b in enumerate(fr) if len(b)==0); f9=next(i for i,b in enumerate(fr) if len(b)==9)
    out={}
    for name,li,lf in (('anchor',0,0),('late starters -> zero frame',1,0),('lowered finals -> dim 9',0,1),('both',1,1)):
        d2=dict(dag); d2['regs']={k:list(v) for k,v in dag['regs'].items()}; ni=nf=0
        for k,v in d2['regs'].items():
            if v[0]!='helper': continue
            if li and len(fr[v[1]])>0: v[1]=z; ni+=1
            if lf and len(fr[v[2]])<9: v[2]=f9; nf+=1
        w,_=D.realise(d2,None,(),verify=False); w['verifier_profile']=w0.get('verifier_profile') if 'verifier_profile' in w0 else w.get('verifier_profile')
        ev=RP.evaluate(w,profile); out[name]=dict(legal=ev['legal'],kappa=ev['kappa'],changed_init=ni,changed_final=nf,n_viol=ev['n_viol'],viol=ev['viol'][:2])
        print('%-30s legal %s kappa %.12f (d %+.3e) init loosened %d final loosened %d %s'%(name,ev['legal'],ev['kappa'],ev['kappa']-out['anchor']['kappa'],ni,nf,ev['viol'][:1]))
    return out

def tighten_demo(anchor='5756',profile=None):
    """loosen every endpoint of the anchor (counterfactual 'both'), then apply `helpers: learned`: kappa must return to the anchor except for rule exceptions (first use at dim 9)"""
    os.environ['TK_FREE_BOUNDS']='1'
    from tkcommon import load,profile_of
    import dag as D, random
    from synth import sample as SM, gen as G, repair as RP
    p,w0=load(anchor); profile=profile or profile_of(w0)[0]
    spec=SM.anchor_spec(anchor,profile); dag,info=G.generate(spec)
    fr=dag['frames']; z=next(i for i,b in enumerate(fr) if len(b)==0); f9=next(i for i,b in enumerate(fr) if len(b)==9)
    d2=dict(dag); d2['regs']={k:list(v) for k,v in dag['regs'].items()}; d2['schedule']=dict(dag['schedule'])
    for k,v in d2['regs'].items():
        if v[0]=='helper':
            if len(fr[v[1]])>0: v[1]=z
            if len(fr[v[2]])<9: v[2]=f9
    w,_=D.realise(d2,None,(),verify=False); kl=RP.evaluate(w,profile)['kappa']
    log=postprocess(d2,dict(modes=dict(helpers='learned')),random.Random(0))
    w,_=D.realise(d2,None,(),verify=False); ev=RP.evaluate(w,profile)
    k0=RP.evaluate(D.realise(dag,None,(),verify=False)[0],profile)['kappa']
    print('anchor %.12f loosened %.12f tightened %.12f (legal %s) log %s'%(k0,kl,ev['kappa'],ev['legal'],log))
    return dict(anchor=k0,loose=kl,tight=ev['kappa'],legal=ev['legal'],log=log)
