"""Actual OQ4 source records through nested fixed-role CALL/RETURN.

The 46-bit controlled payload is deliberately not a complete GL64 packet.
No claim that the controlled return executes a residual permutation.
Derived from Jose Manuel's macro_selected_checks and zxv/PR3690.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from unittest.mock import patch
import adapter


def body(tape):
    from words import BLANK
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def run():
    catalogue, topology = adapter.load()
    from catalogue import Specifications
    from cardinal_counts import Count
    from check_support import audit, inspect_count, no_decode
    from frame_checks import snapshot, restored
    from macro_binding import SelectedBinding, view
    from macro_code import Code
    from macro_machine import Machine
    import macro_machine
    import oracle
    from packet import read_prefix
    from plan import Request
    from records import Fields, Program, Tape
    from controller import Callback
    from words import Arena, need

    specifications = Specifications(catalogue)
    binding = SelectedBinding(specifications)
    ancestor_id = next(i for i,r in enumerate(catalogue.requests)
                       if r.kind == 'IDLE' and r.base.rank == 26)
    copy_id = catalogue.identifier('COPY', 0, 22014)
    ancestor_record, copy_record = (catalogue.requests[i] for i in (ancestor_id,copy_id))
    need(ancestor_id == 27776 and ancestor_record.role == 209 and ancestor_record.stage == 6,
         'actual current OQ4 idle, not a synthetic template')
    need(copy_id == 1603 and copy_record.role == 475 and copy_record.old_frame == 515,
         'actual COPY515 catalogue site')
    definitions = []
    for identifier,common in ((ancestor_id,False),(copy_id,True)):
        template = catalogue.template_for(identifier,common)
        low = tuple(map(tuple,oracle.inverse(oracle.reduce_rational(template.preparation,3),3)))
        definition = binding.residual(identifier,common,low,0)
        need(definition.plan.good, 'actual good native/common source class')
        definitions.append(definition)
    ancestor, copy = definitions
    need([len(d.plan.commands) for d in definitions]==[6722,4936],
         "actual rank26/rank7 full forward adapter invoices")
    window = catalogue.template['local_programs']['forward'][22014:22079]
    need(len(window)==65 and window[0]==[2,475,659,515,0,7,0] and
         window[-1]==[3,475,659,515,0,0,0], 'actual complete COPY515 read window')
    targets=tuple(event[1] for event in window[1:-1])
    need(len(targets)==len(set(targets))==63 and all(
         event==[1,role,659,1,0,0] and role not in (475,659)
         for role,event in zip(targets,window[1:-1])), 'all actual private-result consumers')
    arena, indices = Arena(3), Arena(13)
    modulus, size, depth = arena.input(3), indices.input(2048), indices.input(0)
    program = Program.fixture(indices,arena,2048,2,(),catalogue.codes.bits)
    source, old_directory = Tape(), Tape()
    initial = bytes((i*7 ^ i//3)&1 for i in range(46))
    for bit in initial:source.append(bit)
    source.rewind()
    borrowed = snapshot(arena), snapshot(indices)
    saved_program = body(program.tape)
    counts = [Count.literal(v) for v in (2,11,2,5,3)]
    code = Code(tuple(('checkpoint','controlled',i) for i in range(6)),660)
    machine = Machine(binding,topology,(code,),Arena(3,131072),Arena(13,1024))
    evidence = {'ancestor_request':ancestor_id,'copy_request':copy_id,
                'ancestor_record':ancestor_record.record(),'copy_record':copy_record.record(),
                'catalogue':catalogue.receipt(),'forward_adapter_commands':[6722,4936],
                'both_sweeps_ADD_passes_per_f':[13444,9872],'controlled_payload_bits':46, 'controlled_fibre_bits':23, 'residue_bank_capacity':131072, 'index_bank_capacity':1024,
                'scope':'Actual source-bound nested physical protocol; controlled child outputs, not complete GL64 residual execution'}

    def setup_stock():
        machine.commit(machine.tape('rows'),'unused')
        machine.save_count(Count.product(machine.count('unused'),machine.count('before')),'leading')

    def state():
        return (snapshot(machine.arena),snapshot(machine.indices),
                {label:body(tape) for label,tape in machine.roles.items()})

    def check_state(saved,changed=None):
        restored(machine.arena,saved[0]);restored(machine.indices,saved[1])
        audit(machine.arena,[machine.arena.words[i] for i in machine.arena.live])
        audit(machine.indices,[machine.indices.words[i] for i in machine.indices.live])
        for label,tape in machine.roles.items():
            need(body(tape)==(changed if label=='current' and changed is not None else saved[2][label]),
                 'exact parked numerical/stream parent restoration')
        machine.boundary()

    def descriptor(level,expected,parent,child):
        index = machine.indices.literal(level)
        metadata,a,b = machine.program.step(index)
        need(metadata == (0,expected.code,expected.plan.rank,0,0,0) and
             (inspect_count(a),inspect_count(b)) == (parent,child),'actual appended source/rank/extent')
        machine.indices.free_many(index,a,b)
        return list(metadata)

    with machine.pool.install():
        machine.load_root(source,old_directory,program.tape,modulus,size,depth,*counts)
        setup_stock()
        with no_decode():machine.residual_begin('source',ancestor)
        machine.close_geometry();machine.boundary()
        root_state = state()
        with no_decode():need(machine.block(ancestor,('good',1,0)),'actual rank26 physical gate')
        machine.boundary()
        need((inspect_count(machine.size),inspect_count(machine.depth)) == (832,1),'actual ancestor grants')
        first_descriptor = descriptor(1,ancestor,2048,832)
        root_gap = 5*3**2432
        need(tuple(inspect_count(machine.count(k)) for k in ('old_count','rows','before','gap','suffix'))
             == (2,11,2,root_gap,3),'whole ancestor projected capsule with separate unused stock')
        setup_stock()
        machine.save_count(Count.literal(23),'fibre')
        target_initial={role:bytes(((i*11+role*3)^(i//5))&1 for i in range(46)) for role in targets}
        for role,bits in target_initial.items():
            for bit in bits:machine.tape(('stage',role)).append(bit)
            machine.tape(('stage',role)).rewind()
        machine.commit(machine.tape('source'),('stage',475))
        with no_decode():
            machine.dispatch(('copy',('stage',475),'copy_source'))
            machine.residual_begin('copy_source',copy)
        machine.close_geometry();machine.boundary()
        machine.pc = 3
        saved = state()
        saved_child_program = body(machine.tape('program'))
        coordinates = (0,90)
        coefficients = []
        field_count = machine.indices.literal(2)
        prefix = read_prefix(machine.tape('directory'),field_count)
        machine.tape('directory').rewind()
        try:
            for coordinate in coordinates:
                index = machine.indices.literal(coordinate)
                with no_decode():
                    value = binding.coefficient(machine,copy,prefix,Request('child',index,child_kind='good'))
                coefficients.append(inspect_count(value))
                need(coefficients[-1] == 2,'actual ancestor supplies root unit to COPY child')
                machine.arena.free(value);machine.indices.free(index)
        finally:
            prefix.clear();machine.indices.free(field_count)
        check_state(saved)
        semantic_rejections=[]
        # Serialize the obsolete actual rank34 using the current rank26 source
        # code: this must reject before any coefficient evaluation or CALL.
        bad_program=Program.fixture(machine.indices,machine.arena,2048,2,
                                    ((0,ancestor.code,34,0,0,0),),catalogue.codes.bits)
        fields=Fields.fixture(machine.indices,machine.arena,
                              [(d.code,[[0]*64 for _ in range(64)]) for d in definitions],catalogue.codes.bits)
        for label,test_program,test_fields in [('obsolete_rank34',bad_program,fields)]:
            try:
                with no_decode():Callback(machine.context.ring,machine.indices,test_program,test_fields,
                                          specifications,copy.code,allow_fallback=True)
            except ValueError as error:
                need(str(error)=='actual selected rank','obsolete ancestor rejects at source rank')
                semantic_rejections.append(label)
            else:raise ValueError('obsolete ancestor rank accepted')
        bad_program.tape.clear();fields.tape.clear()
        next_template=catalogue.template_for(copy_id+1,True)
        other_low=tuple(map(tuple,oracle.inverse(oracle.reduce_rational(next_template.preparation,3),3)))
        other=binding.residual(copy_id+1,True,other_low,0)
        fields=Fields.fixture(machine.indices,machine.arena,
                              [(d.code,[[0]*64 for _ in range(64)]) for d in (ancestor,other)],catalogue.codes.bits)
        try:
            with no_decode():Callback(machine.context.ring,machine.indices,machine.program,fields,
                                      specifications,copy.code,allow_fallback=True)
        except ValueError as error:
            need(str(error)=='original global raw-field code','foreign current source prefix rejects')
            semantic_rejections.append('foreign_COPY_prefix')
        else:raise ValueError('foreign current prefix accepted')
        fields.tape.clear()
        check_state(saved)
        rejected=[]
        original_events=macro_machine.block_events
        for label,changes in [('wrong_parent',{'parent_identity':None}),
                              ('foreign_program',{'parent_identity':view(Program,machine,machine.program.tape)}),
                              ('wrong_source',{'source_code':copy.code+1})]:
            def malformed(page,block):
                events=original_events(page,block)
                try:
                    for event in events:yield replace(event,**changes) if event.kind=='enter' else event
                finally:events.close()
            try:
                with no_decode(),patch.object(macro_machine,'block_events',malformed):
                    machine.block(copy,('good',1,0))
            except ValueError as error:
                need(str(error)=='recursive gate belongs to the current program and source','typed source rejection')
                rejected.append(label)
            else:raise ValueError('malformed gate accepted')
            finally:machine.close_geometry()
            check_state(saved)
            need(all(not body(t) for t in machine.handoff.values()),'reject before child handoff mutation')
        with no_decode():need(machine.block(copy,('good',1,0)),'actual rank7 physical gate')
        machine.boundary()
        need((inspect_count(machine.size),inspect_count(machine.depth))==(91,2),'nonterminal rank7 child')
        descriptors=[descriptor(1,ancestor,2048,832),descriptor(2,copy,832,91)]
        need(descriptors[0]==first_descriptor,'unchanged actual ancestor descriptor')
        need(tuple(inspect_count(machine.count(k)) for k in ('old_count','rows','before','gap','suffix'))
             == (2,11,2,5*3**3914,3),'complete two-level capsule, no U/B confusion')
        changed = bytes(1-bit for bit in reversed(initial))
        for bit in changed:machine.output.append(bit)
        machine.output.rewind()
        with no_decode():need(not machine.complete_return(),'return to actual ancestor child')
        need(machine.pc==4 and not machine.root and body(machine.tape('program'))==saved_child_program,
             'serialized continuation and program return')
        check_state(saved,changed)
        with no_decode():
            machine.dispatch(('residual_end','copy_source',copy))
            machine.dispatch(('move','copy_source',('stage',659)))
        need(body(machine.tape(('stage',475)))==initial and body(machine.tape(('stage',659)))==changed,
             'physical COPY borrowed source and distinct owned output')
        for role,event in zip(targets,window[1:-1]):
            with no_decode():machine.dispatch(('xor',('stage',role),('stage',659)))
            need(body(machine.tape(('stage',role)))==bytes(a^b for a,b in zip(target_initial[role],changed)),
                 'actual physical XOR consumes the distinct returned private output')
            need(body(machine.tape(('stage',475)))==initial and body(machine.tape(('stage',659)))==changed,
                 'COPY source and private output immutable throughout all63 readers')
            machine.boundary()
        with no_decode():machine.dispatch(('clear',('stage',659)))
        need(not body(machine.tape(('stage',659))) and not body(machine.tape('copy_source')),
             'paid private-output disposal')
        # Controlled result of the enclosing rank26 callee, not a residual oracle.
        ancestor_output = bytes(bit^1 for bit in initial)
        for bit in ancestor_output:machine.output.append(bit)
        machine.output.rewind()
        with no_decode():need(not machine.complete_return(),'return to original physical parent')
        need(machine.root and machine.pc==1,'resume original successor once')
        check_state(root_state,ancestor_output)
        need(not body(machine.output) and all(not body(tape) for tape in machine.handoff.values()),
             'all protected output and handoff ports consumed after both returns')
        need(machine.numerical.machine.tapes == [{}, {0:'^'}] and
             machine.numerical.machine.heads == [0,1],
             'complete physical parking stack and packet port restored to baseline')
        machine.close_frame();machine.erase_work()
        need(machine.numerical.machine.tapes == [{}, {}],
             'erase the final owned parking marker, not just parent live contents')
    need(body(source)==initial and body(program.tape)==saved_program and not body(old_directory)
         and source.head==program.tape.head==old_directory.head==1,'borrowed source/program/heads restored')
    restored(arena,borrowed[0]);restored(indices,borrowed[1])
    evidence.update(status='PASS_ACTUAL_OQ4_NESTED_PHYSICAL_PROTOCOL',widths=[2048,832,91],
                    descriptors=descriptors,coefficients=coefficients,rejected_gates=rejected,
                    semantic_rejections=semantic_rejections,
                    counts=machine.counts,parking_charge=machine.numerical.machine.counts,
                    peak_scratch_leases=machine.pool.peak,
                    complete_GL64_payload_executed=False,stock_is_controlled_fixture=True,
                    numerical_decode_disabled=True, private_result_consumers=63, literal_COPY_window_events=65,
                    literal_COPY_window_sha256=hashlib.sha256(json.dumps(window,separators=(',',':')).encode()).hexdigest())
    program.tape.clear();source.clear();old_directory.clear()
    for value in counts:value.close()
    arena.free(modulus);indices.free_many(size,depth)
    need(not arena.live and not indices.live,'closed borrowed fixture')
    return evidence


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
