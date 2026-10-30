"""tk a2x -- A2 paid rank exchange screen (PR5643 zxv; composed in PR5650).  Move class: a scalar chain  ADD(t,s,c1) @i ... first reader ADD(u,t,c2) @j  (no write of s between)
is rewritten  ADD(u,s,c1*c2) @f2 in place of event i,  ADD(u,t,c2) kept,  ADD(t,s,c1) @f3 re-inserted after position P3 in [j, latest] (before the next read of t / write of s).
Values are unchanged (u gets c1*c2*s early, t gets c1*s late) but the frame itineraries of t, s, u change: a paid rank is exchanged for a cheaper one when
H(rank profile) improves.  sites(): every chain with t,s,u public and distinct; the free parameters (f2, P3, f3) range over frames near u,s / t,s plus the chain's own frames
(MOVES1026 a2scan.py); sites on the chart pair (3,127) only are skipped unless --all-frames.  Ported on the shared View (any owned count, public = len(initial))."""
import collections
from bisect import bisect_right,bisect_left
from fractions import Fraction as Q
import movekit as M
from movekit import qs

class A2X(M.Plugin):
    name='a2x'; doc=__doc__; site_fields=('t','s','u','c1','c2')
    all_frames=bool(int(__import__('os').environ.get('TK_A2X_ALL','0')))      # TK_A2X_ALL=1: also chains on the (3,127) charts and chains whose reader sits on another chart (f1 != fj)
    def prepare(self,v):
        S=v.S; rd=collections.defaultdict(list); wr=collections.defaultdict(list); touch=collections.defaultdict(list)
        for i,e in enumerate(S):
            if e[0]=='ADD': touch[e[1]].append(i); touch[e[2]].append(i); rd[e[2]].append(i); wr[e[1]].append(i)
            elif e[0]=='SCALE': touch[e[1]].append(i); rd[e[1]].append(i); wr[e[1]].append(i)
            elif e[0]=='COPY': touch[e[1]].append(i); touch[e[2]].append(i); rd[e[2]].append(i); wr[e[1]].append(i)
            else: touch[e[1]].append(i); wr[e[1]].append(i)
        return dict(rd=rd,wr=wr,touch=touch)
    def chains(self,v,ctx):
        S=v.S; pub=v.n; rd,wr=ctx['rd'],ctx['wr']; out=[]
        for i,e in enumerate(S):
            if e[0]!='ADD' or e[1]>=pub or e[2]>=pub: continue
            t,s=e[1],e[2]; L=rd[t]; k=bisect_right(L,i)
            if k>=len(L): continue
            j=L[k]; ej=S[j]
            if ej[0]!='ADD' or ej[1]>=pub or ej[1] in(s,t): continue
            ws=wr[s]; k2=bisect_right(ws,i)
            if k2<len(ws) and ws[k2]<j: continue
            out.append((i,j,t,s,ej[1],e[4],ej[4]))
        return out
    def latest(self,v,ctx,j,t,s):
        n=len(v.S); rd,wr=ctx['rd'],ctx['wr']
        k=bisect_right(rd[t],j); lim1=rd[t][k]-1 if k<len(rd[t]) else n-1
        k=bisect_right(wr[s],j); lim2=wr[s][k]-1 if k<len(wr[s]) else n-1
        return min(lim1,lim2)
    def nearfr(self,v,ctx,i,regs):
        S=v.S; touch=ctx['touch']; o=[]
        def fr(j): e=S[j]; return e[2] if e[0] in('INIT','CLEAR') else e[-1]
        for r in regs:
            L=touch[r]; k=bisect_left(L,i)
            for j in L[max(0,k-2):k]+L[k:k+3]: o.append(fr(j))
        o=list(dict.fromkeys(o))[:7]
        return o+[3,127]+[v.w['initial'][r] for r in regs]+[v.w['final'][r] for r in regs]
    def sites(self,v,ctx):
        S=v.S
        for (i,j,t,s,u,f1,fj) in self.chains(v,ctx):
            if not self.all_frames and (f1!=fj or f1 in(3,127)): continue
            c1,c2=S[i][3],S[j][3]
            F2=list(dict.fromkeys([f1,fj]+self.nearfr(v,ctx,i,(u,s))))[:10]; F3=list(dict.fromkeys([f1,fj]+self.nearfr(v,ctx,j,(t,s))))[:10]
            Lt=self.latest(v,ctx,j,t,s)
            for f2 in F2:
                for P3 in dict.fromkeys([j,Lt]):
                    for f3 in F3:
                        yield dict(i=i,j=j,t=t,s=s,u=u,c1=c1,c2=c2,f2=f2,P3=P3,f3=f3)
    def span(self,v,ed): return ed['i'],max(ed['j'],ed['P3'])
    # update_sites: none -- the whole class enumerates in ~25 ms, wsearch rebuilds it
    def scalars(self,v,ed):
        S=v.S; i,j,P3=ed['i'],ed['j'],ed['P3']; c1,c2=Q(ed['c1']),Q(ed['c2'])
        assert S[i][:3]==['ADD',ed['t'],ed['s']] and S[j][:3]==['ADD',ed['u'],ed['t']],'stale site'
        early=['ADD',ed['u'],ed['s'],qs(c1*c2),ed['f2']]; late=['ADD',ed['t'],ed['s'],qs(c1),ed['f3']]
        return S[:i]+[early]+S[i+1:P3+1]+[late]+S[P3+1:]
PLUGIN=A2X()
def main(a): return M.cli(PLUGIN,a)
