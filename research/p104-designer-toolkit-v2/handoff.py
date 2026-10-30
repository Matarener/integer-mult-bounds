"""tk handoff WORD [--apply] [--inline] [--out F] [--classes ...] [--top N]
Complete successor hand-off screen (TKHANDOFF).  A hand-off = for a helper h whose data has been read for the last time (event T), cut its remaining
tail (all later MOVEs/ADDs onto h) at some time s>=T, move h to a LOWER final frame F' (span(cur_h(s)) <= span(F') < span(final_h)) and cancel the residual row
(row_h - e_h) there with partner registers resident in F' at time s.  The helper's tail is a VARIABLE (final frame + pending climbs), which is what the
older in-place screens (ho4: hold at the current frame, span test at that frame only) missed -- see HOMISS/NOTES.md (#5569's helper 706).
Enumerated (every candidate is rebuilt as a full word, passes legal.check, and is priced exactly):
  S  symbolic tail retarget: for every helper h, every cut time s>=T_h, every frame F' holding residents at s: solve residual = sum c_i row_i over ALL
     residents of F' (dyadic c_i; owned scratch INITed at s included; 1, 2, 3+ partners; zero partners = pure).  Subclasses by label:
       cur   F' == cur_h(s)           (no MOVE inserted; the 'current-frame hand-off')
       ret   F' above cur_h(s)        (MOVE inserted; HOMISS tail-retarget, #5569's 706 is 1 partner)
       multi >=2 partners; scratch: some partner is an owned scratch register (>=735); pure: no partner needed
  B  relabel: keep the original tail ADD events in place, move them (and h) to F' (all ADD sources must be resident in F' at their times).
  After all candidates: --apply greedily adds compatible ones (distinct helpers, re-checked + re-priced after each), then re-enumerates until nothing positive;
  finally (J) joint retime: `tk retime W --free starts,finals,stops` is run on the handed-off word (printed command / queued).
Run it inside hq (default; --inline to run in this process)."""
import sys,os,json,gzip,copy,time,collections,decimal
from fractions import Fraction as Q
from tkcommon import *
PR=(1<<61)-1
def modq(q): return q.numerator%PR*pow(q.denominator,PR-2,PR)%PR
def dy(c):
    for k in range(0,24):
        v=c*pow(2,k,PR)%PR
        if v>PR//2: v-=PR
        if abs(v)<(1<<16): return Q(v,1<<k)
    return None
class Sim:
    """forward symbolic simulation: rows (Fraction dicts), version counters, frame residents"""
    def __init__(s,w):
        s.w=w; s.P=w['program']; s.N=len(w['initial'])+legal.nown(w)
        s.rows=[{r:Q(1)} for r in range(s.N)]; s.cur=list(w['initial'])+[None]*legal.nown(w)
        for r in legal.retired_of(w): s.cur[r]=None      # prepared573: the retired public role is owned scratch, absent until its INIT
        s.ver=[0]*s.N; s.byF=collections.defaultdict(set)
        for r,f in enumerate(s.cur):
            if f is not None: s.byF[f].add(r)
        s.mod={}
    def step(s,e):
        op,r=e[0],e[1]; rows=s.rows
        if op=='MOVE':
            s.byF[s.cur[r]].discard(r); s.cur[r]=e[3]; s.byF[e[3]].add(r); return r
        if op=='INIT':
            rows[r]={}; s.cur[r]=e[2]; s.byF[e[2]].add(r)
        elif op=='CLEAR':
            rows[r]={}; s.byF[s.cur[r]].discard(r); s.cur[r]=None
        else:
            q=Q(e[-2])
            if op=='SCALE': rows[r]={k:q*x for k,x in rows[r].items()}
            elif op=='COPY': rows[r]={k:q*x for k,x in rows[e[2]].items()}
            else:
                d=rows[r]
                for k,v in rows[e[2]].items():
                    x=d.get(k,0)+q*v
                    if x: d[k]=x
                    else: d.pop(k,None)
        s.ver[r]+=1; s.mod.pop(r,None); return r
    def mrow(s,r):
        m=s.mod.get(r)
        if m is None: m=s.mod[r]={k:modq(v) for k,v in s.rows[r].items()}
        return m
def solve(sim,h,F,cap=300):
    """find dyadic c_i (residents of F, not h) with row_h + sum c_i row_i = e_h.  returns list[(reg,Q)] or None (not representable) ; [] if residual 0"""
    tgt={}
    for k,v in sim.rows[h].items():
        if k!=h: tgt[k]=-v
    x=sim.rows[h].get(h,Q(0))
    if x!=1: tgt[h]=Q(1)-x
    if not tgt: return []
    keys=set(tgt)
    res=[r for r in sim.byF.get(F,()) if r!=h and sim.rows[r]]
    if not res: return None
    if len(res)>cap:
        res.sort(key=lambda r:-len(keys&sim.rows[r].keys())); res=res[:cap]
    union=set()
    for r in res: union|=sim.rows[r].keys()
    if not keys<=union: return None
    # modular elimination with combo tracking
    basis=[]       # (pivot,row,combo)
    for r in res:
        row=dict(sim.mrow(r)); cb={r:1}
        for pk,pr,pc in basis:
            a=row.get(pk)
            if a:
                for kk,vv in pr.items():
                    nv=(row.get(kk,0)-a*vv)%PR
                    if nv: row[kk]=nv
                    else: row.pop(kk,None)
                for kk,vv in pc.items(): cb[kk]=(cb.get(kk,0)-a*vv)%PR
        if row:
            pk=min(row); inv=pow(row[pk],PR-2,PR)
            row={kk:vv*inv%PR for kk,vv in row.items()}; cb={kk:vv*inv%PR for kk,vv in cb.items() if vv}
            basis.append((pk,row,cb))
    t={k:modq(v) for k,v in tgt.items()}; sol={}
    for pk,pr,pc in basis:
        a=t.get(pk)
        if a:
            for kk,vv in pr.items():
                nv=(t.get(kk,0)-a*vv)%PR
                if nv: t[kk]=nv
                else: t.pop(kk,None)
            for kk,vv in pc.items(): sol[kk]=(sol.get(kk,0)+a*vv)%PR
    if t: return None
    out=[]
    for r,c in sol.items():
        if c:
            q=dy(c)
            if q is None: return None
            out.append((r,q))
    # exact verification
    acc=dict(sim.rows[h])
    for r,q in out:
        for k,v in sim.rows[r].items():
            y=acc.get(k,0)+q*v
            if y: acc[k]=y
            else: acc.pop(k,None)
    if acc!={h:Q(1)}: return None
    return sorted(out)
def enumerate_S(w,log=print,allow_fin=False):
    """returns list of candidates dict(cls,h,s,F,cur,partners,fin)"""
    P=w['program']; fr=legal.spans(w); dim=[len(b) for b in w['frames']]
    NPUB=len(w['initial']); live=set(w['live']); main=live|{r+112 for r in live}
    hel=[r for r in range(NPUB) if r not in main and r not in legal.retired_of(w)]
    fin=w['final']; ini=w['initial']
    T={}; L={}; hs=set(hel)
    for i,e in enumerate(P):
        if e[0] in('ADD','COPY'): T[e[2]]=i
        if e[1] in hs: L[e[1]]=i
    rel={}
    def ok_frame(c,F,f):     # span(c) <= span(F) < span(f), F a real step or the current frame
        k=(c,F,f); v=rel.get(k)
        if v is None: v=rel[k]=(fr[F]<fr[f] or (allow_fin and fr[F]==fr[f])) and (c==F or fr[c]<fr[F])
        return v
    sim=Sim(w); seen={}; cands=[]; t0=time.time(); ntest=0
    starts=collections.defaultdict(list)
    for h in hel: starts[max(T.get(h,-1),0)].append(h)
    live_h=set()
    for s,e in enumerate(P):
        r=sim.step(e)
        new=[]
        for h in starts.get(s,()):
            if L.get(h,-1)>s and (fr[sim.cur[h]]<fr[fin[h]] or (allow_fin and fr[sim.cur[h]]<=fr[fin[h]])): live_h.add(h); new.append(h)
        if r in live_h and (L[r]<=s or (fr[sim.cur[r]]==fr[fin[r]] and not allow_fin)): live_h.discard(r)
        if not live_h: continue
        todo=[]
        for h in set(new)|({r} if r in live_h else set()):
            for F in list(sim.byF):
                if sim.byF[F] and ok_frame(sim.cur[h],F,fin[h]): todo.append((h,F))
        Fr=sim.cur[r]
        if Fr is not None:
            for h in live_h:
                if h!=r and h not in new and ok_frame(sim.cur[h],Fr,fin[h]): todo.append((h,Fr))
        for h,F in todo:
            key=(h,F,sim.ver[h],tuple(sorted((x,sim.ver[x]) for x in sim.byF[F] if x!=h))) if len(sim.byF[F])<40 else None
            if key is not None:
                if key in seen: continue
                seen[key]=1
            ntest+=1
            sol=solve(sim,h,F)
            if sol is None: continue
            cands.append(dict(h=h,s=s,F=F,cur=sim.cur[h],partners=[(x,str(q)) for x,q in sol],fin=fin[h],
                              sig=(h,F,tuple(sol)),cls=classify(sim.cur[h],F,sol)))
    log('S-enum: %d solves, %d raw candidates, %.0fs'%(ntest,len(cands),time.time()-t0))
    return cands
OWNED=set()    # owned scratch roles of the word under screen (legal.owned_set); set by screen()/main
def classify(cur,F,sol):
    c=['cur' if cur==F else 'ret']
    if not sol: c.append('pure')
    elif len(sol)>=2: c.append('multi')
    if any(x in OWNED for x,_ in sol): c.append('scratch')
    return '+'.join(c)
def build(w,c):
    """full word for candidate c (S): keep events <=s, insert MOVE+ADDs, drop later events with dest h"""
    P=w['program']; h=c['h']; s=c['s']
    ins=[]
    if c['cur']!=c['F']: ins.append(['MOVE',h,c['cur'],c['F'],False])
    for x,q in c['partners']: ins.append(['ADD',h,x,q,c['F']])
    wn=dict(w); wn['program']=P[:s+1]+ins+[e for e in P[s+1:] if e[1]!=h]
    wn['final']=list(w['final']); wn['final'][h]=c['F']
    return wn
def enumerate_B(w,log=print):
    """relabel variant: original tail ADDs (after the first tail MOVE) stay in place relabelled to F'; MOVEs of h in the tail are replaced by one MOVE to F' before the first ADD that needs it"""
    P=w['program']; fr=legal.spans(w); NPUB=len(w['initial']); live=set(w['live']); main=live|{r+112 for r in live}
    hel=[r for r in range(NPUB) if r not in main and r not in legal.retired_of(w)]; hs=set(hel); fin=w['final']
    T={}
    for i,e in enumerate(P):
        if e[0] in('ADD','COPY'): T[e[2]]=i
    tails={h:[i for i in range(T.get(h,-1)+1,len(P)) if P[i][1]==h] for h in hel}
    cur=list(w['initial'])+[None]*legal.nown(w); want={}
    for r_ in legal.retired_of(w): cur[r_]=None
    for h,t in tails.items():
        for i in t: want[i]=want.get(i,0)
    srcfr={}
    for i,e in enumerate(P):
        if i in want and e[0]=='ADD': srcfr[i]=cur[e[2]]
        if e[0]=='MOVE': cur[e[1]]=e[3]
        elif e[0]=='INIT': cur[e[1]]=e[2]      # SPEED fix (Oct 28): owned registers get their frame from INIT and lose it at CLEAR (was: None -> TypeError on #6030)
        elif e[0]=='CLEAR': cur[e[1]]=None
    out=[]
    curh=list(w['initial'])+[None]*legal.nown(w); curat={}
    for r_ in legal.retired_of(w): curh[r_]=None
    for i,e in enumerate(P):
        if i in want: curat[i]=curh[e[1]]
        if e[0]=='MOVE': curh[e[1]]=e[3]
        elif e[0]=='INIT': curh[e[1]]=e[2]
        elif e[0]=='CLEAR': curh[e[1]]=None
    for h,t in tails.items():
        mv=[i for i in t if P[i][0]=='MOVE']
        if not mv or any(P[i][0] not in('MOVE','ADD') or (P[i][0]=='ADD' and P[i][2]==h) for i in t): continue
        m1=mv[0]; adds=[i for i in t if P[i][0]=='ADD' and i>m1]
        a0=curat[m1]
        cands=set(srcfr[i] for i in adds)|{P[i][3] for i in mv}
        if a0 is None: continue
        for F in cands:
            if F is None or F==fin[h] or not(fr[a0]<fr[F]<fr[fin[h]]): continue      # a source with no frame (cleared / never initialised) cannot host the hand-off
            if any(srcfr[i]!=F for i in adds): continue
            out.append(dict(cls='B',h=h,F=F,m1=m1,mv=mv,adds=adds,cur=a0,fin=fin[h],partners=[(P[i][2],P[i][3]) for i in adds]))
    log('B-enum: %d candidates'%len(out)); return out
def buildB(w,c):
    P=w['program']; h=c['h']; F=c['F']; wn=dict(w); out=[]
    for i,e in enumerate(P):
        if i in c['mv']:
            if i==c['m1']: out.append(['MOVE',h,c['cur'],F,False])
            continue
        e=list(e)
        if i in c['adds']: e[-1]=F
        out.append(e)
    wn['program']=out; wn['final']=list(w['final']); wn['final'][h]=F
    return wn
_KD={}
def kdec(T,P):
    """X.kappa_dec(T,P,30) memoised on the invoice (exact; most candidates share the base invoice or each other's)."""
    key=(tuple(sorted(T.items())),tuple(sorted(P.items())))
    if key not in _KD: _KD[key]=X.kappa_dec(T,P,30)
    return _KD[key]
def evaluate(w,cands,k0,builder,log=print,tag=''):
    res=[]; nl=0
    for c in cands:
        wn=(buildB if c['cls']=='B' else buildC if 'adds' in c else build)(w,c)
        try: rep=legal.check(wn,maxviol=3)
        except Exception as ex: c['err']=str(ex); continue
        if not rep['ok']: c['viol']=str(rep['violations'][:1]); continue
        nl+=1
        Tt,Pp=X.invoice(rep); k=kdec(Tt,Pp); c['kappa']=str(k); c['dk']=float(k-k0)
        res.append(c)
    log('%s: %d candidates, %d legal'%(tag,len(cands),nl)); return res
def dedupe(cands):
    d={}
    for c in cands:
        k=c.get('sig') or (c['h'],c['F'],tuple(c['partners']),c['cls'])
        d.setdefault(k,[]).append(c)
    return d
# ---------------------------------------------------------------------------------------------------------------------------
# C: cross-time pooled hand-off.  Cut at s0 (T_h or a later ADD onto h); every later h-event is dropped; the residual D=row_h(s0)-e_h may be cancelled by ANY
# set of "versions" (register r != h, row content at some time, in frame F') alive in F' at some time t >= s0: ADD h += c*r placed right after event max(create,s0).
# (The existing tails of 183 of 404 helpers on #5561 need partner values from different times -- the single-time class S cannot see them.)
import numpy as np
PS=1048573
class FB:
    def __init__(s,N): s.N=N; s.B=np.zeros((0,N),dtype=np.int64); s.piv=np.zeros(0,dtype=np.int64)
    def red(s,v):
        if len(s.piv)==0: return v%PS
        return (v-(v[s.piv]@s.B))%PS
    def add(s,v):
        v=s.red(v); nz=np.flatnonzero(v)
        if len(nz)==0: return
        pc=int(nz[0]); v=v*pow(int(v[pc]),PS-2,PS)%PS
        if len(s.piv): s.B=(s.B-np.outer(s.B[:,pc],v))%PS
        s.B=np.vstack([s.B,v[None,:]]); s.piv=np.append(s.piv,pc)
def versions(w,need):
    """forward pass: list of versions [r,F,create,leave,rowdict], and D(h,s0) dicts for the needed (h,s0) pairs"""
    P=w['program']; sim=Sim(w); V=[]; openv={}
    def opn(r,c): openv[r]=len(V); V.append([r,sim.cur[r],c,None,dict(sim.rows[r])])
    for r in range(sim.N): opn(r,-1)
    D={}
    for s,e in enumerate(P):
        r=sim.step(e)
        if r in openv: V[openv.pop(r)][3]=s
        if sim.cur[r] is not None: opn(r,s)
        for h in need.get(s,()): D[(h,s)]=dict(sim.rows[h]); D[(h,s,'cur')]=sim.cur[h]
    for i in openv.values(): V[i][3]=len(P)
    return V,D
def enumerate_C(w,log=print,allow_fin=False):
    t0=time.time(); P=w['program']; fr=legal.spans(w); NPUB=len(w['initial']); N=NPUB+legal.nown(w)
    live=set(w['live']); main=live|{r+112 for r in live}; hel=[r for r in range(NPUB) if r not in main and r not in legal.retired_of(w)]; hs=set(hel); fin=w['final']; ini=w['initial']
    T={}; L={}
    for i,e in enumerate(P):
        if e[0] in('ADD','COPY'): T[e[2]]=i
        if e[1] in hs: L[e[1]]=i
    cuts=collections.defaultdict(list); need=set()
    for h in hel:
        if h not in L: continue
        cp=[max(T.get(h,-1),0)]+[i for i in range(T.get(h,-1)+1,L[h]) if P[i][1]==h and P[i][0]!='MOVE']
        for s0 in cp:
            if s0<L[h]: cuts[s0].append(h); need.add((h,s0))
    V,D=versions(w,cuts)
    log('C: %d versions, %d cut points (%d helper,cut), %.0fs'%(len(V),len(cuts),len(need),time.time()-t0))
    validF=set(f for f in range(len(fr)) if any(fr[ini[h]]<=fr[f]<fr[fin[h]] or (allow_fin and fr[f]==fr[fin[h]]) for h in hel))
    inv=pow(2,PS-2,PS)
    def vec(row):
        a=np.zeros(N,dtype=np.int64)
        for k,v in row.items(): a[k]=v.numerator%PS*pow(v.denominator,PS-2,PS)%PS
        return a
    order=sorted((i for i,v in enumerate(V) if v[1] in validF),key=lambda i:-V[i][3]); ptr=0
    fb=collections.defaultdict(lambda:FB(N)); hits=[]; ntest=0
    for s0 in sorted(cuts,reverse=True):
        while ptr<len(order) and V[order[ptr]][3]>s0:
            v=V[order[ptr]]; fb[v[1]].add(vec(v[4])); ptr+=1
        for h in cuts[s0]:
            d=dict(D[(h,s0)]); d[h]=d.get(h,Q(0))-1
            d={k:x for k,x in d.items() if x}
            c0=D[(h,s0,'cur')]
            if c0 is None: continue
            dv=-vec(d)%PS
            for F,b in fb.items():
                if len(b.piv)==0 or not ((fr[F]<fr[fin[h]] or (allow_fin and F==fin[h])) and (c0==F or fr[c0]<fr[F])): continue
                ntest+=1
                if not d: hits.append((h,s0,F)); continue
                if not np.any(b.red(dv)): hits.append((h,s0,F))
    log('C: %d tests, %d hits, %.0fs'%(ntest,len(hits),time.time()-t0))
    return V,hits,D
def extract_C(w,V,hit,D):
    """exact dyadic solution over the pool of versions of frame F alive at some t>=s0 (r != h); returns candidate dict or None"""
    P=w['program']; h,s0,F=hit
    d=dict(D[(h,s0)]); d[h]=d.get(h,Q(0))-1
    tgt={k:-x for k,x in d.items() if x}
    if not tgt: return dict(cls=('cur' if D[(h,s0,'cur')]==F else 'ret')+'+pure',h=h,s=s0,F=F,cur=D[(h,s0,'cur')],adds=[],fin=w['final'][h],partners=[],cut=s0)
    keys=set(tgt)
    pool=[i for i,v in enumerate(V) if v[1]==F and v[3]>s0 and v[0]!=h and v[4] and (keys&v[4].keys() or True)]
    pool.sort(key=lambda i:(-len(keys&V[i][4].keys()),V[i][2]))
    pool=pool[:1500]
    def m(row): return {k:modq(x) for k,x in row.items()}
    basis=[]
    for i in pool:
        row=m(V[i][4]); cb={i:1}
        for pk,pr,pc in basis:
            a=row.get(pk)
            if a:
                for kk,vv in pr.items():
                    nv=(row.get(kk,0)-a*vv)%PR
                    if nv: row[kk]=nv
                    else: row.pop(kk,None)
                for kk,vv in pc.items(): cb[kk]=(cb.get(kk,0)-a*vv)%PR
        if row:
            pk=min(row); iv=pow(row[pk],PR-2,PR)
            basis.append((pk,{kk:vv*iv%PR for kk,vv in row.items()},{kk:vv*iv%PR for kk,vv in cb.items() if vv}))
    t={k:modq(x) for k,x in tgt.items()}; sol={}
    for pk,pr,pc in basis:
        a=t.get(pk)
        if a:
            for kk,vv in pr.items():
                nv=(t.get(kk,0)-a*vv)%PR
                if nv: t[kk]=nv
                else: t.pop(kk,None)
            for kk,vv in pc.items(): sol[kk]=(sol.get(kk,0)+a*vv)%PR
    if t: return None
    adds=[]
    for i,c in sol.items():
        if c:
            q=dy(c)
            if q is None: return None
            v=V[i]; adds.append((max(v[2],s0),v[0],q,i))
    acc=dict(D[(h,s0)])
    for _,r,q,i in adds:
        for k,x in V[i][4].items():
            y=acc.get(k,0)+q*x
            if y: acc[k]=y
            else: acc.pop(k,None)
    if acc!={h:Q(1)}: return None
    adds.sort()
    times={a[0] for a in adds}
    cls='cur' if D[(h,s0,'cur')]==F else 'ret'
    if len(adds)>=2: cls+='+multi'
    if len(times)>=2: cls+='+xtime'
    if any(a[1] in OWNED for a in adds): cls+='+scratch'
    return dict(cls=cls,h=h,s=s0,F=F,cur=D[(h,s0,'cur')],fin=w['final'][h],adds=[(t_,r,str(q)) for t_,r,q,_ in adds],partners=[(r,str(q)) for _,r,q,_ in adds],cut=s0,
                sig=(h,F,tuple((r,str(q)) for _,r,q,_ in adds)))
def buildC(w,c):
    P=w['program']; h=c['h']; s0=c['cut']; F=c['F']
    ins=collections.defaultdict(list)
    for t_,r,q in c['adds']: ins[t_].append(['ADD',h,r,q,F])
    first=min(ins) if ins else s0
    out=[]
    for i,e in enumerate(P):
        if i>s0 and e[1]==h: continue
        out.append(e)
        if i==first and c['cur']!=F: out.append(['MOVE',h,c['cur'],F,False])
        out.extend(ins.get(i,[]))
    wn=dict(w); wn['program']=out; wn['final']=list(w['final']); wn['final'][h]=F
    return wn

EPS=1e-15
FASTMIN=1e-13      # --fast: the incremental dk (float root, noise ~2e-16) must exceed this to be verified exactly; sub-1e-13 gains are dropped (far below any useful step)
class FastPos:
    """GEN2POLISH --fast (positive-only) prefilter for big words: IncrWord.try_edit(diff_edit) prices a candidate in ~15 ms (vs ~230 ms for legal.check + kappa_dec on a 20k-event word);
    only candidates with incremental dk > FASTMIN go to the exact path (legal.check + 30-digit kappa).  Never rejects on legality (incr also tests native pairs, legal.check does not)."""
    def __init__(s,w):
        import movekit; from incr import IncrWord,diff_edit
        s.iw=IncrWord(movekit.pin(w)); s.w0=s.iw.to_word(); s.de=diff_edit; s.ok=s.w0['program']==w['program']
    def dk(s,c):
        wn=(buildB if c['cls']=='B' else buildC if 'adds' in c else build)(s.w0,c)
        r=s.iw.try_edit(s.de(s.w0,wn)); return r.dk
def screen(w,log=print,maxalt=3,classes='SBC',fast=False):
    OWNED.clear(); OWNED.update(legal.owned_set(w))
    fp=None; _t0=time.time()
    if fast:
        try: fp=FastPos(w); assert fp.ok
        except Exception as ex: log('fast prefilter unavailable (%s): exact path'%str(ex)[:80]); fp=None
    def ev(c,k0):      # exact evaluation, or (fast) the incremental price only: candidates with incr dk > FASTMIN are returned UNVERIFIED (dk = incremental dk, kappa = 'incr'); apply_fast verifies them exactly
        if fp is not None:
            try:
                d=fp.dk(c)
                if d is None or d<=FASTMIN: return []
                return [dict(c,dk=float(d),kappa='incr',fast=True)]
            except Exception: pass
        return evaluate(w,[c],k0,build,lambda *a:None)
    rep0=legal.check(w); assert rep0['ok'],'base word illegal'
    T0,P0=X.invoice(rep0); k0=X.kappa_dec(T0,P0,30)
    log('base kappa %s'%k0)
    allc=[]
    if 'S' in classes:
        raw=enumerate_S(w,log); groups=dedupe(raw); ngr=0; leg=[]
        for k,g in groups.items():
            ngr+=1
            for c in g[:maxalt]:
                r=ev(c,k0)
                if r: c['nalt']=len(g); leg.append(r[0]); break
        log('S: %d raw, %d distinct (h,F,partners), %d legal%s [%.0fs]'%(len(raw),ngr,len(leg),' (fast: positive only)' if fp is not None else '',time.time()-_t0)); allc+=leg
    if 'C' in classes:
        V,hits,D=enumerate_C(w,log); byhf=collections.defaultdict(list)
        for h,s0,F in hits: byhf[(h,F)].append((h,s0,F))
        ex=[]; nx=0
        for k,hl in byhf.items():
            for hit in hl[:maxalt]:
                c=extract_C(w,V,hit,D)
                if c is None: continue
                nx+=1; r=ev(c,k0)
                if r: ex.append(r[0]); break
        log('C: %d (h,F) pairs hit, %d extracted+legal [%.0fs]'%(len(byhf),len(ex),time.time()-_t0)); allc+=ex
        del V
    if 'B' in classes: allc+=evaluate(w,enumerate_B(w,log),k0,None,log,'B')
    # merge duplicates (same h,F,partners) keep first
    seen=set(); out=[]
    for c in sorted(allc,key=lambda c:-c['dk']):
        key=(c['h'],c['F'],tuple(c['partners']))
        if key in seen: continue
        seen.add(key); out.append(c)
    return k0,out
def tojson(c): return {k:v for k,v in c.items() if k not in('sig',)}
def applyone(w,c):
    return (buildB if c['cls']=='B' else buildC if 'adds' in c else build)(w,c)
def apply_greedy(w,log=print,maxrounds=40,fast=False):
    cur=w; hist=[]
    for rd in range(maxrounds):
        k0,cs=screen(cur,lambda *a:None,fast=fast)
        pos=[c for c in cs if c['dk']>EPS]
        log('apply round %d: kappa %s, %d positive candidates'%(rd,str(k0)[:20],len(pos)))
        if not pos: break
        for c in pos:
            wn=applyone(cur,c); rep=legal.check(wn,maxviol=3)
            if rep['ok']:
                T_,P_=X.invoice(rep); k=X.kappa_dec(T_,P_,30)
                if k>k0+decimal.Decimal(EPS):
                    log('  applied h=%d F=%s %s dk=%+.4e -> %s'%(c['h'],c['F'],c['cls'],float(k-k0),str(k)[:20])); hist.append((c['h'],c['F'],c['cls'],str(k))); cur=wn; break
        else: break
    return cur,hist
def apply_fast(w,log=print,maxrounds=12,first=None):
    """--fast --apply: per round, ONE incremental screen (positive-only, unverified), candidates by descending highest-referenced index, at most one per helper (an application only touches events after its own cut, so earlier cuts keep
    valid indices); each is rebuilt, legal.check'ed and exactly priced and kept only if legal and kappa rises.  Rounds repeat until nothing applies."""
    cur=w; hist=[]; kcur=None
    for rd in range(maxrounds):
        k0,cs=first if (rd==0 and first) else screen(cur,lambda *a:None,fast=True)
        if kcur is None: kcur=k0
        cand=[c for c in cs if c.get('fast') and c['cls']!='B']
        def s0(c): return c['s'] if 's' in c else c['cut']
        def top(c): return max([s0(c)]+[t for t,_,_ in c.get('adds',[])])      # highest program index the candidate refers to
        order=sorted(cand,key=lambda c:(-top(c),-c['dk']))
        log('apply round %d: kappa %s, %d incremental-positive candidates'%(rd,str(kcur)[:20],len(order)))
        napp=0; used=set(); limit=10**9      # applied edits only touch events after their cut: a later candidate stays index-valid if everything it refers to is <= the smallest applied cut
        for c in order:
            if top(c)>limit or c['h'] in used: continue
            wn=applyone(cur,c); rep=legal.check(wn,maxviol=3)
            if not rep['ok']: continue
            T_,P_=X.invoice(rep); k=kdec(T_,P_)
            if k>kcur+decimal.Decimal(EPS):
                log('  applied h=%d F=%s %s dk=%+.4e -> %s'%(c['h'],c['F'],c['cls'],float(k-kcur),str(k)[:20])); hist.append((c['h'],c['F'],c['cls'],str(k))); cur=wn; kcur=k; napp+=1; limit=min(limit,s0(c)); used.add(c['h'])
        log('  round %d applied %d'%(rd,napp))
        if not napp: break
    return cur,hist
def selftest(w,log=print):
    """completeness self-test: with F' == final allowed, the pooled class C must rediscover the existing tail of EVERY helper that has a tail ADD (and S the single-time ones)"""
    P=w['program']; live=set(w['live']); main=live|{r+112 for r in live}; T={}
    for i,e in enumerate(P):
        if e[0] in('ADD','COPY'): T[e[2]]=i
    hel=[r for r in range(len(w['initial'])) if r not in main and r not in legal.retired_of(w)]
    withtail=[h for h in hel if any(P[i][1]==h and P[i][0]=='ADD' for i in range(T.get(h,-1)+1,len(P)))]
    V,hits,D=enumerate_C(w,lambda *a:None,allow_fin=True)
    found={h for h,s0,F in hits if F==w['final'][h]}
    log('SELFTEST C recovers %d/%d existing helper tails at their final frame'%(len(found&set(withtail)),len(withtail)))
    return len(found&set(withtail))==len(withtail)
def main(a):
    path,w=load(a.word)
    OWNED.clear(); OWNED.update(legal.owned_set(w))
    if a.selftest: return 0 if selftest(w,print) else 1
    if not a.inline:
        name=a.name or 'tk_handoff_'+sha(path)[:8]
        out=a.out or '%s/handoff_%s.json'%(OUT,name)
        os.makedirs(OUT,exist_ok=True)
        submit(name,a.tl,[PY,'-B',HERE+'/tk.py','handoff',path,'--inline','--out',out]+(['--apply'] if a.apply else []),a.wait)
        print('log: %s/jobs/%s.log   output: %s'%(W,name,out))
        if a.wait and os.path.exists(W+'/jobs/%s.log'%name): print(open(W+'/jobs/%s.log'%name).read()[-3000:])
        return
    t0=time.time(); lg=lambda m:print(m,flush=True)
    k0,allc=screen(w,lg,classes=a.classes,fast=getattr(a,'fast',False))
    print('\nLEGAL hand-offs (exact kappa), best first (|dk|<1e-15 = 0):')
    for c in allc[:a.top]:
        print('%+.4e  kappa %s  %-20s h=%d  %s->%s (fin %s)  partners %s%s'%(c['dk'] if abs(c['dk'])>EPS else 0.0,c['kappa'][:16],c['cls'],c['h'],c['cur'],c['F'],c['fin'],c['partners'][:4],'' if 'cut' not in c and 'nalt' not in c else '  [cut %d]'%c.get('cut',c.get('s'))))
    byc=collections.Counter(c['cls'] for c in allc); pos=collections.Counter(c['cls'] for c in allc if c['dk']>EPS)
    print('by class (legal):',dict(byc),' positive:',dict(pos))
    for c in allc:
        if c['dk']>EPS and float(c['kappa'])>float(a.threshold): print('CANDIDATE above %s: h=%d F=%s %s kappa %s'%(a.threshold,c['h'],c['F'],c['cls'],c['kappa']))
    if a.out: json.dump(dict(base=str(k0),cands=[tojson(c) for c in allc]),open(a.out,'w'),indent=0,default=str)
    if a.apply:
        wn,hist=apply_fast(w,lg,first=(k0,allc)) if getattr(a,'fast',False) else apply_greedy(w,lg)
        rep=legal.check(wn); T_,P_=X.invoice(rep); k=X.kappa_dec(T_,P_,30)
        o=(a.out or OUT+'/handoff')+'.applied.json.gz'
        json.dump(wn,gzip.open(o,'wt')); print('APPLIED %d hand-offs: kappa %s -> %s legal %s -> %s'%(len(hist),str(k0)[:20],str(k)[:20],rep['ok'],o))
        print('next (joint retime): tk retime %s --free starts,finals,stops --wait'%o)
    print('done %.0fs'%(time.time()-t0))
