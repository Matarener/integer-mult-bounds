"""Independent binary-basis ledger and declared free-operator contract for the three staged entries.

The basis walker (b, subset, perpendicular, transform, inverse, ledger) is PR3945's checks/independent_frames.py
unchanged (Dugongue, OpenAI Codex assisted); the staged-entry contract and controls are new.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.  Standard library only.
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

PINS=json.loads((PACKAGE/'INPUTS.json').read_text(encoding='utf8'))['canonical_sha256']
STAGED={'600':([45],[127,45]),'608':([45],[97,45]),'609':([45],[97,45])}
DELETED=[['add',183,600,1,4],['add',202,600,-1,4],['add',175,600,1,4],['add',123,600,-1,4],
         ['add',114,608,1,4],['add',137,608,-1,4],['add',173,608,1,4],['add',121,608,-1,4],
         ['add',114,609,1,4],['add',137,609,1,4],['add',173,609,1,4],['add',121,609,1,4]]
RELEASES=[['add',121,609,1,2],['add',137,608,-1,2],['add',202,600,-1,2],['add',602,600,-1,1],['add',610,608,-1,1],['add',610,609,-1,1]]
DELETED_AT=[77,78,79,80,93,94,95,96,97,98,99,100]
RELEASED_AT=[388,410,474,927,948,950]
DELTA={1:6,2:2,3:5,4:-7}

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
        if field not in ('A','B','restore','cleanup','start_extra','report','warps'):
            need(old[field]==new[field],'changed caller field '+field)
    need(old['helper_final']==new['helper_final'] and len(new['helper_final'])==91,'returns unchanged')
    keys=set(old['start_extra'])|set(new['start_extra'])
    changed={r:(old['start_extra'].get(r),new['start_extra'].get(r)) for r in keys if old['start_extra'].get(r)!=new['start_extra'].get(r)}
    need(changed=={r:(list(x),list(y)) for r,(x,y) in STAGED.items()},'staged entrance set')
    for r,(x,y) in changed.items():
        need(subset(b(x),b(y)) and len(b(y))==len(b(x))+1 and r not in new['helper_final'],'entrance raised by one dimension on an ordinary helper')
    for sec in ('A','restore'):
        need(signature(old[sec])==signature(new[sec]),'free opcode sequence '+sec)
    so,sn=signature(old['B']),signature(new['B'])
    need([so[i] for i in DELETED_AT]==DELETED,'declared deleted reads at their source positions')
    need([sn[i] for i in RELEASED_AT]==RELEASES,'declared releases at their target positions')
    need([g for i,g in enumerate(so) if i not in DELETED_AT]==[g for i,g in enumerate(sn) if i not in RELEASED_AT],'B opcode sequence differs only by declared deletions and releases')
    need(Counter(map(json.dumps,sn))==Counter(map(json.dumps,so))-Counter(map(json.dumps,DELETED))+Counter(map(json.dumps,RELEASES)),'opcode multiset balance')
    need([r[1:3] for r in old['warps']]==[r[1:3] for r in new['warps']],'native matrices/lenders')
    po,io=ledger(old);pn,inn=ledger(new)
    delta={r:pn[r]-po[r] for r in set(po)|set(pn) if pn[r]!=po[r]}
    need(delta==DELTA and sum(r*n for r,n in delta.items())==-3,'local profile delta/rank mass')
    need(io==Counter({5:28,6:18,7:53,8:96,9:213}),'old width inventory')
    need(inn==Counter({5:28,6:18,7:56,8:93,9:213}),'new width inventory')
    return {'old_profile':dict(po),'new_profile':dict(pn),'local_profile_delta':delta,'staged_entrances':sorted(changed,key=int),'deleted_reads':len(DELETED),'releases':len(RELEASES),'buffers':91}

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
    z=copy.deepcopy(new);z['start_extra']['608']=[45]
    reject('missing staged entrance',lambda:compare(old,z))
    z=copy.deepcopy(new);k=next(i for i,g in enumerate(z['B']) if g[:-1]==RELEASES[0]);z['B'][k][3]+=1
    reject('changed release coefficient',lambda:compare(old,z))
    z=copy.deepcopy(new);g=next(g for g in z['A'] if g[0]=='add');g[3]+=1
    reject('changed scalar operator',lambda:compare(old,z))
    return outcomes

def main():
    results={};mutation_checks=[]
    for provider in ('base','extra'):
        old,new=read('OLD-'+provider+'.json.gz'),read('NEW-'+provider+'.json.gz')
        results[provider]=compare(old,new)
        if '--controls' in sys.argv:mutation_checks += [provider+': '+x for x in controls(old,new)]
    print(json.dumps({'status':'PASS_INDEPENDENT_BINARY_BASIS_LEDGER','canonical_source_sha256':PINS,'providers':results,'rejected_controls':mutation_checks,'scope':'Independent local binary frames, exact histogram/inventory and declared staged-entry operator contract; native phases, dirty semantics and literal owner/outer assembly checked separately.'},sort_keys=True))

if __name__=='__main__':main()
