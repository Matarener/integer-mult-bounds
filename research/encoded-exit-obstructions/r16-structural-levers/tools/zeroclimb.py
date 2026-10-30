"""Control screen: climbs (paid jobs) on registers whose exact row is identically zero (free zero_retag)."""
exec(open(__file__.replace('zeroclimb.py','split.py')).read().split("for side in ('forward', 'backward'):")[0])
for side in ('forward','backward'):
    back = side=='backward'; prog = w['programs'][side]
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}; rows['C', 0] = v.identity(('C', 0))
    z = Counter(); n = 0
    for e in prog:
        if e[0]=='scalar':
            g,frame=e[1:]; t=tuple(g[1])
            if g[0]=='clear': rows[t]={}
            elif g[0]=='copy': rows[t]=dict(rows[tuple(g[2])])
            elif g[0]=='add': v.add(rows[t], rows[tuple(g[2])], Q(g[3],g[4]))
            else: q=Q(g[2],g[3]); rows[t]={a:q*x for a,x in rows[t].items()}
        elif e[0]=='warp': rows[tuple(e[1])]=v.warp(rows[tuple(e[1])],e[2],back)
        elif e[0]=='climb':
            n+=1
            if not rows['L',e[2]]: z[e[5]]+=1
    print(side,'climbs',n,'on identically-zero rows:',dict(z))
