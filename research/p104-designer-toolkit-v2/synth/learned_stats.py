"""GENLEARN: structural statistics of a P104-family word (helpers, itineraries, meetings, junk, roots).
usage: python3 toolkit/synth/learned_stats.py ALIAS [--json out]"""
import sys,os,gzip,json,collections
H=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def loadw(a):
    p=a if os.path.exists(a) else H+'/words/%s.json.gz'%a
    return json.load(gzip.open(p))
def analyse(w):
    fr=w['frames']; dim=lambda f: len(fr[f]); n=len(w['initial']); live=set(w['live']); pr=w['program']
    def role(r):
        if r in live: return 'X'
        if r-112 in live and r<n: return 'Y'
        return 'H' if r<n else 'O'
    R=[role(r) for r in range(n)]
    cur=list(w['initial'])+[None]*64
    it=collections.defaultdict(list)       # reg -> [dims visited]
    for r in range(n): it[r]=[dim(cur[r])]
    ev=collections.defaultdict(list)       # helper -> (idx, kind, partner role, partner reg, dim of frame)
    adds=[]                                # (idx, dst, src, dim, roles)
    owned_live={}; jobs=collections.defaultdict(collections.Counter)
    for i,e in enumerate(pr):
        o=e[0]
        if o=='MOVE':
            r=e[1]; cur[r]=e[3]
            if r<n: it[r].append(dim(e[3]))
            else: it.setdefault(r,[]).append(dim(e[3]))
        elif o in('ADD','COPY'):
            d,s=e[1],e[2]; f=e[4]; dd=dim(f)
            rd=R[d] if d<n else 'O'; rs=R[s] if s<n else 'O'
            adds.append((i,d,s,dd,rd,rs,e[3]))
        elif o=='INIT': cur[e[1]]=e[2]; it[e[1]]=[dim(e[2])]
    return dict(R=R,it=it,adds=adds,n=n,fr=fr,w=w)
def stats(a):
    w=loadw(a); A=analyse(w); R=A['R']; it=A['it']; adds=A['adds']; n=A['n']
    out={}
    hel=[r for r in range(n) if R[r]=='H']
    out['n_helpers']=len(hel); out['n_X']=R.count('X'); out['n_Y']=R.count('Y')
    # helper activity
    hadds=collections.defaultdict(list)
    for (i,d,s,dd,rd,rs,q) in adds:
        if rd=='H': hadds[d].append((i,'dst',s,rs,dd))
        if rs=='H': hadds[s].append((i,'src',d,rd,dd))
    used=[h for h in hel if hadds[h]]
    out['helpers_used']=len(used)
    out['start_dim']=dict(collections.Counter(it[h][0] for h in hel))
    out['final_dim']=dict(collections.Counter(it[h][-1] for h in hel))
    out['n_moves_hist']=dict(sorted(collections.Counter(len(it[h])-1 for h in hel).items()))
    out['itin_top']=[(('>'.join(map(str,k))),c) for k,c in collections.Counter(tuple(it[h]) for h in hel).most_common(25)]
    # jobs served per helper: distinct non-helper partners (roots O, X, Y) ; X/Y/O counts
    jx=collections.Counter(); jy=collections.Counter(); jo=collections.Counter(); jh=collections.Counter(); tot=collections.Counter()
    for h in hel:
        px=set();py=set();po=set();ph=set()
        for (i,k,p,rp,dd) in hadds[h]:
            {'X':px,'Y':py,'O':po,'H':ph}[rp].add(p)
        jx[len(px)]+=1; jy[len(py)]+=1; jo[len(po)]+=1; jh[len(ph)]+=1; tot[len(px)+len(py)+len(po)]+=1
    out['partners_X']=dict(sorted(jx.items())); out['partners_Y']=dict(sorted(jy.items())); out['partners_O']=dict(sorted(jo.items())); out['partners_H']=dict(sorted(jh.items()))
    out['partners_nonhelper_total']=dict(sorted(tot.items()))
    # ADD topology by (dim, dst role, src role)
    t=collections.Counter(); 
    for (i,d,s,dd,rd,rs,q) in adds: t[(dd,rd+'<-'+rs)]+=1
    out['add_dim_roles']={'%d %s'%k:v for k,v in sorted(t.items())}
    out['add_by_roles']=dict(collections.Counter(rd+'<-'+rs for (i,d,s,dd,rd,rs,q) in adds))
    out['add_by_dim']=dict(sorted(collections.Counter(dd for (i,d,s,dd,rd,rs,q) in adds).items()))
    # root-landing frames: ADD with dst role O
    rl=collections.Counter(); rsrc=collections.Counter()
    for (i,d,s,dd,rd,rs,q) in adds:
        if rd=='O': rl[(dd,rs)]+=1
        if rs=='O': rsrc[(dd,rd)]+=1
    out['root_dst_dim_srcrole']={'%d %s'%k:v for k,v in sorted(rl.items())}
    out['root_src_dim_dstrole']={'%d %s'%k:v for k,v in sorted(rsrc.items())}
    # which helpers carry roots: helpers that are dst of ADD from O
    carry=set(d for (i,d,s,dd,rd,rs,q) in adds if rd=='H' and rs=='O')
    out['helpers_reading_root']=len(carry)
    rootsof=collections.defaultdict(set)
    for (i,d,s,dd,rd,rs,q) in adds:
        if rd=='H' and rs=='O': rootsof[d].add(s)
    out['roots_per_carrier']=dict(sorted(collections.Counter(len(v) for v in rootsof.values()).items()))
    out['carrier_start_dim']=dict(collections.Counter(it[h][0] for h in carry))
    # meetings: consecutive ADD runs sharing frame f in a time-window; group by (frame) ... use maximal runs of ADDs with the same frame between non-ADD events
    meets=[]; run=None
    for i,e in enumerate(w_prog(a)):
        pass
    return out,A
_cache={}
def w_prog(a):
    return loadw(a)['program']
def meetings(a):
    w=loadw(a); fr=w['frames']; dim=lambda f: len(fr[f]); pr=w['program']
    runs=[]; cur=None
    for i,e in enumerate(pr):
        if e[0] in('ADD','COPY'):
            f=e[4]
            if cur and cur[0]==f and i==cur[3]+1 : 
                cur[1].update([e[1],e[2]]); cur[3]=i; cur[4]+=1
            else:
                if cur: runs.append(cur)
                cur=[f,set([e[1],e[2]]),i,i,1]
        else:
            if cur and e[0]!='MOVE' : runs.append(cur); cur=None
            elif cur and e[0]=='MOVE': runs.append(cur); cur=None
    if cur: runs.append(cur)
    return runs,dim
if __name__=='__main__':
    for a in sys.argv[1:]:
        o,A=stats(a); print('==',a)
        for k,v in o.items(): print(k,v)

def meet_stats(a):
    """meetings = maximal windows of ADD/COPY/SCALE events at ONE frame, not interrupted by a MOVE or an event at another frame.
    Returns list of dict(dim,frame,lo,hi,regs,nadd,roles)."""
    w=loadw(a); fr=w['frames']; n=len(w['initial']); live=set(w['live']); pr=w['program']
    def role(r):
        if r>=n: return 'O'
        if r in live: return 'X'
        if r-112 in live: return 'Y'
        return 'H'
    M=[]; cur=None
    for i,e in enumerate(pr):
        if e[0] in('ADD','COPY'):
            f=e[4]
            if cur is None or cur['f']!=f:
                if cur: M.append(cur)
                cur=dict(f=f,lo=i,hi=i,regs=set(),nadd=0)
            cur['regs'].update([e[1],e[2]]); cur['nadd']+=1; cur['hi']=i
        elif e[0]=='SCALE':
            if cur: cur['regs'].add(e[1])
        else:
            if cur: M.append(cur); cur=None
    if cur: M.append(cur)
    for m in M:
        m['dim']=len(fr[m['f']]); m['roles']=''.join(sorted(role(r) for r in m['regs']))
        m['nroles']={k:m['roles'].count(k) for k in 'HXYO'}
    return M

def more_stats(a):
    """GENLEARN part 2: helper classes, junk patterns, main itineraries, butterflies, phases."""
    w=loadw(a); fr=w['frames']; dim=lambda f: len(fr[f]); n=len(w['initial']); live=set(w['live']); pr=w['program']
    def role(r):
        if r>=n: return 'O'
        if r in live: return 'X'
        if r-112 in live: return 'Y'
        return 'H'
    R=[role(r) for r in range(n)]
    out={}
    it=collections.defaultdict(list); cur=list(w['initial'])
    for r in range(n): it[r]=[dim(cur[r])]
    sig=collections.defaultdict(collections.Counter)    # helper -> Counter((dim, partner role, dir))
    ph=collections.defaultdict(list)
    for i,e in enumerate(pr):
        if e[0]=='MOVE':
            if e[1]<n: it[e[1]].append(dim(e[3]))
        elif e[0] in('ADD','COPY'):
            d,s=e[1],e[2]; dd=dim(e[4])
            if d<n and R[d]=='H': sig[d][(dd,R[s] if s<n else 'O','in')]+=1
            if s<n and R[s]=='H': sig[s][(dd,R[d] if d<n else 'O','out')]+=1
    hel=[r for r in range(n) if R[r]=='H']
    # helper classes
    def cls(h):
        s=sig[h]; mid=[k for k in s if 0<k[0]<9]
        d0=[k for k in s if k[0]==0]; d9=[k for k in s if k[0]==9]
        if not s: return 'idle'
        if not mid: return 'junk-only(d0%s,d9%s)'%('Y' if any(k[1]=='Y' for k in d0) else '-', 'y' if d9 else '-')
        hasX=any(k[1]=='X' for k in mid); hasO=any(k[1]=='O' for k in mid); hasY=any(k[1]=='Y' for k in mid)
        return 'mid(%s%s%s)'%('X' if hasX else '','O' if hasO else '','Y' if hasY else '')+('+d0Y' if any(k[1]=='Y' for k in d0) else '')
    C=collections.Counter(cls(h) for h in hel); out['helper_classes']=dict(C.most_common())
    out['class_start']={c:dict(collections.Counter(it[h][0] for h in hel if cls(h)==c)) for c in C}
    out['class_nmoves_mean']={c:round(sum(len(it[h])-1 for h in hel if cls(h)==c)/C[c],2) for c in C}
    out['class_final']={c:dict(collections.Counter(it[h][-1] for h in hel if cls(h)==c)) for c in C}
    # rank sequences
    rs=collections.Counter(); ranks=collections.Counter()
    for h in hel:
        s=it[h]; rk=tuple(s[k+1]-s[k] for k in range(len(s)-1)); rs[rk]+=1
        for x in rk: ranks[x]+=1
    out['helper_rank_seq_top']=[(''.join(map(str,k)) if max(k,default=0)<10 else str(k),c) for k,c in rs.most_common(20)]
    out['helper_hop_ranks']=dict(sorted(ranks.items()))
    out['helper_rank_tax_lnsum']=round(sum((s[-1]-s[0])*math.log(max(s[-1]-s[0],1))-sum((s[k+1]-s[k])*math.log(s[k+1]-s[k]) for k in range(len(s)-1) if s[k+1]>s[k]) for s in (it[h] for h in hel)),1)
    # junk: dim-0 Y<-H
    y_h=collections.defaultdict(set); h_y=collections.defaultdict(set); yh_cnt=0
    for e in pr:
        if e[0]=='ADD' and dim(e[4])==0 and e[1]<n and R[e[1]]=='Y' and e[2]<n and R[e[2]]=='H': y_h[e[1]].add(e[2]); h_y[e[2]].add(e[1]); yh_cnt+=1
    out['junk_d0_YH_events']=yh_cnt
    out['junk_helpers_per_Y']=_summ([len(v) for v in y_h.values()]); out['junk_Y_per_helper']=_summ([len(v) for v in h_y.values()]); out['junk_helpers_touched']=len(h_y)
    out['junk_Y_per_helper_hist']=dict(sorted(collections.Counter(len(v) for v in h_y.values()).items()))
    # junk fraction: helpers touched by dim0 Y loads that also have mid activity
    out['junk_helpers_with_mid']=sum(1 for h in h_y if any(0<k[0]<9 for k in sig[h]))
    # unload pattern at dim 9
    un=collections.Counter(); 
    for h in hel:
        s=sig[h]; un[(sum(v for k,v in s.items() if k[0]==9 and k[2]=='in'),)]+=1
    out['d9_in_events_per_helper']=_summ([sum(v for k,v in sig[h].items() if k[0]==9 and k[2]=='in') for h in hel])
    out['d9_helpers_active']=sum(1 for h in hel if any(k[0]==9 for k in sig[h]))
    # X and Y itineraries
    def itin(role_):
        c=collections.Counter(); ns=collections.Counter()
        for r in range(n):
            if R[r]==role_: c[tuple(it[r])]+=1; ns[len(it[r])-1]+=1
        return c,ns
    cx,nx=itin('X'); cy,ny=itin('Y')
    out['X_nmoves']=dict(sorted(nx.items())); out['Y_nmoves']=dict(sorted(ny.items()))
    out['X_start_final']=dict(collections.Counter((t[0],t[-1]) for t in cx.elements())); out['Y_start_final']=dict(collections.Counter((t[0],t[-1]) for t in cy.elements()))
    out['X_dims_visited']=dict(sorted(collections.Counter(d for t in cx.elements() for d in t[1:-1]).items()))
    out['Y_dims_visited']=dict(sorted(collections.Counter(d for t in cy.elements() for d in t[1:-1]).items()))
    # butterflies: ADD a<-b q1 immediately followed (<=3 events later) by ADD b<-a q in {-1/2,-1,1/2} same frame
    bf=collections.Counter()
    for i,e in enumerate(pr):
        if e[0]=='ADD' and e[1]<n:
            for j in range(i+1,min(i+3,len(pr))):
                f=pr[j]
                if f[0]=='ADD' and f[1]==e[2] and f[2]==e[1] and f[4]==e[4]:
                    bf[(dim(e[4]),e[3],f[3])]+=1; break
    out['butterfly_by_dim_qq']={ '%d %s %s'%k:v for k,v in sorted(bf.items(),key=lambda kv:-kv[1])[:16]}
    out['butterfly_total']=sum(bf.values())
    out['butterfly_by_dim']=dict(sorted(collections.Counter({k[0] for k in bf} and [k[0] for k in bf.elements()]).items()))
    # phases
    firstmv=next(i for i,e in enumerate(pr) if e[0]=='MOVE'); lastmv=max(i for i,e in enumerate(pr) if e[0]=='MOVE')
    out['phase_bounds']=dict(first_move=firstmv,last_move=lastmv,n=len(pr))
    return out
import math
def _summ(v):
    if not v: return {}
    v=sorted(v); return dict(n=len(v),min=v[0],med=v[len(v)//2],mean=round(sum(v)/len(v),1),max=v[-1])

def phases(a):
    """phase boundaries: J (junk loads, before first MOVE), F (front end, to first INIT), R (INIT..last CLEAR), B (back end to the start of the dim-9 restore), Z (restore)."""
    w=loadw(a); fr=w['frames']; pr=w['program']
    firstmv=next(i for i,e in enumerate(pr) if e[0]=='MOVE')
    ini=[i for i,e in enumerate(pr) if e[0]=='INIT' and len(fr[e[2]])==8]; rr={pr[i][1] for i in ini}      # the 8 root lifetimes (INIT at dim 8)
    clr=[i for i,e in enumerate(pr) if e[0]=='CLEAR' and e[1] in rr and i>ini[0]]
    lastmid=max(i for i,e in enumerate(pr) if e[0] in('ADD','COPY') and 0<len(fr[e[4]])<9)
    # restore start: after the last MOVE of any helper? use the last event whose frame dim in 1..8 minus nothing -> Z starts at the first dim-9 ADD after which <5% of ADDs are mid
    d9=[i for i,e in enumerate(pr) if e[0] in('ADD','COPY') and len(fr[e[4]])==9]
    zs=d9[0]
    # robust: last window of 500 ADDs with >=10% mid
    add_idx=[i for i,e in enumerate(pr) if e[0] in('ADD','COPY')]
    import bisect
    zs=None
    for k in range(len(add_idx)-500,-1,-100):
        seg=add_idx[k:k+500]; mid=sum(1 for i in seg if 0<len(fr[pr[i][4]])<9)
        if mid>=50: zs=add_idx[k+500]; break
    return dict(J=(0,firstmv),F=(firstmv,ini[0]),R=(ini[0],clr[-1]+1),B=(clr[-1]+1,zs),Z=(zs,len(pr)))
def phase_stats(a):
    w=loadw(a); fr=w['frames']; pr=w['program']; n=len(w['initial']); live=set(w['live']); P=phases(a)
    role=lambda r:'O' if r>=n else ('X' if r in live else ('Y' if r-112 in live else 'H'))
    M=meet_stats(a); res={}
    for name,(lo,hi) in P.items():
        c=collections.Counter(); mv=collections.Counter(); ad=collections.Counter(); cur=None
        for i in range(lo,hi):
            e=pr[i]
            if e[0]=='MOVE':
                ro=role(e[1]); mv[(ro,len(fr[e[3]])-len(fr[e[2]]))]+=1
            elif e[0] in('ADD','COPY'):
                ad[(len(fr[e[4]]),role(e[1])+'<-'+role(e[2]))]+=1
        ms=[m for m in M if lo<=m['lo']<hi]
        mm=collections.Counter()
        for m in ms: mm[(m['dim'],len(m['regs']))]+=1
        res[name]=dict(range=(lo,hi),n_events=hi-lo,moves_total=sum(mv.values()),moves_by_role_rank={'%s%d'%k:v for k,v in sorted(mv.items())},
            adds_total=sum(ad.values()),adds_by_dim=dict(sorted(collections.Counter({d:sum(v for (dd,_),v in ad.items() if dd==d) for d in range(10)}).items())),
            adds_by_roles=dict(collections.Counter({r:sum(v for (_,rr),v in ad.items() if rr==r) for r in {rr for (_,rr) in ad}}).most_common()),
            meetings=len(ms),meet_size_by_dim={d:dict(sorted(collections.Counter(len(m['regs']) for m in ms if m['dim']==d).items())) for d in range(10) if any(m['dim']==d for m in ms)})
    return res
