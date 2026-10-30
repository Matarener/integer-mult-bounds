#!/usr/bin/env python3
"""REALISEFIX differential gate for the edit-emitting plugin path (sedit.py).  For sampled sites of the prims (P1 P2 P3 P8), ibase and the macros (cofrm carry conj):
  SEdit.materialise == the list route's S2 (events, initial, final) | movekit.quick(SEdit) == quick(S2) (kappa and paid) | View.rebuild_edit program == rebuild_ref program |
  IncrWord.try_edit(SEdit) == try_edit(diff_edit(base, rebuilt)) (legal, kappa) on a subsample | Carry.sites == Carry.sites_ref (same edits, same order) on a window.
usage: tests/sedit_diff.py WORD [--stride K] [--max N] [--incr-every M] [--carry-window LO HI]"""
import sys,os,time,collections
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK); os.environ['TK_FREE_BOUNDS']='1'
import tkcommon,movekit as M,prims,macros,ibase,incr
import sedit as SE
A=sys.argv[1:]
def opt(k,d=None): return A[A.index(k)+1] if k in A else d
word=A[0]; stride=int(opt('--stride','7')); mx=int(opt('--max','400')); incr_every=int(opt('--incr-every','25'))
cw=tuple(int(x) for x in A[A.index('--carry-window')+1:A.index('--carry-window')+3]) if '--carry-window' in A else (13000,13060)
_,w=tkcommon.load(word); w=M.pin(w); v=M.View(w); P=prims.PLUGIN; ctx=P.prepare(v); cnt=collections.Counter(); bad=[]
for _ in range(M.DQ_AFTER+1): M.quick(v,v.S)
try:
    import prims_extra; prims_extra.register()
except Exception as ex: print('prims_extra n/a',ex)
iw=incr.IncrWord(w)
def compare(tag,ed,S2,ini,fin,se):
    if not (se.materialise(v.S)==S2 and (se.ini if se.ini is not None else v.w['initial'])==(ini or v.w['initial']) and (se.fin if se.fin is not None else v.w['final'])==(fin or v.w['final'])):
        cnt[tag+'_MAT_MISMATCH']+=1; bad.append((tag,'materialise',ed)); return
    k1=M.quick(v,se); k2=M.quick(v,S2,initial=ini,final=fin)
    if not (k1[0]==k2[0] and dict(k1[1])==dict(k2[1])): cnt[tag+'_QUICK_MISMATCH']+=1; bad.append((tag,'quick',ed,k1,k2)); return
    cnt[tag+'_ok']+=1
    if k2[0] is None: return
    try: w2=v.rebuild_ref(S2,initial=ini,final=fin)
    except ValueError: w2=None
    try: w3=v.rebuild_edit(se)
    except ValueError: w3=None
    if (w2 is None)!=(w3 is None) or (w2 is not None and w2['program']!=w3['program']): cnt[tag+'_REBUILD_MISMATCH']+=1; bad.append((tag,'rebuild',ed)); return
    cnt[tag+'_rebuild_ok']+=1
    if w2 is not None and cnt[tag+'_ok']%incr_every==0:
        r1=iw.try_edit(se); r2=iw.try_edit(incr.diff_edit(v.w,w2))
        if not (r1[0]==r2[0] and (r1[1]==r2[1] or (r1[1] is not None and abs(r1[1]-r2[1])<1e-18))): cnt[tag+'_INCR_MISMATCH']+=1; bad.append((tag,'incr',ed,tuple(r1)[:3],tuple(r2)[:3]))
        else: cnt[tag+'_incr_ok']+=1
t0=time.time()
for pn in ('P1','P2','P3','P8'):
    n=0; seen=0
    try: gen=P.sites(v,ctx,prims=(pn,))
    except Exception as ex: print(pn,'sites error',repr(ex)[:80]); continue
    for ed in gen:
        seen+=1
        if seen%stride: continue
        if n>=mx: break
        n+=1
        try: pr=P.parts(v,ed)
        except (prims.Block,ValueError,KeyError,IndexError,AssertionError,TypeError): pr='raised'
        try: se=P.sedit(v,ed)
        except (prims.Block,ValueError,KeyError,IndexError,AssertionError,TypeError): se='raised'
        if (pr=='raised')!=(se=='raised'): cnt[pn+'_RAISE_MISMATCH']+=1; bad.append((pn,'raise',ed)); continue
        if pr=='raised' or pr is None: cnt[pn+'_raised']+=1; continue
        compare(pn,ed,pr[0],pr[1],pr[2],se)
    print(pn,n,'sites [%.0fs]'%(time.time()-t0),flush=True)
# ibase / conj (pass-through of P3 sites) and macros
for mn in ('cofrm','conj'):
    m=macros.LIB[mn]; n=0; seen=0
    for ed in m.sites(v,ctx,window=None if mn=='conj' else cw):
        seen+=1
        if seen%stride: continue
        if n>=mx: break
        n+=1
        try: S2,ini,fin=(m.scalars(v,ed) if mn!='conj' else P.parts(v,ed['steps'][0]))
        except (prims.Block,ValueError,KeyError,IndexError,AssertionError,TypeError): S2='raised'
        try: se=m.sedit(v,ed)
        except (prims.Block,ValueError,KeyError,IndexError,AssertionError,TypeError,NotImplementedError): se='raised'
        if (S2=='raised')!=(se=='raised'): cnt[mn+'_RAISE_MISMATCH']+=1; bad.append((mn,'raise',ed)) if mn!='conj' else None; continue
        if S2=='raised': continue
        compare(mn,ed,S2,ini,fin,se)
    print(mn,n,'sites [%.0fs]'%(time.time()-t0),flush=True)
# ibase plugin
n=0
for ed in ibase.PLUGIN.sites(v,ibase.PLUGIN.prepare(v)):
    n+=1
    if n%(stride*5) or n>mx*stride*5: continue
    try: S2=ibase.PLUGIN.scalars(v,ed)
    except (ValueError,KeyError,IndexError,AssertionError): continue
    se=ibase.PLUGIN.sedit(v,ed); compare('ibase',ed,S2,None,None,se)
# carry: same sites in the same order
a=list(macros.LIB['carry'].sites(v,ctx,window=cw)); b=list(macros.LIB['carry'].sites_ref(v,ctx,window=cw))
if a!=b: cnt['CARRY_SITES_MISMATCH']+=1; bad.append(('carry',len(a),len(b)))
else: cnt['carry_sites_ok']+=len(a)
for ed in a[:max(1,mx//8)]:
    S2,ini,fin=macros.LIB['carry'].scalars(v,ed); compare('carry',ed,S2,ini,fin,macros.LIB['carry'].sedit(v,ed))
print('SEDIT_DIFF',word,dict(cnt),'MISMATCHES',sum(c for k,c in cnt.items() if 'MISMATCH' in k),'[%.0fs]'%(time.time()-t0))
for b_ in bad[:6]: print('  BAD',str(b_)[:300])
sys.exit(1 if bad else 0)
