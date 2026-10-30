exec(open(__file__.replace('split_ctl.py','split.py')).read().split("for side in ('forward', 'backward'):")[0])
import itertools
for side in ('forward','backward'):
    back = side=='backward'; prog = w['programs'][side]
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}; rows['C', 0] = v.identity(('C', 0))
    nsc=0; dirty_max=Counter(); cleanmid=Counter()
    first = {}; last = {}
    for j,e in enumerate(prog):
        for r in ([tuple(x) for x in e[1][1:3] if isinstance(x,list)] if e[0]=='scalar' else []):
            first.setdefault(r,j); last[r]=j
    # evaluate cleanliness of every helper at every event index (slow path, sampled every 50 events)
    for j,e in enumerate(prog):
        if e[0]=='scalar':
            g,frame=e[1:]; t=tuple(g[1]); nsc+=1
            if g[0]=='clear': rows[t]={}
            elif g[0]=='copy': rows[t]=dict(rows[tuple(g[2])])
            elif g[0]=='add': v.add(rows[t], rows[tuple(g[2])], Q(g[3],g[4]))
            else: q=Q(g[2],g[3]); rows[t]={a:q*x for a,x in rows[t].items()}
        elif e[0]=='warp':
            _,r,op,o,n=e; rows[tuple(r)]=v.warp(rows[tuple(r)],op,back)
        if j%25==0:
            holders=defaultdict(set)
            for r,row in rows.items():
                for (var,wd) in row: holders[var].add(r)
            for i in range(224,632):
                h=('L',i)
                if first.get(h,10**9) < j < last.get(h,-1):
                    if {var for (var,wd) in rows[h]}<={h} and holders[h]<={h}: cleanmid[i]+=1
    ok = all(rows['L',r]==v.expected(('L',r),[],back,False) for r in range(632))
    print(side,'scalar',nsc,'final rows == expected (positive control):',ok,'helpers clean strictly inside their op span (sampled):',len(cleanmid))
