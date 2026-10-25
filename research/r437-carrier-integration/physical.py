"""Source-bound carrier preparation, complete geometry and completed-child consumer.

Reuse #4062/#4025 preparation and #4077 spectator methods at their actual
boundaries. The executed completed-child fibre is explicitly factored from the unexecuted
production packet. Chris R / Clear1nsight, OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from types import SimpleNamespace as NS
import ast, hashlib, importlib.util, json, sys
from functools import lru_cache
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import compiler
need=compiler.need

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def acts(m):return {k:getattr(m,k) for k in ('reads','writes','moves')}
def sub(a,b):return {k:a[k]-b[k] for k in a}
def plus(rows):return {k:sum(r[k] for r in rows) for k in ('reads','writes','moves')}
def sha(x):return hashlib.sha256(x).hexdigest()
def count_value(x):
    cells=x.tape.cells[1:];stop=cells.index(3)
    need(all(v in(0,1) for v in cells[:stop]),'canonical observer Count')
    return sum(v<<i for i,v in enumerate(cells[:stop]))

@lru_cache(None)
def source(variant,stage=0):
    cat,top=compiler.load(variant)
    from catalogue import Specifications
    import oracle
    record=compiler.early_source87(cat,top,stage)
    template=cat.template_for(record['identifier'],True)
    low=tuple(map(tuple,oracle.inverse(oracle.reduce_rational(template.preparation,3),3)))
    specs=Specifications(cat)
    handle=compiler.source_handle(cat,record['identifier'],True,low)
    spec=compiler.resolve_handle(cat,specs,handle)
    plan=specs.plan(handle.code)
    need(spec.good and plan.good and plan.rank==2,'actual changed SOURCE87 rank2 good request')
    return NS(cat=cat,top=top,record=record,specs=specs,handle=handle,spec=spec,plan=plan,low=low)

def shared_geometry():
    # Bind Tekalign's exact AST adapter to the already-loaded actual runtime.
    runtime=load('spectator_runtime_carrier',ROOT/'research/encoded-child-spectators/runtime.py')
    import words,records,stream,cardinality,cardinal_counts,layout
    env=NS(words=words,records=records,stream=stream,cardinality=cardinality,cardinal_counts=cardinal_counts,layout=layout)
    tree=ast.parse(Path(stream.__file__).read_bytes())
    node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Counter')
    def counter_type(workspace):
        ns=dict(vars(stream));ns['Tape']=lambda:workspace
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(stream.__file__),'exec'),ns)
        return ns['Counter']
    env.counter_type=counter_type
    # powers imports its sibling runtime only for need; avoid module collisions.
    ns={'__name__':'carrier_spectator_powers'}
    raw=(ROOT/'research/encoded-child-spectators/powers.py').read_text()
    need(raw.count('from runtime import need')==1,'exact spectator import')
    ns['need']=need;exec(compile(raw.replace('from runtime import need',''),'<credited spectator powers>','exec'),ns)
    powers=ns['Powers'](env)
    return powers,runtime.adapt(env,powers)

def preparation(s,optimized=True):
    import words as w,records as r,directory as d,counts,controller,macro_binding,cardinality,packet,numeric,layout,children
    from cardinal_counts import Count
    registry=[];old_init=r.Tape.__init__
    def record(t):old_init(t);registry.append(t)
    r.Tape.__init__=record
    original_callback=macro_binding.Callback;original_dir=d.high_power;original_counts=counts.high_power
    if optimized:
        f=load('carrier_forward_fields',ROOT/'research/r437-preparation-composition/forward_fields.py')
        macro_binding.Callback=f.install(controller.Callback,r,Path(controller.__file__),vars(controller))
        prior=load('carrier_radix',ROOT/'research/r437-preparation-composition/predecessor4025/verify.py');prior.authenticate()
        share=lambda value,ring,q,dimension:prior.high_power_shared(value,ring,q,dimension,cardinality.radix_power)
        d.high_power=counts.high_power=share
    Q=s.cat.codes.bits;I=13;L=3;n=64
    ia=w.Arena(I,256);ra=w.Arena(L,65536);mod=ra.literal(3);ring=w.Ring(mod)
    program=r.Program.fixture(ia,ra,2048,2,((0,s.handle.code,2,0,0,0),),Q)
    old_fields=r.Fields.fixture(ia,ra,[(s.handle.code,[[0]*64 for _ in range(64)])],Q)
    old=old_fields.tape;old_count=Count.literal(1)
    depth=ia.literal(1);size=ia.literal(n)
    spectators=[Count.literal(x) for x in (2,3,2)]
    extra=ra.literal(1);extra.head=2;ix=ia.literal(1);ix.head=2
    protected=[(x,bytes(x.cells),x.head) for x in [ra.template,ia.template]+[ra.words[i] for i in ra.live]+[ia.words[i] for i in ia.live]+[program.tape,old,old_count.tape]+[x.tape for x in spectators]]
    live=(set(ra.live),set(ia.live));old_tapes=set(map(id,registry));slots=(len(ra.words),len(ia.words))
    def snapshot():return {'record':plus([acts(t.meter) for t in registry]),'residue':acts(ra.meter),'index':acts(ia.meter)}
    phases={}
    def phase(label,fn):
        before=snapshot();out=fn();after=snapshot();phases[label]={k:sub(after[k],before[k]) for k in before};return out
    old_inspect=w.Word.inspect;w.Word.inspect=lambda _s:(_ for _ in()).throw(ValueError('runtime Word decoding forbidden'))
    ra.meter.peak_live=len(ra.live);ia.meter.peak_live=len(ia.live);start=snapshot()
    context=phase('context_create',lambda:d.Context(ring,s.cat.codes))
    fields=phase('field_control',lambda:ia.literal(2))
    directory,prefixes=phase('directory_produce',lambda:d.produce(old,depth,old_count,s.handle.code,context))
    runtime=NS(indices=ia,arena=ra,context=context,program=program,binding=NS(codes=s.cat.codes),size=size,depth=depth)
    binding=object.__new__(macro_binding.SelectedBinding);binding.specifications=s.specs
    definition=NS(code=s.handle.code,plan=s.plan)
    def validate():
        first=packet.read_prefix(directory,fields);directory.rewind()
        try:binding.validate_residual(runtime,definition,first)
        finally:first.clear()
    phase('first_prefix_validate_dispose',validate)
    # Full physical Layout, no reduced geometry. It computes the child spectator
    # cardinalities even though the corresponding enormous payload is not built.
    def make_geometry():
        columns=ia.literal(1)
        page=numeric.Geometry(s.plan,ia,columns,depth,s.handle.code,program)
        return page,layout.Layout(page,size,ring,3,*spectators),columns
    page,geometry,columns=phase('geometry_create',make_geometry)
    event=phase('child_event_controls',lambda:NS(first=ia.literal(0),second=ia.literal(126),width=ia.literal(2),depth=ia.literal(2),child_kind='good',field=0,reverse=False,half=False,source_code=s.handle.code,parent_identity=program))
    powers,method=phase('geometry_strategy',shared_geometry) if optimized else (None,layout.Layout.child_extents)
    extents=phase('complete_child_extents',lambda:method(geometry,event.first,event.second,event.width,before=spectators[0]))
    observed=[count_value(x) for x in extents]
    expected=[2,3*3**124,2]
    need(observed==expected,'actual rank2 source geometry including all124 other atoms and external gap')
    need(observed[0]*observed[1]*observed[2]*3**4==12*3**128,'complete parent/child volume equality')
    def make_child():
        first=packet.read_prefix(directory,fields);directory.rewind()
        try:return binding.child_program(runtime,definition,event,first)
        finally:first.clear()
    output=phase('first_prefix_child_program_dispose',make_child)
    outsha=sha(bytes(output.cells));dirsha=sha(bytes(directory.cells))
    # Exact typed handoff copies of all metadata. Payload copy remains explicit.
    def handoff():
        result=[]
        for src in [directory,output,prefixes.tape,*[e.tape for e in extents]]:
            dst=r.Tape();d.append_tape(src,dst);dst.rewind();need(bytes(dst.cells)==bytes(src.cells),'handoff complete metadata copy');result.append(dst)
        return result
    handoffs=phase('metadata_handoff_copy',handoff)
    def dispose():
        for t in handoffs:t.clear()
        output.clear();directory.clear();prefixes.close()
        for x in extents:x.close()
        geometry.close();page.close();ia.free_many(columns,fields,event.first,event.second,event.width,event.depth);context.close()
    phase('metadata_geometry_output_disposal',dispose)
    end=snapshot();total={k:sub(end[k],start[k]) for k in start}
    need(all(total[k]==plus([x[k] for x in phases.values()]) for k in total),'complete preparation phase invoice')
    need(live==(set(ra.live),set(ia.live)),'preparation ownership restored')
    need(all(bytes(x.cells)==raw and x.head==head for x,raw,head in protected),'borrowed bytes and heads restored')
    need(all(t.head==1 and all(v==w.BLANK for v in t.cells[1:]) for t in registry if id(t) not in old_tapes),'all created metadata backing erased')
    need(all(word.head==1 and all(v==w.BLANK for v in word.cells[1:]) for bank in(ia,ra) for i,word in enumerate(bank.words) if i not in bank.live),'released numerical backing erased')
    if powers:need(not powers.busy,'spectator workspace released')
    w.Word.inspect=old_inspect;macro_binding.Callback=original_callback;d.high_power=original_dir;counts.high_power=original_counts;r.Tape.__init__=old_init
    return {'variant':s.cat.variant,'optimized':optimized,'request':s.record,'Q':Q,'n':n,'q':3,'w':1,'history_depth':1,'complete_high_cube':True,'high_cube_rows':1,'physical_payload_executed':False,'complete_parent_payload_bits':str(12*3**128),'child_spectators':[str(x) for x in observed],'child_width':2,'program_sha256':outsha,'directory_sha256':dirsha,'phases':phases,'total':total,'new_residue_slots':len(ra.words)-slots[0],'new_index_slots':len(ia.words)-slots[1],'additional_residue_peak':ra.meter.peak_live-len(live[0]),'additional_index_peak':ia.meter.peak_live-len(live[1]),'borrowed_preserved':True,'owned_erased':True,'CSE_applied':False,'CSE_reason':'No fixed-PAIR history; actual generated child is GOOD. No hypothetical CSE saving.'}

def weighted_child(s, seed=1, losing=False, optimized=True, hoist=True):
    """Complete rank2 child on four atoms; actual fresh source coefficients.

    The executable child domain B=2,G=3,S=2 is complete (972 bits). The parent
    projection has G=3*3**124, whose lifting theorem is stated in PHYSICAL.md.
    """
    import words as w,records as r,directory,macro_binding,packet_engine,trace,numeric,layout,episode,counts,controller,cardinality,peel,packet
    from cardinal_counts import Count
    registry=[];old_init=r.Tape.__init__
    def record(t):old_init(t);registry.append(t)
    r.Tape.__init__=record
    original_callback=macro_binding.Callback;original_dir=directory.high_power;original_counts=counts.high_power
    if optimized:
        f=load('carrier_forward_fields_join',ROOT/'research/r437-preparation-composition/forward_fields.py')
        macro_binding.Callback=f.install(controller.Callback,r,Path(controller.__file__),vars(controller))
        prior_radix=load('carrier_radix_join',ROOT/'research/r437-preparation-composition/predecessor4025/verify.py');prior_radix.authenticate()
        share=lambda value,ring,q,dimension:prior_radix.high_power_shared(value,ring,q,dimension,cardinality.radix_power)
        directory.high_power=counts.high_power=share
    ia=w.Arena(13,512);ra=w.Arena(3,65536);mod=ra.literal(3);ring=w.Ring(mod)
    program=r.Program.fixture(ia,ra,2048,2,((0,s.handle.code,2,0,0,0),),s.cat.codes.bits)
    old_fields=r.Fields.fixture(ia,ra,[(s.handle.code,[[0]*64 for _ in range(64)])],s.cat.codes.bits)
    old_count=Count.literal(1)
    parent_unused=Count.literal(9475)
    parent_depth=ia.literal(1);parent_size=ia.literal(64)
    binding=object.__new__(macro_binding.SelectedBinding);binding.specifications=s.specs
    definition=NS(code=s.handle.code,plan=s.plan)
    before,gap,suffix=[Count.literal(x) for x in(2,3,2)]
    nbits=972;source=r.Tape();target=r.Tape()
    initial=bytes(((i*17+i//3+seed*7)^(i//5))&1 for i in range(nbits))
    target_bits=bytes(((i*13+i//7+seed*3)^(i//2))&1 for i in range(nbits))
    for bit in initial:source.append(bit)
    for bit in target_bits:target.append(bit)
    source.rewind();target.rewind()
    spectator=ra.literal(1);spectator.head=2
    protected=[(x,bytes(x.cells),x.head) for x in [ia.template,ra.template]+[ia.words[i] for i in ia.live]+[ra.words[i] for i in ra.live]+[program.tape,old_fields.tape,old_count.tape,parent_unused.tape,source,target,before.tape,gap.tape,suffix.tape]]
    live=(set(ra.live),set(ia.live));prior=set(map(id,registry))
    def snapshot():return {'record':plus([acts(t.meter) for t in registry]),'residue':acts(ra.meter),'index':acts(ia.meter)}
    phases={};coef_calls=[];lifetime=[]
    def phase(name,fn):
        x=snapshot();out=fn();y=snapshot();phases[name]={k:sub(y[k],x[k]) for k in x};return out
    old_inspect=w.Word.inspect;w.Word.inspect=lambda _:(_ for _ in()).throw(ValueError('runtime numerical decoding forbidden'))
    baseline=snapshot()
    context=phase('context_create',lambda:directory.Context(ring,s.cat.codes))
    runtime=NS(indices=ia,arena=ra,context=context,program=program,binding=NS(codes=s.cat.codes),depth=parent_depth,size=parent_size)
    current_directory,prefixes=phase('directory_produce',lambda:directory.produce(old_fields.tape,parent_depth,old_count,s.handle.code,context))
    fields=NS(tape=current_directory)
    parent_fields=phase('current_fields_control',lambda:ia.literal(2))
    import packet
    def first_action(action):
        first=packet.read_prefix(current_directory,parent_fields);current_directory.rewind()
        try:return action(first)
        finally:first.clear()
    phase('actual_validate_residual',lambda:first_action(lambda first:binding.validate_residual(runtime,definition,first)))
    child_event=NS(child_kind='good',field=0,reverse=False,half=False)
    child_program=phase('actual_child_program',lambda:first_action(lambda first:binding.child_program(runtime,definition,child_event,first))) if hoist else None
    if losing:
        need(hoist,'losing duplicate control belongs to paid hoisted path')
        def redundant():
            duplicate=first_action(lambda first:binding.child_program(runtime,definition,child_event,first))
            need(bytes(duplicate.cells)==bytes(child_program.cells),'same output losing control');duplicate.clear()
        phase('redundant_child_constructor_losing_control',redundant)
    produced_program_sha=sha(bytes(child_program.cells)) if hoist else None;produced_directory_sha=sha(bytes(current_directory.cells))
    powers,geometry_method=phase('geometry_strategy',shared_geometry) if optimized else (None,layout.Layout.child_extents)
    def parent_geometry():
        cols=ia.literal(1);g=numeric.Geometry(s.plan,ia,cols,parent_depth,s.handle.code,program)
        ll=layout.Layout(g,parent_size,ring,3,before,gap,suffix)
        first,second,width=[ia.literal(v) for v in(0,126,2)]
        ext=geometry_method(ll,first,second,width,before=before)
        need([count_value(y) for y in ext]==[2,3*3**124,2],'full actual parent spectator projection')
        ia.free_many(first,second,width);ll.close();g.close();ia.free(cols)
        return ext
    parent_extents=phase('full_parent_child_extents',parent_geometry)
    def handoff():
        out=[]
        for src in [current_directory,child_program,prefixes.tape,parent_unused.tape,*[v.tape for v in parent_extents]]:
            dst=r.Tape();directory.append_tape(src,dst);dst.rewind();need(bytes(dst.cells)==bytes(src.cells),'complete fresh metadata handoff');out.append(dst)
        return out
    handoffs=phase('complete_metadata_handoff',handoff) if hoist else []
    def adopt():
        child_size=ia.literal(2);child_depth=ia.literal(2);child_rows=Count.literal(1)
        child_prefixes=Count(handoffs[2]) if hoist else prefixes
        child_runtime=NS(indices=ia,arena=ra,context=context,binding=NS(codes=s.cat.codes),size=child_size,depth=child_depth)
        child_runtime.program=macro_binding.view(r.Program,child_runtime,handoffs[1]) if hoist else program
        binding.ambient=s.handle.code
        incoming=binding.incoming(child_runtime) if hoist else None
        return child_size,child_depth,child_rows,child_prefixes,child_runtime,incoming
    child_size,child_depth,child_rows,child_prefixes,child_runtime,incoming=phase('adopt_actual_handoff_metadata' if hoist else 'baseline_child_geometry_controls',adopt)
    def coefficient(prefix,request):
        from dataclasses import replace
        need(request.kind=='child' and request.child_kind=='good' and not request.half and not request.reverse,'typed completed GOOD child request')
        eligible=(request.field==0 and request.reference is None and not request.reverse_adapter)
        if hoist:eligible=eligible and w.Unsigned(ia).compare(request.coordinate,child_size)<0
        value=incoming.coefficient(prefix,replace(request,kind='incoming')) if hoist and eligible else binding.coefficient(runtime,definition,prefix,request)
        v=sum(x<<j for j,x in enumerate(value.cells[1:]) if x in(0,1))
        coordinate=sum(x<<j for j,x in enumerate(request.coordinate.cells[1:]) if x in(0,1))
        coef_calls.append({'coordinate':coordinate,'negative_inverse':request.negative_inverse,'value':v})
        return value
    def execute():
        # A completed below-cutoff child has two width2 banks. Canonical
        # peel.run is an internal-node method and rejects n<64; this explicit
        # bridge uses its unchanged leaf primitives and the consumed child's
        # incoming coefficient interface, without weakening that guard.
        cols=ia.literal(1);g=numeric.Geometry(NS(dimension=2,rank=2),ia,cols,child_depth,s.handle.code,child_runtime.program)
        ll=layout.Layout(g,child_size,ring,3,before,gap,suffix)
        first,second,span=[ia.literal(v) for v in(0,2,2)]
        field_count=ia.literal(2)
        try:
            return packet_engine.run(source,trace.leaf(g,first,second,span,'good'),ll,handoffs[0] if hoist else current_directory,child_prefixes,field_count,coefficient,observe=lifetime.append)
        finally:
            ll.close();g.close();ia.free_many(cols,first,second,span,field_count)
    stable=[(t,bytes(t.cells),t.head) for t in [program.tape,current_directory,*handoffs]]
    returned=phase('actual_complete_weighted_child',execute)
    need(all(bytes(t.cells)==raw and t.head==head for t,raw,head in stable),'immutable source program and directory throughout completed child')
    need(returned is not source and lifetime==['enter','return'],'actual completed child owns protected returned packet')
    need(len(coef_calls)==12 and [q['value'] for q in coef_calls]==[2,2,1,1,2,2]*2,'six actual source coefficients per atom, two atoms')
    need([q['coordinate'] for q in coef_calls]==[0]*6+[1]*6,'complete rank2 child coverage')
    expected=bytearray()
    for b in range(2):
      for x0 in range(3):
       for x1 in range(3):
        for g in range(3):
         for y0 in range(3):
          for y1 in range(3):
           for z in range(2):
            at=((((((b*3+2*y1%3)*3+2*y0%3)*3+g)*3+2*x1%3)*3+2*x0%3)*2+z)
            expected.append(initial[at])
    need(bytes(returned.cells[1:])==bytes(expected),'complete four-atom weighted pullback incl all finite spectators')
    # D forward has the immediate literal carrier consumer helper467. C's
    # same child comparison stops at return; it has no such immediate ADD.
    consumer=None;consumer_sha=None
    if s.cat.variant=='D':
        call=s.top.call(s.record['key'][1],s.record['key'][2]);pos=s.record['position']+1
        consumer_event=call.events[pos]
        need(consumer_event[0]==1 and consumer_event[2]==87,'literal next SOURCE87 reader')
        consumer_count=phase('consumer_old_count',lambda:Count.literal(1));fibre=phase('consumer_fibre',lambda:Count.literal(nbits))
        consumer=phase('actual_literal_xor_consumer',lambda:episode.xor_packet(returned,target,context,consumer_count,fibre))
        need(bytes(consumer.cells[1:])==bytes(a^b for a,b in zip(expected,target_bits)),'actual literal consumer receives computed child output')
        consumer_sha=sha(bytes(consumer.cells))
    else:consumer_event=None;pos=None
    return_sha=sha(bytes(returned.cells))
    if consumer is not None:
        def consumer_dispose():consumer.clear();consumer_count.close();fibre.close()
        phase('literal_consumer_disposal',consumer_dispose)
    def dispose():
        returned.clear();ia.free_many(child_size,child_depth);child_rows.close()
        if hoist:child_prefixes.close()
        for t in handoffs:t.clear()
        for e in parent_extents:e.close()
        if hoist:child_program.clear()
        current_directory.clear();prefixes.close();context.close();ia.free(parent_fields)
    phase('return_geometry_metadata_disposal',dispose)
    final=snapshot();total={k:sub(final[k],baseline[k]) for k in baseline}
    need(all(total[k]==plus([p[k] for p in phases.values()]) for k in total),'full child phase cost')
    need(live==(set(ra.live),set(ia.live)),'child numerical ownership restored')
    need(all(bytes(x.cells)==raw and x.head==head for x,raw,head in protected),'child borrowed bytes/heads preserved')
    need(all(t.head==1 and all(v==w.BLANK for v in t.cells[1:]) for t in registry if id(t) not in prior),'all child/consumer owned record work erased')
    need(all(word.head==1 and all(v==w.BLANK for v in word.cells[1:]) for bank in(ia,ra) for i,word in enumerate(bank.words) if i not in bank.live),'all released numerical work erased')
    w.Word.inspect=old_inspect;r.Tape.__init__=old_init
    macro_binding.Callback=original_callback;directory.high_power=original_dir;counts.high_power=original_counts
    return {'variant':s.cat.variant,'optimized':optimized,'consume_produced_program':hoist,'losing_control':losing,'request':s.record,'q':3,'w':1,'source_root':2048,'current_width':64,'history_depth':1,'consumed_child_history_depth':2,'consumed_actual_handoff_program':hoist,'history_kind':'actual GOOD rank2 source; generic admitted history, no selected-root reachability assertion','child_width':2,'actual_child_program_sha256':produced_program_sha,'actual_directory_sha256':produced_directory_sha,'parent_unused_rows':9475,'executed_child_rows':1,'full_parent_payload_bits':str(9475*12*3**128),'full_parent_child_spectators':['2',str(3*3**124),'2'],'complete_child_bits':nbits,'spectators':[2,3,2],'coefficient_calls':coef_calls,'phases':phases,'total':total,'return_sha256':return_sha,'consumer_sha256':consumer_sha,'literal_consumer_event':consumer_event,'literal_consumer_position':pos,'source_preserved':True,'owned_erased':True,'full_production_parent_executed':False}

def checked_child(s, **kwargs):
    import admission,numerical
    domain=admission.RootDomain(2048,64,1,1,3,13,s.cat.codes.bits,numerical.stock_unit(3,1))
    result,receipt=admission.checked_entry(s.cat,s.specs,s.handle,domain,
        lambda:weighted_child(s,**kwargs),mode='semantic',expected_key=tuple(s.record['key']),expected_common=True)
    result['entry_admission']=receipt
    result['entry_gate_unit']='host source/parameter validation; not a fixed-tape scan tariff'
    return result

def acquisition(s,drop_role=None):
    """Trace actual Driver.local chronology with explicitly symbolic packets.

    This establishes read order and literal source identity. It does not claim
    to execute GL64 gather, route, or preceding residual payload primitives.
    """
    from unittest.mock import patch
    driver=compiler.logical_driver()
    call=s.top.call(s.record['key'][1],s.record['key'][2])
    acquisitions=[];literals=[];calls=[];objects=[]
    class Packet:
        def __init__(self,roots):self.roots=frozenset(roots);self.cleared=False;objects.append(self)
        def clear(self):self.cleared=True
        def rewind(self):pass
    families={family:Packet({('family',family)}) for family in {o.family for o in call.owners}}
    def owner(matrix,low,codes):
        key=sha(compiler.canonical([[str(v) for v in row] for row in matrix]).encode())
        return key,('forward',key),('backward',key)
    def gather(packet,context,old_count,native,fibre):
        role=len(acquisitions);o=call.owners[role]
        need(packet is families[o.family] and not packet.cleared,'original family read before local mutations')
        acquisitions.append((role,o.family,native))
        return Packet(set() if role==drop_role else {role})
    def route(packet,*args):return Packet(packet.roots)
    def xor(source,target,*args):return Packet(source.roots|target.roots)
    class Stop(Exception):pass
    class Consumer:
        def apply(self,payload,identifier,common,low,*args,**kwargs):
            calls.append(identifier)
            if identifier==s.record['identifier']:
                need(len(acquisitions)==659 and set(r[0] for r in acquisitions)==set(range(659)),'all arbitrary dirty roles acquired before changed request')
                need(87 in payload.roots,'SOURCE87 original dirty dependency read before early MOVE')
                raise Stop()
            return Packet(payload.roots)
    observe=lambda kind,*labels:literals.append(labels) if kind=='literal' else None
    d=driver.Driver(NS(codes=s.cat.codes),s.top,Consumer(),NS(rewind=lambda:None),None,None,None,None,None,observe=observe)
    with patch.object(driver,'compile_owner',owner),patch.object(driver,'gather',gather),patch.object(driver,'route_packet',route),patch.object(driver,'xor_packet',xor),patch.object(driver,'clone_packet',lambda p,*a:Packet(p.roots)):
        it=d.local(families,call,s.low)
        try:
            while True:next(it)
        except Stop:pass
        else:raise ValueError('target source request not reached')
        finally:it.close()
    need(len(literals)==s.record['position']+1,'every chronological literal before and including changed MOVE')
    need(calls[-1]==s.record['identifier'],'fresh request delivered to actual Driver consumer')
    need(all(p.cleared for p in objects if p not in families.values()),'symbolic staged packets disposed on controlled stop')
    return {'request':s.record,'gathers_before_first_move':659,'original_dirty_roles':list(range(659)),'literal_prefix_events':len(literals),'preceding_and_current_recursive_sites':len(calls),'source87_original_acquired':True,'actual_driver_source_sha256':sha((ROOT/'research/selected-bit-physical-caller/inputs/pr2753/driver.py').read_bytes()),'primitive_execution':'symbolic packet interface, not GL64 physical payload','cleanup':True}

def wrong_step_control(s):
    import words as w,records as r,directory,macro_binding
    from plan import Request
    ia=w.Arena(13,512);ra=w.Arena(3,65536);mod=ra.literal(3);context=directory.Context(w.Ring(mod),s.cat.codes)
    parent=r.Program.fixture(ia,ra,2048,2,((0,s.handle.code,2,0,0,0),),s.cat.codes.bits)
    fields=r.Fields.fixture(ia,ra,[(s.handle.code,[[0]*64 for _ in range(64)])]*2,s.cat.codes.bits)
    runtime=NS(indices=ia,arena=ra,context=context,program=parent,binding=NS(codes=s.cat.codes))
    binding=object.__new__(macro_binding.SelectedBinding);binding.specifications=s.specs;binding.ambient=s.handle.code
    definition=NS(code=s.handle.code,plan=s.plan)
    output=binding.child_program(runtime,definition,NS(child_kind='good',field=0,reverse=False,half=False),fields.tape)
    steps=[i for i,v in enumerate(output.cells) if v==r.STEP]
    need(len(steps)==2,'actual produced two-step program')
    rank_bit=steps[-1]+1+(r.FINITE_BITS+1)+(s.cat.codes.bits+1)
    need(output.cells[rank_bit]==0,'actual produced rank2 low bit')
    output.cells[rank_bit]=1
    child=NS(indices=ia,arena=ra,context=context,binding=NS(codes=s.cat.codes),size=ia.literal(2),depth=ia.literal(2))
    child.program=macro_binding.view(r.Program,child,output);index=ia.literal(0)
    live=(set(ra.live),set(ia.live));saved=[(x,bytes(x.cells),x.head) for x in(parent.tape,fields.tape,output)]
    try:binding.incoming(child).coefficient(fields.tape,Request('incoming',index))
    except ValueError as e:need(str(e)=='actual selected rank','mutated produced STEP rejects at source rank')
    else:raise ValueError('wrong produced STEP accepted')
    need(live==(set(ra.live),set(ia.live)),'wrong STEP numerical rollback')
    need(all(bytes(x.cells)==raw and x.head==head for x,raw,head in saved),'wrong STEP borrowed restoration')
    output.clear();parent.tape.clear();fields.tape.clear();context.close();context.ring.close();ia.free_many(index,child.size,child.depth);ra.free(mod)
    need(not ia.live and not ra.live,'control terminal numerical cleanup')
    return 'actual produced STEP rank2-to3 rejected before child payload; borrowed state restored'

def part(name):
    if name=='preparation':
        prep=[]
        for variant in 'CD':prep.extend(preparation(source(variant),o) for o in(False,True))
        for offset in(0,2):
            old,new=prep[offset:offset+2]
            need(old['program_sha256']==new['program_sha256'] and old['directory_sha256']==new['directory_sha256'],'matched preparation output')
            need(old['total']['residue']['moves']>new['total']['residue']['moves'],'preparation residue traversal saving; other lanes retained explicitly')
        need(prep[0]['total']==prep[2]['total'] and prep[1]['total']==prep[3]['total'],'exact C/D preparation equality')
        return prep
    if name in ('C','D','losing','reverse','reconstruct'):
        return checked_child(source('C' if name=='C' else 'D',int(name=='reverse')),losing=name=='losing',hoist=name!='reconstruct')
    need(name=='controls','known physical part')
    acquisitions=[acquisition(source(v,stage)) for v in 'CD' for stage in(0,1)]
    controls=[wrong_step_control(source('D'))]
    for stage in(0,1):
        try:acquisition(source('D',stage),drop_role=87)
        except ValueError as e:need(str(e)=='SOURCE87 original dirty dependency read before early MOVE','missing original dirty read rejection')
        else:raise ValueError('missing original dirty read accepted')
        controls.append('missing original SOURCE87 dirty acquisition rejected orientation '+str(stage))
    return {'acquisition':acquisitions,'controls':controls}

def audit():
    # Independent processes isolate the canonical runtime module namespace and
    # allow a bounded replay of these expensive encoded arithmetic fixtures.
    import subprocess,concurrent.futures
    names=('preparation','C','D','losing','reverse','reconstruct','controls')
    def run_part(name):
        command=[sys.executable,'-I','-B']+([] if __debug__ else ['-O'])+[str(Path(__file__).resolve()),'--part',name]
        p=subprocess.run(command,capture_output=True,text=True,timeout=600)
        need(p.returncode==0,'physical part '+name+': '+p.stderr)
        return json.loads(p.stdout)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(run_part,names))
    prep=results[0];children=results[1:6]
    c,d,losing,reverse,reconstruct=children
    common=lambda x:{k:v for k,v in x['phases'].items() if 'consumer' not in k}
    need(common(c)==common(d),'exact C/D matched complete return boundary invoice')
    need(c['return_sha256']==d['return_sha256']==losing['return_sha256']==reverse['return_sha256'],'matched actual computed child return')
    need(d['consumer_sha256']==losing['consumer_sha256']==reconstruct['consumer_sha256'],'genuine same-output losing construction')
    need(all(reconstruct['total'][lane][action]>=d['total'][lane][action] for lane in d['total'] for action in d['total'][lane]),'paid handoff program consumption dominates rebuilding at each coefficient')
    need(all(losing['total'][lane][action]>=d['total'][lane][action] for lane in d['total'] for action in d['total'][lane]),'losing control every lane paid')
    need(losing['total']['record']['reads']>d['total']['record']['reads'],'redundant constructor strict loss')
    acquisitions=results[6]['acquisition'];controls=results[6]['controls']
    return {'status':'PASS_SOURCE_BOUND_CARRIER_REGIONAL_CALLER','preparation_comparison':prep,'integrated_children':children,'acquisition':acquisitions,'controls':controls,'CSE':'not applied; no fixed-PAIR ancestor guard at these actual GOOD contexts','full_production_execution':False,'scope':'Actual fresh compiler -> encoded directory/program/handoff -> complete 972-bit four-atom child -> literal D consumer. Parent GL64 gather/route and124-atom spectator expansion remain quantified/inherited, not physically executed.'}

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--audit',action='store_true');p.add_argument('--part',choices=('preparation','C','D','losing','reverse','reconstruct','controls'));p.add_argument('--check',action='store_true');p.add_argument('--variant',choices=['C','D'],default='D');p.add_argument('--original',action='store_true');p.add_argument('--output');p.add_argument('--atom',action='store_true');p.add_argument('--acquisition',action='store_true');p.add_argument('--stage',type=int,default=0);p.add_argument('--losing',action='store_true');a=p.parse_args()
    s=None if a.audit or a.check or a.part else source(a.variant,a.stage);result=part(a.part) if a.part else audit() if a.audit or a.check else acquisition(s) if a.acquisition else checked_child(s,losing=a.losing,optimized=not a.original) if a.atom else preparation(s,not a.original)
    raw=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.check:
        need(json.loads((HERE/'PHYSICAL-RESULT.json').read_text())==result,'frozen complete physical receipt');print('PASS_CARRIER_PHYSICAL')
    elif a.output:Path(a.output).write_text(raw)
    else:print(raw)
if __name__=='__main__':main()
