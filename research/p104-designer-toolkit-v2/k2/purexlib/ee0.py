"""[K2LEVERS copy of ext/MARKETS/ee0.py (solve)] MARKETS END-EARLY census: per helper, last non-F9 event, its frame f, deviation v (form - own symbol) right after; can registers co-present at f
(at that moment) cancel v exactly?  Later uses of h as a SOURCE (block) counted.  R0 saving = tax(chain) - tax(chain cut at f)."""
import os
import sys,gzip,json,collections,math
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + '/synth')
import kernel2net as KN
from fractions import Fraction as Q
def solve(v,vecs):
    """v in span(vecs)? gaussian elimination on dict vectors; returns coeffs or None"""
    piv=[]  # (pivot symbol, row dict, combo dict)
    for idx,u in enumerate(vecs):
        r=dict(u); c={idx:Q(1)}
        for p,pr,pc in piv:
            if p in r:
                f=r[p]
                for k,x in pr.items():
                    r[k]=r.get(k,0)-f*x
                    if r[k]==0: del r[k]
                for k,x in pc.items():
                    c[k]=c.get(k,0)-f*x
                    if c[k]==0: del c[k]
        if r:
            p=next(iter(r)); f=r[p]; r={k:x/f for k,x in r.items()}; c={k:x/f for k,x in c.items()}
            for i,(q,qr,qc) in enumerate(piv):
                if p in qr:
                    g=qr[p]
                    for k,x in r.items():
                        qr[k]=qr.get(k,0)-g*x
                        if qr[k]==0: del qr[k]
                    for k,x in c.items():
                        qc[k]=qc.get(k,0)-g*x
                        if qc[k]==0: del qc[k]
            piv.append((p,r,c))
    r=dict(v); out={}
    for p,pr,pc in piv:
        if p in r:
            f=r[p]
            for k,x in pr.items():
                r[k]=r.get(k,0)-f*x
                if r[k]==0: del r[k]
            for k,x in pc.items(): out[k]=out.get(k,0)+f*x
    return None if r else out
def main(p):
    w=json.load(gzip.open(p)); n=len(w['initial']); role=KN.roles(w); dim=[len(b) for b in w['frames']]; P=w['program']
    last={}; srcafter=collections.Counter()
    for i,e in enumerate(P):
        if e[0] in('ADD','COPY','SCALE'):
            f=e[-1]
            regs=(e[1],e[2]) if e[0]!='SCALE' else (e[1],)
            if dim[f]<9:
                for r in regs: last[r]=i
    for i,e in enumerate(P):
        if e[0] in('ADD','COPY') and dim[e[-1]]==9 and role(e[2])=='H' and last.get(e[2],-1)<i: srcafter[e[2]]+=1
    want=collections.defaultdict(list)
    for h,i in last.items():
        if role(h)=='H': want[i].append(h)
    form=collections.defaultdict(dict,{r:{r:Q(1)} for r in range(n)}); cur=collections.defaultdict(lambda:None,{r:w["initial"][r] for r in range(n)})
    at=collections.defaultdict(set)
    for r in range(n): at[cur[r]].add(r)
    ch=KN.chains(w); res=collections.Counter(); sav=collections.Counter(); ex=[]
    for i,e in enumerate(P):
        o=e[0]
        if o=='MOVE':
            at[cur[e[1]]].discard(e[1]); cur[e[1]]=e[3]; at[e[3]].add(e[1])
        elif o in('ADD','COPY'):
            d,s,q=e[1],e[2],Q(e[3]); fd=dict(form[d]) if o=='ADD' else {}
            for c,v in form[s].items():
                fd[c]=fd.get(c,0)+q*v
                if fd[c]==0: del fd[c]
            form[d]=fd
        elif o=='SCALE': form[e[1]]={c:v*Q(e[2]) for c,v in form[e[1]].items()}
        elif o in('INIT','CLEAR'):
            form[e[1]]={}
            if o=='INIT': at[cur[e[1]]].discard(e[1]); cur[e[1]]=e[2]; at[e[2]].add(e[1])
        for h in want.get(i,[]):
            f=cur[h]; v={k:x for k,x in form[h].items() if not (k==h and x==1)}
            if form[h].get(h,0)!=1: v[h]=form[h].get(h,0)-1
            ds=[dim[x] for x in ch[h]]; s=KN.tax_dims(ds)-KN.tax_dims([d for d in ds if d<=dim[f]])
            if not v: key='clean'
            else:
                others=[r for r in at[f] if r!=h and role(r) in('X','H')]
                c=solve(v,[form[r] for r in others]); key='span' if c is not None else 'nospan'
            key=(key,'srcafter' if srcafter[h] else 'ok',dim[f])
            res[key]+=1; sav[key]+=s
    for k in sorted(res): print(k,res[k],round(sav[k],1))
if __name__=='__main__': main(sys.argv[1])
