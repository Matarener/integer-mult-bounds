"""Independent binary-basis and unchanged free-operator contract checks.

Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
Standard library only; no credited audit or solver implementation is imported.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import json,gzip,hashlib,sys,copy
PACKAGE=Path(__file__).resolve().parent.parent

def need(ok,why):
    if not ok:raise ValueError(why)

def b(vectors):
    pivots={}
    for x in vectors:
        need(type(x) is int and 0<=x<512,'bad frame vector')
        while x:
            p=x.bit_length()-1
            if p in pivots:x^=pivots[p]
            else:pivots[p]=x;break
    for p in sorted(pivots):
        for q in sorted(pivots,reverse=True):
            if q>p and (pivots[q]>>p)&1:pivots[q]^=pivots[p]
    return tuple(pivots[p] for p in sorted(pivots,reverse=True))

def subset(A,B):return b(A+B)==B
FULL=b([1<<j for j in range(9)])
def perpendicular(port):
    pivot=(port&-port).bit_length()-1
    return b([(1<<j)^((1<<pivot) if (port>>j)&1 else 0) for j in range(9) if j!=pivot])
def transform(F,G):
    def apply(x):
        y=0
        for j in range(9):
            if (x>>j)&1:y^=G[j]
        return y
    return b([apply(x) for x in F])
def inverse(G):
    inv={}
    for x in range(512):
        y=0
        for j in range(9):
            if x>>j&1:y^=G[j]
        need(y not in inv,'singular native matrix');inv[y]=x
    return [inv[1<<j] for j in range(9)]

def ledger(w):
    removed=set(w['removed']);live=set(range(704))-removed
    start={r:b([w['ports'][r]]) if r<112 else () for r in live}
    for r,F in w['start_extra'].items():start[int(r)]=b(F)
    end={r:(FULL if r<112 or r>=224 else perpendicular(w['ports'][r-112])) for r in live}
    for r,F in w['helper_final'].items():end[int(r)]=b(F)
    cur=dict(start);profile=Counter()
    def climb(r,F):
        F=b(F);need(subset(cur[r],F),'nonmonotone frame at '+str(r));d=len(F)-len(cur[r]);cur[r]=F
        if d:profile[d]+=1
    def scalar(g):
        for r in g[1:3] if g[0]=='add' else g[1:2]:climb(r,g[-1])
    for g in w['A']:
        if g[0]!='warp':scalar(g);continue
        _,r,op,U,E=g;G=w['warps'][abs(op)-1][2]
        if op<0:G=inverse(G)
        need(cur[r]==b(U),'A native entry');need(transform(b(U),G)==b(E),'A native map');cur[r]=b(E)
    for t in range(112,224):need(cur[t]==b(w['target_levels'].get(str(t-112),[])),'target cut level')
    for r,U in zip(w['centers'],w['center_frames']):
        need(cur[r]==b(U),'centre entry');temporary=b(U)
        served={b(w['target_levels'].get(str(g[1]-112),[])) for g in w['cut'] if g[2]==r}
        for T in sorted(served,key=lambda F:-len(F)):
            need(subset(T,temporary),'centre nesting');d=len(temporary)-len(T)
            if d:profile[d]+=1
            temporary=T
        # The actual descent is on a private copy; live cur[r] stays U.
    at={}
    for record in w['warps']:at.setdefault(record[0],[]).append(record)
    for i in range(len(w['B'])+1):
        for _,r,G,U,E in at.get(i,[]):
            need(cur[r]==b(U),'B native entry');need(transform(b(U),G)==b(E),'B native map');cur[r]=b(E)
        if i<len(w['B']):scalar(w['B'][i])
    for g in w['restore']:scalar(g)
    for r in sorted(live):climb(r,end[r])
    inventory=Counter(len(end[r])-len(start[r]) for r in live if r>=224)
    need(dict(profile)=={int(r):n for r,n in w['report']['local_profile'].items()},'profile mismatch')
    need(dict(inventory)=={int(r):n for r,n in w['report']['width_inventory'].items()},'inventory mismatch')
    return profile,inventory

PINS={
    'OLD-base.json.gz':'a140d980692fb1688b6b85021e06e2aea7d97eb3fd2b09cbd6c47afb0cc7f9da',
    'OLD-extra.json.gz':'309e6b90bad582081b90cce08f820da62ab11602a8298852cb7ef6f16b8942c8',
    'NEW-base.json.gz':'cee1ddcbdf3cdcba99146f281cbb452440dd1ed641aa3a47ccc3343680ae7ddc',
    'NEW-extra.json.gz':'cc1826748ed24cd085a5756b46f0090d5a43ad54820c025366cf2848aca589b2'}
CHANGED=[277,282,293,298,307,309,314,323,325,330,337,339,341,346,353,355,357,362,369,371,373,378,385,387,389,394]
DELTA={1:42,2:-13,3:-6,4:7}

def read(name):
    w=json.loads(gzip.decompress((PACKAGE/'inputs'/name).read_bytes()))
    scientific=hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(scientific==PINS[name],'canonical source guard '+name)
    return w

def signature(seq):
    return [g[:3] if g[0]=='warp' else g[:-1] for g in seq
            if not(g[0]=='scale' and Q(g[2],g[3])==1)]

def compare(old,new):
    for field in old:
        if field not in ('A','B','restore','cleanup','helper_final','report','warps'):
            need(old[field]==new[field],'changed caller field '+field)
    need(set(old['helper_final'])==set(new['helper_final']) and len(new['helper_final'])==91,'buffer keys/count')
    changed=sorted(int(r) for r in old['helper_final'] if b(old['helper_final'][r])!=b(new['helper_final'][r]))
    need(changed==CHANGED,'changed terminal identity set')
    for r in changed:
        before,after=b(old['helper_final'][str(r)]),b(new['helper_final'][str(r)])
        need(subset(before,after) and len(after)==len(before)+1,'terminal codimension1 extension')
    for sec in ('A','B','restore','cleanup'):
        need(signature(old[sec])==signature(new[sec]),'free opcode sequence '+sec)
    need([r[1:3] for r in old['warps']]==[r[1:3] for r in new['warps']],'native matrices/lenders')
    po,io=ledger(old);pn,inn=ledger(new)
    delta={r:pn[r]-po[r] for r in set(po)|set(pn) if pn[r]!=po[r]}
    need(delta==DELTA and sum(r*n for r,n in delta.items())==26,'local profile delta/rank mass')
    need(io==Counter({4:26,5:2,6:18,7:53,8:96,9:213}),'old width inventory')
    need(inn==Counter({5:28,6:18,7:53,8:96,9:213}),'new width inventory')
    return {'old_profile':dict(po),'new_profile':dict(pn),'local_profile_delta':delta,'terminal_extensions':26,'buffers':91}

def controls(old,new):
    outcomes=[]
    def reject(label,callback):
        try:callback()
        except ValueError:outcomes.append(label);return
        raise ValueError('mutation was accepted: '+label)
    z=copy.deepcopy(new);z['report']['local_profile']['1']+=1
    reject('wrong paid histogram',lambda:ledger(z))
    z=copy.deepcopy(new);z['warps'][0][4]=[]
    reject('wrong native exit frame',lambda:ledger(z))
    z=copy.deepcopy(new)
    g=next(g for g in z['A'] if g[0]=='add');g[3]+=1
    reject('changed scalar operator',lambda:compare(old,z))
    z=copy.deepcopy(new);z['helper_final'][str(CHANGED[0])]=old['helper_final'][str(CHANGED[0])]
    reject('missing promoted return',lambda:compare(old,z))
    return outcomes

def main():
    results={};mutation_checks=[]
    for provider in ('base','extra'):
        old,new=read('OLD-'+provider+'.json.gz'),read('NEW-'+provider+'.json.gz')
        results[provider]=compare(old,new)
        if '--controls' in sys.argv:mutation_checks += [provider+': '+x for x in controls(old,new)]
    print(json.dumps({'status':'PASS_INDEPENDENT_BINARY_BASIS_LEDGER','canonical_source_sha256':PINS,'providers':results,'rejected_controls':mutation_checks,'scope':'Independent local binary frames, exact histogram/inventory and unchanged free-operator contract; native phases and literal owner/outer assembly checked separately.'},sort_keys=True))

if __name__=='__main__':main()
