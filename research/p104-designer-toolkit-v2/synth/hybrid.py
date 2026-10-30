"""synth.hybrid -- HYBRID lane: swarm helper network + generated (single-jump) X/Y mains.  See ../module docstring.
analyse(word): per main register (X_i, Y_j), its chain of stops and the CONTACTS at every stop (ADD/COPY/SCALE events that read or write the main
while it sits in that frame), by partner role.  A stop with no contact is idle (deletable for free)."""
import sys,os,json,collections,gzip
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
from tkcommon import *
def load(p):
    return json.load(gzip.open(p)) if p.endswith('.gz') else json.load(open(p))
def chains(w):
    """reg -> list of epochs [frame, t_start, t_end, contacts[list of (t, kind, partner)]]"""
    n=len(w['initial']); cur={}; ep=collections.defaultdict(list)
    for r in range(n): ep[r].append([w['initial'][r],0,None,[]])
    for t,e in enumerate(w['program']):
        op=e[0]
        if op=='MOVE':
            r=e[1]
            if r<n: ep[r][-1][2]=t; ep[r].append([e[3],t,None,[]])
        elif op in('ADD','COPY'):
            d,s=e[1],e[2]
            if d<n: ep[d][-1][3].append((t,'w',s))
            if s<n: ep[s][-1][3].append((t,'r',d))
        elif op=='SCALE':
            if e[1]<n: ep[e[1]][-1][3].append((t,'s',None))
    return ep
def analyse(w,out=print):
    live=w['live']; n=len(w['initial']); dim=[len(b) for b in w['frames']]
    X=set(live); Y={r+112 for r in live}
    def role(r): return 'X' if r in X else ('Y' if r in Y else ('helper' if r<n else 'owned'))
    ep=chains(w); rep={}
    for name,regs in (('X',sorted(X)),('Y',sorted(Y))):
        idle=0; stops=0; hist=collections.Counter(); bystop=[]
        for r in regs:
            for k,(f,a,b,c) in enumerate(ep[r]):
                stops+=1
                ks=collections.Counter((x[1],role(x[2]) if x[2] is not None else '-') for x in c)
                if not c: idle+=1
                bystop.append((r,k,dim[f],len(c),dict(ks)))
                hist[(dim[f],min(len(c),9))]+=1
        rep[name]=dict(epochs=stops,idle=idle,bystop=bystop)
        out('%s: %d epochs (incl. initial), idle (no contact) %d'%(name,stops,idle))
        bd=collections.defaultdict(collections.Counter)
        for (r,k,d,nc,ks) in bystop:
            for kk,v in ks.items(): bd[d][kk]+=v
        for d in sorted(bd): out('  dim %d: epochs %d, contacts %s'%(d,sum(1 for s in bystop if s[2]==d),dict(bd[d])))
    return rep
if __name__=='__main__':
    w=load(sys.argv[1]); analyse(w)
def relabel_hybrid(w,which='XY'):
    """EXACT hybrid: every main M (X_i and/or Y_j) gets a shadow helper S born at M's initial frame and ending at M's final frame.  At t=0 (co-present):
    S+=M; M-=S; S+=M  (S=m, M=-h); every original event on M is retargeted to S (the swarm network sees S exactly where it saw M); M itself does ONE MOVE
    initial -> final (the generated main: rank 8, no stops) at the end, then M+=S; S-=M; M+=S restores (M=m, S=h).  Owned ids shift by the number of shadows."""
    import copy
    w=copy.deepcopy(w); n=len(w['initial']); live=w['live']
    mains=([r for r in live] if 'X' in which else [])+([r+112 for r in live] if 'Y' in which else [])
    ns=len(mains); sh={m:n+k for k,m in enumerate(mains)}
    ro=lambda r:r+ns if r>=n else sh.get(r,r)
    pre=[];post=[]
    for m in mains:
        s=sh[m]; a,b=w['initial'][m],w['final'][m]
        pre+= [['ADD',s,m,'1',a],['ADD',m,s,'-1',a],['ADD',s,m,'1',a]]
        post+=[['MOVE',m,a,b,False],['ADD',m,s,'1',b],['ADD',s,m,'-1',b],['ADD',m,s,'1',b]]
    prog=[]
    for e in w['program']:
        e=list(e); e[1]=ro(e[1])
        if e[0] in('ADD','COPY'): e[2]=ro(e[2])
        prog.append(e)
    w['program']=pre+prog+post
    w['initial']=w['initial']+[w['initial'][m] for m in mains]; w['final']=w['final']+[w['final'][m] for m in mains]
    w['public']=len(w['initial'])
    return w
def main_tax(w,iw,out=print):
    """exact invoice view (IncrWord ledger) of the mains: kappa with X / Y / both main lines replaced by single rank-8 jumps (the generated mains = the
    invoice-swap ceiling on THIS word), the per-stop deletion value (merge the two hops at one stop, nothing else changed) and its ladder."""
    import price_exact as PX
    T,P=iw.ledger(); C=PX.CALLS; k0=PX.kappa(T,P)
    live=w['live']; dim=[len(b) for b in w['frames']]; ep=chains(w)
    def hops(r): return [abs(dim[ep[r][k+1][0]]-dim[ep[r][k][0]]) for k in range(len(ep[r])-1)]
    def kap_with(changes):
        P2=collections.Counter(P)
        for r,d in changes.items(): P2[r]+=d
        return PX.kappa(dict(T),{a:b for a,b in P2.items() if b})
    res={}
    for name,regs in (('X',live),('Y',[r+112 for r in live]),('XY',list(live)+[r+112 for r in live])):
        ch=collections.Counter()
        for r in regs:
            for h in hops(r): ch[h]-=C
            ch[sum(hops(r))]+=C
        res[name]=kap_with(ch); out('all %s mains -> one jump: kappa %.10f (%+.3e vs %.10f)'%(name,res[name],res[name]-k0,k0))
    lad=[]
    for r in list(live)+[r+112 for r in live]:
        h=hops(r)
        for s in range(1,len(h)):
            a,b=h[s-1],h[s]; ch=collections.Counter({a:-C}); ch[b]-=C; ch[a+b]+=C
            lad.append((kap_with(ch)-k0,r,s,dim[ep[r][s][0]],len(ep[r][s][3])))
    lad.sort(reverse=True)
    out('intermediate main stops %d; per-stop deletion value: max %.3e median %.3e sum %.3e'%(len(lad),lad[0][0],lad[len(lad)//2][0],sum(x[0] for x in lad)))
    bc=collections.Counter(min(x[4],5) for x in lad); bv=collections.defaultdict(float)
    for x in lad: bv[min(x[4],5)]+=x[0]
    out('  by contacts at the stop (5 = 5+): '+', '.join('%d: %d stops, value %.3e'%(c,bc[c],bv[c]) for c in sorted(bc)))
    return res,lad,k0
def joint_screen(w,comp='3',jmax=400,log=print):
    """TKRELAY's compensated joint layer (relay.Relay.joint_edits / comp_single_edits) priced by IncrWord, with a key-safe log (relay.py's log line
    needs ed['i'], which joint edits lack).  -> list of (dk, legal, why, edit)"""
    import relay as RL, movekit as MK, incr
    v=MK.View(w); tl=RL.PLUGIN.prepare(v); iw=incr.IncrWord(w); out=[]
    jl=RL.PLUGIN.joint_edits(v,tl,log)[:jmax] if comp in('1','3') else []
    if comp in('2','3'): jl=jl+RL.PLUGIN.comp_single_edits(v,tl,log)[:jmax]
    for ed in jl:
        try: w2=v.rebuild(RL.PLUGIN.scalars(v,ed)); res=iw.try_edit(incr.diff_edit(w,w2))
        except (ValueError,KeyError,IndexError,AssertionError) as ex: out.append((None,False,repr(ex)[:80],ed)); continue
        out.append((res.dk,bool(res.legal),res.reason,ed))
    return out
def neighbour_frames(w,lad):
    """for every single-contact main stop: does the contact partner's chain visit the main's previous or next frame (a retime without a new stop)?
    and what is the partner's frame just before / after the contact (the partner's own neighbours)."""
    ep=chains(w); fr=[frozenset(_sp(b)) for b in w['frames']]; c=collections.Counter(); ex=[]
    for (v,r,s,d,nc) in lad:
        if nc!=1: continue
        t,kind,p=ep[r][s][3][0]; fp,fn=ep[r][s-1][0],ep[r][s+1][0]
        pf=[e[0] for e in ep[p]] if p is not None and p<len(w['initial']) else []
        k=(('prev' if fp in pf else '')+('next' if fn in pf else '')) or 'none'
        # partner's epoch containing t
        pe=[e for e in ep[p] if e[1]<=t and (e[2] is None or e[2]>t)] if pf else []
        c[(kind,k)]+=1; ex.append((r,s,kind,p,k))
    return c,ex
def _sp(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return s
