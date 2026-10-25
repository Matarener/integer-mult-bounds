"""trace which registers hold helper H's input over time (exact rows)."""
import sys
from lift import *
side=sys.argv[1]; H=('L',int(sys.argv[2])); back=side=='backward'; prog=w['programs'][side]
rows={('L',i):v.identity(('L',i)) for i in range(632)}; rows['C',0]=v.identity(('C',0))
cur={('L',i):fm for i,fm in enumerate(c['start'])}; cur['C',0]=None
def hv(r): return {wd:x for (var,wd),x in rows[r].items() if var==H}
for j,e in enumerate(prog):
    k=e[0]
    if k=='scalar':
        gg,frame=e[1:]; t=tuple(gg[1]); before=hv(t)
        if gg[0]=='clear': rows[t]={}
        elif gg[0]=='copy': rows[t]=dict(rows[tuple(gg[2])])
        elif gg[0]=='add': v.add(rows[t],rows[tuple(gg[2])],Q(gg[3],gg[4]))
        else: q=Q(gg[2],gg[3]); rows[t]={a:q*x for a,x in rows[t].items()}
        cur[t]=frame
        if hv(t)!=before: print(j,gg,'dim',dim(frame),'->',{str(a):str(b) for a,b in hv(t).items()})
    elif k=='warp':
        _,r,op,of,nf=e; t=tuple(r); rows[t]=v.warp(rows[t],op,back); cur[t]=nf
        if hv(t): print(j,'WARP',t,'holds')
    elif k=='climb': cur[('L',e[2])]=e[4]
