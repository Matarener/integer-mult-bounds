"""k2.levers -- K2LEVERS lane (../module docstring): the generator levers as moves usable on any word.  Scope [TOOLING / k2 engine move families].
Engine-native (C++, k2levers.inc, runtime weights): 'lbirth' (late birth at the frame where the helper's pure-junk loads can be taken) and 'eend' (local early end).
This module adds the one lever that is NOT a local edit:
  eend_global(word): PUREX's end-early with the JOINT dim-0 junk solve (copied purex/purex2/ee0 in k2/purexlib/): enders = helpers whose x-content is redundant at their last
  non-F9 frame (Y relays at dim 8, optionally X-main splits at dims < 8); the dim-0 block is re-solved exactly (Z = I + Delta, transvections, dyadic) and the word re-realised.
  ROUTE-B words only: the dim-0 / body / F9 block structure is required (purex.Ctx); swarm words (e.g. #5907) raise NotBlockForm.
  sa(word, ...): k2 SA on a word (net round trip + validation), for chaining eend_global -> engine families.
No side effects at import (no env changes; TK_FREE_BOUNDS is set only inside eend_global and restored)."""
import os,sys,gzip,json,collections,tempfile,contextlib
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
class NotBlockForm(Exception): pass
@contextlib.contextmanager
def _env(k,v):
    old=os.environ.get(k); os.environ[k]=v
    try: yield
    finally:
        if old is None: os.environ.pop(k,None)
        else: os.environ[k]=old
def _paths():
    for p in (os.path.join(HERE,'purexlib'),TK,os.path.join(TK,'synth'),os.path.join(os.path.dirname(TK),'infra')):
        if p not in sys.path: sys.path.insert(0,p)
def block_form(w):
    """True iff the word has the route-B block structure purex needs (dim-0 Y loads / body / F9 block)."""
    _paths(); import purex as PX
    try: PX.Ctx(w); return True
    except AssertionError: return False
def canon_f9(w):
    """Float dim-0 ADDs into Ys to the front and every F9-frame ADD after all non-F9 ops when they commute (ADD r+=c*s writes r, reads s; ADDs into one register commute; SCALE/INIT/CLEAR/COPY do not),
    then re-realise lazily.  Restores the dim-0/body/F9 block form after engine moves interleaved F9 ops with the body.  returns word or None (a dependency forbids it)."""
    _paths(); import dag as D
    d=D.decompile(w,forms=False); fr=d['frames']; F9=max(range(len(fr)),key=lambda f:len(fr[f])); ops=d['ops']
    Z=[i for i in range(len(fr)) if len(fr[i])==0][0]; n=d['meta']['npub']; live=set(d['meta']['live'])
    isY=lambda r: r<n and (r-112) in live
    zy=[]; rest=[]; We=set(); Re=set(); Se=set()                     # leading block: dim-0 ADDs into Ys float to the front past commuting ops
    for o in ops:
        if o[0]=='ADD' and o[4]==Z and isY(o[1]) and o[2] not in We and o[2] not in Se and o[1] not in Re and o[1] not in Se: zy.append(o); continue
        rest.append(o); r=o[1]; s2=o[2] if o[0] in ('ADD','COPY') else None
        (We if o[0]=='ADD' else Se).add(r)
        if s2 is not None: Re.add(s2)
    ops=zy+rest
    body=[]; f9=[]; Wp=set(); Rp=set()
    for o in ops:
        if o[0]=='ADD' and o[4]==F9: f9.append(o); Wp.add(o[1]); Rp.add(o[2]); continue
        r=o[1]; s=o[2] if o[0] in ('ADD','COPY') else None
        if s is not None and s in Wp: return None                  # reads a register a pending F9 ADD writes
        if r in Rp: return None                                     # writes a register a pending F9 ADD reads
        if o[0]!='ADD' and r in Wp: return None                     # non-additive write vs pending ADD into r
        body.append(o)
    if ops==body+f9 and ops==d['ops']: return w
    d2=dict(d); d2['ops']=body+f9; d2.pop('schedule',None)
    w2,rep=D.realise(d2,schedule='lazy',verify=True)
    if rep['undelivered']: return None
    w2['verifier_profile']=dict(w.get('verifier_profile') or {}); return w2
def eend_global(w,dims=(4,8),xstops=True,maxn=None,verbose=False):
    """returns (word, info).  info: enders by end dim, kappa (IncrWord), legal, events, R0 by role."""
    _paths(); import purex as PX, purex2 as P2, kernel2net as KN, incr
    from tkcommon import profile_of
    with _env('TK_FREE_BOUNDS','1'):
        wc=canon_f9(w)
        if wc is not None: w=wc
        try: c0=PX.Ctx(w)
        except AssertionError as e: raise NotBlockForm(str(e))
        en=c0.census(maxn=maxn,xstops=xstops,dims=set(dims) if dims else None)
        if not en: return w,dict(enders={},kappa=None,note='no enders')
        c,body,f9,zops,Delta=P2.run(w,en,verbose=verbose)
        E={e['h']:e for e in en}; ops=P2.finish(c,body,f9,zops,E,verbose=verbose)
        bad=[o for o in ops if o[0]=='ADD' and not PX.dy(o[3])]
        if bad: raise ValueError('non-dyadic coefficient %s'%bad[:2])
        dag=dict(c.d); dag['ops']=ops; dag['regs']={k:list(v) for k,v in c.d['regs'].items()}
        for h,e in E.items(): dag['regs'][str(h)][2]=e['f']
        w2,rep=c.D.realise(dag,schedule='lazy',verify=True)
        if rep['undelivered']: raise ValueError('realise: undelivered %s'%rep['undelivered'][:3])
        w2['verifier_profile']=dict(w.get('verifier_profile') or {})
        iw=incr.IncrWord(w2,profile=profile_of(w)[0])
        by,tot=KN.r0(w2)
        info=dict(enders=dict(collections.Counter(c0.dim[e['f']] for e in en)),zops=len(zops),kappa=iw.kappa,legal=iw.legal_all,viol=iw.viol[:3],events=len(w2['program']),R0={k:round(v,2) for k,v in by.items()})
    return w2,info
def sa(w,opts,mode='sa',compact=False,timeout=3600):
    """k2 engine run on a word: dump net, run, validate (python == C++, exact contract).  returns (word_or_None, validation dict, engine result)."""
    _paths(); import tkcommon,kernel2net as KN,k2search_validate as V
    from k2 import engine, screen
    name,_=tkcommon.profile_of(w); d=tempfile.mkdtemp(prefix='k2lev_')
    with tkcommon.use_profile(name):
        if compact: w,_=screen.compact(w,log=lambda *a:None)
        base=os.path.join(d,'base.json.gz'); json.dump(w,gzip.open(base,'wt')); net=os.path.join(d,'in.net'); KN.dump_net(w,net)
        out=os.path.join(d,'out.net'); o=dict(opts); o['out']=out; r=engine.run(net,mode,o,timeout=timeout)
        if not os.path.exists(out): return None,None,r
        res=V.validate(out,base,os.path.join(d,'out.json.gz'),exact=True)
    w2=json.load(gzip.open(res['word'],'rt')) if str(res['word']).endswith('.gz') else json.load(open(res['word']))
    return w2,res,r
if __name__=='__main__':
    a=sys.argv[1:]
    if not a or a[0] not in ('eend',):
        print('usage: python -B k2/levers.py eend IN.json.gz OUT.json.gz [--dims 4,8] [--no-xstops] [--max N]'); sys.exit(2)
    _paths(); import tkcommon
    w=tkcommon.load(a[1])[1]; dims=tuple(int(x) for x in a[a.index('--dims')+1].split(',')) if '--dims' in a else (4,8)
    w2,info=eend_global(w,dims=dims,xstops='--no-xstops' not in a,maxn=int(a[a.index('--max')+1]) if '--max' in a else None)
    print(json.dumps(info,default=str)); tkcommon.save_canonical(w2,a[2]); print('wrote',a[2])
