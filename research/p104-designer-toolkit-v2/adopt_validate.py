"""validation half of `tk adopt`: reproduce the PR's published crossing interval with (1) tk price (fast exact model), (2) tk check --native, (3) tk accept (the vendored stack of the
PR's OWN local.py / pricing.py, run unpatched and with the toolkit's claim-literal patch), and print a precise diff of what the toolkit does not model when anything differs."""
import sys,os,json,gzip,time,decimal,hashlib
from fractions import Fraction as Q
import tkcommon
from tkcommon import *
import tkstack
def _f(s): return float(Q(s))
def interval_of(o): return [o['crossing_lo'],o['crossing_hi']]
def diff_fast(prof,rep,T,P,side,bud,w):
    """model-vs-RESULT.json diff for the fast path: which census number / rule differs"""
    out=[]; c=prof['census']
    lg=[v for v in rep['violations']]
    if lg: out.append('legal.py rejects the PR\'s own word: %s  -> legality rule not modelled (use the PR\'s local.py via accept)'%['%s@%s'%(v[1],v[0]) for v in lg[:3]])
    for key,mine,theirs in (('paid',rep['paid'],c['paid']),('helpers',rep['helpers'],c['helpers'])):
        if key=='paid': continue
        d=tkstack.dict_diff(tkstack.norm(mine),theirs)
        if d: out.append('census %s differs (legal.py vs RESULT local): %s'%(key,d[:4]))
    for k,mine,theirs in (('lifetimes',rep.get('lifetimes'),c['owned_lifetimes']),('peak',rep.get('owned_peak'),c['peak_owned_fields'])):
        if mine!=theirs: out.append('owned %s: toolkit %s vs RESULT %s'%(k,mine,theirs))
    if sum(P.values())!=c['paid_calls'] or sum(T.values())!=c['productive_fields']:
        out.append('invoice totals: toolkit paid_calls %d fields %d vs RESULT %s / %s'%(sum(P.values()),sum(T.values()),c['paid_calls'],c['productive_fields']))
    if c.get('local_routes') is not None and bud['routes']!=c['local_routes']:
        out.append('route budget: toolkit %d vs RESULT local_routes %d  (price_exact.budgets formula or owned-lifetime term)'%(bud['routes'],c['local_routes']))
    if c.get('real_scalar_allowance') is not None and bud['scalar']!=c['real_scalar_allowance']:
        out.append('scalar allowance: toolkit %d vs RESULT %d (scalar cost rule)'%(bud['scalar'],c['real_scalar_allowance']))
    return out
def check_side(prof,res,side):
    """alpha/gamma/delta of the toolkit vs the PR's strictification enclosures (float vs enclosure at the TESTED point; informative)"""
    st=res.get('complete_cost',{}).get('strictification') or {}
    out=[]
    for k in('alpha','gamma','delta'):
        e=st.get(k)
        if e and isinstance(e,dict) and 'upper' in e:
            if not(side[k]<=float(e['upper'])+1e-9): out.append('%s toolkit %.12f > PR upper %s'%(k,side[k],e['upper']))
    return out
def validate(rec,say=print,accept=True):
    prof=rec['profile']; alias=prof['alias']; path=rec['word']; res=dict(alias=alias,steps={},ok=True,notes=[])
    import legal,price,check,accept as A
    import price_exact as X
    w=legal.load(path); exp=prof['expect']['interval']
    with tkcommon.use_profile(alias):
        # 1. fast price
        t=time.time(); o=price.fast(path,w,use_cache=False); got=interval_of(o)
        ok1=got==exp
        rep=legal.check(w); T,P=X.invoice(rep); bud=X.budgets(rep)
        res['steps']['price']=dict(ok=ok1,got=got,expect=exp,legal=o['legal'],side_ok=o['side']['ok'],seconds=round(time.time()-t,1))
        if not ok1 or not o['legal']:
            res['ok']=False; res['steps']['price']['diff']=diff_fast(prof,rep,T,P,o['side'],bud,w)
        else:
            # informational cross-checks even when the interval reproduces
            d=diff_fast(prof,rep,T,P,o['side'],bud,w)
            if d: res['steps']['price']['notes']=d
        # 2. check --native
        t=time.time(); role=roles(w); nat=check.native_check(w,w['program'],role)
        ok2=o['legal'] and nat['nbad']==0; res['steps']['check_native']=dict(ok=ok2,legal=o['legal'],pairs=nat['distinct_pairs'],bad=nat['nbad'],seconds=round(time.time()-t,1))
        if not ok2: res['ok']=False; res['steps']['check_native']['first_bad']=nat['bad'][:3]
        # 3. accept via the vendored stack
        if accept and prof.get('stack'):
            exact=prof['expect']['raw_root_interval']
            for patched in (False,True):
                t=time.time(); r=tkstack.run_isolated(prof,path,patched=patched)
                key='accept_patched' if patched else 'accept_unpatched'
                if r.get('ok'):
                    ok3=([r['crossing_lo'],r['crossing_hi']]==exp) and (patched or r['raw_root_interval']==[str(Q(x)) for x in exact])
                    res['steps'][key]=dict(ok=ok3,got=[r['crossing_lo'],r['crossing_hi']],outer=r['outer_checks'],paid_calls=r['paid_calls'],fields=r['productive_fields'],seconds=round(time.time()-t,1))
                    if not ok3: res['ok']=False; res['steps'][key]['diff']=tkstack.dict_diff([r['crossing_lo'],r['crossing_hi']],exp)
                else:
                    res['ok']=False; res['steps'][key]=dict(ok=False,stage=r.get('stage'),error=r.get('error'),seconds=round(time.time()-t,1))
        elif accept: res['ok']=False; res['steps']['accept']=dict(ok=False,error='no vendored stack (see unmodelled)')
    return res
def finish(rec,a):
    prof=rec['profile']; alias=prof['alias']
    for u in rec['unmodelled']: print('UNMODELLED: '+u)
    if not prof.get('stack'):
        print('tk adopt %s: no authoritative stack could be assembled from the PR; profile NOT registered'%alias); return 1
    # the alias word must be the PR's word: warn if the shipped toolkit word differs
    wdst=HERE+'/words/%s.json.gz'%alias
    if os.path.exists(wdst) and hashlib.sha256(open(wdst,'rb').read()).hexdigest()!=prof['expect']['word_sha256']:
        raw=gzip.decompress(open(wdst,'rb').read()); praw=gzip.decompress(open(rec['word'],'rb').read()) if rec['word'].endswith('.gz') else open(rec['word'],'rb').read()
        if json.loads(raw)!=json.loads(praw): print('NOTE: toolkit words/%s.json.gz differs from the PR head word (alias word is from another head); validating the PR head word %s'%(alias,rec['word']))
    from adopt import write_profile
    write_profile(prof); tkcommon._load_data_profiles()
    res=validate(rec,accept=not a.no_accept)
    prof['validation']=dict(date=time.strftime('%Y-%m-%d'),ok=res['ok'],steps=res['steps'])
    # does the legacy auto-selection for this family agree with the derived constants?  if not, the data profile must win automatically
    w=json.load(gzip.open(rec['word'])) if rec['word'].endswith('.gz') else json.load(open(rec['word']))
    leg=tkcommon.PROFILES[tkcommon._legacy_auto(w)]
    differs=[k for k,v in (('decay',prof['compiler']['decay_f']),('reserve',prof['compiler']['reserve_f']),('peak',prof['peak']),('lifetimes',prof['lifetimes'])) if leg.get(k) is not None and leg.get(k)!=v]
    prof['auto']=bool(differs and (tkcommon._legacy_auto(w)!='default' or len(w['initial'])>737))
    if differs: print('NOTE: legacy profile %s differs from the PR in %s -> data profile %s takes precedence for this family (auto)'%(tkcommon._legacy_auto(w),differs,alias))
    write_profile(prof); tkcommon._load_data_profiles()
    if a.json: print(json.dumps(res,indent=1,default=str)); return 0 if res['ok'] else 1
    print('tk adopt PR%s (%s, %s): profile public %d owned %s lifetimes %s peak %s | decay %s power %s reserve %s | expect %s'%(prof['pr'],prof['package'].split('/')[-1],prof['head'][:10],prof['public'],prof['owned_fields'],prof['lifetimes'],prof['peak'],prof['compiler']['decay'],prof['compiler']['power'],prof['compiler']['reserve'],prof['expect']['interval']))
    for k,v in res['steps'].items():
        print('  %-18s %s  %s'%(k,'PASS' if v['ok'] else 'FAIL',{x:y for x,y in v.items() if x not in('ok','diff','notes')}))
        for d in v.get('diff') or []: print('      DIFF '+str(d))
        for d in v.get('notes') or []: print('      note '+str(d))
    print('RESULT: %s'%('ADOPTED, all published interval(s) reproduced' if res['ok'] else 'NOT reproduced -- see DIFF lines (profile is written but flagged validation.ok=false)'))
    return 0 if res['ok'] else 1
