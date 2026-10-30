"""tk price WORD [--real] [--wait] [--json]
Fast: exact invoice from the replay (infra/legal.py) -> kappa root (Decimal-50) + side constraints + budgets, ~0.5 s, cached by file sha.
--real: the real unmodified verifier stack (local.replay, reverse_columns, native, physical caller, price.run) via W/bin/hq.sh (~5 min), cached."""
import sys,os,json,time,decimal,subprocess
from tkcommon import *
def fast(path,w,use_cache=True):
    c,f=cache_get('price',path)
    if c and use_cache: c['cached']=True; return c
    rep=legal.check(w); T,P=X.invoice(rep)
    kd=X.kappa_dec(T,P,50); D=decimal.Decimal
    lo=(kd*10**14).to_integral_value(rounding=decimal.ROUND_FLOOR)/D(10**14)
    out=dict(word=os.path.basename(path),sha=sha(path)[:16],legal=rep['ok'],violations=[list(map(str,v)) for v in rep['violations'][:5]],
             kappa=str(kd)[:20],crossing_lo=str(lo),crossing_hi=str(lo+D(1)/D(10**14)),
             paid=rep['paid'],helpers=rep['helpers'],sumT=sum(T.values()),sumP=sum(P.values()),
             surplus=sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items()),
             side=X.side(T,P),budgets=X.budgets(rep),public=len(w['initial']),events=len(w['program']),cached=False)
    cache_put(f,out); return out
def matches(e,o):
    """claim e (decimal string) vs our root: >=14 decimals -> must be an end of the 1e-14 crossing interval; else equals the root truncated to its digits"""
    D=decimal.Decimal; d=len(e.split('.')[1]); k=D(o['kappa'])
    if d>=14: return D(o['crossing_lo'])<=D(e)<=D(o['crossing_hi'])
    return k.quantize(D(1).scaleb(-d),rounding=decimal.ROUND_FLOOR)==D(e)
def fmt(o):
    L=[]
    L.append('word %s  (sha %s, %d regs, %d events)'%(o['word'],o['sha'],o['public'],o['events']))
    L.append('kappa = %s   crossing interval [%s, %s]'%(o['kappa'],o['crossing_lo'],o['crossing_hi']))
    if not o['legal']: L.append('WARNING: word is ILLEGAL (tk check); the invoice below is unverified: %s'%o['violations'][:2])
    L.append('invoice: fields %d  paid calls %d  rank surplus %d   paid %s  helpers %s'%(o['sumT'],o['sumP'],o['surplus'],o['paid'],o['helpers']))
    s=o['side']; L.append('side: alpha %.10f gamma %.4f delta %.4f -> %s'%(s['alpha'],s['gamma'],s['delta'],'ok' if s['ok'] else 'FAIL'))
    b=o['budgets']; L.append('budgets: event slack %d, scalar slack %d%s'%(b['event_slack'],b['scalar_budget_slack'],'  (cached)' if o.get('cached') else ''))
    return '\n'.join(L)
def real_job(path,w,wait=False,TL=1800):
    c,f=cache_get('real',path)
    if c and ('interval' in c or 'error' in c): return c      # a partial file (job still running) is not a result
    name='tk_real_'+sha(path)[:10]
    submit(name,TL,[PY,'-B',HERE+'/real.py',path,'--out',f],wait)
    if not wait: return None
    return json.load(open(f)) if os.path.exists(f) else dict(error='no result; see %s'%(W+'/jobs/%s.log'%name))
def main(a):
    path,w=load(a.word); o=fast(path,w,not a.no_cache)
    if a.json: print(json.dumps(o,indent=1,default=str))
    else: print(fmt(o))
    exp=EXPECT.get(a.word)
    if exp: print('expected %s: %s'%(exp,'MATCH' if matches(exp,o) else 'MISMATCH'))
    if a.real:
        r=real_job(path,w,a.wait)
        if r is None: print('real stack submitted via hq.sh; rerun `tk price %s --real` (reads cache) when jobs/tk_real_*.done exists'%a.word)
        else: print('REAL:',json.dumps(r,default=str))
