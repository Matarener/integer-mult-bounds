# SPDX-License-Identifier: Apache-2.0
"""Literal nonchild partition and conservative signed-cost building blocks.

Chris R / Clear1nsight, substantial OpenAI Codex assistance. Jose Manuel's
physical controller and monomial implementation supply the source operations.
All inherited imports must occur after the package's authenticated cold load.
This module computes certificates; it is not an encoded runtime compiler.
"""
from collections import Counter, defaultdict, deque
from copy import copy
from fractions import Fraction
from functools import lru_cache


def need(ok, why):
    if not ok: raise ValueError(why)


def nat(n, positive=False):
    need(type(n) is int and n >= int(positive), 'exact nonnegative integer')
    return n


def operation_key(op):
    """Ignore only raw source-event index; retain roles, literal and direction."""
    return (op[0], *op[2:])


def occurrence_partition(old, new):
    """Explicit stable occurrence injection, never a rank-only histogram."""
    available=defaultdict(deque)
    for j,op in enumerate(new): available[operation_key(op)].append(j)
    paired=[]; removed=[]; used=set()
    for i,op in enumerate(old):
        key=operation_key(op)
        if available[key]:
            j=available[key].popleft();used.add(j);paired.append((i,j))
        else: removed.append(i)
    added=[j for j in range(len(new)) if j not in used]
    need(len(paired)+len(removed)==len(old) and len(paired)+len(added)==len(new),
         'disjoint complete occurrence partition')
    need(all(operation_key(old[i])==operation_key(new[j]) for i,j in paired),
         'literal matched operation')
    return paired,removed,added


def census(parent, service):
    """Audit authenticated compiled source and derive fixed recipe gate debit.

    Owner-basis words are NOT replaced by identity-owner fixtures. They are
    inventoried separately for the uniform-cover theorem.
    """
    from phase_recipe import Recipe
    vectors=tuple('v'+str(i) for i in range(parent.dimension))
    need(parent.dimension==73 and parent.families==14336,'selected source binding')
    need(parent.core.owner_specs is parent.source.owner_specs and
         parent.core.events is parent.source.events and
         parent.core.cover is parent.source.cover, 'unchanged exact core owner/group geometry')
    removed_gates=Counter();added_gates=Counter();rows={};removed_kinds=Counter()
    added_kinds=Counter();removed_scalar=Counter();added_scalar=Counter()
    removed_monomials=[]
    for direction in ('forward','backward'):
        old=parent.source.codes[direction];new=parent.core.codes[direction]
        paired,removed,added=occurrence_partition(old,new)
        need(all(old[i][0]!='monomial' or parent.source.recipes[old[i][3]]==parent.core.recipes[new[j][3]]
                 for i,j in paired), 'matched monomial literal bytes')
        for i in removed:
            op=old[i];removed_kinds[op[0]]+=1
            if op[0]=='scalar':removed_scalar[op[4]]+=1
            if op[0]=='monomial':
                literal=parent.source.recipes[op[3]]
                word=tuple(Recipe(literal,vectors).word)
                removed_gates.update(word)
                removed_monomials.append({'direction':direction,'pc':i,'role':op[2],
                    'recipe':op[3],'inverse':op[4],'gate_count':len(word)})
        for j in added:
            op=new[j];added_kinds[op[0]]+=1
            if op[0]=='scalar':added_scalar[op[4]]+=1
        rows[direction]={'old_operations':len(old),'new_operations':len(new),
            'paired_occurrences':paired,'removed_pcs':removed,'added_pcs':added}
    need(removed_kinds==Counter(monomial=32,copy=8,child=16,scalar=6,marker=2),
         'complete removed nonchild and child alphabet')
    need(removed_scalar==Counter({('add',-1,1):6}), 'six removed unit subtract dispatches')
    need(not (removed_scalar-added_scalar),'same-literal added scalar witnesses')
    # Cache only checker copies of finite cover arithmetic. Production is unchanged.
    p=copy(parent);p.cover=copy(parent.cover)
    p.cover.unrank=lru_cache(None)(parent.cover.unrank)
    p.cover.rank=lru_cache(None)(parent.cover.rank)
    s=copy(service);s.cover=p.cover
    need(tuple(p.cover.unrank(0))==tuple(1<<i for i in range(73)), 'identity-owner fixed-gate separator')
    new_monomials=0;owner_basis=0;extra_nonmap_groups=0
    for i,event in enumerate(p.events):
        if event[0]!='qq16' or event[4][0] in ('retained_core','cover_map'):continue
        group=p.group(i,0,0)
        need(bool(group.code),'emitted extra producer group')
        extra_nonmap_groups+=1
        for op in group.code:
            if op[0]!='monomial':continue
            # Each line emits owner inverse,right,left,owner forward. Identity
            # owner contributes zero gates but remains a paid monomial call.
            new_monomials+=1
            added_gates.update(Recipe(group.recipes[op[3]],vectors).word)
        owner_basis+=2*sum(op[0]=='child' for op in group.code)
    for i,event in enumerate(s.events):
        if len(event[2])==1 and event[2][0][1][0]=='map':continue
        group=s.group(i,0,0)
        for op in group.code:
            if op[0]=='monomial' and op[3] in ('right','left'):
                new_monomials+=1
                added_gates.update(Recipe(group.recipes[op[3]],vectors).word)
        owner_basis+=sum(op[0]=='monomial' and op[3]=='owner' for op in group.code)
    need(new_monomials==800 and owner_basis==736,'complete fixed and owner basis monomial census')
    from qq16_producer import order
    map_orders=Counter(order(tuple(parent.packet['map_registry'][event[4][2]]['owner_right_matrix_columns']))
                       for event in parent.events if event[0]=='qq16' and event[4][0]=='cover_map')
    map_groups=sum((Fraction(count,k) for k,count in map_orders.items()),Fraction(0))
    service_inventory=service.audit()['physical_per_cover']
    need(extra_nonmap_groups==41 and map_groups==Fraction(12286,51), 'literal candidate-only producer groups')
    expected_service={'all_gather_scatter_commit_groups':2022,
        'all_monomial_calls_including_map_translations':1696,
        'scalar_engine_calls_including_map_sign_corrections':3484,
        'map_exchanges':176,'private_zero_calls':48,'rank_one_children':336}
    need(all(service_inventory[k]==v for k,v in expected_service.items()), 'complete service invoice without doubled exchange negation')
    # 64 of the 800 measured call bases above are identity-owner placeholders;
    # their general-owner gate contribution is in the separate owner sum.
    deficits=removed_gates-added_gates
    need(sum(removed_gates.values())==736 and sum(added_gates.values())==7150,
         'literal fixed gate inventories')
    need(deficits==Counter({('add',6,8):4,('add',8,6):1}), 'exact uncovered gate geometries')
    def entries(counter):return [[list(k),v] for k,v in sorted(counter.items())]
    return {'units':'per complete cover divided by Gamma',
        'occurrence_partition':rows,'removed_kinds':dict(removed_kinds),
        'added_core_kinds':dict(added_kinds),'removed_scalars':entries(removed_scalar),
        'added_matching_scalars':entries(added_scalar),
        'removed_monomials':removed_monomials,
        'removed_gates':entries(removed_gates),'added_fixed_gates':entries(added_gates),
        'fixed_gate_deficits':entries(deficits),'owner_basis_monomials':owner_basis,
        'fixed_recipe_call_bases':800,'added_calls_after_32_base_matches':768,
        'producer_extra_nonmap_groups':extra_nonmap_groups,'producer_map_groups':str(map_groups),
        'service_source_inventory':service_inventory,
        'service_groups':2022,'service_bank_fraction':'1/32',
        'source_call_base_geometry':'same P,U,H_b,c,73 vector fields; family-bank size excluded from local monomial packet',
        'requires_owner_cover_gate_theorem':True}


def extra_gather_lower(gamma, bank_bits):
    """Candidate-only scans after exact matching of the two original core groups.

    Read and step every bank bit, then rewind. The nonnegative omitted work
    includes every Counter, selected-packet append, scatter, commit and all
    service/compiler activity. This is not diagnostic-volume subtraction.
    """
    nat(gamma,True);nat(bank_bits,True)
    need(gamma%51==0 and bank_bits%32==0,'complete cover and service-bank divisibility')
    volume=(41*gamma+12286*(gamma//51))*bank_bits+2022*gamma*(bank_bits//32)
    need(volume==Fraction(281593,816)*gamma*bank_bits,'literal added-only scan volume')
    return {'reads':2*volume,'writes':0,'moves':2*volume,
        'total':4*volume,'discarded_positive_intervals':True,
        'coefficient_total_Gamma_B':'281593/204'}


def removed_small_upper(v,L,header_bits=2685):
    """Componentwise conservative bounds for 8 copies and 16 external shells.

    L is the complete inherited Count-length envelope, not log of active width.
    The bound follows the source loop table in NONCHILD.md. Complete C bodies,
    monomial atoms, constructor/retirement and finite control are excluded.
    """
    nat(v,True);nat(L,True);nat(header_bits,True)
    need(L>=16 and header_bits==2685,'complete Count envelope and frozen B header')
    copy_bound=(1<<20)*(v+1+L**4)
    shell_bound=(1<<24)*(v+1+L**4+header_bits)
    each=8*copy_bound+16*shell_bound
    return {'copy_count':8,'shell_count':16,'copy_per_component_upper':copy_bound,
        'shell_per_component_upper':shell_bound,'rwm_upper':[each]*3,
        'total_upper':3*each,'six_unit_scalars_matched_to_identical_added_literals':True,
        'body_and_descendants_excluded':True}


def controls():
    old=[('scalar',0,1,2,('add',-1,1)),('scalar',1,1,2,('add',-1,1)),('child',2,4,8)]
    new=[('scalar',5,1,2,('add',-1,1)),('child',7,4,8)]
    paired,removed,added=occurrence_partition(old,new)
    need(paired==[(0,0),(2,1)] and removed==[1] and added==[], 'duplicate occurrence identity')
    result=extra_gather_lower(51,32)
    need(result['total']==281593*8,'exact one-cover denominator')
    rejected=[]
    for label,call in (
        ('partial cover',lambda:extra_gather_lower(1,32)),
        ('wrong service bank volume',lambda:extra_gather_lower(51,33)),
        ('Boolean multiplicity',lambda:extra_gather_lower(True,32)),
        ('negative removed upper',lambda:removed_small_upper(-1,8))):
        try:call()
        except ValueError:rejected.append(label)
        else:raise ValueError('accepted nonchild mutation:'+label)
    return {'duplicate_occurrence_control':True,'rejections':rejected}


def phase_pair_calibrations():
    """Actual four-phase source pair traffic, not a production admission test."""
    import records, signed_phase
    from cardinal_counts import Count
    from words import BLANK
    tracked=[];original=records.Tape.__init__
    def recording(tape):
        original(tape);tracked.append(tape)
    records.Tape.__init__=recording
    def meter():return tuple(sum(getattr(t.meter,k) for t in tracked) for k in ('reads','writes','moves'))
    def body(t):return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
    cases=[]
    try:
        for h in (4,8,17):
            values=(3,-2)
            raw=bytes((x>>i)&1 for x in values for i in range(h))
            for phase in range(4):
                width=Count.literal(h);source=records.Tape();target=records.Tape()
                real,imag=records.Tape(),records.Tape()
                for bit in raw:source.append(bit)
                source.rewind();before=meter()
                signed_phase.pair(source,target,width,phase,real,imag)
                actual=tuple(a-b for a,b in zip(meter(),before))
                expected=(values,(-values[1],values[0]),(-values[0],-values[1]),(values[1],-values[0]))[phase]
                encoded=bytes((x>>i)&1 for x in expected for i in range(h))
                need(body(target)==encoded,'actual signed phase endpoint')
                need(body(source)==raw and width.tape.head==1,'borrowed phase width and source bytes')
                need(not body(real) and not body(imag) and real.head==imag.head==1,'phase scratch retired')
                cases.append({'H_b':h,'phase':phase,'rwm':list(actual),'input':[3,-2]})
                source.clear();target.clear();width.close()
        for h in (4,8,17):
            need(len({tuple(x['rwm']) for x in cases if x['H_b']==h})==1,'all four actual phase action schedules')
        return {'cases':cases,'all_phases_same_actions':True,
                'scope':'actual reduced pair primitive; general phase equality follows source loop proof'}
    finally:records.Tape.__init__=original


def gather_calibrations():
    """Actual borrowed bank scan lower bounds, including all allocated Counters."""
    import records
    from bank_packets import BankPackets
    from cardinal_counts import Count
    from words import BLANK
    tracked=[];original=records.Tape.__init__
    def recording(tape):original(tape);tracked.append(tape)
    records.Tape.__init__=recording
    def meter():return tuple(sum(getattr(t.meter,k) for t in tracked) for k in ('reads','writes','moves'))
    def body(t):return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
    cases=[]
    try:
        for prefixes,unused,row_bits in ((1,1,1),(2,1,4),(1,3,5)):
            bank=BankPackets(3,2,1);counts=tuple(Count.literal(x) for x in (prefixes,unused,row_bits))
            length=prefixes*3*2*unused*row_bits
            raw=bytes((i*7+i//3)%2 for i in range(length));source=records.Tape()
            for bit in raw:source.append(bit)
            source.rewind();bank.select(((1,0),));before=meter()
            returned=bank.gather(source,*counts)
            actual=tuple(a-b for a,b in zip(meter(),before))
            need(actual[0]>=2*length and actual[2]>=2*length,'literal gathered source scan lower')
            need(body(source)==raw and source.head==1,'borrowed entire bank restored')
            segment=unused*row_bits
            expected=b''.join(raw[(p*6+2)*segment:(p*6+3)*segment] for p in range(prefixes))
            need(body(returned[0])==expected,'selected owner payload extent')
            scatter_before=meter();scattered=bank.scatter(source,*counts)
            scatter_actions=tuple(a-b for a,b in zip(meter(),scatter_before))
            need(scatter_actions[1]>=length and body(scattered)==raw, 'complete scatter output writes')
            bank.commit(source)
            need(body(source)==raw and source.head==1, 'unchanged complete group bank endpoint')
            source.clear()
            for value in counts:value.close()
            need(bank.state=='closed' and all(not body(t) for t in bank.packets),'gather roles retired')
            cases.append({'prefixes':prefixes,'unused':unused,'row_bits':row_bits,
                          'bank_bits':length,'rwm':list(actual),'lower':[2*length,0,2*length],
                          'scatter_rwm':list(scatter_actions),'scatter_write_lower':length})
        return {'cases':cases,'scope':'complete actual BankPackets.gather on reduced geometry; no selected O73 payload execution'}
    finally:records.Tape.__init__=original


def extra_group_lower(gamma, bank_bits):
    """Disjoint gather R/M and scatter-output W subset of extra group cycles."""
    result=extra_gather_lower(gamma,bank_bits)
    volume=result['reads']//2
    need(result['reads']==2*volume and result['moves']==2*volume,'even gather scan bound')
    return {'reads':2*volume,'writes':volume,'moves':2*volume,'total':5*volume,
            'coefficient_total_Gamma_B':'1407965/816',
            'intervals':['BankPackets.gather source reads and moves',
                         'BankPackets.scatter output writes'],
            'disjoint_nonnegative_source_subtraces':True}
