"""synth.hubladder -- HUB-HUB MERGE LADDERS (HUBLADDER, see ../module docstring).  Scope [toolkit synth, hub-hub merge ladder network].

Network model (annealed against the R0 tax surrogate by the C++ kernel synth/hubladder.cpp; nothing copied from a swarm word):
  register = Y main or hub.  It has a read frame F (Y: Q_j = p_j^perp, hub: the frame where its parent reads it) and a SPINE = nested chain of frames inside F (the frames are X-flag stops).
  It picks X_i directly at the spine frame where i has a stop.  Ports it cannot pick on the spine are delivered by CHILD hubs read at a spine frame V (child top = V, child spine strictly inside V), recursively
  (HUB-HUB merge).  A hub is identified by (top frame, port set, normalised signs) and is SHARED by every parent that needs it, so a ladder is priced once.
  R0 tax: hub 9ln9 - sum r ln r over the rank increments (spine dims + top, then F9); Y 8ln8 - sum over (spine dims + 8); X_i as in hubgen.
plan(ports) -> dict(flags, hubs{id:dict(top,picks,kids)}, ys{j:dict(picks,kids)}, E)  from data/hubladder_plan.json     solve(...) runs the kernel     validate(pl, ports) -> checks supports/frames, returns stats
apply(bk, ctx): frontgen hook (helpers: ladder): registers hubs, picks (reg += coef X_i at the pick frame) and child reads (parent += coef child at the child's top frame).
"""
import os,sys,json,math,subprocess,tempfile,hashlib,collections
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
DATA=os.path.join(HERE,'data','hubladder_plan.json')
par=lambda a,b:bin(a&b).count('1')%2
def _H(r): return r*math.log(r) if r>0 else 0.0
def span(vs):
    s={0}
    for v in vs: s|={x^v for x in s}
    return frozenset(s)
def kernel_binary():
    src=os.path.join(HERE,'hubladder.cpp')
    exe=os.path.join(tempfile.gettempdir(),'hubladder_%s'%hashlib.md5(open(src,'rb').read()).hexdigest()[:8])
    if not os.path.exists(exe): subprocess.check_call(['c++','-O2','-std=c++17','-o',exe,src])
    return exe
def parse_output(text):
    flags={}; hubs={}; ys={}; E=None
    def kids(t): return [tuple(int(y) for y in x.split(':')) for x in t]
    for ln in text.splitlines():
        t=ln.split()
        if not t: continue
        if t[0]=='E': E=float(t[1])
        elif t[0]=='Q': flags[int(t[1])]=[int(x) for x in t[2:]]
        elif t[0]=='H':
            k=t.index('picks'); kk=t.index('kids')
            hubs[int(t[1])]=dict(top=tuple(int(x) for x in t[3:6]),picks=[tuple(int(y) for y in x.split(':')) for x in t[k+1:kk]],kids=kids(t[kk+1:]))
        elif t[0]=='Y':
            k=t.index('picks'); kk=t.index('kids')
            ys[int(t[1])]=dict(picks=[tuple(int(y) for y in x.split(':')) for x in t[k+1:kk]],kids=kids(t[kk+1:]))
    return dict(flags=flags,hubs=hubs,ys=ys,E=E)
def write_signs(path,res):
    open(path,'w').write('\n'.join(' '.join(str((r>0)-(r<0)) for r in row) for row in res)+'\n')
def solve(ports,res,seed=1,iters=20000,T0=0.8,T1=0.1,init=None,out=None,maxd=6):
    exe=kernel_binary(); d=tempfile.mkdtemp(); pf=os.path.join(d,'ports.txt'); open(pf,'w').write('%d\n%s\n'%(len(ports),' '.join(map(str,ports))))
    sf=os.path.join(d,'signs.txt'); write_signs(sf,res)
    cmd=[exe,pf,sf,str(seed),str(iters),str(T0),str(T1),'-',str(maxd)]
    if init:
        inf=os.path.join(d,'init.txt'); open(inf,'w').write('\n'.join(' '.join(map(str,init[i])) for i in range(len(ports)))); cmd[7]=inf
    pl=parse_output(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout); pl['ports']=ports
    if out: save_plan(pl,out)
    return pl
def save_plan(pl,path):
    json.dump(dict(ports=pl['ports'],E=pl['E'],flags={str(k):v for k,v in pl['flags'].items()},hubs={str(k):v for k,v in pl['hubs'].items()},ys={str(k):v for k,v in pl['ys'].items()}),open(path,'w'))
def load_plan(path=DATA):
    J=json.load(open(path)); f=lambda L:[tuple(x) for x in L]
    return dict(ports=J['ports'],E=J['E'],flags={int(k):v for k,v in J['flags'].items()},hubs={int(k):dict(top=tuple(v['top']),picks=f(v['picks']),kids=f(v['kids'])) for k,v in J['hubs'].items()},
                ys={int(k):dict(picks=f(v['picks']),kids=f(v['kids'])) for k,v in J['ys'].items()})
def tax_chain(ds,hub):
    prev=0; t=_H(9 if hub else 8)
    for d in ds: t-=_H(d-prev); prev=d
    return t-(_H(9-prev) if hub else 0)
def tax_x(dims):
    prev=1; t=_H(8)
    for d in sorted(dims):
        if d>1: t-=_H(d-prev); prev=d
    return t-_H(9-prev)
def validate(pl,ports):
    """exact structural check: every Y's content support = its 48 orthogonal ports exactly once; every pick frame / child top lies inside the register's top; spine+child tops form one nested chain.
    returns stats incl. R0 tax by role."""
    m=len(ports); flags=pl['flags']; fsp=lambda i,s:span(flags[i][:s+1])
    for i in flags: assert flags[i][0]==ports[i]
    Qsp=lambda j:frozenset(x for x in range(512) if par(x,ports[j])==0)
    memo={}
    def top_of(h): 
        ti,ts,tj=h['top']; return fsp(ti,ts) if ti>=0 else Qsp(tj)
    def support(reg,top):
        cnt=collections.Counter(); frames=set()
        for (i,s) in reg['picks']:
            f=fsp(i,s); assert f<=top,'pick frame outside top'; frames.add(f); cnt[i]+=1
        for (vi,vs,hid) in reg['kids']:
            h=pl['hubs'][hid]; ct=fsp(vi,vs) if vi>=0 else top; ht=top_of(h); assert ht==ct,'child top frame mismatch'
            frames.add(ct)
            if hid not in memo: memo[hid]=support(h,ht)
            for i,c in memo[hid].items(): cnt[i]+=c
        fl=sorted(frames,key=len)
        for a,b in zip(fl,fl[1:]): assert a<=b,'rungs not nested'
        return cnt
    used=set(); xd={i:set() for i in range(m)}; tax_y=0.0; tax_h=0.0
    def rungs(reg,top):
        fr={top}|{fsp(i,s) for (i,s) in reg['picks']}|{fsp(vi,vs) if vi>=0 else top for (vi,vs,h) in reg['kids']}
        return sorted(len(f).bit_length()-1 for f in fr)
    for j in range(m):
        O={i for i in range(m) if par(ports[i],ports[j])==0}
        c=support(pl['ys'][j],Qsp(j)); assert set(c)==O and all(v==1 for v in c.values()),'Y%d content support wrong: miss %s dup %s'%(j,sorted(O-set(c))[:5],[i for i,v in c.items() if v>1][:5])
        tax_y+=tax_chain(rungs(pl['ys'][j],Qsp(j)),False)
        stack=[pl['ys'][j]]; 
        for (i,s) in pl['ys'][j]['picks']: xd[i].add(s+1)
    for hid,h in pl['hubs'].items():
        tax_h+=tax_chain(rungs(h,top_of(h)),True)
        for (i,s) in h['picks']: xd[i].add(s+1)
    tx=sum(tax_x(xd[i]) for i in range(m))
    return dict(hubs=len(pl['hubs']),tax_y=tax_y,tax_hubs=tax_h,tax_x=tx,tax_total=tax_y+tax_h+tx)
def apply(bk,ctx):
    """frontgen hook (helpers: ladder).  bk['hub'] = dict(hubs=[dict(j)], seq=[...], info).  seq ops (emission order = ascending dim, children before parents inside a dim):
       dict(kind='pick', dst=hub idx|None, j, i, coef(Fraction), frame)  dst += coef * X_i at frame;   dict(kind='rd', dst, j, child=hub idx, coef, frame)  dst += coef * child at frame"""
    from fractions import Fraction as Q
    ports=ctx['ports']; fid=ctx['fid']; Qf=ctx['Qf']; res=ctx['res']; pl=load_plan(); assert pl['ports']==ports,'stored ladder plan is for other ports; run hubladder.solve'
    info=validate(pl,ports); flags=pl['flags']; m=len(ports)
    sgn=lambda j,i:(res[j][i]>0)-(res[j][i]<0)
    hubs=[]; hidx={}; seq=[]; height={}
    mag=lambda j,i:abs(res[j][i])
    def tmask(hid):
        h=pl['hubs'][hid]; S=set(i for i,s in h['picks'])
        for vi,vs,k in h['kids']: S|=tmask(k)
        return S
    tm={}
    def T(hid):
        if hid not in tm: tm[hid]=tmask(hid)
        return tm[hid]
    def topframe(spec,j_default=None):
        ti,ts,tj=spec; return fid(flags[ti][:ts+1]) if ti>=0 else Qf[tj]
    def emit(reg,j,regtop,reg_i0,rep_j,picks,kids,h):
        # reg: hub idx or None (Y); content sign rule: Y wants -res_ji ; hub wants -res_{rep,i}*s_rep(i0)
        for (i,s) in picks:
            coef=-res[j][i] if reg is None else -res[j][i]*sgn(j,reg_i0)
            seq.append(dict(kind='pick',dst=reg,j=j,i=i,coef=coef,frame=fid(flags[i][:s+1]),dim=s+1,h=h))
        for (vi,vs,k) in kids:
            fr=fid(flags[vi][:vs+1]) if vi>=0 else regtop; dim=(vs+1) if vi>=0 else None
            i0=min(T(k)); coef=Q(sgn(j,i0)) if reg is None else Q(sgn(j,reg_i0)*sgn(j,i0))
            seq.append(dict(kind='rd',dst=reg,j=j,child=None,childh=k,coef=coef,frame=fr,dim=dim,h=h))
    def visit(hid,j):
        if hid in hidx: return
        hidx[hid]=len(hubs); hubs.append(dict(j=j,hid=hid)); h=pl['hubs'][hid]
        for vi,vs,k in h['kids']: visit(k,j)
    for j in range(m):
        for vi,vs,k in pl['ys'][j]['kids']: visit(k,j)
    def hh(hid):
        if hid not in height: height[hid]=1+max([hh(k) for vi,vs,k in pl['hubs'][hid]['kids']]+[0])
        return height[hid]
    for hid in pl['hubs']:
        if hid not in hidx: raise AssertionError('unreachable hub')
        j=hubs[hidx[hid]]['j']; h=pl['hubs'][hid]
        emit(hidx[hid],j,topframe(h['top']),min(T(hid)),j,h['picks'],h['kids'],hh(hid))
    for j in range(m):
        y=pl['ys'][j]; emit(None,j,Qf[j],None,j,y['picks'],y['kids'],100000)
    for o in seq:
        if o['kind']=='rd': o['child']=hidx[o['childh']]
        if o['dim'] is None: o['dim']=len(ctx['frames'][o['frame']]) if 'frames' in ctx else None
    return dict(hubs=hubs,ops=[],seq=seq,info=info)
