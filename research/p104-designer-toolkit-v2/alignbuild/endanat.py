"""ENDANATOMY task 1: per early-ending helper (end frame dim<9): end frame, co-present registers, minimal redundancy set, junk sharing, placement.
EXACT full-coordinate replay (as OWNEDRANK/meas1.py).  usage: compute(w) -> dict(rows, tw)   [alignbuild copy of ENDANATOMY/anat.py; exact Fraction replay]"""
import sys,gzip,json,collections,pickle,itertools
import os
_TK=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_TK+'/synth',_TK+'/gen2'):
    if _p not in sys.path: sys.path.insert(0,_p)
import kernel2net as KN
from ee0 import solve
from fractions import Fraction as Q
def compute(w):
    n=len(w['initial']); role=KN.roles(w); fb=w['frames']; dim=[len(b) for b in fb]; P=w['program']; T=len(P)
    V={r:{r:Q(1)} for r in range(n)}; cur={r:w['initial'][r] for r in range(n)}
    ver=collections.defaultdict(list)
    for r in range(n): ver[r].append((-1,dict(V[r])))
    stay=collections.defaultdict(list); tin={r:-1 for r in range(n)}
    lastop=collections.defaultdict(lambda:-1)
    ev=collections.defaultdict(list)   # r -> (t,op,partner,frame,coef,dir) dir 'w' written 'r' read
    chain={r:[dim[w['initial'][r]]] for r in range(n)}
    for t,e in enumerate(P):
        o=e[0]
        if o=='MOVE':
            r=e[1]
            if r<n: stay[r].append((cur[r],tin[r],t)); cur[r]=e[3]; tin[r]=t; chain[r].append(dim[e[3]])
        elif o=='INIT':
            r=e[1]
            if r<n: V[r]={}; cur[r]=e[2]; tin[r]=t; ver[r].append((t,{}))
            else: V[r]={}
        elif o=='CLEAR':
            r=e[1]
            if r<n: stay[r].append((cur[r],tin[r],t)); V[r]={}; cur[r]=None
            else: V[r]={}
        elif o=='SCALE':
            r=e[1]; V[r]={c:v*Q(e[2]) for c,v in V[r].items()}
            if r<n: ver[r].append((t,dict(V[r]))); lastop[r]=t
        elif o in('ADD','COPY'):
            d,s,q,f=e[1],e[2],Q(e[3]) if o=='ADD' else Q(1),e[4]
            fd=dict(V[d]) if o=='ADD' else {}
            for c,v in V[s].items():
                fd[c]=fd.get(c,0)+q*v
                if fd[c]==0: del fd[c]
            V[d]=fd
            if d<n: ver[d].append((t,dict(fd))); lastop[d]=t
            if s<n: lastop[s]=max(lastop[s],t)
            if d<n: ev[d].append((t,o,s,f,q,'w'))
            if s<n: ev[s].append((t,o,d,f,q,'r'))
    for r in range(n): stay[r].append((cur[r],tin[r],T))
    pstay=collections.defaultdict(list)
    for r in range(n):
        for f,ti,to in stay[r]: pstay[f].append((r,ti,to))
    def versions(r,t0,t1):
        out=[]; vs=ver[r]
        for k,(tt,cc) in enumerate(vs):
            te=vs[k+1][0] if k+1<len(vs) else T
            if te>t0 and tt<t1 and cc: out.append(cc)
        return out
    def val_at(r,t):
        c={}
        for tt,cc in ver[r]:
            if tt<t: c=cc
            else: break
        return c
    rows=[]
    endsat=collections.defaultdict(list)
    for h in range(n):
        if role(h)!='H': continue
        g,ti,to=stay[h][-1]
        if dim[g]<9: endsat[g].append(h)
    for h in range(n):
        if role(h)!='H': continue
        g,ti,to=stay[h][-1]
        if dim[g]>=9: continue
        t_end=lastop[h]
        D={c:-v for c,v in val_at(h,ti+1).items()}
        for c,v in ver[h][-1][1].items():
            D[c]=D.get(c,0)+v
            if D[c]==0: del D[c]
        flip=False
        if D and ver[h][-1][1]:
            # end may carry a sign flip (SCALE -1): nominal final is +-arrival; test D with the other sign too (resolved below)
            D2={c:v for c,v in val_at(h,ti+1).items()}
            for c,v in ver[h][-1][1].items():
                D2[c]=D2.get(c,0)+v
                if D2[c]==0: del D2[c]
        else: D2=None
        pres=[]; vers={}
        for r,a0,a1 in pstay.get(g,[]):
            if r==h or a1<=ti or a0>=t_end: continue
            vv=versions(r,max(ti,a0),min(t_end,a1))
            pres.append(dict(r=r,role=role(r),chain=list(chain[r]),arr=a0,dep=a1,cont=a1>t_end,nver=len(vv),
                             ends_here=(role(r)=='H' and stay[r][-1][0]==g)))
            vers.setdefault(r,[]).extend(vv)
        regs=[p['r'] for p in pres if vers[p['r']]]
        pub=[v for r in regs for v in vers[r]]
        okp=(not D) or (bool(pub) and solve(D,pub) is not None)
        if not okp and D2 is not None and pub and solve(D2,pub) is not None: okp=True; D=D2; flip=True
        # minimal register subset: relevant = regs with versions overlapping support of D (any coord) else all
        mins=None
        if D and okp:
            rel=[r for r in regs if any(set(v)&set(D) for v in vers[r])] or regs
            for k in range(1,min(5,len(rel))+1):
                for S in itertools.combinations(rel,k):
                    if solve(D,[v for r in S for v in vers[r]]) is not None: mins=list(S); break
                if mins: break
            if mins is None:   # greedy deletion
                S=list(regs)
                for r in list(S):
                    T2=[x for x in S if x!=r]
                    if T2 and solve(D,[v for x in T2 for v in vers[x]]) is not None: S=T2
                mins=S
        Dx=[c for c in D if role(c)=='X']; Dy=[c for c in D if role(c)=='Y']; Dh=[c for c in D if role(c)=='H']
        # junk sharing: H-coords of D carried by suppliers
        sup=[]
        for r in (mins or []):
            sv=set(c for v in vers[r] for c in v)
            jh=sorted(set(Dh)&sv)
            es=set(endsat[g])
            evg=[e for e in ev[r] if e[3]==g and e[2]!=h]
            evne=[e for e in ev[r] if e[3]==g and e[2] not in es]
            evall=[e for e in ev[r] if e[3]==g]
            arr_r=[p['arr'] for p in pres if p['r']==r][0]
            evh=[e for e in ev[r] if e[2]==h]
            hread=[e for e in ev[h] if e[2]==r]
            sup.append(dict(r=r,role=role(r),chain=chain[r],nonend=len(evne),evg=len(evall),arr_before=arr_r<ti,arr=arr_r,jshared=len(jh),ev_other_at_g=len(evg),ev_with_h=len(evh),h_reads=len(hread),
                            hx=len(set(h_c for v in vers[r] for h_c in v if role(h_c)=='X')),
                            ends_here=(role(r)=='H' and stay[r][-1][0]==g),
                            others_same_g=len(endsat[g])))
        rows.append(dict(h=h,g=g,d=dim[g],flip=flip,Dxl=sorted(Dx),Dhl=sorted(Dh)[:60],mates=sorted({e[2] for e in ev[h] if e[0]=='ADD' and e[3]==g and e[5]=='w'}|{e[2] for e in ev[h] if e[3]==g and e[5]=='r'}),chain=list(chain[h]),arr=ti,tend=t_end,D=len(D),Dx=len(Dx),Dy=len(Dy),Dh=len(Dh),okpub=okp,
                         pres=pres,mins=mins,sup=sup,enders_at_g=list(endsat[g]),
                         hevents_g=sum(1 for e in ev[h] if e[3]==g), hx_supp=len(set(c for v in [ver[h][-1][1]] for c in v if role(c)=='X'))))
    # TWIN analysis per end frame (CHARTLP deficiency form): S = continuing contentful co-present at g, arrival values; P drops e_N (N = enders at g)
    tw={}
    for g,N in endsat.items():
        Nset=set(N); tmax=max(lastop[h] for h in N); tmin=min(stay[h][-1][1] for h in N)
        S=[]
        for r,a0,a1 in pstay.get(g,[]):
            if r in Nset: continue
            if a0==-1 and w['initial'][r]==g: continue      # births at g are not arrivals (CHARTLP lemma)
            v=val_at(r,a0+1)
            S.append((r,a0,v,{c:x for c,x in v.items() if c not in Nset}))
        vecs=[p for _,_,_,p in S]
        # rank_P(S) via incremental elimination
        piv=[]; indep=[]
        for i,u in enumerate(vecs):
            if u and (not indep or solve(u,[vecs[j] for j in indep]) is None): indep.append(i)
        rk=len(indep); nz=sum(1 for u in vecs if u)
        # minimal circuits of size 2 and 3 among nonzero P-vectors (zero P-vector = size-1 circuit)
        circ=[]
        idx=[i for i,u in enumerate(vecs) if u]
        for i in range(len(vecs)):
            if not vecs[i]: circ.append((i,))
        for a_,b_ in itertools.combinations(idx,2):
            if solve(vecs[a_],[vecs[b_]]) is not None: circ.append((a_,b_))
        c2={x for c in circ for x in c}
        for tri in itertools.combinations(idx,3):
            if any(set(c)<=set(tri) for c in circ): continue
            if solve(vecs[tri[0]],[vecs[tri[1]],vecs[tri[2]]]) is not None: circ.append(tri)
        # one minimal dependent set (circuit) of the P-vectors by deletion, if deficiency>0
        cdel=None
        if len(S)-rk>0:
            cur_=[i for i in range(len(S))]
            def dep(L):
                ind=[]
                for i in L:
                    u=vecs[i]
                    if u and (not ind or solve(u,[vecs[j] for j in ind]) is None): ind.append(i)
                return len(ind)<len(L)
            for i in list(cur_):
                t2=[x for x in cur_ if x!=i]
                if dep(t2): cur_=t2
            cdel=[S[i][0] for i in cur_]
        info=[]
        for i,(r,a0,v,Pv) in enumerate(S):
            rd=[e[2] for e in ev[r] if e[5]=='w' and e[2] in Nset]    # r read an ender (ender junk spread to r)
            prev=chain[r][chain[r].index(dim[g])-1] if dim[g] in chain[r] and chain[r].index(dim[g])>0 else None
            info.append(dict(r=r,role=role(r),chain=chain[r],prev=prev,born=chain[r][0],arr=a0,P_nnz=len(Pv),read_enders=len(rd),holds_eN=sum(1 for c in v if c in Nset)))
        def xr(vs):
            xs=[{c:x for c,x in v.items() if role(c)=='X'} for v in vs]; ind=[]
            for u in xs:
                if u and (not ind or solve(u,ind) is None): ind.append(u)
            return len(ind)
        Av=[val_at(h,stay[h][-1][1]+1) for h in N]
        qx=xr([v for _,_,v,_ in S]+Av)-xr([v for _,_,v,_ in S])
        tw[g]=dict(cdel=cdel,q=qx,d=dim[g],enders=list(N),nS=len(S),rankP=rk,defic=len(S)-rk,circuits=[tuple(S[i][0] for i in c) for c in circ],info=info)
    return dict(rows=rows,tw=tw)
