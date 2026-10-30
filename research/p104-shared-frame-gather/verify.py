"""Exact one-frame gather obstruction at call3 local13660, prepared for zxv.

Substantial OpenAI Codex assistance. Apache-2.0. No subagents.
Predecessor maps, code and notices retain their attribution in inputs/.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

def read(path):
    data=(HERE/path).read_bytes()
    return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

# Independent coordinate reconstruction: coefficients refer to literal prefix rows,
# not to the row-echelon implementation's internal normalized rows.
def linear_combination(co,by_event,helpers):
    out={}
    for event,q in co.items():
        for col,v in by_event[event]['row'].items():
            if col in helpers:out[col]=out.get(col,Q(0))+q*v
    return {k:v for k,v in out.items() if v}

def binary_rank(rows):
    pivots={}
    for value in rows:
        while value:
            bit=value.bit_length()-1
            if bit not in pivots:
                pivots[bit]=value;break
            value^=pivots[bit]
    return len(pivots)

def run():
    for pin in read('SOURCES.json')['runtime_inputs']:
        need(sha256((HERE/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'Input hash '+pin['path'])
    E=load('retained_paid_rows','inputs/predecessor-experiment.py');E.HERE=HERE
    w=read('inputs/word5718.json.gz');controller=read('inputs/controller5718.json')
    maps=read('inputs/QUERY-MAPS.json.gz')
    paid,selected,_,helpers=E.walk(w)
    need(len(paid)==3426 and w['public']==744 and w['owned_fields']==9,'Source dimensions')
    need(encode(paid)==maps['queries'],'All 3426 exact query rows, versions, epochs and frames')
    bindings=E.caller_bindings(w,controller)
    need(encode(bindings)==maps['native_input_bindings'],'Every raw original/helper binding, route and source gauge')
    need(controller['physical_events'][:4]==[['LOCAL',0,0,False],['Q_POWER',0,-2],['SIGNED_SWAP',0,1],['LOCAL',1,0,False]],'Actual call0 to call3 chronology')
    item=next(x for x in selected if x['query']['event']==13660);target=item['query']
    need((target['role'],target['old'],target['new'],target['rank'],target['input_version'],target['owned_epoch'])==(748,518,598,7,3,1),'Assigned query identity')
    prefix=[p for p in paid if p['event']<target['event']];by_event={p['event']:p for p in prefix}
    need(len(prefix)==1211 and target['row'][21]==Q(-1,4),'Exact fresh helper21 target')
    target_helpers=E.project(target['row'],helpers)
    # Free destination-frame observations are also granted free at the gather frame.
    # They are zero on helper21 and cannot weaken our lower bound.
    destination=[(f'current:{r}:v{v}',row) for r,v,last,row in item['donors']]
    destination += [(f"retained:{p['event']}",p['row']) for p in item['retained_same_call']]
    need(all(not row.get(21) for label,row in destination),'Fresh helper absent from every destination observation')
    # Build one exact coordinate isomorphism on the whole available helper history.
    basis=E.Basis()
    for p in prefix:basis.insert(E.project(p['row'],helpers),p['event'])
    # Grant destination fields for free; include their coordinate directions too.
    for label,row in destination:basis.insert(E.project(row,helpers),label)
    all_sources=dict(by_event)
    for label,row in destination:all_sources[label]={'row':row}
    coordinates=[]
    for p in prefix:
        rem,co=basis.solve(E.project(p['row'],helpers));need(not rem,'Every prefix row in coordinate span')
        need(linear_combination(co,all_sources,helpers)==E.project(p['row'],helpers),'Independent exact prefix-coordinate expansion')
        coordinates.append(co)
    rem,tc=basis.solve(target_helpers);need(not rem,'Target coordinates exist in full history')
    need(linear_combination(tc,all_sources,helpers)==target_helpers,'Independent exact target-coordinate expansion')
    destco=[]
    for label,row in destination:
        rem,co=basis.solve(E.project(row,helpers));need(not rem,'Destination coordinates');destco.append(co)
        need(linear_combination(co,all_sources,helpers)==E.project(row,helpers),'Independent destination-coordinate expansion')
    C=E.load('clifford_exact.py');V=E.load('native_verify.py')
    charts=[C.canonical_frame(9,tuple(f)) for f in w['frames']]
    lagrangians=[tuple(x|(z<<9) for x,z,ph in c.adjoint().tab[9:]) for c in charts]
    independent_lagrangians=[]
    for f,c in enumerate(charts):
        circuit=V.frame(tuple(w['frames'][f]),9)
        need(V.tableau(circuit)==c.tab,'Independent signed canonical frame '+str(f))
        tab=V.tableau(V.adjoint(circuit))
        independent_lagrangians.append(tuple(x|(z<<9) for x,z,ph in tab[9:]))
    @lru_cache(None)
    def distance(a,b):
        value=C.rank(lagrangians[a]+lagrangians[b])-9
        need(value==binary_rank(independent_lagrangians[a]+independent_lagrangians[b])-9,'Independent pair tariff')
        need(0<=value<=9,'Gaussian distance range')
        return value
    # Gaussian rank is the Lagrangian metric d(A,B)=rank(L_A+L_B)-9.
    # Check literal native compositions for all final edges and a reproducible
    # cross-sample of ingress edges; the independent interpreter checks every frame.
    literal_checks=0
    for f in range(len(charts)):
        op=charts[f].adjoint().then(charts[598])
        need(distance(f,598)==C.rank([x for x,z,ph in op.tab[9:]]),'Literal final native rank')
        literal_checks+=1
    for a in range(0,len(charts),53):
        for b in range(0,len(charts),79):
            op=charts[a].adjoint().then(charts[b])
            need(distance(a,b)==C.rank([x for x,z,ph in op.tab[9:]]),'Literal sampled ingress native rank');literal_checks+=1
    need([f for f in range(len(charts)) if distance(f,598)==0]==[598],'Rank-zero final alignment has literal frame598')
    first_use={f:-1 for f in w['initial']}
    for event,ins in enumerate(w['program'][:13660]):
        if ins[0]=='MOVE':fs=ins[2:4]
        elif ins[0] in ('INIT','CLEAR'):fs=[ins[2]]
        else:fs=[ins[-1]]
        for f in fs:first_use.setdefault(f,event)
    helper21=[p for p in prefix if p['row'].get(21)]
    receipts=[];stats=Counter();extra=Counter()
    # Allow arbitrary source-coframe preaggregation before one ingress job.
    # Every bundle may use every earlier version at that literal source frame.
    groups={}
    for i,p in enumerate(prefix):groups.setdefault(p['new'],[]).append(i)
    supports={f:set().union(*(set(coordinates[i]) for i in indices)) for f,indices in groups.items()}
    target_support=set(tc)
    destination_ignored=set().union(*(set(co) for co in destco))
    for frame in range(len(charts)):
        final=distance(frame,598);budget=6-final
        common=dict(frame=frame,first_physical_use=first_use.get(frame),final_rank=final,ingress_rank_budget=budget)
        if budget<0:
            receipts.append(dict(**common,status='FINAL_DELIVERY_ALREADY_COSTS_AT_LEAST_H7'));stats['final_rank']+=1;continue
        costs={f:distance(f,frame) for f in groups}
        # Free arbitrary old-call and main information vanish on the fresh-helper21 difference.
        if not any(p['row'].get(21) and costs[p['new']]<=budget for p in prefix):
            need(not any(row.get(21) for _,row in destination),'No free fresh helper')
            receipts.append(dict(**common,status='FRESH_HELPER21_UNAVAILABLE_WITHIN_INGRESS_BUDGET',
                minimum_helper21_ingress_rank=min(distance(p['new'],frame) for p in helper21)))
            stats['helper21']+=1;continue
        certificate=None
        for threshold in (0,1,2,3,4,5,6,8,10,12,16,20,30,40,60,80):
            free_frames=[f for f,cost in costs.items() if cost==0 or (cost<=budget and len(supports[f])>threshold)]
            ignored=destination_ignored|set().union(*(supports[f] for f in free_frames))
            uncovered=target_support-ignored
            widths={f:len(s-ignored) for f,s in supports.items()}
            # Unbounded knapsack overestimates coverage: repetitions and overlaps
            # are all counted as new coordinates. Hence it is a valid upper bound.
            maxwidth={r:max((widths[f] for f,cost in costs.items() if cost==r),default=0) for r in range(1,budget+1)}
            dp=[0]*(budget+1)
            for b in range(1,budget+1):
                dp[b]=max([dp[b-1]]+[maxwidth[r]+dp[b-r] for r in range(1,b+1)])
            if len(uncovered)>dp[budget]:
                certificate=dict(threshold=threshold,free_source_frames=free_frames,
                    ignored_coordinates=sorted(ignored,key=str),uncovered_target_coordinates=sorted(uncovered,key=str),
                    max_coordinate_coverage_by_ingress_rank=maxwidth,coverage_capacity_dp=dp,
                    obstruction_margin=len(uncovered)-dp[budget],
                    source_frame_ingress_ranks=costs)
                break
        need(certificate is not None,'Every eligible gather frame has an exact support-budget obstruction')
        receipts.append(dict(**common,status='EXACT_HELPER_COORDINATE_COVER_EXCEEDS_BUDGET',certificate=certificate))
        stats['support']+=1;extra[final]+=1
    need(len(receipts)==1090 and sum(stats.values())==1090,'Complete bounded frame domain')
    physical_count=sum(r['first_physical_use'] is not None for r in receipts)
    # Native phase and constructive gather controls use actual prefix outputs.
    controls=control_checks(E,w,prefix,target,charts,distance,C,V,helpers,coordinates,tc,destination)
    invoice=E.invoice(w,controller)
    invoice.pop('adjacent_main_best_cache_tree')  # Outside this assigned query.
    result=dict(status='PASS_SHARED_FRAME_GATHER_OBSTRUCTION_NO_NEW_KAPPA',
        assigned_query=target,caller_event=3,local_cut=13660,
        scope='One common pinned canonical frame; arbitrary combinations of unchanged earlier paid snapshots preaggregated within each source coframe, independent source-frame ingress, scalar recombination, one final canonical delivery. Distinct call0/call3 raw helper columns. No changed source graph or matrix-valued recombination.',
        exact_input_coverage=dict(paid_query_maps=3426,available_same_call_paid_outputs=len(prefix),
            public_columns=744,owned_columns=9,helpers_per_invocation=len(helpers),caller_binding_phase_checks=bindings['phase_checks'],
            basis_rank=len(basis.rows),source_coframe_bundles=len(groups),target_coordinate_support=len(tc),all_1090_frames_independently_interpreted=True,
            literal_relative_rank_checks=literal_checks,independently_checked_pair_distances=distance.cache_info().currsize),
        frame_domain=dict(all_pinned_frames=1090,physically_seen_before_cut=physical_count,
            unseen_frames_granted_only_as_favorable_rejection_relaxation=1090-physical_count),
        rejection_counts=stats,support_frames_by_final_rank=extra,
        minimum_support_obstruction_margin=min(r['certificate']['obstruction_margin'] for r in receipts if 'certificate' in r),
        helper21_paid_sources=[{k:v for k,v in p.items() if k!='row'}|{'coefficient':p['row'][21]} for p in helper21],
        hypothetical_complete_signed_bill=dict(removed_paid={7:-1},target_delta={},
            necessary_gather_paid='sum_i H_distance(snapshot_i,frame) + H_distance(frame,598) >= H7 for every 0<t<1',
            proof='Strict improvement requires total positive Gaussian rank <=6, since sum r_i^t >= (sum r_i)^t. Every such source subset is excluded in every tested gather frame.',
            additional_cost_obligations={'acquisition_COPY':'unknown, nonnegative; optimistically omitted only for exclusion',
                'read_retention_and_owned_storage':'unknown, nonnegative; no productive credit',
                'ingress_and_final_monomial_normalizers':'unknown ordinary work; all positive recursive Gaussian ranks included',
                'source_restoration_dirty_return':'unknown; no source-consuming alteration is granted',
                'owned_clear_and_retained_value_cleanup':'unknown, nonnegative',
                'main_and_other_helper_corrections':'unknown; all main information granted free for exclusion',
                'ordinary_dyadic_arithmetic_and_routes':'unknown, nonnegative',
                'compiler_precision_stock_outer':'unrun for any changed program because no candidate survives'},
            conclusion='No fully costed improvement can exist inside the tested protocol. No alternative program was emitted.'),
        unchanged_complete_source_invoice=invoice,realized_delta_paid={},realized_delta_targets={},kappa_status='NO_NEW_KAPPA',controls=controls)
    certificate=dict(schema='one-frame-gather-exact-cover/1',query=target,
        prefix_events=[p['event'] for p in prefix],source_frame_groups={f:[prefix[i]['event'] for i in ix] for f,ix in groups.items()},source_helper_coordinates=coordinates,
        target_helper_coordinates=tc,destination_observation_coordinates=destco,frame_receipts=receipts)
    return encode(result),encode(certificate)


def control_checks(E,w,prefix,target,charts,distance,C,V,helpers,coordinates,tc,destination):
    def rejected(fn,label):
        try:fn()
        except ValueError:return True
        raise ValueError('Negative control accepted: '+label)
    def available(p,cut):need(p['event']<cut,'Future paid answer version')
    by_event={p['event']:p for p in prefix}
    # A nested owned local discovery control: capture 432 after12489 and read
    # 433 after12491 in their common frame33. Deliver their sum to empty frame3
    # through one shared rank-one native descent, then observe and CLEAR it.
    # This is a synthetic target, not the assigned centre or a supplier change.
    a,b=by_event[12489],by_event[12491];frame=33
    need(a['row']!=b['row'] and a['new']==b['new']==33,'Actual two-source gather fixture')
    for p in (a,b):available(p,13660)
    row=dict(a['row']);E.plus(row,b['row'])
    recombined={};E.plus(recombined,a['row']);E.plus(recombined,b['row']);need(row==recombined,'Exact constructive gather all744 scalar columns')
    native_controls=[]
    for old,new in [(33,3),(104,3),(3,598),(518,598)]:
        op=charts[old].adjoint().then(charts[new]);recipe,compiled=C.lower_child(op)
        V.equal(V.recipe(recipe),V.adjoint(V.frame(tuple(w['frames'][old]),9))+V.frame(tuple(w['frames'][new]),9),'Native exact gather map and absolute phase')
        need(recipe['rank']==distance(old,new),'Lowered native tariff')
        native_controls.append(dict(old=old,new=new,rank=recipe['rank'],recipe=recipe))
    from copy import deepcopy
    wrong=deepcopy(native_controls[0]['recipe']);wrong['left']['phase']=(wrong['left']['phase']+1)%4
    wrong_phase=rejected(lambda:V.equal(V.recipe(wrong),V.recipe(native_controls[0]['recipe']),'Wrong absolute phase'),'phase')
    # Explicit discovery control: exact elimination must discover both actual sources
    # as an available two-source representation at their charged shared frame.
    fixture=E.Basis();fixture.insert(a['row'],a['event']);fixture.insert(b['row'],b['event'])
    rem,co=fixture.solve(row);need(not rem and co=={a['event']:Q(1),b['event']:Q(1)},'Discover constructive shared-gather fixture')
    def validate_source(record,cut,invocation=3):
        available(record,cut)
        need(invocation==3,'Distinct invocation helper namespace')
        expected=by_event.get(record['event'])
        need(expected is not None,'Actual paid output')
        for key in ('role','output_version','owned_epoch','new'):
            need(record[key]==expected[key],'Exact snapshot '+key)
    validate_source(a,13660);validate_source(b,13660)
    future=dict(a,event=13661)
    future_rejected=rejected(lambda:validate_source(future,13660),'future version')
    stale_rejected=rejected(lambda:validate_source(a,13660,invocation=0),'stale helper')
    oldversion=dict(a,output_version=a['output_version']-1)
    oldversion_rejected=rejected(lambda:validate_source(oldversion,13660),'old version')
    nofresh=E.Basis()
    for p in prefix:nofresh.insert({k:v for k,v in E.project(p['row'],helpers).items() if k!=21},p['event'])
    need(bool(nofresh.solve(E.project(target['row'],helpers))[0]),'Missing fresh helper21 cannot reconstruct target')
    retag_rejected=rejected(lambda:need(distance(33,3)==0,'Nonzero ingress cannot be retagged free'),'unpaid retag')
    # A separate invoice fixture has two nonzero ingresses into3, then3->598.
    def validate_paid(edges,bill):
        expected=Counter(distance(x,y) for x,y in edges if distance(x,y))
        need(expected==bill,'Ingress is part of the complete invoice')
    edges=[(33,3),(104,3),(3,598)]
    validate_paid(edges,Counter({1:3}))
    underpriced=rejected(lambda:validate_paid(edges,Counter({1:1})),'underpriced ingress')
    def complete_claim(obligations):
        need(all(value=='proved' for value in obligations.values()),'Unknown retained-value cleanup prevents a complete claim')
    cleanup=rejected(lambda:complete_claim({'native':'proved','cleanup':'unknown'}),'cleanup')
    wrongframe=rejected(lambda:validate_source(dict(a,new=3),13660),'wrong frame')
    # Literal scalar/lifetime fragment with sources left untouched.
    source_copies={p['role']:dict(p['row']) for p in (a,b)}
    cache=dict(source_copies[a['role']]);E.plus(cache,source_copies[b['role']])
    need(cache==row and E.set_span(w['frames'][3])<E.set_span(w['frames'][33]),'Nested control delivery')
    need(source_copies=={p['role']:p['row'] for p in (a,b)},'Control preserves both arbitrary sources')
    observed=dict(cache);cache.clear();need(observed==row and not cache,'Control observed then owned CLEAR')
    # Standard exact arbitrary-state endpoint replay is E.walk, including all nine
    # arbitrary owned entrance columns and every literal INIT/CLEAR lifetime.
    return dict(constructive_gather=dict(events=[a['event'],b['event']],versions=[a['output_version'],b['output_version']],
        frames=[a['new'],b['new']],gather_frame=33,destination_frame=3,completion_cut=13660,all_scalar_columns=744,
        coefficients=co,ingress_ranks=[],shared_final_rank=distance(33,3),
        retention='COPY 432 immediately after12489, ADD 433 immediately after12491; retain one owned value to local13660.',
        operations=[['INIT','cacheA',33],['COPY','cacheA',a['role'],'1',33],
            ['ADD','cacheA',b['role'],'1',33],['MOVE','cacheA',33,3,True],['OBSERVE','cacheA',3],['CLEAR','cacheA',3]],
        physical_admission='Local nested scalar/native/lifetime control only; arbitrary-width retention hosting and supplier admission are not asserted.',
        invoice='1 owned INIT +1 COPY +1 ADD +1 native H1 +1 observation +1 CLEAR; one retained owned value, no target credit. Ordinary/hosting tariff unspecified; this is a discovery control only.'),
        exact_native_controls=native_controls,wrong_global_phase_rejected=wrong_phase,
        future_version_rejected=future_rejected,old_snapshot_version_rejected=oldversion_rejected,stale_helper_namespace_rejected=stale_rejected,
        missing_fresh_helper_rejected=True,unpaid_ingress_retag_rejected=retag_rejected,
        underpriced_ingress_rejected=underpriced,unknown_cleanup_zero_rejected=cleanup,wrong_snapshot_frame_rejected=wrongframe)

if __name__=='__main__':
    result,certificate=run()
    for path,obj in [('results/RESULT.json',result),('results/CERTIFICATE.json.gz',certificate)]:
        if '--write' in sys.argv:
            raw=(json.dumps(obj,sort_keys=True,indent=2)+'\n').encode()
            (HERE/path).write_bytes(gzip.compress(raw,mtime=0) if path.endswith('.gz') else raw)
        else:need(read(path)==obj,'Full deterministic receipt '+path)
    print(result['status'])
