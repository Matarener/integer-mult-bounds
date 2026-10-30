#!/usr/bin/env python3
"""GENBUDGET tests.  usage: admit_test.py [--full]
 1. admit.py agrees with the PR's OWN pricing.run on adopted words: alpha/gamma/delta inside the certified intervals, local scalar + routes equal, raw bound, verdict ok (quick: 5756; --full: + 5751 5718 5739 5713)
 2. negative controls: patch one literal of the real pricing.py (decay, reserve, scalar cap, cutoff c/b) -> real run rejects, oracle rejects the SAME constraint family (--full or quick for decay + scalar)
 3. oracle-only: event cap / scalar cap literals flagged with the right slack sign; best() admits 5756 at its own literals
 4. synth.compact: value/legality preserving on adopted words and on the FRONTGEN word (if out/frontgen_star.json.gz exists): events down, same final values, same paid MOVEs"""
import sys,os,json,gzip,copy
TD=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,TD+'/..')
from fractions import Fraction as Q
from tkcommon import *
import admit as AD, tkstack
full='--full' in sys.argv
bad=0
def need(c,what):
    global bad
    print(('PASS ' if c else 'FAIL ')+what,flush=True); bad+=not c
def inside(x,iv,tol=1e-24): return float(iv['lower'])-tol<=x<=float(iv['upper'])+tol
def real(alias,patch=None):
    old=tkstack.patched_source
    if patch:
        def ps(prof,path,w,local,native):
            src,vals=old(prof,path,w,local,native)
            for a,b in patch:
                assert a in src,('patch target missing',a); src=src.replace(a,b)
            return src,vals
        tkstack.patched_source=ps
    try: return tkstack.stack_accept(tkstack.profile(alias),ALIASES[alias],patched=True)
    finally: tkstack.patched_source=old
def D(x): return Q(str(x))
def oracle(alias,r,**over):
    cl=r['claim']; lit=AD.lits_of(alias); lit.update(over)
    return AD.check(ALIASES[alias],lit=lit,tested=D(cl['TESTED']),claim=D(cl['KAPPA']),profile=alias)
byname=lambda rep:{x['name']:x for x in rep['constraints']}
words=['5756']+(['5751','5718','5739','5713'] if full else [])
for a in words:
    if a not in ALIASES: print('SKIP',a); continue
    r=real(a)
    if not r['ok']: need(False,'%s real stack accepted (%s)'%(a,r['error'])); continue
    res=r['result']; S=res['strictification']; N=res['nonrecursive']; o=oracle(a,r); c=byname(o)
    al,ga,de=[inside(c[k]['value'],S[n]) for k,n in(('alpha<1-eps','alpha'),('gamma<D','gamma'),('delta<D','delta'))]
    need(al and ga and de,'%s oracle alpha/gamma/delta inside the real certified intervals'%a)
    need(c['scalar']['value']==N['local_scalar']+N['local_routes'],'%s oracle scalar units == real local_scalar+local_routes (%d)'%(a,c['scalar']['value']))
    need(18*10**7+AD.PHYS_RAW_CONST==N['raw_scalar_upper'],'%s raw bound constant == real raw_scalar_upper (%d)'%(a,N['raw_scalar_upper']))
    need(o['ok'],'%s oracle ADMITS what the real pricing accepts (fail: %s)'%(a,[x['name'] for x in o['constraints'] if not x['ok']]))
NEG=[('decay .95 (gamma fails)',[('Q(125,128)','Q(95,100)')],dict(decay=Q(95,100)),'gamma<D'),
     ('scalar cap 5e6',[('local_routes < 10**7','local_routes < 5*10**6')],dict(scalar_cap=5*10**6),'scalar'),
     ('reserve 1e-8 (alpha fails)',[('Q(1,10**12)','Q(1,10**8)')],dict(reserve=Q(1,10**8)),'alpha<1-eps'),
     ('cutoff c=60,b=64 (c^64<b^63 fails)',[('1024,16,17','1024,60,64')],dict(c=60,b=64),'tail c^64<b^63')]
for nm,patch,over,fam in (NEG if full else NEG[:1]):
    try: r=real('5756',patch)
    except AssertionError as e: need(False,'negative control %s: patch target missing %s'%(nm,e)); continue
    o=oracle('5756',r,**over) if r['ok'] or r.get('stage')=='price.run' else None
    fails=[x['name'] for x in o['constraints'] if not x['ok']] if o else []
    need((not r['ok']) and r.get('stage')=='price.run' and fam in fails,'negative control %s: real rejects (%s) and oracle fails %s (%s)'%(nm,(r.get('error') or '')[:50],fam,fails))
# oracle-only
rep=AD.check('5756'); need(rep['ok'],'5756 admissible at its own literals')
lit=AD.lits_of('5756'); lit['event_cap']=25000
rr=AD.check('5756',lit=lit); need(not byname(rr)['events']['ok'] and byname(rr)['events']['slack']==25000-25844,'event cap 25000 rejects 5756 with slack -844')
b=AD.best('5756'); need(b['admits_any'] and b['strict_ok'],'best(5756): admits, strict literals suffice, no literal change needed (%s)'%b['changes'])
# synth.compact
from synth import compact as CP
for a in('5756','5551'):
    p,w=load(a); nw,st=CP.compact(w,native=False)
    need(st['values_equal'] and st['legal_after'] and st['events_after']<=st['events_before'] and st['paid_after']==st['paid_before'],'compact %s: values equal, legal, events %d -> %d, scalar %d -> %d'%(a,st['events_before'],st['events_after'],st['scalar_before'],st['scalar_after']))
fg=TD+'/../out/frontgen_star.json.gz'
if os.path.exists(fg):
    os.environ['TK_FREE_BOUNDS']='1'; os.environ['TK_PROFILE']='5756'
    w=legal.load(fg); nw,st=CP.compact(w,native=False)
    need(st['values_equal'] and st['legal_after'] and st['events_after']<=st['events_before']-20000 and st['scalar_after']<st['scalar_before'],'compact FRONTGEN: values equal, legal, events %d -> %d, scalar %d -> %d'%(st['events_before'],st['events_after'],st['scalar_before'],st['scalar_after']))
    # mutation control: a corrupted compact result must be caught by the equality check (flip one CSE ADD coefficient)
    bad_w=copy.deepcopy(nw); i=next(k for k,e in enumerate(bad_w['program']) if e[0]=='ADD'); bad_w['program'][i][3]='7/2'
    r1=legal.check(bad_w,K=4); r0=legal.check(nw,K=4); need((not r1['ok']) and r0['ok'],'compact verify catches a corrupted coefficient')
sys.exit(1 if bad else 0)
