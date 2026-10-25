"""Actual current-row comparison and paid ownership controls; source-bound."""
from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys
import types

P=Path(__file__).resolve().parent
ROOT=P.parents[1]


def need(ok,why):
    if not ok:raise ValueError(why)


def load(name,path):
    module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def authenticate():
    sources={}
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            digest=sha256((ROOT/row['path']).read_bytes()).hexdigest()
            need(digest==row['sha256'],'source SHA256 '+row['path']);sources[row['path']]=digest
    return sources


def modules():
    original=load('row_fixture',ROOT/'research/crt-mixed-row-entry/verify.py')
    rom=load('rom_producer',ROOT/'research/crt-encoded-benes-rom-producer/microcode.py')
    return original,original.modules(),rom,load('row_join',P/'join.py'),rom.producer_program()


def case(mod,moduli,widths,ell,state,level,start,row,fault=None):
    helper,old,rom,join,program=mod;w,r,e,numeric,caller_module,crt,row_module=old
    precision=1+sum(widths[start:start+(1<<level)])
    source=helper.axis_stream(w,r,e,moduli,widths,state)
    dirty=[helper.port(w,e,helper.bits(3*i+1,precision)+[w.RIGHT]) for i in range(8)]
    for i,tape in enumerate(dirty):
        for _ in range(i%3):tape.step(1)
    before=helper.snapshot([source,*dirty]);traffic=helper.traffic([source,*dirty])
    query=join.RowQuery(w,r,e,numeric,row_module,rom,program,source,dirty,widths,ell,level,start,row,fault)
    caller=caller_module.Caller(moduli,widths,ell,crt)
    expected=caller.apply(state,caller.row(state,level,row))
    middle=start+(1<<(level-1));stop=start+(1<<level)
    if query.output is None:
        need(not query.entry.active and helper.snapshot([source,*dirty])==before,'idle boundary')
        query.close()
        return dict(idle=True,row=row,producer_instructions=0)
    cells=query.output.cells;at=1;actual=[]
    for h in widths[middle:stop]:
        actual.append(sum(int(cells[at+j])<<j for j in range(h)));at+=h
        need(cells[at]=='|','returned coordinate delimiter');at+=1
    need(cells[at]=='R' and all(x=='_' for x in cells[at+1:]),'returned stream end')
    need(tuple(actual)==expected[middle:stop],'physical micro-row endpoint')
    need(helper.snapshot([source,*dirty])==before,'borrowed preservation before close')
    need(query.produced_rom.cells is query.service['rom'],'same produced ROM backing')
    need(all(t.head==0 for t in query.ports),'joined returned heads')
    owned=[*query.entry.inputs,*query.entry.context.owned]
    query.close()
    need(helper.snapshot([source,*dirty])==before,'borrowed preservation after close')
    need(all(all(x==w.BLANK for x in t.cells) and t.head==1 for t in owned),'all numerical entry ports retired')
    need(all(all(x=='_' for x in t.cells) and t.head==0 for t in query.ports),'all new port backing retired')
    need(all(all(x=='_' for x in cells) for cells in query.service.values()),'all producer and header backing retired')
    adapter_actions=sum(t.actions for t in query.ports)
    numerical=query.entry.context.arena.meter
    source_actions=helper.traffic([source,*dirty,*owned])-traffic+numerical.reads+numerical.writes+numerical.moves
    length=2+sum(3*h+4 for h in widths);n=1<<level
    active=[axis for axis in range(middle,stop) if caller_module.local_row(widths[axis],ell,row) is not None]
    work=length+(n+1)*(precision+2)+sum((2**widths[i]+1)*(widths[i]+1)+2**widths[i]*(2*widths[i]-1)+2*widths[i]+4 for i in active)
    entry_bound=2**20*(precision+2)**4+2**16*(precision+2)**2+128*(length+precision+n+1)
    rom_bound=sum(2*10**6*precision**2*(2**widths[i]+1)**3*(widths[i]+1)**4 for i in active)
    total_bound=entry_bound+rom_bound+4096*work
    need(source_actions+adapter_actions+query.producer_steps<=total_bound,'complete local time invoice')
    entry_storage=57*(precision+2)+3*(precision-2)*(2*precision+4)+6+3*precision+4*n+4
    rom_storage=sum(100*(precision+2)+5*precision*2**widths[i]*(widths[i]**2+3*widths[i]+1)+2**widths[i]*(4*widths[i]-1)+10*(widths[i]+1)+4*precision+9 for i in active)
    extra_storage=2*(max(widths[middle:stop])+3)+sum(widths[middle:stop])+len(widths[middle:stop])+3
    unique={id(t.cells):t.cells for t in query.ports}
    unique.update({id(cells):cells for cells in query.service.values()})
    retained=sum(len(t.cells) for t in owned)+sum(len(cells) for cells in unique.values())
    need(retained<=entry_storage+rom_storage+extra_storage,'complete retained backing invoice')
    return dict(idle=False,moduli=list(moduli),widths=list(widths),state=list(state),level=level,start=start,row=row,
                precision=precision,output=actual,producer_calls=query.invocations,
                producer_instructions=query.producer_steps,adapter_tape_actions=adapter_actions,
                entry_and_numeric_tape_actions=source_actions,
                producer_retained_cells=sum(len(cells) for cells in query.service.values()),
                new_retained_cells=sum(len(t.cells) for t in query.ports[:-2]),
                entry_retained_cells=sum(len(t.cells) for t in owned),distinct_owned_cells=retained,
                time_bound=total_bound,storage_bound=entry_storage+rom_storage+extra_storage)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--probe',action='store_true');ap.add_argument('--four-axis',action='store_true');ap.add_argument('--write-result',action='store_true');args=ap.parse_args()
    sources=authenticate();mod=modules()
    if args.four_axis:
        actual=case(mod,(5,7,11,13),(3,3,4,4),4,(1,5,0,9),2,0,0)
        result=dict(status='PASS_FOUR_AXIS_CURRENT_ROW',sources=sources,case=actual,
                    join_sha256=sha256((P/'join.py').read_bytes()).hexdigest())
        receipt=P/'ACTUAL4.json'
        if args.write_result:receipt.write_text(json.dumps(result,indent=2)+'\n')
        elif receipt.exists():need(json.dumps(json.loads(receipt.read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed four-axis receipt drift')
        print(result['status'],json.dumps(actual));return
    first=case(mod,(7,3),(3,2),3,(1,1),1,0,0)
    if args.probe:print('PASS_ACTUAL_CURRENT_ROW_PROBE',json.dumps(first));return
    cases=[first];state=(1,1)
    for row in range(1,5):
        out=case(mod,(7,3),(3,2),3,state,1,0,row);cases.append(out)
        if not out['idle']:state=(state[0],out['output'][0])
    need(state==(1,2),'actual complete padded level endpoint')
    endpoint=list(state)
    cases.append(case(mod,(7,3),(3,2),3,(7,1),1,0,1))
    controls=[]
    for fault,state,row in (('zero_offset',(1,1),1),('wrong_local_row',(1,1),1),
                            ('suppress_query',(1,3),4),('omit_layers_disposal',(1,1),0)):
        try:case(mod,(7,3),(3,2),3,state,1,0,row,fault)
        except ValueError:controls.append(fault)
        else:raise ValueError('undetected fault '+fault)
    result=dict(status='PASS_CURRENT_ROW_QUERY',sources=sources,cases=cases,controls=controls,
                join_sha256=sha256((P/'join.py').read_bytes()).hexdigest(),level_endpoint=endpoint)
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(json.dumps(json.loads((P/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed receipt drift')
    print(result['status'],json.dumps(result['cases']))


if __name__=='__main__':main()
