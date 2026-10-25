"""Candidates (h, P) whose blocking contacts are all reads of h before its first producer."""
from timeline import *
def candidates(w,ev,con,start,end,widths=(8,9)):
    rest=set(map(int,w['helper_final'])); removed=set(w['removed'])
    out=[]
    for h in range(224,704):
        if h in removed or h in rest: continue
        E=start[h]; wd=C.dim(end[h])-C.dim(E)
        if wd not in widths: continue
        cs=[ev[p] for p in con[h]]
        prod=next((i for i,e in enumerate(cs) if writes(e,h)),len(cs))
        seen=set()
        for u in range(1,512):
            if E>>u & 1: continue
            P=0
            for x in C.points(E): P|=1<<x; P|=1<<(x^u)
            if P in seen: continue
            seen.add(P)
            block=[i for i,e in enumerate(cs) if e['frame'] is None or (e['frame'] & P)!=P]
            lb=max(block) if block else -1
            if lb>=prod: continue
            if any(not(cs[i]['kind']=='add' and cs[i]['g'][2]==h) for i in block): continue
            lo=cs[lb]['pos']+1 if lb>=0 else 0
            hi=cs[prod]['pos'] if prod<len(cs) else len(ev)
            out.append(dict(h=h,width=wd,P=P,u=u,nblock=len(block),lo=lo,hi=hi,
                            block=[cs[i]['pos'] for i in block],
                            next_frame=cs[lb+1]['frame'] if lb+1<len(cs) else None))
    return out
