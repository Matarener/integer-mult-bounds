"""Literal original-owner affine replay with two retained execution engines.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Source finite-control, counter and dense-interpreter authors retain credit.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def authenticate():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],'source hash: '+row['path'])


def module(name,path):
    out = types.ModuleType(name); out.__file__ = str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),out.__dict__)
    return out


def load():
    authenticate(); modules = {}
    try:
        for name in ['machine','counters','shear']:
            need(name not in sys.modules,'no preloaded retained macro')
            modules[name] = module(name,P/'inputs'/f'{name}.py')
            sys.modules[name] = modules[name]
    finally:
        for name in modules:
            sys.modules.pop(name,None)
    original = (P/'inputs/source-kernel.py').read_text()
    for before,after in json.loads((P/'DELTA.json').read_text()):
        need(original.count(before) == 1,'exact declared source edit')
        original = original.replace(before,after)
    need(original == (P/'kernel.py').read_text(),'only declared owner-interface edits')
    return modules,module('old_affine',P/'inputs/source-kernel.py'),module('new_affine',P/'kernel.py'),module('dense_affine',P/'inputs/independent.py')


def export(program):
    return json.loads(json.dumps(dict(tapes=program.tapes,entry=program.entry,instructions=program.instructions)))


def observe(tapes,visits=None):
    if visits is None:
        return [dict(cells=t.snapshot(),head=t.head,span=t.high-t.low+1) for t in tapes]
    return [dict(cells=dict(t.cells),head=t.head,span=max(v or {t.head})-min(v or {t.head})+1) for t,v in zip(tapes,visits)]


def execute(modules,dense,program,bank,volume,engine):
    if engine == 'dense':
        tapes,steps = dense.execute(export(program),bank,1024*volume+1)
        return observe(tapes),steps
    m = modules['machine']
    run = m.Machine(program,[m.Tape(cells,head) for cells,head in bank]).run(1024*volume+1)
    return observe(run.tapes,run.visits),run.steps


def check(state,steps,bank,expected,dense,half=False):
    bits = [dense.ONE if b else dense.ZERO for b in expected]
    cells,head = dense.marked(bits,bank[0][1]-1)
    need(state[0]['cells'] == cells and state[0]['head'] == head,'same original owner and head')
    private = set(dense.WORK) | ({14} if half else set())
    for t,row in enumerate(state):
        if t in private:
            need(not row['cells'] and row['head'] == bank[t][1],'all private cells and heads return')
        elif t != 0:
            need(row['cells'] == bank[t][0] and row['head'] == bank[t][1],'descriptor and arbitrary spare preservation')
    span = sum(r['span'] for r in state)
    need(steps <= 1024*len(expected) and span <= 64*len(expected),'complete physical tariff')
    return span


def fixtures():
    for q in range(1,7):
        for c in range(q):
            for offset in range(q):
                yield (1,q,1,1),c,offset,[((j*j+3*j+c+offset)^(j>>1))&1 for j in range(q*q)]
    for c in range(3):
        for offset in range(3):
            for axis in range(9):
                yield (1,3,1,1),c,offset,[int(j == axis) for j in range(9)]
    for bits in range(16):
        for c,offset in [(0,0),(0,1),(1,0),(1,1)]:
            yield (1,2,1,1),c,offset,[(bits>>j)&1 for j in range(4)]
    for shape in [(2,5,2,2),(2,6,3,2),(3,7,2,2),(2,9,2,3)]:
        p,q,g,s = shape
        for c,offset in [(0,q-1),(q-1,q-1),(2,3%q)]:
            yield shape,c,offset,[(j*13+j//3+c+offset)&1 for j in range(p*q*q*g*s)]


def reject(label,fn):
    try:
        fn()
    except (ValueError,RuntimeError):
        return label
    raise ValueError('accepted control: '+label)


def run(write=False):
    modules,old,new,dense = load(); tables = {}; programs = {}
    for half in [False,True]:
        name = 'half_program' if half else 'build_program'
        for inv in [False,True]:
            baseline = getattr(old,name)(modules,inv)
            compatible = getattr(new,name)(modules,inv)
            need(canonical(export(compatible)) == canonical(export(baseline)),'default table unchanged byte-for-byte')
            program = getattr(new,name)(modules,inv,inplace=True)
            key = f'{name}:{inv}'; programs[key] = program; tables[key] = export(program)
            dense.validate(tables[key])
            need(not any(r[0] in ('branch','move','write') and r[1] == 1 for r in program.instructions),'spare tape is never accessed')
    if write:
        (P/'TABLE.json.gz').write_bytes(gzip.compress(canonical(tables)+b'\n',mtime=0))
    else:
        need(canonical(tables) == canonical(json.loads(gzip.decompress((P/'TABLE.json.gz').read_bytes()))),'complete fixed tables')
    counts = dict(generic_calls=0,half_calls=0,roundtrips=0,payload_bits=0)
    digest = sha256(); maximum_steps = maximum_span = 0
    for case_id,(shape,c,offset,payload) in enumerate(fixtures()):
        for inv in [False,True]:
            bank = dense.fixtures(shape,c,offset,payload,translated=True)
            old_bank = deepcopy(bank)
            spare_origin = bank[1][1]
            bank[1] = ({spare_origin-7:dense.ONE,spare_origin:dense.MARK,spare_origin+9:dense.LEFT},spare_origin)
            baseline,baseline_steps = execute(modules,dense,old.build_program(modules,inv),old_bank,len(payload),'sparse')
            expected = dense.oracle(shape,c,offset,payload,inv)
            program = programs[f'build_program:{inv}']
            first = None
            for engine in ['sparse','dense']:
                state,steps = execute(modules,dense,program,bank,len(payload),engine)
                span = check(state,steps,bank,expected,dense)
                need(steps == baseline_steps-3,'exact three-transition reduction')
                need(span == sum(r['span'] for r in baseline)-len(payload)-1,'one complete output span removed')
                observation = (state,steps)
                if first is not None:
                    need(observation == first,'disjoint interpreter cells heads spans and steps')
                first = observation
            if case_id % 13 == 0:
                current = [(r['cells'],r['head']) for r in state]
                back,back_steps = execute(modules,dense,programs[f'build_program:{not inv}'],current,len(payload),'dense')
                check(back,back_steps,current,payload,dense)
                need(all(r['cells'] == b[0] and r['head'] == b[1] for r,b in zip(back,bank)),'entire physical inverse roundtrip')
                counts['roundtrips'] += 1
            counts['generic_calls'] += 1;counts['payload_bits'] += len(payload)
            maximum_steps=max(maximum_steps,steps);maximum_span=max(maximum_span,span)
            digest.update(canonical([shape,c,offset,inv,steps,span,expected]))
    for q in [3,5,7,9,17]:
        shape=(2,q,2,2);payload=[(j*j+j//5+q)&1 for j in range(8*q*q)]
        for inv in [False,True]:
            bank=dense.fixtures(shape,(q+1)//2,0,payload,True);bank[14]=({},bank[14][1]-1)
            old_bank=deepcopy(bank);origin=bank[1][1];bank[1]=({origin:dense.MARK,origin-4:dense.ONE},origin)
            baseline,old_steps=execute(modules,dense,old.half_program(modules,inv),old_bank,len(payload),'sparse')
            expected=dense.oracle(shape,(q+1)//2,0,payload,inv);observations=[]
            for engine in ['sparse','dense']:
                state,steps=execute(modules,dense,programs[f'half_program:{inv}'],bank,len(payload),engine)
                span=check(state,steps,bank,expected,dense,half=True)
                need(steps==old_steps-3 and span==sum(r['span'] for r in baseline)-len(payload)-1,'linked half exact resource delta')
                observations.append((state,steps))
            need(observations[0]==observations[1],'complete linked half interpreter agreement')
            current=[(r['cells'],r['head']) for r in state]
            back,back_steps=execute(modules,dense,programs[f'half_program:{not inv}'],current,len(payload),'dense')
            check(back,back_steps,current,payload,dense,half=True)
            need(all(r['cells']==b[0] and r['head']==b[1] for r,b in zip(back,bank)),'linked half whole-bank inverse roundtrip')
            counts['roundtrips']+=1
            counts['half_calls']+=1;counts['payload_bits']+=len(payload)
            maximum_steps=max(maximum_steps,steps);maximum_span=max(maximum_span,span)
            digest.update(canonical([q,inv,steps,span,expected]))
    controls=[];shape=(2,5,2,2);payload=[int(j==40) for j in range(200)];bank=dense.fixtures(shape,3,2,payload,True)
    program=programs['build_program:False'];good,steps=execute(modules,dense,program,bank,len(payload),'dense');expected=dense.oracle(shape,3,2,payload)
    wrong_owner=deepcopy(good);wrong_owner[1],wrong_owner[0]=wrong_owner[0],wrong_owner[1]
    controls.append(reject('replace the physical owner',lambda:check(wrong_owner,steps,bank,expected,dense)))
    retained=deepcopy(good);retained[2]['cells'][bank[2][1]]=dense.ONE
    controls.append(reject('retain a private bucket bit',lambda:check(retained,steps,bank,expected,dense)))
    wrong_head=deepcopy(good);wrong_head[0]['head']+=1
    controls.append(reject('omit owner head return',lambda:check(wrong_head,steps,bank,expected,dense)))
    wrong_direction,_=execute(modules,dense,programs['build_program:True'],bank,len(payload),'dense')
    controls.append(reject('wrong orientation',lambda:check(wrong_direction,steps,bank,expected,dense)))
    bad=deepcopy(tables['build_program:False']);bad['instructions'][next(k for k,r in enumerate(bad['instructions']) if r[0]=='move')][2]=2
    controls.append(reject('nonlocal motion',lambda:dense.validate(bad)))
    for tape,value in [(5,0),(14,6),(16,6)]:
        bad_bank=deepcopy(bank);bad_bank[tape]=dense.binary(value,bank[tape][1]-1)
        controls.append(reject('invalid descriptor '+str(tape),lambda b=bad_bank:dense.execute(tables['build_program:False'],b,1024*len(payload)+1)))
    # Delete the added owner rewind from a separately compiled code mutant.
    code=(P/'kernel.py').read_text();segment="    if inplace:\n        c.emit_rewind(a, b.SOURCE, 'original_owner_before_emit')\n"
    need(code.count(segment)==1,'specific owner-rewind mutant')
    mutant=types.ModuleType('missing_owner_rewind');exec(compile(code.replace(segment,''),'<owner-rewind-control>','exec'),mutant.__dict__)
    bad_program=mutant.build_program(modules,inplace=True)
    def missing_rewind():
        state,count=execute(modules,dense,bad_program,bank,len(payload),'dense');check(state,count,bank,expected,dense)
    controls.append(reject('regenerated table without owner rewind',missing_rewind))
    # Extra local work has the same endpoint but changes the exact charge.
    bad=deepcopy(tables['build_program:False']);halt=next(k for k,r in enumerate(bad['instructions']) if r[0]=='halt')
    bad['instructions'][halt]=['goto',len(bad['instructions'])];bad['instructions'] += [['move',0,1],['move',0,-1],['halt']]
    tapes,changed_steps=dense.execute(bad,bank,1024*len(payload)+1);changed=observe(tapes)
    need(all((a['cells'],a['head'])==(b['cells'],b['head']) for a,b in zip(changed,good)),'cost mutant preserves every endpoint')
    controls.append(reject('endpoint-preserving uncharged work',lambda:need(changed_steps==steps,'exact charge changes')))
    return dict(source='fixed-tape-affine-shear at de5ec2e7a6074068452f45b1a191b5c72832df4a',counts=counts,
        tables={k:dict(instructions=len(v['instructions']),sha256=sha256(canonical(v)).hexdigest()) for k,v in tables.items()},
        tapes=19,alphabet_symbols=7,transitions_bound_per_bit=1024,visited_cells_bound_per_bit=64,
        exact_transition_delta=-3,exact_visited_span_delta='-(V+1)',maximum_fixture_steps=maximum_steps,
        maximum_fixture_span=maximum_span,transcript_sha256=digest.hexdigest(),rejected_controls=controls,
        limits=['Later-target complete-stream interface only.','General coefficient producers, earlier-target routing, ROW/cache and full supplier admission remain open.'])


if __name__=='__main__':
    write=sys.argv[1:]==['--write'];need(write or not sys.argv[1:],'supported arguments')
    result=run(write)
    if write:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(canonical(result)==canonical(json.loads((P/'RESULT.json').read_text())),'complete typed receipt')
    print('PASS_INPLACE_RUNTIME_AFFINE')
    print(json.dumps(result['counts'],sort_keys=True))
