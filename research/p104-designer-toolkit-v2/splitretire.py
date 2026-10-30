"""SPLITRETIRE (P4+P7 split-then-retire macro): CEILING + ELIGIBILITY screen.  See module docstring.
Eligibility predicate (frames and roles only): a public helper r with gain_est>0 (P7 census ceiling) whose every needed hop a->b has an exact relation
  y_r(struck) = sum c_j row_sj over S = COFR(b) U RETIME(b),  COFR = registers at chart b at the hop, RETIME = registers whose NEXT event is a MOVE into b and untouched
  in between (their hop can be pulled to the hop of r at ZERO census cost: same rank, same register).  Any other completion adds a paid hop: exact price -7.44e-5*rank
  on #5795 (P7 ceilings are <= 4.6e-6), so it is net negative by >= 16x.  A P4 split (split2/split) that would create the sibling must also be census-neutral.
usage: splitretire.py WORD [--json OUT]"""
import sys,os,collections,json
import tkcommon, legal, prims_role as PR
from bisect import bisect_right
def hop_cost(w,k=1):
    rep=legal.check(w,maxviol=5); paid=collections.Counter(rep['paid']); hel=collections.Counter(rep['helpers'])
    k0=PR.kappa_of(paid,hel); p=paid.copy(); p[k]+=1; return PR.kappa_of(p,hel)-k0
def screen(w,maxk=4):
    S=PR.find_sites(w,partial=True); P=w['program']
    by=collections.defaultdict(list)
    for s in S: by[s['missing']].append(s)
    ceil={m:(len(v),sum(s['gain_est'] for s in v)) for m,v in sorted(by.items())}
    one=[s for s in S if s['missing']==1 and s['gain_est']>0]
    regs=[s['r'] for s in one]; tr=PR.trace(w,regs); want={}
    for s in one:
        m=[x for x in tr[s['r']]['moves'] if x[3] and x[4] is None]
        want[(s['r'],m[0][0])]=s
    mvs=collections.defaultdict(list); tch=collections.defaultdict(list)
    for i,e in enumerate(P):
        if e[0]=='MOVE': mvs[e[1]].append((i,e[2],e[3],e[4])); continue
        for r in ((e[1],) if e[0] in('SCALE','INIT','CLEAR') else (e[1],e[2])): tch[r].append(i)
    g=PR.replay_moves(w,regs); next(g); free=[]; inspan=0
    for (i,r,a,b,later,rows,cur,byf) in g:
        s0=want.get((r,i))
        if s0 is None: continue
        y=PR.strike(rows,r,r); cands=[]
        for s in range(len(rows)):
            if s==r or cur[s] is None or cur[s]==b: continue
            nxt=[m for m in mvs[s] if m[0]>i]
            if not nxt or nxt[0][2]!=b: continue
            t=tch[s]; k=bisect_right(t,i)
            if k<len(t) and t[k]<nxt[0][0]: continue
            cands.append(s)
        allc=[s for s in byf[b] if s!=r]+cands
        plan=PR.solve_relation(y,{s:PR.strike(rows,r,s) for s in allc},allc,maxk=maxk,cap=24)
        if plan: free.append(dict(r=r,hop=i,a=a,b=b,plan=[(s,str(c),s in cands) for s,c in plan],gain=s0['gain_est']))
    return dict(ceiling_by_missing_hops=ceil,one_hop_positive=len(one),one_hop_gross=sum(s['gain_est'] for s in one),
                census_free_completions=free,hop_cost_rank1=hop_cost(w,1))
if __name__=='__main__':
    os.environ.setdefault('TK_FREE_BOUNDS','1'); p,w=tkcommon.load(sys.argv[1]); R=screen(w); print(json.dumps(R,indent=1,default=str))
