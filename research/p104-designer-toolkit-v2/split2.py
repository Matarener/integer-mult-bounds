"""tk split2 -- two-boundary helper split screen (PR5718, flyingviper).  Generalises `tk split` (same input/output basis) to DISTINCT input and output bases.
Move class: helper p (initial chart Z = empty frame, final chart G, intermediate chart F visited at a cut c) retires at F and a NEW independent public helper `fresh` (initial F, final G)
takes over every later occurrence of p.  One target H(dG-dZ) becomes H(dF-dZ)+H(dG-dF) (strictly more productive fields, no paid MOVE added).  Exact linear algebra (PROOF.md of #5718):
  A = scalar prefix map (rows over initial inputs) at the cut,  a = row_p(A),  c = q*row_s(A) for a partner s sitting on F at the cut (q=0: none),  h = a + c,  k = h - e_p,
  d = B e_p (column of the suffix map: how a unit in p at the cut reaches the endpoints).
  Preconditions: h_p = 1, supp(h) on registers whose initial chart is Z (so `p -= k_r r` is a legal ADD at Z), d_p = 1, supp(d)\\p on registers with initial Z and final G.
  Word: [p -= k_r*r @Z for r in supp k] [r += d_r*p @Z for r in supp d \\ p] | prefix up to the cut | p += q*s @F | suffix with p renamed to fresh (owned ids shift +1) |
        [r -= d_r*fresh @G for r in supp d \\ p] | cleanup  fresh += corr_r*r @G  (corr solves the remaining endpoint error of fresh over the final-G registers).  p ends on F, fresh F -> G.
The terminal (long-cleanup) variant of PR5718 has the same invoice as its 3-operation shortcut; only the event count differs (+~118 events), so repeated splits are bounded by the 26000 event cap.
sites(): helpers p with initial Z, visits of an intermediate chart F, cuts after p's last event on F and just before its next event; partners s on F with rows cancelling a's non-Z part.
Back-test: PR5713 word -> PR5718 (p=708, F=602, partner 154 q=1/2) .00311024572012.   Uses numpy float64 rows (dyadic => exact) and the shared legal.check as authority."""
import collections
from fractions import Fraction as Q
import numpy as np
import movekit as M
from movekit import qs

_QC={}
def fq(s):
    x=_QC.get(s)
    if x is None: x=_QC[s]=(Q(s),float(Q(s)))
    return x
def run_rows(S,NR,own,stop=None,rows=None):
    """float64 matrix: row r = register r as a linear function of the initial inputs after S[:stop+1]"""
    if rows is None:
        rows=np.eye(NR)
        for r in own: rows[r]=0
    for i,e in enumerate(S):
        if stop is not None and i>stop: break
        op,r=e[0],e[1]
        if op=='ADD': rows[r]+=fq(e[3])[1]*rows[e[2]]
        elif op=='SCALE': rows[r]*=fq(e[2])[1]
        elif op=='COPY': rows[r]=fq(e[3])[1]*rows[e[2]]
        else: rows[r]=0
    return rows
def push(S,start,NR,u0):
    """propagate a state vector (column) forward through S[start:]: the map B applied to u0"""
    u=list(u0)
    for e in S[start:]:
        op,r=e[0],e[1]
        if op=='ADD': u[r]+=fq(e[3])[1]*u[e[2]]
        elif op=='SCALE': u[r]*=fq(e[2])[1]
        elif op=='COPY': u[r]=fq(e[3])[1]*u[e[2]]
        else: u[r]=0.0
    return u
def zero_frame(w):
    z=[i for i,f in enumerate(w['frames']) if len(f)==0]; return z[0] if z else None
def dyadic(x):
    q=Q(x)
    return q.denominator&(q.denominator-1)==0 and abs(q)+1<2**16

class Split2(M.Plugin):
    name='split2'; doc=__doc__; quick=False; site_fields=('p','F','s'); maxsupp=12
    def prepare(self,v):
        w=v.w; main=set(w['live'])|{r+112 for r in w['live']}; Z=zero_frame(w); dim=v.dim
        helpers=[r for r in range(v.n) if r not in main and w['initial'][r]==Z]
        ev=collections.defaultdict(list)
        for i,e in enumerate(v.S):
            if e[0] in('INIT','CLEAR'): ev[e[1]].append(i); continue
            ev[e[1]].append(i)
            if e[0] in('ADD','COPY'): ev[e[2]].append(i)
        for r in ev: ev[r]=sorted(set(ev[r]))
        return dict(main=main,Z=Z,helpers=helpers,ev=ev)
    def frame_at(self,v,ev,r,i):
        """chart of r after S[:i+1] (its last event's chart, else its initial chart)"""
        from bisect import bisect_right
        L=ev.get(r,[]); k=bisect_right(L,i)
        if k==0: return v.w['initial'][r]
        e=v.S[L[k-1]]; return e[2] if e[0] in('INIT','CLEAR') else e[-1]
    def cuts(self,v,ctx):
        """-> sorted list of (c, p, F): cut after S index c, p resting on intermediate chart F"""
        w=v.w; dim=v.dim; Z=ctx['Z']; out=[]
        for p in ctx['helpers']:
            G=w['final'][p]
            if dim[G]-dim[Z]<2: continue
            L=ctx['ev'].get(p,[]); fr=[]
            for i in L:
                e=v.S[i]; fr.append(e[-1] if e[0] not in('INIT','CLEAR') else e[2])
            # runs of equal chart
            j=0
            while j<len(L):
                k=j
                while k+1<len(fr) and fr[k+1]==fr[j]: k+=1
                F=fr[j]
                if F not in(Z,G) and dim[Z]<dim[F]<dim[G] and v.spans[Z]<v.spans[F]<v.spans[G]:
                    cs={L[k]}
                    if k+1<len(L): cs.add(L[k+1]-1)
                    else: cs.add(len(v.S)-1)
                    for c in sorted(cs): out.append((c,p,F))
                j=k+1
        return sorted(out)
    def sites(self,v,ctx):
        w=v.w; n=v.n; NR=v.NR; Z=ctx['Z']; S=v.S; dim=v.dim; own=v.own
        E0=np.array([r<n and w['initial'][r]==Z for r in range(NR)])
        cuts=self.cuts(v,ctx); byc=collections.defaultdict(list)
        for c,p,F in cuts: byc[c].append((p,F))
        rows=np.eye(NR)
        for r in own: rows[r]=0
        curf=np.array(list(w['initial'])+[-1]*(NR-len(w['initial'])))
        cand=[]
        for i,e in enumerate(S):
            op,r=e[0],e[1]
            if op=='ADD': rows[r]+=fq(e[3])[1]*rows[e[2]]; curf[r]=e[-1]; curf[e[2]]=e[-1]
            elif op=='SCALE': rows[r]*=fq(e[2])[1]; curf[r]=e[-1]
            elif op=='COPY': rows[r]=fq(e[3])[1]*rows[e[2]]; curf[r]=e[-1]; curf[e[2]]=e[-1]
            elif op=='INIT': rows[r]=0; curf[r]=e[2]
            else: rows[r]=0; curf[r]=-1
            for p,F in byc.get(i,()):
                a=rows[p].copy(); a[NR-len(own):]=0       # owned coordinates carry no input
                Gp=w['final'][p]
                partners=[(None,0.0)]
                nz=~E0
                nz[n:]=False
                if np.any(a[nz]!=0) or True:
                    aout=a.copy(); aout[E0]=0; aout[n:]=0
                    if np.any(aout!=0):
                        partners=[]
                        j=int(np.nonzero(aout)[0][0])
                        for s in np.nonzero(curf==F)[0]:
                            s=int(s)
                            if s==p or s>=n: continue
                            rs=rows[s].copy(); rs[E0]=0; rs[n:]=0
                            if rs[j]==0: continue
                            q=-aout[j]/rs[j]
                            if q!=0 and np.array_equal(aout+q*rs,np.zeros(NR)) and dyadic(Q(q)): partners.append((s,q))
                    # else no partner needed
                for s,q in partners:
                    h=a+(q*rows[s] if s is not None else 0); h[n:]=0
                    if h[p]!=1: continue
                    # support of h must lie on Z-initial registers
                    if np.any(h[~E0]!=0): continue
                    u0=[0.0]*NR; u0[p]=1.0; d=push(S,i+1,NR,u0)
                    if d[p]!=1: continue
                    sup=[r for r in range(NR) if d[r]!=0 and r!=p]
                    if len(sup)>self.maxsupp or any((r>=n or not E0[r] or w['final'][r]!=Gp) for r in sup): continue
                    if float(np.dot(h,np.array(d)))!=1.0: continue
                    gain=_H(dim[F]-dim[Z])+_H(dim[Gp]-dim[F])-_H(dim[Gp])
                    cand.append((gain,dict(p=p,c=i,F=F,s=s,q=None if s is None else qs(Q(q)))))
        cand.sort(key=lambda t:-t[0])
        for g,ed in cand: yield ed
    def apply(self,v,ed):
        w=v.w; n=v.n; NR=v.NR; Z=zero_frame(w); S=v.S; own=v.own
        p,c,F,s=ed['p'],ed['c'],ed['F'],ed['s']; q=Q(ed['q']) if ed['q'] is not None else Q(0); Gp=w['final'][p]; fresh=n
        rows=run_rows(S,NR,own,stop=c); h=rows[p].copy(); h[n:]=0
        if s is not None: h=h+float(q)*rows[s]; h[n:]=0
        assert h[p]==1,'h_p'
        k=h.copy(); k[p]=0
        u0=[0.0]*NR; u0[p]=1.0; d=push(S,c+1,NR,u0); assert d[p]==1,'d_p'
        sup=[r for r in range(NR) if d[r]!=0 and r!=p]
        ren=lambda r,i: (fresh if (r==p and i>c) else (r+1 if r>=n else r))
        def rn(e,i):
            e=list(e); e[1]=ren(e[1],i)
            if e[0] in('ADD','COPY'): e[2]=ren(e[2],i)
            return e
        pre=[['ADD',p,int(r),qs(-Q(float(k[r]))),Z] for r in range(n) if k[r]!=0]
        pre+=[['ADD',int(r),p,qs(Q(float(d[r]))),Z] for r in sup]
        body=[]
        for i,e in enumerate(S):
            body.append(rn(e,i))
            if i==c and s is not None: body.append(['ADD',p,s,qs(q),F])
        end=[['ADD',int(r),fresh,qs(-Q(float(d[r]))),Gp] for r in sup]
        S2=pre+body+end
        NR2=NR+1
        own2={r+1 for r in own}
        rows2=run_rows(S2,NR2,own2)
        exp=np.zeros((NR2,NR2))
        for r in range(n+1): exp[r,r]=1
        for r in w['live']: exp[r+112,r]+=1
        wrong=[r for r in range(NR2) if not np.array_equal(rows2[r],exp[r])]
        assert wrong in ([fresh],[]),'endpoint rows %s'%wrong[:6]
        g=rows2[fresh]-exp[fresh]      # fresh row minus e_fresh, over input coordinates
        corr=np.zeros(NR2)
        cc=-g.copy()
        # Y registers r=x+112 carry e_x + e_r: process Y first
        for x in w['live']:
            y=x+112; corr[y]=cc[y]; cc[x]-=corr[y]; cc[y]=0
        for r in range(n+1):
            if cc[r]!=0: corr[r]+=cc[r]
        corr[fresh]=0
        cs=[r for r in range(n+1) if corr[r]!=0]
        final2=list(w['final'])+[Gp]; final2[p]=F
        assert all(final2[r]==Gp for r in cs),'cleanup register off the final chart'
        S2+= [['ADD',fresh,int(r),qs(Q(float(corr[r]))),Gp] for r in cs]
        initial2=list(w['initial'])+[F]
        res=v.rebuild_shifted(S2,initial2,final2)
        return res
def _H(r,kappa=0.0031): return r**(1-kappa) if r>0 else 0.0
PLUGIN=Split2()
def main(a): return M.cli(PLUGIN,a)

def _rebuild_shifted(v,S2,initial,final):
    """rebuild for a word with one more public register: View with n+1 public, owned ids shifted by one"""
    w=dict(v.w); w['initial']=initial; w['final']=final; w['public']=len(initial); w['owned_fields']=legal.nown(v.w)
    w['verifier_profile']=dict(legal.profile_params(v.w),public=len(initial),owned_fields=legal.nown(v.w))
    v2=M.View(w); return v2.rebuild(S2)
M.View.rebuild_shifted=_rebuild_shifted
from tkcommon import legal
