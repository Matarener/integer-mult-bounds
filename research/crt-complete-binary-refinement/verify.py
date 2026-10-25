"""Bounded independent source/bit simulation; never a full binary layer replay."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,why):
    if not ok:raise ValueError(why)


def load(path):
    module=types.ModuleType(path.stem);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    result={}
    for row in manifest['files']:
        if row['usage']=='input':
            raw=(ROOT/row['path']).read_bytes()
            need(sha256(raw).hexdigest()==row['sha256'],'source corruption: '+row['path'])
            result[row['path']]=row['sha256']
    return result


def digest(value):
    return sha256(repr(value).encode()).hexdigest()


def typed_equal(a,b):
    return json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)


class Harness:
    def __init__(self):
        self.low=load(HERE/'lower.py')
        self.source=load(ROOT/'research/crt-complete-repair-control/machine.py')
        self.bits=load(ROOT/'research/crt-binary-key-port/binary.py')
        self.code,self.owned,self.stages=self.source.assemble(ROOT)
        self.roles=tuple(self.source.prepare(self.owned,{x:[] for x in ('G','H','K','Y','J','B','data','rom')}))
        self.regs,self.tapes,self.rounds=self.low.closure(self.code,self.roles,self.source.registers(self.code))
        self.lower=self.low.Lower(self.code,self.roles,self.regs,self.tapes)
        self.program,self.starts=self.lower.compile()

    def encoded(self,tapes,heads=None,lower=None):
        lower=lower or self.lower
        out={}
        for role,cells in tapes.items():
            tape=self.bits.BitTape([b for x in cells for b in self.word(lower,x)],13*(heads or {}).get(role,0))
            out[role]=tape
        return out

    @staticmethod
    def word(lower,value):
        n=lower.codes[lower_value(value)]
        return [(n>>j)&1 for j in range(13)]

    @staticmethod
    def put(machine,lower,name,value):
        n=lower.codes[lower_value(value)]
        for j in range(13):
            if (name,j) in lower.registers:machine.registers[lower.registers[name,j]]=(n>>j)&1

    @staticmethod
    def value(machine,lower,name):
        n=sum(machine.registers[lower.registers[name,j]]<<j for j in range(13))
        return lower.reverse[n]

    def compare_tapes(self,expected,heads,actual,lower=None):
        lower=lower or self.lower
        for role,cells in expected.items():
            need(actual[role].head==13*heads[role],'physical head '+role)
            wanted={i:b for i,b in enumerate(b for x in cells for b in self.word(lower,x)) if b}
            need(actual[role].cells==wanted,'physical tape '+role)

    def micro(self,row,values,tapes,heads=None,fault=None):
        """Original source executor is the reference, not a rewritten interpreter."""
        code=[row,('halt','accept'),('halt','false')]
        if row[0]=='branch':code[0]=('branch',row[1],1,2)
        if row[0]=='jump':code[0]=('jump',1)
        regs={r:{None,lower_value(values.get(r,None))} for r in self.source.registers(code)}
        # Full static domains retain valid alternatives for dynamic dispatch.
        for r in regs:
            if r in self.regs:regs[r].update(self.regs[r])
        if row[0]=='field':
            regs[row[-1]].update(x[row[2]] for x in list(regs[row[1][1]])
                                if isinstance(x,tuple) and row[2]<len(x))
        tp={r:set(map(lower_value,v))|{'_'} for r,v in tapes.items()}
        low=self.low.Lower(code,tuple(tapes),regs,tp,fault=fault)
        program,starts=low.compile();physical=self.encoded(tapes,heads,low)
        machine=self.bits.Machine(program,len(low.registers),physical)
        while machine.pc!=starts[0]:machine.step()
        for name,value in values.items():self.put(machine,low,name,value)
        reference={r:list(v) for r,v in tapes.items()}
        def seed(pc,t,h,r,*_):
            r.update(values)
            if heads:h.update(heads)
        result=self.source.execute(code,reference,observe={0:seed},max_steps=3)
        nextpc=2 if result['status']=='false' else 1
        if row[0]=='halt':
            machine.run()
        else:
            machine.step()
            steps=0
            while machine.pc!=starts[nextpc]:
                need(machine.status is None,'premature bit rejection')
                machine.step();steps+=1;need(steps<300000,'micro block budget')
            for name,value in result['registers'].items():
                if all((name,j) in low.registers for j in range(13)):
                    need(self.value(machine,low,name)==lower_value(value),'register refinement '+name)
            machine.run()
        self.compare_tapes(reference,result['heads'],physical,low)
        need(machine.status==result['status'],'halt refinement')
        need(not any(machine.registers),'control erasure')
        return sum(machine.census.values())

    def cut(self,entry,stop,tapes,initial_regs=None,heads=None,budget=200000):
        """One persistent set of encoded objects, checked at source boundaries."""
        physical=self.encoded(tapes,heads)
        machine=self.bits.Machine(self.program,len(self.lower.registers),physical)
        # Every finite control bit is initialized by the emitted prefix.
        while machine.pc!=self.starts[0]:machine.step()
        for name,value in (initial_regs or {}).items():self.put(machine,self.lower,name,value)
        machine.pc=self.starts[entry]
        reference={r:list(v) for r,v in tapes.items()}
        last=[None];count=[0];expectedpc=[entry]
        class Done(Exception):pass
        def observe(pc,t,h,r,steps,cells):
            if count[0]==0:
                r.update(initial_regs or {})
                if heads:h.update(heads)
            if last[0] is not None:
                # Step at least once: a source self-loop is still a transition.
                machine.step()
                while machine.pc!=self.starts[pc]:
                    need(machine.status is None,'cut rejected before source boundary')
                    machine.step()
                previous=self.code[last[0]];op,*a=previous
                if op in ('read','copy','field','not','record','eq','ne','in','notin','xorbit','andbit','orbit'):
                    name=a[-1]
                    need(self.value(machine,self.lower,name)==lower_value(r[name]),'cut register '+name)
                if op in ('read','write','move'):
                    role=resolve(previous[1],r)
                    need(physical[role].head==13*h[role],'cut head '+role)
                    if op=='write':
                        index=h[role]
                        got=sum(physical[role].cells.get(13*index+j,0)<<j for j in range(13))
                        need(got==self.lower.codes[lower_value(t[role][index])],'cut write')
            count[0]+=1
            if pc==stop:
                self.compare_tapes(t,h,physical)
                raise Done
            need(count[0]<budget,'bounded source cut budget')
            last[0]=pc
        # A static entry jump is harness control; no caller data are changed.
        code=list(self.code);code[0]=('jump',entry)
        callbacks={pc:observe for pc in range(len(code))}
        if entry!=0:callbacks[0]=lambda *args:None
        try:self.source.execute(code,reference,observe=callbacks,max_steps=budget+1)
        except Done:pass
        else:raise ValueError('cut stop not reached')
        return dict(source_boundaries=count[0],binary_actions=sum(machine.census.values()),
                    tape_actions=sum(sum(t.actions.values()) for t in physical.values()),
                    encoded_tapes=digest({r:sorted(t.cells.items()) for r,t in physical.items()}))


def lower_value(x):
    if isinstance(x,bool):return int(x)
    if isinstance(x,tuple):return tuple(lower_value(y) for y in x)
    return x


def resolve(a,regs):
    if a[0]=='c':return a[1]
    if a[0]=='r':return regs[a[1]]
    return tuple(resolve(x,regs) for x in a[1])


def microchecks(h):
    C=lambda x:('c',x);R=lambda x:('r',x)
    cases=[]
    def add(row,values={},tapes=None,heads=None):cases.append((row,values,tapes or {'data':['_']},heads))
    for x in (('R',0),('R',4095),('S',False,True,'0','1')):
        add(('read',C('data'),'x'),tapes={'data':[x]})
        add(('write',C('data'),R('x')),{'x':x})
        add(('copy',R('x'),'x'),{'x':x})
    add(('move',C('data'),C(1)))
    add(('move',C('data'),C(-1)),tapes={'data':['_','_']},heads={'data':1})
    for op in ('eq','ne'):
        for x,y in ((False,0),(True,1),('0',0),(('R',0),('R',4095)),(None,None)):
            add((op,R('x'),R('y'),'x'),{'x':x,'y':y})
    for op in ('in','notin'):
        for x in ('0','1','_'):
            add((op,R('x'),('tuple',(C('0'),C('1'))),'x'),{'x':x})
    for x in (None,False,True,'0',('R',0)):
        add(('not',R('x'),'x'),{'x':x});add(('branch',R('x'),1,2),{'x':x})
        add(('record',R('x'),'x'),{'x':x})
    for op in ('xorbit','andbit','orbit'):
        for x in ('0','1'):
            for y in ('0','1'):add((op,R('x'),R('y'),'x'),{'x':x,'y':y})
    for i in range(5):add(('field',R('x'),i,'x'),{'x':('G',True,False,'1','0')})
    add(('copy',('tuple',(C('G'),R('x'),R('y'),C('0'),C('1'))),'z'),{'x':True,'y':False})
    add(('jump',1));add(('halt','accept'))
    actions=sum(h.micro(*case) for case in cases)
    rejected=[]
    for fault,case in (('short_stride',(('move',C('data'),C(1)),{}, {'data':['_']},None)),
                       ('keep_control',(('copy',C('1'),'x'),{}, {'data':['_']},None))):
        try:h.micro(*case,fault=fault)
        except ValueError:rejected.append(fault)
        else:raise ValueError('undetected mutant '+fault)
    # Actual dynamic tape-register instruction: distinguish borrowed tapes.
    rolepc=next(i for i,(op,*a) in enumerate(h.code) if op=='read' and a[0][0]=='r')
    row=h.code[rolepc];name=row[1][1];roles=sorted(h.regs[name]&set(h.roles))
    roles.append(next(r for r in h.roles if r not in roles))
    tapes={r:['_'] for r in roles};tapes[roles[0]]=['1']
    h.micro(row,{name:roles[0]},tapes)
    try:h.micro(row,{name:roles[0]},tapes,fault='wrong_role')
    except ValueError:rejected.append('wrong_role')
    else:raise ValueError('undetected role mutant')
    return dict(cases=len(cases)+1,binary_actions=actions,mutants=rejected,dynamic_role_pc=rolepc)


def control_graph(h,program):
    starts=set(h.starts[:-1]);tails={len(h.program)-(i+1)*(len(h.lower.registers)+1) for i in range(2)}
    edges=0
    for i,(lo,hi) in enumerate(zip(h.starts,h.starts[1:])):
        source_op,*source_args=h.code[i]
        expected={h.starts[i+1]}
        if source_op=='jump':expected={h.starts[source_args[0]]}
        elif source_op=='branch':expected={h.starts[source_args[1]],h.starts[source_args[2]]}
        elif source_op=='halt':expected=set()
        for pc in range(lo,hi):
            op,*a=program[pc]
            targets=a[1:] if op=='branch' else a if op=='jump' else [pc+1]
            for target in targets:
                need(type(target) is int and 0<=target<len(program),'literal in-range control target')
                need((lo<target<hi and target>pc) or target in expected or target in tails,
                     'unpriced internal loop/cross-block target')
                edges+=1
            if op in ('read','write_reg','move'):need(a[0] in h.roles,'literal tape role')
            if op=='move':need(a[1] in (-1,1),'unit bit move')
            if op=='set':need(a[1] in (0,1),'bit constant')
    return edges


def structural(h):
    edges=control_graph(h,h.program)
    bad=list(h.program);pc=next(i for i in range(h.starts[0],h.starts[-1]) if bad[i][0]=='branch')
    bad[pc]=('branch',bad[pc][1],h.starts[-2],h.starts[-2])
    try:control_graph(h,bad)
    except ValueError:pass
    else:raise ValueError('wrong source relocation accepted')
    machine=h.bits.Machine(h.program,len(h.lower.registers),{})
    machine.registers[:]=[1]*len(machine.registers)
    while machine.pc!=h.starts[0]:machine.step()
    for (name,j),index in h.lower.registers.items():
        expected=(h.lower.codes[None]>>j)&1 if name in h.regs else 0
        need(machine.registers[index]==expected,'dirty finite control initialization')
    need(not typed_equal({'count':1},{'count':True}),'typed receipt Boolean control')
    need(not typed_equal({'count':1},{'count':1.0}),'typed receipt floating control')
    # Entry domains must include the actual ROM markers, independently of codes.
    need({'L','R','0','1','_'}<=h.tapes['rom'],'actual ROM closure alphabet')
    bad=list(h.code);bad[0]=('unknown_source_op',)
    try:h.low.closure(bad,h.roles,h.source.registers(h.code))
    except ValueError:pass
    else:raise ValueError('unknown source opcode accepted')
    return dict(control_edges=edges,dirty_initialization_bits=len(machine.registers),
                rejected=['receipt_boolean','receipt_float','unknown_source_opcode','wrong_source_relocation'])


def actualcuts(h):
    borrowed={x:['<',*('1'*v),'>','_'] for x,v in zip(('G','H','K','Y','J','B'),(2,2,6,8,2,0))}
    borrowed.update(data=['<',('R',123),'>'],rom=['L',*('1'*32),'R'])
    tapes=h.source.prepare(h.owned,borrowed)
    producer=h.cut(1,h.stages['scanner'],tapes)
    # Obtain the genuine complete scanner/split entry using the exact source.
    entry,end=h.stages['key_sites'][0];snapshot={}
    class Capture(Exception):pass
    def capture(pc,t,heads,regs,*_):
        snapshot.update(tapes={r:list(v) for r,v in t.items()},heads=dict(heads),regs=dict(regs));raise Capture
    try:h.source.execute(h.code,tapes,observe={entry:capture},max_steps=4000000)
    except Capture:pass
    need(snapshot,'actual source key-entry capture')
    key=h.cut(entry,end,snapshot['tapes'],snapshot['regs'],snapshot['heads'],budget=100000)
    return dict(producer=producer,actual_scanner_split_key=key,
                boundary='Key entry is source-generated and encoded once; scanner itself is not binary-replayed.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');ap.add_argument('--light',action='store_true');args=ap.parse_args()
    pins=authenticate();h=Harness()
    need(len(h.lower.reverse)==len(h.lower.codes),'injective codebook')
    need(all(h.lower.codes[x]==4096+x[1] for x in h.low.RECORDS),'all record encodings')
    need(all((code>=4096)==(value in h.low.RECORDS) for value,code in h.lower.codes.items()),'record classifier exactness')
    controls=microchecks(h)
    result=dict(status='PASS_COMPLETE_BINARY_REFINEMENT',sources=pins,closure_rounds=h.rounds,
                source_instructions=len(h.code),source_opcodes=dict(sorted(Counter(r[0] for r in h.code).items())),
                tape_roles=len(h.roles),codes=len(h.lower.codes),binary_instructions=len(h.program),
                control_bits=len(h.lower.registers),max_block=max(b-a for a,b in zip(h.starts,h.starts[1:])),
                source_program_sha256=digest(h.code),binary_program_sha256=digest(h.program),micro=controls,
                structural=structural(h))
    if args.light:print(json.dumps(result,indent=2));return
    result['cuts']=actualcuts(h)
    if args.write_result:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(typed_equal(json.loads((HERE/'RESULT.json').read_text()),result),'frozen typed receipt mismatch')
    print(result['status'],json.dumps(result['cuts']))


if __name__=='__main__':main()
