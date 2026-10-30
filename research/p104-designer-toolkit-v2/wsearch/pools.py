"""pools -- incremental site pools (SEARCHPERF).  A plugin's pool of edits is enumerated once; after an edit is committed the pool is UPDATED, not rebuilt:
    Delta(v_old, v_new)   the scalar-program difference between two Views: hunks [(olo,ohi,nlo,nhi)] (greedy local resync, one big hunk if the program was reordered),
                          .map(p) = new position of old S position p (None inside a hunk), .regs = registers whose events changed (+ registers whose initial/final changed),
                          .frames_ok = the old frames are an unchanged prefix of the new ones (otherwise every pool is rebuilt)
    plugin.update_sites(v_old, v_new, delta, pool) -> new pool or None (None / missing hook = rebuild)
Stale sites are never a correctness problem: every adoption is re-evaluated exactly (IncrWord / legal.check), a stale site is merely a worse proposal."""
from bisect import bisect_right
K=5; WIN=64
def hunks(A,B):
    na,nb=len(A),len(B); i=j=0; out=[]
    while i<na and j<nb:
        if A[i]==B[j]: i+=1; j+=1; continue
        found=None
        for tot in range(1,2*WIN+1):
            for do in range(max(0,tot-WIN),min(tot,WIN)+1):
                dn=tot-do
                if i+do>na or j+dn>nb: continue
                if A[i+do:i+do+K]==B[j+dn:j+dn+K]: found=(do,dn); break
            if found: break
        if found is None:         # reordered / large change: one hunk up to the common suffix
            s=0
            while s<na-i and s<nb-j and A[na-1-s]==B[nb-1-s]: s+=1
            out.append((i,na-s,j,nb-s)); return out
        do,dn=found; out.append((i,i+do,j,j+dn)); i+=do; j+=dn
    if i<na or j<nb: out.append((i,na,j,nb))
    return out
class Delta:
    def __init__(s,v_old,v_new):
        A,B=v_old.S,v_new.S; s.h=hunks(A,B); s.olo=[h[0] for h in s.h]; s.ohi=[h[1] for h in s.h]
        s.cum=[0]
        for olo,ohi,nlo,nhi in s.h: s.cum.append(s.cum[-1]+(nhi-nlo)-(ohi-olo))
        regs=set()
        for olo,ohi,nlo,nhi in s.h:
            for e in A[olo:ohi]+B[nlo:nhi]:
                regs.add(e[1])
                if e[0] in('ADD','COPY'): regs.add(e[2])
        wo,wn=v_old.w,v_new.w
        for r in range(min(len(wo['initial']),len(wn['initial']))):
            if wo['initial'][r]!=wn['initial'][r] or wo['final'][r]!=wn['final'][r]: regs.add(r)
        s.regs=regs; fo,fn=wo['frames'],wn['frames']
        s.frames_ok=len(fn)>=len(fo) and all(list(fo[k])==list(fn[k]) for k in range(len(fo)))
        s.nhunks=len(s.h)
    def map(s,p):
        n=bisect_right(s.ohi,p)            # hunks entirely before p (an insertion at p shifts p)
        if n<len(s.h) and s.olo[n]<=p<s.ohi[n]: return None
        return p+s.cum[n]
