"""Independent boundary audit of the unchanged PR5496 multi-target join.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. Observers never supply a successful execution's operands.
"""
import argparse
from functools import lru_cache
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


class AuditError(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise AuditError(reason)


def canonical(value):
    """Preserve JSON types: True must not compare equal to 1 in a receipt."""
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def authenticate():
    hashes = {}
    for row in json.loads((PACKAGE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(sha256(raw).hexdigest() == row['sha256'], 'source hash: ' + row['path'])
            hashes[row['path']] = row['sha256']
    for row in json.loads((PACKAGE / 'VENDORED.json').read_text())['files']:
        raw = (PACKAGE / row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'vendor hash: ' + row['path'])
        hashes[row['path']] = row['sha256']
    return hashes


def load(name, path, raw=None):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes() if raw is None else raw, str(path), 'exec'), module.__dict__)
    return module


def modules():
    base = ROOT / 'research/r437-preparation-composition/predecessor4025/source'
    w = load('words', base / 'words.py')
    r = load('audit_records', base / 'records.py')
    e = load('audit_entry', ROOT / 'research/encoded-crt-entry-lifecycle/entry.py')
    num = load('audit_numeric', ROOT / 'research/encoded-current-crt/producer.py')
    row = load('audit_row_entry', ROOT / 'research/crt-mixed-row-entry/bridge.py')
    rom = load('audit_rom', ROOT / 'research/crt-encoded-benes-rom-producer/microcode.py')
    return w, r, e, num, row, rom, rom.producer_program()


@lru_cache(None)
def network(permutation):
    """Exhaustive color oracle, independent of the source's DFS and arena.

    The least satisfying tuple chooses zero at each component's minimum
    vertex, the canonical source orientation. Only h<=3 is exercised.
    """
    n = len(permutation)
    need(n >= 2 and n & (n - 1) == 0, 'oracle dyadic size')
    need(sorted(permutation) == list(range(n)), 'oracle permutation')
    if n == 2:
        return ((0, (permutation[0], permutation[0])),)
    inv = tuple(permutation.index(y) for y in range(n))
    edges = [(x, x+1) for x in range(0,n,2)] + [(inv[y],inv[y+1]) for y in range(0,n,2)]
    color = next((c for c in itertools.product((0,1), repeat=n)
                  if all(c[x] != c[y] for x,y in edges)), None)
    need(color is not None, 'oracle bipartite matchings')
    children = []
    for c in (0,1):
        selected = [next(x for x in (2*j,2*j+1) if color[x] == c) for j in range(n//2)]
        children.append(network(tuple(permutation[x]//2 for x in selected)))
    layers = [(0,tuple(color[x] ^ (x%2) for x in range(n)))]
    for k in range(len(children[0])):
        layers.append((children[0][k][0]+1,
                       tuple(children[x%2][k][1][x//2] for x in range(n))))
    layers.append((0,tuple(color[inv[y]] ^ (y%2) for y in range(n))))
    return tuple(layers)


def rotation(h, modulus, offset):
    return tuple((x+offset)%modulus if x<modulus else x for x in range(1<<h))


def oracle(case):
    """Bounded congruence search, not the retained CRT reconstruction."""
    moduli, widths, state = case['moduli'],case['widths'],case['state']
    start, size = case['start'],1<<case['level']
    middle, stop = start+size//2,start+size
    product = math.prod(moduli[start:middle])
    if any(state[i]>=moduli[i] for i in range(start,middle)):
        lower=0
    else:
        candidates=[k for k in range(product)
                    if all((k-state[i]*math.prod(moduli[start:i]))%moduli[i]==0
                           for i in range(start,middle))]
        need(len(candidates)==1,'oracle unique current child')
        lower=candidates[0]
    rows=[]
    for i in range(middle,stop):
        h,s,g,ell=widths[i],moduli[i],case['row'],case['ell']
        offsets=[c for c in range(s) if (product*c-lower)%s==0]
        need(len(offsets)==1,'oracle unique offset')
        c=offsets[0];product*=s
        active=h==ell or g not in (ell-1,ell)
        local=g if h==ell or g<ell-1 else g-2
        layers=network(rotation(h,s,c));value=state[i]
        if active:
            bit,table=layers[local];value^=table[value]<<bit
        rows.append(dict(axis=i,h=h,modulus=s,offset=c,active=active,
                         local=local if active else None,input=state[i],output=value,layers=layers))
    return lower,rows


def port(w,e,symbols):
    tape=e.Port(w)
    for symbol in symbols:tape.append(symbol)
    tape.rewind();return tape


def bits(value,width):
    return [(value>>j)&1 for j in range(width)]


def snapshot(ports):
    return [(bytes(p.cells),p.head) for p in ports]


def traffic(ports):
    return sum(p.meter.reads+p.meter.writes+p.meter.moves for p in ports)


def read_header(cells,precision,offset=False):
    ending=['|','R'] if offset else ['R']
    need(cells[:1]==['L'] and cells[precision+1:precision+1+len(ending)]==ending,'header delimiters')
    need(all(x in ('0','1') for x in cells[1:precision+1]),'header binary width')
    need(all(x=='_' for x in cells[precision+1+len(ending):]),'header blank tail')
    return sum(int(x)<<j for j,x in enumerate(cells[1:precision+1]))


def body(cells,expected):
    need(cells[:len(expected)]==expected and all(x=='_' for x in cells[len(expected):]),
         'produced canonical table or blank tail')


def bank_storage(precision,height):
    """Derived in PROOF.md, including all four caller-owned headers."""
    n=1<<height
    return 5*precision*n*(height*height+3*height+1)+n*(4*height-1)+48*precision+2*height+104


def fresh_extents(registers,precision,height):
    need(len(registers)==44 and len(set(registers))==44,'fixed scalar role inventory')
    n=1<<height
    result={role:precision+2 for role in registers}
    result.update(arena=5*precision*n*(height*height+3*height+1)+2,
                  spool=n*(2*height-1)+2,layers=(n+1)*(2*height-1)+2,rom=n+2,
                  h=precision+2,modulus=precision+2,selected_layer=precision+2,offsets=precision+3)
    need(sum(result.values())==bank_storage(precision,height),'expanded bank formula')
    return result


class ObserveROM:
    def __init__(self,rom,precision,expected):
        self.execute_original=rom.execute
        self.registers=rom.REGS
        self.precision,self.expected=precision,expected
        self.calls=[];self.identities=None;self.previous_extents=None
        self.headers=('h','modulus','selected_layer','offsets')

    def execute(self,program,tapes,max_steps):
        index=len(self.calls)
        need(index<len(self.expected),'too many producer invocations')
        expected=self.expected[index]
        ids={k:id(v) for k,v in tapes.items()}
        need(len(set(ids.values()))==len(ids),'distinct producer backing roles')
        if self.identities is None:self.identities=ids
        else:need(ids==self.identities,'same producer bank at next target')
        before={k:len(v) for k,v in tapes.items()}
        if self.previous_extents is not None:
            need(all(before[k]>=self.previous_extents[k] for k in before),'retained backing never shrinks')
        need(all(all(x=='_' for x in v) for k,v in tapes.items() if k not in self.headers),
             'blank producer reentry including old tails')
        values={k:read_header(tapes[k],self.precision,k=='offsets') for k in self.headers}
        wanted=dict(h=expected['h'],modulus=expected['modulus'],
                    selected_layer=expected['local'],offsets=expected['offset'])
        need(values==wanted,'current target header correspondence')
        header_bytes={k:tuple(tapes[k]) for k in self.headers}
        result=self.execute_original(program,tapes,max_steps=max_steps)
        need(result['status']=='accept','actual producer acceptance')
        need(all(h==0 for h in result['heads'].values()),'actual producer heads')
        need(all(tuple(tapes[k])==header_bytes[k] for k in self.headers),'producer borrowed headers')
        need(all(all(x=='_' for x in v) for k,v in tapes.items()
                 if k not in self.headers+('rom','layers')),'producer private restoration')
        table=expected['layers'][expected['local']][1]
        body(tapes['rom'],['L',*map(str,table),'R'])
        layers=['L']
        for _,table in expected['layers']:layers += [*map(str,table),'|']
        body(tapes['layers'],layers+['R'])
        after={k:len(v) for k,v in tapes.items()}
        fresh=fresh_extents(self.registers,self.precision,expected['h'])
        need(set(before)==set(fresh),'complete bank role inventory')
        need(after=={k:max(before[k],fresh[k]) for k in fresh},'exact rolewise retained extents')
        self.previous_extents=after
        self.calls.append(dict(axis=expected['axis'],headers=values,instructions=result['steps'],
                               before_extents=before,after_extents=after,
                               rom_sha256=sha256(''.join(tapes['rom']).encode()).hexdigest()))
        return result


CASES=[
    dict(name='two_short_first',moduli=[5,7,3,2],widths=[3,3,2,2],state=[1,5,2,1],row=0),
    dict(name='two_short_distinct_offsets',moduli=[5,7,3,2],widths=[3,3,2,2],state=[3,2,1,1],row=4),
    dict(name='shrinking_bank',moduli=[2,5,7,3],widths=[2,3,3,2],state=[1,4,7,3],row=4),
    dict(name='growing_bank',moduli=[2,5,3,7],widths=[2,3,2,3],state=[1,4,3,7],row=4),
    dict(name='leading_idle',moduli=[2,5,3,7],widths=[2,3,2,3],state=[1,4,3,7],row=2),
    dict(name='trailing_idle',moduli=[2,5,7,3],widths=[2,3,3,2],state=[1,4,7,3],row=2),
    dict(name='invalid_left',moduli=[5,7,3,2],widths=[3,3,2,2],state=[5,5,3,1],row=4),
    dict(name='all_idle',moduli=[5,7,3,2],widths=[3,3,2,2],state=[1,5,2,1],row=2),
    dict(name='nonroot_minimum_guide',moduli=[5,7,3,2],widths=[3,3,2,2],state=[1,5,1,1],row=4,level=1,start=2),
]
for _case in CASES:
    _case.setdefault('ell',3);_case.setdefault('level',2);_case.setdefault('start',0)


def run_case(mod,case,mutation=None,fault=None):
    w,r,e,num,row,rom,program=mod
    raw=(PACKAGE/'vendor/pr5496-join.py').read_bytes()
    if mutation:
        old,new=mutation;need(raw.count(old)==1,'unique source mutation');raw=raw.replace(old,new)
    join=load('audited_join',PACKAGE/'vendor/pr5496-join.py',raw)
    source_data=[]
    for s,h,x in zip(case['moduli'],case['widths'],case['state']):
        source_data += [r.ROOT]+[w.ONE]*h+[r.WORD_END]+bits(s,h)+[r.WORD_END]+bits(x,h)+[r.RECORD_END]
    source=port(w,e,source_data+[w.RIGHT])
    n=1<<case['level'];precision=1+sum(case['widths'][case['start']:case['start']+n])
    dirty=[port(w,e,bits((5*j+3)%(1<<precision),precision)+[w.RIGHT]) for j in range(8)]
    for j,tape in enumerate(dirty):
        for _ in range(j%3):tape.step(1)
    borrowed=[source,*dirty]
    before,initial_traffic=snapshot(borrowed),traffic(borrowed)
    lower,expected=oracle(case);active=[x for x in expected if x['active']]
    observer=ObserveROM(rom,precision,active)
    entry_cut={}
    class ObservedEntry(row.RowEntry):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            if self.context is not None:
                entry_cut['ports']=[*borrowed,*self.inputs,*self.context.owned]
                entry_cut['traffic']=traffic(entry_cut['ports'])
    proxy_row=types.SimpleNamespace(RowEntry=ObservedEntry)
    proxy_rom=types.SimpleNamespace(REGS=rom.REGS,execute=observer.execute)
    query=join.RowQuery(w,r,e,num,proxy_row,proxy_rom,program,source,dirty,
                        case['widths'],case['ell'],case['level'],case['start'],case['row'],fault)
    need(snapshot(borrowed)==before,'borrowed input bytes and heads')
    need(len(observer.calls)==len(active),'one producer call per active target')
    if not active:
        need(query.output is None and not query.ports and query.service is None,'idle no owned bank')
        query.close();need(traffic(borrowed)==initial_traffic,'idle no tape work')
        return dict(name=case['name'],idle=True,calls=[],lower=lower)
    cells,at,actual=query.output.cells,1,[]
    need(cells[0]=='L','output left marker')
    for target in expected:
        h=target['h'];need(all(x in ('0','1') for x in cells[at:at+h]),'output exact-width bits')
        actual.append(sum(int(cells[at+j])<<j for j in range(h)));at+=h
        need(cells[at]=='|','one output delimiter per target');at+=1
    need(cells[at]=='R' and all(x=='_' for x in cells[at+1:]),'output right marker and blank tail')
    need(actual==[x['output'] for x in expected],'independent micro-row endpoint')
    need(all(p.head==0 for p in query.ports),'joined returned heads')
    need({k:id(v) for k,v in query.service.items()}==observer.identities,'terminal same bank identities')
    need(all(all(x=='_' for x in v) for v in query.service.values()),'terminal complete producer disposal')
    adapter=sum(p.actions for p in query.ports)+traffic(entry_cut['ports'])-entry_cut['traffic']
    length=2+sum(3*h+4 for h in case['widths'])
    work=length+(n+1)*(precision+2)+sum(
        (2**x['h']+1)*(x['h']+1)+2**x['h']*(2*x['h']-1)+2*x['h']+4 for x in active)
    owned=[*query.entry.inputs,*query.entry.context.owned]
    before_close=sum(p.actions for p in query.ports);query.close()
    adapter+=sum(p.actions for p in query.ports)-before_close
    need(adapter<=4096*work,'adapter-only tape-action allowance')
    need(snapshot(borrowed)==before,'borrowed preservation after close')
    need(all(p.head==1 and all(x==w.BLANK for x in p.cells) for p in owned),'numerical retirement')
    need(all(p.head==0 and all(x=='_' for x in p.cells) for p in query.ports),'joined retirement including result')
    unique={id(p.cells):p.cells for p in query.ports}
    unique.update({id(v):v for v in query.service.values()})
    # Independent partition: all service roles, plus exactly three other
    # backings (coordinate, countdown and returned output). Headers and the
    # two output observers alias service backings and are counted once.
    bank_ids={id(v) for v in query.service.values()}
    extras=[p.cells for p in query.ports if id(p.cells) not in bank_ids]
    need(len(extras)==3 and len({id(v) for v in extras})==3,'three extra backings')
    bank_retained=sum(len(v) for v in query.service.values())
    extra_retained=sum(len(v) for v in extras)
    largest=max(x['h'] for x in active)
    need(bank_retained==bank_storage(precision,largest),'exact shared-bank footprint')
    need(extra_retained==2*(largest+2)+sum(x['h'] for x in expected)+len(expected)+2,
         'exact three-extra-port footprint')
    need(sum(map(len,unique.values()))==bank_retained+extra_retained,'complete backing partition')
    retained=sum(len(p.cells) for p in owned)+bank_retained+extra_retained
    return dict(name=case['name'],idle=False,lower=lower,precision=precision,
                offsets=[x['offset'] for x in expected],output=actual,calls=observer.calls,
                adapter_tape_actions=adapter,adapter_bound=4096*work,
                owned_retained_cells=retained,numerical_owned_roles=len(owned),
                producer_retained_cells=bank_retained,extra_retained_cells=extra_retained,
                expected_query_coordinates=[x['input'] for x in active])


def rejected(label,fn,text):
    try:fn()
    except ValueError as exc:
        need(text in str(exc),'wrong rejection for '+label+': '+str(exc))
        return dict(name=label,rejected_by=str(exc))
    raise AuditError('undetected control '+label)


def controls(mod,results):
    cases={x['name']:x for x in CASES};late=cases['two_short_distinct_offsets'];out=[]
    out.append(rejected('stale_zero_offset',lambda:run_case(mod,late,fault='zero_offset'),
                        'current target header correspondence'))
    out.append(rejected('wrong_local_row',lambda:run_case(mod,late,fault='wrong_local_row'),
                        'current target header correspondence'))
    padded=dict(late,name='padded_control',state=[1,5,3,1])
    out.append(rejected('suppress_padded_query',lambda:run_case(mod,padded,fault='suppress_query'),
                        'independent micro-row endpoint'))
    out.append(rejected('omit_layers_disposal',lambda:run_case(mod,late,fault='omit_layers_disposal'),
                        'blank producer reentry including old tails'))
    out.append(rejected('omit_result_retirement',lambda:run_case(mod,late,mutation=(
        b'if self.output is not None:self.output.erase()',b'if self.output is not None:pass')),
        'joined retirement including result'))
    out.append(rejected('skip_idle_offset_record',lambda:run_case(mod,cases['leading_idle'],mutation=(
        b'else:\n                skip_numeric_field(result,guide,w,records.WORD_END)',
        b'else:\n                pass')),'offset record end'))
    out.append(rejected('replace_bank_between_targets',lambda:run_case(mod,late,mutation=(
        b'run=rom_module.execute(self.program,self.service,max_steps=budget)',
        b'run=rom_module.execute(self.program,self.service if self.invocations==0 else {k:list(v) for k,v in self.service.items()},max_steps=budget)')),
        'same producer bank at next target'))
    k,targets=oracle(cases['growing_bank']);short_prefix=math.prod(cases['growing_bank']['moduli'][:2])
    wrong=k*pow(short_prefix,-1,cases['growing_bank']['moduli'][3])%cases['growing_bank']['moduli'][3]
    need(wrong!=targets[1]['offset'],'prefix omission discriminator')
    out.append(dict(name='omit_preceding_right_modulus',correct=targets[1]['offset'],wrong=wrong))
    k,_=oracle(cases['two_short_first']);raw_digits=1+5*5
    need(k!=raw_digits,'current child versus original digits discriminator')
    out.append(dict(name='treat_current_as_original_digits',correct=k,wrong=raw_digits))
    shrinking=next(x for x in results if x['name']=='shrinking_bank')
    actual=shrinking['producer_retained_cells']
    last_height=shrinking['calls'][-1]['headers']['h']
    wrong=bank_storage(shrinking['precision'],last_height)
    out.append(rejected('bill_only_final_smaller_target',
                        lambda:need(actual==wrong,'exact shared-bank footprint'),
                        'exact shared-bank footprint'))
    omitted_spool=actual-shrinking['calls'][-1]['after_extents']['spool']
    out.append(rejected('omit_retained_spool',
                        lambda:need(actual==omitted_spool,'complete bank includes spool'),
                        'complete bank includes spool'))
    need(canonical({'value':True})!=canonical({'value':1}),'typed receipt control')
    out.append(dict(name='boolean_integer_receipt_collision',rejected=True))
    return out


def oracle_checks():
    count=addresses=0
    for h in (2,3):
        for s in range(2,1<<h):
            for offset in range(s):
                perm=rotation(h,s,offset);layers=network(perm)
                for bit,table in layers:
                    need(all(table[x]==table[x^(1<<bit)] for x in range(1<<h)),'oracle switch involution')
                for x in range(1<<h):
                    y=x
                    for bit,table in layers:y^=table[y]<<bit
                    need(y==perm[x],'oracle composed rotation');addresses+=1
                count+=1
    return dict(networks=count,addresses=addresses)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true')
    parser.add_argument('--case',choices=[x['name'] for x in CASES]);args=parser.parse_args()
    sources=authenticate();calibration=oracle_checks();mod=modules();results=[]
    for case in CASES:
        if args.case is None or args.case==case['name']:
            results.append(run_case(mod,case));print('PASS_CASE',case['name'],flush=True)
    if args.case:print(json.dumps(results,indent=2));return
    negative=controls(mod,results)
    result=dict(status='PASS_CRT_MULTITARGET_ROW_AUDIT',sources=sources,oracle=calibration,
                cases=results,controls=negative,producer_calls=sum(len(x['calls']) for x in results))
    receipt=PACKAGE/'RESULT.json'
    if args.write_result:receipt.write_text(json.dumps(result,indent=2)+'\n')
    else:need(canonical(json.loads(receipt.read_text()))==canonical(result),'typed receipt drift')
    print(result['status'],'cases='+str(len(results)),'producer_calls='+str(result['producer_calls']),
          'controls='+str(len(negative)),'no_new_kappa=true')


if __name__=='__main__':main()
