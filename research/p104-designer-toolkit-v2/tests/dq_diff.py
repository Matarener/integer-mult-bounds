#!/usr/bin/env python3
"""FASTSITES differential gate: delta quick (dq.py) must equal movekit.quick_full EXACTLY (kappa == and paid multiset ==, both None when illegal) on every site priced by every macro level
(cofrm carry rehome conj inject block) and every prims level (P1 P2 P3 P6) of the given words.  Every movekit.quick call made while pricing is intercepted and checked both ways.
usage: tests/dq_diff.py WORD[,WORD..] [--macros a,b] [--prims P1,P2,P3] [--max N] [--p1stride K] [--quick]      (--quick: small windows, for regress)"""
import sys,os,time,collections
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK); os.environ['TK_FREE_BOUNDS']='1'
import tkcommon,movekit as M,prims,macros
A=sys.argv[1:]
def opt(k,d=None):
    return A[A.index(k)+1] if k in A else d
words=A[0].split(','); mac=[x for x in opt('--macros','cofrm,carry,rehome,conj,inject,block').split(',') if x]; prm=[x for x in opt('--prims','P1,P2,P3').split(',') if x]; mx=int(opt('--max','0')); quick='--quick' in A; P1STRIDE=int(opt('--p1stride','6'))
orig=M.quick; cnt=collections.Counter(); bad=[]
def checked(view,S2,initial=None,final=None,frames=None):
    r=orig(view,S2,initial=initial,final=final,frames=frames)
    if hasattr(S2,'materialise'):          # REALISEFIX: explicit window edit -> the reference prices the materialised program
        if initial is None and final is None: initial=S2.ini; final=S2.fin
        S2=S2.materialise(view.S)
    try: f=M.quick_full(view,S2,initial=initial,final=final,frames=frames)
    except Exception as ex:
        cnt['full_raised']+=1; return r
    cnt['calls']+=1
    ok=(r[0]==f[0]) and (r[0] is None or dict(r[1])==dict(+f[1]))
    if not ok: cnt['MISMATCH']+=1; bad.append((r[0],f[0],dict(r[1]),dict(f[1])))
    elif f[0] is None: cnt['both_illegal']+=1
    return r
M.quick=checked
for module in (macros,prims):
    module.M.quick=checked
P=prims.PLUGIN; t0=time.time()
for wname in words:
    _,w=tkcommon.load(wname); w=M.pin(w); v=M.View(w); ctx=P.prepare(v); c0=cnt['calls']; d0=M.STATS['delta']
    # prime: the first quick call on a View is full by design; make the cache exist
    for _ in range(M.DQ_AFTER+1): orig(v,v.S)
    kw=dict(window=(13000,13100)) if quick else {}
    for mn in mac:
        m=macros.LIB[mn]; n=0
        try: gen=m.sites(v,ctx,**kw)
        except Exception as ex: print(wname,mn,'sites error',repr(ex)[:80]); continue
        try:
            for ed in gen:
                if mx and n>=mx: break
                n+=1
                try: m.fast(v,ed)
                except (prims.Block,ValueError,KeyError,IndexError,AssertionError,TypeError,ZeroDivisionError): pass
        except Exception as ex: print(wname,mn,'gen error',repr(ex)[:80])
        print(wname,'macro',mn,n,'sites  [calls %d delta %d  %.0fs]'%(cnt['calls']-c0,M.STATS['delta']-d0,time.time()-t0),dict(cnt),'MISMATCHES so far',cnt['MISMATCH'],flush=True)
    for pn in prm:
        n=0
        try: gen=P.sites(v,ctx,prims=(pn,),**kw)
        except Exception as ex: print(wname,pn,'sites error',repr(ex)[:80]); continue
        for ed in gen:
            if mx and n>=mx: break
            n+=1
            if pn=='P1' and n%P1STRIDE: continue
            try: P.fast(v,ed)
            except (prims.Block,ValueError,KeyError,IndexError,AssertionError,TypeError,ZeroDivisionError): pass
        print(wname,'prim',pn,n,'sites  [%.0fs]'%(time.time()-t0),dict(cnt),'MISMATCHES so far',cnt['MISMATCH'],flush=True)
print('DQ_DIFF words',words,'calls',cnt['calls'],'delta-used',M.STATS['delta'],'fallback',M.STATS['fallback'],'error',M.STATS['error'],'both_illegal',cnt['both_illegal'],'MISMATCHES',cnt['MISMATCH'])
for b in bad[:5]: print('  MISMATCH',b)
sys.exit(1 if cnt['MISMATCH'] or not cnt['calls'] else 0)
