"""bitword: BIT-side (G20 local word) model for the toolkit.  [BITADAPT]  Profile-driven (profiles/bit<PR>.json kind=bit).
Word = {start,final: frame id per register (None allowed), records: ADD d s f | Q d s t k | ZERO_Q d s t k | ERASE d f | INIT d f, owned: ids}.
Frame law differs from the P104 complex side: fixed catalogue of exact-QQ frames (dims 0..8); ADD needs st[d]==st[s]==f; Q needs exact QQ nesting and k = dim gap, 0<k<8;
Q events are DERIVED from the scalar program + frame labels via PATHS (construct.emit of the PR), exactly like MOVE re-insertion on the complex side.
check(word)  : fast in-process oracle with localisation (rows over GF(2), frames, owned rules, final frames, endpoint columns); the PR's isolated checker (bitstack) stays the authority.
price(word)  : exact raw crossing + fine admitted (PR #5708 chain) from local paid (P = P_pr + CALLS*(paid - paid_pr), T fixed under local-only edits)."""
import sys,os,gzip,json
from fractions import Fraction as F
from collections import Counter
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); PROFDIR=HERE+'/profiles'
sys.path.insert(0,HERE)
import bitval
def pkgdir(alias): return PROFDIR+'/'+alias+'/pkg'
def prof(alias='bit5708'): return json.load(open(PROFDIR+'/%s.json'%alias))
def load(path):
    raw=open(path,'rb').read(); raw=gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw
    return json.loads(raw)
def is_bit(w): return isinstance(w,dict) and 'records' in w and 'owned' in w and 'start' in w
def save(w,path):
    open(path,'wb').write(gzip.compress((json.dumps(w,separators=(',',':'))).encode(),mtime=0))
class Ctx:
    """frames + paths + base invoice of an adopted profile"""
    def __init__(s,alias='bit5708'):
        s.alias=alias; s.prof=prof(alias); d=pkgdir(alias)
        s.frames=json.load(open(d+'/'+s.prof['frames_file']))['frames']
        s.dims={int(k):v['dim'] for k,v in s.frames.items()}
        s.paths=json.load(open(d+'/PATHS.json')) if os.path.exists(d+'/PATHS.json') else {}
        s._nest={}
        s.baseword=load(d+'/WORD.json.gz'); inv=json.load(open(d+'/INVOICE.json'))
        s.P0={int(k):v for k,v in inv['paid'].items()}; s.T0={int(k):v for k,v in inv['targets'].items()}
        s.local0=Counter(e[4] for e in s.baseword['records'] if e[0]=='Q'); s.calls=s.prof['calls']
        s.width=len(s.baseword['start'])
    def nested(s,a,b,k):
        key=(a,b,k)
        if key in s._nest: return s._nest[key]
        lo,hi=(a,b) if s.dims[a]<s.dims[b] else (b,a); ok=(0<k<8 and s.dims[hi]-s.dims[lo]==k)
        if ok:
            B=s.frames[str(lo)]['B']; A=s.frames[str(hi)]['A']
            ok=all(sum(F(v)*F(w) for v,w in zip(x,y))==0 for x in B for y in A)
        s._nest[key]=ok; return ok
def expected_rows(width,owned):
    return [0 if i in owned else (1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(width)]
def check(w,ctx,maxv=50):
    """-> list of violations (rule, event index, detail); [] = legal under the fast oracle (no physical mod-p fields: bitstack does those)"""
    V=[]; add=lambda *a: V.append(a)
    width=ctx.width; owned=set(w['owned']); st=w['start'][:]    # records run from word['start'] (entry frames) to word['final']
    rows=[1<<i for i in range(width)]
    for ix,e in enumerate(w['records']):
        op,d=e[0],e[1]
        if op=='ERASE':
            if d not in owned: add('No retained original erasure',ix,e)
            rows[d]=0; st[d]=e[2]
        elif op=='INIT':
            if d not in owned or rows[d]: add('Whole zero INIT',ix,e)
            st[d]=e[2]
        elif op=='ADD':
            s,f=e[2],e[3]
            if d==s or not (st[d]==st[s]==f): add('Actual common-frame XOR',ix,'d=%d st=%s s=%d st=%s f=%s'%(d,st[d],s,st[s],f))
            rows[d]^=rows[s]
        elif op in('Q','ZERO_Q'):
            s,t,k=e[2:5]
            if st[d]!=s: add('Actual current source FRAME',ix,'d=%d st=%s e=%s'%(d,st[d],e))
            elif not ctx.nested(s,t,k): add('Exact QQ nested residual / rank',ix,e)
            if op=='ZERO_Q' and rows[d]: add('Free move only whole zero',ix,e)
            st[d]=t
        else: add('Unknown event',ix,e)
        if len(V)>=maxv: return V
    if st!=w['final']: add('All final frames',-1,[i for i in range(width) if st[i]!=w['final'][i]][:10])
    exp=expected_rows(width,owned); bad=[i for i in range(width) if rows[i]!=exp[i]]
    if bad: add('Endpoint columns',-1,'%d bad e.g. %s'%(len(bad),bad[:8]))
    return V
def local_paid(w): return Counter(e[4] for e in w['records'] if e[0]=='Q')
def invoice(w,ctx):
    lp=local_paid(w); P=dict(ctx.P0)
    for k in set(lp)|set(ctx.local0): P[k]=P.get(k,0)+ctx.calls*(lp.get(k,0)-ctx.local0.get(k,0))
    return dict(ctx.T0),{k:v for k,v in P.items() if v}
def admitted_fine(raw,ctx):
    """PR #5708 chain: tested=floor_1e-14(raw)-4e-14 (PR convention: raw interval [n-2,n+2]e-14), uniform=tested-1e-14, C1=uniform-1e-14, 5 levels rho=1/100 grid 1e-15 strict-below"""
    p=ctx.prof['ordinary']
    if p.get('chain')=='q8x3': return bitval.adm(raw,8)
    grid=10**p['grid']; tested=F(int(raw*10**14)-4,10**14); uniform=tested-F(1,10**14); C1=uniform-F(1,10**14)
    backend=F(p['prior_admitted']); 
    for _ in range(5):
        a=F(99,100)*C1+F(1,100)*backend; n=-((-a.numerator*grid)//a.denominator)-1; backend=F(n,grid)
    return backend
def price(w,ctx):
    T,P=invoice(w,ctx); k=bitval.crossing(T,P,bitval.mpf('0.001'),bitval.mpf('0.02')); 
    return dict(T=T,P=P,raw=k,admitted=admitted_fine(k,ctx),surplus=sum(r*c for r,c in T.items())-sum(r*c for r,c in P.items()))
# ---------- derived-Q view (construct.emit of the PR) ----------
def scalars(w): return [e[:] for e in w['records'] if e[0] not in('Q','ZERO_Q')]
def emit(w,scal,ctx):
    width=ctx.width; owned=set(w['owned']); rows=[1<<i for i in range(width)]; state=w['start'][:]; out=[]
    def route(d,target):
        src=state[d]
        if src==target: return
        if src is None:
            if not(d in owned and not rows[d]): raise ValueError('Only zero owned header')
            out.append(['INIT',d,target]); state[d]=target; return
        path=ctx.paths.get('%s:%s'%(src,target))
        if not path: raise ValueError('no route %s:%s'%(src,target))
        for a,b,rank in path:
            out.append(['Q' if rows[d] else 'ZERO_Q',d,a,b,rank]); state[d]=b
    for e in scal:
        op,d=e[:2]
        if op in('ERASE','INIT'): rows[d],state[d]=0,e[2]; out.append(e[:])
        else:
            s,fr=e[2:]
            if not rows[s]: continue
            route(d,fr); route(s,fr); out.append(e[:]); rows[d]^=rows[s]
    for d,fr in enumerate(w['final']):
        if d in owned:
            if state[d]!=fr: out.append(['ERASE',d,fr]); state[d]=fr
        else: route(d,fr)
    return dict(w,records=out)
