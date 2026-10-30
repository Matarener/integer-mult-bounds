"""ctxmine2_scan -- resumable batch driver of ctxmine2 (CTXMINE2).
 python3 -B ctxmine2_scan.py WORD --kind hub|owned|random|stride --name NAME [--shard i/n] [--depth 3] [--tl 9] [--beam 40] [--budget 13000] [--nrand 2000] [--seed 5]
Writes ext/CTXMINE2/out/NAME.prog (one line per finished window; resume skips them), NAME.jsonl (one line per improving rewrite, exact-confirmed) and, if every shard window is done, a RESULTS.md line.
 python3 -B ctxmine2_scan.py --summarize PREFIX...   -> coverage / counts over out/PREFIX*.prog.   Never sets env at import."""
import os,sys,json,gzip,time,collections,random
import movekit as M, ctxmine as CM, ctxmine2 as C2
from ctxmine_scan import sig_of,trace_key
from prims import Block
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,'ext','CTXMINE2','out'); RES=os.path.join(HERE,'ext','CTXMINE2','RESULTS.md')
def windows(v,kind,W=8,nrand=2000,seed=5):
    n=len(v.S)
    if kind=='hub': ws=CM.hub_windows(v,W,topn=8,per=10**6)
    elif kind=='owned': ws=CM.owned_windows(v,W)
    elif kind=='random': ws=[(i,i+W) for i in sorted(random.Random(seed).sample(range(n-W),nrand))]
    elif kind=='stride': ws=[(i,i+W) for i in range(0,n-W,W//2)]
    else: raise SystemExit('kind')
    out=[];seen=set()
    for x in ws:
        if x not in seen: seen.add(x); out.append(x)
    random.Random(1).shuffle(out)       # uniform partial coverage if a chunk is cut
    return out
def run(word,kind,name,W=8,shard=(0,1),depth=3,tl=9.0,beam=40,budget=13000,nrand=2000,seed=5,log=print,maxw=0):
    from tkcommon import load
    p,w=load(word); w=M.pin(w); v=M.View(w); S0=v.S
    for _ in range(6): M.quick(v,S0)
    k0=M.quick(v,S0)[0]; k0e=M.evaluate(w)['kappa']; num=C2.Num(S0,v.n)
    wins=windows(v,kind,W,nrand,seed); tot=len(wins); wins=[x for i,x in enumerate(wins) if i%shard[1]==shard[0]]
    if maxw: wins=wins[:maxw]
    prog=os.path.join(OUT,name+'.prog'); done=set()
    if os.path.exists(prog):
        for l in open(prog):
            try: done.add(tuple(json.loads(l)['w']))
            except Exception: pass
    fp=open(prog,'a'); fo=open(os.path.join(OUT,name+'.jsonl'),'a'); t0=time.time(); nd=0; stop=False
    for (lo,hi) in wins:
        if (lo,hi) in done: continue
        if time.time()-t0>budget: stop=True; break
        st=collections.Counter(); tw=time.time()
        try: res=C2.search2(v,num,lo,hi,depth=depth,beam=beam,tl=tl,k0=k0,stats=st)
        except (Block,ValueError,KeyError,IndexError) as ex: res=[]; st['err']+=1
        seen=set(); dist=[]
        for r in res:
            kk=trace_key(r['S'],r['lo'],r['hi'])
            if kk not in seen: seen.add(kk); dist.append(r)
        nimp=0
        for r in dist[:3]:
            try: w2=v.rebuild(r['S']); o=M.evaluate(w2)
            except Exception as ex: o=dict(legal=False)
            ge=(o['kappa']-k0e) if o.get('legal') else None
            fo.write(json.dumps(dict(word=word,lo=lo,hi=hi,gain_quick=r['gain'],legal=bool(o.get('legal')),ok=bool(o.get('ok')),gain_exact=ge,path=[list(map(str,x)) for x in r['path']],tags=r['tags'],sig=sig_of(S0,r['S'],v)))+'\n'); fo.flush()
            if ge is not None and ge>1e-15:
                nimp+=1; json.dump(w2,gzip.open(os.path.join(OUT,'CANDIDATE-%s-%s-%d-%d.json.gz'%(name,word,lo,hi)),'wt'))
                log('IMPROVING exact %+.3e window %d-%d %s'%(ge,lo,hi,r['path']))
        fp.write(json.dumps(dict(w=[lo,hi],legal=st['legal'],ch=st['children'],ne=st['NOTEQUIV'],k={a[2:]:b for a,b in st.items() if a.startswith('l_')},imp=len(dist),exact_imp=nimp,wall=round(time.time()-tw,1),trunc=bool(time.time()-tw>=tl)))+'\n'); fp.flush(); nd+=1
    fp.close(); fo.close()
    left=[x for x in wins if x not in done]
    ndone=sum(1 for l in open(prog)); 
    msg='CTXMINE2_%s: %s %s depth %d tl %g beam %d shard %d/%d -> %d/%d windows done%s (%s)'%(name,word,kind,depth,tl,beam,shard[0],shard[1],ndone,len(wins),' PARTIAL(budget)' if stop else '',os.path.join('ext/CTXMINE2/out',name+'.prog'))
    log(msg)
    if os.path.exists(os.path.dirname(RES)): open(RES,'a').write(msg+'\n')
def summarize(prefixes):
    cov=set();tot=collections.Counter();wall=0
    for fn in sorted(os.listdir(OUT)):
        if fn.endswith('.prog') and any(fn.startswith(p) for p in prefixes):
            for l in open(os.path.join(OUT,fn)):
                d=json.loads(l); tot['windows']+=1; tot['legal']+=d['legal']; tot['imp']+=d['imp']; tot['exact_imp']+=d['exact_imp']; tot['trunc']+=d['trunc']; tot['notequiv']+=d['ne']; wall+=d['wall']
                for k,c in d['k'].items(): tot['legal_'+k]+=c
                cov.update(range(d['w'][0],d['w'][1]))
    print(dict(tot),'events covered',len(cov),'cpu-h %.2f'%(wall/3600))
def main():
    import argparse
    if len(sys.argv)>1 and sys.argv[1]=='--summarize': return summarize(sys.argv[2:])
    os.environ.setdefault('TK_FREE_BOUNDS','1')
    ap=argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('--kind',default='hub'); ap.add_argument('--name',required=True); ap.add_argument('--shard',default='0/1')
    ap.add_argument('--depth',type=int,default=3); ap.add_argument('--tl',type=float,default=9); ap.add_argument('--beam',type=int,default=40); ap.add_argument('--budget',type=float,default=13000)
    ap.add_argument('--nrand',type=int,default=2000); ap.add_argument('--seed',type=int,default=5); ap.add_argument('--max',type=int,default=0); a=ap.parse_args()
    run(a.word,a.kind,a.name,shard=tuple(int(x) for x in a.shard.split('/')),depth=a.depth,tl=a.tl,beam=a.beam,budget=a.budget,nrand=a.nrand,seed=a.seed,maxw=a.max)
if __name__=='__main__': main()
