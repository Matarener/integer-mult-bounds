"""tk split WORD [--apply] [--max N] [--out F] [--public-cap 750|0] [--event-cap 26000|0]
Independent helper-split screen + greedy applier (SPLITGEN lane).  Move class = #5599's 'independent helper splits': at a common-chart cut after a MOVE,
a helper combination (row a, column b; prefix image c and suffix image d supported on one helper group, ab=cd=1) finishes early at the intermediate chart F
and a fresh independent input z at F replaces it: one H(dimV-dimU) target becomes H(dimF-dimU)+H(dimV-dimF).  Paid calls are untouched; the gain is more productive fields
(concavity of the target moment).  Eligibility = vendored search.candidates (splitvendor/, #5599 package, Ali Romman + Codex, Apache-2.0): group of non-main roles
with common (initial,final), strictly nested intermediate chart F, pure row/column pairing, dyadic basis programs.
For every hit the split is built (construct.split), replayed by the package's local.replay (paid multiset unchanged), checked with legal.check, and priced exactly with the word's profile
(env TK_PROFILE; default by public count).  Greedy: apply best dkappa, rescan (cut indices move), repeat.  Caps: public registers <= --public-cap (package local.py: 750; 0 = off), events <= --event-cap (26000).
Per-split side check also reports the smallest tail decay D in {39/40,...,.99} for which side() is ok (PARAMS lane: D, log power are free per package).
Native check of a result: `tk check OUT --native` (fastnative)."""
import sys,os,json,gzip,copy,time,decimal
from tkcommon import *
V=HERE+'/splitvendor'
import sys as _s
if '--public-cap' in _s.argv:
    _c=int(_s.argv[_s.argv.index('--public-cap')+1]); os.environ['TK_SPLIT_PUBMAX']=str(_c if _c else 10**6)
if V not in sys.path: sys.path.insert(0,V)
import local as L, construct as C, search as S
from collections import defaultdict
D_GRID=[0.97,0.975,0.98,0.985,0.99]
def screen(w):
    mains=set(w['live'])|{r+112 for r in w['live']}; groups=defaultdict(set)
    for r in range(w['public']):
        if r not in mains and r not in legal.retired_of(w): groups[w['initial'][r],w['final'][r]].add(r)
    hits=[]
    for (e,x),roles in groups.items():
        if len(w['frames'][x])-len(w['frames'][e])>1: hits.extend(S.candidates(w,roles,e,x))
    return hits
def kappa_of(w,prof=None):   # split words are priced with the #5599 compiler profile (decay 39/40, power 1024) unless TK_PROFILE says otherwise
    retarget_pin(w); rep=legal.check(w); T,P=X.invoice(rep)
    k=float(X.kappa_dec(T,P,30)); spr=profile_of(w,prof)[1] if prof else (profile_of(w)[1] if (legal.is_prepared(w) or legal.has_of(w)) else profile_of(w,'p5599')[1]); dec=spr['decay']     # TKHYG2: tail from the same profile
    rsv=profile_of(w)[1].get('reserve',1e-10) if legal.has_of(w) else 1e-10     # PR5627-line pricing.py: alpha < 1-1e-12
    s=side_of(T,P,spr,decay=dec,reserve=rsv); mind=None
    for d in D_GRID:
        if side_of(T,P,spr,decay=d,reserve=rsv)['ok']: mind=d; break
    return dict(ok=rep['ok'],kappa=k,side_ok=s['ok'],min_decay=mind,events=len(w['program']),fields=sum(T.values()),paid=sum(rep['paid'].values()))
def build(w,h):
    hh=dict(h)
    for s in 'abcd': hh[s]={str(k):str(v) for k,v in h[s].items()}
    w2=C.split(w,hh)
    if legal.is_prepared(w2):      # prepared573: the new independent input is public role n (old n..n+7 owned roles shift up by one); the checker's 748/756/747 literals retarget to n+1 (as PR5606 -> PR5612 did)
        n=w['public']; w2['fields']=n+9; w2['independent_public']=sorted(w2['independent_public']+[n]); w2['owned_roles']=sorted(legal.retired_of(w2))+list(range(n+1,n+9))
    return w2
def retarget_pin(w2):
    """owned_fields words: verify.py pins public==743; a split adds one public role, so the pin literal is retargeted to the word under test (as PR5606 -> PR5612 retargeted 748/756/747).  A package shipping a split word must edit that pin."""
    if legal.has_of(w2): legal.OWNED9['public']=len(w2['initial'])
DKCACHE={}
def enum(w,base,per_class=6,log=print):
    """Gain depends on the rank pair only (paid calls fixed): price a few hits per rank pair, then rank classes by dk; hits of a class are built best-first (fewest events)."""
    hits=screen(w); by=defaultdict(list)
    for i,h in enumerate(hits): by[tuple(h['ranks'])].append((i,h))
    out=[]
    for rk,lst in by.items():
        done=0
        for i,h in lst:
            if done>=per_class: break
            try:
                w2=build(w,h)
                if legal.has_of(w2) and not legal.is_prepared(w2):      # PR5627 local.py (owned_fields): the vendored PR5599 local.replay cannot read 9 owned roles -> same paid multiset via the owned_fields-aware legal.check
                    retarget_pin(w2); r2=legal.check(w2,maxviol=3); assert r2['ok'] and r2['paid']==legal.check(w)['paid'],'owned_fields split not legal / paid multiset changed: %s'%(r2['violations'][:1],)
                elif legal.is_prepared(w2):      # the package local.py cannot read the prepared interface: same paid multiset via the prepared-aware legal.check
                    r2=legal.check(w2,maxviol=3); assert r2['ok'] and r2['paid']==legal.check(w)['paid'],'prepared split not legal / paid multiset changed: %s'%(r2['violations'][:1],)
                else: L.replay(w2)
            except Exception as ex: out.append(dict(i=i,hit=h,err=str(ex)[:80])); continue
            k=kappa_of(w2); out.append(dict(i=i,hit=h,w=w2,dk=k['kappa']-base['kappa'],dev=k['events']-base['events'],**k)); done+=1
    log('  %d hits; classes %s'%(len(hits),{k:len(v) for k,v in by.items()}))
    return out
def main(a):
    path,w=load(a.word); cur=w; base=kappa_of(cur); applied=[]
    log=lambda *x:print(*x,flush=True)
    log('start kappa %.13f public %d events %d'%(base['kappa'],len(cur['initial']),base['events']))
    for step in range(a.max):
        if a.public_cap and len(cur['initial'])+1>a.public_cap: log('public cap %d reached'%a.public_cap); break
        t=time.time(); es=[e for e in enum(cur,base) if 'w' in e and e['ok'] and e['dk']>0 and (not a.event_cap or e['events']<=a.event_cap)]
        es=[e for e in es if e['side_ok'] or a.free_decay and e['min_decay']]
        log('step %d: %d legal improving hits (%.0fs)'%(step,len(es),time.time()-t))
        if not es: break
        if a.list:
            for e in sorted(es,key=lambda e:-e['dk'])[:a.list]: log('  cut %d frame %d pivot %d ranks %s dk %+.3e events %+d side %s minD %s'%(e['hit']['cut_after'],e['hit']['frame'],e['hit']['pivot'],e['hit']['ranks'],e['dk'],e['dev'],e['side_ok'],e['min_decay']))
        b=max(es,key=lambda e:(e['dk']/max(1,e['dev']) if a.rate else round(e['dk'],11),-e['dev']))
        cur=b['w']; base=kappa_of(cur); applied.append(dict(cut_after=b['hit']['cut_after'],frame=b['hit']['frame'],pivot=b['hit']['pivot'],ranks=b['hit']['ranks'],dk=b['dk'],events=b['dev']))
        log('  APPLY cut %d frame %d pivot %d ranks %s dk %+.3e (+%d events) -> kappa %.13f public %d events %d side %s minD %s'%(applied[-1]['cut_after'],applied[-1]['frame'],applied[-1]['pivot'],applied[-1]['ranks'],b['dk'],b['dev'],base['kappa'],len(cur['initial']),base['events'],base['side_ok'],base['min_decay']))
        if not a.apply: break
    if a.apply:
        out=a.out or HERE+'/out/split_%s.json.gz'%os.path.basename(path).split('.')[0]
        json.dump(cur,gzip.open(out,'wt')); json.dump(applied,open(out+'.splits.json','w'))
        log('wrote %s : %d splits, kappa %.13f, public %d, events %d; run tk check --native %s'%(out,len(applied),base['kappa'],len(cur['initial']),base['events'],out))
