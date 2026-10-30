#!/usr/bin/env python3
"""fastnative vs reference (infra/native_pair.py on the unmodified vendor kernels): identical per-pair outputs and verdicts.
usage:
  fastnative_test.py --quick                    regression: one small word (every 25th MOVE/helper pair of #5545) + 150 random pairs (nested, random, malformed); ~15 s
  fastnative_test.py --word W --side ref|fast --out F.json     all distinct pairs of word W (alias/path) -> {pair key: [ok,value]} (ref ~150 s, fast ~10 s)
  fastnative_test.py --compare A.json B.json    per-pair equality of two such files
  fastnative_test.py --mutants N --out F.json [--side ref(default, real comparison)|fast(dry run)]   N fuzz mutants (TKAUDIT fuzz op lists, #5580/#5551) -> new pairs + verdict per mutant
Exit 0 on success."""
import sys,os,json,time,random,argparse,copy,gzip
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.join(HERE,'..'); sys.path.insert(0,TKD); sys.dont_write_bytecode=True
from tkcommon import *
import native_pair as REF
import fastnative as FAST
def init_both():
    REF.init(closure_root()); FAST.init(closure_root(),ref=False)
def pairs_of(w):
    fr=w['frames']; main=set(w['live'])|{r+112 for r in w['live']}
    P={(e[2],e[3]) for e in w['program'] if e[0]=='MOVE'}|{(w['initial'][r],w['final'][r]) for r in range(len(w['initial'])) if r not in main}
    return sorted({(tuple(fr[a]),tuple(fr[b])) for a,b in P})
def pk(a,b): return ','.join(map(str,a))+'|'+','.join(map(str,b))
def rbasis(rnd,d):
    while True:
        b=[rnd.randrange(1,512) for _ in range(d)]; s={0}
        try:
            for v in b:
                assert v not in s; s|={x^v for x in s}
            return b
        except AssertionError: pass
def random_pairs(n,seed):
    rnd=random.Random(seed); out=[]
    for i in range(n):
        d=rnd.randrange(1,10); b=rbasis(rnd,d); k=rnd.randrange(0,d+1); kind=i%3
        if kind==0: out.append((tuple(rnd.sample(b,k)),tuple(b)))                        # nested subset
        elif kind==1: out.append((tuple(rbasis(rnd,rnd.randrange(0,9))),tuple(rbasis(rnd,rnd.randrange(0,10)))))   # unrelated (usually illegal)
        else: out.append((tuple(b),tuple(b[:k]+[b[j]^b[(j+1)%d] for j in range(k,d)] if d>1 else b)))      # perturbed
    return out
def cmp_pairs(prs):
    bad=[]
    for a,b in prs:
        r=REF.ok(a,b); f=FAST.ok(a,b)
        if r!=f: bad.append((a,b,r,f))
    return bad
def quick():
    init_both(); t=time.time()
    p,w=load('5545'); prs=pairs_of(w)[::25]+random_pairs(150,1)
    bad=cmp_pairs(prs); nfail=sum(1 for a,b in prs if not REF.ok(a,b)[0])
    print('fastnative_test --quick: %d pairs (%d illegal) in %.1fs, mismatches %d'%(len(prs),nfail,time.time()-t,len(bad)))
    for x in bad[:5]: print('  MISMATCH',x)
    assert nfail>=20,'test needs illegal pairs too'
    return 1 if bad else 0
def run_word(spec,side,out):
    N=REF if side=='ref' else FAST
    N.init(closure_root(),**({} if side=='ref' else {'ref':False}))
    p,w=load(spec); t=time.time(); res={}
    for a,b in pairs_of(w): res[pk(a,b)]=list(N.ok(a,b))
    json.dump(dict(word=spec,side=side,seconds=round(time.time()-t,1),n=len(res),all_ok=all(v[0] for v in res.values()),pairs=res),open(out,'w'))
    print('%s %s: %d pairs, all legal=%s, %.1fs'%(spec,side,len(res),all(v[0] for v in res.values()),time.time()-t))
def compare(fa,fb):
    A=json.load(open(fa));B=json.load(open(fb)); pa,pb=A['pairs'],B['pairs']
    diff=[k for k in set(pa)|set(pb) if pa.get(k)!=pb.get(k)]
    print('%s(%s %.0fs) vs %s(%s %.0fs): %d pairs, differences %d, verdict %s/%s'%(A['word'],A['side'],A['seconds'],B['word'],B['side'],B['seconds'],len(pa),len(diff),A['all_ok'],B['all_ok']))
    return 1 if diff or A['all_ok']!=B['all_ok'] else 0
def mutants(n,out,side):
    import fuzz_real as FR
    init_both(); rows=[];t=time.time(); seen=set(); mism=0; withnew=0
    global REF
    if side=='fast': REF=FAST      # dry run of the harness only (fast vs fast)
    for word in('5580','5551'):
        p,base=load(word); bp=set(pairs_of(base)); bad_base=[x for x in bp if not FAST.ok(*x)[0]]
        src=os.path.join(HERE,'..','ext','TKAUDIT','fuzz','fuzz_%s_single.jsonl'%word)
        cand=[json.loads(l) for l in open(src)]
        want=n//2
        # prefer mutants that touch frames of MOVEs / initial / final (the only ops that can change native pairs), then fill with the rest
        pri=[c for c in cand if any(o[0] in('final','init') or (o[0]=='set' and base['program'][o[1]%len(base['program'])][0]=='MOVE') for o in c['ops'])]
        rest=[c for c in cand if c not in pri]
        for c in (pri+rest)[:want]:
            w=FR.mutant(base,c['ops']); mp=set(pairs_of(w)); new=sorted(mp-bp)
            r=[REF.ok(a,b) for a,b in new]; f=[FAST.ok(a,b) for a,b in new]
            vr=all(x[0] for x in r) and not bad_base; vf=all(x[0] for x in f) and not bad_base
            # full verdict: every pair of the mutant (cached: base pairs identical for both)
            fr_all=all(REF.ok(a,b)[0] for a,b in mp); ff_all=all(FAST.ok(a,b)[0] for a,b in mp)
            withnew+=bool(new); ok_=(r==f and fr_all==ff_all); mism+=not ok_
            rows.append(dict(word=word,i=c['i'],ops=c['ops'],new_pairs=len(new),ref_verdict=fr_all,fast_verdict=ff_all,same=ok_,new_illegal=sum(1 for x in r if not x[0])))
    json.dump(dict(rows=rows,seconds=round(time.time()-t,1)),open(out,'w'),indent=0)
    print('mutants: %d (%d with new native pairs, %d with an illegal native verdict), mismatches %d, %.0fs'%(len(rows),withnew,sum(1 for r in rows if not r['ref_verdict']),mism,time.time()-t))
    return 1 if mism else 0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--quick',action='store_true'); ap.add_argument('--word'); ap.add_argument('--side',default=None); ap.add_argument('--out')
    ap.add_argument('--compare',nargs=2); ap.add_argument('--mutants',type=int); a=ap.parse_args()
    if a.quick: return quick()
    if a.word: return run_word(a.word,a.side or 'fast',a.out) or 0
    if a.compare: return compare(*a.compare)
    if a.mutants: return mutants(a.mutants,a.out or '/dev/null',a.side or 'ref')
    ap.print_help(); return 2
if __name__=='__main__': sys.exit(main())
