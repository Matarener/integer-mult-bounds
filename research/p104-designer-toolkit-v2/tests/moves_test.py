#!/usr/bin/env python3
"""Tests for the move-class plugins (TKMOVES): tk ibase / a2x / blockmove / split2 on top of movekit.
usage: tests/moves_test.py [--quick] [--heavy]
 --quick  (default, single core, ~1-2 min): View.rebuild reproduces words exactly; every plugin REDISCOVERS its PR's move from the PR's base word at the PR's kappa
          (a2x #5643 on #5627, blockmove #5739 on #5713, split2 #5718 on #5713, ibase #5678 chain step 1 on #5660) and the exact edit applied by hand gives the PR's crossing interval;
          #5718 (744 public) is legal under the in-memory pin; blockmove composes onto #5718; plugins are registered in `tk <class>` and eval.SCREENS; negative controls.
 --heavy  full rediscovery by the drivers (queued by cpuq): ibase greedy on #5660 reaches #5678 (.003108158509803); a2x shard screen of #5627 ranks #5643's edit first."""
import sys,os,json,gzip,subprocess,tempfile,time
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.join(HERE,'..'); sys.path.insert(0,TKD); sys.dont_write_bytecode=True
PY=sys.executable; fails=[];n=0
def need(c,what):
    global n; n+=1; print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
def tk(*a,timeout=600):
    r=subprocess.run([PY,'-B',os.path.join(TKD,'tk.py')]+list(a),capture_output=True,text=True,timeout=timeout); return r.returncode,r.stdout+r.stderr
A=sys.argv[1:]; heavy='--heavy' in A; quick='--quick' in A or not heavy
import movekit as M, a2x, blockmove, split2, ibase
from tkcommon import *
WD=TKD+'/words/'
def W(a): return M.pin(legal.load(WD+a+'.json.gz'))
if quick:
    # 1. rebuild is exact (same paid multiset, same kappa, same event count) on the words the moves start from
    for a,k in(('5713','0.00310915224562'),('5718','0.00311024572012'),('5627','0.00310440547057')):
        w=W(a); v=M.View(w); w2=v.rebuild(v.S); o=M.evaluate(w); o2=M.evaluate(w2)
        need(o['legal'] and o2['legal'] and o['paid']==o2['paid'] and abs(o['kappa']-o2['kappa'])<1e-17 and len(w2['program'])==len(w['program']) and M.interval(w)['lo']==k,'View.rebuild reproduces %s (legal, paid multiset, kappa, events)'%a)
        kq,_=M.quick(v,v.S); need(abs(kq-o['kappa'])<1e-17,'quick() == evaluate() on %s'%a)
    # 2. a2x: #5643 from #5627
    w=W('5627'); v=M.View(w); pl=a2x.PLUGIN; ctx=pl.prepare(v)
    eds=[e for e in pl.sites(v,ctx) if e['i']==13039]
    PR=dict(i=13039,j=13040,t=388,s=715,u=340,c1='-4',c2='1',f2=396,P3=13040,f3=127)
    need(PR in eds,'a2x.sites rediscovers the #5643 edit on #5627')
    w2=pl.apply(v,PR); need(M.evaluate(w2)['ok'] and M.interval(w2)['lo']=='0.00310458658556','a2x edit -> #5643 crossing .00310458658556')
    kb=max(M.quick(v,pl.scalars(v,e))[0] or 0 for e in eds); need(abs(kb-M.evaluate(w2)['kappa'])<1e-16,'a2x: the best variant of the site is the #5643 kappa')
    # 3. blockmove: #5739 from #5713
    w=W('5713'); v=M.View(w); pl=blockmove.PLUGIN; ctx=pl.prepare(v)
    ed=dict(i0=11349,i1=11444,G=[79,80,82,90,91,92,94,95]); w2=pl.apply(v,ed); o=M.evaluate(w2)
    need(o['ok'] and M.interval(w2)['lo']=='0.00310927387521','blockmove PR edit (block of 96 ops, G suffix) -> #5739 crossing .00310927387521')
    found=[e for e in pl.sites(v,ctx)]
    need(len(found)>=1 and any(e['i0']==11349 and e['i1']==11444 and e['quick']>=o['kappa']-1e-16 for e in found),'blockmove.sites rediscovers the #5739 block at kappa >= the PR')
    need(M.evaluate(pl.apply(v,[e for e in found if e['i0']==11349][0]))['kappa']>=o['kappa']-1e-16,'blockmove best edit exact-confirmed by evaluate()')
    # 4. split2: #5718 from #5713
    pl=split2.PLUGIN; ctx=pl.prepare(v); t=time.time(); eds=list(pl.sites(v,ctx))
    need(any(e['p']==708 and e['F']==602 and e['s']==154 and e['q']=='1/2' for e in eds),'split2.sites rediscovers #5718 (pivot 708, chart 602, partner 154 q=1/2)')
    e=[e for e in eds if e['s']==154][0]; w2=pl.apply(v,e); o=M.evaluate(w2)
    need(o['ok'] and M.interval(w2)['lo']=='0.00311024572012' and len(w2['initial'])==744 and o['fields']==12976,'split2 edit -> #5718 crossing .00311024572012, 744 public, 12976 fields')
    bad=dict(e,q='1/4');
    try: ok_bad=not M.evaluate(pl.apply(v,bad)).get('ok')
    except AssertionError: ok_bad=True
    need(ok_bad,'negative control: a wrong partner coefficient is rejected by the endpoint-row assertion')
    # 5. #5718 under the in-memory pin; blockmove composes onto it (the merged-batch frontier)
    w5=W('5718'); o5=M.evaluate(w5); need(o5['ok'] and M.interval(w5)['lo']=='0.00311024572012' and w5.get('verifier_profile',{}).get('public')==744,'#5718 legal + side/budgets ok under verifier_profile public=744')
    v5=M.View(w5); pl=blockmove.PLUGIN; f5=list(pl.sites(v5,pl.prepare(v5)))
    need(len(f5)==1 and f5[0]['ops']==96 and M.evaluate(pl.apply(v5,f5[0]))['kappa']>o5['kappa']+1.2e-7,'blockmove on #5718: one site, +1.2e-7 (the #5739 move composed)')
    need(M.evaluate(pl.apply(v5,f5[0]))['legal'],'composed word legal')
    # 6. ibase: #5678 chain step 1 from #5660 (site proxy + exact edit)
    w=W('5660'); v=M.View(w); t=time.time(); ps=ibase.proxy_sites(v)
    need(len(ps)==658 and ps[0][0]==-3,'ibase.proxy_sites: 658 sites on #5660 (MOVES1026 census)')
    ED=dict(a=438,b=733,q='-4',s0=1090,s1=1313,ef=794,xf=127); w2=ibase.PLUGIN.apply(v,ED); o=M.evaluate(w2)
    need(o['ok'] and abs(o['kappa']-0.0031072018966577515)<1e-15,'ibase step 1 (438/733 conjugation) -> .0031072018966578 (+4.3855e-7)')
    CH=[dict(a=119,b=128,q='-1',s0=703,s1=704,ef=3,xf=602),dict(a=125,b=139,q='-1',s0=704,s1=705,ef=3,xf=602),dict(a=128,b=139,q='-1',s0=703,s1=704,ef=3,xf=602)]
    for e in CH: w2=ibase.PLUGIN.apply(M.View(w2),e)
    need(M.evaluate(w2)['ok'] and M.interval(w2)['lo']=='0.00310815850980','ibase 4-edit chain (438/733 + the 703 fan) reproduces #5678 .00310815850980')
    # 7. registration + CLI
    import eval as E; M.register_screens()
    need(all(c in E.SCREENS for c in M.CLASSES),'eval.SCREENS has ibase a2x blockmove split2')
    for c in M.CLASSES:
        rc,o=tk(c,'--help'); need(rc==0 and '--apply' in o and '--shard' in o,'tk %s --help'%c)
    rc,o=tk('blockmove',WD+'5713.json.gz','--edit',json.dumps(dict(i0=11349,i1=11444,G=[79,80,82,90,91,92,94,95])))
    need(rc==0 and 'gain +1.216e-07' in o,'tk blockmove --edit applies the PR edit (+1.216e-07)')
    rc,o=tk('split2',WD+'5713.json.gz','--edit',json.dumps(dict(p=708,c=12412,F=602,s=154,q='1/2')))
    need(rc==0 and 'gain +1.093e-06' in o,'tk split2 --edit applies the #5718 edit (+1.093e-06)')
if heavy:
    d=tempfile.mkdtemp(); out=d+'/ib.json.gz'
    rc,o=tk('ibase',WD+'5660.json.gz','--apply','--out',out,timeout=14400); k=M.evaluate(legal.load(out))['kappa'] if os.path.exists(out) else 0
    need(rc==0 and abs(k-0.003108158509803)<2e-15,'ibase greedy on #5660 reaches #5678 .003108158509803 (got %.15f)'%k)
    rc,o=tk('a2x',WD+'5627.json.gz','--list','3',timeout=14400); need('13039' in o.split('\n')[2] if len(o.split('\n'))>2 else False,'a2x full screen of #5627 ranks the #5643 site first')
print('\n%d tests, %d failed'%(n,len(fails)))
for f in fails: print('FAILED:',f)
sys.exit(1 if fails else 0)
