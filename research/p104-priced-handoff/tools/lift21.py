"""Priced co-framed hand-off screen (frame-flexible) on a P104 word.
At each scalar-event boundary t and helper h (mid-life), S0 = holders(h) U {h}.
Necessary: h in span(rows of S) for S >= S0 (we try S0 then S0 + registers whose frames allow co-framing greedy).
Frame feasibility: each j in S between its last scalar frame A_j and next scalar frame B_j; F with sum A_j <= F <= cap B_j.
Price: gain = 18*[f(dF-d0)+f(d1-dF)-f(d1-d0)] ; cost = 18*sum_j [P-moment change of j's chain A_j->B_j forced through F]."""
import gzip,json,sys,math
from fractions import Fraction as Q
from collections import defaultdict,Counter
C=float(sys.argv[3]) if len(sys.argv)>3 else 0.0030814
f=lambda x: x**(1-C) if x>0 else 0.0
w=json.load(gzip.open(sys.argv[1]))
NP=w['public']; NR=NP+8
FR=w['frames']; dim=[len(x) for x in FR]
def span_of(b):
    out={0}
    for v in b: out|={x^v for x in out}
    return frozenset(out)
SP=[span_of(b) for b in FR]
def rrefb(basis):
    rows=[]
    for v in basis:
        for r in rows:
            if v^r<v: v^=r
        if v:
            rows=[(r^v if r^v<r else r) for r in rows]; rows.append(v)
    return rows
def elems(b):
    out={0}
    for v in b: out|={x^v for x in out}
    return frozenset(out)
EL=[sum(1<<x for x in SP_) for SP_ in SP]
def contains(mask,basis):
    return all(mask>>v&1 for v in basis)
live=set(w['live']); main=live|{r+112 for r in live}
P=w['program']
# per-register timeline: list of (event index, frame) at scalar events; and chain of frames between them
cur=list(w['initial'])+[None]*8
sev=defaultdict(list)   # r -> list of (i, frame at i)
chains=defaultdict(list) # r -> list of chains: frames visited between consecutive scalar events
chain_now={r:[cur[r]] for r in range(NP)}
for i,e in enumerate(P):
    op,r=e[:2]
    if op=='MOVE':
        cur[r]=e[3]; 
        if r<NP: chain_now[r].append(e[3])
        continue
    regs=(r,) if op in('INIT','CLEAR','SCALE') else (r,e[2])
    for x in regs:
        if x>=NP: continue
        sev[x].append((i,cur[x])); chains[x].append(chain_now[x]); chain_now[x]=[cur[x]]
for r in range(NP): chains[r].append(chain_now[r])  # final chain to final frame
# chains[r][k] = frames from scalar event k-1 (or initial) to scalar event k (or final)
import bisect
sidx={r:[i for i,_ in sev[r]] for r in range(NP)}
def window(j,t):
    """for boundary after event t: chain from last scalar event<=t to next >t"""
    k=bisect.bisect_right(sidx[j],t)
    return chains[j][k]
def pm(ch):  # paid moment of chain
    return sum(f(dim[b]-dim[a]) for a,b in zip(ch,ch[1:]))
def best_cost(ch,Fs):
    """cost of forcing chain ch (A..B) through subspace Fs (frozenset), min over placements; returns (cost) or None"""
    A,B=ch[0],ch[-1]
    if not (SP[A]<=Fs<=SP[B]): return None
    base=pm(ch)
    best=None
    # keep chain stops comparable with Fs: new chain = stops below Fs that are subsets, Fs, stops above that contain Fs
    lo=[x for x in ch if SP[x]<=Fs]; hi=[x for x in ch if Fs<=SP[x]]
    # chain is totally ordered; lo is a prefix, hi a suffix (possibly overlapping at Fs)
    dl=[dim[x] for x in lo]; dh=[dim[x] for x in hi]
    dF=len(Fs).bit_length()-1
    new=dl+[dF]+dh
    nm=sum(f(b-a) for a,b in zip(new,new[1:]) if b>a)
    return base-nm   # positive = moment loss? we return P-moment increase as cost (new-old)
def cost(ch,Fs):
    A,B=ch[0],ch[-1]
    if not (SP[A]<=Fs<=SP[B]): return None
    lo=[dim[x] for x in ch if SP[x]<=Fs]; hi=[dim[x] for x in ch if Fs<=SP[x]]
    dF=len(Fs).bit_length()-1
    new=lo+[dF]+hi
    return sum(f(b-a) for a,b in zip(new,new[1:]) if b>a)-pm(ch)
# replay rows
rows=[{r:Q(1)} for r in range(NR)]
holders=defaultdict(set)
for r in range(NR): holders[r].add(r)
def setrow(r,new):
    for k in rows[r]:
        if k not in new: holders[k].discard(r)
    for k in new: holders[k].add(r)
    rows[r]=new
def inspan(h,S):
    piv={}
    for j in S:
        v=dict(rows[j])
        for p,rv in list(piv.items()):
            c=v.get(p)
            if c:
                for k,x in rv.items():
                    y=v.get(k,0)-c*x
                    if y: v[k]=y
                    else: v.pop(k,None)
        if not v: continue
        p=min(v); c=v[p]; v={k:x/c for k,x in v.items()}
        for q,rv in piv.items():
            cc=rv.get(p)
            if cc:
                for k,x in v.items():
                    y=rv.get(k,0)-cc*x
                    if y: rv[k]=y
                    else: rv.pop(k,None)
        piv[p]=v
    t={h:Q(1)}
    for p,rv in piv.items():
        c=t.get(p)
        if c:
            for k,x in rv.items():
                y=t.get(k,0)-c*x
                if y: t[k]=y
                else: t.pop(k,None)
    return t
PR=(1<<61)-1
def inspanp(h,S):
    piv={}
    for j in S:
        v={k:int(x.numerator*pow(x.denominator,-1,PR))%PR for k,x in rows[j].items()}
        for p,rv in piv.items():
            c=v.get(p)
            if c:
                for k,x in rv.items():
                    y=(v.get(k,0)-c*x)%PR
                    if y: v[k]=y
                    else: v.pop(k,None)
        if not v: continue
        p=min(v); ci=pow(v[p],-1,PR); v={k:x*ci%PR for k,x in v.items()}
        for q,rv in piv.items():
            cc=rv.get(p)
            if cc:
                for k,x in v.items():
                    y=(rv.get(k,0)-cc*x)%PR
                    if y: rv[k]=y
                    else: rv.pop(k,None)
        piv[p]=v
    t={h:1}
    for p,rv in piv.items():
        c=t.get(p)
        if c:
            for k,x in rv.items():
                y=(t.get(k,0)-c*x)%PR
                if y: t[k]=y
                else: t.pop(k,None)
    return t
first={r:sidx[r][0] for r in range(NP) if sidx[r]}; last={r:sidx[r][-1] for r in range(NP) if sidx[r]}
d0=[dim[w['initial'][r]] for r in range(NP)]; d1=[dim[w['final'][r]] for r in range(NP)]
stats=Counter(); best=[]; extpts=[]
def cur_at(j,i,lob,hiM):
    ch=window(j,i)
    return contains(EL[ch[-1]],lob) and (EL[ch[0]]|hiM)==hiM
seen=set()
for i,e in enumerate(P):
    if i%2000==0: print('ev',i,dict(stats),flush=True)
    op,r=e[:2]
    if op=='MOVE': continue
    touched=set(rows[r])
    if op in('INIT','CLEAR'): setrow(r,{})
    elif op=='SCALE': q=Q(e[-2]); setrow(r,{k:q*x for k,x in rows[r].items()})
    else:
        q=Q(e[-2]); s=e[2]
        if op=='COPY': setrow(r,{k:q*x for k,x in rows[s].items()})
        else:
            new=dict(rows[r])
            for k,x in rows[s].items():
                v=new.get(k,0)+q*x
                if v: new[k]=v
                else: new.pop(k,None)
            setrow(r,new)
    touched|=set(rows[r])|{r}
    if op in('ADD','COPY'): touched|=set(rows[e[2]])|{e[2]}
    for h in touched:
        if not(h<NP and h not in main and h in first and first[h]<=i<last[h]): continue
        stats['points']+=1
        S=set(holders[h])|{h}
        if any(j>=NP for j in S): stats['owned_holder']+=1; continue
        chh=window(h,i)
        if not (dim[chh[0]]<d1[h]-0 and dim[chh[-1]]>d0[h] and max(dim[chh[0]],d0[h]+1)<=min(dim[chh[-1]],d1[h]-1)):
            stats['own_window_no_mid']+=1; continue
        wins={j:window(j,i) for j in S}
        hiM=EL[chh[-1]]; loB=list(FR[chh[0]])
        for j,ch in wins.items():
            hiM&=EL[ch[-1]]; loB+=FR[ch[0]]
        lob=rrefb(loB); dlo=len(lob); dhi=hiM.bit_count().bit_length()-1
        if not all((EL[ch[-1]]>>0) and contains(EL[ch[-1]],lob) for ch in wins.values()):
            stats['frame_infeasible']+=1; continue
        if max(dlo,d0[h]+1)>min(dhi,d1[h]-1): stats['no_mid_dim']+=1; continue
        if inspanp(h,S):
            stats['span_fail']+=1
            hiS=frozenset(x for x in range(512) if hiM>>x&1)
            ext=[j for j in range(NP) if j not in S and cur_at(j,i,lob,hiM)]
            if inspanp(h,list(S)+ext): stats['span_fail_ext']+=1; continue
            stats['span_ok_ext']+=1
            g=lambda a,b: f(a)+f(b)-f(a+b) if a>0 and b>0 else 0.0
            W={j:window(j,i) for j in list(S)+ext}
            Fc={x for ch in W.values() for x in ch if contains(EL[x],lob) and (EL[x]|hiM)==hiM and d0[h]<dim[x]<d1[h]}
            for F in Fc:
                k=dim[F]
                gain=g(k-d0[h],d1[h]-k)
                def cj(j):
                    ch=W[j]
                    if F in ch: return 0.0
                    if not(contains(EL[F],FR[ch[0]]) and contains(EL[ch[-1]],FR[F])): return None
                    return g(k-dim[ch[0]],dim[ch[-1]]-k)
                base=[cj(j) for j in S]
                if None in base: continue
                base=sum(base)
                if base>=gain: continue
                cs=sorted((c,j) for j in ext for c in [cj(j)] if c is not None)
                T=[]
                ok=not inspanp(h,list(S))
                for c,j in cs:
                    if ok or base+sum(cj(x) for x in T)+c>=gain: break
                    T.append(j); ok=not inspanp(h,list(S)+T)
                if not ok: continue
                for j in sorted(T,key=lambda x:-cj(x)):
                    T2=[x for x in T if x!=j]
                    if not inspanp(h,list(S)+T2): T=T2
                cost=base+sum(cj(x) for x in T)
                extpts.append((gain-cost,gain,cost,h,i,k,F,len(S),T))
            continue
        stats['span_ok']+=1
        g=lambda a,b: f(a)+f(b)-f(a+b) if a>0 and b>0 else 0.0
        for k in range(max(dlo,d0[h]+1),min(dhi,d1[h]-1)+1):
            gain=g(k-d0[h],d1[h]-k)
            opts=[]
            for Fk in (('lo',) if k==dlo else ())+(('hi',) if k==dhi else ())+('gen',):
                c=0.0
                for j,ch in wins.items():
                    dA,dB=dim[ch[0]],dim[ch[-1]]
                    if Fk=='lo' and dA==dlo and EL[ch[0]].bit_count()==1<<dlo and contains(EL[ch[0]],lob): continue
                    if Fk=='hi' and EL[ch[-1]]==hiM: continue
                    c+=g(k-dA,dB-k)
                opts.append((c,Fk))
            c,Fk=min(opts)
            best.append((gain-c,gain,c,h,i,k,Fk,len(S)))
best.sort(reverse=True)
extpts.sort(reverse=True);print('extpts',len(extpts),'net>0',sum(x[0]>0 for x in extpts));[print(x) for x in extpts[:15]]
print(dict(stats))
print('candidates',len(best),'net>0',sum(1 for b in best if b[0]>1e-15))
for b in best[:25]: print(b)
json.dump(best[:5000],open(sys.argv[2],'w'))
