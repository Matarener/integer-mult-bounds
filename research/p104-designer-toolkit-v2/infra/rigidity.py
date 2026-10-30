"""FRAME RIGIDITY under the VERIFIER's real freedom (tests P104CH 'frames are rigid given a fixed circuit').
Clusters = union-find of (register, stop) segments joined by equal-frame ADD/COPY (same as P104CH cl.py).  Ascending links
along each register chain (owned: descending).  A cluster's frame must satisfy L(c) <= F <= U(c), L = SUM of anchored frames
below it, U = INTERSECTION of anchored frames above it (over ALL subspaces of F2^9, not just the word's 1027 frames: every nested
pair is natively legal at price = dim gap, native_pair.py).  Anchors:  'P104CH' = every register's initial & final;
'VERIFIER' = only what local.py/native() pins: X initial = <p>, Y final = p^perp  (helper initial/final, X final, Y initial free).
Reports #clusters forced (L==U) and the log2 number of admissible frames (Gaussian binomials).
python rigidity.py WORD.json.gz"""
import sys,collections,math,legal
def run(path):
    w=legal.load(path);prog=w['program'];NH=len(w['initial']);live=set(w['live']);main=live|{r+112 for r in live}
    fr=legal.spans(w); 
    parent={}
    def find(x):
        while parent.setdefault(x,x)!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def uni(a,b): parent[find(a)]=find(b)
    stop=collections.defaultdict(int); chain=collections.defaultdict(list); fcur={}
    for r in range(NH): chain[r].append((0,w['initial'][r])); fcur[r]=w['initial'][r]
    for r in range(NH,NH+8): fcur[r]=None
    for e in prog:
        op,r=e[0],e[1]
        if op=='MOVE': stop[r]+=1; chain[r].append((stop[r],e[3])); fcur[r]=e[3]
        elif op=='INIT':
            chain[r]=[(0,e[2])]; stop[r]=0
        elif op in('ADD','COPY'):
            uni((r,stop[r]),(e[2],stop[e[2]]))
    segs=[(r,s,f) for r in chain for s,f in chain[r]]
    for r,s,f in segs: find((r,s))
    cf={}
    for r,s,f in segs: cf[find((r,s))]=f
    links=set()
    for r,ch in chain.items():
        for (s1,f1),(s2,f2) in zip(ch,ch[1:]):
            a,b=find((r,s1)),find((r,s2))
            links.add((a,b) if r<NH else (b,a))      # lo -> hi
    up=collections.defaultdict(list);dn=collections.defaultdict(list)
    for a,b in links: up[a].append(b); dn[b].append(a)
    def sp(f): return fr[f]
    def anchors(mode):
        A=set()
        for r in range(NH):
            if mode=='P104CH' or (r in live): A.add(find((r,0)))
            if mode=='P104CH' or (r-112 in live and r in main and r not in live): A.add(find((r,stop[r])))
        return A
    out={}
    for mode in ('P104CH','VERIFIER'):
        A=anchors(mode)
        # propagate: L(c)=sum of anchored frames at or below; U(c)=intersection at or above (bit-vector over 512 points; sum via span)
        order=list(cf)
        def reach(adj,starts):
            seen=set(starts);st=list(starts)
            while st:
                x=st.pop()
                for y in adj[x]:
                    if y not in seen: seen.add(y);st.append(y)
            return seen
        below={a:reach(dn,[a]) for a in A}; above={a:reach(up,[a]) for a in A}
        Lset=collections.defaultdict(list);Uset=collections.defaultdict(list)
        for a in A:
            for c in above[a]: Lset[c].append(a)     # c above a  => a<=c
            for c in below[a]: Uset[c].append(a)     # c below a  => c<=a
        forced=0;free=0;bits=[]
        for c in order:
            if c in A: continue
            Lb=set([0])
            for a in Lset[c]: Lb=Lb|set(x^y for x in Lb for y in sp(cf[a])) if False else Lb
            # sum of subspaces: closure via bases
            basis=[]
            for a in Lset[c]:
                for v in w['frames'][cf[a]]: basis.append(v)
            Ls=set([0])
            for v in basis:
                if v not in Ls: Ls|={x^v for x in Ls}
            Us=None
            for a in Uset[c]:
                Us=set(sp(cf[a])) if Us is None else (Us&set(sp(cf[a])))
            if Us is None: Us=set(range(512))
            dL=len(Ls).bit_length()-1; dU=len(Us).bit_length()-1
            if len(Ls)==len(Us): forced+=1
            else:
                free+=1; m=dU-dL
                bits.append(m)
        out[mode]=(len(order),len(A),forced,free,collections.Counter(bits))
        print(mode,'clusters',len(order),'anchored',len(A),'forced(L==U)',forced,'with freedom',free,'quotient dims',dict(sorted(collections.Counter(bits).items())),flush=True)
    return out
if __name__=='__main__': run(sys.argv[1])
