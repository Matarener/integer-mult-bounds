import sys;sys.path.insert(0,'.')
import bitprims as B,bitword,bisect
from collections import Counter,defaultdict,deque
def ac_domains(v):
    sc=v.scal;paths=v.ctx.paths;fw=defaultdict(set);bw=defaultdict(set)
    for k in paths:
        a,b=map(int,k.split(':'));fw[a].add(b);bw[b].add(a)
    allf=set(v.ctx.dims)
    var=[i for i,e in enumerate(sc) if e[0]=='ADD' and e[1] not in v.owned and e[2] not in v.owned]
    isvar=set(var)
    dom={i:set(allf) for i in var}
    # edges: consecutive events on a register chain: (prev,next) each either var node or fixed frame
    edges=[]
    for r,L in v.S.tl.items():
        if r in v.owned: continue
        seq=[('F',v.w['start'][r])]+[('N',i) for i in L]+[('F',v.w['final'][r])]
        for x,y in zip(seq,seq[1:]): edges.append((x,y))
    adj=defaultdict(list)
    for x,y in edges:
        if x[0]=='N' and x[1] in isvar: adj[x[1]].append((x,y))
        if y[0]=='N' and y[1] in isvar: adj[y[1]].append((x,y))
    def dset(z):
        if z[0]=='F': return {z[1]}
        return dom[z[1]] if z[1] in isvar else {sc[z[1]][3]}
    q=deque(var);inq=set(var)
    while q:
        n=q.popleft();inq.discard(n)
        new=set(dom[n])
        for x,y in adj[n]:
            if x==('N',n) or x[1]==n and x[0]=='N':
                # n is prev: g must have some h in dset(y) with g==h or h in fw[g]
                Dy=dset(y);new={g for g in new if g in Dy or fw[g]&Dy}
            else:
                Dx=dset(x);new={g for g in new if g in Dx or bw[g]&Dx}
        if new!=dom[n]:
            dom[n]=new
            for x,y in adj[n]:
                for z in (x,y):
                    if z[0]=='N' and z[1] in isvar and z[1]!=n and z[1] not in inq: q.append(z[1]);inq.add(z[1])
    return dom
if __name__=='__main__':
    v=B.BitView('bit5708');dom=ac_domains(v)
    print(Counter(len(d) for d in dom.values()).most_common(12))
