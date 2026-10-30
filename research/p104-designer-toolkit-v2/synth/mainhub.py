"""synth.mainhub -- MAINS AS HUBS (MAINHUB, see ../module docstring).  Scope [toolkit synth, joint main+helper network design with mains as hubs].

Extends synth.hubladder (hub-hub merge ladders, shared hubs; kernel synth/mainhub.cpp) with three ways for MAIN registers to host meetings:
  X packets   X_a absorbs co-present X_b (same flag frame, stop sa) with signs sig: readers of X_a at stops >= sa get x_a + sum sig_b x_b in one pick
              (or, where every source is still co-present and clean, read X_a - sum sig X_b = x_a: 'transparent').  Undone at F9 in reverse stop order.
  Y-Y pairs   Y_j (agree collector) and Y_k meet at V = Q_j cap Q_k (dim 7): Y_j += -1/2 Y_k ; Y_k += Y_j.  The inverse is applied to the y's at frame 0 (all Y co-present there).
  root copies the back-end copy u(j,k) (born 0, takes 2C_jk root_k at <l_k>, read by Y_j at Q_j) climbs through frames containing l_k and picks residual ports / reads hubs for Y_j.
plan text format (kernel stdout): E, P j k role, A a s b:sig.., Q i flags, H id top ti ts tj tb k basis.. T hi lo picks i:s.. kids vi:vs:id.., C j l picks.. kids.., Y j picks.. kids..
"""
import os,sys,json,math,subprocess,tempfile,hashlib,collections
from fractions import Fraction as Fr
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
DATA=os.path.join(HERE,'data','mainhub_plan.txt')
par=lambda a,b:bin(a&b).count('1')%2
def _H(r): return r*math.log(r) if r>0 else 0.0
def span(vs):
    s={0}
    for v in vs: s|={x^v for x in s}
    return frozenset(s)
def tax_chain(ds,hub):
    prev=0; t=_H(9 if hub else 8)
    for d in ds: t-=_H(d-prev); prev=d
    return t-(_H(9-prev) if hub else 0)
def kernel_binary():
    src=os.path.join(HERE,'mainhub.cpp')
    exe=os.path.join(tempfile.gettempdir(),'mainhub_%s'%hashlib.md5(open(src,'rb').read()).hexdigest()[:8])
    if not os.path.exists(exe): subprocess.check_call(['c++','-O2','-std=c++17','-o',exe,src])
    return exe
def parse_output(text):
    pl=dict(E=None,pairs={},role={},absorb={},flags={},hubs={},copies={},ys={},roots={})
    kid=lambda t:[tuple(int(y) for y in x.split(':')) for x in t]
    for ln in text.splitlines():
        t=ln.split()
        if not t: continue
        if t[0]=='E': pl['E']=float(t[1])
        elif t[0]=='P':
            j,k,r=map(int,t[1:4]); pl['pairs'][j]=k; pl['pairs'][k]=j; pl['role'][j]=r; pl['role'][k]=1-r
        elif t[0]=='A': pl['absorb'][int(t[1])]=(int(t[2]),{int(x.split(':')[0]):int(x.split(':')[1]) for x in t[3:]})
        elif t[0]=='Q': pl['flags'][int(t[1])]=[int(x) for x in t[2:]]
        elif t[0]=='H':
            nb=int(t[7]); tb=[int(x) for x in t[8:8+nb]]; k=t.index('picks'); kk=t.index('kids')
            pl['hubs'][int(t[1])]=dict(top=(int(t[3]),int(t[4]),int(t[5])),tb=tb,picks=kid(t[k+1:kk]),kids=kid(t[kk+1:]))
        elif t[0]=='C':
            k=t.index('picks'); kk=t.index('kids'); pl['copies'].setdefault(int(t[1]),[]).append(dict(line=int(t[2]),picks=kid(t[k+1:kk]),kids=kid(t[kk+1:])))
        elif t[0]=='R':
            kk=t.index('kids'); pl['roots'][int(t[1])]=dict(u=int(t[2]),kids=kid(t[kk+1:]))
        elif t[0]=='Y':
            k=t.index('picks'); kk=t.index('kids'); pl['ys'][int(t[1])]=dict(picks=kid(t[k+1:kk]),kids=kid(t[kk+1:]))
    return pl
def load_plan(path=DATA): return parse_output(open(path).read())
class Geo:
    """frames and packet semantics of a plan"""
    def __init__(s,pl,ports):
        s.pl=pl; s.P=ports; s.m=len(ports); s.fl=pl['flags']; s._f={}
    def fsp(s,i,ss):
        k=(i,ss)
        if k not in s._f: s._f[k]=span(s.fl[i][:ss+1])
        return s._f[k]
    def Qsp(s,j): return frozenset(x for x in range(512) if par(x,s.P[j])==0)
    def Vsp(s,j): k=s.pl['pairs'][j]; return frozenset(x for x in range(512) if par(x,s.P[j])==0 and par(x,s.P[k])==0)
    def top(s,h,j):
        ti,ts,tj=h['top']
        if ti>=0: return s.fsp(ti,ts)
        if ti==-1: return s.Qsp(tj)
        if ti==-2: return frozenset(x for x in range(512) if par(x,s.P[tj])==0 and par(x,s.P[ts])==0)
        if ti==-5: return span(h['tb'])
        if ti==-7: return frozenset(x for x in range(512) if par(x,ts)==0)
        raise ValueError(h['top'])
    def item(s,a,ss):
        """(kind, ports) of a pick of X_a at stop ss: 'single' | 'packet' | 'transp' (read X_a - sum sig X_b)"""
        A=s.pl['absorb'].get(a)
        if A is None or ss<A[0]: return 'single',{a}
        sa,sig=A
        if all(s.fsp(b,ss)==s.fsp(a,ss) and (b not in s.pl['absorb'] or s.pl['absorb'][b][0]>ss) for b in sig): return 'transp',{a}
        return 'packet',{a}|set(sig)
def _S4():
    from synth import frontgen as FG
    return FG.load_code()[0]
def validate(pl,ports,lines=None,res=None):
    """exact structural check (supports, frames nested inside tops, packet sign consistency) + R0 tax by role; asserts on failure."""
    G=Geo(pl,ports); m=len(ports); memo={}
    for i in range(m): assert pl['flags'][i][0]==ports[i]
    for a,(sa,sig) in pl['absorb'].items():
        for b in sig: assert G.fsp(b,sa)==G.fsp(a,sa),'absorb source not co-framed'; assert b not in pl['absorb'] or pl['absorb'][b][0]>sa,'source dirty'
        for c,(sc,sg2) in pl['absorb'].items():
            if a in sg2: assert sa>sc,'absorber is an earlier dirty source'
    S4=_S4() if pl['roots'] else None
    sgn=lambda j,i:((res[j][i]>0)-(res[j][i]<0)) if j<m else ((S4[j-m][i]>0)-(S4[j-m][i]<0))
    xstops={i:set() for i in range(m)}
    for a,(sa,sig) in pl['absorb'].items():
        xstops[a].add(sa)
        for b in sig: xstops[b].add(sa)
    def support(reg,top,j,key=None):
        cnt=collections.Counter(); frames={top}
        for (i,ss) in reg['picks']:
            f=G.fsp(i,ss); assert f<=top,'pick frame outside top'; frames.add(f); kind,pt=G.item(i,ss); xstops[i].add(ss)
            if kind=='transp': [xstops[b].add(ss) for b in pl['absorb'][i][1]]
            if kind=='packet' and (res is not None or j>=m):
                for b in pt-{i}: assert sgn(j,b)*sgn(j,i)==pl['absorb'][i][1][b],'packet sign mismatch'
            for p in pt: cnt[p]+=1
        for (vi,vs,hid) in reg['kids']:
            h=pl['hubs'][hid]; ht=G.top(h,j)
            ct=G.fsp(vi,vs) if vi>=0 else (ht if vi==-5 else top)
            assert ht==ct,'child top mismatch'; assert ct<=top
            frames.add(ct)
            k2=(hid,j if res is not None else 0)
            if k2 not in memo: memo[k2]=support(h,ht,j)[0]
            for i,c in memo[k2].items(): cnt[i]+=c
        fl=sorted(frames,key=len)
        for a_,b_ in zip(fl,fl[1:]): assert a_<=b_,'rungs not nested'
        return cnt,sorted(len(f).bit_length()-1 for f in fl)
    tax_y=0.0; tax_c=0.0; ncopy=0
    for j in range(m):
        O={i for i in range(m) if par(ports[i],ports[j])==0}; y=pl['ys'][j]
        if j in pl['pairs']:
            V=G.Vsp(j); k=pl['pairs'][j]
            ag=pl['role'][j]; Tin={i for i in O if par(ports[i],ports[k])==0 and ((sgn(j,i)==sgn(k,i))==bool(ag))}
            yin=dict(picks=y['picks'],kids=[x for x in y['kids'] if x[0]!=-3]); yout=dict(picks=[],kids=[x for x in y['kids'] if x[0]==-3])
            c1,r1=support(yin,V,j); c2,_=support(dict(picks=[],kids=[(-1,-1,h) for _,_,h in yout['kids']]),G.Qsp(j),j)
            need=Tin|{i for i in O if par(ports[i],ports[k])}
            c=c1+c2; rd=sorted(set(r1)|{7,8})
        else:
            c,rd=support(y,G.Qsp(j),j)
            for cp in pl['copies'].get(j,[]):
                l=cp['line']; cc,rc=support(cp,G.Qsp(j),j)
                for (i,ss) in cp['picks']: assert l in G.fsp(i,ss),'copy pick frame misses l_k'
                for (vi,vs,hid) in cp['kids']: assert vi>=0 and l in G.fsp(vi,vs),'copy kid frame misses l_k'
                c=c+cc; tax_c+=tax_chain([1]+[d for d in rc],True)-tax_chain([1,8],True); ncopy+=1
            need=O
        assert set(c)==need and all(v==1 for v in c.values()),'Y%d content support wrong: miss %s extra %s dup %s'%(j,sorted(need-set(c))[:6],sorted(set(c)-need)[:6],[i for i,v in c.items() if v>1][:6])
        tax_y+=tax_chain(rd,False)
    for k,R in pl['roots'].items():
        H=frozenset(x for x in range(512) if par(x,R['u'])==0); need={i for i in range(m) if S4[k][i]}
        c,_=support(dict(picks=[],kids=R['kids']),H,m+k)
        assert set(c)==need and all(v==1 for v in c.values()),'root %d support wrong'%k
    tax_h=0.0
    for hid,h in pl['hubs'].items():
        # rungs from any reader: top + pick frames + kid tops
        j=None
        top=G.top(h,0) if h['top'][0] in (-5,-7) or h['top'][0]>=0 else G.top(h,h['top'][2])
        fr={top}|{G.fsp(i,ss) for (i,ss) in h['picks']}|{(G.fsp(vi,vs) if vi>=0 else (G.top(pl['hubs'][k],0) if vi==-5 else top)) for (vi,vs,k) in h['kids']}
        tax_h+=tax_chain(sorted(len(f).bit_length()-1 for f in fr),True)
    def tax_x(st):
        prev=1; t=_H(8)
        for ss in sorted(st):
            d=ss+1
            if d>1: t-=_H(d-prev); prev=d
        return t-_H(9-prev)
    tx=sum(tax_x(xstops[i]) for i in range(m))
    return dict(hubs=len(pl['hubs']),tax_y=tax_y,tax_hubs=tax_h,tax_x=tx,tax_copies=tax_c,copies_used=ncopy,tax_total=tax_y+tax_h+tx+tax_c,
                roots_as_trees=len(pl['roots']),pairs=len(pl['pairs'])//2,absorbers=len(pl['absorb']),packet_ports=sum(len(v[1]) for v in pl['absorb'].values()))
def apply(bk,ctx,path=None):
    """frontgen hook (helpers: mainhub).  Returns dict(hubs, ops=[], seq=[kind 'g' ops], pre=[F0 ops], restore=[F9 ops], info).
    register refs: ('Y',j) ('X',i) ('H',hub idx) ('C',copy idx)."""
    ports=ctx['ports']; fid=ctx['fid']; Qf=ctx['Qf']; res=ctx['res']; line=ctx['line']; F0=ctx['F0']; F9=ctx['F9']
    pl=load_plan(path or os.environ.get('MAINHUB_PLAN',DATA)); m=len(ports); G=Geo(pl,ports)
    info=validate(pl,ports,res=res); fl=pl['flags']
    S4=_S4() if pl['roots'] else None
    U=lambda r,i:((res[r][i]<0)-(res[r][i]>0)) if r<m else ((S4[r-m][i]>0)-(S4[r-m][i]<0))   # unit target sign of reader r (Y: -res, root: S4)
    fr=lambda i,ss:fid(fl[i][:ss+1])
    # copies of the star back end: (j,k) -> (copy index, Y coefficient)
    kof={l:k for k,l in enumerate(line)}; cmap={}
    for j,st in bk['ysteps'].items():
        for (f,cr,rr) in st:
            for ci,cf in cr: cmap[(j,bk['copies'][ci]['k'])]=(ci,Fr(cf))
    hubs=[]; hidx={}; seq=[]; restore_rd=[]; restore_pk=[]; height={}
    def tmask(hid,seen=None):
        h=pl['hubs'][hid]; S=set()
        for i,ss in h['picks']: S|=G.item(i,ss)[1]
        for vi,vs,k in h['kids']: S|=tmask(k)
        return S
    tm={}
    def T(hid):
        if hid not in tm: tm[hid]=tmask(hid)
        return tm[hid]
    def hh(hid):
        if hid not in height: height[hid]=1+max([hh(k) for vi,vs,k in pl['hubs'][hid]['kids']]+[0])
        return height[hid]
    def frame_of_kid(vi,vs,k,regtop):
        if vi>=0: return fr(vi,vs),vs+1
        h=pl['hubs'][k]
        if vi==-5: f=G.top(h,0); return fid(sorted(f-{0})),len(f).bit_length()-1
        return regtop
    def emit(dst,j,scale,regtop,picks,kids,hgt,restore):
        """dst register ref; its content must equal scale * sum_{ports} U(j,i) x_i (hub: scale U(j,i0) = unit normalised; Y 1/2; pair disagree collector 1; copy 1/(2cf); root 1/4)"""
        for (i,ss) in picks:
            kind,pt=G.item(i,ss); c=scale*U(j,i); f=fr(i,ss)
            seq.append(dict(kind='g',dst=dst,src=('X',i),coef=c,frame=f,dim=ss+1,h=hgt))
            if kind=='transp':
                for b,sg in pl['absorb'][i][1].items(): seq.append(dict(kind='g',dst=dst,src=('X',b),coef=-c*sg,frame=f,dim=ss+1,h=hgt))
            if restore:
                if kind=='single': restore_pk.append(dict(dst=dst,src=('X',i),coef=-c,frame=F9))
                elif kind=='transp': restore_pk.append(dict(dst=dst,src=('X',i),coef=-c,frame=F9))   # content gained is c*x_a only; X clean at F9
                else: restore_pk.append(dict(dst=dst,src=('X',i),coef=-c,frame=F9)); [restore_pk.append(dict(dst=dst,src=('X',b),coef=-c*sg,frame=F9)) for b,sg in pl['absorb'][i][1].items()]
        for (vi,vs,k) in kids:
            f,d=frame_of_kid(vi,vs,k,regtop); i0=min(T(k)); c=scale*U(j,i0)   # child content = U(j,i0) * sum U(j,i) x_i (unit)
            seq.append(dict(kind='g',dst=dst,src=('H',hidx[k]),coef=c,frame=f,dim=d,h=hgt))
            if restore: restore_rd.append((hgt,dict(dst=dst,src=('H',hidx[k]),coef=-c,frame=F9)))
    def visit(hid,j):
        if hid in hidx: return
        for vi,vs,k in pl['hubs'][hid]['kids']: visit(k,j)
        hidx[hid]=len(hubs); hubs.append(dict(j=j,hid=hid))
    for k,R in pl['roots'].items():
        for vi,vs,h in R['kids']: visit(h,m+k)
    for j in range(m):
        for vi,vs,k in pl['ys'][j]['kids']: visit(k,j)
        for cp in pl['copies'].get(j,[]):
            for vi,vs,k in cp['kids']: visit(k,j)
    for hid in pl['hubs']: assert hid in hidx,'unreachable hub'
    for hid,h in pl['hubs'].items():
        j=hubs[hidx[hid]]['j']; i0=min(T(hid)); top=G.top(h,j)
        emit(('H',hidx[hid]),j,U(j,i0),(fid(sorted(top-{0})),len(top).bit_length()-1),h['picks'],h['kids'],hh(hid),True)
    for j in range(m):
        y=pl['ys'][j]
        if j in pl['pairs']:
            k=pl['pairs'][j]; V=G.Vsp(j); Vf=(fid(sorted(V-{0})),7)
            sc=Fr(1,2) if pl['role'][j] else Fr(1)          # agree collector holds c_j on agree ports; the other holds 2 c_k on disagree ports
            emit(('Y',j),j,sc,Vf,y['picks'],[x for x in y['kids'] if x[0]!=-3],100000,False)
            emit(('Y',j),j,Fr(1,2),(Qf[j],8),[],[(-1,-1,h) for _,_,h in y['kids'] if _==-3],100000,False)
            if pl['role'][j]:   # j = agree collector: forward mix at V after all dim<=7 reads, inverse at frame 0
                seq.append(dict(kind='g',dst=('Y',j),src=('Y',k),coef=Fr(-1,2),frame=Vf[0],dim=7,h=10**6))
                seq.append(dict(kind='g',dst=('Y',k),src=('Y',j),coef=Fr(1),frame=Vf[0],dim=7,h=10**6+1))
        else:
            emit(('Y',j),j,Fr(1,2),(Qf[j],8),y['picks'],y['kids'],100000,False)
            for cp in pl['copies'].get(j,[]):
                ci,cf=cmap[(j,kof[cp['line']])]
                emit(('C',ci),j,Fr(1,2)/cf,(Qf[j],8),cp['picks'],cp['kids'],100000,True)
    pre=[]
    for j in range(m):
        if j in pl['pairs'] and pl['role'][j]:
            k=pl['pairs'][j]
            pre.append(dict(dst=('Y',k),src=('Y',j),coef=Fr(-1),frame=F0)); pre.append(dict(dst=('Y',j),src=('Y',k),coef=Fr(1,2),frame=F0))
    for a,(sa,sig) in pl['absorb'].items():
        for b,sg in sig.items(): seq.append(dict(kind='g',dst=('X',a),src=('X',b),coef=Fr(sg),frame=fr(a,sa),dim=sa+1,h=-1))
    xundo=[dict(dst=('X',a),src=('X',b),coef=Fr(-sg),frame=F9) for a,(sa,sig) in sorted(pl['absorb'].items(),key=lambda t:-t[1][0]) for b,sg in sig.items()]
    restore=xundo+[o for _,o in sorted(restore_rd,key=lambda t:-t[0])]+restore_pk
    for o in seq: o['coef']=Fr(o['coef'])
    for o in restore: o['coef']=Fr(o['coef'])
    rootreads=None
    assert not (pl['roots'] and any(pl['copies'].values())),'root trees run every hub op before the roots: copy carriers (picks after the root read) are not allowed'
    if pl['roots']:   # root k reads its S_k-signed trees at H_k: R_k = sum S4/4 x = 1/4 * sum U x
        rootreads={k:[(('H',hidx[h]),Fr(1,4)*U(m+k,min(T(h)))) for vi,vs,h in R['kids']] for k,R in pl['roots'].items()}
    return dict(hubs=hubs,ops=[],seq=seq,pre=pre,restore=restore,info=info,rootreads=rootreads)
