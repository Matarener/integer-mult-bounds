# SPDX-License-Identifier: Apache-2.0
"""Finite full-cover D/current-return compiler and encoded service-bank join.

Chris R with OpenAI Codex assistance. Physical primitives and original recursive
C retain Jose Manuel's source/refinement credit. Authenticate dependencies first.
"""
from collections import Counter
from fractions import Fraction
from copy import copy
from functools import lru_cache
from hashlib import sha256
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


class DecoderBinding:
    """Every event is a complete cover barrier; private words stay per owner.

    The binding has no access to payloads or encoded input sizes. Signed line
    recipes and owner maps are finite authenticated compilation constants.
    The service must dispatch child capsules to a separate ORIGINAL C Machine.
    """
    maximum_rank = 1
    private = 16

    def __init__(self, word, phases, maps, cover, Group, literal, ScalarProgram,
                 signed_recipe, map_group, order, ports=112, dimension=73,
                 continuation=True):
        self.dimension, self.ports, self.families = dimension, ports, 4*ports
        self.cover, self.Group, self.literal = cover, Group, literal
        self.signed_recipe, self.map_group = signed_recipe, map_group
        self.map_order = order
        self.maps = maps
        self.labels = tuple(r['q'] for r in phases['recipes'])
        need(len(self.labels) == ports, 'complete finite port labels')
        self.slots = max([4*ports] + [order(tuple(m['owner_right_matrix_columns'])) for m in maps.values()])
        need(self.slots <= self.families*cover.size, 'finite group slots fit service bank')
        self.catalogue = {k: ScalarProgram(*k) for k in
                          [('scale', 0, 1), ('scale', -1, 1)] +
                          [('add', n, d) for n,d in ((1,1),(-1,1),(1,4),(-1,4))]}
        self.word = tuple(tuple(e) for e in word)
        events, block = [], None
        for i, raw in enumerate(word):
            e = tuple(raw)
            if e[0] == 'begin':
                need(block is None and e[2] in (8,16), 'non-nested finite private word')
                block = [i, e[1], e[2], []]
            elif e[0] == 'end':
                need(block is not None and tuple(e[1:]) == tuple(block[1:3]), 'matching private end')
                events.append(('private', block[0], tuple(block[3]), block[2]))
                block = None
            elif block is not None:
                need(e[0] in ('clear','add'), 'private scope contains only scalar operations')
                block[3].append((i,e))
            elif e[0] == 'checkpoint':
                events.append(('checkpoint', i, (), 0))
            else:
                need(e[0] in ('clear','add','line','map'), 'complete decoder grammar')
                events.append(('public', i, ((i,e),), 0))
        need(block is None, 'closed decoder private scope')
        self.decoder_events = len(events)
        if continuation:
            for p in range(ports):
                events.append(('public',len(word)+p,((len(word)+p,('add','W'+str(p),'Z'+str(p),'1')),),0))
            for p in range(ports):
                events.append(('public',len(word)+ports+p,((len(word)+ports+p,('add','Z'+str(p),'W'+str(p),'-1')),),0))
            for p in range(ports):
                events.append(('public',len(word)+2*ports+p,((len(word)+2*ports+p,('line','W'+str(p),p,-1)),),0))
        self.events = tuple(events)
        # No producer fence is part of this service. The shared child adapter's
        # fence hook is disabled by an unreachable finite event value.
        self.global_fence = len(events)
        for event in self.events:
            for _,e in event[2]:
                if e[0] in ('clear','add','line','map'):
                    need(e[1][0] in ('Z','W','F','G'), 'borrowed X/Y are immutable')

    def family(self, name):
        need(type(name) is str and name[0] in 'XYZW' and name[1:].isdigit(), 'persistent role')
        p=int(name[1:]); need(0 <= p < self.ports, 'persistent port')
        return 'XYZW'.index(name[0])*self.ports+p

    def group_count(self, event):
        need(0 <= event < len(self.events), 'finite decoder event')
        return 1

    def group(self, event, subgroup, owner):
        need(subgroup == 0, 'complete cover before next decoder event')
        kind,index,body,private = self.events[event]
        if kind == 'checkpoint':
            return self.Group(((0,owner),), (), {})
        if len(body)==1 and body[0][1][0]=='map':
            e=body[0][1]
            return self.map_group(self.cover,owner,self.family(e[1]),
                                  self.maps[(e[2],e[3],e[4])],self.Group,self.literal)
        names=[]
        for _,e in body:
            for name in (e[1:3] if e[0]=='add' else e[1:2]):
                if name[0] in 'XYZW' and name not in names: names.append(name)
        need(names and len(names)<=self.slots, 'gathered persistent decoder roles')
        keys=tuple((self.family(name),owner) for name in names)
        def role(name):
            if name[0] in 'XYZW': return names.index(name)
            need(name[0] in 'FG' and name[1:].isdigit(), 'private role alphabet')
            r=int(name[1:])+(8 if name[0]=='G' else 0)
            need(0 <= r < private, 'private role within current generation')
            return self.slots+r
        code=[]; recipes={}
        for occurrence,e in body:
            target=role(e[1])
            if e[0]=='clear':
                code.append(('zero',occurrence,target) if target>=self.slots else
                            ('scalar',occurrence,target,None,('scale',0,1)))
            elif e[0]=='add':
                c=Fraction(e[3]);key=('add',c.numerator,c.denominator)
                need(key in self.catalogue and target!=role(e[2]), 'paid scalar literal and distinct ports')
                code.append(('scalar',occurrence,target,role(e[2]),key))
            else:
                need(e[0]=='line' and private==0 and e[3] in (-1,1), 'native outside private word')
                q=self.labels[e[2]]; pair=self.signed_recipe(q,e[3],self.dimension)
                g=self.literal(self.cover.unrank(owner))
                recipes.update({'owner':g,'right':pair['right'],'left':pair['left']})
                code.extend((('monomial',occurrence,target,'owner',True),
                             ('monomial',occurrence,target,'right',False),
                             ('child',occurrence,target,1),
                             ('monomial',occurrence,target,'left',False),
                             ('monomial',occurrence,target,'owner',False)))
        need(len(code)<65536, 'finite service program counter')
        return self.Group(keys,tuple(code),recipes)

    def audit(self):
        # Checker-only memoization of exact finite geometry. The production
        # binding/cover and its charged runtime instructions remain unchanged.
        audit_binding=copy(self)
        audit_binding.cover=copy(self.cover)
        audit_binding.cover.rank=lru_cache(maxsize=None)(self.cover.rank)
        audit_binding.cover.unrank=lru_cache(maxsize=None)(self.cover.unrank)
        lines=[(i,e) for i,e in enumerate(self.word) if e[0]=='line']
        if self.ports==112:
            need(lines[0]==(4,('line','W0',0,1)), 'frozen first positive line')
            need(next((i,e) for i,e in lines if e[3]<0)==(1705,('line','Z10',76,-1)), 'frozen first negative line')
            need(self.labels[0]==11 and self.labels[76]==448, 'actual literal source labels')
            need(len(lines)==224, 'all frozen native events')
        census=Counter();private_words=0;maxpc=0; compiled=[]
        map_orders=Counter(); map_groups=Fraction(0); map_swaps=Fraction(0)
        map_translations=identity_translations=nonmap_groups=0
        nonmap_census=Counter(); intrinsic=owner_basis=0
        for i,event in enumerate(self.events):
            private_words+=event[0]=='private'
            g=audit_binding.group(i,0,0);maxpc=max(maxpc,len(g.code))
            for op in g.code:census[op[0]]+=1
            compiled.append([g.keys,g.code,g.recipes])
            body=event[2]
            if len(body)==1 and body[0][1][0]=='map':
                e=body[0][1];record=self.maps[(e[2],e[3],e[4])]
                h=self.map_order(tuple(record['owner_right_matrix_columns']))
                map_orders[h]+=1
                nonzero=record['payload_translation_at_identity_owner']!=0
                # Right multiplication acts freely: every orbit has size h.
                # Every orthogonal owner is invertible, so d(delta) is nonzero
                # precisely when delta is. Count each actual map occurrence.
                if h>1 or nonzero:map_groups+=Fraction(1,h)
                map_swaps+=Fraction(h-1,h)
                map_translations+=int(nonzero)
                identity_translations+=sum(op[0]=='monomial' for op in g.code)
            else:
                nonmap_groups+=int(bool(g.code))
                for op in g.code:
                    nonmap_census[op[0]]+=1
                    if op[0]=='monomial':
                        intrinsic+=int(op[3] in ('right','left'))
                        owner_basis+=int(op[3]=='owner')
        def number(q):
            q=Fraction(q)
            return q.numerator if q.denominator==1 else str(q)
        physical={'map_order_histogram':dict(sorted(map_orders.items())),
                  'map_control_visits':sum(map_orders.values()),
                  'map_gather_scatter_commit_groups':number(map_groups),
                  'map_exchanges':number(map_swaps),
                  'map_sign_corrections':number(map_swaps),
                  'map_translation_monomials':map_translations,
                  'map_identity_leader_translation_monomials':identity_translations,
                  'nonmap_groups':nonmap_groups,
                  'all_gather_scatter_commit_groups':number(nonmap_groups+map_groups),
                  'rank_one_children':nonmap_census['child'],
                  'physical_line_monomials':nonmap_census['monomial'],
                  'intrinsic_wrappers':intrinsic,'owner_basis_monomials':owner_basis,
                  'all_monomial_calls_including_map_translations':nonmap_census['monomial']+map_translations,
                  'scalar_engine_calls_including_map_sign_corrections':number(nonmap_census['scalar']+map_swaps),
                  'private_zero_calls':nonmap_census['zero'],
                  'unit':'per full cover divided by Gamma, except identity-leader translation diagnostic'}
        return {'status':'PASS_FULL_COVER_DECODER_COMPILATION','events':len(self.events),
                'literal_decoder_events':len(self.word),'decoder_native_calls':len(lines),
                'compiled_identity_owner_census':dict(sorted(census.items())),
                'physical_per_cover':physical,
                'private_words':private_words,'maximum_pc':maxpc,'families':self.families,
                'slots':self.slots,'private':self.private,
                'compiled_identity_owner_sha256':sha256(json.dumps(compiled,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                'scope':'All finite signed occurrences and cover-barrier compiler; arithmetic correctness inherits authenticated D and source primitive refinements.'}


class ServiceBank:
    """Paid P,family,cover,U,row assembly and fixed-field return extraction.

    Entire source fields are read-only. Every length stays an encoded Count.
    The 224 zero families are newly owned backing; initialization is charged.
    Invoke under an independently installed fixed scratch scope.
    """
    def __init__(self,Tape,Counter,blank,fields=224):
        self.bank=Tape();self.Counter,self.blank=Counter,blank
        self.fields=fields;self.state='closed'

    def _segment(self,source,target,extent,zeros=False):
        remaining=self.Counter(extent)
        try:
            while not remaining.finished:
                value=0 if zeros else source.read()
                need(value in (0,1),'complete binary service segment')
                target.append(value)
                if not zeros:source.step(1)
                remaining.decrement()
        finally:remaining.close()

    def assemble(self,borrowed,prefixes,field_prefix_bits):
        need(self.state=='closed' and len(borrowed)==self.fields, 'closed complete service inputs')
        need(len({id(t) for t in (*borrowed,self.bank)})==self.fields+1,'distinct borrowed/service tapes')
        self.bank.clear()
        for tape in borrowed:tape.rewind()
        counter=self.Counter(prefixes)
        try:
            while not counter.finished:
                for tape in borrowed:self._segment(tape,self.bank,field_prefix_bits)
                for _ in range(self.fields):self._segment(None,self.bank,field_prefix_bits,True)
                counter.decrement()
            need(all(t.read()==self.blank for t in borrowed),'exact whole-family service inputs')
            self.state='assembled'
        finally:
            counter.close();self.bank.rewind()
            for tape in borrowed:tape.rewind()
        return self.bank

    def extract(self,returned,borrowed,outputs,prefixes,field_prefix_bits):
        need(self.state=='assembled' and len(outputs)==len(borrowed)==self.fields,'live complete return')
        need(len({id(t) for t in (*outputs,*borrowed,returned,self.bank)})==2*self.fields+2,
             'exclusive returned and immutable source roles')
        returned.rewind()
        for t in borrowed:t.rewind()
        for t in outputs:t.clear()
        counter=self.Counter(prefixes)
        try:
            while not counter.finished:
                for tape in borrowed:
                    count=self.Counter(field_prefix_bits)
                    try:
                        while not count.finished:
                            need(returned.read() in (0,1) and returned.read()==tape.read(),
                                 'all borrowed returned fields preserved')
                            returned.step(1);tape.step(1);count.decrement()
                    finally:count.close()
                for tape in outputs:self._segment(returned,tape,field_prefix_bits)
                counter.decrement()
            need(returned.read()==self.blank and all(t.read()==self.blank for t in borrowed),'exact complete service return')
        finally:
            counter.close();returned.rewind()
            for t in (*borrowed,*outputs):t.rewind()
        returned.clear();self.bank.clear();self.state='closed'


def finite_maps(word, P, routes, labels, bridge):
    """Compile exact retained affine owner maps before any numerical input."""
    maps={}
    for e in word:
        if e[0]!='map':continue
        _,_,stage,p,inverse=e
        need(stage in (1,2) and type(inverse) is bool,'literal signed map selector')
        g=routes[stage][p]
        b=P.alignment(g,P.F17) if stage==1 else bridge(P,g,labels[p])
        if inverse:b=P.act(g,b)
        maps[(stage,p,inverse)]={'owner_right_matrix_columns':list(g),
                               'payload_translation_at_identity_owner':b}
    return maps


def service_descriptors(caller,Count,families):
    """Paid encoded node descriptors; caller already passed its actual stock cut.

    Allocate/retire these Counts inside the external service's fixed pool.
    source child rows stay U, with ORIGINAL C depth stock, even though this
    finite service's top-level divisor is families*Gamma.
    """
    from machine import INPUTS
    need(caller.group is None and caller.bank.state=='closed', 'completed acquisition fence')
    result={name:Count(caller.c(name)) for name in INPUTS}
    result['rows'].close()
    result['rows']=Count(caller.c('unused'))
    result['rows'].multiply_small(families*caller.binding.cover.size)
    return result
