"""Full fresh catalogue, owner and algebra checks. See COMPILER.md for scope."""
from collections import Counter,defaultdict
from dataclasses import replace
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
import json
import sys
import compiler as c

need=c.need

def projector_certificate(cat):
    """Idempotence and an exact characteristic polynomial for every base."""
    from check_transport import dyadic,dyadic_unit,determinant
    result=[]
    for key,base in sorted(cat.bases.items()):
        if base.kind=='idle':
            need(len(set(base.data))==base.rank,'idle coordinate projector rank')
            result.append([key,base.rank,'coordinate',list(base.data)])
            continue
        a=[list(map(F,row)) for row in base.data]
        need(len(a)==8 and all(len(r)==8 for r in a),'local residual dimension')
        need(all(dyadic(x) for row in a for x in row),'projector denominators invertible at odd primes')
        square=[[sum(a[i][k]*a[k][j] for k in range(8)) for j in range(8)] for i in range(8)]
        need(square==a,'fresh base idempotence')
        # Rational elimination records a nonzero rank minor. Uniform odd-prime
        # rank follows instead from the exact characteristic polynomial below.
        b=[r[:] for r in a];rows=list(range(8));pivots=[];ri=0
        for j in range(8):
            i=next((i for i in range(ri,8) if b[i][j]),None)
            if i is None:continue
            b[i],b[ri]=b[ri],b[i];rows[i],rows[ri]=rows[ri],rows[i]
            pivots.append((rows[ri],j));pivot=b[ri][j]
            for k in range(ri+1,8):
                ratio=b[k][j]/pivot
                b[k]=[x-ratio*y for x,y in zip(b[k],b[ri])]
            ri+=1
        need(ri==base.rank,'rational projector rank')
        minor=[[a[i][j] for _,j in pivots] for i,_ in pivots]
        det=determinant(minor)
        need(det!=0,'rational rank minor')
        values=[]
        for t in range(9):
            char=determinant([[F(t if i==j else 0)-a[i][j] for j in range(8)] for i in range(8)])
            need(char==F(t)**(8-base.rank)*F(t-1)**base.rank,'exact projector characteristic polynomial')
            values.append(str(char))
        result.append([key,base.rank,pivots,str(det),values])
    return {'bases':len(result),'local':sum(b.kind=='local' for b in cat.bases.values()),
            'sha256':c.digest(result),'domain':'every odd prime; dyadic idempotent plus characteristic polynomial t^(8-r)(t-1)^r'}

def full(cat,top):
    from check_transport import reconstructed_chart,dyadic,dyadic_unit,determinant,distinguishing_entry
    matrices={};chartrows=[]
    for chart in sorted(cat.charts,key=lambda x:c.canonical(x.key)):
        matrix=reconstructed_chart(chart,cat.geometry)
        need(matrix==cat.chart_matrix(chart),'independent reconstructed chart')
        need(all(dyadic(x) for row in matrix for x in row),'dyadic chart')
        det=determinant(matrix);need(dyadic_unit(det),'invertible every odd prime')
        matrices[chart]=matrix;chartrows.append([chart.key,str(det)])
    @lru_cache(None)
    def witness(a,b):return distinguishing_entry(matrices[a],matrices[b])
    wdigest=sha256();pairs=0
    for stage in range(9):
        for replica in range(32):
            call=top.call(stage,replica);groups=defaultdict(list)
            for role,owner in enumerate(call.owners):groups[owner.family].append((role,owner.chart))
            for family,owners in sorted(groups.items()):
                for i,(role,a) in enumerate(owners):
                    for other,b in owners[:i]:
                        entry=witness(a,b);pairs+=1
                        wdigest.update((c.canonical([stage,replica,family,role,other,*entry])+'\n').encode())
    for identifier,r in enumerate(cat.requests):
        need(cat.identifier(*r.key)==identifier,'every literal request roundtrip')
        if r.kind=='IDLE':need(top.idle_family(identifier,r.replica)==r.family,'absolute IDLE family')
        else:
            call=top.call(r.stage,r.replica)
            need(call.requests[r.position]==identifier,'actual caller request position')
            owner=call.owners[r.role]
            need((r.family,r.chart)==(owner.family,owner.chart) if r.kind=='MOVE' else
                 r.family==28416 and r.source_chart==owner.chart,'native/source owner binding')
    ids=[i for event in top.schedule if event['kind']=='idle' for replica in range(32)
         for i in top.idle_identifiers(event['idx'],replica)]
    need(len(ids)==len(set(ids))==len(cat.requests.idles),'exactly once IDLE')
    need(set(ids)==set(range(cat.requests.starts[-1],len(cat.requests))),'complete IDLE enumeration')
    return {'charts':len(chartrows),'chart_sha256':c.digest(chartrows),'owner_pairs':pairs,
            'owner_witness_sha256':wdigest.hexdigest(),'idle_enumeration':len(ids),
            'projectors':projector_certificate(cat)}

def controls(old,new,top):
    from catalogue import Specifications
    from sources import identity
    low=tuple(tuple(map(int,row)) for row in identity(64));specs=Specifications(new)
    report=[]
    def reject(name,action):
        try:action()
        except (ValueError,TypeError,KeyError,AttributeError):report.append(name)
        else:raise ValueError('accepted negative control '+name)
    witness=c.early_source87(new,top)
    identifier=witness['identifier'];handle=c.source_handle(new,identifier,False,low)
    spec=c.resolve_handle(new,specs,handle)
    need(spec.template.record[:2]==('pooled-replica-request-v1',0),'compiled explicit replica')
    reject('stale baseline handle',lambda:c.resolve_handle(new,specs,c.source_handle(old,identifier,False,low)))
    reject('wrong replica',lambda:c.resolve_handle(new,specs,replace(handle,request_key=('MOVE',0,1,witness['position']))))
    reject('legacy replica blind lookup',lambda:new.identifier('MOVE',0,witness['position']))
    reject('legacy IDLE enumeration',lambda:top.idles)
    reject('mismatched Specifications',lambda:c.resolve_handle(new,Specifications(old),handle))
    changed=copy_catalogue(new);changed.q=5
    reject('cross prime context',lambda:c.resolve_handle(new,specs,replace(handle,identity=c.codebook_identity(changed))))
    reject('untagged integer code',lambda:c.resolve_handle(new,specs,handle.code))
    copyid=next(i for i,r in enumerate(new.requests) if r.kind=='COPY')
    reject('native COPY',lambda:specs.bind(copyid,False,low))
    # A correctly typed numeric source code resolves differently after a context
    # change: tagging is necessary even when field widths happen to coincide.
    compiled=[]
    for stage in (0,1):
        item=c.early_source87(new,top,stage)
        for common in (False,True):
            h=c.source_handle(new,item['identifier'],common,low);s=c.resolve_handle(new,specs,h)
            compiled.append({'request':item['identifier'],'stage':stage,'rank':s.template.rank,'common':common,'good':s.good})
    return {'rejected':report,'compiled_changed_sources':compiled}

def copy_catalogue(cat):
    import copy
    return copy.copy(cat)

def driver_schedule(cat,top):
    """Actual global_word control flow, formal per-low payload substitution.

    Only this metadata replay substitutes tape functions. The returned Driver
    class itself retains real gather/route/residual/return functions for callers.
    """
    from control import LocalState
    from unittest.mock import patch
    module=c.logical_driver()
    class FormalTape:
        def close(self):pass
        def clear(self):pass
    class TraceDriver(module.Driver):
        def local(self,families,call,low):
            state=LocalState(call)
            for position,_event in enumerate(call.events):
                op,role=state.accept(position)
                if op in (0,2):yield call.requests[position]
            state.finish()
        def idle(self,families,identifier,replica):
            need(top.idle_family(identifier,replica)==cat.requests[identifier].family,'driver exact IDLE replica')
            for _low in cat.low_classes():yield identifier
    trace=object.__new__(TraceDriver)
    trace.topology=top;trace.context=None;trace.observe=None;trace.old_count=None;trace.fibre=None
    families=[FormalTape() for _ in range(top.families)]
    original=cat.low_classes;cat.low_classes=lambda:iter(('formal-low-label',))
    try:
        with patch.object(module,'family_rows',lambda _context:FormalTape()),patch.object(module,'xor_family',lambda *_args:FormalTape()):
            ids=list(trace.global_word(families))
    finally:cat.low_classes=original
    need(len(ids)==len(set(ids))==len(cat.requests),'actual Driver complete once-per-low paid enumeration')
    need(set(ids)==set(range(len(cat.requests))),'actual Driver all fresh IDs')
    h=sha256()
    for identifier in ids:h.update((str(identifier)+'\n').encode())
    return {'requests_per_formal_low_label':len(ids),'chronological_identifier_sha256':h.hexdigest(),
            'source':'actual retained Driver.global_word with single explicit-replica IDLE adaptation',
            'scope':'metadata/control-flow replay; family/tape payloads substituted; no physical execution'}

def regional_emitter(cat,top):
    """A real canonical plan emitter on one actual IDLE, identity low class.

    This is an explicitly bounded region of the finite compiler, not full GL64
    enumeration or physical execution. Every replica IDLE was checked above.
    """
    from catalogue import Specifications
    from macro_binding import SelectedBinding
    from sources import identity
    from types import SimpleNamespace
    import macro_code
    identifier=next(i for i,r in enumerate(cat.requests) if r.kind=='IDLE' and r.base.rank==14)
    request=cat.requests[identifier]
    region=SimpleNamespace(catalogue=cat,replicas=32,
        schedule=({'kind':'idle','idx':request.stage},),
        idle_identifiers=lambda child,replica:(identifier,) if (child,replica)==(request.stage,request.replica) else (),
        idle_family=top.idle_family)
    specifications=Specifications(cat);binding=SelectedBinding(specifications)
    low=tuple(tuple(map(int,row)) for row in identity(64))
    original=cat.low_classes
    cat.low_classes=lambda:iter((low,))
    try:
        try:macro_code.compile_node(region,binding)
        except AttributeError:pass
        else:raise ValueError('old replica-blind macro compiler accepted new topology')
        emitted=c.compile_node(region,binding)
    finally:
        cat.low_classes=original
    residuals=[row[2] for row in emitted.operations if row[0]=='residual_begin']
    need(len(residuals)==1 and residuals[0].identifier==identifier and not residuals[0].common,
         'actual native IDLE compiled exactly once')
    need(emitted.operations[0]==('node',) and emitted.operations[-1]==('return',),'regional terminal control')
    tags=Counter(row[0] for row in emitted.operations)
    need(tags['gather']==tags['scatter']==tags['clear']==1,'regional gather/return/cleanup emitter')
    wrong=SimpleNamespace(catalogue=object())
    try:c.compile_node(region,wrong)
    except ValueError:pass
    else:raise ValueError('macro source/native context mixup accepted')
    return {'request':identifier,'replica':request.replica,'rank':14,'q':cat.q,
            'dimension':64,'low_classes_executed':1,'source_specification_good':specifications[residuals[0].code].good,
            'operations':dict(sorted(tags.items())),
            'old_replica_blind_compiler_rejected':True,'source_native_context_mixup_rejected':True,
            'scope':'actual canonical SelectedBinding and Cursor plan; one actual IDLE, identity low header; no physical execution'}

def run():
    old,ot=c.load('C');new,nt=c.load('D')
    return {'status':'PASS_FRESH_CARRIER_POOLED_COMPILER',
            'C':dict(c.compiler_receipt(old),coverage=full(old,ot)),
            'D':dict(c.compiler_receipt(new),coverage=full(new,nt)),
            'controls':controls(old,new,nt),'regional_emitter':regional_emitter(new,nt),'driver_schedule':driver_schedule(new,nt),
            'incremental_code_bits':new.codes.bits-old.codes.bits,
            'physical_execution':False,'numerical_admission':'separate numerical.py premise'}

if __name__=='__main__':
    result=run()
    if '--write' in sys.argv:(c.HERE/'COMPILER-CHECKS.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(json.loads((c.HERE/'COMPILER-CHECKS.json').read_text())==json.loads(json.dumps(result)),'frozen full compiler receipt')
    print(json.dumps(result,sort_keys=True))
