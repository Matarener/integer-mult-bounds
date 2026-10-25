import sys; sys.path.insert(0,'/Users/joelpulikkan/imb-harness/r13/tools')
from construct import *
w=load(); M=build_mip(w,'forward',0.00302, wide='wide' in sys.argv)
Fm=M['S']['Fm']; nv=M['nv']; x=np.zeros(nv)
for (i,X),v in M['V'].items(): x[v]=1.0 if M['cur'][i]==X else 0.0
# used nodes per key
used=defaultdict(set)
seg=M['S']['seg']
for (i,X),v in M['V'].items():
    if M['cur'][i]==X:
        for R,k in seg[i].items():
            if isinstance(k,int): used[R,k].add(X)
gaps=defaultdict(set)
for (key,u,v_) in M['arcs']: gaps[key].add(u); gaps[key].add(v_)
for key,ch in M['chains'].items():
    for a,b in zip(ch,ch[1:]):
        if (key,a,b) not in M['arcs'] and not any(k==key and u==a for (k,u,_) in []): pass
        nodes=[a]+sorted([X for X in used[key] if X not in ch and Fm.le(a,X) and Fm.le(X,b)],key=lambda X:Fm.dims[X])+[b]
        for u,v_ in zip(nodes,nodes[1:]):
            j=M['arcs'].get((key,u,v_))
            if j is None:
                if len(nodes)>2 or any((key,a,t) in M['arcs'] for t in [b]): print('missing arc',key,u,v_,Fm.dims[u],Fm.dims[v_],Fm.le(u,v_))
            else: x[j]=1
A=M['A'].tocsr(); r=A@x
bad=[(k,r[k],M['lb'][k],M['ub'][k]) for k in range(len(M['lb'])) if r[k]<M['lb'][k]-1e-9 or r[k]>M['ub'][k]+1e-9]
print('violations',len(bad),bad[:10])
k0=bad[0][0]
cols=A[k0].indices
inv={v:k for k,v in M['arcs'].items()}
print([inv.get(c_,('V?',c_)) for c_ in cols][:10])
key=inv[cols[0]][0]; print('chain',[(X,Fm.dims[X]) for X in M['chains'][key]], 'used',[(X,Fm.dims[X]) for X in used[key]])
