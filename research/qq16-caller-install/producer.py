# SPDX-License-Identifier: Apache-2.0
"""Source-bound QQ16 F0/B1 full-cover producer for the physical C dispatcher.

Inputs are authenticated decoded source objects. Control uses only the fixed
supplier alphabet, never numerical payloads or decoded input-sized descriptors.
Chris R with OpenAI Codex assistance; retained physical compiler: Jose Manuel.
"""
from collections import Counter
from copy import copy
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def act(columns, value):
    result = 0
    for i, column in enumerate(columns):
        if value >> i & 1:
            result ^= column
    return result


def multiply(left, right):
    return tuple(act(left, x) for x in right)

def transpose(matrix):
    return tuple(sum(((matrix[i]>>j)&1)<<i for i in range(len(matrix)))
                 for j in range(len(matrix)))

def row_act(rows,value):
    return sum(((row&value).bit_count()%2)<<i for i,row in enumerate(rows))

def row_multiply(left,right):
    return tuple(act(right,row) for row in left)


def order(matrix, cap=704):
    identity = tuple(1 << i for i in range(len(matrix)))
    current = identity
    for k in range(1, cap + 1):
        current = multiply(current, matrix)
        if current == identity:
            return k
    raise ValueError('owner cycle exceeds the fixed packet inventory')


def cycle(cover, index, matrix):
    """Right multiplication has equal finite order at every group owner."""
    g = cover.unrank(index)
    values = []
    for _ in range(order(matrix)):
        values.append((cover.rank(g), g))
        # Source OrthogonalCover exposes ROWS, while the QQ16 certificate
        # explicitly stores map COLUMNS. Transpose exactly once here.
        g = row_multiply(g, transpose(matrix))
    need(g == values[0][1] and len({i for i, _ in values}) == len(values),
         'complete distinct owner cycle')
    return tuple(values)


def map_group(cover, cover_index, family, record, Group, literal):
    """In-place cycle rotation followed by the literal output-owner translation.

    An actual source exchange maps (x,y) to (y,-x); scaling its second output
    by -1 makes a plain swap. Adjacent plain swaps rotate an ordered cycle left.
    Each nonleader owner emits no program; its cycle was already completed.
    """
    matrix = tuple(record['owner_right_matrix_columns'])
    delta = record['payload_translation_at_identity_owner']
    orbit = cycle(cover, cover_index, matrix)
    if cover_index != min(i for i, _ in orbit):
        return Group(((family, cover_index),), (), {})
    keys = tuple((family, i) for i, _ in orbit)
    code, recipes = [], {}
    for i in range(len(orbit)-1):
        code.extend((('exchange', -1, i, i+1),
                     ('scalar', -1, i+1, None, ('scale', -1, 1))))
    identity = tuple(1 << i for i in range(len(matrix)))
    for role, (_, owner) in enumerate(orbit):
        shift = row_act(owner, delta)
        if shift:
            key = 'producer-translation:' + str(shift)
            recipes[key] = literal(identity, shift)
            code.append(('monomial', -1, role, key, False))
    # Identity maps are allowed to have an empty program.
    return Group(keys, tuple(code), recipes)


def helper_contract(data, packet):
    """Normalized scalar replay plus complete source common-label discipline.

    Inherits every native endpoint's labelled operator refinement, including
    the original centre children. It does not replace centres by arbitrary
    outputs, or mistake unit normalized rows for physical identity operators.
    """
    evidence={}
    def slot(token):
        kind,index=token
        need(kind in ('L','C') and 0<=index<(704 if kind=='L' else 8), 'helper replay role')
        return index+(704 if kind=='C' else 0)
    for orientation in ('forward','backward'):
        original=data['programs'][orientation]
        clean=packet['core_words'][orientation]
        alphabet=('climb','adapter','residual_adapter')
        need([x for x in original if x[0] in alphabet]==[x for x in clean if x[0] in alphabet],
             'identical complete persistent native sequence')
        for label,program in (('source',original),('core',clean)):
            rows=[{i:Fraction(1)} for i in range(712)]
            frames=list(data['word']['start'])+[None]*8
            for e in program:
                if e[0]=='climb':
                    need(frames[e[2]]==e[3], 'source climb common-label input')
                    frames[e[2]]=e[4]
                elif e[0]=='center':
                    need(frames[704+e[1]]==e[2], 'source centre common-label input')
                    frames[704+e[1]]=e[3]
                elif e[0]=='scalar':
                    op,frame=e[1:];target=slot(op[1])
                    if op[0]=='clear':
                        rows[target]={};frames[target]=frame
                    elif op[0]=='copy':
                        source=slot(op[2]);need(frames[source]==frame, 'copy common label')
                        rows[target]=dict(rows[source]);frames[target]=frame
                    else:
                        need(frames[target]==frame, 'scalar target common label')
                        if op[0]=='scale':
                            c=Fraction(op[2],op[3]);rows[target]={k:v*c for k,v in rows[target].items() if v*c}
                        else:
                            need(op[0]=='add','normalized scalar alphabet')
                            source=slot(op[2]);need(frames[source]==frame, 'scalar source common label')
                            c=Fraction(op[3],op[4])
                            for k,v in rows[source].items():
                                rows[target][k]=rows[target].get(k,0)+c*v
                                if not rows[target][k]:del rows[target][k]
            need(frames[:704]==data['word']['final'], 'all final persistent common labels')
            need(all(rows[i]=={i:1} for i in range(224,704)), 'all 480 normalized helper unit rows')
            need(all(not row for row in rows[704:]), 'all eight private fields returned zero')
        evidence[orientation]={'normalized_helper_unit_rows':480,'persistent_final_labels':704,
                               'private_zero_returns':8,'persistent_native_sequences_identical':True}
    return evidence


class ProducerBinding:
    """Replace exactly source events 0 and 4; retain every other source event.

    Dependency classes are injected after source authentication. `global_fence`
    is the last B macro index, tested after finish_group at cover_index=Gamma.
    This is a binding for the source machine, not a new refinement theorem for
    every recursive use of a modified supplier. Recursive child calls must use
    the separate original endpoint required by the caller installation.
    """
    def __init__(self, data, packet, SelectedBinding, Group, compile_local,
                 embed, literal, ScalarProgram):
        self.source = SelectedBinding(data)
        self.core = copy(self.source)
        core_data = dict(data, programs=packet['core_words'])
        self.core.codes, self.core.recipes = {}, {}
        for direction in ('forward', 'backward'):
            code, recipes, _ = compile_local(core_data, direction)
            self.core.codes[direction] = code
            self.core.recipes.update({k: embed(v, 73) for k, v in recipes.items()})
        self.helper_evidence=helper_contract(data,packet)
        self.packet, self.Group, self.literal, self.embed = packet, Group, literal, embed
        for name in ('dimension','maximum_rank','families','slots','private','cover'):
            setattr(self, name, getattr(self.source, name))
        self.events, self.source_events = [], {}
        for i, event in enumerate(self.source.events):
            if i in (0, 4):
                stage, direction, case = (0, 'forward', 'F_0') if i == 0 else (1, 'backward', 'B_1_2')
                call = self.source.calls[event['time']]
                need((event['replica'],event['stage'],call['orientation']) == (0,stage,direction),
                     'actual first producer pair')
                need([o.family for o in self.source.owner_specs[event['time']][:224]] == list(range(224)),
                     'literal first-pair physical data families')
                for macro_index, macro in enumerate(packet['programs'][case]):
                    self.events.append(('qq16', i, case, macro_index, macro))
                if i == 4:
                    self.global_fence = len(self.events)-1
            else:
                self.source_events[i] = len(self.events)
                self.events.append(('source', i))
        self.events = tuple(self.events)
        keys = set()
        for program in (*data['programs'].values(), *packet['core_words'].values()):
            for e in program:
                if e[0] == 'scalar' and e[1][0] in ('add','scale'):
                    op=e[1]; j=3 if op[0]=='add' else 2; c=Fraction(op[j],op[j+1]);keys.add((op[0],c.numerator,c.denominator))
        for case in ('F_0','B_1_2'):
            for macro in packet['programs'][case]:
                body=macro[2] if macro[0] in ('cover_sweep','private_sweep') else [macro]
                for e in body:
                    if e[0]=='scalar' and e[1][0] in ('add','scale'):
                        op=e[1];j=3 if op[0]=='add' else 2;c=Fraction(op[j],op[j+1]);keys.add((op[0],c.numerator,c.denominator))
        keys.add(('scale',-1,1))
        self.catalogue={key:ScalarProgram(*key) for key in keys}

    def group_count(self, event_index):
        e=self.events[event_index]
        return self.source.group_count(e[1]) if e[0]=='source' else 1

    def group(self, event_index, subgroup, cover_index):
        e=self.events[event_index]
        if e[0]=='source':
            return self.source.group(e[1],subgroup,cover_index)
        need(subgroup==0,'one complete cover per QQ16 barrier')
        _,source_index,case,macro_index,macro=e
        if macro[0]=='retained_core':
            need(macro[1]==('forward' if source_index==0 else 'backward'), 'retained core orientation')
            return self.core.group(source_index,0,cover_index)
        if macro[0]=='cover_map':
            need(macro[1][0]=='L' and 0<=macro[1][1]<224, 'map of actual producer data family')
            return map_group(self.cover,cover_index,macro[1][1],self.packet['map_registry'][macro[2]],self.Group,self.literal)
        g=self.cover.unrank(cover_index)
        keys=tuple((family,cover_index) for family in range(224))
        code, recipes=[],{}
        def role(token):
            typ,i=token
            need(type(i) is int and ((typ=='L' and 0<=i<224) or (typ=='C' and 0<=i<8)), 'outer producer role')
            return i if typ=='L' else self.slots+i
        def mono(target, record, inverse=False):
            key='producer:'+sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            recipes[key]=record;code.append(('monomial',macro_index,target,key,inverse))
        body=macro[2] if macro[0] in ('cover_sweep','private_sweep') else [macro]
        for event in body:
            if event[0]=='scalar':
                op=event[1]; target=role(op[1])
                if op[0]=='clear':
                    need(target>=self.slots,'private producer CLEAR');code.append(('zero',macro_index,target))
                elif op[0]=='copy':
                    need(target>=self.slots,'private producer COPY');code.append(('copy',macro_index,target,role(op[2])))
                else:
                    need(op[0] in ('add','scale'),'producer scalar opcode')
                    j=3 if op[0]=='add' else 2;c=Fraction(op[j],op[j+1]); key=(op[0],c.numerator,c.denominator)
                    need(key in self.catalogue,'paid producer scalar catalogue')
                    code.append(('scalar',macro_index,target,role(op[2]) if op[0]=='add' else None,key))
            else:
                need(event[0]=='native_line','complete producer macro alphabet')
                target=role(event[1]);native=self.packet['native_line_recipes'][event[2]]
                need(native['rank']==1,'literal producer rank-one call')
                mono(target,self.literal(g),True)
                mono(target,self.embed(native['recipe']['right'],self.dimension))
                code.append(('child',macro_index,target,1))
                mono(target,self.embed(native['recipe']['left'],self.dimension))
                mono(target,self.literal(g))
        need(len(code)<65536,'source finite PC width')
        return self.Group(keys,tuple(code),recipes)

    def height_programs(self):
        """One body per touched family/owner path; permutations have height zero.

        Distinct-family selected owner charts make each core group partition
        its touched fields, so looping Gamma does not multiply the height.
        Include all three unchanged intervening source cores conservatively.
        Omit only outer owner-view monomials, whose height and debt are zero;
        their physical actions remain in the separate full-group invoice.
        """
        result=[]
        for i,event in enumerate(self.events):
            if event[0]=='source':
                if event[1] in (1,2,3):
                    call=self.source.calls[self.source.events[event[1]]['time']]
                    result.append(self.source.codes[call['orientation']])
            elif event[4][0]=='retained_core':
                result.append(self.core.codes[event[4][1]])
            elif event[4][0]!='cover_map':
                result.append(self.group(i,0,0).code)
        need(len(result)==46, 'complete aggregate producer interval height bodies')
        return tuple(result)

    def root_child_census(self):
        """Count every root child instruction, including the unmodified suffix.

        Local owner views contain no child instruction, so their cached compiled
        bodies give the exact multiplicity. Idle groups have one child iff their
        literal remainder exists; reconstruct its checked active suffix for
        every finite subgroup. Counts do not depend on the cover owner.
        """
        source=self.source
        local={direction:Counter(op[3] for op in code if op[0]=='child')
               for direction,code in source.codes.items()}
        core={direction:Counter(op[3] for op in code if op[0]=='child')
              for direction,code in self.core.codes.items()}
        per_event=[];idle_samples={};kinds=Counter()
        no_children={'bridge','terminal','terminal_Y_translations',
                     'bank_padding_cover_sweep','translate_every_live_family'}
        for index,event in enumerate(source.events):
            kind=event['kind'];kinds[kind]+=1;hist=Counter()
            if kind=='local_cover_sweep':
                need(source.group_count(index)==1,'one local core per cover owner')
                hist.update(local[source.calls[event['time']]['orientation']])
            elif kind=='idle_cover_sweep':
                need(source.group_count(index)==224,'complete two-side idle port census')
                for subgroup in range(224):
                    side,port=divmod(subgroup,112)
                    child=event['child_indices'][side]
                    remainder=source.remainders.get((event['replica'],child,port))
                    if remainder:
                        family=896*event['replica']+(2*event['pair']+side)*112+port
                        axes=source.data['phases']['recipes'][port]['idle_children'][child]['orthogonal_axes']
                        active=tuple(axes[remainder['pending_offset']:])
                        need(remainder['family']==family and len(active)==remainder['rank'],
                             'actual idle child family and pending suffix')
                        hist[len(active)]+=1
                        idle_samples.setdefault(len(active),(index,subgroup))
            else:
                need(kind in no_children,'complete source child-emitting event alphabet')
            per_event.append(hist)
        # Check the exact dispatcher instructions for each admitted idle rank;
        # the full finite subgroup census above checks every remainder instance.
        sampled=copy(source);sampled.cover=copy(source.cover)
        sampled.cover.unrank=lru_cache(maxsize=1)(source.cover.unrank)
        for rank,(index,subgroup) in idle_samples.items():
            actual=Counter(op[3] for op in sampled.group(index,subgroup,0).code if op[0]=='child')
            need(actual==Counter({rank:1}),'actual idle dispatcher rank witness')
        def total(indices):
            answer=Counter()
            for index in indices:answer.update(per_event[index])
            return answer
        original_pair=total((0,4));retained_core=core['forward']+core['backward']
        outer=Counter()
        for event in self.events:
            if event[0]!='qq16':continue
            macro=event[4]
            if macro[0] in ('cover_map','retained_core'):continue
            body=macro[2] if macro[0] in ('cover_sweep','private_sweep') else [macro]
            for op in body:
                if op[0]=='native_line':
                    outer[self.packet['native_line_recipes'][op[2]]['rank']]+=1
        removed=original_pair-retained_core
        need(removed==Counter({8:16}) and retained_core-original_pair==Counter()
             and outer==Counter({1:32}),'exact replaced centres and new producer lines')
        intervening=total((1,2,3));idle=per_event[5];bridge=per_event[6]
        baseline_prefix=total(range(7))
        installed_prefix=retained_core+outer+intervening+idle+bridge
        suffix=total(range(7,len(per_event)))
        baseline=baseline_prefix+suffix;installed=installed_prefix+suffix
        need(baseline-removed+outer==installed,'whole-root native count conservation')
        def record(hist):
            return {'rank_counts':dict(sorted(hist.items())),
                    'calls':sum(hist.values()),
                    'rank_mass':sum(rank*count for rank,count in hist.items())}
        return {'units':'root child invocations per Gamma; service children separate',
                'baseline_events':len(source.events),'installed_events':len(self.events),
                'source_event_kinds':dict(sorted(kinds.items())),
                'original_pair_0_4':record(original_pair),
                'clean_retained_pair_cores':record(retained_core),
                'qq16_added_lines':record(outer),
                'intervening_source_1_3':record(intervening),
                'idle_source_5':record(idle),'bridge_source_6':record(bridge),
                'baseline_entry_through_bridge':record(baseline_prefix),
                'installed_entry_through_bridge':record(installed_prefix),
                'retained_later_source_7_481':record(suffix),
                'baseline_whole_root':record(baseline),
                'installed_whole_root':record(installed),
                'removed_centres':record(removed),
                'idle_rank_dispatch_witnesses':len(idle_samples),
                'protocol_scope':'Every installed root child uses external-child transfer; same rank does not cancel differing parent protocols or packet contexts.'}

    def audit(self):
        # Checker-only memoization of the exact fixed cover value. It changes
        # neither the runtime binding nor the source finite-control answers.
        audit_source=copy(self.source)
        audit_source.cover=copy(self.source.cover)
        audit_source.cover.unrank=lru_cache(maxsize=1)(self.source.cover.unrank)
        overlap={}
        for source_index in (1,2,3):
            event=self.source.events[source_index]
            owner_families={o.family for o in self.source.owner_specs[event['time']]}
            overlap[source_index]=sorted(owner_families & set(range(224)))
            need(not overlap[source_index], 'intervening source event touches changed pair0 data')
        for port in range(112):
            g=audit_source.group(6,port,0)
            need(g.keys==((port,0),(224+port,0),(336+port,0),(112+port,0)),
                 'both literal bridge legs use immutable original ports')
            need(g.code==(('scalar',-1,0,1,('add',1,1)),
                          ('scalar',-1,2,3,('add',-1,1))), 'both signed bridge instructions')
            for side in range(2):
                g=audit_source.group(5,112*side+port,0)
                need(all(family>=224 for family,_ in g.keys), 'idle pair1 excludes changed pair0')
        orders=Counter(); outer=Counter(); nonmap=0; translated=0
        for event in self.events:
            if event[0]=='qq16' and event[4][0]!='cover_map':
                nonmap+=1
                macro=event[4]
                if macro[0]!='retained_core':
                    for x in macro[2] if macro[0] in ('cover_sweep','private_sweep') else [macro]:
                        outer[x[0]+(':'+x[1][0] if x[0]=='scalar' else '')]+=1
            if event[0]=='qq16' and event[4][0]=='cover_map':
                record=self.packet['map_registry'][event[4][2]]
                orders[order(tuple(record['owner_right_matrix_columns']))]+=1
                translated+=bool(record['payload_translation_at_identity_owner'])
        need(orders==Counter({2:464,5:24,12:20,6:12,20:4,17:4}), 'complete literal 528 map orders')
        need(nonmap==43 and translated==528 and outer==Counter({'scalar:add':2200,'scalar:clear':32,'scalar:scale':16,'native_line':32}), 'complete literal producer outer invoice')
        need(self.source_events[5]==self.global_fence+1 and self.source_events[6]==self.global_fence+2,
             'idle and bridge immediately follow global acquisition fence')
        return {'status':'PASS_SOURCE_BOUND_PRODUCER_PLAN','expanded_events':len(self.events),
                'global_fence_last_event':self.global_fence,'source_events_retained':len(self.source_events),
                'helper_endpoint_common_label_checks':self.helper_evidence,
                'root_child_census':self.root_child_census(),
                'outer_macro_counts':dict(sorted(outer.items())),
                'nonmap_groups_per_cover':nonmap,'translated_map_calls_per_cover':translated,
                'map_groups_per_cover':str(sum(Fraction(c,k) for k,c in orders.items())),
                'plain_swaps_per_cover':str(sum(Fraction(c*(k-1),k) for k,c in orders.items())),
                'map_owner_control_visits_per_cover':sum(orders.values()),
                'intervening_pair0_owner_intersections':overlap,
                'both_bridge_legs_bound':112,'idle_groups_exclude_pair0':224,
                'map_orders':dict(sorted(orders.items())), 'maximum_map_packet_slots':max(orders),
                'scope':'Finite control and operator lowering; separate original recursive native endpoint required. No production payload execution.'}


def machine_class(Machine, Count, transfer, erase_marker):
    """Adapt only the child boundary and the one completed global fence.

    `native_child` is a distinct, original-binding closed Machine. Its output
    is consumed before the next call. The parent's packet groups are never
    passed to this child; only prepare_child's owned capsule is borrowed.
    `at_fence` is an optional installed continuation, called once at the bank-
    closed global fence, with the parent scratch scope suspended.
    """
    class ProducerMachine(Machine):
        def __init__(self, binding, native, catalogue, native_child, at_fence=None, observe=None):
            super().__init__(binding,native,catalogue,observe)
            need(native_child is not self and native_child.closed,
                 'separate closed original native child engine')
            need(native_child.binding is not binding and
                 not isinstance(native_child.binding,ProducerBinding),
                 'retain original recursive endpoint rather than reentering QQ16 producer')
            self.native_child=native_child
            self.at_fence=at_fence
            self.fence_calls=0

        def run(self, payload, descriptors):
            need(self.closed and self.native_child.closed, 'closed producer and native engines')
            self.fence_calls=0
            return super().run(payload,descriptors)

        def enter_child(self):
            need(self.scope.manager is None, 'source run exits parent allocation scope before child entry')
            self.primitive_boundary()
            root,event,subgroup,cover_index,next_pc,target,rank=self.header.read(self.roles['header'])
            need((bool(root),event,subgroup,cover_index,next_pc)==
                 (self.root,self.event,self.subgroup,self.cover_index,self.pc+1),
                 'prepared child belongs to exact current producer instruction')
            need(self.group.code[self.pc][0]=='child' and self.group.code[self.pc][2:]==(target,rank),
                 'literal prepared child target and rank')
            descriptors={}
            for name in self.capsule:
                if name!='current':
                    c=object.__new__(Count);c.tape=self.capsule[name];descriptors[name]=c
            result=self.native_child.run(self.capsule['current'],descriptors)
            transfer(result,self.packet(target));erase_marker(result)
            for tape in self.capsule.values():
                tape.clear()
            self.roles['header'].clear()
            self.pc=next_pc
            if self.observe:
                self.observe(self,'external-child-return')

        def finish_group(self):
            super().finish_group()
            if (self.root and self.event==self.binding.global_fence and
                    self.subgroup==0 and self.cover_index==self.binding.cover.size):
                need(self.group is None and self.pc==0 and self.bank.state=='closed',
                     'completed global producer fence')
                self.primitive_boundary()
                need(self.fence_calls==0,'single producer continuation fence')
                self.fence_calls+=1
                if self.at_fence is not None:
                    with self.scope.suspended():
                        self.at_fence(self)
                self.primitive_boundary()
    return ProducerMachine
