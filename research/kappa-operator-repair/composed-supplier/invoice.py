#!/usr/bin/env python3
"""Bind freshly emitted complex operators to every actual PR3945 owner row.

Native recount is credited reuse of the adaptive continuation. Owner predicates
follow PR3638/3734/3815/3945, with productive/nonalias and exact endpoint checks.
Three separately authored rational price engines must agree. Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
REPO = SCOPE.parents[1]
P3945 = SCOPE / 'sources/PR3945/research/staged544-terminal-gap-fill'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', type=Path, default=HERE/'candidate')
    ap.add_argument('--base-native', type=Path, default=HERE/'native-base')
    ap.add_argument('--extra-native', type=Path, default=HERE/'native-extra')
    ap.add_argument('--out', type=Path, default=HERE/'invoice')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    inv_path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    native_path = REPO/'research/kappa-adaptive-continuation/global-budget/native_owner_invoice.py'
    I = load(inv_path, 'composition_independent_invoice')
    N = load(native_path, 'composition_native_recount')
    owner = P3945/'owner'
    inp = owner/'inputs'
    widths, profiles, receipts, pins = {}, {}, {}, {}

    def pin(path):
        pins[str(path.resolve().relative_to(REPO))] = I.digest(path)
        return I.read(path)

    for tag, provider, work in [('base','gauge44',args.base_native),('extra','extra',args.extra_native)]:
        local = work/'native/local'
        complete = pin(work/'RESULT.json')
        supplied = args.candidate/('BORROW-WORD-43'+tag+'.json.gz')
        borrow = pin(supplied)
        predecessor = pin(inp/('WORD-'+tag+'.json.gz'))
        I.need(complete['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY', 'complete native execution')
        I.need([s['step'] for s in complete['steps']]==['native','ledgers','local-replay','wrappers','phases']
               and all(s['exit_code']==0 for s in complete['steps']), 'all five executed native stages')
        I.need(complete['word_sha256']==I.digest(supplied)==I.digest(work/'INPUT.json.gz'), 'actual native input')
        pin(work/'INPUT.json.gz')
        for rel, digest in complete['source_sha256'].items():
            path=work/'source'/rel
            I.need(I.digest(path)==digest, 'executed compiler pin')
            pins[str(path.relative_to(REPO))]=digest
        word = pin(local/'CANONICAL-WORD.json.gz')
        programs = pin(local/'LOCAL-PROGRAMS.json.gz')
        checks = pin(local/'LOCAL-CHECKS.json')
        replay = pin(local/'INDEPENDENT-LOCAL-REPLAY.json')
        phases = pin(local/'CLIFFORD-REVIEW.json')
        I.need(replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'full native operator check')
        I.need(phases['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES', 'full native phase check')
        I.need(replay['canonical_word_sha256']==phases['canonical_word_sha256']==I.digest(local/'CANONICAL-WORD.json.gz'), 'native proof word binding')
        I.need(replay['local_programs_sha256']==I.digest(local/'LOCAL-PROGRAMS.json.gz'), 'native proof program binding')
        I.need(word['R']==408 and len(word['start'])==len(word['final'])==632 and len(word['zero_buffers'])==91, 'live/native inventory')
        origins=list(range(224))+word['helper_origin']
        I.need(word['helper_origin']==sorted(set(range(224,704))-set(borrow['removed'])), 'literal original helper map')
        full=N.basis([1<<i for i in range(9)])
        for reg, origin in enumerate(origins):
            before=N.basis([predecessor['ports'][origin]]) if origin<112 else N.basis(predecessor['start_extra'].get(str(origin),[]))
            if 112<=origin<224:
                port=predecessor['ports'][origin-112]
                after=N.basis([v for v in range(512) if not ((v&port).bit_count()&1)])
            else:
                after=N.basis(predecessor['helper_final'].get(str(origin),full))
            I.need(N.basis(word['frames'][word['start'][reg]])==before, 'same actual owner entrance subspace')
            I.need(N.basis(word['frames'][word['final'][reg]])==after, 'same actual owner exit subspace')
        width=[len(N.basis(word['frames'][word['final'][r]]))-len(N.basis(word['frames'][word['start'][r]])) for r in range(224,632)]
        I.need(Counter(width)=={5:28,6:18,7:53,8:96,9:213}, 'new ordered hosted widths')
        profile={int(r):n for r,n in word['local_profile'].items()}
        I.need(profile=={1:2481,2:711,3:219,4:109,5:20,8:8}, 'composed local profile')
        for orientation in ['forward','backward']:
            raw=json.dumps(programs[orientation],sort_keys=True,separators=(',',':')).encode()
            I.need(hashlib.sha256(raw).hexdigest()==checks[orientation]['sha256'], 'native emitted stream')
            I.need(N.recount(I,word,programs[orientation])==profile, 'independent literal native rank recount')
            I.need(checks[orientation]['all_columns']==632 and checks[orientation]['zero_buffers_returned_to_zero']==91, 'all-input native coverage')
        I.need(sum(r*n for r,n in profile.items())==1792+64+sum(width), 'rank conservation with enlarged helper credit')
        widths[provider],profiles[provider]=width,profile
        receipts[provider]={'word_sha256':I.digest(supplied),'native_word_sha256':I.digest(local/'CANONICAL-WORD.json.gz'),
                            'programs_sha256':I.digest(local/'LOCAL-PROGRAMS.json.gz'), 'scalar_checks':checks}
    order=pin(inp/'ORDER.json');dispatch={(s,r):tag for s,r,tag in pin(inp/'DISPATCH.json')}
    clock={tuple(call):t for t,call in enumerate(order)}
    I.need(len(order)==3240 and set(clock)==set(dispatch)=={(s,r) for s in range(9) for r in range(360)},'complete clock and dispatch')
    I.need(all(all(clock[s,r]<clock[s+1,r] for s in range(8)) for r in range(360)),'each owner stage chronology')
    template,plan=pin(inp/'TEMPLATE.json.gz'),pin(inp/'PLAN.json.gz')
    caps={c['child']:c['rank'] for c in template['idle_children']}
    family={c:2*plan['pairs'][str(c)]+plan['sides'][str(c)] for c in caps}
    pair={e['stage']:e['pair'] for e in template['recipe'] if e['kind']=='local'}
    windows={}
    for owner_id in range(360):
        touched={};tick=None
        for event in template['execution_schedule']:
            kind=event['kind']
            if kind=='local_cover_sweep':
                tick=clock[event['stage'],owner_id];touched[pair[event['stage']]]=tick
            elif kind=='bridge':
                I.need(tick is not None,'bridge time');touched[event['src']]=touched[event['dst']]=tick
            elif kind=='idle_cover_sweep':
                for child in event['child_indices']:
                    if child in caps:
                        I.need((owner_id,child) not in windows,'unique idle interval')
                        windows[owner_id,child]=(caps[child],touched.get(event['pair'],-1),tick)
            else:
                I.need(kind in ['bank_padding_cover_sweep','translate_every_live_family','terminal_Y_translations','terminal'],'known unchanged schedule')
    intervals=defaultdict(list)
    for (o,c),(_,lo,hi) in windows.items():intervals[o,family[c]].append((lo,hi))
    I.need(all(all(max(a,c)>=min(b,d) for j,(a,b) in enumerate(xs) for c,d in xs[j+1:]) for xs in intervals.values()),'nonoverlapping physical windows')
    fill=pin(owner/'FILL.json.gz')
    I.need(fill['columns']==['time','helper','owner_replica','child','port','offset'] and not fill['dispatch_overrides'],'actual unchanged fill schema')
    I.need(len(fill['rows'])==1321920,'complete role count')
    used=Counter();seen=set()
    for j,row in enumerate(fill['rows']):
        I.need(len(row)==6 and all(type(v)is int for v in row),'integer owner record')
        t,h,o,c,p,z=row
        I.need(t==j//408 and h==j%408 and (o,c) in windows and 0<=p<112,'actual helper identity')
        if h==0:seen=set()
        cap,lo,hi=windows[o,c]
        I.need(lo<t<=hi,'strict owner entrance / closed departure')
        physical=896*o+112*family[c]+p
        I.need(physical not in seen,'same-call physical family injection');seen.add(physical)
        stage,replica=order[t]
        I.need(physical//224!=4*replica+pair[stage],'data and helper physical nonaliasing')
        width=widths[dispatch[stage,replica]][h]
        I.need(z==used[o,c,p] and z+width<=cap,'compact chronological offset and capacity')
        used[o,c,p]+=width
    idle=Counter()
    for (o,c),(cap,_,_) in windows.items():
        for p in range(112):
            rem=cap-used[o,c,p]
            I.need(rem>=0,'nonnegative idle capacity')
            if rem:idle[rem]+=1
    I.need(idle=={3:23328,5:4320,48:137952},'literal residual inventory, no idle-axis transfers')
    profile=Counter(idle)
    for stage,replica in order:profile.update(profiles[dispatch[stage,replica]])
    I.need(sum(r*n for r,n in profile.items())==65088*360,'complete deficit 320 per replica')
    I.need(max(profile)<=I.C.max_idle_rank(73),'recursive rank guard')
    root=I.root(profile,73,322560);lower,upper=map(Q,root['rational'])
    R=load(P3945/'vendor/rational_price.py','composition_second_price')
    signed=dict(profile);signed[73]=-322560
    I.need(R.interval(signed,lower)[1]<0<R.interval(signed,upper)[0],'second rational price engine')
    E=load(REPO/'research/native-complex-moment552/engines/moment.py','composition_third_price')
    I.need(E.moment(dict(profile),73,322560,lower)[1]<1<E.moment(dict(profile),73,322560,upper)[0],'third rational price engine')
    baseline=Q('.001730739780298357321619')
    I.need(lower>baseline,'improves valid retained complex baseline')
    for p in [Path(__file__),inv_path,native_path,P3945/'vendor/rational_price.py',REPO/'research/native-complex-moment552/engines/moment.py']:
        pins[str(p.relative_to(REPO))]=I.digest(p)
    result={'status':'PASS_FRESH_NATIVE_LITERAL_OWNERS_AND_THREE_ENGINE_COMPLEX_INVOICE',
            'root':root,'gain_over_valid_complex_lower':str(lower-baseline),
            'profile':dict(sorted(profile.items())),'local_profile':profiles,'idle_profile':dict(sorted(idle.items())),
            'native_receipts':receipts,'helper_rows':1321920,'calls':3240,'replicas':360,
            'owner_windows':len(windows),'productive_families':322560,'physical_families':323069,
            'native_orientations_recounted':4,'helpers':408,'width_inventory':dict(Counter(widths['gauge44'])),
            'full_global_operator_gate':'Separate symbolic controller/hosting gate required; no MOVES are used.',
            'conditional_kappa_if_inherited_interfaces_hold':str(lower-Q(1,10**46)-Q(1,10**70)),
            'scope':'Fresh finite native/operator/phase receipts plus exact complete owner layout and three-engine arithmetic. Inherited physical/all-size/compiler, resource/precision/recovery and outer transfer assumptions remain.',
            'source_pins':pins}
    (args.out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],root['decimal'],flush=True)


if __name__=='__main__':
    main()
