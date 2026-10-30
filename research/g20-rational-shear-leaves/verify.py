"""Check the complete G20 rational-shear producer/consumer interface."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import types

P=Path(__file__).resolve().parent
ROOT=P.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def authenticate():
    for r in json.loads((P/'SOURCES.json').read_text())['files']:
        if r['usage']=='input':need(sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],'source hash: '+r['path'])


def module(name,path):
    m=types.ModuleType(name);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m


def load():
    authenticate();modules={}
    try:
        for name in ['machine','counters','shear']:
            need(name not in sys.modules,'no preloaded retained macro')
            modules[name]=module(name,P/'inputs'/f'{name}.py');sys.modules[name]=modules[name]
    finally:
        for name in modules:sys.modules.pop(name,None)
    original=(P/'inputs/source-offset.py').read_text()
    for a,b in json.loads((P/'DELTA.json').read_text()):
        need(a in original,'declared bounded extension');original=original.replace(a,b)
    need(original==(P/'offset.py').read_text(),'only declared quarter-domain extension')
    return modules,module('affine',P/'inputs/affine.py'),module('quarter',P/'offset.py'),module('leaves',P/'kernel.py'),module('dense',P/'inputs/independent.py'),module('edge_machine',P/'inputs/controller.py')


def export(program):
    return json.loads(json.dumps(dict(tapes=program.tapes,entry=program.entry,instructions=program.instructions)))


def observe(tapes,visits=None):
    if visits is None:return [dict(cells=t.snapshot(),head=t.head,span=t.high-t.low+1) for t in tapes]
    return [dict(cells=dict(t.cells),head=t.head,span=max(v or {t.head})-min(v or {t.head})+1) for t,v in zip(tapes,visits)]


def execute(modules,dense,program,bank,cap,engine='dense'):
    if engine=='dense':
        t,s=dense.execute(export(program),bank,cap);return observe(t),s
    m=modules['machine'];r=m.Machine(program,[m.Tape(c,h) for c,h in bank]).run(cap)
    return observe(r.tapes,r.visits),r.steps


def descriptor_bank(dense,q):
    bank=[({17*t-13:dense.MARK},17*t-13) for t in range(19)]
    bank[5]=dense.binary(q,53);bank[14]=({},-41)
    return bank


def descriptor_check(state,steps,bank,dense,q,k):
    c=k*pow(4,-1,q)%q
    cells,head=dense.binary(c+1,bank[14][1])
    need(state[14]['cells']==cells and state[14]['head']==head,'exact canonical owned residue descriptor')
    for t,r in enumerate(state):
        if t!=14:need(r['cells']==bank[t][0] and r['head']==bank[t][1],'all descriptor spectators and Q return')
    need(steps<=64*q.bit_length()+128,'complete literal descriptor bound')
    need(state[14]['span']<=q.bit_length()+4,'descriptor temporary span')
    return c


def leaf_check(state,steps,bank,dense,shape,payload,k,inverse):
    q=shape[1];expected=dense.oracle(shape,k*pow(4,-1,q)%q,0,payload,inverse)
    cells,head=dense.marked([dense.ONE if b else dense.ZERO for b in expected],bank[0][1]-1)
    need(state[0]['cells']==cells and state[0]['head']==head,'complete original-owner rational leaf')
    private=set(dense.WORK)|{14,16}
    for t,r in enumerate(state):
        if t in private:need(not r['cells'] and r['head']==bank[t][1],'all coefficient offset and private cells/heads return')
        elif t!=0:need(r['cells']==bank[t][0] and r['head']==bank[t][1],'extent and spare preservation')
    span=sum(r['span'] for r in state)
    need(steps<=1024*len(payload) and span<=64*len(payload),'complete producer consumer physical bill')
    return expected,span


def reject(label,fn):
    try:fn()
    except (ValueError,RuntimeError):return label
    raise ValueError('accepted control: '+label)


def run(write=False):
    modules,affine,quarter,leaf,dense,edge=load();source=json.loads((P/'inputs/route-RESULT.json').read_text())
    coefficients=sorted({F(c) for key in ['old_histogram','new_histogram','scale_free_histogram'] for c in source[key]['ADD']})
    need(len(coefficients)==14 and all((4*c).denominator==1 and abs(4*c)<=16 for c in coefficients),'complete source coefficient class')
    codes=[int(4*c) for c in coefficients];tables={};programs={};preparers={}
    for k in codes:
        preparers[k]=leaf.prepare(modules,quarter,k);tables[f'prepare:{k}']=export(preparers[k])
        for inv in [False,True]:
            key=f'{k}:{inv}';programs[key]=leaf.build(modules,quarter,affine,k,inv);tables[key]=export(programs[key])
            dense.validate(tables[key])
            need(not any(r[0] in ('branch','write','move') and r[1]==1 for r in programs[key].instructions),'spare tape unused')
    if write:(P/'TABLE.json.gz').write_bytes(gzip.compress(canonical(tables)+b'\n',mtime=0))
    else:need(canonical(json.loads(gzip.decompress((P/'TABLE.json.gz').read_bytes())))==canonical(tables),'all compiled tables')
    digest=sha256();descriptor_cases=legacy_cases=leaf_cases=bits=roundtrips=0;peak_steps=0
    qs=[*range(1,128,2),255,257,511,513,1023,1025,2**40-1,2**40+1,2**4096-1,2**4096+1]
    symbol_map={None:dense.BLANK,0:dense.ZERO,1:dense.ONE,2:dense.RIGHT,3:dense.LEFT}
    for k in codes:
        for q in qs:
            bank=descriptor_bank(dense,q);observations=[]
            for engine in ['sparse','dense']:
                state,steps=execute(modules,dense,preparers[k],bank,64*q.bit_length()+129,engine)
                descriptor_check(state,steps,bank,dense,q,k);observations.append((state,steps))
            need(observations[0]==observations[1],'descriptor interpreter agreement')
            if q>1:
                initial={-1:3,**{i:(q>>i)&1 for i in range(q.bit_length())},q.bit_length():2}
                old_tapes=[initial,{}];stats=edge.run_tapes(quarter.compile_offset(k),old_tapes)
                expected={position+bank[14][1]+1:symbol_map[symbol] for position,symbol in old_tapes[1].items() if symbol is not None}
                need(state[14]['cells']==expected,'retained explicit-edge machine agrees with ABI compiler')
                legacy_cases+=1
            digest.update(canonical([k,str(q),steps,state[14]['span'],str(k*pow(4,-1,q)%q)]));descriptor_cases+=1
        for q in [1,3,5,7,9,17]:
            shape=(1,1,1,1) if q==1 else (2,q,2,2);volume=shape[0]*q*q*shape[2]*shape[3]
            fixtures=[[(j*7+j//3+k)&1 for j in range(volume)]]
            if q==3:fixtures += [[int(j==i) for j in range(volume)] for i in [0,8,23,40,71]]
            if q==1:fixtures += [[0]*volume,[1]*volume]
            for payload in fixtures:
                for inv in [False,True]:
                    bank=dense.fixtures(shape,0,0,payload,True)
                    bank[14]=({},bank[14][1]-1);bank[16]=({},bank[16][1]-1)
                    o=bank[1][1];bank[1]=({o-9:dense.ONE,o:dense.MARK,o+5:dense.RIGHT},o)
                    observations=[]
                    for engine in ['sparse','dense']:
                        state,steps=execute(modules,dense,programs[f'{k}:{inv}'],bank,1024*volume+1,engine)
                        expected,span=leaf_check(state,steps,bank,dense,shape,payload,k,inv);observations.append((state,steps))
                    need(observations[0]==observations[1],'full physical leaf interpreter agreement')
                    if q in (1,3,9) and payload is fixtures[0]:
                        current=[(r['cells'],r['head']) for r in state]
                        back,back_steps=execute(modules,dense,programs[f'{k}:{not inv}'],current,1024*volume+1)
                        leaf_check(back,back_steps,current,dense,shape,expected,k,not inv)
                        need(all(r['cells']==b[0] and r['head']==b[1] for r,b in zip(back,bank)),'entire linked inverse return')
                        roundtrips+=1
                    digest.update(canonical([k,q,inv,steps,span,expected]));leaf_cases+=1;bits+=volume;peak_steps=max(peak_steps,steps)
    # Execute the actual Q=5^3 modulus for the two previously unprepared fractions.
    for k in [1,6]:
        q=125;shape=(1,q,1,1);payload=[int(j in [126,501,15624]) for j in range(q*q)]
        bank=dense.fixtures(shape,0,0,payload,True);bank[14]=({},bank[14][1]-1);bank[16]=({},bank[16][1]-1)
        observations=[]
        for engine in ['sparse','dense']:
            state,steps=execute(modules,dense,programs[f'{k}:False'],bank,1024*len(payload)+1,engine)
            expected,span=leaf_check(state,steps,bank,dense,shape,payload,k,False);observations.append((state,steps))
        need(observations[0]==observations[1],'Q125 complete pair fiber')
        digest.update(canonical([k,q,steps,span,expected]));leaf_cases+=1;bits+=len(payload);peak_steps=max(peak_steps,steps)
    controls=[]
    for q in [0,2,4,8]:
        bank=descriptor_bank(dense,q)
        controls.append(reject('invalid modulus '+str(q),lambda b=bank:execute(modules,dense,preparers[1],b,10000)))
    bank=descriptor_bank(dense,5);bank[5]=dense.marked([dense.ONE,dense.ZERO],53)
    controls.append(reject('noncanonical modulus',lambda:execute(modules,dense,preparers[1],bank,10000)))
    bank=descriptor_bank(dense,125);state,steps=execute(modules,dense,preparers[6],bank,10000)
    controls.append(reject('rational floor instead of modular coefficient',lambda:need(state[14]['cells']==dense.binary(2,bank[14][1])[0],'3/2 mod125 is63, not1')))
    shape=(1,5,1,1);payload=[int(j==10) for j in range(25)];bank=dense.fixtures(shape,0,0,payload,True)
    bank[14]=({},bank[14][1]-1);bank[16]=({},bank[16][1]-1)
    omitted=leaf.link(modules,[leaf.zero_offset(modules),preparers[1],affine.build_program(modules,inplace=True),leaf.erase(modules,16)])
    def missing_clear():
        state,steps=execute(modules,dense,omitted,bank,32001);leaf_check(state,steps,bank,dense,shape,payload,1,False)
    controls.append(reject('omit physical coefficient erasure',missing_clear))
    def wrong_sign():
        state,steps=execute(modules,dense,programs['-1:False'],bank,32001);leaf_check(state,steps,bank,dense,shape,payload,1,False)
    controls.append(reject('wrong signed coefficient',wrong_sign))
    bad=deepcopy(tables['1:False']);i=next(i for i,r in enumerate(bad['instructions']) if r[0]=='move');bad['instructions'][i][2]=2
    controls.append(reject('nonlocal compiled motion',lambda:dense.validate(bad)))
    return dict(source_prs=[5332,5820,5842],coefficients=list(map(str,coefficients)),quarter_codes=codes,
        descriptor_cases=descriptor_cases,legacy_abi_cases=legacy_cases,complete_leaf_calls=leaf_cases,payload_bits=bits,
        whole_bank_roundtrips=roundtrips,tapes=19,alphabet_symbols=7,transition_bound_per_bit=1024,visited_bound_per_bit=64,
        descriptor_bound='64*bit_length(Q)+128',maximum_fixture_steps=peak_steps,transcript_sha256=digest.hexdigest(),
        tables={k:dict(instructions=len(v['instructions']),sha256=sha256(canonical(v)).hexdigest()) for k,v in tables.items()},
        rejected_controls=controls,limits=['Later-target complete pair fibers only.','No G20 physical head/cache/padding/earlier-target or full supplier admission.'])


if __name__=='__main__':
    write=sys.argv[1:]==['--write'];need(write or not sys.argv[1:],'supported arguments')
    result=run(write)
    if write:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(canonical(result)==canonical(json.loads((P/'RESULT.json').read_text())),'complete typed receipt')
    print('PASS_G20_RATIONAL_SHEAR_LEAVES')
    print(json.dumps({k:result[k] for k in ['descriptor_cases','legacy_abi_cases','complete_leaf_calls','payload_bits','whole_bank_roundtrips']},sort_keys=True))
