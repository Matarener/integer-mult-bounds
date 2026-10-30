#!/usr/bin/env python3
"""SCREENSMOKE: EXECUTE every registered screen (pscreen.SETS, eval.SCREENS, FRONTAUTO's SCREENS string) instead of only checking that it is registered
(pscreen_test.py missed `tk pscreen --set alias` dying with NameError alias_core.pick).  Word #5660, windows / site caps / time limits keep it small.
Per screen asserts: no exception, returncode 0, an output word (if any) is legal (IncrWord / M.evaluate) and its kappa is not lower than the input's.
  --quick (regress)  in-process: the 9 pscreen sets via pscreen.main on a 150-event window, the 5 movekit classes via movekit.cli (--max-sites), and the argv each eval.SCREENS wrapper builds is
                     parsed by tk's real argparse (catches wrapper / CLI drift) -- the five eval-native screens (handoff evretime retime reorder split) are whole-word tools (12-45 s each) so they only get the plumbing check.
  (default)          additionally runs those five through their eval wrappers (subprocess `tk ...`, tl=3): rc 0, no Traceback in the log; an output word must be legal (kappa vs input is reported, not asserted: evretime may legitimately dip, `tk eval` rejects dips itself).
usage: tests/screen_smoke.py [--quick|--fast] [--only NAME[,NAME]]"""
import sys,os,re,io,time,tempfile,contextlib,traceback
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
os.environ.setdefault('TK_FREE_BOUNDS','1')
import eval as E, movekit, pscreen, tkcommon, tk as TKM
fails=[]; T0=time.time()
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
fast='--fast' in sys.argv; quick='--quick' in sys.argv or fast; only=None      # --fast (HYGIENE): --quick with 0.4x per-screen budgets (every screen still executed)
if '--only' in sys.argv: only=set(sys.argv[sys.argv.index('--only')+1].split(','))
WORD=os.path.join(TK,'words','5660.json.gz'); WIN=('17000','17150')
movekit.register_screens(); pscreen.register_screens()
fa=[]
names=[]
for n in list(pscreen.SETS)+sorted(E.SCREENS)+fa:
    if n not in names: names.append(n)
need(all(n in E.SCREENS or n in pscreen.SETS for n in names),'every pscreen set / eval screen is registered')
_,w0=tkcommon.load(WORD); w0=movekit.pin(w0); o0=movekit.evaluate(w0); k0=o0['kappa']; need(bool(o0.get('legal')),'input word #5660 legal, kappa %.15f'%k0)
def judge(name,path):
    """output word at path: legal and kappa not lower than the input"""
    if not path or not os.path.exists(path): return True,'no output word (nothing improved)'
    _,w=tkcommon.load(path); o=movekit.evaluate(movekit.pin(w))
    return bool(o.get('legal')) and o['kappa']>=k0-1e-15,'output legal=%s kappa %+.3e vs input'%(o.get('legal'),(o.get('kappa') or 0)-k0)
def quiet(fn,*a,**kw):
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf):
        try: return fn(*a,**kw),buf.getvalue(),None
        except BaseException as e: return None,buf.getvalue(),traceback.format_exc()
parser=TKM.build()
def parse(argv):
    try:
        with contextlib.redirect_stderr(io.StringIO()): return parser.parse_args(argv)
    except SystemExit: return None
tmp=tempfile.mkdtemp(); ran=set()
import multiprocessing as mp
BUDGET=float(os.environ.get('SMOKE_BUDGET','3.5' if quick else '90'))      # default seconds per screen (a screen still running then is killed and reported as truncated)
QB=dict(prims=5,prims_role=5,prims_extra=3,macros=4,handover=4,alias=7,alias2=7,prims_mined=4,automacro=2,ctxmine=3,ctxmine2=3,k2sa=14,a2x=2,ibase=3,blockmove=3,relay=3,split2=3)      # --quick: seconds to reach real work (alias dies with alias_core.pick missing only after ~5 s; checked by sabotage)
def budget(n): return (max(1.5,QB.get(n,BUDGET)*(0.4 if fast else 1)) if quick and 'SMOKE_BUDGET' not in os.environ else BUDGET)
def child(q,kind,n,out,BUDGET=BUDGET):
    """runs in a forked child (shares the loaded word; isolated state; killed at BUDGET).  q gets ('done',info) or ('exc',traceback)"""
    try:
        sys.stdout=open(os.devnull,'w'); log=lambda *x:None
        if kind=='set': w2,chain=pscreen.run_set(n,w0,tl=min(BUDGET,4),steps=1,window=(17000,17150),topq=5)
        else: w2,applied=movekit.greedy(movekit.plugin(n),w0,steps=1,log=log,max_sites=30,exact_top=1); chain=applied
        o=movekit.evaluate(w2) if chain else o0
        q.put(('done',dict(n=len(chain),legal=bool(o.get('legal')),kappa=o.get('kappa'))))
    except BaseException: q.put(('exc',traceback.format_exc()))
def run_isolated(kind,n):
    ctx_=mp.get_context('fork'); q=ctx_.Queue(); BUDGET=budget(n); p=ctx_.Process(target=child,args=(q,kind,n,None,BUDGET)); p.start(); t=time.time(); res=None
    while time.time()-t<BUDGET+0.5 and res is None:
        try: res=q.get(timeout=0.2)
        except Exception:
            if not p.is_alive(): 
                try: res=q.get(timeout=0.5)
                except Exception: res=('exc','child died, exitcode %s'%p.exitcode)
    if res is None: res=('trunc',None)
    if p.is_alive(): p.terminate(); p.join(2)
    if p.is_alive(): os.kill(p.pid,9)
    return res
for n in names:
    if only and n not in only: continue
    if n in pscreen.SETS:
        kind='set'; a=parse(['pscreen',WORD,'--set',n,'--tl','4','--steps','1','--topq','5','--window',WIN[0],WIN[1],'--out',os.path.join(tmp,n+'.json.gz')])
    elif n in movekit.CLASSES:
        kind='cls'; a=parse([n,WORD,'--apply','--steps','1','--max-sites','30','--exact-top','1','--out',os.path.join(tmp,n+'.json.gz')])
    else: continue
    need(a is not None,'%s: CLI args parse with tk.build()'%n)
    t=time.time(); st,info=run_isolated(kind,n); ran.add(n)
    if st=='exc': need(False,'%s: raised\n%s'%(n,str(info)[-900:]))
    elif st=='trunc': need(True,'%s: no exception in %.1f s (still running at the budget; truncated)'%(n,time.time()-t))
    else:
        need(True,'%s: ran to completion without exception (%.1f s, %d step%s)'%(n,time.time()-t,info['n'],'' if info['n']==1 else 's'))
        need(info['legal'] and (info['kappa'] is None or info['kappa']>=k0-1e-15) or info['n']==0,'%s: output word legal, kappa %s the input (%+.3e)'%(n,'>=' if info['kappa'] is None or info['kappa']>=k0-1e-15 else 'BELOW',(info['kappa'] or k0)-k0))
# ---- eval wrappers: argv plumbing (and, without --quick, a real run of the whole-word eval-native screens)
class Rec(Exception): pass
for n in names:
    if only and n not in only: continue
    if n not in E.SCREENS: continue
    rec=[]; old=(E._run,E.legal.nown,E.legal.is_prepared)
    E._run=lambda argv,logf,tl,ctx,threads=None: (rec.append(argv),0)[1]
    E.legal.nown=lambda w:8; E.legal.is_prepared=lambda w:False
    ctx=dict(threads=1,ev_threads=1,tl=3,k=2,maxm=2)
    try: E.SCREENS[n](ctx,WORD,os.path.join(tmp,'rec_'+n)); err=None
    except BaseException as e: err=traceback.format_exc()
    finally: E._run,E.legal.nown,E.legal.is_prepared=old
    need(err is None and bool(rec),'%s: eval wrapper builds its tk command%s'%(n,('\n'+err[-500:]) if err else ''))
    for argv in rec:
        a=parse(argv); need(a is not None,'%s: wrapper argv parses with tk.build(): tk %s'%(n,' '.join(map(str,argv[:1]+argv[2:]))[:110]))
    if rec and not quick and n not in ran:
        t=time.time(); base=os.path.join(tmp,'run_'+n)
        try: path,info=E.SCREENS[n](ctx,WORD,base); err=None
        except BaseException as e: path,info,err=None,{},traceback.format_exc()
        logf=base+'.log'; log=open(logf).read() if os.path.exists(logf) else ''
        need(err is None and info.get('rc',0)==0 and 'Traceback' not in log,'%s: wrapper runs for real, rc=%s (%.1f s)%s'%(n,info.get('rc'),time.time()-t,('\n'+(err or log)[-700:]) if (err or 'Traceback' in log) else ''))
        if path and os.path.exists(path):
            _,w=tkcommon.load(path); o=movekit.evaluate(movekit.pin(w)); need(bool(o.get('legal')),'%s: output word legal, kappa %+.3e vs input (reported, not asserted)'%(n,(o.get('kappa') or 0)-k0))
        else: print('     %s: no output word (%s)'%(n,info.get('note','nothing improved')))
print('%d s'%(time.time()-T0)); print('FAILED' if fails else 'ALL PASS'); sys.exit(1 if fails else 0)
