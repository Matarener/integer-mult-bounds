#!/usr/bin/env python3
"""Independent exact signed-owner phase primitive and native lowering.

Reads authenticated data, not the producer's owner/phase routines. The
noncommuting controller is separately replayed from its serialized events.
This certifies reusable primitives, not a completed H supplier.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
KAPPA=HERE.parents[1]
ARCH=KAPPA/'architecture'
DIM=73
AXES=[1<<i for i in range(DIM)]


def need(value,message):
    if not value:
        raise AssertionError(message)


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def act(columns,value):
    out=0
    while value:
        bit=value&-value;out^=columns[bit.bit_length()-1];value^=bit
    return out


def native_owner(recipe,stage):
    basis=recipe['idle_children'][0]['orthogonal_axes'][:8]
    swaps=[axis^(1<<(9+8*(stage-1)+j)) for j,axis in enumerate(basis)]
    columns=[]
    for axis in AXES:
        out=axis
        for vector in swaps:
            if (axis&vector).bit_count()&1:
                out^=vector
        columns.append(out)
    return columns


def lower_owner(columns,support):
    positions=[j for j in range(DIM) if support>>j&1]
    rows=[sum(((columns[j]>>i)&1)<<k for k,j in enumerate(positions)) for i in positions]
    original=list(rows);reduction=[]
    for j in range(len(rows)):
        pivot=next(i for i in range(j,len(rows)) if rows[i]>>j&1)
        if pivot!=j:
            rows[j],rows[pivot]=rows[pivot],rows[j]
            reduction.append(['SWAP_BITS',positions[j],positions[pivot]])
        for i in range(len(rows)):
            if i!=j and rows[i]>>j&1:
                rows[i]^=rows[j]
                reduction.append(['XOR_BIT',positions[i],positions[j]])
    need(rows==[1<<i for i in range(len(rows))],'Complete finite binary elimination')
    gates=list(reversed(reduction));replayed=[1<<i for i in range(len(rows))]
    index={v:i for i,v in enumerate(positions)}
    for kind,d,s in gates:
        a,b=index[d],index[s]
        if kind=='XOR_BIT':
            replayed[a]^=replayed[b]
        else:
            replayed[a],replayed[b]=replayed[b],replayed[a]
    need(replayed==original,'Literal native address-gate program realizes the declared owner')
    return gates


def add(a,b,scale=1):
    out=dict(a)
    for word,value in b.items():
        out[word]=out.get(word,F(0))+scale*value
        if not out[word]:
            del out[word]
    return out


def scalar_product(a,b,left):
    out=[[{} for _ in range(6)] for _ in range(6)]
    for i in range(6):
        for j in range(6):
            for k in range(6):
                polynomial,coefficient=(b[k][j],a[i][k]) if left else (a[i][k],b[k][j])
                out[i][j]=add(out[i][j],polynomial,coefficient)
    return out


def controller_check(probe):
    source=read(KAPPA/'bit/COMPLEX-CONTROLLER-FACTOR.json')['selected_p3_keep43']
    m=[[{():F(1)} if i==j else {} for j in range(6)] for i in range(6)]
    for event in source['physical_events']:
        kind=event[0]
        if kind=='LOCAL':
            _,stage,pair,back=event;a,b=2*pair,2*pair+1
            dst,src,sign=(a,b,-1) if back else (b,a,1)
            m[dst]=[add(x,y,sign) for x,y in zip(m[dst],m[src])]
            for role in (a,b):
                m[role]=[{(stage,)+word:value for word,value in cell.items()} for cell in m[role]]
        elif kind=='IDLE':
            _,pair,stages=event
            for stage in stages:
                for role in (2*pair,2*pair+1):
                    m[role]=[{(stage,)+word:value for word,value in cell.items()} for cell in m[role]]
        elif kind=='ADD':
            _,d,s,c=event;m[d]=[add(x,y,F(c)) for x,y in zip(m[d],m[s])]
        else:
            need(kind=='SIGNED_SWAP','Known literal controller event')
            _,a,b=event;m[a],m[b]=m[b],[{w:-v for w,v in cell.items()} for cell in m[a]]
    left=[[F(x) for x in row] for row in probe['left']]
    right=[[F(x) for x in row] for row in probe['right']]
    m=scalar_product(scalar_product(left,m,True),right,False)
    words=[tuple(w) for w in probe['diagonal_words']]
    need(m==[[{words[i]:F(1)} if i==j else {} for j in range(6)] for i in range(6)],
         'All36 free noncommuting entries of the serialized p3 controller')
    need(len(set(words))==3,'Three independently needed interval monodromies')
    return {'exact_free_polynomial_entries':36,'diagonal_words':[list(w) for w in words],
            'distinct_interval_words':3,
            'scope':'Stage multipliers are arbitrary; this algebraic identity does not remove physical Q gauges or prove a shared paid boundary.'}


def main():
    proposal_path=ARCH/'AGGREGATE-H-PROBE.json';proposal=read(proposal_path)
    for name,expected in proposal['source_sha256'].items():
        need(digest(ROOT/name)==expected,'Exact proposal source binding '+name)
    phase_path=ROOT/'research/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
    phases=read(phase_path)
    need(digest(phase_path)==proposal['native_source_pins']['DATA-PHASES.json'],'Exact retained native phase data')
    need(len(phases['recipes'])==112 and phases['m']==73,'Actual native ports and ambient dimension')
    records=[];bare_failures=0;weights=Counter();counts=Counter();total_tests=0
    for item in proposal['phase_lifts']['records']:
        stage,port=item['stage'],item['port'];recipe=phases['recipes'][port]
        need(1<=stage<=8,'Known fresh-stage embedding')
        columns=native_owner(recipe,stage)
        need(columns==item['owner_columns'],'Owner reconstructed independently from actual orthogonal-complement axes')
        fresh_positions=list(range(9+8*(stage-1),9+8*stage))
        active=list(range(9))+fresh_positions
        support=sum(1<<j for j in active);old=(1<<9)-1;fresh=support^old;q=recipe['q']
        need(all(columns[j]==AXES[j] for j in range(DIM) if not support>>j&1),
             'All external spectator coordinates fixed')
        need(all(not columns[j]&~support for j in active),'No hidden support outside the seventeen active axes')
        need([act(columns,column) for column in columns]==AXES,'Exact native owner involution on all73 columns')
        transposed=[sum(((columns[j]>>i)&1)<<j for j in range(DIM)) for i in range(DIM)]
        need(transposed==columns,'Actual owner is symmetric and orthogonal, fixing Fourier convention')
        need(act(columns,q)==q,'Every owner fixes its exact native port normal')
        delta=[(1-(columns[j]&support).bit_count())%4 if j in active else 0 for j in range(DIM)]
        need(all(x in (0,2) for x in delta),'Full Gaussian discrepancy is an even linear phase')
        d=sum((x//2)<<j for j,x in enumerate(delta))
        need(d==item['character_mask'] and d.bit_count() in (4,8),'Independent Pauli character correction')
        need(act(columns,d)==d and not (d&q).bit_count()%2,'Character is fixed by owner and orthogonal to q')
        gates=lower_owner(columns,support);gate_counts=Counter(g[0] for g in gates)
        weights[d.bit_count()]+=1;counts.update(gate_counts)
        tests=[0]+[1<<j for j in active]+[(1<<i)^(1<<j) for x,i in enumerate(active) for j in active[x+1:]]
        bare_witness=None
        for y in tests:
            gy=act(columns,y);z=gy^d
            need(act(columns,z)^d==y,'Signed affine Fourier owner is exactly involutive')
            need((z&support).bit_count()%4==(y&support).bit_count()%4,'Absolute full Gaussian phase is preserved')
            need((z&q).bit_count()%2==(y&q).bit_count()%2,'Absolute q-line Gaussian phase is preserved')
            need(((z&old).bit_count()+((z&q).bit_count()%2))%4==(1+(y&fresh).bit_count())%4,
                 'Old F9*Cq hole conjugates to exactly i times fresh8')
            if bare_witness is None and (gy&support).bit_count()%4!=(y&support).bit_count()%4:
                bare_witness=y
        need(bare_witness is not None,'Bare owner fails absolute phase; character correction is necessary')
        bare_failures+=1;total_tests+=len(tests)
        records.append({'stage':stage,'port':port,'q':q,'character_mask':d,
                        'character_weight':d.bit_count(),'native_address_gates':gates,
                        'native_address_gate_counts':dict(gate_counts),
                        'physical_character':'multiply coefficient at x by (-1)^parity(d & x)',
                        'physical_operator_order':'G then Z_d; they commute because Gd=d',
                        'Fourier_affine_map':'y -> G*y+d = G*(y+d)',
                        'absolute_constant_Z4':0,'old_hole_to_fresh_constant_Z4':1,
                        'bare_owner_counterexample_frequency':bare_witness})
    need(len(records)==896 and len({(r['stage'],r['port']) for r in records})==896,
         'Every one of eight stages times112 native ports')
    controller=controller_check(proposal['noncommuting_p3'])
    sources=[Path(__file__),proposal_path,ARCH/'aggregate_h_probe.py',phase_path,
             KAPPA/'bit/COMPLEX-CONTROLLER-FACTOR.json']
    result={'schema':'independent-signed-owner-phase-and-lowering-audit/1',
            'status':'PASS_ALL896_EXACT_SIGNED_OWNER_LIFTS_AND_NATIVE_BINARY_LOWERING',
            'sources_sha256':{str(path.relative_to(ROOT)):digest(path) for path in sources},
            'checked_recipes':len(records),'complete_quadratic_test_points':total_tests,
            'character_weights':dict(weights),'native_address_gate_totals':dict(counts),
            'bare_absolute_phase_negative_controls':bare_failures,
            'universal_proof':'A Z4 parity sum has degree at most two; evaluations at0,basis vectors,and basis pairs determine every coefficient. Each map fixes every other coordinate.',
            'all_column_lift':'Apply this signed monomial independently per column. Every displayed identity remains exact; the hole-to-fresh scalar becomes i^f and must be charged as an explicit scalar phase.',
            'native_cost_contract':'Finite XOR-bit and SWAP-bit recipes plus one coefficient-character pass; no recursive Fourier request. Their actual compact movement and scalar costs must be added when surrounding a native word.',
            'records':records,'noncommuting_controller':controller,
            'not_proved':['Actual whole native H-word contacts after replacing owners.',
                          'Closure of the three distinct Q-conjugated interval monodromies.',
                          'A224-H1 shared correction instead of the direct672-H1 correction.',
                          'Any new complete kappa claim.']}
    out=HERE/'GAMMA-PHASE-AUDIT.json';out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:result[key] for key in ('status','checked_recipes','complete_quadratic_test_points','character_weights','native_address_gate_totals')}))


if __name__=='__main__':
    main()
