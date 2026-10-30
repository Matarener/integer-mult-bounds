"""ctxmine_scan -- batch driver of ctxmine (window superoptimisation on real words).  CLI:
   python3 -B ctxmine_scan.py WORD --kind owned|hub|random|all [--W 8] [--shard i/n] [--out F.jsonl] [--depth 3] [--tl 30] [--max N]
One JSON line per window that has an improving rewrite (exact-confirmed for the best distinct ones) + a trailing 'summary' line.  Never sets env at import."""
import os,sys,json,gzip,time,collections
import movekit as M
import ctxmine as CM
from prims import Block

def sig_of(S,S2,v):
    """abstract signature of the rewrite: changed middle slices with registers renamed by first occurrence and a role letter (p=public main X/Y, h=helper, o=owned), frames dropped"""
    n=min(len(S),len(S2)); p=0
    while p<n and S[p][:-1]==S2[p][:-1] if S[p][0]!='INIT' and S[p][0]!='CLEAR' else (p<n and S[p]==S2[p]): p+=1
    q=0
    while q<n-p and S[len(S)-1-q][:-1]==S2[len(S2)-1-q][:-1]: q+=1
    A=S[p:len(S)-q]; B=S2[p:len(S2)-q]
    from tkcommon import roles
    rl=roles(v.w); names={}
    def nm(r):
        if r not in names:
            role='o' if r>=v.n else {'helper':'h','X':'x','Y':'y'}.get(rl(r),'p')
            names[r]=role+str(len(names))
        return names[r]
    def fmt(ev): return ';'.join('%s(%s%s%s)'%(e[0][:2],nm(e[1]),('<-'+nm(e[2])) if e[0] in('ADD','COPY') else '',(',%s'%e[3]) if e[0]=='ADD' else (',%s'%e[2] if e[0]=='SCALE' else '')) for e in ev if e[0] not in('INIT','CLEAR') or True)
    return fmt(A)+' => '+fmt(B)
def trace_key(S2,lo,hi): return tuple(sorted(tuple(e) for e in S2[lo:hi]))
def windows_for(v,kind,W):
    out=[]
    if kind in('owned','all'): out+=CM.owned_windows(v,W)
    if kind in('hub','all'): out+=CM.hub_windows(v,W)
    if kind in('random','all'): out+=CM.random_windows(v,W)
    seen=set(); res=[]
    for w in out:
        if w not in seen: seen.add(w); res.append(w)
    return res
def run(word,kind='owned',W=8,shard=(0,1),out=None,depth=3,tl=30,tol=1e-5,beam=100,maxw=0,log=print,exact_top=3,windows=None,candidate_dir=None,must_lift=False):
    from tkcommon import load
    p,w=load(word); w=M.pin(w); v=M.View(w); S0=v.S
    for _ in range(6): M.quick(v,S0)
    k0=M.quick(v,S0)[0]; k0e=M.evaluate(w)['kappa']
    wins=windows if windows is not None else windows_for(v,kind,W)
    tot=len(wins); wins=[x for i,x in enumerate(wins) if i%shard[1]==shard[0]]
    if maxw: wins=wins[:maxw]
    fo=open(out,'a') if out else None; summ=collections.Counter(); t0=time.time(); best=None
    for (lo,hi) in wins:
        st=collections.Counter()
        try: res=CM.search(v,lo,hi,depth=depth,tol=tol,beam=beam,tl=tl,stats=st,k0=k0,must_lift=must_lift)
        except (Block,ValueError,KeyError,IndexError) as ex: summ['err']+=1; continue
        summ['windows']+=1; summ['legal']+=st['legal']; summ['children']+=st['children']; summ['notequiv']+=st['NOTEQUIV']
        seen=set(); dist=[]
        for r in res:
            kk=trace_key(r['S'],r['lo'],r['hi'])
            if kk in seen: continue
            seen.add(kk); dist.append(r)
        if not dist: continue
        summ['windows_improving']+=1
        for r in dist[:exact_top]:
            try: w2=v.rebuild(r['S']); o=M.evaluate(w2)
            except Exception as ex: o=dict(legal=False,why=repr(ex)[:80])
            rec=dict(word=word,lo=lo,hi=hi,gain_quick=r['gain'],legal=bool(o.get('legal')),ok=bool(o.get('ok')),gain_exact=(o['kappa']-k0e) if o.get('legal') else None,path=[list(map(str,x)) for x in r['path']],tags=r['tags'],sig=sig_of(S0,r['S'],v),n_distinct=len(dist))
            if fo: fo.write(json.dumps(rec)+'\n'); fo.flush()
            if o.get('legal') and rec['gain_exact']>1e-15:
                summ['exact_improving']+=1
                if best is None or rec['gain_exact']>best[0]:
                    best=(rec['gain_exact'],rec)
                    if candidate_dir:
                        json.dump(w2,gzip.open(os.path.join(candidate_dir,'CANDIDATE-%s-%d-%d.json.gz'%(word,lo,hi)),'wt'))
            log('window %d-%d: %+.3e quick, exact %s, tags %s, %s'%(lo,hi,r['gain'],rec['gain_exact'],r['tags'],rec['sig'][:140]))
    summ['total_windows_in_kind']=tot; summ['shard_windows']=len(wins); summ['wall']=round(time.time()-t0,1)
    if fo: fo.write(json.dumps(dict(summary=dict(summ),word=word,kind=kind,W=W,shard=list(shard),depth=depth,tl=tl,tol=tol,beam=beam))+'\n'); fo.close()
    log('SUMMARY',dict(summ)); return best
def main():
    os.environ.setdefault('TK_FREE_BOUNDS','1')
    import argparse
    ap=argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('word'); ap.add_argument('--kind',default='owned'); ap.add_argument('--W',type=int,default=8); ap.add_argument('--shard',default='0/1')
    ap.add_argument('--out'); ap.add_argument('--depth',type=int,default=3); ap.add_argument('--tl',type=float,default=30); ap.add_argument('--tol',type=float,default=1e-5); ap.add_argument('--beam',type=int,default=100); ap.add_argument('--max',type=int,default=0)
    ap.add_argument('--candidate-dir'); ap.add_argument('--must-lift',action='store_true'); a=ap.parse_args()
    run(a.word,a.kind,a.W,tuple(int(x) for x in a.shard.split('/')),a.out,a.depth,a.tl,a.tol,a.beam,a.max,candidate_dir=a.candidate_dir,must_lift=a.must_lift)
if __name__=='__main__': main()
