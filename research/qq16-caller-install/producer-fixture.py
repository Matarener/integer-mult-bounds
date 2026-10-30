# SPDX-License-Identifier: Apache-2.0
"""Reduced physical producer routing and original-child return controls.

Authenticate source closure before launching this fixture. Payload construction
and expected values are test oracles only, not production entry compilers.
"""
from pathlib import Path
import sys,json
from hashlib import sha256
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import runtime
runtime.cold()
runtime.module('producer',Path(__file__).resolve().parent/'producer.py')
import cohort
from cardinal_counts import Count
from records import Tape
from ordinary import Ordinary
from macro_code import Code
from machine import Machine,transfer
from session import erase_marker
from selected_binding import Group,literal
from fixture_binding import FixtureBinding
from cover import OrthogonalCover
from scalar_program import ScalarProgram
from words import BLANK
from producer import map_group,machine_class,act,multiply,need


def native():
    return Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),
                    SimpleNamespace(families=0),(Code((('unreachable',),),0),),capacity=64)


def raw(t):
    return bytes(t.cells[1:]).rstrip(bytes([BLANK]))


def encode(values,h):
    return bytes((x>>b)&1 for pair in values for x in pair for b in range(h))


def execute(binding,expected,external=False):
    child=Machine(FixtureBinding(),native(),FixtureBinding().catalogue)
    fences=[]
    def at_fence(parent):
        need(parent.scope.manager is None and parent.group is None and
             parent.bank.state=='closed' and parent.cover_index==binding.cover.size and
             parent.pc==0 and parent.subgroup==0, 'actual suspended global fence')
        parent.primitive_boundary()
        fences.append(parent.event)
    engine=(machine_class(Machine,Count,transfer,erase_marker)(binding,native(),binding.catalogue,child,at_fence)
            if external else Machine(binding,native(),binding.catalogue))
    # These owned private tapes are discardable scratch, not borrowed inputs.
    for tape in engine.private:
        for bit in (1,0,1):tape.append(bit)
        tape.rewind()
    descriptors={k:Count.literal(v) for k,v in dict(prefixes=2,rows=binding.families*binding.cover.size,front=0,compact_bits=0,
        before=0,width=binding.dimension,after=0,back=0,spacing=1,guard=1,residue=0,
        component_bits=16,coefficients=1,root_width=binding.dimension).items()}
    count=2*binding.families*binding.cover.size*(1<<binding.dimension)
    values=[(64*(i+1),64*((i*5)%13-6)) for i in range(count)]
    source=Tape();data=encode(values,16)
    for b in data:source.append(b)
    source.rewind();snapshots={k:bytes(v.tape.cells) for k,v in descriptors.items()}
    out=engine.run(source,descriptors);actual=raw(out)
    need(actual==encode(expected(values,binding),16),'literal nonconstant physical producer endpoint')
    need(raw(source)==data and all(bytes(v.tape.cells)==snapshots[k] for k,v in descriptors.items()),
         'borrowed producer payload and encoded descriptors preserved')
    need(engine.closed and child.closed and all(t.read()==BLANK for t in engine.parked),
         'producer and original native child eventually close')
    need(fences==([0] if external else []), 'one actual continuation fence')
    answer={'sha256':sha256(actual).hexdigest(),'values':len(values),'outer_prefixes':2,
            'borrowed_preserved':True,'closed':True,'discardable_private_dirty_on_entry':True,
            'actual_global_fence_callbacks':len(fences)}
    out.clear();source.clear()
    for v in descriptors.values():v.close()
    return answer


class MapBinding:
    dimension=2;maximum_rank=1;families=2;slots=2;private=1
    events=('literal_map',);global_fence=0
    def __init__(self,mutation=None):
        self.cover=OrthogonalCover(2);self.mutation=mutation
        self.record={'owner_right_matrix_columns':[2,1],'payload_translation_at_identity_owner':1}
        self.catalogue={('scale',-1,1):ScalarProgram('scale',-1,1)}
    def group_count(self,i):return 1
    def group(self,i,j,k):
        g=map_group(self.cover,k,0,self.record,Group,literal)
        if self.mutation=='omit_exchange':
            return Group(g.keys,tuple(x for x in g.code if x[0] not in ('exchange','scalar')),g.recipes)
        if self.mutation=='omit_translation':
            return Group(g.keys,tuple(x for x in g.code if x[0]!='monomial'),g.recipes)
        if self.mutation=='omit_sign':
            return Group(g.keys,tuple(x for x in g.code if x[0]!='scalar'),g.recipes)
        return g


def map_expected(values,binding):
    out=values[:]
    # Actual physical monomial serialization has v0 as the more significant bit.
    for prefix in range(2):
        for d in range(2):
            owner=binding.cover.unrank(d)
            source=binding.cover.rank(multiply(owner,(2,1)))
            shift=act(owner,1);address_shift=((shift&1)<<1)|((shift>>1)&1)
            for z in range(4):out[prefix*16+d*4+z]=values[prefix*16+source*4+(z^address_shift)]
    return out


def child_expected(values,binding):
    out=values[:]
    for prefix in range(2):
        for owner in range(2):
            start=prefix*16+owner*4
            for z in (0,1):
                a,b=values[start+z];c,d=values[start+z+2]
                out[start+z]=((a-b+c+d)//2,(a+b-c+d)//2)
                out[start+z+2]=((a+b+c-d)//2,(-a+b+c+d)//2)
    return out


class ChildBinding(MapBinding):
    def group(self,i,j,k):return Group(((0,k),), (('child',-1,0,1),),{})

class Map3Binding(MapBinding):
    dimension=3;slots=3
    def __init__(self,mutation=None):
        self.cover=OrthogonalCover(3);self.mutation=mutation
        self.record={'owner_right_matrix_columns':[2,4,1],
                     'payload_translation_at_identity_owner':1}
        if mutation=='transpose_record':self.record['owner_right_matrix_columns']=[4,1,2]
        self.catalogue={('scale',-1,1):ScalarProgram('scale',-1,1)}
    def group(self,i,j,k):
        group=map_group(self.cover,k,0,self.record,Group,literal)
        if self.mutation=='transpose_owner_translation':
            recipes=dict(group.recipes)
            for op in group.code:
                if op[0]=='monomial':
                    owner=self.cover.unrank(group.keys[op[2]][1])
                    recipes[op[3]]=literal((1,2,4),act(owner,1))
            return Group(group.keys,group.code,recipes)
        return group

def map3_expected(values,binding):
    result=values[:];gamma=6;addresses=8
    # Independent dense row-matrix multiplication, with the fixture map
    # columns (2,4,1), hence mathematical rows (4,1,2).
    right_rows=(4,1,2)
    for prefix in range(2):
        for d in range(gamma):
            left=binding.cover.unrank(d)
            product_rows=tuple(sum((sum(((left[i]>>k)&1)*((right_rows[k]>>j)&1)
                                      for k in range(3))%2)<<j for j in range(3))
                               for i in range(3))
            source=binding.cover.rank(product_rows)
            shift=tuple((left[i]&1) for i in range(3))
            physical=sum(v<<(2-i) for i,v in enumerate(shift))
            for z in range(addresses):
                result[prefix*2*gamma*addresses+d*addresses+z]=values[
                    prefix*2*gamma*addresses+source*addresses+(z^physical)]
    return result


class Signed3Binding(Map3Binding):
    """Both actual signed native lines conjugated by every O3 owner."""
    def group(self,i,j,k):
        owner=literal(self.cover.unrank(k))
        recipes={'owner':owner,'identity':literal((1,2,4)),
                 'negative':literal((1,2,4),1)}
        reverse=self.mutation=='reverse_owner_conjugation'
        code=[]
        for target in range(2):
            code.extend((('monomial',-1,target,'owner',not reverse),
                         ('monomial',-1,target,'identity',False),
                         ('child',-1,target,1),
                         ('monomial',-1,target,'identity' if target==0 else 'negative',False),
                         ('monomial',-1,target,'owner',reverse)))
        return Group(((0,k),(1,k)),tuple(code),recipes)


def signed3_expected(values,binding):
    result=values[:]
    for prefix in range(2):
        for family in range(2):
            for owner in range(6):
                rows=binding.cover.unrank(owner)
                # Independent dense row-dot-vector d*q for q=e0; source
                # serializes coordinate zero as the most significant bit.
                direction=tuple(sum(((rows[i]>>j)&1)*(1 if j==0 else 0)
                                    for j in range(3))%2 for i in range(3))
                mask=sum(bit<<(2-i) for i,bit in enumerate(direction))
                need(mask in (1,2,4),'O3 permutation owner image of q')
                start=prefix*96+family*48+owner*8
                for address in range(8):
                    if address&mask:continue
                    a,b=values[start+address];c,d=values[start+(address^mask)]
                    numerators=(a-b+c+d,a+b-c+d,a+b+c-d,-a+b+c+d)
                    need(all(x%2==0 for x in numerators),'exact signed-line fixture grid')
                    plus=tuple(x//2 for x in numerators[:2])
                    minus=tuple(x//2 for x in numerators[2:])
                    result[start+address],result[start+(address^mask)]=(
                        (plus,minus) if family==0 else (minus,plus))
    return result


def run():
    results={'cycle':execute(MapBinding(),map_expected),
             'nonsymmetric_row_column_cycle':execute(Map3Binding(),map3_expected),
             'nonsymmetric_signed_native_conjugation':execute(Signed3Binding(),signed3_expected,True),
             'external_original_child':execute(ChildBinding(),child_expected,True)}
    rejected=[]
    for name in ('omit_exchange','omit_translation','omit_sign'):
        try:execute(MapBinding(name),map_expected)
        except ValueError as exc:
            need('literal nonconstant physical producer endpoint' in str(exc), 'targeted mutation failure')
            rejected.append(name)
        else:raise ValueError('mutation accepted: '+name)
    for name in ('transpose_record','transpose_owner_translation'):
        try:execute(Map3Binding(name),map3_expected)
        except ValueError as exc:
            need('literal nonconstant physical producer endpoint' in str(exc), 'targeted convention failure')
            rejected.append(name)
        else:raise ValueError('matrix convention mutation accepted: '+name)
    try:execute(Signed3Binding('reverse_owner_conjugation'),signed3_expected,True)
    except ValueError as exc:
        need('literal nonconstant physical producer endpoint' in str(exc),
             'targeted nonsymmetric native conjugation failure')
        rejected.append('reverse_owner_conjugation')
    else:raise ValueError('reversed native owner conjugation accepted')
    results['rejected']=rejected
    results['scope']='Reduced actual Tape/BankPackets/MonomialPackets/Ordinary/Machine execution; no selected O73 payload or supplier theorem.'
    return results


if __name__=='__main__':
    try:print(json.dumps(run(),sort_keys=True))
    finally:runtime.cleanup()
