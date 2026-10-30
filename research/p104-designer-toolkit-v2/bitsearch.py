"""bitsearch: exact greedy/LNS local search on BIT words.  [BITADAPT]  `python bitsearch.py ALIAS [MAXMIN] [CLASS]`
Move classes (all value-preserving at the scalar level; Q events are re-derived by emit):  relabel (ADD frame -> neighbour frame), move (ADD past commuting events to another timeline slot, with frame in
{neighbour frames, own}), swap (adjacent independent events).  Every candidate is evaluated EXACTLY by emit + paid histogram (linear weights of the exact marginal for ordering, exact crossing for the winner).
Writes best-so-far to ext/BITADAPT/CANDIDATE-<alias>-*.json.gz ONLY when the fast oracle is legal and the exact raw crossing exceeds the base (then the PR checker must confirm: tk accept)."""
import sys,os,json,time,bisect,copy
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import bitword,bitscreen,bitval
from collections import Counter
OUT=os.path.dirname(os.path.abspath(__file__)) + '/ext/BITADAPT'
def paid_cost(recs,W): return sum(W[e[4]] for e in recs if e[0]=='Q')
def run(alias,maxmin=20,classes=('relabel','move','swap')):
    ctx=bitword.Ctx(alias); w=ctx.baseword; S=bitscreen.Screen(w,ctx); W=S.W; t0=time.time()
    base_cost=paid_cost(w['records'],W); scal=bitword.scalars(w); n=len(scal); stats=Counter(); best=(0.0,None)
    owned=S.owned
    def evaluate(s2):
        try: w2=bitword.emit(w,s2,ctx)
        except Exception: stats['emit_fail']+=1; return None
        stats['eval']+=1; return w2,base_cost-paid_cost(w2['records'],W)
    def consider(s2,label):
        nonlocal best
        r=evaluate(s2)
        if r is None: return
        w2,gain=r
        if gain>1e-12:
            V=bitword.check(w2,ctx,2)
            if V: stats['gain_but_illegal']+=1; return
            stats['improving']+=1
            if gain>best[0]: best=(gain,w2); print('IMPROVING %s gain %.3e'%(label,gain),flush=True)
    for i,e in enumerate(scal):
        if time.time()-t0>maxmin*60: print('time cap'); break
        if e[0]!='ADD' or e[1] in owned or e[2] in owned: continue
        d,sr,f=e[1],e[2],e[3]
        # neighbour frames
        nf=set()
        for r in (d,sr):
            L=S.tl[r]; j=bisect.bisect_left(L,i)
            if j>0: nf.add(scal[L[j-1]][3])
            if j+1<len(L): nf.add(scal[L[j+1]][3])
            nf.add(w['start'][r]); nf.add(w['final'][r])
        if 'relabel' in classes:
            for g in nf:
                if g is None or g==f: continue
                s2=copy.copy(scal); s2[i]=e[:3]+[g]; consider(s2,'relabel %d->%s'%(i,g))
        if 'move' in classes or 'swap' in classes:
            lo=i
            while lo>0 and i-lo<600 and not bitscreen._blocks(scal[lo-1],d,sr): lo-=1
            hi=i
            while hi<n-1 and hi-i<600 and not bitscreen._blocks(scal[hi+1],d,sr): hi+=1
            pts=set()
            if 'swap' in classes: pts|={i-1,i+2}
            if 'move' in classes:
                for r in (d,sr):
                    L=S.tl[r]; a=bisect.bisect_left(L,lo); b=bisect.bisect_right(L,hi)
                    for j in range(a,b):
                        if L[j]!=i: pts.add(L[j]); pts.add(L[j]+1)
                pts|={lo,hi+1}
            for p in sorted(pts):
                if p<lo or p>hi+1 or p in(i,i+1): continue
                for g in {f}|nf:
                    if g is None: continue
                    s2=copy.copy(scal); ev=s2.pop(i); ev=ev[:3]+[g]; s2.insert(p-1 if p>i else p,ev); consider(s2,'move %d->%d f=%s'%(i,p,g))
    print('DONE',alias,dict(stats),'best gain',best[0],'time %.0fs'%(time.time()-t0))
    if best[1] is not None:
        p=bitword.price(best[1],ctx); path=OUT+'/CANDIDATE-%s-%d.json.gz'%(alias,int(time.time())); bitword.save(best[1],path)
        print('CANDIDATE',path,'raw',float(p['raw']),'admitted',float(p['admitted']))
    return best
if __name__=='__main__':
    run(sys.argv[1] if len(sys.argv)>1 else 'bit5708',float(sys.argv[2]) if len(sys.argv)>2 else 20,tuple(sys.argv[3].split(',')) if len(sys.argv)>3 else ('relabel','move','swap'))
