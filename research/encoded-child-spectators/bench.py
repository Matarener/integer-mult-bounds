"""Meter the whole named geometry/child-extents interval, including teardown."""
from types import SimpleNamespace as NS
import time
from runtime import need,load,adapt
from powers import Powers
from tariff import predicted
LANES=('record','residue','index')


def actions(m):return [m.reads,m.writes,m.moves]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def decode(tape):
    cells=tape.cells[1:];end=cells.index(3)
    need(all(x in (0,1) for x in cells[:end]),'observer binary Count')
    return sum(v<<i for i,v in enumerate(cells[:end]))


def run(case,shared):
    env=load();w=env.words;r=env.records;registry=[]
    old_init=r.Tape.__init__
    def observed(t):old_init(t);registry.append(t)
    r.Tape.__init__=observed
    q,precision,n=case['q'],case['w'],case['n'];I=case.get('I',max(9,(2*n+128).bit_length()+1))
    L=(q**precision).bit_length()+1
    ia=w.Arena(I,128);ra=w.Arena(L,64)
    modulus=ra.literal(q**precision);ring=w.Ring(modulus)
    size,depth,first,second,width=[ia.literal(x) for x in (n,case.get('h',2),case['first'],case['second'],case['width'])]
    before,gap,suffix=[env.cardinal_counts.Count.literal(x) for x in case.get('spectators',(3,5,7))]
    spectators=(before,gap,suffix)
    extra=ra.literal(1);extra.head=2
    protected=[(obj,bytes(obj.cells),obj.head) for obj in [ia.template,ra.template]+list(ia.words)+list(ra.words)+[x.tape for x in spectators]]
    live=(set(ia.live),set(ra.live));slot_start=(len(ia.words),len(ra.words))
    prior_tapes=set(map(id,registry))
    def snapshot():
        return {'record':[sum(actions(t.meter)[k] for t in registry) for k in range(3)],
                'residue':actions(ra.meter),'index':actions(ia.meter)}
    # Measure one complete validator walk outside the compared interval.
    b=actions(ra.meter);steps=sum(1 for _ in env.cardinality.radix_power(ring,q));rho=sub(actions(ra.meter),b)
    need(steps==precision,'complete valid q-power radix witness')
    slot_start=(len(ia.words),len(ra.words))
    powers=Powers(env) if shared else None
    method=adapt(env,powers) if shared else env.layout.Layout.child_extents
    ia.meter.peak_live=len(ia.live);ra.meter.peak_live=len(ra.live)
    old_inspect=w.Word.inspect;w.Word.inspect=lambda _self:(_ for _ in ()).throw(ValueError('runtime numerical decoding forbidden'))
    baseline=snapshot();started=time.perf_counter();outputs=[];page=None;layout=None;columns=None;fields=None
    try:
        raw=w.Unsigned(ia);divisor=ia.literal(64)
        columns,remainder=raw.divmod(size,divisor);ia.free_many(divisor,remainder)
        page=env.Geometry(NS(dimension=64),ia,columns,depth,0,object())
        layout=env.layout.Layout(page,size,ring,q,*spectators)
        fields=page.plus(depth,page.one)
        outputs=method(layout,first,second,width,before=before)
        result=[decode(x.tape) for x in outputs]  # Checker observation, never runtime control.
        serialized=[bytes(x.tape.cells).hex() for x in outputs]
        need(all(x.tape.head==1 for x in outputs),'returned marginal heads')
        for x in outputs:x.close()
        outputs=[];layout.close();layout=None;page.close();page=None
        ia.free_many(columns,fields);columns=fields=None
    finally:
        w.Word.inspect=old_inspect;r.Tape.__init__=old_init
    elapsed=time.perf_counter()-started;final=snapshot()
    delta={k:sub(final[k],baseline[k]) for k in LANES}
    need(live==(set(ia.live),set(ra.live)),'all geometry numerical ownership returned')
    need(all(bytes(obj.cells)==data and obj.head==head for obj,data,head in protected),'all borrowed bytes and heads restored')
    new_tapes=[t for t in registry if id(t) not in prior_tapes]
    need(all(t.head==1 and all(v==w.BLANK for v in t.cells[1:]) for t in new_tapes),'all created record backing erased')
    need(all(word.head==1 and all(v==w.BLANK for v in word.cells[1:]) for bank in (ia,ra) for j,word in enumerate(bank.words) if j not in bank.live),'all released numerical backing erased')
    if powers:need(not powers.busy,'counter workspace released')
    f=n//64;delta_n=n-64*f
    phi=lambda x:x if x<64*f else x+2*delta_n
    a,b=phi(case['first']),phi(case['second']);c=case['width']
    exponents=[a,b-a-c,2*n-b-c]
    need(all(e>=0 for e in exponents),'valid nonnegative complete child spectators')
    B,G,S=case.get('spectators',(3,5,7));A=q**precision
    expected=[B*A**exponents[0],A**exponents[1],S*A**exponents[2]]
    region=0 if a>=n else 2 if b+c<=n else 1;expected[region]*=G
    need(result==expected,'independent actual ordered geometry values')
    need(result[0]*result[1]*result[2]*A**(2*c)==B*G*S*A**(2*n),'complete spectator/body volume with external gap exactly once')
    return {'case':case,'shared':shared,'index_width':I,'residue_width':L,'exponents':exponents,
            'radix_invoice':rho,'actions':delta,'total_actions':sum(sum(v) for v in delta.values()),
            'output_hex':serialized,'output_values':[str(v) for v in result],
            'extra_numerical_peak':{'index':ia.meter.peak_live-len(live[0]),'residue':ra.meter.peak_live-len(live[1])},
            'new_numerical_slots':{'index':len(ia.words)-slot_start[0],'residue':len(ra.words)-slot_start[1]},
            'created_record_roles':len(new_tapes),'created_record_backing':sum(len(t.cells) for t in new_tapes),
            'seconds_observation':elapsed,'borrowed_state_restored':True,'owned_backing_erased':True}


def pair(case):
    old,new=run(case,False),run(case,True)
    need(old['output_hex']==new['output_hex'],'identical complete returned serialization')
    expected=predicted(old['exponents'],old['index_width'],case['w'],old['radix_invoice'])
    actual={k:sub(old['actions'][k],new['actions'][k]) for k in LANES}
    need(all(actual[k]==list(expected[k+'_saving']) for k in LANES),'exact whole-interval independent delta')
    return {'original':old,'shared':new,'saving':actual,'predicted_delta':expected,
            'total_action_saving':old['total_actions']-new['total_actions']}
