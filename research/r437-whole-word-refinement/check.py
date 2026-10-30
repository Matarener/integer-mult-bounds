"""Source-bound symbolic translation check. No physical payload execution.

The compiler, dispatcher and logical Driver are extracted unchanged except for
streaming the compiler's append-only operation list, to bound verifier memory.
Primitive semantics are explicit free-term constructors, not numerical oracles.
"""
import ast
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CALLER=ROOT/'research/selected-bit-physical-caller'
PRE=CALLER/'inputs/pr2753/predecessor'
EMPTY=b''
XOR_TRACE=None


def need(ok,message):
    if not ok:raise ValueError(message)


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))


def extract(path,name,namespace,stream=False,mutation=None):
    tree=ast.parse(path.read_text())
    node=next(x for x in tree.body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name==name)
    if mutation is not None:node=mutation(node)
    if stream:
        replacements=0
        for item in ast.walk(node):
            if isinstance(item,ast.Assign) and len(item.targets)==1 and isinstance(item.targets[0],ast.Name) and item.targets[0].id=='operations':
                need(ast.dump(item.value)==ast.dump(ast.parse('[("node",)]',mode='eval').body),'exact append-only compiler list initialization')
                item.value=ast.Call(ast.Name('OperationSink',ast.Load()),[item.value],[]);replacements+=1
        need(replacements==1,'one compiler list streaming substitution')
    exec(compile(ast.fix_missing_locations(ast.Module([node],type_ignores=[])),str(path),'exec'),namespace)
    return namespace[name]


def term(tag,*args):
    h=hashlib.sha256();h.update(tag.encode());h.update(b'\0')
    for value in args:
        data=value if isinstance(value,bytes) else canonical(value).encode()
        h.update(len(data).to_bytes(8,'big'));h.update(data)
    return h.digest()


class Packet:
    def __init__(self,data=EMPTY):self.data=data
    def clear(self):self.data=EMPTY
    def rewind(self):pass


def read(packet):
    need(packet.data!=EMPTY,'read a live complete abstract packet')
    return packet.data


def gather(family,context,old_count,low,fibre):return Packet(term('gather',read(family),low))
def route_packet(packet,route,context,old_count,fibre):return Packet(term('route',read(packet),route))
def scatter(family,packet,context,old_count,low,fibre):return Packet(term('scatter',read(family),read(packet),low))
def xor_packet(source,target,*unused):
    a,b=read(source),read(target);out=term('xor',a,b)
    if XOR_TRACE is not None:
        XOR_TRACE['count']+=1;XOR_TRACE['digest'].update(a+b+out)
    return Packet(out)
def clone_packet(source,*unused):return Packet(read(source))
def transfer(source,target):target.data=read(source);source.clear()
def family_rows(context):return NS(close=lambda:None)
def compile_owner(chart,low,codes):return (('native',low,chart),('forward',low,chart),('backward',low,chart))


class Fields:
    def __init__(self,*args):pass


def pending(event):
    a,b=event['source_level'],event['target_level']
    axes=list(range(1,8+7*b)) if a==-1 else list(range(8+7*a,8+7*b))
    need(len(axes)==event['rank'],'source pending-rank formula')
    return axes


class Topology:
    """Direct scalar/index projection of current source; no projector arithmetic."""
    replicas=32;pairs=4;ports=111;families=28416;stride=888
    def __init__(self,lows=('alpha',)):
        self.template=json.loads(gzip.decompress((HERE/'inputs/template.json.gz').read_bytes()))
        self.word=json.loads(gzip.decompress((HERE/'inputs/word.json.gz').read_bytes()))
        self.schedule=self.template['schedule'];self.lows=tuple(lows)
        self.catalogue=NS(low_classes=lambda:iter(self.lows),codes=None)
        self.requests={};self.idles={};self.recipes={};self.records=[]
        idle_events={e['idx']:e for e in self.schedule if e['kind']=='idle'}
        for stage in range(9):
            c=self.template['calls'][32*stage];reverse=c['orientation']=='reverse'
            events=tuple(map(tuple,self.template['local_programs'][c['orientation']]))
            ids=[]
            for position,event in enumerate(events):
                if event[0] in (0,2):
                    ids.append(len(self.records));self.records.append((stage,position,event[0],event[1]))
                else:ids.append(None)
            start=tuple(self.word['final'] if reverse else self.word['start'])
            end=tuple(self.word['start'] if reverse else self.word['final'])
            self.recipes[stage]=events,tuple(ids),start,end,reverse
        occupied=defaultdict(set)
        for child,copy,offset,width,_stage,_helper in self.template['hosting']['slots']:
            axes=pending(idle_events[child])[offset:offset+width]
            need(not occupied[child,copy].intersection(axes),'disjoint occupied idle supports')
            occupied[child,copy].update(axes)
        self.idle_records={}
        for child,event in idle_events.items():
            self.idles[child]=[]
            for copy in range(222):
                axes=tuple(sorted(set(pending(event))-occupied[child,copy]))
                if not axes:continue
                identifier=len(self.records);self.records.append((child,copy,3,axes))
                self.idles[child].append(identifier)
                self.idle_records[identifier]=(event['pair']*222+copy,len(axes))
        need(len(self.records)==28233,'exact current source ordinal count')
        need(self.idle_records[27776][1]==26 and self.idle_records[27777][1]==42,'actual OQ4 changed idles')
        self.idle_events=idle_events
    @lru_cache(None)
    def call(self,stage,replica):
        c=self.template['calls'][32*stage+replica]
        owners=[]
        for family,route in c['owners']:
            if route[0]=='data':chart=('data',route[2],route[1],())
            else:
                _,child,offset,width=route;axes=tuple(pending(self.idle_events[child])[offset:offset+width])
                chart=('host',family%111 if min(axes)<8 else -1,-1,axes)
            owners.append(NS(family=family,chart=chart))
        events,ids,start,end,reverse=self.recipes[stage]
        need(len(owners)==len(start)==len(end)==659,'actual R437 staged role extent')
        return NS(stage=stage,replica=replica,owners=tuple(owners),events=events,requests=ids,start=start,end=end,reverse=reverse)
    def matrix(self,chart):return chart
    def idle_family(self,identifier,replica):return self.idle_records[identifier][0]+888*replica
    def family(self,replica,pair,side,port):return 888*replica+(2*pair+side)*111+port


class Consumer:
    def __init__(self,mode=0):self.mode=mode;self.count=0;self.trace=hashlib.sha256()
    def apply(self,packet,identifier,common,low,*unused,mode=None):
        self.count+=1;result=term('residual',identifier,common,low,self.mode if mode is None else mode,read(packet))
        self.trace.update(result)
        return Packet(result)


def family_digest(families):
    h=hashlib.sha256()
    for i in sorted(families):h.update(read(families[i]))
    return h.hexdigest()


class AbstractMachine:
    def __init__(self,topology,consumer,dispatch,mutant=None):
        self.topology=topology;self.consumer=consumer;self.context=NS(codes=None)
        self.roles={('family',i):Packet(term('initial-arbitrary-family',i)) for i in range(topology.families)}
        self.observe=None;self.checkpoints=[];self.counts=Counter();self.mutant=mutant
        self.dispatch=dispatch.__get__(self)
    def tape(self,label):return self.roles.setdefault(label,Packet())
    def count(self,label):return None
    def commit(self,result,label):
        target=self.tape(label)
        if result is not target:target.data=read(result)
    def node(self):pass
    def close_geometry(self):pass
    def residual_begin(self,role,definition):self.commit(self.tape(role),'current')
    def block(self,definition,block):
        if block[0]=='good':self.commit(self.consumer.apply(self.tape('current'),definition.identifier,definition.common,definition.low,mode=definition.mode),'current')
        return False
    def returned(self):return True
    def run_one(self,operation):
        self.counts[operation[0]]+=1
        if operation[0]=='checkpoint':
            self.checkpoints.append((operation[1:],family_digest({i:self.tape(('family',i)) for i in range(self.topology.families)})))
        if self.mutant:self.mutant(self,operation)
        else:self.dispatch(operation)
        if operation[0]=="clear":need(not self.tape(operation[1]).data,"every emitted disposal completed")


def bindings():
    env=dict(need=need,dataclass=dataclass,FiniteFields=Fields)
    state=extract(PRE/'control.py','LocalState',env)
    cursor=extract(CALLER/'residual_blocks.py','Cursor',env)
    primitives=dict(gather=gather,scatter=scatter,route_packet=route_packet,xor_packet=xor_packet,
                    xor_family=xor_packet,transfer=transfer,clone_packet=clone_packet,
                    family_rows=family_rows,compile_owner=compile_owner,LocalState=state,need=need)
    driver=extract(PRE/'driver.py','Driver',dict(primitives))
    tree=ast.parse((CALLER/'macro_machine.py').read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Machine')
    dispatch=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='dispatch')
    denv=dict(primitives);exec(compile(ast.Module([dispatch],type_ignores=[]),str(CALLER/'macro_machine.py'),'exec'),denv)
    return state,cursor,driver,denv['dispatch']


def check_word(topology,mode=0,mutant=None):
    global XOR_TRACE
    state,cursor,Driver,dispatch=bindings();consumer=Consumer(mode)
    XOR_TRACE=dict(count=0,digest=hashlib.sha256())
    families={i:Packet(term('initial-arbitrary-family',i)) for i in range(topology.families)}
    expected=[]
    def observe(kind,*labels):
        if kind=='global_return':expected.append((labels,family_digest(families)))
    logical=Driver(NS(codes=None),topology,consumer,Packet(),None,None,None,None,None,observe)
    logical.global_word(families)
    expected_xor=(XOR_TRACE['count'],XOR_TRACE['digest'].hexdigest())
    XOR_TRACE=dict(count=0,digest=hashlib.sha256())
    mconsumer=Consumer(mode);machine=AbstractMachine(topology,mconsumer,dispatch,mutant)
    class OperationSink:
        def __init__(self,initial):
            for op in initial:self.append(op)
        def append(self,operation):machine.run_one(operation)
        def __iter__(self):return iter(())
    def residual(identifier,common,low,mode):
        return NS(identifier=identifier,common=common,low=low,mode=mode,axis=None,plan=NS(good=True))
    compiler=extract(CALLER/'macro_code.py','compile_node',
                     dict(LocalState=state,Cursor=cursor,compile_owner=compile_owner,need=need,
                          Code=lambda operations,staged_roles:NS(staged_roles=staged_roles),OperationSink=OperationSink),stream=True)
    code=compiler(topology,NS(residual=residual),mode)
    actual_xor=(XOR_TRACE['count'],XOR_TRACE['digest'].hexdigest());XOR_TRACE=None
    need(expected_xor==actual_xor,'all ordered local and family XOR inputs and outputs')
    need(expected==machine.checkpoints,'all ordered global checkpoint expressions')
    need(consumer.count==mconsumer.count and consumer.trace.digest()==mconsumer.trace.digest(),'all ordered residual input/output expressions')
    need(all(not p.data for label,p in machine.roles.items() if isinstance(label,tuple) and label[0]=='stage'),'private and staged payload disposal')
    return dict(checkpoints=len(expected),residuals=consumer.count,staged_roles=code.staged_roles,
                complete_xor_count=expected_xor[0],xor_trace_sha256=expected_xor[1],
                source_residual_trace_sha256=consumer.trace.hexdigest(),final_family_terms_sha256=family_digest(families),
                macros=dict(sorted(machine.counts.items())))


def tiny():
    # Two distinct family packets, one COPY interval and two lows; dirty x,y
    # remain unconstrained symbolic inputs. Includes IDLE/bridge/exchange.
    events=((2,0,2,0,1,7,0),(1,1,2,1,1,0),(3,0,2,0,1,0,0))
    call=NS(stage=0,replica=0,owners=(NS(family=0,chart='a'),NS(family=1,chart='b')),
            events=events,requests=(0,None,None),start=(0,1),end=(0,1),reverse=False)
    t=NS(replicas=1,pairs=1,ports=1,families=2,
         schedule=({'kind':'local_cover_sweep','stage':0},{'kind':'idle','idx':0},
                   {'kind':'bridge','coefficient':1,'dst':0,'src':1},{'kind':'exchange'}),
         catalogue=NS(low_classes=lambda:iter(('alpha','beta')),codes=None),
         idles={0:(1,)},call=lambda *args:call,matrix=lambda x:x,
         idle_family=lambda *args:0,family=lambda replica,pair,side,port:(pair+side)%2)
    return t


def controls():
    outcomes={};t=tiny();check_word(t);check_word(t,mode=1)
    def moved_copy(machine,op):
        if op[0]=='copy':transfer(machine.tape(op[1]),machine.tape(op[2]))
        else:machine.dispatch(op)
    def lost_private(machine,op):
        if op[0]=='move' and op[1]=='copy_source':machine.tape(op[1]).clear()
        else:machine.dispatch(op)
    def stale_scatter(machine,op):
        if op[0]=='route_scatter':
            family=op[2];machine.tape(('family',family)).data=term('initial-arbitrary-family',family)
        machine.dispatch(op)
    def skipped_clear(machine,op):
        if op[0]!='clear' or op[1]!=('stage',2):machine.dispatch(op)
    def reverse_xor(machine,op):
        if op[0] in ('xor','family_xor'):machine.dispatch((op[0],op[2],op[1]))
        else:machine.dispatch(op)
    for name,mutation in [('move_instead_of_clone',moved_copy),('lost_private_output',lost_private),
                          ('stale_family_scatter',stale_scatter),('omit_disposal',skipped_clear),('reverse_XOR_roles',reverse_xor)]:
        try:check_word(t,mutant=mutation)
        except ValueError as e:outcomes[name]=str(e)
        else:raise ValueError('accepted semantic mutant: '+name)
    return outcomes


def guard_gap():
    """Actual omitted source check; no production bug claimed on admitted data."""
    t=tiny();c=t.call(0,0);c.owners=(NS(family=0,chart='a'),NS(family=0,chart='a'))
    state,cursor,Driver,_=bindings();families={i:Packet(term('initial-arbitrary-family',i)) for i in range(2)}
    d=Driver(NS(codes=None),t,Consumer(),Packet(),None,None,None,None,None)
    try:d.global_word(families)
    except ValueError as e:need(str(e)=='disjoint complete owned low packets','exact logical duplicate-owner rejection')
    else:raise ValueError('logical Driver accepted duplicate owner')
    compiler=extract(CALLER/'macro_code.py','compile_node',dict(LocalState=state,Cursor=cursor,
        compile_owner=compile_owner,need=need,Code=lambda operations,staged_roles:NS(operations=operations)))
    code=compiler(t,NS(residual=lambda identifier,common,low,mode:NS(identifier=identifier,common=common,
         low=low,axis=None,plan=NS(good=True))))
    need(len(code.operations)>0,'finite compiler accepts duplicate-owner topology')
    return {'logical_driver':'REJECTED: disjoint complete owned low packets',
            'finite_compiler':'ACCEPTED', 'conclusion':'Compiler success alone does not imply source-domain admission.'}


def run_control():
    """Execute the unchanged dispatch loop with explicit well-bracketed actions.

    This models the call/return contract only. It is not a second physical return
    test and makes no claim that the primitive call/return code meets it.
    """
    from contextlib import nullcontext
    tree=ast.parse((CALLER/'macro_machine.py').read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Machine')
    method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    env=dict(need=need);exec(compile(ast.Module([method],type_ignores=[]),'<unchanged Machine.run>','exec'),env)
    class Harness:
        def __init__(self,depth):
            self.closed=False;self.pool=NS(install=nullcontext,empty=lambda:None)
            self.numerical=NS(machine=NS(tapes=[{},{0:'^'}]));self.depth=depth;self.stack=[]
            self.programs=(NS(operations=('enter','call','after','return')),)
            self.counts={'macros':0};self.output=Packet();self.trace=[]
        def load_root(self,*args):self.mode=0;self.pc=0
        def boundary(self):pass
        def dispatch(self,op):
            self.trace.append((self.depth,self.pc,op))
            if op=='call' and self.depth:
                self.stack.append((self.depth,self.pc+1));self.depth-=1;self.pc=0;return 'jump'
            if op=='return':
                if not self.stack:return 'done'
                self.depth,self.pc=self.stack.pop();return 'jump'
            return 'next'
        def erase_work(self):self.closed=True
    results=[]
    for depth in (0,1,2,17):
        h=Harness(depth);env['run'](h,*([None]*11))
        expected=[(i,p,op) for i in range(depth,-1,-1) for p,op in ((0,'enter'),(1,'call'))]
        expected += [(i,p,op) for i in range(0,depth+1) for p,op in ((2,'after'),(3,'return'))]
        need(h.trace==expected and h.closed and not h.stack,'run next/jump/done continuation simulation')
        results.append({'depth':depth,'macros':h.counts['macros']})
    return results


def run():
    t=Topology();result=check_word(t)
    need(result['residuals']==903456 and result['staged_roles']==660,'complete actual source skeleton census')
    result.update(status='PASS_R437_SYMBOLIC_WHOLE_WORD_REFINEMENT',formal_low_labels=1,
                  symbolic_low_scope='One formal arbitrary low; all-low claim is the written loop induction, not GL64 enumeration.',
                  controls=controls(),duplicate_owner_guard_gap=guard_gap(),run_loop_contract_checks=run_control(),physical_payload_executed=False,
                  primitive_contracts_proved=False)
    return result


if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
