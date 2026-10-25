#!/usr/bin/env python3
"""Meter the frozen directory producer, including all Count/Counter tape work.

Apache-2.0. ToikY with substantial OpenAI Codex assistance. The six canonical
source files implement the object under review; no source bytes are changed.
Setup supplies an already valid Context. No full source/specification/stock
admission or physical finite-state tariff is inferred from this component.
"""
from __future__ import annotations
from contextlib import contextmanager
import hashlib
import itertools
import json
from pathlib import Path
import sys
import types

HERE=Path(__file__).resolve().parent
PINS={
 'CALLER.py':('7bc6e42072a09a08ac961e05c3da01cde012d740d4b4c605f298d994f2ad7c5a','5a032e8923f7f8b22bb98f3e39b804beb9906c16'),
 'NOTICE.md':('c446b32b8a621844fb2fbe654810c8122035bdd43fed2132f1137d98cb6f9943','ef9f81510db86eaf2f0a7191d85e92a6db30ddc0'),
 'cardinality.py':('505d5e560c5a507e6184edcc19a87cf1fed243eb34a5cb21fbe1e4fe017e7f22','b8ba857e32c5903408e1e61ff916300848b4a208'),
 'counts.py':('00b476dbda0e8cc99886bf794439e1cb9e775f435f599a3557e99321fe084069','81b48940ce222290a40d4fb349ce827f4788469d'),
 'directory.py':('4270e370b2bfe38ef73aadcd97d1b3496b56bd582115d74331eb9e5ceb90bec7','c74cacf5ce809c0561d374f137a52df0992b4226'),
 'records.py':('0c9c4b23e998597fb877bb1a29da69ac869b68262abe635b162b4dba9c69b372','4f00467a0ff580954ad2fd0c7380240c753ddef3'),
 'stream.py':('c7dc7da5b00f27016982ada4c0416f8328568b00df16d97012f33d4b372d79b5','5e5a4bb0f98971447043e25d4dd6991bfc070389'),
 'words.py':('5c37f57708ba3131bdcb03139f9dbc29886bee44569c09cbba51b68f75acd7f9','8d4ba37e2778acb35b34e0719df2caf138fbeb50'),
}
CASES=(
 {'name':'small_h0','d':1,'q':3,'w':2,'B':3,'h':0,'Q':4,'I':3},
 {'name':'small_h1','d':2,'q':3,'w':2,'B':2,'h':1,'Q':4,'I':3},
 {'name':'small_h2','d':2,'q':3,'w':2,'B':1,'h':2,'Q':5,'I':4},
 {'name':'binary_long_carry','d':1,'q':2,'w':4,'B':3,'h':0,'Q':3,'I':3},
 {'name':'binary_nine_digits','d':3,'q':2,'w':2,'B':1,'h':1,'Q':3,'I':3},
 {'name':'radix5_history2','d':1,'q':5,'w':2,'B':2,'h':2,'Q':4,'I':4},
 {'name':'dimension64_cap1','d':64,'q':3,'w':1,'B':1,'h':1,'Q':6507,'I':4},
)


def need(condition,message):
    if not condition:raise ValueError(message)


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))

def digest(raw):return hashlib.sha256(raw).hexdigest()

def no_duplicate_keys(pairs):
    result={}
    for key,value in pairs:
        need(key not in result,'duplicate receipt key: '+key)
        result[key]=value
    return result

def load_receipt(path=None):
    return json.loads((HERE/'RESULT.json' if path is None else Path(path)).read_text(),object_pairs_hook=no_duplicate_keys)


def authenticate():
    for name,(sha,blob) in PINS.items():
        path=HERE/'source'/name
        need(not path.is_symlink(),'source symlink: '+name)
        raw=path.read_bytes()
        need(digest(raw)==sha,'source bytes: '+name)
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,
             'source Git blob: '+name)


@contextmanager
def sources():
    authenticate()
    names=('words','records','stream','cardinality','counts','directory')
    saved={name:sys.modules.get(name) for name in names}
    modules={}
    try:
        for name in names:
            module=types.ModuleType(name);module.__file__=str(HERE/'source'/(name+'.py'))
            sys.modules[name]=module
            exec(compile((HERE/'source'/(name+'.py')).read_bytes(),module.__file__,'exec'),module.__dict__)
            modules[name]=module
        yield types.SimpleNamespace(**modules)
    finally:
        for name,value in saved.items():
            if value is None:sys.modules.pop(name,None)
            else:sys.modules[name]=value


def actions(meter):return {key:getattr(meter,key) for key in ('reads','writes','moves')}

def difference(after,before):return {key:after[key]-before[key] for key in after}

def sum_actions(rows):return {key:sum(row[key] for row in rows) for key in ('reads','writes','moves')}


def field_bytes(code,digits,Q,L):
    return bytes([(code>>i)&1 for i in range(Q)]+[5]+
                 [bit for value in digits for bit in [(value>>i)&1 for i in range(L)]+[5]]+[6])


def decode_count(value):
    raw=bytes(value.tape.cells)
    end=raw.index(3,1)
    return sum(bit<<(i-1) for i,bit in enumerate(raw[1:end],1))


def high_power_shared(value,ring,q,dimension,radix_power):
    first=True
    for _ in radix_power(ring,q):
        if first:
            first=False
        else:
            for _ in range(dimension*dimension):
                value.multiply_small(q)


def run_case(config,candidate=False,alter_old=None,alter_code=None):
    need(isinstance(config,dict),'case schema')
    need(type(candidate) is bool,'candidate mode')
    d,q,w,B,h,Q,I=(config[k] for k in ('d','q','w','B','h','Q','I'))
    need(all(type(x) is int for x in (d,q,w,B,h,Q,I)) and
         d>0 and q>=2 and w>=1 and B>=1 and h>=0 and Q>=2 and I>=max(2,h.bit_length()+1),'case domain')
    M=d*d;modulus=q**w;c=q**(w-1);H=c**M;L=modulus.bit_length()+1
    need(H<=10000,'bounded fixture output enumeration; no full nontrivial GL64 lift')
    F=Q+2+M*(L+1)
    with sources() as S:
        registry=[]
        original_init=S.records.Tape.__init__;original_step=S.records.Tape.step
        def tape_init(tape):
            original_init(tape);tape.audit_max_head=1;registry.append(tape)
        def tape_step(tape,direction):
            original_step(tape,direction);tape.audit_max_head=max(tape.audit_max_head,tape.head)
        S.records.Tape.__init__=tape_init;S.records.Tape.step=tape_step
        arena=S.words.Arena(L,capacity=M+64);indices=S.words.Arena(I,capacity=16)
        ring=S.words.Ring(arena.literal(modulus))
        vocabulary=types.SimpleNamespace(q=q,dimension=d,bits=Q,limit=1<<Q)
        context=S.directory.Context(ring,vocabulary)
        fields=indices.literal(h);old_count=S.counts.Count.literal(B)
        old=S.records.Tape()
        old_prefixes=[]
        for outer in range(B):
            prefix=b''
            for level in range(h):
                code=(outer+level) % vocabulary.limit
                digits=[(outer+level+j)%c for j in range(M)]
                prefix+=field_bytes(code,digits,Q,L)
            old_prefixes.append(prefix)
        old.cells=bytearray([S.words.LEFT])+bytearray(b''.join(old_prefixes));old.head=1
        code=min(3,vocabulary.limit-1)
        if alter_old is not None:alter_old(old,S)
        if alter_code is not None:code=alter_code(code,vocabulary)
        spectator=arena.literal(1);spectator.head=2
        index_spectator=indices.literal(1);index_spectator.head=2
        protected_words=[arena.template,indices.template]+[arena.words[j] for j in arena.live]+[indices.words[j] for j in indices.live]
        protected_word_states=[(word,bytes(word.cells),word.head) for word in protected_words]
        protected_count_state=(bytes(context.highs.tape.cells),context.highs.tape.head)
        input_bytes=bytes(old.cells)
        input_count_bytes=bytes(old_count.tape.cells)
        protected=set(arena.live);protected_index=set(indices.live)
        before_record={id(t):actions(t.meter) for t in registry}
        before_residue=actions(arena.meter);before_index=actions(indices.meter)
        before_count=len(registry);before_slots=len(arena.words)
        arena.meter.peak_live=len(arena.live);indices.meter.peak_live=len(indices.live)
        arena.meter.allocations=0;indices.meter.allocations=0
        increments=[];active={};advances=0;radix_trace=[];multipliers=[]
        original_radix=S.cardinality.radix_power
        original_multiply=S.cardinality.Natural.multiply_small
        def traced_radix(ring,q):
            entry={'yields':0,'complete':False}
            radix_trace.append(entry);start=actions(arena.meter)
            try:
                for value in original_radix(ring,q):
                    entry['yields']+=1
                    yield value
                entry['complete']=True
            finally:
                entry['residue_actions']=difference(actions(arena.meter),start)
        def multiply(value,multiplier):
            multipliers.append((id(value.tape),multiplier))
            return original_multiply(value,multiplier)
        S.cardinality.radix_power=traced_radix
        S.cardinality.Natural.multiply_small=multiply
        original_odometer_init=S.directory.Odometer.__init__
        original_advance=S.directory.Odometer.advance
        original_increment=S.words.Unsigned.increment_in_place
        def odometer_init(odometer,ctx):
            original_odometer_init(odometer,ctx)
            active.clear();active.update({id(word):j for j,word in enumerate(word for row in odometer.digits for word in row)})
            increments.append([0]*M)
        def increment(raw,word):
            need(id(word) in active,'only odometer increments on producer path')
            increments[-1][active[id(word)]]+=1
            return original_increment(raw,word)
        def advance(odometer):
            nonlocal advances
            advances+=1
            return original_advance(odometer)
        S.directory.Odometer.__init__=odometer_init
        S.directory.Odometer.advance=advance
        S.words.Unsigned.increment_in_place=increment
        if candidate:
            S.directory.high_power=lambda value,ring,q,dimension:high_power_shared(value,ring,q,dimension,S.cardinality.radix_power)
        original_inspect=S.words.Word.inspect
        S.words.Word.inspect=lambda self:(_ for _ in ()).throw(ValueError('runtime numerical decoding forbidden'))
        try:
            output,expected=S.directory.produce(old,fields,old_count,code,context)
        finally:
            S.words.Word.inspect=original_inspect
        totals=sum_actions([difference(actions(t.meter),before_record.get(id(t),dict(reads=0,writes=0,moves=0))) for t in registry])
        residue=difference(actions(arena.meter),before_residue)
        index=difference(actions(indices.meter),before_index)
        created=registry[before_count:]
        need(len(created)==5+2*B,'complete source-created record tape inventory')
        need(expected.tape is created[0] and output is created[4],'returned source tape identities')
        need(len(radix_trace)==(1 if candidate else M) and all(row['complete'] and row['yields']==w for row in radix_trace),'complete exact radix traversal trace')
        need(len(multipliers)==M*(w-1) and all(tape==id(expected.tape) and multiplier==q for tape,multiplier in multipliers),'exact ordered expected Count q multipliers')
        need(all(row['residue_actions']==radix_trace[0]['residue_actions'] for row in radix_trace),'uniform complete radix traversal bill')
        roles=['expected','emitted_literal_temporary','emitted','outer','output']+[role for _ in range(B) for role in ('saved_prefix','history_counter')]
        record_rows=[]
        for role,tape in zip(roles,created):
            record_rows.append({'role':role,'actions':difference(actions(tape.meter),before_record.get(id(tape),dict(reads=0,writes=0,moves=0))),
                                'visited_cells':tape.audit_max_head+1,'head':tape.head})
        expected_bytes=b''.join(prefix+field_bytes(code,high,Q,L) for prefix in old_prefixes
                                for high in itertools.product(range(c),repeat=M))
        need(bytes(output.cells)==bytes([S.words.LEFT])+expected_bytes,'exact canonical output order and bytes')
        need(bytes(old.cells)==input_bytes and old.head==1,'borrowed old directory bytes/head preserved')
        need(bytes(old_count.tape.cells)==input_count_bytes and old_count.tape.head==1 and fields.head==1,
             'borrowed count/history words preserved')
        need(output.head==expected.tape.head==1 and decode_count(expected)==B*H,'returned heads and complete count')
        need(arena.live==protected and indices.live==protected_index,'all temporary numerical words returned')
        need(all(bytes(word.cells)==raw and word.head==head for word,raw,head in protected_word_states),'all protected numerical bytes/heads preserved')
        need((bytes(context.highs.tape.cells),context.highs.tape.head)==protected_count_state,'protected context cardinality bytes/head preserved')
        need(all(t.head==1 and (len(t.cells)<=1 or t.cells[1]==S.words.BLANK)
                 for t in created if t is not output and t is not expected.tape),'scratch record tapes cleared')
        need(len(expected_bytes)==B*H*(h+1)*F and advances==B*H,'full output extent and odometer visits')
        need(increments==[[c**(j+1) for j in range(M)] for _ in range(B)],'every odometer digit visit')
        result={'config':dict(config),'candidate_shared_radix':candidate,'geometry':{'M':M,'modulus':modulus,'cap':c,'H':H,'L':L,'F':F,
                                                'old_body':B*h*F,'output_body':len(expected_bytes)},
                'record_tapes':totals,'residue_words':residue,'index_words':index,
                'radix_traversals':len(radix_trace),'radix_yields_each':w,'radix_complete_each':True,
                'single_radix_residue_actions':radix_trace[0]['residue_actions'],
                'ordered_expected_q_multipliers':len(multipliers),
                'created_record_tapes':len(created),'record_roles':record_rows,
                'borrowed_old_actions':difference(actions(old.meter),before_record[id(old)]),
                'borrowed_old_count_actions':difference(actions(old_count.tape.meter),before_record[id(old_count.tape)]),
                'additional_residue_peak':arena.meter.peak_live-len(protected),
                'residue_allocations':arena.meter.allocations,'new_residue_slots':len(arena.words)-before_slots,
                'residue_slots_at_exit':len(arena.words),'protected_residue_words':len(protected),
                'odometer_advances':advances,'odometer_increment_visits':sum(sum(row) for row in increments),
                'input_sha256':digest(input_bytes),'output_sha256':digest(bytes(output.cells)),
                'output_head':output.head,'expected_head':expected.tape.head,'returned_prefix_count':B*H,
                'all_borrowed_bytes_heads_preserved':True,'all_scratch_cleared':True,
                'runtime_word_decoding_used':False,'full_source_stock_admitted':False}
        expected.close();output.clear()
        old.clear();old_count.close();indices.free(fields);indices.free(index_spectator);arena.free(spectator)
        context.close();ring.close();arena.free(ring.modulus)
        need(not arena.live and not indices.live,'fixture teardown inventory')
        return result


def audit():
    pairs=[]
    for config in CASES:
        original=run_case(config)
        candidate=run_case(config,candidate=True)
        need(original['record_tapes']==candidate['record_tapes'] and original['index_words']==candidate['index_words'],'unchanged complete record/index invoice')
        need(original['output_sha256']==candidate['output_sha256'] and original['returned_prefix_count']==candidate['returned_prefix_count'],'exact same produced directory')
        need(original['additional_residue_peak']==candidate['additional_residue_peak'],'same complete producer numerical peak')
        saved=difference(original['residue_words'],candidate['residue_words'])
        radix=original['single_radix_residue_actions']
        need(radix==candidate['single_radix_residue_actions'],'same complete single radix traversal bill')
        need(saved=={key:(config['d']**2-1)*value for key,value in radix.items()},'exact omitted radix traversal savings')
        pairs.append({'config':dict(config),'original':original,'shared_radix':candidate,'saved_residue_actions':saved})
    return {'schema_version':1,'cases':pairs,'scope':'produce with an already valid protected Context; no shared-source adoption or full Pi/stock admission'}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true',help='Authoring only: regenerate RESULT.json; ordinary replay never writes files.');args=parser.parse_args()
    try:
        result=audit()
        if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        else:need(canonical(result)==canonical(load_receipt()),'complete typed receipt')
        print('PASS_DIRECTORY_PRODUCER_COMPONENT cases='+str(len(result['cases']))+' actual_dimension64_cap1 no_full_Pi_no_stock_admission')
    except Exception as error:
        print('FAIL_DIRECTORY_PRODUCER_COMPONENT '+str(error),file=sys.stderr);raise SystemExit(1)
