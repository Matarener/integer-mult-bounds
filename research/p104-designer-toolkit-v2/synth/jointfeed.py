"""synth.jointfeed -- JOINTFEED lane (see ../module docstring).  Scope [toolkit synth, joint signal+residual feeder design].

frontgen hook `helpers: joint`.  Inputs: demand vectors + frame law + R0 law (nothing copied from a swarm word).
Kernel: ext/JOINTFEED/jf.cpp (fork of synth/mainhub.cpp; plan = kernel stdout, JOINTFEED_PLAN=<file> or data/jointfeed_plan.txt).
Design (one network for signal and residual):
  * residual + root trees + Y-Y pairs + X packets exactly as synth.mainhub (pre-root ops, ascending dim);
  * JOINT FEEDERS: a root copy u(j,k) (born 0, takes 2C_jk root_k at <l_k> AFTER the root descends) climbs through X-stop frames that hold l_k inside Q_j and on the way
    picks residual ports of Y_j and/or READS S_k-signed root-tree hubs (partial roots of its own root, already paid by the front end) whose ports are sign-consistent with Y_j;
    Y_j reads it at Q_j.  Its picks are post-root, so the kernel only lets it pick X_i at stops >= every pre-root use of X_i (X chains stay monotone, checked again here).
    Paired Ys may own feeders too (they take ports of Q_j \\ V, read after the pair mix).
  * every (j,k) WITHOUT a used feeder gets its signal from SHAREDSUM's shared relays + collector Z_j (sharedsum.plan_signal on the masked C2; cached in data/jointfeed_signal.json).
apply(bk, ctx) -> new bk (copies = feeders + relays, ysteps, hub dict with seq / post / prerestore / restore / rootreads).
"""
import os,sys,json,collections
from fractions import Fraction as Fr
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
DATA=os.path.join(HERE,'data','jointfeed_plan.txt'); SIGDATA=os.path.join(HERE,'data','jointfeed_signal.json')
par=lambda a,b:bin(a&b).count('1')%2

def validate(pl,ports,res):
    """exact structural check as mainhub.validate, with feeders allowed for paired Ys and with root trees; returns R0 by role"""
    from synth import mainhub as MHB
    G=MHB.Geo(pl,ports); m=len(ports); memo={}
    S4=MHB._S4()
    sgn=lambda j,i:((res[j][i]>0)-(res[j][i]<0)) if j<m else ((S4[j-m][i]>0)-(S4[j-m][i]<0))
    def support(reg,top,j):
        cnt=collections.Counter(); frames={top}
        for (i,ss) in reg['picks']:
            f=G.fsp(i,ss); assert f<=top,'pick frame outside top'; frames.add(f); kind,pt=G.item(i,ss)
            if kind=='packet':
                for b in pt-{i}: assert sgn(j,b)*sgn(j,i)==pl['absorb'][i][1][b],'packet sign mismatch'
            for p in pt: cnt[p]+=1
        for (vi,vs,hid) in reg['kids']:
            h=pl['hubs'][hid]; ht=G.top(h,j)
            ct=G.fsp(vi,vs) if vi>=0 else (ht if vi==-5 else top)
            assert ht==ct,'child top mismatch'; assert ct<=top
            frames.add(ct)
            k2=(hid,j)
            if k2 not in memo: memo[k2]=support(h,ht,j)[0]
            sub=memo[k2]; i0=min(sub)
            for i in sub: assert sgn(j,i)*sgn(j,i0)==sgn(hubowner[hid],i)*sgn(hubowner[hid],i0),'shared hub not sign-consistent with reader %d'%j
            for i,c in sub.items(): cnt[i]+=c
        fl=sorted(frames,key=len)
        for a_,b_ in zip(fl,fl[1:]): assert a_<=b_,'rungs not nested'
        return cnt,sorted(len(f).bit_length()-1 for f in fl)
    # hub owner = first reader in visiting order (roots first), as apply() normalises
    hubowner={}
    def own(hid,j):
        if hid in hubowner: return
        hubowner[hid]=j
        for vi,vs,k in pl['hubs'][hid]['kids']: own(k,j)
    for k,R in pl['roots'].items():
        for vi,vs,h in R['kids']: own(h,m+k)
    for j in range(m):
        for vi,vs,k in pl['ys'][j]['kids']: own(k,j)
        for cp in pl['copies'].get(j,[]):
            for vi,vs,k in cp['kids']: own(k,j)
    nfeed=0
    for j in range(m):
        O={i for i in range(m) if par(ports[i],ports[j])==0}; y=pl['ys'][j]
        c=collections.Counter()
        for cp in pl['copies'].get(j,[]):
            l=cp['line']; cc,_=support(cp,G.Qsp(j),j); nfeed+=1
            for (i,ss) in cp['picks']: assert l in G.fsp(i,ss),'feeder pick frame misses l_k'
            for (vi,vs,hid) in cp['kids']: assert vi>=0 and l in G.fsp(vi,vs),'feeder kid frame misses l_k'
            c=c+cc
        if j in pl['pairs']:
            V=G.Vsp(j); k=pl['pairs'][j]
            ag=pl['role'][j]; Tin={i for i in O if par(ports[i],ports[k])==0 and ((sgn(j,i)==sgn(k,i))==bool(ag))}
            yin=dict(picks=y['picks'],kids=[x for x in y['kids'] if x[0]!=-3]); yout=dict(picks=[],kids=[x for x in y['kids'] if x[0]==-3])
            c1,_=support(yin,V,j); c2,_=support(dict(picks=[],kids=[(-1,-1,h) for _,_,h in yout['kids']]),G.Qsp(j),j)
            need=Tin|{i for i in O if par(ports[i],ports[k])}
            c=c+c1+c2
        else:
            c2,_=support(y,G.Qsp(j),j); c=c+c2; need=O
        assert set(c)==need and all(v==1 for v in c.values()),'Y%d content support wrong: miss %s extra %s dup %s'%(j,sorted(need-set(c))[:6],sorted(set(c)-need)[:6],[i for i,v in c.items() if v>1][:6])
    for k,R in pl['roots'].items():
        H=frozenset(x for x in range(512) if par(x,R['u'])==0); need={i for i in range(m) if S4[k][i]}
        c,_=support(dict(picks=[],kids=R['kids']),H,m+k)
        assert set(c)==need and all(v==1 for v in c.values()),'root %d support wrong'%k
    return dict(feeders=nfeed,hubowner=hubowner)

def _signal(C2,line,mask):
    """SHAREDSUM signal plan on the (j,k) pairs not served by a feeder; cached by the masked code"""
    from synth import sharedsum as SSM
    Cm=[[0 if (j,k) in mask else C2[j][k] for k in range(len(C2[0]))] for j in range(len(C2))]
    if os.path.exists(SIGDATA):
        J=json.load(open(SIGDATA))
        if J.get('C2')==Cm and J.get('line')==line: return J
    J=min((SSM.plan_signal(Cm,line,seed=sd,iters=int(os.environ.get('JF_SIGITERS','60000'))) for sd in (1,2,3)),key=lambda J:J['ztax']+J['rtax']); J['C2']=Cm; J['line']=line
    json.dump(J,open(SIGDATA,'w')); return J

def apply(bk,ctx,path=None):
    from synth import mainhub as MHB, sharedsum as SSM
    ports=ctx['ports']; fid=ctx['fid']; Qf=ctx['Qf']; res=ctx['res']; line=ctx['line']; F0=ctx['F0']; F9=ctx['F9']; C2=ctx['C2']
    pl=MHB.load_plan(path or os.environ.get('JOINTFEED_PLAN',DATA)); m=len(ports); G=MHB.Geo(pl,ports)
    V=validate(pl,ports,res); hubowner=V['hubowner']; fl=pl['flags']
    S4=MHB._S4()
    U=lambda r,i:((res[r][i]<0)-(res[r][i]>0)) if r<m else ((S4[r-m][i]>0)-(S4[r-m][i]<0))
    fr=lambda i,ss:fid(fl[i][:ss+1])
    kof={l:k for k,l in enumerate(line)}
    feeders=[(j,cp) for j in range(m) for cp in pl['copies'].get(j,[])]
    mask={(j,kof[cp['line']]) for j,cp in feeders}
    copies=[]; cmap={}
    for (j,cp) in feeders:
        k=kof[cp['line']]; cmap[(j,k)]=len(copies); copies.append(dict(k=k,cin=Fr(2*C2[j][k])))
    hubs=[]; hidx={}; seq=[]; post=[]; restore_rd=[]; restore_pk=[]; height={}
    tm={}
    def T(hid):
        if hid not in tm:
            h=pl['hubs'][hid]; S=set()
            for i,ss in h['picks']: S|=G.item(i,ss)[1]
            for vi,vs,k in h['kids']: S|=T(k)
            tm[hid]=S
        return tm[hid]
    def hh(hid):
        if hid not in height: height[hid]=1+max([hh(k) for vi,vs,k in pl['hubs'][hid]['kids']]+[0])
        return height[hid]
    def frame_of_kid(vi,vs,k,regtop):
        if vi>=0: return fr(vi,vs),vs+1
        h=pl['hubs'][k]
        if vi==-5: f=G.top(h,0); return fid(sorted(f-{0})),len(f).bit_length()-1
        return regtop
    xmax=collections.defaultdict(int); xmin_post=collections.defaultdict(lambda:99)
    def emit(dst,j,scale,regtop,picks,kids,hgt,restore,out):
        for (i,ss) in picks:
            kind,pt=G.item(i,ss); c=scale*U(j,i); f=fr(i,ss)
            out.append(dict(kind='g',dst=dst,src=('X',i),coef=c,frame=f,dim=ss+1,h=hgt))
            srcs=[i]+([b for b in pl['absorb'][i][1]] if kind=='transp' else [])
            for b in srcs:
                if out is post: xmin_post[b]=min(xmin_post[b],ss)
                else: xmax[b]=max(xmax[b],ss)
            if kind=='transp':
                for b,sg in pl['absorb'][i][1].items(): out.append(dict(kind='g',dst=dst,src=('X',b),coef=-c*sg,frame=f,dim=ss+1,h=hgt))
            if restore:
                restore_pk.append(dict(dst=dst,src=('X',i),coef=-c,frame=F9))
                if kind=='packet': [restore_pk.append(dict(dst=dst,src=('X',b),coef=-c*sg,frame=F9)) for b,sg in pl['absorb'][i][1].items()]
        for (vi,vs,k) in kids:
            f,d=frame_of_kid(vi,vs,k,regtop); i0=min(T(k)); c=scale*U(j,i0)
            out.append(dict(kind='g',dst=dst,src=('H',hidx[k]),coef=c,frame=f,dim=d,h=hgt))
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
        j=hubs[hidx[hid]]['j']; assert j==hubowner[hid]; i0=min(T(hid)); top=G.top(h,j)
        emit(('H',hidx[hid]),j,U(j,i0),(fid(sorted(top-{0})),len(top).bit_length()-1),h['picks'],h['kids'],hh(hid),True,seq)
    for j in range(m):
        y=pl['ys'][j]
        if j in pl['pairs']:
            k=pl['pairs'][j]; Vs=G.Vsp(j); Vf=(fid(sorted(Vs-{0})),7)
            sc=Fr(1,2) if pl['role'][j] else Fr(1)
            emit(('Y',j),j,sc,Vf,y['picks'],[x for x in y['kids'] if x[0]!=-3],100000,False,seq)
            emit(('Y',j),j,Fr(1,2),(Qf[j],8),[],[(-1,-1,h) for _,_,h in y['kids'] if _==-3],100000,False,seq)
            if pl['role'][j]:
                seq.append(dict(kind='g',dst=('Y',j),src=('Y',k),coef=Fr(-1,2),frame=Vf[0],dim=7,h=10**6))
                seq.append(dict(kind='g',dst=('Y',k),src=('Y',j),coef=Fr(1),frame=Vf[0],dim=7,h=10**6+1))
        else:
            emit(('Y',j),j,Fr(1,2),(Qf[j],8),y['picks'],y['kids'],100000,False,seq)
        for cp in pl['copies'].get(j,[]):      # JOINT FEEDER (post-root): content cin*root_k + (1/2) sum U(j,i) x_i over its ports; Y_j reads it with coefficient 1
            ci=cmap[(j,kof[cp['line']])]
            emit(('C',ci),j,Fr(1,2),(Qf[j],8),cp['picks'],cp['kids'],100000,True,post)
    for b in list(xmin_post):
        assert xmin_post[b]>=xmax[b],'X%d: post-root pick at stop %d below a pre-root use at stop %d (chain would descend)'%(b,xmin_post[b],xmax[b])
    pre=[]
    for j in range(m):
        if j in pl['pairs'] and pl['role'][j]:
            k=pl['pairs'][j]
            pre.append(dict(dst=('Y',k),src=('Y',j),coef=Fr(-1),frame=F0)); pre.append(dict(dst=('Y',j),src=('Y',k),coef=Fr(1,2),frame=F0))
    for a,(sa,sig) in pl['absorb'].items():
        for b,sg in sig.items(): seq.append(dict(kind='g',dst=('X',a),src=('X',b),coef=Fr(sg),frame=fr(a,sa),dim=sa+1,h=-1))
    xundo=[dict(dst=('X',a),src=('X',b),coef=Fr(-sg),frame=F9) for a,(sa,sig) in sorted(pl['absorb'].items(),key=lambda t:-t[1][0]) for b,sg in sig.items()]
    restore=xundo+[o for _,o in sorted(restore_rd,key=lambda t:-t[0])]+restore_pk
    for o in seq+post+restore: o['coef']=Fr(o['coef'])
    rootreads={k:[(('H',hidx[h]),Fr(1,4)*U(m+k,min(T(h)))) for vi,vs,h in R['kids']] for k,R in pl['roots'].items()}
    # ---- signal for the (j,k) pairs without a feeder: SHAREDSUM relays + collectors (only for Ys with something left)
    SG=_signal(C2,line,mask)
    nrel0=len(copies); where={}
    for ri,(k,ch) in enumerate(SG['relays']):
        copies.append(dict(k=k,cin=Fr(1)))
        for S in ch: where[(k,frozenset(S))]=nrel0+ri
    prer=[]; nZ=0
    for j,o in enumerate(SG['orders']):
        if not o: continue
        z=len(hubs); hubs.append(dict(j=j,hid=('Z',j))); nZ+=1
        S=frozenset()
        for g in SSM._steps(o,SG['cuts'][j]):
            S=S|set(g); f=fid([line[s] for s in sorted(S)]); d=SSM._rank([line[s] for s in S])
            for k in g:
                c=Fr(2*C2[j][k])
                post.append(dict(kind='g',dst=('H',z),src=('C',where[(k,S)]),coef=c,frame=f,dim=d,h=0))
                prer.append(dict(dst=('H',z),src=('C',where[(k,S)]),coef=-c,frame=F9))
        post.append(dict(kind='g',dst=('Y',j),src=('H',z),coef=Fr(1),frame=Qf[j],dim=8,h=1))
    ysteps={j:[(Qf[j],[(cmap[(j,kof[cp['line']])],Fr(1)) for cp in pl['copies'].get(j,[])],[])] for j in range(m)}
    info=dict(hubs=len(pl['hubs']),feeders=len(feeders),feeder_picks=sum(len(cp['picks']) for _,cp in feeders),
              feeder_hub_reads=sum(len(cp['kids']) for _,cp in feeders),feeder_roottree_reads=sum(1 for _,cp in feeders for (vi,vs,h) in cp['kids'] if hubowner[h]>=m),
              signal_relays=len(SG['relays']),signal_Z=nZ,model_ztax=SG['ztax'],model_relay_tax=SG['rtax'],pairs=len(pl['pairs'])//2,absorbers=len(pl['absorb']),plan_E=pl['E'])
    hub=dict(hubs=hubs,ops=[],seq=seq,post=post,pre=pre,prerestore=prer,restore=restore,info=info,rootreads=rootreads)
    b2=dict(bk); b2['rcar']=[]; b2['hub']=hub; b2['copies']=copies; b2['ysteps']=ysteps
    return b2
