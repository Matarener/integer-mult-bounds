# SPDX-License-Identifier: Apache-2.0
"""One continuous reduced physical caller/recovery/current-return/bridge run.

Authenticated actual primitive implementations are used at every arithmetic
endpoint. The two-dimensional finite control and initial/expected arrays are
explicit test fixtures, not a selected O73 execution or production loader.
"""
from pathlib import Path
import sys,json
from hashlib import sha256
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import runtime
runtime.cold()
P=runtime.module('qq16_producer',HERE/'producer.py')
D=runtime.module('qq16_decoder',HERE/'decoder.py')
K=runtime.module('qq16_packet',HERE/'packet.py')
L=runtime.module('qq16_lifecycle',HERE/'lifecycle.py')
J=runtime.module('qq16_installer',HERE/'installer.py')
C=runtime.module('qq16_connection',HERE/'connection.py')
from machine import Machine,transfer
from cardinal_counts import Count
from records import Tape
from ordinary import Ordinary
from macro_code import Code
from session import erase_marker
from selected_binding import Group,literal
from fixture_binding import FixtureBinding
from cover import OrthogonalCover
from scalar_program import ScalarProgram
from words import BLANK
from stream import Counter
from root_layer import RootLayer


def native():
    return Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),SimpleNamespace(families=0),
                    (Code((('unreachable',),),0),),capacity=64)


def raw(t):return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
def encode(values,h):return bytes((x>>b)&1 for pair in values for x in pair for b in range(h))
def recipe(q,sign,dimension):
    P.need(q==1 and dimension==2 and sign in (-1,1),'reduced actual signed line')
    return {'right':literal((1,2)),'left':literal((1,2),0 if sign==1 else 1)}


class CallerBinding:
    dimension=2;maximum_rank=1;families=4;slots=4;private=1
    events=('Q_signed_pair','intervening_dirty_helper','idle_pair1','both_bridge_legs')
    global_fence=1
    def __init__(self,wrong_sign=False):
        self.cover=OrthogonalCover(2);self.wrong_sign=wrong_sign
        self.catalogue={k:ScalarProgram(*k) for k in [('add',1,1),('add',-1,1),('scale',-1,1)]}
    def group_count(self,event):return 1
    def group(self,event,subgroup,owner):
        P.need(subgroup==0 and 0<=event<4,'literal reduced parent control')
        if event==0:
            keys=((0,owner),(1,owner));code=[];recipes={}
            for target,sign in ((0,1),(1,1 if self.wrong_sign else -1)):
                for name,record in [('g',literal(self.cover.unrank(owner))),
                                    ('right',recipe(1,sign,2)['right']),
                                    ('left',recipe(1,sign,2)['left'])]:
                    recipes[str(target)+name]=record
                code.extend((('monomial',-1,target,str(target)+'g',True),
                             ('monomial',-1,target,str(target)+'right',False),
                             ('child',-1,target,1),
                             ('monomial',-1,target,str(target)+'left',False),
                             ('monomial',-1,target,str(target)+'g',False)))
            return Group(keys,tuple(code),recipes)
        if event==1:
            # Nonconstant dirty helper receives two real translation operations.
            return Group(((3,owner),),(('monomial',-1,0,'shift',False),
                                     ('monomial',-1,0,'shift',False)),{'shift':literal((1,2),1)})
        if event==2:
            return Group(((2,owner),),(('child',-1,0,1),),{})
        return Group(((0,owner),(2,owner),(3,owner),(1,owner)),
                     (('scalar',-1,0,1,('add',1,1)),
                      ('scalar',-1,2,3,('add',-1,1))),{})

class OriginalBinding(FixtureBinding):
    """Direct sum of two disjoint source complete-C fixture groups.

    This preserves the original source instructions and matches the caller's
    four-family row-stock geometry; it is still explicitly reduced geometry.
    """
    families=4
    def group_count(self,event):
        P.need(event==0,'original reduced C event')
        return 2
    def group(self,event,subgroup,owner):
        P.need(subgroup in (0,1),'original disjoint complete-C group')
        source=super().group(event,0,owner)
        return Group(tuple((family+2*subgroup,d) for family,d in source.keys),
                     source.code,source.recipes)


def line(values,mask,sign):
    """Independent exact Gaussian 2x2 tensor on one physical address bit."""
    result=list(values)
    for a in range(4):
        if a&mask:continue
        b=a^mask;x,y=values[a];u,v=values[b]
        plus=((x-y+u+v)//2,(x+y-u+v)//2)
        other=((x+y+u-v)//2,(-x+y+u+v)//2)
        P.need(all(z%2==0 for z in (x-y+u+v,x+y-u+v,x+y+u-v,-x+y+u+v)),
               'exact reduced input grid')
        result[a],result[b]=(plus,other) if sign==1 else (other,plus)
    return result


def expected(values,binding):
    result=list(values)
    for prefix in range(2):
        for owner in range(2):
            start=prefix*32+owner*4
            x=values[start:start+4];y=values[start+8:start+12]
            u=values[start+16:start+20];v=values[start+24:start+28]
            direction=P.act(binding.cover.unrank(owner),1)
            mask=((direction&1)<<1)|((direction>>1)&1)
            # Q is H+ on X and H- on Y. D recovers both. The reduced current
            # return then applies W+=Z, Z-=W, W=H-(W), exactly its literal word.
            z=[(-a,-b) for a,b in y]
            w=line([(a+c,b+d) for (a,b),(c,d) in zip(x,y)],mask,-1)
            idle=line(u,2,1)  # source prepare_child selects the leading column
            result[start:start+4]=[(a+c,b+d) for (a,b),(c,d) in zip(z,idle)]
            result[start+8:start+12]=w
            result[start+16:start+20]=idle
            result[start+24:start+28]=[(a-c,b-d) for (a,b),(c,d) in zip(v,w)]
    return result


def run_case(mutation=None):
    binding=CallerBinding(mutation=='wrong_producer_sign')
    word=[['clear','Z0','current'],['add','Z0','X0','1'],['line','Z0',0,-1],
          ['clear','W0','current'],['add','W0','Y0','1'],['line','W0',0,1]]
    decoder=D.DecoderBinding(word,{'recipes':[{'q':1}]},{},binding.cover,Group,literal,
        ScalarProgram,recipe,P.map_group,P.order,ports=1,dimension=2,continuation=True)
    original=OriginalBinding()
    root=RootLayer(original,native(),original.catalogue)
    child=root.machine
    public_root=(root.current,root.output,root.plan)
    inherited_native=child.monomial.compact.binary.native
    try:
        C.install(root,binding,decoder,lambda:inherited_native)
    except ValueError as exc:
        P.need('three distinct admitted Ordinary inventories' in str(exc),
               'factory rejects shared ordinary backend')
    else:raise ValueError('factory accepted shared ordinary backend')
    P.need(root.machine is child,'rejected factory preserves original root')
    installation=C.install(root,binding,decoder,native)
    parent=root.machine
    service=installation.service
    P.need(parent.at_fence is installation and parent.native_child is child and
           public_root==(root.current,root.output,root.plan),
           'actual connection factory installs root and exact original child')
    seen=[]
    def fence(parent):
        seen.append((parent.event,parent.cover_index,parent.pc,parent.bank.state))
        if mutation=='early_fence':
            parent.cover_index-=1
        if mutation=='output_alias':
            installation.storage.outputs=(installation.acquisition.packets[0],installation.storage.outputs[1])
        installation(parent)
    parent.at_fence=fence
    # Attachment rejection controls inspect the same closed objects before
    # numerical input, temporarily exposing the retained original endpoint.
    # The successful execution below uses the factory-created attachment.
    root.machine=child
    root.closed=False
    try:
        J.attach_root(root,parent)
    except ValueError as exc:
        P.need('closed root construction' in str(exc),'active RootLayer attachment rejected')
    else:raise ValueError('active RootLayer attachment accepted')
    finally:root.closed=True
    parent.native_child=service
    try:
        J.attach_root(root,parent)
    except ValueError as exc:
        P.need('retain the root original C engine' in str(exc),'wrong inherited endpoint rejected')
    else:raise ValueError('wrong original RootLayer child accepted')
    finally:parent.native_child=child
    for attribute in ('dimension','maximum_rank','families','cover'):
        original_value=getattr(binding,attribute)
        setattr(binding,attribute,SimpleNamespace(size=3) if attribute=='cover' else original_value+1)
        try:
            J.attach_root(root,parent)
        except ValueError as exc:
            P.need('unchanged root-plan dimension rank family and cover geometry' in str(exc),
                   'changed root-plan geometry rejected: '+attribute)
        else:raise ValueError('changed root-plan geometry accepted: '+attribute)
        finally:setattr(binding,attribute,original_value)
    root.machine=parent
    P.need(root.machine is parent and public_root==(root.current,root.output,root.plan),
           'actual RootLayer compile-time attachment preserves public roles and plan')
    values=[(256*((i*7)%19-9),256*((i*11)%23-11)) for i in range(64)]
    source=Tape();data=encode(values,32)
    for bit in data:source.append(bit)
    source.rewind()
    descriptors={k:Count.literal(v) for k,v in dict(prefixes=2,rows=8,front=0,compact_bits=0,
        before=0,width=2,after=0,back=0,spacing=1,guard=1,residue=0,component_bits=32,
        coefficients=1,root_width=2).items()}
    descriptor_images={k:bytes(v.tape.cells) for k,v in descriptors.items()}
    for tape in (*installation.storage.roles,*parent.private):
        for bit in (1,0,1,1):tape.append(bit)
        tape.rewind()
    try:
        result=parent.run(source,descriptors);actual=raw(result)
        P.need(actual==encode(expected(values,binding),32),'composed producer recovery current-return and both bridge outputs')
        P.need(raw(source)==data and all(bytes(v.tape.cells)==descriptor_images[k] for k,v in descriptors.items()),
               'complete borrowed entry and descriptors preserved')
        P.need(seen==[(1,2,0,'closed')] and installation.calls==1 and installation.completed,
               'one exact completed producer fence installed')
        P.need(parent.closed and service.closed and child.closed and installation.storage.stage=='closed'
               and installation.bundle.state=='closed' and installation.compiler.closed,
               'all caller/service/native/compiler lifetimes retired')
        P.need(all(t.read()==BLANK for t in (*installation.storage.roles,*parent.parked)),
               'dirty owned helpers and output generations retired')
        answer={'status':'PASS_CONTINUOUS_PHYSICAL_CALLER_INSTALLATION','sha256':sha256(actual).hexdigest(),
            'outer_prefixes':2,'families':4,'owners':2,'complex_values':64,'physical_component_bits':32,
            'all_entry_exit_outputs_checked':True,'actual_signed_original_C_calls':True,
            'borrowed_preserved':True,'dirty_owned_scratch_retired':True,'both_bridge_legs':True,
            'actual_root_layer_attachment_checked':True,'root_attachment_negative_controls':6,
            'actual_connection_factory_checked':True,'factory_inventory_rejection_checked':True,
            'source_preparation':'test oracle only','scope':'Reduced physical composition; selected O73 proof and production cost remain separate.'}
        result.clear()
        if mutation is None:
            # A different nonconstant input exercises fresh generations on the
            # same three engines and the same Installation after adoption.
            second_values=[(-b,a) for a,b in reversed(values)]
            second_data=encode(second_values,32)
            source.clear()
            for bit in second_data:source.append(bit)
            source.rewind()
            result=parent.run(source,descriptors)
            second_actual=raw(result)
            P.need(second_actual==encode(expected(second_values,binding),32) and
                   raw(source)==second_data and installation.calls==2 and installation.completed,
                   'same physical engines accept a fresh full generation')
            P.need(seen==[(1,2,0,'closed')]*2 and installation.storage.stage=='closed' and
                   all(bytes(v.tape.cells)==descriptor_images[k] for k,v in descriptors.items()),
                   'second generation preserves descriptors and closes at exact fence')
            answer['same_engine_second_generation_sha256']=sha256(second_actual).hexdigest()
            answer['completed_generations']=2
            result.clear()
        return answer
    except ValueError:
        if mutation in ('early_fence','output_alias'):
            P.need(raw(source)==data and source.head==1 and
                   all(bytes(v.tape.cells)==descriptor_images[k] and v.tape.head==1
                       for k,v in descriptors.items()),
                   'internal rejection preserves borrowed bytes and heads before fixture cleanup')
            P.need(installation.storage.stage=='closed' and installation.bundle.state=='closed'
                   and installation.compiler.closed and service.closed and child.closed
                   and all(t.read()==BLANK for t in J.owned_tapes(installation)),
                   'Installation.discard closes all owned backing before fixture cleanup')
        raise
    finally:
        source.clear()
        for v in descriptors.values():v.close()
        # Rejection cleanup belongs to the fixture, with no postfailure result
        # admitted. Successful cleanup above is checked before this recovery.
        for m in (parent,service,child):m.discard()
        for t in (*installation.storage.roles,installation.bundle.bank):t.clear()
        installation.compiler.close()


def main():
    good=run_case();rejects={}
    for mutation,reason in [('wrong_producer_sign','composed producer recovery'),
                            ('early_fence','whole-cover producer fence'),
                            ('output_alias','exclusive physical caller/native/wrapper inventory')]:
        try:run_case(mutation)
        except ValueError as exc:
            P.need(reason in str(exc),'targeted integrated rejection '+mutation+': '+str(exc))
            rejects[mutation]=str(exc)
        else:raise ValueError('accepted integrated mutation '+mutation)
    return {'continuous':good,'rejections':rejects,
            'internal_rejection_cleanup_checked_before_fixture_recovery':True}


if __name__=='__main__':
    try:print(json.dumps(main(),sort_keys=True))
    finally:runtime.cleanup()
