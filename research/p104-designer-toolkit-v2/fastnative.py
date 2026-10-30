"""fastnative: bit-exact fast path for the native Gaussian-recipe pair check (tk check --native, tk accept, tk eval).

The REFERENCE is the byte-pinned PR5545 vendor pair p104-native-channel/vendor/{clifford_exact,native_verify}.py (never modified).
This module exec's an untouched copy of each into private module objects and replaces ONLY the hot pure-Python kernels with numpy versions:
  clifford_exact.Op.zero_state   dense int64 numpy state vector (permute / xor / diagonal Z4 phase / C gate); falls back to the reference
                                 kernel if any magnitude could leave int64 range
  native_verify.state            dense numpy interpreter, same dict+denominator result, same 'not injective' rejection
All control flow (lower_child, monomial, tableau, asserts, require, exception text) is the reference code, so verdicts and reasons are identical.
API mirrors infra/native_pair.py:  init(root); ok(a,b) -> (True,rank) | (False,reason).   REF=1 env or init(root,ref=True) gives the reference.
tests: tests/fastnative_test.py """
import sys,os,importlib.util,hashlib
from functools import lru_cache
import numpy as np
ROOT=None;C=V=None;REF=False
_SUB='/research/p104-native-channel/vendor/'
PINNED={'clifford_exact.py':None,'native_verify.py':None}
def _load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
_PAR={}
def _par(N):
    t=_PAR.get(N)
    if t is None:
        t=np.zeros(N,dtype=np.int64)
        for i in range(N.bit_length()-1): t^=(np.arange(N)>>i)&1
        _PAR[N]=t
    return t
def _mvtab(rows,N):
    xs=np.arange(N,dtype=np.int64);par=_par(N);out=np.zeros(N,dtype=np.int64)
    for i,r in enumerate(rows): out|=par[xs&(r&(N-1))]<<i      # r bits >= n never meet x<N
    return out
def _qtab(Q,alpha,n):
    N=1<<n;xs=np.arange(N,dtype=np.int64);par=_par(N);acc=np.zeros(N,dtype=np.int64)
    for i in range(n):
        bit=(xs>>i)&1
        acc+=bit*alpha[i]+2*bit*par[((Q[i]>>(i+1))&(N-1))&(xs>>(i+1))]
    return acc%4
_qcache={}
def qtab(Q,alpha,n):
    k=(Q,alpha,n);t=_qcache.get(k)
    if t is None:
        if len(_qcache)>4096: _qcache.clear()
        t=_qcache[k]=_qtab(Q,alpha,n)
    return t
_mcache={}
def mvtab(rows,N):
    k=(rows,N);t=_mcache.get(k)
    if t is None:
        if len(_mcache)>4096: _mcache.clear()
        t=_mcache[k]=_mvtab(rows,N)
    return t
def _rot(a,b,p):
    """multiply (a,b) by i^p elementwise, p int array in 0..3"""
    na=np.where(p==0,a,np.where(p==1,-b,np.where(p==2,-a,b)))
    nb=np.where(p==0,b,np.where(p==1,a,np.where(p==2,-b,-a)))
    return na,nb
LIM=1<<58
def make_zero_state(ref):
    def zero_state(self,basis=0):
        n=self.n;N=1<<n;a=np.zeros(N,dtype=np.int64);b=np.zeros(N,dtype=np.int64);a[basis]=1;den=0;xs=np.arange(N,dtype=np.int64)
        for e in self.circuit:
            t=e[0]
            if t=='P':
                m=mvtab(tuple(e[1]),N);na=np.zeros(N,dtype=np.int64);nb=np.zeros(N,dtype=np.int64);na[m]=a;nb[m]=b;a,b=na,nb   # repeated target: last x wins, as in the reference loop
            elif t=='X': idx=xs^e[1];a=a[idx];b=b[idx]
            elif t=='D': a,b=_rot(a,b,qtab(tuple(e[1]),tuple(e[2]),n))
            elif t=='phase': a,b=_rot(a,b,np.full(N,e[1]%4,dtype=np.int64))
            elif t=='C':
                if (np.abs(a).max()>=LIM) or (np.abs(b).max()>=LIM): return ref(self,basis)
                q,sgn=e[1:];c=a[xs^q];d=b[xs^q]
                a,b=a-sgn*b+c+sgn*d,b+sgn*a+d-sgn*c;den+=1
            else: raise AssertionError(e)
            if den:
                while den and not ((a|b)&1).any(): a=a//2;b=b//2;den-=1
        return list(zip(a.tolist(),b.tolist())),den
    return zero_state
def make_tableau(ref):
    itcache={}
    def invT(m):
        r=itcache.get(m)
        if r is None:
            if len(itcache)>4096: itcache.clear()
            r=itcache[m]=mvtab(tuple(V.transpose(V.inverse(m))),512)
        return r
    def tableau(circuit,n=9):
        circuit=tuple(circuit)
        if n!=9: return ref(circuit,n)
        for g in circuit:       # preconditions for the 512-entry tables; anything unusual -> reference
            t=g[0]
            if t=='P':
                if len(g[1])!=9 or max(g[1])>=512: return ref(circuit,n)
            elif t=='X' or t=='C':
                if not 0<=g[1]<512: return ref(circuit,n)
            elif t=='D':
                if len(g[1])!=9 or len(g[2])!=9 or max(g[1])>=512: return ref(circuit,n)
            elif t!='phase': return ref(circuit,n)
        xs=[1<<i for i in range(9)]+[0]*9;zs=[0]*9+[1<<i for i in range(9)];ps=[0]*18
        for g in circuit:
            t=g[0]
            if t=='P':
                m=mvtab(tuple(g[1]),512).tolist();mi=invT(tuple(g[1])).tolist()
                xs=[m[x] for x in xs];zs=[mi[z] for z in zs]
            elif t=='X':
                q=g[1];ps=[p+2*((z&q).bit_count()&1) for p,z in zip(ps,zs)]
            elif t=='C':
                q=g[1];s=3*g[2]
                for k in range(18):
                    if (zs[k]&q).bit_count()&1: xs[k]^=q;ps[k]+=s
            elif t=='D':
                qt=qtab(tuple(g[1]),tuple(g[2]),9).tolist();m=mvtab(tuple(g[1]),512).tolist()
                ps=[p+qt[x] for p,x in zip(ps,xs)];zs=[z^m[x] for z,x in zip(zs,xs)]
            else: ps=[p+0 for p in ps]
            ps=[p%4 for p in ps]
        return tuple(zip(xs,zs,ps))
    return tableau
def make_state(ref):
    def state(circuit,basis=0):
        N=512;a=np.zeros(N,dtype=np.int64);b=np.zeros(N,dtype=np.int64);a[basis]=1;den=0;xs=np.arange(N,dtype=np.int64)
        for gate in circuit:
            t=gate[0]
            if t=='C':
                if (np.abs(a).max()>=LIM) or (np.abs(b).max()>=LIM): return ref(circuit,basis)
                d,s=gate[1:];c=a[xs^d];e=b[xs^d]
                a,b=a-s*b+c+s*e,b+s*a+e-s*c;den+=1
            else:
                if t=='P':
                    live=((a|b)!=0).nonzero()[0];m=mvtab(tuple(gate[1]),N)[live]
                    if len(np.unique(m))!=len(m): V.require(False,'A monomial address map is not injective')
                    na=np.zeros(N,dtype=np.int64);nb=np.zeros(N,dtype=np.int64);na[m]=a[live];nb[m]=b[live];a,b=na,nb
                elif t=='X': idx=xs^gate[1];a=a[idx];b=b[idx]
                elif t=='D': a,b=_rot(a,b,qtab(tuple(gate[1]),tuple(gate[2]),9))
                else:
                    V.require(t=='phase','Unknown Gaussian state gate'); a,b=_rot(a,b,np.full(N,gate[1]%4,dtype=np.int64))
        # (reference filters zero pairs after every gate; dense zeros are equivalent)
            while den and not ((a|b)&1).any(): den-=1;a=a//2;b=b//2
        nz=((a|b)!=0).nonzero()[0]
        return {int(i):(int(a[i]),int(b[i])) for i in nz},den
    return state
def init(root,ref=None):
    global ROOT,C,V,REF
    ROOT=root;REF=bool(int(os.environ.get('TK_NATIVE_REF','0'))) if ref is None else ref
    pre='nvref' if REF else 'nvfast'
    C=_load(root+_SUB+'clifford_exact.py',pre+'_clifford');V=_load(root+_SUB+'native_verify.py',pre+'_gauss')
    if not REF:
        C.Op.zero_state=make_zero_state(C.Op.zero_state)
        V.state=make_state(V.state);V.tableau=make_tableau(V.tableau)
    chart.cache_clear();ok.cache_clear()
@lru_cache(None)
def chart(b): return C.canonical_frame(9,tuple(b))
@lru_cache(None)
def ok(a,b):
    try:
        recipe,_=C.lower_child(chart(a).adjoint().then(chart(b)))
        exp=V.adjoint(V.frame(list(a),9))+V.frame(list(b),9)
        V.equal(V.recipe(recipe),exp,'phase')
        if recipe['rank']!=abs(len(a)-len(b)): return (False,'rank %d != gap'%recipe['rank'])
        return (True,recipe['rank'])
    except Exception as e: return (False,str(e)[:80])
