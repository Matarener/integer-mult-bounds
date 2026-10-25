#!/usr/bin/env python3
"""Independent focused contact/invoice audit; inherited native/outer premises.

No author scientific module is executed. Rational intervals reuse the pinned
earlier engine. Credit and exact scope: CONTRACT.md. Apache-2.0, Codex-assisted.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json

B = Path(__file__).resolve().parent
ROOT = B.parents[1]
PINS = json.loads((B/'INPUTS.json').read_text())


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def span(basis):
    out = {0}
    for axis in basis:
        need(type(axis) is int and 0 < axis < 512 and axis not in out,
             'independent nine-axis frame')
        out |= {v ^ axis for v in tuple(out)}
    return out


def add(a, b, coefficient):
    out = dict(a)
    for key, value in b.items():
        value = out.get(key, Q(0)) + coefficient*value
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    return out


def contact(source):
    events = source['program']
    expected = {16798:['MOVE',345,739,240,False],
                16799:['ADD',341,345,'-1',240],
                16800:['SCALE',341,'-1',240],
                17061:['MOVE',341,240,127,False],
                17067:['MOVE',345,240,127,False]}
    need(all(events[i] == e for i,e in expected.items()), 'five pinned source sites')
    touched = {}
    for owner, end in [(341,17061),(345,17067)]:
        hits = []
        for i in range(16798,end):
            e = events[i]
            used = [e[1]] + ([e[2]] if e[0] in ('ADD','COPY') else [])
            if owner in used:
                hits.append(i)
        need(hits == ([16799,16800] if owner==341 else [16798,16799]),
             'complete source/destination read interval')
        touched[str(owner)] = hits
    A,Bb,D = [span(source['frames'][i]) for i in (739,240,127)]
    need(A < Bb < D and (len(A),len(Bb),len(D))==(8,16,512), 'actual nested 3/4/9 planes')
    edits = {16798:[['MOVE',341,240,127,False],['MOVE',345,739,127,False]],
             16799:[['ADD',341,345,'-1',127]],
             16800:[['SCALE',341,'-1',127]],17061:[],17067:[]}
    out = deepcopy(source)
    out['program'] = [deepcopy(e) for i,old in enumerate(events) for e in edits.get(i,[old])]
    need([e[:-1] for e in events if e[0]!='MOVE'] ==
         [e[:-1] for e in out['program'] if e[0]!='MOVE'], 'unchanged complete scalar/owned chronology')
    return out,touched


def replay(word):
    frames = [span(b) for b in word['frames']]
    dims = list(map(len,word['frames']))
    rows = [{i:Q(1)} for i in range(743)]
    charts = list(word['initial']) + [None]*8
    active = set()
    peak = 0
    paid = Counter()
    for event in word['program']:
        op,dst = event[:2]
        need(0<=dst<743,'valid destination')
        if op=='MOVE':
            _,dst,a,b,private=event
            need(charts[dst]==a and (dst in active)==private,'owned/source frame')
            need((frames[b]<frames[a]) if private else (frames[a]<frames[b]),'strict nested MOVE')
            charts[dst]=b
            paid[abs(dims[b]-dims[a])]+=1
        elif op=='INIT':
            need(dst>=735 and dst not in active,'owned entry only')
            active.add(dst)
            rows[dst]={}
            charts[dst]=event[2]
            peak=max(peak,len(active))
        elif op=='CLEAR':
            need(dst in active and charts[dst]==event[2],'live owned clear')
            active.remove(dst)
            rows[dst]={}
            charts[dst]=None
        else:
            coefficient,chart=Q(event[-2]),event[-1]
            need(coefficient!=0 and charts[dst]==chart,'scalar chart/coefficient')
            if op=='SCALE':
                rows[dst]={k:coefficient*v for k,v in rows[dst].items()}
            else:
                need(op in ('ADD','COPY'),'known scalar instruction')
                src=event[2]
                need(src!=dst and charts[src]==chart,'common source chart')
                if op=='COPY':
                    need(dst in active and not rows[dst],'COPY into owned zero')
                    rows[dst]={k:coefficient*v for k,v in rows[src].items()}
                else:
                    rows[dst]=add(rows[dst],rows[src],coefficient)
    need(not active and peak==1 and charts[:735]==word['final'],'complete public and owned frames')
    live=set(word['live'])
    for i,row in enumerate(rows):
        target={i:Q(1)} if i<735 else {}
        if i-112 in live:
            target[i-112]=Q(1)
        need(row==target,'all743 exact endpoint rows')
    helpers=Counter(dims[word['final'][i]]-dims[word['initial'][i]]
                    for i in range(735) if i not in live and i-112 not in live)
    need(sum(helpers.values())==527 and min(helpers)>0,'527 independent productive helpers')
    return paid,helpers


def invoice(local_paid,helpers,controller):
    p,t=Counter(),Counter()
    counts=Counter()
    for e in controller['physical_events']:
        counts[e[0]]+=1
        if e[0]=='LOCAL':
            need(e[3] is False,'forward invocation at every full site')
            p.update(local_paid)
            t.update(helpers)
        elif e[0]=='QUERY_SHEAR':
            p[1]+=104
        elif e[0]=='IDLE':
            need(len(e[2])==len(set(e[2])),'distinct idle stages')
            p[8*len(e[2])]+=208
    for term in controller['diagonal']:
        t[1+8*sum(term[1:])]+=104
    need(counts['LOCAL']==18 and counts['QUERY_SHEAR']==counts['IDLE']==15 and
         len(controller['diagonal'])==32,'literal complete occurrence map')
    return p,t


def main():
    for name,sha in PINS['files'].items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,'source pin '+name)
    source=read(B/'sources/predecessor/WORD.json.gz')
    emitted=read(B/'sources/contact/WORD.json.gz')
    modified,windows=contact(source)
    need(modified==emitted,'independently emitted word equals full committed JSON')
    old_p,old_t=replay(source)
    new_p,new_t=replay(modified)
    delta=Counter(new_p);delta.subtract(old_p)
    need({r:n for r,n in delta.items() if n}=={1:-1,5:-1,6:1},'local paid delta')
    need(new_t==old_t,'all helper targets retained')
    controller=read(B/'sources/predecessor/CONTROLLER.json')
    old_P,old_T=invoice(old_p,old_t,controller)
    P,T=invoice(new_p,new_t,controller)
    published=read(B/'sources/contact/RESULT.json')
    prior=read(B/'sources/predecessor/RESULT.json')
    for saved,p,t in [(published,P,T),(prior,old_P,old_T)]:
        costs=saved['complete_cost']
        need(p==Counter({int(r):n for r,n in costs['paid'].items()}) and
             t==Counter({int(r):n for r,n in costs['targets'].items()}),'complete saved invoice')
    need(T==old_T,'zero complete target delta')
    spec=importlib.util.spec_from_file_location('earlier_interval_engine',ROOT/'outputs/economic-sensitivity-feasibility-20261025/interval_math.py')
    im=importlib.util.module_from_spec(spec);spec.loader.exec_module(im)
    power=lru_cache(None)(im.power)

    def moment(p,t,c):
        lo=hi=Q(0)
        for r in set(p)|set(t):
            n=t[r]-p[r]
            if n:
                a,b=power(r,c)
                lo+=n*(a if n>0 else b)
                hi+=n*(b if n>0 else a)
        return lo,hi

    def display(pair):
        return im.interval(*pair)

    root_lo,root_hi=map(Q,published['complete_cost']['raw_root_interval'])
    need(moment(P,T,root_lo)[0]>0 and moment(P,T,root_hi)[1]<0,'published raw crossing independently bracketed')
    C=Q('.0033')
    current=moment(P,T,C)
    g=moment(Counter({6:1}),Counter({1:1,5:1}),C)
    need(current[1]<0 and g[0]>0,'target deficit and strict single-edit gain')
    limit=P[5]
    maxed=Counter(P)
    maxed[1]-=limit;maxed[5]-=limit;maxed[6]+=limit
    ceiling=moment(maxed,T,C)
    need(ceiling[1]<0,'even every rank5 edit misses target')
    # Exact sufficient derivative bound for uniqueness of the optimistic-family
    # crossing after division by6^t; see the paper derivation in the report.
    signed=Counter(T);signed.subtract(maxed)
    need(signed[1]<0 and signed[2]<0 and signed[3]<0 and signed[4]<0 and signed[5]>0,
         'only adverse normalized derivative below6 is rank5')
    need(all(signed[r]>0 for r in (7,8,9)),'positive local high-rank terms')
    need(Q(-signed[1],6)>Q(signed[5],5),'rank1 derivative dominates adverse rank5 term on0<=t<=1')
    need(all(T[r+1]==P[r] for r in (16,24,32,40,48,56,64,72)), 'positive paired tail derivative')
    grid=10**12
    lo,hi=0,10**10
    need(moment(maxed,T,Q(lo,grid))[0]>0 and moment(maxed,T,Q(hi,grid))[1]<0,'optimistic-family root bracket')
    while hi-lo>1:
        mid=(lo+hi)//2
        pair=moment(maxed,T,Q(mid,grid))
        need(pair[0]>0 or pair[1]<0,'strict bisection decision')
        if pair[0]>0:lo=mid
        else:hi=mid
    need(moment(maxed,T,Q(lo,grid))[0]>0 and moment(maxed,T,Q(hi,grid))[1]<0,'strict family ceiling enclosure')
    ceil=lambda x:-(-x.numerator//x.denominator)
    required=[ceil(-current[1]/g[1]),ceil(-current[0]/g[0])]
    need(required[0]==required[1] and required[0]>limit,'required edit count exceeds inventory')

    rank_mass=sum(r*n for r,n in new_p.items())
    need(rank_mass==5894,'preserved local paid rank mass')
    q,rem=divmod(rank_mass,9)
    relaxed_local=Counter({9:q})
    if rem:relaxed_local[rem]+=1
    relaxed=Counter(P)
    relaxed.subtract({r:18*n for r,n in new_p.items()})
    relaxed.update({r:18*n for r,n in relaxed_local.items()})
    need(min(relaxed.values())>=0,'only local calls replaced in broad relaxation')
    broad=moment(relaxed,T,C)
    need(broad[0]>0,'broader rank-mass relaxation is not economically excluded')
    costs=published['complete_cost']
    compiler=costs['compiler'];H=compiler['H'];j=compiler['integer_test_exponent']
    gap=Q(compiler['gap']);step=gap.denominator
    need(gap.numerator==1 and H==step*j and (H+1)**1000<2**j and
         (step*(j-1)+1)**1000>=2**(j-1),'reported integer compiler threshold and preceding grid failure')
    need(735==source['public']==emitted['public'] and len(source['program'])==25311 and
         len(emitted['program'])==25310,'unchanged source contract within fixed26000 event budget')

    controls={}
    for name,change in [('one_operand_only',lambda w:w['program'][16798].__setitem__(3,240)),
                        ('wrong_sign',lambda w:w['program'][16800].__setitem__(3,'1'))]:
        bad=deepcopy(modified);change(bad)
        try:replay(bad)
        except (ValueError,IndexError,TypeError):controls[name]='rejected'
        else:raise ValueError('control accepted '+name)
    bad=deepcopy(source);bad['program'][16801]=['ADD',400,341,'1',240]
    try:contact(bad)
    except ValueError:controls['intervening_source_read']='rejected'
    else:raise ValueError('undeclared read accepted')
    controls['target_loss_reverses_credit']='explicit full target equality checked'
    result={'schema':'p104-focused-contact-audit/v1','reviewed_head':PINS['reviewed_head'],
            'source_windows':windows,'source_events':len(source['program']),'new_events':len(modified['program']),
            'independent_normalized_endpoint_rows':743,'coefficients_including_zeros':743**2,
            'source_endpoint':'pass','changed_endpoint':'pass','owned_returns':'pass',
            'native_phase_and_allwidth':'inherited chart identity; not freshly replayed',
            'local_paid_before':dict(old_p),'local_paid_after':dict(new_p),
            'complete_paid_before':dict(old_P),'complete_paid_after':dict(P),'complete_targets':dict(T),
            'compiler_integer_threshold_only_checked':H,
            'funding_scope':'complete native/precision/compiler theorem and58outer obligations not independently admitted here',
            'C_probe':str(C),'current_moment_at_target':display(current),
            'one_1plus5_to6_edit_gain_at_target':display(g),
            'remaining_global_edit_inventory':limit,'remaining_identical_local_contacts_upper':new_p[5],
            'required_global_edits_at_target':required[0],
            'required_identical_contacts_per18sites':ceil(Q(required[0],18)),
            'all_remaining_edits_moment_at_target':display(ceiling),
            'all_remaining_edits_raw_ceiling_interval':[str(Q(lo,grid)),str(Q(hi,grid))],
            'ceiling_monotonicity':'after division by6^t, rank1 dominates only adverse rank5 derivative; paired high tails positive',
            'broader_relaxed_local_profile':dict(relaxed_local),
            'broader_relaxed_moment_at_target':display(broad),
            'broader_relaxation_physical_witness':False,'controls':controls,
            'new_kappa':None,'stop':True}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__=='__main__':main()
