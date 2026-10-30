"""S10 exact-certified branch and bound (v4) for one case of the S9 lifted relaxation (model.py).
max g.x s.t. A x <= b, 0 <= x <= up integer; prove max < target.  Certificate = leaves (path, y), verified by ecert.py.
Node processing:  LP (HiGHS dual simplex, warm) -> dyadic dual y -> exact bound S(y, box); prune if S < target.
Otherwise (a) reduced-cost tightening with y; (b) PROBING: for the deficient column j with largest LP value solve the LP
with x_j >= 1; if that is pruned by dual y_j, the column is fixed to 0 by a certified tightening step with y_j (and with
the images of y_j under the stabilizer of the case's fixed type t1, which permute rows/columns of the model); (c) else branch.
argv: c cm case [maxnodes] [out.pkl]"""
import pickle, sys, time, os, numpy as np, highspy
from model import build, data
SC=1<<24
SYM=os.environ.get('SYM','1')=='1'
def stabilizer(case,meta,nc):
    """row perms (640 cliques + e-row) and column perms of the stabilizer of t1's miss set; identity first"""
    D=data(); T,dom=D['T'],D['dom']; G=pickle.load(open('orbits.pkl','rb'))['G']; Cp=dom['Cperm']
    r=dom['reps'][case]; m=T[r][4]; cols=meta['cols']
    key={(int(T[i][2]),T[i][4].tobytes()):k for k,i in enumerate(cols)}
    out=[]
    for p in range(len(G)):
        cp=Cp[p]
        if not (m[np.argsort(cp)]==m).all(): continue      # image of miss set = m  <=> m[cp^-1] == m
        rowp=np.concatenate([cp,[640]])
        colp=np.empty(nc,np.int64); colp[:60]=np.array(G[p])
        for k,i in enumerate(cols):
            mm=np.zeros(640,bool); mm[cp[np.nonzero(T[i][4])[0]]]=True
            colp[60+k]=60+key[(int(T[i][2]),mm.tobytes())]
        out.append((rowp,colp))
    return out
def solve(c,cm,case,maxnodes=10**7,out=None,log=True):
    A,b,g,up,target,meta=build(c,cm,case)
    nr,nc=A.shape; AT=A.T.tocsr(); TS=target*SC
    sym=stabilizer(case,meta,nc) if (SYM and case>=0) else []
    if log: print('  stabilizer order',len(sym),flush=True)
    h=highspy.Highs(); h.setOptionValue('output_flag',False); h.setOptionValue('threads',1)
    lp=highspy.HighsLp(); lp.num_col_=nc; lp.num_row_=nr
    lp.col_cost_=-g.astype(float); lp.col_lower_=np.zeros(nc); lp.col_upper_=up.astype(float)
    lp.row_lower_=np.full(nr,-highspy.kHighsInf); lp.row_upper_=b.astype(float)
    Ac=A.tocsc(); lp.a_matrix_.format_=highspy.MatrixFormat.kColwise; lp.a_matrix_.start_=Ac.indptr; lp.a_matrix_.index_=Ac.indices; lp.a_matrix_.value_=Ac.data.astype(float)
    h.passModel(lp); idx=np.arange(nc,dtype=np.int32)
    def S(y,lo,hi):
        d=g*SC-AT.dot(y); return int(y.dot(b))+int(np.maximum(d*lo,d*hi).sum()),d
    def lpdual(lo,hi):
        h.changeColsBounds(nc,idx,lo.astype(float),hi.astype(float)); h.run()
        if h.getModelStatus()==highspy.HighsModelStatus.kInfeasible:
            ok,ray=h.getDualRay(); ray=np.maximum(-np.array(ray),0); ray=ray/ray.max()
            for sc in (1e6,1e9,1e12):
                y=np.floor(ray*SC*sc).astype(np.int64); s,_=S(y,lo,hi)
                if s<TS: return y,None
            raise RuntimeError('farkas fail')
        sol=h.getSolution(); return np.floor(np.maximum(-np.array(sol.row_dual),0)*SC).astype(np.int64),np.array(sol.col_value)
    def tighten(y,lo,hi):
        s,d=S(y,lo,hi); gap=s-TS
        if gap<0: return None
        free=hi>lo; ch=[]
        neg=np.nonzero(free&(d<0))[0]; nh=lo[neg]+gap//(-d[neg]); sel=nh<hi[neg]
        pos=np.nonzero(free&(d>0))[0]; nl=hi[pos]-gap//d[pos]; sel2=nl>lo[pos]
        for j,v in zip(neg[sel],nh[sel]): hi[j]=v; ch.append((int(j),int(lo[j]),int(v)))
        for j,v in zip(pos[sel2],nl[sel2]): lo[j]=v; ch.append((int(j),int(v),int(hi[j])))
        return ch
    leaves=[]; stack=[(np.zeros(nc,np.int64),up.astype(np.int64).copy(),())]
    st=dict(nodes=0,lps=0,probes=0,probe_fix=0,tight=0); t0=time.time(); found=None
    while stack:
        lo,hi,path=stack.pop(); st['nodes']+=1
        if st['nodes']>maxnodes: return dict(status='NODELIMIT',stats=st,meta=meta)
        y,x=lpdual(lo,hi); st['lps']+=1
        s,_=S(y,lo,hi)
        if s<TS: leaves.append((path,y)); continue
        lo=lo.copy(); hi=hi.copy()
        ch=tighten(y,lo,hi)
        if ch: path=path+(('T',y,tuple(ch)),); st['tight']+=len(ch)
        # probing on deficient columns
        nd=np.nonzero((x[60:]>1e-6)&(hi[60:]>lo[60:])&(lo[60:]==0))[0]+60
        probed=False
        if len(nd):
            j=int(nd[np.argmax(x[nd])]); lo1=lo.copy(); lo1[j]=1
            yj,_=lpdual(lo1,hi); st['lps']+=1; st['probes']+=1
            sj,_=S(yj,lo1,hi)
            if sj<TS:
                ims=[yj]
                for rowp,colp in (sym[1:] if sym else []):
                    yy=np.empty_like(yj); yy[rowp]=yj; ims.append(yy)
                for yy in ims:
                    ch=tighten(yy,lo,hi)
                    if ch: path=path+(('T',yy,tuple(ch)),); st['probe_fix']+=len(ch)
                assert hi[j]==0
                stack.append((lo,hi,path)); probed=True
        if probed: continue
        frac=np.abs(x-np.round(x))
        if frac.max()<1e-6:
            xi=np.round(x).astype(np.int64)
            if g.dot(xi)>=target and (A.dot(xi)<=b).all(): found=xi; break
            raise RuntimeError('integral LP with bound >= target but gain %s'%g.dot(xi))
        cand=np.nonzero(frac>1e-6)[0]; ndc=cand[cand>=60]
        j=int(ndc[np.argmax(frac[ndc])]) if len(ndc) else int(cand[np.argmax(frac[cand])])
        v=int(np.floor(x[j])); lo2=lo.copy(); lo2[j]=v+1; hi2=hi.copy(); hi2[j]=v
        stack.append((lo,hi2,path+((j,'<=',v),))); stack.append((lo2,hi,path+((j,'>=',v+1),)))
        if log and st['nodes']%200==0: print('  ',st,'leaves',len(leaves),'stack',len(stack),'free n',int((hi[60:]>0).sum()),'%.0fs'%(time.time()-t0),flush=True)
    res=dict(status='FEASIBLE' if found is not None else 'EXCLUDED',stats=st,leaves=leaves,x=found,meta=meta,time=time.time()-t0)
    if out: pickle.dump(res,open(out,'wb'))
    return res
if __name__=='__main__':
    c,cm,case=map(int,sys.argv[1:4]); mx=int(sys.argv[4]) if len(sys.argv)>4 else 10**7
    out=sys.argv[5] if len(sys.argv)>5 else 'certs/cert_%d_%d_%d.pkl'%(c,cm,case)
    r=solve(c,cm,case,mx,out)
    print('EBB4 c=%d cost<=%d case %d -> %s %s leaves %s %.0fs'%(c,cm,case,r['status'],r['stats'],len(r.get('leaves',[])),r.get('time',0)),flush=True)
