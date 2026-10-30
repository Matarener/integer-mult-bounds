"""synth.hubgen -- HUB network for the residual line of the FRONTGEN word (HUBGEN, see ../module docstring).  Scope [toolkit synth, hub/butterfly + async-relay helper network].

Used by frontgen when the spec says `front: generated, helpers: hub` (`tk synth --front-gen --helpers hub`).

MODEL (no template topology is copied; the structure is ANNEALED against the R0 surrogate, kernel synth/hubsa.cpp):
  * X_i gets a FLAG of stops f_s(i) = span(q_i[0..s]) (q_i[0] = p_i, dim s+1, s <= 6) -- an X main with several stops costs R0 tax 8 ln 8 - sum r ln r over its used stops.
  * Y_j needs  -res_ji x_i  for the 48 ports i with p_i perp p_j.  It collects them on a CHAIN of nested frames inside Q_j: the biggest chain is Y_j's own main (it meets X_i at a stop of X_i that lies
    inside Q_j); every other chain is a private HUB (helper born at frame 0, picks x_i with coefficient -res_ji at X-stops along its nested chain, is read by Y_j at Q_j, climbs to F9 where it is restored
    by undoing its pickups).  A hub's R0 tax is 9 ln 9 - sum r ln r over (d1, d2-d1, ..., 8-dr, 1): one aggregated hub replaces up to a_t star carriers (1 pickup each, tax 6.154 each).
  * SA state = the X flags; for fixed flags the cover of each Y_j (min number of nested chains through its usable X stops) is built greedily (longest chain by DP).
plan(ports) -> dict(flags={i:[q0..q6]}, ycover={j:[(i, level, chain),...]}, info)   loaded from data/hubgen_plan.json (validated: frames nested, inside Q_j, every orth port covered once)
solve(ports, seed, iters, T0, T1, init=None)   runs the C++ kernel (compiled on demand) and stores the plan
"""
import os,sys,json,math,subprocess,tempfile,hashlib
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
DATA=os.path.join(HERE,'data','hubgen_plan.json')
par=lambda a,b:bin(a&b).count('1')%2
def _H(r): return r*math.log(r) if r>0 else 0.0
def span(vs):
    s={0}
    for v in vs: s|={x^v for x in s}
    return frozenset(s)
def kernel_binary():
    exe=os.path.join(tempfile.gettempdir(),'hubsa_%s'%hashlib.md5(open(os.path.join(HERE,'hubsa.cpp'),'rb').read()).hexdigest()[:8])
    if not os.path.exists(exe):
        subprocess.check_call(['c++','-O2','-std=c++17','-o',exe,os.path.join(HERE,'hubsa.cpp')])
    return exe
def parse_output(text):
    flags={}; ycover={}; E=None
    for ln in text.splitlines():
        t=ln.split()
        if not t: continue
        if t[0]=='E': E=float(t[1])
        elif t[0]=='Q': flags[int(t[1])]=[int(x) for x in t[2:]]
        elif t[0]=='Y':
            j=int(t[1]); ycover[j]=[tuple(int(y) for y in x.split(':')) for x in t[3:]]
    return dict(flags=flags,ycover=ycover,E=E)
def solve(ports,seed=1,iters=100000,T0=2.0,T1=0.1,init=None,out=None):
    exe=kernel_binary(); d=tempfile.mkdtemp(); pf=os.path.join(d,'ports.txt'); open(pf,'w').write('%d\n%s\n'%(len(ports),' '.join(map(str,ports))))
    cmd=[exe,pf,str(seed),str(iters),str(T0),str(T1)]
    if init:
        inf=os.path.join(d,'init.txt'); open(inf,'w').write('\n'.join(' '.join(map(str,init[i])) for i in range(len(ports)))); cmd.append(inf)
    txt=subprocess.run(cmd,capture_output=True,text=True,check=True).stdout
    pl=parse_output(txt)
    if out: json.dump(dict(ports=ports,flags={str(k):v for k,v in pl['flags'].items()},ycover={str(k):v for k,v in pl['ycover'].items()},E=pl['E']),open(out,'w'))
    return pl
def load_plan(path=DATA):
    J=json.load(open(path)); return dict(ports=J['ports'],flags={int(k):v for k,v in J['flags'].items()},ycover={int(k):[tuple(x) for x in v] for k,v in J['ycover'].items()},E=J['E'])
def tax_hub(ds):
    prev=0; t=_H(9)
    for d in ds: t-=_H(d-prev); prev=d
    return t-_H(8-prev)-_H(1)
def tax_y(ds):
    prev=0; t=_H(8)
    for d in ds: t-=_H(d-prev); prev=d
    return t-_H(8-prev)
def tax_x(dims):
    prev=1; t=_H(8)
    for d in sorted(dims):
        if d>1: t-=_H(d-prev); prev=d
    return t-_H(9-prev)
def validate(pl,ports):
    """check the plan against the geometry; returns (pieces, info). pieces[j] = list of chains, chain = list of (dim, [ports]) ascending; chain 0 is Y_j's own"""
    m=len(ports); flags=pl['flags']; pieces={}; nh=0; tax=0.0; xdims={i:set() for i in range(m)}
    for j in range(m):
        Oj=[i for i in range(m) if par(ports[i],ports[j])==0]
        cov=pl['ycover'][j]; assert sorted(c[0] for c in cov)==sorted(Oj),'cover of Y%d does not match the orth set'%j
        ch={}
        for (i,s,c) in cov:
            q=flags[i][:s+1]; assert q[0]==ports[i]
            assert all(par(v,ports[j])==0 for v in q),'frame of X%d level %d not inside Q_%d'%(i,s,j)
            assert len(span(q))==1<<(s+1),'dependent flag'
            ch.setdefault(c,{}).setdefault(s,[]).append(i); xdims[i].add(s+1)
        chains=[]
        for c in sorted(ch):
            seq=sorted(ch[c].items())
            for (s1,l1),(s2,l2) in zip(seq,seq[1:]):
                a=span(flags[l1[0]][:s1+1]); b=span(flags[l2[0]][:s2+1]); assert a<b,'chain not nested (Y%d chain %d)'%(j,c)
            # all ports of one level must share the frame
            for s,l in seq: assert len({span(flags[i][:s+1]) for i in l})==1
            chains.append([(s+1,l) for s,l in seq])
        pieces[j]=chains; nh+=len(chains)-1
        for k,chn in enumerate(chains):
            ds=[d for d,_ in chn]; tax+= tax_y(ds) if k==0 else tax_hub(ds)
    taxx=sum(tax_x(xdims[i]) for i in range(m))
    return pieces,dict(hubs=nh,tax_chains=tax,tax_x=taxx,tax_total=tax+taxx)
def apply(bk,ctx):
    """frontgen hook: replaces the star residual by the annealed hub network.  ctx = dict(ports, frames, fid, Qf, res).  Returns bk with bk['rcar']=[] and bk['hub'] = dict(hubs=[dict(j)], ops=[...])
    ops are tuples (dim, dst, src, coef_sign_kind, frame_id, j, i) -- see frontgen for the emission order"""
    ports=ctx['ports']; pl=load_plan(); assert pl['ports']==ports,'stored hub plan is for other ports; run hubgen.solve'
    pieces,info=validate(pl,ports); fid=ctx['fid']; Qf=ctx['Qf']; flags=pl['flags']
    hubs=[]; ops=[]
    for j,chains in pieces.items():
        for k,chn in enumerate(chains):
            hi=None
            if k>0: hi=len(hubs); hubs.append(dict(j=j))
            for d,l in chn:
                for i in l:
                    f=fid(flags[i][:d])
                    ops.append(dict(dim=d,kind='pick',hub=hi,j=j,i=i,frame=f))
            if k>0: ops.append(dict(dim=8,kind='read',hub=hi,j=j,frame=Qf[j]))
    bk=dict(bk); bk['rcar']=[]; bk['hub']=dict(hubs=hubs,ops=ops,info=info)
    return bk
