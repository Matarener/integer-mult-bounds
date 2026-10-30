"""synth.kernel2net -- KERNEL2 explicit-network layer (see ../module docstring).  Scope [toolkit synth, unified generalised SA kernel].

A legal word is exactly a RENDEZVOUS EVENT PROGRAM: per register a nested MOVE chain of frames, and events (ADD/COPY/SCALE/INIT/CLEAR) at a frame where every register involved is
currently located (verified on #5811: 0 violations over 25984 events).  R0 = sum over registers of tax(distinct chain dims) = D ln D - sum r ln r (X, Y, H alike; owned 0).
This module: encode(word) -> text net for ext/KERNEL2/k2.cpp (K2_NET mode), pure-python replay (exact Fractions), per-role R0.  No side effects at import.
"""
import sys,os,math,collections
from fractions import Fraction as Q
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
if TK not in sys.path: sys.path.insert(0,TK)
_H=lambda r:r*math.log(r) if r>0 else 0.0
def tax_dims(ds):
    ds=sorted(set(ds)); D=ds[-1]-ds[0]
    return _H(D)-sum(_H(b-a) for a,b in zip(ds,ds[1:])) if D>0 else 0.0
def roles(w):
    n=len(w['initial']); live=set(w['live'])
    def role(r):
        if r>=n: return 'O'
        if r in live: return 'X'
        if r-112 in live: return 'Y'
        return 'H'
    return role
def chains(w):
    """per register: list of frame ids visited (initial + MOVE targets + INIT frame)"""
    n=len(w['initial']); ch={r:[w['initial'][r]] for r in range(n)}
    for e in w['program']:
        if e[0]=='MOVE': ch[e[1]].append(e[3])
        elif e[0]=='INIT' and e[1] not in ch: ch[e[1]]=[e[2]]
        elif e[0]=='INIT': ch[e[1]].append(e[2])
    return ch
def r0(w):
    """exact R0 by role from MOVE chains"""
    role=roles(w); dim=[len(b) for b in w['frames']]; tot=collections.defaultdict(float)
    for r,c in chains(w).items(): tot[role(r)]+=tax_dims([dim[f] for f in c])
    return dict(tot),sum(tot.values())
def check_rendezvous(w):
    """co-presence of every event's registers at the event frame; returns violation count"""
    n=len(w['initial']); cur={r:w['initial'][r] for r in range(n)}; bad=0
    for e in w['program']:
        o=e[0]
        if o=='MOVE': cur[e[1]]=e[3]
        elif o in('ADD','COPY'): bad+=(cur.get(e[1])!=e[4])+(cur.get(e[2])!=e[4])
        elif o=='SCALE': bad+=cur.get(e[1])!=e[3]
        elif o=='INIT': cur[e[1]]=e[2]
        elif o=='CLEAR': bad+=cur.get(e[1])!=e[2]
    return bad
def replay(w):
    """exact symbolic replay: register -> {symbol: Fraction}.  symbols = initial registers (x_i, y_j, helper junk)."""
    n=len(w['initial']); form={r:{r:Q(1)} for r in range(n)}
    for e in w['program']:
        o=e[0]
        if o in('ADD','COPY'):
            d,s,q=e[1],e[2],Q(e[3]); fd=dict(form.get(d,{})) if o=='ADD' else {}
            for c,v in form.get(s,{}).items():
                fd[c]=fd.get(c,0)+q*v
                if fd[c]==0: del fd[c]
            form[d]=fd
        elif o=='SCALE': form[e[1]]={c:v*Q(e[2]) for c,v in form[e[1]].items()}
        elif o in('INIT','CLEAR'): form[e[1]]={}
    return form
def dump_net(w,path):
    """text net for k2.cpp: F frames (id dim basis..), R regs (id role init_frame), then the event stream in word order"""
    role=roles(w); n=len(w['initial']); F=w['frames']
    with open(path,'w') as f:
        owned=sorted({e[1] for e in w['program'] if e[0]=='INIT' and e[1]>=n})
        f.write('NET %d %d %d %d\n'%(n,len(owned),len(F),len(w['program'])))
        for i,b in enumerate(F): f.write('F %d %d %s\n'%(i,len(b),' '.join(map(str,b))))
        for r in range(n): f.write('R %d %s %d\n'%(r,role(r),w['initial'][r]))
        for r in owned: f.write('R %d O -1\n'%r)
        for e in w['program']:
            o=e[0]
            if o=='MOVE': f.write('M %d %d\n'%(e[1],e[3]))
            elif o in('ADD','COPY'): f.write('%s %d %d %s %d\n'%('A' if o=='ADD' else 'C',e[1],e[2],e[3],e[4]))
            elif o=='SCALE': f.write('S %d %s %d\n'%(e[1],e[2],e[3]))
            elif o=='INIT': f.write('I %d %d\n'%(e[1],e[2]))
            elif o=='CLEAR': f.write('X %d %d\n'%(e[1],e[2]))
def signature(form):
    """order-independent checksum of a replay result (compared against the C++ replay)"""
    s=0.0
    for r,fm in form.items():
        for c,v in fm.items(): s+=float(v)*((r*7919+c*104729)%1000003)
    return s
if __name__=='__main__':
    from tkcommon import load
    _,w=load(sys.argv[1]); by,tot=r0(w); print('R0',{k:round(v,2) for k,v in by.items()},round(tot,2),'rendezvous violations',check_rendezvous(w))
    fm=replay(w); print('signature %.6f'%signature(fm))
    if len(sys.argv)>2: dump_net(w,sys.argv[2]); print('wrote',sys.argv[2])
