"""autodec -- AUTOMACRO lane: automatic decomposition of real (base -> PR) word diffs into primitive applications.

    python3 -B autodec.py BASE PR [--json F]        one pair
    python3 -B autodec.py --corpus [--out F]        every pair of CORPUS (below)

Method (all exact, MOVE-free scalar program; MOVEs are derived):
 1. MATCH events of base/PR by signature (op, registers, coefficient) and occurrence number (identical ADDs commute, so k-th with k-th).  Unmatched = removed/added; matched with a
    different frame SPAN = relabelled; matched but pushed across a CONFLICTING neighbour (per-register run-sequence of W/R/X events differs) = moved (P1).
 2. CLUSTER the changed events by shared registers (union-find); a cluster is one primitive application or one composition.
 3. TAG a cluster by an ordered rule list with exact algebraic checks (Steinberg correction relation, inverse pairs, owned involvement, new registers, copy lifetimes ...).
    Every tag names the primitive (P1s P1c P2 P3 P4 P7 P8 P9 P13 P14 ... ) or a NEW family (N:*) when the composition leaves the existing plugin reach.
 4. RESIDUE = clusters whose tags include UNEXPLAINED or N:*; clustered by shape in automacro_mine.py.
"""
import sys,os,json,gzip,collections,itertools
from fractions import Fraction as Q
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import tkcommon as TC
from tkcommon import legal,roles
WORDS=HERE+'/words'
# corpus: PR -> (base, kappa).  Base = the word of the swarm line the PR was built on (min multiset distance among lower-kappa words; verified by hand against module docstring)
CORPUS=[('5553','5551'),('5561','5553'),('5569','5561'),('5580','5569'),('5565','5551'),('5599','5580'),('5612','5599'),('5613','5612'),('5627','5613'),('5644','5627'),('5650','5644'),('5660','5650'),
        ('5666','5660'),('5678','5660'),('5684','5678'),('5713','5684'),('5718','5713'),('5739','5713'),('5751','5718'),('5756','5751'),('5774','5756'),('5796','5756'),('5786','5774'),
        ('5795','5786'),('5802','5795'),('5811','5802'),('5812','5811'),('5827','5811')]
def load(n):
    f='%s/%s.json.gz'%(WORDS,n)
    w=legal.load(f); return w
def sig(e):
    op=e[0]
    if op in('INIT','CLEAR'): return (op,e[1])
    return tuple(e[:-1])
def wfr(e): return e[-1]
def kinds(e):
    """(register, kind) pairs for conflict-run analysis"""
    op=e[0]
    if op=='ADD': return ((e[1],'W'),(e[2],'R'))
    if op=='COPY': return ((e[1],'X'),(e[2],'R'))
    return ((e[1],'X'),)
class Prog:
    def __init__(s,w):
        s.w=w; s.ev=[e for e in w['program'] if e[0]!='MOVE']; s.spans=legal.spans(w); s.n=len(w['initial'])
        s.sig=[sig(e) for e in s.ev]; occ=collections.Counter(); s.key=[]
        for sg in s.sig: occ[sg]+=1; s.key.append((sg,occ[sg]))
        s.pos={k:i for i,k in enumerate(s.key)}
        s.role=roles(w); s._tl=None
    def touchlist(s):
        if s._tl is None:
            d=collections.defaultdict(list)
            for i,e in enumerate(s.ev):
                for r in set(touched(e)): d[r].append(i)
            s._tl=d
        return s._tl
def runs_of(P,keep):
    """per register: list of run-index per kept key.  run = maximal block of W events or of R events; X events are singleton runs"""
    reg=collections.defaultdict(list)
    for i,e in enumerate(P.ev):
        if P.key[i] not in keep: continue
        for r,k in kinds(e): reg[r].append((k,P.key[i]))
    out={}
    for r,L in reg.items():
        idx={}; run=-1; last=None
        for k,key in L:
            if k=='X' or k!=last: run+=1
            last=k; idx[key]=run
        out[r]=idx
    return out
class UF:
    def __init__(s): s.p={}
    def f(s,x):
        s.p.setdefault(x,x)
        while s.p[x]!=x: s.p[x]=s.p[s.p[x]]; x=s.p[x]
        return x
    def u(s,a,b): s.p[s.f(a)]=s.f(b)
def diff(A,B):
    """-> dict(removed=[idx in A], added=[idx in B], relab=[(iA,iB)], moved=[(iA,iB,regs)], matched)"""
    kA=set(A.key); kB=set(B.key); common=kA&kB
    removed=[i for i,k in enumerate(A.key) if k not in kB]; added=[j for j,k in enumerate(B.key) if k not in kA]
    relab=[]
    for k in common:
        i,j=A.pos[k],B.pos[k]
        ea,eb=A.ev[i],B.ev[j]
        if ea[0] in('INIT','CLEAR') or ea[0]=='MOVE':
            if A.spans[ea[-1]]!=B.spans[eb[-1]]: relab.append((i,j))
        elif A.spans[ea[-1]]!=B.spans[eb[-1]]: relab.append((i,j))
    ra=runs_of(A,common); rb=runs_of(B,common); moved=[]; movedkeys=set()
    for r in set(ra)&set(rb):
        da,db=ra[r],rb[r]
        # relative order test: keys whose run index differs after normalising shifts (run counts equal when the sequences have the same block structure)
        if len(set(da.values()))!=len(set(db.values())) or any(da[k]!=db[k] for k in da.keys()&db.keys()):
            ks=[k for k in da.keys()&db.keys() if da[k]!=db[k]]
            for k in ks: movedkeys.add((k,r))
    moved=sorted({k for k,r in movedkeys}); mregs=collections.defaultdict(set)
    for k,r in movedkeys: mregs[k].add(r)
    return dict(removed=removed,added=added,relab=relab,moved=[(A.pos[k],B.pos[k],sorted(mregs[k])) for k in moved])
def touched(e):
    return (e[1],) if e[0] in('INIT','CLEAR','SCALE') else (e[1],e[2])
def is_owned(P,r): return P.role(r)=='owned'
def qf(x): return Q(x)
def steinberg_partner(A_ev,C_ev,B_ev):
    """is C the Steinberg correction of the ADD A passing the ADD B?  A=(t<-s,a) B=(u<-v,b):  B reads t (v==t): C=(u<-s,ab);  B writes s (u==s): C=(t<-v,+-ab).  returns coef sign class or None"""
    if A_ev[0]!='ADD' or C_ev[0]!='ADD' or B_ev[0]!='ADD': return None
    t,s,a=A_ev[1],A_ev[2],qf(A_ev[3]); u,v,b=B_ev[1],B_ev[2],qf(B_ev[3])
    if v==t and u!=s:
        if C_ev[1]==u and C_ev[2]==s and abs(qf(C_ev[3]))==abs(a*b): return 'reads'
    if u==s and v!=t:
        if C_ev[1]==t and C_ev[2]==v and abs(qf(C_ev[3]))==abs(a*b): return 'writes'
    return None
def classify_cluster(A,B,D,cl):
    """cl = dict(rem=[iA],add=[iB],rel=[(iA,iB)],mov=[(iA,iB,regs)]).  -> (tags, params)"""
    tags=[]; par={}
    rem=[A.ev[i] for i in cl['rem']]; add=[B.ev[j] for j in cl['add']]
    cnt=lambda L:collections.Counter(e[0] for e in L)
    cr,ca=cnt(rem),cnt(add)
    own=lambda P,e: any(is_owned(P,r) for r in touched(e))
    newregs={r for e in add for r in touched(e) if r>=A.n}
    par.update(rem=dict(cr),add=dict(ca),relab=len(cl['rel']),moved=len(cl['mov']),dims=sorted({len(B.w['frames'][e[-1]]) for e in add if e[0]=='ADD'}))
    # --- structural families
    if any(r>=A.n and r<B.n for e in add for r in touched(e)): tags.append('P4r/P13(newreg)'); par['newregs']=sorted({r for e in add for r in touched(e) if A.n<=r<B.n})[:6]
    if ca.get('COPY',0) or cr.get('COPY',0): tags.append('P4c(copy)' if ca.get('COPY',0)>=cr.get('COPY',0) else 'P4c-merge')
    if ca.get('INIT',0)!=cr.get('INIT',0): tags.append('P8/P7(lifetime)')
    if ca.get('SCALE',0) or cr.get('SCALE',0): tags.append('P9(scale)')
    # --- ADD algebra
    addA=[e for e in add if e[0]=='ADD']; remA=[e for e in rem if e[0]=='ADD']
    inv_add=[(e,f) for e,f in itertools.combinations(addA,2) if e[1]==f[1] and e[2]==f[2] and qf(e[3])==-qf(f[3])]
    inv_rem=[(e,f) for e,f in itertools.combinations(remA,2) if e[1]==f[1] and e[2]==f[2] and qf(e[3])==-qf(f[3])]
    if inv_add: tags.append('P3(conj)x%d'%len(inv_add))
    if inv_rem and not inv_add: tags.append('P0(cancel)x%d'%len(inv_rem))
    # Steinberg corrections: an added ADD that is the correction of a moved / relabelled ADD past a neighbour event of the base
    movedA=[A.ev[i] for i,j,r in cl['mov']]+[A.ev[i] for i,j in cl['rel']]
    stein=0; owned_corr=0
    from bisect import bisect_left,bisect_right
    tl=A.touchlist()
    mov_pos={}   # id(event)->old positions
    for i,j,r in cl['mov']: mov_pos[i]=1
    for i,j in cl['rel']: mov_pos[i]=1
    cand=[i for i in mov_pos if A.ev[i][0]=='ADD'][:400]
    for e in addA[:600]:
        found=False
        for i0 in cand:
            mA=A.ev[i0]
            for r in (mA[1],mA[2]):
                L=tl.get(r,())
                a_=bisect_left(L,i0-400); b_=bisect_right(L,i0+400)
                for k in L[a_:b_]:
                    if steinberg_partner(mA,e,A.ev[k]): found=True; break
                if found: break
            if found: break
        if found:
            stein+=1
            if own(B,e): owned_corr+=1
    if stein: tags.append('P1c x%d'%stein)
    if owned_corr: tags.append('P1c-owned-corr x%d'%owned_corr); par['owned_corr']=owned_corr
    # remaining added ADDs involving owned registers
    rest=[e for e in addA if own(B,e) and not any(e is f for p in inv_add for f in p)]
    if rest and not stein: tags.append('P8(owned ADDs)x%d'%len(rest))
    elif len(rest)>owned_corr: tags.append('P8(owned ADDs)x%d'%(len(rest)-owned_corr))
    if cl['mov'] and not (stein or inv_add or addA or remA): tags.append('P1s(moves)x%d'%len(cl['mov']))
    elif cl['mov'] and (addA or remA): par['also_moved']=len(cl['mov'])
    if cl['rel'] and not tags: tags.append('P2(relabel)x%d'%len(cl['rel']))
    elif cl['rel']: par['also_relabel']=len(cl['rel'])
    flow=collections.Counter()
    for i,j in cl['rel']:
        a_,b_=len(A.w['frames'][A.ev[i][-1]]),len(B.w['frames'][B.ev[j][-1]])
        flow['same' if a_==b_ else ('down' if b_<a_ else 'up')]+=1
    if flow: par['dimflow']=dict(flow)
    if cl['rel'] and tags and tags[0].startswith('P2'):
        tags[0]='P2(relabel-%s)x%d'%('/'.join(sorted(flow)),len(cl['rel']))
    if tags and tags[0].startswith('P2') and len(cl['rel'])>=50 and not (addA or remA): tags[0]='P5(block %s)x%d'%('/'.join(sorted(flow)),len(cl['rel']))
    if not tags:
        dm=par['dims']; nadd,nrem=len(addA),len(remA)
        if nadd and not nrem and not cl['mov'] and not cl['rel'] and nadd<=6 and max(dm or [0])<=4: tags.append('P6/P3x(pre-post ADDs)x%d'%nadd)
        elif nrem and not nadd and not cl['mov'] and not cl['rel'] and nrem<=2: tags.append('P6/P0(contact/drop)x%d'%nrem)
        elif nadd==nrem and 0<nadd<=2 and not cl['mov'] and not cl['rel']: tags.append('P3/P1c(correction swap)x%d'%nadd)
    if not tags: tags.append('UNEXPLAINED')
    return tags,par
GAP=150
def decompose(base,pr,verbose=False):
    A=Prog(load(base)); B=Prog(load(pr)); D=diff(A,B)
    if len(D['removed'])>1500 and abs(len(D['removed'])-len(D['added']))<0.1*len(D['removed']):      # register renumbering / role-layout change (#5627: 748 public -> 743 + 9 owned_fields): not a primitive
        return dict(base=base,pr=pr,n_removed=len(D['removed']),n_added=len(D['added']),n_relab=len(D['relab']),n_moved=len(D['moved']),newregs=B.n-A.n,endpoints=endpoints(A,B),
                    clusters=[dict(shape='renumber',roles={},tags=['P7/RENUMBER(layout change)'],par=dict(rem={},add={}),nregs=0,regs=[],size=len(D['removed'])+len(D['added']),pos=(0,len(A.ev)))])
    uf=UF()
    items=[]
    for i in D['removed']: items.append(('rem',i,touched(A.ev[i])))
    for j in D['added']: items.append(('add',j,touched(B.ev[j])))
    for i,j in D['relab']: items.append(('rel',(i,j),touched(A.ev[i])))
    for i,j,rg in D['moved']: items.append(('mov',(i,j,rg),touched(A.ev[i])))
    # B-coordinate of every base event: B position of the last common-key event at or before it
    comm=set(B.pos)&set(A.pos); posB=[0]*len(A.ev); cur=0
    for i,k in enumerate(A.key):
        if k in comm: cur=B.pos[k]
        posB[i]=cur
    def ipos(kind,x):
        if kind=='add': return x
        if kind=='rem': return posB[x]
        if kind=='rel': return posB[x[0]]
        return posB[x[0]]
    byreg=collections.defaultdict(list)
    for k,(kind,x,regs) in enumerate(items):
        p=ipos(kind,x)
        for r in regs: byreg[r].append((p,k))
    for r,L in byreg.items():
        L.sort(); 
        for (p1,k1),(p2,k2) in zip(L,L[1:]):
            if p2-p1<=GAP: uf.u(('i',k1),('i',k2))
    groups=collections.defaultdict(lambda:dict(rem=[],add=[],rel=[],mov=[],regs=set()))
    for k,(kind,x,regs) in enumerate(items):
        g=groups[uf.f(('i',k))]; g[{'rem':'rem','add':'add','rel':'rel','mov':'mov'}[kind]].append(x); g['regs']|=set(regs)
    clusters=[]
    for g in groups.values():
        tags,par=classify_cluster(A,B,D,g)
        pos=[A.ev and i for i in g['rem']]+[i for i,j in g['rel']]+[i for i,_,_ in g['mov']]+g['add']
        rl=collections.Counter(A.role(r) if r<A.n else 'new' if r<B.n else 'owned' for r in g['regs'])
        shape='rem%s add%s rel%d mov%d regs%s'%(sorted(par['rem'].items()),sorted(par['add'].items()),len(g['rel']),len(g['mov']),sorted(rl.items()))
        clusters.append(dict(shape=shape,roles=dict(rl),tags=tags,par=par,nregs=len(g['regs']),regs=sorted(g['regs'])[:8],size=len(g['rem'])+len(g['add'])+len(g['rel'])+len(g['mov']),pos=(min(pos),max(pos)) if pos else None))
    clusters.sort(key=lambda c:-c['size'])
    ep=endpoints(A,B)
    return dict(base=base,pr=pr,n_removed=len(D['removed']),n_added=len(D['added']),n_relab=len(D['relab']),n_moved=len(D['moved']),newregs=B.n-A.n,endpoints=ep,clusters=clusters)
def endpoints(A,B):
    wa,wb=A.w,B.w; n=min(A.n,B.n); out=collections.Counter()
    for r in range(n):
        if A.spans[wa['initial'][r]]!=B.spans[wb['initial'][r]]: out[A.role(r)+'.start']+=1
        if A.spans[wa['final'][r]]!=B.spans[wb['final'][r]]: out[A.role(r)+'.final']+=1
    return dict(out)
def summarize(d):
    c=collections.Counter()
    for cl in d['clusters']:
        c['+'.join(t.split(' x')[0] for t in cl['tags'])]+=1
    return dict(c)
def main(argv):
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('base',nargs='?'); ap.add_argument('pr',nargs='?'); ap.add_argument('--corpus',action='store_true'); ap.add_argument('--out'); ap.add_argument('--json'); ap.add_argument('--only')
    a=ap.parse_args(argv)
    pairs=CORPUS if a.corpus else [(a.pr,a.base)]
    if a.only: pairs=[p for p in pairs if p[0] in a.only.split(',')]
    res=[]
    for pr,base in pairs:
        try: d=decompose(base,pr)
        except Exception as ex:
            import traceback; traceback.print_exc(); d=dict(base=base,pr=pr,error=repr(ex))
        res.append(d)
        if 'error' not in d:
            print('#%s <- #%s  removed %d added %d relab %d moved %d newregs %d endpoints %s | %d clusters | %s'%(pr,base,d['n_removed'],d['n_added'],d['n_relab'],d['n_moved'],d['newregs'],d['endpoints'],len(d['clusters']),json.dumps(summarize(d))[:600]),flush=True)
    if a.out or a.json: json.dump(res,open(a.out or a.json,'w'),indent=1,default=str)
if __name__=='__main__': main(sys.argv[1:])
