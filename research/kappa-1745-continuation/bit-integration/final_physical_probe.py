"""Actual T35 final early-birth-prefix R437 records through fixed-role CALL/RETURN.

The 46-bit controlled payload is deliberately not a complete GL64 packet.
No claim that the controlled return executes a residual permutation.
Adapted from PR3967's physical_probe.py, itself derived from Jose Manuel's
macro_selected_checks and zxv/PR3690. Native replica keys and actual rank42
owners replace the retained OQ4 rank26 catalogue. All physical guards remain.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from dataclasses import replace
import gzip
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
ROOT = HERE.parents[2]
ADAPTER = SCOPE.parent / 'kappa-next-regime/native-catalogue/adapter.py'
WORD = SCOPE / 'bit-word/early-birth-prefixes/WORD.json.gz'
TEMPLATE = HERE / 'early-birth-prefixes/GLOBAL-TEMPLATE.json.gz'
ORIGINAL = SCOPE.parent / 'kappa-next-regime/sources/PR3967/research/r437-oq4-caller-binding/physical_probe.py'
WORD_SHA = 'f84bdf9b2d4e8758584e3a4759519acc2307e3723fb23568bb7ed4fde617a908'
TEMPLATE_SHA = '3106ca655ac51aea273f6af98b1bbe045cbe553242b393cdc320996681b8d1cd'
ORIGINAL_SHA = '4fb0958485d7bd3d77435d882c91f4a9462ac877b0bd99cbd55d0db505a35460'
CATALOGUE_SHA = '88c84088263813185899a6392b04d801a1e1e649309090320086add782bd73a2'
sys.path.insert(0, str(ADAPTER.parent))
import adapter


def body(tape):
    from words import BLANK
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def run():
    adapter.need(hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == ORIGINAL_SHA,
                 'exact credited physical probe source')
    adapter.need(hashlib.sha256(gzip.decompress(TEMPLATE.read_bytes())).hexdigest() == TEMPLATE_SHA,
                 'exact current T35 owner template content')
    catalogue, topology = adapter.load(template_path=TEMPLATE, word_path=WORD,
                                       word_content_sha256=WORD_SHA)
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
                       if r.kind == 'IDLE' and r.base.rank == 42 and
                       r.stage == 6 and r.replica == 1 and r.role == 209)
    copy_id = catalogue.identifier('COPY', 0, 21600, 1)
    ancestor_record, copy_record = (catalogue.requests[i] for i in (ancestor_id,copy_id))
    need(ancestor_record.role == 209 and ancestor_record.family == 1097 and
         ancestor_record.stage == 6 and ancestor_record.replica == 1 and
         ancestor_id in topology.idles_for(6, 1),
         'actual current T35 rank42 idle with explicit replica and owner')
    need(copy_id == 4514 and copy_record.role == 475 and copy_record.old_frame == 515 and
         copy_record.replica == 1 and copy_record.family == 31080,
         'actual COPY515 catalogue site and common-field owner')
    receipt = catalogue.receipt()
    need(receipt['binding_sha256'] == CATALOGUE_SHA and receipt['canonical_requests'] == 987525,
         'complete current T35 word catalogue binding')
    definitions = []
    for identifier,common in ((ancestor_id,False),(copy_id,True)):
        template = catalogue.template_for(identifier,common)
        low = tuple(map(tuple,oracle.inverse(oracle.reduce_rational(template.preparation,3),3)))
        definition = binding.residual(identifier,common,low,0)
        need(definition.plan.good, 'actual good native/common source class')
        definitions.append(definition)
    ancestor, copy = definitions
    need([len(d.plan.commands) for d in definitions]==[7666,4936],
         "actual rank42/rank7 full forward adapter invoices")
    window = catalogue.template['local_programs']['forward'][21600:21665]
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
                'catalogue':receipt,'forward_adapter_commands':[7666,4936],
                'both_sweeps_ADD_passes_per_f':[15332,9872],'controlled_payload_bits':46, 'controlled_fibre_bits':23, 'residue_bank_capacity':131072, 'index_bank_capacity':1024,
                'word_content_sha256':WORD_SHA,'template_content_sha256':TEMPLATE_SHA,
                'source_sha256':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in (Path(__file__).resolve(),ADAPTER,WORD,TEMPLATE,ORIGINAL)},
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
        with no_decode():need(machine.block(ancestor,('good',1,0)),'actual rank42 physical gate')
        machine.boundary()
        need((inspect_count(machine.size),inspect_count(machine.depth)) == (1344,1),'actual ancestor grants')
        first_descriptor = descriptor(1,ancestor,2048,1344)
        root_gap = 5*3**1408
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
        coordinates = (0,146)
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
        # Serialize obsolete rank26 and rank34 with the current rank42 source
        # code: each rejects before coefficient evaluation or CALL.
        fields=Fields.fixture(machine.indices,machine.arena,
                              [(d.code,[[0]*64 for _ in range(64)]) for d in definitions],catalogue.codes.bits)
        for obsolete_rank in (26,34):
            bad_program=Program.fixture(machine.indices,machine.arena,2048,2,
                                        ((0,ancestor.code,obsolete_rank,0,0,0),),catalogue.codes.bits)
            try:
                with no_decode():Callback(machine.context.ring,machine.indices,bad_program,fields,
                                          specifications,copy.code,allow_fallback=True)
            except ValueError as error:
                need(str(error)=='actual selected rank','obsolete ancestor rejects at source rank')
                semantic_rejections.append('obsolete_rank'+str(obsolete_rank))
            else:raise ValueError('obsolete ancestor rank accepted')
            finally:bad_program.tape.clear()
        fields.tape.clear()
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
        # An otherwise identical COPY in replica2 has its own global raw code.
        # Supplying that field must not satisfy the actual replica1 source.
        foreign_replica_id=catalogue.identifier('COPY',0,21600,2)
        need(foreign_replica_id == 7427 and catalogue.requests[foreign_replica_id].replica == 2,
             'actual distinct replica COPY source')
        replica_template=catalogue.template_for(foreign_replica_id,True)
        replica_low=tuple(map(tuple,oracle.inverse(oracle.reduce_rational(replica_template.preparation,3),3)))
        replica_other=binding.residual(foreign_replica_id,True,replica_low,0)
        fields=Fields.fixture(machine.indices,machine.arena,
                              [(d.code,[[0]*64 for _ in range(64)]) for d in (ancestor,replica_other)],catalogue.codes.bits)
        try:
            with no_decode():Callback(machine.context.ring,machine.indices,machine.program,fields,
                                      specifications,copy.code,allow_fallback=True)
        except ValueError as error:
            need(str(error)=='original global raw-field code','foreign replica prefix rejects')
            semantic_rejections.append('foreign_replica_COPY_prefix')
        else:raise ValueError('foreign replica prefix accepted')
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
        need((inspect_count(machine.size),inspect_count(machine.depth))==(147,2),'nonterminal rank7 child')
        descriptors=[descriptor(1,ancestor,2048,1344),descriptor(2,copy,1344,147)]
        need(descriptors[0]==first_descriptor,'unchanged actual ancestor descriptor')
        need(tuple(inspect_count(machine.count(k)) for k in ('old_count','rows','before','gap','suffix'))
             == (2,11,2,5*3**3802,3),'complete two-level capsule, no U/B confusion')
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
        # Controlled result of the enclosing rank42 callee, not a residual oracle.
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
    evidence.update(status='PASS_ACTUAL_T35_FINAL_EARLY_BIRTH_NESTED_PHYSICAL_PROTOCOL',widths=[2048,1344,147],
                    descriptors=descriptors,coefficients=coefficients,rejected_gates=rejected,
                    semantic_rejections=semantic_rejections,
                    coefficient_coordinates=list(coordinates),gap_exponents=[1408,3802],
                    ancestor_replica=1,copy_replica=1,foreign_copy_replica=2,
                    literal_COPY_window_positions=[21600,21665],
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
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'PHYSICAL-PROBE.json',
                        help='fresh JSON receipt path; default: alongside this script')
    arguments=parser.parse_args()
    result=run()
    arguments.output.parent.mkdir(parents=True,exist_ok=True)
    arguments.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','widths','coefficients','rejected_gates',
          'semantic_rejections','complete_GL64_payload_executed','controlled_payload_bits')},sort_keys=True))
