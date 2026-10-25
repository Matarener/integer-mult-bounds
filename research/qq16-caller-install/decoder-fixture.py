# SPDX-License-Identifier: Apache-2.0
"""Reduced actual decoder grammar and all-output prefix zipper controls.

Authenticate source closure before execution. Initial payloads/expected arrays
are test oracles only. This does not execute selected O73 production geometry.
"""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import sys,json
from hashlib import sha256
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import runtime
runtime.cold()
runtime.module('producer',HERE/'producer.py')
runtime.module('decoder',HERE/'decoder.py')
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
from stream import Counter
from producer import map_group,machine_class,order,need
from decoder import DecoderBinding,ServiceBank


def native():
    return Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),
                    SimpleNamespace(families=0),(Code((('unreachable',),),0),),capacity=64)


def raw(t):return bytes(t.cells[1:]).rstrip(bytes([BLANK]))

def encode(values,h):return bytes((x>>b)&1 for pair in values for x in pair for b in range(h))

def recipe(q,sign,dimension):
    need(dimension==2 and q in (1,2),'reduced signed orthogonal axes')
    axes=(1,2) if q==1 else (2,1)
    return {'right':literal(axes),'left':literal(axes,0 if sign==1 else q)}


def zipper():
    fields=224;inputs=tuple(Tape() for _ in range(fields));outputs=tuple(Tape() for _ in range(fields))
    service=ServiceBank(Tape,Counter,BLANK,fields)
    p,n=Count.literal(3),Count.literal(7)
    images=[]
    for family,t in enumerate(inputs):
        bits=bytes(((family*7+prefix*5+bit*3)>>(bit%3))&1 for prefix in range(3) for bit in range(7))
        images.append(bits)
        for b in bits:t.append(b)
        t.rewind()
    bank=service.assemble(inputs,p,n)
    expected=b''.join(b''.join(x[k*7:(k+1)*7] for x in images)+bytes(fields*7) for k in range(3))
    need(raw(bank)==expected,'prefix-major all448family bank order')
    returned=Tape();returned_bits=bytearray(expected)
    outimages=[bytes((family+prefix+bit)%2 for prefix in range(3) for bit in range(7)) for family in range(fields)]
    for prefix in range(3):
        start=prefix*fields*14+fields*7
        returned_bits[start:start+fields*7]=b''.join(x[prefix*7:(prefix+1)*7] for x in outimages)
    for b in returned_bits:returned.append(b)
    returned.rewind()
    service.extract(returned,inputs,outputs,p,n)
    need(all(raw(t)==v for t,v in zip(inputs,images)),'all224 borrowed values preserved')
    need(all(raw(t)==v for t,v in zip(outputs,outimages)),'all224 output family order')
    need(raw(service.bank)==raw(returned)==b'' and service.state=='closed','bank/output consumed')
    # Prefix truncation is rejected without changing a borrowed source.
    short=Tape()
    for b in images[0][:-1]:short.append(b)
    short.rewind();rejected=False
    try:service.assemble((short,*inputs[1:]),p,n)
    except ValueError:rejected=True
    need(rejected and all(raw(t)==v for t,v in zip(inputs,images)),'short-source rejected with original sources preserved')
    answer={'status':'PASS_224_OUTPUT_ENCODED_PREFIX_ZIPPER','prefixes':3,'borrowed':224,'owned':224,
            'bits_per_family_prefix':7,'assembled_sha256':sha256(expected).hexdigest(),
            'all_outputs_checked':True,'short_input_rejected':True}
    for t in (*inputs,*outputs,short,service.bank):t.clear()
    p.close();n.close()
    return answer


def physical(mutation=None):
    word=[['clear','Z0','current'],['add','Z0','X0','1'],
          ['clear','Z1','current'],['add','Z1','X1','1'],
          ['clear','W0','current'],['add','W0','Y0','1'],
          ['clear','W1','current'],['add','W1','Y1','1'],
          ['line','W0',0,1],['map','W1',1,0,False],
          ['begin','private',8],['clear','F0','current'],
          ['add','F0','Z0','1'],['add','Z1','F0','1/4'],
          ['add','Z1','F0','-1/4'],['add','F0','Z0','-1'],
          ['clear','F0','current'],['end','private',8],
          ['map','W1',1,0,True],['line','W0',0,-1],
          ['checkpoint','return']]
    if mutation=='negative_sign': word[19][3]=1
    maps={(1,0,False):{'owner_right_matrix_columns':[2,1],'payload_translation_at_identity_owner':1},
          (1,0,True):{'owner_right_matrix_columns':[2,1],'payload_translation_at_identity_owner':2}}
    binding=DecoderBinding(word,{'recipes':[{'q':1},{'q':2}]},maps,OrthogonalCover(2),Group,literal,
                           ScalarProgram,recipe,map_group,order,ports=2,dimension=2)
    childbinding=FixtureBinding();child=Machine(childbinding,native(),childbinding.catalogue)
    engine=machine_class(Machine,Count,transfer,erase_marker)(binding,native(),binding.catalogue,child)
    h=20;rows=16;prefixes=2
    desc={k:Count.literal(v) for k,v in dict(prefixes=prefixes,rows=rows,front=0,compact_bits=0,before=0,
        width=2,after=0,back=0,spacing=1,guard=1,residue=0,component_bits=h,coefficients=1,root_width=2).items()}
    # Physical order P, family8, owner2, payload4. Includes arbitrary nonzero owned dirt.
    values=[(256*(3+i%17),256*((i*5)%13-6)) for i in range(prefixes*rows*4)]
    src=Tape();data=encode(values,h)
    for b in data:src.append(b)
    src.rewind();snapshots={k:raw(v.tape) for k,v in desc.items()}
    out=engine.run(src,desc)
    expected=values[:]
    def cm(a,b,negative):
        x=complex(*a);y=complex(*b)
        pair=((x+y+1j*(x-y))/2,(x+y-1j*(x-y))/2)
        if negative:pair=pair[::-1]
        return [(int(z.real),int(z.imag)) for z in pair]
    for prefix in range(prefixes):
        for owner in range(2):
            for port in range(2):
                xx=prefix*64+port*8+owner*4
                yy=prefix*64+(2+port)*8+owner*4
                zz=prefix*64+(4+port)*8+owner*4
                ww=prefix*64+(6+port)*8+owner*4
                for z in range(4):
                    expected[zz+z]=tuple(-a for a in values[yy+z])
                    expected[ww+z]=tuple(a+b for a,b in zip(values[xx+z],values[yy+z]))
                # Cover owner swaps the two intrinsic q axes.
                axis=(2 if port==0 else 1) if owner==0 else (1 if port==0 else 2)
                for z in range(4):
                    if not z&axis:
                        expected[ww+z],expected[ww+(z^axis)]=cm(expected[ww+z],expected[ww+(z^axis)],True)
    need(raw(out)==encode(expected,h),'actual D-grammar both-sign/current-return endpoint')
    need(raw(src)==data and all(raw(v.tape)==snapshots[k] for k,v in desc.items()),'borrowed inputs and descriptors preserved')
    need(engine.closed and child.closed and all(t.read()==BLANK for t in engine.parked),'all service/native state closed')
    result={'status':'PASS_ACTUAL_REDUCED_DECODER_GRAMMAR','prefixes':prefixes,'cover':2,
            'nonconstant_complex_values':len(values),'dimension':2,'component_bits':h,
            'endpoint_sha256':sha256(raw(out)).hexdigest(),'both_signs':True,'private_scope':8,
            'compiler':binding.audit(),'scope':'Reduced full grammar on actual source Machine/MonomialPackets/native C, not selected full D or O73 production execution.'}
    out.clear();src.clear()
    for v in desc.values():v.close()
    return result


def run():
    result={'zipper':zipper(),'physical':physical()}
    try: physical('negative_sign')
    except ValueError as exc:
        need('actual D-grammar both-sign/current-return endpoint' in str(exc), 'targeted native sign failure')
        result['negative_sign_rejected']=True
    else: raise ValueError('native sign mutation accepted')
    return result

if __name__=='__main__':
    try:print(json.dumps(run(),sort_keys=True))
    finally:runtime.cleanup()
