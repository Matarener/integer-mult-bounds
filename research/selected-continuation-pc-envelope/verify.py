"""Bounded source derivation, independent fallback plans and actual header codec."""
import argparse
import ast
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from math import prod
from pathlib import Path
import sys
from types import SimpleNamespace as NS
sys.path.insert(0,str(Path(__file__).resolve().parent))
from envelope import authenticate,derive,source_header,extract,fallback_bound,need,HERE,BASE,VENDOR


def rejects(fn,marker):
    try:fn()
    except (ValueError,OverflowError) as e:
        need(marker in str(e),'wrong rejection '+str(e));return
    raise ValueError('control survived '+marker)


def plan_checks(data,header):
    env={'dataclass':dataclass,'prod':prod,'need':need,'__name__':__name__}
    extract(data[VENDOR+'plan.py'],{'Reference','Command','Plan','compile_plan'},env)
    Cursor=extract(data[BASE+'residual_blocks.py'],{'Cursor'},{'need':need,'FiniteFields':header['FiniteFields']})['Cursor']
    # Directly count source commands with an independently derived cost census.
    cases=0;max_blocks=0
    for q,d in ((3,2),(5,2),(3,3)):
        seen=set()
        for u in product(range(q),repeat=d):
            if not any(u):continue
            for v in product(range(q),repeat=d):
                if sum(a*b for a,b in zip(u,v))%q!=1:continue
                matrix=tuple(tuple(a*b%q for b in v) for a in u)
                if matrix in seen:continue
                seen.add(matrix)
                for good in (False,True):
                    plan=env['compile_plan'](matrix,1,q,good)
                    count=3 if good else sum(3 if c.kind=='child' else 1 for c in plan.commands)
                    n=2*d
                    expected=3 if good else 6*(n-1)+4*n*(n-1)+3*sum(r[0]=='swap' for r in plan.reductions)+int(plan.negative_sign)
                    need(count==expected and 3<=count<=fallback_bound(d),'source fallback exact census')
                    cursor=Cursor(plan);observed=0
                    while not cursor.done:cursor.take();observed+=1
                    need(observed==count,'literal Cursor block count')
                    cases+=1;max_blocks=max(max_blocks,count)
    return {'projector_plan_cases':cases,'max_small_blocks':max_blocks}


def header_checks(data,e):
    h=source_header(data);Tape,Fields=h['Tape'],h['FiniteFields']
    bounds=(2,1,e.upper,8,8,8,8,8)
    schema=Fields(bounds);tape=Tape()
    owner=NS(header=schema,root=True,mode=0,pc=e.lower-2,size=NS(slot=3),depth=NS(slot=4),
             context=NS(cap=NS(slot=2)),tape=lambda label:tape)
    ring=NS(modulus=NS(slot=0),one=NS(slot=1))
    h['write_source'](owner,ring)
    need(len(tape.cells)==1+sum(schema.widths),'actual serialized extent')
    owner.mode=0;owner.pc=0
    h['read_source'](owner,ring)
    need(owner.pc==e.lower-1 and tape.head==1,'source call/return projected PC restoration')
    tape.clear()
    width=sum(schema.widths)
    need(tape.meter.record()==dict(reads=6*width+9,writes=2*width,moves=6*width+12,peak_live=0,allocations=0),'exact actual tape codec cost')
    meter=tape.meter.record()
    rejects(lambda:schema.write(tape,(1,0,e.upper,0,0,0,0,0)),'finite continuation label')
    # An upper-bound schema alone does not certify exact index-provider admission.
    probe=Tape();Fields((e.upper,)).write(probe,(e.upper-1,))
    need(Fields((e.upper,)).read(probe)==(e.upper-1,),'format admits upper interval')
    class TooLong:
        def __len__(self):return e.lower
    rejects(lambda:len(TooLong()),'cannot fit')
    return {'header_width_bits':width,'pc_width_bits':schema.widths[2],
            'projected_source_call_return':'PASS; header statements only, no parking/payload replay',
            'header_roundtrip_and_clear_meter':meter,
            'length_overflow_rejected':True,'exact_index_admission':'REQUIRED_NOT_PROVIDED'}


def semantic_controls(data):
    changed=dict(data)
    key=BASE+'residual_blocks.py'
    need(changed[key].count(b'if stage < 2:')==1,'stage mutant anchor')
    changed[key]=changed[key].replace(b'if stage < 2:',b'if stage < 1:')
    rejects(lambda:plan_checks(changed,source_header(data)),'literal Cursor block count')
    changed=dict(data);key=BASE+'macro_machine.py'
    changed[key]=changed[key].replace(b'self.pc + 1,',b'self.pc,')
    rejects(lambda:source_header(changed),'source saved next PC')
    need(fallback_bound(64)>6*127+4*128*127,'swap/sign terms retained')
    return ['child stage omitted','saved successor omitted','swap/sign upper terms required']


def run():
    data=authenticate();e,source=derive(data)
    need((e.nonblocks_per_low,e.residuals_per_low,e.fixed,e.block_max)==(9580608,904896,78175,66168),'actual source census')
    need(e.lower>sys.maxsize and e.lower<e.upper,'nontrivial selected interval')
    result={'status':'PASS_SOURCE_CONTINUATION_PC_ENVELOPE','source':source,
      'envelope':{'low_cardinality_bits':e.low_classes.bit_length(),
       'lower_multiplier':e.nonblocks_per_low+3*e.residuals_per_low,
       'upper_multiplier':e.nonblocks_per_low+e.block_max*e.residuals_per_low,'fixed':e.fixed,
       'nonblocks_per_low':e.nonblocks_per_low,'residuals_per_low':e.residuals_per_low,'max_blocks_per_residual':e.block_max,
       'lower_pc_bits':(e.lower-1).bit_length(),'upper_pc_bits':(e.upper-1).bit_length(),
       'lower_sha256':sha256(hex(e.lower).encode()).hexdigest(),'upper_sha256':sha256(hex(e.upper).encode()).hexdigest()},
      'plans':plan_checks(data,source_header(data)),'header':header_checks(data,e),
      'semantic_controls':semantic_controls(data),
      'scope':'Historical source-selected PR2753/PR589 caller; not selected PR5413 supplier admission or full index implementation.'}
    authenticate();return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    result=run();text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if a.write:(HERE/'RESULT.json').write_text(text)
    else:need((HERE/'RESULT.json').read_text()==text,'typed receipt')
    print(text,end='')
