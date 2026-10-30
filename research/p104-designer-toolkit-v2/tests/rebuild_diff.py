#!/usr/bin/env python3
"""FASTSITES gate: View.rebuild (incremental, dq.rebuild_splice) == View.rebuild_ref (full JIT rebuild) EXACTLY (program list, or the same exception) on edits of real words:
prims P1/P2/P3 sites, macro composites, plus random window splices (delete / duplicate / permute / reframe events, including ones that kill registers).
usage: tests/rebuild_diff.py WORD[,WORD..] [--n N] [--seed S]"""
import sys,os,random,time,collections
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK); os.environ['TK_FREE_BOUNDS']='1'
import tkcommon,movekit as M,prims,macros
A=sys.argv[1:]; words=A[0].split(','); N=int(A[A.index('--n')+1]) if '--n' in A else 3000; seed=int(A[A.index('--seed')+1]) if '--seed' in A else 1
cnt=collections.Counter(); bad=[]
def check(v,S2,tag):
    try: ref=v.rebuild_ref(S2)['program']; er=None
    except Exception as ex: ref=None; er=(type(ex).__name__,str(ex))
    try: got=v.rebuild(S2)['program']; eg=None
    except Exception as ex: got=None; eg=(type(ex).__name__,str(ex))
    cnt['n']+=1; cnt['n_'+tag]+=1
    if er is not None: cnt['raised']+=1
    if ref!=got or er!=eg: cnt['MISMATCH']+=1; bad.append((tag,er,eg,len(v.S),len(S2)))
P=prims.PLUGIN; rng=random.Random(seed); t0=time.time()
for wn in words:
    _,w=tkcommon.load(wn); w=M.pin(w); w=M.View(w).rebuild_ref(M.View(w).S); v=M.View(w); ctx=P.prepare(v); n0=M.STATS['rebuild_inc']          # canonical (JIT) base, as every adopted word of a search is
    for _ in range(M.RB_AFTER+1): v.rebuild(v.S)          # make the cache
    if not v.__dict__.get('_tj'): print(wn,'base program is not canonical JIT: incremental rebuild disabled (nothing to test)'); continue
    S=v.S; LIFE=[j for j,e in enumerate(S) if e[0] in('INIT','CLEAR')]
    for pn in ('P1','P2','P3'):
        k=0
        try: gen=P.sites(v,ctx,prims=(pn,))
        except Exception as ex: print('sites',pn,repr(ex)[:80]); continue
        for ed in gen:
            if k>=N: break
            k+=1
            try: pr=P.parts(v,ed)
            except Exception: continue
            if pr is None or pr[1] is not None or pr[2] is not None: continue
            check(v,pr[0],pn)
    for it in range(N):
        n=len(S); lo=rng.randrange(0,n+1); hi=min(n,lo+rng.choice([0,1,2,5,20,200])); mode=rng.choice(['del','dup','perm','frame','ins','rev','kill','kill','init'])
        win=[list(e) for e in S[lo:hi]]
        if mode=='del': new=[]
        elif mode=='dup': new=win+win
        elif mode=='perm': new=win[:]; rng.shuffle(new)
        elif mode=='rev': new=win[::-1]
        elif mode=='frame':
            new=win
            if new:
                j=rng.randrange(len(new)); e=new[j]; fr=rng.randrange(len(w['frames']))
                if e[0] in('INIT','CLEAR'): e[2]=fr
                else: e[-1]=fr
        elif mode in('kill','init'):
            op='CLEAR' if mode=='kill' else 'INIT'; idx=[j for j in LIFE if S[j][0]==op]
            new=win
            if idx: new=win+[list(S[rng.choice(idx)])]
            if mode=='init' and idx and rng.random()<.5: new=[e for e in win if e[0]!='INIT']
        else:
            new=win
            if S:
                e=list(S[rng.randrange(n)]); new=win+[e]
        S2=S[:lo]+new+S[hi:]; check(v,S2,'rand_'+mode)
    print(wn,'checked',cnt['n'],'incremental used',M.STATS['rebuild_inc']-n0,'errors(raised by ref)',cnt['raised'],'MISMATCH',cnt['MISMATCH'],'%.0fs'%(time.time()-t0),flush=True)
print('REBUILD_DIFF checked',cnt['n'],'MISMATCHES',cnt['MISMATCH'],'inc',M.STATS['rebuild_inc'],'inc_err',M.STATS['rebuild_err'])
for b in bad[:5]: print('  MISMATCH',b)
sys.exit(1 if cnt['MISMATCH'] or M.STATS['rebuild_err'] else 0)
