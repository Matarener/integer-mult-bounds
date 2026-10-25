"""Source-level all-replica audit, no full-volume physical replay."""
from collections import Counter, defaultdict
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys
import replica_catalogue as rc
import adapter
from check_transport import determinant,dyadic,dyadic_unit,reconstructed_chart,distinguishing_entry,canonical

HERE=Path(__file__).resolve().parent
need=rc.need

def run():
    cat,top=rc.load()
    charts=set()
    calls=[]
    for stage in range(9):
        for replica in range(32):
            call=top.call(stage,replica); calls.append(call)
            charts.update(owner.chart for owner in call.owners)
    charts.update(request.chart for request in cat.requests.idles)
    charts.update(request.chart for rows in cat.requests.prototypes for request in rows if request.kind=='COPY')
    matrices={};dets=Counter();cdigest=sha256()
    for chart in sorted(charts,key=lambda c:canonical(c.key)):
        m=reconstructed_chart(chart,cat.geometry)
        need(m==cat.chart_matrix(chart),'actual pooled chart agrees with independent reconstruction')
        need(all(dyadic(x) for row in m for x in row),'dyadic entries')
        det=determinant(m);need(dyadic_unit(det),'chart invertible at every odd prime')
        matrices[chart]=m;dets[str(det)]+=1
        cdigest.update((canonical([chart.key,str(det)])+'\n').encode())
    @lru_cache(None)
    def witness(a,b):return distinguishing_entry(matrices[a],matrices[b])
    pairs=0;wdigest=sha256();stage_pairs=Counter()
    for call in calls:
        groups=defaultdict(list)
        for role,owner in enumerate(call.owners):groups[owner.family].append((role,owner.chart))
        for family,roles in sorted(groups.items()):
            for index,(role,a) in enumerate(roles):
                for other,b in roles[:index]:
                    entry=witness(a,b);pairs+=1;stage_pairs[call.stage]+=1
                    wdigest.update((canonical([call.stage,call.replica,family,role,other,*entry])+'\n').encode())
    profile=Counter();kinds=Counter();digest=sha256();resolved=0
    for identifier,r in enumerate(cat.requests):
        need(cat.requests.identifier(*r.key)==identifier,'full request key round trip')
        if r.kind!='IDLE':
            call=top.call(r.stage,r.replica)
            need(call.requests[r.position]==identifier,'actual caller source identifier')
            owner=call.owners[r.role]
            need((r.family,r.chart)==(owner.family,owner.chart) if r.kind=='MOVE'
                 else r.family==28416 and r.source_chart==owner.chart,'typed owner/source chart')
        else:
            need(top.idle_family(identifier,r.replica)==r.family,'absolute idle family')
        resolved+=1;profile[r.base.rank]+=1;kinds[r.kind]+=1
        digest.update((canonical(r.record())+'\n').encode())
    need(profile==cat.profile and resolved==903456,'complete physical profile')
    idle_ids=[i for event in top.schedule if event['kind']=='idle'
              for replica in range(32) for i in top.idle_identifiers(event['idx'],replica)]
    need(len(idle_ids)==63936 and len(set(idle_ids))==63936,'exact once idle enumeration')
    need(set(idle_ids)==set(range(cat.requests.starts[-1],len(cat.requests))),'full idle coverage')
    controls=[]
    def reject(name,action):
        try:action()
        except (ValueError,TypeError,KeyError,AttributeError):controls.append(name)
        else:raise ValueError('accepted control '+name)
    reject('replica omitted',lambda:cat.requests.identifier('MOVE',6,19236))
    reject('wrong idle replica',lambda:top.idle_family(idle_ids[0],(cat.requests[idle_ids[0]].replica+1)%32))
    reject('legacy idle consumer',lambda:top.idles)
    reject('replica factorized profile',lambda:need(all(n%32==0 for n in profile.values()),'profile is not replica factorized'))
    first=cat.requests.identifier('MOVE',6,1,19236)
    zero=cat.requests.identifier('MOVE',6,0,19236)
    a,b=cat.requests[first],cat.requests[zero]
    need(a.role==b.role==643 and a.family==b.family==209 and a.chart!=b.chart,'actual first moved helper witness')
    reject('same-family duplicate chart',lambda:distinguishing_entry(matrices[a.chart],matrices[a.chart]))
    need(cat.codes.bits-cat.old_code_bits==5,'expanded source-code field is exactly five bits wider')
    from catalogue import Specifications
    from sources import identity
    specs=Specifications(cat); low=tuple(tuple(map(int,row)) for row in identity(64))
    rank14=next(i for i in idle_ids if cat.requests[i].base.rank==14)
    copy_id=next(i for i,r in enumerate(cat.requests.prototypes[0]) if r.kind=='COPY')
    compiled=[]
    for identifier,common in ((first,True),(first,False),(rank14,False),(copy_id,True)):
        handle=rc.source_handle(cat,identifier,common,low)
        spec=rc.resolve_handle(cat,specs,handle)
        r=cat.requests[identifier]
        need(spec.template.record[:2]==(rc.VERSION,r.replica),'compiled source retains replica identity')
        need(spec.template.rank==r.base.rank,'actual source rank')
        compiled.append({'request':identifier,'kind':r.kind,'replica':r.replica,'rank':r.base.rank,
                         'common':common,'good':spec.good})
    reject('stale source codebook',lambda:rc.resolve_handle(cat,specs,rc.SourceHandle(rc.VERSION,adapter.REQUEST_DIGEST,handle.code)))
    import copy
    wrong_context=copy.copy(cat);wrong_context.q=5
    reject('different prime source codebook',lambda:rc.resolve_handle(cat,specs,rc.SourceHandle(rc.VERSION,rc.codebook_identity(wrong_context),handle.code)))
    reject('mismatched Specifications context',lambda:rc.resolve_handle(cat,Specifications(wrong_context),handle))
    reject('untagged integer source',lambda:rc.resolve_handle(cat,specs,handle.code))
    reject('native COPY request',lambda:specs.bind(copy_id,False,low))
    return dict(status='PASS_POOLED_REPLICA_NATIVE_REQUEST_INTERFACE',request_count=resolved,
                request_kinds=dict(sorted(kinds.items())),profile=dict(sorted(profile.items())),
                rank_mass=sum(r*n for r,n in profile.items()),request_sha256=digest.hexdigest(),
                chart_count=len(charts),determinants=dict(sorted(dets.items())),chart_sha256=cdigest.hexdigest(),
                same_family_pairs=pairs,per_stage_pairs=dict(sorted(stage_pairs.items())),
                witness_sha256=wdigest.hexdigest(),unique_chart_pair_witnesses=witness.cache_info().currsize,
                old_q3_code_bits=cat.old_code_bits,new_q3_code_bits=cat.codes.bits,code_bits_delta=5,
                first_moved_request=first,replica_zero_request=zero,
                controls=controls,compiled_actual_sources=compiled,source_identity=cat.source_identity,ERASE_guards=len(cat.erase_guards),local_owner_gathers_per_low=189792,idle_owner_gathers_per_low=63936,
                routes_per_low=379584,family_scans_per_low=507456,
                full_physical_caller_executed=False,supplier_admitted=False)

if __name__=='__main__':
    value=run()
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    else:need(json.loads((HERE/'RESULT.json').read_bytes())==json.loads(json.dumps(value)),'exact frozen interface receipt')
    print(json.dumps(value,sort_keys=True))
