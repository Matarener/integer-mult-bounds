"""R19: anatomy of the unliftable residual at a hand-off point (side, helper, event)."""
import sys
from lift import *
side=sys.argv[1]; H=('L',int(sys.argv[2])); J=int(sys.argv[3]); back=side=='backward'; prog=w['programs'][side]
anch,clb=timelines(prog)
rows={('L',i):v.identity(('L',i)) for i in range(632)}; rows['C',0]=v.identity(('C',0))
cur={('L',i):fm for i,fm in enumerate(c['start'])}; cur['C',0]=None
for j,e in enumerate(prog[:J+1]):
    k=e[0]
    if k=='scalar':
        gg,frame=e[1:]; t=tuple(gg[1])
        if gg[0]=='clear': rows[t]={}; cur[t]=frame
        elif gg[0]=='copy': rows[t]=dict(rows[tuple(gg[2])])
        elif gg[0]=='add': v.add(rows[t],rows[tuple(gg[2])],Q(gg[3],gg[4]))
        else: q=Q(gg[2],gg[3]); rows[t]={a:q*x for a,x in rows[t].items()}
    elif k=='warp':
        _,r,op,of,nf=e; t=tuple(r); rows[t]=v.warp(rows[t],op,back); cur[t]=nf
    elif k=='climb': cur[('L',e[2])]=e[4]
    elif k=='center': cur[('C',e[1])]=e[3]
F=cur[H]; print('h',H,'at frame',F,fr[F],'dim',dim(F))
atF=[r for r in cur if cur[r]==F]; print('R_F',atF)
piv=[]
for r in atF: addpiv(rows[r],piv)
res=reduce({(H,()):Q(1)},piv)
print('residual', {(str(a),str(b)):str(x) for (a,b),x in res.items()})
for (var,wd) in res:
    hold=[r for r in rows if any(vv==var for (vv,ww) in rows[r])]
    print(' var',var,'word',wd,'holders',len(hold))
    for r in hold[:8]:
        A=anch[r]; idx=[a[0] for a in A]; p=bisect.bisect_right(idx,J)
        P=A[p-1][2] if p else c['start'][r[1]]; N=A[p][1] if p<len(A) else c['final'][r[1]]
        print('   ',r,'cur',cur[r],'dim',dim(cur[r]) if cur[r] is not None else None,'P',fr[P],'N',fr[N],'P<=F',SP[P]<=SP[F],'F<=N',SP[F]<=SP[N],'lift',lift_cost(r,J,F,anch,clb))
