"""synth.k2bit -- k2net on the BIT side (G20 local word, profile bitN).  [K2BIT]  Scope [toolkit generality, k2net for G20 BIT words].
A BIT word is the same object as a complex k2net word: a RENDEZVOUS EVENT PROGRAM.  Per register a chain of frames (the Q / ZERO_Q records are the MOVE steps, k = dim gap = the rank);
every ADD d s f happens at a frame where BOTH registers are currently located (st[d]==st[s]==f); ERASE / INIT are the owned events.  Differences from the complex net:
  coefficients are GF(2) (none), frames are the fixed 645-frame exact-QQ catalogue (no new frames), cost = invoice (paid ranks of non-zero-row MOVEs, targets, queries) not R0 chain tax,
  owned registers are priced (their MOVEs are free iff the row is zero = ZERO_Q), and the value contract is rows over GF(2) (endpoint columns), not a dyadic replay.
API: encode(word)->net, decode(net)->word, rendezvous(net,ctx) (violation count), value(net,ctx) (exact raw crossing, independent of bitword.price: own histogram), rederive(net,ctx) (strip MOVEs, re-route
shortest PATHS = bitword.emit), dump_net(net,path) / load_net(path) (text, same line grammar as kernel2net with a 'BITNET' header), CostModel plug (BitCost / ComplexR0).  No side effects at import."""
import sys,os,gzip,json
from collections import Counter
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
if TK not in sys.path: sys.path.insert(0,TK)
import bitword,bitval
def encode(w):
    """word -> net: events in word order; Q/ZERO_Q -> ('M',d,a,b,k,z)"""
    ev=[]
    for r in w['records']:
        o=r[0]
        if o=='ADD': ev.append(('A',r[1],r[2],r[3]))
        elif o=='Q': ev.append(('M',r[1],r[2],r[3],r[4],0))
        elif o=='ZERO_Q': ev.append(('M',r[1],r[2],r[3],r[4],1))
        elif o=='ERASE': ev.append(('E',r[1],r[2]))
        elif o=='INIT': ev.append(('I',r[1],r[2]))
        else: raise ValueError(o)
    return dict(start=list(w['start']),final=list(w['final']),owned=sorted(w['owned']),events=ev,meta={k:v for k,v in w.items() if k not in('records','start','final','owned')})
def decode(net):
    rec=[]
    for e in net['events']:
        o=e[0]
        if o=='A': rec.append(['ADD',e[1],e[2],e[3]])
        elif o=='M': rec.append(['ZERO_Q' if e[5] else 'Q',e[1],e[2],e[3],e[4]])
        elif o=='E': rec.append(['ERASE',e[1],e[2]])
        elif o=='I': rec.append(['INIT',e[1],e[2]])
    w=dict(net['meta']); w.update(start=list(net['start']),final=list(net['final']),owned=list(net['owned']),records=rec); return w
def rendezvous(net,ctx):
    """# violations of: ADD operands co-located at its frame; MOVE source = current frame, exact QQ nesting / rank; ZERO_Q only on a zero row; final frames; endpoint columns (rows over GF(2))"""
    w=decode(net); return len(bitword.check(w,ctx,10**9))
def chains(net):
    """per register: frames visited (start, MOVE targets, INIT frames)"""
    ch={r:[s] for r,s in enumerate(net['start'])}
    for e in net['events']:
        if e[0]=='M': ch[e[1]].append(e[3])
        elif e[0]=='I': ch[e[1]].append(e[2])
    return ch
def histogram(net):
    """paid-rank histogram of the LOCAL word straight from MOVE events (zero-row MOVEs free)"""
    return Counter(e[4] for e in net['events'] if e[0]=='M' and not e[5])
def value(net,ctx):
    """exact raw crossing from the net's own histogram + the profile's global invoice (P = P_pr + calls*(paid-paid_pr), T fixed): independent of bitword.price/local_paid"""
    h=histogram(net); P=dict(ctx.P0)
    for k in set(h)|set(ctx.local0): P[k]=P.get(k,0)+ctx.calls*(h.get(k,0)-ctx.local0.get(k,0))
    P={k:v for k,v in P.items() if v}
    return bitval.crossing(dict(ctx.T0),P,bitval.mpf('0.001'),bitval.mpf('0.02')),P
def rederive(net,ctx):
    """strip all MOVEs and re-derive them by shortest PATHS routing (bitword.emit) -> net.  For a path-minimal word this is the identity."""
    w=decode(net); w2=bitword.emit(w,bitword.scalars(w),ctx); return encode(w2)
def dump_net(net,path):
    with open(path,'w') as f:
        f.write('BITNET %d %d %d\n'%(len(net['start']),len(net['owned']),len(net['events'])))
        f.write('S '+' '.join('-' if x is None else str(x) for x in net['start'])+'\n')
        f.write('Z '+' '.join('-' if x is None else str(x) for x in net['final'])+'\n')
        f.write('O '+' '.join(map(str,net['owned']))+'\n')
        for e in net['events']: f.write(' '.join(map(str,e))+'\n')
def load_net(path,meta=None):
    L=open(path).read().split('\n'); h=L[0].split(); assert h[0]=='BITNET'
    pf=lambda l:[None if x=='-' else int(x) for x in l.split()[1:]]
    ev=[tuple([l.split()[0]]+[int(x) for x in l.split()[1:]]) for l in L[4:] if l]
    return dict(start=pf(L[1]),final=pf(L[2]),owned=[int(x) for x in L[3].split()[1:]],events=ev,meta=meta or {})
# ------------------------------------------------------------------ pluggable cost model (shared interface for K2SEARCH moves)
class CostModel:
    """score(net) -> float (higher better); exact(net)-> authoritative value; legal(net)-> bool.  Moves produce candidate event lists; the model prices them."""
    name='abstract'
class BitCost(CostModel):
    name='bit'
    def __init__(s,alias='bit5708'): s.ctx=bitword.Ctx(alias)
    def legal(s,net): return rendezvous(net,s.ctx)==0
    def exact(s,net): return value(net,s.ctx)[0]
class ComplexR0(CostModel):
    """complex side: R0 = chain tax of the MOVE program (kernel2net.r0); lower is better -> score = -R0"""
    name='complex'
    def __init__(s,w=None): s.w=w
    def exact(s,w):
        from synth import kernel2net as kn; return -kn.r0(w)[1]
    def legal(s,w):
        from synth import kernel2net as kn; return kn.check_rendezvous(w)==0
if __name__=='__main__':
    import time; alias=sys.argv[1] if len(sys.argv)>1 else 'bit5708'; t0=time.time()
    ctx=bitword.Ctx(alias); w=ctx.baseword; net=encode(w)
    pw=bitword.price(w,ctx); v,P=value(net,ctx)
    print(alias,'regs',len(net['start']),'owned',len(net['owned']),'events',len(net['events']),'MOVE',sum(1 for e in net['events'] if e[0]=='M'))
    print('rendezvous violations',rendezvous(net,ctx))
    print('net value raw',v,' bitword.price raw',pw['raw'],' gap',abs(v-pw['raw']))
    print('admitted (fine chain)',bitword.admitted_fine(v,ctx),' published',ctx.prof['ordinary']['admitted'])
    print('roundtrip decode==word records:',decode(net)['records']==w['records'])
    n2=rederive(net,ctx); print('rederive(MOVEs) identical:',n2['events']==net['events'])
    print('time %.1fs'%(time.time()-t0))
